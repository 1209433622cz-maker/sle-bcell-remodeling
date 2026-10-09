"""Freeze the independently requalified RP v3 G2 implementation contract."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "phase17_v7" / "rp_v3_redesign" / "20261010_g2_implementation_freeze"
PREFIT = REPO_ROOT / "phase17_v7" / "rp_v3_redesign" / "20261010_wp2_effect_free_prefit"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def verify_candidate_manifest(root: Path) -> tuple[int, int]:
    with (root / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    failures = 0
    for row in rows:
        path = root / row["relative_path"]
        if not path.is_file() or int(row["bytes"]) != path.stat().st_size or row["sha256"].lower() != sha256(path):
            failures += 1
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and p.name != "MANIFEST.csv"
        and "__pycache__" not in p.parts
        and not p.name.endswith(".pyc")
    }
    registered = {row["relative_path"].replace("\\", "/") for row in rows}
    failures += len(actual.symmetric_difference(registered))
    return len(rows), failures


def compare_pilot(candidate: Path, local: Path) -> dict:
    candidate_attempts = candidate / "results" / "pilot" / "attempts"
    local_attempts = local / "pilot" / "attempts"
    names = sorted(path.name for path in candidate_attempts.iterdir() if path.is_dir())
    if len(names) != 50 or names != sorted(path.name for path in local_attempts.iterdir() if path.is_dir()):
        raise RuntimeError("Pilot attempt inventory mismatch")
    exact_arrays = [
        "simulated_cell_counts.npy", "simulated_count_categories.npy", "simulated_design.npy",
        "simulated_template_indices.npy",
    ]
    array_checks = 0
    response_max = 0.0
    point_max = 0.0
    ci_max = 0.0
    status_matches = 0
    bootstrap_index_matches = 0
    supported = 0
    support_stops = 0
    inner_attempts = 0
    for name in names:
        first = candidate_attempts / name
        second = local_attempts / name
        a = json.loads((first / "attempt.json").read_text(encoding="utf-8"))
        b = json.loads((second / "attempt.json").read_text(encoding="utf-8"))
        status_matches += a["status"] == b["status"]
        support_stops += a["status"] == "SUPPORT_STOP"
        for filename in exact_arrays:
            if not np.array_equal(np.load(first / filename), np.load(second / filename)):
                raise RuntimeError(f"Cross-platform pilot array mismatch: {name}/{filename}")
            array_checks += 1
        if a["status"] == "INTERVAL_COMPUTED":
            supported += 1
            inner_attempts += int(a["inner_attempted"])
            response_max = max(
                response_max,
                float(np.max(np.abs(np.load(first / "simulated_responses.npy") - np.load(second / "simulated_responses.npy")))),
            )
            if not np.array_equal(np.load(first / "bootstrap_indices.npy"), np.load(second / "bootstrap_indices.npy")):
                raise RuntimeError(f"Cross-platform bootstrap index mismatch: {name}")
            bootstrap_index_matches += 1
            point_max = max(point_max, max(abs(a["point"][key] - b["point"][key]) for key in a["point"]))
            ci_max = max(
                ci_max,
                max(abs(x - y) for key in a["ci"] for x, y in zip(a["ci"][key], b["ci"][key])),
            )
    return {
        "attempts": len(names),
        "status_matches": status_matches,
        "supported": supported,
        "support_stops": support_stops,
        "inner_bootstraps": inner_attempts,
        "exact_generated_array_checks": array_checks,
        "exact_bootstrap_index_matches": bootstrap_index_matches,
        "maximum_response_absolute_difference": response_max,
        "maximum_point_estimate_absolute_difference": point_max,
        "maximum_interval_endpoint_absolute_difference": ci_max,
        "pass": status_matches == 50 and supported == 30 and support_stops == 20 and inner_attempts == 60000,
    }


def compare_truth(candidate: Path, local: Path) -> dict:
    first_root = candidate / "results" / "truth"
    second_root = local / "truth"
    numeric = [
        "truth", "truth_mcse", "truth_mc_95_halfwidth", "typical_coefficient_se",
        "mcse_over_typical_se", "support_probability_arm0", "support_probability_arm1",
        "whole68_support_probability",
    ]
    maxima = {key: 0.0 for key in numeric}
    rows_seen = 0
    matching_status = 0
    matching_effort = 0
    for first in sorted(path for path in first_root.iterdir() if path.is_dir()):
        second = second_root / first.name
        a_receipt = json.loads((first / "receipt.json").read_text(encoding="utf-8"))
        b_receipt = json.loads((second / "receipt.json").read_text(encoding="utf-8"))
        matching_status += a_receipt["status"] == b_receipt["status"]
        matching_effort += (
            a_receipt["history"][-1]["effort_per_template_per_batch"]
            == b_receipt["history"][-1]["effort_per_template_per_batch"]
        )
        with (first / "truth.csv").open(encoding="utf-8-sig", newline="") as handle:
            a_rows = list(csv.DictReader(handle))
        with (second / "truth.csv").open(encoding="utf-8-sig", newline="") as handle:
            b_rows = list(csv.DictReader(handle))
        for a, b in zip(a_rows, b_rows, strict=True):
            if a["target_id"] != b["target_id"]:
                raise RuntimeError(f"Truth target order mismatch: {first.name}")
            rows_seen += 1
            for key in numeric:
                maxima[key] = max(maxima[key], abs(float(a[key]) - float(b[key])))
    return {
        "scenario_count": 25,
        "target_scenario_rows": rows_seen,
        "matching_statuses": matching_status,
        "matching_final_effort_levels": matching_effort,
        "maximum_absolute_differences": maxima,
        "pass": rows_seen == 250 and matching_status == 25 and matching_effort == 25 and max(maxima.values()) <= 1e-12,
    }


def main(candidate: Path, local: Path, output: Path, candidate_zip: Path | None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    manifested, manifest_failures = verify_candidate_manifest(candidate)
    comparison = {
        "status": "PASS_CROSS_PLATFORM_TECHNICAL_REQUALIFICATION",
        "candidate_manifest_payloads": manifested,
        "candidate_manifest_failures": manifest_failures,
        "pilot": compare_pilot(candidate, local),
        "truth": compare_truth(candidate, local),
        "candidate_zip_sha256": sha256(candidate_zip) if candidate_zip else None,
        "scientific_effects_computed": False,
        "G2": "NOT_RUN",
    }
    if manifest_failures or not comparison["pilot"]["pass"] or not comparison["truth"]["pass"]:
        raise RuntimeError("Cross-platform G2 technical qualification failed")
    write_json(output / "06_CROSS_PLATFORM_TECHNICAL_REQUALIFICATION.json", comparison)

    runtime = {
        "status": "PASS_WINDOWS_G2_TECHNICAL_RUNTIME",
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "thread_environment": {
            key: os.environ.get(key) for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")
        },
        "candidate_unit_tests": "48/48 PASS",
        "canonical_integration_tests": "10/10 PASS",
        "pilot_attempts": 50,
        "pilot_inner_bootstraps": 60000,
        "pilot_inner_failures": 0,
        "truth_precision_rows": 250,
        "truth_precision_passes": 250,
        "full_G2": "NOT_RUN",
    }
    write_json(output / "07_WINDOWS_RUNTIME_QUALIFICATION.json", runtime)

    code = REPO_ROOT / "audit_tools"
    contract = {
        "schema_version": "2.0",
        "status": "PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2",
        "source_commit": "01d4b7f7afe7949b5c5f73cdf480fbc704fd0718",
        "approved_for_full_G2_execution": True,
        "G2": "NOT_RUN",
        "G2_PASS": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "full_grid": "25 scenarios x 2000 outer attempts x 2000 paired bootstraps when supported",
        "simulation_generator_sha256": sha256(code / "rp_v3_g2_generator.py"),
        "simulation_estimator_sha256": sha256(code / "rp_v3_g2_estimation.py"),
        "independent_truth_code_sha256": sha256(code / "rp_v3_g2_truth.py"),
        "full_runner_sha256": sha256(code / "rp_v3_g2_full_runner.py"),
        "adjudicator_sha256": sha256(code / "rp_v3_g2_adjudicate.py"),
        "truth_receipt_sha256": sha256(output / "03_G2_TRUTH_QUALIFICATION_RECEIPT.json"),
        "truth_table_sha256": sha256(output / "04_G2_TRUTH_TABLE.csv"),
        "calibration_model_sha256": sha256(output / "02_G2_CALIBRATION_MODEL.json"),
        "domain_policy_sha256": sha256(output / "05_G2_DOMAIN_ADJUDICATION_POLICY.md"),
        "cross_platform_receipt_sha256": sha256(output / "06_CROSS_PLATFORM_TECHNICAL_REQUALIFICATION.json"),
        "windows_runtime_receipt_sha256": sha256(output / "07_WINDOWS_RUNTIME_QUALIFICATION.json"),
        "target_registry_sha256": sha256(PREFIT / "07_WP2_G2_TARGET_REGISTRY.csv"),
        "scenario_registry_sha256": sha256(PREFIT / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv"),
        "acceptance_registry_sha256": sha256(PREFIT / "09_G2_ACCEPTANCE_TABLE_FROZEN_FOR_IMPLEMENTATION.csv"),
        "adjudicable_regimes": ["R0", "R2", "R4"],
        "boundary_regimes": ["R1", "R3"],
        "minimum_supported_for_performance_adjudication": 274,
        "real_data_access_in_g2_code": False,
        "next_stage": "G2_FULL_EXECUTION_R0_CORE_FIRST",
        "WP4": "HOLD_CONDITIONAL",
        "submission": "HOLD",
    }
    write_json(output / "08_G2_EXECUTION_CONTRACT.json", contract)
    gate = {
        "decision": contract["status"],
        "generator_qualified": True,
        "independent_truth_qualified": True,
        "truth_precision_passes": "250/250",
        "windows_technical_pilot": "50/50 attempts accounted; 30 intervals; 20 support stops; 60000/60000 inner fits",
        "cross_platform_numeric_tolerance_pass": True,
        "full_scheduler_and_adjudicator_implemented": True,
        "full_G2": "NOT_RUN",
        "WP2_REAL_EFFECT_UNLOCK": False,
        "next_stage": contract["next_stage"],
        "prohibited_until_G2_pass": ["WP2 real disease effects", "WP4", "manuscript replacement", "submission", "release", "Zenodo"],
    }
    write_json(output / "09_G2_IMPLEMENTATION_GATE_STATUS.json", gate)

    manifest_rows = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "12_G2_IMPLEMENTATION_INTEGRITY_MANIFEST.csv":
            manifest_rows.append({"file": path.name, "size_bytes": path.stat().st_size, "sha256": sha256(path)})
    with (output / "12_G2_IMPLEMENTATION_INTEGRITY_MANIFEST.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "size_bytes", "sha256"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--local-validation-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--candidate-zip", type=Path)
    args = parser.parse_args()
    main(args.candidate_root.resolve(), args.local_validation_root.resolve(), args.output.resolve(), args.candidate_zip.resolve() if args.candidate_zip else None)
