"""Build the deterministic npj Systems Biology and Applications target package."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(
    os.environ.get(
        "NPJ_SBA_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_target_refreeze/20260830_target_specific_refreeze",
    )
).resolve()
OUTPUT_ROOT = ROOT / "04_submission/npj_systems_biology_and_applications"
PACKAGE_NAME = "SLE_Bcell_npj_Systems_Biology_and_Applications"
PACKAGE_DIR = OUTPUT_ROOT / PACKAGE_NAME
PACKAGE_ZIP = OUTPUT_ROOT / f"{PACKAGE_NAME}.zip"
CHECKSUM_FILE = OUTPUT_ROOT / f"{PACKAGE_NAME}_SHA256.txt"
RECEIPT = RUN / "03_PACKAGE_BUILD_STATUS.json"
CURRENT_SOURCE_DATA = (
    ROOT / "04_submission/current_submission_package/SLE_Bcell_Submission_Package/05_Source_Data"
)
CURRENT_ADMIN = (
    ROOT / "04_submission/current_submission_package/SLE_Bcell_Submission_Package/06_Administrative"
)
FIXED_ZIP_TIME = (2026, 8, 30, 0, 0, 0)
TITLE = (
    "Disease-blind reconstruction distinguishes reproducible interferon remodeling from "
    "unstable B-cell state assignments in systemic lupus erythematosus"
)
DOI = "10.5281/zenodo.22151739"
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"
STATUS = "PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def checksum(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def safe_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts, f"Unsafe package path: {relative}")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), f"Package path escapes root: {relative}")
    return resolved


def csv_bytes(fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def readme_text() -> str:
    return f"""# Read me first

This package is the final technical hardening candidate for an Article submission to
npj Systems Biology and Applications:

{TITLE}

## Current status

- Technical gate: `{STATUS}`.
- Scientific baseline: author-confirmed QiTeng R2; no new scientific analysis was run.
- Reproducibility archive: doi:{DOI}.
- R1 remains `{R1_HOLD}`.
- C9R remains `{C9R_HOLD}`.
- Corrected source-label-independent external disease-outcome estimation remains locked.
- Exact-file approval by both authors: pending.
- Journal-portal submission and APC commitment: not authorized.
- Official institutional JCR Q1 evidence and APC/OA eligibility receipts: pending.

Do not upload this package until both authors have approved the exact file hashes and
the corresponding author has separately authorized portal submission. The package is
integrity-valid and journal-adapted, but it is not a submission authorization.

## Portal-facing inventory

- `01_Manuscript/`: editable manuscript and WPS-rendered review PDF.
- `02_Main_Figures/`: five vector PDF main figures.
- `03_Supplementary_Information/`: one merged supplementary PDF containing Tables S1-S9 and Figures S1-S10.
- `04_Supplementary_Data/`: three machine-readable supporting archives.
- `05_Administrative/`: target cover letter, author declarations and policy drafts.
- `06_Integrity/`: statistical reporting map, metadata, SHA-256 manifest and verifier.

Run `python 06_Integrity/Verify_Package.py` from the extracted package root. The
ZIP-level SHA-256 is stored beside the ZIP.
"""


def metadata(packaging_commit: str) -> dict:
    return {
        "created_date": "2026-08-30",
        "status": STATUS,
        "target_journal": "npj Systems Biology and Applications",
        "content_type": "Article",
        "manuscript_title": TITLE,
        "title_word_count": 15,
        "abstract_word_count": 140,
        "scientific_baseline": "QiTeng R2",
        "reader_facing_baseline": "QiTeng npj final hardening",
        "reproducibility_archive_doi": DOI,
        "scientific_release_content_commit": "f1859ff8498d5569a1d5027b36ed18c8b7c7536f",
        "packaging_parent_commit": packaging_commit,
        "new_scientific_analysis_performed": False,
        "figure_source_data_byte_identical_to_frozen_baseline": True,
        "main_figures": 5,
        "supplementary_figures_embedded_in_single_pdf": 10,
        "numbered_supplementary_tables": 9,
        "supplementary_table_objects_including_S4B": 10,
        "supplementary_methods_included": False,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "corrected_external_outcome_unlock_authorized": False,
        "exact_package_author_approved": False,
        "submission_authorized": False,
        "apc_commitment_authorized": False,
        "official_jcr_q1_receipt_archived": False,
        "institutional_apc_coverage_verified": False,
    }


def verifier_text() -> str:
    return r'''"""Verify this extracted target package against its SHA-256 manifest."""

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "06_Integrity/FILE_MANIFEST_SHA256.csv"


def checksum(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
expected = {row["relative_path"] for row in rows} | {"06_Integrity/FILE_MANIFEST_SHA256.csv"}
observed = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()}
if expected != observed:
    raise SystemExit("FAIL: package inventory differs")
for row in rows:
    relative = Path(row["relative_path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise SystemExit("FAIL: unsafe manifest path")
    path = ROOT / relative
    if path.stat().st_size != int(row["bytes"]) or checksum(path) != row["sha256"].upper():
        raise SystemExit("FAIL: " + row["relative_path"])
print(f"PASS: {len(rows)} files verified; exact-file author approval and submission authorization remain pending")
'''


def payload() -> dict[str, bytes]:
    documents = RUN / "documents"
    figures = RUN / "portal_figures"
    sources = RUN / "sources"
    mapping = {
        "01_Manuscript/Manuscript.docx": documents / "Manuscript.docx",
        "01_Manuscript/Manuscript.pdf": documents / "Manuscript.pdf",
        "03_Supplementary_Information/Supplementary_Information.pdf": documents / "Supplementary_Information.pdf",
        "04_Supplementary_Data/Supplementary_Data_1_Figure_Source_Data.zip": CURRENT_SOURCE_DATA / "Figure_Source_Data.zip",
        "04_Supplementary_Data/Supplementary_Data_2_Regulator_Sensitivity.zip": CURRENT_SOURCE_DATA / "Regulator_Sensitivity.zip",
        "04_Supplementary_Data/Supplementary_Data_3_Full_Statistical_Results.zip": CURRENT_SOURCE_DATA / "Full_Statistical_Results.zip",
        "05_Administrative/Cover_Letter.docx": documents / "Cover_Letter.docx",
        "05_Administrative/Cover_Letter.pdf": documents / "Cover_Letter.pdf",
        "05_Administrative/Authors_and_Declarations.md": CURRENT_ADMIN / "Authors_and_Declarations.md",
        "05_Administrative/Nature_Portfolio_Reporting_Summary_Draft.md": sources / "Nature_Portfolio_Reporting_Summary_Draft.md",
        "05_Administrative/Editorial_Policy_Checklist_Draft.md": sources / "Editorial_Policy_Checklist_Draft.md",
        "06_Integrity/npj_statistics_reporting_map.csv": RUN / "npj_statistics_reporting_map.csv",
    }
    for number in range(1, 6):
        mapping[f"02_Main_Figures/Figure_{number}.pdf"] = figures / f"Figure_{number}.pdf"
    result = {relative: path.read_bytes() for relative, path in mapping.items()}
    result["00_READ_ME_FIRST.md"] = readme_text().encode("utf-8")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    result["06_Integrity/PACKAGE_METADATA.json"] = (
        json.dumps(metadata(commit), indent=2) + "\n"
    ).encode("utf-8")
    result["06_Integrity/Verify_Package.py"] = verifier_text().encode("utf-8")
    return result


def write_package(package_dir: Path, files: dict[str, bytes]) -> int:
    if package_dir.exists():
        require(package_dir.resolve().is_relative_to(OUTPUT_ROOT.resolve()), "Unsafe package cleanup target")
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)
    for relative, data in sorted(files.items()):
        path = safe_path(package_dir, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    rows = [
        {"relative_path": relative, "bytes": str(len(data)), "sha256": digest(data)}
        for relative, data in sorted(files.items())
    ]
    manifest = package_dir / "06_Integrity/FILE_MANIFEST_SHA256.csv"
    manifest.write_bytes(csv_bytes(["relative_path", "bytes", "sha256"], rows))
    return len(rows)


def verify_package(package_dir: Path) -> int:
    manifest = package_dir / "06_Integrity/FILE_MANIFEST_SHA256.csv"
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    listed = {row["relative_path"] for row in rows}
    observed = {
        path.relative_to(package_dir).as_posix()
        for path in package_dir.rglob("*")
        if path.is_file() and path != manifest
    }
    require(listed == observed and len(listed) == len(rows), "Package manifest inventory differs")
    for row in rows:
        path = safe_path(package_dir, row["relative_path"])
        require(path.stat().st_size == int(row["bytes"]), f"Package size differs: {row['relative_path']}")
        require(checksum(path) == row["sha256"].upper(), f"Package hash differs: {row['relative_path']}")
    return len(rows)


def write_zip(source: Path, output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(f"{PACKAGE_NAME}/{relative}", FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def build() -> dict:
    require(RUN.is_dir(), "Target run directory is missing")
    require(OUTPUT_ROOT.resolve().is_relative_to((ROOT / "04_submission").resolve()), "Unsafe output root")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    files = payload()
    manifest_files = write_package(PACKAGE_DIR, files)
    require(verify_package(PACKAGE_DIR) == manifest_files, "Package verification count differs")
    with tempfile.TemporaryDirectory(dir=OUTPUT_ROOT) as folder:
        first = Path(folder) / "first.zip"
        second = Path(folder) / "second.zip"
        write_zip(PACKAGE_DIR, first)
        write_zip(PACKAGE_DIR, second)
        require(first.read_bytes() == second.read_bytes(), "Deterministic package rebuild differs")
        shutil.copyfile(first, PACKAGE_ZIP)
    with zipfile.ZipFile(PACKAGE_ZIP) as archive:
        require(archive.testzip() is None, "Target package ZIP failed CRC verification")
    CHECKSUM_FILE.write_text(f"{checksum(PACKAGE_ZIP)}  {PACKAGE_ZIP.name}\n", encoding="ascii")
    result = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": STATUS,
        "package_directory": PACKAGE_DIR.relative_to(ROOT).as_posix(),
        "package_zip": PACKAGE_ZIP.relative_to(ROOT).as_posix(),
        "package_zip_bytes": PACKAGE_ZIP.stat().st_size,
        "package_zip_sha256": checksum(PACKAGE_ZIP),
        "manifest_files_verified": manifest_files,
        "deterministic_double_build": True,
        "main_figures": 5,
        "single_supplementary_pdf": True,
        "supplementary_data_archives": 3,
        "new_scientific_analysis_performed": False,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "corrected_external_outcome_unlock_authorized": False,
        "exact_package_author_approved": False,
        "submission_authorized": False,
        "apc_commitment_authorized": False,
    }
    RECEIPT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    build()
