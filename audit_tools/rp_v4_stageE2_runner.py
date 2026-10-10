"""Resumable synthetic-only outer runner for the frozen RP v4 G2C grid."""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
from collections import Counter
from pathlib import Path

try:
    from .rp_v3_g2_estimation import responses
    from .rp_v4_g2c_hc3t import interval
    from .rp_v4_stageE2_common import (
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        sha256_file,
        stable_json,
    )
    from .rp_v4_stageE2_generator import (
        data_digest,
        generate,
        load_inputs,
        scenario_ids,
    )
except ImportError:
    from rp_v3_g2_estimation import responses
    from rp_v4_g2c_hc3t import interval
    from rp_v4_stageE2_common import (
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        sha256_file,
        stable_json,
    )
    from rp_v4_stageE2_generator import (
        data_digest,
        generate,
        load_inputs,
        scenario_ids,
    )


def _jsonl(rows: list[dict]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
        for row in rows
    )


def _read_jsonl(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _validate_chunk(
    rows: list[dict],
    *,
    scenario_id: str,
    scenario_index: int,
    start: int,
    stop: int,
    stage: int,
) -> None:
    if [row.get("attempt_id") for row in rows] != list(range(start, stop + 1)):
        raise ValueError("Checkpoint attempt sequence drift")
    for row in rows:
        if (
            row.get("scenario_id") != scenario_id
            or row.get("scenario_index") != scenario_index
            or row.get("stage") != stage
            or row.get("seed_base") != SEED_BASE
            or row.get("data_kind") != "SIMULATED_ONLY"
            or row.get("real_effects_fitted") is not False
        ):
            raise ValueError("Checkpoint identity or safety drift")


def _attempt_record(
    *,
    model: dict,
    scenario: dict,
    scenario_index: int,
    attempt_id: int,
    authorization,
) -> dict:
    synthetic = generate(
        model, scenario, scenario_index, attempt_id, authorization
    )
    record = {
        "scenario_id": scenario["scenario_id"],
        "scenario_index": scenario_index,
        "attempt_id": attempt_id,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "data_kind": "SIMULATED_ONLY",
        "input_digest": data_digest(synthetic),
        "status": synthetic["support_status"],
        "min_bin_cells": synthetic["min_observed_cells"],
        "under_supported_bins": synthetic["under_supported_bins"],
        "zero_library_bins": synthetic["zero_library_bins"],
        "real_effects_fitted": False,
        "final_stream": authorization.final,
        "G2C_adjudicated": False,
        "external_disease_outcomes_fitted": False,
    }
    if synthetic["support_status"] == "SUPPORTED":
        try:
            outcome = responses(synthetic, model)
            record["synthetic_HC3_t"] = interval(
                synthetic["X"], outcome, data_kind="SIMULATED_ONLY"
            )
        except (ValueError, FloatingPointError, ArithmeticError) as error:
            record["status"] = "NUMERICAL_FAILURE"
            record["numerical_failure_type"] = type(error).__name__
    return record


def run(
    *,
    registry_path: Path,
    calibration_model_path: Path,
    output: Path,
    mode: str,
    resume: bool = False,
    selected_scenarios: tuple[str, ...] = ("C0_X1", "C1_X2", "C2_X3"),
    qualification_attempts: int = 8,
    authorization_path: Path | None = None,
    binding_manifest_path: Path | None = None,
) -> dict:
    if mode == "qualification":
        if not 1 <= qualification_attempts <= 8:
            raise ValueError("Qualification attempts must be between 1 and 8")
        authorization = qualification_authorization("outer")
        attempts_per_scenario = qualification_attempts
        chunk_size = qualification_attempts
        run_scenarios = selected_scenarios
    elif mode == "final":
        if authorization_path is None or binding_manifest_path is None:
            raise PermissionError("Final execution requires exact-code GO inputs")
        authorization = authorize_final(
            purpose="outer",
            authorization_path=authorization_path,
            binding_manifest_path=binding_manifest_path,
        )
        attempts_per_scenario = 4000
        chunk_size = 100
        run_scenarios = tuple(scenario_ids())
    else:
        raise ValueError("Mode must be qualification or final")

    output = Path(output)
    if output.exists() and not resume:
        raise FileExistsError("Output exists; use a new path or explicit resume")
    output.mkdir(parents=True, exist_ok=True)
    registry, model = load_inputs(registry_path, calibration_model_path)
    by_id = {row["scenario_id"]: (index, row) for index, row in enumerate(registry)}
    if len(run_scenarios) != len(set(run_scenarios)) or any(
        scenario_id not in by_id for scenario_id in run_scenarios
    ):
        raise ValueError("Unknown or duplicate requested scenario")

    contract = {
        "schema": "RP_V4_STAGE_E2_OUTER_RUN_1.0",
        "mode": mode,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "scenario_ids": list(run_scenarios),
        "attempts_per_scenario": attempts_per_scenario,
        "chunk_size": chunk_size,
        "data_kind": "SIMULATED_ONLY",
        "real_effects_fitted": False,
        "authorization_sha256": authorization.authorization_sha256,
        "binding_manifest_sha256": authorization.binding_manifest_sha256,
    }
    contract_path = output / "00_RUN_CONTRACT.json"
    contract_text = stable_json(contract)
    if contract_path.exists():
        if contract_path.read_text(encoding="utf-8") != contract_text:
            raise RuntimeError("Resume contract drift")
    else:
        atomic_write_text(contract_path, contract_text)

    reused_chunks = 0
    created_chunks = 0
    all_rows: dict[str, list[dict]] = {scenario_id: [] for scenario_id in run_scenarios}
    for scenario_id in run_scenarios:
        scenario_index, scenario = by_id[scenario_id]
        for start in range(1, attempts_per_scenario + 1, chunk_size):
            stop = min(start + chunk_size - 1, attempts_per_scenario)
            path = output / "attempts" / scenario_id / f"{start:04d}-{stop:04d}.jsonl"
            if path.exists():
                rows = _read_jsonl(path)
                _validate_chunk(
                    rows,
                    scenario_id=scenario_id,
                    scenario_index=scenario_index,
                    start=start,
                    stop=stop,
                    stage=authorization.stage,
                )
                reused_chunks += 1
            else:
                rows = [
                    _attempt_record(
                        model=model,
                        scenario=scenario,
                        scenario_index=scenario_index,
                        attempt_id=attempt_id,
                        authorization=authorization,
                    )
                    for attempt_id in range(start, stop + 1)
                ]
                path.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_text(path, _jsonl(rows))
                created_chunks += 1
            all_rows[scenario_id].extend(rows)

    accounting = []
    for scenario_id in run_scenarios:
        scenario_index, _ = by_id[scenario_id]
        rows = all_rows[scenario_id]
        _validate_chunk(
            rows,
            scenario_id=scenario_id,
            scenario_index=scenario_index,
            start=1,
            stop=attempts_per_scenario,
            stage=authorization.stage,
        )
        counts = Counter(row["status"] for row in rows)
        accounting.append(
            {
                "scenario_id": scenario_id,
                "attempts": len(rows),
                "supported": counts["SUPPORTED"],
                "support_stop": counts["SUPPORT_STOP"],
                "numerical_failures": counts["NUMERICAL_FAILURE"],
                "stage": authorization.stage,
                "final_stream": authorization.final,
                "real_effects_fitted": False,
            }
        )

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=list(accounting[0]), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(accounting)
    accounting_path = output / "01_ATTEMPT_ACCOUNTING.csv"
    accounting_text = stream.getvalue()
    if accounting_path.exists():
        if accounting_path.read_text(encoding="utf-8") != accounting_text:
            raise RuntimeError("Resume accounting drift")
    else:
        atomic_write_text(accounting_path, accounting_text)

    receipt = {
        "schema": "RP_V4_STAGE_E2_OUTER_RECEIPT_1.0",
        "mode": mode,
        "stage": authorization.stage,
        "scenario_count": len(run_scenarios),
        "attempts": len(run_scenarios) * attempts_per_scenario,
        "created_chunks": created_chunks,
        "reused_chunks": reused_chunks,
        "accounting_sha256": sha256_file(accounting_path),
        "final_G2C_adjudicated": False,
        "real_effects_fitted": False,
    }
    receipt_path = output / "02_RUN_RECEIPT.json"
    receipt_text = stable_json(receipt)
    if receipt_path.exists():
        prior = json.loads(receipt_path.read_text(encoding="utf-8"))
        prior.pop("created_chunks", None)
        prior.pop("reused_chunks", None)
        current = dict(receipt)
        current.pop("created_chunks", None)
        current.pop("reused_chunks", None)
        if prior != current:
            raise RuntimeError("Resume receipt drift")
        receipt_path.write_text(receipt_text, encoding="utf-8", newline="\n")
    else:
        atomic_write_text(receipt_path, receipt_text)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--calibration-model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("qualification", "final"), required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--scenarios", nargs="*", default=["C0_X1", "C1_X2", "C2_X3"])
    parser.add_argument("--qualification-attempts", type=int, default=8)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--binding-manifest", type=Path)
    arguments = parser.parse_args()
    print(
        stable_json(
            run(
                registry_path=arguments.registry,
                calibration_model_path=arguments.calibration_model,
                output=arguments.output,
                mode=arguments.mode,
                resume=arguments.resume,
                selected_scenarios=tuple(arguments.scenarios),
                qualification_attempts=arguments.qualification_attempts,
                authorization_path=arguments.authorization,
                binding_manifest_path=arguments.binding_manifest,
            )
        ),
        end="",
    )
