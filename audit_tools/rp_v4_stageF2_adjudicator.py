"""Result-blind, algebra-checking adjudicator for the RP v4 G2C contract."""
from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

import numpy as np

try:
    from .rp_v4_g2c_hc3t import CRITICAL_VALUE, DF, METHOD
except ImportError:
    from rp_v4_g2c_hc3t import CRITICAL_VALUE, DF, METHOD


ATTEMPTS_PER_SCENARIO = 4000
MIN_SUPPORTED = 274
FINAL_STAGE = 141
SEED_BASE = 2026101004
STATUS_SET = {"SUPPORTED", "SUPPORT_STOP", "NUMERICAL_FAILURE"}
COVERAGE_BOUNDS = (0.925, 0.975)
BIAS_TOLERANCE = 0.10
FAILURE_LIMIT = 0.01
TYPE1_UPPER_LIMIT = 0.075
TRUTH_MCSE_TOLERANCE = 0.01


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Invalid Wilson input")
    proportion = successes / total
    denominator = 1 + z * z / total
    midpoint = (proportion + z * z / (2 * total)) / denominator
    half = z * math.sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    ) / denominator
    return midpoint - half, midpoint + half


def validate_interval(value: object) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Missing frozen single-estimand fit")
    if value.get("estimand") != "delta_profile":
        raise ValueError("Wrong estimand in fitted interval")
    if value.get("df") != DF:
        raise ValueError("Interval degrees of freedom drift")
    if value.get("method") != METHOD:
        raise ValueError("Interval method drift")
    if value.get("data_kind") != "SIMULATED_ONLY":
        raise PermissionError("Interval is not synthetic-only")
    if value.get("G2C_PASS") is not False or value.get("WP2_REAL_EFFECT_UNLOCK") is not False:
        raise PermissionError("Attempt-level interval contains an unauthorized unlock")
    fields = (
        "point",
        "ci_lower",
        "ci_upper",
        "standard_error_HC3",
        "critical_value",
        "max_point_leverage",
    )
    if any(field not in value for field in fields):
        raise ValueError("Incomplete fitted record")
    point, lower, upper, standard_error, critical, leverage = (
        float(value[field]) for field in fields
    )
    if not all(
        math.isfinite(number)
        for number in (point, lower, upper, standard_error, critical, leverage)
    ):
        raise ValueError("Nonfinite fitted record")
    if standard_error <= 0 or not 0 <= leverage < 1:
        raise ValueError("Invalid HC3 scale or leverage")
    if not math.isclose(critical, CRITICAL_VALUE, rel_tol=1e-14, abs_tol=1e-14):
        raise ValueError("Student-t critical value drift")
    expected_lower = point - CRITICAL_VALUE * standard_error
    expected_upper = point + CRITICAL_VALUE * standard_error
    if not (
        math.isclose(lower, expected_lower, rel_tol=1e-12, abs_tol=1e-12)
        and math.isclose(upper, expected_upper, rel_tol=1e-12, abs_tol=1e-12)
        and lower < upper
    ):
        raise ValueError("HC3-t(64) interval algebra mismatch")
    return value


def validate_attempts(
    attempts: Iterable[dict],
    scenario_id: str,
    scenario_index: int,
    *,
    stage: int = FINAL_STAGE,
    required_n: int = ATTEMPTS_PER_SCENARIO,
) -> list[dict]:
    rows = list(attempts)
    if len(rows) != required_n:
        raise ValueError(
            f"Incomplete attempt inventory: {scenario_id} {len(rows)}/{required_n}"
        )
    identifiers = [row.get("attempt_id") for row in rows]
    if set(identifiers) != set(range(1, required_n + 1)) or len(
        identifiers
    ) != len(set(identifiers)):
        raise ValueError("Duplicate, missing or out-of-range attempt IDs")
    prohibited = {
        "sample_id",
        "donor_id",
        "disease_group",
        "external_disease_coefficient",
        "patient_id",
        "real_outcome",
        "clinical_activity",
    }
    for row in rows:
        if (
            row.get("scenario_id") != scenario_id
            or row.get("scenario_index") != scenario_index
            or row.get("stage") != stage
        ):
            raise ValueError("Wrong scenario, scenario index or stage")
        if row.get("seed_base") != SEED_BASE:
            raise ValueError("Frozen seed base mismatch")
        if row.get("data_kind") != "SIMULATED_ONLY":
            raise PermissionError("Non-synthetic record refused")
        if (
            row.get("real_effects_fitted") is not False
            or row.get("final_stream") is not True
            or row.get("G2C_adjudicated") is not False
            or row.get("external_disease_outcomes_fitted") is not False
        ):
            raise PermissionError("Attempt safety flags drift")
        if prohibited.intersection(row):
            raise PermissionError("Outcome/linkage keys found in synthetic payload")
        status = row.get("status")
        if status not in STATUS_SET:
            raise ValueError("Invalid attempt status")
        digest = row.get("input_digest")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise ValueError("Missing or invalid synthetic input digest")
        if status == "SUPPORTED":
            validate_interval(row.get("synthetic_HC3_t"))
        elif "synthetic_HC3_t" in row:
            raise ValueError("Stopped or failed attempts must not carry a fit")
        if status == "NUMERICAL_FAILURE" and not isinstance(
            row.get("numerical_failure_type"), str
        ):
            raise ValueError("Numerical failure lacks a failure class")
    return sorted(rows, key=lambda row: row["attempt_id"])


def adjudicate_one(
    attempts: Iterable[dict],
    scenario: dict,
    oracle: dict,
    *,
    stage: int = FINAL_STAGE,
    required_n: int = ATTEMPTS_PER_SCENARIO,
) -> dict:
    scenario_id = scenario["scenario_id"]
    scenario_index = int(scenario["scenario_index"])
    role = scenario["adjudication_role"]
    if role not in {"APPLICABLE_CONJUNCTION", "MANDATORY_BOUNDARY_REPORT"}:
        raise ValueError("Unknown frozen adjudication role")
    rows = validate_attempts(
        attempts,
        scenario_id,
        scenario_index,
        stage=stage,
        required_n=required_n,
    )
    if oracle.get("scenario_id") != scenario_id:
        raise ValueError("Oracle identity mismatch")
    if oracle.get("precision_pass") is not True:
        raise ValueError("Truth precision qualification missing")
    truth = float(oracle["truth"])
    truth_mcse = float(oracle["truth_mcse"])
    typical_se = float(oracle["typical_coefficient_se"])
    if not all(math.isfinite(value) for value in (truth, truth_mcse, typical_se)):
        raise ValueError("Invalid oracle values")
    if typical_se <= 0 or truth_mcse < 0:
        raise ValueError("Invalid oracle scale")
    if truth_mcse > TRUTH_MCSE_TOLERANCE * typical_se:
        raise ValueError("Oracle MCSE gate failed")

    counts = Counter(row["status"] for row in rows)
    supported = [
        row["synthetic_HC3_t"] for row in rows if row["status"] == "SUPPORTED"
    ]
    numerical_failures = counts["NUMERICAL_FAILURE"]
    base = {
        "scenario_id": scenario_id,
        "scenario_index": scenario_index,
        "domain": role,
        "n_attempts": required_n,
        "n_supported": len(supported),
        "support_stop": counts["SUPPORT_STOP"],
        "numerical_failures": numerical_failures,
        "truth": truth,
        "truth_mcse": truth_mcse,
        "oracle_precision_pass": True,
    }
    if numerical_failures / required_n > FAILURE_LIMIT:
        return {**base, "status": "HOLD_NUMERICAL_FAILURE"}
    if role == "MANDATORY_BOUNDARY_REPORT":
        return {**base, "status": "BOUNDARY_REPORTED"}
    if len(supported) < MIN_SUPPORTED:
        return {**base, "status": "HOLD_INSUFFICIENT_SUPPORTED_PERFORMANCE"}

    estimates = np.asarray([fit["point"] for fit in supported], dtype=float)
    empirical_sd = float(estimates.std(ddof=1))
    if not math.isfinite(empirical_sd) or empirical_sd <= 0:
        return {**base, "status": "HOLD_UNDEFINED_EMPIRICAL_SD"}
    bias = float(estimates.mean() - truth)
    mcse_bias = empirical_sd / math.sqrt(len(estimates))
    bias_upper = (abs(bias) + 1.96 * mcse_bias) / empirical_sd
    covered = sum(
        fit["ci_lower"] <= truth <= fit["ci_upper"] for fit in supported
    )
    coverage = covered / len(supported)
    coverage_lower, coverage_upper = wilson_interval(covered, len(supported))
    bias_pass = bias_upper <= BIAS_TOLERANCE
    coverage_pass = (
        coverage_lower >= COVERAGE_BOUNDS[0]
        and coverage_upper <= COVERAGE_BOUNDS[1]
    )

    exact_null = oracle.get("exact_null_registered", False)
    if not isinstance(exact_null, bool):
        raise ValueError("Oracle exact-null flag must be boolean")
    type1_error = None
    type1_upper = None
    type1_pass = None
    if exact_null:
        rejections = sum(
            not (fit["ci_lower"] <= 0 <= fit["ci_upper"]) for fit in supported
        )
        type1_error = rejections / len(supported)
        _, type1_upper = wilson_interval(rejections, len(supported))
        type1_pass = type1_upper <= TYPE1_UPPER_LIMIT
    all_pass = bias_pass and coverage_pass and type1_pass is not False
    return {
        **base,
        "status": "PASS" if all_pass else "HOLD",
        "empirical_sd": empirical_sd,
        "bias": bias,
        "bias_upper_over_emp_sd": bias_upper,
        "bias_pass": bias_pass,
        "coverage": coverage,
        "coverage_wilson_lower": coverage_lower,
        "coverage_wilson_upper": coverage_upper,
        "coverage_pass": coverage_pass,
        "exact_null_registered": exact_null,
        "type1_error": type1_error,
        "type1_wilson_upper": type1_upper,
        "type1_pass": type1_pass,
    }


def full_conjunction(results: list[dict], registry: list[dict]) -> dict:
    registered_ids = [row["scenario_id"] for row in registry]
    result_ids = [row["scenario_id"] for row in results]
    if (
        len(registered_ids) != 40
        or len(set(registered_ids)) != 40
        or len(result_ids) != 40
        or set(result_ids) != set(registered_ids)
    ):
        raise ValueError("Not 40 unique registered scenario results")
    roles = {row["scenario_id"]: row["adjudication_role"] for row in registry}
    if any(
        row.get("n_attempts") != ATTEMPTS_PER_SCENARIO
        or row.get("oracle_precision_pass") is not True
        or row.get("domain") != roles[row["scenario_id"]]
        for row in results
    ):
        raise ValueError("Incomplete registered per-scenario adjudication")
    applicable = [
        row for row in results if roles[row["scenario_id"]] == "APPLICABLE_CONJUNCTION"
    ]
    boundaries = [
        row
        for row in results
        if roles[row["scenario_id"]] == "MANDATORY_BOUNDARY_REPORT"
    ]
    if len(applicable) != 30 or len(boundaries) != 10:
        raise ValueError("Frozen adjudication-domain count drift")
    applicable_pass = all(row["status"] == "PASS" for row in applicable)
    boundary_integrity = all(
        row["status"] == "BOUNDARY_REPORTED" for row in boundaries
    )
    synthetic_pass = applicable_pass and boundary_integrity
    return {
        "g2c_synthetic_applicable_conjunction_pass": synthetic_pass,
        "applicable_pass": sum(row["status"] == "PASS" for row in applicable),
        "applicable_total": 30,
        "boundary_integrity_pass": boundary_integrity,
        "boundary_scenarios_reported": len(boundaries),
        "recommended_for_separate_post_G2C_review": synthetic_pass,
        "real_WP2_outcomes_authorized": False,
        "external_disease_outcomes_authorized": False,
    }
