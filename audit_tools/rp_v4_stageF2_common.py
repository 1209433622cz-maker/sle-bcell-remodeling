"""Fail-closed authorization and integrity controls for RP v4 Stage F2."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy
import statsmodels


REPO_ROOT = Path(__file__).resolve().parents[1]
SEED_BASE = 2026101004
QUALIFICATION_STAGE = 132
FINAL_OUTER_STAGE = 141
FINAL_TRUTH_STAGE = 142
AUTHOR_NAMES = ("Zhi Chen", "Teng Qi")

REQUIRED_BINDING_PATHS = {
    "audit_tools/rp_v4_stageF2_common.py",
    "audit_tools/rp_v4_stageF2_generator.py",
    "audit_tools/rp_v4_stageF2_truth.py",
    "audit_tools/rp_v4_stageF2_runner.py",
    "audit_tools/rp_v4_stageF2_adjudicator.py",
    "audit_tools/rp_v4_stageF2_adjudicate_run.py",
    "audit_tools/rp_v4_stageF2_preflight.py",
    "audit_tools/rp_v4_stageF2_freeze.py",
    "audit_tools/test_rp_v4_stageF2.py",
    "audit_tools/run_rp_v4_stageF2_preflight.ps1",
    "audit_tools/rp_v4_g2c_truth.py",
    "audit_tools/rp_v4_g2c_hc3t.py",
    "audit_tools/rp_v4_g2c_generator.py",
    "audit_tools/rp_v3_g2_estimation.py",
    "audit_tools/rp_v3_g2b_studentized.py",
    "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json",
    "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/05_G2C_FINAL_DGP_REGISTRY.csv",
    "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/06_G2C_FINAL_SEED_AND_COMPUTE_CONTRACT.json",
    "phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/02_G2_CALIBRATION_MODEL.json",
    "phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/04_G2_TRUTH_TABLE.csv",
}


@dataclass(frozen=True)
class ExecutionAuthorization:
    stage: int
    purpose: str
    final: bool
    authorization_sha256: str | None = None
    binding_manifest_sha256: str | None = None
    runtime_receipt_sha256: str | None = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
    ) + "\n"


def atomic_write_text(path: Path, text: str) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    if partial.exists():
        raise RuntimeError(f"Unclean partial file: {partial}")
    with partial.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.replace(partial, path)


def read_json(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def qualification_authorization(purpose: str) -> ExecutionAuthorization:
    if purpose not in {"outer", "truth"}:
        raise ValueError("Unknown qualification purpose")
    return ExecutionAuthorization(
        stage=QUALIFICATION_STAGE,
        purpose=purpose,
        final=False,
    )


def verify_binding_manifest(path: Path) -> str:
    manifest_path = Path(path).resolve()
    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or set(rows[0]) != {"path", "bytes", "sha256"}:
        raise ValueError("Invalid Stage F2 binding manifest schema")
    paths = [row["path"] for row in rows]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate binding manifest path")
    missing = sorted(REQUIRED_BINDING_PATHS.difference(paths))
    if missing:
        raise ValueError(f"Binding manifest omits required files: {missing}")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe binding manifest path")
        source = REPO_ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(f"Bound file missing: {relative.as_posix()}")
        if source.stat().st_size != int(row["bytes"]):
            raise ValueError(f"Bound file size drift: {relative.as_posix()}")
        if sha256_file(source) != row["sha256"].lower():
            raise ValueError(f"Bound file hash drift: {relative.as_posix()}")
    return sha256_file(manifest_path)


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def require_clean_worktree() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        raise PermissionError("Final execution requires a clean Git worktree")


def runtime_identity() -> dict:
    executable = Path(sys.executable).resolve()
    return {
        "python_executable": str(executable),
        "python_executable_sha256": sha256_file(executable),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "statsmodels": statsmodels.__version__,
    }


def verify_runtime_qualification(path: Path, manifest_sha: str) -> str:
    receipt_path = Path(path).resolve()
    receipt = read_json(receipt_path)
    if receipt.get("schema") != "RP_V4_STAGE_F2_WINDOWS_QUALIFICATION_1.0":
        raise PermissionError("Wrong qualified-runtime receipt schema")
    if receipt.get("binding_manifest_sha256") != manifest_sha:
        raise PermissionError("Qualified runtime does not bind this source manifest")
    expected = runtime_identity()
    for key, observed in expected.items():
        registered = receipt.get(key)
        if key == "python_executable" and os.name == "nt":
            if str(registered).casefold() != str(observed).casefold():
                raise PermissionError("Python executable differs from qualified runtime")
        elif registered != observed:
            raise PermissionError(f"Runtime identity drift: {key}")
    if receipt.get("stage141_started") is not False or receipt.get("stage142_started") is not False:
        raise PermissionError("Qualification receipt unexpectedly consumed final streams")
    return sha256_file(receipt_path)


def authorize_final(
    *,
    purpose: str,
    authorization_path: Path,
    binding_manifest_path: Path,
    runtime_qualification_path: Path,
) -> ExecutionAuthorization:
    if purpose not in {"outer", "truth"}:
        raise ValueError("Unknown final authorization purpose")
    authorization_path = Path(authorization_path).resolve()
    authorization = read_json(authorization_path)
    manifest_sha = verify_binding_manifest(binding_manifest_path)
    runtime_sha = verify_runtime_qualification(
        runtime_qualification_path, manifest_sha
    )
    required_true = {
        "author_contract_approved",
        "single_estimand_delta_profile",
        "single_method_OLS_HC3_t64",
        "fixed_40_scenarios_4000_attempts_each",
        "fixed_seed_base_2026101004_stage141_truth142",
        "fixed_truth_precision_and_acceptance_thresholds",
        "no_replenishment_or_posthoc_scenario_removal",
        "failure_closes_branch_no_G2D",
        "final_G2C_does_not_unlock_real_outcomes_automatically",
        "clean_worktree_required",
        "exact_qualified_runtime_required",
        "complete_payload_hash_sealing_required",
        "GO_FOR_FULL_SYNTHETIC_G2C",
    }
    if authorization.get("schema") != "RP_V4_STAGE_G_EXACT_CODE_GO_1.0":
        raise PermissionError("Exact-code GO schema is absent")
    if any(authorization.get(key) is not True for key in required_true):
        raise PermissionError("Full synthetic G2C GO is not complete")
    if tuple(authorization.get("approved_by", [])) != AUTHOR_NAMES:
        raise PermissionError("Both frozen authors must approve exact code")
    if not authorization.get("approved_at"):
        raise PermissionError("Exact-code GO timestamp is absent")
    if authorization.get("code_binding_manifest_sha256") != manifest_sha:
        raise PermissionError("Exact-code GO does not bind this manifest")
    if authorization.get("qualified_runtime_receipt_sha256") != runtime_sha:
        raise PermissionError("Exact-code GO does not bind this runtime receipt")
    if authorization.get("binding_git_commit") != git_head():
        raise PermissionError("Exact-code GO does not bind current Git HEAD")
    require_clean_worktree()
    purpose_key = (
        "authorize_outer_stage141" if purpose == "outer" else "authorize_truth_stage142"
    )
    if authorization.get(purpose_key) is not True:
        raise PermissionError(f"Exact-code GO does not authorize {purpose}")
    stage = FINAL_OUTER_STAGE if purpose == "outer" else FINAL_TRUTH_STAGE
    return ExecutionAuthorization(
        stage=stage,
        purpose=purpose,
        final=True,
        authorization_sha256=sha256_file(authorization_path),
        binding_manifest_sha256=manifest_sha,
        runtime_receipt_sha256=runtime_sha,
    )
