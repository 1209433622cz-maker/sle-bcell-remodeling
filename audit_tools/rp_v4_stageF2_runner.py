"""Hash-sealed, resumable synthetic outer runner for RP v4 Stage F2."""
from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path

try:
    from .rp_v3_g2_estimation import responses
    from .rp_v4_g2c_hc3t import interval
    from .rp_v4_stageF2_common import (
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        read_json,
        sha256_file,
        stable_json,
    )
    from .rp_v4_stageF2_generator import (
        data_digest,
        generate,
        load_inputs,
        scenario_ids,
    )
except ImportError:
    from rp_v3_g2_estimation import responses
    from rp_v4_g2c_hc3t import interval
    from rp_v4_stageF2_common import (
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        read_json,
        sha256_file,
        stable_json,
    )
    from rp_v4_stageF2_generator import (
        data_digest,
        generate,
        load_inputs,
        scenario_ids,
    )


CHUNK_MANIFEST_FIELDS = (
    "scenario_id",
    "scenario_index",
    "start",
    "stop",
    "payload_path",
    "payload_bytes",
    "payload_sha256",
    "seal_path",
    "seal_bytes",
    "seal_sha256",
)


def _jsonl(rows: list[dict]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
        for row in rows
    )


def _read_jsonl(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _csv_text(rows: list[dict], fieldnames: tuple[str, ...] | list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _validate_chunk(
    rows: list[dict],
    *,
    scenario_id: str,
    scenario_index: int,
    start: int,
    stop: int,
    stage: int,
    final_stream: bool,
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
            or row.get("final_stream") is not final_stream
            or row.get("G2C_adjudicated") is not False
            or row.get("external_disease_outcomes_fitted") is not False
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
    synthetic = generate(model, scenario, scenario_index, attempt_id, authorization)
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


def _chunk_paths(
    root: Path, scenario_id: str, start: int, stop: int
) -> tuple[Path, Path]:
    payload = root / "attempts" / scenario_id / f"{start:04d}-{stop:04d}.jsonl"
    seal = payload.with_name(payload.name + ".seal.json")
    return payload, seal


def _seal_payload(
    *,
    root: Path,
    payload: Path,
    seal: Path,
    contract_sha: str,
    scenario_id: str,
    scenario_index: int,
    start: int,
    stop: int,
    stage: int,
) -> dict:
    value = {
        "schema": "RP_V4_STAGE_F2_OUTER_CHUNK_SEAL_1.0",
        "contract_sha256": contract_sha,
        "scenario_id": scenario_id,
        "scenario_index": scenario_index,
        "start": start,
        "stop": stop,
        "stage": stage,
        "payload_path": payload.relative_to(root).as_posix(),
        "payload_bytes": payload.stat().st_size,
        "payload_sha256": sha256_file(payload),
    }
    atomic_write_text(seal, stable_json(value))
    return value


def _verify_chunk_pair(
    *,
    root: Path,
    payload: Path,
    seal: Path,
    contract_sha: str,
    scenario_id: str,
    scenario_index: int,
    start: int,
    stop: int,
    stage: int,
    final_stream: bool,
) -> tuple[list[dict], dict]:
    if payload.exists() != seal.exists():
        raise RuntimeError("Chunk payload/seal pair is incomplete")
    if not payload.exists():
        raise FileNotFoundError(payload)
    value = read_json(seal)
    expected = {
        "schema": "RP_V4_STAGE_F2_OUTER_CHUNK_SEAL_1.0",
        "contract_sha256": contract_sha,
        "scenario_id": scenario_id,
        "scenario_index": scenario_index,
        "start": start,
        "stop": stop,
        "stage": stage,
        "payload_path": payload.relative_to(root).as_posix(),
        "payload_bytes": payload.stat().st_size,
        "payload_sha256": sha256_file(payload),
    }
    if value != expected:
        raise RuntimeError("Chunk payload or seal drift")
    rows = _read_jsonl(payload)
    _validate_chunk(
        rows,
        scenario_id=scenario_id,
        scenario_index=scenario_index,
        start=start,
        stop=stop,
        stage=stage,
        final_stream=final_stream,
    )
    return rows, value


def _manifest_row(
    root: Path,
    payload: Path,
    seal: Path,
    seal_value: dict,
) -> dict:
    return {
        "scenario_id": seal_value["scenario_id"],
        "scenario_index": seal_value["scenario_index"],
        "start": seal_value["start"],
        "stop": seal_value["stop"],
        "payload_path": payload.relative_to(root).as_posix(),
        "payload_bytes": payload.stat().st_size,
        "payload_sha256": sha256_file(payload),
        "seal_path": seal.relative_to(root).as_posix(),
        "seal_bytes": seal.stat().st_size,
        "seal_sha256": sha256_file(seal),
    }


def _accounting_rows(
    all_rows: dict[str, list[dict]],
    scenario_indices: dict[str, int],
    stage: int,
    final_stream: bool,
) -> list[dict]:
    result = []
    for scenario_id, rows in all_rows.items():
        counts = Counter(row["status"] for row in rows)
        result.append(
            {
                "scenario_id": scenario_id,
                "scenario_index": scenario_indices[scenario_id],
                "attempts": len(rows),
                "supported": counts["SUPPORTED"],
                "support_stop": counts["SUPPORT_STOP"],
                "numerical_failures": counts["NUMERICAL_FAILURE"],
                "stage": stage,
                "final_stream": final_stream,
                "real_effects_fitted": False,
            }
        )
    return result


def verify_outer_payload(root: Path) -> dict:
    root = Path(root)
    partials = sorted(root.rglob("*.partial"))
    if partials:
        raise RuntimeError(f"Unclean outer partial files: {partials[:3]}")
    contract_path = root / "00_RUN_CONTRACT.json"
    manifest_path = root / "01_CHUNK_MANIFEST.csv"
    accounting_path = root / "02_ATTEMPT_ACCOUNTING.csv"
    receipt_path = root / "03_RUN_RECEIPT.json"
    contract = read_json(contract_path)
    receipt = read_json(receipt_path)
    if contract.get("schema") != "RP_V4_STAGE_F2_OUTER_RUN_1.0":
        raise ValueError("Wrong outer contract schema")
    if receipt.get("schema") != "RP_V4_STAGE_F2_OUTER_RECEIPT_1.0":
        raise ValueError("Wrong outer receipt schema")
    if receipt.get("contract_sha256") != sha256_file(contract_path):
        raise RuntimeError("Outer contract differs from receipt")
    if receipt.get("chunk_manifest_sha256") != sha256_file(manifest_path):
        raise RuntimeError("Outer chunk manifest differs from receipt")
    if receipt.get("accounting_sha256") != sha256_file(accounting_path):
        raise RuntimeError("Outer accounting differs from receipt")

    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    if not manifest_rows or tuple(manifest_rows[0]) != CHUNK_MANIFEST_FIELDS:
        raise ValueError("Invalid outer chunk manifest schema")
    expected_chunks = int(receipt["chunk_count"])
    if len(manifest_rows) != expected_chunks:
        raise ValueError("Outer chunk count differs from receipt")

    contract_sha = sha256_file(contract_path)
    stage = int(contract["stage"])
    final_stream = bool(contract["final_stream"])
    attempts_per_scenario = int(contract["attempts_per_scenario"])
    chunk_size = int(contract["chunk_size"])
    scenario_ids_value = list(contract["scenario_ids"])
    scenario_indices = {
        key: int(value) for key, value in contract["scenario_indices"].items()
    }
    expected_paths = set()
    expected_seal_paths = set()
    all_rows: dict[str, list[dict]] = {scenario_id: [] for scenario_id in scenario_ids_value}
    row_lookup = {row["payload_path"]: row for row in manifest_rows}
    for scenario_id in scenario_ids_value:
        scenario_index = scenario_indices[scenario_id]
        for start in range(1, attempts_per_scenario + 1, chunk_size):
            stop = min(start + chunk_size - 1, attempts_per_scenario)
            payload, seal = _chunk_paths(root, scenario_id, start, stop)
            relative = payload.relative_to(root).as_posix()
            expected_paths.add(relative)
            expected_seal_paths.add(seal.relative_to(root).as_posix())
            manifest_row = row_lookup.get(relative)
            if manifest_row is None:
                raise ValueError("Expected outer chunk is absent from manifest")
            rows, seal_value = _verify_chunk_pair(
                root=root,
                payload=payload,
                seal=seal,
                contract_sha=contract_sha,
                scenario_id=scenario_id,
                scenario_index=scenario_index,
                start=start,
                stop=stop,
                stage=stage,
                final_stream=final_stream,
            )
            expected_row = {
                key: str(value)
                for key, value in _manifest_row(root, payload, seal, seal_value).items()
            }
            if manifest_row != expected_row:
                raise RuntimeError("Outer chunk manifest row drift")
            all_rows[scenario_id].extend(rows)
    if set(row_lookup) != expected_paths:
        raise ValueError("Unexpected outer chunks are present in manifest")
    actual_jsonl = {
        path.relative_to(root).as_posix() for path in (root / "attempts").rglob("*.jsonl")
    }
    if actual_jsonl != expected_paths:
        raise ValueError("Outer attempt directory contains unregistered chunks")
    actual_seals = {
        path.relative_to(root).as_posix()
        for path in (root / "attempts").rglob("*.seal.json")
    }
    if actual_seals != expected_seal_paths:
        raise ValueError("Outer attempt directory contains unregistered seals")

    accounting = _accounting_rows(all_rows, scenario_indices, stage, final_stream)
    expected_accounting = _csv_text(accounting, list(accounting[0]))
    if accounting_path.read_text(encoding="utf-8") != expected_accounting:
        raise RuntimeError("Outer accounting does not reconcile with chunks")
    if receipt.get("scenario_count") != len(scenario_ids_value):
        raise ValueError("Outer scenario count drift")
    if receipt.get("attempts") != len(scenario_ids_value) * attempts_per_scenario:
        raise ValueError("Outer attempt count drift")
    return receipt


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
    runtime_qualification_path: Path | None = None,
) -> dict:
    if mode == "qualification":
        if not 1 <= qualification_attempts <= 8:
            raise ValueError("Qualification attempts must be between 1 and 8")
        authorization = qualification_authorization("outer")
        attempts_per_scenario = qualification_attempts
        chunk_size = qualification_attempts
        run_scenarios = selected_scenarios
    elif mode == "final":
        if any(
            value is None
            for value in (
                authorization_path,
                binding_manifest_path,
                runtime_qualification_path,
            )
        ):
            raise PermissionError("Final execution requires GO, binding and runtime inputs")
        authorization = authorize_final(
            purpose="outer",
            authorization_path=authorization_path,
            binding_manifest_path=binding_manifest_path,
            runtime_qualification_path=runtime_qualification_path,
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
    if sorted(output.rglob("*.partial")):
        raise RuntimeError("Unclean partial file in outer output")
    if resume and (output / "03_RUN_RECEIPT.json").exists():
        receipt = verify_outer_payload(output)
        return {**receipt, "invocation_created_chunks": 0, "invocation_reused_chunks": receipt["chunk_count"]}

    registry, model = load_inputs(registry_path, calibration_model_path)
    by_id = {row["scenario_id"]: (index, row) for index, row in enumerate(registry)}
    if len(run_scenarios) != len(set(run_scenarios)) or any(
        scenario_id not in by_id for scenario_id in run_scenarios
    ):
        raise ValueError("Unknown or duplicate requested scenario")
    scenario_indices = {scenario_id: by_id[scenario_id][0] for scenario_id in run_scenarios}

    contract = {
        "schema": "RP_V4_STAGE_F2_OUTER_RUN_1.0",
        "mode": mode,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "scenario_ids": list(run_scenarios),
        "scenario_indices": scenario_indices,
        "attempts_per_scenario": attempts_per_scenario,
        "chunk_size": chunk_size,
        "data_kind": "SIMULATED_ONLY",
        "real_effects_fitted": False,
        "final_stream": authorization.final,
        "authorization_sha256": authorization.authorization_sha256,
        "binding_manifest_sha256": authorization.binding_manifest_sha256,
        "runtime_receipt_sha256": authorization.runtime_receipt_sha256,
    }
    contract_path = output / "00_RUN_CONTRACT.json"
    contract_text = stable_json(contract)
    if contract_path.exists():
        if contract_path.read_text(encoding="utf-8") != contract_text:
            raise RuntimeError("Resume contract drift")
    else:
        atomic_write_text(contract_path, contract_text)
    contract_sha = sha256_file(contract_path)

    created_chunks = 0
    reused_chunks = 0
    all_rows: dict[str, list[dict]] = {scenario_id: [] for scenario_id in run_scenarios}
    manifest_rows = []
    expected_payloads = set()
    expected_seals = set()
    for scenario_id in run_scenarios:
        scenario_index, scenario = by_id[scenario_id]
        for start in range(1, attempts_per_scenario + 1, chunk_size):
            stop = min(start + chunk_size - 1, attempts_per_scenario)
            payload, seal = _chunk_paths(output, scenario_id, start, stop)
            expected_payloads.add(payload.relative_to(output).as_posix())
            expected_seals.add(seal.relative_to(output).as_posix())
            if payload.exists() or seal.exists():
                rows, seal_value = _verify_chunk_pair(
                    root=output,
                    payload=payload,
                    seal=seal,
                    contract_sha=contract_sha,
                    scenario_id=scenario_id,
                    scenario_index=scenario_index,
                    start=start,
                    stop=stop,
                    stage=authorization.stage,
                    final_stream=authorization.final,
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
                payload.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_text(payload, _jsonl(rows))
                seal_value = _seal_payload(
                    root=output,
                    payload=payload,
                    seal=seal,
                    contract_sha=contract_sha,
                    scenario_id=scenario_id,
                    scenario_index=scenario_index,
                    start=start,
                    stop=stop,
                    stage=authorization.stage,
                )
                created_chunks += 1
            all_rows[scenario_id].extend(rows)
            manifest_rows.append(_manifest_row(output, payload, seal, seal_value))

    actual_payloads = {
        path.relative_to(output).as_posix()
        for path in (output / "attempts").rglob("*.jsonl")
    }
    if actual_payloads != expected_payloads:
        raise ValueError("Outer output contains unexpected or missing chunks")
    actual_seals = {
        path.relative_to(output).as_posix()
        for path in (output / "attempts").rglob("*.seal.json")
    }
    if actual_seals != expected_seals:
        raise ValueError("Outer output contains unexpected or missing seals")

    manifest_path = output / "01_CHUNK_MANIFEST.csv"
    manifest_text = _csv_text(manifest_rows, CHUNK_MANIFEST_FIELDS)
    if manifest_path.exists():
        if manifest_path.read_text(encoding="utf-8") != manifest_text:
            raise RuntimeError("Resume chunk manifest drift")
    else:
        atomic_write_text(manifest_path, manifest_text)

    accounting = _accounting_rows(
        all_rows, scenario_indices, authorization.stage, authorization.final
    )
    accounting_path = output / "02_ATTEMPT_ACCOUNTING.csv"
    accounting_text = _csv_text(accounting, list(accounting[0]))
    if accounting_path.exists():
        if accounting_path.read_text(encoding="utf-8") != accounting_text:
            raise RuntimeError("Resume accounting drift")
    else:
        atomic_write_text(accounting_path, accounting_text)

    receipt = {
        "schema": "RP_V4_STAGE_F2_OUTER_RECEIPT_1.0",
        "mode": mode,
        "stage": authorization.stage,
        "scenario_count": len(run_scenarios),
        "attempts": len(run_scenarios) * attempts_per_scenario,
        "chunk_count": len(manifest_rows),
        "contract_sha256": sha256_file(contract_path),
        "chunk_manifest_sha256": sha256_file(manifest_path),
        "accounting_sha256": sha256_file(accounting_path),
        "authorization_sha256": authorization.authorization_sha256,
        "binding_manifest_sha256": authorization.binding_manifest_sha256,
        "runtime_receipt_sha256": authorization.runtime_receipt_sha256,
        "final_G2C_adjudicated": False,
        "real_effects_fitted": False,
        "final": authorization.final,
    }
    atomic_write_text(output / "03_RUN_RECEIPT.json", stable_json(receipt))
    verify_outer_payload(output)
    return {
        **receipt,
        "invocation_created_chunks": created_chunks,
        "invocation_reused_chunks": reused_chunks,
    }


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
    parser.add_argument("--runtime-qualification", type=Path)
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
                runtime_qualification_path=arguments.runtime_qualification,
            )
        ),
        end="",
    )
