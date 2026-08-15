#!/usr/bin/env python3
"""Gate C3-01: unlock protected metadata and freeze sample-level model designs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


REQUIRED_C2B4_DECISION = "PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED"
SOURCE_METADATA = [
    "library_uuid",
    "sample_uuid",
    "donor_id",
    "Processing_Cohort",
    "disease",
    "disease_state",
    "sex",
    "ct_cov",
    "ind_cov",
    "development_stage",
    "development_stage_ontology_term_id",
    "self_reported_ethnicity",
]
KEY_COLUMNS = ["library_uuid", "sample_uuid", "donor_id", "Processing_Cohort"]
SAMPLE_INVARIANTS = [
    "donor_id",
    "disease",
    "disease_state",
    "sex",
    "ind_cov",
    "development_stage",
    "development_stage_ontology_term_id",
    "self_reported_ethnicity",
]
KNOWN_B_CT_COV = {"B_naive", "B_mem", "B_atypical", "B_plasma"}
CLUSTER_TO_COMPARTMENT = {
    "0": "B_CONV",
    "1": "B_CONV",
    "2": "B_CONV",
    "3": "B_ASC",
    "4": "B_CONV",
}


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_manifest(root: Path, name: str):
    import pandas as pd

    table = pd.read_csv(root / name)
    failures = []
    for row in table.itertuples(index=False):
        path = root / str(row.relative_path)
        if not path.is_file():
            failures.append({"relative_path": row.relative_path, "issue": "missing"})
        elif path.stat().st_size != int(row.size_bytes):
            failures.append({"relative_path": row.relative_path, "issue": "size"})
        elif hash_file(path) != str(row.sha256).upper():
            failures.append({"relative_path": row.relative_path, "issue": "sha256"})
    return table, failures


def check(name: str, passed: bool, detail: str):
    return name, {"pass": bool(passed), "detail": detail}


def first_value(series):
    return series.iloc[0]


def joined_values(series) -> str:
    values = sorted(set(series.dropna().astype(str)))
    return "|".join(values)


def add_count_fields(table):
    table = table.copy()
    table["conv_cells"] = table["total_cells"] - table["asc_cells"]
    table["asc_fraction"] = table["asc_cells"] / table["total_cells"]
    table["asc_present"] = table["asc_cells"] > 0
    table["ct_cov_missing_fraction"] = table["ct_cov_missing_cells"] / table["total_cells"]
    table["explicit_non_b_fraction"] = table["explicit_non_b_cells"] / table["total_cells"]
    table["residual_doublet_fraction"] = table["residual_doublet_calls"] / table["total_cells"]
    return table


def numeric_rank(table, columns) -> int:
    import numpy as np

    return int(np.linalg.matrix_rank(table[columns].to_numpy(dtype=float)))


def build_model_matrix(table, analysis_id: str, states, extra_filter=None):
    import numpy as np

    work = table[table["disease_state"].isin(states)].copy()
    if extra_filter is not None:
        work = work.loc[extra_filter(work)].copy()
    work.insert(0, "analysis_id", analysis_id)
    work["intercept"] = 1.0
    work["age_centered"] = work["age_years"] - work["age_years"].mean()
    work["ethnicity_asian"] = (work["ethnicity"] == "Asian").astype(int)
    work["ethnicity_european"] = (work["ethnicity"] == "European American").astype(int)
    work["is_managed"] = (work["disease_state"] == "managed").astype(int)
    work["is_flare"] = (work["disease_state"] == "flare").astype(int)
    work["non_asc_cells"] = work["total_cells"] - work["asc_cells"]
    work["logit_start"] = np.log((work["asc_cells"] + 0.5) / (work["non_asc_cells"] + 0.5))
    return work.sort_values(["disease_state", "sample_uuid"]).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-h5ad", required=True)
    parser.add_argument("--source-h5ad", required=True)
    parser.add_argument("--gate-c2b4-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--minimum-cells", type=int, default=50)
    args = parser.parse_args()

    import anndata as ad
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    primary_path = Path(args.primary_h5ad).resolve()
    source_path = Path(args.source_h5ad).resolve()
    c2b4 = Path(args.gate_c2b4_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    figure_dir = output / "figures"
    figure_dir.mkdir(exist_ok=True)

    c2b4_manifest, c2b4_integrity_failures = verify_manifest(
        c2b4, "07_gate_c2b4_integrity_manifest.csv"
    )
    c2b4_decision = json.loads(
        (c2b4 / "06_GATE_C2B4_ADVISOR_DECISION.json").read_text(encoding="utf-8")
    )
    if c2b4_decision.get("decision") != REQUIRED_C2B4_DECISION:
        raise RuntimeError("Gate C2B4 has not authorized protected metadata unlock")
    if c2b4_decision.get("outcome_unlock_authorized") is not True:
        raise RuntimeError("Gate C2B4 outcome unlock flag is false")

    primary = ad.read_h5ad(primary_path, backed="r")
    source = ad.read_h5ad(source_path, backed="r")
    missing_source_columns = [column for column in SOURCE_METADATA if column not in source.obs]
    if missing_source_columns:
        raise RuntimeError(f"Source metadata columns are missing: {missing_source_columns}")
    if "leiden_harmony_r0_4" not in primary.obs:
        raise RuntimeError("Primary representation lacks r=0.4 source clusters")

    primary_ids = primary.obs_names.astype(str)
    source_ids = source.obs_names.astype(str)
    missing_cell_ids = primary_ids.difference(source_ids)
    joined = source.obs.reindex(primary_ids)[SOURCE_METADATA].copy()
    all_null_join_rows = int(joined.isna().all(axis=1).sum())
    for column in SOURCE_METADATA:
        if column != "ct_cov":
            joined[column] = joined[column].astype("string")
    joined["ct_cov"] = joined["ct_cov"].astype("string")

    key_mismatches = {}
    for column in KEY_COLUMNS:
        source_values = joined[column].astype(str).to_numpy()
        primary_values = primary.obs[column].astype(str).to_numpy()
        key_mismatches[column] = int((source_values != primary_values).sum())

    source_positions = primary.obs["source_cell_index"].astype(int).to_numpy()
    positional = source.obs.iloc[source_positions]
    positional_key_match = float(
        (
            positional["library_uuid"].astype(str).to_numpy()
            == primary.obs["library_uuid"].astype(str).to_numpy()
        ).mean()
    )

    cluster = primary.obs["leiden_harmony_r0_4"].astype(str)
    unexpected_clusters = sorted(set(cluster) - set(CLUSTER_TO_COMPARTMENT))
    if unexpected_clusters:
        raise RuntimeError(f"Unexpected r=0.4 clusters: {unexpected_clusters}")
    compartment = cluster.map(CLUSTER_TO_COMPARTMENT)
    age = joined["development_stage"].str.extract(r"(\d+)-year-old", expand=False)
    if age.isna().any():
        raise RuntimeError("Age could not be parsed for every primary cell")

    cell = pd.DataFrame(index=primary_ids)
    cell.index.name = "cell_id"
    cell["source_cell_index"] = primary.obs["source_cell_index"].astype(int).to_numpy()
    for column in SOURCE_METADATA:
        cell[column] = joined[column].to_numpy()
    cell["age_years"] = age.astype(float).to_numpy()
    cell["source_r04_cluster"] = cluster.to_numpy()
    cell["frozen_neutral_id"] = compartment.to_numpy()
    cell["ct_cov_missing"] = cell["ct_cov"].isna()
    cell["ct_cov_known_b"] = cell["ct_cov"].isin(KNOWN_B_CT_COV)
    cell["ct_cov_explicit_non_b"] = (~cell["ct_cov_missing"]) & (~cell["ct_cov_known_b"])
    cell["residual_doublet_auto_call"] = primary.obs[
        "residual_doublet_auto_call"
    ].astype(bool).to_numpy()
    cell["hard_naive_memory_label_authorized"] = False
    cell.to_csv(
        output / "01_unlocked_cell_metadata.csv.gz",
        index=True,
        compression="gzip",
        encoding="utf-8-sig",
    )

    for column in [
        "sample_uuid", "library_uuid", "donor_id", "Processing_Cohort", "disease",
        "disease_state", "sex", "ind_cov", "self_reported_ethnicity",
    ]:
        cell[column] = cell[column].astype("string")

    invariant_audit = []
    for column in SAMPLE_INVARIANTS:
        counts = cell.groupby("sample_uuid", observed=True)[column].nunique(dropna=False)
        invariant_audit.append(
            {
                "level": "sample_uuid",
                "field": column,
                "groups": int(len(counts)),
                "conflicting_groups": int((counts > 1).sum()),
                "maximum_values_per_group": int(counts.max()),
            }
        )
    for column in ["Processing_Cohort"]:
        counts = cell.groupby("library_uuid", observed=True)[column].nunique(dropna=False)
        invariant_audit.append(
            {
                "level": "library_uuid",
                "field": column,
                "groups": int(len(counts)),
                "conflicting_groups": int((counts > 1).sum()),
                "maximum_values_per_group": int(counts.max()),
            }
        )
    for column in ["disease", "sex", "ind_cov"]:
        counts = cell.groupby("donor_id", observed=True)[column].nunique(dropna=False)
        invariant_audit.append(
            {
                "level": "donor_id",
                "field": column,
                "groups": int(len(counts)),
                "conflicting_groups": int((counts > 1).sum()),
                "maximum_values_per_group": int(counts.max()),
            }
        )
    invariant_table = pd.DataFrame(invariant_audit)
    invariant_table.to_csv(
        output / "02_metadata_key_invariants.csv", index=False, encoding="utf-8-sig"
    )

    aggregation = {
        "total_cells": ("frozen_neutral_id", "size"),
        "asc_cells": ("frozen_neutral_id", lambda values: int((values == "B_ASC").sum())),
        "libraries": ("library_uuid", "nunique"),
        "cohorts": ("Processing_Cohort", "nunique"),
        "donor_id": ("donor_id", first_value),
        "disease": ("disease", first_value),
        "disease_state": ("disease_state", first_value),
        "sex": ("sex", first_value),
        "ind_cov": ("ind_cov", first_value),
        "age_years": ("age_years", first_value),
        "ethnicity": ("self_reported_ethnicity", first_value),
        "processing_cohorts": ("Processing_Cohort", joined_values),
        "ct_cov_missing_cells": ("ct_cov_missing", "sum"),
        "explicit_non_b_cells": ("ct_cov_explicit_non_b", "sum"),
        "residual_doublet_calls": ("residual_doublet_auto_call", "sum"),
    }
    sample = (
        cell.reset_index()
        .groupby("sample_uuid", observed=True)
        .agg(**aggregation)
        .reset_index()
    )
    sample = add_count_fields(sample)
    sample["eligible_minimum_cells"] = sample["total_cells"] >= args.minimum_cells
    sample.to_csv(output / "03_sample_design_audit.csv", index=False, encoding="utf-8-sig")

    stratum_aggregation = dict(aggregation)
    stratum_aggregation.pop("cohorts")
    stratum_aggregation.pop("processing_cohorts")
    stratum = (
        cell.reset_index()
        .groupby(["sample_uuid", "Processing_Cohort"], observed=True)
        .agg(**stratum_aggregation)
        .reset_index()
    )
    stratum = add_count_fields(stratum)
    stratum["eligible_minimum_cells"] = stratum["total_cells"] >= args.minimum_cells
    stratum.to_csv(
        output / "04_sample_cohort_design_audit.csv", index=False, encoding="utf-8-sig"
    )

    sample_long = sample.melt(
        id_vars=[
            "sample_uuid", "donor_id", "disease", "disease_state", "sex", "age_years",
            "ethnicity", "libraries", "cohorts", "processing_cohorts", "total_cells",
            "eligible_minimum_cells",
        ],
        value_vars=["conv_cells", "asc_cells"],
        var_name="compartment",
        value_name="cells",
    )
    sample_long["compartment"] = sample_long["compartment"].map(
        {"conv_cells": "B_CONV", "asc_cells": "B_ASC"}
    )
    sample_long["fraction"] = sample_long["cells"] / sample_long["total_cells"]
    sample_long.to_csv(
        output / "05_sample_compartment_counts.csv", index=False, encoding="utf-8-sig"
    )

    stratum_long = stratum.melt(
        id_vars=[
            "sample_uuid", "Processing_Cohort", "donor_id", "disease", "disease_state",
            "sex", "age_years", "ethnicity", "libraries", "total_cells",
            "eligible_minimum_cells",
        ],
        value_vars=["conv_cells", "asc_cells"],
        var_name="compartment",
        value_name="cells",
    )
    stratum_long["compartment"] = stratum_long["compartment"].map(
        {"conv_cells": "B_CONV", "asc_cells": "B_ASC"}
    )
    stratum_long["fraction"] = stratum_long["cells"] / stratum_long["total_cells"]
    stratum_long.to_csv(
        output / "06_sample_cohort_compartment_counts.csv", index=False, encoding="utf-8-sig"
    )

    donor = (
        cell.reset_index()
        .groupby("donor_id", observed=True)
        .agg(
            total_cells=("frozen_neutral_id", "size"),
            asc_cells=("frozen_neutral_id", lambda values: int((values == "B_ASC").sum())),
            samples=("sample_uuid", "nunique"),
            libraries=("library_uuid", "nunique"),
            cohorts=("Processing_Cohort", "nunique"),
            disease=("disease", joined_values),
            disease_states=("disease_state", joined_values),
            sex=("sex", joined_values),
            ind_cov=("ind_cov", joined_values),
        )
        .reset_index()
    )
    donor["asc_fraction"] = donor["asc_cells"] / donor["total_cells"]
    donor.to_csv(output / "07_donor_design_audit.csv", index=False, encoding="utf-8-sig")

    eligible = stratum[stratum["eligible_minimum_cells"]].copy()
    strata_counts = (
        eligible.groupby(["Processing_Cohort", "disease", "disease_state"], observed=True)
        .agg(
            strata=("sample_uuid", "size"),
            unique_samples=("sample_uuid", "nunique"),
            unique_donors=("donor_id", "nunique"),
            median_cells=("total_cells", "median"),
            minimum_cells=("total_cells", "min"),
            zero_asc_strata=("asc_cells", lambda values: int((values == 0).sum())),
        )
        .reset_index()
    )
    strata_counts.to_csv(
        output / "08_eligible_design_strata.csv", index=False, encoding="utf-8-sig"
    )

    cohort_levels = sorted(cell["Processing_Cohort"].dropna().unique())
    sample_cohort_pairs = cell[["sample_uuid", "Processing_Cohort"]].drop_duplicates()
    cohort_sets = {
        cohort: set(
            sample_cohort_pairs.loc[
                sample_cohort_pairs["Processing_Cohort"] == cohort, "sample_uuid"
            ]
        )
        for cohort in cohort_levels
    }
    overlap_rows = []
    for cohort_a in cohort_levels:
        for cohort_b in cohort_levels:
            overlap_rows.append(
                {
                    "cohort_a": cohort_a,
                    "cohort_b": cohort_b,
                    "shared_samples": len(cohort_sets[cohort_a] & cohort_sets[cohort_b]),
                }
            )
    overlap = pd.DataFrame(overlap_rows)
    overlap.to_csv(output / "09_cohort_sample_overlap.csv", index=False, encoding="utf-8-sig")

    missingness_rows = []
    for column in SOURCE_METADATA:
        missingness_rows.append(
            {
                "level": "cell",
                "field": column,
                "rows": len(cell),
                "missing": int(cell[column].isna().sum()),
                "missing_fraction": float(cell[column].isna().mean()),
            }
        )
    missingness = pd.DataFrame(missingness_rows)
    missingness.to_csv(
        output / "10_metadata_missingness.csv", index=False, encoding="utf-8-sig"
    )

    primary_matrix = build_model_matrix(
        eligible[eligible["Processing_Cohort"] == "4.0"],
        "C3A_PRIMARY_C4_MANAGED_VS_NORMAL",
        ["na", "managed"],
    )
    validation_matrix = build_model_matrix(
        eligible[eligible["Processing_Cohort"] == "2.0"],
        "C3A_VALIDATION_C2_EUROPEAN_FEMALE",
        ["na", "managed"],
        lambda table: (table["ethnicity"] == "European American")
        & (table["sex"] == "female"),
    )
    flare_matrix = build_model_matrix(
        eligible[eligible["Processing_Cohort"] == "3.0"],
        "C3A_SECONDARY_C3_FLARE_VS_NORMAL",
        ["na", "flare"],
    )
    primary_matrix.to_csv(
        output / "11_primary_model_matrix.csv", index=False, encoding="utf-8-sig"
    )
    validation_matrix.to_csv(
        output / "12_validation_model_matrix.csv", index=False, encoding="utf-8-sig"
    )
    flare_matrix.to_csv(
        output / "13_flare_model_matrix.csv", index=False, encoding="utf-8-sig"
    )

    primary_rank = numeric_rank(
        primary_matrix, ["intercept", "is_managed", "age_centered", "ethnicity_asian"]
    )
    validation_rank = numeric_rank(
        validation_matrix, ["intercept", "is_managed", "age_centered"]
    )
    flare_rank = numeric_rank(
        flare_matrix, ["intercept", "is_flare", "age_centered", "ethnicity_european"]
    )
    primary_counts = primary_matrix["disease_state"].value_counts().to_dict()
    validation_counts = validation_matrix["disease_state"].value_counts().to_dict()
    flare_counts = flare_matrix["disease_state"].value_counts().to_dict()

    donor_ind_pairs = cell[["donor_id", "ind_cov"]].drop_duplicates()
    donor_multi_ind = int(
        (donor_ind_pairs.groupby("donor_id", observed=True)["ind_cov"].nunique() > 1).sum()
    )
    ind_multi_donor = int(
        (donor_ind_pairs.groupby("ind_cov", observed=True)["donor_id"].nunique() > 1).sum()
    )
    explicit_non_b = int(cell["ct_cov_explicit_non_b"].sum())
    sample_conflicts = int(
        invariant_table.loc[invariant_table["level"] == "sample_uuid", "conflicting_groups"].sum()
    )
    library_conflicts = int(
        invariant_table.loc[invariant_table["level"] == "library_uuid", "conflicting_groups"].sum()
    )
    donor_conflicts = int(
        invariant_table.loc[invariant_table["level"] == "donor_id", "conflicting_groups"].sum()
    )

    checks = dict(
        [
            check(
                "gate_c2b4_integrity",
                not c2b4_integrity_failures,
                f"{len(c2b4_manifest) - len(c2b4_integrity_failures)}/{len(c2b4_manifest)} rows verified",
            ),
            check(
                "gate_c2b4_scope",
                c2b4_decision.get("outcome_unlock_scope")
                == "two-compartment composition and prespecified continuous within-conventional programs",
                str(c2b4_decision.get("outcome_unlock_scope")),
            ),
            check(
                "cell_id_join_complete",
                len(missing_cell_ids) == 0 and all_null_join_rows == 0,
                f"{primary.n_obs - len(missing_cell_ids)}/{primary.n_obs} cell IDs joined; all-null rows={all_null_join_rows}",
            ),
            check(
                "cell_ids_unique",
                primary.obs_names.is_unique and source.obs_names.is_unique,
                f"primary={primary.obs_names.is_unique}; source={source.obs_names.is_unique}",
            ),
            check(
                "key_concordance",
                sum(key_mismatches.values()) == 0,
                "; ".join(f"{key} mismatches={value}" for key, value in key_mismatches.items()),
            ),
            check(
                "join_method_guard",
                positional_key_match < 0.05,
                f"cell-ID join required; positional source_cell_index library match={positional_key_match:.3f}",
            ),
            check(
                "two_compartment_assignment_complete",
                cell["frozen_neutral_id"].notna().all()
                and set(cell["frozen_neutral_id"]) == {"B_CONV", "B_ASC"},
                f"assigned={int(cell['frozen_neutral_id'].notna().sum()):,}/{len(cell):,}",
            ),
            check(
                "sample_metadata_invariants",
                sample_conflicts == 0,
                f"conflicting sample-field groups={sample_conflicts}",
            ),
            check(
                "library_cohort_invariant",
                library_conflicts == 0,
                f"libraries with multiple cohorts={library_conflicts}",
            ),
            check(
                "donor_metadata_invariants",
                donor_conflicts == 0,
                f"conflicting donor-field groups={donor_conflicts}",
            ),
            check(
                "donor_ind_cov_bijection",
                donor_multi_ind == 0 and ind_multi_donor == 0,
                f"donor->multiple ind_cov={donor_multi_ind}; ind_cov->multiple donor={ind_multi_donor}",
            ),
            check(
                "age_complete",
                cell["age_years"].notna().all(),
                f"age range={cell['age_years'].min():.0f}-{cell['age_years'].max():.0f}",
            ),
            check(
                "explicit_non_b_localized",
                explicit_non_b <= 50,
                f"explicit non-B ct_cov labels={explicit_non_b}/{len(cell)}; sensitivity only",
            ),
            check(
                "primary_design_support",
                primary_counts.get("na", 0) >= 30 and primary_counts.get("managed", 0) >= 30,
                f"cohort 4 normal={primary_counts.get('na', 0)}; managed={primary_counts.get('managed', 0)}",
            ),
            check(
                "primary_design_full_rank",
                primary_rank == 4,
                f"rank={primary_rank}/4; n={len(primary_matrix)}",
            ),
            check(
                "validation_design_support",
                validation_counts.get("na", 0) >= 15
                and validation_counts.get("managed", 0) >= 30,
                f"cohort 2 European-female normal={validation_counts.get('na', 0)}; managed={validation_counts.get('managed', 0)}",
            ),
            check(
                "validation_design_full_rank",
                validation_rank == 3,
                f"rank={validation_rank}/3; n={len(validation_matrix)}",
            ),
            check(
                "flare_design_support",
                flare_counts.get("na", 0) >= 12 and flare_counts.get("flare", 0) >= 12,
                f"cohort 3 normal={flare_counts.get('na', 0)}; flare={flare_counts.get('flare', 0)}",
            ),
            check(
                "flare_design_full_rank",
                flare_rank == 4,
                f"rank={flare_rank}/4; n={len(flare_matrix)}",
            ),
        ]
    )
    all_pass = all(result["pass"] for result in checks.values())
    decision = (
        "PASS_GATE_C3_METADATA_JOIN_AND_MODEL_DESIGN_FREEZE"
        if all_pass else "HOLD_GATE_C3_METADATA_OR_DESIGN_REVIEW_REQUIRED"
    )

    model_contract = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "FROZEN" if all_pass else "NOT_FROZEN",
        "minimum_b_cells": args.minimum_cells,
        "biological_replicate": "sample_uuid",
        "technical_stratum": "sample_uuid x Processing_Cohort",
        "canonical_individual_key": "donor_id",
        "ind_cov_policy": "audit alias only; verified one-to-one with donor_id",
        "cell_identity": {
            "B_CONV": "source r0.4 clusters 0,1,2,4",
            "B_ASC": "source r0.4 cluster 3",
        },
        "primary": {
            "analysis_id": "C3A_PRIMARY_C4_MANAGED_VS_NORMAL",
            "cohort": "4.0",
            "states": ["na", "managed"],
            "n": len(primary_matrix),
            "counts": primary_counts,
            "fixed_effects": ["managed", "age_centered", "ethnicity_asian"],
            "sex_policy": "not included; all eligible cohort-4 strata are female",
            "response": "asc_cells of total_cells",
        },
        "validation": {
            "analysis_id": "C3A_VALIDATION_C2_EUROPEAN_FEMALE",
            "cohort": "2.0",
            "states": ["na", "managed"],
            "restriction": "European American and female",
            "n": len(validation_matrix),
            "counts": validation_counts,
            "fixed_effects": ["managed", "age_centered"],
            "interpretation": "directional internal replication; age imbalance requires caution",
        },
        "secondary_flare": {
            "analysis_id": "C3A_SECONDARY_C3_FLARE_VS_NORMAL",
            "cohort": "3.0",
            "states": ["na", "flare"],
            "n": len(flare_matrix),
            "counts": flare_counts,
            "fixed_effects": ["flare", "age_centered", "ethnicity_european"],
            "interpretation": "secondary, not a substitute for managed-state replication",
        },
        "treated_policy": "descriptive only; five eligible cohort-3 strata",
        "abundance_model": "sample-stratum beta-binomial or equivalent overdispersed count model",
        "uncertainty": "donor-clustered or donor-random-effect uncertainty if repeated donors enter a contrast",
        "zero_policy": "retain zero ASC counts; no pseudocount for the primary count likelihood",
        "sensitivity": [
            "minimum B-cell thresholds 20 and 100",
            "exclude explicit non-B ct_cov cells only",
            "exclude residual_doublet_auto_call cells",
            "two-part ASC presence and positive-abundance analysis",
        ],
        "prohibited": [
            "cell-level inferential tests",
            "hard naive-versus-memory composition",
            "platelet-associated B-cell identity",
            "source cluster-4 publication subtype",
            "cohort or covariate selection after viewing effect estimates",
        ],
    }
    (output / "14_MODEL_DESIGN_CONTRACT.json").write_text(
        json.dumps(model_contract, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    contract_lines = [
        "# Gate C3 frozen model-design contract",
        "",
        f"**Status:** `{model_contract['status']}`",
        "",
        f"- Minimum frozen B cells per sample-cohort stratum: {args.minimum_cells}",
        "- Biological replicate: `sample_uuid`",
        "- Technical stratum: `sample_uuid x Processing_Cohort`",
        "- Canonical individual key: `donor_id` (`ind_cov` is a verified alias)",
        "- Primary: cohort 4 managed versus normal, age and ethnicity adjusted",
        "- Internal validation: cohort 2 European-American females, age adjusted",
        "- Secondary: cohort 3 flare versus normal, age and ethnicity adjusted",
        "- Treated cohort-3 samples: descriptive only",
        "",
        "## Binding restrictions",
        "",
    ]
    contract_lines.extend(f"- {item}" for item in model_contract["prohibited"])
    contract_lines.extend(
        [
            "",
            "No abundance effect estimate was inspected when this contract was generated.",
        ]
    )
    (output / "14_MODEL_DESIGN_CONTRACT.md").write_text(
        "\n".join(contract_lines), encoding="utf-8"
    )

    matrix = (
        eligible.groupby(["Processing_Cohort", "disease_state"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(index=cohort_levels, columns=["na", "managed", "flare", "treated"], fill_value=0)
    )
    overlap_matrix = overlap.pivot(index="cohort_a", columns="cohort_b", values="shared_samples")
    overlap_matrix = overlap_matrix.reindex(index=cohort_levels, columns=cohort_levels)

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.7))
    im = axes[0, 0].imshow(matrix.to_numpy(), cmap="Blues", aspect="auto", vmin=0)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = int(matrix.iloc[row, column])
            axes[0, 0].text(column, row, str(value), ha="center", va="center", fontsize=7)
    axes[0, 0].set_xticks(range(matrix.shape[1]), ["Normal", "Managed", "Flare", "Treated"])
    axes[0, 0].set_yticks(range(matrix.shape[0]), [f"Cohort {value}" for value in matrix.index])
    axes[0, 0].set(xlabel="Disease state", ylabel="Processing cohort")
    fig.colorbar(im, ax=axes[0, 0], fraction=0.046, pad=0.04, label="Eligible strata")

    cohort_data = [
        eligible.loc[eligible["Processing_Cohort"] == cohort, "total_cells"].to_numpy()
        for cohort in cohort_levels
    ]
    box = axes[0, 1].boxplot(cohort_data, patch_artist=True, widths=0.55, showfliers=False)
    for patch, color in zip(box["boxes"], ["#6BAED6", "#74C476", "#FDAE6B", "#9E9AC8"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    axes[0, 1].plot([0.7, 4.3], [args.minimum_cells, args.minimum_cells], "--", color="#444444", linewidth=0.7)
    axes[0, 1].set_xticks(range(1, 5), [f"C{value}" for value in cohort_levels])
    axes[0, 1].set(xlabel="Processing cohort", ylabel="B cells per sample-cohort stratum")

    im2 = axes[1, 0].imshow(overlap_matrix.to_numpy(), cmap="Greens", aspect="auto", vmin=0)
    for row in range(overlap_matrix.shape[0]):
        for column in range(overlap_matrix.shape[1]):
            axes[1, 0].text(
                column, row, str(int(overlap_matrix.iloc[row, column])),
                ha="center", va="center", fontsize=7,
            )
    axes[1, 0].set_xticks(range(4), [f"C{value}" for value in cohort_levels])
    axes[1, 0].set_yticks(range(4), [f"C{value}" for value in cohort_levels])
    axes[1, 0].set(xlabel="Processing cohort", ylabel="Processing cohort")
    fig.colorbar(im2, ax=axes[1, 0], fraction=0.046, pad=0.04, label="Shared samples")

    fields = ["ct_cov", "disease", "disease_state", "sex", "ind_cov"]
    missing_plot = missingness.set_index("field").reindex(fields)
    x = np.arange(len(fields))
    axes[1, 1].plot(
        x,
        100 * missing_plot["missing_fraction"].to_numpy(),
        linestyle="none",
        marker="o",
        markersize=5,
        color="#D95F02",
    )
    axes[1, 1].set_xticks(x, fields, rotation=30)
    axes[1, 1].set(ylabel="Missing cells (%)", ylim=(-0.3, 8.0))
    for label, axis in zip("ABCD", axes.flat):
        axis.text(-0.14, 1.06, label, transform=axis.transAxes, fontsize=10, fontweight="bold")
        axis.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.12, top=0.96, wspace=0.35, hspace=0.38)
    fig.savefig(figure_dir / "gate_c3_metadata_and_design_audit.png", dpi=300)
    fig.savefig(figure_dir / "gate_c3_metadata_and_design_audit.pdf")
    plt.close(fig)

    review = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "join_method": "exact cell_id reindex into source CELLxGENE obs",
        "source_cell_index_policy": "intermediate B-lineage index only; prohibited as full-source row position",
        "cells": len(cell),
        "samples": int(cell["sample_uuid"].nunique()),
        "sample_cohort_strata": len(stratum),
        "libraries": int(cell["library_uuid"].nunique()),
        "donors": int(cell["donor_id"].nunique()),
        "ct_cov_missing_cells": int(cell["ct_cov_missing"].sum()),
        "ct_cov_missing_fraction": float(cell["ct_cov_missing"].mean()),
        "explicit_non_b_ct_cov_cells": explicit_non_b,
        "checks": checks,
        "model_contract_frozen": all_pass,
        "effect_estimates_inspected": False,
        "next_if_pass": "fit Gate C3A frozen abundance models and prespecified sensitivities",
        "next_if_hold": "repair metadata keys or unsupported model strata before effect estimation",
    }
    (output / "15_GATE_C3_METADATA_AUDIT.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    review_lines = [
        "# Gate C3 protected-metadata and model-design audit",
        "",
        f"**Decision:** `{decision}`",
        "",
        f"- Cells joined by exact cell ID: {len(cell):,}",
        f"- Biological samples: {review['samples']}",
        f"- Sample-cohort technical strata: {review['sample_cohort_strata']}",
        f"- Libraries: {review['libraries']}",
        f"- Donors: {review['donors']}",
        f"- `ct_cov` missing: {review['ct_cov_missing_cells']:,} ({100 * review['ct_cov_missing_fraction']:.2f}%)",
        f"- Explicit non-B `ct_cov` labels: {explicit_non_b}",
        "- Effect estimates inspected: False",
        "",
        "## Checks",
        "",
    ]
    for name, result in checks.items():
        review_lines.append(
            f"- [{'PASS' if result['pass'] else 'FAIL'}] {name}: {result['detail']}"
        )
    review_lines.extend(
        [
            "",
            "## Binding interpretation",
            "",
            (
                "The metadata join and three prespecified model matrices are frozen. Gate C3A may fit"
                " sample-level abundance models without changing cohorts, cutoffs or covariates after"
                " effect inspection."
                if all_pass else
                "Metadata or design support failed. No Gate C3 effect model is authorized."
            ),
        ]
    )
    (output / "15_GATE_C3_METADATA_AUDIT.md").write_text(
        "\n".join(review_lines), encoding="utf-8"
    )

    status = {
        "status": decision,
        "protected_metadata_join_complete": all_pass,
        "model_design_contract_frozen": all_pass,
        "effect_estimation_authorized": all_pass,
        "effect_estimates_inspected": False,
        "hard_naive_memory_labels_authorized": False,
    }
    (output / "00_GATE_C3_RUN_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    status_lines = [
        "# Gate C3 run status",
        "",
        f"**Status:** `{decision}`",
        "",
        f"- Protected metadata join complete: {all_pass}",
        f"- Model-design contract frozen: {all_pass}",
        f"- Effect estimation authorized: {all_pass}",
        "- Effect estimates inspected: False",
        "- Hard naive-memory labels authorized: False",
        "",
        "See `15_GATE_C3_METADATA_AUDIT.md` and `14_MODEL_DESIGN_CONTRACT.md`.",
    ]
    (output / "00_GATE_C3_RUN_STATUS.md").write_text(
        "\n".join(status_lines), encoding="utf-8"
    )

    manifest_rows = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "16_gate_c3_integrity_manifest.csv":
            manifest_rows.append(
                {
                    "relative_path": path.relative_to(output).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": hash_file(path),
                }
            )
    pd.DataFrame(manifest_rows).to_csv(
        output / "16_gate_c3_integrity_manifest.csv", index=False, encoding="utf-8-sig"
    )
    primary.file.close()
    source.file.close()
    print(json.dumps(review, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
