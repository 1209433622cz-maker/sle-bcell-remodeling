#!/usr/bin/env python3
"""Run the RP v3 WP2 structural preflight without fitting disease effects."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from rp_v3_wp2_kernels import composition_geometry, ilr_positive, rank_no_lapack


BASE = Path("phase17_v7/rp_v3_redesign")
MODEL_COLUMNS = ["intercept", "is_managed", "age_centered", "ethnicity_asian"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def safe_path(root: Path, relative_path: str) -> Path:
    path = (root / str(relative_path).replace("\\", "/")).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Path escapes the allowed root")
    return path


def require_hash(path: Path, expected: str) -> None:
    if not path.is_file() or sha256_file(path) != str(expected).upper():
        raise ValueError(f"Raw-byte hash mismatch or missing: {path}")


def write_json_lf(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2))
        handle.write("\n")


def write_dataframe_lf(frame: pd.DataFrame, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        frame.to_csv(handle, index=False, lineterminator="\n")


def run_prefit(project_root: Path, output: Path) -> dict:
    project_root = project_root.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError("Choose a new output directory; overwrite is forbidden")
    output.mkdir(parents=True)

    try:
        freeze = project_root / BASE / "20261010_wp1_prefit_freeze"
        contract = project_root / BASE / "20261010_wp1_prefit_contract"
        parent_gate = json.loads(
            (contract / "04_PREFIT_GATE_STATUS.json").read_text(encoding="utf-8-sig")
        )
        if parent_gate["status"] != "PASS_WP1_PREFIT_UNLOCK":
            raise ValueError("Wrong parent prefit gate")

        require_hash(freeze / "SHA256SUMS.csv", parent_gate["sufficient_count_manifest_hash"])
        manifest_records = []
        for record in pd.read_csv(freeze / "SHA256SUMS.csv").to_dict("records"):
            path = safe_path(freeze, record["relative_path"])
            require_hash(path, record["sha256"])
            if path.stat().st_size != int(record["bytes"]):
                raise ValueError(f"Size mismatch: {path.name}")
            manifest_records.append(
                {
                    "file": record["relative_path"],
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "pass": True,
                }
            )

        receipts = pd.read_csv(freeze / "input_receipts.csv")
        if len(receipts) != 4:
            raise ValueError("Expected four original parent-input receipts")
        for record in receipts.to_dict("records"):
            require_hash(
                safe_path(project_root, record["file"]), record["expected_sha256"]
            )

        contract_inputs = [
            ("02_SHARED_ANALYSIS_SET.csv", "shared_donor_ID_hash"),
            ("03_SHARED_DESIGN_MATRIX.csv", "shared_covariate_matrix_hash"),
        ]
        for filename, gate_field in contract_inputs:
            require_hash(contract / filename, parent_gate[gate_field])
        require_hash(
            freeze / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv",
            parent_gate["T0_reference_hash"],
        )
        require_hash(freeze / "09_PI_REF.csv", parent_gate["pi_ref_hash"])

        shared = pd.read_csv(
            contract / "02_SHARED_ANALYSIS_SET.csv", dtype={"donor_id": str}
        )
        design = pd.read_csv(
            contract / "03_SHARED_DESIGN_MATRIX.csv", dtype={"donor_id": str}
        )
        stratum_ids = shared.stratum_id.astype(str).tolist()
        if len(stratum_ids) != 68 or shared.donor_id.nunique() != 68:
            raise ValueError("The frozen 68-donor set changed")
        if len(set(stratum_ids)) != 68:
            raise ValueError("Duplicate stratum IDs")
        design = design.set_index("stratum_id").loc[stratum_ids].reset_index()
        if not design.donor_id.eq(shared.donor_id).all():
            raise ValueError("Donor alignment failed")
        if design.is_managed.value_counts().to_dict() != {1: 37, 0: 31}:
            raise ValueError("Disease-arm counts changed")
        if parent_gate["model_columns"] != MODEL_COLUMNS:
            raise ValueError("Parent design columns changed")
        base_design = design[MODEL_COLUMNS].to_numpy(float)
        if rank_no_lapack(base_design) != 4:
            raise ValueError("Base design is not rank four")

        reference = pd.read_csv(freeze / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv")
        if len(reference) != 12 or not reference.reference_strata.eq(43).all():
            raise ValueError("Frozen T0 reference changed")
        gene_columns = [f"raw_IFN_{gene}" for gene in reference.gene_symbol]

        a0_all = pd.read_csv(
            freeze / "A0_sufficient_raw_counts.csv", dtype={"donor_id": str}
        )
        a0 = a0_all.set_index("stratum_id").loc[stratum_ids].reset_index()
        a1_all = pd.read_csv(
            freeze / "A1_bin_sufficient_raw_counts.csv", dtype={"donor_id": str}
        )
        if a1_all.duplicated(["stratum_id", "A1_bin"]).any():
            raise ValueError("Duplicate donor/bin key")
        support_index = pd.MultiIndex.from_product(
            [stratum_ids, range(1, 6)], names=["stratum_id", "A1_bin"]
        )
        a1 = a1_all.set_index(["stratum_id", "A1_bin"]).reindex(support_index).reset_index()
        sufficient_columns = ["cell_count", "full_raw_library_total", *gene_columns]
        if a1[sufficient_columns].isna().any().any():
            raise ValueError("Missing supported bin; no zero fill is permitted")
        if not np.array_equal(
            a1.donor_id.to_numpy(), np.repeat(shared.donor_id.to_numpy(), 5)
        ):
            raise ValueError("A1 donor alignment failed")

        for frame in (a0, a1):
            values = frame[sufficient_columns].to_numpy(float)
            if not np.isfinite(values).all() or (values < 0).any():
                raise ValueError("Invalid raw sufficient statistics")
            if not np.equal(values, np.round(values)).all():
                raise ValueError("Sufficient statistics are not integer-valued")

        counts = a1[gene_columns].to_numpy(float).reshape(68, 5, 12)
        library_totals = a1.full_raw_library_total.to_numpy(float).reshape(68, 5)
        cell_counts = a1.cell_count.to_numpy(float).reshape(68, 5)
        if (cell_counts < 30).any():
            raise ValueError("Frozen all-five-bin support failed")
        if not np.array_equal(counts.sum(axis=1), a0[gene_columns].to_numpy(float)):
            raise ValueError("A1 gene counts do not partition A0")
        if not np.array_equal(
            library_totals.sum(axis=1), a0.full_raw_library_total.to_numpy(float)
        ):
            raise ValueError("A1 library totals do not partition A0")
        if not np.array_equal(cell_counts.sum(axis=1), a0.cell_count.to_numpy(float)):
            raise ValueError("A1 cell counts do not partition A0")

        pi_ref = (
            pd.read_csv(freeze / "09_PI_REF.csv")
            .sort_values("a1_bin")
            .pi_ref.to_numpy(float)
        )
        geometry = composition_geometry(counts, library_totals, cell_counts, pi_ref)
        ilr_cell = ilr_positive(geometry["p_cell"])
        ilr_umi = ilr_positive(geometry["q_umi"])
        five_fraction_rank = rank_no_lapack(np.c_[base_design, geometry["p_cell"]])
        ilr_rank = rank_no_lapack(np.c_[base_design, ilr_cell])

        rows = []
        for donor_index in range(68):
            for bin_index in range(5):
                rows.append(
                    {
                        "stratum_id": stratum_ids[donor_index],
                        "donor_id": shared.donor_id.iloc[donor_index],
                        "A1_bin": bin_index + 1,
                        "cells": int(cell_counts[donor_index, bin_index]),
                        "full_captured_UMI": int(library_totals[donor_index, bin_index]),
                        "p_cell": geometry["p_cell"][donor_index, bin_index],
                        "q_UMI": geometry["q_umi"][donor_index, bin_index],
                        "captured_UMI_per_cell": geometry["captured_umi_per_cell"][
                            donor_index, bin_index
                        ],
                        "fixed_pi": pi_ref[bin_index],
                        "cellref_effective_UMI_weight": geometry[
                            "pi_cellref_umiweights"
                        ][donor_index, bin_index],
                    }
                )
        write_dataframe_lf(
            pd.DataFrame(rows), output / "01_geometry_no_disease_effect.csv"
        )

        coordinates = pd.DataFrame({"stratum_id": stratum_ids})
        for coordinate in range(4):
            coordinates[f"ilr_cell_{coordinate + 1}"] = ilr_cell[:, coordinate]
            coordinates[f"ilr_UMI_{coordinate + 1}"] = ilr_umi[:, coordinate]
        write_dataframe_lf(
            coordinates, output / "02_fixed_composition_coordinates.csv"
        )

        status = {
            "status": "PASS_STRUCTURAL_PREFIT_ONLY",
            "WP2_REAL_EFFECT_UNLOCK": False,
            "G2": "NOT_EXECUTED",
            "donors": 68,
            "controls": 31,
            "managed": 37,
            "bin_count": 5,
            "bin_support_min": int(cell_counts.min()),
            "raw_count_partition_identity": True,
            "library_partition_identity": True,
            "cell_partition_identity": True,
            "base_design_rank": 4,
            "design_with_five_fractions_rank": five_fraction_rank,
            "design_with_five_fractions_columns": 9,
            "design_with_four_ILR_rank": ilr_rank,
            "design_with_four_ILR_columns": 8,
            "conditional_ILR_model_eligible": ilr_rank == 8,
            "max_abs_pooled_CPM_identity_error": float(
                np.abs(geometry["pooled_cpm"] - geometry["q_reconstructed_cpm"]).max()
            ),
            "median_abs_cell_vs_UMI_weight_difference": float(
                np.median(np.abs(geometry["p_cell"] - geometry["q_umi"]))
            ),
            "max_abs_cell_vs_UMI_weight_difference": float(
                np.abs(geometry["p_cell"] - geometry["q_umi"]).max()
            ),
            "T0_unchanged": True,
            "pi_unchanged": True,
            "real_disease_effects_fitted": False,
            "all_numeric_diagnostics_are_unstratified": True,
            "python": platform.python_version(),
            "numpy": np.__version__,
        }
        if ilr_rank < 8:
            status["status"] = "HOLD_OPTIONAL_CONDITIONAL_DESIGN_RANK"
        write_dataframe_lf(
            pd.DataFrame(manifest_records), output / "03_input_verification.csv"
        )
        write_json_lf(output / "04_PREFIT_STATUS.json", status)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return status
    except Exception as error:
        hold = {
            "status": "HOLD",
            "reason": str(error),
            "real_disease_effects_fitted": False,
            "WP2_REAL_EFFECT_UNLOCK": False,
            "G2": "NOT_EXECUTED",
        }
        write_json_lf(output / "04_PREFIT_STATUS.json", hold)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    run_prefit(arguments.project_root, arguments.output)


if __name__ == "__main__":
    main()
