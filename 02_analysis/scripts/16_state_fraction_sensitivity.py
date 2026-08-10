from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests


def donor_state_fractions(
    obs: pd.DataFrame,
    donor_col: str,
    disease_col: str,
    state_col: str,
) -> pd.DataFrame:
    donor_disease = obs[[donor_col, disease_col]].drop_duplicates()
    if donor_disease[donor_col].duplicated().any():
        raise ValueError("At least one donor maps to multiple disease labels.")
    counts = obs.groupby([donor_col, state_col], observed=True).size().rename("n_cells").reset_index()
    totals = obs.groupby(donor_col, observed=True).size().rename("n_total_cells").reset_index()
    donors = donor_disease.merge(totals, on=donor_col, how="left")
    states = pd.DataFrame({state_col: sorted(obs[state_col].dropna().astype(str).unique())})
    grid = donors.assign(_key=1).merge(states.assign(_key=1), on="_key").drop(columns="_key")
    out = grid.merge(counts, on=[donor_col, state_col], how="left")
    out["n_cells"] = out["n_cells"].fillna(0).astype(int)
    out["fraction"] = out["n_cells"] / out["n_total_cells"]
    return out


def disease_tests(frac: pd.DataFrame, disease_col: str, state_col: str) -> pd.DataFrame:
    rows = []
    for state, sub in frac.groupby(state_col, observed=True):
        normal = sub.loc[sub[disease_col] == "normal", "fraction"].to_numpy(float)
        sle = sub.loc[sub[disease_col] == "systemic lupus erythematosus", "fraction"].to_numpy(float)
        if len(normal) == 0 or len(sle) == 0:
            pvalue = np.nan
            u_stat = np.nan
        else:
            stat = mannwhitneyu(sle, normal, alternative="two-sided")
            u_stat = float(stat.statistic)
            pvalue = float(stat.pvalue)
        rows.append(
            {
                state_col: state,
                "n_donors_normal": int(len(normal)),
                "n_donors_sle": int(len(sle)),
                "mean_fraction_normal": float(np.mean(normal)) if len(normal) else np.nan,
                "mean_fraction_sle": float(np.mean(sle)) if len(sle) else np.nan,
                "median_fraction_normal": float(np.median(normal)) if len(normal) else np.nan,
                "median_fraction_sle": float(np.median(sle)) if len(sle) else np.nan,
                "mean_difference_sle_minus_normal": float(np.mean(sle) - np.mean(normal)) if len(normal) and len(sle) else np.nan,
                "mannwhitney_u": u_stat,
                "pvalue": pvalue,
            }
        )
    out = pd.DataFrame(rows)
    mask = out["pvalue"].notna()
    out["fdr_bh"] = np.nan
    if mask.any():
        out.loc[mask, "fdr_bh"] = multipletests(out.loc[mask, "pvalue"], method="fdr_bh")[1]
    return out.sort_values("fdr_bh")


def main() -> None:
    parser = argparse.ArgumentParser(description="Recompute donor-level state fractions after excluding flagged states.")
    parser.add_argument("--scores", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--exclude-state", action="append", default=[])
    parser.add_argument("--donor-column", default="donor_id")
    parser.add_argument("--disease-column", default="disease")
    parser.add_argument("--state-column", default="draft_state")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    obs = pd.read_csv(args.scores, index_col=0, low_memory=False)
    obs[args.state_column] = obs[args.state_column].astype(str)
    before_cells = len(obs)
    if args.exclude_state:
        obs = obs[~obs[args.state_column].isin(args.exclude_state)].copy()
    after_cells = len(obs)

    frac = donor_state_fractions(obs, args.donor_column, args.disease_column, args.state_column)
    tests = disease_tests(frac, args.disease_column, args.state_column)
    metadata = pd.DataFrame(
        [
            {
                "input_cells": before_cells,
                "retained_cells": after_cells,
                "excluded_cells": before_cells - after_cells,
                "excluded_states": ";".join(args.exclude_state),
                "n_donors": int(obs[args.donor_column].nunique()),
            }
        ]
    )
    suffix = "exclude_" + "_".join(s.replace(" ", "_").replace("/", "-") for s in args.exclude_state) if args.exclude_state else "no_exclusion"
    frac.to_csv(outdir / f"donor_state_fractions_{suffix}.csv", index=False, encoding="utf-8-sig")
    tests.to_csv(outdir / f"donor_state_fraction_tests_{suffix}.csv", index=False, encoding="utf-8-sig")
    metadata.to_csv(outdir / f"sensitivity_metadata_{suffix}.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote sensitivity outputs to: {outdir}")
    print(metadata.to_string(index=False))
    print(tests.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
