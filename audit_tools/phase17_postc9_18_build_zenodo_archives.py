"""Build and verify the clean Zenodo research and source-code archives."""

import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

from phase17_postc9_16_verify_scientific_freeze import (
    C9R_HOLD,
    FREEZE,
    R1_HOLD,
    ROOT,
    require_confirmation,
    require_holds,
    scientific_hashes,
)


RELEASE = ROOT / "00_project_management/qiteng_r2_release_2026-08-29"
MANUSCRIPT = ROOT / "04_submission/zenodo_release/manuscript"
CORRECTED_CANDIDATE = ROOT / "04_submission/corrected_candidate.zip"
DEFAULT_OUTPUT = ROOT / "04_submission/zenodo_release/upload"
ARCHIVE_PREFIX = "SLE_Bcell_Remodeling_Archive/"
FIXED_ZIP_TIME = (2026, 8, 29, 0, 0, 0)
NEW_DOI = "10.5281/zenodo.22151739"
OLD_DOI = "10.5281/zenodo.22086892"
RECORD_ID = "22151739"


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def selected_candidate_entries():
    entries = {
        "additional_files/Supplementary_Information.docx": "supplementary/Supplementary_Information.docx",
        "additional_files/Supplementary_Information.pdf": "supplementary/Supplementary_Information.pdf",
        "sources/Supplementary_Information.md": "supplementary/Supplementary_Information.md",
        "additional_files/Figure_Source_Data.zip": "source_data/Figure_Source_Data.zip",
        "additional_files/Full_Statistical_Results.zip": "source_data/Full_Statistical_Results.zip",
        "additional_files/Regulator_Sensitivity.zip": "source_data/Regulator_Sensitivity.zip",
        "reproducibility/DATA_RETRIEVAL.md": "reproducibility/DATA_RETRIEVAL.md",
        "reproducibility/LICENSE": "reproducibility/LICENSE",
        "reproducibility/LICENSE_CONTENT_CC_BY_4.0.md": "reproducibility/LICENSE_CONTENT_CC_BY_4.0.md",
        "reproducibility/LICENSE_SCOPE.md": "reproducibility/LICENSE_SCOPE.md",
        "reproducibility/REPRODUCIBILITY.md": "reproducibility/REPRODUCIBILITY.md",
    }
    for number in range(1, 6):
        for suffix in ("pdf", "png"):
            source = f"figures/Figure_{number}.{suffix}"
            entries[source] = source
    for number in range(1, 11):
        for suffix in ("pdf", "png"):
            source = f"figures_supplementary/Supplementary_Figure_S{number}.{suffix}"
            entries[source] = f"figures/supplementary/Supplementary_Figure_S{number}.{suffix}"
    return entries


LOCAL_ENTRIES = {
    MANUSCRIPT / "Manuscript.docx": "manuscript/Manuscript.docx",
    MANUSCRIPT / "Manuscript.pdf": "manuscript/Manuscript.pdf",
    MANUSCRIPT / "Manuscript.md": "manuscript/Manuscript.md",
    FREEZE / "Scientific_Freeze.md": "governance/Scientific_Freeze.md",
    FREEZE / "User_Confirmation.txt": "governance/User_Confirmation.txt",
    FREEZE / "author_freeze.json": "governance/author_freeze.json",
    FREEZE / "frozen_evidence_manifest.csv": "governance/frozen_evidence_manifest.csv",
    ROOT / "phase17_v7/round6_q1_robustness/20260827_r1_hold_integration/06_AUDIT_AND_PROPAGATION_PREP_STATUS.json": "governance/R1_decision.json",
    ROOT / "phase17_v7/gateC9R/20260828_normalization_correction/15_GATE_C9A_PREFREEZE_DECISION.json": "governance/C9R_decision.json",
    ROOT / "phase17_v7/gateC9R/20260828_normalization_correction/07_MAPPER_CONFIDENCE_CALIBRATION.csv": "governance/C9R_mapper_confidence_calibration.csv",
    RELEASE / "administrative_manuscript_build.json": "quality_control/administrative_manuscript_build.json",
    RELEASE / "final_scientific_freeze_verification.json": "quality_control/final_scientific_freeze_verification.json",
    RELEASE / "manuscript_a11y.json": "quality_control/manuscript_accessibility.json",
    RELEASE / "manuscript_pdf_audit.json": "quality_control/manuscript_pdf_audit.json",
}


def read_candidate_manifest(archive):
    with archive.open("MANIFEST_SHA256.csv") as handle:
        rows = list(csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig", newline="")))
    return {row["relative_path"]: row for row in rows}


def add_payload(payload, provenance, archive_path, data, source_kind, source_path):
    if archive_path in payload:
        raise ValueError("Duplicate archive path: " + archive_path)
    payload[archive_path] = data
    provenance.append({
        "archive_path": archive_path,
        "source_kind": source_kind,
        "source_path": source_path,
        "bytes": str(len(data)),
        "sha256": digest(data),
    })


def csv_bytes(fieldnames, rows):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def make_metadata(source_commit):
    return {
        "title": "SLE B-cell remodeling analysis: code, source data and reproducible release",
        "resource_type": "software",
        "publication_date": "2026-08-29",
        "version": "1.1.0",
        "record_id": RECORD_ID,
        "doi": NEW_DOI,
        "supersedes_version_doi": OLD_DOI,
        "concept_doi": "10.5281/zenodo.22086891",
        "repository": "https://github.com/1209433622cz-maker/sle-bcell-remodeling",
        "source_commit": source_commit,
        "creators": [
            {
                "name": "Chen, Zhi",
                "orcid": "0009-0001-0072-5576",
                "affiliation": "School of Medicine, The Chinese University of Hong Kong, Shenzhen",
            },
            {
                "name": "Qi, Teng",
                "orcid": "0009-0007-7648-4776",
                "affiliation": "School of Medicine, The Chinese University of Hong Kong, Shenzhen",
                "contact_person": True,
            },
        ],
        "licenses": [
            {"id": "MIT", "scope": "Original project code"},
            {
                "id": "CC-BY-4.0",
                "scope": "Original manuscript, composite figures, documentation and project-generated derived source-data tables",
            },
        ],
        "scientific_boundaries": {
            "R1": R1_HOLD,
            "C9R": C9R_HOLD,
            "corrected_external_outcome_unlock_authorized": False,
            "causal_or_clinical_claim_authorized": False,
        },
        "excluded": [
            "raw or recomputable large matrices",
            "per-cell caches",
            "historical journal-specific cover letters and portal files",
            "superseded manuscript files",
            "credentials and local logs",
            "third-party writing-skill packages",
        ],
    }


def make_readme(source_commit):
    return f"""# SLE B-cell remodeling reproducibility archive

This archive accompanies DOI `{NEW_DOI}` and supersedes the initial archive at
`{OLD_DOI}`. The corresponding source-code snapshot is Git commit
`{source_commit}` and is distributed separately as `Source_Code.zip`.

## Scientific scope

The scientific manuscript is the author-confirmed QiTeng R2 baseline with only
three administrative updates: the reserved archive DOI, the reported approval
status and the matching archive reference. Nine scientific sections are hash-
identical to the frozen baseline. No analysis, statistic, figure or claim was
changed to create this archive.

R1 remains `{R1_HOLD}`. C9R remains `{C9R_HOLD}` and corrected external outcome
unlock remains false. These failures are preserved as evidence and must not be
relabelled, threshold-relaxed or retrospectively rescued. Regulatory and
response analyses are observational and do not establish causal binding, a
unique upstream ligand or clinical utility.

## Contents

- `manuscript/`: DOI-integrated DOCX, WPS-rendered PDF and Markdown source.
- `supplementary/`: unchanged supplementary information.
- `figures/`: five main figures and ten supplementary figures in PDF and PNG.
- `source_data/`: unchanged figure source data, full statistical results and
  regulator sensitivity archives.
- `governance/`: frozen author scope, R1/C9R decisions and mapper calibration.
- `quality_control/`: scientific-freeze, document, PDF and accessibility checks.
- `reproducibility/`: retrieval instructions and license scope.
- `SOURCE_PROVENANCE.csv` and `CONTENT_MANIFEST_SHA256.csv`: source mapping and
  byte-level integrity records.

Large public source matrices are not duplicated. GEO, CELLxGENE and all other
third-party resources retain their original terms. The MIT license applies to
original project code; CC BY 4.0 applies only to original manuscript content,
composite figures, documentation and project-generated derived source-data
tables as detailed in `reproducibility/LICENSE_SCOPE.md`.

This is a reproducibility archive, not a journal submission or a peer-reviewed
article. It contains no journal-specific cover letter or portal package.
"""


def build_source_archive(output, source_commit):
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", source_commit + "^{commit}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if resolved != source_commit:
        raise ValueError("Source commit must be the full resolved commit SHA")
    subprocess.run(
        [
            "git",
            "archive",
            "--format=zip",
            "--prefix=sle-bcell-remodeling/",
            f"--output={output}",
            source_commit,
        ],
        cwd=ROOT,
        check=True,
    )
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Source-code ZIP failed CRC verification")


def build_research_archive(output, source_commit):
    payload = {}
    provenance = []
    with zipfile.ZipFile(CORRECTED_CANDIDATE) as source:
        if source.testzip() is not None:
            raise ValueError("Corrected-candidate ZIP failed CRC verification")
        source_manifest = read_candidate_manifest(source)
        for source_path, archive_path in sorted(selected_candidate_entries().items()):
            if source_path not in source_manifest:
                raise ValueError("Missing corrected-candidate payload: " + source_path)
            data = source.read(source_path)
            row = source_manifest[source_path]
            if len(data) != int(row["bytes"]) or digest(data) != row["sha256"]:
                raise ValueError("Corrected-candidate payload changed: " + source_path)
            add_payload(payload, provenance, archive_path, data, "verified corrected candidate", source_path)

    for source_path, archive_path in sorted(LOCAL_ENTRIES.items(), key=lambda item: item[1]):
        data = source_path.read_bytes()
        add_payload(
            payload,
            provenance,
            archive_path,
            data,
            "current Git workspace or generated release candidate",
            source_path.relative_to(ROOT).as_posix(),
        )

    confirmation = json.loads((FREEZE / "author_freeze.json").read_text(encoding="utf-8-sig"))
    require_confirmation(confirmation)
    r1 = json.loads((ROOT / confirmation["R1_decision_path"]).read_text(encoding="utf-8-sig"))
    c9r = json.loads((ROOT / confirmation["C9R_decision_path"]).read_text(encoding="utf-8-sig"))
    require_holds(r1, c9r)
    manuscript_text = payload["manuscript/Manuscript.md"].decode("utf-8-sig")
    if scientific_hashes(manuscript_text) != confirmation["scientific_section_sha256"]:
        raise ValueError("Release manuscript differs from the frozen scientific baseline")
    if manuscript_text.count(NEW_DOI) != 2 or manuscript_text.count(OLD_DOI) != 1:
        raise ValueError("Administrative DOI references are not exact")
    pdf_audit = json.loads(payload["quality_control/manuscript_pdf_audit.json"])
    freeze_audit = json.loads(payload["quality_control/final_scientific_freeze_verification.json"])
    if pdf_audit["status"] != "PASS" or pdf_audit["renderer"] != "WPS Office":
        raise ValueError("Final WPS PDF audit did not pass")
    if freeze_audit["status"] != "PASS_FREEZE_INTEGRITY_NOT_SCIENTIFIC_GATE_PASS":
        raise ValueError("Scientific freeze verification did not pass")

    metadata = make_metadata(source_commit)
    payload["README.md"] = make_readme(source_commit).encode("utf-8")
    payload["Release_Metadata.json"] = (json.dumps(metadata, indent=2) + "\n").encode("utf-8")
    payload["SOURCE_PROVENANCE.csv"] = csv_bytes(
        ["archive_path", "source_kind", "source_path", "bytes", "sha256"],
        sorted(provenance, key=lambda row: row["archive_path"]),
    )
    manifest_rows = [
        {"relative_path": path, "bytes": str(len(data)), "sha256": digest(data)}
        for path, data in sorted(payload.items())
    ]
    payload["CONTENT_MANIFEST_SHA256.csv"] = csv_bytes(
        ["relative_path", "bytes", "sha256"], manifest_rows
    )

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(payload.items()):
            info = zipfile.ZipInfo(ARCHIVE_PREFIX + path, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)

    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Research archive failed CRC verification")
        expected = {ARCHIVE_PREFIX + path for path in payload}
        if set(archive.namelist()) != expected:
            raise ValueError("Research archive inventory mismatch")
        manifest_data = archive.read(ARCHIVE_PREFIX + "CONTENT_MANIFEST_SHA256.csv")
        rows = list(csv.DictReader(io.StringIO(manifest_data.decode("utf-8"))))
        if len(rows) != len(payload) - 1:
            raise ValueError("Research archive manifest count mismatch")
        for row in rows:
            data = archive.read(ARCHIVE_PREFIX + row["relative_path"])
            if len(data) != int(row["bytes"]) or digest(data) != row["sha256"]:
                raise ValueError("Research archive manifest verification failed")
        forbidden = re.compile(r"cover[_ -]?letter|portal|prior_snapshot|main_text", re.I)
        if any(forbidden.search(name) for name in archive.namelist()):
            raise ValueError("Research archive contains a forbidden stale submission path")
    return len(payload), len(manifest_rows), len(provenance)


def file_record(path):
    data = path.read_bytes()
    return {"name": path.name, "bytes": len(data), "sha256": digest(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--receipt", type=Path, default=RELEASE / "zenodo_archive_build.json")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise ValueError("--source-commit must be a full lowercase Git commit SHA")
    output_dir = args.output_dir.resolve()
    if not output_dir.is_relative_to((ROOT / "04_submission/zenodo_release").resolve()):
        raise ValueError("Output directory must remain within the local Zenodo release workspace")
    receipt = args.receipt.resolve()
    if not receipt.is_relative_to((ROOT / "00_project_management").resolve()):
        raise ValueError("Receipt must remain in project management")
    output_dir.mkdir(parents=True, exist_ok=True)
    source_zip = output_dir / "Source_Code.zip"
    research_zip = output_dir / "Research_Archive.zip"
    checksums = output_dir / "SHA256SUMS.txt"
    build_source_archive(source_zip, args.source_commit)
    payload_count, manifest_count, provenance_count = build_research_archive(
        research_zip, args.source_commit
    )
    records = [file_record(research_zip), file_record(source_zip)]
    checksums.write_text(
        "".join(f'{record["sha256"]}  {record["name"]}\n' for record in records),
        encoding="ascii",
    )
    outputs = records + [file_record(checksums)]
    result = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_LOCAL_ARCHIVES_VERIFIED_NOT_UPLOADED_OR_PUBLISHED",
        "zenodo_record_id": RECORD_ID,
        "reserved_doi": NEW_DOI,
        "source_commit": args.source_commit,
        "research_archive_files": payload_count,
        "manifest_rows": manifest_count,
        "provenance_rows": provenance_count,
        "scientific_sections_unchanged": True,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "corrected_external_outcome_unlock_authorized": False,
        "forbidden_stale_submission_files_present": False,
        "outputs": outputs,
        "uploaded": False,
        "published": False,
        "old_record_deleted": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
