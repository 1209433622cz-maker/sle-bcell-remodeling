"""Evaluate the single RP v4 G2C candidate on exposed historical streams.

These results are development evidence only.  They can select/freeze a method,
but they cannot establish forward G2C performance or unlock real outcomes.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

try:
    from .rp_v3_g2_estimation import responses
    from .rp_v3_g2_generator import generate, load_model, scenarios, stream
    from .rp_v3_g2b_adjudicate import load_truth, wilson
    from .rp_v3_g2b_studentized import paired_studentized
    from .rp_v4_g2c_hc3t import ESTIMAND, TARGET_INDEX, interval
except ImportError:  # Direct script execution from audit_tools/.
    from rp_v3_g2_estimation import responses
    from rp_v3_g2_generator import generate, load_model, scenarios, stream
    from rp_v3_g2b_adjudicate import load_truth, wilson
    from rp_v3_g2b_studentized import paired_studentized
    from rp_v4_g2c_hc3t import ESTIMAND, TARGET_INDEX, interval


REPO_ROOT = Path(__file__).resolve().parents[1]
PARENT_FREEZE = REPO_ROOT / "phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze"
PREFIT = REPO_ROOT / "phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit"
G2B_STAGE = 121
APPLICABLE = {"baseline", "depth_imbalance", "RNA_capture_content"}
DIAGNOSTIC_ATTEMPTS = (1, 251, 501, 751, 1001, 1251, 1501, 1751)


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _moment_shape(values: np.ndarray) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    centered = values - values.mean()
    second = np.mean(centered**2)
    if second <= 0:
        return math.nan, math.nan
    skew = float(np.mean(centered**3) / second**1.5)
    excess = float(np.mean(centered**4) / second**2 - 3.0)
    return skew, excess


def run(output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Output directory must be new: {output_dir}")
    output_dir.mkdir(parents=True)
    model = load_model(PARENT_FREEZE / "02_G2_CALIBRATION_MODEL.json")
    scenario_rows = scenarios(PREFIT / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv")
    truth = load_truth(PARENT_FREEZE / "04_G2_TRUTH_TABLE.csv")

    diagnostic_rows: list[dict] = []
    development_rows: list[dict] = []
    for scenario_index, scenario in enumerate(scenario_rows):
        points: list[float] = []
        lowers: list[float] = []
        uppers: list[float] = []
        support_stops = 0
        numerical_failures = 0
        for attempt in range(1, 2001):
            try:
                data = generate(model, scenario, scenario_index, attempt, stage=G2B_STAGE)
                if data["support_status"] == "SUPPORT_STOP":
                    support_stops += 1
                    continue
                Y = responses(data, model)
                result = interval(data["X"], Y, data_kind="SIMULATED_ONLY")
                points.append(result["point"])
                lowers.append(result["ci_lower"])
                uppers.append(result["ci_upper"])

                if attempt in DIAGNOSTIC_ATTEMPTS:
                    g2b = paired_studentized(
                        data["X"],
                        Y,
                        stream(scenario_index, attempt, 5, stage=G2B_STAGE),
                        data_kind="SIMULATED_ONLY",
                    )
                    valid = g2b["success"]
                    tstar = g2b["studentized_errors"][valid, TARGET_INDEX]
                    sest = g2b["se_star_HC3"][valid, TARGET_INDEX]
                    skew, excess = _moment_shape(tstar)
                    boot = g2b["estimates"][valid]
                    decomposition_error = np.max(
                        np.abs(boot[:, TARGET_INDEX] - (boot[:, 1] - boot[:, 0]))
                    )
                    diagnostic_rows.append(
                        {
                            "scenario_id": scenario["scenario_id"],
                            "regime": scenario["regime"],
                            "attempt_id": attempt,
                            "support_status": data["support_status"],
                            "min_observed_cells": data["min_observed_cells"],
                            "point_HC3_se": g2b["se_point_HC3"][TARGET_INDEX],
                            "bootstrap_se_min": float(np.min(sest)),
                            "bootstrap_se_p01": float(np.quantile(sest, 0.01)),
                            "bootstrap_se_p05": float(np.quantile(sest, 0.05)),
                            "bootstrap_se_median": float(np.median(sest)),
                            "se_p01_over_median": float(np.quantile(sest, 0.01) / np.median(sest)),
                            "tstar_q025": float(np.quantile(tstar, 0.025)),
                            "tstar_q975": float(np.quantile(tstar, 0.975)),
                            "tstar_skew": skew,
                            "tstar_excess_kurtosis": excess,
                            "point_max_leverage": g2b["max_point_leverage"],
                            "bootstrap_max_leverage": g2b["max_bootstrap_leverage"],
                            "inner_failures": g2b["failures"],
                            "betaB_profile_bootstrap_corr": float(np.corrcoef(boot[:, 0], boot[:, 1])[0, 1]),
                            "delta_algebra_max_abs_error": float(decomposition_error),
                        }
                    )
            except Exception:
                numerical_failures += 1

        target_truth = truth[(scenario["scenario_id"], ESTIMAND)]
        point = np.asarray(points)
        lower = np.asarray(lowers)
        upper = np.asarray(uppers)
        n = len(point)
        errors = point - target_truth["truth"]
        empirical_sd = float(point.std(ddof=1)) if n > 1 else math.nan
        bias = float(errors.mean()) if n else math.nan
        bias_mcse = empirical_sd / math.sqrt(n) if n else math.nan
        bias_upper = (
            (abs(bias) + 1.96 * bias_mcse) / empirical_sd
            if n > 1 and empirical_sd > 0
            else math.inf
        )
        covered = int(np.sum((lower <= target_truth["truth"]) & (target_truth["truth"] <= upper)))
        cov_lower, cov_upper = wilson(covered, n)
        true_null = target_truth["true_null_registered"]
        rejected = int(np.sum((lower > 0) | (upper < 0))) if true_null else 0
        type_upper = wilson(rejected, n)[1] if true_null else math.nan
        applicable = scenario["regime"] in APPLICABLE
        checks = [
            numerical_failures / 2000 <= 0.01,
            target_truth["truth_precision_pass"],
            bias_upper <= 0.10,
            cov_lower >= 0.925,
            cov_upper <= 0.975,
        ]
        if true_null:
            checks.append(type_upper <= 0.075)
        development_rows.append(
            {
                "scenario_id": scenario["scenario_id"],
                "truth_structure": scenario["truth_structure"],
                "regime": scenario["regime"],
                "applicable_domain": applicable,
                "truth": target_truth["truth"],
                "outer_attempts": 2000,
                "supported_attempts": n,
                "support_stops": support_stops,
                "numerical_failures": numerical_failures,
                "bias": bias,
                "empirical_sd": empirical_sd,
                "bias_upper95_in_empirical_sd": bias_upper,
                "bias_pass": bias_upper <= 0.10,
                "coverage": covered / n if n else math.nan,
                "coverage_wilson_lower": cov_lower,
                "coverage_wilson_upper": cov_upper,
                "coverage_pass": cov_lower >= 0.925 and cov_upper <= 0.975,
                "type_i": rejected / n if true_null and n else "",
                "type_i_wilson_upper": type_upper if true_null else "",
                "type_i_pass": type_upper <= 0.075 if true_null else "",
                "mean_interval_length": float(np.mean(upper - lower)) if n else math.nan,
                "development_decision": (
                    "DEVELOPMENT_PASS"
                    if applicable and all(checks)
                    else "BOUNDARY_REPORTED"
                    if not applicable
                    else "DEVELOPMENT_HOLD"
                ),
            }
        )

    _write_csv(output_dir / "01_EXPOSED_STREAM_STUDENTIZER_DIAGNOSTIC.csv", diagnostic_rows)
    _write_csv(output_dir / "02_SINGLE_CANDIDATE_DEVELOPMENT_PERFORMANCE.csv", development_rows)
    applicable_rows = [row for row in development_rows if row["applicable_domain"]]
    diag = diagnostic_rows
    summary = {
        "status": "DEVELOPMENT_ONLY__NOT_FORWARD_VALIDATION",
        "estimand": ESTIMAND,
        "historical_stage": G2B_STAGE,
        "outer_attempts_per_scenario": 2000,
        "diagnostic_attempts_per_scenario": len(DIAGNOSTIC_ATTEMPTS),
        "applicable_scenarios": len(applicable_rows),
        "candidate_development_passes": sum(
            row["development_decision"] == "DEVELOPMENT_PASS" for row in applicable_rows
        ),
        "all_applicable_development_pass": all(
            row["development_decision"] == "DEVELOPMENT_PASS" for row in applicable_rows
        ),
        "minimum_se_p01_over_median": min(row["se_p01_over_median"] for row in diag),
        "maximum_abs_tstar_skew": max(abs(row["tstar_skew"]) for row in diag),
        "maximum_abs_tstar_excess_kurtosis": max(
            abs(row["tstar_excess_kurtosis"]) for row in diag
        ),
        "maximum_point_leverage": max(row["point_max_leverage"] for row in diag),
        "maximum_bootstrap_leverage": max(row["bootstrap_max_leverage"] for row in diag),
        "maximum_inner_failures": max(row["inner_failures"] for row in diag),
        "minimum_betaB_profile_bootstrap_corr": min(
            row["betaB_profile_bootstrap_corr"] for row in diag
        ),
        "maximum_delta_algebra_abs_error": max(
            row["delta_algebra_max_abs_error"] for row in diag
        ),
        "interpretation": {
            "TRUTH_MISMATCH": "not indicated by the registered observed-measurement truth contract",
            "NONSMOOTH_DELTA": "not indicated; the delta is an algebraically exact coefficient difference",
            "NEAR_ZERO_STUDENTIZER": "evaluate from the frozen p01/median diagnostic",
            "DONOR_LEVERAGE": "evaluate from the frozen leverage diagnostic",
            "FINITE_MC_MARGIN": "historical G2B misses were mild; this candidate is evaluated only on exposed development streams",
            "SUPPORT_SELECTION": "R1/R3 remain reported boundaries and are excluded from applicable-domain conjunction",
            "DGP_SENSITIVITY": "requires independent shifted-DGP validation before any PASS",
        },
        "forward_validation_executed": False,
        "real_effects_fitted": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
    }
    (output_dir / "03_DEVELOPMENT_DIAGNOSTIC_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir.resolve()), indent=2))

