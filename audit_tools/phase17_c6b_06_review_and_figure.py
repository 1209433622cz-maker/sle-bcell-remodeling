#!/usr/bin/env python3
"""Independently audit Gate C6B and render the conditional Figure 5."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from math import fsum, sqrt
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

from phase17_c6b_03_fit_frozen_regulators import (
    CONFIRMATORY,
    CORE,
    IFN_FAMILY,
    REGULATORS,
    build_predictor,
    load_network,
    load_ranked_statistics,
)


CONTRAST_LABELS = {
    "gse174188_primary": "GSE174188 discovery",
    "gse174188_internal_nonoverlap": "GSE174188 donor-nonoverlap",
    "gse135779_childhood": "GSE135779 childhood",
}
REGULATOR_COLORS = {
    "STAT1": "#2166AC",
    "STAT2": "#1B9E77",
    "IRF7": "#7B3294",
    "IRF9": "#D95F02",
    "E2F1": "#5C5C5C",
    "FOXM1": "#8C8C8C",
    "MYC": "#2F2F2F",
    "MYBL2": "#B0B0B0",
}


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def independent_centered_ulm(y: np.ndarray, x: np.ndarray) -> dict[str, float]:
    n = len(x)
    x_mean = fsum(float(value) for value in x) / n
    y_mean = fsum(float(value) for value in y) / n
    sxx = fsum((float(value) - x_mean) ** 2 for value in x)
    sxy = fsum(
        (float(xv) - x_mean) * (float(yv) - y_mean)
        for xv, yv in zip(x, y, strict=True)
    )
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    rss = fsum(
        (float(yv) - intercept - slope * float(xv)) ** 2
        for xv, yv in zip(x, y, strict=True)
    )
    df = n - 2
    se = sqrt((rss / df) / sxx)
    statistic = slope / se
    critical = float(stats.t.ppf(0.975, df=df))
    return {
        "slope": slope,
        "se": se,
        "t_statistic": statistic,
        "p_value": float(2 * stats.t.sf(abs(statistic), df=df)),
        "ci_low": slope - critical * se,
        "ci_high": slope + critical * se,
    }


def style_axis(axis: plt.Axes) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(labelsize=6.5, width=0.6, length=3)
    axis.spines["left"].set_linewidth(0.7)
    axis.spines["bottom"].set_linewidth(0.7)


def panel_letter(axis: plt.Axes, letter: str, x: float = -0.14, y: float = 1.07) -> None:
    axis.text(
        x,
        y,
        letter,
        transform=axis.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
        ha="left",
    )


def draw_design_panel(axis: plt.Axes) -> None:
    axis.set_axis_off()
    panel_letter(axis, "A", x=-0.06, y=1.03)
    columns = [
        (0.155, "Frozen evidence\n3 SLE contrasts", "#2166AC"),
        (0.495, "Signed QL rank\nCollecTRI ULM\n8 regulators", "#1B9E77"),
        (0.835, "Orthogonal support\nM5911 + IFN-beta\nB-cell perturbation", "#D95F02"),
    ]
    for x, label, color in columns:
        axis.plot(
            [x - 0.115, x + 0.115],
            [0.77, 0.77],
            transform=axis.transAxes,
            color=color,
            linewidth=4.5,
            solid_capstyle="butt",
        )
        axis.text(
            x,
            0.48,
            label,
            transform=axis.transAxes,
            ha="center",
            va="center",
            fontsize=7,
            linespacing=1.35,
        )
    for start, end in [((0.28, 0.50), (0.35, 0.50)), ((0.62, 0.50), (0.69, 0.50))]:
        axis.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            transform=axis.transAxes,
            color="#333333",
            linewidth=0.8,
            marker=">",
            markevery=[1],
            markersize=4,
        )
    axis.text(
        0.5,
        0.05,
        "Global BH across 24 confirmatory tests; target deletion and 100 x 80% resampling",
        transform=axis.transAxes,
        ha="center",
        va="bottom",
        fontsize=6.5,
        color="#333333",
    )


def draw_forest(
    axis: plt.Axes,
    rows: list[dict[str, str]],
    regulators: list[str],
    letter: str,
    title: str,
) -> None:
    selected = [row for row in rows if row["regulator"] in regulators]
    selected.sort(
        key=lambda row: (
            list(CONFIRMATORY).index(row["contrast"]),
            regulators.index(row["regulator"]),
        )
    )
    y_values = np.arange(len(selected))[::-1]
    for y_value, row in zip(y_values, selected, strict=True):
        estimate = float(row["slope"])
        low = float(row["ci_low"])
        high = float(row["ci_high"])
        color = REGULATOR_COLORS[row["regulator"]]
        axis.errorbar(
            estimate,
            y_value,
            xerr=[[estimate - low], [high - estimate]],
            fmt="o",
            markersize=3.4,
            markeredgewidth=0,
            color=color,
            ecolor=color,
            elinewidth=0.9,
            capsize=1.8,
            zorder=3,
        )
        if float(row["q_value_global24"]) < 0.05:
            axis.text(high + 0.08, y_value, "*", fontsize=7, va="center", ha="left")
    axis.axvline(0, color="#555555", linewidth=0.7, linestyle="--", zorder=1)
    labels = []
    for row in selected:
        contrast_short = {
            "gse174188_primary": "Disc.",
            "gse174188_internal_nonoverlap": "Nonoverlap",
            "gse135779_childhood": "Child.",
        }[row["contrast"]]
        labels.append(f"{contrast_short}  {row['regulator']}")
    for separator in (3.5, 7.5):
        axis.axhline(separator, color="#D9D9D9", linewidth=0.6, zorder=0)
    axis.set_yticks(y_values, labels)
    axis.set_xlabel("Regulator activity slope (95% CI)", fontsize=7)
    axis.set_title(title, fontsize=8, loc="left", pad=6)
    axis.set_ylim(-0.8, len(selected) - 0.2)
    style_axis(axis)
    panel_letter(axis, letter)


def draw_orthogonal_panel(
    gsea_axis: plt.Axes,
    donor_axis: plt.Axes,
    gsea_rows: list[dict[str, str]],
    donor_rows: list[dict[str, str]],
) -> None:
    panel_letter(gsea_axis, "D", x=-0.24, y=1.14)
    gsea_labels = ["Discovery", "Nonoverlap", "Childhood"]
    gsea_values = [float(row["normalized_enrichment_score"]) for row in gsea_rows]
    gsea_axis.bar(
        np.arange(3),
        gsea_values,
        width=0.64,
        color=["#2166AC", "#1B9E77", "#D95F02"],
        edgecolor="none",
    )
    gsea_axis.set_xticks(np.arange(3), gsea_labels, rotation=35, ha="right")
    gsea_axis.set_ylabel("M5911 NES", fontsize=7)
    gsea_axis.set_title("IFN response enrichment", fontsize=7.5, loc="left", pad=5)
    gsea_axis.set_ylim(0, max(gsea_values) * 1.22)
    style_axis(gsea_axis)

    donor_values = [float(row["mean_paired_log2p1_effect"]) for row in donor_rows]
    donor_axis.bar(
        np.arange(2),
        donor_values,
        width=0.58,
        color=["#C44E52", "#8172B3"],
        edgecolor="none",
    )
    donor_axis.set_xticks(np.arange(2), [row["donor_id"] for row in donor_rows])
    donor_axis.set_ylabel("Mean paired Δlog2(x+1)", fontsize=7)
    donor_axis.set_title("IFN-beta perturbation", fontsize=7.5, loc="left", pad=5)
    donor_axis.set_ylim(0, max(donor_values) * 1.22)
    for index, row in enumerate(donor_rows):
        donor_axis.text(
            index,
            float(row["mean_paired_log2p1_effect"]) + 0.12,
            f"{row['positive_genes']}/12",
            ha="center",
            va="bottom",
            fontsize=6,
        )
    style_axis(donor_axis)


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    resource_dir = args.resource_dir if args.resource_dir.is_absolute() else root / args.resource_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir

    regulator_rows = read_csv(output_dir / "01_CONFIRMATORY_REGULATOR_RESULTS.csv")
    influence_rows = read_csv(output_dir / "02_IFN_TARGET_INFLUENCE_SUMMARY.csv")
    loo_rows = read_csv(output_dir / "03_IFN_TARGET_LEAVE_ONE_OUT.csv")
    resample_rows = read_csv(output_dir / "04_IFN_TARGET_RESAMPLING.csv")
    sensitivity_rows = read_csv(output_dir / "05_SUPPORTIVE_SENSITIVITY_REGULATOR_RESULTS.csv")
    input_audit_rows = read_csv(output_dir / "06_INPUT_AUDIT.csv")
    donor_rows = read_csv(output_dir / "18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv")
    gene_effect_rows = read_csv(output_dir / "17_GSE23307_LOG2P1_PAIRED_GENE_EFFECTS.csv")
    gsea_rows = read_csv(output_dir / "19_MSIGDB_M5911_PRERANKED_GSEA.csv")
    c6b2 = json.loads((output_dir / "07_GATE_C6B2_DECISION.json").read_text(encoding="utf-8"))
    c6b4 = json.loads((output_dir / "20_GATE_C6B4A_ORTHOGONAL_DECISION.json").read_text(encoding="utf-8"))

    network = load_network(
        resource_dir / "resources/collectri_human_omnipath_20260815.tsv.gz"
    )
    recorded = {(row["contrast"], row["regulator"]): row for row in regulator_rows}
    reproduction_deltas: list[float] = []
    for contrast, relative_path in CONFIRMATORY.items():
        symbols, y, _ = load_ranked_statistics(root / relative_path)
        for regulator in REGULATORS:
            fit = independent_centered_ulm(
                y,
                build_predictor(symbols, network[regulator]),
            )
            row = recorded[(contrast, regulator)]
            reproduction_deltas.extend(
                abs(fit[field] - float(row[field]))
                for field in ("slope", "se", "t_statistic", "p_value", "ci_low", "ci_high")
            )
    max_ulm_delta = max(reproduction_deltas)
    independent_q = multipletests(
        [float(row["p_value"]) for row in regulator_rows], method="fdr_bh"
    )[1]
    max_bh_delta = max(
        abs(q_value - float(row["q_value_global24"]))
        for q_value, row in zip(independent_q, regulator_rows, strict=True)
    )

    external_manifest = read_csv(resource_dir / "07_EXTERNAL_RESOURCE_MANIFEST.csv")
    external_hash_pass = all(
        (root / row["project_relative_path"]).is_file()
        and (root / row["project_relative_path"]).stat().st_size == int(row["size_bytes"])
        and sha256_file(root / row["project_relative_path"]) == row["sha256"]
        for row in external_manifest
    )
    input_hash_pass = all(
        sha256_file(root / row["input_path"]) == row["input_sha256"]
        for row in input_audit_rows
    )

    expected_loo = sum(int(row["matched_targets"]) for row in influence_rows)
    loo_groups = Counter((row["contrast"], row["regulator"]) for row in loo_rows)
    influence_count_pass = len(loo_rows) == expected_loo and all(
        loo_groups[(row["contrast"], row["regulator"])] == int(row["matched_targets"])
        for row in influence_rows
    )
    resample_groups = Counter((row["contrast"], row["regulator"]) for row in resample_rows)
    resample_count_pass = len(resample_rows) == 1200 and all(
        resample_groups[(contrast, regulator)] == 100
        for contrast in CONFIRMATORY
        for regulator in IFN_FAMILY
    )
    core_influence_pass = all(
        row["loo_all_same_direction"].lower() == "true"
        and float(row["resample_positive_fraction"]) >= 0.95
        for row in influence_rows
        if row["regulator"] in CORE
    )

    effects_by_donor: dict[str, list[float]] = defaultdict(list)
    for row in gene_effect_rows:
        effects_by_donor[row["donor_id"]].append(float(row["paired_log2p1_effect"]))
    donor_reproduction_delta = max(
        abs(
            fsum(effects_by_donor[row["donor_id"]]) / len(effects_by_donor[row["donor_id"]])
            - float(row["mean_paired_log2p1_effect"])
        )
        for row in donor_rows
    )
    superseded_files = json.loads(
        (output_dir / "15_C6B3A_SCALE_REPAIR_FREEZE.json").read_text(encoding="utf-8")
    )["superseded_outputs"]
    superseded_preserved = all((output_dir / name).is_file() for name in superseded_files)

    checks = {
        "c6b1_qualification_pass": json.loads(
            (resource_dir / "11_C6B1_QUALIFICATION_DECISION.json").read_text(encoding="utf-8")
        )["decision"]
        == "PASS_GATE_C6B1_NO_EFFECT_QUALIFICATION",
        "confirmatory_exact_24_unique": len(regulator_rows) == 24 and len(recorded) == 24,
        "independent_ulm_reproduction": max_ulm_delta <= 1e-10,
        "independent_global_bh_reproduction": max_bh_delta <= 1e-12,
        "c6b2_all_frozen_checks_pass": c6b2["decision"].startswith("PASS")
        and all(c6b2["checks"].values()),
        "influence_row_counts_reconcile": influence_count_pass,
        "resampling_row_counts_reconcile": resample_count_pass,
        "core_influence_pass": core_influence_pass,
        "sensitivity_exact_72": len(sensitivity_rows) == 72,
        "gse23307_gene_effect_exact_24": len(gene_effect_rows) == 24,
        "gse23307_donor_summary_reproduced": donor_reproduction_delta <= 1e-12,
        "scale_repaired_orthogonal_pass": c6b4["decision"].startswith("PASS")
        and all(c6b4["checks"].values()),
        "msigdb_exact_three_positive": len(gsea_rows) == 3
        and all(float(row["normalized_enrichment_score"]) > 0 for row in gsea_rows),
        "external_resource_hashes": external_hash_pass,
        "all_gene_input_hashes": input_hash_pass,
        "superseded_scale_outputs_preserved": superseded_preserved,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    final_decision = (
        "PASS_GATE_C6B_UPPER_Q1_REGULATORY_FRAMING_AUTHORIZED_NONCAUSAL"
        if all(checks.values())
        else "HOLD_GATE_C6B_FINAL_AUDIT_REPAIR_REQUIRED"
    )

    source_rows: list[dict[str, Any]] = []
    for row in regulator_rows:
        source_rows.append(
            {
                "panel": "B" if row["regulator"] in IFN_FAMILY else "C",
                "series": "regulator_activity",
                "category": f"{row['contrast']}|{row['regulator']}",
                "estimate": row["slope"],
                "ci_low": row["ci_low"],
                "ci_high": row["ci_high"],
                "p_value": row["p_value"],
                "q_value": row["q_value_global24"],
                "n_or_targets": row["matched_targets"],
            }
        )
    for row in gsea_rows:
        source_rows.append(
            {
                "panel": "D",
                "series": "MSigDB_M5911_NES",
                "category": row["contrast"],
                "estimate": row["normalized_enrichment_score"],
                "ci_low": "",
                "ci_high": "",
                "p_value": row["permutation_p_value"],
                "q_value": row["q_value_descriptive_three_contrasts"],
                "n_or_targets": row["matched_genes"],
            }
        )
    for row in donor_rows:
        source_rows.append(
            {
                "panel": "D",
                "series": "GSE23307_mean_paired_log2p1_effect",
                "category": row["donor_id"],
                "estimate": row["mean_paired_log2p1_effect"],
                "ci_low": "",
                "ci_high": "",
                "p_value": "not_calculated_n_equals_2",
                "q_value": "",
                "n_or_targets": row["genes"],
            }
        )
    write_csv(
        output_dir / "21_FIGURE5_SOURCE_DATA.csv",
        source_rows,
        ["panel", "series", "category", "estimate", "ci_low", "ci_high", "p_value", "q_value", "n_or_targets"],
    )

    if final_decision.startswith("PASS"):
        plt.rcParams.update(
            {
                "font.family": "Arial",
                "font.size": 7,
                "axes.linewidth": 0.7,
                "pdf.fonttype": 42,
                "ps.fonttype": 42,
                "savefig.facecolor": "white",
            }
        )
        figure = plt.figure(figsize=(7.09, 6.9), constrained_layout=False)
        grid = figure.add_gridspec(
            2,
            2,
            height_ratios=[0.7, 1.45],
            left=0.13,
            right=0.98,
            bottom=0.08,
            top=0.96,
            wspace=0.42,
            hspace=0.42,
        )
        design_axis = figure.add_subplot(grid[0, 0])
        orthogonal_grid = grid[0, 1].subgridspec(1, 2, wspace=0.62)
        gsea_axis = figure.add_subplot(orthogonal_grid[0, 0])
        donor_axis = figure.add_subplot(orthogonal_grid[0, 1])
        ifn_axis = figure.add_subplot(grid[1, 0])
        control_axis = figure.add_subplot(grid[1, 1])
        draw_design_panel(design_axis)
        draw_orthogonal_panel(gsea_axis, donor_axis, gsea_rows, donor_rows)
        draw_forest(
            ifn_axis,
            regulator_rows,
            ["STAT1", "STAT2", "IRF7", "IRF9"],
            "B",
            "IFN-centred regulator activity",
        )
        draw_forest(
            control_axis,
            regulator_rows,
            ["E2F1", "FOXM1", "MYC", "MYBL2"],
            "C",
            "Prespecified proliferation controls",
        )
        figure.text(
            0.98,
            0.015,
            "* global 24-test BH q < 0.05",
            ha="right",
            va="bottom",
            fontsize=6,
            color="#444444",
        )
        figure.savefig(output_dir / "22_FIGURE5_REGULATORY_EVIDENCE.png", dpi=600)
        figure.savefig(output_dir / "22_FIGURE5_REGULATORY_EVIDENCE.pdf")
        plt.close(figure)

    caption = """# Figure 5 | Convergent observational evidence for an IFN-centred regulatory program in SLE conventional B cells.

**a,** Frozen analysis design. Three prespecified robust edgeR quasi-likelihood contrasts were ranked by sign(logFC) x sqrt(F), tested against eight signed CollecTRI regulons with a univariate linear model, and evaluated with one global Benjamini-Hochberg family of 24 tests. **b,** Activity slopes and 95% confidence intervals for the four prespecified IFN-family regulators. **c,** Corresponding estimates for four prespecified proliferation controls. Asterisks denote global 24-test q < 0.05. **d,** Orthogonal response evidence: weighted preranked enrichment of MSigDB M5911 HALLMARK_INTERFERON_ALPHA_RESPONSE (left; 10,000 gene-label permutations per contrast) and paired IFN-beta minus untreated 12-gene program effects in primary B cells from two healthy donors in GSE23307 (right; log2(x + 1) transformation before probe aggregation). Labels above GSE23307 bars show the number of positive genes among 12. No powered P value was calculated for the two-donor perturbation dataset. Regulator activities are observational and do not establish causal or uniquely upstream regulation.
"""
    write_text(output_dir / "23_FIGURE5_CAPTION.md", caption)

    audit_payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": final_decision,
        "checks": checks,
        "independent_reproduction": {
            "maximum_ulm_field_delta": float(max_ulm_delta),
            "maximum_global_bh_delta": float(max_bh_delta),
            "gse23307_donor_mean_delta": float(donor_reproduction_delta),
        },
        "claim_boundary": "convergent observational IFN-centred regulatory evidence; not causal and not a unique upstream stimulus",
        "authorized_figure": "22_FIGURE5_REGULATORY_EVIDENCE.pdf" if final_decision.startswith("PASS") else None,
        "next_stage": "Gate C7 manuscript and full-figure integration with claim-language reconciliation",
    }
    write_text(output_dir / "24_GATE_C6B_FINAL_AUDIT.json", json.dumps(audit_payload, indent=2))
    report = [
        "# Gate C6B final independent audit",
        "",
        f"## `{final_decision}`",
        "",
        "## Independent checks",
        "",
    ]
    report.extend(f"- [{'PASS' if passed else 'FAIL'}] {name}" for name, passed in checks.items())
    report.extend(
        [
            "",
            "## Numerical reproduction",
            "",
            f"- Maximum independently recomputed ULM field delta: `{max_ulm_delta:.3e}`.",
            f"- Maximum independent statsmodels BH delta: `{max_bh_delta:.3e}`.",
            f"- Maximum recomputed GSE23307 donor-mean delta: `{donor_reproduction_delta:.3e}`.",
            "",
            "## Scientific interpretation",
            "",
            "The data authorize an upper-Q1 observational framing in which the independently replicated IFN/ISG program is accompanied by concordant STAT1/STAT2-centred regulatory activity and orthogonal interferon-response evidence. They do not establish causality, a unique upstream ligand or a new B-cell subtype.",
            "",
            "## Next stage",
            "",
            "Gate C7: regenerate the complete figure set around the frozen result hierarchy, reconcile every manuscript claim against the gate decisions, and prepare source-data/caption/method packages before journal selection.",
        ]
    )
    write_text(output_dir / "24_GATE_C6B_FINAL_AUDIT.md", "\n".join(report))

    manifest_rows = []
    for path in sorted(output_dir.iterdir(), key=lambda item: item.name):
        if not path.is_file() or path.name == "25_INTEGRITY_MANIFEST.csv":
            continue
        status = "superseded_audit_only" if path.name in superseded_files else "active"
        manifest_rows.append(
            {
                "file": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "status": status,
            }
        )
    write_csv(
        output_dir / "25_INTEGRITY_MANIFEST.csv",
        manifest_rows,
        ["file", "size_bytes", "sha256", "status"],
    )
    print(json.dumps(audit_payload, indent=2))


if __name__ == "__main__":
    main()
