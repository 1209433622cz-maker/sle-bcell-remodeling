from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scanpy as sc


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a draft Figure 2 panel for B-cell state atlas.")
    parser.add_argument("--h5ad", required=True)
    parser.add_argument("--annotation", required=True)
    parser.add_argument("--donor-state-fractions", required=True)
    parser.add_argument("--state-tests", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    adata = sc.read_h5ad(args.h5ad)
    annotation = pd.read_csv(args.annotation)
    short_map = dict(zip(annotation["leiden"].astype(str), annotation["short_label"]))
    figure_map = dict(zip(annotation["short_label"], annotation["figure_label"]))
    adata.obs["leiden"] = adata.obs["leiden"].astype(str)
    adata.obs["short_state"] = adata.obs["leiden"].map(short_map)

    donor_frac = pd.read_csv(args.donor_state_fractions)
    tests = pd.read_csv(args.state_tests)
    reverse_draft_to_short = dict(zip(annotation["draft_label"], annotation["short_label"]))
    donor_frac["short_state"] = donor_frac["draft_state"].map(reverse_draft_to_short)
    tests["short_state"] = tests["draft_state"].map(reverse_draft_to_short)
    tests_by_state = tests.set_index("short_state")
    donor_frac["figure_state"] = donor_frac["short_state"].map(figure_map)

    state_order = annotation.sort_values("leiden")["short_label"].tolist()
    figure_order = [figure_map[state] for state in state_order]

    palette = dict(zip(state_order, sns.color_palette("tab10", n_colors=len(state_order))))

    umap = adata.obsm["X_umap"]
    obs = adata.obs
    xlim = np.quantile(umap[:, 0], [0.001, 0.999])
    ylim = np.quantile(umap[:, 1], [0.001, 0.999])

    sns.set_theme(style="white", context="talk")
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.05], width_ratios=[1.1, 1.1, 1.25])

    ax0 = fig.add_subplot(gs[0, 0])
    for state in state_order:
        mask = obs["short_state"] == state
        ax0.scatter(umap[mask, 0], umap[mask, 1], s=1, color=palette[state], label=figure_map[state], rasterized=True)
    ax0.set_title("B-cell states")
    ax0.set_xlabel("UMAP1")
    ax0.set_ylabel("UMAP2")
    ax0.set_xlim(xlim)
    ax0.set_ylim(ylim)
    ax0.legend(markerscale=6, fontsize=8, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)

    ax1 = fig.add_subplot(gs[0, 1])
    sc1 = ax1.scatter(
        umap[:, 0],
        umap[:, 1],
        c=obs["ABC_DN2_axis_score"].to_numpy(),
        s=1,
        cmap="viridis",
        rasterized=True,
    )
    ax1.set_title("ABC/DN2-axis score")
    ax1.set_xlabel("UMAP1")
    ax1.set_ylabel("UMAP2")
    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim)
    fig.colorbar(sc1, ax=ax1, fraction=0.046, pad=0.04)

    ax2 = fig.add_subplot(gs[0, 2])
    sc2 = ax2.scatter(
        umap[:, 0],
        umap[:, 1],
        c=obs["Plasmablast_score"].to_numpy(),
        s=1,
        cmap="viridis",
        rasterized=True,
    )
    ax2.set_title("Plasmablast score")
    ax2.set_xlabel("UMAP1")
    ax2.set_ylabel("UMAP2")
    ax2.set_xlim(xlim)
    ax2.set_ylim(ylim)
    fig.colorbar(sc2, ax=ax2, fraction=0.046, pad=0.04)

    ax3 = fig.add_subplot(gs[1, :])
    sns.boxplot(
        data=donor_frac,
        x="figure_state",
        y="fraction_within_donor",
        hue="disease",
        order=figure_order,
        showfliers=False,
        linewidth=1,
        ax=ax3,
    )
    sns.stripplot(
        data=donor_frac,
        x="figure_state",
        y="fraction_within_donor",
        hue="disease",
        order=figure_order,
        dodge=True,
        alpha=0.35,
        size=2,
        linewidth=0,
        ax=ax3,
    )
    handles, labels = ax3.get_legend_handles_labels()
    ax3.legend(handles[:2], labels[:2], title="Disease", loc="upper right", frameon=True, fontsize=10, title_fontsize=11)
    ax3.set_title("Donor-level state fractions")
    ax3.set_xlabel("")
    ax3.set_ylabel("Fraction of donor B-lineage cells")
    ax3.tick_params(axis="x", rotation=20)

    # Add FDR labels above each state.
    ymax = donor_frac["fraction_within_donor"].quantile(0.995)
    for i, state in enumerate(state_order):
        fdr = tests_by_state.loc[state, "fdr_bh"] if state in tests_by_state.index else float("nan")
        ax3.text(i, ymax * 1.03, f"FDR={fdr:.1e}", ha="center", va="bottom", fontsize=7)
    ax3.set_ylim(0, max(0.08, ymax * 1.18))

    fig.suptitle("Figure 2 draft: SLE B-cell state remodeling", y=0.995, fontsize=20)
    fig.tight_layout()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
