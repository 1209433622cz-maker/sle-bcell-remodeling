from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_CATEGORICAL_COLUMNS = [
    "cell_type",
    "author_cell_type",
    "cell_state",
    "disease",
    "disease_state",
    "sex",
    "Processing_Cohort",
    "ct_cov",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize B-cell first-pass scores by Leiden cluster.")
    parser.add_argument("--scores", required=True, help="bcell_obs_scores.csv from first-pass workflow")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--composition-output", default="", help="Optional long-format cluster composition CSV path")
    args = parser.parse_args()

    scores = pd.read_csv(args.scores, index_col=0)
    score_cols = [col for col in scores.columns if col.endswith("_score")]
    summary = (
        scores.groupby("leiden", observed=True)[score_cols]
        .agg(["count", "mean", "median", "std"])
        .sort_index()
    )
    summary.columns = ["__".join(col).strip("_") for col in summary.columns.to_flat_index()]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, encoding="utf-8-sig")
    print(summary.to_string())
    print(f"\nWrote: {out}")

    categorical_cols = [col for col in DEFAULT_CATEGORICAL_COLUMNS if col in scores.columns]
    if categorical_cols:
        rows = []
        for col in categorical_cols:
            counts = scores.groupby(["leiden", col], observed=True).size().rename("n").reset_index()
            totals = counts.groupby("leiden", observed=True)["n"].transform("sum")
            counts["fraction_within_cluster"] = counts["n"] / totals
            counts.insert(1, "variable", col)
            counts = counts.rename(columns={col: "category"})
            rows.append(counts[["leiden", "variable", "category", "n", "fraction_within_cluster"]])
        comp = pd.concat(rows, ignore_index=True)
        comp_out = Path(args.composition_output) if args.composition_output else out.with_name("cluster_composition_long.csv")
        comp.to_csv(comp_out, index=False, encoding="utf-8-sig")
        print(f"Wrote: {comp_out}")


if __name__ == "__main__":
    main()
