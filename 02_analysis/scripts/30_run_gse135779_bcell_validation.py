from __future__ import annotations

import gzip
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
SOURCE_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE135779_nehar_validation" / "source"
PROCESSED_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE135779_nehar_validation"
OUT_DIR = PROJECT_ROOT / "03_results" / "gse135779_bcell_validation"
TABLE_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"

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


def read_genes() -> pd.DataFrame:
    genes = pd.read_csv(SOURCE_DIR / "GSE135779_genes.tsv.gz", sep="\t", header=None)
    genes = genes.iloc[:, :2]
    genes.columns = ["gene_id", "gene_symbol"]
    genes["gene_symbol_upper"] = genes["gene_symbol"].astype(str).str.upper()
    genes.index = make_unique(genes["gene_symbol"].astype(str).tolist())
    return genes


def load_extended_metadata() -> pd.DataFrame:
    meta = pd.read_csv(SOURCE_DIR / "Meta_caSLE_processed_08092021_small.csv")
    if "Unnamed: 0" in meta.columns:
        meta = meta.drop(columns=["Unnamed: 0"])
    meta["barcode"] = meta["index"].astype(str)
    meta["barcode_core"] = meta["barcode"].str.split("-").str[0]
    meta["sample_id"] = meta["IDs"].astype(str)
    meta["donor_name"] = meta["Names"].astype(str)
    meta["disease_label"] = meta["donor_name"].map(lambda x: "SLE" if "SLE" in str(x).upper() else ("HC" if "HD" in str(x).upper() else "unknown"))
    meta["disease"] = meta["disease_label"].map({"SLE": "systemic lupus erythematosus", "HC": "normal"}).fillna("unknown")
    meta["cohort"] = meta["donor_name"].map(lambda x: "adult" if str(x).startswith("a") else ("childhood" if str(x).startswith("c") else "unknown"))
    meta["is_b_subcluster"] = meta["subclusters"].astype(str).str.upper().str.startswith("B")
    return meta


def parse_tar_sample_names(raw_tar: Path) -> pd.DataFrame:
    rows = []
    with tarfile.open(raw_tar, "r") as tar:
        for name in tar.getnames():
            if not name.endswith("_barcodes.tsv.gz"):
                continue
            parts = name.split("_")
            rows.append(
                {
                    "accession": parts[0],
                    "sample_id": parts[1],
                    "barcode_file": name,
                    "matrix_file": name.replace("_barcodes.tsv.gz", "_matrix.mtx.gz"),
                }
            )
    return pd.DataFrame(rows).sort_values("sample_id")


def read_gzip_text_from_tar(tar: tarfile.TarFile, member_name: str) -> list[str]:
    handle = tar.extractfile(member_name)
    if handle is None:
        raise FileNotFoundError(member_name)
    with gzip.open(handle, "rt") as gz:
        return [line.strip() for line in gz if line.strip()]


def read_matrix_from_tar(tar: tarfile.TarFile, member_name: str) -> sparse.csr_matrix:
    handle = tar.extractfile(member_name)
    if handle is None:
        raise FileNotFoundError(member_name)
    with gzip.open(handle, "rb") as gz:
        return mmread(gz).tocsr()


def load_b_subcluster_anndata() -> tuple[ad.AnnData, pd.DataFrame]:
    raw_tar = SOURCE_DIR / "GSE135779_RAW.tar"
    if not raw_tar.exists():
        raise FileNotFoundError(f"Missing {raw_tar}. Run 00_download_gse135779_validation_sources.ps1 -DownloadRaw first.")

    genes = read_genes()
    meta = load_extended_metadata()
    b_meta = meta[meta["is_b_subcluster"] & meta["disease_label"].isin(["HC", "SLE"])].copy()
    samples = parse_tar_sample_names(raw_tar)
    adatas = []
    match_rows = []

    with tarfile.open(raw_tar, "r") as tar:
        for sample in samples.itertuples(index=False):
            sample_meta = b_meta[b_meta["sample_id"] == sample.sample_id].copy()
            if sample_meta.empty:
                match_rows.append({"sample_id": sample.sample_id, "n_b_metadata": 0, "n_matched": 0, "n_matrix_barcodes": 0})
                continue
            barcodes = read_gzip_text_from_tar(tar, sample.barcode_file)
            barcode_to_col = {barcode.split("-")[0]: idx for idx, barcode in enumerate(barcodes)}
            sample_meta["matrix_col"] = sample_meta["barcode_core"].map(barcode_to_col)
            matched = sample_meta["matrix_col"].notna()
            sample_meta = sample_meta.loc[matched].copy()
            match_rows.append(
                {
                    "sample_id": sample.sample_id,
                    "donor_name": sample_meta["donor_name"].iloc[0] if len(sample_meta) else "",
                    "disease_label": sample_meta["disease_label"].iloc[0] if len(sample_meta) else "",
                    "cohort": sample_meta["cohort"].iloc[0] if len(sample_meta) else "",
                    "n_b_metadata": int((b_meta["sample_id"] == sample.sample_id).sum()),
                    "n_matched": int(len(sample_meta)),
                    "n_matrix_barcodes": int(len(barcodes)),
                }
            )
            if sample_meta.empty:
                continue
            matrix = read_matrix_from_tar(tar, sample.matrix_file)
            cols = sample_meta["matrix_col"].astype(int).to_numpy()
            b_matrix = matrix[:, cols].T.tocsr().astype(np.float32)
            obs = sample_meta[
                ["barcode", "barcode_core", "sample_id", "donor_name", "disease", "disease_label", "cohort", "SLEDAI", "subclusters"]
            ].copy()
            obs.index = [f"{sample.sample_id}_{barcode}" for barcode in obs["barcode"]]
            adatas.append(ad.AnnData(X=b_matrix, obs=obs, var=genes.copy()))
            print(f"Loaded {sample.sample_id}: {len(obs)} B-subcluster cells")

    if not adatas:
        raise RuntimeError("No B-subcluster cells were matched to matrices.")
    adata = ad.concat(adatas, join="outer", merge="first", index_unique=None)
    adata.X = adata.X.tocsr().astype(np.float32)
    adata.obs["n_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()
    adata.obs["n_genes"] = np.asarray((adata.X > 0).sum(axis=1)).ravel()
    return adata, pd.DataFrame(match_rows)


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
    score_df = adata.obs[
        ["barcode", "sample_id", "donor_name", "disease", "disease_label", "cohort", "SLEDAI", "subclusters", "n_counts", "n_genes"]
    ].copy()
    presence_rows = []
    for program, genes in PROGRAMS.items():
        present = [gene for gene in genes if gene.upper() in mapping]
        missing = [gene for gene in genes if gene.upper() not in mapping]
        idx = [mapping[gene.upper()] for gene in present]
        score_df[f"{program}_score"] = np.asarray(log_cp10k[:, idx].mean(axis=1)).ravel() if idx else np.nan
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
    threshold = float(cell_scores.loc[cell_scores["disease_label"] == "HC", "ABC_APC_focus_score"].quantile(0.95))
    cell_scores["ABC_APC_focus_high"] = cell_scores["ABC_APC_focus_score"] >= threshold

    donor_scores = (
        cell_scores.groupby(["donor_name", "sample_id", "disease", "disease_label", "cohort"], observed=True)[program_cols]
        .mean()
        .reset_index()
    )
    donor_high = (
        cell_scores.groupby(["donor_name", "sample_id", "disease", "disease_label", "cohort"], observed=True)["ABC_APC_focus_high"]
        .mean()
        .reset_index(name="ABC_APC_focus_high_fraction")
    )
    donor_scores = donor_scores.merge(donor_high, on=["donor_name", "sample_id", "disease", "disease_label", "cohort"], how="left")
    donor_scores["ABC_APC_focus_high_threshold_hc95"] = threshold

    tests = []
    strata = [("all", donor_scores), ("childhood", donor_scores[donor_scores["cohort"] == "childhood"]), ("adult", donor_scores[donor_scores["cohort"] == "adult"])]
    for stratum, df in strata:
        for metric in program_cols + ["ABC_APC_focus_high_fraction"]:
            hc = df.loc[df["disease_label"] == "HC", metric].dropna()
            sle = df.loc[df["disease_label"] == "SLE", metric].dropna()
            pvalue = np.nan
            statistic = np.nan
            if len(hc) > 0 and len(sle) > 0:
                result = mannwhitneyu(sle, hc, alternative="two-sided")
                statistic = float(result.statistic)
                pvalue = float(result.pvalue)
            tests.append(
                {
                    "stratum": stratum,
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
    tests_df = pd.DataFrame(tests)
    tests_df["fdr"] = bh_fdr(tests_df["pvalue"].fillna(1.0).tolist())
    return cell_scores, donor_scores, tests_df


def marker_summary(adata: ad.AnnData, log_cp10k: sparse.csr_matrix) -> pd.DataFrame:
    mapping = gene_index(adata)
    counts = adata.X.tocsr()
    rows = []
    for gene in MARKER_GENES:
        idx = mapping.get(gene.upper())
        if idx is None:
            rows.append({"gene": gene, "present": False})
            continue
        for disease_label in ["HC", "SLE"]:
            mask = adata.obs["disease_label"].to_numpy() == disease_label
            if int(mask.sum()) == 0:
                rows.append(
                    {
                        "gene": gene,
                        "present": True,
                        "disease_label": disease_label,
                        "mean_log_cp10k": np.nan,
                        "pct_detected": np.nan,
                        "n_cells": 0,
                    }
                )
                continue
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


def subcluster_summary(cell_scores: pd.DataFrame) -> pd.DataFrame:
    return (
        cell_scores.groupby(["disease_label", "cohort", "subclusters"], observed=True)
        .size()
        .reset_index(name="n_cells")
        .sort_values(["disease_label", "cohort", "n_cells"], ascending=[True, True, False])
    )


def write_summary(
    path: Path,
    adata: ad.AnnData,
    match_summary: pd.DataFrame,
    program_presence: pd.DataFrame,
    donor_scores: pd.DataFrame,
    tests: pd.DataFrame,
) -> None:
    all_tests = tests[tests["stratum"] == "all"].set_index("metric")
    key_metrics = [
        "ABC_APC_focus_score",
        "ZEB2_TBX21_ITGAX_axis_score",
        "ABC_DN2_core_score",
        "APC_HLA_score",
        "IFN_ISG_score",
        "ABC_APC_focus_high_fraction",
    ]
    lines = [
        "# GSE135779 Independent B-Cell Validation Summary",
        "",
        "## Source And Role",
        "",
        "- GEO accession: GSE135779.",
        "- Role: larger independent SLE/control PBMC validation cohort using metadata-defined B-subcluster cells.",
        "- Parsed source: processed Matrix Market files from `GSE135779_RAW.tar` plus extended cell-level metadata.",
        "",
        "## Parsed Data",
        "",
        f"- B-subcluster cells loaded: {adata.n_obs:,}.",
        f"- Genes loaded: {adata.n_vars:,}.",
        f"- Donor/sample names: {adata.obs['donor_name'].nunique()}.",
        f"- HC donor/sample names: {donor_scores.loc[donor_scores['disease_label'] == 'HC', 'donor_name'].nunique()}.",
        f"- SLE donor/sample names: {donor_scores.loc[donor_scores['disease_label'] == 'SLE', 'donor_name'].nunique()}.",
        f"- Matched B metadata rows: {int(match_summary['n_matched'].sum()):,}.",
        "",
        "## All-Donor Validation Tests",
        "",
    ]
    for metric in key_metrics:
        if metric in all_tests.index:
            row = all_tests.loc[metric]
            lines.append(
                f"- {metric}: delta SLE-HC={row['delta_sle_minus_hc']:.4f}; n HC={int(row['n_hc'])}; n SLE={int(row['n_sle'])}; p={row['pvalue']:.3g}; FDR={row['fdr']:.3g}."
            )
    lines.extend(["", "## Program Gene Coverage", ""])
    for row in program_presence.itertuples(index=False):
        lines.append(f"- {row.program}: {row.n_present}/{row.n_genes} genes present.")
    lines.extend(
        [
            "",
            "## Interpretation Guidance",
            "",
            "Use GSE135779 as the main independent validation layer if ABC/DN2, ABC/APC-focus, or related high-fraction results are directionally consistent with the Perez/GSE174188 discovery analysis. Cohort-stratified results should be inspected before making final manuscript claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_figure(path: Path, adata: ad.AnnData, donor_scores: pd.DataFrame, tests: pd.DataFrame, markers: pd.DataFrame) -> None:
    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    palette = {"HC": "#8EA4B8", "SLE": "#D36B6B"}
    fig = plt.figure(figsize=nature_figsize(15.2, 10.2))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.25, 1.45], height_ratios=[1, 1], wspace=0.42, hspace=0.45)

    def panel_label(axis, label: str) -> None:
        axis.text(
            -0.08,
            1.02,
            label,
            transform=axis.transAxes,
            fontsize=PANEL_LABEL_SIZE,
            fontweight="bold",
            ha="right",
            va="bottom",
        )

    ax = fig.add_subplot(gs[0, 0])
    ax.axis("off")
    panel_label(ax, "a")
    ax.text(
        0.02,
        0.98,
        "GSE135779 validation\n\nMetadata-defined B-subcluster cells\nChildhood + adult SLE/control cohorts\n\nDonor/sample-level program scores\nlog1p(CP10K) from processed MTX",
        va="top",
        ha="left",
        fontsize=6,
        linespacing=1.35,
    )

    ax = fig.add_subplot(gs[0, 1])
    panel_label(ax, "b")
    donor_counts = donor_scores.groupby(["cohort", "disease_label"], observed=True)["donor_name"].nunique().reset_index(name="n_donors")
    sns.barplot(data=donor_counts, x="cohort", y="n_donors", hue="disease_label", palette=palette, ax=ax)
    ax.set_title("Donors by cohort")
    ax.set_xlabel("")
    ax.set_ylabel("Donor/sample names")
    ax.legend(title="", frameon=False)

    selected = ["ABC_APC_focus_score", "ABC_DN2_core_score", "ZEB2_TBX21_ITGAX_axis_score", "APC_HLA_score", "IFN_ISG_score"]
    plot_df = donor_scores.melt(id_vars=["donor_name", "disease_label"], value_vars=selected, var_name="program", value_name="score")
    plot_df["program"] = plot_df["program"].str.replace("_score", "", regex=False).str.replace("_", "\n")
    ax = fig.add_subplot(gs[0, 2])
    panel_label(ax, "c")
    sns.boxplot(data=plot_df, x="program", y="score", hue="disease_label", palette=palette, ax=ax, fliersize=0)
    sns.stripplot(
        data=plot_df,
        x="program",
        y="score",
        hue="disease_label",
        dodge=True,
        palette={"HC": "#222222", "SLE": "#222222"},
        alpha=0.35,
        size=1.6,
        ax=ax,
        legend=False,
    )
    ax.set_title("Independent program validation")
    ax.set_xlabel("")
    ax.set_ylabel("Mean score")
    ax.legend(title="", frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))

    ax = fig.add_subplot(gs[1, 0])
    panel_label(ax, "d")
    sns.boxplot(data=donor_scores, x="disease_label", y="ABC_APC_focus_high_fraction", hue="disease_label", palette=palette, ax=ax, fliersize=0, legend=False)
    sns.stripplot(data=donor_scores, x="disease_label", y="ABC_APC_focus_high_fraction", color="#222222", alpha=0.45, size=1.8, ax=ax)
    high = tests[(tests["stratum"] == "all") & (tests["metric"] == "ABC_APC_focus_high_fraction")].iloc[0]
    ax.set_title("ABC/APC-high cell fraction")
    ax.set_xlabel("")
    ax.set_ylabel("Fraction")
    ax.text(0.03, 0.95, f"Delta={high['delta_sle_minus_hc']:.3f}\nFDR={high['fdr']:.3g}", transform=ax.transAxes, va="top", fontsize=6)

    ax = fig.add_subplot(gs[1, 1:])
    panel_label(ax, "e")
    marker_plot = markers[markers["present"]].copy()
    marker_plot["disease_label"] = pd.Categorical(marker_plot["disease_label"], categories=["HC", "SLE"], ordered=True)
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
    ax.set_title("Marker expression")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=35)
    ax.legend(title="Mean / pct", frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")

    for axis in fig.axes:
        if axis.has_data():
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
    save_nature_figure(fig, path)
    plt.close(fig)


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    adata, match_summary = load_b_subcluster_anndata()
    log_cp10k = normalize_log_cp10k(adata.X.tocsr())
    cell_scores, program_presence = score_programs(adata, log_cp10k)
    cell_scores, donor_scores, tests = summarize_scores(cell_scores)
    markers = marker_summary(adata, log_cp10k)
    subclusters = subcluster_summary(cell_scores)

    adata.write_h5ad(PROCESSED_DIR / "gse135779_b_subcluster_counts.h5ad", compression="gzip")
    match_summary.to_csv(TABLE_DIR / "gse135779_bcell_matrix_metadata_match_summary.csv", index=False)
    cell_scores.to_csv(TABLE_DIR / "gse135779_bcell_program_scores.csv", index=False)
    donor_scores.to_csv(TABLE_DIR / "gse135779_donor_program_scores.csv", index=False)
    tests.to_csv(TABLE_DIR / "gse135779_donor_program_score_tests.csv", index=False)
    program_presence.to_csv(TABLE_DIR / "gse135779_program_gene_presence.csv", index=False)
    markers.to_csv(TABLE_DIR / "gse135779_marker_summary_by_disease.csv", index=False)
    subclusters.to_csv(TABLE_DIR / "gse135779_b_subcluster_counts_by_disease.csv", index=False)
    write_summary(OUT_DIR / "gse135779_bcell_validation_summary.md", adata, match_summary, program_presence, donor_scores, tests)
    make_figure(FIG_DIR / "figure6_gse135779_large_cohort_validation.png", adata, donor_scores, tests, markers)

    print(f"Wrote GSE135779 validation outputs to {OUT_DIR}")
    print(tests[(tests["stratum"] == "all")][["metric", "delta_sle_minus_hc", "pvalue", "fdr"]].to_string(index=False))


if __name__ == "__main__":
    main()
