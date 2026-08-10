#!/usr/bin/env python3
"""Build v7 Figure 1 from frozen hierarchy and hard-QC tables only."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np
import pandas as pd


MM = 1 / 25.4
FIGURE_WIDTH_MM = 183
FIGURE_HEIGHT_MM = 152

BLACK = "#1A1A1A"
GRAY = "#6B6B6B"
LIGHT_GRAY = "#E6E6E6"
NORMAL = "#0072B2"
SLE = "#D55E00"
PRIMARY = "#009E73"
EXPLORATORY = "#E69F00"
DISCOVERY = "#8A8A8A"


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 6.5,
            "axes.titlesize": 7,
            "axes.labelsize": 6.5,
            "axes.linewidth": 1.0,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "xtick.major.width": 1.0,
            "ytick.major.width": 1.0,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "legend.fontsize": 6,
            "lines.linewidth": 1.0,
            "patch.linewidth": 1.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def panel_label(ax, label: str) -> None:
    ax.text(
        -0.08,
        1.06,
        label,
        transform=ax.transAxes,
        fontsize=8,
        fontweight="bold",
        ha="left",
        va="top",
        color=BLACK,
    )


def clean(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)


def workflow_panel(ax) -> None:
    ax.set_axis_off()
    panel_label(ax, "a")
    ax.set_title("Outcome-locked analysis workflow", loc="left", fontweight="bold", pad=3)
    labels = [
        ("Audited\nraw/X", "152,981 cells"),
        ("Frozen\nhard QC", "150,402 cells"),
        ("Disease-blind\nstates", "full B-cell graph"),
        ("Sample-level\ncomposition", "state counts"),
        ("State-wise\npseudobulk", "raw counts"),
        ("Frozen external\nmapping", "GSE135779"),
    ]
    fills = ["#EAF2F8", "#E8F6F3", "#F4F6F6", "#FFF5E6", "#FFF5E6", "#FDEDEC"]
    x_positions = np.linspace(0.01, 0.84, len(labels))
    width = 0.145
    for idx, (x, (title, subtitle)) in enumerate(zip(x_positions, labels)):
        rect = Rectangle((x, 0.31), width, 0.42, facecolor=fills[idx], edgecolor=BLACK, linewidth=1.0)
        ax.add_patch(rect)
        ax.text(x + width / 2, 0.59, title, ha="center", va="center", fontsize=5.4, fontweight="bold", linespacing=1.0)
        ax.text(x + width / 2, 0.41, subtitle, ha="center", va="center", fontsize=4.9, color=GRAY)
        if idx < len(labels) - 1:
            arrow = FancyArrowPatch(
                (x + width + 0.004, 0.52),
                (x_positions[idx + 1] - 0.004, 0.52),
                arrowstyle="-|>",
                mutation_scale=8,
                color=BLACK,
                linewidth=1.0,
            )
            ax.add_patch(arrow)
    ax.text(
        x_positions[2] + width / 2,
        0.16,
        "Disease fields remain physically separate until state freeze",
        ha="center",
        va="center",
        fontsize=5.4,
        color=BLACK,
    )
    ax.plot(
        [x_positions[2] + width / 2, x_positions[2] + width / 2],
        [0.28, 0.22],
        color="#7A3E00",
        linewidth=1.0,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def hierarchy_panel(ax, counts: dict[str, int]) -> None:
    ax.set_axis_off()
    panel_label(ax, "b")
    ax.set_title("Biological and technical hierarchy", loc="left", fontweight="bold", pad=3)
    nodes = [
        (f"{counts['donors']:,} donors", 0.78),
        (f"{counts['samples']:,} biological samples", 0.58),
        (f"{counts['sample_library_records']:,} sample-library records", 0.38),
        (f"{counts['libraries']:,} technical libraries", 0.18),
    ]
    x, width, height = 0.08, 0.64, 0.13
    for idx, (label, y) in enumerate(nodes):
        ax.add_patch(Rectangle((x, y), width, height, facecolor="white", edgecolor=BLACK, linewidth=1.0))
        ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=6.1, fontweight="bold")
        if idx < len(nodes) - 1:
            next_y = nodes[idx + 1][1]
            ax.add_patch(
                FancyArrowPatch(
                    (x + width / 2, y - 0.006),
                    (x + width / 2, next_y + height + 0.006),
                    arrowstyle="-|>",
                    mutation_scale=8,
                    color=BLACK,
                    linewidth=1.0,
                )
            )
    ax.text(0.79, 0.69, f"{counts['repeated_donors']} donors\nrepeated", ha="left", va="center", fontsize=5.7, color=BLACK)
    ax.text(0.79, 0.29, f"{counts['bridge_samples']} samples\nbridge cohorts", ha="left", va="center", fontsize=5.7, color=BLACK)
    ax.plot([0.72, 0.78], [0.71, 0.71], color="#7A3E00", linewidth=1.0)
    ax.plot([0.72, 0.78], [0.31, 0.31], color="#7A3E00", linewidth=1.0)
    ax.text(0.40, 0.04, "Sample = biological unit; library = technical unit", ha="center", fontsize=5.7, color=GRAY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def common_support_panel(ax, technical: pd.DataFrame, strict: pd.DataFrame) -> None:
    panel_label(ax, "c")
    ax.set_title("Apparent versus strict common support", loc="left", fontweight="bold", pad=3)
    groups = [("Technical\nrecords", technical, "n_unique_samples"), ("Strict biological\nsubset", strict, "n_strict_biological_units")]
    x_offsets = [0.0, 2.65]
    for (heading, frame, count_col), offset in zip(groups, x_offsets):
        for cohort in range(1, 5):
            for disease_idx, disease in enumerate(("Normal", "SLE")):
                if count_col == "n_unique_samples":
                    disease_key = "normal" if disease == "Normal" else "systemic lupus erythematosus"
                    match = frame[
                        frame["Processing_Cohort"].eq(float(cohort))
                        & frame["disease"].eq(disease_key)
                    ]
                else:
                    match = frame[
                        frame["processing_cohort"].eq(cohort)
                        & frame["disease"].eq(disease)
                    ]
                value = int(match[count_col].iloc[0]) if len(match) else 0
                x = offset + disease_idx
                y = 5 - cohort
                color = NORMAL if disease == "Normal" else SLE
                size = 18 + 2.2 * value
                if value:
                    ax.scatter(x, y, s=size, color=color, alpha=0.82, edgecolor="white", linewidth=0.7)
                else:
                    ax.scatter(x, y, s=35, facecolor="white", edgecolor=color, linewidth=1.0)
                ax.text(x, y, str(value), ha="center", va="center", fontsize=5.5, color="white" if value > 8 else BLACK, fontweight="bold")
        ax.text(offset + 0.5, 4.62, heading, ha="center", va="bottom", fontsize=6.2, fontweight="bold")
    ax.axvline(1.82, color=LIGHT_GRAY, linewidth=1.0)
    ax.set_xlim(-0.55, 4.25)
    ax.set_ylim(0.45, 5.05)
    ax.set_xticks([0, 1, 2.65, 3.65], ["Normal", "SLE", "Normal", "SLE"])
    ax.set_yticks([1, 2, 3, 4], ["Cohort 4", "Cohort 3", "Cohort 2", "Cohort 1"])
    ax.tick_params(axis="both", length=0)
    ax.spines[:].set_visible(False)
    ax.text(1.80, 0.57, "53 bridge samples inflate technical overlap", ha="center", va="bottom", fontsize=5.5, color=BLACK)


def retention_panel(ax, retention: pd.DataFrame) -> None:
    panel_label(ax, "d")
    ax.set_title("Hard-QC exclusions", loc="left", fontweight="bold", pad=3)
    frame = retention.copy()
    frame["excluded_fraction"] = frame["n_hard_fail"] / frame["n_cells"]
    for disease, color, label, offset in (
        ("normal", NORMAL, "Normal", -0.10),
        ("systemic lupus erythematosus", SLE, "SLE", 0.10),
    ):
        sub = frame[frame["disease"].eq(disease)]
        y = sub["Processing_Cohort"] + offset
        ax.scatter(
            sub["excluded_fraction"] * 100,
            y,
            marker="o",
            s=21,
            color=color,
            label=label,
            linewidth=0,
        )
        for row, y_value in zip(sub.itertuples(index=False), y):
            percent = row.n_hard_fail / row.n_cells * 100
            ax.text(
                percent + 0.06,
                y_value,
                f"{percent:.1f}",
                va="center",
                fontsize=5.2,
                color=BLACK,
            )
    ax.set_xlabel("Cells excluded (%)")
    ax.set_ylabel("Processing cohort")
    ax.set_yticks([1, 2, 3, 4])
    ax.set_xlim(0, 3.2)
    ax.invert_yaxis()
    clean(ax)
    handles = [
        Line2D([0], [0], marker="o", linestyle="none", color=NORMAL, label="Normal", markersize=4),
        Line2D([0], [0], marker="o", linestyle="none", color=SLE, label="SLE", markersize=4),
    ]
    ax.legend(
        handles=handles,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.01, 0.99),
        ncol=2,
        handletextpad=0.3,
        columnspacing=0.8,
    )


def inference_panel(ax, tiers: pd.DataFrame) -> None:
    panel_label(ax, "e")
    ax.set_title("Prespecified inference tiers", loc="left", fontweight="bold", pad=3)
    color_map = {"Discovery only": DISCOVERY, "Exploratory": EXPLORATORY, "Primary": PRIMARY}
    y = np.arange(len(tiers))[::-1]
    for position, row in zip(y, tiers.itertuples(index=False)):
        ax.barh(position, 1, color=color_map[row.inference_tier], height=0.58)
        ax.text(0.04, position, row.stratum, ha="left", va="center", fontsize=6, color="white", fontweight="bold")
        ax.text(1.04, position, row.inference_tier, ha="left", va="center", fontsize=5.8, color=BLACK, fontweight="bold")
    ax.set_xlim(0, 1.68)
    ax.set_ylim(-0.7, len(tiers) - 0.3)
    ax.set_axis_off()
    ax.text(0, -0.58, "Bridge samples: technical diagnostics only", fontsize=5.7, color=BLACK)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gatec1-dir", required=True)
    parser.add_argument("--gatec2b1-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    gatec1 = Path(args.gatec1_dir).resolve()
    gatec2b1 = Path(args.gatec2b1_dir).resolve()
    output = Path(args.output_dir).resolve()
    figures = output / "figures"
    tables = output / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    sample = pd.read_csv(gatec1 / "01_sample_manifest.csv")
    donor = pd.read_csv(gatec1 / "02_donor_manifest.csv")
    library = pd.read_csv(gatec1 / "03_library_manifest.csv")
    technical = pd.read_csv(gatec1 / "04_cohort_disease_common_support.csv")
    repeated = pd.read_csv(gatec1 / "05_repeated_donor_manifest.csv")
    sample_library = pd.read_csv(gatec1 / "07_sample_library_manifest.csv")
    strict_support = pd.read_csv(gatec1 / "15_strict_common_support_reaudit.csv")
    retention = pd.read_csv(gatec2b1 / "02_full_qc_retention_summary.csv")

    required_strict = {"processing_cohort", "disease", "n_strict_biological_units"}
    if set(strict_support.columns) != required_strict:
        raise RuntimeError(f"Unexpected strict-support columns: {list(strict_support.columns)}")
    if int(strict_support["n_strict_biological_units"].sum()) != 195:
        raise RuntimeError("Strict-support table does not contain the expected 195 donors")

    counts = {
        "donors": int(donor["donor_id"].nunique()),
        "samples": int(sample["sample_uuid"].nunique()),
        "sample_library_records": int(len(sample_library)),
        "libraries": int(library["library_uuid"].nunique()),
        "repeated_donors": int(len(repeated)),
        "bridge_samples": int(sample["multi_cohort_sample"].sum()),
    }
    if counts != {
        "donors": 259,
        "samples": 271,
        "sample_library_records": 1373,
        "libraries": 88,
        "repeated_donors": 11,
        "bridge_samples": 53,
    }:
        raise RuntimeError(f"Unexpected hierarchy counts: {counts}")

    tiers = pd.DataFrame(
        {
            "stratum": ["Cohort 1", "Cohort 2", "Cohort 3", "Cohort 4"],
            "inference_tier": ["Discovery only", "Discovery only", "Exploratory", "Primary"],
        }
    )
    pd.DataFrame([counts]).to_csv(tables / "figure1b_hierarchy_counts.csv", index=False)
    technical.to_csv(tables / "figure1c_technical_common_support.csv", index=False)
    strict_support.to_csv(tables / "figure1c_strict_common_support.csv", index=False)
    retention.to_csv(tables / "figure1d_hard_qc_retention.csv", index=False)
    tiers.to_csv(tables / "figure1e_inference_tiers.csv", index=False)

    style()
    fig = plt.figure(figsize=(FIGURE_WIDTH_MM * MM, FIGURE_HEIGHT_MM * MM))
    grid = fig.add_gridspec(
        2,
        12,
        height_ratios=[0.75, 1.25],
        left=0.055,
        right=0.985,
        top=0.965,
        bottom=0.09,
        wspace=1.25,
        hspace=0.48,
    )
    ax_a = fig.add_subplot(grid[0, :8])
    ax_b = fig.add_subplot(grid[0, 8:])
    ax_c = fig.add_subplot(grid[1, :5])
    ax_d = fig.add_subplot(grid[1, 5:9])
    ax_e = fig.add_subplot(grid[1, 9:])

    workflow_panel(ax_a)
    hierarchy_panel(ax_b, counts)
    common_support_panel(ax_c, technical, strict_support)
    retention_panel(ax_d, retention)
    inference_panel(ax_e, tiers)

    png = figures / "figure1_v7_study_design.png"
    pdf = figures / "figure1_v7_study_design.pdf"
    fig.savefig(png, dpi=600, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    print(png)
    print(pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
