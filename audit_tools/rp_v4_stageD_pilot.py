"""Run the non-adjudicative RP v4 Stage D technical pilot."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import time
from pathlib import Path

try:
    from .rp_v3_g2_estimation import responses
    from .rp_v4_g2c_generator import data_digest, generate, load_inputs, sha256_file
    from .rp_v4_g2c_hc3t import interval
    from .rp_v4_g2c_truth import truth_pilot
except ImportError:
    from rp_v3_g2_estimation import responses
    from rp_v4_g2c_generator import data_digest, generate, load_inputs, sha256_file
    from rp_v4_g2c_hc3t import interval
    from rp_v4_g2c_truth import truth_pilot


SELECTED_SCENARIOS = ("C0_X1", "C1_X2", "C2_X3")
MAX_ATTEMPTS = 8


def stable_json(value: dict) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
    ) + "\n"


def atomic_json(path: Path, value: dict) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    partial = path.with_name(path.name + ".partial")
    if partial.exists():
        raise RuntimeError(f"Unclean checkpoint partial: {partial}")
    with partial.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(stable_json(value))
    os.replace(partial, path)


def _write_or_compare(path: Path, text: str) -> None:
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise RuntimeError(f"Replay drift: {path}")
        return
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _attempts(rows: list[dict], model: dict, output: Path, limit: int) -> tuple[list[Path], int, list[dict]]:
    files: list[Path] = []
    reused = 0
    for scenario_id in SELECTED_SCENARIOS:
        scenario_index = next(
            index for index, row in enumerate(rows) if row["scenario_id"] == scenario_id
        )
        scenario = rows[scenario_index]
        for attempt_id in range(1, limit + 1):
            destination = output / "attempts" / scenario_id / f"{attempt_id:04d}.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            synthetic = generate(model, scenario, scenario_index, attempt_id)
            record = {
                "scenario_id": scenario_id,
                "scenario_index": scenario_index,
                "attempt_id": attempt_id,
                "stage": 131,
                "seed_base": 2026101004,
                "data_kind": "SIMULATED_ONLY",
                "input_digest": data_digest(synthetic),
                "status": synthetic["support_status"],
                "min_bin_cells": synthetic["min_observed_cells"],
                "under_supported_bins": synthetic["under_supported_bins"],
                "zero_library_bins": synthetic["zero_library_bins"],
                "real_effects_fitted": False,
                "final_G2C": False,
                "external_disease_outcomes_fitted": False,
            }
            if synthetic["support_status"] == "SUPPORTED":
                outcome = responses(synthetic, model)
                record["synthetic_HC3_t"] = interval(
                    synthetic["X"], outcome, data_kind="SIMULATED_ONLY"
                )
            expected = stable_json(record).encode("utf-8")
            if destination.exists():
                if destination.read_bytes() != expected:
                    raise RuntimeError(f"Checkpoint drift: {destination}")
                reused += 1
            else:
                atomic_json(destination, record)
            files.append(destination)

    accounting: list[dict] = []
    for scenario_id in SELECTED_SCENARIOS:
        entries = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((output / "attempts" / scenario_id).glob("*.json"))
        ]
        if len(entries) != limit or [entry["attempt_id"] for entry in entries] != list(
            range(1, limit + 1)
        ):
            raise ValueError("Incomplete technical attempt sequence")
        accounting.append(
            {
                "scenario_id": scenario_id,
                "attempts": len(entries),
                "supported": sum(entry["status"] == "SUPPORTED" for entry in entries),
                "support_stop": sum(
                    entry["status"] == "SUPPORT_STOP" for entry in entries
                ),
                "numerical_failures": 0,
                "inference": "TECHNICAL_DIAGNOSTIC_ONLY",
                "real_effects_fitted": False,
            }
        )
    return files, reused, accounting


def run(
    *,
    registry: Path,
    calibration_model: Path,
    output: Path,
    limit: int = 8,
    resume: bool = False,
    truth_effort: int = 32768,
) -> dict:
    if not 1 <= limit <= MAX_ATTEMPTS:
        raise ValueError("Technical attempt limit is outside the frozen envelope")
    output = Path(output)
    if output.exists() and not resume:
        raise FileExistsError("Use a new output root or explicit resume")
    output.mkdir(parents=True, exist_ok=True)
    rows, model = load_inputs(Path(registry), Path(calibration_model))
    started = time.perf_counter()
    attempt_files, reused, accounting = _attempts(rows, model, output, limit)

    if limit != MAX_ATTEMPTS:
        return {
            "gate": {
                "stage": "INCOMPLETE_CHECKPOINT_REQUIRES_RESUME",
                "attempts": sum(row["attempts"] for row in accounting),
            },
            "checkpoint_reused": reused,
            "new_attempts": len(SELECTED_SCENARIOS) * limit - reused,
            "elapsed_seconds": round(time.perf_counter() - started, 4),
            "accounting": accounting,
        }

    truth_rows = []
    for scenario_id in SELECTED_SCENARIOS:
        scenario_index = next(
            index for index, row in enumerate(rows) if row["scenario_id"] == scenario_id
        )
        truth_rows.append(
            truth_pilot(
                model,
                rows[scenario_index],
                scenario_index,
                effort_per_arm=truth_effort,
            )
        )
    oracle = {
        "truth": truth_rows,
        "stage": 131,
        "truth_runs": len(truth_rows),
        "final_stage142_consumed": False,
        "independence": (
            "separate Philox oracle; count intensities aggregated before Poisson"
        ),
    }
    oracle_path = output / "03_INDEPENDENT_ORACLE_TECHNICAL.json"
    _write_or_compare(oracle_path, stable_json(oracle))

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(accounting[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(accounting)
    accounting_path = output / "01_ATTEMPT_ACCOUNTING.csv"
    _write_or_compare(accounting_path, stream.getvalue())

    stable_files = [*attempt_files, accounting_path, oracle_path]
    manifest_rows = [
        {
            "path": path.relative_to(output).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(stable_files)
    ]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=("path", "bytes", "sha256"), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(manifest_rows)
    _write_or_compare(output / "04_TECHNICAL_FILE_MANIFEST.csv", stream.getvalue())

    gate = {
        "stage": "RPV4_STAGE_D_TECHNICAL_ONLY",
        "decision": "PASS_DEVELOPMENT_IMPLEMENTATION__HOLD_FINAL_AUTHOR_SIGNOFF",
        "scenario_ids": list(SELECTED_SCENARIOS),
        "technical_attempts": len(SELECTED_SCENARIOS) * limit,
        "synthetic_supported": sum(row["supported"] for row in accounting),
        "synthetic_support_stop": sum(row["support_stop"] for row in accounting),
        "truth_technical_precision": [row["status"] for row in truth_rows],
        "final_grid_160000_executed": False,
        "final_truth_stage_142_executed": False,
        "real_WP2_or_external_outcomes_loaded": False,
        "G2C_PASS": False,
        "manuscript_or_submission_modified": False,
        "author_approved_final_contract": False,
        "StageC_registry_SHA256": sha256_file(Path(registry)),
        "calibration_model_SHA256": sha256_file(Path(calibration_model)),
        "next_stage": "RPV4_STAGE_E__AUTHOR_SIGNOFF_AND_FINAL_G2C_PREFLIGHT",
    }
    gate_path = output / "05_STAGE_D_PROVISIONAL_GATE.json"
    _write_or_compare(gate_path, stable_json(gate))
    return {
        "gate": gate,
        "checkpoint_reused": reused,
        "new_attempts": len(SELECTED_SCENARIOS) * limit - reused,
        "elapsed_seconds": round(time.perf_counter() - started, 4),
        "accounting": accounting,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--calibration-model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--resume", action="store_true")
    arguments = parser.parse_args()
    print(
        json.dumps(
            run(
                registry=arguments.registry,
                calibration_model=arguments.calibration_model,
                output=arguments.output,
                limit=arguments.limit,
                resume=arguments.resume,
            ),
            indent=2,
        )
    )
