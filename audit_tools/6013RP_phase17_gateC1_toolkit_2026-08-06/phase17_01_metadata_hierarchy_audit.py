#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 17 Gate C1-01: extract and audit donor/sample/library/cohort hierarchy.

Read-only for source H5AD. Outputs compact manifests and conflict tables.
No sample is automatically selected as the primary sample for repeated donors.
"""

from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

CORE = [
    "donor_id", "sample_uuid", "library_uuid", "Processing_Cohort",
    "disease", "disease_state", "sex", "self_reported_ethnicity",
    "development_stage",
]

def decode(x: Any) -> str:
    return x.decode("utf-8", errors="replace") if isinstance(x, bytes) else str(x)

def read_obs_column(obs, key: str):
    import numpy as np
    obj = obs[key]
    if hasattr(obj, "keys") and "codes" in obj and "categories" in obj:
        codes = obj["codes"][:]
        cats = [decode(x) for x in obj["categories"][:]]
        return np.array([cats[int(i)] if int(i) >= 0 else "" for i in codes], dtype=object)
    arr = obj[:]
    return np.array([decode(x) for x in arr], dtype=object)

def parse_age(value: str):
    m = re.search(r"(\d+(?:\.\d+)?)\s*-\s*year", str(value), flags=re.I)
    return float(m.group(1)) if m else None

def join_unique(series):
    vals = sorted({str(x) for x in series if str(x) not in {"", "nan", "None"}})
    return " | ".join(vals)

def resolve_project_path(root: Path, value: str) -> Path:
    """Resolve Windows- or POSIX-style project-relative paths."""
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    normalized = value.replace("\\", os.sep).replace("/", os.sep)
    return root / normalized

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=r"H:\cuhk-2025fALL\6013RP-wyf")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument(
        "--discovery",
        default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad",
    )
    args = ap.parse_args()

    import h5py
    import numpy as np
    import pandas as pd

    root = Path(args.project_root).resolve()
    source = resolve_project_path(root, args.discovery)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    with h5py.File(source, "r") as f:
        obs = f["obs"]
        missing = [x for x in CORE if x not in obs]
        if missing:
            raise RuntimeError(f"Missing required obs columns: {missing}")
        data = {key: read_obs_column(obs, key) for key in CORE}

    cells = pd.DataFrame(data)
    cells["age_years"] = cells["development_stage"].map(parse_age)

    # Sample manifest
    sample_fields = [
        "donor_id", "disease", "disease_state", "sex",
        "self_reported_ethnicity", "development_stage",
        "Processing_Cohort", "library_uuid",
    ]
    sample = (
        cells.groupby("sample_uuid", observed=True)
        .agg(
            n_bcells=("sample_uuid", "size"),
            **{f"{c}_n_unique": (c, "nunique") for c in sample_fields},
            **{c: (c, join_unique) for c in sample_fields},
            age_years=("age_years", "median"),
        )
        .reset_index()
    )
    sample["metadata_conflict"] = sample[
        [f"{c}_n_unique" for c in sample_fields]
    ].gt(1).any(axis=1)

    # Donor manifest
    donor_fields = [
        "sample_uuid", "library_uuid", "Processing_Cohort",
        "disease", "disease_state", "sex",
        "self_reported_ethnicity", "development_stage",
    ]
    donor = (
        cells.groupby("donor_id", observed=True)
        .agg(
            n_bcells=("donor_id", "size"),
            **{f"{c}_n_unique": (c, "nunique") for c in donor_fields},
            **{c: (c, join_unique) for c in donor_fields},
            age_years=("age_years", "median"),
        )
        .reset_index()
    )
    donor["repeated_sample_donor"] = donor["sample_uuid_n_unique"] > 1
    donor["multi_cohort_donor"] = donor["Processing_Cohort_n_unique"] > 1
    donor["multi_disease_state_donor"] = donor["disease_state_n_unique"] > 1
    donor["primary_sample_status"] = donor["sample_uuid_n_unique"].map(
        lambda x: "single_sample_eligible" if int(x) == 1 else "manual_rule_required"
    )

    # Library manifest
    library = (
        cells.groupby("library_uuid", observed=True)
        .agg(
            n_bcells=("library_uuid", "size"),
            n_samples=("sample_uuid", "nunique"),
            n_donors=("donor_id", "nunique"),
            Processing_Cohort=("Processing_Cohort", join_unique),
            disease=("disease", join_unique),
        )
        .reset_index()
    )

    support = (
        sample.groupby(["Processing_Cohort", "disease"], observed=True)
        .size().rename("n_samples").reset_index()
    )
    support_donor = (
        cells[["donor_id", "Processing_Cohort", "disease"]].drop_duplicates()
        .groupby(["Processing_Cohort", "disease"], observed=True)
        .size().rename("n_donor_cohort_records").reset_index()
    )
    support = support.merge(
        support_donor, on=["Processing_Cohort", "disease"], how="outer"
    ).fillna(0)

    conflicts = []
    for level_name, table, id_col in [
        ("sample", sample, "sample_uuid"),
        ("donor", donor, "donor_id"),
    ]:
        for col in table.columns:
            if col.endswith("_n_unique"):
                bad = table[table[col] > 1]
                for row in bad.itertuples(index=False):
                    conflicts.append({
                        "level": level_name,
                        "id": getattr(row, id_col),
                        "field": col[:-9],
                        "n_unique": getattr(row, col),
                        "values": getattr(row, col[:-9], ""),
                    })
    conflicts = pd.DataFrame(conflicts)

    sample.to_csv(out / "01_sample_manifest.csv", index=False, encoding="utf-8-sig")
    donor.to_csv(out / "02_donor_manifest.csv", index=False, encoding="utf-8-sig")
    library.to_csv(out / "03_library_manifest.csv", index=False, encoding="utf-8-sig")
    support.to_csv(out / "04_cohort_disease_common_support.csv", index=False, encoding="utf-8-sig")
    donor[donor["repeated_sample_donor"]].to_csv(
        out / "05_repeated_donor_manifest.csv", index=False, encoding="utf-8-sig"
    )
    conflicts.to_csv(out / "06_metadata_conflicts.csv", index=False, encoding="utf-8-sig")

    summary = f"""# Gate C1-01 metadata hierarchy audit

- Time: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}
- Cells: {len(cells):,}
- Samples: {sample['sample_uuid'].nunique():,}
- Donors: {donor['donor_id'].nunique():,}
- Libraries: {library['library_uuid'].nunique():,}
- Repeated-sample donors: {int(donor['repeated_sample_donor'].sum()):,}
- Multi-cohort donors: {int(donor['multi_cohort_donor'].sum()):,}
- Multi-disease-state donors: {int(donor['multi_disease_state_donor'].sum()):,}
- Sample-level metadata conflicts: {int(sample['metadata_conflict'].sum()):,}

No primary sample was automatically selected for repeated donors.
A prespecified biological rule is required before composition or pseudobulk models.
"""
    (out / "01_METADATA_HIERARCHY_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
