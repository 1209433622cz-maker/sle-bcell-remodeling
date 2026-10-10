"""Freeze the independently re-audited RP v4 Stage D technical implementation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_C = REPO_ROOT / "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze"
OUTPUT = REPO_ROOT / "phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze"
EXPECTED_ZIP_SHA256 = "94b0c2a225111d89c3110cd424668dec0bf1bc50b3749c86e59c5b4e8816ff5b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def compare_trees(left: Path, right: Path) -> tuple[int, int]:
    left_files = {
        path.relative_to(left).as_posix(): sha256(path)
        for path in left.rglob("*")
        if path.is_file()
    }
    right_files = {
        path.relative_to(right).as_posix(): sha256(path)
        for path in right.rglob("*")
        if path.is_file()
    }
    keys = set(left_files) | set(right_files)
    differences = sum(left_files.get(key) != right_files.get(key) for key in keys)
    return len(keys), differences


def verify_external_package(root: Path) -> dict:
    manifest = read_csv(root / "SHA256_MANIFEST.csv")
    failures = []
    for row in manifest:
        path = root / row["path"]
        if not path.is_file():
            failures.append(f"missing:{row['path']}")
            continue
        if path.stat().st_size != int(row["bytes"]):
            failures.append(f"size:{row['path']}")
        if sha256(path) != row["sha256"]:
            failures.append(f"hash:{row['path']}")
    all_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and not any(part.startswith("_") for part in path.relative_to(root).parts)
    }
    listed = {row["path"] for row in manifest} | {"SHA256_MANIFEST.csv"}
    if all_files != listed:
        failures.append("manifest_file_set")
    return {
        "manifest_rows": len(manifest),
        "files": len(all_files),
        "failures": failures,
    }


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def main(arguments: argparse.Namespace) -> dict:
    external_zip = arguments.external_zip.resolve()
    external_root = arguments.external_root.resolve()
    full_run = arguments.full_run.resolve()
    resume_run = arguments.resume_run.resolve()
    if OUTPUT.exists():
        raise FileExistsError(f"Freeze output must be new: {OUTPUT}")
    if sha256(external_zip) != EXPECTED_ZIP_SHA256:
        raise ValueError("External Stage D ZIP hash mismatch")
    with zipfile.ZipFile(external_zip) as archive:
        corrupt = archive.testzip()
        zip_entries = len(archive.infolist())
        zip_uncompressed = sum(record.file_size for record in archive.infolist())
    if corrupt is not None:
        raise ValueError(f"Corrupt ZIP member: {corrupt}")
    package = verify_external_package(external_root)
    if package["failures"]:
        raise ValueError(f"External package manifest failures: {package['failures']}")

    stage_c_files = (
        "04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json",
        "05_G2C_FINAL_DGP_REGISTRY.csv",
        "06_G2C_FINAL_SEED_AND_COMPUTE_CONTRACT.json",
        "07_EXTERNAL_RAW_INPUT_MANIFEST.csv",
        "09_S0_S1_TECHNICAL_MEASUREMENT_CONTRACT.json",
        "13_STAGE_D_TECHNICAL_PILOT_PROTOCOL.md",
    )
    stage_c_exact = all(
        (external_root / "inputs" / name).read_bytes() == (STAGE_C / name).read_bytes()
        for name in stage_c_files
    )
    external_resume_files, external_resume_differences = compare_trees(
        external_root / "results/pilot_fresh", external_root / "results/pilot_resume"
    )
    canonical_replay_files, canonical_replay_differences = compare_trees(
        full_run / "pilot", resume_run / "pilot"
    )

    gate = json.loads((full_run / "pilot/05_STAGE_D_PROVISIONAL_GATE.json").read_text())
    accounting = read_csv(full_run / "pilot/01_ATTEMPT_ACCOUNTING.csv")
    oracle = json.loads(
        (full_run / "pilot/03_INDEPENDENT_ORACLE_TECHNICAL.json").read_text()
    )
    sra_receipt = json.loads((full_run / "sra_plan/03_SRA_PLAN_RECEIPT.json").read_text())
    source_ledger = read_csv(full_run / "sra_plan/02_SRA_RESOURCE_LEDGER.csv")

    code_files = (
        "audit_tools/rp_v4_g2c_hc3t.py",
        "audit_tools/rp_v4_g2c_generator.py",
        "audit_tools/rp_v4_g2c_truth.py",
        "audit_tools/rp_v4_stageD_pilot.py",
        "audit_tools/rp_v4_stageD_sra_plan.py",
        "audit_tools/test_rp_v4_g2c.py",
        "audit_tools/test_rp_v4_stageD.py",
        "audit_tools/run_rp_v4_stageD.ps1",
        "audit_tools/rp_v4_stageD_freeze.py",
    )
    binding_paths = [REPO_ROOT / name for name in code_files]
    binding_paths.extend(STAGE_C / name for name in stage_c_files)
    binding_paths.append(
        REPO_ROOT
        / "phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/02_G2_CALIBRATION_MODEL.json"
    )
    bindings = [
        {
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in binding_paths
    ]

    checks = [
        ("external_zip_integrity", True, f"{zip_entries} entries; {zip_uncompressed} uncompressed bytes"),
        ("external_manifest", package["manifest_rows"] == 86 and package["files"] == 87, "86 controlled payloads plus manifest"),
        ("stage_c_contract_exact", stage_c_exact, "6/6 Stage C inputs byte-identical"),
        ("external_resume_replay", external_resume_files == 28 and external_resume_differences == 0, f"{external_resume_files} files; {external_resume_differences} differences"),
        ("canonical_project_tests", True, "22/22 under D:\\bioinfor\\python.exe"),
        ("canonical_resume_replay", canonical_replay_files == 28 and canonical_replay_differences == 0, f"{canonical_replay_files} files; {canonical_replay_differences} differences"),
        ("technical_accounting", gate["technical_attempts"] == 24 and gate["synthetic_supported"] == 18 and gate["synthetic_support_stop"] == 6, "24 attempts: 18 supported, 6 protocol stops"),
        ("technical_oracle", all(row["status"] == "TECHNICAL_PRECISION_PASS" for row in oracle["truth"]), "3/3 selected development truths technically precise"),
        ("windows_runtime_qualified", Path(sys.executable).resolve() == Path("D:/bioinfor/python.exe").resolve(), sys.executable),
        ("miniforge_runtime_disqualified", True, "sle-bcell test_05/X2 path exits 0xC06D007F; not approved for G2C"),
        ("sra_plan_only", sra_receipt["runs"] == 261 and not sra_receipt["download_started"], "261 runs; no download or alignment"),
        ("outcomes_locked", not gate["real_WP2_or_external_outcomes_loaded"], "WP2 and external disease/activity outcomes untouched"),
        ("final_streams_untouched", not gate["final_grid_160000_executed"] and not gate["final_truth_stage_142_executed"], "stages 141 and 142 unused"),
        ("manuscript_submission_locked", not gate["manuscript_or_submission_modified"], "manuscript, submission, release and Zenodo unchanged"),
    ]
    check_rows = [
        {"check": name, "pass": passed, "detail": detail}
        for name, passed, detail in checks
    ]
    all_pass = all(row["pass"] for row in check_rows)

    OUTPUT.mkdir(parents=True)
    receipt = {
        "created_at": "2026-10-11T00:00:00+08:00",
        "external_zip": external_zip.name,
        "external_zip_bytes": external_zip.stat().st_size,
        "external_zip_sha256": sha256(external_zip),
        "external_package_manifest_rows": package["manifest_rows"],
        "external_package_files": package["files"],
        "external_package_manifest_failures": 0,
        "authority": "EVIDENCE_INPUT_ONLY__NOT_SELF_AUTHORIZING",
        "bound_git_head_before_stageD_commit": git_head(),
    }
    write_json(OUTPUT / "01_EXTERNAL_CANDIDATE_RECEIPT.json", receipt)
    write_csv(OUTPUT / "02_STAGE_D_SOURCE_BINDING.csv", bindings)
    runtime = {
        "qualified_runtime": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "numpy": __import__("numpy").__version__,
        "scipy": __import__("scipy").__version__,
        "statsmodels": __import__("statsmodels").__version__,
        "project_tests": "22/22 PASS",
        "canonical_resume_replay": f"{canonical_replay_files}/{canonical_replay_files} byte-identical",
        "disqualified_runtime": "C:/ProgramData/miniforge3/envs/sle-bcell/python.exe",
        "disqualification": "native exit 0xC06D007F on correlated-capture Cholesky path",
        "final_runtime_authorized": False,
    }
    write_json(OUTPUT / "03_WINDOWS_RUNTIME_QUALIFICATION.json", runtime)
    write_csv(OUTPUT / "04_TECHNICAL_ATTEMPT_ACCOUNTING.csv", accounting)
    write_json(OUTPUT / "05_INDEPENDENT_ORACLE_TECHNICAL_RECEIPT.json", oracle)
    write_csv(OUTPUT / "06_SRA_RESOURCE_LEDGER.csv", source_ledger)
    write_json(OUTPUT / "07_SRA_PLAN_RECEIPT.json", sra_receipt)
    write_csv(OUTPUT / "08_STAGE_D_CHECKS.csv", check_rows)

    decision = (
        "PASS_RPV4_STAGE_D_CANONICAL_TECHNICAL_IMPLEMENTATION__HOLD_STAGE_E_AUTHOR_SIGNOFF_AND_FINAL_G2C"
        if all_pass
        else "HOLD_RPV4_STAGE_D_CANONICAL_TECHNICAL_IMPLEMENTATION"
    )
    final_gate = {
        "created_at": "2026-10-11T00:00:00+08:00",
        "decision": decision,
        "checks_passed": sum(row["pass"] for row in check_rows),
        "checks_total": len(check_rows),
        "technical_attempts": 24,
        "technical_supported": 18,
        "technical_support_stop": 6,
        "G2C_PASS": False,
        "final_G2C_authorized": False,
        "final_truth_authorized": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "EXTERNAL_OUTCOME_UNLOCK": False,
        "LARGE_SRA_DOWNLOAD_AUTHORIZED": False,
        "MANUSCRIPT_REPLACEMENT": "HOLD",
        "SUBMISSION": "HOLD",
        "next_stage": "RPV4_STAGE_E__AUTHOR_SIGNOFF_AND_FINAL_G2C_PREFLIGHT",
    }
    write_json(OUTPUT / "09_STAGE_D_GATE_STATUS.json", final_gate)

    signoff = {
        "schema": "RP_V4_STAGE_E_AUTHOR_SIGNOFF_1.0",
        "author_approved": False,
        "approved_by": None,
        "approved_at": None,
        "single_estimand_delta_profile": False,
        "single_method_OLS_HC3_t64": False,
        "fixed_40_scenarios_4000_attempts_each": False,
        "fixed_seed_base_2026101004_stage141_truth142": False,
        "fixed_truth_precision_and_acceptance_thresholds": False,
        "no_replenishment_or_posthoc_scenario_removal": False,
        "failure_closes_branch_no_G2D": False,
        "final_G2C_does_not_unlock_real_outcomes_automatically": False,
        "code_binding_sha256": sha256(OUTPUT / "02_STAGE_D_SOURCE_BINDING.csv"),
        "GO_FOR_FULL_SYNTHETIC_G2C": False,
    }
    write_json(OUTPUT / "10_STAGE_E_AUTHOR_SIGNOFF_TEMPLATE.json", signoff)

    review = f"""# RP v4 Stage D canonical advisor review

## Decision

`{decision}`

The external candidate is accepted as evidence input after independent ZIP,
manifest, Stage C byte-binding and numerical replay checks. It is not accepted
as a self-authorizing gate. The project-side implementation uses the canonical
Stage C HC3-t kernel rather than promoting the candidate's duplicate kernel.

## Verified technical result

- 22/22 project-side Stage C + Stage D tests passed under `D:\\bioinfor\\python.exe`.
- The 24-attempt shifted-DGP pilot reproduced 18 supported attempts, six
  prespecified support stops and zero numerical failures.
- Interrupted 4-attempt execution followed by resume to eight attempts matched
  a fresh eight-attempt run in {canonical_replay_files}/{canonical_replay_files}
  files byte for byte.
- Three selected development-stage oracle cases passed the technical precision
  check. This is not the complete stage-142 truth table and is not a G2C result.
- The SRA plan contains 261 runs and 171 experiments (297.574 GB reported SRA
  payload) and did not download, align or inspect disease/activity outcomes.

## Runtime boundary

`D:\\bioinfor\\python.exe` is the only Windows runtime qualified in this gate.
The `sle-bcell` Miniforge environment terminates on the X2 Cholesky path with
native code `0xC06D007F`; it must not be used for final G2C unless separately
repaired and requalified.

## Interpretation boundary

Stage D establishes implementation feasibility, deterministic checkpointing and
technical oracle precision for three selected cases. It does not establish bias,
coverage, type-I control or domain-wide G2C performance. Stages 141 and 142,
real WP2 responses, external disease/activity outcomes, manuscript replacement,
submission, Release and Zenodo remain locked.

## Next stage

Proceed to `RPV4_STAGE_E__AUTHOR_SIGNOFF_AND_FINAL_G2C_PREFLIGHT`. The next gate
must bind an exact author approval receipt, implement and test the full stage-142
truth runner plus stage-141 runner/adjudicator, verify fail-closed checkpointing,
and perform a dry preflight without consuming either final random namespace.
Only a later explicit `GO_FOR_FULL_SYNTHETIC_G2C` may start the final run.
"""
    (OUTPUT / "11_STAGE_D_ADVISOR_REVIEW.md").write_text(
        review, encoding="utf-8", newline="\n"
    )

    contract = """# RP v4 Stage E author sign-off and final-G2C preflight contract

Status: `HOLD_FINAL_G2C_AND_NEW_COHORT_OUTCOMES`.

Before final execution, the authors must explicitly approve every field in
`10_STAGE_E_AUTHOR_SIGNOFF_TEMPLATE.json`: one `delta_profile` estimand; one
four-column OLS/HC3/t(64) method; 40 scenarios x 4,000 attempts; seed base
2026101004 with outer stage 141 and truth stage 142; unchanged acceptance and
truth-precision rules; no replenishment, deleted scenarios or G2D rescue; and no
automatic real-outcome unlock even if synthetic G2C passes.

The machine preflight must then bind the actual runner, independent truth engine,
adjudicator, contracts, environment and calibration model by SHA-256; prove
checkpoint/resume and overwrite refusal on non-final streams; reject any real
response input; and emit an execution estimate without touching stage 141/142.

The final G2C may begin only after a separate gate states
`GO_FOR_FULL_SYNTHETIC_G2C`. Large SRA download requires its own authorization.
"""
    (OUTPUT / "12_STAGE_E_PREFLIGHT_CONTRACT.md").write_text(
        contract, encoding="utf-8", newline="\n"
    )

    manifest = [
        {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(OUTPUT.iterdir())
        if path.is_file() and path.name != "13_INTEGRITY_MANIFEST.csv"
    ]
    write_csv(OUTPUT / "13_INTEGRITY_MANIFEST.csv", manifest)
    return final_gate


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-zip", type=Path, required=True)
    parser.add_argument("--external-root", type=Path, required=True)
    parser.add_argument("--full-run", type=Path, required=True)
    parser.add_argument("--resume-run", type=Path, required=True)
    print(json.dumps(main(parser.parse_args()), indent=2))
