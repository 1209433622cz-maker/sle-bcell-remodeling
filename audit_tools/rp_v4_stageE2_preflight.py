"""Canonical Windows preflight checks for RP v4 Stage E2."""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
import statsmodels

try:
    from .rp_v4_stageE2_common import (
        AUTHOR_NAMES,
        atomic_write_text,
        authorize_final,
        read_json,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )
    from .rp_v4_stageE2_generator import load_inputs
except ImportError:
    from rp_v4_stageE2_common import (
        AUTHOR_NAMES,
        atomic_write_text,
        authorize_final,
        read_json,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )
    from rp_v4_stageE2_generator import load_inputs


AUTHOR_TRUE_FIELDS = {
    "author_contract_approved",
    "single_estimand_delta_profile",
    "single_method_OLS_HC3_t64",
    "fixed_40_scenarios_4000_attempts_each",
    "fixed_seed_base_2026101004_stage141_truth142",
    "fixed_truth_precision_and_acceptance_thresholds",
    "no_replenishment_or_posthoc_scenario_removal",
    "failure_closes_branch_no_G2D",
    "final_G2C_does_not_unlock_real_outcomes_automatically",
    "large_SRA_download_requires_separate_authorization",
}


def validate_author_contract(path: Path) -> dict:
    value = read_json(path)
    if value.get("schema") != "RP_V4_STAGE_E2_AUTHOR_CONTRACT_SIGNOFF_1.0":
        raise ValueError("Wrong author-contract signoff schema")
    if tuple(value.get("approved_by", [])) != AUTHOR_NAMES:
        raise ValueError("Both frozen authors are not recorded")
    if not value.get("approved_at"):
        raise ValueError("Author-contract timestamp missing")
    if any(value.get(field) is not True for field in AUTHOR_TRUE_FIELDS):
        raise ValueError("Author-contract approvals are incomplete")
    if value.get("GO_FOR_FULL_SYNTHETIC_G2C") is not False:
        raise ValueError("Stage E2 contract signoff must not contain final GO")
    return value


def validate_go_template(path: Path, manifest_sha: str) -> dict:
    value = read_json(path)
    if value.get("schema") != "RP_V4_STAGE_F_EXACT_CODE_GO_1.0":
        raise ValueError("Wrong exact-code GO template schema")
    if value.get("GO_FOR_FULL_SYNTHETIC_G2C") is not False:
        raise ValueError("Final GO template is unexpectedly enabled")
    if value.get("code_binding_manifest_sha256") != manifest_sha:
        raise ValueError("GO template does not name this code manifest")
    if value.get("binding_git_commit") is not None:
        raise ValueError("Unissued GO template must not pre-bind a commit")
    return value


def validate_qualification(
    outer_receipt_path: Path, truth_receipt_path: Path
) -> tuple[dict, dict]:
    outer = read_json(outer_receipt_path)
    truth = read_json(truth_receipt_path)
    if any(
        [
            outer.get("mode") != "qualification",
            outer.get("stage") != 132,
            outer.get("scenario_count") != 3,
            outer.get("attempts") != 24,
            outer.get("final_G2C_adjudicated") is not False,
            outer.get("real_effects_fitted") is not False,
            truth.get("mode") != "qualification",
            truth.get("stage") != 132,
            truth.get("scenario_count") != 3,
            truth.get("all_precision_pass") is not True,
            truth.get("final") is not False,
            truth.get("real_effects_fitted") is not False,
        ]
    ):
        raise ValueError("Qualification receipts do not satisfy Stage E2")
    return outer, truth


def run(
    *,
    registry_path: Path,
    calibration_model_path: Path,
    author_signoff_path: Path,
    go_template_path: Path,
    binding_manifest_path: Path,
    outer_receipt_path: Path,
    truth_receipt_path: Path,
) -> dict:
    load_inputs(registry_path, calibration_model_path)
    author = validate_author_contract(author_signoff_path)
    manifest_sha = verify_binding_manifest(binding_manifest_path)
    validate_go_template(go_template_path, manifest_sha)
    outer, truth = validate_qualification(outer_receipt_path, truth_receipt_path)
    final_refused = False
    try:
        authorize_final(
            purpose="outer",
            authorization_path=go_template_path,
            binding_manifest_path=binding_manifest_path,
        )
    except PermissionError:
        final_refused = True
    if not final_refused:
        raise RuntimeError("Final outer execution was not fail-closed")
    final_truth_refused = False
    try:
        authorize_final(
            purpose="truth",
            authorization_path=go_template_path,
            binding_manifest_path=binding_manifest_path,
        )
    except PermissionError:
        final_truth_refused = True
    if not final_truth_refused:
        raise RuntimeError("Final truth execution was not fail-closed")
    return {
        "schema": "RP_V4_STAGE_E2_WINDOWS_PREFLIGHT_1.0",
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "statsmodels": statsmodels.__version__,
        "author_contract_sha256": sha256_file(author_signoff_path),
        "approved_by": author["approved_by"],
        "binding_manifest_sha256": manifest_sha,
        "outer_qualification_receipt_sha256": sha256_file(outer_receipt_path),
        "truth_qualification_receipt_sha256": sha256_file(truth_receipt_path),
        "outer_qualification": outer,
        "truth_qualification": truth,
        "stage141_fail_closed_without_exact_code_go": final_refused,
        "stage142_fail_closed_without_exact_code_go": final_truth_refused,
        "stage141_started": False,
        "stage142_started": False,
        "real_outcomes_loaded": False,
        "full_synthetic_G2C_authorized": False,
        "decision": "PASS_STAGE_E2_WINDOWS_PREFLIGHT__HOLD_EXACT_CODE_GO",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--calibration-model", type=Path, required=True)
    parser.add_argument("--author-signoff", type=Path, required=True)
    parser.add_argument("--go-template", type=Path, required=True)
    parser.add_argument("--binding-manifest", type=Path, required=True)
    parser.add_argument("--outer-receipt", type=Path, required=True)
    parser.add_argument("--truth-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run(
                registry_path=arguments.registry,
                calibration_model_path=arguments.calibration_model,
                author_signoff_path=arguments.author_signoff,
                go_template_path=arguments.go_template,
                binding_manifest_path=arguments.binding_manifest,
                outer_receipt_path=arguments.outer_receipt,
                truth_receipt_path=arguments.truth_receipt,
            )
    text = stable_json(result)
    if arguments.output is not None:
        atomic_write_text(arguments.output, text)
    print(text, end="")
