from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def fraction_table(df: pd.DataFrame, group_col: str, cluster_col: str = "leiden") -> pd.DataFrame:
    counts = df.groupby([group_col, cluster_col], observed=True).size().rename("n").reset_index()
    group_totals = counts.groupby(group_col, observed=True)["n"].transform("sum")
    cluster_totals = counts.groupby(cluster_col, observed=True)["n"].transform("sum")
    counts["fraction_within_group"] = counts["n"] / group_totals
    counts["fraction_within_cluster"] = counts["n"] / cluster_totals
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Create B-cell cluster composition tables.")
    parser.add_argument("--scores", required=True, help="bcell_obs_scores.csv")
    parser.add_argument("--outdir", required=True, help="Output directory")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.scores, index_col=0)

    if "leiden" not in df.columns:
        raise SystemExit("Input must contain a 'leiden' column.")

    for col in ["disease", "disease_state", "ct_cov", "author_cell_type", "cell_type"]:
        if col in df.columns:
            fraction_table(df, col).to_csv(outdir / f"cluster_by_{col}.csv", index=False, encoding="utf-8-sig")

    if {"donor_id", "disease", "leiden"}.issubset(df.columns):
        donor_counts = df.groupby(["donor_id", "disease", "leiden"], observed=True).size().rename("n").reset_index()
        donor_counts["donor_total_bcells"] = donor_counts.groupby("donor_id", observed=True)["n"].transform("sum")
        donor_counts["fraction_within_donor"] = donor_counts["n"] / donor_counts["donor_total_bcells"]
        donor_counts.to_csv(outdir / "donor_cluster_fractions.csv", index=False, encoding="utf-8-sig")

        donor_summary = (
            donor_counts.groupby(["disease", "leiden"], observed=True)["fraction_within_donor"]
            .agg(["count", "mean", "median", "std"])
            .reset_index()
        )
        donor_summary.to_csv(outdir / "donor_cluster_fraction_summary_by_disease.csv", index=False, encoding="utf-8-sig")

    if {"donor_id", "disease_state", "leiden"}.issubset(df.columns):
        donor_state_counts = df.groupby(["donor_id", "disease_state", "leiden"], observed=True).size().rename("n").reset_index()
        donor_state_counts["donor_total_bcells"] = donor_state_counts.groupby("donor_id", observed=True)["n"].transform("sum")
        donor_state_counts["fraction_within_donor"] = donor_state_counts["n"] / donor_state_counts["donor_total_bcells"]
        donor_state_counts.to_csv(outdir / "donor_cluster_fractions_by_disease_state.csv", index=False, encoding="utf-8-sig")

    print(f"Wrote composition tables to: {outdir}")


if __name__ == "__main__":
    main()
