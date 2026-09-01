#!/usr/bin/env python3
"""Finalize the canonical-source and S4b semantic scientific stop gate."""

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
RUN = ROOT / "phase17_v7/npj_sba_scientific_stop_gate/20260901_canonical_source_s4b_refreeze"
BASE = ROOT / "phase17_v7/npj_sba_integrated_reader_refreeze/20260901_s3_s5_reader_path_refreeze"
DOCUMENTS = RUN / "documents"
QA = RUN / "qa"
LO_DOCUMENTS = QA / "libreoffice_documents"
MANUSCRIPT_STEM = "Manuscript_scientific_stop_gate"
SUPPLEMENT_STEM = "Supplementary_Information_scientific_stop_gate"
BASE_MANUSCRIPT_STEM = "Manuscript_integrated_reader_refreeze"
BASE_SUPPLEMENT_STEM = "Supplementary_Information_integrated_reader_refreeze"
S4 = RUN / "figures/figures/Supplementary_Figure_S4_composition_diagnostics.pdf"
ROOT_MANUSCRIPT = ROOT / "01_manuscript/Manuscript.md"
ROOT_SUPPLEMENT = ROOT / "01_manuscript/Supplementary_Information.md"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
S4_SOURCE_SHA256 = "7BA2660E5A50ADCF28407BCC92A91C791576DD69A9A1ABA9618DEB045C3A4E19"
OLD_CHILDHOOD = "The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 mapped cells per donor."
NEW_CHILDHOOD = "The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 eligible cells in the source-label-defined broad-B analogue per donor."
OLD_TABLE_TITLE = "Supplementary Table S5 | Main-figure source-data map"
NEW_TABLE_TITLE = "Supplementary Table S5 | Selected figure source-data map"
OLD_S4_TITLE = "Primary null is stable to covariance and cell policy"
NEW_S4_TITLE = "B_ASC estimate across covariance and cell policies"
ACTION_REPORT = ROOT / "00_project_management/action_record_2026-09-01_scientific_presentation_stop_gate.md"
FINAL_STATUS = RUN / "04_FINAL_SCIENTIFIC_PRESENTATION_STOP_GATE_STATUS.json"
FINAL_MANIFEST = RUN / "05_FINAL_FILE_MANIFEST.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path: Path) -> list[str]:
    return [(page.extract_text() or "").strip() for page in PdfReader(path).pages]


def normalized(value: str) -> str:
    return " ".join(value.split())


def figure_properties(path: Path) -> dict[str, object]:
    page = PdfReader(path).pages[0]
    text = page.extract_text() or ""
    sizes: list[float] = []

    def collect_size(value: str, _cm: list[float], _tm: list[float], _font: object, font_size: float) -> None:
        if value.strip():
            sizes.append(float(font_size))

    page.extract_text(visitor_text=collect_size)
    fonts = subprocess.run(["pdffonts", str(path)], check=True, capture_output=True, text=True).stdout.splitlines()[2:]
    font_lines = [line for line in fonts if line.strip()]
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width_mm": float(page.mediabox.width) * 25.4 / 72.0,
        "height_mm": float(page.mediabox.height) * 25.4 / 72.0,
        "minimum_character_size_pt": min(sizes),
        "text": text,
        "arial_present": any("Arial" in line for line in font_lines),
        "fonts_embedded_subset_unicode": bool(font_lines) and all(re.search(r"\byes\s+yes\s+yes\b", line) for line in font_lines),
    }


def load_accessibility() -> dict[str, dict[str, int]]:
    reports: dict[str, dict[str, int]] = {}
    for path in sorted((QA / "accessibility").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        reports[path.name] = payload.get("counts", {})
    return reports


def source_hashes(directory: Path) -> dict[str, str]:
    return {path.name: sha256(path) for path in sorted(directory.glob("*.csv"))}


def expected_text_diff(old_pages: list[str], new_pages: list[str], old: str, new: str) -> dict[str, object]:
    old_text = normalized("\n".join(old_pages))
    new_text = normalized("\n".join(new_pages))
    count = old_text.count(old)
    expected = old_text.replace(old, new, 1) if count == 1 else ""
    return {
        "old_phrase_count": count,
        "new_phrase_count": new_text.count(new),
        "expected_only_change": count == 1 and expected == new_text,
    }


def manuscript_phrase_transition(old_pages: list[str], new_pages: list[str]) -> dict[str, object]:
    old_text = normalized("\n".join(old_pages))
    new_text = normalized("\n".join(new_pages))
    old_pattern = re.compile(
        r"The childhood analysis included 43 donors \(11 controls and 32 SLE\) with at least "
        r"50 mapped(?:\d{1,3})? cells per donor\."
    )
    new_pattern = re.compile(
        r"The childhood analysis included 43 donors \(11 controls and 32 SLE\) with at least "
        r"50 eligible(?:\d{1,3})? cells in the source-label-defined broad-B analogue per donor\."
    )
    return {
        "old_pdf_contains_old_phrase": bool(old_pattern.search(old_text)),
        "new_pdf_contains_new_phrase": bool(new_pattern.search(new_text)),
        "new_pdf_excludes_old_phrase": not bool(old_pattern.search(new_text)),
        "line_number_reflow_expected": len(old_text) != len(new_text),
        "expected_only_change": bool(old_pattern.search(old_text))
        and bool(new_pattern.search(new_text))
        and not bool(old_pattern.search(new_text)),
    }


def write_action_report(status: dict[str, object]) -> None:
    documents = status["documents"]
    s4 = status["figure_s4"]
    report = f"""# Action record: scientific-presentation semantic stop gate

**Date:** 2026-09-01
**Final status:** `{status['status']}`
**Scope:** manuscript text, scientific figure semantics and canonical source coherence only; no submission-package, release or Zenodo action

## Objective

Complete the previously interrupted `FINAL_TEXT_FIGURE_CROSS_REFERENCE_AND_SEMANTIC_STOP_GATE` by independently testing the supplied review, repairing only demonstrable localized defects, rebuilding the scientific documents and deciding whether further manuscript or figure modification remains justified.

## Independent adjudication of the supplied review

The two supplied Markdown reviews and pasted review narrative were archived byte-identically under `00_project_management/scientific_stop_gate_2026-09-01/received/`. They were treated as external review evidence, not as executable instructions.

Independent inspection confirmed all three proposed defects:

1. `01_manuscript/Manuscript.md` and `01_manuscript/Supplementary_Information.md` were stale despite being declared by their README as the current author-facing entry points.
2. `50 mapped cells per donor` was ambiguous inside the source-label-defined GSE135779 analysis.
3. Supplementary Fig. S4b used a stronger `Primary null is stable` title than the non-equivalence boundary supports.

The optional Table S5 title correction was also accepted because the table maps selected main and Supplementary figures.

## Source-level repairs

- The current integrated-reader refreeze sources were used as the sole baseline; the stale root files were not repaired line by line.
- The root and phase17 manuscript sources now match byte for byte.
- The childhood sentence now specifies `50 eligible cells in the source-label-defined broad-B analogue per donor`.
- CRediT `Validation` and the two legitimate methodological validation boundaries were deliberately retained.
- Supplementary Table S5 is now titled `Selected figure source-data map`.
- Main-text numerical values, references, authorship, declarations and scientific conclusions were unchanged.

## Figure decisions

- Main figures: **21 KEEP, 0 MODIFY, 0 REPLACE**.
- Supplementary display: **38 panels retained**.
- Supplementary Fig. S4b: **MODIFY TITLE ONLY BY SOURCE REDRAW**.
- Supplementary Figs. S3 and S5: KEEP their pruned versions.
- Supplementary Figs. S1, S2 and S6-S10: KEEP.
- New panels: **0**; replacement panels: **0**; new analyses: **0**.

Figure 1a and Figure 5a were explicitly reconsidered and remain KEEP. Their current roles are necessary and non-duplicative: Fig. 1a defines the disease-blind inference boundary, whereas Fig. 5a distinguishes observational evidence classes and prevents causal over-reading.

## S4 source redraw and numerical invariance

S4 was rerun through the existing plotting function with `NPJ_SBA_STYLE=1`. The new title is `B_ASC estimate across covariance and cell policies`. The word `Primary` was omitted from the review recommendation because it added no evidence role and caused visible right-edge clipping under the enforced 8 pt publication-style contract. The point estimates, intervals, HC1 comparison, axes, null guide, palette and panel geometry were not edited.

- S4 dimensions: {s4['width_mm']:.2f} x {s4['height_mm']:.2f} mm.
- Minimum extracted text size: {s4['minimum_character_size_pt']:.2f} pt.
- Arial is embedded, subset and Unicode encoded.
- S4 Source Data SHA-256 remains `{S4_SOURCE_SHA256}`.
- The old and new S4 PDFs contain identical extracted text after removal of their respective panel-b titles.
- Raster differences are confined to the panel-b title region.
- All 14 other figure PDF/PNG pairs and all 15 Source Data CSVs remain byte-identical to the previous scientific refreeze.

## Document and visual QA

- WPS manuscript: {documents['wps_manuscript']['pages']} pages, SHA-256 `{documents['wps_manuscript']['sha256']}`.
- LibreOffice manuscript: {documents['lo_manuscript']['pages']} pages.
- WPS and LibreOffice Supplementary Information: {documents['wps_supplement']['pages']} pages each.
- The source manuscript differs from the preceding refreeze only by the approved childhood sentence. Both rendered PDFs contain the new sentence and exclude the old sentence; their automatic line numbers reflow locally because the replacement is longer.
- The Supplementary PDF text differs only by the approved Table S5 title; S4b is a source-redrawn embedded figure.
- Supplementary S1-S10 heading pagination and embedded-figure fingerprints passed in both renderers.
- Full contact sheets and high-resolution pages containing the childhood sentence, Table S5 and S4 were generated for visual review. No clipping, overlap, missing glyph, unresolved marker or incoherent page transition was found.
- Both DOCX accessibility reports contain **0 high / 0 medium / 0 low** findings.

## Scientific conclusion

The final hierarchy is coherent and bounded: disease-blind identity reconstruction precedes disease inference; broad frozen-representation identity passes; end-to-end reconstruction exposes a B_ASC-specific boundary; the primary composition result remains unsupported rather than equivalent; B_CONV IFN/ISG is the reproducible process-level signal; GSE135779 supports source-label-defined replication but not source-label-independent taxonomy transfer; and regulator/response evidence remains observational.

No remaining defect justifies reopening identity, composition, pseudobulk, external mapping, regulator, enrichment, overlap-depletion or perturbation analyses. No current figure warrants replacement.

## Reproducibility and release boundary

The complete rerun is available through `audit_tools/run_6013RP_phase17_npj_sba_semantic_stop_gate.ps1`. The author-approved submission package remains byte-identical at `{PACKAGE_SHA256}`. GitHub release and Zenodo records were not changed.

## Next-stage decision

Enter `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`. Active manuscript-text and figure redesign should stop. A future change should require a new, localized and demonstrable scientific defect with source-level evidence; general requests for further polish are not sufficient reason to reopen frozen analyses or figures. Journal-specific formatting remains a separate later operation and is not part of this scientific stop gate.
"""
    ACTION_REPORT.write_text(report, encoding="utf-8", newline="\n")


def write_manifest() -> None:
    rows: list[dict[str, object]] = []
    for path in sorted(item for item in RUN.rglob("*") if item.is_file()):
        if path == FINAL_MANIFEST:
            continue
        rows.append({"relative_path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    with FINAL_MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    integration = json.loads((RUN / "00_CANONICAL_SOURCE_S4B_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
    build = json.loads((RUN / "01_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
    pagination = json.loads((RUN / "02_SUPPLEMENT_PAGINATION_AUDIT.json").read_text(encoding="utf-8"))
    base_status = json.loads((BASE / "04_FINAL_INTEGRATED_READER_REFREEZE_STATUS.json").read_text(encoding="utf-8"))
    wps_audit = json.loads((QA / "wps_pages/document_render_audit.json").read_text(encoding="utf-8"))
    lo_audit = json.loads((QA / "lo_pages/document_render_audit.json").read_text(encoding="utf-8"))

    paths = {
        "wps_manuscript": DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf",
        "wps_supplement": DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf",
        "lo_manuscript": LO_DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf",
        "lo_supplement": LO_DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf",
    }
    base_paths = {
        "wps_manuscript": BASE / "documents" / f"{BASE_MANUSCRIPT_STEM}.pdf",
        "wps_supplement": BASE / "documents" / f"{BASE_SUPPLEMENT_STEM}.pdf",
        "lo_manuscript": BASE / "qa/libreoffice_documents" / f"{BASE_MANUSCRIPT_STEM}.pdf",
        "lo_supplement": BASE / "qa/libreoffice_documents" / f"{BASE_SUPPLEMENT_STEM}.pdf",
    }
    pages = {name: pdf_pages(path) for name, path in paths.items()}
    base_pages = {name: pdf_pages(path) for name, path in base_paths.items()}
    main_source = (RUN / "sources/Manuscript_scientific_stop_gate.md").read_text(encoding="utf-8")
    supp_source = (RUN / "sources/Supplementary_Information_scientific_stop_gate.md").read_text(encoding="utf-8")
    s4 = figure_properties(S4)
    accessibility = load_accessibility()
    new_sources = source_hashes(RUN / "figures/source_data")
    base_sources = source_hashes(BASE / "figures/source_data")

    text_diff = {
        "wps_manuscript": manuscript_phrase_transition(base_pages["wps_manuscript"], pages["wps_manuscript"]),
        "lo_manuscript": manuscript_phrase_transition(base_pages["lo_manuscript"], pages["lo_manuscript"]),
        "wps_supplement": expected_text_diff(base_pages["wps_supplement"], pages["wps_supplement"], OLD_TABLE_TITLE, NEW_TABLE_TITLE),
        "lo_supplement": expected_text_diff(base_pages["lo_supplement"], pages["lo_supplement"], OLD_TABLE_TITLE, NEW_TABLE_TITLE),
    }
    (RUN / "03_TEXT_DIFF_AUDIT.json").write_text(json.dumps(text_diff, indent=2) + "\n", encoding="utf-8", newline="\n")

    contact_sheets = list((QA / "wps_pages").glob("*_contact_*.png")) + list((QA / "lo_pages").glob("*_contact_*.png"))
    affected_pages = {path.name for path in (QA / "affected_pages").glob("*.png")}
    expected_affected_pages = {
        "wps_main_page_07.png", "wps_supp_page_03.png", "wps_supp_page_10.png",
        "lo_main_page_07.png", "lo_supp_page_03.png", "lo_supp_page_10.png",
    }
    checks = {
        "integration_pass": integration.get("status") == "PASS_CANONICAL_SOURCE_SYNC_AND_S4B_SOURCE_REDRAW_DOCUMENT_REBUILD_REQUIRED" and all(integration.get("checks", {}).values()),
        "document_build_pass": build.get("status") == "PASS_SCIENTIFIC_STOP_GATE_DOCX_BUILT_DUAL_RENDER_REQUIRED" and all(value for group in build.get("checks", {}).values() for value in group.values()),
        "previous_scientific_refreeze_locked": base_status.get("status") == "INTEGRATED_READER_PATH_AND_DISPLAY_PRUNE_SCIENTIFIC_REFREEZE_LOCKED",
        "wps_main_31_pages": len(pages["wps_manuscript"]) == 31,
        "lo_main_32_pages": len(pages["lo_manuscript"]) == 32,
        "supplement_16_pages_both": len(pages["wps_supplement"]) == len(pages["lo_supplement"]) == 16,
        "all_pages_nonblank": all(len(page) >= 80 for group in pages.values() for page in group),
        "wps_all_text_within_canvas": bool(wps_audit["all_pages_within_canvas"]),
        "lo_all_text_within_canvas": bool(lo_audit["all_pages_within_canvas"]),
        "all_render_markers_resolved": bool(wps_audit["all_markers_resolved"] and lo_audit["all_markers_resolved"]),
        "supplement_pagination_and_fingerprints_pass": pagination.get("status") == "PASS_SUPPLEMENT_PAGINATION_COHERENCE" and all(pagination.get("checks", {}).values()),
        "approved_source_diffs_and_pdf_semantics": all(item["expected_only_change"] for item in text_diff.values())
        and integration["checks"]["main_exactly_one_changed_line"]
        and integration["checks"]["supplement_exactly_one_changed_line"],
        "root_manuscript_phase17_byte_parity": ROOT_MANUSCRIPT.read_bytes() == (RUN / "sources/Manuscript_scientific_stop_gate.md").read_bytes(),
        "root_supplement_phase17_byte_parity": ROOT_SUPPLEMENT.read_bytes() == (RUN / "sources/Supplementary_Information_scientific_stop_gate.md").read_bytes(),
        "source_label_defined_wording_present": NEW_CHILDHOOD in main_source,
        "ambiguous_mapped_cells_absent": OLD_CHILDHOOD not in main_source,
        "selected_figure_table_title_present": NEW_TABLE_TITLE in supp_source,
        "s4_new_title_present": NEW_S4_TITLE in str(s4["text"]),
        "s4_old_title_absent": OLD_S4_TITLE not in str(s4["text"]),
        "s4_dimensions_unchanged": abs(float(s4["width_mm"]) - 170.0) <= 0.15 and abs(float(s4["height_mm"]) - 125.882) <= 0.15,
        "s4_text_minimum_6pt": float(s4["minimum_character_size_pt"]) >= 6.0,
        "s4_font_arial_embedded": bool(s4["arial_present"] and s4["fonts_embedded_subset_unicode"]),
        "all_15_source_data_files_byte_identical": len(new_sources) == 15 and new_sources == base_sources,
        "s4_source_hash_unchanged": new_sources.get("Supplementary_Figure_S4_source_data.csv") == S4_SOURCE_SHA256,
        "accessibility_zero_findings": len(accessibility) == 2 and all(counts.get("high", 0) == counts.get("medium", 0) == counts.get("low", 0) == 0 for counts in accessibility.values()),
        "contact_sheets_complete": len(contact_sheets) == 18,
        "affected_pages_complete": affected_pages == expected_affected_pages,
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Scientific stop-gate QA failed: {failed}")

    documents = {name: {"path": path.relative_to(ROOT).as_posix(), "pages": len(pages[name]), "sha256": sha256(path)} for name, path in paths.items()}
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SCIENTIFIC_PRESENTATION_STOP_GATE_LOCKED",
        "checks": checks,
        "failed_checks": [],
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_changed": False,
        "new_panels": 0,
        "replacement_panels": 0,
        "main_panels": {"keep": 21, "modify": 0, "replace": 0},
        "supplementary_panels": {"final_display": 38, "title_only_modify": 1, "replace": 0},
        "figure_s4": s4,
        "documents": documents,
        "text_diff_audit": text_diff,
        "source_hashes": new_sources,
        "canonical_sources": {"root_manuscript_sha256": sha256(ROOT_MANUSCRIPT), "root_supplement_sha256": sha256(ROOT_SUPPLEMENT), "exact_phase17_parity": True},
        "visual_qa": {"contact_sheets_reviewed": len(contact_sheets), "affected_pages_reviewed": len(affected_pages), "wps_and_libreoffice": True, "clipping_or_overlap_found": False},
        "accessibility": accessibility,
        "submission_package_sha256": PACKAGE_SHA256,
        "submission_package_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
        "next_stage": "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE",
    }
    FINAL_STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_action_report(status)
    write_manifest()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
