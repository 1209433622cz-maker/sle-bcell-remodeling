"""Verify current release documentation and the unresolved journal-selection gate."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"
CURRENT_DOI = "10.5281/zenodo.22151739"
OLD_DOI = "10.5281/zenodo.22086892"
RELEASE_TAG = "v1.1.0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def safe_path(root, value):
    relative = Path(value)
    require(not relative.is_absolute(), "Manifest path must be relative: " + value)
    resolved = (root / relative).resolve()
    require(resolved.is_relative_to(root.resolve()), "Manifest path escapes root: " + value)
    return resolved


def verify_received_manifest(selection_dir, manifest):
    rows = manifest.get("files", [])
    require(len(rows) == 3, "Received evidence manifest must contain three files")
    paths = [row.get("path") for row in rows]
    require(len(paths) == len(set(paths)), "Received evidence manifest has duplicates")
    for row in rows:
        path = safe_path(selection_dir, row["path"])
        require(path.is_file(), "Received evidence file is missing: " + row["path"])
        require(path.stat().st_size == row["bytes"], "Received evidence size differs: " + row["path"])
        require(checksum(path) == row["sha256"].upper(), "Received evidence SHA-256 differs: " + row["path"])
    return len(rows)


def verify_documentation(root):
    root = root.resolve()
    selection = root / "00_project_management/jcr_q1_journal_selection_2026-08-29"
    readiness_path = root / "00_project_management/qiteng_r2_freeze_2026-08-29/publication_readiness.json"
    readme = (root / "README.md").read_text(encoding="utf-8")
    reproducibility = (root / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
    combined = readme + "\n" + reproducibility

    for phrase in (CURRENT_DOI, OLD_DOI, RELEASE_TAG, "Journal submission remains unauthorized"):
        require(phrase in combined, "Current release boundary is missing: " + phrase)
    for stale in (
        "A matching new archive version is required before journal submission",
        "No new Zenodo DOI has yet been reserved or published",
        "Administrative DOI integration is pending",
        "requested but not yet published",
    ):
        require(stale not in combined, "Stale release statement remains: " + stale)

    status = read_json(selection / "journal_selection_status.json")
    require(status["status"] == "CONDITIONAL_FIT_LEAD_SET_OFFICIAL_JCR_AND_APC_EVIDENCE_PENDING", "Journal gate status differs")
    require(status["selected_target"] is None, "Target journal was selected without complete evidence")
    require(status["official_jcr_profile_export_obtained"] is False, "JCR profile export is overclaimed")
    require(status["all_categories_rank_denominator_quartile_verified"] is False, "JCR quartile is overclaimed")
    require(status["institutional_apc_coverage_verified"] is False, "APC coverage is overclaimed")
    require(status["target_specific_manuscript_adaptation_started"] is False, "Target adaptation started before target freeze")
    require(status["submission_authorized"] is False, "Journal submission was incorrectly authorized")
    require(status["apc_commitment_authorized"] is False, "APC commitment was incorrectly authorized")
    require(status["new_scientific_analysis_performed"] is False, "Unexpected scientific analysis is recorded")
    require(status["R1_decision"] == R1_HOLD, "R1 permanent HOLD differs")
    require(status["C9R_decision"] == C9R_HOLD, "C9R HOLD differs")
    require(status["corrected_external_outcome_unlock_authorized"] is False, "Corrected external outcomes were unlocked")

    sources = read_json(selection / "official_source_snapshot.json")
    require(sources["jcr"]["release"] == 2026 and sources["jcr"]["data_year"] == 2025, "JCR release/data-year boundary differs")
    require(sources["jcr"]["rank_and_quartile_verified"] is False, "Official JCR rank/quartile is overclaimed")
    require(sources["selected_target"] is None, "Official-source snapshot selects a target prematurely")
    require(sources["scientific_changes_performed"] is False, "Official-source review changed science")
    require(len(sources["journals"]) == 2, "Official-source snapshot must contain two conditional candidates")
    require(all(journal["jcr_q1_verified"] is False for journal in sources["journals"]), "Candidate JCR Q1 status is overclaimed")

    readiness = read_json(readiness_path)
    journal = readiness["journal_selection"]
    require(journal["selected_target"] is None, "Publication readiness selects a target prematurely")
    require(journal["jcr_q1_eligibility_verified"] is False, "Publication readiness overclaims JCR Q1")
    require(journal["target_specific_adaptation_started"] is False, "Publication readiness overclaims adaptation")
    require(readiness["remaining_not_completed"]["journal_submission"] is False, "Publication readiness overclaims submission")

    evidence_count = verify_received_manifest(selection, read_json(selection / "received_evidence_manifest.json"))
    return {
        "release_documentation_files_verified": 2,
        "received_evidence_files_verified": evidence_count,
        "current_zenodo_doi": CURRENT_DOI,
        "old_zenodo_tombstone_doi": OLD_DOI,
        "github_release_tag": RELEASE_TAG,
        "selected_target": None,
        "jcr_q1_verified": False,
        "institutional_apc_coverage_verified": False,
        "target_specific_adaptation_started": False,
        "submission_authorized": False,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "scientific_analysis_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "00_project_management/jcr_q1_journal_selection_2026-08-29/release_and_target_documentation_verification.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    require(output.is_relative_to((ROOT / "00_project_management").resolve()), "Receipt must remain in project management")
    checks = verify_documentation(ROOT)
    receipt = {
        "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_RELEASE_DOCUMENTATION_CURRENT_JOURNAL_GATE_UNRESOLVED",
        "checks": checks,
        "next_gate": "Obtain official JCR profile exports and institutional APC/OA evidence before selecting or adapting to a journal",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
