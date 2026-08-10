from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests


def main() -> None:
    parser = argparse.ArgumentParser(description="Test donor-level B-cell cluster fractions by disease.")
    parser.add_argument("--scores", required=True, help="bcell_obs_scores.csv")
    parser.add_argument("--output", required=True, help="Output CSV")
    args = parser.parse_args()

    df = pd.read_csv(args.scores, index_col=0)
    required = {"donor_id", "disease", "leiden"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {', '.join(sorted(missing))}")

    donor_meta = df[["donor_id", "disease"]].drop_duplicates()
    cluster_counts = df.groupby(["donor_id", "leiden"], observed=True).size().rename("n").reset_index()
    donor_totals = df.groupby("donor_id", observed=True).size().rename("donor_total").reset_index()
    clusters = sorted(df["leiden"].astype(str).unique(), key=lambda x: int(x) if x.isdigit() else x)
    donors = donor_meta["donor_id"].astype(str).unique()

    grid = pd.MultiIndex.from_product([donors, clusters], names=["donor_id", "leiden"]).to_frame(index=False)
    donor_cluster = (
        grid.merge(cluster_counts.assign(donor_id=lambda x: x["donor_id"].astype(str), leiden=lambda x: x["leiden"].astype(str)), how="left")
        .merge(donor_totals.assign(donor_id=lambda x: x["donor_id"].astype(str)), on="donor_id", how="left")
        .merge(donor_meta.assign(donor_id=lambda x: x["donor_id"].astype(str)), on="donor_id", how="left")
    )
    donor_cluster["n"] = donor_cluster["n"].fillna(0)
    donor_cluster["fraction_within_donor"] = donor_cluster["n"] / donor_cluster["donor_total"]

    rows = []
    for cluster in clusters:
        sub = donor_cluster[donor_cluster["leiden"] == cluster]
        normal = sub.loc[sub["disease"] == "normal", "fraction_within_donor"].to_numpy()
        sle = sub.loc[sub["disease"] == "systemic lupus erythematosus", "fraction_within_donor"].to_numpy()
        if len(normal) == 0 or len(sle) == 0:
            pvalue = np.nan
            statistic = np.nan
        else:
            test = mannwhitneyu(sle, normal, alternative="two-sided")
            pvalue = float(test.pvalue)
            statistic = float(test.statistic)
        rows.append(
            {
                "leiden": cluster,
                "n_donors_normal": len(normal),
                "n_donors_sle": len(sle),
                "mean_fraction_normal": float(np.mean(normal)) if len(normal) else np.nan,
                "mean_fraction_sle": float(np.mean(sle)) if len(sle) else np.nan,
                "median_fraction_normal": float(np.median(normal)) if len(normal) else np.nan,
                "median_fraction_sle": float(np.median(sle)) if len(sle) else np.nan,
                "mean_difference_sle_minus_normal": float(np.mean(sle) - np.mean(normal)) if len(normal) and len(sle) else np.nan,
                "mannwhitney_u": statistic,
                "pvalue": pvalue,
            }
        )

    out = pd.DataFrame(rows)
    valid = out["pvalue"].notna()
    out["fdr_bh"] = np.nan
    if valid.any():
        out.loc[valid, "fdr_bh"] = multipletests(out.loc[valid, "pvalue"], method="fdr_bh")[1]
    out = out.sort_values(["fdr_bh", "pvalue"], na_position="last")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False, encoding="utf-8-sig")
    print(out.to_string(index=False))
    print(f"\nWrote: {output}")


if __name__ == "__main__":
    main()
