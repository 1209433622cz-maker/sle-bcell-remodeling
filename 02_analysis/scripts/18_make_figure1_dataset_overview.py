from __future__ import annotations

import argparse
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np
import pandas as pd
import seaborn as sns

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


REFINED_STATE_MAP = {
    "Naive B I": "Resting naive B",
    "Naive B II / SLE-enriched naive-like": "Activated SLE-naive-like B",
    "Memory B I": "Memory-like B I",
    "Mixed naive-memory B": "Mixed / transitional B",
    "Memory B II": "TNFRSF13B+ memory-like B",
    "Atypical / ABC-like B": "Atypical ABC/APC-like B",
    "Naive B III / small naive-like cluster": "Flagged platelet/ambient-high B",
    "Plasmablast / plasma cell": "Plasmablast / ASC",
}


STATE_ORDER = [
    "Resting naive B",
    "Activated SLE-naive-like B",
    "Memory-like B I",
    "Mixed / transitional B",
    "TNFRSF13B+ memory-like B",
    "Atypical ABC/APC-like B",
    "Flagged platelet/ambient-high B",
    "Plasmablast / ASC",
]


STATE_COLORS = {
    "Resting naive B": "#4E9F3D",
    "Activated SLE-naive-like B": "#D9822B",
    "Memory-like B I": "#2F6FA3",
    "Mixed / transitional B": "#B08CC2",
    "TNFRSF13B+ memory-like B": "#58A4B0",
    "Atypical ABC/APC-like B": "#B23A48",
    "Flagged platelet/ambient-high B": "#7C7C7C",
    "Plasmablast / ASC": "#6A4C93",
}


DISEASE_COLORS = {"normal": "#9AA4B2", "systemic lupus erythematosus": "#C94C4C"}


def fmt_int(value: int | float) -> str:
    return f"{int(value):,}"


def short_cell_type(name: str) -> str:
    replacements = {
        "CD4-positive, alpha-beta T cell": "CD4 T cell",
        "CD8-positive, alpha-beta T cell": "CD8 T cell",
        "classical monocyte": "Classical monocyte",
        "non-classical monocyte": "Non-classical monocyte",
        "natural killer cell": "NK cell",
        "conventional dendritic cell": "cDC",
        "plasmablast": "Plasmablast",
        "B cell": "B cell",
    }
    return replacements.get(name, name)


def add_panel_label(ax, label: str) -> None:
    ax.text(-0.08, 1.04, label, transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", ha="right", va="bottom")


def draw_box(ax, xy, width, height, text, facecolor="#F5F7FA", edgecolor="#2F3A45", fontsize=6.0) -> None:
    box = Rectangle(
        xy,
        width,
        height,
        linewidth=0.5,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_artist(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#17202A",
        linespacing=1.05,
    )


def draw_arrow(ax, start, end) -> None:
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, linewidth=1.2, color="#425466")
    ax.add_artist(arrow)


def plot_workflow(ax, summary: dict[str, int]) -> None:
    ax.set_axis_off()
    ax.set_title("Study workflow")
    boxes = [
        (
            (0.015, 0.55),
            "Perez/GSE174188\nCELLxGENE object\n"
            f"{fmt_int(summary['source_cells'])} cells\n{fmt_int(summary['source_donors'])} donors",
            "#EEF4FF",
        ),
        (
            (0.265, 0.55),
            "B-lineage extraction\nB cell + plasmablast\n"
            f"{fmt_int(summary['b_cells'])} cells\n{fmt_int(summary['b_donors'])} donors",
            "#ECFDF3",
        ),
        (
            (0.515, 0.55),
            "State mapping\nprovided PCA/UMAP\nLeiden clustering\n8 refined states",
            "#FFF7E6",
        ),
        (
            (0.765, 0.55),
            "Raw-count refinement\nadata.raw.X\nmarkers + programs\nsensitivity analyses",
            "#FDEEEF",
        ),
        (
            (0.265, 0.08),
            "Matrix decision\nX: scaled/preprocessed\nraw.X: count-like",
            "#F4F6F8",
        ),
        (
            (0.515, 0.08),
            "QC decision\ncluster 6 flagged\nplatelet/ambient high",
            "#F4F6F8",
        ),
    ]
    for index, (xy, text, color) in enumerate(boxes):
        height = 0.32 if index < 4 else 0.25
        draw_box(ax, xy, 0.205, height, text, facecolor=color, fontsize=5.4)
    for x0, x1 in [(0.22, 0.265), (0.47, 0.515), (0.72, 0.765)]:
        draw_arrow(ax, (x0, 0.71), (x1, 0.71))
    draw_arrow(ax, (0.3675, 0.55), (0.3675, 0.35))
    draw_arrow(ax, (0.6175, 0.55), (0.6175, 0.35))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def plot_source_cell_types(ax, source_counts: pd.DataFrame) -> None:
    top = source_counts.head(8).copy()
    top["label"] = top["cell_type"].map(short_cell_type)
    colors = ["#D9822B" if x in {"B cell", "Plasmablast"} else "#8FA7BF" for x in top["label"]]
    ax.barh(top["label"][::-1], top["n_cells"][::-1], color=colors[::-1], edgecolor="white", linewidth=0.8)
    ax.set_title("Source immune-cell composition")
    ax.set_xlabel("Cells")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda x, pos: f"{int(x/1000)}k")
    for i, value in enumerate(top["n_cells"][::-1]):
        ax.text(value, i, f" {fmt_int(value)}", va="center", fontsize=6)
    ax.spines[["top", "right"]].set_visible(False)


def plot_donor_summary(ax, donor_counts: pd.DataFrame, b_donor_counts: pd.DataFrame) -> None:
    source = donor_counts.copy()
    source["scope"] = "All cells"
    b = b_donor_counts.copy()
    b["scope"] = "B-lineage"
    data = pd.concat([source, b], ignore_index=True)
    data["disease_label"] = data["disease"].replace({"systemic lupus erythematosus": "SLE", "normal": "Normal"})
    sns.barplot(
        data=data,
        x="scope",
        y="n_donors",
        hue="disease_label",
        hue_order=["Normal", "SLE"],
        palette={"Normal": DISEASE_COLORS["normal"], "SLE": DISEASE_COLORS["systemic lupus erythematosus"]},
        ax=ax,
    )
    ax.set_title("Donors retained by disease")
    ax.set_xlabel("")
    ax.set_ylabel("Donors")
    ax.set_ylim(0, 190)
    ax.legend(frameon=False, fontsize=6, title="", loc="upper right", bbox_to_anchor=(1.0, 0.88))
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", fontsize=6, padding=2)
    ax.spines[["top", "right"]].set_visible(False)


def plot_bcell_breakdown(ax, b_cell_type_counts: pd.DataFrame) -> None:
    data = b_cell_type_counts.copy()
    data["label"] = data["cell_type"].map(short_cell_type)
    colors = ["#4E9F3D" if x == "B cell" else "#6A4C93" for x in data["label"]]
    wedges, texts, autotexts = ax.pie(
        data["n_cells"],
        labels=data["label"],
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 2 else "",
        startangle=90,
        colors=colors,
        wedgeprops={"linewidth": 0.8, "edgecolor": "white"},
        textprops={"fontsize": 6},
    )
    for autotext in autotexts:
        autotext.set_fontsize(6)
        autotext.set_color("white")
    ax.set_title("B-lineage subset")
    ax.text(
        0,
        -1.20,
        "\n".join([f"{row.label}: {fmt_int(row.n_cells)}" for row in data.itertuples(index=False)]),
        ha="center",
        va="top",
        fontsize=6,
    )


def plot_state_counts(ax, state_counts: pd.DataFrame) -> None:
    data = state_counts.copy()
    data["refined_state"] = pd.Categorical(data["refined_state"], categories=STATE_ORDER[::-1], ordered=True)
    data = data.sort_values("refined_state")
    colors = [STATE_COLORS[str(x)] for x in data["refined_state"]]
    ax.barh(data["refined_state"], data["n_cells"], color=colors, edgecolor="white", linewidth=0.8)
    ax.set_title("Refined B-cell state sizes")
    ax.set_xlabel("Cells")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda x, pos: f"{int(x/1000)}k")
    for i, value in enumerate(data["n_cells"]):
        ax.text(value, i, f" {fmt_int(value)}", va="center", fontsize=6)
    ax.spines[["top", "right"]].set_visible(False)


def plot_qc_notes(ax, summary: dict[str, int]) -> None:
    ax.set_axis_off()
    ax.set_title("Analysis guardrails")
    notes = [
        ("Metadata complete", "cell_type, disease and donor_id\ncomplete in the B-lineage table"),
        ("Scaled X retained", "X contains negative values and\nwas not renormalized"),
        ("Raw layer for markers", "adata.raw.X was count-like in\nsampled checks"),
        ("Flagged cluster", "PPBP/PF4/TUBB1/NRGN high;\nexcluded from central claims"),
        ("Donor-level inference", "99 normal and 160 SLE donors"),
    ]
    y = 0.95
    for title, body in notes:
        ax.plot([0.025, 0.025], [y - 0.12, y], color="#425466", linewidth=2.2, solid_capstyle="butt")
        ax.text(0.06, y, title, ha="left", va="top", fontsize=5.4, fontweight="bold", color="#17202A")
        ax.text(0.06, y - 0.042, body, ha="left", va="top", fontsize=4.7, color="#425466", linespacing=1.05)
        y -= 0.19
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Figure 1 dataset and workflow overview.")
    parser.add_argument("--source-h5ad", required=True)
    parser.add_argument("--bcell-scores", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    figdir = outdir / "figures"
    tabledir = outdir / "tables"
    figdir.mkdir(parents=True, exist_ok=True)
    tabledir.mkdir(parents=True, exist_ok=True)

    source = ad.read_h5ad(args.source_h5ad, backed="r")
    source_obs = source.obs[["cell_type", "disease", "disease_state", "donor_id"]].copy()
    try:
        source.file.close()
    except Exception:
        pass

    b_obs = pd.read_csv(args.bcell_scores, index_col=0, low_memory=False)
    b_obs["refined_state"] = b_obs["draft_state"].map(REFINED_STATE_MAP)

    source_counts = source_obs["cell_type"].value_counts().rename_axis("cell_type").reset_index(name="n_cells")
    source_donor_counts = source_obs[["donor_id", "disease"]].drop_duplicates()["disease"].value_counts().rename_axis("disease").reset_index(name="n_donors")
    source_disease_state_donors = (
        source_obs[["donor_id", "disease_state"]].drop_duplicates()["disease_state"].value_counts().rename_axis("disease_state").reset_index(name="n_donors")
    )
    b_donor_counts = b_obs[["donor_id", "disease"]].drop_duplicates()["disease"].value_counts().rename_axis("disease").reset_index(name="n_donors")
    b_disease_state_donors = b_obs[["donor_id", "disease_state"]].drop_duplicates()["disease_state"].value_counts().rename_axis("disease_state").reset_index(name="n_donors")
    b_cell_type_counts = b_obs["cell_type"].value_counts().rename_axis("cell_type").reset_index(name="n_cells")
    state_counts = b_obs["refined_state"].value_counts().rename_axis("refined_state").reset_index(name="n_cells")
    state_counts["fraction"] = state_counts["n_cells"] / state_counts["n_cells"].sum()
    summary = {
        "source_cells": int(source_obs.shape[0]),
        "source_donors": int(source_obs["donor_id"].nunique()),
        "b_cells": int(b_obs.shape[0]),
        "b_donors": int(b_obs["donor_id"].nunique()),
        "b_normal_donors": int(b_donor_counts.loc[b_donor_counts["disease"] == "normal", "n_donors"].iloc[0]),
        "b_sle_donors": int(b_donor_counts.loc[b_donor_counts["disease"] == "systemic lupus erythematosus", "n_donors"].iloc[0]),
        "flagged_cells": int(state_counts.loc[state_counts["refined_state"] == "Flagged platelet/ambient-high B", "n_cells"].iloc[0]),
    }
    summary_df = pd.DataFrame([summary])

    source_counts.to_csv(tabledir / "source_cell_type_counts.csv", index=False, encoding="utf-8-sig")
    source_donor_counts.to_csv(tabledir / "source_donor_counts_by_disease.csv", index=False, encoding="utf-8-sig")
    source_disease_state_donors.to_csv(tabledir / "source_donor_counts_by_disease_state.csv", index=False, encoding="utf-8-sig")
    b_donor_counts.to_csv(tabledir / "bcell_donor_counts_by_disease.csv", index=False, encoding="utf-8-sig")
    b_disease_state_donors.to_csv(tabledir / "bcell_donor_counts_by_disease_state.csv", index=False, encoding="utf-8-sig")
    b_cell_type_counts.to_csv(tabledir / "bcell_cell_type_counts.csv", index=False, encoding="utf-8-sig")
    state_counts.to_csv(tabledir / "bcell_refined_state_counts.csv", index=False, encoding="utf-8-sig")
    summary_df.to_csv(tabledir / "figure1_dataset_summary.csv", index=False, encoding="utf-8-sig")

    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    fig = plt.figure(figsize=nature_figsize(18, 14.5))
    gs = fig.add_gridspec(
        3,
        3,
        width_ratios=[1.15, 0.95, 1.25],
        height_ratios=[0.95, 1.0, 1.08],
        wspace=0.48,
        hspace=0.58,
    )

    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])
    ax_d = fig.add_subplot(gs[1, 2])
    ax_e = fig.add_subplot(gs[2, :2])
    ax_f = fig.add_subplot(gs[2, 2])

    plot_workflow(ax_a, summary)
    plot_source_cell_types(ax_b, source_counts)
    plot_donor_summary(ax_c, source_donor_counts, b_donor_counts)
    plot_bcell_breakdown(ax_d, b_cell_type_counts)
    plot_state_counts(ax_e, state_counts)
    plot_qc_notes(ax_f, summary)

    for ax, label in zip([ax_a, ax_b, ax_c, ax_d, ax_e, ax_f], list("abcdef"), strict=True):
        add_panel_label(ax, label)
    png = figdir / "figure1_dataset_overview.png"
    pdf = figdir / "figure1_dataset_overview.pdf"
    save_nature_figure(fig, png)
    plt.close(fig)
    print(f"Wrote: {png}")
    print(f"Wrote: {pdf}")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
