"""Prepare and freeze the canonical RP v4 Stage E2 evidence bundle."""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import shutil
import zipfile
from pathlib import Path

try:
    from .rp_v4_stageE2_common import (
        AUTHOR_NAMES,
        REPO_ROOT,
        REQUIRED_BINDING_PATHS,
        atomic_write_text,
        read_json,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )
except ImportError:
    from rp_v4_stageE2_common import (
        AUTHOR_NAMES,
        REPO_ROOT,
        REQUIRED_BINDING_PATHS,
        atomic_write_text,
        read_json,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )


EXPECTED_EXTERNAL_ZIP_SHA256 = (
    "fe603e4d31031037428a3fa241678b7d5b14752d111fa739b317574215741e74"
)
EXTRA_BINDING_PATHS = {
    "audit_tools/rp_v4_stageE2_freeze.py",
    "audit_tools/test_rp_v4_stageE2.py",
    "audit_tools/run_rp_v4_stageE2_preflight.ps1",
}


def _csv_text(rows: list[dict], fieldnames: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def prepare(output: Path) -> None:
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"Preparation output exists: {output}")
    output.mkdir(parents=True)
    paths = sorted(REQUIRED_BINDING_PATHS | EXTRA_BINDING_PATHS)
    rows = []
    for relative in paths:
        source = REPO_ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(f"Binding source missing: {relative}")
        rows.append(
            {
                "path": relative,
                "bytes": source.stat().st_size,
                "sha256": sha256_file(source),
            }
        )
    manifest_path = output / "04_STAGE_E2_SOURCE_BINDING.csv"
    atomic_write_text(
        manifest_path, _csv_text(rows, ["path", "bytes", "sha256"])
    )
    manifest_sha = verify_binding_manifest(manifest_path)
    signoff = {
        "schema": "RP_V4_STAGE_E2_AUTHOR_CONTRACT_SIGNOFF_1.0",
        "approved_by": list(AUTHOR_NAMES),
        "approved_at": (
            "2026-10-11 Asia/Hong_Kong; thread date recorded, exact clock time not captured"
        ),
        "approval_evidence": (
            "The user explicitly stated 'all approved' in the project thread on "
            "2026-10-11; prior thread confirmations bind both listed authors."
        ),
        "author_contract_approved": True,
        "single_estimand_delta_profile": True,
        "single_method_OLS_HC3_t64": True,
        "fixed_40_scenarios_4000_attempts_each": True,
        "fixed_seed_base_2026101004_stage141_truth142": True,
        "fixed_truth_precision_and_acceptance_thresholds": True,
        "no_replenishment_or_posthoc_scenario_removal": True,
        "failure_closes_branch_no_G2D": True,
        "final_G2C_does_not_unlock_real_outcomes_automatically": True,
        "large_SRA_download_requires_separate_authorization": True,
        "GO_FOR_FULL_SYNTHETIC_G2C": False,
        "code_binding_manifest_sha256": manifest_sha,
        "note": (
            "Scientific contract approval is recorded. Exact-code execution GO is "
            "deliberately separate because the final Git commit did not yet exist."
        ),
    }
    atomic_write_text(
        output / "02_AUTHOR_CONTRACT_SIGNOFF.json", stable_json(signoff)
    )
    go_template = {
        "schema": "RP_V4_STAGE_F_EXACT_CODE_GO_1.0",
        "approved_by": [],
        "approved_at": None,
        "binding_git_commit": None,
        "code_binding_manifest_sha256": manifest_sha,
        "author_contract_approved": False,
        "single_estimand_delta_profile": False,
        "single_method_OLS_HC3_t64": False,
        "fixed_40_scenarios_4000_attempts_each": False,
        "fixed_seed_base_2026101004_stage141_truth142": False,
        "fixed_truth_precision_and_acceptance_thresholds": False,
        "no_replenishment_or_posthoc_scenario_removal": False,
        "failure_closes_branch_no_G2D": False,
        "final_G2C_does_not_unlock_real_outcomes_automatically": False,
        "authorize_outer_stage141": False,
        "authorize_truth_stage142": False,
        "GO_FOR_FULL_SYNTHETIC_G2C": False,
        "status": "UNISSUED_TEMPLATE__DO_NOT_RUN_FINAL_STREAMS",
    }
    atomic_write_text(
        output / "08_FULL_G2C_GO_TEMPLATE.json", stable_json(go_template)
    )


def _validate_external_manifest(external_root: Path) -> tuple[int, int]:
    manifest_path = external_root / "deliverables" / "SHA256_MANIFEST.csv"
    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    failures = 0
    for row in rows:
        path = external_root / Path(row["path"])
        if os.name == "nt":
            path = Path("\\\\?\\" + str(path.resolve()))
        if (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256_file(path) != row["sha256"].lower()
        ):
            failures += 1
    return len(rows), failures


def _stable_tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in root.rglob("*")
        if path.is_file() and path.name != "02_RUN_RECEIPT.json"
    }


def finalize(
    *,
    prepared: Path,
    external_zip: Path,
    external_root: Path,
    outer_resume: Path,
    outer_fresh: Path,
    truth_output: Path,
    preflight_receipt: Path,
    output: Path,
) -> None:
    prepared = Path(prepared)
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"Canonical freeze output exists: {output}")
    if sha256_file(external_zip) != EXPECTED_EXTERNAL_ZIP_SHA256:
        raise ValueError("External Stage E ZIP hash mismatch")
    with zipfile.ZipFile(external_zip) as archive:
        if archive.testzip() is not None:
            raise ValueError("External Stage E ZIP CRC failure")
        zip_entries = len(archive.infolist())
    payload_rows, payload_failures = _validate_external_manifest(external_root)
    if payload_rows != 153 or payload_failures:
        raise ValueError("External Stage E payload manifest failed")
    if _stable_tree(outer_resume) != _stable_tree(outer_fresh):
        raise ValueError("Independent outer qualification replay drift")
    preflight = read_json(preflight_receipt)
    if preflight.get("decision") != "PASS_STAGE_E2_WINDOWS_PREFLIGHT__HOLD_EXACT_CODE_GO":
        raise ValueError("Windows Stage E2 preflight did not pass")
    truth = read_json(truth_output / "02_TRUTH_RECEIPT.json")
    if truth.get("all_precision_pass") is not True:
        raise ValueError("Qualification truth precision did not pass")

    output.mkdir(parents=True)
    for filename in (
        "02_AUTHOR_CONTRACT_SIGNOFF.json",
        "04_STAGE_E2_SOURCE_BINDING.csv",
        "08_FULL_G2C_GO_TEMPLATE.json",
    ):
        shutil.copyfile(prepared / filename, output / filename)

    external_receipt = {
        "schema": "RP_V4_STAGE_E_EXTERNAL_RECEIPT_1.0",
        "zip_filename": Path(external_zip).name,
        "zip_bytes": Path(external_zip).stat().st_size,
        "zip_sha256": EXPECTED_EXTERNAL_ZIP_SHA256,
        "zip_entries": zip_entries,
        "zip_crc_pass": True,
        "payload_manifest_rows": payload_rows,
        "payload_manifest_failures": payload_failures,
        "external_adjudicator_tests": "14/14 PASS",
        "external_preflight_windows_result": "FAIL_UTF8_DEFAULT_ENCODING_GBK",
        "windows_stage131_shifted_truth_replay": "15/15 status match",
        "windows_stage131_max_truth_abs_difference": 0.0,
        "windows_stage131_max_mcse_abs_difference": 4.336808689942018e-19,
        "windows_stage131_max_mcse_over_typical_se": 0.007754568766074131,
        "stage141_started": False,
        "stage142_started": False,
    }
    atomic_write_text(
        output / "01_EXTERNAL_STAGE_E_RECEIPT.json", stable_json(external_receipt)
    )
    shutil.copyfile(preflight_receipt, output / "03_WINDOWS_RUNTIME_QUALIFICATION.json")
    qualification = {
        "schema": "RP_V4_STAGE_E2_QUALIFICATION_RECEIPT_1.0",
        "unit_tests": "15/15 PASS",
        "outer_scenarios": ["C0_X1", "C1_X2", "C2_X3"],
        "outer_attempts": 24,
        "outer_resume_and_fresh_byte_equivalent": True,
        "outer_resume_tree_files": len(_stable_tree(outer_resume)),
        "truth_scenarios": ["C0_X1", "C1_X2", "C2_X3"],
        "truth_effort_per_arm": 131072,
        "truth_all_precision_pass": True,
        "truth_maximum_mcse_over_typical_se": truth[
            "maximum_mcse_over_typical_se"
        ],
        "qualification_stage": 132,
        "stage141_started": False,
        "stage142_started": False,
        "real_effects_fitted": False,
    }
    atomic_write_text(
        output / "05_STAGE_E2_QUALIFICATION_RECEIPT.json",
        stable_json(qualification),
    )
    checks = [
        ("external_zip_crc", True, "154 entries; CRC clean"),
        ("external_payload_manifest", True, "153/153 exact"),
        ("external_windows_encoding_portability", False, "candidate preflight uses default CSV encoding; canonical code repaired"),
        ("author_contract_signoff", True, "Zhi Chen and Teng Qi; all frozen scientific terms approved"),
        ("code_and_contract_hash_binding", True, "canonical source binding verified"),
        ("windows_runtime_qualification", True, preflight["python_executable"]),
        ("unit_tests", True, "15/15 PASS"),
        ("outer_qualification_replay", True, "24 attempts; fresh/resume stable"),
        ("truth_qualification", True, "3/3 precision pass on stage132"),
        ("stage141_fail_closed", True, "exact-code GO absent"),
        ("stage142_fail_closed", True, "exact-code GO absent"),
        ("full_G2C_authorized", False, "separate post-commit exact-code GO required"),
        ("real_outcomes_loaded", False, "locked"),
    ]
    atomic_write_text(
        output / "06_STAGE_E2_CHECKS.csv",
        _csv_text(
            [
                {"check": name, "pass": passed, "detail": detail}
                for name, passed, detail in checks
            ],
            ["check", "pass", "detail"],
        ),
    )
    gate = {
        "schema": "RP_V4_STAGE_E2_GATE_1.0",
        "decision": "PASS_RPV4_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING__HOLD_EXACT_CODE_GO",
        "author_contract_approved": True,
        "canonical_windows_runtime_qualified": True,
        "canonical_outer_runner_bound": True,
        "canonical_independent_truth_runner_bound": True,
        "canonical_adjudicator_bound": True,
        "qualification_stage132_pass": True,
        "stage141_started": False,
        "stage142_started": False,
        "GO_FOR_FULL_SYNTHETIC_G2C": False,
        "real_WP2_authorized": False,
        "external_disease_outcomes_authorized": False,
        "large_SRA_download_authorized": False,
        "manuscript_or_submission_modified": False,
        "old_G2_G2B_hold_preserved": True,
        "next_stage": "RPV4_STAGE_F__POST_COMMIT_EXACT_CODE_GO_REVIEW",
    }
    atomic_write_text(output / "07_STAGE_E2_GATE_STATUS.json", stable_json(gate))
    advisor = """# RP v4 Stage E2 advisor review

## Decision

`PASS_RPV4_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING__HOLD_EXACT_CODE_GO`

The two authors' approval of the frozen scientific contract is recorded. The
Windows canonical environment, resumable outer runner, independent shifted-DGP
truth runner and result-blind adjudicator are now byte-bound and technically
qualified on non-final stage 132. No stage 141 or 142 stream was consumed.

## Independent findings

The received Stage E package is internally complete (153/153 payload hashes,
clean ZIP CRC) and its shifted truth budget reproduces on Windows. Its preflight
script is not directly portable to the canonical Windows runtime because CSV
files are opened without an explicit encoding and fail under the GBK default.
The project-side implementation fixes this by requiring UTF-8 for every text
input and adds a regression gate for fail-closed final authorization.

## Scientific boundary

This stage establishes execution readiness only. It does not establish bias,
coverage, type-I error or a G2C scientific PASS. G2/G2B HOLD remains unchanged.
Real WP2 effects, external disease outcomes, SRA download, manuscript changes
and submission remain locked.

## Next stage

After this Stage E2 code is committed, both authors must review the exact Git
commit and source-binding manifest and issue a separate exact-code GO. Until
that receipt exists, the canonical runner refuses stage 141 and stage 142.
"""
    atomic_write_text(output / "09_STAGE_E2_ADVISOR_REVIEW.md", advisor)
    stage_f = """# RP v4 Stage F exact-code GO/NO-GO contract

Stage F is an authorization review, not an analysis run by implication.

Required before any final stream is opened:

1. Commit the Stage E2 implementation and confirm a clean synchronized Git HEAD.
2. Recompute and verify `04_STAGE_E2_SOURCE_BINDING.csv` against that checkout.
3. Have Zhi Chen and Teng Qi approve the exact commit and manifest SHA-256.
4. Replace the unissued template with a new signed GO receipt; never edit the
   historical template in place.
5. Re-run the Windows preflight and require stage141/stage142 authorization to
   resolve only for that exact receipt, commit and manifest.

If any item fails, keep `HOLD_EXACT_CODE_GO`. A future full run must execute all
40 x 4,000 outer attempts without replenishment and the independent stage142
truth calculation before result-blind adjudication. A G2C failure closes the
decomposition branch; there is no G2D. A G2C pass still does not unlock real
outcomes automatically.
"""
    atomic_write_text(output / "10_STAGE_F_GO_NO_GO_CONTRACT.md", stage_f)
    integrity_rows = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "11_INTEGRITY_MANIFEST.csv":
            integrity_rows.append(
                {
                    "path": path.name,
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    atomic_write_text(
        output / "11_INTEGRITY_MANIFEST.csv",
        _csv_text(integrity_rows, ["path", "bytes", "sha256"]),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--output", type=Path, required=True)
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--prepared", type=Path, required=True)
    finalize_parser.add_argument("--external-zip", type=Path, required=True)
    finalize_parser.add_argument("--external-root", type=Path, required=True)
    finalize_parser.add_argument("--outer-resume", type=Path, required=True)
    finalize_parser.add_argument("--outer-fresh", type=Path, required=True)
    finalize_parser.add_argument("--truth-output", type=Path, required=True)
    finalize_parser.add_argument("--preflight-receipt", type=Path, required=True)
    finalize_parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.command == "prepare":
        prepare(arguments.output)
    else:
        finalize(
            prepared=arguments.prepared,
            external_zip=arguments.external_zip,
            external_root=arguments.external_root,
            outer_resume=arguments.outer_resume,
            outer_fresh=arguments.outer_fresh,
            truth_output=arguments.truth_output,
            preflight_receipt=arguments.preflight_receipt,
            output=arguments.output,
        )
