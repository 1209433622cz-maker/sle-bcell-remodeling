from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import seaborn as sns
import scanpy as sc

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


REFINED_LABELS = {
    0: "Resting naive B",
    1: "Activated SLE-naive-like B",
    2: "Memory-like B I",
    3: "Mixed / transitional B",
    4: "TNFRSF13B+ memory-like B",
    5: "Atypical ABC/APC-like B",
    6: "Flagged platelet/ambient-high B",
    7: "Plasmablast / ASC",
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


STATE_PALETTE = {
    "Resting naive B": "#4E9F3D",
    "Activated SLE-naive-like B": "#D9822B",
    "Memory-like B I": "#2F6FA3",
    "Mixed / transitional B": "#B08CC2",
    "TNFRSF13B+ memory-like B": "#58A4B0",
    "Atypical ABC/APC-like B": "#B23A48",
    "Flagged platelet/ambient-high B": "#7C7C7C",
    "Plasmablast / ASC": "#6A4C93",
}


DOT_GENES = [
    "TCL1A",
    "IL4R",
    "FCER2",
    "VPREB3",
    "CD69",
    "JUNB",
    "FOS",
    "GPR183",
    "LTB",
    "TNFRSF13B",
    "AIM2",
    "FCRL5",
    "FCRL3",
    "ZEB2",
    "HLA-DRA",
    "CD74",
    "MZB1",
    "JCHAIN",
    "XBP1",
    "TNFRSF17",
    "PPBP",
    "PF4",
    "TUBB1",
]


PROGRAMS = [
    "Naive_B",
    "Memory_B",
    "ABC_DN2",
    "Antigen_presentation",
    "Activation",
    "Plasmablast",
    "Platelet_ambient",
]

PROGRAM_LABELS = {
    "Naive_B": "Naive",
    "Memory_B": "Memory",
    "ABC_DN2": "ABC/DN2",
    "Antigen_presentation": "APC",
    "Activation": "Activation",
    "Plasmablast": "Plasmablast",
    "Platelet_ambient": "Platelet/ambient",
}


FOCUS_STATES = [
    "Activated SLE-naive-like B",
    "Memory-like B I",
    "Atypical ABC/APC-like B",
    "Resting naive B",
    "Plasmablast / ASC",
]

STATE_DISPLAY = {
    "Resting naive B": "Resting naive",
    "Activated SLE-naive-like B": "Activated SLE-naive",
    "Memory-like B I": "Memory-like I",
    "Mixed / transitional B": "Mixed / transitional",
    "TNFRSF13B+ memory-like B": "TNFRSF13B+ memory",
    "Atypical ABC/APC-like B": "ABC/APC-like",
    "Flagged platelet/ambient-high B": "Flagged QC state",
    "Plasmablast / ASC": "Plasmablast / ASC",
}


def add_panel_label(ax, label: str) -> None:
    ax.text(-0.08, 1.04, label, transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="bottom", ha="right")


def fdr_label(value: float) -> str:
    if pd.isna(value):
        return "n.s."
    if value < 1e-4:
        return f"FDR {value:.1e}"
    return f"FDR {value:.3f}"


def short_p(value: float) -> str:
    if pd.isna(value):
        return "n.s."
    if value < 1e-4:
        return f"{value:.1e}"
    return f"{value:.3f}"


def load_umap(h5ad: str) -> tuple[np.ndarray, pd.DataFrame]:
    adata = sc.read_h5ad(h5ad)
    if "X_umap" not in adata.obsm:
        raise SystemExit("Input H5AD does not contain X_umap.")
    obs = adata.obs.copy()
    obs["leiden_int"] = obs["leiden"].astype(str).astype(int)
    obs["refined_state"] = obs["leiden_int"].map(REFINED_LABELS)
    umap = adata.obsm["X_umap"].copy()
    return umap, obs


def plot_umap(ax, umap: np.ndarray, obs: pd.DataFrame) -> None:
    xlim = np.quantile(umap[:, 0], [0.001, 0.999])
    ylim = np.quantile(umap[:, 1], [0.001, 0.999])
    for state in STATE_ORDER:
        mask = obs["refined_state"].to_numpy() == state
        ax.scatter(
            umap[mask, 0],
            umap[mask, 1],
            s=0.7,
            linewidth=0,
            color=STATE_PALETTE[state],
            label=state,
            rasterized=True,
            alpha=0.9 if "Flagged" not in state else 0.72,
        )
    ax.set_title("Refined B-cell states")
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks([])
    ax.set_yticks([])
    if ax.get_legend() is not None:
        ax.get_legend().remove()


def map_state(df: pd.DataFrame, column: str = "draft_state") -> pd.DataFrame:
    draft_to_refined = {
        "Naive B I": "Resting naive B",
        "Naive B II / SLE-enriched naive-like": "Activated SLE-naive-like B",
        "Memory B I": "Memory-like B I",
        "Mixed naive-memory B": "Mixed / transitional B",
        "Memory B II": "TNFRSF13B+ memory-like B",
        "Atypical / ABC-like B": "Atypical ABC/APC-like B",
        "Naive B III / small naive-like cluster": "Flagged platelet/ambient-high B",
        "Plasmablast / plasma cell": "Plasmablast / ASC",
    }
    out = df.copy()
    out["refined_state"] = out[column].map(draft_to_refined)
    return out


def plot_marker_dotplot(ax, marker_summary: pd.DataFrame) -> None:
    data = map_state(marker_summary)
    data = data[data["gene"].isin(DOT_GENES)].copy()
    data["refined_state"] = pd.Categorical(data["refined_state"], categories=STATE_ORDER[::-1], ordered=True)
    data["gene"] = pd.Categorical(data["gene"], categories=[g for g in DOT_GENES if g in set(data["gene"])], ordered=True)
    data = data.sort_values(["refined_state", "gene"])
    x = data["gene"].cat.codes.to_numpy()
    y = data["refined_state"].cat.codes.to_numpy()
    size = 18 + 260 * data["pct_expressing"].to_numpy()
    color = data["mean_log1p_cp10k"].to_numpy()
    sc = ax.scatter(x, y, s=size, c=color, cmap="viridis", edgecolor="0.25", linewidth=0.2)
    ax.set_title("Raw-count marker support")
    ax.set_xticks(range(len(data["gene"].cat.categories)))
    ax.set_xticklabels(list(data["gene"].cat.categories), rotation=55, ha="right", fontsize=5)
    ax.set_yticks(range(len(data["refined_state"].cat.categories)))
    state_categories = list(data["refined_state"].cat.categories)
    ax.set_yticklabels([STATE_DISPLAY[x] for x in state_categories], fontsize=5.2)
    for tick, state in zip(ax.get_yticklabels(), state_categories, strict=True):
        tick.set_color(STATE_PALETTE[state])
        tick.set_fontweight("bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(axis="both", color="0.93", linewidth=0.4)
    ax.set_axisbelow(True)
    cbar = plt.colorbar(sc, ax=ax, fraction=0.028, pad=0.01)
    cbar.set_label("Mean log1p(CP10K)", fontsize=6)
    cbar.ax.tick_params(labelsize=5)
    for pct, label in [(0.1, "10%"), (0.4, "40%"), (0.8, "80%")]:
        ax.scatter([], [], s=18 + 260 * pct, c="lightgray", edgecolor="0.25", linewidth=0.2, label=label)
    ax.legend(
        title="Expressing",
        fontsize=4.8,
        title_fontsize=5.2,
        loc="upper right",
        ncol=3,
        frameon=True,
        facecolor="white",
        edgecolor="none",
        borderpad=0.2,
        handletextpad=0.1,
        columnspacing=0.4,
    )


def plot_donor_fractions(ax, donor_frac: pd.DataFrame, tests: pd.DataFrame) -> None:
    data = map_state(donor_frac)
    data = data[data["refined_state"].isin(FOCUS_STATES)].copy()
    data["refined_state"] = pd.Categorical(data["refined_state"], categories=FOCUS_STATES, ordered=True)
    test_data = map_state(tests).set_index("refined_state")
    hue_order = ["normal", "systemic lupus erythematosus"]
    disease_palette_box = {"normal": "#B9C0C9", "systemic lupus erythematosus": "#C94C4C"}
    disease_palette_points = {"normal": "#6E7781", "systemic lupus erythematosus": "#8F2525"}
    sns.boxplot(
        data=data,
        y="refined_state",
        x="fraction_within_donor",
        hue="disease",
        hue_order=hue_order,
        order=FOCUS_STATES,
        palette=disease_palette_box,
        showfliers=False,
        linewidth=0.8,
        ax=ax,
    )
    sns.stripplot(
        data=data,
        y="refined_state",
        x="fraction_within_donor",
        hue="disease",
        hue_order=hue_order,
        order=FOCUS_STATES,
        palette=disease_palette_points,
        dodge=True,
        alpha=0.38,
        size=1.9,
        linewidth=0,
        ax=ax,
    )
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    ax.set_title("Donor-level abundance", loc="left")
    ax.text(0.73, 1.02, "Normal", color=disease_palette_points["normal"], fontweight="bold", transform=ax.transAxes, ha="right", va="bottom", fontsize=5.2)
    ax.text(0.98, 1.02, "SLE", color=disease_palette_points["systemic lupus erythematosus"], fontweight="bold", transform=ax.transAxes, ha="right", va="bottom", fontsize=5.2)
    ax.set_xlabel("Fraction of donor B-lineage cells")
    ax.set_ylabel("")
    ax.set_yticks(range(len(FOCUS_STATES)))
    ax.set_yticklabels([STATE_DISPLAY[x] for x in FOCUS_STATES], fontsize=5.2)
    xmax = max(data["fraction_within_donor"].quantile(0.995), 0.08)
    for i, state in enumerate(FOCUS_STATES):
        fdr = test_data.loc[state, "fdr_bh"] if state in test_data.index else np.nan
        ax.text(xmax * 1.25, i, fdr_label(fdr), ha="right", va="center", fontsize=4.8)
    ax.set_xlim(0, xmax * 1.30)


def plot_effect_sensitivity(ax, original: pd.DataFrame, sensitivity: pd.DataFrame) -> None:
    orig = map_state(original)
    sens = map_state(sensitivity)
    orig["analysis"] = "Original"
    sens["analysis"] = "Excluding flagged state"
    data = pd.concat([orig, sens], ignore_index=True)
    data = data[data["refined_state"].isin(FOCUS_STATES)].copy()
    data["refined_state"] = pd.Categorical(data["refined_state"], categories=FOCUS_STATES, ordered=True)
    data["display_state"] = data["refined_state"].astype(str).map(STATE_DISPLAY)
    display_order = [STATE_DISPLAY[x] for x in FOCUS_STATES]
    sns.barplot(
        data=data,
        y="display_state",
        x="mean_difference_sle_minus_normal",
        hue="analysis",
        order=display_order,
        palette={"Original": "#7AA6C2", "Excluding flagged state": "#D98B5F"},
        ax=ax,
    )
    ax.axvline(0, color="0.2", linewidth=0.8)
    ax.set_title("Sensitivity to flagged-state exclusion")
    ax.set_xlabel("Mean fraction difference")
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=5.2)
    ax.set_ylim(len(display_order) - 0.5, -1.0)
    ax.legend(
        frameon=False,
        fontsize=4.8,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        ncol=2,
        borderaxespad=0,
        columnspacing=0.8,
        handletextpad=0.3,
    )
    ax.set_xlim(-0.12, 0.19)
    annotation_x = 0.185
    sens_idx = sens.set_index("refined_state")
    for i, state in enumerate(FOCUS_STATES):
        if state in sens_idx.index:
            fdr = sens_idx.loc[state, "fdr_bh"]
            diff = sens_idx.loc[state, "mean_difference_sle_minus_normal"]
            ax.text(annotation_x, i + 0.2, fdr_label(fdr), fontsize=4.8, va="center", ha="right")


def plot_program_heatmap(ax, program_summary: pd.DataFrame) -> None:
    data = map_state(program_summary)
    data = data[data["program"].isin(PROGRAMS)].copy()
    matrix = data.pivot_table(
        index="refined_state",
        columns="program",
        values="mean_log1p_cp10k",
        aggfunc="mean",
    ).reindex(STATE_ORDER)
    matrix = matrix.reindex(columns=PROGRAMS)
    matrix = matrix.rename(columns=PROGRAM_LABELS)
    sns.heatmap(matrix, cmap="YlGnBu", linewidths=0.4, linecolor="white", cbar_kws={"label": "Mean log1p(CP10K)"}, ax=ax)
    ax.set_title("Raw-count program summary")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=45, labelsize=5.5)
    ax.tick_params(axis="y", labelsize=5.5)


def write_state_table(output: Path) -> None:
    rows = [{"leiden": k, "refined_state": v, "color": STATE_PALETTE[v]} for k, v in REFINED_LABELS.items()]
    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create refined Figure 2 v3 for B-cell state atlas.")
    parser.add_argument("--h5ad", required=True)
    parser.add_argument("--marker-summary", required=True)
    parser.add_argument("--program-summary", required=True)
    parser.add_argument("--donor-fractions", required=True)
    parser.add_argument("--state-tests", required=True)
    parser.add_argument("--sensitivity-tests", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--state-table-output", required=True)
    args = parser.parse_args()

    umap, obs = load_umap(args.h5ad)
    marker_summary = pd.read_csv(args.marker_summary)
    program_summary = pd.read_csv(args.program_summary)
    donor_frac = pd.read_csv(args.donor_fractions)
    state_tests = pd.read_csv(args.state_tests)
    sensitivity = pd.read_csv(args.sensitivity_tests)

    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    fig = plt.figure(figsize=nature_figsize(6.8, 5.8), constrained_layout=True)
    outer = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.15])
    top = outer[0].subgridspec(1, 2, width_ratios=[0.78, 1.72], wspace=0.24)
    bottom = outer[1].subgridspec(1, 2, width_ratios=[1.08, 0.92], wspace=0.34)

    ax_a = fig.add_subplot(top[0, 0])
    ax_b = fig.add_subplot(top[0, 1])
    ax_c = fig.add_subplot(bottom[0, 0])
    ax_d = fig.add_subplot(bottom[0, 1])

    plot_umap(ax_a, umap, obs)
    plot_marker_dotplot(ax_b, marker_summary)
    plot_donor_fractions(ax_c, donor_frac, state_tests)
    plot_effect_sensitivity(ax_d, state_tests, sensitivity)

    for ax, label in zip([ax_a, ax_b, ax_c, ax_d], list("abcd"), strict=True):
        add_panel_label(ax, label)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    save_nature_figure(fig, out)
    plt.close(fig)
    write_state_table(Path(args.state_table_output))
    print(f"Wrote: {out}")
    print(f"Wrote: {args.state_table_output}")


if __name__ == "__main__":
    main()
