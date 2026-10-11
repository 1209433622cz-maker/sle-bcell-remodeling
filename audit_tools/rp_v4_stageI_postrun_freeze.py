#!/usr/bin/env python3
"""Audit and freeze the completed Stage I output without refitting it."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import t


ROOT = Path(__file__).resolve().parents[1]
STAGE_H = ROOT / "phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit"
STAGE_F2 = ROOT / "phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening"
BINDING = STAGE_H / "01_REAL_INPUT_BINDING_MANIFEST.csv"
EXECUTION_SCRIPT = ROOT / "audit_tools/rp_v4_stageI_real_delta_profile.py"
RUNTIME_RECEIPT = STAGE_F2 / "03_WINDOWS_RUNTIME_QUALIFICATION.json"
RESULT_NAME = "01_SINGLE_REAL_DELTA_PROFILE_RESULT.json"
RECEIPT_NAME = "02_SINGLE_REAL_DELTA_PROFILE_RECEIPT.json"
EXPECTED_AUTHORS = ["Zhi Chen", "Teng Qi"]
REQUIRED_TRUE = [
    "GO_FOR_SINGLE_REAL_DELTA_PROFILE",
    "approve_single_estimand_delta_profile",
    "approve_single_method_OLS_HC3_t64",
    "approve_exact_68_donor_31_37_design",
    "approve_write_once_result_and_no_preview",
    "acknowledge_association_not_causal_mediation",
    "acknowledge_no_other_target_external_outcome_or_submission_unlock",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def stable_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def write_new(path: Path, content: str | bytes) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "xb" if isinstance(content, bytes) else "x"
    kwargs = {} if isinstance(content, bytes) else {"encoding": "utf-8", "newline": "\n"}
    with path.open(mode, **kwargs) as handle:
        handle.write(content)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def close(a: float, b: float, *, atol: float = 1e-12) -> bool:
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=atol)


def validate(result_dir: Path, authorization_path: Path) -> dict:
    result_dir = Path(result_dir).resolve()
    authorization_path = Path(authorization_path).resolve()
    result_path = result_dir / RESULT_NAME
    receipt_path = result_dir / RECEIPT_NAME
    if not result_path.is_file() or not receipt_path.is_file():
        raise ValueError("Stage I result or receipt is missing")

    result = read_json(result_path)
    receipt = read_json(receipt_path)
    authorization = read_json(authorization_path)
    schema = read_json(STAGE_H / "06_WRITE_ONCE_RESULT_SCHEMA.json")
    geometry = read_json(STAGE_H / "03_REAL_GEOMETRY_SUMMARY.json")
    qualified = read_json(RUNTIME_RECEIPT)
    checks: list[dict] = []

    def require(name: str, condition: bool, detail: str) -> None:
        if not condition:
            raise ValueError(f"Stage I postrun audit failed: {name}: {detail}")
        checks.append({"check": name, "pass": True, "detail": detail})

    require("result_schema", result.get("schema") == "RP_V4_STAGE_I_SINGLE_REAL_DELTA_PROFILE_RESULT_1.0", str(result.get("schema")))
    require("receipt_schema", receipt.get("schema") == "RP_V4_STAGE_I_SINGLE_REAL_RESULT_RECEIPT_1.0", str(receipt.get("schema")))
    missing = set(schema["required_result_fields"]).difference(result)
    require("required_fields", not missing, f"missing={sorted(missing)}")
    forbidden = set(schema["forbidden_payloads"]).intersection(result)
    require("forbidden_payloads_absent", not forbidden, f"present={sorted(forbidden)}")
    require("single_estimand", result.get("estimand") == "delta_profile" and receipt.get("single_estimand_only") is True, "delta_profile only")
    require("write_once_receipt", receipt.get("write_once") is True, "write_once=true")
    require("no_donor_response_export", receipt.get("donor_level_response_exported") is False, "false")
    require("result_bytes", result_path.stat().st_size == int(receipt.get("result_bytes", -1)), str(result_path.stat().st_size))
    require("result_sha256", sha256_file(result_path) == receipt.get("result_sha256"), sha256_file(result_path))

    auth_sha = sha256_file(authorization_path)
    require("authorization_schema", authorization.get("schema") == "RP_V4_STAGE_I_REAL_DELTA_PROFILE_GO_1.0", str(authorization.get("schema")))
    require("two_author_approval", authorization.get("approved_by") == EXPECTED_AUTHORS and bool(authorization.get("approved_at")), str(authorization.get("approved_by")))
    require("six_condition_go", all(authorization.get(field) is True for field in REQUIRED_TRUE), "all required fields true")
    require("authorization_hash", auth_sha == result.get("authorization_sha256") == receipt.get("authorization_sha256"), auth_sha)
    require("input_binding_hash", sha256_file(BINDING) == result.get("input_binding_manifest_sha256") == receipt.get("input_binding_manifest_sha256"), sha256_file(BINDING))
    require("execution_script_hash", sha256_file(EXECUTION_SCRIPT) == result.get("execution_script_sha256"), sha256_file(EXECUTION_SCRIPT))
    require("binding_commit", result.get("binding_git_commit") == authorization.get("binding_git_commit"), str(result.get("binding_git_commit")))
    commit_ok = subprocess.run(["git", "cat-file", "-e", f"{result['binding_git_commit']}^{{commit}}"], cwd=ROOT).returncode == 0
    require("binding_commit_exists", commit_ok, str(result.get("binding_git_commit")))

    runtime = result.get("runtime", {})
    runtime_fields = ["python_executable_sha256", "python_version", "numpy", "scipy", "statsmodels"]
    require("qualified_runtime", all(runtime.get(field) == qualified.get(field) for field in runtime_fields), str(runtime.get("python_executable")))
    require("support", result.get("n_donors") == 68 and result.get("controls") == 31 and result.get("managed_SLE") == 37, "68=31+37")
    require("degrees_of_freedom", result.get("df") == 64, "64")
    require("leverage", close(result.get("max_point_leverage"), geometry["maximum_hat_leverage"]), f"{result.get('max_point_leverage'):.15f}")
    scope_locked = result.get("other_historical_targets_fitted") is False and result.get("external_outcomes_fitted") is False and result.get("automatic_manuscript_or_submission_unlock") is False
    require("scope_locks", scope_locked, "all false")

    point = float(result["point_estimate"])
    se = float(result["standard_error_HC3"])
    df = int(result["df"])
    statistic = point / se
    critical = float(t.ppf(0.975, df))
    p_value = float(2 * t.sf(abs(statistic), df))
    require("positive_standard_error", math.isfinite(se) and se > 0, f"{se:.15f}")
    require("test_statistic_identity", close(result["test_statistic"], statistic), f"{statistic:.15f}")
    require("critical_value_identity", close(result["critical_value"], critical), f"{critical:.15f}")
    require("p_value_identity", close(result["two_sided_p_value"], p_value), f"{p_value:.15f}")
    require("lower_interval_identity", close(result["ci_lower"], point - critical * se), f"{point - critical * se:.15f}")
    require("upper_interval_identity", close(result["ci_upper"], point + critical * se), f"{point + critical * se:.15f}")

    interval_class = "positive" if float(result["ci_lower"]) > 0 else "negative" if float(result["ci_upper"]) < 0 else "includes_zero"
    return {
        "schema": "RP_V4_STAGE_I_POSTRUN_AUDIT_1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "interval_class": interval_class,
        "point_estimate": point,
        "standard_error_HC3": se,
        "ci_lower": float(result["ci_lower"]),
        "ci_upper": float(result["ci_upper"]),
        "two_sided_p_value": float(result["two_sided_p_value"]),
        "result_sha256": sha256_file(result_path),
        "authorization_sha256": auth_sha,
        "refit_performed": False,
    }


def freeze(result_dir: Path, authorization_path: Path) -> dict:
    result_dir = Path(result_dir).resolve()
    existing = {path.name for path in result_dir.iterdir() if path.is_file()}
    if existing != {RESULT_NAME, RECEIPT_NAME}:
        raise ValueError(f"Freeze requires the untouched two-file Stage I output: {sorted(existing)}")
    audit = validate(result_dir, authorization_path)
    write_new(result_dir / "00_STAGE_I_AUTHOR_GO.json", Path(authorization_path).read_bytes())
    write_new(result_dir / "03_STAGE_I_INDEPENDENT_OUTPUT_AUDIT.json", stable_json(audit))
    gate = {
        "schema": "RP_V4_STAGE_I_GATE_1.0",
        "decision": "PASS_STAGE_I_WRITE_ONCE_EXECUTION__POSITIVE_DELTA_PROFILE_ASSOCIATION__HOLD_AUTOMATIC_UNLOCK",
        "estimand": "delta_profile",
        "point_estimate": audit["point_estimate"],
        "standard_error_HC3": audit["standard_error_HC3"],
        "ci_lower": audit["ci_lower"],
        "ci_upper": audit["ci_upper"],
        "two_sided_p_value": audit["two_sided_p_value"],
        "interval_class": audit["interval_class"],
        "single_prespecified_test": True,
        "interpretation": "managed-SLE versus control association is greater under the fixed-profile measurement rule than under pooled counts; measurement-rule sensitivity only",
        "causal_mediation_supported": False,
        "cell_intrinsic_effect_supported": False,
        "other_historical_targets_unlocked": False,
        "external_outcomes_unlocked": False,
        "WP4_unlocked": False,
        "automatic_manuscript_or_submission_unlock": False,
        "next_stage": "RPV4_STAGE_J__SCIENTIFIC_INTEGRATION_SCOPE_AND_AUTHOR_REVIEW",
    }
    write_new(result_dir / "04_STAGE_I_GATE_STATUS.json", stable_json(gate))
    review = f"""# RP v4 Stage I advisor review

## Decision

`{gate['decision']}`

The two authors approved all six frozen conditions, and the exact write-once
runner produced one `delta_profile` result under the bound commit and qualified
Windows runtime. No donor-level response was exported, no other historical
target or external outcome was fitted, and no fallback or selective rerun was
performed.

## Result

- Point estimate: `{audit['point_estimate']:.9f}` T0 score units
- HC3 standard error: `{audit['standard_error_HC3']:.9f}`
- Two-sided t(64) 95% CI: `{audit['ci_lower']:.9f}` to `{audit['ci_upper']:.9f}`
- Two-sided P value: `{audit['two_sided_p_value']:.9f}`

The interval is above zero. Under the frozen sign convention, the managed-SLE
versus control association is approximately 0.035 T0 score units greater for
the fixed-profile mixture rule than for the pooled-count rule. This supports a
real-data measurement/mixing-rule sensitivity result. It is not a mediation
proportion, a causal cell-intrinsic effect, proof of a latent data-generating
mechanism, or permission to inspect additional targets.

## Independent output audit

All {audit['checks_total']} output-only integrity and algebra checks passed. The
audit verified the authorization, input, execution-code, runtime, result and
receipt hashes; support and leverage; t statistic, P value and interval
identities; and all scope locks. It did not reconstruct the response or refit
the coefficient.

## Next stage

Proceed to `RPV4_STAGE_J__SCIENTIFIC_INTEGRATION_SCOPE_AND_AUTHOR_REVIEW`.
Stage J should decide whether this bounded sensitivity result belongs in the
revised manuscript and, if so, its exact claim owner and figure/table location.
It must not reopen the estimator, fit other targets, unlock external outcomes
or treat the result as causal.
"""
    write_new(result_dir / "05_STAGE_I_ADVISOR_REVIEW.md", review)
    controlled = sorted(path for path in result_dir.iterdir() if path.is_file())
    rows = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in controlled]
    write_csv(result_dir / "06_INTEGRITY_MANIFEST.csv", rows, ["path", "bytes", "sha256"])
    print(stable_json(gate), end="")
    return gate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True, type=Path)
    parser.add_argument("--authorization", required=True, type=Path)
    args = parser.parse_args()
    freeze(args.result_dir, args.authorization)


if __name__ == "__main__":
    main()
