"""Record exact candidate-vs-approved differences and preserve incoming review evidence."""

import argparse
import json
from pathlib import Path
import shutil

from verify_review_bundle import CANDIDATE_REPLACED, CONFIRMED_SCOPE_PATHS, archive_entries, sha256, verify_bundle
from phase17_postc9_10_prepare_corrected_candidate import BASELINE_SHA256


def file_record(path, root):
    return {"path":path.relative_to(root).as_posix(), "bytes":path.stat().st_size,
            "sha256":sha256(path.read_bytes())}


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--received", type=Path, action="append", default=[])
    args = parser.parse_args()
    bundle, audit = args.bundle.resolve(), args.audit_dir.resolve()
    if not bundle.is_relative_to(root/"04_submission") or not audit.is_relative_to(root/"00_project_management"):
        raise ValueError("Integration audit must stay in the project workspace")
    verification = verify_bundle(bundle)
    archive = bundle.with_suffix(".zip")
    current = archive_entries(archive.read_bytes())
    for name, payload in current.items():
        if (bundle/name).read_bytes() != payload:
            raise ValueError("ZIP and directory differ: " + name)
    baseline = root/"04_submission/author_confirmed_review.zip"
    if sha256(baseline.read_bytes()) != BASELINE_SHA256:
        raise ValueError("Prior author-confirmed package changed")
    prior = archive_entries(baseline.read_bytes())
    scope = [{"path":name,"byte_identical":prior[name] == current[name]} for name in CONFIRMED_SCOPE_PATHS]
    changed = {row["path"] for row in scope if not row["byte_identical"]}
    if changed != set(CANDIDATE_REPLACED):
        raise ValueError("Unexpected scientific-scope payload change")
    nested = archive_entries(current["additional_files/Figure_Source_Data.zip"])
    old_nested = archive_entries(prior["additional_files/Figure_Source_Data.zip"])
    if nested != old_nested:
        raise ValueError("Figure source data changed")
    previous_pages = root/"00_project_management/author_confirmation_2026-08-28/document_pages"
    pages = []
    for path in sorted((audit/"document_pages").rglob("page-*.png")):
        previous = previous_pages/path.relative_to(audit/"document_pages")
        pages.append({"page":path.relative_to(audit/"document_pages").as_posix(),
                      "sha256":sha256(path.read_bytes()),
                      "identical_to_previous":previous.exists() and path.read_bytes() == previous.read_bytes()})
    if len(pages) != verification["document_pages"]:
        raise ValueError("Page image set does not cover the current rendered documents")
    received = []
    (audit/"received").mkdir(exist_ok=True)
    for path in args.received:
        target = audit/"received"/path.name
        if target.exists() and target.read_bytes() != path.read_bytes():
            raise ValueError("Received review would overwrite different evidence")
        shutil.copy2(path, target)
        received.append(file_record(target, audit))
    result = {
        "status":"PASS_BOUNDED_CORRECTED_CANDIDATE_INTEGRATION", "verification":verification,
        "candidate_zip":file_record(archive, root),"prior_approved_zip":file_record(baseline, root),
        "science_scope_comparison":scope,"unchanged_science_payloads":sum(row["byte_identical"] for row in scope),
        "all_three_statistical_archives_byte_identical":all(
            prior["additional_files/"+name+".zip"] == current["additional_files/"+name+".zip"]
            for name in ("Figure_Source_Data","Full_Statistical_Results","Regulator_Sensitivity")),
        "figure_source_tables_byte_identical":15,
        "page_image_comparison":pages,"unchanged_page_images":sum(row["identical_to_previous"] for row in pages),
        "changed_page_images":[row["page"] for row in pages if not row["identical_to_previous"]],
        "received_documents":received,
        "scope":"Exact editorial delta and artifact integrity, not a new numerical analysis or independent review",
        "submission_authorized":False}
    (audit/"candidate_integration_audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:result[key] for key in ("status","candidate_zip","unchanged_science_payloads",
                     "all_three_statistical_archives_byte_identical","unchanged_page_images","changed_page_images")},indent=2))


if __name__ == "__main__":
    main()
