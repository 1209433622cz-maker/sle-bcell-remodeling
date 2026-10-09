#!/usr/bin/env python3
"""Adjudicate the RP v3 WP2 effect-free preflight and freeze G2 registries."""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from rp_v3_wp2_kernels import freeze_ready


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")


def write_json_lf(path: Path, payload: dict) -> None:
    write_text_lf(path, json.dumps(payload, ensure_ascii=False, indent=2))


def target_registry() -> list[dict]:
    rows = [
        {
            "target_id": "beta_B",
            "operator": "b_X[T0(sum_k q_UMI,k m_k)]",
            "novelty": "WP1_ALIAS_BETA_A0",
            "g2_role": "REQUIRED_REFERENCE",
            "interpretation_boundary": "broad captured-relative-expression association",
        },
        {
            "target_id": "beta_S_profile",
            "operator": "b_X[T0(sum_k pi_ref,k m_k)]",
            "novelty": "WP1_ALIAS_BETA_A1",
            "g2_role": "REQUIRED_REFERENCE",
            "interpretation_boundary": "fixed-profile-mixture association; not pure cell composition",
        },
        {
            "target_id": "delta_profile",
            "operator": "beta_S_profile - beta_B",
            "novelty": "WP1_ALIAS_DELTA_A1_A0",
            "g2_role": "REQUIRED_REFERENCE",
            "interpretation_boundary": "joint identity-axis/profile-mixture sensitivity; not mediation",
        },
        {
            "target_id": "beta_S_cellref",
            "operator": "b_X[T0(sum_k q_cellref,k m_k)]",
            "novelty": "NEW_WP2_BRIDGE_TARGET",
            "g2_role": "REQUIRED_NEW_TARGET",
            "interpretation_boundary": "fixed cell reference with observed captured UMI/cell; not absolute RNA",
        },
        {
            "target_id": "delta_cellref",
            "operator": "beta_S_cellref - beta_B",
            "novelty": "NEW_WP2_BRIDGE_CONTRAST",
            "g2_role": "REQUIRED_NEW_TARGET",
            "interpretation_boundary": "descriptive target contrast; not a mediated proportion",
        },
    ]
    for bin_id in range(1, 6):
        rows.append(
            {
                "target_id": f"beta_bin_{bin_id}",
                "operator": f"b_X[T0(m_bin_{bin_id})]",
                "novelty": "NEW_WP2_AXIS_INTERVAL_TARGET",
                "g2_role": "REQUIRED_NEW_TARGET",
                "interpretation_boundary": "relative-expression association within a frozen axis interval; not a hard subtype",
            }
        )
    rows.append(
        {
            "target_id": "beta_cond_ILR",
            "operator": "managed coefficient in X plus four frozen cell-fraction ILR coordinates",
            "novelty": "NEW_OPTIONAL_CONDITIONAL_DIAGNOSTIC",
            "g2_role": "SEPARATE_DIAGNOSTIC_CONTRACT_REQUIRED",
            "interpretation_boundary": "conditional association; not equivalent to standardization or a direct effect",
        }
    )
    return rows


def scenario_registry() -> list[dict]:
    truth_structures = {
        "C0": ("null", 0.0, 0.0),
        "C1": ("composition_only", 0.35, 0.0),
        "C2": ("within_bin_only", 0.0, 0.40),
        "C3": ("same_direction", 0.35, 0.40),
        "C4": ("opposite_direction", 0.35, -0.40),
    }
    regimes = {
        "R0": ("baseline", 1.0, 1.0, 0.0, 0.0, "REQUIRED_CORE"),
        "R1": ("rarity_support", 0.35, 1.0, 0.0, 0.0, "SUPPORT_BOUNDARY"),
        "R2": ("depth_imbalance", 1.0, 0.50, 0.0, 0.0, "MEASUREMENT_STRESS"),
        "R3": ("adjacent_mislabeling", 1.0, 1.0, 0.15, 0.0, "MISLABEL_STRESS"),
        "R4": ("RNA_capture_content", 1.0, 1.0, 0.0, 0.40, "CAPTURE_STRESS"),
    }
    rows = []
    for core_id, (truth, composition_tilt, within_log2fc) in truth_structures.items():
        for regime_id, values in regimes.items():
            regime, rarity, depth, mislabel, capture, domain = values
            rows.append(
                {
                    "scenario_id": f"{core_id}_{regime_id}",
                    "truth_structure": truth,
                    "regime": regime,
                    "outer_attempts": 2000,
                    "inner_paired_bootstraps": 2000,
                    "composition_log_tilt": composition_tilt,
                    "within_bin_log2fc": within_log2fc,
                    "rare_bin_weight_multiplier": rarity,
                    "managed_depth_multiplier": depth,
                    "adjacent_mislabel_probability": mislabel,
                    "managed_capture_log_tilt": capture,
                    "domain_classification": domain,
                    "execution_status": "NOT_RUN",
                }
            )
    return rows


def acceptance_registry() -> list[dict]:
    return [
        {
            "metric": "bias_upper95_in_empirical_SD",
            "rule": "(abs(bias)+1.96*MCSE_bias)/EmpSD <= 0.10",
            "scope": "adjudicable target-scenario cells",
            "failure_policy": "HOLD_TARGET_SCENARIO",
        },
        {
            "metric": "coverage",
            "rule": "Wilson 95% interval wholly within [0.925,0.975]",
            "scope": "adjudicable target-scenario cells",
            "failure_policy": "HOLD_TARGET_SCENARIO",
        },
        {
            "metric": "true_null_type_I",
            "rule": "Wilson 95% upper bound <= 0.075",
            "scope": "independently registered true-null cells only",
            "failure_policy": "HOLD_TARGET_SCENARIO",
        },
        {
            "metric": "numerical_failure",
            "rule": "failures/2000 <= 0.01; expected support stops reported separately",
            "scope": "all attempted replicates",
            "failure_policy": "HOLD_NUMERICAL_IMPLEMENTATION",
        },
        {
            "metric": "oracle_truth_precision",
            "rule": "oracle MCSE <= 0.01 * typical coefficient SE",
            "scope": "each target-scenario truth receipt",
            "failure_policy": "HOLD_TRUTH_PRECISION",
        },
        {
            "metric": "attempt_accounting",
            "rule": "all attempt IDs retained; no failed-attempt replacement",
            "scope": "all scenarios",
            "failure_policy": "INVALID_RUN",
        },
    ]


def run_review(project_root: Path, prefit_dir: Path) -> dict:
    project_root = project_root.resolve()
    prefit_dir = prefit_dir.resolve()
    if not prefit_dir.is_relative_to(project_root):
        raise ValueError("Prefit output must be inside the project")

    status_path = prefit_dir / "04_PREFIT_STATUS.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    required_true = [
        "raw_count_partition_identity",
        "library_partition_identity",
        "cell_partition_identity",
        "conditional_ILR_model_eligible",
        "T0_unchanged",
        "pi_unchanged",
        "all_numeric_diagnostics_are_unstratified",
    ]
    checks = [
        ("structural_status", status.get("status") == "PASS_STRUCTURAL_PREFIT_ONLY"),
        ("donor_count", status.get("donors") == 68),
        ("arm_counts", status.get("controls") == 31 and status.get("managed") == 37),
        ("five_bins", status.get("bin_count") == 5),
        ("minimum_support", status.get("bin_support_min", 0) >= 30),
        ("base_design_rank", status.get("base_design_rank") == 4),
        ("ilr_design_rank", status.get("design_with_four_ILR_rank") == 8),
        ("no_effect_fit", status.get("real_disease_effects_fitted") is False),
        ("wp2_locked", status.get("WP2_REAL_EFFECT_UNLOCK") is False),
        ("g2_not_run", status.get("G2") == "NOT_EXECUTED"),
    ]
    checks.extend((field, status.get(field) is True) for field in required_true)

    geometry = pd.read_csv(prefit_dir / "01_geometry_no_disease_effect.csv")
    coordinates = pd.read_csv(prefit_dir / "02_fixed_composition_coordinates.csv")
    checks.extend(
        [
            ("geometry_rows", len(geometry) == 68 * 5),
            ("geometry_donors", geometry.stratum_id.nunique() == 68),
            ("coordinate_rows", len(coordinates) == 68),
            ("coordinate_columns", len([c for c in coordinates if c.startswith("ilr_")]) == 8),
            ("cell_closure", np.allclose(geometry.groupby("stratum_id").p_cell.sum(), 1.0)),
            ("umi_closure", np.allclose(geometry.groupby("stratum_id").q_UMI.sum(), 1.0)),
        ]
    )
    audit_rows = [
        {"check": name, "pass": bool(passed), "detail": ""}
        for name, passed in checks
    ]
    write_csv(prefit_dir / "05_WP2_PREFIT_FINAL_AUDIT.csv", audit_rows)

    targets_path = prefit_dir / "07_WP2_G2_TARGET_REGISTRY.csv"
    scenarios_path = prefit_dir / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv"
    acceptance_path = prefit_dir / "09_G2_ACCEPTANCE_TABLE_FROZEN_FOR_IMPLEMENTATION.csv"
    write_csv(targets_path, target_registry())
    write_csv(scenarios_path, scenario_registry())
    write_csv(acceptance_path, acceptance_registry())

    now = datetime.now(ZoneInfo("Asia/Hong_Kong")).isoformat(timespec="seconds")
    gate = {
        "created_at": now,
        "decision": (
            "PASS_WP2_EFFECT_FREE_PREFLIGHT__HOLD_G2_EXECUTION_IMPLEMENTATION_REQUIRED"
            if all(passed for _, passed in checks)
            else "HOLD_WP2_PREFLIGHT_REPAIR_REQUIRED"
        ),
        "structural_prefit_pass": all(passed for _, passed in checks),
        "WP2_REAL_EFFECT_UNLOCK": False,
        "G2": "NOT_RUN",
        "G2_execution_contract_frozen": False,
        "target_registry_frozen_before_G2_results": True,
        "scenario_registry_frozen_before_G2_results": True,
        "acceptance_table_frozen_before_G2_results": True,
        "p_cell_and_q_UMI_are_distinct_estimands": True,
        "median_abs_p_minus_q": status["median_abs_cell_vs_UMI_weight_difference"],
        "maximum_abs_p_minus_q": status["max_abs_cell_vs_UMI_weight_difference"],
        "next_stage": "G2_GENERATOR_TRUTH_ENGINE_AND_TECHNICAL_PILOT",
        "submission": "HOLD",
        "WP4": "HOLD_CONDITIONAL",
    }
    write_json_lf(prefit_dir / "06_WP2_PREFIT_GATE_STATUS.json", gate)

    calibration_path = prefit_dir / "13_G2_RESULT_BLIND_CALIBRATION.json"
    calibration = {
        "created_at": now,
        "scope": "unstratified measurement geometry only; no disease effects or grouped expression summaries",
        "donor_bins": int(len(geometry)),
        "donors": int(geometry.stratum_id.nunique()),
        "cell_count_quantiles": {
            str(probability): float(geometry.cells.quantile(probability))
            for probability in (0.05, 0.5, 0.95)
        },
        "full_captured_UMI_quantiles": {
            str(probability): float(geometry.full_captured_UMI.quantile(probability))
            for probability in (0.05, 0.5, 0.95)
        },
        "captured_UMI_per_cell_quantiles": {
            str(probability): float(geometry.captured_UMI_per_cell.quantile(probability))
            for probability in (0.05, 0.5, 0.95)
        },
        "absolute_p_minus_q_quantiles": {
            str(probability): float(
                (geometry.p_cell - geometry.q_UMI).abs().quantile(probability)
            )
            for probability in (0.05, 0.5, 0.95, 1.0)
        },
        "scenario_strengths_are_protocol_choices_not_observed_disease_effects": True,
    }
    write_json_lf(calibration_path, calibration)

    configuration_buffer = io.StringIO()
    with contextlib.redirect_stdout(configuration_buffer):
        np.show_config()
    runtime_path = prefit_dir / "14_G2_RUNTIME_LOCK.json"
    runtime_lock = {
        "created_at": now,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "thread_environment": {
            key: os.environ.get(key)
            for key in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
        "numpy_configuration": configuration_buffer.getvalue(),
        "runtime_status": "PREFIT_VALIDATED_G2_NUMERICAL_PILOT_STILL_REQUIRED",
    }
    write_json_lf(runtime_path, runtime_lock)

    freeze_dir = project_root / "phase17_v7/rp_v3_redesign/20261010_wp1_prefit_freeze"
    raw_counts_path = freeze_dir / "A1_bin_sufficient_raw_counts.csv"
    branch_assignments_path = freeze_dir / "cell_mapping_and_A1_axis.csv.gz"

    contract = {
        "schema_version": "1.0",
        "created_at": now,
        "status": "HOLD_G2_EXECUTION_FREEZE_IMPLEMENTATION_INCOMPLETE",
        "approved_for_execution": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "G2": "NOT_RUN",
        "shared_donors": 68,
        "controls": 31,
        "managed_SLE": 37,
        "bins": 5,
        "min_cells_per_bin": 30,
        "simulation_outer_replicates": 2000,
        "inner_paired_bootstraps": 2000,
        "outer_seed": 2026101002,
        "truth_seed": 2026101003,
        "prefit_receipt_sha256": sha256_file(status_path),
        "raw_counts_sha256": sha256_file(raw_counts_path),
        "branch_assignments_sha256": sha256_file(branch_assignments_path),
        "simulation_generator_sha256": None,
        "independent_truth_code_sha256": None,
        "truth_receipt_sha256": None,
        "calibration_inputs_sha256": sha256_file(calibration_path),
        "runtime_lock_sha256": sha256_file(runtime_path),
        "scenario_registry_sha256": sha256_file(scenarios_path),
        "acceptance_table_sha256": sha256_file(acceptance_path),
        "target_registry_sha256": sha256_file(targets_path),
        "required_execution_rule": "No WP2 disease effect before a hash-complete G2 contract and applicable-domain PASS",
    }
    contract["freeze_readiness"] = freeze_ready(contract)
    write_json_lf(prefit_dir / "10_G2_IMPLEMENTATION_CONTRACT.json", contract)

    review = f"""# RP v3 WP2 effect-free preflight advisor review

**Created:** {now}
**Decision:** `{gate['decision']}`

## What passed

- The canonical 68-donor population remains 31 controls and 37 source-defined
  managed-SLE donors; the four-column base design is rank 4/4.
- All five frozen A1 bins are observed for every donor, with a minimum of
  {status['bin_support_min']} cells per donor-bin.
- Gene counts, full captured-library totals and cell counts exactly partition
  the parent A0 sufficient statistics.
- Captured-UMI reconstruction recovers pooled CPM to a maximum absolute error of
  {status['max_abs_pooled_CPM_identity_error']:.3e}.
- Cell fractions and captured-UMI fractions are measurably different: median
  absolute difference {status['median_abs_cell_vs_UMI_weight_difference']:.6f},
  maximum {status['max_abs_cell_vs_UMI_weight_difference']:.6f}.
- Four frozen cell-fraction ILR coordinates produce an 8/8 full-rank optional
  conditional design. Five raw fractions plus an intercept remain closure
  redundant (rank {status['design_with_five_fractions_rank']}/9).
- No disease coefficient, disease-stratified expression summary or new IFN score
  was calculated in this gate.

## Scientific adjudication

The WP1 fixed-profile mixture and the new cell-reference reconstruction are
distinct measurement targets. The latter preserves observed captured UMI per
cell and therefore still combines biological RNA output with capture efficiency;
it is not an absolute-RNA or causal cell-composition estimand. The five bins are
frozen intervals of the continuous A1 axis, not validated hard B-cell subtypes.

The target, 25-cell scenario and numerical-acceptance registries are frozen now,
before G2 results. This does not complete the execution contract. The supplied
external candidate contains no simulation generator, independently implemented
truth engine or truth-precision receipt. The project-side preflight now binds
the validated sufficient counts, branch assignment, result-blind geometry
calibration and runtime receipt; the three genuinely missing execution hashes
remain null in `10_G2_IMPLEMENTATION_CONTRACT.json`.

## Next gate

Proceed to `G2_GENERATOR_TRUTH_ENGINE_AND_TECHNICAL_PILOT`. The technical pilot
must prove raw/sufficient-count observation equivalence, independent nonlinear
truth calculation, exact attempt accounting, resumability and the actual paired
bootstrap interval implementation. Only then may the G2 execution contract be
hash-completed. WP2 real effects, WP4, manuscript/figure replacement, submission,
Release and Zenodo remain on hold.
"""
    write_text_lf(prefit_dir / "11_WP2_PREFIT_ADVISOR_REVIEW.md", review)

    manifest_rows = []
    for path in sorted(prefit_dir.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.name == "12_WP2_PREFIT_INTEGRITY_MANIFEST.csv":
            continue
        manifest_rows.append(
            {
                "relative_path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    write_csv(prefit_dir / "12_WP2_PREFIT_INTEGRITY_MANIFEST.csv", manifest_rows)
    print(json.dumps(gate, ensure_ascii=False, indent=2))
    return gate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--prefit-dir", required=True, type=Path)
    arguments = parser.parse_args()
    run_review(arguments.project_root, arguments.prefit_dir)


if __name__ == "__main__":
    main()
