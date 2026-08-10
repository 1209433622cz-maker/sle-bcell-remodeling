from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scanpy as sc
from scipy import sparse


SIGNATURES = {
    "IFN_response": ["ISG15", "IFIT1", "IFIT2", "IFIT3", "MX1", "MX2", "OAS1", "OAS2", "IFI44L", "IFI6"],
    "Antigen_presentation": ["HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1", "CD74", "CIITA", "CD86"],
    "ABC_DN2_axis": ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7"],
    "Plasmablast": ["MZB1", "XBP1", "PRDM1", "JCHAIN", "SDC1", "IRF4", "TNFRSF17"],
    "Naive_B": ["TCL1A", "IGHD", "IGHM", "IL4R", "FCER2", "CCR7"],
    "Activation": ["CD69", "CD83", "CD86", "NFKBIA", "JUNB", "FOS"],
}

METADATA_COLUMNS = [
    "cell_type",
    "author_cell_type",
    "cell_state",
    "disease",
    "disease_state",
    "donor_id",
    "sample_uuid",
    "sex",
    "Processing_Cohort",
    "ct_cov",
    "ind_cov",
]


def present_genes(adata, genes: list[str]) -> list[str]:
    var_names = set(map(str, adata.var_names))
    return [gene for gene in genes if gene in var_names]


def matrix_has_negative_values(adata) -> bool:
    x = adata.X
    if sparse.issparse(x):
        return bool(x.data.size and np.nanmin(x.data) < 0)
    return bool(np.nanmin(x) < 0)


def main() -> None:
    parser = argparse.ArgumentParser(description="First-pass Scanpy workflow for a B-cell H5AD subset.")
    parser.add_argument("--input", required=True, help="B-cell subset .h5ad")
    parser.add_argument("--outdir", default="03_results/first_pass_bcell", help="Output directory")
    parser.add_argument("--n-top-genes", type=int, default=3000)
    parser.add_argument("--resolution", type=float, default=0.6)
    parser.add_argument("--max-cells", type=int, default=0, help="Optional smoke-test downsample size; 0 uses all cells")
    parser.add_argument("--gene-symbol-column", default="", help="Optional adata.var column to use as gene symbols")
    parser.add_argument(
        "--matrix-mode",
        choices=["auto", "raw_counts", "preprocessed"],
        default="auto",
        help="auto detects negative values; use preprocessed for scaled/log-normalized CELLxGENE matrices",
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    figdir = outdir / "figures"
    tabledir = outdir / "tables"
    outdir.mkdir(parents=True, exist_ok=True)
    figdir.mkdir(parents=True, exist_ok=True)
    tabledir.mkdir(parents=True, exist_ok=True)

    sc.settings.figdir = str(figdir)
    sc.settings.verbosity = 2

    adata = sc.read_h5ad(args.input)
    if args.gene_symbol_column:
        if args.gene_symbol_column not in adata.var.columns:
            raise SystemExit(f"Gene symbol column not found in adata.var: {args.gene_symbol_column}")
        adata.var_names = adata.var[args.gene_symbol_column].astype(str).to_numpy()
        adata.var_names_make_unique()
        adata.var.index.name = None
        print(f"Using gene symbols from var column: {args.gene_symbol_column}")

    if args.max_cells and adata.n_obs > args.max_cells:
        sc.pp.subsample(adata, n_obs=args.max_cells, random_state=1)

    if args.matrix_mode == "auto":
        matrix_mode = "preprocessed" if matrix_has_negative_values(adata) else "raw_counts"
    else:
        matrix_mode = args.matrix_mode
    print(f"Matrix mode: {matrix_mode}")

    if matrix_mode == "raw_counts":
        adata.layers["counts"] = adata.X.copy()
        sc.pp.filter_genes(adata, min_cells=10)
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=args.n_top_genes, flavor="cell_ranger")
        sc.pp.scale(adata, max_value=10)
        sc.tl.pca(adata, svd_solver="arpack")
        sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
        sc.tl.umap(adata)
    else:
        # CELLxGENE commonly stores already transformed/scaled matrices.
        # Do not normalize/log1p again. Use provided PCA/UMAP when available.
        if "X_pca" in adata.obsm:
            sc.pp.neighbors(adata, n_neighbors=15, use_rep="X_pca")
        else:
            sc.pp.scale(adata, max_value=10)
            sc.tl.pca(adata, svd_solver="arpack")
            sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
        if "X_umap" not in adata.obsm:
            sc.tl.umap(adata)
    sc.tl.leiden(adata, resolution=args.resolution, key_added="leiden")

    for name, genes in SIGNATURES.items():
        genes_present = present_genes(adata, genes)
        print(f"{name}: {len(genes_present)} / {len(genes)} genes present")
        if len(genes_present) >= 2:
            sc.tl.score_genes(adata, genes_present, score_name=f"{name}_score", use_raw=False)
            (tabledir / f"{name}_genes_used.txt").write_text("\n".join(genes_present), encoding="utf-8")

    color = ["leiden"]
    score_cols = [f"{name}_score" for name in SIGNATURES if f"{name}_score" in adata.obs.columns]
    color.extend(score_cols)
    sc.pl.umap(adata, color=color, wspace=0.35, show=False, save="_bcell_first_pass_scores.png")
    plt.close("all")

    marker_genes = sorted({gene for genes in SIGNATURES.values() for gene in genes if gene in adata.var_names})
    if marker_genes:
        sc.pl.dotplot(
            adata,
            marker_genes,
            groupby="leiden",
            standard_scale="var",
            use_raw=False,
            show=False,
            save="_bcell_marker_dotplot.png",
        )
        plt.close("all")

    obs_cols = [col for col in METADATA_COLUMNS if col in adata.obs.columns]
    obs_cols = obs_cols + ["leiden"] + score_cols
    adata.obs[obs_cols].to_csv(tabledir / "bcell_obs_scores.csv", encoding="utf-8-sig")
    adata.raw = None
    adata.var.index.name = None
    adata.write_h5ad(outdir / "bcell_first_pass_processed.h5ad", compression="gzip")
    print(f"Wrote first-pass outputs to: {outdir}")


if __name__ == "__main__":
    main()
