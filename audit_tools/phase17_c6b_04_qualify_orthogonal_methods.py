#!/usr/bin/env python3
"""Freeze Gate C6B orthogonal mappings and methods without reading expression values."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from datetime import datetime
from pathlib import Path
from typing import Any


FROZEN_IFN_GENES = [
    "ISG15",
    "IFIT1",
    "IFIT2",
    "IFIT3",
    "MX1",
    "MX2",
    "OAS1",
    "OAS2",
    "IFI44L",
    "IFI6",
    "LY6E",
    "IRF7",
]


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
    return parser.parse_args()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def parse_probe_mapping(path: Path) -> list[dict[str, str]]:
    gene_set = set(FROZEN_IFN_GENES)
    rows: list[dict[str, str]] = []
    in_table = False
    header: list[str] | None = None
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            if line == "!platform_table_begin":
                in_table = True
                continue
            if line == "!platform_table_end":
                break
            if not in_table:
                continue
            fields = next(csv.reader([line], delimiter="\t", quotechar='"'))
            if header is None:
                header = fields
                if "ID" not in header or "Gene symbol" not in header:
                    raise ValueError("GPL6104 lacks ID or Gene symbol")
                continue
            record = dict(zip(header, fields, strict=False))
            symbols = sorted(
                {
                    value.strip().upper()
                    for value in record["Gene symbol"].split("///")
                    if value.strip()
                }
            )
            matches = sorted(gene_set & set(symbols))
            for gene in matches:
                rows.append(
                    {
                        "gene_symbol": gene,
                        "probe_id": record["ID"],
                        "platform_gene_symbol_raw": record["Gene symbol"],
                        "mapping_rule": "exact_uppercase_symbol_after_triple_slash_split",
                    }
                )
    rows.sort(key=lambda row: (FROZEN_IFN_GENES.index(row["gene_symbol"]), row["probe_id"]))
    return rows


def read_matrix_header_only(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            if line == "!series_matrix_table_begin":
                header = next(handle).rstrip("\r\n")
                return next(csv.reader([header], delimiter="\t", quotechar='"'))
    raise ValueError("GSE23307 matrix table header not found")


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    resource_dir = args.resource_dir if args.resource_dir.is_absolute() else root / args.resource_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    c6b2 = json.loads((output_dir / "07_GATE_C6B2_DECISION.json").read_text(encoding="utf-8"))
    if c6b2["decision"] != "PASS_GATE_C6B2_REGULATOR_LAYER_PENDING_ORTHOGONAL_REVIEW":
        raise RuntimeError("Gate C6B-2 did not authorize orthogonal analysis")
    freeze = json.loads((resource_dir / "08_EXTERNAL_RESOURCE_FREEZE.json").read_text(encoding="utf-8"))
    if freeze["expression_effects_inspected"]:
        raise RuntimeError("External resource freeze is not expression blind")

    mapping = parse_probe_mapping(resource_dir / "resources/GPL6104.annot.gz")
    mapped_genes = {row["gene_symbol"] for row in mapping}
    matrix_header = read_matrix_header_only(
        resource_dir / "resources/GSE23307_series_matrix.txt.gz"
    )
    pairing = list(
        csv.DictReader(
            (resource_dir / "06_GSE23307_SAMPLE_PAIRING.csv").open(
                "r", encoding="utf-8", newline=""
            )
        )
    )
    included_samples = [
        row["geo_accession"]
        for row in pairing
        if row["include_paired_bcell"].lower() == "true"
    ]
    header_samples = [value.strip('"') for value in matrix_header[1:]]
    checks = {
        "all_12_genes_mapped": mapped_genes == set(FROZEN_IFN_GENES),
        "mapping_has_21_probes": len(mapping) == 21,
        "matrix_header_has_six_samples": len(header_samples) == 6,
        "four_paired_bcell_samples_present": set(included_samples).issubset(header_samples)
        and len(included_samples) == 4,
        "external_freeze_expression_blind": True,
    }
    decision = (
        "PASS_GATE_C6B3_ORTHOGONAL_METHOD_FREEZE"
        if all(checks.values())
        else "HOLD_GATE_C6B3_ORTHOGONAL_MAPPING_REPAIR_REQUIRED"
    )
    write_csv(
        output_dir / "08_GSE23307_FROZEN_PROBE_MAPPING.csv",
        mapping,
        ["gene_symbol", "probe_id", "platform_gene_symbol_raw", "mapping_rule"],
    )
    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "gse23307_expression_effects_inspected": False,
        "msigdb_enrichment_effects_inspected": False,
        "gse23307_method": {
            "samples": included_samples,
            "genes": FROZEN_IFN_GENES,
            "mapped_probes": len(mapping),
            "probe_aggregation": "median submitted log2-normalized intensity within gene and sample",
            "gene_effect": "IFN-beta minus matched untreated control within donor",
            "program_effect": "arithmetic mean of 12 frozen gene effects within donor",
            "acceptance": "program effect positive in HI1 and HI2; no powered P value",
        },
        "msigdb_method": {
            "gene_set": "M5911 HALLMARK_INTERFERON_ALPHA_RESPONSE (97 genes)",
            "rank_metric": "frozen symbol-collapsed sign(logFC)*sqrt(F)",
            "algorithm": "weighted preranked GSEA, exponent 1",
            "null": "10000 deterministic gene-label permutations per confirmatory contrast",
            "multiplicity": "descriptive BH across three M5911 contrasts; outside global 24-test family",
        },
        "checks": checks,
        "next_if_pass": "calculate GSE23307 paired effects and M5911 ranked enrichment",
        "next_if_hold": "repair mappings without reading orthogonal effects",
    }
    write_text(output_dir / "09_C6B3_ORTHOGONAL_METHOD_FREEZE.json", json.dumps(payload, indent=2))
    report = [
        "# Gate C6B-3 orthogonal method freeze",
        "",
        f"## `{decision}`",
        "",
        "No GSE23307 expression values or M5911 enrichment effects were inspected.",
        "",
        "## Checks",
        "",
    ]
    report.extend(f"- [{'PASS' if passed else 'FAIL'}] {name}" for name, passed in checks.items())
    report.extend(
        [
            "",
            "## Frozen scoring",
            "",
            "- 12 genes, 21 probes, median probe aggregation within gene.",
            "- Paired IFN-beta minus control effects are averaged across the 12 genes per donor.",
            "- M5911 uses weighted preranked GSEA with 10,000 deterministic label permutations.",
            "- Both layers are supportive and cannot rescue a failed 24-test regulator family.",
        ]
    )
    write_text(output_dir / "09_C6B3_ORTHOGONAL_METHOD_FREEZE.md", "\n".join(report))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
