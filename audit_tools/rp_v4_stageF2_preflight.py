"""Canonical Windows qualification checks for RP v4 Stage F2."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

try:
    from .rp_v4_stageF2_common import (
        AUTHOR_NAMES,
        REPO_ROOT,
        atomic_write_text,
        read_json,
        runtime_identity,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )
    from .rp_v4_stageF2_generator import load_inputs
    from .rp_v4_stageF2_runner import verify_outer_payload
    from .rp_v4_stageF2_truth import verify_truth_payload
except ImportError:
    from rp_v4_stageF2_common import (
        AUTHOR_NAMES,
        REPO_ROOT,
        atomic_write_text,
        read_json,
        runtime_identity,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )
    from rp_v4_stageF2_generator import load_inputs
    from rp_v4_stageF2_runner import verify_outer_payload
    from rp_v4_stageF2_truth import verify_truth_payload


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
        raise ValueError("Scientific contract signoff must not contain final GO")
    return value


def validate_go_draft(path: Path, manifest_sha: str) -> dict:
    value = read_json(path)
    if value.get("schema") != "RP_V4_STAGE_G_EXACT_CODE_GO_1.0":
        raise ValueError("Wrong exact-code GO draft schema")
    if value.get("GO_FOR_FULL_SYNTHETIC_G2C") is not False:
        raise ValueError("Final GO draft is unexpectedly enabled")
    if value.get("code_binding_manifest_sha256") != manifest_sha:
        raise ValueError("GO draft does not name this code manifest")
    if value.get("binding_git_commit") is not None:
        raise ValueError("Unissued GO draft must not pre-bind a commit")
    if value.get("qualified_runtime_receipt_sha256") is not None:
        raise ValueError("Preflight GO draft must not pre-bind its future receipt")
    return value


def _worktree_clean() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return not bool(result.stdout.strip())


def run(
    *,
    registry_path: Path,
    calibration_model_path: Path,
    author_signoff_path: Path,
    go_draft_path: Path,
    binding_manifest_path: Path,
    outer_root: Path,
    truth_root: Path,
    unit_and_regression_tests: str,
    negative_tamper_tests: str,
) -> dict:
    load_inputs(registry_path, calibration_model_path)
    author = validate_author_contract(author_signoff_path)
    manifest_sha = verify_binding_manifest(binding_manifest_path)
    validate_go_draft(go_draft_path, manifest_sha)
    outer = verify_outer_payload(outer_root)
    truth = verify_truth_payload(
        truth_root,
        registry_path=registry_path,
        calibration_model_path=calibration_model_path,
    )
    if any(
        [
            outer.get("mode") != "qualification",
            outer.get("stage") != 132,
            outer.get("scenario_count") != 3,
            outer.get("attempts") != 24,
            outer.get("chunk_count") != 3,
            outer.get("final") is not False,
            outer.get("real_effects_fitted") is not False,
            truth.get("mode") != "qualification",
            truth.get("stage") != 132,
            truth.get("scenario_count") != 3,
            truth.get("checkpoint_count") != 48,
            truth.get("all_precision_pass") is not True,
            truth.get("all_independent_score_crosschecks_pass") is not True,
            truth.get("final") is not False,
            truth.get("real_effects_fitted") is not False,
        ]
    ):
        raise ValueError("Qualification receipts do not satisfy Stage F2")
    return {
        "schema": "RP_V4_STAGE_F2_WINDOWS_QUALIFICATION_1.0",
        **runtime_identity(),
        "author_contract_sha256": sha256_file(author_signoff_path),
        "approved_by": author["approved_by"],
        "binding_manifest_sha256": manifest_sha,
        "outer_contract_sha256": outer["contract_sha256"],
        "outer_chunk_manifest_sha256": outer["chunk_manifest_sha256"],
        "outer_accounting_sha256": outer["accounting_sha256"],
        "outer_receipt_sha256": sha256_file(outer_root / "03_RUN_RECEIPT.json"),
        "truth_contract_sha256": truth["contract_sha256"],
        "truth_scenario_manifest_sha256": truth["scenario_manifest_sha256"],
        "truth_csv_sha256": truth["truth_csv_sha256"],
        "truth_receipt_sha256": sha256_file(truth_root / "03_TRUTH_RECEIPT.json"),
        "truth_maximum_mcse_over_typical_se": truth[
            "maximum_mcse_over_typical_se"
        ],
        "outer_qualification": outer,
        "truth_qualification": truth,
        "unit_and_regression_tests": unit_and_regression_tests,
        "negative_tamper_tests": negative_tamper_tests,
        "worktree_clean_during_development_qualification": _worktree_clean(),
        "clean_worktree_enforced_at_final_authorization": True,
        "stage141_fail_closed_without_exact_code_go": True,
        "stage142_fail_closed_without_exact_code_go": True,
        "stage141_started": False,
        "stage142_started": False,
        "real_outcomes_loaded": False,
        "full_synthetic_G2C_authorized": False,
        "decision": "PASS_STAGE_F2_WINDOWS_QUALIFICATION__HOLD_POST_COMMIT_EXACT_CODE_GO",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--calibration-model", type=Path, required=True)
    parser.add_argument("--author-signoff", type=Path, required=True)
    parser.add_argument("--go-draft", type=Path, required=True)
    parser.add_argument("--binding-manifest", type=Path, required=True)
    parser.add_argument("--outer-root", type=Path, required=True)
    parser.add_argument("--truth-root", type=Path, required=True)
    parser.add_argument("--unit-and-regression-tests", required=True)
    parser.add_argument("--negative-tamper-tests", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    result = run(
        registry_path=arguments.registry,
        calibration_model_path=arguments.calibration_model,
        author_signoff_path=arguments.author_signoff,
        go_draft_path=arguments.go_draft,
        binding_manifest_path=arguments.binding_manifest,
        outer_root=arguments.outer_root,
        truth_root=arguments.truth_root,
        unit_and_regression_tests=arguments.unit_and_regression_tests,
        negative_tamper_tests=arguments.negative_tamper_tests,
    )
    atomic_write_text(arguments.output, stable_json(result))
    print(stable_json(result), end="")
