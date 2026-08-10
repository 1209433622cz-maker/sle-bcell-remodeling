#!/usr/bin/env python3
"""Review residual Scrublet risk without applying a cell-exclusion rule."""

from __future__ import annotations

import argparse
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import spearmanr


MODULES = {
    "b_lineage": ["CD79A", "CD79B", "MS4A1", "CD19", "CD22", "CD37", "CD74", "HLA-DRA"],
    "t_nk": ["CD3D", "CD3E", "TRBC1", "TRBC2", "NKG7", "GNLY"],
    "myeloid": ["LST1", "TYROBP", "FCER1G", "S100A8", "S100A9", "FCGR3A"],
    "platelet": ["PPBP", "PF4", "NRGN"],
    "erythroid": ["HBB", "HBA1", "HBA2", "ALAS2"],
}


def gene_indices(adata: ad.AnnData, genes: list[str]) -> tuple[list[int], list[str]]:
    names = adata.var["feature_name"].astype(str) if "feature_name" in adata.var else pd.Series(adata.var_names)
    lookup: dict[str, int] = {}
    for idx, name in enumerate(names):
        lookup.setdefault(name.upper(), idx)
    found = [gene for gene in genes if gene.upper() in lookup]
    return [lookup[gene.upper()] for gene in found], found


def row_sum(matrix) -> np.ndarray:
    return np.asarray(matrix.sum(axis=1)).ravel()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5ad", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_h5ad = Path(args.input_h5ad).resolve()
    output = Path(args.output_dir).resolve()
    score_path = output / "06_full_cell_doublet_scores.csv.gz"
    summary_path = output / "05_full_library_doublet_summary.csv"
    if not score_path.is_file() or not summary_path.is_file():
        raise FileNotFoundError("Gate C2B1 score and library-summary files are required")

    adata = ad.read_h5ad(input_h5ad)
    forbidden = {"disease", "disease_state", "ct_cov"} & set(adata.obs.columns)
    if forbidden:
        raise RuntimeError(f"Protected fields leaked into working AnnData: {sorted(forbidden)}")

    scores = pd.read_csv(score_path, dtype={"cell_id": str, "library_uuid": str})
    if scores["cell_id"].duplicated().any():
        raise RuntimeError("Duplicate cell IDs in score table")
    aligned = scores.set_index("cell_id").reindex(adata.obs_names.astype(str))
    if aligned["library_uuid"].isna().any():
        raise RuntimeError("Score table does not cover every hard-QC cell")
    predicted = aligned["predicted_doublet"]
    if predicted.dtype != bool:
        predicted = predicted.astype(str).str.lower().map({"true": True, "false": False})
    if predicted.isna().any():
        raise RuntimeError("Unparseable predicted_doublet values")

    total_counts = row_sum(adata.X)
    if sparse.issparse(adata.X):
        detected_genes = np.asarray(adata.X.getnnz(axis=1)).ravel()
    else:
        detected_genes = np.count_nonzero(adata.X, axis=1)
    denominator = np.maximum(total_counts, 1)

    module_fractions: dict[str, np.ndarray] = {}
    module_coverage: list[dict] = []
    for module, genes in MODULES.items():
        indices, found = gene_indices(adata, genes)
        values = row_sum(adata.X[:, indices]) / denominator if indices else np.zeros(adata.n_obs)
        module_fractions[module] = values
        module_coverage.append(
            {"module": module, "requested_genes": len(genes), "found_genes": len(found), "genes": " | ".join(found)}
        )

    diagnostics = pd.DataFrame(
        {
            "cell_id": adata.obs_names.astype(str),
            "source_cell_index": adata.obs["source_cell_index"].to_numpy(),
            "library_uuid": adata.obs["library_uuid"].astype(str).to_numpy(),
            "doublet_score": aligned["doublet_score"].to_numpy(),
            "predicted_doublet": predicted.to_numpy(),
            "total_counts": total_counts,
            "detected_genes": detected_genes,
            **{f"fraction_{name}": values for name, values in module_fractions.items()},
        }
    )
    non_b_cols = [f"fraction_{name}" for name in ("t_nk", "myeloid", "platelet", "erythroid")]
    diagnostics["max_non_b_fraction"] = diagnostics[non_b_cols].max(axis=1)
    diagnostics.to_csv(output / "10_residual_doublet_cell_diagnostics.csv.gz", index=False, compression="gzip")
    pd.DataFrame(module_coverage).to_csv(output / "11_residual_doublet_module_coverage.csv", index=False)

    metrics = ["doublet_score", "total_counts", "detected_genes", "fraction_b_lineage", *non_b_cols, "max_non_b_fraction"]
    group_rows = []
    for flag, frame in diagnostics.groupby("predicted_doublet", observed=False):
        for metric in metrics:
            values = frame[metric].dropna()
            group_rows.append(
                {
                    "predicted_doublet": bool(flag),
                    "metric": metric,
                    "n": int(len(values)),
                    "median": float(values.median()),
                    "q90": float(values.quantile(0.90)),
                    "q95": float(values.quantile(0.95)),
                }
            )
    pd.DataFrame(group_rows).to_csv(output / "12_residual_doublet_group_summary.csv", index=False)

    correlation_rows = []
    scored = diagnostics.dropna(subset=["doublet_score"])
    for metric in ["total_counts", "detected_genes", "fraction_b_lineage", *non_b_cols, "max_non_b_fraction"]:
        rho, p_value = spearmanr(scored["doublet_score"], scored[metric], nan_policy="omit")
        correlation_rows.append({"metric": metric, "spearman_rho": rho, "p_value": p_value, "n": len(scored)})
    correlations = pd.DataFrame(correlation_rows)
    correlations.to_csv(output / "13_residual_doublet_score_correlations.csv", index=False)

    library = pd.read_csv(summary_path, dtype={"library_uuid": str})
    library_qc = diagnostics.groupby("library_uuid", observed=False).agg(
        median_total_counts=("total_counts", "median"),
        median_detected_genes=("detected_genes", "median"),
        median_non_b_fraction=("max_non_b_fraction", "median"),
    ).reset_index()
    library = library.merge(library_qc, on="library_uuid", how="left", validate="one_to_one")
    library.to_csv(output / "14_residual_doublet_library_review.csv", index=False)

    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    finite = scored[np.isfinite(scored["doublet_score"])].copy()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.6))
    axes[0, 0].hist(finite["doublet_score"], bins=60, color="#4477AA", edgecolor="white")
    axes[0, 0].set(xlabel="Residual Scrublet score", ylabel="Cells")
    axes[0, 1].hexbin(np.log10(finite["total_counts"] + 1), finite["doublet_score"], gridsize=45, mincnt=1, cmap="Greys")
    axes[0, 1].set(xlabel="log10(total counts + 1)", ylabel="Residual Scrublet score")
    axes[1, 0].hexbin(finite["max_non_b_fraction"] * 100, finite["doublet_score"], gridsize=45, mincnt=1, cmap="Greys")
    axes[1, 0].set(xlabel="Maximum non-B marker fraction (%)", ylabel="Residual Scrublet score")
    ok_library = library[library["status"].isin(["ok", "resumed"])]
    axes[1, 1].scatter(ok_library["n_cells"], ok_library["predicted_doublet_fraction"] * 100, s=16, color="#CC6677")
    axes[1, 1].set(xlabel="Eligible cells per library", ylabel="Automatic calls (%)")
    for axis in axes.ravel():
        axis.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figures / "residual_doublet_multimetric_review.png", dpi=300, facecolor="white")
    fig.savefig(figures / "residual_doublet_multimetric_review.pdf", facecolor="white")
    plt.close(fig)

    top_correlations = correlations.reindex(correlations["spearman_rho"].abs().sort_values(ascending=False).index).head(4)
    correlation_text = "\n".join(
        f"- {row.metric}: Spearman rho {row.spearman_rho:.3f} (n = {int(row.n):,})"
        for row in top_correlations.itertuples(index=False)
    )
    predicted_fraction = diagnostics["predicted_doublet"].mean()
    report = f"""# Gate C2B1 residual doublet multimetric assessment

**Status:** REVIEW REQUIRED; no exclusion mask has been frozen or applied.

- Hard-QC cells reviewed: {len(diagnostics):,}
- Cells with residual Scrublet scores: {diagnostics['doublet_score'].notna().sum():,}
- Automatic residual-risk calls: {diagnostics['predicted_doublet'].sum():,} ({predicted_fraction:.2%})
- Protected outcome fields in the working object: none

## Strongest score associations

{correlation_text}

## Binding interpretation

This pass evaluates residual doublet risk after the source workflow; automatic
calls do not by themselves justify a second deletion step. Review library-level
extremes, RNA-content association, mixed-lineage marker fractions and, after
Gate C2B2, localization in the disease-blind state graph.

Carry `all-hard-QC` as the primary branch. Define a high-confidence-singlet
sensitivity branch only after the multimetric and cluster-localization review,
and report whether composition and within-state conclusions are robust to it.
"""
    (output / "15_GATE_C2B1_RESIDUAL_DOUBLET_ASSESSMENT.md").write_text(report, encoding="utf-8")
    print(output / "15_GATE_C2B1_RESIDUAL_DOUBLET_ASSESSMENT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
