"""Regression tests for the npj SBA exact-file approval preparation gate."""

import csv
import json
import os
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(
    os.environ.get(
        "NPJ_SBA_APPROVAL_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_submission_gate/20260830_exact_file_approval_preparation",
    )
).resolve()
MANAGEMENT = ROOT / "00_project_management/npj_sba_exact_file_approval_2026-08-30"


class NpjSbaExactFileApprovalPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.status = json.loads(
            (RUN / "00_EXACT_FILE_APPROVAL_PREPARATION.json").read_text(encoding="utf-8")
        )

    def test_technical_preparation_passes_without_authorization(self):
        self.assertEqual(
            self.status["status"],
            "PASS_TECHNICAL_PREPARATION_AUTHOR_AND_INSTITUTION_RECEIPTS_REQUIRED",
        )
        self.assertEqual(self.status["failed_checks"], [])
        self.assertFalse(self.status["submission_authorized"])
        self.assertFalse(self.status["apc_commitment_authorized"])

    def test_package_is_exact_and_science_is_unchanged(self):
        self.assertEqual(self.status["package_bytes"], 15196223)
        self.assertEqual(
            self.status["package_sha256"],
            "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1",
        )
        self.assertFalse(self.status["scientific_analysis_rerun"])
        self.assertFalse(self.status["manuscript_text_changed"])
        self.assertTrue(self.status["supplementary_figure_s8_layout_changed"])
        self.assertTrue(self.status["manuscript_or_figure_changed"])
        self.assertTrue(self.status["checks"]["approval_contract_package_identity_exact"])
        self.assertTrue(self.status["checks"]["approval_contract_content_hashes_match_manifest"])

    def test_author_and_external_receipts_remain_pending(self):
        self.assertFalse(self.status["author_approval_complete"])
        self.assertFalse(self.status["official_jcr_q1_receipt_archived"])
        self.assertFalse(self.status["institutional_apc_coverage_verified"])
        self.assertFalse(self.status["reporting_summary_completed_and_author_approved"])

    def test_current_reporting_summary_and_retired_checklist_are_distinguished(self):
        forms = json.loads((RUN / "02_OFFICIAL_FORM_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(
            forms["reporting_summary"]["status"],
            "CURRENT_DYNAMIC_XFA_AUTHOR_COMPLETION_REQUIRED",
        )
        self.assertTrue(forms["reporting_summary"]["adobe_reader_required"])
        self.assertEqual(
            forms["editorial_policy_checklist"]["status"],
            "RETIRED_NO_LONGER_REQUIRED",
        )
        self.assertFalse(forms["editorial_policy_checklist"]["upload"])

    def test_portal_manifest_excludes_retired_form_and_is_not_authorized(self):
        with (RUN / "01_PORTAL_UPLOAD_MANIFEST.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 12)
        self.assertFalse(any("Editorial" in row["portal_role"] for row in rows))
        self.assertTrue(all(row["upload_status"] == "NOT_AUTHORIZED" for row in rows))
        self.assertEqual(rows[-1]["approval_status"], "PENDING_ADOBE_COMPLETION_AND_BOTH_AUTHORS")

    def test_approval_contract_has_four_independent_pending_markers(self):
        text = (MANAGEMENT / "Exact_File_Author_Approval.md").read_text(encoding="utf-8")
        for marker in (
            "ZHI_CHEN_APPROVAL: PENDING",
            "TENG_QI_APPROVAL: PENDING",
            "PORTAL_SUBMISSION_AUTHORIZATION: PENDING",
            "APC_COMMITMENT_AUTHORIZATION: PENDING",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
