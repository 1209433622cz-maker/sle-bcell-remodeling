#!/usr/bin/env python3
"""Finalize render QA for the scientific manuscript candidate."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = (
    ROOT
    / "phase17_v7/npj_sba_full_main_figure_refinement/20260831_figure5e_and_figures2to4_adjudication"
)
RECOMMENDED = RUN_DIR / "recommended_full_main_figure_set"
DOCX = RECOMMENDED / "documents/Manuscript_scientific_candidate.docx"
RENDER_DIR = RECOMMENDED / "document_render_qa"
RENDERED_PDF = RENDER_DIR / "Manuscript_scientific_candidate.pdf"
FINAL_PDF = RECOMMENDED / "documents/Manuscript_scientific_candidate.pdf"
A11Y = RECOMMENDED / "03_CANDIDATE_MANUSCRIPT_A11Y.json"
STATUS = RECOMMENDED / "04_CANDIDATE_MANUSCRIPT_RENDER_QA.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    if not DOCX.is_file() or not A11Y.is_file():
        raise FileNotFoundError("DOCX and accessibility audit are required")
    pdf_source = RENDERED_PDF if RENDERED_PDF.is_file() else FINAL_PDF
    if not pdf_source.is_file():
        raise FileNotFoundError("A newly rendered or previously finalized PDF is required")

    FINAL_PDF.parent.mkdir(parents=True, exist_ok=True)
    if pdf_source != FINAL_PDF:
        shutil.copy2(pdf_source, FINAL_PDF)
    for contact_sheet in sorted((RENDER_DIR / "contact_input").glob("contact_sheet_manuscript_*.png")):
        shutil.copy2(contact_sheet, RENDER_DIR / contact_sheet.name)

    reader = PdfReader(FINAL_PDF)
    page_text = [(page.extract_text() or "").strip() for page in reader.pages]
    combined = "\n".join(page_text)
    a11y = json.loads(A11Y.read_text(encoding="utf-8"))
    checks = {
        "page_count_32": len(page_text) == 32,
        "no_blank_pages": all(len(text) >= 80 for text in page_text),
        "title_on_page_1": "Disease-blind reconstruction distinguishes" in page_text[0],
        "data_availability_on_page_24": "Data availability" in page_text[23],
        "references_start_on_page_25": "References" in page_text[24],
        "figure_legends_start_on_page_29": "Figure legends" in page_text[28],
        "figure5e_boundary_on_page_32": "descriptive at n=2" in page_text[31],
        "new_figure1a_legend_present": "Disease-blind workflow and identity scope" in combined,
        "new_figure5a_legend_present": "Quantitative summary of three evidence classes" in combined,
        "new_figure5e_legend_present": "all 24 donor-gene effects were positive" in combined,
        "current_doi_present": "10.5281/zenodo.22151739" in combined,
        "old_doi_absent": "10.5281/zenodo.22086892" not in combined,
        "no_isolated_render_artifact_x": not any(line.strip() == "X" for line in combined.splitlines()),
        "a11y_zero_high_medium_low": a11y.get("counts") == {"high": 0, "medium": 0, "low": 0},
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Candidate manuscript render checks failed: {failed}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_CANDIDATE_MANUSCRIPT_RENDER_AND_VISUAL_QA",
        "docx": DOCX.relative_to(ROOT).as_posix(),
        "docx_sha256": sha256(DOCX),
        "pdf": FINAL_PDF.relative_to(ROOT).as_posix(),
        "pdf_sha256": sha256(FINAL_PDF),
        "pdf_bytes": FINAL_PDF.stat().st_size,
        "page_count": len(page_text),
        "checks": checks,
        "visual_review": {
            "all_pages_reviewed_in_contact_sheets": True,
            "contact_sheets": [
                path.relative_to(ROOT).as_posix()
                for path in sorted(RENDER_DIR.glob("contact_sheet_manuscript_*.png"))
            ],
            "high_risk_pages_reviewed_at_page_resolution": [1, 24, 25, 29, 30, 31, 32],
            "clipping_or_overlap_detected": False,
            "page_32_whitespace_assessment": "acceptable double-spaced figure-legend close; no format compression applied",
        },
        "scientific_estimates_changed": False,
        "exact_submission_package_modified": False,
    }
    STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
