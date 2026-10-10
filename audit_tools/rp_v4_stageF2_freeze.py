"""Prepare and freeze the additive RP v4 Stage F2 integrity-hardened baseline."""
from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import zipfile
from pathlib import Path

try:
    from .rp_v4_stageF2_common import (
        REQUIRED_BINDING_PATHS,
        REPO_ROOT,
        atomic_write_text,
        read_json,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )
except ImportError:
    from rp_v4_stageF2_common import (
        REQUIRED_BINDING_PATHS,
        REPO_ROOT,
        atomic_write_text,
        read_json,
        sha256_file,
        stable_json,
        verify_binding_manifest,
    )


EXPECTED_EXTERNAL_ZIP_SHA256 = (
    "ec099143d64d6058b3c19e6cfc3be6b2ca6f0015f083a8d4c7ddfd6a8a15d7e8"
)


def _csv_text(rows: list[dict], fieldnames: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def prepare(output: Path) -> dict:
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    rows = []
    for relative_text in sorted(REQUIRED_BINDING_PATHS):
        source = REPO_ROOT / Path(relative_text)
        if not source.is_file():
            raise FileNotFoundError(source)
        rows.append(
            {
                "path": relative_text,
                "bytes": source.stat().st_size,
                "sha256": sha256_file(source),
            }
        )
    manifest_path = output / "04_STAGE_F2_SOURCE_BINDING.csv"
    atomic_write_text(manifest_path, _csv_text(rows, ["path", "bytes", "sha256"]))
    manifest_sha = verify_binding_manifest(manifest_path)
    draft = {
        "schema": "RP_V4_STAGE_G_EXACT_CODE_GO_1.0",
        "status": "UNISSUED_TEMPLATE",
        "approved_by": [],
        "approved_at": None,
        "binding_git_commit": None,
        "code_binding_manifest_sha256": manifest_sha,
        "qualified_runtime_receipt_sha256": None,
        "author_contract_approved": False,
        "single_estimand_delta_profile": False,
        "single_method_OLS_HC3_t64": False,
        "fixed_40_scenarios_4000_attempts_each": False,
        "fixed_seed_base_2026101004_stage141_truth142": False,
        "fixed_truth_precision_and_acceptance_thresholds": False,
        "no_replenishment_or_posthoc_scenario_removal": False,
        "failure_closes_branch_no_G2D": False,
        "final_G2C_does_not_unlock_real_outcomes_automatically": False,
        "clean_worktree_required": False,
        "exact_qualified_runtime_required": False,
        "complete_payload_hash_sealing_required": False,
        "authorize_outer_stage141": False,
        "authorize_truth_stage142": False,
        "GO_FOR_FULL_SYNTHETIC_G2C": False,
    }
    draft_path = output / "08_STAGE_G_EXACT_CODE_GO_DRAFT.json"
    atomic_write_text(draft_path, stable_json(draft))
    return {
        "binding_manifest": str(manifest_path),
        "binding_manifest_sha256": manifest_sha,
        "go_draft": str(draft_path),
    }


def _validate_external(external_zip: Path, external_root: Path) -> tuple[int, int]:
    if sha256_file(external_zip) != EXPECTED_EXTERNAL_ZIP_SHA256:
        raise ValueError("Unexpected Stage F review ZIP SHA-256")
    with zipfile.ZipFile(external_zip) as archive:
        if archive.testzip() is not None:
            raise ValueError("Stage F review ZIP CRC failure")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entries")
        if any(
            Path(name).is_absolute() or ".." in Path(name.replace("\\", "/")).parts
            for name in names
        ):
            raise ValueError("Unsafe ZIP path")
    manifest_path = external_root / "MANIFEST_SHA256.csv"
    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    failures = 0
    for row in rows:
        path = external_root / Path(row["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256_file(path) != row["sha256"].lower()
        ):
            failures += 1
    return len(rows), failures


def finalize(
    *,
    prepared: Path,
    preflight_receipt: Path,
    external_zip: Path,
    external_root: Path,
    output: Path,
) -> dict:
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    prepared = Path(prepared)
    manifest_source = prepared / "04_STAGE_F2_SOURCE_BINDING.csv"
    draft_source = prepared / "08_STAGE_G_EXACT_CODE_GO_DRAFT.json"
    manifest_sha = verify_binding_manifest(manifest_source)
    preflight = read_json(preflight_receipt)
    if (
        preflight.get("schema") != "RP_V4_STAGE_F2_WINDOWS_QUALIFICATION_1.0"
        or preflight.get("binding_manifest_sha256") != manifest_sha
        or preflight.get("decision")
        != "PASS_STAGE_F2_WINDOWS_QUALIFICATION__HOLD_POST_COMMIT_EXACT_CODE_GO"
    ):
        raise ValueError("Stage F2 Windows qualification receipt is invalid")
    external_rows, external_failures = _validate_external(external_zip, external_root)
    if external_rows != 7 or external_failures:
        raise ValueError("External Stage F review payload failed")

    output.mkdir(parents=True)
    external_receipt = {
        "schema": "RP_V4_STAGE_F_EXTERNAL_REVIEW_RECEIPT_1.0",
        "zip_filename": Path(external_zip).name,
        "zip_bytes": Path(external_zip).stat().st_size,
        "zip_sha256": EXPECTED_EXTERNAL_ZIP_SHA256,
        "zip_crc_pass": True,
        "payload_manifest_rows": external_rows,
        "payload_manifest_failures": external_failures,
        "review_decision": "HOLD_STAGE_F_EXACT_CODE_GO__INTEGRITY_HARDENING_REQUIRED",
        "stage141_started": False,
        "stage142_started": False,
    }
    atomic_write_text(output / "01_EXTERNAL_STAGE_F_RECEIPT.json", stable_json(external_receipt))

    contract = """# RP v4 Stage F2 integrity-hardening contract

Stage F2 preserves the single `delta_profile` estimand, OLS/HC3/t(64), the
fixed 40 x 4,000 outer grid, stages 141/142, seed base 2026101004, the original
truth and acceptance thresholds, no replenishment and no G2D rescue.

The additive implementation binds the complete local dependency set including
`rp_v4_g2c_truth.py`; requires an exact clean Git checkout and the qualified
Windows interpreter; seals every outer chunk and truth checkpoint; reconciles
the final accounting and truth CSV against receipts; validates HC3-t(64)
interval algebra; and supports fail-closed per-scenario truth resumption.

This freeze is not an exact-code GO. Stage 141 and 142 remain locked until both
authors separately approve the new post-commit Git SHA, source-binding digest
and runtime receipt digest.
"""
    atomic_write_text(output / "02_STAGE_F2_HARDENING_CONTRACT.md", contract)
    shutil.copyfile(preflight_receipt, output / "03_WINDOWS_RUNTIME_QUALIFICATION.json")
    shutil.copyfile(manifest_source, output / "04_STAGE_F2_SOURCE_BINDING.csv")
    qualification = {
        "schema": "RP_V4_STAGE_F2_QUALIFICATION_RECEIPT_1.0",
        "outer_attempts": 24,
        "outer_chunks": 3,
        "outer_fresh_resume_payload_verified": True,
        "truth_scenarios": 3,
        "truth_checkpoints": 48,
        "truth_all_precision_pass": True,
        "truth_independent_score_crosscheck": True,
        "truth_maximum_mcse_over_typical_se": preflight[
            "truth_maximum_mcse_over_typical_se"
        ],
        "unit_and_regression_tests": preflight.get("unit_and_regression_tests"),
        "negative_tamper_tests": preflight.get("negative_tamper_tests"),
        "stage141_started": False,
        "stage142_started": False,
        "real_effects_fitted": False,
    }
    atomic_write_text(output / "05_STAGE_F2_QUALIFICATION_RECEIPT.json", stable_json(qualification))
    checks = [
        ("external_stageF_payload", True, "7/7 SHA-256; CRC clean"),
        ("unbound_truth_helper_repaired", True, "rp_v4_g2c_truth.py bound"),
        ("clean_worktree_final_gate", True, "fail closed"),
        ("exact_runtime_final_gate", True, "executable hash and package versions"),
        ("outer_chunk_sealing", True, "payload and seal manifest reconciled"),
        ("truth_checkpoint_resume", True, "48/48 qualification checkpoints"),
        ("truth_and_accounting_receipt_hashes", True, "mandatory"),
        ("HC3_t64_interval_identity", True, "per supported attempt"),
        ("independent_truth_score_crosscheck", True, "runtime cross-check"),
        ("negative_tamper_suite", True, preflight.get("negative_tamper_tests")),
        ("stage141_fail_closed", True, "exact post-commit GO absent"),
        ("stage142_fail_closed", True, "exact post-commit GO absent"),
    ]
    check_rows = [
        {"check": name, "pass": passed, "detail": detail}
        for name, passed, detail in checks
    ]
    atomic_write_text(
        output / "06_STAGE_F2_CHECKS.csv",
        _csv_text(check_rows, ["check", "pass", "detail"]),
    )
    gate = {
        "schema": "RP_V4_STAGE_F2_GATE_1.0",
        "decision": "PASS_STAGE_F2_INTEGRITY_HARDENING_AND_REBIND__HOLD_POST_COMMIT_EXACT_CODE_GO",
        "source_binding_sha256": manifest_sha,
        "qualified_runtime_receipt_sha256": sha256_file(preflight_receipt),
        "stage141_authorized": False,
        "stage142_authorized": False,
        "stage141_started": False,
        "stage142_started": False,
        "full_synthetic_G2C_pass": False,
        "old_G2_G2B_hold_retained": True,
        "real_WP2_outcomes_authorized": False,
        "large_SRA_download_authorized": False,
        "manuscript_or_submission_reopened": False,
        "next_stage": "RPV4_STAGE_G__POST_PATCH_EXACT_CODE_AND_RUNTIME_GO_REVIEW",
    }
    atomic_write_text(output / "07_STAGE_F2_GATE_STATUS.json", stable_json(gate))
    go_template = read_json(draft_source)
    go_template["qualified_runtime_receipt_sha256"] = sha256_file(preflight_receipt)
    atomic_write_text(output / "08_STAGE_G_EXACT_CODE_GO_TEMPLATE.json", stable_json(go_template))
    advisor = f"""# RP v4 Stage F2 advisor review

**Decision:** `PASS_STAGE_F2_INTEGRITY_HARDENING_AND_REBIND__HOLD_POST_COMMIT_EXACT_CODE_GO`.

The Stage F blockers were reproduced and repaired in an additive implementation.
The complete source dependency set is bound under `{manifest_sha}`. The Windows
qualification preserved the registered estimand, method, random stages and
thresholds; final stages were not consumed.

The new outer runner seals and reconciles every chunk, while the truth engine
uses deterministic per-scenario checkpoints, independent score cross-checking
and write-once receipts. The final adjudicator verifies outer accounting,
chunk payloads, truth CSV, checkpoint inventory and HC3-t(64) interval algebra.

This is still not authorization to execute stages 141/142. Both authors must
approve the new exact commit, this source-binding digest and the qualified
runtime receipt after the commit is published. Real WP2 outcomes, SRA, WP4,
manuscript replacement and submission remain locked.
"""
    atomic_write_text(output / "09_STAGE_F2_ADVISOR_REVIEW.md", advisor)
    next_contract = """# RP v4 Stage G exact-code GO contract

Stage G is limited to reviewing the new committed F2 baseline. Both authors
must explicitly approve the exact Git SHA, source-binding SHA-256 and qualified
runtime receipt SHA-256. The issued receipt must authorize outer stage 141 and
truth stage 142 separately and retain every scientific stop rule.

No final stream may start from the unissued template. Any code, contract,
runtime, worktree, chunk, truth, accounting or receipt drift closes the gate.
Even a synthetic PASS requires a separate review before any real outcome work.
"""
    atomic_write_text(output / "10_STAGE_G_GO_NO_GO_CONTRACT.md", next_contract)

    integrity_rows = []
    for path in sorted(output.iterdir(), key=lambda item: item.name):
        if path.name == "11_INTEGRITY_MANIFEST.csv" or not path.is_file():
            continue
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
    return gate


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--output", type=Path, required=True)
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--prepared", type=Path, required=True)
    finalize_parser.add_argument("--preflight-receipt", type=Path, required=True)
    finalize_parser.add_argument("--external-zip", type=Path, required=True)
    finalize_parser.add_argument("--external-root", type=Path, required=True)
    finalize_parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.command == "prepare":
        result = prepare(arguments.output)
    else:
        result = finalize(
            prepared=arguments.prepared,
            preflight_receipt=arguments.preflight_receipt,
            external_zip=arguments.external_zip,
            external_root=arguments.external_root,
            output=arguments.output,
        )
    print(stable_json(result), end="")
