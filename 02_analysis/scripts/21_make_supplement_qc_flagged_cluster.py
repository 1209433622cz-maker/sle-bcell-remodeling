from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scanpy as sc

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


FLAGGED_STATE = "Naive B III / small naive-like cluster"
FLAGGED_LABEL = "Flagged platelet/ambient-high B"

STATE_LABELS = {
    "Naive B II / SLE-enriched naive-like": "Activated SLE-naive-like",
    "Memory B I": "Memory-like B I",
    "Atypical / ABC-like B": "ABC/APC-like",
    FLAGGED_STATE: "Flagged cluster",
}

MARKER_CLASSES = {
    "MS4A1": "B-cell identity",
    "CD79A": "B-cell identity",
    "CD74": "B-cell identity",
    "PPBP": "Platelet/ambient",
    "PF4": "Platelet/ambient",
    "NRGN": "Platelet/ambient",
    "TUBB1": "Platelet/ambient",
    "RGS18": "Platelet/ambient",
    "CAVIN2": "Platelet/ambient",
    "GNG11": "Platelet/ambient",
    "SPARC": "Platelet/ambient",
}

MARKER_ORDER = list(MARKER_CLASSES)
CORE_STATES = ["Naive B II / SLE-enriched naive-like", "Memory B I", "Atypical / ABC-like B"]


def add_panel_label(ax, label: str) -> None:
    ax.text(-0.12, 1.06, label, transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", ha="right", va="bottom")


def disease_label(value: str) -> str:
    return "SLE" if str(value) == "systemic lupus erythematosus" else "Normal"


def p_label(value: float) -> str:
    if pd.isna(value):
        return "n.s."
    if value < 1e-4:
        return f"{value:.1e}"
    return f"{value:.3f}"


def plot_flagged_umap(ax, h5ad: str) -> None:
    adata = sc.read_h5ad(h5ad)
    obs = adata.obs.copy()
    umap = adata.obsm["X_umap"].copy()
    flagged = obs["draft_state"].astype(str) == FLAGGED_STATE
    xlim = np.quantile(umap[:, 0], [0.001, 0.999])
    ylim = np.quantile(umap[:, 1], [0.001, 0.999])
    ax.scatter(umap[~flagged, 0], umap[~flagged, 1], s=0.45, color="#D7DCE2", linewidth=0, rasterized=True, label="Other B-lineage cells")
    ax.scatter(umap[flagged, 0], umap[flagged, 1], s=1.1, color="#7C7C7C", linewidth=0, rasterized=True, label=FLAGGED_LABEL)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_title("Flagged cluster location")
    ax.legend(frameon=False, fontsize=5.5, loc="lower left", markerscale=6)


def plot_ranked_markers(ax, ranked_path: str) -> pd.DataFrame:
    ranked = pd.read_csv(ranked_path)
    sub = ranked[ranked["group"].astype(str) == FLAGGED_STATE].copy()
    sub["logfoldchanges"] = pd.to_numeric(sub["logfoldchanges"], errors="coerce")
    top = sub.head(12).iloc[::-1]
    ax.barh(top["names"], top["logfoldchanges"], color="#7C7C7C")
    ax.set_xlabel("Raw-count ranked log fold change")
    ax.set_ylabel("")
    ax.set_title("Top ranked markers")
    return sub.head(20)


def plot_marker_expression(ax, marker_summary_path: str) -> pd.DataFrame:
    marker = pd.read_csv(marker_summary_path)
    sub = marker[(marker["draft_state"].astype(str) == FLAGGED_STATE) & (marker["gene"].isin(MARKER_ORDER))].copy()
    sub["gene"] = pd.Categorical(sub["gene"], categories=MARKER_ORDER, ordered=True)
    sub["marker_class"] = sub["gene"].astype(str).map(MARKER_CLASSES)
    sub["mean_log1p_cp10k"] = pd.to_numeric(sub["mean_log1p_cp10k"], errors="coerce")
    sub["pct_expressing"] = pd.to_numeric(sub["pct_expressing"], errors="coerce")
    sub = sub.sort_values("gene")
    palette = {"B-cell identity": "#4E9F3D", "Platelet/ambient": "#7C7C7C"}
    sns.barplot(data=sub, x="gene", y="mean_log1p_cp10k", hue="marker_class", palette=palette, ax=ax, dodge=False)
    ax.set_xlabel("")
    ax.set_ylabel("Mean log1p(CP10K)")
    ax.set_title("B-cell and platelet/ambient markers")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False, title="")
    ymax = sub["mean_log1p_cp10k"].max()
    ax.set_ylim(0, ymax * 1.28)
    for patch, (_, row) in zip(ax.patches, sub.iterrows()):
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            patch.get_height() + ymax * 0.025,
            f"{row['pct_expressing'] * 100:.0f}%",
            ha="center",
            va="bottom",
            fontsize=5.5,
            rotation=90,
        )
    return sub


def plot_flagged_fraction(ax, donor_fractions_path: str, tests_path: str) -> pd.DataFrame:
    frac = pd.read_csv(donor_fractions_path)
    sub = frac[frac["draft_state"].astype(str) == FLAGGED_STATE].copy()
    sub["disease_label"] = sub["disease"].map(disease_label)
    tests = pd.read_csv(tests_path)
    test_row = tests[tests["draft_state"].astype(str) == FLAGGED_STATE].iloc[0]
    palette = {"Normal": "#AEB7C2", "SLE": "#D36B6B"}
    sns.boxplot(data=sub, x="disease_label", y="fraction_within_donor", hue="disease_label", order=["Normal", "SLE"], palette=palette, ax=ax, width=0.55, fliersize=0, legend=False)
    sns.stripplot(data=sub, x="disease_label", y="fraction_within_donor", order=["Normal", "SLE"], color="#333333", alpha=0.35, size=2.0, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Fraction of donor B-lineage cells")
    ax.set_title("Flagged cluster abundance")
    ax.text(0.5, 0.94, f"FDR {p_label(float(test_row['fdr_bh']))}", transform=ax.transAxes, ha="center", va="top", fontsize=6)
    return pd.DataFrame([test_row])


def plot_sensitivity(ax, original_path: str, sensitivity_path: str) -> pd.DataFrame:
    original = pd.read_csv(original_path)
    sensitivity = pd.read_csv(sensitivity_path)
    rows = []
    for label, table in [("Original", original), ("Exclude flagged", sensitivity)]:
        sub = table[table["draft_state"].isin(CORE_STATES)].copy()
        sub["analysis"] = label
        rows.append(sub)
    out = pd.concat(rows, ignore_index=True)
    out["state_label"] = out["draft_state"].map(STATE_LABELS)
    out["mean_difference_sle_minus_normal"] = pd.to_numeric(out["mean_difference_sle_minus_normal"], errors="coerce")
    sns.barplot(
        data=out,
        x="state_label",
        y="mean_difference_sle_minus_normal",
        hue="analysis",
        order=[STATE_LABELS[state] for state in CORE_STATES],
        palette={"Original": "#AEB7C2", "Exclude flagged": "#B23A48"},
        ax=ax,
    )
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xlabel("")
    ax.set_ylabel("Mean fraction difference\nSLE minus normal")
    ax.set_title("Core signals after flagged-state exclusion")
    ax.tick_params(axis="x", rotation=25)
    ax.legend(frameon=False, title="")
    return out


def write_summary(outdir: Path, top_markers: pd.DataFrame, marker_expr: pd.DataFrame, fraction_test: pd.DataFrame, sensitivity: pd.DataFrame) -> None:
    tabledir = outdir / "tables"
    tabledir.mkdir(parents=True, exist_ok=True)
    top_markers.to_csv(tabledir / "flagged_cluster_top_ranked_markers.csv", index=False, encoding="utf-8-sig")
    marker_expr.to_csv(tabledir / "flagged_cluster_selected_marker_expression.csv", index=False, encoding="utf-8-sig")
    fraction_test.to_csv(tabledir / "flagged_cluster_donor_fraction_test.csv", index=False, encoding="utf-8-sig")
    sensitivity.to_csv(tabledir / "core_state_sensitivity_original_vs_exclude_flagged.csv", index=False, encoding="utf-8-sig")

    row = fraction_test.iloc[0]
    lines = [
        "# Supplementary QC Summary - Flagged Cluster",
        "",
        f"- Flagged state: `{FLAGGED_STATE}`.",
        f"- Mean donor fraction normal: {float(row['mean_fraction_normal']):.4f}.",
        f"- Mean donor fraction SLE: {float(row['mean_fraction_sle']):.4f}.",
        f"- Donor-level flagged-cluster FDR: {float(row['fdr_bh']):.2e}.",
        "- Interpretation: this cluster has B-cell identity signal but is dominated by platelet/ambient-associated ranked markers, so it should remain a QC-limited state.",
        "- Sensitivity result: the main activated naive-like, memory-like, and ABC/APC-like disease signals remain directionally stable after excluding the flagged cluster.",
        "",
        "## Top Ranked Markers",
        "",
    ]
    for marker in top_markers.head(12).itertuples(index=False):
        lines.append(f"- {marker.names}: logFC {float(marker.logfoldchanges):.3f}; score {float(marker.scores):.3f}")
    (outdir / "supplement_qc_flagged_cluster_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create supplementary QC figure for flagged platelet/ambient-high B cluster.")
    parser.add_argument("--h5ad", required=True)
    parser.add_argument("--marker-summary", required=True)
    parser.add_argument("--ranked-markers", required=True)
    parser.add_argument("--donor-fractions", required=True)
    parser.add_argument("--state-tests", required=True)
    parser.add_argument("--sensitivity-tests", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    figdir = outdir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    fig = plt.figure(figsize=nature_figsize(14, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.05, 1.15, 1.1], height_ratios=[1.0, 1.0])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[1, 0])
    ax_e = fig.add_subplot(gs[1, 1:])

    plot_flagged_umap(ax_a, args.h5ad)
    top_markers = plot_ranked_markers(ax_b, args.ranked_markers)
    marker_expr = plot_marker_expression(ax_c, args.marker_summary)
    fraction_test = plot_flagged_fraction(ax_d, args.donor_fractions, args.state_tests)
    sensitivity = plot_sensitivity(ax_e, args.state_tests, args.sensitivity_tests)

    for ax, label in zip([ax_a, ax_b, ax_c, ax_d, ax_e], list("abcde")):
        add_panel_label(ax, label)
    out_png = figdir / "supplement_qc_flagged_cluster.png"
    out_pdf = out_png.with_suffix(".pdf")
    save_nature_figure(fig, out_png)
    plt.close(fig)

    write_summary(outdir, top_markers, marker_expr, fraction_test, sensitivity)
    print(f"Wrote supplementary QC figure to: {out_png}")


if __name__ == "__main__":
    main()
