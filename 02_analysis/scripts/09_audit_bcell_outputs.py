from __future__ import annotations

import argparse
import json
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd


def read_shape(path: Path) -> tuple[int, int]:
    obj = ad.read_h5ad(path, backed="r")
    shape = (int(obj.n_obs), int(obj.n_vars))
    obj.file.close()
    return shape


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit first-pass B-cell outputs for consistency.")
    parser.add_argument("--source-h5ad", required=True)
    parser.add_argument("--subset-h5ad", required=True)
    parser.add_argument("--processed-h5ad", required=True)
    parser.add_argument("--scores", required=True)
    parser.add_argument("--cluster-summary", required=True)
    parser.add_argument("--composition", required=True)
    parser.add_argument("--disease-tests", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    source = Path(args.source_h5ad)
    subset = Path(args.subset_h5ad)
    processed = Path(args.processed_h5ad)
    scores_path = Path(args.scores)
    summary_path = Path(args.cluster_summary)
    composition_path = Path(args.composition)
    disease_tests_path = Path(args.disease_tests)

    scores = pd.read_csv(scores_path, index_col=0)
    summary = pd.read_csv(summary_path)
    composition = pd.read_csv(composition_path)
    disease_tests = pd.read_csv(disease_tests_path)

    source_shape = read_shape(source)
    subset_shape = read_shape(subset)
    processed_shape = read_shape(processed)

    score_cols = [col for col in scores.columns if col.endswith("_score")]
    cluster_counts = scores["leiden"].astype(str).value_counts().sort_index(key=lambda s: s.astype(int))
    summary_counts = summary.set_index(summary["leiden"].astype(str))["IFN_response_score__count"].astype(int)
    summary_counts = summary_counts.sort_index(key=lambda s: s.astype(int))

    checks: dict[str, object] = {
        "source_h5ad_exists": source.exists(),
        "subset_h5ad_exists": subset.exists(),
        "processed_h5ad_exists": processed.exists(),
        "scores_csv_exists": scores_path.exists(),
        "source_shape": source_shape,
        "subset_shape": subset_shape,
        "processed_shape": processed_shape,
        "scores_rows": int(scores.shape[0]),
        "scores_columns": list(scores.columns),
        "score_columns": score_cols,
        "n_clusters": int(scores["leiden"].nunique()),
        "cluster_counts": cluster_counts.to_dict(),
        "summary_counts": summary_counts.to_dict(),
        "cluster_counts_match_summary": cluster_counts.to_dict() == summary_counts.to_dict(),
        "scores_rows_match_subset": int(scores.shape[0]) == subset_shape[0],
        "processed_rows_match_subset": processed_shape[0] == subset_shape[0],
        "processed_vars_match_subset": processed_shape[1] == subset_shape[1],
        "missing_score_values": {col: int(scores[col].isna().sum()) for col in score_cols},
        "metadata_missing_values": {
            col: int(scores[col].isna().sum())
            for col in ["cell_type", "author_cell_type", "disease", "disease_state", "donor_id", "ct_cov"]
            if col in scores.columns
        },
        "cell_type_counts": scores["cell_type"].value_counts(dropna=False).to_dict() if "cell_type" in scores else {},
        "author_cell_type_counts": scores["author_cell_type"].value_counts(dropna=False).to_dict()
        if "author_cell_type" in scores
        else {},
        "disease_counts_cells": scores["disease"].value_counts(dropna=False).to_dict() if "disease" in scores else {},
        "disease_counts_donors": scores[["donor_id", "disease"]].drop_duplicates()["disease"].value_counts().to_dict()
        if {"donor_id", "disease"}.issubset(scores.columns)
        else {},
        "disease_tests_rows": int(disease_tests.shape[0]),
        "best_disease_test": disease_tests.sort_values("fdr_bh").head(1).to_dict(orient="records"),
    }

    comp_sums = (
        composition.groupby(["variable", "leiden"], observed=True)["fraction_within_cluster"]
        .sum()
        .reset_index()
    )
    comp_complete = comp_sums[np.isclose(comp_sums["fraction_within_cluster"], 1.0, rtol=1e-6, atol=1e-6)]
    checks["composition_rows"] = int(composition.shape[0])
    checks["composition_complete_variable_cluster_pairs"] = int(comp_complete.shape[0])
    checks["composition_total_variable_cluster_pairs"] = int(comp_sums.shape[0])

    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(checks, indent=2, default=str), encoding="utf-8")

    lines = [
        "# B-cell First-Pass Output QA",
        "",
        "## Shapes",
        "",
        f"- Source H5AD: {source_shape[0]:,} cells x {source_shape[1]:,} features.",
        f"- B-cell subset H5AD: {subset_shape[0]:,} cells x {subset_shape[1]:,} features.",
        f"- Processed B-cell H5AD: {processed_shape[0]:,} cells x {processed_shape[1]:,} features.",
        f"- Score table rows: {scores.shape[0]:,}.",
        "",
        "## Core Consistency Checks",
        "",
        f"- Score rows match subset cells: {checks['scores_rows_match_subset']}.",
        f"- Processed rows match subset cells: {checks['processed_rows_match_subset']}.",
        f"- Cluster counts match cluster summary: {checks['cluster_counts_match_summary']}.",
        f"- Number of Leiden clusters: {checks['n_clusters']}.",
        "",
        "## Cell-Type Counts",
        "",
    ]
    for key, value in checks["cell_type_counts"].items():
        lines.append(f"- {key}: {value:,}")
    lines.extend(["", "## Donor Counts By Disease", ""])
    for key, value in checks["disease_counts_donors"].items():
        lines.append(f"- {key}: {value:,}")
    lines.extend(["", "## Missing Values", ""])
    for key, value in checks["metadata_missing_values"].items():
        lines.append(f"- {key}: {value:,}")
    lines.extend(["", "## Best Disease Test", ""])
    if checks["best_disease_test"]:
        row = checks["best_disease_test"][0]
        lines.append(
            f"- Cluster {row['leiden']}: mean SLE {row['mean_fraction_sle']:.4f}, "
            f"mean normal {row['mean_fraction_normal']:.4f}, FDR {row['fdr_bh']:.3e}."
        )
    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- The output is internally consistent for Phase 1.",
            "- Because the CELLxGENE matrix is preprocessed/scaled, these results are suitable for state mapping and figure planning, not final raw-count differential expression.",
            "- Donor-level cluster fraction tests reduce, but do not eliminate, pseudoreplication concerns.",
        ]
    )
    Path(args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
