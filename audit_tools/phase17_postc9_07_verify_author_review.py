"""Verify the bounded external-review edit against the preserved prior bundle."""

import json
from pathlib import Path
import re

from phase17_postc9_06_build_correction_package import verify_directory_manifest
from verify_review_bundle import archive_entries, sha256, verify_bundle


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "00_project_management/external_review_2026-08-28"
FIGURES = ROOT / "phase17_v7/post_gateC9/20260828_advisor_correction_review"
C9 = ROOT / "phase17_v7/gateC9R/20260828_normalization_correction"
EDITS = (
    ("Reference donor-grouped cross-validation selected regularization and confidence thresholds.",
     "Reference donor-grouped cross-validation evaluated regularization and candidate confidence thresholds under prespecified state-specific eligibility criteria."),
    ("The conventional-B mapping in GSE135779 relies on source labels and supports a broad analog rather than exact identity transfer.",
     "The conventional-B mapping in GSE135779 relies on source labels and supports a broad analog rather than exact identity transfer. A post-freeze attempt to reconstruct external B-lineage selection without source labels failed its frozen B_ASC reference-calibration criterion after normalization was corrected, so no corrected disease outcome was estimated."),
)


def main():
    current_root = ROOT / "04_submission/author_review"
    verification = verify_bundle(current_root)
    old_zip = (ROOT / "04_submission/correction_review.zip").read_bytes()
    if sha256(old_zip) != "DA07D1D7F87E559A7778618FDFAE5BD55DA77291E1F0BAA44B915CDE209B5993":
        raise ValueError("The preserved previous review ZIP changed")
    old = archive_entries(old_zip)
    current_zip = (ROOT / "04_submission/author_review.zip").read_bytes()
    current = archive_entries(current_zip)
    disk = {p.relative_to(current_root).as_posix(): p.read_bytes()
            for p in current_root.rglob("*") if p.is_file()}
    if current != disk:
        raise ValueError("Current ZIP and extracted bundle differ")
    unchanged = [name for name in old if name.startswith(("figures/", "figures_supplementary/"))]
    if len(unchanged) != 30:
        raise ValueError("Expected thirty figure files")
    unchanged += ["additional_files/"+name for name in
                  ("Figure_Source_Data.zip", "Full_Statistical_Results.zip", "Regulator_Sensitivity.zip")]
    unchanged += ["sources/"+name+".md" for name in
                  ("Supplementary_Information", "Research_Proposal", "Cover_Letter")]
    unchanged += ["reproducibility/"+name for name in (
        "phase17_c9_common.py", "phase17_c9_01_prefreeze_label_agnostic_mapping.py",
        "phase17_c9_02_unlock_outcomes_and_review.py",
        "run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1")]
    for name in unchanged:
        if current[name] != old[name]:
            raise ValueError(f"Unexpected content change: {name}")
    before = old["sources/Manuscript.md"].decode("utf-8")
    after = current["sources/Manuscript.md"].decode("utf-8")
    expected = before
    for source, replacement in EDITS:
        if expected.count(source) != 1:
            raise ValueError("Expected edit anchor is not unique")
        expected = expected.replace(source, replacement)
    if expected != after:
        raise ValueError("Manuscript has edits beyond the two reviewed sentences")
    numbers = re.findall(r"\d+(?:\.\d+)?", before)
    if numbers != re.findall(r"\d+(?:\.\d+)?", after):
        raise ValueError("Manuscript numeric-token sequence changed")
    receipt = json.loads((AUDIT / "received_and_history_manifest.json").read_text(encoding="utf-8-sig"))
    for row in receipt["files"]:
        path = (AUDIT / row["relative_path"]).resolve()
        if not path.is_relative_to(AUDIT.resolve()):
            raise ValueError("Received-record path escapes audit directory")
        payload = path.read_bytes()
        if len(payload) != row["bytes"] or sha256(payload) != row["sha256"]:
            raise ValueError("A received or historical record changed")
    frozen = verify_directory_manifest(C9, "17_FILE_INTEGRITY_MANIFEST.csv")
    figure_files = verify_directory_manifest(FIGURES, "02_REVIEW_FIGURE_MANIFEST.csv")
    previous_pages = ROOT / "00_project_management/post_gateC9_release_review_2026-08-28/document_pages"
    pages = []
    for path in sorted((AUDIT / "document_pages").glob("*/*.png")):
        relative = path.relative_to(AUDIT / "document_pages")
        original = previous_pages / relative
        pages.append({"page_image": relative.as_posix(),
                      "identical_to_previous": original.exists() and path.read_bytes() == original.read_bytes()})
    if len(pages) != verification["document_pages"]:
        raise ValueError("Page images do not cover every rendered page")
    result = {"status":"PASS_BOUNDED_EDITORIAL_CONSISTENCY",
              "bundle_zip_sha256":sha256(current_zip), "bundle_zip_bytes":len(current_zip),
              "unchanged_package_payloads":len(unchanged), "unchanged_paths":unchanged,
              "manuscript_exact_edits":len(EDITS), "unchanged_numeric_tokens":len(numbers),
              "received_history_and_recount_files_verified":len(receipt["files"]),
              "frozen_c9_files_verified":len(frozen), "figure_source_files_verified":len(figure_files),
              "identical_page_images":sum(row["identical_to_previous"] for row in pages),
              "changed_page_images":[row["page_image"] for row in pages if not row["identical_to_previous"]],
              "scope":"Content and byte-level comparison; changed pages require separately recorded visual inspection; no scientific model rerun."}
    (AUDIT / "post_edit_consistency.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({key:value for key,value in result.items() if key != "unchanged_paths"}, indent=2))


if __name__ == "__main__":
    main()
