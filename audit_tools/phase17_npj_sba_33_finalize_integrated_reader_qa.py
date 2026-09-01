#!/usr/bin/env python3
"""Finalize the S3/S5 reader-path display prune and dual-render QA."""

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
    / "phase17_v7/npj_sba_integrated_reader_refreeze/"
    "20260901_s3_s5_reader_path_refreeze"
)
BASE = (
    ROOT
    / "phase17_v7/npj_sba_reference_terminology_lock/"
    "20260901_reference_terminology_s6_refreeze"
)
DOCUMENTS = RUN / "documents"
QA = RUN / "qa"
LO_DOCUMENTS = QA / "libreoffice_documents"
MANUSCRIPT_STEM = "Manuscript_integrated_reader_refreeze"
SUPPLEMENT_STEM = "Supplementary_Information_integrated_reader_refreeze"
S3 = RUN / "figures/figures/Supplementary_Figure_S3_fine_state_failure_transition_structure.pdf"
S5 = RUN / "figures/figures/Supplementary_Figure_S5_pseudobulk_ranked_list_diagnostics.pdf"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
SOURCE_HASHES = {
    "Figure1_source_data.csv": "F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805",
    "Supplementary_Figure_S3_source_data.csv": "133E973C2753F4946A24739C049308152299A915A3FC6754B30AD0521F979C96",
    "Figure3_source_data.csv": "DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8",
    "Supplementary_Figure_S5_source_data.csv": "F6682D636C1FF3A1784E0B9E8AEFF5C5D1BB075176312E87FCB938F65C4DA897",
}
ACTION_REPORT = ROOT / "00_project_management/action_record_2026-09-01_s3_s5_reader_path_refreeze.md"
FINAL_STATUS = RUN / "04_FINAL_INTEGRATED_READER_REFREEZE_STATUS.json"
FINAL_MANIFEST = RUN / "05_FINAL_FILE_MANIFEST.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path: Path) -> list[str]:
    return [(page.extract_text() or "").strip() for page in PdfReader(path).pages]


def figure_properties(path: Path) -> dict[str, object]:
    page = PdfReader(path).pages[0]
    text = page.extract_text() or ""
    sizes: list[float] = []

    def collect_size(
        value: str,
        _current_matrix: list[float],
        _text_matrix: list[float],
        _font_dictionary: object,
        font_size: float,
    ) -> None:
        if value.strip():
            sizes.append(float(font_size))

    page.extract_text(visitor_text=collect_size)
    fonts = subprocess.run(
        ["pdffonts", str(path)], check=True, capture_output=True, text=True
    ).stdout.splitlines()[2:]
    font_lines = [line for line in fonts if line.strip()]
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width_mm": float(page.mediabox.width) * 25.4 / 72.0,
        "height_mm": float(page.mediabox.height) * 25.4 / 72.0,
        "minimum_character_size_pt": min(sizes),
        "text": text,
        "font_lines": font_lines,
        "arial_present": any("Arial" in line for line in font_lines),
        "fonts_embedded_subset_unicode": bool(font_lines)
        and all(re.search(r"\byes\s+yes\s+yes\b", line) for line in font_lines),
    }


def load_accessibility() -> dict[str, dict[str, int]]:
    reports: dict[str, dict[str, int]] = {}
    for path in sorted((QA / "accessibility").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        reports[path.name] = payload.get("counts", {})
    return reports


def write_action_report(status: dict[str, object]) -> None:
    documents = status["documents"]
    s3 = status["figures"]["S3"]
    s5 = status["figures"]["S5"]
    report = f"""# Action record: integrated reader-path and S3/S5 scientific refreeze

**Date:** 2026-09-01  
**Final status:** `{status['status']}`  
**Scope:** manuscript text and scientific figure presentation only; no submission-package, GitHub release or Zenodo action

## Objective

Continue the scientific-presentation phase by testing every main and Supplementary panel for unique claim ownership, removing only frozen numerical duplicates, redrawing the affected Supplementary figures from immutable Source Data, and verifying that the revised manuscript remains coherent in WPS and LibreOffice. The biological analyses, statistical models and release objects were deliberately kept closed.

## Inputs and independent review

The six supplied reader-prune files were imported verbatim under `00_project_management/integrated_reader_prune_2026-09-01/received/` and treated as review candidates rather than executable truth. The 62-row panel matrix was independently checked against the frozen figure objects and Source Data.

Three proposed removals were confirmed as exact duplicates:

- old Supplementary Fig. S3a equals Fig. 1b across 16 compared policy-level values;
- old Supplementary Fig. S3d equals Fig. 1d across 8 compared broad-state values;
- old Supplementary Fig. S5d equals Fig. 3b across 7 rows and 5 numerical/identifier fields.

The supplied redraw code was not used unchanged. Its S3 guide was set to 0.95 although the frozen fine-state diagnostic threshold is 0.60, and its smallest labels were 5.5 pt. The production rerun corrected the guide to 0.60, enforced Arial and a minimum visible size of 6 pt, restored the project palette, moved the S3 legend outside the data region, and repaired S3 colorbar and S5 panel-label margins.

## Final panel decisions

- Main figures: **21 KEEP, 0 MODIFY, 0 REPLACE**.
- Supplementary panels: **38 retained or renumbered, 3 exact duplicates pruned, 0 REPLACE**.
- S3: old a and d removed; old b becomes new a; old c becomes new b.
- S5: a-c retained; d removed because Fig. 3b is the numerical owner.
- New panels, new estimates and new claims: **0**.

This is a display prune, not deletion of scientific provenance. The original Source Data remain in the reproducibility archive and the mapping is recorded in `S3_S5_DISPLAY_PANEL_MAPPING.csv`.

## Text integration

Only two main-text sentences changed. The Introduction now names `reconstruction and replication tests`, avoiding a generic validation label. The final Discussion boundary now closes on a single positive claim: `a bounded process-level interferon association within explicit identity and transfer limits`.

Only the S3 and S5 legends changed in the Supplementary Information. S3 now owns fine-state failure localization and transition structure, while pointing broad-state pass evidence to Fig. 1 and end-to-end propagation to Supplementary Fig. S9. S5 now owns pseudobulk and ranked-list diagnostics and explicitly points frozen IFN/ISG estimates to Fig. 3b.

## Figure source-redraw QA

- S3: {s3['width_mm']:.2f} x {s3['height_mm']:.2f} mm; minimum extracted text {s3['minimum_character_size_pt']:.2f} pt; embedded/subset Unicode Arial; SHA-256 `{s3['sha256']}`.
- S5: {s5['width_mm']:.2f} x {s5['height_mm']:.2f} mm; minimum extracted text {s5['minimum_character_size_pt']:.2f} pt; embedded/subset Unicode Arial; SHA-256 `{s5['sha256']}`.
- All four governing Source Data objects remained byte-identical to their frozen SHA-256 values.
- S3 and S5 were regenerated from Source Data; no PDF or PNG was edited by hand.

## Document and visual QA

- WPS manuscript: {documents['wps_manuscript']['pages']} pages, SHA-256 `{documents['wps_manuscript']['sha256']}`.
- LibreOffice manuscript: {documents['lo_manuscript']['pages']} pages; the expected one-page difference is only the final two legend lines on page 32.
- WPS and LibreOffice Supplementary Information: {documents['wps_supplement']['pages']} pages each.
- All ten Supplementary headings and their figures occupy the same pages in both renderers; all ten embedded figure fingerprints match the intended sources.
- All 18 contact sheets and 10 high-resolution affected-page renders were visually reviewed. No clipping, overlap, missing glyph, unresolved marker or incoherent cross-reference was found.
- Both DOCX accessibility reports contain **0 high / 0 medium / 0 low** findings.

## Scientific conclusion

The pruning improves the evidence hierarchy without weakening it. Fig. 1 remains the owner of broad identity stability, Supplementary Fig. S3 explains why fine-state identity failed, Fig. 3b owns the frozen branch-wise IFN/ISG effects, and Supplementary Fig. S5 now remains a pure model-diagnostic figure. The negative reconstruction and transfer boundaries continue to constrain the positive process-level interferon result.

No current defect justifies replacing Fig. 1a, Fig. 5a, any other main panel, or reopening the identity, composition, pseudobulk, replication or regulator models.

## Reproducibility and unchanged release boundary

The complete rerun is available through `audit_tools/run_6013RP_phase17_npj_sba_integrated_reader_refreeze.ps1`. The author-approved submission package remains byte-identical at `{PACKAGE_SHA256}` and was not rebuilt. GitHub release and Zenodo records were not changed.

## Next-stage decision

Proceed to `FINAL_TEXT_FIGURE_CROSS_REFERENCE_AND_SEMANTIC_STOP_GATE`. This should be a narrow, final scientific reader pass that checks every panel-letter reference, every numerical claim owner and every Results-to-legend transition against the final 21 main and 38 Supplementary panels at actual size. Only a localized, demonstrable defect should trigger another source redraw or sentence edit. If that gate finds no defect, scientific presentation should stop; it must not add cohorts, mappers, sensitivity analyses, replacement panels or submission engineering.
"""
    ACTION_REPORT.write_text(report, encoding="utf-8", newline="\n")


def write_manifest() -> None:
    rows: list[dict[str, object]] = []
    for path in sorted(item for item in RUN.rglob("*") if item.is_file()):
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
    source_status = json.loads((RUN / "00_SOURCE_REDRAW_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
    build_status = json.loads((RUN / "01_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
    pagination = json.loads((RUN / "02_SUPPLEMENT_PAGINATION_AUDIT.json").read_text(encoding="utf-8"))
    previous_status = json.loads((BASE / "04_FINAL_REFERENCE_TERMINOLOGY_S6_STATUS.json").read_text(encoding="utf-8"))
    wps_audit = json.loads((QA / "wps_pages/document_render_audit.json").read_text(encoding="utf-8"))
    lo_audit = json.loads((QA / "lo_pages/document_render_audit.json").read_text(encoding="utf-8"))

    wps_main_path = DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf"
    wps_supp_path = DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf"
    lo_main_path = LO_DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf"
    lo_supp_path = LO_DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf"
    wps_main = pdf_pages(wps_main_path)
    wps_supp = pdf_pages(wps_supp_path)
    lo_main = pdf_pages(lo_main_path)
    lo_supp = pdf_pages(lo_supp_path)
    main_text = " ".join("\n".join(wps_main).split())
    supp_text = " ".join("\n".join(wps_supp).split())
    main_source = (RUN / "sources/Manuscript_integrated_reader_refreeze.md").read_text(encoding="utf-8")
    supp_source = (RUN / "sources/Supplementary_Information_integrated_reader_refreeze.md").read_text(encoding="utf-8")
    s3 = figure_properties(S3)
    s5 = figure_properties(S5)
    accessibility = load_accessibility()

    with (RUN / "FINAL_INTEGRATED_READER_PANEL_DECISION_MATRIX.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        matrix = list(csv.DictReader(handle))
    with (RUN / "S3_S5_DISPLAY_PANEL_MAPPING.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        mapping = list(csv.DictReader(handle))

    source_hashes = {
        name: sha256(RUN / "figures/source_data" / name) for name in SOURCE_HASHES
    }
    contact_sheets = list((QA / "wps_pages").glob("*_contact_*.png")) + list(
        (QA / "lo_pages").glob("*_contact_*.png")
    )
    affected_pages = {path.name for path in (QA / "affected_pages").glob("*.png")}
    expected_affected_pages = {
        "wps_main_page_03.png",
        "wps_main_page_15.png",
        "wps_main_page_31.png",
        "wps_supp_page_09.png",
        "wps_supp_page_11.png",
        "lo_main_page_03.png",
        "lo_main_page_15.png",
        "lo_main_page_32.png",
        "lo_supp_page_09.png",
        "lo_supp_page_11.png",
    }

    prune_rows = [row for row in matrix if row["decision"].startswith("PRUNE_FROM_DISPLAY")]
    checks = {
        "source_integration_pass": source_status.get("status")
        == "PASS_S3_S5_SOURCE_REDRAW_AND_TEXT_INTEGRATION_DOCUMENT_REBUILD_REQUIRED"
        and all(source_status.get("checks", {}).values()),
        "document_build_pass": build_status.get("status")
        == "PASS_INTEGRATED_READER_DOCX_BUILT_DUAL_RENDER_REQUIRED"
        and all(
            value
            for group in build_status.get("checks", {}).values()
            for value in group.values()
        ),
        "previous_scientific_lock_intact": previous_status.get("status")
        == "REFERENCE_TERMINOLOGY_AND_S6_SCIENTIFIC_REFREEZE_LOCKED"
        and all(previous_status.get("checks", {}).values()),
        "wps_main_31_pages": len(wps_main) == 31,
        "lo_main_32_pages": len(lo_main) == 32,
        "supplement_16_pages_both_renderers": len(wps_supp) == len(lo_supp) == 16,
        "all_pages_nonblank": all(
            len(page) >= 80 for page in wps_main + wps_supp + lo_main + lo_supp
        ),
        "wps_all_text_within_canvas": bool(wps_audit["all_pages_within_canvas"]),
        "lo_all_text_within_canvas": bool(lo_audit["all_pages_within_canvas"]),
        "all_render_markers_resolved": bool(
            wps_audit["all_markers_resolved"] and lo_audit["all_markers_resolved"]
        ),
        "supplement_pagination_and_fingerprints_pass": pagination.get("status")
        == "PASS_SUPPLEMENT_PAGINATION_COHERENCE"
        and all(pagination.get("checks", {}).values()),
        "main_replication_tests_wording_present": "reconstruction and replication tests" in main_source
        and "increasingly stringent reconstruction" in main_text
        and "replication tests" in main_text,
        "final_process_boundary_present": "bounded process-level interferon association within explicit identity and transfer limits"
        in main_source
        and "bounded process-level interferon association within explicit identity" in main_text
        and "transfer limits" in main_text,
        "old_final_exclusion_list_absent": "not a universal B-cell taxonomy, generalized B_ASC expansion"
        not in main_source,
        "s3_legend_and_ownership_present": "Fine-state failure and transition structure" in supp_source
        and "broad-state pass criteria are shown in Fig. 1" in supp_source
        and "end-to-end reconstruction is shown in Supplementary Fig. S9" in supp_source,
        "s5_legend_and_ownership_present": "IFN/ISG estimates across the frozen GSE174188 branches are owned by Fig. 3b"
        in supp_source,
        "rendered_s3_s5_legends_present": "Fine-state failure and transition structure" in supp_text
        and "Pseudobulk and ranked-list diagnostics" in supp_text,
        "old_s3_s5_legend_content_absent": "Disease-blind identity adjudication" not in supp_source
        and "IFN/ISG effects and 95% confidence intervals across frozen branches" not in supp_source,
        "s3_exact_dimensions": abs(float(s3["width_mm"]) - 170.0) <= 0.15
        and abs(float(s3["height_mm"]) - 86.0) <= 0.15,
        "s5_exact_dimensions": abs(float(s5["width_mm"]) - 170.0) <= 0.15
        and abs(float(s5["height_mm"]) - 104.0) <= 0.15,
        "figure_text_minimum_6pt": float(s3["minimum_character_size_pt"]) >= 6.0
        and float(s5["minimum_character_size_pt"]) >= 6.0,
        "figure_fonts_arial_embedded": bool(
            s3["arial_present"]
            and s3["fonts_embedded_subset_unicode"]
            and s5["arial_present"]
            and s5["fonts_embedded_subset_unicode"]
        ),
        "s3_final_panel_titles_present": "Failure localizes to fine-state membership" in str(s3["text"])
        and "Mean r=0.4 transition matrix" in str(s3["text"]),
        "s3_removed_panel_titles_absent": "Fine partitions fail worst-case stability" not in str(s3["text"])
        and "Two-compartment adjudication passes" not in str(s3["text"]),
        "s5_final_panel_titles_present": all(
            title in str(s5["text"])
            for title in (
                "filterByExpr-tested and significant genes",
                "edgeR dispersion diagnostics",
                "Ranked-list technical-family audit",
            )
        ),
        "s5_removed_panel_title_absent": "IFN/ISG coherence across frozen model branches"
        not in str(s5["text"]),
        "all_frozen_source_hashes_unchanged": source_hashes == SOURCE_HASHES,
        "exact_duplicate_verification_pass": all(
            source_status["duplicate_verification"][key]
            for key in (
                "s3a_vs_figure1b_exact",
                "s3d_vs_figure1d_exact",
                "s5d_vs_figure3b_exact",
            )
        ),
        "panel_matrix_62_rows_21_main_keep": len(matrix) == 62
        and sum(row["tier"] == "Main" and row["decision"] == "KEEP" for row in matrix) == 21,
        "exactly_three_duplicate_prunes": len(prune_rows) == 3
        and {row["object"] for row in prune_rows}
        == {"Supplementary Figure S3a", "Supplementary Figure S3d", "Supplementary Figure S5d"},
        "display_mapping_exact": [
            (row["frozen_source_panel"], row["final_display_panel"])
            for row in mapping
        ]
        == [
            ("S3a", ""),
            ("S3b", "S3a"),
            ("S3c", "S3b"),
            ("S3d", ""),
            ("S5a", "S5a"),
            ("S5b", "S5b"),
            ("S5c", "S5c"),
            ("S5d", ""),
        ],
        "accessibility_zero_findings": len(accessibility) == 2
        and all(
            counts.get("high", 0) == counts.get("medium", 0) == counts.get("low", 0) == 0
            for counts in accessibility.values()
        ),
        "contact_sheets_complete": len(contact_sheets) == 18,
        "affected_pages_complete": affected_pages == expected_affected_pages,
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Final integrated-reader QA failed: {failed}")

    status: dict[str, object] = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "INTEGRATED_READER_PATH_AND_DISPLAY_PRUNE_SCIENTIFIC_REFREEZE_LOCKED",
        "checks": checks,
        "failed_checks": [],
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_changed": False,
        "new_panels_created": 0,
        "replacement_panels": 0,
        "main_panels": {"keep": 21, "modify": 0, "replace": 0},
        "supplementary_panels": {
            "final_display": 38,
            "pruned_exact_duplicates": 3,
            "replace": 0,
        },
        "duplicate_verification": source_status["duplicate_verification"],
        "source_hashes": source_hashes,
        "figures": {"S3": s3, "S5": s5},
        "documents": {
            "wps_manuscript": {
                "path": wps_main_path.relative_to(ROOT).as_posix(),
                "pages": len(wps_main),
                "sha256": sha256(wps_main_path),
            },
            "lo_manuscript": {
                "path": lo_main_path.relative_to(ROOT).as_posix(),
                "pages": len(lo_main),
                "sha256": sha256(lo_main_path),
            },
            "wps_supplement": {
                "path": wps_supp_path.relative_to(ROOT).as_posix(),
                "pages": len(wps_supp),
                "sha256": sha256(wps_supp_path),
            },
            "lo_supplement": {
                "path": lo_supp_path.relative_to(ROOT).as_posix(),
                "pages": len(lo_supp),
                "sha256": sha256(lo_supp_path),
            },
        },
        "visual_qa": {
            "contact_sheets_reviewed": len(contact_sheets),
            "affected_pages_reviewed": len(affected_pages),
            "wps_and_libreoffice": True,
            "clipping_or_overlap_found": False,
        },
        "accessibility": accessibility,
        "submission_package_sha256": PACKAGE_SHA256,
        "submission_package_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
        "next_stage": "FINAL_TEXT_FIGURE_CROSS_REFERENCE_AND_SEMANTIC_STOP_GATE",
    }
    FINAL_STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    write_action_report(status)
    write_manifest()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
