"""Portable integrity and boundary checks; Python standard library only."""

import argparse
import csv
from datetime import date
import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile


CONFIRMED = "CONFIRMED_REVIEWED_SNAPSHOT"
AUTHOR_APPROVAL_EDITS = {
    "sources/Manuscript.md": (
        "Both authors approved the earlier materials. Renewed final approval of the corrected manuscript and supporting materials is pending.",
        "Both authors have approved the corrected manuscript and supporting materials.",
    ),
    "sources/Cover_Letter.md": (
        "The revised materials and final journal choice require renewed author approval before submission; this review letter is not evidence of that approval.",
        "Both authors have approved the corrected review materials. Journal choice, final formatted files and submission authorization remain to be confirmed.",
    ),
}
CONFIRMED_SCOPE_PATHS = (
    tuple("sources/" + name + ".md" for name in
          ("Manuscript", "Supplementary_Information", "Research_Proposal", "Cover_Letter"))
    + tuple(f"figures/Figure_{number}.{ext}" for number in range(1, 6) for ext in ("pdf", "png"))
    + tuple(f"figures_supplementary/Supplementary_Figure_S{number}.{ext}"
            for number in range(1, 11) for ext in ("pdf", "png"))
    + tuple("additional_files/" + name + ".zip" for name in
            ("Figure_Source_Data", "Full_Statistical_Results", "Regulator_Sensitivity"))
    + tuple("reproducibility/" + name for name in
            ("phase17_c9_common.py", "phase17_c9_01_prefreeze_label_agnostic_mapping.py",
             "phase17_c9_02_unlock_outcomes_and_review.py",
             "run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1"))
)


def sha256(payload):
    return hashlib.sha256(payload).hexdigest().upper()


def safe_name(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or "\\" in name or ":" in name or any(part in {"", ".", ".."} for part in name.split("/")):
        raise ValueError(f"Unsafe payload path: {name}")
    return name


def csv_records(payload):
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))


def verify_entries(entries, manifest_name):
    rows = csv_records(entries[manifest_name])
    if not rows:
        raise ValueError("Empty manifest")
    names = set()
    for row in rows:
        name = safe_name(row.get("relative_path", row.get("file", row.get("filename", ""))))
        if name in names or name == manifest_name:
            raise ValueError(f"Duplicate or self-referencing manifest entry: {name}")
        names.add(name)
        if name not in entries:
            raise ValueError(f"Missing payload: {name}")
        payload = entries[name]
        size = row.get("bytes", row.get("size_bytes"))
        if len(payload) != int(size) or sha256(payload) != row["sha256"].upper():
            raise ValueError(f"Size/hash mismatch: {name}")
    if set(entries) != names | {manifest_name}:
        raise ValueError("Manifest does not describe the complete payload set")
    return len(rows)


def archive_entries(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entries")
        for name in names:
            safe_name(name)
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC failure")
        return {name:archive.read(name) for name in names}


def require_review_status(status):
    if status.get("review_only") is not True or status.get("submission_authorized") is not False:
        raise ValueError("This correction bundle must remain review-only")
    if status.get("corrected_disease_outcomes_estimated") is not False:
        raise ValueError("Corrected disease outcomes must remain unestimated")
    if (status.get("matching_archive_doi") is not None or status.get("target_journal") is not None
            or status.get("author_reapproval") not in {"PENDING", CONFIRMED}):
        raise ValueError("No matching DOI or final submission approval has been recorded")


def verify_confirmation_receipt(entries, gate):
    key = "governance/author_confirmation.json"
    manifest_key = "governance/Reviewed_Package_MANIFEST_SHA256.csv"
    if key not in entries or manifest_key not in entries:
        raise ValueError("Confirmed author reapproval requires a receipt and reviewed manifest")
    if sha256(entries[key]) != gate.get("confirmation_evidence_sha256"):
        raise ValueError("Confirmation evidence hash mismatch")
    receipt = json.loads(entries[key])
    if (receipt.get("record_type") != "USER_MESSAGE_REPORTING_BOTH_AUTHORS"
            or receipt.get("authors") != ["Zhi Chen", "Teng Qi"]
            or not isinstance(receipt.get("statement"), str) or not receipt["statement"].strip()
            or receipt.get("current_content_confirmed") is not True
            or receipt.get("external_feedback_and_disposition_considered") is not True
            or gate.get("author_review_of_external_feedback") is not True):
        raise ValueError("Receipt does not record both authors' current-content confirmation")
    reserved = ("independently_collected_author_signatures", "external_reviewer_identity_authenticated",
                "target_journal_selected", "apc_commitment_authorized", "new_archive_release_authorized",
                "future_material_changes_preapproved", "submission_authorized")
    if any(receipt.get(key) is not False for key in reserved):
        raise ValueError("Author confirmation cannot authorize reserved actions")
    try:
        recorded_date = date.fromisoformat(receipt["confirmation_date"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid author confirmation date") from exc
    if any(row.get("date") != recorded_date.isoformat() or row.get("evidence") != "author_confirmation.json"
           for row in gate["authors"]):
        raise ValueError("Author dates and evidence do not match the receipt")
    reviewed = receipt.get("reviewed_package", {})
    digest = reviewed.get("sha256", "")
    if (not re.fullmatch(r"[0-9A-F]{64}", digest) or digest != gate.get("reviewed_package_sha256")
            or reviewed.get("manifest_sha256") != sha256(entries[manifest_key])
            or not isinstance(reviewed.get("bytes"), int) or reviewed["bytes"] <= 0):
        raise ValueError("Reviewed snapshot identity mismatch")
    safe_name(reviewed["path"])
    return receipt


def verify_confirmed_snapshot_scope(entries, gate):
    """Approval follows the reviewed content, not arbitrary later payloads."""
    verify_confirmation_receipt(entries, gate)
    receipt = json.loads(entries["governance/author_confirmation.json"])
    supplemental = receipt.get("supplemental_document_approval")
    if supplemental is not None:
        approved = supplemental.get("approved_source_sha256", {})
        if (set(approved) != set(AUTHOR_APPROVAL_EDITS) or not supplemental.get("statement")
                or supplemental.get("confirmation_date") != receipt["confirmation_date"]):
            raise ValueError("Incomplete supplemental manuscript and cover-letter approval")
        if any(name not in entries or sha256(entries[name]) != digest for name,digest in approved.items()):
            raise ValueError("Current manuscript or cover letter differs from its explicit approval")
    rows = csv_records(entries["governance/Reviewed_Package_MANIFEST_SHA256.csv"])
    reference = {}
    for row in rows:
        name = safe_name(row["relative_path"])
        if name in reference:
            raise ValueError("Duplicate reviewed manifest entry")
        reference[name] = row
    for name in CONFIRMED_SCOPE_PATHS:
        if name not in entries or name not in reference:
            raise ValueError(f"Reviewed scientific payload missing: {name}")
        payload = entries[name]
        if name in AUTHOR_APPROVAL_EDITS:
            before, after = AUTHOR_APPROVAL_EDITS[name]
            text = payload.decode("utf-8")
            if text.count(after) != 1 or before in text:
                raise ValueError(f"Administrative approval statement missing: {name}")
            payload = text.replace(after, before).encode("utf-8")
        row = reference[name]
        if sha256(payload) != row["sha256"] or len(payload) != int(row["bytes"]):
            raise ValueError(f"Unapproved content change outside the administrative update: {name}")
    return len(CONFIRMED_SCOPE_PATHS)


def verify_review_governance(entries):
    names = {"Author_Confirmation.md", "Reporting_Checklist.md", "External_Methods_Review.md", "review_gate.json"}
    if not all("governance/" + name in entries for name in names):
        raise ValueError("Current review governance records are incomplete")
    gate = json.loads(entries["governance/review_gate.json"])
    if gate.get("gate") != "EXTERNAL_METHODS_REVIEW_AND_AUTHOR_REAPPROVAL_GATE":
        raise ValueError("Unexpected review gate")
    if (gate.get("external_feedback_received") is not True
            or gate.get("external_methods_review_status") != "FEEDBACK_RECEIVED_CLOSURE_PENDING"
            or gate.get("reviewer_identity") is not None
            or gate.get("reviewer_independence_confirmed") is not False
            or gate.get("external_methods_review_decision") is not None):
        raise ValueError("Feedback cannot be promoted to external methods approval")
    authors = gate.get("authors", [])
    if len(authors) != 2 or {row.get("name") for row in authors} != {"Zhi Chen", "Teng Qi"}:
        raise ValueError("Current author reapproval requires the two named authors")
    decisions = {row.get("decision") for row in authors}
    if (gate.get("submission_authorized") is not False or gate.get("target_journal") is not None
            or gate.get("matching_archive_doi") is not None):
        raise ValueError("Review governance cannot authorize a release or submission")
    author_text = entries["governance/Author_Confirmation.md"].decode("utf-8-sig")
    if decisions == {"PENDING"}:
        if any(row.get("date") is not None or row.get("evidence") is not None for row in authors):
            raise ValueError("Pending author reapproval cannot have approval evidence")
        if re.search(r"(?im)^\s*[-*]\s+\[x\]", author_text):
            raise ValueError("Pending author form contains checked approval boxes")
    elif decisions == {CONFIRMED}:
        receipt = verify_confirmation_receipt(entries, gate)
        if CONFIRMED not in author_text or receipt["reviewed_package"]["sha256"] not in author_text:
            raise ValueError("Author form does not identify the confirmed reviewed snapshot")
        sections = author_text.split("## Decisions reserved for the authors", 1)
        if len(sections) != 2 or re.search(r"(?im)^\s*[-*]\s+\[x\]", sections[1]):
            raise ValueError("Reserved author decisions must remain unchecked")
    else:
        raise ValueError("Current author reapproval has an unsupported or mixed decision")
    checklist = entries["governance/Reporting_Checklist.md"].decode("utf-8-sig")
    if "Earlier package record" in checklist or "46/46" in checklist:
        raise ValueError("Historical acceptance checks leaked into the current checklist")
    issue = gate.get("postapproval_presentation_issue")
    if issue is not None:
        record = "governance/" + safe_name(issue.get("record", ""))
        if (issue.get("id") != "F1C_THRESHOLD_LABEL" or issue.get("scientific_values_changed") is not False
                or issue.get("status") != "CORRECTED_PREVIEW_NOT_YET_INTEGRATED" or record not in entries):
            raise ValueError("Known postapproval presentation issue is not fully disclosed")
    return gate


def verify_document_provenance(entries, records):
    if len(records) != 4:
        raise ValueError("Four source-to-DOCX build records are required")
    for row in records:
        source = "sources/"+PurePosixPath(row["source"]).name
        matches = [payload for name,payload in entries.items() if PurePosixPath(name).name == PurePosixPath(row["output"]).name]
        if sha256(entries[source]) != row["source_sha256"] or len(matches) != 1 or sha256(matches[0]) != row["docx_sha256"]:
            raise ValueError("Markdown and rendered DOCX were built from different snapshots")


def verify_bundle(root):
    root = root.resolve()
    entries = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlinks are not permitted in the review bundle")
        if path.is_file():
            name = safe_name(path.relative_to(root).as_posix())
            entries[name] = path.read_bytes()
    count = verify_entries(entries, "MANIFEST_SHA256.csv")
    status = json.loads(entries["STATUS.json"])
    require_review_status(status)
    governance = verify_review_governance(entries)
    author_state = governance["authors"][0]["decision"]
    if status["author_reapproval"] != author_state:
        raise ValueError("Package and author confirmation status disagree")
    if status.get("external_methods_review_status") != governance["external_methods_review_status"]:
        raise ValueError("Package and review governance status disagree")
    for key in ("journal_requirement", "postapproval_presentation_issue"):
        if status.get(key) != governance.get(key):
            raise ValueError(f"Package and governance disagree on {key}")
    verify_document_provenance(entries,json.loads(entries["quality_control/document_build.json"])["documents"])
    confirmed_scope = 0
    if author_state == CONFIRMED:
        confirmed_scope = verify_confirmed_snapshot_scope(entries, governance)
        if status.get("reviewed_package_sha256") != governance["reviewed_package_sha256"]:
            raise ValueError("Package and author-approved snapshot disagree")
        if status.get("author_review_of_external_feedback") is not True:
            raise ValueError("Package omits recorded author consideration of feedback")
    elif b"Renewed final approval of the corrected manuscript and supporting materials is pending." not in entries["sources/Manuscript.md"]:
        raise ValueError("Pending manuscript must disclose pending renewed approval")
    archives = {}
    for name, manifest in (("Figure_Source_Data.zip", "MANIFEST_SHA256.csv"),
                           ("Full_Statistical_Results.zip", "MANIFEST_SHA256.csv"),
                           ("Regulator_Sensitivity.zip", "SHA256SUMS.csv")):
        content = archive_entries(entries[f"additional_files/{name}"])
        archives[name] = {"members":verify_entries(content, manifest), "content":content}
    sources = archives["Figure_Source_Data.zip"]["content"]
    if len([name for name in sources if name.endswith("_source_data.csv")]) != 15:
        raise ValueError("Expected source tables for 5 main and 10 supplementary figures")
    stats = archives["Full_Statistical_Results.zip"]["content"]
    prefix = "external_mapping_calibration/"
    if governance["scientific_input_manifest_sha256"] != sha256(stats[prefix+"01_INPUT_SHA256_MANIFEST.csv"]):
        raise ValueError("Review gate refers to different scientific inputs")
    extension = {name:payload for name,payload in stats.items() if name.startswith(prefix)}
    if len(extension) != 20:
        raise ValueError("Corrected calibration attachment must contain 20 documented files")
    decision = json.loads(stats[prefix+"15_GATE_C9A_PREFREEZE_DECISION.json"])
    if decision["decision"] != "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED" or decision["outcome_unlock_authorized"] is not False:
        raise ValueError("Correction HOLD was changed")
    calibration = csv_records(stats[prefix+"07_MAPPER_CONFIDENCE_CALIBRATION.csv"])
    selected = [row for row in calibration if row["mapper"] == "elastic_net" and row["selected"].lower() == "true"]
    if len(calibration) != 72 or len(selected) != 1 or float(selected[0]["B_ASC_precision"]) >= .90:
        raise ValueError("Frozen calibration family or failed precision was changed")
    if any(row["eligible"].lower() == "true" for row in calibration if row["mapper"] == "elastic_net"):
        raise ValueError("Ineligible primary mapper was promoted")
    excluded = {"03_REFERENCE_LIBRARY_SIZE_AUDIT.csv", "08_REFERENCE_OOF_PREDICTIONS.csv", "10_CELL_PREDICTIONS_LOCAL.csv.gz"}
    if any(PurePosixPath(name).name in excluded for name in extension):
        raise ValueError("Local per-cell export was packaged")
    if sources["Supplementary_Figure_S10_source_data.csv"] != stats[prefix+"Supplementary_Figure_S10_source_data.csv"]:
        raise ValueError("S10 source differs across attachments")
    portal = csv_records(entries["PORTAL_FILES.csv"])
    if len(portal) != 11 or any(row["authorization"] != "DRAFT_NOT_FOR_UPLOAD" for row in portal):
        raise ValueError("Draft portal map changed")
    for row in portal:
        payload = entries[safe_name(row["path"])]
        if sha256(payload) != row["sha256"] or len(payload) != int(row["bytes"]):
            raise ValueError("Portal map differs from payload")
    render = json.loads(entries["quality_control/document_render_audit.json"])
    hashes = render["document_hashes"]
    if len(hashes) != 8 or not render["all_pages_within_canvas"] or not render["all_markers_resolved"]:
        raise ValueError("Incomplete four-document rendering evidence")
    for row in hashes:
        matches = [payload for name,payload in entries.items() if PurePosixPath(name).name == row["file"]]
        if len(matches) != 1 or sha256(matches[0]) != row["sha256"] or len(matches[0]) != row["bytes"]:
            raise ValueError(f"Render evidence does not match {row['file']}")
    for name,payload in entries.items():
        if name.endswith(".docx"):
            content = archive_entries(payload)
            xml = ET.fromstring(content["word/document.xml"])
            if "[[SUPPLEMENTARY_FIGURE" in " ".join(xml.itertext()):
                raise ValueError("Unresolved figure marker")
            if name.endswith("Supplementary_Information.docx"):
                if len(xml.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline")) != 10:
                    raise ValueError("Supplement must embed ten figures")
    a11y = json.loads(entries["quality_control/accessibility.json"])
    if len(a11y) != 4 or any(any(record["counts"].values()) for record in a11y):
        raise ValueError("Document accessibility review is incomplete")
    return {"status":"PASS_PORTABLE_TECHNICAL_VERIFICATION", "payload_files":count,
            "nested_manifest_rows":{name:record["members"] for name,record in archives.items()},
            "document_pages":render["pages"],"submission_authorized":False,
            "external_methods_review_status":governance["external_methods_review_status"],
            "author_reapproval":author_state,"confirmed_scope_payloads":confirmed_scope,
            "postapproval_presentation_issue":governance.get("postapproval_presentation_issue"),
            "scope":"Sizes, hashes, complete manifests, DOCX structure and recorded review boundaries; not a numerical rerun or independent scientific review."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(verify_bundle(args.bundle), indent=2))
