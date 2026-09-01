#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager

MM = 1 / 25.4

# Established semantic palette from the current project presentation layer.
BLUE = "#2C6EAD"
TEAL = "#2A9D8F"
ORANGE = "#E69F00"
RED = "#D55E00"
GREY = "#B8BDC7"
DARK = "#333333"

def require_arial() -> None:
    try:
        path = font_manager.findfont("Arial", fallback_to_default=False)
    except Exception as exc:
        raise SystemExit(
            "Arial is not available in this environment. "
            "Abort rather than silently substituting Arimo/DejaVu. "
            f"Original error: {exc}"
        )
    if "arial" not in Path(path).name.lower():
        raise SystemExit(f"Resolved font is not Arial: {path}")

def apply_style() -> None:
    mpl.rcParams.update({
        "font.family": "Arial",
        "font.size": 6,
        "axes.titlesize": 7,
        "axes.labelsize": 6,
        "axes.linewidth": 0.5,
        "axes.titlepad": 3,
        "xtick.labelsize": 5.5,
        "ytick.labelsize": 5.5,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "legend.fontsize": 5.5,
        "lines.linewidth": 0.7,
        "patch.linewidth": 0.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
    })

def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def panel_label(ax, letter):
    ax.text(-0.13, 1.04, letter, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="bottom", ha="left")

def save_exact(fig, out_pdf: Path, width_mm: float, height_mm: float):
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(width_mm * MM, height_mm * MM, forward=True)
    fig.savefig(out_pdf, bbox_inches=None, pad_inches=0)
    fig.savefig(out_pdf.with_suffix(".png"), dpi=600, bbox_inches=None, pad_inches=0)
    plt.close(fig)

def build_s3(sd: Path, out_pdf: Path) -> None:
    df = pd.read_csv(sd)
    b = df[df["panel"].eq("b")].copy()
    c = df[df["panel"].eq("c")].copy()

    fig, axes = plt.subplots(1, 2, gridspec_kw={"wspace": 0.34})
    ax = axes[0]
    policy_labels = {
        "five_state": "5-state",
        "four_state_platelet_overlay_merged": "4-state",
        "three_state_identity_core": "3-state",
    }
    colors = {"5-state": BLUE, "4-state": TEAL, "3-state": ORANGE}
    y = 0
    yticks, ylabels = [], []
    for policy in ["five_state", "four_state_platelet_overlay_merged", "three_state_identity_core"]:
        sub = b[b["policy"].eq(policy)].sort_values("reference_state")
        label = policy_labels[policy]
        for _, r in sub.iterrows():
            ax.plot([r["minimum_jaccard"], r["median_jaccard"]], [y, y],
                    color=colors[label], alpha=0.75)
            ax.scatter(r["median_jaccard"], y, s=13, marker="o",
                       color=colors[label], zorder=3)
            ax.scatter(r["minimum_jaccard"], y, s=12, marker="x",
                       color=colors[label], linewidths=0.7, zorder=3)
            yticks.append(y)
            ylabels.append(f"{label} C{int(r['reference_state'])}")
            y += 1
        y += 0.55
    ax.axvline(0.95, ls="--", lw=0.6, color=GREY)
    ax.set_xlim(-0.03, 1.02)
    ax.set_xlabel("Cluster Jaccard")
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()
    ax.set_title("Failure localizes to fine-state membership", loc="left")
    clean_axes(ax)
    panel_label(ax, "a")

    ax = axes[1]
    clusters = sorted(set(c["reference_cluster"].dropna().astype(int)) |
                      set(c["mapped_reference_cluster"].dropna().astype(int)))
    n = max(clusters) + 1
    mat = np.zeros((n, n), dtype=float)
    for _, r in c.iterrows():
        mat[int(r["reference_cluster"]), int(r["mapped_reference_cluster"])] = float(r["fraction_of_reference_cluster"])
    im = ax.imshow(mat, cmap="Blues", vmin=0, vmax=1, aspect="equal")
    ax.set_xlabel("Mapped reference cluster")
    ax.set_ylabel("Original cluster")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_title("Mean r=0.4 transition matrix", loc="left")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.ax.tick_params(labelsize=5.5, width=0.5, length=2.5)
    panel_label(ax, "b")

    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.16, top=0.90)
    save_exact(fig, out_pdf, 170, 82)

def build_s5(sd: Path, out_pdf: Path) -> None:
    df = pd.read_csv(sd)
    m = df[df["source_table"].eq("model_summary")].copy()
    q = df[df["panel"].eq("c")].copy()

    order = [
        "primary_base", "primary_min20", "primary_min100",
        "primary_residual_risk_negative", "validation_full",
        "validation_nonoverlap", "flare_full"
    ]
    labels = ["Primary", ">=20", ">=100", "Risk-negative", "Internal", "Nonoverlap", "Flare"]
    m["analysis_name"] = pd.Categorical(m["analysis_name"], categories=order, ordered=True)
    m = m.sort_values("analysis_name")
    x = np.arange(len(m))

    fig = plt.figure()
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.06], hspace=0.52, wspace=0.33)
    axa = fig.add_subplot(gs[0, 0])
    axb = fig.add_subplot(gs[0, 1])
    axc = fig.add_subplot(gs[1, :])

    axa.bar(x, m["tested_genes"], color=GREY, width=0.72, label="Tested")
    axa.bar(x, m["fdr_0_05_genes"], color=RED, width=0.72, label="BH q<0.05")
    axa.set_ylabel("Genes")
    axa.set_xticks(x)
    axa.set_xticklabels(labels, rotation=35, ha="right")
    axa.set_title("filterByExpr-tested and significant genes", loc="left")
    axa.legend(frameon=False, ncol=2, loc="upper left")
    clean_axes(axa)
    panel_label(axa, "a")

    axb.plot(x, m["common_dispersion"], marker="o", markersize=2.8, color=BLUE, label="Common")
    axb.plot(x, m["median_tagwise_dispersion"], marker="o", markersize=2.8, color=ORANGE, label="Median tagwise")
    axb.set_ylabel("Dispersion")
    axb.set_xticks(x)
    axb.set_xticklabels(labels, rotation=35, ha="right")
    axb.set_title("edgeR dispersion diagnostics", loc="left")
    axb.legend(frameon=False, ncol=2, loc="upper left")
    clean_axes(axb)
    panel_label(axb, "b")

    q = q.sort_values("rank_cutoff")
    axc.plot(q["rank_cutoff"], 100*q["mitochondrial_fraction"], marker="o", markersize=2.8, label="Mitochondrial")
    axc.plot(q["rank_cutoff"], 100*q["ribosomal_fraction"], marker="o", markersize=2.8, label="Ribosomal")
    axc.plot(q["rank_cutoff"], 100*q["hemoglobin_fraction"], marker="o", markersize=2.8, label="Haemoglobin")
    axc.plot(q["rank_cutoff"], 100*q["immunoglobulin_fraction"], marker="o", markersize=2.8, label="Immunoglobulin")
    axc.set_xlabel("Top-ranked genes")
    axc.set_ylabel("Technical-family fraction (%)")
    axc.set_title("Ranked-list technical-family audit", loc="left")
    axc.legend(frameon=False, ncol=4, loc="upper left")
    clean_axes(axc)
    panel_label(axc, "c")

    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.13, top=0.93)
    save_exact(fig, out_pdf, 170, 104)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package-root", type=Path, required=True,
                    help="Root of 20260901_reference_terminology_s6_refreeze")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()

    require_arial()
    apply_style()

    sd = args.package_root / "figures" / "source_data"
    args.outdir.mkdir(parents=True, exist_ok=True)

    build_s3(sd / "Supplementary_Figure_S3_source_data.csv",
             args.outdir / "Supplementary_Figure_S3_fine_state_failure_transition_structure.pdf")
    build_s5(sd / "Supplementary_Figure_S5_source_data.csv",
             args.outdir / "Supplementary_Figure_S5_pseudobulk_ranked_list_diagnostics.pdf")

    mapping = pd.DataFrame([
        ["S3a", "", "display-pruned; evidence owner Figure 1b"],
        ["S3b", "S3a", "retained"],
        ["S3c", "S3b", "retained"],
        ["S3d", "", "display-pruned; evidence owner Figure 1d"],
        ["S5a", "S5a", "retained"],
        ["S5b", "S5b", "retained"],
        ["S5c", "S5c", "retained"],
        ["S5d", "", "display-pruned; evidence owner Figure 3b"],
    ], columns=["frozen_source_panel", "final_display_panel", "action"])
    mapping.to_csv(args.outdir / "S3_S5_display_panel_mapping.csv", index=False)

if __name__ == "__main__":
    main()
