#!/usr/bin/env python3
"""Finalize dual-render QA for the reference-terminology and S6 refreeze."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_reference_terminology_lock/"
    "20260901_reference_terminology_s6_refreeze"
)
DOCUMENTS = RUN / "documents"
QA = RUN / "qa"
LO_DOCUMENTS = QA / "libreoffice_documents"
MANUSCRIPT_STEM = "Manuscript_reference_terminology_s6_refreeze"
SUPPLEMENT_STEM = "Supplementary_Information_reference_terminology_s6_refreeze"
S6 = RUN / "figures/figures/Supplementary_Figure_S6_replication_robustness_diagnostics.pdf"
S6_SOURCE = RUN / "figures/source_data/Supplementary_Figure_S6_source_data.csv"
S6_SOURCE_SHA256 = "A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
ACTION_REPORT = ROOT / "00_project_management/action_record_2026-09-01_reference_terminology_s6_refreeze.md"
FINAL_MANIFEST = RUN / "05_FINAL_FILE_MANIFEST.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path: Path) -> list[str]:
    return [(page.extract_text() or "").strip() for page in PdfReader(path).pages]


def extract_s6_properties() -> dict[str, object]:
    reader = PdfReader(S6)
    page = reader.pages[0]
    width_mm = float(page.mediabox.width) * 25.4 / 72.0
    height_mm = float(page.mediabox.height) * 25.4 / 72.0
    text = page.extract_text() or ""
    sizes: list[float] = []

    def collect_text_size(
        value: str,
        _current_matrix: list[float],
        _text_matrix: list[float],
        _font_dictionary: object,
        font_size: float,
    ) -> None:
        if value.strip():
            sizes.append(float(font_size))

    page.extract_text(visitor_text=collect_text_size)
    font_result = subprocess.run(
        ["pdffonts", str(S6)],
        check=True,
        capture_output=True,
        text=True,
    )
    font_lines = [line for line in font_result.stdout.splitlines()[2:] if line.strip()]
    return {
        "width_mm": width_mm,
        "height_mm": height_mm,
        "minimum_character_size_pt": min(sizes),
        "text": text,
        "font_lines": font_lines,
        "fonts_embedded_subset_unicode": bool(font_lines)
        and all(re.search(r"\byes\s+yes\s+yes\b", line) for line in font_lines),
        "arial_present": any("Arial" in line for line in font_lines),
    }


def write_action_report(status: dict[str, object]) -> None:
    documents = status["documents"]
    report = f"""# Action record: reference, terminology and Supplementary Figure S6 scientific refreeze

**Date:** 2026-09-01
**Final status:** `{status['status']}`
**Scope:** scientific text and figure presentation only; no submission-package, release or Zenodo action

## Objective

Resolve the last demonstrated evidence-language inconsistencies without reopening the frozen biological or statistical analyses. The round independently verified method citations, normalized evidence-class terminology across the manuscript and Supplementary Information, redrew Supplementary Figure S6 from its locked Source Data, rebuilt both documents, and completed WPS/LibreOffice render QA.

## Independent decisions

- Added Chen, Lun and Smyth (2016) beside the original edgeR package citation because it directly supports filtering, TMM normalization and the robust quasi-likelihood workflow.
- Reworded FRY as a fast self-contained approximation to the directional `mroast/ROAST` gene-set test; the analysis and all q values were unchanged.
- Corrected the exact title of the MSigDB hallmark collection paper.
- Reserved `validation` for generic calibration, prospective validation, CRediT Validation and explicit statements that a same-data analysis is not independent validation.
- Standardized GSE174188 as discovery plus internal replication and GSE135779 as source-label-defined independent replication.
- Rejected direct use of the uploaded S6 candidate because tight bounding-box export reduced its width to about 167 mm, substituted Arimo for the established Arial contract and added an unnecessary figure-wide title.
- Retained the established four-panel S6 geometry, semantic palette and panel order; only panel a/c terminology, figure filename and legend title were changed.

## Scientific-object changes

- Numerical estimates changed: **0**
- Statistical models rerun: **0**
- Source Data changed: **0**
- Main panels: **21 KEEP, 0 MODIFY, 0 REPLACE**
- Supplementary figures: **S1-S5 and S7-S10 KEEP; S6 MODIFY by source redraw; 0 REPLACE**
- New biological claims: **0**

## Reference and terminology integration

The reference list now contains 33 contiguous references with continuous first-appearance order and no orphan citation. The manuscript now uses `biological-unit-aware inference`, `internal replication`, `source-defined managed SLE`, `source-defined flare`, `source-label-defined GSE135779 replication`, and the bounded phrase `support an IFN-centred regulatory context`. The Supplementary Information uses the same evidence classes in Tables S1, S5 and S8 and in the S6 legend.

## S6 source-redraw QA

- Source Data SHA-256: `{S6_SOURCE_SHA256}`; byte-identical to the previous frozen object and the received candidate input.
- Final physical size: {status['s6']['width_mm']:.2f} x {status['s6']['height_mm']:.2f} mm.
- Minimum extracted text size: {status['s6']['minimum_character_size_pt']:.2f} pt.
- Fonts: embedded/subset Unicode Arial.
- Panel titles: `GSE135779 donor support by analysis`, `Childhood primary program family`, `Source-label omission sensitivity`, `Childhood donor influence`.
- No figure-wide title was added; the scientific title remains in the Supplementary legend.

## Document and render QA

- Manuscript: {documents[MANUSCRIPT_STEM + '.pdf']['pages']} pages, WPS PDF SHA-256 `{documents[MANUSCRIPT_STEM + '.pdf']['sha256']}`.
- Supplementary Information: {documents[SUPPLEMENT_STEM + '.pdf']['pages']} pages, WPS PDF SHA-256 `{documents[SUPPLEMENT_STEM + '.pdf']['sha256']}`.
- WPS and LibreOffice retained complete content; their manuscript pagination differed by one page because LibreOffice moved the final legend fragment to page 32, while Supplementary pagination remained 16 pages in both renderers. All page text stayed inside the canvas, all ten Supplementary figures resolved, and all pages were nonblank.
- DOCX accessibility audits contained no high- or medium-severity findings.
- The author-confirmed submission package remains byte-identical at `{PACKAGE_SHA256}` and was not rebuilt.

## Primary verification sources

- Chen, Lun and Smyth edgeR quasi-likelihood workflow: https://pubmed.ncbi.nlm.nih.gov/27508061/
- limma manual for `fry`/`mroast`: https://bioconductor.org/packages/release/bioc/manuals/limma/man/limma.pdf
- ROAST primary paper: https://pubmed.ncbi.nlm.nih.gov/20610611/
- MSigDB hallmark primary paper: https://pubmed.ncbi.nlm.nih.gov/26771021/

## Boundary and next stage

The scientific evidence chain is now textually closed: disease-blind identity scaffold; GSE174188 sample-cohort inference and internal replication; GSE135779 source-label-defined donor replication; observational regulator context; response-set concordance; descriptive perturbational context. No current defect justifies reopening disease-effect models, identity mapping, TF analysis, Source Data or another panel.

The next stage should be `FINAL_INTEGRATED_READER_SIMULATION_AND_REDUNDANCY_PRUNE`: read the manuscript and all legends in final order at actual size, test whether each paragraph and panel has a unique claim owner, remove only genuine repetition, and stop when no reader-path defect can be localized. It should not add cohorts, sensitivity analyses, replacement panels or submission engineering.
"""
    ACTION_REPORT.write_text(report, encoding="utf-8", newline="\n")


def write_final_manifest() -> None:
    rows = []
    for path in sorted(candidate for candidate in RUN.rglob("*") if candidate.is_file()):
        if path == FINAL_MANIFEST:
            continue
        rows.append(
            {
                "relative_path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    with FINAL_MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    manuscript = DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf"
    supplement = DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf"
    lo_manuscript = LO_DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf"
    lo_supplement = LO_DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf"
    wps_audit = json.loads((QA / "wps_pages/document_render_audit.json").read_text(encoding="utf-8"))
    lo_audit = json.loads((QA / "lo_pages/document_render_audit.json").read_text(encoding="utf-8"))
    pagination_audit = json.loads((RUN / "02_SUPPLEMENT_PAGINATION_AUDIT.json").read_text(encoding="utf-8"))
    main_pages = pdf_pages(manuscript)
    supplement_pages = pdf_pages(supplement)
    lo_main_pages = pdf_pages(lo_manuscript)
    lo_supplement_pages = pdf_pages(lo_supplement)
    main_text = " ".join("\n".join(main_pages).split())
    supplement_text = " ".join("\n".join(supplement_pages).split())
    s6 = extract_s6_properties()
    wps_contacts = sorted((QA / "wps_pages").glob("*_contact_*.png"))
    lo_contacts = sorted((QA / "lo_pages").glob("*_contact_*.png"))
    contacts = wps_contacts + lo_contacts
    affected_pages = sorted((QA / "affected_pages").glob("*.png"))

    accessibility: dict[str, dict[str, int]] = {}
    for path in sorted((QA / "accessibility").glob("*.json")):
        report = json.loads(path.read_text(encoding="utf-8"))
        accessibility[path.name] = report.get("counts", {})

    source_text = (RUN / "sources/Manuscript_reference_terminology_s6_refreeze.md").read_text(encoding="utf-8")
    references = source_text.split("## References\n", 1)[1].split("## Figure legends\n", 1)[0]
    reference_numbers = [int(value) for value in re.findall(r"(?m)^(\d+)\. ", references)]
    with (RUN / "SUPPLEMENTARY_FIGURE_REFERENCE_TERMINOLOGY_DECISION_MATRIX.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        supplementary_decisions = list(csv.DictReader(handle))

    checks = {
        "manuscript_page_count_plausible": len(main_pages) in {31, 32},
        "supplement_page_count_plausible": len(supplement_pages) in {16, 17},
        "dual_render_page_counts_compatible": abs(len(main_pages) - len(lo_main_pages)) <= 1
        and len(supplement_pages) == len(lo_supplement_pages),
        "all_pages_nonblank": all(
            len(page) >= 80
            for page in main_pages + supplement_pages + lo_main_pages + lo_supplement_pages
        ),
        "wps_all_text_within_canvas": bool(wps_audit["all_pages_within_canvas"]),
        "lo_all_text_within_canvas": bool(lo_audit["all_pages_within_canvas"]),
        "all_markers_resolved": bool(wps_audit["all_markers_resolved"] and lo_audit["all_markers_resolved"]),
        "supplement_pagination_audit_pass": pagination_audit.get("status")
        == "PASS_SUPPLEMENT_PAGINATION_COHERENCE"
        and all(pagination_audit.get("checks", {}).values()),
        "biological_unit_aware_source_present": "biological-unit-aware inference" in source_text,
        "internal_replication_source_present": "internal replication estimate" in source_text,
        "gse135779_replication_source_present": "independent SLE replication dataset" in source_text,
        "regulatory_context_source_present": "support an IFN-centred regulatory context" in source_text,
        "rendered_semantic_anchors_present": all(
            anchor in main_text
            for anchor in ("biological-unit-aware", "GSE135779", "IFN-centred", "regulatory")
        ),
        "s6_legend_present": "GSE135779 replication and robustness diagnostics" in supplement_text,
        "old_s6_legend_absent": "Independent-validation diagnostics" not in supplement_text,
        "references_1_to_33": reference_numbers == list(range(1, 34)),
        "s6_width_170mm": abs(float(s6["width_mm"]) - 170.0) <= 0.15,
        "s6_height_expected": 127.0 <= float(s6["height_mm"]) <= 129.5,
        "s6_minimum_text_at_least_6pt": float(s6["minimum_character_size_pt"]) >= 6.0,
        "s6_arial_embedded": bool(s6["arial_present"] and s6["fonts_embedded_subset_unicode"]),
        "s6_panel_a_title": "GSE135779 donor support by analysis" in str(s6["text"]),
        "s6_panel_c_title": "Source-label omission sensitivity" in str(s6["text"]),
        "s6_old_terms_absent": "External validation" not in str(s6["text"])
        and "Mapping-label" not in str(s6["text"]),
        "s6_source_byte_identical": sha256(S6_SOURCE) == S6_SOURCE_SHA256,
        "s6_only_supplementary_modify": [
            row["figure"] for row in supplementary_decisions if row["decision"] != "KEEP"
        ]
        == ["S6"],
        "accessibility_no_high_or_medium": len(accessibility) == 2
        and all(counts.get("high", 0) == 0 and counts.get("medium", 0) == 0 for counts in accessibility.values()),
        "contact_sheets_created": len(contacts) >= 16,
        "affected_pages_review_set_complete": {path.name for path in affected_pages}
        == {"wps_supp-12.png", "lo_supp-12.png", "wps_main-31.png", "lo_main-32.png"},
        "package_sha_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Final reference-terminology/S6 QA failed: {failed}")

    status: dict[str, object] = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "REFERENCE_TERMINOLOGY_AND_S6_SCIENTIFIC_REFREEZE_LOCKED",
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
        "s6": {
            "bytes": S6.stat().st_size,
            "sha256": sha256(S6),
            "source_data_sha256": sha256(S6_SOURCE),
            "width_mm": float(s6["width_mm"]),
            "height_mm": float(s6["height_mm"]),
            "minimum_character_size_pt": float(s6["minimum_character_size_pt"]),
            "font_lines": s6["font_lines"],
        },
        "visual_review": {
            "wps_contact_sheets": [path.relative_to(ROOT).as_posix() for path in wps_contacts],
            "libreoffice_contact_sheets": [path.relative_to(ROOT).as_posix() for path in lo_contacts],
            "affected_pages_at_180_dpi": [path.relative_to(ROOT).as_posix() for path in affected_pages],
            "clipping_overlap_missing_glyph_or_object_mismatch": False,
        },
        "scientific_estimates_changed": False,
        "source_data_changed": False,
        "main_panels": {"keep": 21, "modify": 0, "replace": 0},
        "supplementary_figures": {"keep": 9, "modify_source_redraw": 1, "replace": 0},
        "release_or_zenodo_changed": False,
        "submission_package_changed": False,
        "submission_package_sha256": sha256(PACKAGE),
        "final_file_manifest": FINAL_MANIFEST.relative_to(ROOT).as_posix(),
        "action_report": ACTION_REPORT.relative_to(ROOT).as_posix(),
        "next_stage": "FINAL_INTEGRATED_READER_SIMULATION_AND_REDUNDANCY_PRUNE",
    }
    (RUN / "04_FINAL_REFERENCE_TERMINOLOGY_S6_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_action_report(status)
    write_final_manifest()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
