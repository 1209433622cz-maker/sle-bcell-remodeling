"""Independent, authorization-gated truth engine for shifted RP v4 DGPs."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

import numpy as np

try:
    from . import rp_v4_g2c_truth as frozen
    from .rp_v4_stageE2_common import (
        ExecutionAuthorization,
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        sha256_file,
        stable_json,
    )
    from .rp_v4_stageE2_generator import load_inputs
except ImportError:
    import rp_v4_g2c_truth as frozen
    from rp_v4_stageE2_common import (
        ExecutionAuthorization,
        SEED_BASE,
        atomic_write_text,
        authorize_final,
        qualification_authorization,
        sha256_file,
        stable_json,
    )
    from rp_v4_stageE2_generator import load_inputs


def _rng(
    scenario_index: int, batch: int, authorization: ExecutionAuthorization
) -> np.random.Generator:
    if authorization.purpose != "truth":
        raise PermissionError("Truth engine requires truth authorization")
    sequence = np.random.SeedSequence(
        [SEED_BASE, authorization.stage, scenario_index, batch, 95]
    )
    return np.random.Generator(np.random.Philox(sequence))


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
    return {
        "attempts": attempts,
        "n0": int(valid0.sum()),
        "n1": int(valid1.sum()),
        "sum0": float(score0.sum()),
        "sum1": float(score1.sum()),
        "sq0": float(score0 @ score0),
        "sq1": float(score1 @ score1),
    }


def truth_one(
    model: dict,
    scenario: dict,
    scenario_index: int,
    authorization: ExecutionAuthorization,
    *,
    effort_per_arm: int = 131072,
    batches: int = 16,
) -> dict:
    if authorization.purpose != "truth":
        raise PermissionError("Wrong authorization purpose")
    if scenario["family"] != "PRESPECIFIED_SHIFT":
        raise ValueError("Stage E2 truth engine handles shifted DGPs only")
    if effort_per_arm != 131072 or batches != 16:
        raise ValueError("Final shifted truth budget is frozen at 131072 x 16")
    attempts = effort_per_arm // batches
    batch_rows = [
        _coupled_batch(
            model,
            scenario,
            scenario_index,
            batch,
            attempts,
            authorization,
        )
        for batch in range(batches)
    ]
    n0 = sum(row["n0"] for row in batch_rows)
    n1 = sum(row["n1"] for row in batch_rows)
    if min(n0, n1) <= 100:
        raise RuntimeError("Final truth support is insufficient")
    mean0 = sum(row["sum0"] for row in batch_rows) / n0
    mean1 = sum(row["sum1"] for row in batch_rows) / n1
    variance0 = max(
        sum(row["sq0"] for row in batch_rows) / n0 - mean0**2, 0.0
    )
    variance1 = max(
        sum(row["sq1"] for row in batch_rows) / n1 - mean1**2, 0.0
    )
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
    precision_pass = truth_mcse <= 0.01 * typical_se
    if not precision_pass:
        raise RuntimeError("Final truth precision gate failed; no replenishment")
    return {
        "scenario_id": scenario["scenario_id"],
        "truth": truth,
        "truth_mcse": truth_mcse,
        "typical_coefficient_se": float(typical_se),
        "mcse_over_typical_se": float(truth_mcse / typical_se),
        "precision_pass": True,
        "exact_null_registered": exact,
        "truth_basis": "EXACT_SHIFTED_ARM_SYMMETRY" if exact else "PAIRED_INDEPENDENT_ORACLE",
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
    }


def run(
    *,
    registry_path: Path,
    calibration_model_path: Path,
    output: Path,
    mode: str,
    selected_scenarios: tuple[str, ...] = ("C0_X1", "C1_X2", "C2_X3"),
    authorization_path: Path | None = None,
    binding_manifest_path: Path | None = None,
) -> dict:
    if mode == "qualification":
        authorization = qualification_authorization("truth")
        run_scenarios = selected_scenarios
    elif mode == "final":
        if authorization_path is None or binding_manifest_path is None:
            raise PermissionError("Final truth requires exact-code GO inputs")
        authorization = authorize_final(
            purpose="truth",
            authorization_path=authorization_path,
            binding_manifest_path=binding_manifest_path,
        )
        run_scenarios = tuple(f"C{structure}_X{stress}" for structure in range(5) for stress in range(1, 4))
    else:
        raise ValueError("Mode must be qualification or final")

    output = Path(output)
    if output.exists():
        raise FileExistsError("Truth output exists; final truth is write-once")
    output.mkdir(parents=True)
    registry, model = load_inputs(registry_path, calibration_model_path)
    by_id = {row["scenario_id"]: (index, row) for index, row in enumerate(registry)}
    if len(run_scenarios) != len(set(run_scenarios)) or any(
        scenario_id not in by_id for scenario_id in run_scenarios
    ):
        raise ValueError("Unknown or duplicate truth scenario")
    if any(by_id[scenario_id][1]["family"] != "PRESPECIFIED_SHIFT" for scenario_id in run_scenarios):
        raise ValueError("Only shifted scenarios may enter the Stage E2 truth runner")

    rows = []
    for scenario_id in run_scenarios:
        scenario_index, scenario = by_id[scenario_id]
        rows.append(
            truth_one(
                model,
                scenario,
                scenario_index,
                authorization,
            )
        )
    fieldnames = list(rows[0])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    truth_path = output / "01_SHIFTED_TRUTH.csv"
    atomic_write_text(truth_path, stream.getvalue())
    receipt = {
        "schema": "RP_V4_STAGE_E2_TRUTH_RECEIPT_1.0",
        "mode": mode,
        "stage": authorization.stage,
        "seed_base": SEED_BASE,
        "scenario_count": len(rows),
        "all_precision_pass": all(row["precision_pass"] for row in rows),
        "maximum_mcse_over_typical_se": max(
            row["mcse_over_typical_se"] for row in rows
        ),
        "truth_csv_sha256": sha256_file(truth_path),
        "authorization_sha256": authorization.authorization_sha256,
        "binding_manifest_sha256": authorization.binding_manifest_sha256,
        "real_effects_fitted": False,
        "final": authorization.final,
    }
    atomic_write_text(output / "02_TRUTH_RECEIPT.json", stable_json(receipt))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--calibration-model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("qualification", "final"), required=True)
    parser.add_argument("--scenarios", nargs="*", default=["C0_X1", "C1_X2", "C2_X3"])
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--binding-manifest", type=Path)
    arguments = parser.parse_args()
    print(
        json.dumps(
            run(
                registry_path=arguments.registry,
                calibration_model_path=arguments.calibration_model,
                output=arguments.output,
                mode=arguments.mode,
                selected_scenarios=tuple(arguments.scenarios),
                authorization_path=arguments.authorization,
                binding_manifest_path=arguments.binding_manifest,
            ),
            indent=2,
            sort_keys=True,
        )
    )
