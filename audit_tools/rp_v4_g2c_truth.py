"""Independent development-stage truth engine for RP v4 G2C.

The oracle uses a separate Philox stream and does not import the G2C generator,
scoring estimator, regression kernel, fitted disease effects or bootstrap
outputs.  Stage 142 remains reserved for the later signed final runner.
"""
from __future__ import annotations

import numpy as np


SEED_BASE = 2026101004
DEVELOPMENT_STAGE = 131


def _rng(scenario_index: int, batch: int) -> np.random.Generator:
    sequence = np.random.SeedSequence(
        [SEED_BASE, DEVELOPMENT_STAGE, scenario_index, batch, 95]
    )
    return np.random.Generator(np.random.Philox(sequence))


def _case_setup(scenario: dict) -> tuple[float, float, float, float, float, float, str]:
    structure = int(scenario["scenario_id"][1])
    if scenario["family"] == "PRESPECIFIED_SHIFT":
        suffix = scenario["scenario_id"][-2:]
        if suffix not in {"X1", "X2", "X3"}:
            raise ValueError("Unknown shifted-DGP suffix")
        composition = 0.35 if structure in {1, 3, 4} else 0.0
        within_bin = (
            0.4 if structure in {2, 3} else -0.4 if structure == 4 else 0.0
        )
        return composition, within_bin, 1.0, 1.0, 0.0, 0.0, scenario["stress"]
    params = scenario["params"]
    return (
        float(params["composition_log_tilt"]),
        float(params["within_bin_log2fc"]),
        float(params["rare_bin_weight_multiplier"]),
        float(params["managed_depth_multiplier"]),
        float(params["adjacent_mislabel_probability"]),
        float(params["managed_capture_log_tilt"]),
        "NONE",
    )


def transition(mode: str, mislabel_probability: float) -> np.ndarray:
    matrix = np.zeros((5, 5), dtype=float)
    for origin in range(5):
        adjacent = [dest for dest in range(5) if abs(origin - dest) == 1]
        if mode == "NONADJACENT_LABEL_CONTAMINATION":
            nonadjacent = [
                dest
                for dest in range(5)
                if dest != origin and abs(origin - dest) > 1
            ]
            matrix[origin, origin] = 0.92
            for dest in adjacent:
                matrix[origin, dest] = 0.05 / len(adjacent)
            for dest in nonadjacent:
                matrix[origin, dest] = 0.03 / len(nonadjacent)
        else:
            matrix[origin, origin] = 1.0 - mislabel_probability
            for dest in adjacent:
                matrix[origin, dest] = mislabel_probability / len(adjacent)
    return matrix


def _score_delta(categories: np.ndarray, observed_n: np.ndarray, model: dict) -> tuple[np.ndarray, np.ndarray]:
    libraries = categories.sum(axis=2)
    valid = np.all(observed_n >= 30, axis=1) & np.all(libraries > 0, axis=1)
    if not np.any(valid):
        return valid, np.zeros(0, dtype=float)
    counts = categories[valid, :, :12].astype(float)
    totals = libraries[valid].astype(float)
    fixed = np.sum(
        (counts * 1e6 / totals[:, :, None]) * np.asarray(model["pi"])[None, :, None],
        axis=1,
    )
    pooled = counts.sum(axis=1) * 1e6 / totals.sum(axis=1)[:, None]
    mean = np.asarray(model["mu"])
    standard_deviation = np.asarray(model["sd"])

    def score(values: np.ndarray) -> np.ndarray:
        transformed = np.log2(values + 0.5)
        return np.mean((transformed - mean) / standard_deviation, axis=1)

    return valid, score(fixed) - score(pooled)


def _coupled_batch(
    model: dict,
    scenario: dict,
    scenario_index: int,
    batch: int,
    attempts: int,
) -> dict:
    """Draw two marginally valid arms with variance-reducing coupling."""
    rng = _rng(scenario_index, batch)
    composition, within_bin, rare, depth, mislabel, capture_tilt, mode = (
        _case_setup(scenario)
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
            bins[:, index] = 0.6 * bins[:, index - 1] + np.sqrt(1 - 0.6**2) * rng.normal(
                0.0, 0.2, size=attempts
            )
        factor = np.exp(donor + bins - 0.5 * (0.35**2 + 0.2**2))
        rate0 *= factor[:, :, None]
        rate1 *= factor[:, :, None]

    matrix = transition(mode, mislabel)

    def draw_flow(counts: np.ndarray) -> np.ndarray:
        flows = np.zeros((attempts, 5, 5), dtype=np.int64)
        for origin in range(5):
            if matrix[origin, origin] == 1:
                flows[:, origin, origin] = counts[:, origin]
            else:
                flows[:, origin, :] = rng.multinomial(counts[:, origin], matrix[origin])
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
    valid0, score0 = _score_delta(categories0, observed0, model)
    valid1, score1 = _score_delta(categories1, observed1, model)
    return {
        "attempts": attempts,
        "n0": int(valid0.sum()),
        "n1": int(valid1.sum()),
        "sum0": float(score0.sum()),
        "sum1": float(score1.sum()),
        "sq0": float(score0 @ score0),
        "sq1": float(score1 @ score1),
    }


def truth_pilot(
    model: dict,
    scenario: dict,
    scenario_index: int,
    *,
    effort_per_arm: int = 32768,
    batches: int = 16,
) -> dict:
    """Qualify selected truths on development streams without final evidence."""
    if (
        effort_per_arm < 1088
        or effort_per_arm > 131072
        or effort_per_arm % batches
    ):
        raise ValueError("Invalid technical truth effort or batch count")
    attempts = effort_per_arm // batches
    batch_rows = [
        _coupled_batch(model, scenario, scenario_index, batch, attempts)
        for batch in range(batches)
    ]
    n0 = sum(row["n0"] for row in batch_rows)
    n1 = sum(row["n1"] for row in batch_rows)
    if min(n0, n1) <= 100:
        return {
            "scenario_id": scenario["scenario_id"],
            "status": "HOLD_TRUTH_SUPPORT_INSUFFICIENT",
            "attempts_per_arm": effort_per_arm,
            "final_stage_142_consumed": False,
        }
    mean0 = sum(row["sum0"] for row in batch_rows) / n0
    mean1 = sum(row["sum1"] for row in batch_rows) / n1
    variance0 = max(sum(row["sq0"] for row in batch_rows) / n0 - mean0**2, 0.0)
    variance1 = max(sum(row["sq1"] for row in batch_rows) / n1 - mean1**2, 0.0)
    design = np.asarray(model["synthetic_design"], dtype=float)
    coefficient_weights = (np.linalg.inv(design.T @ design) @ design.T)[1]
    typical_standard_error = np.sqrt(
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
    monte_carlo_standard_error = float(
        np.std(influence, ddof=1) / np.sqrt(batches)
    )
    exact = (
        scenario["scenario_id"].startswith("C0_")
        and scenario["family"] == "PRESPECIFIED_SHIFT"
    )
    precision_pass = exact or monte_carlo_standard_error <= 0.01 * typical_standard_error
    return {
        "scenario_id": scenario["scenario_id"],
        "status": (
            "TECHNICAL_PRECISION_PASS"
            if precision_pass
            else "TECHNICAL_PRECISION_NOT_YET_QUALIFIED"
        ),
        "truth": 0.0 if exact else float(mean1 - mean0),
        "truth_mcse": 0.0 if exact else monte_carlo_standard_error,
        "observed_pair_difference": float(mean1 - mean0),
        "paired_mcse_before_exact_symmetry": monte_carlo_standard_error,
        "typical_coefficient_se": float(typical_standard_error),
        "mcse_over_typical": float(
            monte_carlo_standard_error / typical_standard_error
        ),
        "truth_type": "EXACT_SYMMETRY" if exact else "PAIRED_INDEPENDENT_ORACLE",
        "n0": n0,
        "n1": n1,
        "attempts_per_arm": effort_per_arm,
        "batches": batches,
        "minimum_conditional_support": min(n0, n1) / effort_per_arm,
        "real_effects_fitted": False,
        "final_stage_142_consumed": False,
    }
