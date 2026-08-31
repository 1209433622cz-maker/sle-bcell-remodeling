#!/usr/bin/env python3
"""Finalize dual-render QA and remove redundant render intermediates."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_scientific_coherence_refreeze/20260831_claim_order_reader_boundaries"
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
    qa_resolved = QA.resolve()
    if qa_resolved not in resolved.parents:
        raise RuntimeError(f"Refusing to remove render directory outside QA: {resolved}")
    if resolved.is_dir():
        shutil.rmtree(resolved)


def main() -> None:
    manuscript = DOCUMENTS / "Manuscript_scientific_coherence_refreeze_candidate.pdf"
    supplement = DOCUMENTS / "Supplementary_Information_scientific_coherence_refreeze_candidate.pdf"
    wps_audit_path = QA / "wps_pages/document_render_audit.json"
    lo_audit_path = QA / "lo_pages/document_render_audit.json"
    wps_audit = json.loads(wps_audit_path.read_text(encoding="utf-8"))
    lo_audit = json.loads(lo_audit_path.read_text(encoding="utf-8"))
    manuscript_pages = pdf_pages(manuscript)
    supplement_pages = pdf_pages(supplement)
    manuscript_text = " ".join("\n".join(manuscript_pages).split())
    supplement_text = " ".join("\n".join(supplement_pages).split())
    manuscript_compact = "".join(manuscript_text.split())
    supplement_compact = "".join(supplement_text.split())

    contacts = copy_contacts(QA / "wps_pages", "WPS") + copy_contacts(
        QA / "lo_pages", "LibreOffice"
    )
    shutil.copy2(wps_audit_path, RUN / "03_WPS_RENDER_AUDIT.json")
    shutil.copy2(lo_audit_path, RUN / "04_LIBREOFFICE_RENDER_AUDIT.json")
    LO_PDFS.mkdir(parents=True, exist_ok=True)
    lo_manuscript = LO_PDFS / "Manuscript_scientific_coherence_refreeze_candidate_LibreOffice.pdf"
    lo_supplement = LO_PDFS / "Supplementary_Information_scientific_coherence_refreeze_candidate_LibreOffice.pdf"
    shutil.copy2(QA / "lo_documents/Manuscript.pdf", lo_manuscript)
    shutil.copy2(QA / "lo_documents/Supplementary_Information.pdf", lo_supplement)

    a11y = {}
    for path in sorted((QA / "accessibility").glob("*.json")):
        report = json.loads(path.read_text(encoding="utf-8"))
        a11y[path.name] = report.get("counts")

    checks = {
        "wps_page_count_32_plus_16": len(manuscript_pages) == 32 and len(supplement_pages) == 16,
        "libreoffice_page_count_32_plus_16": lo_audit["pages"] == 48,
        "dual_render_page_count_match": wps_audit["pages"] == lo_audit["pages"] == 48,
        "all_pages_nonblank": all(len(page) >= 80 for page in manuscript_pages + supplement_pages),
        "wps_all_text_within_canvas": bool(wps_audit["all_pages_within_canvas"]),
        "lo_all_text_within_canvas": bool(lo_audit["all_pages_within_canvas"]),
        "all_markers_resolved": bool(
            wps_audit["all_markers_resolved"] and lo_audit["all_markers_resolved"]
        ),
        "title_present": "less stable B-cell state assignments" in manuscript_text,
        "abstract_landing_present": (
            "reproducibilitywasstrongerforaprocess-levelinterferonprogram"
            in manuscript_compact
        ),
        "composition_null_language_absent": "primary composition null" not in manuscript_text,
        "s9_reader_legend_present": (
            "fourmettheircriteriaandminimumstate-medianJaccarddidnot"
            in supplement_compact
        ),
        "s10_reader_heading_present": (
            "Referencecalibrationlimitssource-label-independentexternaltransfer"
            in supplement_compact
        ),
        "a11y_zero": all(
            counts == {"high": 0, "medium": 0, "low": 0} for counts in a11y.values()
        )
        and len(a11y) == 2,
        "eighteen_contact_sheets": len(contacts) == 18,
        "package_sha_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Dual-render final QA failed: {failed}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SCIENTIFIC_COHERENCE_DUAL_RENDER_AND_VISUAL_QA",
        "documents": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "pages": len(manuscript_pages) if path == manuscript else len(supplement_pages),
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
        "checks": checks,
        "accessibility": a11y,
        "visual_review": {
            "all_wps_pages_reviewed": list(range(1, 49)),
            "all_libreoffice_pages_reviewed": list(range(1, 49)),
            "clipping_overlap_missing_glyph_or_object_mismatch": False,
            "s9_s10_legible_at_document_scale": True,
            "contact_sheets": [path.relative_to(ROOT).as_posix() for path in contacts],
        },
        "scientific_estimates_changed": False,
        "source_data_changed": False,
        "exact_submission_package_modified": False,
        "exact_submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "05_DUAL_RENDER_FINAL_QA_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    for directory in (
        QA / "wps_pages",
        QA / "lo_pages",
        QA / "lo_render",
        QA / "lo_documents",
        QA / "libreoffice_render",
        QA / "libreoffice_documents",
        QA / "libreoffice_pages",
    ):
        remove_within_qa(directory)

    print(json.dumps({
        "status": status["status"],
        "pages_reviewed": 96,
        "contact_sheets_retained": len(contacts),
        "documents": status["documents"],
        "package_sha256": status["exact_submission_package_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
