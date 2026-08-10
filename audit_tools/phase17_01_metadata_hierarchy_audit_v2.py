#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, os, re
from pathlib import Path
from typing import Any

REQ = ["donor_id","sample_uuid","library_uuid","Processing_Cohort","disease","disease_state","sex","self_reported_ethnicity","development_stage"]
SAMPLE_INV = ["donor_id","disease","disease_state","sex","self_reported_ethnicity","development_stage"]
DONOR_INV = ["disease","sex","self_reported_ethnicity"]

def decode(x: Any) -> str:
    return x.decode("utf-8", errors="replace") if isinstance(x, bytes) else str(x)

def read_vec(group, key):
    import numpy as np
    obj = group[key]
    if hasattr(obj, "keys") and "codes" in obj and "categories" in obj:
        codes = obj["codes"][:]
        cats = [decode(x) for x in obj["categories"][:]]
        return np.array([cats[int(i)] if 0 <= int(i) < len(cats) else "" for i in codes], dtype=object)
    return np.array([decode(x) for x in obj[:]], dtype=object)

def resolve(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else root / value.replace("\\", os.sep).replace("/", os.sep)

def join_unique(s):
    return " | ".join(sorted({str(x) for x in s if str(x) not in {"","nan","None","<NA>"}}))

def parse_age(x):
    m = re.search(r"(\d+(?:\.\d+)?)\s*-\s*year", str(x), re.I)
    return float(m.group(1)) if m else None

def manifest(df, group, cols):
    named = {"n_bcells": (group, "size")}
    for c in cols:
        named[f"{c}_n_unique"] = (c, "nunique")
        named[c] = (c, join_unique)
    return df.groupby(group, observed=True).agg(**named).reset_index()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--discovery", default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad")
    args = ap.parse_args()

    import h5py, pandas as pd
    root = Path(args.project_root).resolve(); src = resolve(root, args.discovery)
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    with h5py.File(src, "r") as f:
        obs = f["obs"]
        missing = [x for x in REQ if x not in obs]
        if missing: raise RuntimeError(f"Missing obs fields: {missing}")
        cells = pd.DataFrame({x: read_vec(obs, x) for x in REQ})
    cells["age_years"] = cells["development_stage"].map(parse_age)

    sample = manifest(cells, "sample_uuid", SAMPLE_INV + ["library_uuid","Processing_Cohort"])
    sample["biological_metadata_conflict"] = sample[[f"{x}_n_unique" for x in SAMPLE_INV]].gt(1).any(axis=1)
    sample["multi_library_sample"] = sample["library_uuid_n_unique"] > 1
    sample["multi_cohort_sample"] = sample["Processing_Cohort_n_unique"] > 1

    donor_cols = ["sample_uuid","library_uuid","Processing_Cohort","disease","disease_state","sex","self_reported_ethnicity","development_stage"]
    donor = manifest(cells, "donor_id", donor_cols)
    donor["repeated_sample_donor"] = donor["sample_uuid_n_unique"] > 1
    donor["multi_cohort_donor"] = donor["Processing_Cohort_n_unique"] > 1
    donor["multi_disease_state_donor"] = donor["disease_state_n_unique"] > 1
    donor["identity_metadata_conflict"] = donor[[f"{x}_n_unique" for x in DONOR_INV]].gt(1).any(axis=1)
    donor["primary_sample_status"] = donor["sample_uuid_n_unique"].map(lambda n: "single_sample_eligible" if int(n)==1 else "prespecified_rule_required")

    library = manifest(cells, "library_uuid", ["sample_uuid","donor_id","Processing_Cohort","disease"])
    library["library_cohort_conflict"] = library["Processing_Cohort_n_unique"] > 1
    library["mixed_disease_library"] = library["disease_n_unique"] > 1

    sl = cells.groupby(["sample_uuid","library_uuid"], observed=True).agg(
        n_bcells=("sample_uuid","size"), donor_id=("donor_id",join_unique),
        disease=("disease",join_unique), disease_state=("disease_state",join_unique),
        Processing_Cohort_n_unique=("Processing_Cohort","nunique"),
        Processing_Cohort=("Processing_Cohort",join_unique)
    ).reset_index()
    sl["record_conflict"] = sl["Processing_Cohort_n_unique"] > 1

    sc = cells.groupby(["sample_uuid","Processing_Cohort"], observed=True).agg(
        n_bcells=("sample_uuid","size"), n_libraries=("library_uuid","nunique"),
        donor_id=("donor_id",join_unique), disease=("disease",join_unique),
        disease_state=("disease_state",join_unique)
    ).reset_index()
    totals = cells.groupby("sample_uuid", observed=True).size().rename("sample_total_bcells").reset_index()
    sc = sc.merge(totals, on="sample_uuid", how="left")
    sc["cohort_cell_fraction_within_sample"] = sc["n_bcells"] / sc["sample_total_bcells"]

    support_sc = sc.groupby(["Processing_Cohort","disease"], observed=True).agg(
        n_sample_cohort_records=("sample_uuid","size"),
        n_unique_samples=("sample_uuid","nunique"),
        n_unique_donors=("donor_id","nunique"),
        n_bcells=("n_bcells","sum")
    ).reset_index()
    support_sl = sl.groupby(["Processing_Cohort","disease"], observed=True).agg(
        n_sample_library_records=("sample_uuid","size"),
        n_unique_samples_from_libraries=("sample_uuid","nunique"),
        n_unique_libraries=("library_uuid","nunique"),
        n_bcells_from_libraries=("n_bcells","sum")
    ).reset_index()
    support = support_sc.merge(support_sl, on=["Processing_Cohort","disease"], how="outer").fillna(0)

    conflicts = []
    for _, r in sample[sample["biological_metadata_conflict"]].iterrows():
        for field in SAMPLE_INV:
            if int(r[f"{field}_n_unique"]) > 1:
                conflicts.append({"level":"sample","id":r["sample_uuid"],"field":field,"n_unique":int(r[f"{field}_n_unique"]),"values":r[field],"interpretation":"unexpected biological inconsistency"})
    for _, r in donor[donor["identity_metadata_conflict"]].iterrows():
        for field in DONOR_INV:
            if int(r[f"{field}_n_unique"]) > 1:
                conflicts.append({"level":"donor","id":r["donor_id"],"field":field,"n_unique":int(r[f"{field}_n_unique"]),"values":r[field],"interpretation":"unexpected donor identity inconsistency"})
    for _, r in library[library["library_cohort_conflict"]].iterrows():
        conflicts.append({"level":"library","id":r["library_uuid"],"field":"Processing_Cohort","n_unique":int(r["Processing_Cohort_n_unique"]),"values":r["Processing_Cohort"],"interpretation":"unexpected technical-library inconsistency"})
    conflicts = pd.DataFrame(conflicts, columns=["level","id","field","n_unique","values","interpretation"])

    flags = sample.loc[sample["multi_library_sample"] | sample["multi_cohort_sample"],
        ["sample_uuid","n_bcells","library_uuid_n_unique","library_uuid","Processing_Cohort_n_unique","Processing_Cohort","multi_library_sample","multi_cohort_sample"]].copy()
    flags["interpretation"] = "expected technical multiplicity; not a biological conflict"

    sample.to_csv(out/"01_sample_manifest.csv",index=False,encoding="utf-8-sig")
    donor.to_csv(out/"02_donor_manifest.csv",index=False,encoding="utf-8-sig")
    library.to_csv(out/"03_library_manifest.csv",index=False,encoding="utf-8-sig")
    support.to_csv(out/"04_cohort_disease_common_support.csv",index=False,encoding="utf-8-sig")
    donor[donor["repeated_sample_donor"]].to_csv(out/"05_repeated_donor_manifest.csv",index=False,encoding="utf-8-sig")
    conflicts.to_csv(out/"06_metadata_conflicts.csv",index=False,encoding="utf-8-sig")
    sl.to_csv(out/"07_sample_library_manifest.csv",index=False,encoding="utf-8-sig")
    sc.to_csv(out/"08_sample_cohort_manifest.csv",index=False,encoding="utf-8-sig")
    flags.to_csv(out/"09_relationship_flags.csv",index=False,encoding="utf-8-sig")

    summary = f"""# Gate C1-01 metadata hierarchy audit v2

- Time: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}
- Cells: {len(cells):,}
- Samples: {sample.shape[0]:,}
- Donors: {donor.shape[0]:,}
- Libraries: {library.shape[0]:,}
- Repeated-sample donors: {int(donor['repeated_sample_donor'].sum()):,}
- Multi-library samples: {int(sample['multi_library_sample'].sum()):,}
- Multi-cohort samples: {int(sample['multi_cohort_sample'].sum()):,}
- Multi-cohort donors: {int(donor['multi_cohort_donor'].sum()):,}
- Multi-disease-state donors: {int(donor['multi_disease_state_donor'].sum()):,}
- True sample biological conflicts: {int(sample['biological_metadata_conflict'].sum()):,}
- True donor identity conflicts: {int(donor['identity_metadata_conflict'].sum()):,}
- Library cohort conflicts: {int(library['library_cohort_conflict'].sum()):,}
- Total true conflict rows: {len(conflicts):,}

Multiple libraries/cohorts per sample are technical multiplicity, not automatically metadata conflict.
Source was read only.
"""
    (out/"01_METADATA_HIERARCHY_SUMMARY.md").write_text(summary,encoding="utf-8")
    print(summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
