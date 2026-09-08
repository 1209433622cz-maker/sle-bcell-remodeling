#!/usr/bin/env python3
"""Regression tests for the final cross-document scientific-presentation freeze."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ScientificPresentationMaintenanceFreezeTests(unittest.TestCase):
    def test_integration_and_document_build_passed(self) -> None:
        integration = json.loads((RUN / "06_FINAL_CROSS_DOCUMENT_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
        build = json.loads((RUN / "07_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(integration["failed_checks"], [])
        self.assertEqual(build["failed_checks"], [])
        self.assertTrue(all(integration["checks"].values()))
        self.assertTrue(all(build["checks"].values()))

    def test_source_driven_edits_are_exact(self) -> None:
        before_main = (RUN / "sources/Manuscript_before_final_cross_document_freeze.md").read_text(encoding="utf-8")
        after_main = (RUN / "sources/Manuscript_scientific_presentation_freeze.md").read_text(encoding="utf-8")
        before_supp = (RUN / "sources/Supplementary_Information_before_final_cross_document_freeze.md").read_text(encoding="utf-8")
        after_supp = (RUN / "sources/Supplementary_Information_scientific_presentation_freeze.md").read_text(encoding="utf-8")
        self.assertEqual(before_main.count("within explicit identity and transfer limits."), 1)
        self.assertEqual(after_main.count("within explicit identity, transfer and mechanistic limits."), 1)
        self.assertEqual(before_main.replace("within explicit identity and transfer limits.", "within explicit identity, transfer and mechanistic limits.", 1), after_main)
        changed_s5_rows = [row for row in read_csv(RUN / "05_TEXT_EDIT_LEDGER.csv") if row["document"] == "Supplementary Information"]
        self.assertEqual(len(changed_s5_rows), 3)
        reconstructed = before_supp
        for row in changed_s5_rows:
            self.assertEqual(reconstructed.count(row["old"]), 1)
            reconstructed = reconstructed.replace(row["old"], row["new"], 1)
        self.assertEqual(reconstructed, after_supp)

    def test_independent_cross_document_audit_is_54_of_54(self) -> None:
        rows = read_csv(RUN / "01_FINAL_CROSS_DOCUMENT_AUDIT_REPRODUCED.csv")
        self.assertEqual(len(rows), 54)
        self.assertTrue(all(row["pass"].lower() == "true" for row in rows))

    def test_claim_and_panel_ownership_are_locked(self) -> None:
        claims = read_csv(RUN / "02_FINAL_CLAIM_OWNER_MATRIX.csv")
        panels = read_csv(RUN / "03_FINAL_MAIN_PANEL_DECISION_MATRIX.csv")
        self.assertEqual(len(claims), 11)
        self.assertTrue(all(row["status"] == "KEEP" for row in claims))
        self.assertEqual(len(panels), 21)
        self.assertTrue(all(row["final_decision"].startswith("KEEP") for row in panels))
        replacements = [row["panel"] for row in panels if "source replacement already accepted" in row["final_decision"].lower()]
        self.assertEqual(replacements, ["Figure 1d", "Figure 4d", "Figure 5d"])

    def test_all_figure_and_source_data_assets_are_unchanged(self) -> None:
        rows = read_csv(RUN / "04_FROZEN_FIGURE_AND_SOURCE_DATA_MANIFEST.csv")
        self.assertEqual(len(rows), 45)
        self.assertTrue(all(row["unchanged"].lower() == "true" for row in rows))
        self.assertTrue(all(row["parent_sha256"] == row["candidate_sha256"] for row in rows))

    def test_root_sources_and_submission_package_are_locked(self) -> None:
        self.assertEqual(sha256(ROOT / "01_manuscript/Manuscript.md"), sha256(RUN / "sources/Manuscript_scientific_presentation_freeze.md"))
        self.assertEqual(sha256(ROOT / "01_manuscript/Supplementary_Information.md"), sha256(RUN / "sources/Supplementary_Information_scientific_presentation_freeze.md"))
        self.assertEqual(sha256(PACKAGE), "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1")

    def test_final_status_and_manifest_when_present(self) -> None:
        status_path = RUN / "09_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json"
        manifest_path = RUN / "10_FINAL_FILE_MANIFEST.csv"
        if not status_path.exists() or not manifest_path.exists():
            self.skipTest("Final maintenance-freeze status not written yet")
        status = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE")
        self.assertEqual(status["failed_checks"], [])
        self.assertTrue(all(status["checks"].values()))
        self.assertEqual(status["page_pixel_comparison"]["manuscript_identical_pages"], 30)
        self.assertEqual(status["page_pixel_comparison"]["manuscript_changed_pages"], [15])
        self.assertEqual(status["page_pixel_comparison"]["supplement_identical_pages"], 11)
        self.assertEqual(status["page_pixel_comparison"]["supplement_changed_pages"], [3, 4, 5, 6])
        rows = read_csv(manifest_path)
        self.assertEqual(status["final_manifest"]["rows"], len(rows))
        for row in rows:
            target = ROOT / row["relative_path"]
            self.assertTrue(target.is_file(), row["relative_path"])
            self.assertEqual(target.stat().st_size, int(row["bytes"]), row["relative_path"])
            self.assertEqual(sha256(target), row["sha256"], row["relative_path"])


if __name__ == "__main__":
    unittest.main()
