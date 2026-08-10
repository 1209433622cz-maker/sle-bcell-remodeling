#!/usr/bin/env python3
"""Recompute the strict donor-level cohort-by-disease support table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DISEASE_LABELS = {
    "normal": "Normal",
    "systemic lupus erythematosus": "SLE",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gatec1-dir", required=True)
    args = parser.parse_args()

    gatec1 = Path(args.gatec1_dir).resolve()
    donor_path = gatec1 / "02_donor_manifest.csv"
    donor = pd.read_csv(donor_path, dtype={"donor_id": str})

    required = {
        "donor_id",
        "sample_uuid_n_unique",
        "Processing_Cohort_n_unique",
        "Processing_Cohort",
        "disease_n_unique",
        "disease",
    }
    missing = sorted(required - set(donor.columns))
    if missing:
        raise RuntimeError(f"Missing donor-manifest fields: {missing}")
    if donor["donor_id"].duplicated().any():
        raise RuntimeError("Donor manifest contains duplicate donor_id rows")

    strict = donor.loc[
        donor["sample_uuid_n_unique"].eq(1)
        & donor["Processing_Cohort_n_unique"].eq(1)
        & donor["disease_n_unique"].eq(1)
    ].copy()
    strict["processing_cohort"] = strict["Processing_Cohort"].astype(float).astype(int)
    strict["disease_label"] = strict["disease"].map(DISEASE_LABELS)
    if strict["disease_label"].isna().any():
        unknown = sorted(strict.loc[strict["disease_label"].isna(), "disease"].unique())
        raise RuntimeError(f"Unmapped disease labels: {unknown}")

    index = pd.MultiIndex.from_product(
        [[1, 2, 3, 4], ["Normal", "SLE"]],
        names=["processing_cohort", "disease"],
    )
    support = (
        strict.groupby(["processing_cohort", "disease_label"], observed=False)
        .size()
        .reindex(index, fill_value=0)
        .rename("n_strict_biological_units")
        .reset_index()
    )
    if int(support["n_strict_biological_units"].sum()) != len(strict):
        raise RuntimeError("Strict support table does not reconcile to eligible donors")
    if len(strict) != 195:
        raise RuntimeError(f"Unexpected strict donor count: {len(strict)}")

    output_csv = gatec1 / "15_strict_common_support_reaudit.csv"
    output_md = gatec1 / "16_STRICT_COMMON_SUPPORT_ERRATUM.md"
    support.to_csv(output_csv, index=False)

    rows = "\n".join(
        f"| {row.processing_cohort} | {row.disease} | {row.n_strict_biological_units} |"
        for row in support.itertuples(index=False)
    )
    output_md.write_text(
        f"""# Gate C1 strict common-support re-audit

**Status:** corrected, programmatically reproducible table.  
**Source:** `{donor_path}`

## Binding definition

The strict subset contains donors represented by exactly one biological sample,
assigned to exactly one processing cohort, with one unambiguous disease label.
No sample is selected from a repeated-sample donor in this ambiguity-free
summary. The subset contains {len(strict)} donors.

| Processing cohort | Disease | Strict biological units |
|---:|---|---:|
{rows}

## Erratum

The earlier manually transcribed values 28/0, 1/78, 5/15 and 38/23 do not
reproduce from either Gate C1 manifest. They must not be used. The corrected
normal/SLE counts are 28/0, 1/87, 5/8 and 41/25 for cohorts 1-4, respectively.

This correction does not change the inferential ranking: cohort 4 remains the
primary direct comparison, cohort 3 remains small and exploratory, and cohorts
1-2 remain discovery/technical strata without credible direct disease support.
""",
        encoding="utf-8",
    )
    print(output_csv)
    print(output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
