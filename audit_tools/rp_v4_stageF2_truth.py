"""Resumable, hash-sealed and independently cross-checked Stage F2 truth engine."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from pathlib import Path

import numpy as np

try:
    from . import rp_v4_g2c_truth as frozen
    from .rp_v4_stageF2_common import (
        ExecutionAuthorization,
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        read_json,
        sha256_file,
        stable_json,
    )
    from .rp_v4_stageF2_generator import load_inputs
except ImportError:
    import rp_v4_g2c_truth as frozen
    from rp_v4_stageF2_common import (
        ExecutionAuthorization,
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        read_json,
        sha256_file,
        stable_json,
    )
    from rp_v4_stageF2_generator import load_inputs


TRUTH_FIELDS = (
    "scenario_id",
    "truth",
    "truth_mcse",
    "typical_coefficient_se",
    "mcse_over_typical_se",
    "precision_pass",
    "exact_null_registered",
    "truth_basis",
    "observed_pair_difference",
    "paired_mcse_before_exact_symmetry",
    "accepted_arm0",
    "accepted_arm1",
    "attempted_per_arm",
    "batches",
    "stage",
    "seed_base",
    "data_kind",
    "real_effects_fitted",
    "final",
    "independent_score_crosscheck",
)


def _rng(
    scenario_index: int, batch: int, authorization: ExecutionAuthorization
) -> np.random.Generator:
    if authorization.purpose != "truth":
        raise PermissionError("Truth engine requires truth authorization")
    sequence = np.random.SeedSequence(
        [SEED_BASE, authorization.stage, scenario_index, batch, 95]
    )
    return np.random.Generator(np.random.Philox(sequence))


def _score_delta_reference(
    categories: np.ndarray, observed_n: np.ndarray, model: dict
) -> tuple[np.ndarray, np.ndarray]:
    """Independent expression of the truth score used for runtime cross-checking."""
    libraries = np.sum(categories, axis=2)
    valid = (np.min(observed_n, axis=1) >= 30) & (np.min(libraries, axis=1) > 0)
    if not np.any(valid):
        return valid, np.zeros(0, dtype=float)
    selected = categories[valid, :, 0:12].astype(np.float64)
    totals = libraries[valid, :].astype(np.float64)
    profile = np.asarray(model["pi"], dtype=np.float64)
    fixed_cpm = np.einsum(
        "nbg,nb,b->ng", selected, 1_000_000.0 / totals, profile
    )
    pooled_cpm = (
        np.sum(selected, axis=1)
        * (1_000_000.0 / np.sum(totals, axis=1))[:, None]
    )
    center = np.asarray(model["mu"], dtype=np.float64)
    scale = np.asarray(model["sd"], dtype=np.float64)
    fixed_score = np.mean((np.log2(fixed_cpm + 0.5) - center) / scale, axis=1)
    pooled_score = np.mean((np.log2(pooled_cpm + 0.5) - center) / scale, axis=1)
    return valid, fixed_score - pooled_score


def _coupled_batch(
    model: dict,
    scenario: dict,
    scenario_index: int,
    batch: int,
    attempts: int,
    authorization: ExecutionAuthorization,
) -> dict:
    rng = _rng(scenario_index, batch, authorization)
    composition, within_bin, rare, depth, mislabel, capture_tilt, mode = (
        frozen._case_setup(scenario)
    )
    template_ids = np.resize(np.arange(68), attempts)
    rng.shuffle(template_ids)
    template_n = model["template_n"][template_ids]
    template_rate = model["template_rate"][template_ids]
    template_probs = model["template_probs"][template_ids]
    axis = np.asarray([-1.0, -0.5, 0.0, 0.5, 1.0])

    weight0 = template_n - 29.0
    weight0 /= weight0.sum(axis=1, keepdims=True)
    weight1 = (template_n - 29.0) * np.exp(composition * axis)[None, :]
    weight1 /= weight1.sum(axis=1, keepdims=True)
    free = template_n.sum(axis=1) - 150
    n0 = 30 + rng.multinomial(free, weight0)
    n1 = n0.copy() if composition == 0 else 30 + rng.multinomial(free, weight1)
    if rare != 1.0:
        retained0 = rng.binomial(n0[:, 0], rare)
        retained1 = (
            retained0.copy() if composition == 0 else rng.binomial(n1[:, 0], rare)
        )
        n0[:, 4] += n0[:, 0] - retained0
        n0[:, 0] = retained0
        n1[:, 4] += n1[:, 0] - retained1
        n1[:, 0] = retained1

    rate0 = template_rate[:, :, None] * template_probs
    rate1 = (
        template_rate * depth * np.exp(capture_tilt * axis)[None, :]
    )[:, :, None] * template_probs
    rate1[:, :, :12] *= 2.0**within_bin
    if mode == "GAMMA_POISSON_OVERDISPERSION":
        factor = rng.gamma(10.0, 0.1, size=rate0.shape)
        rate0 *= factor
        rate1 *= factor
    if mode == "CORRELATED_CAPTURE_HETEROGENEITY":
        donor = rng.normal(0.0, 0.35, size=(attempts, 1))
        bins = np.empty((attempts, 5), dtype=float)
        bins[:, 0] = rng.normal(0.0, 0.2, size=attempts)
        for index in range(1, 5):
            bins[:, index] = 0.6 * bins[:, index - 1] + np.sqrt(
                1 - 0.6**2
            ) * rng.normal(0.0, 0.2, size=attempts)
        factor = np.exp(donor + bins - 0.5 * (0.35**2 + 0.2**2))
        rate0 *= factor[:, :, None]
        rate1 *= factor[:, :, None]

    matrix = frozen.transition(mode, mislabel)

    def draw_flow(counts: np.ndarray) -> np.ndarray:
        flows = np.zeros((attempts, 5, 5), dtype=np.int64)
        for origin in range(5):
            if matrix[origin, origin] == 1:
                flows[:, origin, origin] = counts[:, origin]
            else:
                flows[:, origin, :] = rng.multinomial(
                    counts[:, origin], matrix[origin]
                )
        return flows

    flow0 = draw_flow(n0)
    flow1 = flow0.copy() if composition == 0 else draw_flow(n1)
    observed0 = flow0.sum(axis=1)
    observed1 = flow1.sum(axis=1)
    lambda0 = np.einsum("nkd,nkg->ndg", flow0, rate0)
    lambda1 = np.einsum("nkd,nkg->ndg", flow1, rate1)
    shared = rng.poisson(np.minimum(lambda0, lambda1))
    categories0 = shared + rng.poisson(np.maximum(lambda0 - lambda1, 0.0))
    categories1 = shared + rng.poisson(np.maximum(lambda1 - lambda0, 0.0))

    valid0, score0 = frozen._score_delta(categories0, observed0, model)
    valid1, score1 = frozen._score_delta(categories1, observed1, model)
    reference_valid0, reference_score0 = _score_delta_reference(
        categories0, observed0, model
    )
    reference_valid1, reference_score1 = _score_delta_reference(
        categories1, observed1, model
    )
    if not (
        np.array_equal(valid0, reference_valid0)
        and np.array_equal(valid1, reference_valid1)
        and np.allclose(score0, reference_score0, rtol=1e-12, atol=1e-12)
        and np.allclose(score1, reference_score1, rtol=1e-12, atol=1e-12)
    ):
        raise RuntimeError("Independent truth score cross-check failed")
    return {
        "schema": "RP_V4_STAGE_F2_TRUTH_BATCH_1.0",
        "scenario_id": scenario["scenario_id"],
        "scenario_index": scenario_index,
        "batch": batch,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "attempts": attempts,
        "n0": int(valid0.sum()),
        "n1": int(valid1.sum()),
        "sum0": float(score0.sum()),
        "sum1": float(score1.sum()),
        "sq0": float(score0 @ score0),
        "sq1": float(score1 @ score1),
        "data_kind": "SIMULATED_ONLY",
        "real_effects_fitted": False,
        "independent_score_crosscheck": True,
        "final": authorization.final,
    }


def _batch_paths(root: Path, scenario_id: str, batch: int) -> tuple[Path, Path]:
    payload = root / "checkpoints" / scenario_id / f"batch_{batch:02d}.json"
    return payload, payload.with_name(payload.name + ".seal.json")


def _batch_seal(
    root: Path, payload: Path, seal: Path, contract_sha: str
) -> dict:
    row = read_json(payload)
    value = {
        "schema": "RP_V4_STAGE_F2_TRUTH_BATCH_SEAL_1.0",
        "contract_sha256": contract_sha,
        "scenario_id": row["scenario_id"],
        "scenario_index": row["scenario_index"],
        "batch": row["batch"],
        "stage": row["stage"],
        "payload_path": payload.relative_to(root).as_posix(),
        "payload_bytes": payload.stat().st_size,
        "payload_sha256": sha256_file(payload),
    }
    atomic_write_text(seal, stable_json(value))
    return value


def _verify_batch_pair(
    *,
    root: Path,
    payload: Path,
    seal: Path,
    contract_sha: str,
    expected: dict | None = None,
) -> tuple[dict, dict]:
    if payload.exists() != seal.exists():
        raise RuntimeError("Truth checkpoint/seal pair is incomplete")
    if not payload.exists():
        raise FileNotFoundError(payload)
    row = read_json(payload)
    seal_value = read_json(seal)
    value = {
        "schema": "RP_V4_STAGE_F2_TRUTH_BATCH_SEAL_1.0",
        "contract_sha256": contract_sha,
        "scenario_id": row.get("scenario_id"),
        "scenario_index": row.get("scenario_index"),
        "batch": row.get("batch"),
        "stage": row.get("stage"),
        "payload_path": payload.relative_to(root).as_posix(),
        "payload_bytes": payload.stat().st_size,
        "payload_sha256": sha256_file(payload),
    }
    if seal_value != value:
        raise RuntimeError("Truth checkpoint or seal drift")
    if expected is not None and row != expected:
        raise RuntimeError("Truth checkpoint does not reproduce its fixed random stream")
    return row, seal_value


def _aggregate_truth(
    model: dict,
    scenario: dict,
    authorization: ExecutionAuthorization,
    batch_rows: list[dict],
    effort_per_arm: int,
    batches: int,
) -> dict:
    n0 = sum(row["n0"] for row in batch_rows)
    n1 = sum(row["n1"] for row in batch_rows)
    if min(n0, n1) <= 100:
        raise RuntimeError("Final truth support is insufficient")
    mean0 = sum(row["sum0"] for row in batch_rows) / n0
    mean1 = sum(row["sum1"] for row in batch_rows) / n1
    variance0 = max(sum(row["sq0"] for row in batch_rows) / n0 - mean0**2, 0.0)
    variance1 = max(sum(row["sq1"] for row in batch_rows) / n1 - mean1**2, 0.0)
    design = np.asarray(model["synthetic_design"], dtype=float)
    coefficient_weights = (np.linalg.inv(design.T @ design) @ design.T)[1]
    typical_se = np.sqrt(
        variance0 * np.sum(coefficient_weights[design[:, 1] == 0] ** 2)
        + variance1 * np.sum(coefficient_weights[design[:, 1] == 1] ** 2)
    )
    per_batch0 = n0 / batches
    per_batch1 = n1 / batches
    influence = np.asarray(
        [
            (row["sum1"] - row["n1"] * mean1) / per_batch1
            - (row["sum0"] - row["n0"] * mean0) / per_batch0
            for row in batch_rows
        ]
    )
    mcse = float(np.std(influence, ddof=1) / np.sqrt(batches))
    exact = scenario["scenario_id"].startswith("C0_")
    truth = 0.0 if exact else float(mean1 - mean0)
    truth_mcse = 0.0 if exact else mcse
    if not math.isfinite(float(typical_se)) or typical_se <= 0:
        raise RuntimeError("Truth scale is invalid")
    if truth_mcse > 0.01 * typical_se:
        raise RuntimeError("Final truth precision gate failed; no replenishment")
    return {
        "scenario_id": scenario["scenario_id"],
        "truth": truth,
        "truth_mcse": truth_mcse,
        "typical_coefficient_se": float(typical_se),
        "mcse_over_typical_se": float(truth_mcse / typical_se),
        "precision_pass": True,
        "exact_null_registered": exact,
        "truth_basis": (
            "EXACT_SHIFTED_ARM_SYMMETRY" if exact else "PAIRED_INDEPENDENT_ORACLE"
        ),
        "observed_pair_difference": float(mean1 - mean0),
        "paired_mcse_before_exact_symmetry": mcse,
        "accepted_arm0": n0,
        "accepted_arm1": n1,
        "attempted_per_arm": effort_per_arm,
        "batches": batches,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "data_kind": "SIMULATED_ONLY",
        "real_effects_fitted": False,
        "final": authorization.final,
        "independent_score_crosscheck": True,
    }


def _scenario_result(
    root: Path,
    scenario_id: str,
    truth: dict,
    pairs: list[tuple[Path, Path]],
) -> dict:
    inventory = [
        {
            "payload_path": payload.relative_to(root).as_posix(),
            "payload_bytes": payload.stat().st_size,
            "payload_sha256": sha256_file(payload),
            "seal_path": seal.relative_to(root).as_posix(),
            "seal_bytes": seal.stat().st_size,
            "seal_sha256": sha256_file(seal),
        }
        for payload, seal in pairs
    ]
    return {
        "schema": "RP_V4_STAGE_F2_TRUTH_SCENARIO_RESULT_1.0",
        "scenario_id": scenario_id,
        "batch_inventory": inventory,
        "truth": truth,
    }


def _csv_text(rows: list[dict], fieldnames: tuple[str, ...] | list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def verify_truth_payload(
    root: Path,
    *,
    registry_path: Path,
    calibration_model_path: Path,
) -> dict:
    root = Path(root)
    partials = sorted(root.rglob("*.partial"))
    if partials:
        raise RuntimeError(f"Unclean truth partial files: {partials[:3]}")
    contract_path = root / "00_TRUTH_CONTRACT.json"
    manifest_path = root / "01_TRUTH_SCENARIO_MANIFEST.csv"
    truth_path = root / "02_SHIFTED_TRUTH.csv"
    receipt_path = root / "03_TRUTH_RECEIPT.json"
    contract = read_json(contract_path)
    receipt = read_json(receipt_path)
    if contract.get("schema") != "RP_V4_STAGE_F2_TRUTH_RUN_1.0":
        raise ValueError("Wrong truth contract schema")
    if receipt.get("schema") != "RP_V4_STAGE_F2_TRUTH_RECEIPT_1.0":
        raise ValueError("Wrong truth receipt schema")
    if receipt.get("contract_sha256") != sha256_file(contract_path):
        raise RuntimeError("Truth contract differs from receipt")
    if receipt.get("scenario_manifest_sha256") != sha256_file(manifest_path):
        raise RuntimeError("Truth scenario manifest differs from receipt")
    if receipt.get("truth_csv_sha256") != sha256_file(truth_path):
        raise RuntimeError("Truth CSV differs from receipt")

    registry, model = load_inputs(registry_path, calibration_model_path)
    by_id = {row["scenario_id"]: (index, row) for index, row in enumerate(registry)}
    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    scenario_ids_value = list(contract["scenario_ids"])
    if len(manifest_rows) != len(scenario_ids_value):
        raise ValueError("Truth scenario manifest count drift")
    manifest_by_id = {row["scenario_id"]: row for row in manifest_rows}
    if set(manifest_by_id) != set(scenario_ids_value):
        raise ValueError("Truth scenario manifest identity drift")

    authorization = ExecutionAuthorization(
        stage=int(contract["stage"]),
        purpose="truth",
        final=bool(contract["final"]),
    )
    effort = int(contract["effort_per_arm"])
    batches = int(contract["batches"])
    truth_rows = []
    expected_checkpoint_paths = set()
    expected_checkpoint_seals = set()
    for scenario_id in scenario_ids_value:
        scenario_index, scenario = by_id[scenario_id]
        result_path = root / "scenarios" / f"{scenario_id}.json"
        manifest_row = manifest_by_id[scenario_id]
        if (
            manifest_row["result_path"] != result_path.relative_to(root).as_posix()
            or int(manifest_row["result_bytes"]) != result_path.stat().st_size
            or manifest_row["result_sha256"] != sha256_file(result_path)
        ):
            raise RuntimeError("Truth scenario result differs from manifest")
        result = read_json(result_path)
        if result.get("scenario_id") != scenario_id:
            raise ValueError("Truth scenario result identity drift")
        batch_rows = []
        expected_inventory = []
        for batch in range(batches):
            payload, seal = _batch_paths(root, scenario_id, batch)
            expected_checkpoint_paths.add(payload.relative_to(root).as_posix())
            expected_checkpoint_seals.add(seal.relative_to(root).as_posix())
            row, _ = _verify_batch_pair(
                root=root,
                payload=payload,
                seal=seal,
                contract_sha=sha256_file(contract_path),
            )
            batch_rows.append(row)
            expected_inventory.append(
                {
                    "payload_path": payload.relative_to(root).as_posix(),
                    "payload_bytes": payload.stat().st_size,
                    "payload_sha256": sha256_file(payload),
                    "seal_path": seal.relative_to(root).as_posix(),
                    "seal_bytes": seal.stat().st_size,
                    "seal_sha256": sha256_file(seal),
                }
            )
        if result.get("batch_inventory") != expected_inventory:
            raise RuntimeError("Truth checkpoint inventory drift")
        expected_truth = _aggregate_truth(
            model, scenario, authorization, batch_rows, effort, batches
        )
        if result.get("truth") != expected_truth:
            raise RuntimeError("Truth scenario aggregation drift")
        truth_rows.append(expected_truth)

    actual_checkpoint_paths = {
        path.relative_to(root).as_posix()
        for path in (root / "checkpoints").rglob("batch_*.json")
        if not path.name.endswith(".seal.json")
    }
    if actual_checkpoint_paths != expected_checkpoint_paths:
        raise ValueError("Truth checkpoint inventory contains extra or missing payloads")
    actual_checkpoint_seals = {
        path.relative_to(root).as_posix()
        for path in (root / "checkpoints").rglob("*.seal.json")
    }
    if actual_checkpoint_seals != expected_checkpoint_seals:
        raise ValueError("Truth checkpoint inventory contains extra or missing seals")
    if truth_path.read_text(encoding="utf-8") != _csv_text(truth_rows, TRUTH_FIELDS):
        raise RuntimeError("Truth CSV does not reconcile with scenario checkpoints")
    return receipt


def run(
    *,
    registry_path: Path,
    calibration_model_path: Path,
    output: Path,
    mode: str,
    resume: bool = False,
    selected_scenarios: tuple[str, ...] = ("C0_X1", "C1_X2", "C2_X3"),
    authorization_path: Path | None = None,
    binding_manifest_path: Path | None = None,
    runtime_qualification_path: Path | None = None,
) -> dict:
    if mode == "qualification":
        authorization = qualification_authorization("truth")
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
            raise PermissionError("Final truth requires GO, binding and runtime inputs")
        authorization = authorize_final(
            purpose="truth",
            authorization_path=authorization_path,
            binding_manifest_path=binding_manifest_path,
            runtime_qualification_path=runtime_qualification_path,
        )
        run_scenarios = tuple(
            f"C{structure}_X{stress}"
            for structure in range(5)
            for stress in range(1, 4)
        )
    else:
        raise ValueError("Mode must be qualification or final")

    output = Path(output)
    if output.exists() and not resume:
        raise FileExistsError("Truth output exists; use explicit resume")
    output.mkdir(parents=True, exist_ok=True)
    if sorted(output.rglob("*.partial")):
        raise RuntimeError("Unclean partial file in truth output")
    if resume and (output / "03_TRUTH_RECEIPT.json").exists():
        return verify_truth_payload(
            output,
            registry_path=registry_path,
            calibration_model_path=calibration_model_path,
        )

    registry, model = load_inputs(registry_path, calibration_model_path)
    by_id = {row["scenario_id"]: (index, row) for index, row in enumerate(registry)}
    if len(run_scenarios) != len(set(run_scenarios)) or any(
        scenario_id not in by_id for scenario_id in run_scenarios
    ):
        raise ValueError("Unknown or duplicate truth scenario")
    if any(
        by_id[scenario_id][1]["family"] != "PRESPECIFIED_SHIFT"
        for scenario_id in run_scenarios
    ):
        raise ValueError("Only shifted scenarios may enter the Stage F2 truth runner")

    effort_per_arm = 131072
    batches = 16
    attempts_per_batch = effort_per_arm // batches
    contract = {
        "schema": "RP_V4_STAGE_F2_TRUTH_RUN_1.0",
        "mode": mode,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "scenario_ids": list(run_scenarios),
        "scenario_indices": {
            scenario_id: by_id[scenario_id][0] for scenario_id in run_scenarios
        },
        "effort_per_arm": effort_per_arm,
        "batches": batches,
        "attempts_per_batch": attempts_per_batch,
        "data_kind": "SIMULATED_ONLY",
        "real_effects_fitted": False,
        "final": authorization.final,
        "authorization_sha256": authorization.authorization_sha256,
        "binding_manifest_sha256": authorization.binding_manifest_sha256,
        "runtime_receipt_sha256": authorization.runtime_receipt_sha256,
    }
    contract_path = output / "00_TRUTH_CONTRACT.json"
    contract_text = stable_json(contract)
    if contract_path.exists():
        if contract_path.read_text(encoding="utf-8") != contract_text:
            raise RuntimeError("Truth resume contract drift")
    else:
        atomic_write_text(contract_path, contract_text)
    contract_sha = sha256_file(contract_path)

    truth_rows = []
    manifest_rows = []
    for scenario_id in run_scenarios:
        scenario_index, scenario = by_id[scenario_id]
        batch_rows = []
        pairs = []
        for batch in range(batches):
            payload, seal = _batch_paths(output, scenario_id, batch)
            expected = _coupled_batch(
                model,
                scenario,
                scenario_index,
                batch,
                attempts_per_batch,
                authorization,
            )
            if payload.exists() or seal.exists():
                row, _ = _verify_batch_pair(
                    root=output,
                    payload=payload,
                    seal=seal,
                    contract_sha=contract_sha,
                    expected=expected,
                )
            else:
                payload.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_text(payload, stable_json(expected))
                _batch_seal(output, payload, seal, contract_sha)
                row = expected
            batch_rows.append(row)
            pairs.append((payload, seal))
        truth = _aggregate_truth(
            model, scenario, authorization, batch_rows, effort_per_arm, batches
        )
        result = _scenario_result(output, scenario_id, truth, pairs)
        result_path = output / "scenarios" / f"{scenario_id}.json"
        result_text = stable_json(result)
        if result_path.exists():
            if result_path.read_text(encoding="utf-8") != result_text:
                raise RuntimeError("Truth scenario result drift")
        else:
            atomic_write_text(result_path, result_text)
        truth_rows.append(truth)
        manifest_rows.append(
            {
                "scenario_id": scenario_id,
                "scenario_index": scenario_index,
                "result_path": result_path.relative_to(output).as_posix(),
                "result_bytes": result_path.stat().st_size,
                "result_sha256": sha256_file(result_path),
                "checkpoint_count": batches,
            }
        )

    manifest_path = output / "01_TRUTH_SCENARIO_MANIFEST.csv"
    manifest_text = _csv_text(manifest_rows, list(manifest_rows[0]))
    if manifest_path.exists():
        if manifest_path.read_text(encoding="utf-8") != manifest_text:
            raise RuntimeError("Truth scenario manifest drift")
    else:
        atomic_write_text(manifest_path, manifest_text)
    truth_path = output / "02_SHIFTED_TRUTH.csv"
    truth_text = _csv_text(truth_rows, TRUTH_FIELDS)
    if truth_path.exists():
        if truth_path.read_text(encoding="utf-8") != truth_text:
            raise RuntimeError("Truth CSV drift")
    else:
        atomic_write_text(truth_path, truth_text)

    receipt = {
        "schema": "RP_V4_STAGE_F2_TRUTH_RECEIPT_1.0",
        "mode": mode,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "scenario_count": len(truth_rows),
        "checkpoint_count": len(truth_rows) * batches,
        "all_precision_pass": all(row["precision_pass"] for row in truth_rows),
        "all_independent_score_crosschecks_pass": all(
            row["independent_score_crosscheck"] for row in truth_rows
        ),
        "maximum_mcse_over_typical_se": max(
            row["mcse_over_typical_se"] for row in truth_rows
        ),
        "contract_sha256": sha256_file(contract_path),
        "scenario_manifest_sha256": sha256_file(manifest_path),
        "truth_csv_sha256": sha256_file(truth_path),
        "authorization_sha256": authorization.authorization_sha256,
        "binding_manifest_sha256": authorization.binding_manifest_sha256,
        "runtime_receipt_sha256": authorization.runtime_receipt_sha256,
        "real_effects_fitted": False,
        "final": authorization.final,
    }
    atomic_write_text(output / "03_TRUTH_RECEIPT.json", stable_json(receipt))
    verify_truth_payload(
        output,
        registry_path=registry_path,
        calibration_model_path=calibration_model_path,
    )
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--calibration-model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("qualification", "final"), required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--scenarios", nargs="*", default=["C0_X1", "C1_X2", "C2_X3"])
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
                authorization_path=arguments.authorization,
                binding_manifest_path=arguments.binding_manifest,
                runtime_qualification_path=arguments.runtime_qualification,
            )
        ),
        end="",
    )
