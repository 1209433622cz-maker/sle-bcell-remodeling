"""Portable integrity and boundary checks; Python standard library only."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile


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
    if status.get("matching_archive_doi") is not None or status.get("author_reapproval") != "PENDING":
        raise ValueError("No matching DOI or renewed author approval has been recorded")


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
    verify_document_provenance(entries,json.loads(entries["quality_control/document_build.json"])["documents"])
    if b"Renewed final approval of the corrected manuscript and supporting materials is pending." not in entries["sources/Manuscript.md"]:
        raise ValueError("Current manuscript must disclose pending renewed approval")
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
            "scope":"Sizes, hashes, complete manifests, DOCX structure and recorded review boundaries; not a numerical rerun or independent scientific review."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(verify_bundle(args.bundle), indent=2))
