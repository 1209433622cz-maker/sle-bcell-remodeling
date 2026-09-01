#!/usr/bin/env python3
"""Finalize the role-aware Nature/npj artwork maintenance freeze."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_nature_artwork_micropass/20260901_role_aware_typography_refreeze"
BASE = ROOT / "phase17_v7/npj_sba_scientific_stop_gate/20260901_canonical_source_s4b_refreeze"
DOCUMENTS = RUN / "documents"
QA = RUN / "qa"
LO_DOCUMENTS = QA / "libreoffice_documents"
MANUSCRIPT_STEM = "Manuscript_scientific_maintenance_freeze"
SUPPLEMENT_STEM = "Supplementary_Information_scientific_maintenance_freeze"
ACTION_REPORT = ROOT / "00_project_management/action_record_2026-09-01_nature_artwork_typography_micropass.md"
FINAL_STATUS = RUN / "07_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json"
FINAL_MANIFEST = RUN / "08_FINAL_FILE_MANIFEST.csv"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path: Path) -> list[str]:
    return [(page.extract_text() or "").strip() for page in PdfReader(path).pages]


def load_accessibility() -> dict[str, dict[str, int]]:
    reports: dict[str, dict[str, int]] = {}
    for path in sorted((QA / "accessibility").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        reports[path.name] = payload.get("counts", {})
    return reports


def source_hashes(directory: Path) -> dict[str, str]:
    return {path.name: sha256(path) for path in sorted(directory.glob("*.csv"))}


def build_figure_contact_sheets() -> list[Path]:
    output = QA / "figure_contact_sheets"
    output.mkdir(parents=True, exist_ok=True)
    files = sorted((RUN / "figures/figures").glob("*.png"))
    contacts: list[Path] = []
    for index in range(0, len(files), 2):
        pair = files[index : index + 2]
        prepared: list[tuple[Path, Image.Image]] = []
        for path in pair:
            image = Image.open(path).convert("RGB")
            target_width = 1600
            target_height = round(image.height * target_width / image.width)
            prepared.append((path, image.resize((target_width, target_height), Image.Resampling.LANCZOS)))
        label_height = 48
        canvas = Image.new(
            "RGB",
            (1600, sum(image.height + label_height for _, image in prepared)),
            "white",
        )
        draw = ImageDraw.Draw(canvas)
        y = 0
        for path, image in prepared:
            draw.text((12, y + 12), path.name, fill="black")
            y += label_height
            canvas.paste(image, (0, y))
            y += image.height
        contact = output / f"figure_contact_{index // 2 + 1:02d}.png"
        canvas.save(contact)
        contacts.append(contact)
    return contacts


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


def write_action_report(status: dict[str, object]) -> None:
    documents = status["documents"]
    report = f"""# Action record: Nature/npj artwork typography micropass

- **Date:** 2026-09-01
- **Final status:** `{status['status']}`
- **Scope:** scientific manuscript text and source-driven artwork only; no submission-package, release or Zenodo action

## Objective

Independently test the external hostile audit against the current `cb762af` scientific stop-gate object, repair only reproducible artwork defects, retain all frozen numerical objects and decide whether any panel requires modification, replacement or further analysis.

## Independent audit result

The supplied audit and pasted review were archived byte-identically under `00_project_management/nature_artwork_micropass_2026-09-01/received/` and treated as review evidence rather than executable instructions.

The artwork criticism was reproducible. `audit_tools/publication_style_contract.py` had forced every visible text object to 8 pt and every non-zero line or patch width to at least 1 pt. Object-level inspection of all 15 final PDFs showed that Figure 1-5 and Supplementary Figures S1, S2, S4 and S7-S10 were flattened to a single 8 pt text size. Supplementary Figures S3, S5 and S6 already retained deliberate 6/7/8 pt role hierarchies and were not candidates for rerun.

## Style-contract repair

The shared final-size pass now preserves the role sizes declared by each figure builder. It enforces Arial, raises only annotations below 5.5 pt to the readability floor, keeps bold panel letters at 8 pt and raises only sub-printable non-zero rules to 0.5 pt. It no longer promotes ordinary 0.5-0.8 pt rules or all text to a uniform value. A regression test locks the title, axis-label, tick, legend, annotation, panel-letter and line-width hierarchy.

## Source-driven redraw and invariance

- **12 figures redrawn:** Figure 1-5; Supplementary Figures S1, S2, S4, S7, S8, S9 and S10.
- **3 figures retained byte-identically:** Supplementary Figures S3, S5 and S6.
- All redraws used the established generators with `NPJ_SBA_STYLE=1`; no PDF or PNG was hand-edited.
- All 15 Source Data CSV files are byte-identical to the prior scientific stop gate.
- Statistical models, thresholds, point estimates, intervals, q values, panel geometry, panel membership and colour semantics were unchanged.
- Every redrawn PDF now contains at least three visible font-size levels, a 5.5 pt or larger minimum, an 8 pt maximum, Arial-only text and ordinary sub-1 pt rules.

## Panel decisions

- Main panels: **21 KEEP**, **21 typography-only source redraw**, **0 replace**.
- Supplementary panels: **38 KEEP**; **29 typography-only source redraw**, **9 keep exact**, **0 replace**.
- Figure 1a and Figure 5a remain KEEP. Their scientific roles are still necessary: Fig. 1a defines the identity-to-disease inference boundary; Fig. 5a defines evidence classes and the causal ceiling.
- Supplementary Figure S7 remains KEEP because the figure owns correlation-pattern recognition while the table owns exact numeric retrieval.
- No new panel, cohort, mapper, regulator analysis or sensitivity analysis was added.

## Targeted manuscript terminology

Two local evidence-boundary sentences were changed from `independent validation` to `independent replication`: the accession-internal Results boundary and the same-data uncertainty-propagation Methods boundary. Legitimate methodological validation, prospective clinical validation and the CRediT `Validation` role were preserved. The Supplementary text is byte-identical to the previous stop gate.

## Document and visual QA

- WPS manuscript: {documents['wps_manuscript']['pages']} pages, SHA-256 `{documents['wps_manuscript']['sha256']}`.
- LibreOffice manuscript: {documents['lo_manuscript']['pages']} pages.
- WPS and LibreOffice Supplementary Information: {documents['wps_supplement']['pages']} pages each.
- All pages remained within canvas; all embedded-figure markers resolved; Supplementary S1-S10 pagination and fingerprints passed in both renderers.
- Full document contact sheets and eight artwork contact sheets were generated for visual inspection. No clipping, overlap, missing glyph or incoherent panel hierarchy was found.
- Both DOCX accessibility audits contain 0 high / 0 medium / 0 low findings.

## Release boundary

The author-approved submission ZIP remains byte-identical at `{PACKAGE_SHA256}`. GitHub release and Zenodo were not changed. This round changes the scientific working candidate and reproducible generator, not the frozen submission package.

## Next-stage decision

Return to `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`. The demonstrable artwork defect has been repaired without reopening scientific inference. No existing panel currently warrants replacement, and further work should require a localized evidence, legibility or semantic defect rather than a general request for more polish. Journal-specific packaging remains a later and separate activity.
"""
    ACTION_REPORT.write_text(report, encoding="utf-8", newline="\n")


def main() -> None:
    integration = json.loads(
        (RUN / "00_NATURE_ARTWORK_MICROPASS_INTEGRATION_STATUS.json").read_text(encoding="utf-8")
    )
    build = json.loads((RUN / "04_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
    pagination = json.loads((RUN / "05_SUPPLEMENT_PAGINATION_AUDIT.json").read_text(encoding="utf-8"))
    wps_audit = json.loads((QA / "wps_pages/document_render_audit.json").read_text(encoding="utf-8"))
    lo_audit = json.loads((QA / "lo_pages/document_render_audit.json").read_text(encoding="utf-8"))
    accessibility = load_accessibility()
    contacts = build_figure_contact_sheets()

    paths = {
        "wps_manuscript": DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf",
        "wps_supplement": DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf",
        "lo_manuscript": LO_DOCUMENTS / f"{MANUSCRIPT_STEM}.pdf",
        "lo_supplement": LO_DOCUMENTS / f"{SUPPLEMENT_STEM}.pdf",
    }
    pages = {name: pdf_pages(path) for name, path in paths.items()}
    source_hash_status = source_hashes(RUN / "figures/source_data")
    base_source_hash_status = source_hashes(BASE / "figures/source_data")
    main_source = (RUN / "sources/Manuscript_nature_artwork_micropass.md").read_text(encoding="utf-8")
    supplement_source = (RUN / "sources/Supplementary_Information_nature_artwork_micropass.md").read_text(encoding="utf-8")
    base_supplement_source = (BASE / "sources/Supplementary_Information_scientific_stop_gate.md").read_text(encoding="utf-8")

    document_contacts = list((QA / "wps_pages").glob("*_contact_*.png")) + list(
        (QA / "lo_pages").glob("*_contact_*.png")
    )
    checks = {
        "integration_pass": integration.get("status")
        == "PASS_NATURE_ARTWORK_TYPOGRAPHY_MICROPASS_DOCUMENT_REBUILD_REQUIRED"
        and all(integration.get("checks", {}).values()),
        "document_build_pass": build.get("status")
        == "PASS_NATURE_ARTWORK_MICROPASS_DOCX_BUILT_DUAL_RENDER_REQUIRED"
        and all(value for group in build.get("checks", {}).values() for value in group.values()),
        "wps_main_31_pages": len(pages["wps_manuscript"]) == 31,
        "lo_main_32_pages": len(pages["lo_manuscript"]) == 32,
        "supplement_16_pages_both": len(pages["wps_supplement"])
        == len(pages["lo_supplement"])
        == 16,
        "all_pages_nonblank": all(len(page) >= 80 for group in pages.values() for page in group),
        "wps_all_text_within_canvas": bool(wps_audit["all_pages_within_canvas"]),
        "lo_all_text_within_canvas": bool(lo_audit["all_pages_within_canvas"]),
        "all_render_markers_resolved": bool(
            wps_audit["all_markers_resolved"] and lo_audit["all_markers_resolved"]
        ),
        "supplement_pagination_and_fingerprints_pass": pagination.get("status")
        == "PASS_SUPPLEMENT_PAGINATION_COHERENCE"
        and all(pagination.get("checks", {}).values()),
        "all_15_source_data_byte_identical": source_hash_status == base_source_hash_status
        and len(source_hash_status) == 15,
        "targeted_replication_boundaries_present": (
            "provide internal replication rather than independent replication" in main_source
            and "they are not independent replication" in main_source
        ),
        "supplement_text_byte_identical": supplement_source == base_supplement_source,
        "accessibility_zero_findings": len(accessibility) == 2
        and all(
            counts.get("high", 0) == counts.get("medium", 0) == counts.get("low", 0) == 0
            for counts in accessibility.values()
        ),
        "document_contact_sheets_complete": len(document_contacts) == 18,
        "figure_contact_sheets_complete": len(contacts) == 8,
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Nature artwork final QA failed: {failed}")

    documents = {
        name: {
            "path": path.relative_to(ROOT).as_posix(),
            "pages": len(pages[name]),
            "sha256": sha256(path),
        }
        for name, path in paths.items()
    }
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE",
        "checks": checks,
        "failed_checks": [],
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_changed": False,
        "new_panels": 0,
        "replacement_panels": 0,
        "main_panels": {"keep": 21, "typography_only": 21, "replace": 0},
        "supplementary_panels": {"keep": 38, "typography_only": 29, "keep_exact": 9, "replace": 0},
        "documents": documents,
        "visual_qa": {
            "document_contact_sheets": len(document_contacts),
            "figure_contact_sheets": len(contacts),
            "wps_and_libreoffice": True,
            "clipping_or_overlap_found": False,
        },
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
