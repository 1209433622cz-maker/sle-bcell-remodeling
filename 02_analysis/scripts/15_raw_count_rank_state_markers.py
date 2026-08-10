from __future__ import annotations

import argparse
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse


def to_csr(x) -> sparse.csr_matrix:
    if sparse.issparse(x):
        return x.tocsr()
    return sparse.csr_matrix(np.asarray(x))


def choose_balanced_cells(labels: pd.Series, max_cells_per_group: int, random_seed: int) -> np.ndarray:
    rng = np.random.default_rng(random_seed)
    chosen: list[np.ndarray] = []
    for group in pd.unique(labels):
        idx = np.flatnonzero(labels.to_numpy() == group)
        if max_cells_per_group > 0 and len(idx) > max_cells_per_group:
            idx = rng.choice(idx, size=max_cells_per_group, replace=False)
        chosen.append(np.sort(idx))
    return np.sort(np.concatenate(chosen))


def make_report(marker_df: pd.DataFrame, output: Path, top_n: int = 15) -> None:
    lines = [
        "# Raw-Count Ranked State Markers",
        "",
        "Markers were ranked on a balanced subset using raw counts, normalize_total, and log1p.",
        "This is suitable for annotation refinement. For final disease DE, use donor-aware pseudobulk/modeling.",
        "",
    ]
    for group in marker_df["group"].drop_duplicates():
        sub = marker_df[marker_df["group"] == group].head(top_n)
        lines.append(f"## {group}")
        for row in sub.itertuples(index=False):
            logfc = getattr(row, "logfoldchanges", np.nan)
            p_adj = getattr(row, "pvals_adj", np.nan)
            lines.append(f"- {row.names}: score {row.scores:.3f}; logFC {logfc:.3f}; FDR {p_adj:.3g}")
        lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank state marker genes from raw counts.")
    parser.add_argument("--input", required=True, help="B-cell subset h5ad containing .raw.X")
    parser.add_argument("--labels", required=True, help="CSV with obs index and state labels")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--state-column", default="draft_state")
    parser.add_argument("--gene-symbol-column", default="feature_name")
    parser.add_argument("--max-cells-per-state", type=int, default=3000)
    parser.add_argument("--method", default="t-test_overestim_var", choices=["t-test", "t-test_overestim_var", "wilcoxon"])
    parser.add_argument("--n-genes", type=int, default=100)
    parser.add_argument("--min-cells", type=int, default=20)
    parser.add_argument("--random-seed", type=int, default=13)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    tabledir = outdir / "tables"
    tabledir.mkdir(parents=True, exist_ok=True)

    labels = pd.read_csv(args.labels, index_col=0, low_memory=False)
    source = ad.read_h5ad(args.input, backed="r")
    if source.raw is None:
        raise SystemExit("Input AnnData has no .raw matrix.")
    labels = labels.reindex(source.obs_names)
    if labels[args.state_column].isna().any():
        raise SystemExit("Labels do not align with AnnData obs_names.")

    selected = choose_balanced_cells(labels[args.state_column].astype(str), args.max_cells_per_state, args.random_seed)
    print(f"Selected {len(selected):,} cells for marker ranking")
    obs = labels.iloc[selected].copy()
    x = to_csr(source.raw.X[selected, :])
    var = source.raw.var.copy()
    try:
        source.file.close()
    except Exception:
        pass

    adata = ad.AnnData(X=x, obs=obs, var=var)
    if args.gene_symbol_column not in adata.var.columns:
        raise SystemExit(f"Gene symbol column not found: {args.gene_symbol_column}")
    adata.var_names = adata.var[args.gene_symbol_column].astype(str).to_numpy()
    adata.var_names_make_unique()
    adata.var.index.name = None
    adata.obs[args.state_column] = adata.obs[args.state_column].astype(str).astype("category")

    sc.pp.filter_genes(adata, min_cells=args.min_cells)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.tl.rank_genes_groups(
        adata,
        groupby=args.state_column,
        method=args.method,
        n_genes=args.n_genes,
        corr_method="benjamini-hochberg",
    )
    marker_df = sc.get.rank_genes_groups_df(adata, group=None)
    marker_df.to_csv(tabledir / "raw_count_ranked_state_markers.csv", index=False, encoding="utf-8-sig")
    counts = obs[args.state_column].value_counts().rename_axis(args.state_column).reset_index(name="n_cells")
    counts.to_csv(tabledir / "raw_count_ranked_state_marker_cell_counts.csv", index=False, encoding="utf-8-sig")
    make_report(marker_df, outdir / "raw_count_ranked_state_markers_summary.md")
    print(f"Wrote ranked marker outputs to: {outdir}")


if __name__ == "__main__":
    main()
