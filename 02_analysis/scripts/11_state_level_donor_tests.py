from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests


def main() -> None:
    parser = argparse.ArgumentParser(description="State-level donor fraction tests by disease.")
    parser.add_argument("--scores", required=True, help="Score table with draft_state")
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.scores, index_col=0)
    if not {"donor_id", "disease", "draft_state"}.issubset(df.columns):
        raise SystemExit("scores must contain donor_id, disease, and draft_state")

    donor_meta = df[["donor_id", "disease"]].drop_duplicates()
    states = list(pd.Series(df["draft_state"].dropna().unique()).sort_values())
    donors = donor_meta["donor_id"].astype(str).unique()
    counts = df.groupby(["donor_id", "draft_state"], observed=True).size().rename("n").reset_index()
    totals = df.groupby("donor_id", observed=True).size().rename("donor_total").reset_index()
    grid = pd.MultiIndex.from_product([donors, states], names=["donor_id", "draft_state"]).to_frame(index=False)
    donor_state = (
        grid.merge(counts.assign(donor_id=lambda x: x["donor_id"].astype(str)), how="left")
        .merge(totals.assign(donor_id=lambda x: x["donor_id"].astype(str)), how="left")
        .merge(donor_meta.assign(donor_id=lambda x: x["donor_id"].astype(str)), how="left")
    )
    donor_state["n"] = donor_state["n"].fillna(0)
    donor_state["fraction_within_donor"] = donor_state["n"] / donor_state["donor_total"]

    rows = []
    for state in states:
        sub = donor_state[donor_state["draft_state"] == state]
        normal = sub.loc[sub["disease"] == "normal", "fraction_within_donor"].to_numpy()
        sle = sub.loc[sub["disease"] == "systemic lupus erythematosus", "fraction_within_donor"].to_numpy()
        test = mannwhitneyu(sle, normal, alternative="two-sided")
        rows.append(
            {
                "draft_state": state,
                "n_donors_normal": len(normal),
                "n_donors_sle": len(sle),
                "mean_fraction_normal": float(np.mean(normal)),
                "mean_fraction_sle": float(np.mean(sle)),
                "median_fraction_normal": float(np.median(normal)),
                "median_fraction_sle": float(np.median(sle)),
                "mean_difference_sle_minus_normal": float(np.mean(sle) - np.mean(normal)),
                "pvalue": float(test.pvalue),
            }
        )
    tests = pd.DataFrame(rows)
    tests["fdr_bh"] = multipletests(tests["pvalue"], method="fdr_bh")[1]
    tests = tests.sort_values(["fdr_bh", "pvalue"])

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    donor_state.to_csv(outdir / "donor_state_fractions.csv", index=False, encoding="utf-8-sig")
    tests.to_csv(outdir / "donor_state_fraction_disease_tests.csv", index=False, encoding="utf-8-sig")
    print(tests.to_string(index=False))
    print(f"Wrote state-level outputs to: {outdir}")


if __name__ == "__main__":
    main()
