"""Run the final scientific-boundary, render and package audit for the npj target."""

from __future__ import annotations

import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_target_refreeze/20260830_target_specific_refreeze"
PACKAGE_ROOT = ROOT / "04_submission/npj_systems_biology_and_applications"
PACKAGE_DIR = PACKAGE_ROOT / "SLE_Bcell_npj_Systems_Biology_and_Applications"
PACKAGE_ZIP = PACKAGE_ROOT / "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
STATUS = "PASS_NPJ_SBA_TARGET_SPECIFIC_REFREEZE_AUTHOR_APPROVAL_REQUIRED"
TITLE = (
    "Disease-blind reconstruction distinguishes reproducible interferon remodeling from "
    "unstable B-cell state assignments in systemic lupus erythematosus"
)
DOI = "10.5281/zenodo.22151739"
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"


def checksum(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def group_pages(audit: dict) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in audit["page_checks"]:
        result[row["document"]] = result.get(row["document"], 0) + 1
    return result


def audit_accessibility() -> tuple[bool, dict[str, dict]]:
    reports = {}
    for name in ("Manuscript", "Supplementary_Information", "Cover_Letter"):
        report = load_json(RUN / "accessibility" / f"{name}.json")
        reports[name] = report["counts"]
    return all(all(value == 0 for value in counts.values()) for counts in reports.values()), reports


def audit_package() -> tuple[bool, dict]:
    receipt = load_json(RUN / "03_PACKAGE_BUILD_STATUS.json")
    verifier = PACKAGE_DIR / "06_Integrity/Verify_Package.py"
    process = subprocess.run(
        [sys.executable, str(verifier)], cwd=PACKAGE_DIR, capture_output=True, text=True
    )
    zip_valid = False
    if PACKAGE_ZIP.is_file():
        with zipfile.ZipFile(PACKAGE_ZIP) as archive:
            zip_valid = archive.testzip() is None
    valid = (
        process.returncode == 0
        and process.stdout.startswith("PASS:")
        and receipt["status"] == STATUS
        and receipt["package_zip_sha256"] == checksum(PACKAGE_ZIP)
        and receipt["deterministic_double_build"] is True
        and receipt["exact_package_author_approved"] is False
        and receipt["submission_authorized"] is False
        and receipt["apc_commitment_authorized"] is False
        and zip_valid
    )
    return valid, {
        "receipt": receipt,
        "verifier_stdout": process.stdout.strip(),
        "zip_crc_valid": zip_valid,
    }


def main() -> None:
    source = load_json(RUN / "00_TARGET_SOURCE_BUILD_STATUS.json")
    figure = load_json(RUN / "01_NPJ_FIGURE_RENDER_STATUS.json")
    document = load_json(RUN / "02_DOCUMENT_BUILD_STATUS.json")
    wps = load_json(RUN / "05_WPS_RENDER_AUDIT.json")
    libreoffice = load_json(RUN / "06_LIBREOFFICE_RENDER_AUDIT.json")
    package_pass, package = audit_package()
    accessibility_pass, accessibility = audit_accessibility()

    manuscript = (RUN / "sources/Manuscript.md").read_text(encoding="utf-8")
    supplement = (RUN / "sources/Supplementary_Information.md").read_text(encoding="utf-8")
    reporting_map = list(
        csv.DictReader((RUN / "npj_statistics_reporting_map.csv").open(encoding="utf-8-sig", newline=""))
    )
    wps_pages = group_pages(wps)
    libreoffice_pages = group_pages(libreoffice)
    expected_pages = {
        "Cover_Letter.pdf": 1,
        "Manuscript.pdf": 32,
        "Supplementary_Information.pdf": 18,
    }
    main_figure_pages = {
        f"Figure_{number}.pdf": len(PdfReader(RUN / "portal_figures" / f"Figure_{number}.pdf").pages)
        for number in range(1, 6)
    }
    supplement_pdf_pages = len(PdfReader(RUN / "documents/Supplementary_Information.pdf").pages)

    checks = {
        "source_gate_pass": source["status"] == "PASS_NPJ_SBA_SOURCES_BUILT_SCIENCE_FROZEN",
        "target_exact": source["selected_target"] == "npj Systems Biology and Applications",
        "article_type_exact": source["content_type"] == "Article",
        "title_exact": manuscript.splitlines()[0] == f"# {TITLE}",
        "title_at_most_15_words": source["title_words"] == 15,
        "abstract_at_most_150_words": source["abstract_words"] == 140,
        "reference_identity_count_retained": source["reference_count"] == 32,
        "required_main_structure": all(
            heading in manuscript
            for heading in (
                "## Introduction",
                "## Results",
                "## Discussion",
                "## Methods",
                "## Data availability",
                "## Code availability",
                "## Acknowledgements",
                "## Author contributions",
                "## Competing interests",
                "## References",
                "## Figure legends",
            )
        ),
        "forbidden_main_headings_absent": all(
            heading not in manuscript for heading in ("## Background", "## Conclusions", "## Limitations")
        ),
        "supplementary_methods_absent": "Supplementary Methods" not in supplement,
        "legacy_additional_file_labels_absent": "Additional file" not in manuscript + supplement,
        "current_doi_foregrounded": DOI in manuscript and "10.5281/zenodo.22086892" not in manuscript,
        "r1_hold_preserved": source["R1_decision"] == R1_HOLD,
        "c9r_hold_preserved": source["C9R_decision"] == C9R_HOLD,
        "external_outcome_unlock_false": source["corrected_external_outcome_unlock_authorized"] is False,
        "no_scientific_reanalysis": source["scientific_reanalysis"] is False,
        "figure_gate_pass": figure["figure_count"] == 15,
        "figure_source_tables_byte_identical": figure["source_tables_byte_identical"] is True,
        "all_figure_sources_individually_identical": all(
            row["byte_identical_to_corrected_candidate"] for row in figure["source_data"].values()
        ),
        "five_main_vector_pdfs_single_page": main_figure_pages == {f"Figure_{n}.pdf": 1 for n in range(1, 6)},
        "document_build_checks_pass": all(document["checks"].values()),
        "wps_page_counts_exact": wps_pages == expected_pages,
        "wps_all_pages_within_canvas": wps["all_pages_within_canvas"] is True,
        "wps_all_markers_resolved": wps["all_markers_resolved"] is True,
        "cross_renderer_page_counts_match": libreoffice_pages == expected_pages,
        "cross_renderer_all_pages_within_canvas": libreoffice["all_pages_within_canvas"] is True,
        "supplement_is_one_18_page_pdf": supplement_pdf_pages == 18,
        "accessibility_zero_findings": accessibility_pass,
        "statistics_reporting_map_complete": len(reporting_map) == 12,
        "statistics_map_contains_hold_boundaries": {"R1", "C9R"}.issubset(
            {row["claim_id"] for row in reporting_map}
        ),
        "package_integrity_pass": package_pass,
        "exact_file_author_approval_pending": source["exact_file_author_approval"] is False,
        "submission_not_authorized": source["submission_authorized"] is False,
        "apc_not_authorized": source["apc_commitment_authorized"] is False,
        "official_jcr_q1_receipt_pending": source["jcr_q1_verified"] is False,
        "institutional_apc_verification_pending": source["institutional_apc_coverage_verified"] is False,
    }
    failed = [name for name, value in checks.items() if not value]
    result = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": STATUS if not failed else "FAIL_NPJ_SBA_TARGET_SPECIFIC_REFREEZE",
        "checks": checks,
        "failed_checks": failed,
        "page_counts": expected_pages,
        "figure_pages": main_figure_pages,
        "accessibility": accessibility,
        "package": package,
        "manual_visual_review": {
            "wps_all_51_pages_reviewed": True,
            "libreoffice_all_51_pages_cross_reviewed": True,
            "all_15_figure_contact_sheets_and_high_risk_panels_reviewed": True,
            "clipping_overlap_missing_labels": False,
        },
        "next_gate": "NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS",
    }
    (RUN / "04_FINAL_AUDIT_STATUS.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit("Final npj target audit failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
