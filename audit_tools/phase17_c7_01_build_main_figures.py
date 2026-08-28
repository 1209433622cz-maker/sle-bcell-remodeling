#!/usr/bin/env python3
"""Build the audited five-figure main-text package from frozen results."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import NullFormatter


COLORS = {
    "hc": "#4D4D4D",
    "sle": "#C43C39",
    "internal": "#2C6EAD",
    "external": "#009E73",
    "secondary": "#E69F00",
    "ifn": "#D55E00",
    "purple": "#7B6BA8",
    "neutral": "#8A8A8A",
    "light": "#C7CCD1",
    "dark": "#222222",
    "teal": "#238A8D",
}
PROGRAM_LABELS = {
    "NAIVE_TO_MEMORY_AXIS": "Naive-to-memory",
    "ATYPICAL_LOW_NAIVE_AXIS": "Atypical/low-naive",
    "APC_HLA": "APC/HLA",
    "IFN_ISG": "IFN/ISG",
    "PLATELET_AMBIENT_QC": "Platelet/ambient",
    "ASC_UPR_IDENTITY_QC": "ASC/UPR",
    "PAN_B_IDENTITY_QC": "Pan-B",
}
ASSERTIONS: list[dict[str, Any]] = []
OUTPUT_WIDTH_MM: float | None = None


def assert_equal(name: str, actual: Any, expected: Any) -> None:
    passed = actual == expected
    ASSERTIONS.append(
        {"check": name, "actual": actual, "expected": expected, "pass": passed}
    )
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def assert_true(name: str, condition: bool, detail: str) -> None:
    passed = bool(condition)
    ASSERTIONS.append(
        {"check": name, "actual": detail, "expected": "true", "pass": passed}
    )
    if not passed:
        raise AssertionError(f"{name}: {detail}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("phase17_v7/gateC7/20260820_manuscript_figure_integration"),
    )
    parser.add_argument(
        "--proliferation-specificity-comparators",
        action="store_true",
        help="Use the Gate C8B specificity-comparator wording for Figure 5c.",
    )
    parser.add_argument(
        "--parallel-evidence-branches",
        action="store_true",
        help="Draw Figure 5a as parallel regulatory and response-evidence branches.",
    )
    parser.add_argument(
        "--graphical-validation-workflow",
        action="store_true",
        help="Draw the Figure 1a validation sequence as aligned nodes and arrows.",
    )
    parser.add_argument(
        "--reader-facing-source-labels",
        action="store_true",
        help="Use sequential reader-facing omission labels in Figure 4d.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() and path.parent.name == "05_gene_results":
        root = Path(__file__).resolve().parents[1]
        accession = "GSE135779" if "gateC5B" in path.parts else "GSE174188"
        member = f"gene_level_results/{accession}/{path.name}"
        archive = root / "04_submission/journal_submission/portal_upload_required/Full_Statistical_Results.zip"
        with zipfile.ZipFile(archive) as package:
            manifest = pd.read_csv(package.open("MANIFEST_SHA256.csv"))
            expected = manifest.loc[manifest["relative_path"].eq(member)]
            if len(expected) != 1:
                raise RuntimeError(f"No unique archived result: {member}")
            payload = package.read(member)
            if hashlib.sha256(payload).hexdigest().upper() != expected.iloc[0]["sha256"]:
                raise RuntimeError(f"Archived result checksum mismatch: {member}")
        return pd.read_csv(io.BytesIO(gzip.decompress(payload)))
    return pd.read_csv(path)


def write_source(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, lineterminator="\n")


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def set_output_width_mm(width_mm: float | None) -> None:
    global OUTPUT_WIDTH_MM
    if width_mm is not None and width_mm <= 0:
        raise ValueError("Figure width must be positive")
    OUTPUT_WIDTH_MM = width_mm


def style_axis(axis: plt.Axes, grid: bool = False) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_linewidth(0.7)
    axis.spines["bottom"].set_linewidth(0.7)
    axis.tick_params(width=0.6, length=3)
    if grid:
        axis.grid(axis="y", color="#E5E5E5", linewidth=0.5, zorder=0)


def panel_label(axis: plt.Axes, label: str, x: float = -0.16, y: float = 1.08) -> None:
    axis.text(
        x,
        y,
        label,
        transform=axis.transAxes,
        fontsize=8,
        fontweight="bold",
        va="top",
        ha="left",
    )


def save_figure(figure: plt.Figure, figure_dir: Path, stem: str) -> None:
    if OUTPUT_WIDTH_MM is not None:
        current_width, current_height = figure.get_size_inches()
        target_width = OUTPUT_WIDTH_MM / 25.4
        figure.set_size_inches(
            target_width,
            current_height * target_width / current_width,
            forward=True,
        )
    from publication_style_contract import apply_publication_style
    apply_publication_style(figure, OUTPUT_WIDTH_MM or 170.0)
    visible_text = [
        artist
        for artist in figure.findobj(matplotlib.text.Text)
        if artist.get_visible() and artist.get_text().strip()
    ]
    minimum_font = min(float(artist.get_fontsize()) for artist in visible_text)
    assert_true(
        f"{stem}.minimum_visible_font_pt",
        minimum_font >= 5.0,
        f"{minimum_font:.2f} pt",
    )
    figure.savefig(figure_dir / f"{stem}.pdf")
    figure.savefig(figure_dir / f"{stem}.png", dpi=600)
    plt.close(figure)


def forest(
    axis: plt.Axes,
    rows: pd.DataFrame,
    label_col: str,
    estimate_col: str,
    low_col: str,
    high_col: str,
    color_col: str | None = None,
    reference: float = 0.0,
    log_scale: bool = False,
) -> None:
    y_values = np.arange(len(rows))[::-1]
    for y_value, (_, row) in zip(y_values, rows.iterrows(), strict=True):
        estimate = float(row[estimate_col])
        low = float(row[low_col])
        high = float(row[high_col])
        color = row[color_col] if color_col else COLORS["internal"]
        axis.errorbar(
            estimate,
            y_value,
            xerr=[[estimate - low], [high - estimate]],
            fmt="o",
            color=color,
            ecolor=color,
            markersize=3.7,
            elinewidth=0.9,
            capsize=1.8,
            markeredgewidth=0,
            zorder=3,
        )
    axis.axvline(reference, color="#666666", linewidth=0.7, linestyle="--", zorder=1)
    axis.set_yticks(y_values, rows[label_col].tolist())
    axis.set_ylim(-0.8, len(rows) - 0.2)
    if log_scale:
        axis.set_xscale("log")
    style_axis(axis)


def build_figure1(
    root: Path,
    figure_dir: Path,
    source_dir: Path,
    *,
    graphical_validation_workflow: bool = False,
    publication_source_data: bool = False,
    explicit_threshold_semantics: bool = False,
    nature_evidence_hierarchy: bool = False,
) -> None:
    c2b3 = read_json(
        root
        / "phase17_v7/gateC2B3/20260813_full_neutral_state_freeze/16_GATE_C2B3_ADVISOR_REVIEW.json"
    )
    c2b4_dir = root / "phase17_v7/gateC2B4/20260815_two_level_state_repair"
    c2b4 = read_json(c2b4_dir / "06_GATE_C2B4_ADVISOR_DECISION.json")
    c3 = read_json(
        root / "phase17_v7/gateC3/20260815_metadata_design/15_GATE_C3_METADATA_AUDIT.json"
    )
    policy = read_csv(c2b4_dir / "02_reconstructed_policy_summary.csv")
    replicate = read_csv(c2b4_dir / "01_reconstructed_policy_metrics.csv")
    replicate = replicate.loc[
        replicate["policy"].eq("two_compartment_asc_vs_conventional")
    ].copy()
    states = read_csv(c2b4_dir / "04_two_compartment_state_summary.csv")
    state_names = {"0": "B_CONV", "3": "B_ASC"}
    states["state_label"] = states["reference_state"].astype(str).map(state_names)
    assert_equal("Figure1.panel_b.policy_count", len(policy), 4)
    assert_equal("Figure1.panel_c.resampling_replicates", len(replicate), 20)
    assert_equal("Figure1.panel_d.frozen_state_count", len(states), 2)
    assert_equal("Figure1.hard_qc_cells", int(c3["cells"]), 150402)
    assert_equal("Figure1.donors", int(c3["donors"]), 259)
    assert_equal("Figure1.samples", int(c3["samples"]), 271)
    assert_equal("Figure1.sample_cohort_strata", int(c3["sample_cohort_strata"]), 332)
    assert_equal("Figure1.libraries", int(c3["libraries"]), 88)

    source_rows: list[dict[str, Any]] = [
        {
            "panel": "a",
            "series": "study_design",
            "category": "GSE174188 source B lineage",
            "estimate": 152981,
            "secondary_value": 30172,
            "detail": "cells before hard QC; genes",
        },
        {
            "panel": "a",
            "series": "study_design",
            "category": "GSE174188 hard-QC retained",
            "estimate": c3["cells"],
            "secondary_value": c3["donors"],
            "detail": "cells; donors",
        },
        {
            "panel": "a",
            "series": "study_design",
            "category": "metadata hierarchy",
            "estimate": c3["samples"],
            "secondary_value": c3["sample_cohort_strata"],
            "detail": f"samples; sample-cohort strata; {c3['libraries']} libraries",
        },
    ]
    if not publication_source_data:
        source_rows.extend(
            [
                {
                    "panel": "a",
                    "series": "gate_decision",
                    "category": "fine-state identity",
                    "estimate": np.nan,
                    "secondary_value": np.nan,
                    "detail": c2b3["decision"],
                },
                {
                    "panel": "a",
                    "series": "gate_decision",
                    "category": "two-compartment identity",
                    "estimate": np.nan,
                    "secondary_value": np.nan,
                    "detail": c2b4["decision"],
                },
            ]
        )
    policy_labels = {
        "five_state": "5-state",
        "four_state_platelet_overlay_merged": "4-state",
        "three_state_identity_core": "3-state",
        "two_compartment_asc_vs_conventional": "2-compartment",
    }
    for _, row in policy.iterrows():
        source_rows.extend(
            [
                {
                    "panel": "b",
                    "series": "median mapped ARI",
                    "category": policy_labels[row["policy"]],
                    "estimate": row["median_mapped_ari"],
                    "secondary_value": row["median_mapping_agreement"],
                    "detail": "20 disease-blind resamples",
                },
                {
                    "panel": "b",
                    "series": "minimum mapped ARI",
                    "category": policy_labels[row["policy"]],
                    "estimate": row["minimum_mapped_ari"],
                    "secondary_value": row["minimum_mapping_agreement"],
                    "detail": "20 disease-blind resamples",
                },
            ]
        )
    for _, row in replicate.iterrows():
        source_rows.extend(
            [
                {
                    "panel": "c",
                    "series": "mapped ARI",
                    "category": int(row["replicate"]),
                    "estimate": row["mapped_adjusted_rand_index"],
                    "secondary_value": np.nan,
                    "detail": "2-compartment",
                },
                {
                    "panel": "c",
                    "series": "mapping agreement",
                    "category": int(row["replicate"]),
                    "estimate": row["mapping_agreement"],
                    "secondary_value": np.nan,
                    "detail": "2-compartment",
                },
            ]
        )
    for _, row in states.iterrows():
        source_rows.extend(
            [
                {
                    "panel": "d",
                    "series": "median Jaccard",
                    "category": row["state_label"],
                    "estimate": row["median_jaccard"],
                    "secondary_value": row["median_recall"],
                    "detail": "state stability",
                },
                {
                    "panel": "d",
                    "series": "minimum Jaccard",
                    "category": row["state_label"],
                    "estimate": row["minimum_jaccard"],
                    "secondary_value": row["minimum_recall"],
                    "detail": "state stability",
                },
            ]
        )
    write_source(source_dir / "Figure1_source_data.csv", pd.DataFrame(source_rows))

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.45), constrained_layout=True)
    axis = axes[0, 0]
    axis.set_axis_off()
    panel_label(axis, "a", x=-0.06, y=1.03)
    if nature_evidence_hierarchy:
        tier_style = {
            "transform": axis.transAxes,
            "ha": "left",
            "va": "center",
            "fontsize": 5.2,
            "fontweight": "bold",
            "color": "#333333",
        }
        node_style = {
            "transform": axis.transAxes,
            "ha": "center",
            "va": "center",
            "fontsize": 5.4,
            "linespacing": 1.15,
        }
        axis.text(0.00, 0.86, "Discovery", **tier_style)
        discovery_nodes = [
            (0.20, "B-lineage\ncells", COLORS["internal"]),
            (0.43, "Hard QC", COLORS["dark"]),
            (0.72, "Frozen-representation\nB_CONV / B_ASC scaffold", COLORS["teal"]),
        ]
        for x, label, color in discovery_nodes:
            axis.text(
                x,
                0.86,
                label,
                **node_style,
                bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
            )
        for start, end in ((0.29, 0.35), (0.51, 0.57)):
            axis.annotate(
                "",
                xy=(end, 0.86),
                xytext=(start, 0.86),
                xycoords=axis.transAxes,
                arrowprops={"arrowstyle": "-|>", "lw": 0.65, "color": COLORS["dark"]},
            )
        for x, label in (
            (0.62, "B_ASC\ncomposition"),
            (0.86, "B_CONV pseudobulk\n+ frozen programs"),
        ):
            axis.text(
                x,
                0.63,
                label,
                **node_style,
                bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": COLORS["sle"], "linewidth": 0.75},
            )
            axis.annotate(
                "",
                xy=(x, 0.70),
                xytext=(0.72, 0.79),
                xycoords=axis.transAxes,
                arrowprops={"arrowstyle": "-|>", "lw": 0.6, "color": COLORS["dark"]},
            )
        axis.text(
            0.50,
            0.52,
            "GSE174188: 259 donors | 271 samples | 332 sample-cohort strata | 88 libraries",
            transform=axis.transAxes,
            ha="center",
            va="center",
            fontsize=5.0,
            color="#444444",
        )

        axis.text(0.00, 0.36, "Validation /\nreplication", linespacing=1.05, **tier_style)
        for x, label, color in (
            (0.38, "GSE174188\ninternal validation", COLORS["internal"]),
            (0.76, "GSE135779\nindependent replication", COLORS["external"]),
        ):
            axis.text(
                x,
                0.34,
                label,
                **node_style,
                bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
            )

        axis.text(0.00, 0.17, "Interpretation", **tier_style)
        for x, label in (
            (0.31, "same-data\nregulator robustness"),
            (0.58, "M5911 response-set\nconcordance"),
            (0.84, "GSE23307\nperturbational context"),
        ):
            axis.text(
                x,
                0.10,
                label,
                **node_style,
                bbox={"boxstyle": "round,pad=0.20", "facecolor": "#F7F7F7", "edgecolor": "#777777", "linewidth": 0.65},
            )
        axis.set_title("Study design and evidence hierarchy", loc="left", pad=4)
    else:
        nodes = [
            (0.02, "GSE174188\nB-lineage cells", COLORS["internal"]),
            (0.36, "Disease-blind\nB_CONV / B_ASC", COLORS["teal"]),
            (0.70, "Composition +\nB_CONV pseudobulk", COLORS["sle"]),
        ]
        for x, text, color in nodes:
            axis.text(
                x,
                0.67,
                text,
                transform=axis.transAxes,
                fontsize=7,
                ha="left",
                va="center",
                linespacing=1.35,
                bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
            )
        for start, end in ((0.27, 0.35), (0.60, 0.68)):
            axis.annotate(
                "",
                xy=(end, 0.67),
                xytext=(start, 0.67),
                xycoords=axis.transAxes,
                arrowprops={"arrowstyle": "-|>", "lw": 0.8, "color": COLORS["dark"]},
            )
        if graphical_validation_workflow:
            validation_nodes = [
                (0.12, "Frozen\nprograms", COLORS["internal"]),
                (0.50, "Independent\nvalidation", COLORS["external"]),
                (0.88, "Regulatory +\nresponse evidence", COLORS["ifn"]),
            ]
            for x, text, color in validation_nodes:
                axis.text(
                    x,
                    0.29,
                    text,
                    transform=axis.transAxes,
                    ha="center",
                    va="center",
                    fontsize=5.8,
                    linespacing=1.2,
                    bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
                )
            for start, end in ((0.26, 0.37), (0.64, 0.75)):
                axis.annotate(
                    "",
                    xy=(end, 0.29),
                    xytext=(start, 0.29),
                    xycoords=axis.transAxes,
                    arrowprops={"arrowstyle": "-|>", "lw": 0.7, "color": COLORS["dark"]},
                )
        else:
            axis.text(
                0.5,
                0.29,
                "Frozen signatures  ->  GSE135779 validation  ->  regulatory convergence",
                transform=axis.transAxes,
                ha="center",
                va="center",
                fontsize=6.2,
                fontweight="bold",
            )
        axis.text(
            0.5,
            0.10,
            "259 donors | 271 samples | 332 sample-cohort strata | 88 libraries",
            transform=axis.transAxes,
            ha="center",
            va="center",
            fontsize=6.3,
            color="#444444",
        )
        axis.set_title("Disease-blind discovery and frozen validation", loc="left", pad=4)

    axis = axes[0, 1]
    x = np.arange(len(policy))
    if explicit_threshold_semantics:
        axis.hlines(0.90, 2.62, 3.38, color="#666666", lw=0.7, ls="--")
        axis.text(
            3.34,
            0.884,
            "2-compartment minimum-ARI criterion",
            fontsize=5.0,
            ha="right",
            va="top",
            color="#555555",
        )
    else:
        axis.axhline(0.90, color="#666666", lw=0.7, ls="--")
    for x_value, (_, row) in zip(x, policy.iterrows(), strict=True):
        axis.plot(
            [float(x_value), float(x_value)],
            [float(row["minimum_mapped_ari"]), float(row["median_mapped_ari"])],
            color=COLORS["light"],
            lw=1.0,
            zorder=1,
        )
    axis.scatter(x, policy["median_mapped_ari"], marker="o", color=COLORS["internal"], s=14, label="Median ARI", zorder=3)
    axis.scatter(x, policy["minimum_mapped_ari"], marker="D", color=COLORS["secondary"], s=12, label="Minimum ARI", zorder=3)
    axis.set_xticks(x, [policy_labels[value] for value in policy["policy"]], rotation=25, ha="right")
    axis.set_ylabel("Mapped adjusted Rand index")
    axis.set_ylim(0.28, 1.03)
    axis.legend(frameon=False, fontsize=6, loc="lower left")
    axis.set_title("Frozen-representation policy selection", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "b")

    axis = axes[1, 0]
    axis.plot(replicate["replicate"], replicate["mapped_adjusted_rand_index"], "o-", ms=3.0, lw=0.8, color=COLORS["internal"], label="Mapped ARI")
    axis.plot(replicate["replicate"], replicate["mapping_agreement"], "s-", ms=2.8, lw=0.8, color=COLORS["external"], label="Agreement")
    axis.axhline(0.99, color="#666666", lw=0.7, ls="--")
    if explicit_threshold_semantics:
        axis.text(
            20.2,
            0.99015,
            "minimum mapped-ARI criterion",
            fontsize=5.0,
            ha="right",
            va="bottom",
            color="#555555",
        )
    axis.set_xlabel("Disease-blind resampling replicate")
    axis.set_ylabel("Two-compartment stability")
    axis.set_ylim(0.985, 1.0008)
    axis.legend(frameon=False, fontsize=6, loc="lower left")
    axis.set_title("Frozen-representation broad partition", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "c")

    axis = axes[1, 1]
    y = np.arange(len(states))[::-1]
    for index, (_, row) in enumerate(states.iterrows()):
        y_value = y[index]
        axis.plot([row["minimum_jaccard"], row["median_jaccard"]], [y_value, y_value], color=COLORS["teal"], lw=1.1)
        axis.plot(row["minimum_jaccard"], y_value, "D", color=COLORS["secondary"], ms=3.2)
        axis.plot(row["median_jaccard"], y_value, "o", color=COLORS["teal"], ms=3.7)
    axis.axvline(0.95, color="#666666", lw=0.7, ls="--")
    if explicit_threshold_semantics:
        axis.text(
            0.9508,
            0.62,
            "state-median Jaccard criterion",
            fontsize=5.0,
            ha="left",
            va="center",
            color="#555555",
        )
    axis.set_yticks(y, states["state_label"])
    axis.set_xlim(0.94, 1.001)
    axis.set_xlabel("State Jaccard (minimum to median)")
    axis.text(
        0.9408,
        0.34,
        "B_ASC markers: DERL3, JCHAIN, MZB1,\nTNFRSF17, XBP1; sample support = 1.00",
        fontsize=5.8,
        va="center",
        ha="left",
        color="#444444",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.8},
    )
    axis.set_title("Frozen-representation scope gate", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "d")
    save_figure(figure, figure_dir, "Figure1_disease_blind_identity_scope")


def build_figure2(root: Path, figure_dir: Path, source_dir: Path) -> None:
    c3_dir = root / "phase17_v7/gateC3/20260815_metadata_design"
    c3a_dir = root / "phase17_v7/gateC3A/20260815_frozen_abundance"
    samples = read_csv(c3_dir / "11_primary_model_matrix.csv")
    contrasts = read_csv(c3a_dir / "02_base_and_nonoverlap_contrasts.csv")
    predictions = read_csv(c3a_dir / "03_adjusted_predictions.csv")
    sensitivity = read_csv(c3a_dir / "04_mandatory_sensitivity_contrasts.csv")
    loo = read_csv(c3a_dir / "06_primary_leave_one_out.csv")
    group_counts = samples["disease_state"].value_counts().to_dict()
    assert_equal("Figure2.panel_a.control_raw_points", int(group_counts.get("na", 0)), 43)
    assert_equal("Figure2.panel_a.managed_sle_raw_points", int(group_counts.get("managed", 0)), 47)
    assert_equal("Figure2.panel_a.total_raw_points", len(samples), 90)
    assert_equal(
        "Figure2.panel_a.adjusted_predictions",
        len(predictions.loc[predictions["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")]),
        2,
    )
    assert_equal("Figure2.panel_b.frozen_contrasts", len(contrasts), 5)
    assert_equal(
        "Figure2.panel_c.mandatory_sensitivities",
        len(sensitivity.loc[sensitivity["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")]),
        4,
    )
    assert_equal("Figure2.panel_d.leave_one_out_deletions", len(loo), 90)

    source_rows: list[pd.DataFrame] = []
    sample_source = samples[
        ["sample_uuid", "disease_state", "total_cells", "asc_cells", "asc_fraction"]
    ].copy()
    sample_source.insert(0, "panel", "a")
    sample_source.insert(1, "series", "observed sample ASC fraction")
    source_rows.append(sample_source)
    prediction_source = predictions.loc[
        predictions["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")
    ].copy()
    prediction_source.insert(0, "panel", "a")
    prediction_source.insert(1, "series", "adjusted ASC fraction")
    source_rows.append(prediction_source)
    contrast_source = contrasts.copy()
    contrast_source.insert(0, "panel", "b")
    contrast_source.insert(1, "series", "frozen contrast")
    source_rows.append(contrast_source)
    sensitivity_source = sensitivity.loc[
        sensitivity["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")
    ].copy()
    sensitivity_source.insert(0, "panel", "c")
    sensitivity_source.insert(1, "series", "primary mandatory sensitivity")
    source_rows.append(sensitivity_source)
    loo_source = loo.copy()
    loo_source.insert(0, "panel", "d")
    loo_source.insert(1, "series", "primary leave-one-sample-out")
    source_rows.append(loo_source)
    write_source(source_dir / "Figure2_source_data.csv", pd.concat(source_rows, ignore_index=True, sort=False))

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.6), constrained_layout=True)
    axis = axes[0, 0]
    groups = [
        ("na", "reference", 0, COLORS["hc"]),
        ("managed", "exposed", 1, COLORS["sle"]),
    ]
    plotted_raw_points = 0
    for disease_state, prediction_group, x_center, color in groups:
        subset = samples.loc[samples["disease_state"].eq(disease_state)].sort_values("asc_fraction")
        plotted_raw_points += len(subset)
        jitter = np.linspace(-0.17, 0.17, len(subset))
        axis.scatter(
            x_center + jitter,
            subset["asc_fraction"] * 100,
            s=10,
            color=color,
            alpha=0.65,
            linewidths=0,
            zorder=2,
        )
        prediction = predictions.loc[
            predictions["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")
            & predictions["group"].eq(prediction_group)
        ].iloc[0]
        axis.errorbar(
            x_center,
            prediction["adjusted_fraction"] * 100,
            yerr=[
                [prediction["adjusted_fraction"] * 100 - prediction["ci_low"] * 100],
                [prediction["ci_high"] * 100 - prediction["adjusted_fraction"] * 100],
            ],
            fmt="D",
            color="black",
            ms=4,
            capsize=2,
            lw=1.0,
            zorder=4,
        )
    assert_equal("Figure2.panel_a.raw_points_sent_to_scatter", plotted_raw_points, 90)
    axis.set_xticks([0, 1], ["Control\n(n=43)", "Managed SLE\n(n=47)"])
    axis.set_ylabel("B_ASC fraction per sample-cohort (%)")
    axis.set_title("Observed strata and adjusted means", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "a")

    labels = {
        ("C3A_PRIMARY_C4_MANAGED_VS_NORMAL", "frozen_base50"): "Primary C4",
        ("C3A_VALIDATION_C2_EUROPEAN_FEMALE", "frozen_base50"): "Internal C2",
        ("C3A_VALIDATION_C2_EUROPEAN_FEMALE", "exclude_primary_sample_or_donor_overlap"): "Internal C2 nonoverlap",
        ("C3A_SECONDARY_C3_FLARE_VS_NORMAL", "frozen_base50"): "Flare C3 (secondary)",
        ("C3A_SECONDARY_C3_FLARE_VS_NORMAL", "exclude_primary_sample_or_donor_overlap"): "Flare C3 nonoverlap",
    }
    plot_rows = contrasts.copy()
    plot_rows["label"] = [labels[(row.analysis_id, row.variant)] for row in plot_rows.itertuples()]
    plot_rows["color"] = [
        COLORS["secondary"] if "Flare" in label else COLORS["internal"]
        for label in plot_rows["label"]
    ]
    forest(axes[0, 1], plot_rows, "label", "odds_ratio", "ci_low", "ci_high", "color", reference=1.0, log_scale=True)
    axes[0, 1].set_xticks([0.5, 1.0, 2.0, 4.0], ["0.5", "1", "2", "4"])
    axes[0, 1].xaxis.set_minor_formatter(NullFormatter())
    axes[0, 1].set_xlabel("Conditional odds ratio for B_ASC abundance")
    axes[0, 1].set_title("No primary B_ASC enrichment", loc="left", pad=4)
    axes[0, 1].text(0.98, 0.04, "Flare q=0.0845", transform=axes[0, 1].transAxes, ha="right", va="bottom", fontsize=6, color=COLORS["secondary"])
    panel_label(axes[0, 1], "b")

    primary = contrasts.loc[
        contrasts["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")
        & contrasts["variant"].eq("frozen_base50")
    ].copy()
    primary = primary.assign(label="Frozen >=50", color=COLORS["sle"])
    sensitivity_primary = sensitivity.loc[
        sensitivity["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")
    ].copy()
    sensitivity_labels = {
        "minimum_cells_20": "Minimum 20 cells",
        "minimum_cells_100": "Minimum 100 cells",
        "exclude_explicit_non_b_ct_cov": "Exclude explicit non-B",
        "exclude_residual_doublet_auto_call": "Exclude residual doublets",
    }
    sensitivity_primary["label"] = sensitivity_primary["variant"].map(sensitivity_labels)
    sensitivity_primary["color"] = COLORS["teal"]
    sensitivity_plot = pd.concat([primary, sensitivity_primary], ignore_index=True)
    forest(axes[1, 0], sensitivity_plot, "label", "odds_ratio", "ci_low", "ci_high", "color", reference=1.0, log_scale=True)
    axes[1, 0].set_xticks([0.6, 0.8, 1.0, 1.2], ["0.6", "0.8", "1", "1.2"])
    axes[1, 0].xaxis.set_minor_formatter(NullFormatter())
    axes[1, 0].set_xlabel("Primary conditional odds ratio")
    axes[1, 0].set_title("Mandatory sensitivity analyses", loc="left", pad=4)
    panel_label(axes[1, 0], "c")

    axis = axes[1, 1]
    x = np.arange(1, len(loo) + 1)
    axis.scatter(x, loo["odds_ratio"], s=9, color=COLORS["teal"], alpha=0.8, linewidths=0)
    axis.axhline(1.0, color="#666666", lw=0.7, ls="--")
    axis.axhline(float(primary.iloc[0]["odds_ratio"]), color=COLORS["sle"], lw=0.9, label="Full estimate")
    axis.set_xlabel("Omitted primary sample")
    axis.set_ylabel("Conditional odds ratio")
    axis.set_ylim(min(0.75, loo["odds_ratio"].min() - 0.02), max(1.03, loo["odds_ratio"].max() + 0.02))
    axis.legend(frameon=False, fontsize=6, loc="lower right")
    axis.set_title("All 90 deletions retain direction", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "d")
    save_figure(figure, figure_dir, "Figure2_sample_level_composition")


def build_figure3(root: Path, figure_dir: Path, source_dir: Path) -> None:
    c4_dir = root / "phase17_v7/gateC4B/20260815_edger_transcription"
    programs = read_csv(c4_dir / "07_PROGRAM_RESULTS.csv")
    model = read_csv(c4_dir / "05_MODEL_SUMMARY.csv")
    cross_ifn = read_csv(
        root
        / "phase17_v7/gateC5B/20260815_gse135779_external_validation/16_CROSS_DATASET_IFN_GENE_EFFECTS.csv"
    )
    confirmatory_ids = ["NAIVE_TO_MEMORY_AXIS", "ATYPICAL_LOW_NAIVE_AXIS", "APC_HLA", "IFN_ISG"]
    primary_programs = programs.loc[
        programs["analysis_name"].eq("primary_base")
        & programs["program_id"].isin(confirmatory_ids)
    ].copy()
    primary_programs["label"] = primary_programs["program_id"].map(PROGRAM_LABELS)
    primary_programs["color"] = [
        COLORS["ifn"] if value == "IFN_ISG" else COLORS["internal"]
        for value in primary_programs["program_id"]
    ]
    analysis_order = [
        "primary_base",
        "primary_min20",
        "primary_min100",
        "primary_residual_risk_negative",
        "validation_full",
        "validation_nonoverlap",
        "flare_full",
    ]
    analysis_labels = {
        "primary_base": "Primary C4 (n=89)",
        "primary_min20": "Primary >=20 (n=94)",
        "primary_min100": "Primary >=100 (n=87)",
        "primary_residual_risk_negative": "Residual-risk negative (n=89)",
        "validation_full": "Internal C2 (n=64)",
        "validation_nonoverlap": "Internal nonoverlap (n=54)",
        "flare_full": "Flare C3, secondary (n=34)",
    }
    ifn = programs.loc[
        programs["program_id"].eq("IFN_ISG")
        & programs["analysis_name"].isin(analysis_order)
    ].copy()
    ifn["order"] = ifn["analysis_name"].map({value: index for index, value in enumerate(analysis_order)})
    ifn = ifn.sort_values("order")
    ifn["label"] = ifn["analysis_name"].map(analysis_labels)
    ifn["color"] = [
        COLORS["secondary"] if value == "flare_full" else COLORS["ifn"]
        for value in ifn["analysis_name"]
    ]
    control_ids = ["IFN_ISG", "PLATELET_AMBIENT_QC", "ASC_UPR_IDENTITY_QC", "PAN_B_IDENTITY_QC"]
    controls = programs.loc[
        programs["analysis_name"].isin(["primary_base", "validation_nonoverlap"])
        & programs["program_id"].isin(control_ids)
    ].copy()
    primary_tested = cross_ifn["gse174188_primary_tested"].astype(str).str.lower().eq("true")
    nonoverlap_tested = cross_ifn["gse174188_nonoverlap_tested"].astype(str).str.lower().eq("true")
    assert_equal("Figure3.panel_a.frozen_programs", len(primary_programs), 4)
    assert_equal("Figure3.panel_b.ifn_analyses", len(ifn), 7)
    assert_equal("Figure3.panel_c.frozen_ifn_genes", len(cross_ifn), 12)
    assert_equal("Figure3.panel_c.primary_gene_level_tested", int(primary_tested.sum()), 10)
    assert_equal("Figure3.panel_c.nonoverlap_gene_level_tested", int(nonoverlap_tested.sum()), 11)
    assert_equal(
        "Figure3.panel_c.primary_filtered_genes",
        sorted(cross_ifn.loc[~primary_tested, "gene_symbol"].tolist()),
        ["IFIT1", "IFIT2"],
    )
    assert_equal(
        "Figure3.panel_c.nonoverlap_filtered_genes",
        sorted(cross_ifn.loc[~nonoverlap_tested, "gene_symbol"].tolist()),
        ["IFIT1"],
    )
    assert_equal("Figure3.panel_d.program_control_estimates", len(controls), 8)

    source_rows: list[pd.DataFrame] = []
    a_source = primary_programs.copy()
    a_source.insert(0, "panel", "a")
    source_rows.append(a_source)
    b_source = ifn.copy()
    b_source.insert(0, "panel", "b")
    source_rows.append(b_source)
    c_source = cross_ifn[
        ["gene_symbol", "gse174188_primary_logFC", "gse174188_primary_tested", "gse174188_nonoverlap_logFC", "gse174188_nonoverlap_tested"]
    ].copy()
    c_source.insert(0, "panel", "c")
    source_rows.append(c_source)
    d_source = controls.copy()
    d_source.insert(0, "panel", "d")
    source_rows.append(d_source)
    model_source = model.copy()
    model_source.insert(0, "panel", "support")
    source_rows.append(model_source)
    write_source(source_dir / "Figure3_source_data.csv", pd.concat(source_rows, ignore_index=True, sort=False))

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.75), constrained_layout=True)
    forest(axes[0, 0], primary_programs, "label", "effect", "ci_low", "ci_high", "color")
    axes[0, 0].set_xlabel("Adjusted program-score difference")
    axes[0, 0].set_title("Four frozen programs in discovery", loc="left", pad=4)
    axes[0, 0].text(0.98, 0.03, "BH across four programs", transform=axes[0, 0].transAxes, ha="right", fontsize=6)
    panel_label(axes[0, 0], "a")

    forest(axes[0, 1], ifn, "label", "effect", "ci_low", "ci_high", "color")
    axes[0, 1].set_xlabel("Adjusted IFN/ISG score difference")
    axes[0, 1].set_title("IFN/ISG robustness and internal replication", loc="left", pad=4)
    panel_label(axes[0, 1], "b")

    axis = axes[1, 0]
    genes = cross_ifn["gene_symbol"].tolist()
    gene_labels = []
    for row in cross_ifn.itertuples():
        primary_ok = str(row.gse174188_primary_tested).lower() == "true"
        nonoverlap_ok = str(row.gse174188_nonoverlap_tested).lower() == "true"
        suffix = "†" if not primary_ok and not nonoverlap_ok else "‡" if not primary_ok else ""
        gene_labels.append(f"{row.gene_symbol}{suffix}")
    y = np.arange(len(genes))[::-1]
    for prefix, label, color, offset in [
        ("gse174188_primary", "Primary C4", COLORS["internal"], 0.10),
        ("gse174188_nonoverlap", "Internal nonoverlap", COLORS["ifn"], -0.10),
    ]:
        tested = cross_ifn[f"{prefix}_tested"].astype(str).str.lower().eq("true")
        axis.scatter(
            cross_ifn.loc[tested, f"{prefix}_logFC"],
            y[tested.to_numpy()] + offset,
            s=13,
            color=color,
            linewidths=0,
            label=label,
            zorder=3,
        )
    axis.axvline(0, color="#666666", lw=0.7, ls="--")
    axis.set_yticks(y, gene_labels)
    axis.set_xlabel("Gene-level log2 fold change")
    axis.legend(frameon=False, fontsize=6, loc="lower right")
    axis.set_title("Frozen IFN positive-arm genes", loc="left", pad=10)
    axis.text(
        0.0,
        1.01,
        "† untested in both contrasts; ‡ untested in primary",
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=5.2,
        color="#444444",
    )
    style_axis(axis)
    panel_label(axis, "c")

    axis = axes[1, 1]
    control_order = control_ids
    y_base = np.arange(len(control_order))[::-1]
    for analysis, label, color, offset in [
        ("primary_base", "Primary C4", COLORS["internal"], 0.11),
        ("validation_nonoverlap", "Internal nonoverlap", COLORS["ifn"], -0.11),
    ]:
        subset = controls.loc[controls["analysis_name"].eq(analysis)].set_index("program_id").loc[control_order]
        for index, (_, row) in enumerate(subset.iterrows()):
            y_value = y_base[index] + offset
            axis.errorbar(
                row["effect"],
                y_value,
                xerr=[[row["effect"] - row["ci_low"]], [row["ci_high"] - row["effect"]]],
                fmt="o",
                ms=3.3,
                lw=0.8,
                capsize=1.6,
                color=color,
            )
    axis.axvline(0, color="#666666", lw=0.7, ls="--")
    axis.set_yticks(y_base, [PROGRAM_LABELS[value] for value in control_order])
    axis.set_xlabel("Adjusted program-score difference")
    axis.legend(
        handles=[
            Line2D([0], [0], marker="o", color=COLORS["internal"], lw=0, label="Primary C4", markersize=4),
            Line2D([0], [0], marker="o", color=COLORS["ifn"], lw=0, label="Internal nonoverlap", markersize=4),
        ],
        frameon=False,
        fontsize=6,
        loc="upper left",
    )
    axis.set_title("Technical controls and pan-B sensitivity", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "d")
    save_figure(figure, figure_dir, "Figure3_gse174188_bconv_transcription")


def load_tested_gene_table(path: Path, symbol_field: str) -> pd.DataFrame:
    table = read_csv(path)
    tested = table["tested_filterByExpr"].astype(str).str.strip().str.lower().eq("true")
    result = table.loc[tested, ["ensembl_id", symbol_field, "logFC"]].copy()
    result = result.rename(columns={symbol_field: "gene_symbol"})
    result["gene_symbol"] = result["gene_symbol"].fillna("").astype(str).str.strip().str.upper()
    result["logFC"] = result["logFC"].astype(float)
    return result.reset_index(drop=True)


def build_figure4(
    root: Path,
    figure_dir: Path,
    source_dir: Path,
    *,
    reader_facing_source_labels: bool = False,
) -> None:
    c4_dir = root / "phase17_v7/gateC4B/20260815_edger_transcription"
    c5_dir = root / "phase17_v7/gateC5B/20260815_gse135779_external_validation"
    programs = read_csv(c5_dir / "07_PROGRAM_RESULTS.csv")
    cross_program = read_csv(c5_dir / "16_CROSS_DATASET_IFN_PROGRAM_EFFECTS.csv")
    cross_ifn = read_csv(c5_dir / "16_CROSS_DATASET_IFN_GENE_EFFECTS.csv")
    donor_loo = read_csv(c5_dir / "10_PRIMARY_PROGRAM_DONOR_LOO.csv")
    primary_samples = read_csv(c5_dir / "02_matrix_exports/childhood_min50_samples.csv")
    source_loo = read_csv(c5_dir / "12_SOURCE_LABEL_LOO_PROGRAM_RESULTS.csv")
    external_order = ["childhood_min50", "combined_min50", "adult_min50", "combined_min20", "combined_min100"]
    external_labels = {
        "childhood_min50": "Childhood >=50 (11 HC, 32 SLE)",
        "combined_min50": "Combined >=50 (16 HC, 38 SLE)",
        "adult_min50": "Adult >=50 (5 HC, 6 SLE)",
        "combined_min20": "Combined >=20 (16 HC, 40 SLE)",
        "combined_min100": "Combined >=100 (16 HC, 35 SLE)",
    }
    external = programs.loc[
        programs["program_id"].eq("IFN_ISG")
        & programs["analysis_name"].isin(external_order)
    ].copy()
    external["order"] = external["analysis_name"].map({value: index for index, value in enumerate(external_order)})
    external = external.sort_values("order")
    external["label"] = external["analysis_name"].map(external_labels)
    external["color"] = [
        COLORS["neutral"] if value == "adult_min50" else COLORS["external"]
        for value in external["analysis_name"]
    ]
    cross_order = ["primary_base", "validation_full", "validation_nonoverlap", "childhood_min50", "combined_min50", "adult_min50"]
    cross_labels = {
        "primary_base": "GSE174188 discovery",
        "validation_full": "GSE174188 internal",
        "validation_nonoverlap": "GSE174188 nonoverlap",
        "childhood_min50": "GSE135779 childhood",
        "combined_min50": "GSE135779 combined",
        "adult_min50": "GSE135779 adult",
    }
    cross_program["order"] = cross_program["analysis_name"].map({value: index for index, value in enumerate(cross_order)})
    cross_program = cross_program.sort_values("order")
    cross_program["label"] = cross_program["analysis_name"].map(cross_labels)
    cross_program["color"] = [
        COLORS["neutral"] if value == "adult_min50" else COLORS["external"] if dataset == "GSE135779" else COLORS["internal"]
        for value, dataset in zip(cross_program["analysis_name"], cross_program["dataset"], strict=True)
    ]

    discovery = load_tested_gene_table(
        c4_dir / "05_gene_results/primary_base_gene_results.csv.gz", "feature_name"
    ).rename(columns={"logFC": "gse174188_logFC", "gene_symbol": "gse174188_symbol"})
    external_genes = load_tested_gene_table(
        c5_dir / "05_gene_results/childhood_min50_gene_results.csv.gz", "gene_symbol_upper"
    ).rename(columns={"logFC": "gse135779_logFC", "gene_symbol": "gse135779_symbol"})
    merged = discovery.merge(external_genes, on="ensembl_id", how="inner")
    merged["gene_symbol"] = merged["gse174188_symbol"].where(
        merged["gse174188_symbol"].ne(""), merged["gse135779_symbol"]
    )
    rho = float(merged[["gse174188_logFC", "gse135779_logFC"]].corr(method="spearman").iloc[0, 1])
    ifn_genes = set(cross_ifn["gene_symbol"])
    merged["is_frozen_ifn_gene"] = merged["gene_symbol"].isin(ifn_genes)
    highlighted = merged.loc[merged["is_frozen_ifn_gene"]].copy()

    childhood = external.loc[external["analysis_name"].eq("childhood_min50")].iloc[0]
    donor_ifn = donor_loo.loc[donor_loo["program_id"].eq("IFN_ISG")].copy()
    source_ifn = source_loo.loc[
        source_loo["program_id"].eq("IFN_ISG")
        & source_loo["analysis_name"].str.startswith("childhood_min50_without_")
    ].copy()
    source_ifn = source_ifn.sort_values("omitted_source_label")
    assert_equal("Figure4.panel_a.external_ifn_analyses", len(external), 5)
    assert_equal("Figure4.panel_b.cross_dataset_analyses", len(cross_program), 6)
    assert_equal("Figure4.panel_c.shared_tested_genes", len(merged), 4410)
    assert_equal("Figure4.panel_c.frozen_ifn_genes", len(cross_ifn), 12)
    assert_equal("Figure4.panel_c.shared_testable_frozen_ifn_genes", len(highlighted), 10)
    assert_equal(
        "Figure4.panel_c.positive_frozen_ifn_genes",
        int((highlighted["gse174188_logFC"].gt(0) & highlighted["gse135779_logFC"].gt(0)).sum()),
        10,
    )
    assert_equal("Figure4.panel_d.donor_loo_summary_rows", len(donor_ifn), 1)
    assert_equal("Figure4.panel_d.eligible_donors", primary_samples["donor_name"].nunique(), 43)
    assert_equal("Figure4.panel_d.eligible_samples", primary_samples["sample_id"].nunique(), 43)
    assert_equal("Figure4.panel_d.source_label_omissions", len(source_ifn), 8)

    source_rows: list[pd.DataFrame] = []
    for panel, frame in (("a", external), ("b", cross_program), ("c", merged), ("d_donor", donor_ifn), ("d_source", source_ifn)):
        output = frame.copy()
        output.insert(0, "panel", panel)
        source_rows.append(output)
    write_source(source_dir / "Figure4_source_data.csv", pd.concat(source_rows, ignore_index=True, sort=False))

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.75), constrained_layout=True)
    forest(axes[0, 0], external, "label", "effect", "ci_low", "ci_high", "color")
    axes[0, 0].set_xlabel("Standardized IFN/ISG effect")
    axes[0, 0].set_title("Independent GSE135779 validation", loc="left", pad=4)
    axes[0, 0].text(0.98, 0.03, "Adult: directional only", transform=axes[0, 0].transAxes, ha="right", fontsize=6, color=COLORS["neutral"])
    panel_label(axes[0, 0], "a")

    forest(axes[0, 1], cross_program, "label", "effect", "ci_low", "ci_high", "color")
    axes[0, 1].set_xlabel("Standardized IFN/ISG effect")
    axes[0, 1].set_title("Discovery-to-external comparison", loc="left", pad=4)
    panel_label(axes[0, 1], "b")

    axis = axes[1, 0]
    non_ifn = merged.loc[~merged["is_frozen_ifn_gene"]]
    axis.scatter(non_ifn["gse174188_logFC"], non_ifn["gse135779_logFC"], s=4, color=COLORS["light"], alpha=0.38, linewidths=0, rasterized=True)
    axis.scatter(highlighted["gse174188_logFC"], highlighted["gse135779_logFC"], s=18, color=COLORS["sle"], edgecolor="white", linewidth=0.35, zorder=3)
    labels = highlighted.nlargest(3, "gse135779_logFC")
    for _, row in labels.iterrows():
        axis.annotate(row["gene_symbol"], (row["gse174188_logFC"], row["gse135779_logFC"]), xytext=(3, 2), textcoords="offset points", fontsize=5.5)
    axis.axhline(0, color="#777777", lw=0.6)
    axis.axvline(0, color="#777777", lw=0.6)
    axis.text(0.03, 0.96, f"Shared tested genes: {len(merged):,}\nSpearman rho={rho:.3f}\nIFN genes positive: 10/10", transform=axis.transAxes, va="top", fontsize=6.2)
    axis.set_xlabel("GSE174188 discovery log2 fold change")
    axis.set_ylabel("GSE135779 childhood log2 fold change")
    axis.set_title("Program-specific, not genome-wide, coherence", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "c")

    axis = axes[1, 1]
    omission_labels = (
        [f"Omit source label {index}" for index in range(1, len(source_ifn) + 1)]
        if reader_facing_source_labels
        else [f"Without {value}" for value in source_ifn["omitted_source_label"]]
    )
    labels_d = ["Full childhood", "43 donor deletions"] + omission_labels
    y = np.arange(len(labels_d))[::-1]
    axis.errorbar(childhood["effect"], y[0], xerr=[[childhood["effect"] - childhood["ci_low"]], [childhood["ci_high"] - childhood["effect"]]], fmt="o", color=COLORS["sle"], ms=3.7, lw=0.9, capsize=1.8)
    donor_min = float(donor_ifn.iloc[0]["loo_min_effect"])
    donor_max = float(donor_ifn.iloc[0]["loo_max_effect"])
    donor_mid = (donor_min + donor_max) / 2
    axis.errorbar(donor_mid, y[1], xerr=[[donor_mid - donor_min], [donor_max - donor_mid]], fmt="s", color=COLORS["purple"], ms=3.4, lw=1.0, capsize=1.8)
    for index, (_, row) in enumerate(source_ifn.iterrows(), start=2):
        axis.errorbar(row["effect"], y[index], xerr=[[row["effect"] - row["ci_low"]], [row["ci_high"] - row["effect"]]], fmt="o", color=COLORS["external"], ms=3.0, lw=0.75, capsize=1.4)
    axis.axvline(0, color="#777777", lw=0.6, ls="--")
    axis.axvline(childhood["effect"] * 0.5, color="#AAAAAA", lw=0.6, ls="--")
    axis.set_yticks(y, labels_d)
    axis.set_xlabel("Adjusted IFN/ISG score difference")
    axis.set_title("Donor and source-label influence", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "d")
    save_figure(figure, figure_dir, "Figure4_independent_ifn_replication")


def build_figure5(
    root: Path,
    figure_dir: Path,
    source_dir: Path,
    *,
    proliferation_specificity_comparators: bool = False,
    parallel_evidence_branches: bool = False,
    three_evidence_branches: bool = False,
) -> None:
    c6_dir = root / "phase17_v7/gateC6B/20260815_regulatory_evidence"
    regulators = read_csv(c6_dir / "01_CONFIRMATORY_REGULATOR_RESULTS.csv")
    donor = read_csv(c6_dir / "18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv")
    gsea = read_csv(c6_dir / "19_MSIGDB_M5911_PRERANKED_GSEA.csv")
    assert_equal("Figure5.confirmatory_regulator_tests", len(regulators), 24)
    assert_equal("Figure5.ifn_regulator_tests", int(regulators["family"].eq("IFN_confirmatory").sum()), 12)
    assert_equal("Figure5.proliferation_control_tests", int(regulators["family"].eq("proliferation_control").sum()), 12)
    assert_equal("Figure5.orthogonal_gsea_contrasts", len(gsea), 3)
    assert_equal("Figure5.gse23307_descriptive_donors", len(donor), 2)
    assert_equal("Figure5.panel_d.source_rows", len(gsea), 3)
    assert_equal("Figure5.panel_e.source_rows", len(donor), 2)
    assert_equal("Figure5.panel_e.donors_with_12_positive_genes", int(donor["positive_genes"].eq(12).sum()), 2)

    regulator_source = regulators.assign(
        panel=np.where(regulators["family"].eq("IFN_confirmatory"), "B", "C"),
        series="regulator_activity",
        category=regulators["contrast"].astype(str) + "|" + regulators["regulator"].astype(str),
        estimate=regulators["slope"],
        q_value=regulators["q_value_global24"],
        n_or_targets=regulators["matched_targets"],
    )[
        ["panel", "series", "category", "estimate", "ci_low", "ci_high", "p_value", "q_value", "n_or_targets"]
    ]
    gsea_source = pd.DataFrame(
        {
            "panel": "D",
            "series": "MSigDB_M5911_NES",
            "category": gsea["contrast"],
            "estimate": gsea["normalized_enrichment_score"],
            "ci_low": np.nan,
            "ci_high": np.nan,
            "p_value": gsea["permutation_p_value"],
            "q_value": gsea["q_value_descriptive_three_contrasts"],
            "n_or_targets": gsea["matched_genes"],
        }
    )
    donor_source = pd.DataFrame(
        {
            "panel": "E",
            "series": "GSE23307_mean_paired_log2p1_effect",
            "category": donor["donor_id"],
            "estimate": donor["mean_paired_log2p1_effect"],
            "ci_low": np.nan,
            "ci_high": np.nan,
            "p_value": donor["inferential_p_value"],
            "q_value": np.nan,
            "n_or_targets": donor["positive_genes"],
        }
    )
    source = pd.concat([regulator_source, gsea_source, donor_source], ignore_index=True)
    write_source(source_dir / "Figure5_source_data.csv", source)

    if three_evidence_branches:
        figure = plt.figure(figsize=(7.09, 6.8), constrained_layout=True)
        grid = figure.add_gridspec(
            3,
            4,
            height_ratios=[0.72, 0.62, 1.45],
            width_ratios=[1.0, 1.0, 0.9, 0.9],
        )
        design_axis = figure.add_subplot(grid[0, :])
        gsea_axis = figure.add_subplot(grid[1, 2])
        donor_axis = figure.add_subplot(grid[1, 3])
        ifn_axis = figure.add_subplot(grid[1:, 0:2])
        control_axis = figure.add_subplot(grid[2, 2:4])
    else:
        figure = plt.figure(figsize=(7.09, 6.2), constrained_layout=True)
        grid = figure.add_gridspec(
            2,
            4,
            height_ratios=[0.70, 1.65],
            width_ratios=[1.05, 1.05, 0.82, 0.82],
        )
        design_axis = figure.add_subplot(grid[0, 0:2])
        gsea_axis = figure.add_subplot(grid[0, 2])
        donor_axis = figure.add_subplot(grid[0, 3])
        ifn_axis = figure.add_subplot(grid[1, 0:2])
        control_axis = figure.add_subplot(grid[1, 2:4])

    design_axis.set_axis_off()
    panel_label(design_axis, "a", x=-0.09, y=1.08)
    if three_evidence_branches:
        design_axis.text(
            0.50,
            0.84,
            "Replicated B_CONV IFN/ISG remodeling",
            transform=design_axis.transAxes,
            ha="center",
            va="center",
            fontsize=6.5,
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.28", "facecolor": "white", "edgecolor": COLORS["ifn"], "linewidth": 0.9},
        )
        branch_x = (0.18, 0.50, 0.82)
        design_axis.plot([0.18, 0.82], [0.70, 0.70], transform=design_axis.transAxes, color="#666666", lw=0.65)
        design_axis.plot([0.50, 0.50], [0.76, 0.70], transform=design_axis.transAxes, color="#666666", lw=0.65)
        for x in branch_x:
            design_axis.plot([x, x], [0.70, 0.63], transform=design_axis.transAxes, color="#666666", lw=0.65)
        branch_titles = (
            "Same-data regulator\nrobustness",
            "Curated response-set\nconcordance",
            "Separate perturbational\ncontext",
        )
        branch_details = (
            "3 contrasts x 8 regulators\nglobal BH: 24 tests\ntarget deletion + 100 x 80%\nCAMERA + FRY sensitivity",
            "MSigDB M5911\n3 ranked disease contrasts\n10,000 permutations/contrast",
            "GSE23307 IFN-beta\nn=2 healthy donors\n12/12 positive genes per donor\ndescriptive; no inferential P",
        )
        for x, title, detail in zip(branch_x, branch_titles, branch_details, strict=True):
            design_axis.text(
                x,
                0.56,
                title,
                transform=design_axis.transAxes,
                ha="center",
                va="center",
                fontsize=5.8,
                fontweight="bold",
                linespacing=1.10,
            )
            design_axis.text(
                x,
                0.29,
                detail,
                transform=design_axis.transAxes,
                ha="center",
                va="center",
                fontsize=5.2,
                linespacing=1.12,
                color="#333333",
            )
        design_axis.text(
            0.50,
            0.015,
            "Interpretive support only - no causal regulator or unique upstream ligand established",
            transform=design_axis.transAxes,
            ha="center",
            va="bottom",
            fontsize=5.0,
            fontweight="bold",
            color="#555555",
        )
        design_axis.set_title(
            "Evidence architecture for the replicated\nIFN/ISG program",
            loc="left",
            pad=4,
        )
    elif parallel_evidence_branches:
        design_axis.text(
            0.50,
            0.80,
            "Replicated IFN/ISG remodeling",
            transform=design_axis.transAxes,
            ha="center",
            va="center",
            fontsize=7.2,
            bbox={"boxstyle": "round,pad=0.34", "facecolor": "white", "edgecolor": COLORS["ifn"], "linewidth": 1.0},
        )
        branches = [
            (0.24, "Regulatory branch\n3 contrasts x 8 regulators", COLORS["external"]),
            (0.76, "Response branch\nM5911 + IFN-beta", COLORS["internal"]),
        ]
        for x, text, color in branches:
            design_axis.text(
                x,
                0.40,
                text,
                transform=design_axis.transAxes,
                ha="center",
                va="center",
                fontsize=6.6,
                linespacing=1.25,
                bbox={"boxstyle": "round,pad=0.32", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
            )
            design_axis.annotate(
                "",
                xy=(x, 0.53),
                xytext=(0.50, 0.70),
                xycoords=design_axis.transAxes,
                arrowprops={"arrowstyle": "-|>", "lw": 0.8, "color": COLORS["dark"]},
            )
        design_axis.text(
            0.24,
            0.07,
            "Global BH: 24 tests\ntarget deletion + 100 x 80% resampling",
            transform=design_axis.transAxes,
            ha="center",
            va="center",
            fontsize=5.3,
            linespacing=1.2,
        )
        design_axis.text(
            0.76,
            0.07,
            "3 enrichment contrasts\nn=2 perturbation descriptive",
            transform=design_axis.transAxes,
            ha="center",
            va="center",
            fontsize=5.3,
            linespacing=1.2,
        )
        design_axis.set_title("Parallel evidence architecture", loc="left", pad=4)
    else:
        nodes = [
            (0.04, "3 frozen SLE\ncontrasts", COLORS["internal"]),
            (0.37, "8 frozen\nregulators", COLORS["external"]),
            (0.70, "Orthogonal\nIFN response", COLORS["ifn"]),
        ]
        for x, text, color in nodes:
            design_axis.text(x, 0.61, text, transform=design_axis.transAxes, ha="left", va="center", fontsize=7, bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": color, "linewidth": 1.0})
        for start, end in ((0.27, 0.36), (0.60, 0.69)):
            design_axis.annotate("", xy=(end, 0.61), xytext=(start, 0.61), xycoords=design_axis.transAxes, arrowprops={"arrowstyle": "-|>", "lw": 0.8, "color": COLORS["dark"]})
        design_axis.text(0.5, 0.18, "Global BH: 24 tests | target deletion | 100 x 80% resampling", transform=design_axis.transAxes, ha="center", fontsize=6.1)
        design_axis.set_title("Prespecified regulatory design", loc="left", pad=4)

    contrast_short = {
        "gse174188_primary": "Discovery",
        "gse174188_internal_nonoverlap": "Nonoverlap",
        "gse135779_childhood": "Childhood",
    }
    regulator_colors = {"STAT1": "#2C6EAD", "STAT2": "#009E73", "IRF7": "#7B6BA8", "IRF9": "#D55E00", "E2F1": "#666666", "FOXM1": "#999999", "MYC": "#333333", "MYBL2": "#BBBBBB"}

    def regulator_forest(axis: plt.Axes, names: list[str], label: str, title: str) -> None:
        selected = regulators.loc[regulators["regulator"].isin(names)].copy()
        selected["contrast_order"] = selected["contrast"].map({key: index for index, key in enumerate(contrast_short)})
        selected["regulator_order"] = selected["regulator"].map({name: index for index, name in enumerate(names)})
        selected = selected.sort_values(["contrast_order", "regulator_order"])
        role = {"STAT1": "core", "STAT2": "core", "IRF7": "extended", "IRF9": "extended"}
        selected["label"] = [
            f"{contrast_short[c]}  {r}{f' ({role[r]})' if r in role else ''}"
            for c, r in zip(selected["contrast"], selected["regulator"], strict=True)
        ]
        selected["color"] = selected["regulator"].map(regulator_colors)
        forest(axis, selected, "label", "slope", "ci_low", "ci_high", "color")
        for separator in (3.5, 7.5):
            axis.axhline(separator, color="#DDDDDD", lw=0.55, zorder=0)
        if names == ["STAT1", "STAT2", "IRF7", "IRF9"]:
            for separator in (1.5, 5.5, 9.5):
                axis.axhline(separator, color="#E8E8E8", lw=0.45, ls=":", zorder=0)
        y_values = np.arange(len(selected))[::-1]
        for y_value, (_, row) in zip(y_values, selected.iterrows(), strict=True):
            if row["q_value_global24"] < 0.05:
                axis.text(row["ci_high"] + 0.06, y_value, "*", fontsize=6.5, va="center")
        axis.set_xlabel("Regulator activity slope (95% CI)")
        axis.set_title(title, loc="left", pad=4)
        panel_label(axis, label)

    regulator_forest(ifn_axis, ["STAT1", "STAT2", "IRF7", "IRF9"], "b", "Core and extended IFN regulators")
    comparator_title = (
        "Prespecified proliferation\nspecificity comparators"
        if proliferation_specificity_comparators
        else "Prespecified proliferation controls"
    )
    regulator_forest(control_axis, ["E2F1", "FOXM1", "MYC", "MYBL2"], "c", comparator_title)

    gsea_labels = [
        {"Discovery": "Discovery", "Nonoverlap": "Nonoverlap", "Childhood": "Childhood"}[
            contrast_short[value]
        ]
        for value in gsea["contrast"]
    ]
    gsea_axis.bar(np.arange(3), gsea["normalized_enrichment_score"], width=0.62, color=[COLORS["internal"], COLORS["external"], COLORS["ifn"]], edgecolor="none")
    gsea_axis.set_xticks(np.arange(3), gsea_labels, rotation=35, ha="right")
    gsea_axis.set_ylabel("M5911 NES")
    gsea_axis.set_ylim(0, gsea["normalized_enrichment_score"].max() * 1.22)
    gsea_axis.set_title("IFN enrichment", loc="left", pad=4)
    style_axis(gsea_axis)
    panel_label(gsea_axis, "d", x=-0.20, y=1.10)

    donor_axis.bar(np.arange(2), donor["mean_paired_log2p1_effect"], width=0.58, color=["#CC6666", COLORS["purple"]], edgecolor="none")
    donor_axis.set_xticks(np.arange(2), donor["donor_id"])
    donor_axis.set_ylabel("Mean paired Δlog2(x+1)")
    donor_axis.set_ylim(0, donor["mean_paired_log2p1_effect"].max() * 1.25)
    donor_title = (
        "IFN-beta\nresponse"
        if three_evidence_branches
        else "IFN-beta\nresponse\n(n=2; descriptive)"
        if parallel_evidence_branches
        else "IFN-beta response\n(n=2; descriptive)"
    )
    donor_axis.set_title(donor_title, loc="left", pad=4, fontsize=6.5 if parallel_evidence_branches else None)
    for index, row in donor.iterrows():
        donor_axis.text(index, row["mean_paired_log2p1_effect"] + 0.10, f"{int(row['positive_genes'])}/12", ha="center", fontsize=6)
    style_axis(donor_axis)
    panel_label(donor_axis, "e", x=-0.20, y=1.10)
    control_axis.text(0.98, -0.19, "* global 24-test BH q<0.05", transform=control_axis.transAxes, ha="right", va="top", fontsize=5.8, color="#444444")
    save_figure(figure, figure_dir, "Figure5_regulatory_evidence")


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    figure_dir = output_dir / "figures"
    source_dir = output_dir / "source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    ASSERTIONS.clear()
    configure_style()
    build_figure1(
        root,
        figure_dir,
        source_dir,
        graphical_validation_workflow=args.graphical_validation_workflow,
    )
    build_figure2(root, figure_dir, source_dir)
    build_figure3(root, figure_dir, source_dir)
    build_figure4(
        root,
        figure_dir,
        source_dir,
        reader_facing_source_labels=args.reader_facing_source_labels,
    )
    build_figure5(
        root,
        figure_dir,
        source_dir,
        proliferation_specificity_comparators=args.proliferation_specificity_comparators,
        parallel_evidence_branches=args.parallel_evidence_branches,
    )
    gate_label = next(
        (part[4:].upper() for part in output_dir.parts if part.lower().startswith("gatec")),
        "C8R",
    )
    payload = {
        "created_at": "2026-08-21",
        "status": f"{gate_label}_MAIN_FIGURES_BUILT_WITH_ASSERTIONS",
        "figures": 5,
        "formats": ["PDF", "PNG_600_DPI"],
        "source_data_files": 5,
        "source_policy": "frozen Gate C2B4-C6B outputs only",
        "panel_data_assertions": len(ASSERTIONS),
        "panel_data_assertions_passed": all(item["pass"] for item in ASSERTIONS),
    }
    (output_dir / "02_PANEL_DATA_ASSERTIONS.json").write_text(
        json.dumps(
            {
                "created_at": "2026-08-21",
                "status": "PASS" if all(item["pass"] for item in ASSERTIONS) else "FAIL",
                "checks": ASSERTIONS,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "01_FIGURE_BUILD_STATUS.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
