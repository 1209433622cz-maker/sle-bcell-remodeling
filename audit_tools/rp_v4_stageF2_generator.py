"""Authorization-gated RP v4 G2C generator for Stage F2."""
from __future__ import annotations

import numpy as np

try:
    from . import rp_v4_g2c_generator as frozen
    from .rp_v4_stageF2_common import ExecutionAuthorization, SEED_BASE
except ImportError:
    import rp_v4_g2c_generator as frozen
    from rp_v4_stageF2_common import ExecutionAuthorization, SEED_BASE


def stream(
    scenario_index: int,
    attempt_id: int,
    component_id: int,
    authorization: ExecutionAuthorization,
) -> np.random.Generator:
    if authorization.purpose != "outer":
        raise PermissionError("Outer generator requires outer authorization")
    if not (
        0 <= scenario_index < 40
        and 1 <= attempt_id <= 4000
        and 0 <= component_id < 100
    ):
        raise ValueError("Out-of-contract random-stream address")
    sequence = np.random.SeedSequence(
        [SEED_BASE, authorization.stage, scenario_index, attempt_id, component_id]
    )
    return np.random.default_rng(sequence)


def generate(
    model: dict,
    scenario: dict,
    scenario_index: int,
    attempt_id: int,
    authorization: ExecutionAuthorization,
) -> dict:
    if authorization.purpose != "outer":
        raise PermissionError("Wrong authorization purpose")
    if scenario["scenario_id"] != frozen.scenario_ids()[scenario_index]:
        raise ValueError("Scenario identity mismatch")

    design = model["synthetic_design"].copy()
    disease = design[:, 1]
    template_ids = stream(scenario_index, attempt_id, 0, authorization).integers(
        0, 68, size=68
    )
    template_n = model["template_n"][template_ids]
    template_rate = model["template_rate"][template_ids]
    template_probs = model["template_probs"][template_ids]
    params = frozen.effective_parameters(scenario)

    weights = (template_n - 29) * np.exp(
        disease[:, None]
        * params["composition_log_tilt"]
        * model["tilt_axis"][None, :]
    )
    weights /= weights.sum(axis=1, keepdims=True)
    latent_n = 30 + stream(
        scenario_index, attempt_id, 1, authorization
    ).multinomial(template_n.sum(axis=1) - 150, weights)

    rare = params["rare_bin_weight_multiplier"]
    if rare != 1.0:
        retained = stream(scenario_index, attempt_id, 2, authorization).binomial(
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

    shifted = (
        scenario["stress"]
        if scenario["family"] == "PRESPECIFIED_SHIFT"
        else "NONE"
    )
    if shifted == "GAMMA_POISSON_OVERDISPERSION":
        if not np.isclose(
            float(scenario["params"]["coefficient_of_variation"]), np.sqrt(0.1)
        ):
            raise ValueError("Gamma-Poisson coefficient of variation changed")
        rate *= stream(scenario_index, attempt_id, 5, authorization).gamma(
            10.0, 0.1, size=rate.shape
        )
    if shifted == "CORRELATED_CAPTURE_HETEROGENEITY":
        rate *= frozen.correlated_capture_multiplier(
            stream(scenario_index, attempt_id, 6, authorization), 68, scenario
        )[:, :, None]

    if shifted == "NONADJACENT_LABEL_CONTAMINATION":
        if (
            float(scenario["params"]["adjacent_component"]) != 0.05
            or float(scenario["params"]["nonadjacent_component"]) != 0.03
        ):
            raise ValueError("Nonadjacent transition contract changed")
        transition = frozen.shifted_transition()
    else:
        transition = frozen.legacy_transition(
            params["adjacent_mislabel_probability"]
        )

    flow_rng = stream(scenario_index, attempt_id, 3, authorization)
    flows = np.zeros((68, 5, 5), dtype=np.int64)
    for origin in range(5):
        if np.isclose(transition[origin, origin], 1.0):
            flows[:, origin, origin] = latent_n[:, origin]
        else:
            flows[:, origin, :] = flow_rng.multinomial(
                latent_n[:, origin], transition[origin]
            )
    observed_n = flows.sum(axis=1)

    count_rng = stream(scenario_index, attempt_id, 4, authorization)
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


data_digest = frozen.data_digest
load_inputs = frozen.load_inputs
scenario_ids = frozen.scenario_ids
