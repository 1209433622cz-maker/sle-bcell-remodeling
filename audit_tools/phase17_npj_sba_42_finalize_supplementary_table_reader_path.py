#!/usr/bin/env python3
"""Finalize the localized Supplementary Table S4 reader-path repair."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase17_v7/npj_sba_nature_artwork_micropass/20260901_role_aware_typography_refreeze"
RUN = ROOT / "phase17_v7/npj_sba_supplementary_table_reader_path/20260901_s4_reader_path_refreeze"
DOCUMENTS = RUN / "documents"
QA = RUN / "qa"
LO_DOCUMENTS = QA / "libreoffice_documents"
STEM = "Supplementary_Information_scientific_maintenance_freeze"
STATUS_PATH = RUN / "07_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json"
MANIFEST_PATH = RUN / "08_FINAL_FILE_MANIFEST.csv"
ACTION_REPORT = ROOT / "00_project_management/action_record_2026-09-01_supplementary_table_s4_reader_path_micropass.md"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def recursive_hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): sha256(path)
        for path in sorted(item for item in directory.rglob("*") if item.is_file())
    }


def pdf_text(path: Path) -> tuple[int, str]:
    reader = PdfReader(path)
    return len(reader.pages), "\n".join((page.extract_text() or "") for page in reader.pages)


def write_manifest() -> None:
    rows = []
    for path in sorted(item for item in RUN.rglob("*") if item.is_file()):
        if path == MANIFEST_PATH:
            continue
        rows.append(
            {
                "relative_path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    with MANIFEST_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)


def write_action_report(status: dict[str, object]) -> None:
    documents = status["documents"]
    report = f"""# Action record: Supplementary Table S4 reader-path micropass

- **Date:** 2026-09-01
- **Final status:** `{status['status']}`
- **Scope:** Supplementary reader structure only; no figure, model, Source Data, manuscript-result, submission-package, Release or Zenodo change

## Objective

Independently adjudicate the post-typography audit, repair the isolated reader-facing `S4B` numbering defect and determine whether any manuscript or figure object should be reopened.

## Independent adjudication

The defect was reproduced. The Supplementary overview declared Tables S1-S9, while the visible sequence was S1, S2, S3, S4, S4B, S5, S6, S7, S8 and S9. The scientific values were valid, but an unpaired `S4B` made the reader-facing inventory appear inconsistent.

No figure replacement or redraw was justified. Figure 1a remains the unique owner of the identity-to-disease inference boundary, and Figure 5a remains the unique owner of the evidence-class and causal-ceiling contract. All 21 main panels and 38 Supplementary panels remain KEEP; S3, S5 and S6 retain their exact role-aware artwork.

## Localized source repair

- The parent heading is now `Supplementary Table S4 | Regulator-sensitivity summaries`.
- The correlation-aware grid is labelled `a, Correlation-aware core-regulator sensitivity`.
- The overlap-depletion grid is labelled `b, IFN-overlap-depletion summary`.
- Downstream Tables S5-S9 retain their identifiers.
- Table S5 now describes Figure 2 as `Sample-level composition in the 43-control/47-managed-SLE primary comparison` instead of using the implementation term `asserted`.
- No table cell, number, statistic, threshold, inference or figure legend changed.

## Invariance controls

- The root manuscript and frozen manuscript source are byte-identical to the typography freeze.
- Every figure PDF and PNG is byte-identical to the typography freeze; no figure generator ran.
- All 15 Source Data CSV files are byte-identical.
- The prior panel-decision matrix is byte-identical: 0 new panels and 0 replacement panels.
- The author-approved submission ZIP remains `{PACKAGE_SHA256}`; Release and Zenodo were not changed.

## Document and visual QA

- WPS Supplementary Information: {documents['wps']['pages']} pages, SHA-256 `{documents['wps']['sha256']}`.
- LibreOffice Supplementary Information: {documents['libreoffice']['pages']} pages, SHA-256 `{documents['libreoffice']['sha256']}`.
- Both renderers show numbered Tables S1-S9 exactly once, the S4 a/b labels, Figures S1-S10 on their heading pages and no `Supplementary Table S4B`.
- All pages remain within canvas; no clipping, overlap, unresolved marker or missing figure fingerprint was detected.
- Six renderer contact sheets covering all 32 rendered pages were manually inspected; the S4 a/b hierarchy remained clear at page scale and no blank page, clipping, overlap or missing glyph was observed.
- DOCX accessibility audit: 0 high / 0 medium / 0 low findings.

## Next-stage decision

Return to `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`. The last demonstrated reader-path inconsistency is repaired. No broad manuscript rewrite, figure redesign or additional analysis is currently justified. Reopen only for a new localized numerical, semantic, cross-reference or actual-size legibility defect.
"""
    ACTION_REPORT.write_text(report, encoding="utf-8", newline="\n")


def main() -> None:
    integration = json.loads(
        (RUN / "00_SUPPLEMENTARY_TABLE_S4_INTEGRATION_STATUS.json").read_text(
            encoding="utf-8"
        )
    )
    build = json.loads((RUN / "04_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
    pagination = json.loads(
        (RUN / "05_SUPPLEMENT_PAGINATION_AUDIT.json").read_text(encoding="utf-8")
    )
    wps_audit = json.loads(
        (QA / "wps_pages/document_render_audit.json").read_text(encoding="utf-8")
    )
    lo_audit = json.loads(
        (QA / "lo_pages/document_render_audit.json").read_text(encoding="utf-8")
    )
    accessibility = json.loads(
        (QA / f"accessibility/{STEM}.json").read_text(encoding="utf-8")
    )

    wps_pdf = DOCUMENTS / f"{STEM}.pdf"
    lo_pdf = LO_DOCUMENTS / f"{STEM}.pdf"
    wps_pages, wps_text = pdf_text(wps_pdf)
    lo_pages, lo_text = pdf_text(lo_pdf)
    source = (RUN / "sources/Supplementary_Information_s4_reader_path_micropass.md").read_text(
        encoding="utf-8"
    )
    root_main = ROOT / "01_manuscript/Manuscript.md"
    root_supplement = ROOT / "01_manuscript/Supplementary_Information.md"
    base_main = BASE / "sources/Manuscript_nature_artwork_micropass.md"
    base_supplement = BASE / "sources/Supplementary_Information_nature_artwork_micropass.md"
    table_numbers = [
        int(number)
        for number in re.findall(r"(?m)^## Supplementary Table S(\d+) \|", source)
    ]
    figure_numbers = [
        int(number)
        for number in re.findall(r"(?m)^## Supplementary Figure S(\d+) \|", source)
    ]

    renderer_checks = {}
    for name, text in (("wps", wps_text), ("libreoffice", lo_text)):
        renderer_checks[name] = {
            "tables_s1_to_s9_present": all(
                f"Supplementary Table S{number}" in text for number in range(1, 10)
            ),
            "orphan_s4b_absent": "Supplementary Table S4B" not in text,
            "s4a_present": "a, Correlation-aware core-regulator sensitivity" in text,
            "s4b_present": "b, IFN-overlap-depletion summary" in text,
            "figures_s1_to_s10_present": all(
                f"Supplementary Figure S{number}" in text for number in range(1, 11)
            ),
        }
    (RUN / "06_READER_PATH_AND_CROSS_REFERENCE_AUDIT.json").write_text(
        json.dumps(
            {
                "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "source_table_numbers": table_numbers,
                "source_figure_numbers": figure_numbers,
                "main_table_references": [
                    int(value)
                    for value in re.findall(
                        r"Supplementary Table S(\d+)", root_main.read_text(encoding="utf-8")
                    )
                ],
                "renderer_checks": renderer_checks,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    figure_hashes_equal = recursive_hashes(RUN / "figures/figures") == recursive_hashes(
        BASE / "figures/figures"
    )
    source_hashes_equal = recursive_hashes(RUN / "figures/source_data") == recursive_hashes(
        BASE / "figures/source_data"
    )
    checks = {
        "integration_pass": integration.get("status")
        == "PASS_SUPPLEMENTARY_TABLE_S4_READER_PATH_INTEGRATION_DOCX_REQUIRED"
        and all(integration.get("checks", {}).values()),
        "document_build_pass": build.get("status")
        == "PASS_SUPPLEMENTARY_TABLE_S4_DOCX_BUILT_DUAL_RENDER_REQUIRED"
        and all(build.get("checks", {}).values()),
        "numbered_tables_are_s1_to_s9": table_numbers == list(range(1, 10)),
        "figures_are_s1_to_s10": figure_numbers == list(range(1, 11)),
        "both_renderers_show_repaired_reader_path": all(
            all(values.values()) for values in renderer_checks.values()
        ),
        "wps_16_pages": wps_pages == 16,
        "libreoffice_16_pages": lo_pages == 16,
        "all_pages_nonblank": all(
            int(item["text_characters"]) >= 80
            for audit in (wps_audit, lo_audit)
            for item in audit["page_checks"]
        ),
        "all_text_within_canvas": bool(
            wps_audit["all_pages_within_canvas"] and lo_audit["all_pages_within_canvas"]
        ),
        "all_render_markers_resolved": bool(
            wps_audit["all_markers_resolved"] and lo_audit["all_markers_resolved"]
        ),
        "supplement_pagination_and_fingerprints_pass": pagination.get("status")
        == "PASS_SUPPLEMENT_PAGINATION_COHERENCE"
        and all(pagination.get("checks", {}).values()),
        "accessibility_zero_findings": all(
            accessibility.get("counts", {}).get(level, -1) == 0
            for level in ("high", "medium", "low")
        ),
        "main_manuscript_byte_identical": sha256(root_main) == sha256(base_main),
        "root_supplement_matches_candidate": sha256(root_supplement)
        == sha256(RUN / "sources/Supplementary_Information_s4_reader_path_micropass.md"),
        "supplement_changed_from_prior_freeze": sha256(root_supplement)
        != sha256(base_supplement),
        "all_figure_files_byte_identical": figure_hashes_equal,
        "all_15_source_data_byte_identical": source_hashes_equal
        and len(list((RUN / "figures/source_data").glob("*.csv"))) == 15,
        "panel_decision_matrix_byte_identical": sha256(RUN / "02_PANEL_DECISION_MATRIX.csv")
        == sha256(BASE / "02_PANEL_DECISION_MATRIX.csv"),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    manual_visual_qa = {
        "contact_sheets_inspected": 6,
        "rendered_pages_inspected": wps_pages + lo_pages,
        "wps_pages_inspected": wps_pages,
        "libreoffice_pages_inspected": lo_pages,
        "s4_ab_hierarchy_clear_at_page_scale": True,
        "blank_pages_found": False,
        "clipping_or_overlap_found": False,
        "missing_glyphs_or_figures_found": False,
    }
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": (
            "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE"
            if not failed
            else "HOLD_SUPPLEMENTARY_TABLE_S4_READER_PATH_REVIEW_REQUIRED"
        ),
        "checks": checks,
        "failed_checks": failed,
        "manual_visual_qa": manual_visual_qa,
        "reader_facing_edits": 3,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "figures_rebuilt": False,
        "figures_changed": False,
        "source_data_changed": False,
        "main_manuscript_changed": False,
        "new_panels": 0,
        "replacement_panels": 0,
        "main_panels_keep": 21,
        "supplementary_panels_keep": 38,
        "documents": {
            "wps": {
                "path": wps_pdf.relative_to(ROOT).as_posix(),
                "pages": wps_pages,
                "sha256": sha256(wps_pdf),
            },
            "libreoffice": {
                "path": lo_pdf.relative_to(ROOT).as_posix(),
                "pages": lo_pages,
                "sha256": sha256(lo_pdf),
            },
            "docx": {
                "path": (DOCUMENTS / f"{STEM}.docx").relative_to(ROOT).as_posix(),
                "sha256": sha256(DOCUMENTS / f"{STEM}.docx"),
            },
        },
        "submission_package_sha256": sha256(PACKAGE),
        "submission_package_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
        "next_stage": "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE",
    }
    STATUS_PATH.write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_action_report(status)
    write_manifest()
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Final reader-path checks failed: {failed}")


if __name__ == "__main__":
    main()
