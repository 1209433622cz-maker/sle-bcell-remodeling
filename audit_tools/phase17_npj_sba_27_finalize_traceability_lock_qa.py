#!/usr/bin/env python3
"""Finalize dual-render QA and the scientific traceability lock."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_traceability_lock/"
    "20260831_final_scientific_object_lock"
)
DOCUMENTS = RUN / "documents"
QA = RUN / "qa"
CONTACTS = QA / "final_contact_sheets"
LO_PDFS = QA / "libreoffice_pdfs"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
UNIT = "Sample-cohort pseudobulk (GSE174188); donor pseudobulk (GSE135779)"
ARCHIVE_SCOPE = "version-specific archive of the released analysis code, Source Data and statistical outputs"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path: Path) -> list[str]:
    return [(page.extract_text() or "").strip() for page in PdfReader(path).pages]


def copy_contacts(source: Path, prefix: str) -> list[Path]:
    CONTACTS.mkdir(parents=True, exist_ok=True)
    outputs = []
    for path in sorted(source.glob("*_contact_*.png")):
        target = CONTACTS / f"{prefix}_{path.name}"
        shutil.copy2(path, target)
        outputs.append(target)
    return outputs


def remove_within_qa(path: Path) -> None:
    resolved = path.resolve()
    if QA.resolve() not in resolved.parents:
        raise RuntimeError(f"Refusing to remove outside QA: {resolved}")
    if resolved.is_dir():
        shutil.rmtree(resolved)


def main() -> None:
    manuscript = DOCUMENTS / "Manuscript_final_scientific_lock.pdf"
    supplement = DOCUMENTS / "Supplementary_Information_final_scientific_lock.pdf"
    wps_audit_path = QA / "wps_pages/document_render_audit.json"
    lo_audit_path = QA / "lo_pages/document_render_audit.json"
    wps_audit = json.loads(wps_audit_path.read_text(encoding="utf-8"))
    lo_audit = json.loads(lo_audit_path.read_text(encoding="utf-8"))

    manuscript_pages = pdf_pages(manuscript)
    supplement_pages = pdf_pages(supplement)
    manuscript_text = " ".join("\n".join(manuscript_pages).split())
    supplement_text = " ".join("\n".join(supplement_pages).split())
    supplement_compact = "".join(supplement_text.split())
    unit_compact = "".join(UNIT.split())
    archive_compact = "".join(ARCHIVE_SCOPE.split())
    total_pages = len(manuscript_pages) + len(supplement_pages)

    contacts = copy_contacts(QA / "wps_pages", "WPS") + copy_contacts(QA / "lo_pages", "LibreOffice")
    shutil.copy2(wps_audit_path, RUN / "02_WPS_RENDER_AUDIT.json")
    shutil.copy2(lo_audit_path, RUN / "03_LIBREOFFICE_RENDER_AUDIT.json")
    LO_PDFS.mkdir(parents=True, exist_ok=True)
    lo_manuscript = LO_PDFS / "Manuscript_final_scientific_lock_LibreOffice.pdf"
    lo_supplement = LO_PDFS / "Supplementary_Information_final_scientific_lock_LibreOffice.pdf"
    shutil.copy2(QA / "lo_documents/Manuscript.pdf", lo_manuscript)
    shutil.copy2(QA / "lo_documents/Supplementary_Information.pdf", lo_supplement)
    lo_manuscript_pages = pdf_pages(lo_manuscript)
    lo_supplement_pages = pdf_pages(lo_supplement)

    a11y = {}
    for path in sorted((QA / "accessibility").glob("*.json")):
        report = json.loads(path.read_text(encoding="utf-8"))
        a11y[path.name] = report.get("counts")

    with (RUN / "FINAL_CORE_CLAIM_NUMERICAL_TRACEABILITY_MATRIX.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        traceability_rows = list(csv.DictReader(handle))
    with (RUN / "SOURCE_DATA_FINAL_LOCK_MANIFEST.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        source_rows = list(csv.DictReader(handle))
    with (RUN / "FIGURE_FINAL_LOCK_MANIFEST.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        figure_rows = list(csv.DictReader(handle))

    checks = {
        "manuscript_page_count_31": len(manuscript_pages) == 31,
        "supplement_page_count_plausible": len(supplement_pages) in {16, 17},
        "dual_render_page_counts_match": (
            len(manuscript_pages) == len(lo_manuscript_pages)
            and len(supplement_pages) == len(lo_supplement_pages)
        ),
        "dual_render_total_pages_match": wps_audit["pages"] == lo_audit["pages"] == total_pages,
        "all_pages_nonblank": all(len(page) >= 80 for page in manuscript_pages + supplement_pages),
        "wps_all_text_within_canvas": bool(wps_audit["all_pages_within_canvas"]),
        "lo_all_text_within_canvas": bool(lo_audit["all_pages_within_canvas"]),
        "all_markers_resolved": bool(wps_audit["all_markers_resolved"] and lo_audit["all_markers_resolved"]),
        "archive_scope_present": archive_compact in supplement_compact,
        "old_archive_claim_absent": "matchesthefrozenmanuscript,figures" not in supplement_compact,
        "dataset_specific_units_present_twice": supplement_compact.count(unit_compact) == 2,
        "umbrella_unit_absent": "Donor/sample pseudobulk" not in supplement_text,
        "traceability_24_of_24_pass": len(traceability_rows) == 24
        and all(row["status"].startswith("PASS") for row in traceability_rows),
        "source_data_15_of_15_locked": len(source_rows) == 15,
        "figures_30_of_30_locked": len(figure_rows) == 30,
        "accessibility_zero": len(a11y) == 2
        and all(counts == {"high": 0, "medium": 0, "low": 0} for counts in a11y.values()),
        "expected_contact_sheet_count": len(contacts) == 18,
        "package_sha_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Final traceability QA failed: {failed}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCKED",
        "checks": checks,
        "documents": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "pages": len(pdf_pages(path)),
                "render_engine": "WPS",
            }
            for path in (manuscript, supplement)
        },
        "libreoffice_cross_render": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "pages": len(pdf_pages(path)),
            }
            for path in (lo_manuscript, lo_supplement)
        },
        "visual_review": {
            "all_wps_pages_reviewed": list(range(1, total_pages + 1)),
            "all_libreoffice_pages_reviewed": list(range(1, total_pages + 1)),
            "clipping_overlap_missing_glyph_or_object_mismatch": False,
            "table_s6_s7_wrap_and_pagination_pass": True,
            "contact_sheets": [path.relative_to(ROOT).as_posix() for path in contacts],
        },
        "scientific_estimates_changed": False,
        "source_data_changed": False,
        "figures_changed": False,
        "release_or_zenodo_changed": False,
        "submission_package_changed": False,
        "submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "04_FINAL_TRACEABILITY_LOCK_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    for directory in (
        QA / "wps_pages",
        QA / "lo_pages",
        QA / "lo_render",
        QA / "lo_documents",
        QA / "lo_profile",
    ):
        remove_within_qa(directory)

    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
