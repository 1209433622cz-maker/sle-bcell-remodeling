"""Chunked, resumable full-G2 runner for the RP v3 WP2 estimands.

This module only accepts the frozen simulation calibration object. It never
loads real WP2 responses and cannot fit a real disease coefficient.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import time
from pathlib import Path

import numpy as np

try:
    from .rp_v3_g2_estimation import TARGETS, paired_bootstrap, responses
    from .rp_v3_g2_generator import FULL_STAGE, data_digest, generate, load_model, scenarios, stream
except ImportError:  # Direct script execution from audit_tools/.
    from rp_v3_g2_estimation import TARGETS, paired_bootstrap, responses
    from rp_v3_g2_generator import FULL_STAGE, data_digest, generate, load_model, scenarios, stream


REPO_ROOT = Path(__file__).resolve().parents[1]
FREEZE_DIR = REPO_ROOT / "phase17_v7" / "rp_v3_redesign" / "20261010_g2_implementation_freeze"
PREFIT_DIR = REPO_ROOT / "phase17_v7" / "rp_v3_redesign" / "20261010_wp2_effect_free_prefit"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(repo_root: Path = REPO_ROOT) -> dict:
    freeze = repo_root / FREEZE_DIR.relative_to(REPO_ROOT)
    prefit = repo_root / PREFIT_DIR.relative_to(REPO_ROOT)
    paths = {
        "generator": repo_root / "audit_tools" / "rp_v3_g2_generator.py",
        "estimator": repo_root / "audit_tools" / "rp_v3_g2_estimation.py",
        "full_runner": repo_root / "audit_tools" / "rp_v3_g2_full_runner.py",
        "adjudicator": repo_root / "audit_tools" / "rp_v3_g2_adjudicate.py",
        "calibration_model": freeze / "02_G2_CALIBRATION_MODEL.json",
        "truth_table": freeze / "04_G2_TRUTH_TABLE.csv",
        "domain_policy": freeze / "05_G2_DOMAIN_ADJUDICATION_POLICY.md",
        "target_registry": prefit / "07_WP2_G2_TARGET_REGISTRY.csv",
        "scenario_registry": prefit / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv",
        "acceptance_registry": prefit / "09_G2_ACCEPTANCE_TABLE_FROZEN_FOR_IMPLEMENTATION.csv",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing G2 binding inputs: " + ", ".join(missing))
    result = {
        "schema": "RP_V3_G2_FULL_1.0",
        "stage": FULL_STAGE,
        "outer_attempts_per_scenario": 2000,
        "inner_paired_bootstraps": 2000,
        "scenario_count": 25,
        "target_count": 10,
        "real_effects_permitted": False,
        "hashes": {key: sha256(path) for key, path in paths.items()},
    }
    result["binding_sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return result


def _write_csv_gz(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_bytes(gzip.compress(text.getvalue().encode("utf-8"), mtime=0))


def _manifest(directory: Path) -> dict:
    files = {
        path.name: sha256(path)
        for path in sorted(directory.iterdir())
        if path.is_file() and path.name != "manifest.json"
    }
    result = {"files": files}
    (directory / "manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return result


def verify_chunk(directory: Path, expected_binding: str) -> dict:
    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Partial G2 chunk must be preserved and rerun elsewhere: {directory}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = {p.name for p in directory.iterdir() if p.is_file() and p.name != "manifest.json"}
    if actual != set(manifest["files"]) or any(p.is_dir() for p in directory.iterdir()):
        raise RuntimeError(f"Chunk contains missing or orphan payloads: {directory}")
    for name, digest in manifest["files"].items():
        if sha256(directory / name) != digest:
            raise RuntimeError(f"Chunk hash mismatch: {directory / name}")
    receipt = json.loads((directory / "receipt.json").read_text(encoding="utf-8"))
    if receipt["binding_sha256"] != expected_binding:
        raise RuntimeError(f"Chunk belongs to a different frozen implementation: {directory}")
    return receipt


FIELDS = [
    "scenario_id", "regime", "domain_classification", "attempt_id", "target_id", "status",
    "point", "ci_lower", "ci_upper", "min_observed_cells", "under_supported_bins",
    "zero_library_bins", "inner_attempted", "inner_successful", "inner_failures",
    "data_sha256", "bootstrap_indices_sha256", "error_type", "error",
]


def _rows_for_attempt(model: dict, scenario: dict, scenario_index: int, attempt: int) -> list[dict]:
    common = {
        "scenario_id": scenario["scenario_id"],
        "regime": scenario["regime"],
        "domain_classification": scenario["domain_classification"],
        "attempt_id": attempt,
        "point": "",
        "ci_lower": "",
        "ci_upper": "",
        "min_observed_cells": "",
        "under_supported_bins": "",
        "zero_library_bins": "",
        "inner_attempted": 0,
        "inner_successful": 0,
        "inner_failures": 0,
        "data_sha256": "",
        "bootstrap_indices_sha256": "",
        "error_type": "",
        "error": "",
    }
    try:
        data = generate(model, scenario, scenario_index, attempt, stage=FULL_STAGE)
        common.update(
            min_observed_cells=data["min_observed_cells"],
            under_supported_bins=data["under_supported_bins"],
            zero_library_bins=data["zero_library_bins"],
            data_sha256=data_digest(data),
        )
        if data["support_status"] == "SUPPORT_STOP":
            return [{**common, "target_id": target, "status": "SUPPORT_STOP"} for target in TARGETS]
        y = responses(data, model)
        boot = paired_bootstrap(
            data["X"], y, stream(scenario_index, attempt, 5, stage=FULL_STAGE), attempts=2000
        )
        common.update(
            inner_attempted=boot["attempted"],
            inner_successful=int(boot["success"].sum()),
            inner_failures=int(boot["failures"]),
            bootstrap_indices_sha256=hashlib.sha256(
                np.ascontiguousarray(boot["indices"]).tobytes()
            ).hexdigest(),
        )
        status = "INTERVAL_COMPUTED" if boot["gate"] == "TECHNICAL_INTERVAL_COMPUTED" else boot["gate"]
        return [
            {
                **common,
                "target_id": target,
                "status": status,
                "point": format(float(boot["point"][j]), ".17g"),
                "ci_lower": format(float(boot["interval"][j, 0]), ".17g"),
                "ci_upper": format(float(boot["interval"][j, 1]), ".17g"),
            }
            for j, target in enumerate(TARGETS)
        ]
    except Exception as exc:  # Persist every numerical/implementation failure.
        common.update(error_type=type(exc).__name__, error=str(exc))
        return [
            {**common, "target_id": target, "status": "NUMERICAL_OR_IMPLEMENTATION_FAILURE"}
            for target in TARGETS
        ]


def run_chunk(
    output_root: Path,
    scenario_id: str,
    attempt_start: int,
    attempt_end: int,
    repo_root: Path = REPO_ROOT,
) -> dict:
    if not 1 <= attempt_start <= attempt_end <= 2000:
        raise ValueError("Attempt range must be within 1..2000")
    bound = binding(repo_root)
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    run_binding = output_root / "run_binding.json"
    if run_binding.exists():
        if json.loads(run_binding.read_text(encoding="utf-8")) != bound:
            raise RuntimeError("Output root belongs to a different frozen implementation")
    else:
        run_binding.write_text(
            json.dumps(bound, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )

    freeze = repo_root / FREEZE_DIR.relative_to(REPO_ROOT)
    prefit = repo_root / PREFIT_DIR.relative_to(REPO_ROOT)
    all_scenarios = scenarios(prefit / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv")
    matches = [(i, row) for i, row in enumerate(all_scenarios) if row["scenario_id"] == scenario_id]
    if len(matches) != 1:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    scenario_index, scenario = matches[0]
    model = load_model(freeze / "02_G2_CALIBRATION_MODEL.json")

    scenario_dir = output_root / scenario_id
    scenario_dir.mkdir(exist_ok=True)
    chunk_dir = scenario_dir / f"chunk_{attempt_start:04d}_{attempt_end:04d}"
    if chunk_dir.exists():
        receipt = verify_chunk(chunk_dir, bound["binding_sha256"])
        if receipt["attempt_start"] != attempt_start or receipt["attempt_end"] != attempt_end:
            raise RuntimeError("Existing chunk range mismatch")
        return {**receipt, "reused": True}

    chunk_dir.mkdir()
    started = time.perf_counter()
    rows: list[dict] = []
    for attempt in range(attempt_start, attempt_end + 1):
        rows.extend(_rows_for_attempt(model, scenario, scenario_index, attempt))
    _write_csv_gz(chunk_dir / "attempt_targets.csv.gz", rows, FIELDS)
    attempt_status = {}
    for row in rows:
        attempt_status.setdefault(int(row["attempt_id"]), row["status"])
    counts = {status: list(attempt_status.values()).count(status) for status in sorted(set(attempt_status.values()))}
    receipt = {
        "status": "G2_CHUNK_COMPLETE",
        "binding_sha256": bound["binding_sha256"],
        "scenario_id": scenario_id,
        "attempt_start": attempt_start,
        "attempt_end": attempt_end,
        "attempts": attempt_end - attempt_start + 1,
        "target_rows": len(rows),
        "attempt_status_counts": counts,
        "elapsed_seconds": time.perf_counter() - started,
        "no_replenishment": True,
        "real_effects_fitted": False,
    }
    (chunk_dir / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    _manifest(chunk_dir)
    return {**receipt, "reused": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--attempt-start", type=int, required=True)
    parser.add_argument("--attempt-end", type=int, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run_chunk(args.output_root, args.scenario, args.attempt_start, args.attempt_end),
            indent=2,
        )
    )
