#!/usr/bin/env python3
"""Run the frozen Gate C6B GSE23307 and MSigDB orthogonal analyses."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from phase17_c6b_03_fit_frozen_regulators import (
    CONFIRMATORY,
    bh_adjust,
    load_ranked_statistics,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--resource-dir",
        type=Path,
        default=Path("phase17_v7/gateC6B/20260815_pre_effect_resource_freeze"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("phase17_v7/gateC6B/20260815_regulatory_evidence"),
    )
    parser.add_argument("--seed", type=int, default=20260815)
    parser.add_argument("--permutations", type=int, default=10000)
    return parser.parse_args()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def stable_seed(base_seed: int, label: str) -> int:
    token = f"{base_seed}|{label}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(token).digest()[:8], "little")


def load_selected_expression(
    matrix_path: Path,
    selected_probes: set[str],
) -> tuple[list[str], dict[str, list[float]]]:
    sample_ids: list[str] | None = None
    values: dict[str, list[float]] = {}
    in_table = False
    with gzip.open(matrix_path, "rt", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            if line == "!series_matrix_table_begin":
                in_table = True
                continue
            if line == "!series_matrix_table_end":
                break
            if not in_table:
                continue
            fields = next(csv.reader([line], delimiter="\t", quotechar='"'))
            if sample_ids is None:
                if fields[0] != "ID_REF":
                    raise ValueError("GSE23307 matrix does not begin with ID_REF")
                sample_ids = fields[1:]
                continue
            probe = fields[0]
            if probe in selected_probes:
                row_values = [float(value) for value in fields[1:]]
                if len(row_values) != len(sample_ids) or not all(
                    np.isfinite(row_values)
                ):
                    raise ValueError(f"Invalid expression row for {probe}")
                values[probe] = row_values
    if sample_ids is None:
        raise ValueError("GSE23307 matrix table not found")
    missing = selected_probes - set(values)
    if missing:
        raise ValueError(f"Mapped probes absent from matrix: {sorted(missing)}")
    return sample_ids, values


def enrichment_score(
    ranked_statistics: np.ndarray,
    hit_positions: np.ndarray,
) -> tuple[float, int]:
    positions = np.sort(np.asarray(hit_positions, dtype=int))
    n_genes = len(ranked_statistics)
    n_hits = len(positions)
    if n_hits == 0 or n_hits == n_genes:
        raise ValueError("GSEA requires both hit and miss genes")
    weights = np.abs(ranked_statistics[positions])
    weight_sum = float(weights.sum())
    if weight_sum == 0:
        weights = np.ones(n_hits, dtype=float)
        weight_sum = float(n_hits)
    hit_cumulative = np.cumsum(weights / weight_sum)
    misses_before = positions - np.arange(n_hits)
    run_at_hit = hit_cumulative - misses_before / (n_genes - n_hits)
    previous_hits = np.concatenate([np.asarray([0.0]), hit_cumulative[:-1]])
    run_before_hit = previous_hits - misses_before / (n_genes - n_hits)
    positive_index = int(np.argmax(run_at_hit))
    negative_index = int(np.argmin(run_before_hit))
    positive_es = float(run_at_hit[positive_index])
    negative_es = float(run_before_hit[negative_index])
    if abs(positive_es) >= abs(negative_es):
        return positive_es, int(positions[positive_index])
    return negative_es, int(positions[negative_index])


def run_preranked_gsea(
    symbols: list[str],
    statistics: np.ndarray,
    gene_set: set[str],
    permutations: int,
    seed: int,
) -> dict[str, Any]:
    order = np.argsort(-statistics, kind="mergesort")
    ranked_statistics = statistics[order]
    ranked_symbols = np.asarray(symbols)[order]
    hit_positions = np.flatnonzero(np.isin(ranked_symbols, sorted(gene_set)))
    observed_es, peak_position = enrichment_score(ranked_statistics, hit_positions)
    rng = np.random.default_rng(seed)
    null_es = np.empty(permutations, dtype=float)
    for index in range(permutations):
        positions = rng.choice(len(ranked_symbols), size=len(hit_positions), replace=False)
        null_es[index] = enrichment_score(ranked_statistics, positions)[0]
    same_sign = null_es[null_es >= 0] if observed_es >= 0 else null_es[null_es < 0]
    if len(same_sign) == 0:
        raise ValueError("GSEA null lacks same-sign estimates")
    p_value = float(
        (1 + np.sum(np.abs(same_sign) >= abs(observed_es))) / (1 + len(same_sign))
    )
    nes = float(observed_es / np.mean(np.abs(same_sign)))
    if observed_es >= 0:
        leading = [
            str(ranked_symbols[position])
            for position in hit_positions
            if position <= peak_position
        ]
    else:
        leading = [
            str(ranked_symbols[position])
            for position in hit_positions
            if position >= peak_position
        ]
    return {
        "ranked_genes": len(ranked_symbols),
        "matched_genes": len(hit_positions),
        "enrichment_score": observed_es,
        "normalized_enrichment_score": nes,
        "permutation_p_value": p_value,
        "permutations": permutations,
        "positive_null_permutations": int(np.sum(null_es >= 0)),
        "negative_null_permutations": int(np.sum(null_es < 0)),
        "peak_rank_one_based": peak_position + 1,
        "leading_edge_genes": ";".join(leading),
        "leading_edge_count": len(leading),
    }


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    resource_dir = args.resource_dir if args.resource_dir.is_absolute() else root / args.resource_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    method_freeze = json.loads(
        (output_dir / "09_C6B3_ORTHOGONAL_METHOD_FREEZE.json").read_text(encoding="utf-8")
    )
    if method_freeze["decision"] != "PASS_GATE_C6B3_ORTHOGONAL_METHOD_FREEZE":
        raise RuntimeError("Gate C6B-3 did not authorize orthogonal effect calculation")
    if method_freeze["gse23307_expression_effects_inspected"]:
        raise RuntimeError("Gate C6B-3 record must be expression blind")
    scale_repair = json.loads(
        (output_dir / "15_C6B3A_SCALE_REPAIR_FREEZE.json").read_text(encoding="utf-8")
    )
    if scale_repair["decision"] != "PASS_C6B3A_OBJECTIVE_SCALE_REPAIR_RERUN_REQUIRED":
        raise RuntimeError("Objective GSE23307 scale repair was not authorized")

    mapping = list(
        csv.DictReader(
            (output_dir / "08_GSE23307_FROZEN_PROBE_MAPPING.csv").open(
                "r", encoding="utf-8", newline=""
            )
        )
    )
    probe_to_gene = {row["probe_id"]: row["gene_symbol"] for row in mapping}
    sample_ids, expression = load_selected_expression(
        resource_dir / "resources/GSE23307_series_matrix.txt.gz",
        set(probe_to_gene),
    )
    sample_index = {sample: index for index, sample in enumerate(sample_ids)}
    pairing = [
        row
        for row in csv.DictReader(
            (resource_dir / "06_GSE23307_SAMPLE_PAIRING.csv").open(
                "r", encoding="utf-8", newline=""
            )
        )
        if row["include_paired_bcell"].lower() == "true"
    ]
    included_samples = [row["geo_accession"] for row in pairing]
    gene_probes: dict[str, list[str]] = defaultdict(list)
    for probe, gene in probe_to_gene.items():
        gene_probes[gene].append(probe)

    selected_raw_values = [value for probe_values in expression.values() for value in probe_values]
    if min(selected_raw_values) < 0:
        raise ValueError("GSE23307 log2(x + 1) repair requires non-negative intensities")
    sample_gene_rows: list[dict[str, Any]] = []
    gene_sample_value: dict[tuple[str, str], float] = {}
    for gene in method_freeze["gse23307_method"]["genes"]:
        probes = sorted(gene_probes[gene])
        for sample in included_samples:
            value = float(
                np.median(
                    [
                        np.log2(expression[probe][sample_index[sample]] + 1.0)
                        for probe in probes
                    ]
                )
            )
            gene_sample_value[(gene, sample)] = value
            sample_gene_rows.append(
                {
                    "gene_symbol": gene,
                    "sample": sample,
                    "probe_count": len(probes),
                    "probe_ids": ";".join(probes),
                    "median_log2p1_expression": value,
                }
            )

    pairing_by_donor = defaultdict(dict)
    for row in pairing:
        pairing_by_donor[row["donor_id"]][row["condition"]] = row["geo_accession"]
    gene_effect_rows: list[dict[str, Any]] = []
    donor_rows: list[dict[str, Any]] = []
    for donor in sorted(pairing_by_donor):
        ifn_sample = pairing_by_donor[donor]["IFN_beta"]
        control_sample = pairing_by_donor[donor]["control"]
        donor_effects = []
        for gene in method_freeze["gse23307_method"]["genes"]:
            ifn_value = gene_sample_value[(gene, ifn_sample)]
            control_value = gene_sample_value[(gene, control_sample)]
            effect = ifn_value - control_value
            donor_effects.append(effect)
            gene_effect_rows.append(
                {
                    "donor_id": donor,
                    "gene_symbol": gene,
                    "ifn_sample": ifn_sample,
                    "control_sample": control_sample,
                    "ifn_median_log2p1_expression": ifn_value,
                    "control_median_log2p1_expression": control_value,
                    "paired_log2p1_effect": effect,
                    "positive": effect > 0,
                }
            )
        donor_rows.append(
            {
                "donor_id": donor,
                "genes": len(donor_effects),
                "mean_paired_log2p1_effect": float(np.mean(donor_effects)),
                "median_paired_log2p1_effect": float(np.median(donor_effects)),
                "positive_genes": sum(value > 0 for value in donor_effects),
                "positive_gene_fraction": float(np.mean(np.asarray(donor_effects) > 0)),
                "program_direction": "positive" if np.mean(donor_effects) > 0 else "nonpositive",
                "inferential_p_value": "not_calculated_n_equals_2",
            }
        )

    with (resource_dir / "05_MSIGDB_M5911_GENE_SET.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        msigdb_genes = {row["gene_symbol"] for row in csv.DictReader(handle)}
    gsea_rows: list[dict[str, Any]] = []
    for contrast, relative_path in CONFIRMATORY.items():
        symbols, statistics, _ = load_ranked_statistics(root / relative_path)
        result = run_preranked_gsea(
            symbols,
            statistics,
            msigdb_genes,
            args.permutations,
            stable_seed(args.seed, contrast),
        )
        gsea_rows.append({"contrast": contrast, **result})
    q_values = bh_adjust([row["permutation_p_value"] for row in gsea_rows])
    for row, q_value in zip(gsea_rows, q_values, strict=True):
        row["q_value_descriptive_three_contrasts"] = float(q_value)

    write_csv(
        output_dir / "16_GSE23307_LOG2P1_GENE_SAMPLE_EXPRESSION.csv",
        sample_gene_rows,
        list(sample_gene_rows[0]),
    )
    write_csv(
        output_dir / "17_GSE23307_LOG2P1_PAIRED_GENE_EFFECTS.csv",
        gene_effect_rows,
        list(gene_effect_rows[0]),
    )
    write_csv(
        output_dir / "18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv",
        donor_rows,
        list(donor_rows[0]),
    )
    write_csv(
        output_dir / "19_MSIGDB_M5911_PRERANKED_GSEA.csv",
        gsea_rows,
        list(gsea_rows[0]),
    )

    checks = {
        "gse23307_two_donors_positive": len(donor_rows) == 2
        and all(row["mean_paired_log2p1_effect"] > 0 for row in donor_rows),
        "gse23307_no_powered_p_value": all(
            row["inferential_p_value"] == "not_calculated_n_equals_2" for row in donor_rows
        ),
        "msigdb_positive_all_three": len(gsea_rows) == 3
        and all(row["normalized_enrichment_score"] > 0 for row in gsea_rows),
        "msigdb_no_material_contradiction": all(
            row["enrichment_score"] > 0 for row in gsea_rows
        ),
        "frozen_mapping_and_method_used": True,
    }
    decision = (
        "PASS_GATE_C6B4A_SCALE_REPAIRED_ORTHOGONAL_EVIDENCE_PENDING_INDEPENDENT_AUDIT"
        if all(checks.values())
        else "HOLD_GATE_C6B4_ORTHOGONAL_CONTRADICTION_REVIEW_REQUIRED"
    )
    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "gse23307_expression_effects_inspected": True,
        "msigdb_enrichment_effects_inspected": True,
        "permutations_per_contrast": args.permutations,
        "gse23307_scale": {
            "submitted_scale": "quantile_normalized_linear_intensity",
            "selected_raw_minimum": min(selected_raw_values),
            "selected_raw_maximum": max(selected_raw_values),
            "transform": "log2(x + 1) before probe aggregation"
        },
        "checks": checks,
        "gse23307_donor_results": donor_rows,
        "msigdb_results": gsea_rows,
        "next_if_pass": "perform independent Gate C6B audit and conditionally render Figure 5",
        "next_if_hold": "retain regulator results as qualified observational support without central framing",
    }
    write_text(output_dir / "20_GATE_C6B4A_ORTHOGONAL_DECISION.json", json.dumps(payload, indent=2))
    report = [
        "# Gate C6B-4A scale-repaired orthogonal response decision",
        "",
        f"## `{decision}`",
        "",
        "## GSE23307 paired B-cell response",
        "",
    ]
    report.extend(
        f"- {row['donor_id']}: mean paired log2(x+1) effect={row['mean_paired_log2p1_effect']:.4f}; "
        f"positive genes={row['positive_genes']}/{row['genes']}; no powered P value"
        for row in donor_rows
    )
    report.extend(["", "## MSigDB M5911", ""])
    report.extend(
        f"- {row['contrast']}: NES={row['normalized_enrichment_score']:.3f}, "
        f"permutation P={row['permutation_p_value']:.3g}, "
        f"descriptive q={row['q_value_descriptive_three_contrasts']:.3g}"
        for row in gsea_rows
    )
    report.extend(["", "## Checks", ""])
    report.extend(f"- [{'PASS' if passed else 'FAIL'}] {name}" for name, passed in checks.items())
    report.extend(
        [
            "",
            "## Consequence",
            "",
            payload["next_if_pass"] if decision.startswith("PASS") else payload["next_if_hold"],
        ]
    )
    write_text(output_dir / "20_GATE_C6B4A_ORTHOGONAL_DECISION.md", "\n".join(report))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
