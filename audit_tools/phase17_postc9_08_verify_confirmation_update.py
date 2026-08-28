"""Verify approved-snapshot continuity and the separate Figure 1 correction preview."""

import json
from pathlib import Path
import re

from phase17_postc9_06_build_correction_package import verify_directory_manifest
from verify_review_bundle import AUTHOR_APPROVAL_EDITS, CONFIRMED_SCOPE_PATHS, archive_entries, sha256, verify_bundle


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT/"00_project_management/author_confirmation_2026-08-28"


def main():
    current_root = ROOT/"04_submission/author_confirmed_review"
    result = verify_bundle(current_root)
    receipt = json.loads((AUDIT/"author_confirmation.json").read_text(encoding="utf-8"))
    old_zip = (ROOT/receipt["reviewed_package"]["path"]).read_bytes()
    if sha256(old_zip) != receipt["reviewed_package"]["sha256"]:
        raise ValueError("The author-reviewed snapshot changed")
    old = archive_entries(old_zip)
    current_zip = current_root.with_suffix(".zip").read_bytes()
    current = archive_entries(current_zip)
    disk = {p.relative_to(current_root).as_posix():p.read_bytes() for p in current_root.rglob("*") if p.is_file()}
    if disk != current:
        raise ValueError("Extracted confirmation package differs from its ZIP")
    numerical_tokens = {}
    for name, (before, after) in AUTHOR_APPROVAL_EDITS.items():
        previous = old[name].decode("utf-8")
        new = current[name].decode("utf-8")
        if previous.count(before) != 1 or previous.replace(before, after) != new:
            raise ValueError(f"Unexpected edit beyond the author-approval statement: {name}")
        tokens = re.findall(r"\d+(?:\.\d+)?", previous)
        if tokens != re.findall(r"\d+(?:\.\d+)?", new):
            raise ValueError(f"Numeric sequence changed: {name}")
        numerical_tokens[name] = len(tokens)
    unchanged = [name for name in CONFIRMED_SCOPE_PATHS if name not in AUTHOR_APPROVAL_EDITS]
    if any(old[name] != current[name] for name in unchanged):
        raise ValueError("An approved scientific payload changed")
    copies = json.loads((AUDIT/"preservation_manifest.json").read_text(encoding="utf-8-sig"))
    preserved = 0
    for row in copies["files"]:
        if row["source_copy_only"]:
            continue
        path = (AUDIT/row["relative_path"]).resolve()
        if not path.is_relative_to(AUDIT.resolve()):
            raise ValueError("Preservation path escapes the audit directory")
        payload = path.read_bytes()
        if len(payload) != row["bytes"] or sha256(payload) != row["sha256"]:
            raise ValueError("A preserved pending form or recount changed")
        preserved += 1
    frozen = verify_directory_manifest(ROOT/"phase17_v7/gateC9R/20260828_normalization_correction",
                                       "17_FILE_INTEGRITY_MANIFEST.csv")
    figures = verify_directory_manifest(ROOT/"phase17_v7/post_gateC9/20260828_advisor_correction_review",
                                        "02_REVIEW_FIGURE_MANIFEST.csv")
    preview = ROOT/"phase17_v7/post_gateC9/20260828_figure1_label_review"
    preview_record = json.loads((preview/"01_LABEL_CORRECTION_AUDIT.json").read_text())
    for row in preview_record["files"]:
        path = (preview/row["path"]).resolve()
        if not path.is_relative_to(preview):
            raise ValueError("Preview path escapes its directory")
        if path.stat().st_size != row["bytes"] or sha256(path.read_bytes()) != row["sha256"]:
            raise ValueError("Figure 1 correction preview changed")
    if (preview_record["generator_sha256"] != sha256((ROOT/"audit_tools/phase17_c7_01_build_main_figures.py").read_bytes())
            or not preview_record["source_data_byte_identical"]
            or not all(row["pass"] for row in preview_record["assertions"])):
        raise ValueError("Figure correction provenance is inconsistent")
    old_pages = ROOT/"00_project_management/external_review_2026-08-28/document_pages"
    changed, same = [], []
    for path in sorted((AUDIT/"document_pages").glob("*/*.png")):
        relative = path.relative_to(AUDIT/"document_pages")
        previous = old_pages/relative
        (same if previous.exists() and path.read_bytes() == previous.read_bytes() else changed).append(relative.as_posix())
    if len(same)+len(changed) != result["document_pages"]:
        raise ValueError("Current page images do not cover the rendered documents")
    draft = (AUDIT/"Journal_Format_Draft.md").read_text(encoding="utf-8")
    title = draft.split("## Candidate Title\n",1)[1].split("\n## ",1)[0].strip()
    abstract = draft.split("## Candidate Abstract\n",1)[1].split("\n## ",1)[0].strip()
    counts = {"title_words":len(title.split()), "abstract_whitespace_words":len(abstract.split()),
              "abstract_words_splitting_hyphens":len(re.findall(r"[A-Za-z0-9]+(?:,[0-9]+)*",abstract))}
    if counts["title_words"] > 15 or counts["abstract_words_splitting_hyphens"] > 150:
        raise ValueError("Editorial candidate exceeds its planned word limits")
    audit = {"status":"PASS_APPROVAL_SCOPE_AND_ADMINISTRATIVE_BUILD",
             "reviewed_package_sha256":receipt["reviewed_package"]["sha256"],
             "current_package_sha256":sha256(current_zip), "current_package_bytes":len(current_zip),
             "approved_scope_payloads":result["confirmed_scope_payloads"],
             "unchanged_payloads":len(unchanged), "unchanged_paths":unchanged,
             "administrative_sentence_changes":2, "unchanged_numeric_tokens":numerical_tokens,
             "preserved_records_verified":preserved, "frozen_c9_files_verified":len(frozen),
             "original_figure_source_files_verified":len(figures),
             "identical_page_images":len(same), "changed_page_images":changed,
             "figure1_preview_files_verified":len(preview_record["files"]),
             "figure1_preview_assertions_passed":len(preview_record["assertions"]),
             "editorial_draft_counts":counts,
             "known_issue_not_yet_integrated":"F1C_THRESHOLD_LABEL",
             "submission_authorized":False,
             "scope":"No model rerun. Two administrative source edits only in the confirmation package; Figure 1 correction is a separate preview. Visual inspection is recorded in the action report."}
    (AUDIT/"confirmation_consistency.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:value for key,value in audit.items() if key != "unchanged_paths"},indent=2))


if __name__ == "__main__":
    main()
