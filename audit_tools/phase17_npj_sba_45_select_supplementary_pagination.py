#!/usr/bin/env python3
"""Adjudicate the 15-page Supplementary candidate without forcing compaction."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from docx import Document
from pypdf import PdfReader

import phase17_npj_sba_09_supplement_pagination_audit as pagination


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order"
QA = RUN / "qa/pagination_candidates"
FIGURES = RUN / "figures/figures"
DOCUMENTS = RUN / "documents"

STANDARD_STEM = "Supplementary_Information_standard_candidate"
COMPACT_STEM = "Supplementary_Information_compact_candidate"
FINAL_STEM = "Supplementary_Information_scientific_maintenance_freeze"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def page_with_complete_s1(path: Path) -> int | None:
    heading = "Supplementary Figure S1 | Source integrity and hard-quality-control diagnostics"
    legend_end = "threshold residual-risk scores for all 88 libraries."
    normalized_heading = re.sub(r"\s+", "", heading).lower()
    normalized_legend_end = re.sub(r"\s+", "", legend_end).lower()
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = re.sub(r"\s+", "", page.extract_text() or "").lower()
        if normalized_heading in text and normalized_legend_end in text:
            return number
    return None


def candidate_summary(wps_pdf: Path, lo_pdf: Path, expected_pages: int) -> dict[str, object]:
    sources = pagination.load_expected_sources(FIGURES)
    wps = pagination.inspect(wps_pdf, sources)
    lo = pagination.inspect(lo_pdf, sources)
    wps_s1_page = page_with_complete_s1(wps_pdf)
    lo_s1_page = page_with_complete_s1(lo_pdf)
    checks = {
        "wps_expected_pages": wps["pages"] == expected_pages,
        "libreoffice_expected_pages": lo["pages"] == expected_pages,
        "wps_all_heading_figure_pairs_same_page": wps["all_heading_figure_pairs_same_page"],
        "libreoffice_all_heading_figure_pairs_same_page": lo["all_heading_figure_pairs_same_page"],
        "wps_all_expected_figure_fingerprints_match": wps["all_expected_figure_fingerprints_match"],
        "libreoffice_all_expected_figure_fingerprints_match": lo["all_expected_figure_fingerprints_match"],
        "wps_complete_s1_heading_and_legend_same_page": wps_s1_page is not None,
        "libreoffice_complete_s1_heading_and_legend_same_page": lo_s1_page is not None,
    }
    return {
        "checks": checks,
        "pass": all(checks.values()),
        "wps": wps,
        "libreoffice": lo,
        "wps_complete_s1_page": wps_s1_page,
        "libreoffice_complete_s1_page": lo_s1_page,
    }


def main() -> None:
    standard_docx = QA / f"{STANDARD_STEM}.docx"
    compact_docx = QA / f"{COMPACT_STEM}.docx"
    wps_standard = QA / "wps" / f"{STANDARD_STEM}.pdf"
    wps_compact = QA / "wps" / f"{COMPACT_STEM}.pdf"
    lo_standard = QA / "lo_standard" / STANDARD_STEM / f"{STANDARD_STEM}.pdf"
    lo_compact = QA / "lo_compact" / COMPACT_STEM / f"{COMPACT_STEM}.pdf"
    for path in (standard_docx, compact_docx, wps_standard, wps_compact, lo_standard, lo_compact):
        if not path.is_file():
            raise FileNotFoundError(path)

    standard = candidate_summary(wps_standard, lo_standard, 16)
    compact = candidate_summary(wps_compact, lo_compact, 15)
    if compact["pass"]:
        selected_name = "compact_15_page_candidate"
        selected_docx = compact_docx
        selected_pages = 15
        decision = "ADOPT_COMPACT_15_PAGE_CANDIDATE"
        rationale = "Both renderers retained the complete S1 title, legend and image on one page."
    elif standard["pass"]:
        selected_name = "standard_16_page_candidate"
        selected_docx = standard_docx
        selected_pages = 16
        decision = "RETAIN_STANDARD_16_PAGE_CANDIDATE"
        rationale = "The compact candidate failed at least one cross-render pagination criterion."
    else:
        raise RuntimeError("Neither Supplementary pagination candidate passed structural review")

    final_docx = DOCUMENTS / f"{FINAL_STEM}.docx"
    shutil.copy2(selected_docx, final_docx)
    document = Document(final_docx)
    document.core_properties.author = "Zhi Chen; Teng Qi"
    document.core_properties.title = "Supplementary information"
    document.core_properties.subject = "Supplementary first-citation-order scientific maintenance freeze"
    document.core_properties.comments = (
        f"{decision}; display-only renumbering from byte-identical figures and Source Data."
    )
    document.save(final_docx)

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SUPPLEMENTARY_PAGINATION_CANDIDATE_SELECTED_FINAL_RENDER_REQUIRED",
        "decision": decision,
        "rationale": rationale,
        "selected_candidate": selected_name,
        "selected_expected_pages": selected_pages,
        "standard_candidate": standard,
        "compact_candidate": compact,
        "final_docx": {
            "path": final_docx.relative_to(ROOT).as_posix(),
            "bytes": final_docx.stat().st_size,
            "sha256": sha256(final_docx),
        },
        "font_size_reduced": False,
        "table_compression_applied": False,
        "scientific_content_changed_by_pagination": False,
    }
    (RUN / "06_PAGINATION_EXPERIMENT_AND_SELECTION.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
