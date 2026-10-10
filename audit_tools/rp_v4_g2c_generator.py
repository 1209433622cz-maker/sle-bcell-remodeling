"""RP v4 synthetic-only generator for the frozen 40-scenario G2C grid.

Stage D may use only the development namespace (stage 131).  The final stage
141 namespace remains inaccessible until a later author-approved runner binds
the exact contracts and code hashes.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


SEED_BASE = 2026101004
DEVELOPMENT_STAGE = 131
FINAL_STAGE = 141
EXPECTED_REGISTRY_SHA256 = (
    "d764828ae1807a4a79082eaf1d34f9a2822d7c2b17886b525545901e3a14af5f"
)
EXPECTED_MODEL_SHA256 = (
    "ecc817549566c1a423237d488313efdba3684965e5c30ff2aa89fc6dc3d7fa0f"
)
MODEL_ARRAY_FIELDS = (
    "template_n",
    "template_rate",
    "template_probs",
    "mu",
    "sd",
    "pi",
    "synthetic_design",
    "tilt_axis",
)
LEGACY_PARAMETERS = (
    "composition_log_tilt",
    "within_bin_log2fc",
    "rare_bin_weight_multiplier",
    "managed_depth_multiplier",
    "adjacent_mislabel_probability",
    "managed_capture_log_tilt",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def scenario_ids() -> list[str]:
    return [f"C{c}_R{r}" for c in range(5) for r in range(5)] + [
        f"C{c}_X{x}" for c in range(5) for x in range(1, 4)
    ]


def load_inputs(registry_path: Path, model_path: Path) -> tuple[list[dict], dict]:
    registry_path = Path(registry_path)
    model_path = Path(model_path)
    if sha256_file(registry_path) != EXPECTED_REGISTRY_SHA256:
        raise ValueError("Stage C scenario registry hash mismatch")
    if sha256_file(model_path) != EXPECTED_MODEL_SHA256:
        raise ValueError("Calibration snapshot hash mismatch")

    with registry_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if [row["scenario_id"] for row in rows] != scenario_ids():
        raise ValueError("Scenario order or identity differs from Stage C")

    for index, row in enumerate(rows):
        if int(row["outer_attempts"]) != 4000:
            raise ValueError("Scenario attempt count changed")
        if row["adjudication_role"] not in {
            "APPLICABLE_CONJUNCTION",
            "MANDATORY_BOUNDARY_REPORT",
        }:
            raise ValueError("Unknown adjudication role")
        if (index < 25) != (row["family"] == "OLD_COMPARABLE"):
            raise ValueError("DGP family order changed")
        row["params"] = json.loads(row["parameters"])
        if index < 25:
            if set(row["params"]) != set(LEGACY_PARAMETERS):
                raise ValueError("Legacy scenario parameters changed")
        else:
            expected = {
                "X1": "GAMMA_POISSON_OVERDISPERSION",
                "X2": "CORRELATED_CAPTURE_HETEROGENEITY",
                "X3": "NONADJACENT_LABEL_CONTAMINATION",
            }
            suffix = row["scenario_id"][-2:]
            if expected.get(suffix) != row["stress"]:
                raise ValueError("Shifted-DGP semantics changed")

    model = json.loads(model_path.read_text(encoding="utf-8"))
    if (
        model.get("data_kind") != "CALIBRATION_NO_REAL_EFFECT"
        or model.get("true_template_labels_present") is not False
    ):
        raise PermissionError("Only the outcome-free calibration model is allowed")
    for key in MODEL_ARRAY_FIELDS:
        dtype = np.int64 if key == "template_n" else float
        model[key] = np.asarray(model[key], dtype=dtype)
    if (
        model["template_n"].shape != (68, 5)
        or model["template_rate"].shape != (68, 5)
        or model["template_probs"].shape != (68, 5, 13)
    ):
        raise ValueError("Calibration dimensions changed")
    if (
        not np.allclose(model["template_probs"].sum(axis=2), 1.0, atol=1e-12)
        or np.any(model["template_probs"] <= 0)
    ):
        raise ValueError("Invalid full-library probabilities")
    design = model["synthetic_design"]
    if design.shape != (68, 4) or int(np.sum(design[:, 1] == 0)) != 31:
        raise ValueError("Fixed donor design changed")
    return rows, model


def stream(
    scenario_index: int,
    attempt_id: int,
    component_id: int,
    *,
    stage: int = DEVELOPMENT_STAGE,
) -> np.random.Generator:
    if stage != DEVELOPMENT_STAGE:
        raise PermissionError("Stage D refuses reserved final-stage random streams")
    if not (
        0 <= scenario_index < 40
        and 1 <= attempt_id <= 4000
        and 0 <= component_id < 100
    ):
        raise ValueError("Out-of-contract random-stream address")
    sequence = np.random.SeedSequence(
        [SEED_BASE, stage, scenario_index, attempt_id, component_id]
    )
    return np.random.default_rng(sequence)


def shifted_transition() -> np.ndarray:
    transition = np.zeros((5, 5), dtype=float)
    for origin in range(5):
        adjacent = [dest for dest in range(5) if abs(origin - dest) == 1]
        nonadjacent = [
            dest for dest in range(5) if dest != origin and abs(origin - dest) > 1
        ]
        transition[origin, origin] = 0.92
        for dest in adjacent:
            transition[origin, dest] = 0.05 / len(adjacent)
        for dest in nonadjacent:
            transition[origin, dest] = 0.03 / len(nonadjacent)
    if not np.allclose(transition.sum(axis=1), 1.0):
        raise RuntimeError("Shifted transition rows do not sum to one")
    return transition


def legacy_transition(mislabel_probability: float) -> np.ndarray:
    transition = np.eye(5) * (1.0 - mislabel_probability)
    for origin in range(5):
        adjacent = [dest for dest in (origin - 1, origin + 1) if 0 <= dest < 5]
        for dest in adjacent:
            transition[origin, dest] = mislabel_probability / len(adjacent)
    return transition


def effective_parameters(scenario: dict) -> dict[str, float]:
    if scenario["family"] == "OLD_COMPARABLE":
        return {key: float(scenario["params"][key]) for key in LEGACY_PARAMETERS}
    structure = int(scenario["scenario_id"][1])
    composition = 0.35 if structure in {1, 3, 4} else 0.0
    within_bin = 0.4 if structure in {2, 3} else -0.4 if structure == 4 else 0.0
    return {
        "composition_log_tilt": composition,
        "within_bin_log2fc": within_bin,
        "rare_bin_weight_multiplier": 1.0,
        "managed_depth_multiplier": 1.0,
        "adjacent_mislabel_probability": 0.0,
        "managed_capture_log_tilt": 0.0,
    }


def correlated_capture_multiplier(
    rng: np.random.Generator, n_rows: int, scenario: dict
) -> np.ndarray:
    if scenario["stress"] != "CORRELATED_CAPTURE_HETEROGENEITY":
        return np.ones((n_rows, 5), dtype=float)
    params = scenario["params"]
    expected = (
        float(params["donor_log_sd"]) == 0.35
        and float(params["bin_log_sd"]) == 0.2
        and float(params["bin_AR1_rho"]) == 0.6
        and params["lognormal_mean_correction"] is True
    )
    if not expected:
        raise ValueError("Correlated-capture assumptions changed")
    donor = rng.normal(0.0, 0.35, size=(n_rows, 1))
    distance = np.abs(np.subtract.outer(np.arange(5), np.arange(5)))
    covariance = (0.2**2) * 0.6**distance
    bins = rng.standard_normal((n_rows, 5)) @ np.linalg.cholesky(covariance).T
    return np.exp(donor + bins - 0.5 * (0.35**2 + 0.2**2))


def generate(
    model: dict,
    scenario: dict,
    scenario_index: int,
    attempt_id: int,
    *,
    stage: int = DEVELOPMENT_STAGE,
) -> dict:
    if stage != DEVELOPMENT_STAGE:
        raise PermissionError("Final random streams remain locked")
    if scenario["scenario_id"] != scenario_ids()[scenario_index]:
        raise ValueError("Scenario identity mismatch")

    design = model["synthetic_design"].copy()
    disease = design[:, 1]
    template_ids = stream(scenario_index, attempt_id, 0, stage=stage).integers(
        0, 68, size=68
    )
    template_n = model["template_n"][template_ids]
    template_rate = model["template_rate"][template_ids]
    template_probs = model["template_probs"][template_ids]
    params = effective_parameters(scenario)

    weights = (template_n - 29) * np.exp(
        disease[:, None]
        * params["composition_log_tilt"]
        * model["tilt_axis"][None, :]
    )
    weights /= weights.sum(axis=1, keepdims=True)
    latent_n = 30 + stream(
        scenario_index, attempt_id, 1, stage=stage
    ).multinomial(template_n.sum(axis=1) - 150, weights)

    rare = params["rare_bin_weight_multiplier"]
    if rare != 1.0:
        retained = stream(scenario_index, attempt_id, 2, stage=stage).binomial(
            latent_n[:, 0], rare
        )
        latent_n[:, 4] += latent_n[:, 0] - retained
        latent_n[:, 0] = retained

    capture = template_rate * np.power(
        params["managed_depth_multiplier"], disease[:, None]
    )
    capture *= np.exp(
        disease[:, None]
        * params["managed_capture_log_tilt"]
        * model["tilt_axis"][None, :]
    )
    rate = capture[:, :, None] * template_probs
    rate[:, :, :12] *= np.exp2(
        disease[:, None, None] * params["within_bin_log2fc"]
    )

    shifted = scenario["stress"] if scenario["family"] == "PRESPECIFIED_SHIFT" else "NONE"
    if shifted == "GAMMA_POISSON_OVERDISPERSION":
        if not np.isclose(
            float(scenario["params"]["coefficient_of_variation"]), np.sqrt(0.1)
        ):
            raise ValueError("Gamma-Poisson coefficient of variation changed")
        rate *= stream(scenario_index, attempt_id, 5, stage=stage).gamma(
            10.0, 0.1, size=rate.shape
        )
    if shifted == "CORRELATED_CAPTURE_HETEROGENEITY":
        rate *= correlated_capture_multiplier(
            stream(scenario_index, attempt_id, 6, stage=stage), 68, scenario
        )[:, :, None]

    if shifted == "NONADJACENT_LABEL_CONTAMINATION":
        if (
            float(scenario["params"]["adjacent_component"]) != 0.05
            or float(scenario["params"]["nonadjacent_component"]) != 0.03
        ):
            raise ValueError("Nonadjacent transition contract changed")
        transition = shifted_transition()
    else:
        transition = legacy_transition(params["adjacent_mislabel_probability"])

    flow_rng = stream(scenario_index, attempt_id, 3, stage=stage)
    flows = np.zeros((68, 5, 5), dtype=np.int64)
    for origin in range(5):
        if np.isclose(transition[origin, origin], 1.0):
            flows[:, origin, origin] = latent_n[:, origin]
        else:
            flows[:, origin, :] = flow_rng.multinomial(
                latent_n[:, origin], transition[origin]
            )
    observed_n = flows.sum(axis=1)

    count_rng = stream(scenario_index, attempt_id, 4, stage=stage)
    categories = np.zeros((68, 5, 13), dtype=np.int64)
    for origin in range(5):
        for destination in range(5):
            if transition[origin, destination] > 0:
                categories[:, destination, :] += count_rng.poisson(
                    flows[:, origin, destination, None] * rate[:, origin, :]
                )
    libraries = categories.sum(axis=2)
    supported = np.all(observed_n >= 30) and np.all(libraries > 0)
    return {
        "data_kind": "SIMULATED_ONLY",
        "n": observed_n,
        "categories": categories,
        "X": design,
        "template_indices": template_ids,
        "flow": flows,
        "latent_n": latent_n,
        "scenario_id": scenario["scenario_id"],
        "attempt": attempt_id,
        "support_status": "SUPPORTED" if supported else "SUPPORT_STOP",
        "under_supported_bins": int(np.sum(observed_n < 30)),
        "min_observed_cells": int(observed_n.min()),
        "zero_library_bins": int(np.sum(libraries == 0)),
    }


def data_digest(data: dict) -> str:
    digest = hashlib.sha256()
    for key in ("n", "categories", "X", "template_indices", "flow"):
        value = np.ascontiguousarray(data[key])
        digest.update(key.encode())
        digest.update(value.dtype.str.encode())
        digest.update(str(value.shape).encode())
        digest.update(value.tobytes())
    return digest.hexdigest()
