#!/usr/bin/env python3
"""Regression tests for the Supplementary first-citation-order refreeze."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unittest
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SupplementaryCitationRefreezeTests(unittest.TestCase):
    def test_final_scientific_presentation_freeze_is_locked(self) -> None:
        status = json.loads(
            (RUN / "08_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(status["status"], "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE")
        self.assertTrue(all(status["checks"].values()))
        self.assertEqual(status["failed_checks"], [])
        self.assertFalse(status["scientific_estimates_changed"])
        self.assertFalse(status["figures_redrawn"])
        self.assertFalse(status["source_data_values_changed"])
        self.assertEqual(status["new_panels"], 0)
        self.assertEqual(status["replacement_panels"], 0)
        self.assertEqual(status["manual_visual_qa"]["contact_sheets_inspected"], 18)
        self.assertEqual(status["manual_visual_qa"]["rendered_pages_inspected"], 92)

    def test_reader_path_and_table_coverage_are_complete(self) -> None:
        main = (ROOT / "01_manuscript/Manuscript.md").read_text(encoding="utf-8")
        body = main.split("## Figure legends", 1)[0]
        seen = []
        for value in re.findall(r"Supplementary Fig(?:ure)?\. S(10|[1-9])", body):
            number = int(value)
            if number not in seen:
                seen.append(number)
        self.assertEqual(seen, list(range(1, 11)))
        status = json.loads(
            (RUN / "08_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(status["supplementary_table_citation_coverage"], list(range(1, 10)))

    def test_display_renumbering_is_byte_identical(self) -> None:
        with (RUN / "03_SUPPLEMENTARY_DISPLAY_ID_PROVENANCE.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 30)
        self.assertTrue(all(row["byte_identical"].lower() == "true" for row in rows))
        self.assertTrue(all(row["old_sha256"] == row["new_sha256"] for row in rows))
        self.assertEqual(len({(row["old_display_id"], row["new_display_id"]) for row in rows}), 10)

    def test_all_panels_are_retained(self) -> None:
        with (RUN / "02_PANEL_DECISION_MATRIX.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        main = [row for row in rows if row["tier"] == "Main"]
        supplement = [row for row in rows if row["tier"] == "Supplementary"]
        self.assertEqual(len(main), 21)
        self.assertEqual(len(supplement), 38)
        self.assertTrue(all(row["scientific_decision"] == "KEEP" for row in rows))
        self.assertIn("Figure 1a", {row["object"] for row in main})
        self.assertIn("Figure 5a", {row["object"] for row in main})

    def test_final_documents_and_package_are_stable(self) -> None:
        documents = RUN / "documents"
        lo_documents = RUN / "qa/libreoffice_documents"
        self.assertEqual(
            len(PdfReader(documents / "Manuscript_scientific_maintenance_freeze.pdf").pages),
            31,
        )
        self.assertEqual(
            len(PdfReader(lo_documents / "Manuscript_scientific_maintenance_freeze.pdf").pages),
            31,
        )
        self.assertEqual(
            len(
                PdfReader(
                    documents / "Supplementary_Information_scientific_maintenance_freeze.pdf"
                ).pages
            ),
            15,
        )
        self.assertEqual(
            len(
                PdfReader(
                    lo_documents / "Supplementary_Information_scientific_maintenance_freeze.pdf"
                ).pages
            ),
            15,
        )
        self.assertEqual(sha256(PACKAGE), PACKAGE_SHA256)


if __name__ == "__main__":
    unittest.main()
