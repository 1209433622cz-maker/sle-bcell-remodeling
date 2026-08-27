#!/usr/bin/env python3
"""Independently audit Round 6 R1 and propagate broad-state uncertainty."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from datetime import datetime
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.io import mmread, mmwrite


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RAW_SHA256 = "DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5"
EXPECTED_REFERENCE_SHA256 = "594A040FC483973B38B744D5D0E526633D7F1C91F2544D34C28D35F2084E3AFB"
EXPECTED_R1_SCRIPT_SHA256 = "7A28EB02C49F0B2C951180D83438D82FF1E4D83E7D7CC345BFA7987040A9A960"
PRIMARY_BRANCH = "harmony"
PRIMARY_RESOLUTION = 0.4
THRESHOLDS = {
    "median_mapped_ari": 0.95,
    "minimum_mapped_ari": 0.90,
    "median_mapping_agreement": 0.995,
    "minimum_mapping_agreement": 0.990,
    "minimum_state_median_jaccard": 0.95,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r1-run-dir", type=Path, required=True)
    parser.add_argument("--raw-h5ad", type=Path, required=True)
    parser.add_argument("--reference-h5ad", type=Path, required=True)
    parser.add_argument("--gate-c3-dir", type=Path, required=True)
    parser.add_argument("--gate-c3a-dir", type=Path, required=True)
    parser.add_argument("--gate-c4b-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_mtx_gz(path: Path) -> sparse.csr_matrix:
    with gzip.open(path, "rb") as handle:
        return sparse.csr_matrix(mmread(handle), dtype=np.int64)


def write_mtx_gz(path: Path, matrix: sparse.spmatrix) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb", compresslevel=6) as handle:
        mmwrite(handle, matrix.tocoo(), field="integer", symmetry="general")


def recompute_summaries(
    metrics: pd.DataFrame, states: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    state_summary = (
        states.groupby(["branch", "resolution", "reference_state"], observed=True)
        .agg(
            median_jaccard=("jaccard", "median"),
            minimum_jaccard=("jaccard", "min"),
            median_recall=("recall", "median"),
            minimum_recall=("recall", "min"),
        )
        .reset_index()
    )
    branch_summary = (
        metrics.groupby(["branch", "resolution"], observed=True)
        .agg(
            replicates=("replicate", "nunique"),
            median_mapped_ari=("mapped_adjusted_rand_index", "median"),
            minimum_mapped_ari=("mapped_adjusted_rand_index", "min"),
            median_mapped_ami=("mapped_adjusted_mutual_information", "median"),
            minimum_mapped_ami=("mapped_adjusted_mutual_information", "min"),
            median_mapping_agreement=("majority_mapping_agreement", "median"),
            minimum_mapping_agreement=("majority_mapping_agreement", "min"),
        )
        .reset_index()
        .merge(
            state_summary.groupby(["branch", "resolution"], observed=True)
            .agg(minimum_state_median_jaccard=("median_jaccard", "min"))
            .reset_index(),
            on=["branch", "resolution"],
            how="left",
        )
    )
    return branch_summary, state_summary


def assert_frame_equal_numeric(
    observed: pd.DataFrame, expected: pd.DataFrame, keys: list[str], label: str
) -> None:
    left = observed.sort_values(keys).reset_index(drop=True)
    right = expected.sort_values(keys).reset_index(drop=True)
    if list(left.columns) != list(right.columns) or len(left) != len(right):
        raise RuntimeError(f"{label} schema or row count differs")
    for column in left.columns:
        if pd.api.types.is_numeric_dtype(left[column]) and pd.api.types.is_numeric_dtype(
            right[column]
        ):
            if not np.allclose(
                left[column].to_numpy(float),
                right[column].to_numpy(float),
                rtol=1e-12,
                atol=1e-12,
                equal_nan=True,
            ):
                raise RuntimeError(f"{label} numeric mismatch in {column}")
        elif not left[column].astype(str).equals(right[column].astype(str)):
            raise RuntimeError(f"{label} value mismatch in {column}")


def corrected_matrix(
    raw: ad.AnnData,
    changed: pd.DataFrame,
    cell: pd.DataFrame,
    base: sparse.csr_matrix,
    samples: pd.DataFrame,
) -> tuple[sparse.csr_matrix, int]:
    key_to_column = {
        (str(row.sample_uuid), float(row.Processing_Cohort)): index
        for index, row in enumerate(samples.itertuples(index=False))
    }
    source_indices: list[int] = []
    sample_columns: list[int] = []
    signs: list[int] = []
    for row in changed.itertuples(index=False):
        source_index = int(row.raw_row_index)
        metadata = cell.iloc[source_index]
        key = (str(metadata["sample_uuid"]), float(metadata["Processing_Cohort"]))
        if key not in key_to_column:
            continue
        if row.reference_state == "B_ASC" and row.mapped_state == "B_CONV":
            sign = 1
        elif row.reference_state == "B_CONV" and row.mapped_state == "B_ASC":
            sign = -1
        else:
            raise RuntimeError("Unexpected broad-state transition")
        source_indices.append(source_index)
        sample_columns.append(key_to_column[key])
        signs.append(sign)
    if not source_indices:
        return base.copy(), 0
    selected = raw.X[np.asarray(source_indices), :]
    selected = selected.tocsr() if sparse.issparse(selected) else sparse.csr_matrix(selected)
    assignment = sparse.csr_matrix(
        (
            np.asarray(signs, dtype=np.int64),
            (np.asarray(sample_columns), np.arange(len(source_indices))),
        ),
        shape=(len(samples), len(source_indices)),
    )
    delta = (assignment @ selected).transpose().tocsr()
    corrected = (base + delta).tocsr()
    corrected.sum_duplicates()
    corrected.eliminate_zeros()
    if corrected.shape != base.shape or (corrected.data < 0).any():
        raise RuntimeError("Corrected B_CONV matrix is invalid")
    return corrected, len(source_indices)


def main() -> None:
    args = parse_args()
    r1 = args.r1_run_dir.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    matrix_dir = output / "matrix_exports"
    matrix_dir.mkdir(exist_ok=True)
    print("[AUDIT] validating run contracts and input hashes", flush=True)

    run_contract = read_json(r1 / "00_RUN_CONTRACT.json")
    final_status = read_json(r1 / "05_FULL_PIPELINE_RESAMPLING_STATUS.json")
    analysis_script = ROOT / "audit_tools" / "phase17_round6_03_full_pipeline_identity_resampling.py"
    integrity = {
        "raw_sha256": sha256_file(args.raw_h5ad.resolve()),
        "reference_sha256": sha256_file(args.reference_h5ad.resolve()),
        "r1_script_sha256": sha256_file(analysis_script),
    }
    if integrity != {
        "raw_sha256": EXPECTED_RAW_SHA256,
        "reference_sha256": EXPECTED_REFERENCE_SHA256,
        "r1_script_sha256": EXPECTED_R1_SCRIPT_SHA256,
    }:
        raise RuntimeError(f"R1 input or executable integrity mismatch: {integrity}")
    if run_contract.get("analysis_script_sha256") != EXPECTED_R1_SCRIPT_SHA256:
        raise RuntimeError("Run contract references an unexpected analysis script")
    if run_contract.get("test_mode") is not False or int(run_contract.get("replicates", 0)) != 20:
        raise RuntimeError("R1 is not the required full 20-replicate scientific run")
    if run_contract.get("thresholds") != THRESHOLDS:
        raise RuntimeError("R1 thresholds differ from the frozen contract")

    cell_path = args.gate_c3_dir.resolve() / "01_unlocked_cell_metadata.csv.gz"
    cell = pd.read_csv(cell_path, low_memory=False)
    cell["source_cell_index"] = pd.to_numeric(cell["source_cell_index"]).astype(int)
    if not cell["source_cell_index"].is_unique:
        raise RuntimeError("Gate C3 source-cell indices are not unique")
    source_to_row = pd.Series(
        np.arange(len(cell), dtype=int), index=cell["source_cell_index"].to_numpy()
    )
    frozen_reference = np.where(
        pd.to_numeric(cell["source_r04_cluster"]).to_numpy() == 3, "B_ASC", "B_CONV"
    )

    replicate_dirs = sorted(r1.glob("replicate_*"))
    if len(replicate_dirs) != 20:
        raise RuntimeError(f"Expected 20 replicate directories; found {len(replicate_dirs)}")
    all_metrics: list[pd.DataFrame] = []
    all_states: list[pd.DataFrame] = []
    boundary_rows: list[dict] = []
    changed_by_replicate: dict[int, pd.DataFrame] = {}
    replicate_manifest: list[dict] = []
    print("[AUDIT] reading and independently checking 20 replicate outputs", flush=True)
    for expected_replicate, directory in enumerate(replicate_dirs, start=1):
        status = read_json(directory / "00_REPLICATE_STATUS.json")
        expected_contract = {**run_contract, "replicate": expected_replicate}
        if status.get("contract") != expected_contract:
            raise RuntimeError(f"Replicate {expected_replicate} contract mismatch")
        if status.get("status") != "COMPLETE" or status.get("harmony_converged") is not True:
            raise RuntimeError(f"Replicate {expected_replicate} is incomplete or unconverged")
        if int(status.get("cells", 0)) != 120_320 or int(status.get("selected_hvgs", 0)) != 3000:
            raise RuntimeError(f"Replicate {expected_replicate} shape/HVG contract failed")
        metrics = pd.read_csv(directory / "01_REPLICATE_METRICS.csv")
        states = pd.read_csv(directory / "02_STATE_METRICS.csv")
        if len(metrics) != 6 or len(states) != 12:
            raise RuntimeError(f"Replicate {expected_replicate} metric row counts differ")
        all_metrics.append(metrics)
        all_states.append(states)

        assignments = pd.read_csv(
            directory / "04_R04_CELL_ASSIGNMENTS.csv.gz",
            usecols=[
                "source_cell_index",
                "branch",
                "reference_state",
                "mapped_state",
                "mapping_agreement",
            ],
        )
        assignments = assignments.loc[assignments["branch"] == PRIMARY_BRANCH].copy()
        assignments["source_cell_index"] = pd.to_numeric(
            assignments["source_cell_index"]
        ).astype(int)
        if len(assignments) != 120_320 or not assignments["source_cell_index"].is_unique:
            raise RuntimeError(f"Replicate {expected_replicate} assignment membership failed")
        assignments["raw_row_index"] = assignments["source_cell_index"].map(source_to_row)
        if assignments["raw_row_index"].isna().any():
            raise RuntimeError(f"Replicate {expected_replicate} contains unknown source indices")
        assignments["raw_row_index"] = assignments["raw_row_index"].astype(int)
        row_positions = assignments["raw_row_index"].to_numpy()
        if not np.array_equal(assignments["reference_state"].to_numpy(), frozen_reference[row_positions]):
            raise RuntimeError(f"Replicate {expected_replicate} frozen reference mismatch")
        agreement = assignments["reference_state"].eq(assignments["mapped_state"])
        if not agreement.equals(assignments["mapping_agreement"].astype(bool)):
            raise RuntimeError(f"Replicate {expected_replicate} agreement flag mismatch")
        changed = assignments.loc[~agreement].copy()
        changed_by_replicate[expected_replicate] = changed

        for reference_state in ("B_ASC", "B_CONV"):
            reference_mask = assignments["reference_state"].eq(reference_state)
            mapped_mask = assignments["mapped_state"].eq(reference_state)
            intersection = int((reference_mask & mapped_mask).sum())
            union = int((reference_mask | mapped_mask).sum())
            state_row = states.loc[
                states["branch"].eq(PRIMARY_BRANCH)
                & np.isclose(states["resolution"], PRIMARY_RESOLUTION)
                & states["reference_state"].eq(reference_state)
            ].iloc[0]
            recomputed_jaccard = intersection / union
            recomputed_recall = intersection / int(reference_mask.sum())
            if not np.isclose(recomputed_jaccard, state_row["jaccard"], atol=1e-12):
                raise RuntimeError(f"Replicate {expected_replicate} {reference_state} Jaccard mismatch")
            if not np.isclose(recomputed_recall, state_row["recall"], atol=1e-12):
                raise RuntimeError(f"Replicate {expected_replicate} {reference_state} recall mismatch")
            boundary_rows.append(
                {
                    "replicate": expected_replicate,
                    "reference_state": reference_state,
                    "reference_cells": int(reference_mask.sum()),
                    "mapped_cells": int(mapped_mask.sum()),
                    "intersection": intersection,
                    "union": union,
                    "false_negative": int((reference_mask & ~mapped_mask).sum()),
                    "false_positive": int((~reference_mask & mapped_mask).sum()),
                    "jaccard": recomputed_jaccard,
                    "recall": recomputed_recall,
                }
            )
        replicate_manifest.append(
            {
                "replicate": expected_replicate,
                "cells": int(status["cells"]),
                "genes_after_min_cells": int(status["genes_after_min_cells"]),
                "selected_hvgs": int(status["selected_hvgs"]),
                "harmony_iterations": int(status["harmony_iterations"]),
                "harmony_converged": bool(status["harmony_converged"]),
                "changed_primary_cells": len(changed),
                "status_sha256": sha256_file(directory / "00_REPLICATE_STATUS.json"),
                "metrics_sha256": sha256_file(directory / "01_REPLICATE_METRICS.csv"),
                "states_sha256": sha256_file(directory / "02_STATE_METRICS.csv"),
                "hvg_sha256": sha256_file(directory / "03_SELECTED_HVGS.csv"),
                "assignments_sha256": sha256_file(directory / "04_R04_CELL_ASSIGNMENTS.csv.gz"),
            }
        )
        print(f"[AUDIT] replicate {expected_replicate}/20 verified", flush=True)

    metrics = pd.concat(all_metrics, ignore_index=True)
    states = pd.concat(all_states, ignore_index=True)
    boundary = pd.DataFrame(boundary_rows)
    branch_summary, state_summary = recompute_summaries(metrics, states)
    assert_frame_equal_numeric(
        metrics,
        pd.read_csv(r1 / "01_ALL_REPLICATE_METRICS.csv"),
        ["replicate", "branch", "resolution"],
        "aggregate replicate metrics",
    )
    assert_frame_equal_numeric(
        states,
        pd.read_csv(r1 / "02_ALL_STATE_METRICS.csv"),
        ["replicate", "branch", "resolution", "reference_state"],
        "aggregate state metrics",
    )
    assert_frame_equal_numeric(
        branch_summary,
        pd.read_csv(r1 / "03_BRANCH_RESOLUTION_SUMMARY.csv"),
        ["branch", "resolution"],
        "branch summary",
    )
    assert_frame_equal_numeric(
        state_summary,
        pd.read_csv(r1 / "04_STATE_SUMMARY.csv"),
        ["branch", "resolution", "reference_state"],
        "state summary",
    )
    primary = branch_summary.loc[
        branch_summary["branch"].eq(PRIMARY_BRANCH)
        & np.isclose(branch_summary["resolution"], PRIMARY_RESOLUTION)
    ].iloc[0]
    recomputed_primary = {
        key: float(primary[key])
        for key in (
            "median_mapped_ari",
            "minimum_mapped_ari",
            "median_mapped_ami",
            "minimum_mapped_ami",
            "median_mapping_agreement",
            "minimum_mapping_agreement",
            "minimum_state_median_jaccard",
        )
    }
    if any(
        not np.isclose(recomputed_primary[key], final_status["primary_metrics"][key], atol=1e-12)
        for key in recomputed_primary
    ):
        raise RuntimeError("Final status metrics do not match independent recomputation")

    print("[PROPAGATION] loading raw counts and frozen pseudobulk matrices", flush=True)
    raw = ad.read_h5ad(args.raw_h5ad.resolve())
    if not sparse.issparse(raw.X) or raw.n_obs != len(cell):
        raise RuntimeError("Raw matrix is not the expected sparse cell matrix")
    if not np.array_equal(
        pd.to_numeric(raw.obs["source_cell_index"]).to_numpy(int),
        cell["source_cell_index"].to_numpy(int),
    ):
        raise RuntimeError("Raw/Gate C3 source-index order differs")
    genes = pd.read_csv(
        args.gate_c4b_dir.resolve() / "02_matrix_exports" / "gene_metadata.csv.gz"
    )
    if not np.array_equal(raw.var_names.astype(str), genes["ensembl_id"].astype(str)):
        raise RuntimeError("Raw feature order differs from the frozen C4B exports")
    analysis_definitions = {
        "primary_base": {
            "matrix": "primary_base_counts.mtx.gz",
            "samples": "primary_base_samples.csv",
        },
        "validation_nonoverlap": {
            "matrix": "validation_nonoverlap_counts.mtx.gz",
            "samples": "validation_nonoverlap_samples.csv",
        },
    }
    base_matrices: dict[str, sparse.csr_matrix] = {}
    sample_tables: dict[str, pd.DataFrame] = {}
    export_dir = args.gate_c4b_dir.resolve() / "02_matrix_exports"
    for analysis, definition in analysis_definitions.items():
        base_matrices[analysis] = read_mtx_gz(export_dir / definition["matrix"])
        sample_tables[analysis] = pd.read_csv(export_dir / definition["samples"])
        if base_matrices[analysis].shape != (raw.n_vars, len(sample_tables[analysis])):
            raise RuntimeError(f"Frozen {analysis} matrix shape differs")
    matrix_manifest: list[dict] = []
    for replicate in range(1, 21):
        changed = changed_by_replicate[replicate]
        for analysis, definition in analysis_definitions.items():
            corrected, changed_in_analysis = corrected_matrix(
                raw,
                changed,
                cell,
                base_matrices[analysis],
                sample_tables[analysis],
            )
            destination = matrix_dir / f"replicate_{replicate:03d}_{analysis}_counts.mtx.gz"
            write_mtx_gz(destination, corrected)
            matrix_manifest.append(
                {
                    "replicate": replicate,
                    "analysis": analysis,
                    "relative_path": destination.relative_to(output).as_posix(),
                    "genes": corrected.shape[0],
                    "samples": corrected.shape[1],
                    "changed_cells_in_analysis": changed_in_analysis,
                    "total_umi": int(corrected.sum()),
                    "bytes": destination.stat().st_size,
                    "sha256": sha256_file(destination),
                }
            )
        print(f"[PROPAGATION] corrected matrix replicate {replicate}/20 written", flush=True)
    raw.file.close()

    branch_summary.to_csv(output / "01_RECOMPUTED_BRANCH_SUMMARY.csv", index=False)
    state_summary.to_csv(output / "02_RECOMPUTED_STATE_SUMMARY.csv", index=False)
    boundary.to_csv(output / "03_BOUNDARY_EXCHANGE.csv", index=False)
    pd.DataFrame(replicate_manifest).to_csv(output / "04_REPLICATE_INTEGRITY_MANIFEST.csv", index=False)
    pd.DataFrame(matrix_manifest).to_csv(output / "05_MATRIX_EXPORT_MANIFEST.csv", index=False)

    primary_state = state_summary.loc[
        state_summary["branch"].eq(PRIMARY_BRANCH)
        & np.isclose(state_summary["resolution"], PRIMARY_RESOLUTION)
    ].set_index("reference_state")
    checks = {
        "twenty_complete_replicates": len(replicate_dirs) == 20,
        "twenty_harmony_converged": all(row["harmony_converged"] for row in replicate_manifest),
        "aggregate_metrics_exactly_reproduced": True,
        "aggregate_states_exactly_reproduced": True,
        "final_status_exactly_reproduced": True,
        "formal_hold_retained": final_status.get("decision")
        == "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY",
        "basc_drives_state_jaccard_hold": bool(
            primary_state.loc["B_ASC", "median_jaccard"] < THRESHOLDS["minimum_state_median_jaccard"]
            and primary_state.loc["B_CONV", "median_jaccard"]
            >= THRESHOLDS["minimum_state_median_jaccard"]
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Round 6 R1 audit/preparation checks failed: {checks}")
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_R1_HOLD_INDEPENDENT_AUDIT_AND_PROPAGATION_PREP",
        "r1_decision": final_status["decision"],
        "integrity": integrity,
        "primary_metrics": recomputed_primary,
        "state_medians": {
            state: {
                "median_jaccard": float(primary_state.loc[state, "median_jaccard"]),
                "minimum_jaccard": float(primary_state.loc[state, "minimum_jaccard"]),
                "median_recall": float(primary_state.loc[state, "median_recall"]),
            }
            for state in ("B_ASC", "B_CONV")
        },
        "boundary_exchange": {
            "median_changed_cells": float(
                pd.DataFrame(replicate_manifest)["changed_primary_cells"].median()
            ),
            "minimum_changed_cells": int(
                pd.DataFrame(replicate_manifest)["changed_primary_cells"].min()
            ),
            "maximum_changed_cells": int(
                pd.DataFrame(replicate_manifest)["changed_primary_cells"].max()
            ),
        },
        "checks": checks,
        "next": "run isolated frozen composition and TMM-logCPM/HC3 IFN propagation models",
    }
    (output / "06_AUDIT_AND_PROPAGATION_PREP_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
