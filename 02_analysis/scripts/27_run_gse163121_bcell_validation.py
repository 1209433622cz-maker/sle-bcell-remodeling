from __future__ import annotations

import gzip
import io
import tarfile
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import sparse
from scipy.io import mmread
from scipy.stats import mannwhitneyu

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE163121_bcell_validation" / "source"
OUT_DIR = PROJECT_ROOT / "03_results" / "gse163121_bcell_validation"
TABLE_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"
PROCESSED_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE163121_bcell_validation"


PROGRAMS = {
    "ABC_APC_focus": ["FCRL5", "FCRL3", "ZEB2", "ITGAX", "TBX21", "CD74", "HLA-DRA", "HLA-DPB1", "MS4A1"],
    "ZEB2_TBX21_ITGAX_axis": ["ZEB2", "TBX21", "ITGAX"],
    "FCRL_axis": ["FCRL5", "FCRL3"],
    "HLA_CD74_axis": ["CD74", "HLA-DRA", "HLA-DRB1", "HLA-DPB1"],
    "ABC_DN2_core": ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7"],
    "APC_HLA": ["CD74", "HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1", "CIITA", "CD86"],
    "IFN_ISG": ["ISG15", "IFIT1", "IFIT2", "IFIT3", "MX1", "MX2", "OAS1", "OAS2", "IFI44L", "IFI6"],
    "Naive_B": ["TCL1A", "VPREB3", "IGHD", "IL4R", "CXCR4", "CD79B"],
    "Plasmablast_ASC": ["XBP1", "PRDM1", "MZB1", "JCHAIN", "SDC1", "TNFRSF17"],
}

MARKER_GENES = ["FCRL5", "FCRL3", "ZEB2", "ITGAX", "TBX21", "CD74", "HLA-DRA", "MS4A1", "ISG15", "MZB1"]


def bh_fdr(pvalues: list[float]) -> list[float]:
    p = np.asarray(pvalues, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = np.empty(n, dtype=float)
    running = 1.0
    for i in range(n - 1, -1, -1):
        running = min(running, ranked[i] * n / (i + 1))
        adjusted[order[i]] = running
    return adjusted.tolist()


def parse_sample_from_member(name: str) -> dict[str, str]:
    # Example: GSM4972215_filtered_gene_bc_matrices-SLE1.tar.gz
    accession = name.split("_", 1)[0]
    label = name.split("-")[-1].replace(".tar.gz", "")
    disease_label = "SLE" if label.upper().startswith("SLE") else "HC"
    disease = "systemic lupus erythematosus" if disease_label == "SLE" else "normal"
    return {
        "sample_accession": accession,
        "sample_label": label,
        "donor_id": label,
        "disease": disease,
        "disease_label": disease_label,
    }


def make_unique(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out: list[str] = []
    for name in names:
        if name not in seen:
            seen[name] = 0
            out.append(name)
        else:
            seen[name] += 1
            out.append(f"{name}-{seen[name]}")
    return out


def read_inner_text(inner: tarfile.TarFile, name: str) -> str:
    handle = inner.extractfile(name)
    if handle is None:
        raise FileNotFoundError(name)
    return handle.read().decode("utf-8")


def read_sample_from_nested_tar(outer: tarfile.TarFile, member: tarfile.TarInfo) -> ad.AnnData:
    sample_meta = parse_sample_from_member(member.name)
    outer_handle = outer.extractfile(member)
    if outer_handle is None:
        raise FileNotFoundError(member.name)
    with tarfile.open(fileobj=outer_handle, mode="r:gz") as inner:
        barcodes = read_inner_text(inner, "barcodes.tsv").strip().splitlines()
        genes = pd.read_csv(io.StringIO(read_inner_text(inner, "genes.tsv")), sep="\t", header=None)
        if genes.shape[1] == 1:
            genes.columns = ["gene_symbol"]
            genes["gene_id"] = genes["gene_symbol"]
        else:
            genes = genes.iloc[:, :2]
            genes.columns = ["gene_id", "gene_symbol"]
        matrix_handle = inner.extractfile("matrix.mtx")
        if matrix_handle is None:
            raise FileNotFoundError("matrix.mtx")
        matrix = mmread(matrix_handle).tocsr().T

    obs = pd.DataFrame(index=[f"{sample_meta['sample_label']}_{barcode}" for barcode in barcodes])
    for key, value in sample_meta.items():
        obs[key] = value
    obs["barcode"] = barcodes
    var = genes.copy()
    var["gene_symbol_upper"] = var["gene_symbol"].astype(str).str.upper()
    var.index = make_unique(var["gene_symbol"].astype(str).tolist())
    return ad.AnnData(X=matrix, obs=obs, var=var)


def load_gse163121() -> ad.AnnData:
    raw_tar = SOURCE_DIR / "GSE163121_RAW.tar"
    if not raw_tar.exists():
        raise FileNotFoundError(f"Missing {raw_tar}. Run 00_download_gse163121_bcell_validation.ps1 first.")
    adatas = []
    with tarfile.open(raw_tar, "r") as outer:
        members = sorted([m for m in outer.getmembers() if m.name.endswith(".tar.gz")], key=lambda m: m.name)
        for member in members:
            print(f"Reading {member.name}")
            adatas.append(read_sample_from_nested_tar(outer, member))
    adata = ad.concat(adatas, join="outer", merge="first", index_unique=None)
    adata.X = adata.X.tocsr().astype(np.float32)
    adata.obs["n_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()
    adata.obs["n_genes"] = np.asarray((adata.X > 0).sum(axis=1)).ravel()
    return adata


def normalize_log_cp10k(counts: sparse.csr_matrix) -> sparse.csr_matrix:
    library_size = np.asarray(counts.sum(axis=1)).ravel().astype(np.float32)
    scale = np.divide(10000.0, library_size, out=np.zeros_like(library_size), where=library_size > 0)
    normalized = counts.multiply(scale[:, None]).tocsr()
    normalized.data = np.log1p(normalized.data)
    return normalized


def gene_index(adata: ad.AnnData) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, symbol in enumerate(adata.var["gene_symbol_upper"].astype(str)):
        mapping.setdefault(symbol, idx)
    return mapping


def score_programs(adata: ad.AnnData, log_cp10k: sparse.csr_matrix) -> tuple[pd.DataFrame, pd.DataFrame]:
    mapping = gene_index(adata)
    score_df = adata.obs[["sample_accession", "sample_label", "donor_id", "disease", "disease_label", "n_counts", "n_genes"]].copy()
    presence_rows = []
    for program, genes in PROGRAMS.items():
        present = [gene for gene in genes if gene.upper() in mapping]
        missing = [gene for gene in genes if gene.upper() not in mapping]
        idx = [mapping[gene.upper()] for gene in present]
        if idx:
            score_df[f"{program}_score"] = np.asarray(log_cp10k[:, idx].mean(axis=1)).ravel()
        else:
            score_df[f"{program}_score"] = np.nan
        presence_rows.append(
            {
                "program": program,
                "n_genes": len(genes),
                "n_present": len(present),
                "present_genes": ";".join(present),
                "missing_genes": ";".join(missing),
            }
        )
    return score_df, pd.DataFrame(presence_rows)


def summarize_scores(cell_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    program_cols = [col for col in cell_scores.columns if col.endswith("_score")]
    sample_scores = (
        cell_scores.groupby(["sample_accession", "sample_label", "disease", "disease_label"], observed=True)[program_cols]
        .mean()
        .reset_index()
    )
    threshold = float(cell_scores.loc[cell_scores["disease_label"] == "HC", "ABC_APC_focus_score"].quantile(0.95))
    cell_scores["ABC_APC_focus_high"] = cell_scores["ABC_APC_focus_score"] >= threshold
    high_fraction = (
        cell_scores.groupby(["sample_accession", "sample_label", "disease", "disease_label"], observed=True)["ABC_APC_focus_high"]
        .mean()
        .reset_index(name="ABC_APC_focus_high_fraction")
    )
    sample_scores = sample_scores.merge(high_fraction, on=["sample_accession", "sample_label", "disease", "disease_label"], how="left")
    sample_scores["ABC_APC_focus_high_threshold_hc95"] = threshold

    test_rows = []
    for metric in program_cols + ["ABC_APC_focus_high_fraction"]:
        hc = sample_scores.loc[sample_scores["disease_label"] == "HC", metric].dropna()
        sle = sample_scores.loc[sample_scores["disease_label"] == "SLE", metric].dropna()
        pvalue = np.nan
        statistic = np.nan
        if len(hc) > 0 and len(sle) > 0:
            result = mannwhitneyu(sle, hc, alternative="two-sided")
            statistic = float(result.statistic)
            pvalue = float(result.pvalue)
        test_rows.append(
            {
                "metric": metric,
                "n_hc": int(len(hc)),
                "n_sle": int(len(sle)),
                "mean_hc": float(hc.mean()) if len(hc) else np.nan,
                "mean_sle": float(sle.mean()) if len(sle) else np.nan,
                "delta_sle_minus_hc": float(sle.mean() - hc.mean()) if len(hc) and len(sle) else np.nan,
                "mannwhitney_u": statistic,
                "pvalue": pvalue,
            }
        )
    tests = pd.DataFrame(test_rows)
    tests["fdr"] = bh_fdr(tests["pvalue"].fillna(1.0).tolist())
    return cell_scores, sample_scores, tests


def marker_summary(adata: ad.AnnData, log_cp10k: sparse.csr_matrix) -> pd.DataFrame:
    mapping = gene_index(adata)
    rows = []
    counts = adata.X.tocsr()
    for gene in MARKER_GENES:
        idx = mapping.get(gene.upper())
        if idx is None:
            rows.append({"gene": gene, "present": False})
            continue
        for disease_label in ["HC", "SLE"]:
            mask = (adata.obs["disease_label"].to_numpy() == disease_label)
            gene_counts = counts[mask, idx]
            gene_expr = log_cp10k[mask, idx]
            rows.append(
                {
                    "gene": gene,
                    "present": True,
                    "disease_label": disease_label,
                    "mean_log_cp10k": float(np.asarray(gene_expr.mean(axis=0)).ravel()[0]),
                    "pct_detected": float(np.asarray((gene_counts > 0).mean(axis=0)).ravel()[0]),
                    "n_cells": int(mask.sum()),
                }
            )
    return pd.DataFrame(rows)


def write_summary(
    path: Path,
    adata: ad.AnnData,
    program_presence: pd.DataFrame,
    sample_scores: pd.DataFrame,
    tests: pd.DataFrame,
) -> None:
    abc = tests.loc[tests["metric"] == "ABC_APC_focus_score"].iloc[0]
    zeb2_axis = tests.loc[tests["metric"] == "ZEB2_TBX21_ITGAX_axis_score"].iloc[0]
    ifn = tests.loc[tests["metric"] == "IFN_ISG_score"].iloc[0]
    hla = tests.loc[tests["metric"] == "APC_HLA_score"].iloc[0]
    high = tests.loc[tests["metric"] == "ABC_APC_focus_high_fraction"].iloc[0]
    lines = [
        "# GSE163121 Independent B-Cell Validation Summary",
        "",
        "## Source",
        "",
        "- GEO accession: GSE163121.",
        "- Title: Single-cell RNA sequencing of B cells from healthy donors and SLE patients.",
        "- Design: healthy controls n=2 and SLE patients n=3, B cells isolated from PBMCs.",
        "- Role in manuscript: small independent B-cell validation dataset for directionality of ABC/APC-like, APC/HLA, IFN, and plasmablast-associated programs.",
        "",
        "## Parsed Data",
        "",
        f"- Cells loaded: {adata.n_obs:,}.",
        f"- Genes loaded: {adata.n_vars:,}.",
        f"- Samples: {adata.obs['sample_label'].nunique()}.",
        f"- HC cells: {(adata.obs['disease_label'] == 'HC').sum():,}.",
        f"- SLE cells: {(adata.obs['disease_label'] == 'SLE').sum():,}.",
        "",
        "## Main Directional Validation",
        "",
        f"- ZEB2/TBX21/ITGAX axis score delta, SLE minus HC: {zeb2_axis['delta_sle_minus_hc']:.4f}; sample-level p={zeb2_axis['pvalue']:.3g}; FDR={zeb2_axis['fdr']:.3g}.",
        f"- IFN/ISG score delta, SLE minus HC: {ifn['delta_sle_minus_hc']:.4f}; sample-level p={ifn['pvalue']:.3g}; FDR={ifn['fdr']:.3g}.",
        f"- ABC/APC focus composite score delta, SLE minus HC: {abc['delta_sle_minus_hc']:.4f}; sample-level p={abc['pvalue']:.3g}; FDR={abc['fdr']:.3g}.",
        f"- ABC/APC-high cell fraction delta, SLE minus HC: {high['delta_sle_minus_hc']:.4f}; sample-level p={high['pvalue']:.3g}; FDR={high['fdr']:.3g}.",
        f"- APC/HLA score delta, SLE minus HC: {hla['delta_sle_minus_hc']:.4f}; sample-level p={hla['pvalue']:.3g}; FDR={hla['fdr']:.3g}.",
        "",
        "## Interpretation Boundary",
        "",
        "This dataset is valuable because it is B-cell specific and independent of Perez/GSE174188, but the donor count is small. It supports the SLE B-cell ZEB2/TBX21/ITGAX and IFN activation axes directionally, while the global APC/HLA score is not increased. It should be presented as directional external B-cell validation and boundary evidence, not as a fully powered donor-level replication cohort.",
        "",
        "## Program Gene Coverage",
        "",
    ]
    for row in program_presence.itertuples(index=False):
        lines.append(f"- {row.program}: {row.n_present}/{row.n_genes} genes present.")
    lines.extend(["", "## Sample-Level Scores", ""])
    for row in sample_scores.itertuples(index=False):
        lines.append(f"- {row.sample_label} ({row.disease_label}): ABC/APC score={row.ABC_APC_focus_score:.4f}; ABC/APC-high fraction={row.ABC_APC_focus_high_fraction:.4f}.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_figure(path: Path, adata: ad.AnnData, sample_scores: pd.DataFrame, tests: pd.DataFrame, markers: pd.DataFrame) -> None:
    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    disease_palette = {"HC": "#8EA4B8", "SLE": "#D36B6B"}
    fig = plt.figure(figsize=nature_figsize(15, 10))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.2, 1.5], height_ratios=[1, 1], wspace=0.38, hspace=0.42)

    ax = fig.add_subplot(gs[0, 0])
    ax.axis("off")
    ax.text(-0.03, 1.05, "a", transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top")
    ax.text(
        0.02,
        0.98,
        "Independent B-cell validation\nGSE163121\n\nHC n=2, SLE n=3\nB cells isolated from PBMCs\n\nScores use log1p(CP10K)\nfrom CellRanger filtered matrices",
        va="top",
        ha="left",
        fontsize=6,
        linespacing=1.35,
    )

    ax = fig.add_subplot(gs[0, 1])
    ax.text(-0.16, 1.08, "b", transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top")
    counts = adata.obs.groupby(["sample_label", "disease_label"], observed=True).size().reset_index(name="n_cells")
    sns.barplot(data=counts, x="sample_label", y="n_cells", hue="disease_label", palette=disease_palette, ax=ax, dodge=False)
    ax.set_title("Cells per sample")
    ax.set_xlabel("")
    ax.set_ylabel("B cells")
    ax.tick_params(axis="x", rotation=35)
    ax.legend(title="", frameon=False)

    selected = ["ZEB2_TBX21_ITGAX_axis_score", "ABC_DN2_core_score", "ABC_APC_focus_score", "APC_HLA_score", "IFN_ISG_score"]
    plot_df = sample_scores.melt(
        id_vars=["sample_label", "disease_label"],
        value_vars=selected,
        var_name="program",
        value_name="score",
    )
    plot_df["program"] = plot_df["program"].str.replace("_score", "", regex=False).str.replace("_", "\n")
    ax = fig.add_subplot(gs[0, 2])
    ax.text(-0.12, 1.08, "c", transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top")
    sns.stripplot(data=plot_df, x="program", y="score", hue="disease_label", palette=disease_palette, dodge=True, size=2.2, ax=ax)
    ax.set_title("Sample-level program scores")
    ax.set_xlabel("")
    ax.set_ylabel("Mean score")
    ax.legend(title="", frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))

    ax = fig.add_subplot(gs[1, 0])
    ax.text(-0.16, 1.08, "d", transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top")
    sns.stripplot(
        data=sample_scores,
        x="disease_label",
        y="ABC_APC_focus_high_fraction",
        hue="disease_label",
        palette=disease_palette,
        size=2.5,
        ax=ax,
        legend=False,
    )
    sns.pointplot(
        data=sample_scores,
        x="disease_label",
        y="ABC_APC_focus_high_fraction",
        color="#333333",
        errorbar=None,
        markers="_",
        markersize=8,
        linestyles="",
        ax=ax,
    )
    high = tests.loc[tests["metric"] == "ABC_APC_focus_high_fraction"].iloc[0]
    ax.set_title("ABC/APC-high fraction\n(HC 95th percentile threshold)")
    ax.set_xlabel("")
    ax.set_ylabel("Fraction of B cells")
    ax.text(0.03, 0.95, f"Delta={high['delta_sle_minus_hc']:.3f}\np={high['pvalue']:.3g}", transform=ax.transAxes, va="top", fontsize=6)

    ax = fig.add_subplot(gs[1, 1:])
    ax.text(-0.08, 1.08, "e", transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top")
    marker_plot = markers[markers["present"]].copy()
    marker_plot["pct_size"] = marker_plot["pct_detected"] * 500
    y_order = ["HC", "SLE"]
    marker_plot["disease_label"] = pd.Categorical(marker_plot["disease_label"], categories=y_order, ordered=True)
    sns.scatterplot(
        data=marker_plot,
        x="gene",
        y="disease_label",
        size="pct_detected",
        sizes=(10, 110),
        hue="mean_log_cp10k",
        palette="viridis",
        edgecolor="#333333",
        linewidth=0.3,
        ax=ax,
    )
    ax.set_title("Marker expression by disease group")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=35)
    ax.legend(title="Mean / pct", frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")

    save_nature_figure(fig, path)
    plt.close(fig)


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    adata = load_gse163121()
    log_cp10k = normalize_log_cp10k(adata.X.tocsr())
    cell_scores, program_presence = score_programs(adata, log_cp10k)
    cell_scores, sample_scores, tests = summarize_scores(cell_scores)
    markers = marker_summary(adata, log_cp10k)

    adata.write_h5ad(PROCESSED_DIR / "gse163121_bcell_counts.h5ad", compression="gzip")
    cell_scores.to_csv(TABLE_DIR / "gse163121_cell_program_scores.csv", index=False)
    sample_scores.to_csv(TABLE_DIR / "gse163121_sample_program_scores.csv", index=False)
    tests.to_csv(TABLE_DIR / "gse163121_sample_program_score_tests.csv", index=False)
    program_presence.to_csv(TABLE_DIR / "gse163121_program_gene_presence.csv", index=False)
    markers.to_csv(TABLE_DIR / "gse163121_marker_summary_by_disease.csv", index=False)
    write_summary(OUT_DIR / "gse163121_bcell_validation_summary.md", adata, program_presence, sample_scores, tests)
    make_figure(FIG_DIR / "figure6_gse163121_independent_bcell_validation.png", adata, sample_scores, tests, markers)

    print(f"Wrote GSE163121 validation outputs to {OUT_DIR}")
    print(tests[["metric", "delta_sle_minus_hc", "pvalue", "fdr"]].to_string(index=False))


if __name__ == "__main__":
    main()
