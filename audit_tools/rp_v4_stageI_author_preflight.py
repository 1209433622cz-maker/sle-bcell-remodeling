#!/usr/bin/env python3
"""Prepare an unissued, commit-bound Stage I author decision packet."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
import statsmodels

try:
    from .rp_v4_stageI_real_delta_profile import execute
except ImportError:
    from rp_v4_stageI_real_delta_profile import execute


ROOT = Path(__file__).resolve().parents[1]
STAGE_H = ROOT / "phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit"
STAGE_F2 = ROOT / "phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening"
BINDING = STAGE_H / "01_REAL_INPUT_BINDING_MANIFEST.csv"
EXECUTION_SCRIPT = ROOT / "audit_tools/rp_v4_stageI_real_delta_profile.py"
RUNTIME_RECEIPT = STAGE_F2 / "03_WINDOWS_RUNTIME_QUALIFICATION.json"
AUTHORS = ["Zhi Chen", "Teng Qi"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def write_new(path: Path, text: str) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def require_clean_synchronized_main() -> str:
    if git("status", "--porcelain", "--untracked-files=all"):
        raise PermissionError("Author preflight requires a clean worktree")
    head = git("rev-parse", "HEAD")
    upstream = git("rev-parse", "@{u}")
    branch = git("branch", "--show-current")
    if branch != "main" or upstream != head:
        raise PermissionError("Author preflight requires synchronized main")
    return head


def runtime_identity() -> dict:
    executable = Path(sys.executable).resolve()
    return {
        "python_executable": str(executable),
        "python_executable_sha256": sha256_file(executable),
        "python_version": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "statsmodels": statsmodels.__version__,
    }


def verify_stage_h_integrity() -> None:
    with (STAGE_H / "11_INTEGRITY_MANIFEST.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 10:
        raise ValueError("Stage H integrity manifest cardinality changed")
    for row in rows:
        path = STAGE_H / row["path"]
        if not path.is_file() or path.stat().st_size != int(row["bytes"]) or sha256_file(path) != row["sha256"]:
            raise ValueError(f"Stage H integrity failure: {row['path']}")


def build_draft(commit: str, binding_sha: str, script_sha: str) -> dict:
    return {
        "schema": "RP_V4_STAGE_I_REAL_DELTA_PROFILE_GO_1.0",
        "approved_by": [],
        "approved_at": None,
        "GO_FOR_SINGLE_REAL_DELTA_PROFILE": False,
        "approve_single_estimand_delta_profile": False,
        "approve_single_method_OLS_HC3_t64": False,
        "approve_exact_68_donor_31_37_design": False,
        "approve_write_once_result_and_no_preview": False,
        "acknowledge_association_not_causal_mediation": False,
        "acknowledge_no_other_target_external_outcome_or_submission_unlock": False,
        "input_binding_manifest_sha256": binding_sha,
        "execution_script_sha256": script_sha,
        "binding_git_commit": commit,
        "qualified_python_executable": "D:/bioinfor/python.exe",
    }


def run(output: Path, *, enforce_clean: bool = True) -> dict:
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("Use a new author-preflight output directory")
    head = require_clean_synchronized_main() if enforce_clean else git("rev-parse", "HEAD")

    gate = read_json(STAGE_H / "08_STAGE_H_GATE_STATUS.json")
    if gate.get("decision") != "PASS_STAGE_H_EFFECT_BLIND_APPLICABILITY__HOLD_STAGE_I_AUTHOR_SIGNOFF":
        raise ValueError("Stage H gate is not eligible for author review")
    if gate.get("real_response_loaded") is not False or gate.get("real_disease_coefficient_fitted") is not False:
        raise ValueError("Stage H effect firewall is not intact")
    verify_stage_h_integrity()
    binding_sha = sha256_file(BINDING)
    script_sha = sha256_file(EXECUTION_SCRIPT)
    if binding_sha != gate.get("input_binding_manifest_sha256") or script_sha != gate.get("execution_script_sha256"):
        raise ValueError("Stage H exact hashes drifted")

    qualified = read_json(RUNTIME_RECEIPT)
    observed_runtime = runtime_identity()
    for field, value in observed_runtime.items():
        expected = qualified.get(field)
        if field == "python_executable":
            if str(expected).casefold() != str(value).casefold():
                raise ValueError("Qualified Python path drift")
        elif expected != value:
            raise ValueError(f"Qualified runtime drift: {field}")

    output.mkdir(parents=True)
    baseline = {
        "schema": "RP_V4_STAGE_I_POST_STAGE_H_BASELINE_1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "binding_git_commit": head,
        "branch": "main",
        "upstream_synchronized": bool(enforce_clean),
        "stage_H_gate_sha256": sha256_file(STAGE_H / "08_STAGE_H_GATE_STATUS.json"),
        "input_binding_manifest_sha256": binding_sha,
        "execution_script_sha256": script_sha,
        "qualified_runtime_receipt_sha256": sha256_file(RUNTIME_RECEIPT),
        "runtime": observed_runtime,
        "real_response_loaded": False,
        "real_disease_coefficient_fitted": False,
    }
    write_new(output / "01_POST_STAGE_H_EXACT_BASELINE.json", stable_json(baseline))
    draft = build_draft(head, binding_sha, script_sha)
    write_new(output / "02_STAGE_I_AUTHOR_GO_DRAFT.json", stable_json(draft))

    checks = [
        {"check": "stage_H_gate", "pass": True, "detail": gate["decision"]},
        {"check": "stage_H_integrity", "pass": True, "detail": "10/10 controlled files"},
        {"check": "input_binding_hash", "pass": True, "detail": binding_sha},
        {"check": "execution_script_hash", "pass": True, "detail": script_sha},
        {"check": "qualified_runtime", "pass": True, "detail": observed_runtime["python_executable"]},
        {"check": "git_commit_bound", "pass": True, "detail": head},
        {"check": "real_response_loaded", "pass": True, "detail": "false"},
        {"check": "real_coefficient_fitted", "pass": True, "detail": "false"},
        {"check": "author_GO_issued", "pass": False, "detail": "awaiting explicit approval by Zhi Chen and Teng Qi"},
    ]
    write_csv(output / "03_STAGE_I_AUTHOR_PREFLIGHT_CHECKS.csv", checks, ["check", "pass", "detail"])

    forbidden_output = output / "forbidden_unsigned_result"
    try:
        execute(output / "02_STAGE_I_AUTHOR_GO_DRAFT.json", BINDING, forbidden_output)
    except PermissionError as error:
        fail_closed = {
            "schema": "RP_V4_STAGE_I_UNSIGNED_FAIL_CLOSED_1.0",
            "pass": True,
            "exception": type(error).__name__,
            "detail": str(error),
            "result_directory_created": forbidden_output.exists(),
            "real_response_loaded": False,
            "real_disease_coefficient_fitted": False,
        }
    else:
        raise AssertionError("Unsigned Stage I draft did not fail closed")
    if forbidden_output.exists():
        raise AssertionError("Unsigned Stage I created a result directory")
    write_new(output / "04_UNSIGNED_FAIL_CLOSED_RECEIPT.json", stable_json(fail_closed))

    decision_form = f"""# RP v4 Stage I exact author decision form\n\n**Bound Git commit:** `{head}`  \n**Input manifest SHA-256:** `{binding_sha}`  \n**Execution script SHA-256:** `{script_sha}`  \n**Qualified runtime:** `D:\\bioinfor\\python.exe`\n\nBefore Stage I can run, both Zhi Chen and Teng Qi must explicitly approve all of the following:\n\n1. One estimand only: `delta_profile`.\n2. One method only: donor-level OLS, HC3 variance and two-sided t(64) interval.\n3. Exact frozen support: 68 donors, 31 controls and 37 managed-SLE donors.\n4. One write-once execution with no preview, fallback, donor removal, threshold change or selective rerun.\n5. Interpretation as an association difference between measurement/mixing rules, not causal mediation or a cell-intrinsic disease effect.\n6. No automatic unlock of the other nine historical targets, external outcomes, WP4, manuscript replacement or submission.\n\nThe current JSON draft is intentionally unsigned and cannot execute.\n"""
    write_new(output / "05_STAGE_I_AUTHOR_DECISION_FORM.md", decision_form)
    status = {
        "schema": "RP_V4_STAGE_I_AUTHOR_PREFLIGHT_GATE_1.0",
        "decision": "READY_FOR_EXPLICIT_TWO_AUTHOR_DECISION__STAGE_I_NOT_AUTHORIZED",
        "binding_git_commit": head,
        "preflight_checks_passed": 8,
        "preflight_checks_total": 8,
        "author_GO_issued": False,
        "stage_I_execution_authorized": False,
        "real_response_loaded": False,
        "real_disease_coefficient_fitted": False,
        "next_if_approved": "issue exact GO in ignored local evidence area, then run one write-once delta_profile fit",
        "next_if_not_approved": "retain Stage G synthetic methods result and close real execution",
    }
    write_new(output / "06_STAGE_I_AUTHOR_PREFLIGHT_GATE.json", stable_json(status))
    review = f"""# RP v4 Stage I author-decision preflight review\n\n## Decision\n\n`{status['decision']}`\n\nThe post-Stage-H baseline is synchronized at commit `{head}`. Stage H integrity, the input manifest, execution script and qualified Windows runtime all match their frozen hashes. The unissued draft was passed to the real-result runner and failed before response construction; no result directory was created.\n\nThis packet is not author approval. It prepares a precise object for the two authors to approve or reject. Stage I remains locked until the human user explicitly confirms approval on behalf of both named authors and all six conditions in `05_STAGE_I_AUTHOR_DECISION_FORM.md`.\n\nExternal outcomes, WP4, manuscript changes and submission remain out of scope.\n"""
    write_new(output / "07_STAGE_I_AUTHOR_PREFLIGHT_ADVISOR_REVIEW.md", review)
    controlled = sorted(path for path in output.iterdir() if path.is_file())
    rows = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in controlled]
    write_csv(output / "08_INTEGRITY_MANIFEST.csv", rows, ["path", "bytes", "sha256"])
    print(stable_json(status), end="")
    return status


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
