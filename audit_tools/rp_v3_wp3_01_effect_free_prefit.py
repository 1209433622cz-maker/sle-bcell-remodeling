#!/usr/bin/env python3
"""Run the RP v3 WP3 effect-free source and operator preflight.

The preflight verifies canonical external counts, donor identities, eligibility,
feature coverage and the frozen score implementation. It never computes real
scores, disease-group expression summaries, coefficients, intervals or P values.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import rankdata


PROGRAM = (
    "IFI44L", "IFI6", "IFIT1", "IFIT2", "IFIT3", "IRF7",
    "ISG15", "LY6E", "MX1", "MX2", "OAS1", "OAS2",
)
HISTORICAL_DESIGNS = (
    "GSE135779_adult_min50_design.csv",
    "GSE135779_childhood_min50_design.csv",
    "GSE135779_combined_min100_design.csv",
    "GSE135779_combined_min20_design.csv",
    "GSE135779_combined_min50_design.csv",
)
CHILDHOOD_DESIGN_BLOB = "10032be53d419437ff1d64de9461e026b5217e79"


def require(condition: bool, message: str) -> None:
    if not bool(condition):
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
    ).hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    payload = frame.to_csv(index=False, lineterminator="\n").encode("utf-8")
    path.write_bytes(payload)


def write_json(payload: dict, path: Path) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    path.write_bytes(text.encode("utf-8"))


def safe_unique_join(
    left: pd.DataFrame,
    right: pd.DataFrame,
    keys: list[str],
) -> pd.DataFrame:
    require(not left.duplicated(keys).any(), "duplicate left keys")
    require(not right.duplicated(keys).any(), "duplicate right keys")
    joined = left.merge(
        right,
        on=keys,
        how="left",
        validate="one_to_one",
        indicator=True,
        suffixes=("", "_source"),
    )
    require(joined["_merge"].eq("both").all(), "unmatched keys")
    return joined.drop(columns="_merge")


def validate_counts(matrix: sparse.csr_matrix, totals: pd.Series) -> None:
    require(np.issubdtype(matrix.dtype, np.integer), "raw counts must be integer")
    require(
        np.isfinite(matrix.data).all() and (matrix.data >= 0).all(),
        "raw counts must be finite and nonnegative",
    )
    observed = np.asarray(matrix.sum(axis=1)).ravel()
    require(np.array_equal(observed, totals.to_numpy()), "full denominator mismatch")


def load_stage0b_module(path: Path):
    spec = importlib.util.spec_from_file_location("rp_v3_stage0b_operator", path)
    require(spec is not None and spec.loader is not None, "cannot load Stage 0B operator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_rank_operator(path: Path) -> None:
    module = load_stage0b_module(path)
    values = sparse.csr_matrix(
        np.asarray([[0.0, 0.0, 2.0, 2.0], [5.0, 1.0, 1.0, 0.0]])
    )
    observed = module.percentile_program_score(values, [0, 2])
    expected = np.asarray(
        [
            np.mean(rankdata(row, method="average")[[0, 2]] / len(row))
            for row in values.toarray()
        ]
    )
    require(np.allclose(observed, expected, atol=0.0, rtol=0.0), "rank operator drift")


def canonical_inputs(workspace: Path) -> dict[str, Path | list[Path]]:
    stage0b = workspace / "phase17_v7/rp_v3_redesign/20261009_stage0b"
    external = stage0b / "external_source_rebuild"
    historical = (
        workspace
        / "phase17_v7/gateC8S/20260821_supplementary_traceability_freeze"
        / "full_statistical_results/sanitized_design_matrices"
    )
    childhood = (
        workspace
        / "phase17_v7/gateC5A/20260815_gse135779_source_mapping_freeze"
        / "13_CHILDHOOD_MIN50_MODEL_MATRIX.csv"
    )
    operator = workspace / "audit_tools/rp_v3_stage0b_02_minimal_trial.py"
    return {
        "stage0b": stage0b,
        "external": external,
        "historical": historical,
        "childhood": childhood,
        "operator": operator,
    }


def run(workspace: Path, output: Path) -> None:
    workspace = workspace.resolve()
    require(not output.exists(), "output exists; use a new directory")
    paths = canonical_inputs(workspace)
    for value in paths.values():
        require(Path(value).exists(), f"missing canonical input: {value}")
    output.mkdir(parents=True)

    stage0b = Path(paths["stage0b"])
    external = Path(paths["external"])
    historical = Path(paths["historical"])
    childhood_path = Path(paths["childhood"])
    operator_path = Path(paths["operator"])

    source_files = sorted(path for path in external.iterdir() if path.is_file())
    source_files.extend(
        stage0b / name
        for name in (
            "04_SCORE_CONTRACTS.json",
            "04_T_RANK_BACKGROUND.csv.gz",
            "11_T0_FROZEN_REFERENCE_PARAMETERS.csv",
        )
    )
    source_files.extend(historical / name for name in HISTORICAL_DESIGNS)
    source_files.extend((childhood_path, operator_path))
    source_files = sorted(source_files, key=lambda path: path.relative_to(workspace).as_posix())
    for path in source_files:
        require(path.exists(), f"missing canonical input: {path}")
    initial_hashes = {path: sha256(path) for path in source_files}

    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        require(condition, name)
        checks.append({"check": name, "pass": True, "detail": detail})

    counts = sparse.load_npz(external / "07_EXTERNAL_PSEUDOBULK_COUNTS.npz").tocsr()
    metadata = pd.read_csv(external / "08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv")
    source = pd.read_csv(external / "03_SAMPLE_SOURCE_AUDIT.csv")
    genes = pd.read_csv(
        external / "09_EXTERNAL_GENE_UNIVERSE.csv.gz",
        keep_default_na=False,
    )
    labels = pd.read_csv(external / "05_SOURCE_LABEL_DICTIONARY.csv")
    contract = json.loads((stage0b / "04_SCORE_CONTRACTS.json").read_text(encoding="utf-8-sig"))
    t0 = pd.read_csv(stage0b / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv")
    rank_background = pd.read_csv(
        stage0b / "04_T_RANK_BACKGROUND.csv.gz",
        keep_default_na=False,
    )["gene_symbol"]

    check(
        "matrix_shape_and_dictionary_rows",
        counts.shape == (len(metadata), len(genes)) == (672, 32738),
        "672 rows x 32,738 measured features",
    )
    check(
        "pseudobulk_row_index_exact",
        np.array_equal(metadata.pseudobulk_row, np.arange(len(metadata))),
    )
    validate_counts(counts, metadata.library_size_umi)
    check("all_full_library_sums_exact", True)
    check(
        "detected_genes_match",
        np.array_equal(counts.getnnz(axis=1), metadata.detected_genes),
    )
    check(
        "sample_donor_identity_unique",
        len(source) == 56
        and source.sample_id.nunique() == 56
        and source.donor_name.nunique() == 56,
    )

    broad = metadata[
        metadata.representation.eq("compartment")
        & metadata.frozen_compartment.eq("B_CONV_ANALOG")
    ].copy()
    check("broad_rows_one_per_sample", len(broad) == 56 and broad.sample_id.nunique() == 56)
    joined = safe_unique_join(
        broad,
        source[["sample_id", "donor_name", "cohort", "bconv_cells", "bconv_library_size_umi"]],
        ["sample_id"],
    )
    check(
        "compartment_source_count_metadata_match",
        np.array_equal(joined.cell_count, joined.bconv_cells)
        and np.array_equal(joined.library_size_umi, joined.bconv_library_size_umi),
    )

    source_labels = labels[
        labels.frozen_compartment.eq("B_CONV_ANALOG")
    ].source_label.tolist()
    check("eight_frozen_bconv_source_labels", len(source_labels) == 8)
    for sample_id in sorted(source.sample_id):
        bin_metadata = metadata[
            metadata.sample_id.eq(sample_id)
            & metadata.source_label.isin(source_labels)
        ]
        require(len(bin_metadata) == 8, f"missing source-label rows: {sample_id}")
        broad_row = int(
            broad.loc[broad.sample_id.eq(sample_id), "pseudobulk_row"].iloc[0]
        )
        summed = counts[bin_metadata.pseudobulk_row].sum(axis=0)
        require(
            np.array_equal(np.asarray(summed).ravel(), counts[broad_row].toarray().ravel()),
            f"source-label count partition failure: {sample_id}",
        )
        require(
            int(bin_metadata.cell_count.sum())
            == int(broad.loc[broad.sample_id.eq(sample_id), "cell_count"].iloc[0]),
            f"source-label cell partition failure: {sample_id}",
        )
    check("56_of_56_label_to_broad_count_and_cell_closure", True)

    check(
        "t0_gene_set_order_exact",
        contract["program_members"] == t0.gene_symbol.tolist()
        and tuple(contract["program_members"]) == PROGRAM
        and t0.gene_symbol.nunique() == 12,
    )
    check(
        "t0_finite_positive_reference43",
        np.isfinite(t0.select_dtypes("number")).all().all()
        and (t0.control_population_sd_log2_cpm_plus_0_5 > 0).all()
        and t0.reference_strata.eq(43).all(),
    )
    symbols = genes.gene_symbol_upper.astype(str)
    symbol_set = set(symbols)
    rank_set = set(rank_background)
    check(
        "rank_background_unique18873",
        len(rank_background) == 18873 and rank_background.nunique() == 18873,
    )
    check("rank_background_available_external", rank_set.issubset(symbol_set))
    feature_rows = [
        {
            "gene_symbol": gene,
            "external_features": int(symbols.eq(gene).sum()),
            "rank_background_present": gene in rank_set,
            "T0_reference_present": gene in set(t0.gene_symbol),
        }
        for gene in PROGRAM
    ]
    check(
        "IFN12_present",
        all(
            row["external_features"] >= 1
            and row["rank_background_present"]
            and row["T0_reference_present"]
            for row in feature_rows
        ),
    )

    joined["eligible_min50"] = joined.cell_count.ge(50)
    joined["exclusion_reason"] = np.where(
        joined.eligible_min50,
        "",
        "source_label_BCONV_cells_below_frozen_50",
    )
    check(
        "childhood_ID_linked_design_blob_verified",
        git_blob_sha1(childhood_path) == CHILDHOOD_DESIGN_BLOB,
    )
    childhood = pd.read_csv(childhood_path)
    linked = safe_unique_join(
        childhood,
        joined[
            [
                "sample_id", "donor_name", "cohort", "cell_count",
                "library_size_umi", "pseudobulk_row", "eligible_min50",
            ]
        ],
        ["sample_id"],
    )
    check(
        "childhood_donor_and_cohort_match",
        linked.donor_name.eq(linked.donor_name_source).all()
        and linked.cohort.eq(linked.cohort_source).all(),
    )
    check(
        "childhood_design_exact_support",
        set(childhood.sample_id)
        == set(
            joined.loc[
                joined.cohort.eq("childhood") & joined.eligible_min50,
                "sample_id",
            ]
        ),
    )
    check(
        "childhood_raw_metadata_matches_frozen_design",
        childhood.bconv_cells.eq(linked.cell_count).all()
        and childhood.bconv_library_size_umi.eq(linked.library_size_umi).all(),
    )
    check(
        "childhood_explicit_groups",
        childhood.groupby("disease_group").size().to_dict() == {"HC": 11, "SLE": 32},
    )
    check(
        "childhood_design_rank2",
        childhood.intercept.eq(1).all() and set(childhood.is_sle) == {0, 1},
    )

    covariate_aliases = {
        "age": ("age", "age_years"),
        "sex": ("sex", "gender"),
        "ancestry": ("ethnicity", "ancestry"),
        "treatment": ("treatment", "medication", "drug"),
        "activity": ("SLEDAI", "activity", "disease_activity"),
        "processing_batch": ("batch", "processing_cohort", "library_uuid"),
    }
    covariates = []
    for covariate, aliases in covariate_aliases.items():
        present = [
            column
            for column in childhood.columns
            if column.lower() in {alias.lower() for alias in aliases}
        ]
        covariates.append(
            {
                "covariate": covariate,
                "verified_in_current_ID_linked_design": bool(present),
                "column_names": ";".join(present),
                "interpretation": "available" if present else "not_available_in_this_verified_design",
            }
        )

    missing = pd.read_csv(external / "04_METADATA_WITHOUT_MATRIX_SAMPLES.csv")
    missing_donors = missing[["sample_id", "donor_name", "cohort"]].drop_duplicates()
    cohort_support = (
        joined.groupby("cohort")
        .agg(
            matrix_samples=("sample_id", "nunique"),
            donors=("donor_name", "nunique"),
            min50_supported=("eligible_min50", "sum"),
        )
        .reset_index()
    )
    design_rows = []
    for name in HISTORICAL_DESIGNS:
        design = pd.read_csv(historical / name)
        design_rows.append(
            {
                "file": name,
                "n_rows": len(design),
                "n_controls": int(design.is_sle.eq(0).sum()),
                "n_SLE": int(design.is_sle.eq(1).sum()),
                "design_columns": design.design_columns.iloc[0],
                "identity_role": "SANITIZED_HISTORICAL_COUNTS_ONLY__NOT_JOIN_KEY",
            }
        )

    verify_rank_operator(operator_path)
    check(
        "T_rank_source_operator_exact",
        True,
        "scipy rankdata(method=average) divided by full background size M",
    )
    check(
        "input_hashes_unchanged_during_run",
        all(sha256(path) == digest for path, digest in initial_hashes.items()),
    )

    receipts = pd.DataFrame(
        [
            {
                "path": path.relative_to(workspace).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": initial_hashes[path],
            }
            for path in source_files
        ]
    )
    write_csv(receipts, output / "01_WP3_PREFIT_INPUT_RECEIPTS.csv")
    write_csv(pd.DataFrame(checks), output / "02_WP3_PREFIT_CHECKS.csv")
    write_csv(
        joined[
            [
                "sample_id", "donor_name", "cohort", "pseudobulk_row",
                "cell_count", "library_size_umi", "eligible_min50",
                "exclusion_reason",
            ]
        ],
        output / "03_EXTERNAL_ELIGIBILITY.csv",
    )
    write_csv(
        linked[
            [
                "sample_id", "donor_name", "disease_group", "pseudobulk_row",
                "cell_count", "library_size_umi",
            ]
        ],
        output / "04_PRIMARY_CHILDHOOD_SOURCE_LINKAGE.csv",
    )
    write_csv(cohort_support, output / "05_COHORT_SUPPORT.csv")
    write_csv(pd.DataFrame(feature_rows), output / "06_IFN_AND_RANK_COVERAGE.csv")
    write_csv(pd.DataFrame(covariates), output / "07_COVARIATE_AVAILABILITY.csv")
    write_csv(missing_donors, output / "08_METADATA_WITHOUT_MATRIX.csv")
    write_csv(pd.DataFrame(design_rows), output / "09_HISTORICAL_DESIGN_ACCOUNTING.csv")

    receipt = {
        "status": "PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION",
        "checks_passed": len(checks),
        "counts_shape": list(counts.shape),
        "counts_nnz": int(counts.nnz),
        "sample_matrices": 56,
        "source_donors": 56,
        "eligible_min50": int(joined.eligible_min50.sum()),
        "primary_childhood": len(childhood),
        "primary_controls": 11,
        "primary_SLE": 32,
        "metadata_only_donors_without_source_matrix": missing_donors.to_dict("records"),
        "source_labels": source_labels,
        "source_gene_features": len(genes),
        "rank_symbols": len(rank_background),
        "IFN_members": len(PROGRAM),
        "T0_control_reference_n": 43,
        "T_rank_percentile_convention": "average_rank_divided_by_background_size_M",
        "stage0b_score_operator_sha256": sha256(operator_path),
        "raw_tar_and_barcode_regeneration_performed": False,
        "source_label_independent_mapping_performed": False,
        "real_IFN_scores_generated": False,
        "disease_group_expression_summaries_generated": False,
        "real_disease_effects_fitted": False,
        "confidence_intervals_or_p_values_generated": False,
        "clinical_or_cross_platform_measurement_calibration_validated": False,
        "WP3_OUTCOME_EXECUTION_AUTHORIZED": False,
        "next_stage": "WP3_EFFECT_FREE_MEASUREMENT_SENSITIVITY_PROTOCOL_AND_DRY_RUN",
    }
    write_json(receipt, output / "10_WP3_PREFIT_GATE_STATUS.json")
    print(json.dumps(receipt, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.workspace, args.output)


if __name__ == "__main__":
    main()
