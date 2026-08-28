"""Stage a bounded Figure 1 correction; preserve the approved ZIP and statistics."""

import argparse
import json
from pathlib import Path
import shutil

from phase17_postc9_06_build_correction_package import csv_bytes, verify_directory_manifest
from verify_review_bundle import CANDIDATE, CANDIDATE_EDITS, CANDIDATE_REPLACED, archive_entries, sha256, verify_entries


ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA256 = "0363C066FB7F8FAD5E867FC820ED7F80C8F3D1A10E0A1CB43B8A7A51FCA92234"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--figure1-dir", type=Path, required=True)
    parser.add_argument("--refresh-figure-only", action="store_true")
    args = parser.parse_args()
    review, audit, figure1 = (path.resolve() for path in (args.review_dir, args.audit_dir, args.figure1_dir))
    if not review.is_relative_to(ROOT/"phase17_v7/post_gateC9") or not audit.is_relative_to(ROOT/"00_project_management"):
        raise ValueError("Candidate staging must stay inside the project review directories")
    if args.refresh_figure_only:
        if (ROOT/"04_submission/corrected_candidate.zip").exists():
            raise ValueError("The packaged candidate is immutable; start a new build")
        if json.loads((audit/"candidate_stage.json").read_text())["baseline_zip_sha256"] != BASELINE_SHA256:
            raise ValueError("Cannot refresh staging from a different baseline")
        verify_directory_manifest(review, "02_REVIEW_FIGURE_MANIFEST.csv")
    elif (review/"figures").exists() or (audit/"review_gate.json").exists():
        raise ValueError("Candidate already staged; choose a new directory rather than overwrite it")
    baseline = ROOT/"04_submission/author_confirmed_review.zip"
    if sha256(baseline.read_bytes()) != BASELINE_SHA256:
        raise ValueError("Approved baseline ZIP changed")
    entries = archive_entries(baseline.read_bytes())
    verify_entries(entries, "MANIFEST_SHA256.csv")
    old = ROOT/"phase17_v7/post_gateC9/20260828_advisor_correction_review"
    verify_directory_manifest(old, "02_REVIEW_FIGURE_MANIFEST.csv")
    label = json.loads((figure1/"01_LABEL_CORRECTION_AUDIT.json").read_text())
    for row in label["files"]:
        payload = (figure1/row["path"]).read_bytes()
        if sha256(payload) != row["sha256"] or len(payload) != row["bytes"]:
            raise ValueError("Figure 1 rerun bytes differ from its audit")
    if (old/"source_data/Figure1_source_data.csv").read_bytes() != (figure1/"source_data/Figure1_source_data.csv").read_bytes():
        raise ValueError("Figure 1 source data changed")
    for name, changes in CANDIDATE_EDITS.items():
        expected = entries[name].decode("utf-8")
        for before, after in changes:
            if expected.count(before) != 1 or after in expected:
                raise ValueError("Ambiguous candidate change")
            expected = expected.replace(before, after)
        folder = "04_submission" if name.endswith("Cover_Letter.md") else "01_manuscript"
        if (ROOT/folder/Path(name).name).read_bytes() != expected.encode("utf-8"):
            raise ValueError("Canonical source has a change outside the declared editorial delta")
    review.mkdir(parents=True, exist_ok=True)
    audit.mkdir(parents=True, exist_ok=True)
    for folder in ("figures", "source_data"):
        (review/folder).mkdir(exist_ok=args.refresh_figure_only)
        for path in sorted((old/folder).iterdir()):
            if args.refresh_figure_only and not path.name.startswith("Figure1_"):
                continue
            source = figure1/folder/path.name if path.name.startswith("Figure1_") else path
            shutil.copy2(source, review/folder/path.name)
    for name in CANDIDATE_REPLACED:
        target = audit/"prior_snapshot"/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(entries[name])
    for name in ("author_confirmation.json", "Reviewed_Package_MANIFEST_SHA256.csv", "External_Methods_Review.md"):
        (audit/name).write_bytes(entries["governance/"+name])
    (audit/"Prior_Review_Gate.json").write_bytes(entries["governance/review_gate.json"])
    previous = ROOT/"00_project_management/author_confirmation_2026-08-28"
    for name in ("calibration_recount.csv", "calibration_recount_audit.json"):
        shutil.copy2(previous/name, audit/name)
    shutil.copy2(figure1/"01_LABEL_CORRECTION_AUDIT.json", audit/"figure1_label_correction.json")
    gate = json.loads(entries["governance/review_gate.json"])
    gate.update({"gate":"EXTERNAL_METHODS_REVIEW_AND_AUTHOR_REAPPROVAL_GATE",
                 "candidate_baseline_zip_sha256":BASELINE_SHA256,
                 "prior_review_gate_sha256":sha256(entries["governance/review_gate.json"]),
                 "baseline_repository_commit":"c68775982f47a637dbc2bfa1b89df3640984b31d"})
    gate["authors"] = [{"name":name,"decision":CANDIDATE,"date":None,"evidence":None}
                       for name in ("Zhi Chen", "Teng Qi")]
    gate["postapproval_presentation_issue"]["status"] = "INTEGRATED_CORRECTED_CANDIDATE_PENDING_APPROVAL"
    write_json(audit/"review_gate.json", gate)
    old_assertions = json.loads((old/"01_FIGURE_BUILD_ASSERTIONS.json").read_text())
    write_json(review/"01_FIGURE_BUILD_ASSERTIONS.json", {
        "status":"BUILT_PENDING_VISUAL_REVIEW", "all_pass":all(row["pass"] for row in label["assertions"]),
        "checks":label["assertions"], "assertions":len(label["assertions"]),
        "scope":"Figure 1 regenerated; Figures 2-5 and S1-S10 byte-identical to the previous reviewed build",
        "inherited_assertions_sha256":sha256((old/"01_FIGURE_BUILD_ASSERTIONS.json").read_bytes()),
        "inherited_assertions_all_pass":old_assertions["all_pass"]})
    files = sorted(path for folder in ("figures", "source_data") for path in (review/folder).iterdir())
    rows = [{"filename":path.relative_to(review).as_posix(),"size_bytes":path.stat().st_size,
             "sha256":sha256(path.read_bytes())} for path in files]
    (review/"02_REVIEW_FIGURE_MANIFEST.csv").write_bytes(csv_bytes(rows))
    write_json(audit/"candidate_stage.json", {
        "status":"STAGED_FOR_DOCUMENT_REBUILD", "baseline_zip_sha256":BASELINE_SHA256,
        "figure_and_source_files":len(rows), "unchanged_figure_and_source_files":sum(
            path.read_bytes() == (old/path.relative_to(review)).read_bytes() for path in files),
        "allowed_changes":CANDIDATE_EDITS, "submission_authorized":False})
    print("Candidate staged with immutable statistical sources and explicit pending approval.")


if __name__ == "__main__":
    main()
