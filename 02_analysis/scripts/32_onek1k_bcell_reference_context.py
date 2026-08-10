from __future__ import annotations

from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import sparse

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE196830_onek1k_cellxgene" / "source"
OUT_DIR = PROJECT_ROOT / "03_results" / "onek1k_bcell_reference_context"
TABLE_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"

H5AD = SOURCE_DIR / "onek1k_gse196830_cellxgene.h5ad"

B_CELL_REGEX = r"B cell|plasmablast|plasma cell"

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

MARKER_GENES = [
    "ZEB2",
    "TBX21",
    "ITGAX",
    "FCRL5",
    "FCRL3",
    "CD74",
    "HLA-DRA",
    "HLA-DRB1",
    "HLA-DPA1",
    "HLA-DPB1",
    "MS4A1",
    "ISG15",
    "IFIT1",
    "MX1",
    "TLR7",
    "FTO",
    "MZB1",
    "XBP1",
]

CELL_TYPE_LABELS = {
    "naive B cell": "Naive B",
    "memory B cell": "Memory B",
    "transitional stage B cell": "Transitional B",
    "plasmablast": "Plasmablast",
}


def gene_mapping(var: pd.DataFrame) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, symbol in enumerate(var.index.astype(str)):
        mapping.setdefault(symbol.upper(), idx)
    for column in ["feature_name", "gene_symbol", "gene_name", "name"]:
        if column not in var.columns:
            continue
        for idx, symbol in enumerate(var[column].astype(str)):
            mapping.setdefault(symbol.upper(), idx)
    return mapping


def unique_genes() -> list[str]:
    genes: list[str] = []
    for program_genes in PROGRAMS.values():
        genes.extend(program_genes)
    genes.extend(MARKER_GENES)
    return list(dict.fromkeys(genes))


def zscore_series(values: pd.Series) -> pd.Series:
    std = values.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.zeros(len(values)), index=values.index)
    return (values - values.mean()) / std


def normalize_target_counts(raw_target: sparse.spmatrix, library_size: np.ndarray) -> sparse.csr_matrix:
    counts = raw_target.tocsr().astype(np.float32)
    scale = np.divide(10000.0, library_size, out=np.zeros_like(library_size, dtype=np.float32), where=library_size > 0)
    normalized = counts.multiply(scale[:, None]).tocsr()
    normalized.data = np.log1p(normalized.data)
    return normalized


def score_programs(
    b_obs: pd.DataFrame,
    log_target: sparse.csr_matrix,
    target_positions: dict[str, int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scores = b_obs[["cell_type", "donor_id", "disease", "assay", "tissue", "nCount_RNA", "nFeature_RNA"]].copy()
    presence_rows = []
    for program, genes in PROGRAMS.items():
        present = [gene for gene in genes if gene in target_positions]
        missing = [gene for gene in genes if gene not in target_positions]
        idx = [target_positions[gene] for gene in present]
        scores[f"{program}_score"] = np.asarray(log_target[:, idx].mean(axis=1)).ravel() if idx else np.nan
        presence_rows.append(
            {
                "program": program,
                "n_genes": len(genes),
                "n_present": len(present),
                "present_genes": ";".join(present),
                "missing_genes": ";".join(missing),
            }
        )
    return scores, pd.DataFrame(presence_rows)


def summarize_programs(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    program_cols = [col for col in scores.columns if col.endswith("_score")]
    donor_cell_type = (
        scores.groupby(["donor_id", "cell_type"], observed=True)
        .agg(
            n_cells=("cell_type", "size"),
            disease=("disease", "first"),
            assay=("assay", "first"),
            tissue=("tissue", "first"),
            **{col: (col, "mean") for col in program_cols},
        )
        .reset_index()
    )
    cell_type_rows = []
    for cell_type, group in scores.groupby("cell_type", observed=True):
        row = {
            "cell_type": cell_type,
            "n_cells": int(len(group)),
            "n_donors": int(group["donor_id"].astype(str).nunique()),
        }
        for col in program_cols:
            values = group[col].dropna()
            row[f"{col}_mean"] = float(values.mean()) if len(values) else np.nan
            row[f"{col}_median"] = float(values.median()) if len(values) else np.nan
            row[f"{col}_q25"] = float(values.quantile(0.25)) if len(values) else np.nan
            row[f"{col}_q75"] = float(values.quantile(0.75)) if len(values) else np.nan
        cell_type_rows.append(row)
    return donor_cell_type, pd.DataFrame(cell_type_rows).sort_values("n_cells", ascending=False)


def summarize_markers(
    scores: pd.DataFrame,
    raw_target: sparse.csr_matrix,
    log_target: sparse.csr_matrix,
    target_positions: dict[str, int],
) -> pd.DataFrame:
    rows = []
    cell_types = scores["cell_type"].astype(str)
    donors = scores["donor_id"].astype(str)
    for cell_type in cell_types.drop_duplicates():
        mask = (cell_types == cell_type).to_numpy()
        n_cells = int(mask.sum())
        n_donors = int(donors.loc[mask].nunique())
        for gene in MARKER_GENES:
            if gene not in target_positions:
                rows.append(
                    {
                        "cell_type": cell_type,
                        "gene": gene,
                        "present": False,
                        "n_cells": n_cells,
                        "n_donors": n_donors,
                        "mean_log_cp10k": np.nan,
                        "pct_detected": np.nan,
                    }
                )
                continue
            j = target_positions[gene]
            raw_col = raw_target[mask, j]
            log_col = log_target[mask, j]
            rows.append(
                {
                    "cell_type": cell_type,
                    "gene": gene,
                    "present": True,
                    "n_cells": n_cells,
                    "n_donors": n_donors,
                    "mean_log_cp10k": float(np.asarray(log_col.mean(axis=0)).ravel()[0]),
                    "pct_detected": float((raw_col > 0).mean() * 100.0),
                }
            )
    return pd.DataFrame(rows)


def plot_reference_context(
    cell_type_summary: pd.DataFrame,
    marker_summary: pd.DataFrame,
    output: Path,
) -> None:
    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    order = cell_type_summary["cell_type"].head(12).tolist()
    order_labels = [CELL_TYPE_LABELS.get(cell_type, cell_type) for cell_type in order]
    program_cols = [col for col in cell_type_summary.columns if col.endswith("_score_mean")]
    heatmap = cell_type_summary.set_index("cell_type").loc[order, program_cols]
    heatmap.columns = [col.replace("_score_mean", "") for col in heatmap.columns]
    heatmap_z = heatmap.apply(zscore_series, axis=0)
    heatmap_z.index = order_labels
    program_labels = {
        "ABC_APC_focus": "ABC/APC focus",
        "ZEB2_TBX21_ITGAX_axis": "ZEB2/TBX21/ITGAX",
        "FCRL_axis": "FCRL axis",
        "HLA_CD74_axis": "HLA/CD74 axis",
        "ABC_DN2_core": "ABC/DN2 core",
        "APC_HLA": "APC/HLA",
        "IFN_ISG": "IFN/ISG",
        "Naive_B": "Naive B",
        "Plasmablast_ASC": "Plasmablast/ASC",
    }
    heatmap_z.columns = [program_labels.get(column, column) for column in heatmap_z.columns]

    selected_genes = [gene for gene in MARKER_GENES if gene in marker_summary.loc[marker_summary["present"], "gene"].unique()]
    dot = marker_summary[marker_summary["cell_type"].isin(order) & marker_summary["gene"].isin(selected_genes)].copy()
    dot["cell_type_label"] = dot["cell_type"].map(lambda value: CELL_TYPE_LABELS.get(str(value), str(value)))
    dot["cell_type_label"] = pd.Categorical(dot["cell_type_label"], categories=order_labels[::-1], ordered=True)
    dot["gene"] = pd.Categorical(dot["gene"], categories=selected_genes, ordered=True)

    fig = plt.figure(figsize=nature_figsize(14.5, 8.2), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.45])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    sns.heatmap(
        heatmap_z.T,
        cmap="vlag",
        center=0,
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"label": "Program score z-score"},
        ax=ax1,
    )
    ax1.text(-0.14, 1.07, "a", transform=ax1.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top")
    ax1.set_title("OneK1K B-lineage program context")
    ax1.set_xlabel("")
    ax1.set_ylabel("")
    ax1.set_xticklabels(["Naive", "Memory", "Transitional", "Plasmablast"], rotation=30, ha="right")

    sizes = dot["pct_detected"].fillna(0).clip(lower=0, upper=100)
    ax2.text(-0.08, 1.07, "b", transform=ax2.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", va="top")
    scatter = ax2.scatter(
        dot["gene"].astype(str),
        dot["cell_type_label"].astype(str),
        s=6 + sizes * 0.55,
        c=dot["mean_log_cp10k"],
        cmap="viridis",
        edgecolor="0.25",
        linewidth=0.25,
    )
    ax2.set_title("Marker expression across OneK1K B-lineage compartments")
    ax2.set_xlabel("")
    ax2.set_ylabel("")
    ax2.tick_params(axis="x", rotation=60)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    cbar = fig.colorbar(scatter, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("Mean log1p(CP10K)")
    for size, label in [(8, "low"), (32, "medium"), (60, "high")]:
        ax2.scatter([], [], s=size, c="lightgray", edgecolor="0.25", label=label)
    ax2.legend(
        title="% detected",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.24),
        ncol=3,
        frameon=False,
        columnspacing=0.8,
        handletextpad=0.35,
    )
    save_nature_figure(fig, output)
    plt.close(fig)


def write_summary(
    path: Path,
    n_total: int,
    n_b: int,
    n_donors: int,
    cell_type_counts: pd.DataFrame,
    program_presence: pd.DataFrame,
) -> None:
    full_programs = int((program_presence["n_present"] == program_presence["n_genes"]).sum())
    lines = [
        "# OneK1K B-Lineage Reference Context",
        "",
        "## Input",
        "",
        f"- Source H5AD: `{H5AD}`.",
        f"- Total cells in source: {n_total:,}.",
        f"- B-lineage-like cells analyzed: {n_b:,}.",
        f"- B-lineage-like donors analyzed: {n_donors:,}.",
        "",
        "## Normalization",
        "",
        "Target-gene raw counts from `X` were normalized as log1p(CP10K) using the full-library `nCount_RNA` metadata column. Only B-lineage-like cells and program/marker genes were loaded into memory.",
        "",
        "## Program Gene Coverage",
        "",
        f"- Programs with all genes present: {full_programs}/{len(program_presence)}.",
        "",
        "## Largest B-Lineage Compartments",
        "",
    ]
    for row in cell_type_counts.head(10).itertuples(index=False):
        lines.append(f"- {row.cell_type}: {row.n_cells:,} cells; {row.n_donors:,} donors.")
    lines.extend(
        [
            "",
            "## Recommended Manuscript Use",
            "",
            "Use this result as external B-lineage reference context for manuscript programs. Do not frame it as SLE-vs-control validation; GSE135779 remains the independent disease-validation cohort.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not H5AD.exists():
        raise FileNotFoundError(f"Missing {H5AD}. Run 00_download_onek1k_gse196830_cellxgene.ps1 first.")
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    adata = ad.read_h5ad(H5AD, backed="r")
    obs = adata.obs.copy()
    var = adata.var.copy()
    mapping = gene_mapping(var)

    missing_columns = [col for col in ["cell_type", "donor_id", "disease", "assay", "tissue", "nCount_RNA", "nFeature_RNA"] if col not in obs.columns]
    if missing_columns:
        raise KeyError(f"Required OneK1K metadata columns missing: {missing_columns}")

    b_mask = obs["cell_type"].astype(str).str.contains(B_CELL_REGEX, case=False, regex=True, na=False)
    b_obs = obs.loc[b_mask, ["cell_type", "donor_id", "disease", "assay", "tissue", "nCount_RNA", "nFeature_RNA"]].copy()
    genes = unique_genes()
    present_genes = [gene for gene in genes if gene.upper() in mapping]
    missing_genes = [gene for gene in genes if gene.upper() not in mapping]
    target_var_indices = [mapping[gene.upper()] for gene in present_genes]
    target_positions = {gene: idx for idx, gene in enumerate(present_genes)}

    print(f"Loading OneK1K B-lineage target matrix: {int(b_mask.sum()):,} cells x {len(target_var_indices):,} genes")
    raw_target = adata[b_mask.to_numpy(), target_var_indices].X
    if not sparse.issparse(raw_target):
        raw_target = sparse.csr_matrix(raw_target)
    raw_target = raw_target.tocsr().astype(np.float32)

    library_size = pd.to_numeric(b_obs["nCount_RNA"], errors="coerce").fillna(0).to_numpy(dtype=np.float32)
    log_target = normalize_target_counts(raw_target, library_size)

    scores, program_presence = score_programs(b_obs, log_target, target_positions)
    donor_cell_type, cell_type_summary = summarize_programs(scores)
    marker_summary = summarize_markers(scores, raw_target, log_target, target_positions)
    cell_type_counts = (
        b_obs.groupby("cell_type", observed=True)
        .agg(n_cells=("cell_type", "size"), n_donors=("donor_id", lambda x: x.astype(str).nunique()))
        .reset_index()
        .sort_values("n_cells", ascending=False)
    )

    program_presence.to_csv(TABLE_DIR / "onek1k_bcell_program_gene_presence.csv", index=False)
    target_presence = pd.DataFrame(
        [{"gene": gene, "present": gene in present_genes} for gene in genes]
    )
    target_presence.to_csv(TABLE_DIR / "onek1k_bcell_target_gene_presence.csv", index=False)
    cell_type_counts.to_csv(TABLE_DIR / "onek1k_bcell_cell_type_counts.csv", index=False)
    cell_type_summary.to_csv(TABLE_DIR / "onek1k_bcell_program_summary_by_cell_type.csv", index=False)
    donor_cell_type.to_csv(TABLE_DIR / "onek1k_bcell_program_summary_by_donor_cell_type.csv", index=False)
    marker_summary.to_csv(TABLE_DIR / "onek1k_bcell_marker_expression_by_cell_type.csv", index=False)
    scores.to_csv(TABLE_DIR / "onek1k_bcell_cell_program_scores.csv", index=False)

    plot_reference_context(cell_type_summary, marker_summary, FIG_DIR / "figure7_candidate_onek1k_bcell_reference_context.png")
    write_summary(
        OUT_DIR / "onek1k_bcell_reference_context_summary.md",
        adata.n_obs,
        len(b_obs),
        int(b_obs["donor_id"].astype(str).nunique()),
        cell_type_counts,
        program_presence,
    )
    adata.file.close()

    print(f"Wrote OneK1K B-cell reference context outputs to {OUT_DIR}")
    print(f"Present target genes: {len(present_genes)}; missing target genes: {len(missing_genes)}")
    print(cell_type_counts.to_string(index=False))


if __name__ == "__main__":
    main()
