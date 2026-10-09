"""Adjudicate a complete RP v3 full-G2 run against the frozen rules."""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    from .rp_v3_g2_estimation import TARGETS
    from .rp_v3_g2_full_runner import FREEZE_DIR, PREFIT_DIR, REPO_ROOT, binding, verify_chunk
    from .rp_v3_g2_generator import scenarios
except ImportError:  # Direct script execution from audit_tools/.
    from rp_v3_g2_estimation import TARGETS
    from rp_v3_g2_full_runner import FREEZE_DIR, PREFIT_DIR, REPO_ROOT, binding, verify_chunk
    from rp_v3_g2_generator import scenarios


Z975 = 1.959963984540054
MIN_SUPPORTED_FOR_COVERAGE_GATE = 274
ADJUDICABLE_REGIMES = {"baseline", "depth_imbalance", "RNA_capture_content"}
BOUNDARY_REGIMES = {"rarity_support", "adjacent_mislabeling"}


def wilson(successes: int, total: int, z: float = Z975) -> tuple[float, float]:
    if total <= 0 or not 0 <= successes <= total:
        return math.nan, math.nan
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    half = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denominator
    return center - half, center + half


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def load_truth(path: Path) -> dict[tuple[str, str], dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        key = (row["scenario_id"], row["target_id"])
        if key in result:
            raise ValueError(f"Duplicate truth row: {key}")
        result[key] = {
            "truth": float(row["truth"]),
            "truth_mcse": float(row["truth_mcse"]),
            "truth_precision_pass": _as_bool(row["precision_pass"]),
            "true_null_registered": _as_bool(row["true_null_registered"]),
            "truth_basis": row["truth_basis"],
        }
    if len(result) != 250:
        raise ValueError(f"Expected 250 truth rows, found {len(result)}")
    return result


def load_scenario_rows(run_root: Path, scenario_id: str, expected_binding: str) -> list[dict]:
    scenario_dir = run_root / scenario_id
    if not scenario_dir.is_dir():
        raise FileNotFoundError(f"Missing full-G2 scenario directory: {scenario_dir}")
    rows = []
    for chunk in sorted(scenario_dir.glob("chunk_*_*")):
        verify_chunk(chunk, expected_binding)
        with gzip.open(chunk / "attempt_targets.csv.gz", "rt", encoding="utf-8", newline="") as handle:
            rows.extend(csv.DictReader(handle))
    expected_pairs = {(attempt, target) for attempt in range(1, 2001) for target in TARGETS}
    actual_pairs = [(int(row["attempt_id"]), row["target_id"]) for row in rows]
    if len(actual_pairs) != 20000 or set(actual_pairs) != expected_pairs or len(set(actual_pairs)) != len(actual_pairs):
        raise RuntimeError(f"Incomplete or duplicated attempt-target accounting for {scenario_id}")
    for attempt in range(1, 2001):
        statuses = {row["status"] for row in rows if int(row["attempt_id"]) == attempt}
        if len(statuses) != 1:
            raise RuntimeError(f"Inconsistent target status for {scenario_id} attempt {attempt}")
    return rows


def adjudicate_target(
    scenario: dict,
    target_id: str,
    rows: list[dict],
    truth: dict,
) -> dict:
    target_rows = [row for row in rows if row["target_id"] == target_id]
    supported = [row for row in target_rows if row["status"] == "INTERVAL_COMPUTED"]
    support_stops = sum(row["status"] == "SUPPORT_STOP" for row in target_rows)
    numerical_failures = sum(row["status"] not in {"INTERVAL_COMPUTED", "SUPPORT_STOP"} for row in target_rows)
    numerical_rate = numerical_failures / 2000.0
    numerical_pass = numerical_rate <= 0.01
    applicable = scenario["regime"] in ADJUDICABLE_REGIMES
    performance_eligible = len(supported) >= MIN_SUPPORTED_FOR_COVERAGE_GATE

    result = {
        "scenario_id": scenario["scenario_id"],
        "truth_structure": scenario["truth_structure"],
        "regime": scenario["regime"],
        "domain_classification": scenario["domain_classification"],
        "target_id": target_id,
        "truth": truth["truth"],
        "truth_mcse": truth["truth_mcse"],
        "truth_precision_pass": truth["truth_precision_pass"],
        "true_null_registered": truth["true_null_registered"],
        "truth_basis": truth["truth_basis"],
        "outer_attempts": 2000,
        "supported_attempts": len(supported),
        "support_stops": support_stops,
        "support_rate": len(supported) / 2000.0,
        "numerical_failures": numerical_failures,
        "numerical_failure_rate": numerical_rate,
        "numerical_pass": numerical_pass,
        "applicable_domain": applicable,
        "performance_eligible": performance_eligible,
        "minimum_supported_for_coverage_gate": MIN_SUPPORTED_FOR_COVERAGE_GATE,
        "bias": "",
        "bias_mcse": "",
        "rmse": "",
        "empirical_sd": "",
        "bias_upper95_in_empirical_sd": "",
        "bias_pass": "",
        "coverage": "",
        "coverage_wilson_lower": "",
        "coverage_wilson_upper": "",
        "coverage_pass": "",
        "type_i": "",
        "type_i_wilson_upper": "",
        "type_i_pass": "",
        "mean_interval_length": "",
        "decision": "",
    }

    if performance_eligible:
        point = np.array([float(row["point"]) for row in supported])
        lower = np.array([float(row["ci_lower"]) for row in supported])
        upper = np.array([float(row["ci_upper"]) for row in supported])
        errors = point - truth["truth"]
        bias = float(errors.mean())
        empirical_sd = float(point.std(ddof=1))
        bias_mcse = empirical_sd / math.sqrt(len(point))
        bias_scaled = (
            (abs(bias) + 1.96 * bias_mcse) / empirical_sd if empirical_sd > 0 else math.inf
        )
        covered = int(np.sum((lower <= truth["truth"]) & (truth["truth"] <= upper)))
        coverage_lower, coverage_upper = wilson(covered, len(point))
        coverage_pass = coverage_lower >= 0.925 and coverage_upper <= 0.975
        result.update(
            bias=bias,
            bias_mcse=bias_mcse,
            rmse=float(np.sqrt(np.mean(errors * errors))),
            empirical_sd=empirical_sd,
            bias_upper95_in_empirical_sd=bias_scaled,
            bias_pass=bias_scaled <= 0.10,
            coverage=covered / len(point),
            coverage_wilson_lower=coverage_lower,
            coverage_wilson_upper=coverage_upper,
            coverage_pass=coverage_pass,
            mean_interval_length=float(np.mean(upper - lower)),
        )
        if truth["true_null_registered"]:
            rejected = int(np.sum((lower > 0.0) | (upper < 0.0)))
            _, type_i_upper = wilson(rejected, len(point))
            result.update(
                type_i=rejected / len(point),
                type_i_wilson_upper=type_i_upper,
                type_i_pass=type_i_upper <= 0.075,
            )

    if not numerical_pass:
        decision = "HOLD_NUMERICAL_IMPLEMENTATION"
    elif not applicable:
        decision = "BOUNDARY_REPORTED"
    elif not performance_eligible:
        decision = "HOLD_SUPPORT_LIMITED"
    else:
        checks = [truth["truth_precision_pass"], result["bias_pass"], result["coverage_pass"]]
        if truth["true_null_registered"]:
            checks.append(result["type_i_pass"])
        decision = "PASS_TARGET_SCENARIO" if all(checks) else "HOLD_TARGET_SCENARIO"
    result["decision"] = decision
    return result


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def adjudicate(run_root: Path, output_dir: Path, repo_root: Path = REPO_ROOT) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Adjudication output must be new: {output_dir}")
    bound = binding(repo_root)
    run_binding = json.loads((run_root / "run_binding.json").read_text(encoding="utf-8"))
    if run_binding != bound:
        raise RuntimeError("Full-G2 output binding does not match the current frozen implementation")
    freeze = repo_root / FREEZE_DIR.relative_to(REPO_ROOT)
    prefit = repo_root / PREFIT_DIR.relative_to(REPO_ROOT)
    truth = load_truth(freeze / "04_G2_TRUTH_TABLE.csv")
    scenario_rows = scenarios(prefit / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv")
    target_results = []
    accounting = []
    for scenario in scenario_rows:
        rows = load_scenario_rows(run_root, scenario["scenario_id"], bound["binding_sha256"])
        statuses = {}
        for row in rows:
            statuses.setdefault(int(row["attempt_id"]), row["status"])
        accounting.append(
            {
                "scenario_id": scenario["scenario_id"],
                "regime": scenario["regime"],
                "outer_attempts": 2000,
                "interval_computed": sum(v == "INTERVAL_COMPUTED" for v in statuses.values()),
                "support_stops": sum(v == "SUPPORT_STOP" for v in statuses.values()),
                "numerical_failures": sum(v not in {"INTERVAL_COMPUTED", "SUPPORT_STOP"} for v in statuses.values()),
            }
        )
        for target in TARGETS:
            target_results.append(adjudicate_target(scenario, target, rows, truth[(scenario["scenario_id"], target)]))

    target_unlock = {}
    for target in TARGETS:
        required = [
            row for row in target_results if row["target_id"] == target and row["applicable_domain"]
        ]
        if len(required) != 15:
            raise RuntimeError(f"Unexpected applicable-domain count for {target}: {len(required)}")
        target_unlock[target] = all(row["decision"] == "PASS_TARGET_SCENARIO" for row in required)
    overall_pass = all(target_unlock.values())
    result = {
        "decision": "PASS_G2_APPLICABLE_DOMAIN" if overall_pass else "HOLD_G2_APPLICABLE_DOMAIN",
        "binding_sha256": bound["binding_sha256"],
        "full_grid_complete": True,
        "target_scenario_rows": len(target_results),
        "adjudicable_target_scenario_rows": sum(row["applicable_domain"] for row in target_results),
        "boundary_target_scenario_rows": sum(not row["applicable_domain"] for row in target_results),
        "target_unlock_recommendation": target_unlock,
        "recommended_for_post_G2_unlock_review": overall_pass,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "post_G2_review_required": True,
        "boundary_policy": "R1 and R3 remain mandatory reported stress domains but do not enter the applicable-domain conjunction",
        "simultaneous_confidence_claim": False,
        "submission": "HOLD",
        "WP4": "HOLD_CONDITIONAL",
    }
    output_dir.mkdir(parents=True)
    _write_csv(output_dir / "01_G2_ATTEMPT_ACCOUNTING.csv", accounting)
    _write_csv(output_dir / "02_G2_TARGET_SCENARIO_ADJUDICATION.csv", target_results)
    (output_dir / "03_G2_FINAL_DECISION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(adjudicate(args.run_root.resolve(), args.output_dir.resolve()), indent=2))
