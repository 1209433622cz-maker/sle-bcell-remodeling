from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scanpy as sc

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

FOCUS_STATE = "Atypical ABC/APC-like B"
FLAGGED_STATE = "Flagged platelet/ambient-high B"

PROGRAM_ORDER = ["ABC_ranked", "ABC_DN2", "APC_HLA", "IFN_response", "Activation", "Memory_B", "Naive_B", "Plasmablast"]
PROGRAM_LABELS = {
    "ABC_ranked": "ABC ranked",
    "ABC_DN2": "ABC/DN2",
    "APC_HLA": "APC/HLA",
    "IFN_response": "IFN",
    "Activation": "Activation",
    "Memory_B": "Memory",
    "Naive_B": "Naive",
    "Plasmablast": "Plasmablast",
}
DISEASE_STATE_ORDER = ["na", "managed", "flare", "treated"]
DISEASE_STATE_LABELS = {"na": "Normal", "managed": "SLE managed", "flare": "SLE flare", "treated": "SLE treated"}


def add_panel_label(ax, label: str, x: float = -0.10) -> None:
    ax.text(x, 1.05, label, transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", ha="right", va="bottom")


def p_label(value: float) -> str:
    if pd.isna(value):
        return "n.s."
    if value < 1e-4:
        return f"{value:.1e}"
    return f"{value:.3f}"


def load_umap(h5ad: str) -> tuple[np.ndarray, pd.DataFrame]:
    adata = sc.read_h5ad(h5ad)
    obs = adata.obs.copy()
    obs["refined_state"] = obs["draft_state"].astype(str).map(REFINED_STATE_MAP)
    umap = adata.obsm["X_umap"].copy()
    return umap, obs


def plot_focus_umap(ax, umap: np.ndarray, obs: pd.DataFrame) -> None:
    xlim = np.quantile(umap[:, 0], [0.001, 0.999])
    ylim = np.quantile(umap[:, 1], [0.001, 0.999])
    other = (obs["refined_state"] != FOCUS_STATE) & (obs["refined_state"] != FLAGGED_STATE)
    flagged = obs["refined_state"] == FLAGGED_STATE
    focus = obs["refined_state"] == FOCUS_STATE
    ax.scatter(umap[other, 0], umap[other, 1], s=0.45, color="#D7DCE2", linewidth=0, rasterized=True, label="Other B states")
    ax.scatter(umap[flagged, 0], umap[flagged, 1], s=0.65, color="#8A8A8A", linewidth=0, rasterized=True, label="Flagged")
    ax.scatter(umap[focus, 0], umap[focus, 1], s=1.1, color="#B23A48", linewidth=0, rasterized=True, label="ABC/APC-like")
    ax.set_title("Atypical ABC/APC-like B-cell state")
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.legend(frameon=False, fontsize=5.5, loc="lower left", markerscale=6)


def plot_abundance(ax, donor_fractions: pd.DataFrame, state_tests: pd.DataFrame, sensitivity_tests: pd.DataFrame) -> None:
    df = donor_fractions.copy()
    df["refined_state"] = df["draft_state"].map(REFINED_STATE_MAP)
    df = df[df["refined_state"] == FOCUS_STATE].copy()
    palette = {"normal": "#9AA4B2", "systemic lupus erythematosus": "#C94C4C"}
    disease_order = ["normal", "systemic lupus erythematosus"]
    sns.boxplot(
        data=df,
        x="disease",
        y="fraction_within_donor",
        hue="disease",
        order=disease_order,
        hue_order=disease_order,
        palette=palette,
        showfliers=False,
        legend=False,
        ax=ax,
    )
    sns.stripplot(
        data=df,
        x="disease",
        y="fraction_within_donor",
        hue="disease",
        order=disease_order,
        hue_order=disease_order,
        palette=palette,
        alpha=0.45,
        size=2.2,
        linewidth=0,
        legend=False,
        ax=ax,
    )
    tests = state_tests.copy()
    tests["refined_state"] = tests["draft_state"].map(REFINED_STATE_MAP)
    sens = sensitivity_tests.copy()
    sens["refined_state"] = sens["draft_state"].map(REFINED_STATE_MAP)
    orig_fdr = tests.loc[tests["refined_state"] == FOCUS_STATE, "fdr_bh"].iloc[0]
    sens_fdr = sens.loc[sens["refined_state"] == FOCUS_STATE, "fdr_bh"].iloc[0]
    ax.set_title("Donor-level abundance")
    ax.set_xlabel("")
    ax.set_ylabel("Fraction of donor B-lineage cells")
    ax.set_xticks([0, 1], ["Normal", "SLE"])
    ymax = max(df["fraction_within_donor"].quantile(0.995), 0.08)
    ax.text(0.5, ymax * 1.08, f"Original FDR {p_label(orig_fdr)}\nSensitivity FDR {p_label(sens_fdr)}", ha="center", va="bottom", fontsize=5.5)
    ax.set_ylim(0, ymax * 1.28)
    ax.spines[["top", "right"]].set_visible(False)


def plot_program_comparison(ax, program_long: pd.DataFrame) -> None:
    df = program_long[(program_long["n_cells"] >= 10) & (program_long["refined_state"] != FLAGGED_STATE)].copy()
    df = df[df["program"].isin(PROGRAM_ORDER)].copy()
    focus = (
        df[df["refined_state"] == FOCUS_STATE]
        .groupby(["donor_id", "program"], observed=True)["mean_log1p_cp10k"]
        .mean()
        .rename("ABC/APC-like")
    )
    other = (
        df[df["refined_state"] != FOCUS_STATE]
        .groupby(["donor_id", "program"], observed=True)["mean_log1p_cp10k"]
        .mean()
        .rename("Other retained states")
    )
    paired = pd.concat([focus, other], axis=1, join="inner").dropna().reset_index()
    paired = paired.melt(
        id_vars=["donor_id", "program"],
        value_vars=["ABC/APC-like", "Other retained states"],
        var_name="comparison",
        value_name="mean_log1p_cp10k",
    )
    paired["program_label"] = pd.Categorical(paired["program"].map(PROGRAM_LABELS), categories=[PROGRAM_LABELS[p] for p in PROGRAM_ORDER], ordered=True)
    palette = {"ABC/APC-like": "#B23A48", "Other retained states": "#B8C0CC"}
    sns.boxplot(data=paired, x="program_label", y="mean_log1p_cp10k", hue="comparison", palette=palette, showfliers=False, linewidth=0.8, ax=ax)
    ax.set_title("Paired donor pseudobulk programs")
    ax.set_xlabel("")
    ax.set_ylabel("Mean log1p(CP10K)")
    ax.tick_params(axis="x", rotation=35, labelsize=5.5)
    ax.legend(frameon=False, fontsize=5.5, title="")
    ax.spines[["top", "right"]].set_visible(False)


def plot_gene_effects(ax, gene_tests: pd.DataFrame) -> None:
    keep = gene_tests[gene_tests["delta_focus_minus_other"] > 0].sort_values("delta_focus_minus_other", ascending=False).head(14).copy()
    keep = keep.sort_values("delta_focus_minus_other")
    ax.barh(keep["gene"], keep["delta_focus_minus_other"], color="#B23A48", edgecolor="white", linewidth=0.7)
    ax.set_title("Top paired donor marker effects")
    ax.set_xlabel("Paired donor delta log1p(CP10K)\nABC/APC-like minus other states")
    ax.set_ylabel("")
    for i, row in enumerate(keep.itertuples(index=False)):
        ax.text(row.delta_focus_minus_other, i, f" {p_label(row.fdr_bh)}", va="center", fontsize=5.5)
    ax.spines[["top", "right"]].set_visible(False)


def plot_disease_state_heatmap(ax, disease_summary: pd.DataFrame) -> None:
    df = disease_summary[disease_summary["program"].isin(["ABC_ranked", "ABC_DN2", "APC_HLA", "IFN_response", "Activation"])].copy()
    matrix = df.pivot_table(index="disease_state", columns="program", values="mean_log1p_cp10k", aggfunc="mean")
    matrix = matrix.reindex(DISEASE_STATE_ORDER)
    matrix = matrix.rename(index=DISEASE_STATE_LABELS)
    matrix = matrix.rename(columns=PROGRAM_LABELS)
    matrix = matrix[[PROGRAM_LABELS[p] for p in ["ABC_ranked", "ABC_DN2", "APC_HLA", "IFN_response", "Activation"]]]
    sns.heatmap(matrix, cmap="YlOrRd", linewidths=0.5, linecolor="white", cbar_kws={"label": "Mean log1p(CP10K)"}, ax=ax)
    ax.set_title("Disease-state program context")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=35, labelsize=5.5)
    ax.tick_params(axis="y", labelsize=5.5)


def write_focus_table(output: Path, program_tests: pd.DataFrame, gene_tests: pd.DataFrame) -> None:
    top_programs = program_tests.sort_values("delta_focus_minus_other", ascending=False).head(6).copy()
    top_genes = gene_tests[gene_tests["delta_focus_minus_other"] > 0].sort_values("delta_focus_minus_other", ascending=False).head(15).copy()
    rows = []
    for row in top_programs.itertuples(index=False):
        rows.append({"type": "program", "name": row.program, "delta": row.delta_focus_minus_other, "fdr_bh": row.fdr_bh})
    for row in top_genes.itertuples(index=False):
        rows.append({"type": "gene", "name": row.gene, "delta": row.delta_focus_minus_other, "fdr_bh": row.fdr_bh})
    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create focused Figure 3 for the ABC/APC-like B-cell state.")
    parser.add_argument("--h5ad", required=True)
    parser.add_argument("--donor-fractions", required=True)
    parser.add_argument("--state-tests", required=True)
    parser.add_argument("--sensitivity-tests", required=True)
    parser.add_argument("--program-long", required=True)
    parser.add_argument("--gene-tests", required=True)
    parser.add_argument("--program-tests", required=True)
    parser.add_argument("--disease-summary", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--focus-table-output", required=True)
    args = parser.parse_args()

    umap, obs = load_umap(args.h5ad)
    donor_fractions = pd.read_csv(args.donor_fractions)
    state_tests = pd.read_csv(args.state_tests)
    sensitivity_tests = pd.read_csv(args.sensitivity_tests)
    program_long = pd.read_csv(args.program_long)
    gene_tests = pd.read_csv(args.gene_tests)
    program_tests = pd.read_csv(args.program_tests)
    disease_summary = pd.read_csv(args.disease_summary)

    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    fig = plt.figure(figsize=nature_figsize(18, 12.5))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.05, 1.45, 1.1], height_ratios=[1.0, 1.0], wspace=0.48, hspace=0.45)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1:])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    ax_e = fig.add_subplot(gs[1, 2])

    plot_focus_umap(ax_a, umap, obs)
    plot_program_comparison(ax_b, program_long)
    plot_abundance(ax_c, donor_fractions, state_tests, sensitivity_tests)
    plot_gene_effects(ax_d, gene_tests)
    plot_disease_state_heatmap(ax_e, disease_summary)

    for ax, label in zip([ax_a, ax_b, ax_c, ax_d], list("abcd"), strict=True):
        add_panel_label(ax, label)
    add_panel_label(ax_e, "e", x=-0.16)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    save_nature_figure(fig, out)
    plt.close(fig)
    write_focus_table(Path(args.focus_table_output), program_tests, gene_tests)
    print(f"Wrote: {out}")
    print(f"Wrote: {out.with_suffix('.pdf')}")
    print(f"Wrote: {args.focus_table_output}")


if __name__ == "__main__":
    main()
