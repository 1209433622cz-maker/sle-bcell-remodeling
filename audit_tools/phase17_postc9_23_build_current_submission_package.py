"""Build and verify the current journal-neutral submission preflight package."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "00_project_management/current_submission_package_2026-08-30"
RESEARCH_ARCHIVE = ROOT / "04_submission/zenodo_release/upload/Research_Archive.zip"
ARCHIVE_PREFIX = "SLE_Bcell_Remodeling_Archive/"
ARCHIVE_SHA256 = "AAE67863FC6B34B0AC091F8D38524FFC55A7CF364FF7FF4B4D43FEDFA4AE0095"
OUTPUT_ROOT = ROOT / "04_submission/current_submission_package"
PACKAGE_NAME = "SLE_Bcell_Submission_Package"
PACKAGE_DIR = OUTPUT_ROOT / PACKAGE_NAME
PACKAGE_ZIP = OUTPUT_ROOT / (PACKAGE_NAME + ".zip")
CHECKSUM_FILE = OUTPUT_ROOT / (PACKAGE_NAME + "_SHA256.txt")
RECEIPT = WORK / "package_build.json"
FIXED_ZIP_TIME = (2026, 8, 30, 0, 0, 0)
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"
CURRENT_DOI = "10.5281/zenodo.22151739"
TITLE = "Disease-blind single-cell reconstruction distinguishes unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def checksum(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def safe_relative(root, value):
    path = Path(value)
    require(not path.is_absolute(), "Manifest path must be relative: " + value)
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), "Manifest path escapes package: " + value)
    return resolved


def archive_entries():
    entries = {
        "manuscript/Manuscript.docx": "01_Manuscript/Manuscript.docx",
        "manuscript/Manuscript.pdf": "01_Manuscript/Manuscript.pdf",
        "supplementary/Supplementary_Information.docx": "02_Supplementary_Information/Supplementary_Information.docx",
        "supplementary/Supplementary_Information.pdf": "02_Supplementary_Information/Supplementary_Information.pdf",
        "source_data/Figure_Source_Data.zip": "05_Source_Data/Figure_Source_Data.zip",
        "source_data/Full_Statistical_Results.zip": "05_Source_Data/Full_Statistical_Results.zip",
        "source_data/Regulator_Sensitivity.zip": "05_Source_Data/Regulator_Sensitivity.zip",
    }
    for number in range(1, 6):
        entries[f"figures/Figure_{number}.pdf"] = f"03_Main_Figures/Figure_{number}.pdf"
    for number in range(1, 11):
        entries[f"figures/supplementary/Supplementary_Figure_S{number}.pdf"] = (
            f"04_Supplementary_Figures/Supplementary_Figure_S{number}.pdf"
        )
    return entries


def cover_letter_text(path):
    with zipfile.ZipFile(path) as archive:
        parts = ["word/document.xml"] + sorted(
            name for name in archive.namelist() if name.startswith("word/footer") and name.endswith(".xml")
        )
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    text = []
    with zipfile.ZipFile(path) as archive:
        for part in parts:
            root = ET.fromstring(archive.read(part))
            text.extend(node.text or "" for node in root.iter(namespace + "t"))
    return " ".join(text)


def verify_cover_letter(path):
    text = cover_letter_text(path)
    for phrase in (
        TITLE,
        CURRENT_DOI,
        "permanent R1 HOLD",
        "C9R HOLD",
        "no corrected external disease outcome was estimated",
        "ten supplementary figures",
        "exact-file author approval pending",
    ):
        require(phrase in text, "Cover-letter DOCX boundary is missing: " + phrase)
    for stale in ("Genome Medicine", "10.5281/zenodo.22086892", "matching revised archive remains required"):
        require(stale not in text, "Cover-letter DOCX retains stale text: " + stale)


def csv_bytes(fieldnames, rows):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def read_archive_manifest(archive):
    data = archive.read(ARCHIVE_PREFIX + "CONTENT_MANIFEST_SHA256.csv")
    rows = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    return {row["relative_path"]: row for row in rows}


def readme_text():
    return f"""# Read me first

This is a journal-neutral editorial preflight package for:

{TITLE}

## Current status

- Scientific baseline: author-confirmed QiTeng R2.
- Reproducibility archive: doi:{CURRENT_DOI}.
- Target journal: not selected.
- Official JCR Q1 evidence: not yet archived.
- Institutional APC/OA eligibility: not yet verified.
- Target-specific formatting: not started.
- Exact-file author approval for this package: pending.
- Journal submission and APC commitment: not authorized.

Do not upload this ZIP or its files to a journal portal. After a JCR Q1 target is
frozen, adapt only the title, abstract, section structure, declarations, figure
dimensions and cover letter required by that journal; rebuild and obtain approval
of the exact final file hashes before any portal action.

## Inventory

- `01_Manuscript/`: current 18-page DOCX and WPS-rendered PDF.
- `02_Supplementary_Information/`: current DOCX and PDF.
- `03_Main_Figures/`: five vector PDF figures.
- `04_Supplementary_Figures/`: ten vector PDF supplementary figures.
- `05_Source_Data/`: figure source data, full statistics and regulator sensitivity.
- `06_Administrative/`: journal-neutral cover-letter draft, authors/declarations and readiness status.
- `07_Integrity/`: machine-readable metadata, SHA-256 manifest and self-verifier.

All scientific files were copied byte-for-byte from the publicly verified Zenodo
Research Archive. The cover letter is newly generated administrative material and
is explicitly marked as a draft. R1 remains `{R1_HOLD}`; C9R remains `{C9R_HOLD}`;
no corrected external disease outcome was estimated.

Run `python 07_Integrity/Verify_Package.py` from the package root to verify every
listed file. The ZIP-level SHA-256 is stored beside the ZIP.
"""


def author_text():
    return """# Authors and declarations

## Authors

- First author: Zhi Chen; MSc student in Bioinformatics; zhichen1@link.cuhk.edu.cn; ORCID 0009-0001-0072-5576.
- Corresponding author: Teng Qi; MSc student in Bioinformatics; tengqi@link.cuhk.edu.cn; ORCID 0009-0007-7648-4776.
- Affiliation: School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen 518172, China.

## Author contributions

ZC: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft. TQ: Conceptualization, Methodology, Project administration, Validation, Writing - review and editing.

## Confirmed declarations

- Ethics: secondary analysis of publicly available, de-identified human transcriptomic data; no participant recruitment, intervention or new specimen collection; no additional ethics approval required for this secondary analysis. Source-study ethics and consent remain governed by the original publications.
- Consent for publication: not applicable; no identifiable participant information is included.
- Competing interests: none declared.
- Funding: no specific funding.
- Acknowledgements: not applicable.
- Originality and exclusivity: original work and not under consideration by another journal.
- Generative AI: disclosed in the manuscript; authors retain responsibility for all analyses, code, text, references, figures and source data.
- Licences: MIT for original code; CC BY 4.0 for original manuscript content, composite figures, documentation and project-generated derived source-data tables; third-party data are not relicensed.

These statements reproduce the author-confirmed scientific baseline and supplied declarations. They are a portal-entry aid, not independently collected signatures or an institutional ethics/APC determination. Exact target-formatted files still require author approval.
"""


def readiness_text():
    return f"""# Submission readiness

Status: JOURNAL_NEUTRAL_PACKAGE_VERIFIED_NOT_AUTHORIZED_FOR_SUBMISSION

- [x] Current scientific baseline included.
- [x] Five main and ten supplementary figures included.
- [x] Figure source data, full statistical results and regulator sensitivity included.
- [x] Current Zenodo DOI included.
- [x] R1 and C9R HOLD boundaries preserved.
- [ ] Target journal selected using archived JCR Q1 evidence.
- [ ] Institutional APC/OA route verified.
- [ ] Journal-specific formatting completed.
- [ ] Journal-specific cover letter completed.
- [ ] Exact final DOCX/PDF/figure hashes approved by both authors.
- [ ] Journal submission explicitly authorized.
- [ ] APC commitment explicitly authorized.

Current conditional fit lead: npj Systems Biology and Applications.
Second conditional candidate: Communications Biology.
Selected target: none.

The cover-letter draft deliberately omits a journal-specific fit paragraph. Do not
convert either `{R1_HOLD}` or `{C9R_HOLD}` into a PASS and do not unlock corrected
external disease outcomes during target adaptation.
"""


def verifier_text():
    return r'''"""Verify this extracted submission package against its SHA-256 manifest."""

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "07_Integrity/FILE_MANIFEST_SHA256.csv"


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
expected = {row["relative_path"] for row in rows} | {"07_Integrity/FILE_MANIFEST_SHA256.csv"}
observed = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()}
if observed != expected:
    raise SystemExit("FAIL: package inventory differs")
for row in rows:
    relative = Path(row["relative_path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise SystemExit("FAIL: unsafe manifest path")
    path = ROOT / relative
    if path.stat().st_size != int(row["bytes"]) or checksum(path) != row["sha256"].upper():
        raise SystemExit("FAIL: " + row["relative_path"])
print(f"PASS: {len(rows)} files verified; package is integrity-valid but not authorized for submission")
'''


def metadata(packaging_commit):
    return {
        "created_date": "2026-08-30",
        "status": "JOURNAL_NEUTRAL_PACKAGE_VERIFIED_NOT_AUTHORIZED_FOR_SUBMISSION",
        "manuscript_title": TITLE,
        "scientific_baseline": "QiTeng R2",
        "source_archive": "Research_Archive.zip",
        "source_archive_sha256": ARCHIVE_SHA256,
        "source_archive_doi": CURRENT_DOI,
        "scientific_release_content_commit": "f1859ff8498d5569a1d5027b36ed18c8b7c7536f",
        "packaging_parent_commit": packaging_commit,
        "selected_target": None,
        "jcr_q1_verified": False,
        "institutional_apc_coverage_verified": False,
        "target_specific_adaptation_started": False,
        "exact_package_author_approved": False,
        "submission_authorized": False,
        "apc_commitment_authorized": False,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "corrected_external_outcome_unlock_authorized": False,
        "new_scientific_analysis_performed": False,
        "new_scientific_file_created": False,
        "cover_letter_status": "JOURNAL_NEUTRAL_DRAFT_EXACT_FILE_APPROVAL_PENDING",
    }


def verify_manifest(package_dir):
    manifest = package_dir / "07_Integrity/FILE_MANIFEST_SHA256.csv"
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(rows, "Package manifest is empty")
    listed = {row["relative_path"] for row in rows}
    require(len(listed) == len(rows), "Package manifest has duplicate paths")
    observed = {
        path.relative_to(package_dir).as_posix()
        for path in package_dir.rglob("*")
        if path.is_file() and path != manifest
    }
    require(observed == listed, "Package manifest inventory differs")
    for row in rows:
        path = safe_relative(package_dir, row["relative_path"])
        require(path.stat().st_size == int(row["bytes"]), "Package file size differs: " + row["relative_path"])
        require(checksum(path) == row["sha256"].upper(), "Package file SHA-256 differs: " + row["relative_path"])
    return len(rows)


def build(output_root, receipt, cover_docx, cover_pdf, cover_source):
    output_root = output_root.resolve()
    require(output_root.is_relative_to((ROOT / "04_submission").resolve()), "Output root must remain under 04_submission")
    package_dir = output_root / PACKAGE_NAME
    package_zip = output_root / (PACKAGE_NAME + ".zip")
    checksum_file = output_root / (PACKAGE_NAME + "_SHA256.txt")
    require(package_dir.resolve().is_relative_to(output_root), "Unsafe package directory")
    require(checksum(RESEARCH_ARCHIVE) == ARCHIVE_SHA256, "Public Research Archive SHA-256 differs")
    verify_cover_letter(cover_docx)
    require(cover_pdf.is_file() and cover_pdf.stat().st_size > 0, "Rendered cover-letter PDF is missing")

    if package_dir.exists():
        shutil.rmtree(package_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir()
    payload = {}
    with zipfile.ZipFile(RESEARCH_ARCHIVE) as archive:
        require(archive.testzip() is None, "Research Archive CRC verification failed")
        manifest = read_archive_manifest(archive)
        for source, target in archive_entries().items():
            require(source in manifest, "Research Archive manifest is missing: " + source)
            data = archive.read(ARCHIVE_PREFIX + source)
            row = manifest[source]
            require(len(data) == int(row["bytes"]) and digest(data) == row["sha256"].upper(), "Research Archive payload differs: " + source)
            payload[target] = data

    packaging_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    payload["00_READ_ME_FIRST.md"] = readme_text().encode("utf-8")
    payload["06_Administrative/Cover_Letter_Draft.md"] = cover_source.read_bytes()
    payload["06_Administrative/Cover_Letter_Draft.docx"] = cover_docx.read_bytes()
    payload["06_Administrative/Cover_Letter_Draft.pdf"] = cover_pdf.read_bytes()
    payload["06_Administrative/Authors_and_Declarations.md"] = author_text().encode("utf-8")
    payload["06_Administrative/Submission_Readiness.md"] = readiness_text().encode("utf-8")
    payload["07_Integrity/PACKAGE_METADATA.json"] = (
        json.dumps(metadata(packaging_commit), indent=2) + "\n"
    ).encode("utf-8")
    payload["07_Integrity/Verify_Package.py"] = verifier_text().encode("utf-8")

    for relative, data in sorted(payload.items()):
        path = safe_relative(package_dir, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    rows = [
        {"relative_path": relative, "bytes": str(len(data)), "sha256": digest(data)}
        for relative, data in sorted(payload.items())
    ]
    manifest_path = package_dir / "07_Integrity/FILE_MANIFEST_SHA256.csv"
    manifest_path.write_bytes(csv_bytes(["relative_path", "bytes", "sha256"], rows))
    file_count = verify_manifest(package_dir)

    if package_zip.exists():
        package_zip.unlink()
    with zipfile.ZipFile(package_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in package_dir.rglob("*") if item.is_file()):
            relative = path.relative_to(package_dir).as_posix()
            info = zipfile.ZipInfo(PACKAGE_NAME + "/" + relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(package_zip) as archive:
        require(archive.testzip() is None, "Submission package ZIP failed CRC verification")
        expected = {
            PACKAGE_NAME + "/" + path.relative_to(package_dir).as_posix()
            for path in package_dir.rglob("*")
            if path.is_file()
        }
        require(set(archive.namelist()) == expected, "Submission package ZIP inventory differs")
    checksum_file.write_text(checksum(package_zip) + "  " + package_zip.name + "\n", encoding="ascii")

    result = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_JOURNAL_NEUTRAL_PACKAGE_VERIFIED_NOT_SUBMISSION_AUTHORIZED",
        "package_directory": package_dir.relative_to(ROOT).as_posix(),
        "package_zip": package_zip.relative_to(ROOT).as_posix(),
        "package_zip_bytes": package_zip.stat().st_size,
        "package_zip_sha256": checksum(package_zip),
        "checksum_file": checksum_file.relative_to(ROOT).as_posix(),
        "manifest_files_verified": file_count,
        "main_figures": 5,
        "supplementary_figures": 10,
        "source_data_archives": 3,
        "source_archive_sha256_verified": True,
        "scientific_files_copied_byte_for_byte": len(archive_entries()),
        "cover_letter_status": "JOURNAL_NEUTRAL_DRAFT_EXACT_FILE_APPROVAL_PENDING",
        "selected_target": None,
        "jcr_q1_verified": False,
        "institutional_apc_coverage_verified": False,
        "target_specific_adaptation_started": False,
        "exact_package_author_approved": False,
        "submission_authorized": False,
        "apc_commitment_authorized": False,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "corrected_external_outcome_unlock_authorized": False,
        "new_scientific_analysis_performed": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--receipt", type=Path, default=RECEIPT)
    parser.add_argument("--cover-docx", type=Path, default=WORK / "Cover_Letter_Draft.docx")
    parser.add_argument("--cover-pdf", type=Path, default=OUTPUT_ROOT / "_cover_render/Cover_Letter_Draft.pdf")
    parser.add_argument("--cover-source", type=Path, default=WORK / "Cover_Letter_Draft.md")
    args = parser.parse_args()
    receipt = args.receipt.resolve()
    require(receipt.is_relative_to((ROOT / "00_project_management").resolve()), "Receipt must remain in project management")
    build(
        args.output_root,
        receipt,
        args.cover_docx.resolve(),
        args.cover_pdf.resolve(),
        args.cover_source.resolve(),
    )
