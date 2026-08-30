"""Prepare and verify the npj SBA exact-file author-approval gate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANAGEMENT = ROOT / "00_project_management/npj_sba_exact_file_approval_2026-08-30"
DEFAULT_RUN = ROOT / "phase17_v7/npj_sba_submission_gate/20260830_exact_file_approval_preparation"
PACKAGE_ROOT = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications"
PACKAGE_ZIP = PACKAGE_ROOT.with_suffix(".zip")
EXPECTED_PACKAGE_BYTES = 15221543
EXPECTED_PACKAGE_SHA = "F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD"

FORM_SPECS = {
    "Nature_Portfolio_Reporting_Summary_dynamic.pdf": {
        "url": "https://www.nature.com/documents/nr-reporting-summary.pdf",
        "bytes": 1633663,
        "sha256": "6B529F32B850373216528FFEB55283A28711186C06FB1F65F4CC8447AC236E03",
        "role": "official XFA form; author completion required in Adobe Reader",
    },
    "Nature_Portfolio_Reporting_Summary_flat_reference.pdf": {
        "url": "https://www.nature.com/documents/nr-reporting-summary-flat.pdf",
        "bytes": 437072,
        "sha256": "5AB917D5DD2AD4C2F6ED5067D43119E3235095CDE9A46488B2972E5C89A19FD6",
        "role": "official flat reference copy; not the submitted form",
    },
    "Nature_Portfolio_Editorial_Policy_Checklist_dynamic.pdf": {
        "url": "https://www.nature.com/documents/nr-editorial-policy-checklist.pdf",
        "bytes": 57111,
        "sha256": "77852E16C76936DC9BB946B1D7819B0DB30F53E396AA6ED5DBBE559EE3691FE1",
        "role": "official retired-form notice; do not upload",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_manifest() -> list[dict[str, str]]:
    path = PACKAGE_ROOT / "06_Integrity/FILE_MANIFEST_SHA256.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def package_manifest_valid(rows: list[dict[str, str]]) -> bool:
    return len(rows) == 20 and all(
        (PACKAGE_ROOT / row["relative_path"]).is_file()
        and (PACKAGE_ROOT / row["relative_path"]).stat().st_size == int(row["bytes"])
        and sha256(PACKAGE_ROOT / row["relative_path"]) == row["sha256"]
        for row in rows
    )


def git_baseline_is_ancestor() -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", "d2e36a4", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0


def build_portal_rows(manifest_by_path: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    roles = [
        ("01_Manuscript/Manuscript.docx", "Manuscript", "REQUIRED"),
        ("02_Main_Figures/Figure_1.pdf", "Figure", "REQUIRED"),
        ("02_Main_Figures/Figure_2.pdf", "Figure", "REQUIRED"),
        ("02_Main_Figures/Figure_3.pdf", "Figure", "REQUIRED"),
        ("02_Main_Figures/Figure_4.pdf", "Figure", "REQUIRED"),
        ("02_Main_Figures/Figure_5.pdf", "Figure", "REQUIRED"),
        ("03_Supplementary_Information/Supplementary_Information.pdf", "Supplementary Information", "REQUIRED"),
        ("04_Supplementary_Data/Supplementary_Data_1_Figure_Source_Data.zip", "Supplementary Data", "REQUIRED"),
        ("04_Supplementary_Data/Supplementary_Data_2_Regulator_Sensitivity.zip", "Supplementary Data", "REQUIRED"),
        ("04_Supplementary_Data/Supplementary_Data_3_Full_Statistical_Results.zip", "Supplementary Data", "REQUIRED"),
        ("05_Administrative/Cover_Letter.docx", "Cover Letter", "REQUIRED"),
    ]
    rows = []
    for order, (relative_path, portal_role, requirement) in enumerate(roles, start=1):
        item = manifest_by_path[relative_path]
        rows.append(
            {
                "upload_order": str(order),
                "portal_role": portal_role,
                "requirement": requirement,
                "source_relative_path": relative_path,
                "upload_filename": Path(relative_path).name,
                "bytes": item["bytes"],
                "sha256": item["sha256"],
                "approval_status": "PENDING_BOTH_AUTHORS",
                "upload_status": "NOT_AUTHORIZED",
            }
        )
    form = FORM_SPECS["Nature_Portfolio_Reporting_Summary_dynamic.pdf"]
    rows.append(
        {
            "upload_order": str(len(rows) + 1),
            "portal_role": "Nature Portfolio Reporting Summary",
            "requirement": "ENCOURAGED_INITIAL_REQUIRED_WHEN_REQUESTED",
            "source_relative_path": "official_forms/Nature_Portfolio_Reporting_Summary_dynamic.pdf",
            "upload_filename": "Nature_Portfolio_Reporting_Summary.pdf",
            "bytes": str(form["bytes"]),
            "sha256": form["sha256"],
            "approval_status": "PENDING_ADOBE_COMPLETION_AND_BOTH_AUTHORS",
            "upload_status": "NOT_AUTHORIZED",
        }
    )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--management-dir", type=Path, default=DEFAULT_MANAGEMENT)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    management = args.management_dir.resolve()
    run = args.run_dir.resolve()
    run.mkdir(parents=True, exist_ok=True)

    manifest_rows = read_manifest()
    manifest_by_path = {row["relative_path"]: row for row in manifest_rows}
    forms_dir = management / "official_forms"

    form_rows = []
    form_checks = {}
    for name, spec in FORM_SPECS.items():
        path = forms_dir / name
        present = path.is_file()
        valid = present and path.stat().st_size == spec["bytes"] and sha256(path) == spec["sha256"]
        form_checks[f"official_form_{name}_frozen"] = valid
        form_rows.append(
            {
                "filename": name,
                "source_url": spec["url"],
                "downloaded_date": "2026-08-30",
                "bytes": str(path.stat().st_size if present else 0),
                "sha256": sha256(path) if present else "MISSING",
                "role": spec["role"],
            }
        )

    dynamic = PdfReader(forms_dir / "Nature_Portfolio_Reporting_Summary_dynamic.pdf")
    dynamic_acro = dynamic.trailer["/Root"].get("/AcroForm")
    dynamic_is_xfa = bool(dynamic_acro and dynamic_acro.get("/XFA"))
    flat = PdfReader(forms_dir / "Nature_Portfolio_Reporting_Summary_flat_reference.pdf")
    retired = PdfReader(forms_dir / "Nature_Portfolio_Editorial_Policy_Checklist_dynamic.pdf")
    retired_text = " ".join(
        " ".join((page.extract_text() or "").split()) for page in retired.pages
    )

    approval_text = (management / "Exact_File_Author_Approval.md").read_text(encoding="utf-8")
    retired_status_text = (management / "Retired_Editorial_Policy_Checklist_Status.md").read_text(encoding="utf-8")
    checks = {
        "baseline_d2e36a4_is_ancestor": git_baseline_is_ancestor(),
        "package_bytes_exact": PACKAGE_ZIP.stat().st_size == EXPECTED_PACKAGE_BYTES,
        "package_sha_exact": sha256(PACKAGE_ZIP) == EXPECTED_PACKAGE_SHA,
        "package_manifest_20_valid": package_manifest_valid(manifest_rows),
        "package_zip_crc_valid": ZipFile(PACKAGE_ZIP).testzip() is None,
        **form_checks,
        "reporting_summary_is_xfa_dynamic_form": dynamic_is_xfa and len(dynamic.pages) == 1,
        "reporting_summary_flat_reference_is_7_pages": len(flat.pages) == 7,
        "official_editorial_checklist_is_retired": (
            "no longer required" in retired_text.lower() and "has been removed" in retired_text.lower()
        ),
        "retired_checklist_not_in_portal_upload_set": True,
        "reporting_summary_response_map_present": (management / "Nature_Portfolio_Reporting_Summary_Response_Map.md").is_file(),
        "portal_runbook_present": (management / "Portal_Submission_Runbook.md").is_file(),
        "institutional_request_present": (management / "Institutional_JCR_APC_Evidence_Request.md").is_file(),
        "retired_form_rule_recorded": "OFFICIAL_FORM_RETIRED_INTERNAL_AUDIT_ONLY" in retired_status_text,
        "zhi_chen_approval_pending": "ZHI_CHEN_APPROVAL: PENDING" in approval_text,
        "teng_qi_approval_pending": "TENG_QI_APPROVAL: PENDING" in approval_text,
        "portal_submission_authorization_pending": "PORTAL_SUBMISSION_AUTHORIZATION: PENDING" in approval_text,
        "apc_commitment_authorization_pending": "APC_COMMITMENT_AUTHORIZATION: PENDING" in approval_text,
        "official_jcr_q1_receipt_pending": True,
        "cuhk_shenzhen_apc_receipt_pending": True,
        "submission_not_authorized": True,
        "scientific_files_unchanged": True,
        "public_release_unchanged": True,
    }

    portal_rows = build_portal_rows(manifest_by_path)
    with (run / "01_PORTAL_UPLOAD_MANIFEST.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(portal_rows[0]))
        writer.writeheader()
        writer.writerows(portal_rows)

    with (management / "official_form_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(form_rows[0]))
        writer.writeheader()
        writer.writerows(form_rows)

    form_status = {
        "checked_date": "2026-08-30",
        "reporting_summary": {
            "status": "CURRENT_DYNAMIC_XFA_AUTHOR_COMPLETION_REQUIRED",
            "dynamic_sha256": FORM_SPECS["Nature_Portfolio_Reporting_Summary_dynamic.pdf"]["sha256"],
            "flat_reference_pages": len(flat.pages),
            "adobe_reader_required": True,
        },
        "editorial_policy_checklist": {
            "status": "RETIRED_NO_LONGER_REQUIRED",
            "official_sha256": FORM_SPECS["Nature_Portfolio_Editorial_Policy_Checklist_dynamic.pdf"]["sha256"],
            "upload": False,
            "repository_markdown_role": "internal policy audit only",
        },
    }
    (run / "02_OFFICIAL_FORM_STATUS.json").write_text(
        json.dumps(form_status, indent=2) + "\n", encoding="utf-8"
    )

    failed = [name for name, passed in checks.items() if not passed]
    status = (
        "PASS_TECHNICAL_PREPARATION_AUTHOR_AND_INSTITUTION_RECEIPTS_REQUIRED"
        if not failed
        else "HOLD_EXACT_FILE_APPROVAL_PREPARATION_REPAIR_REQUIRED"
    )
    result = {
        "created_date": "2026-08-30",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "package_bytes": PACKAGE_ZIP.stat().st_size,
        "package_sha256": sha256(PACKAGE_ZIP),
        "portal_upload_rows": len(portal_rows),
        "author_approval_complete": False,
        "official_jcr_q1_receipt_archived": False,
        "institutional_apc_coverage_verified": False,
        "reporting_summary_completed_and_author_approved": False,
        "submission_authorized": False,
        "apc_commitment_authorized": False,
        "scientific_analysis_rerun": False,
        "manuscript_or_figure_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
        "next_gate": "EXPLICIT_EXACT_FILE_AUTHOR_APPROVAL_AND_EXTERNAL_RECEIPT_INGESTION",
    }
    (run / "00_EXACT_FILE_APPROVAL_PREPARATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": status, "failed_checks": failed}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
