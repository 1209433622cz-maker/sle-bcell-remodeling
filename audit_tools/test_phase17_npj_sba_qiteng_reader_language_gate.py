#!/usr/bin/env python3
"""Regression tests for the QiTeng reader-language and hard-negative gate."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_qiteng_round3/20260929_reader_language_hard_negative"
BASELINE = RUN / "input_r2/SLE_Bcell_Submission_Package"
PACKAGE = ROOT / "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


class QiTengReaderLanguageGateTests(unittest.TestCase):
    def test_build_contract_and_source_data_are_unchanged(self) -> None:
        status = json.loads((RUN / "build_status.json").read_text(encoding="utf-8"))
        self.assertTrue(status["figure_assertions_passed"])
        self.assertTrue(all(status["source_data_byte_identical"].values()))
        self.assertTrue(status["supplementary_figure_s10_source_data_byte_identical"])
        self.assertFalse(status["statistical_outputs_changed"])

    def test_reader_facing_figure_labels_are_present(self) -> None:
        figure2 = pdf_text(PACKAGE / "Figures/Figure_2.pdf")
        figure3 = pdf_text(PACKAGE / "Figures/Figure_3.pdf")
        figure_s10 = pdf_text(PACKAGE / "Author_Resources/Supplementary_Figures/Supplementary_Figure_S10.pdf")
        self.assertIn("Primary >=50", figure2)
        self.assertIn("Four prespecified programs in discovery", figure3)
        self.assertIn("Prespecified IFN-arm genes", figure3)
        self.assertIn("ULM after prespecified 12-gene depletion", figure_s10)
        self.assertIn("Prespecified targets retained (%)", figure_s10)

    def test_internal_reader_labels_are_absent_from_final_package_text(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in PACKAGE.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".csv", ".json"}
        )
        for forbidden in (
            "Four frozen programs",
            "Post-freeze sensitivity",
            "Frozen >=50",
            "Frozen IFN-arm genes",
            "ULM after frozen 12-gene depletion",
            "Frozen targets retained (%)",
        ):
            self.assertNotIn(forbidden, text)

    def test_scientific_archives_and_unchanged_owners_match_round2(self) -> None:
        unchanged = [
            "Manuscript/Manuscript.docx",
            "Manuscript/Manuscript.pdf",
            "Figures/Figure_1.pdf",
            "Figures/Figure_4.pdf",
            "Figures/Figure_5.pdf",
            "Supplementary_Data/Supplementary_Data_1_Figure_Source_Data.zip",
            "Supplementary_Data/Supplementary_Data_2_Regulator_Sensitivity.zip",
            "Supplementary_Data/Supplementary_Data_3_Full_Statistical_Results.zip",
            "Cover_Letter/Cover_Letter.docx",
            "Cover_Letter/Cover_Letter.pdf",
        ]
        for relative in unchanged:
            self.assertEqual(sha256(PACKAGE / relative), sha256(BASELINE / relative), relative)

    def test_manifest_is_complete_and_self_consistent(self) -> None:
        with (PACKAGE / "SHA256SUMS.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        actual = {
            path.relative_to(PACKAGE).as_posix()
            for path in PACKAGE.rglob("*")
            if path.is_file() and path.name != "SHA256SUMS.csv"
        }
        self.assertEqual(len(rows), 38)
        self.assertEqual(actual, {row["relative_path"] for row in rows})
        for row in rows:
            path = PACKAGE / row["relative_path"]
            self.assertEqual(path.stat().st_size, int(row["bytes"]), row["relative_path"])
            self.assertEqual(sha256(path), row["sha256"], row["relative_path"])

    def test_hard_negative_owners_remain_explicit(self) -> None:
        manuscript = (PACKAGE / "Manuscript/Manuscript.extracted.txt").read_text(encoding="utf-8")
        supplement = (PACKAGE / "Supplementary_Information/Supplementary_Information.extracted.txt").read_text(encoding="utf-8")
        self.assertIn("failed a prespecified antibody-secreting-cell overlap criterion", manuscript)
        self.assertIn("no corrected external disease effect was estimated", manuscript)
        self.assertIn("No inferential P value was calculated at n=2", manuscript)
        self.assertIn("does not support an overlap-independent interpretation", supplement)

    def test_zip_is_complete_and_unambiguous(self) -> None:
        zip_path = PACKAGE.parent / "SLE_Bcell_Submission_Package_2026-09-29.zip"
        with zipfile.ZipFile(zip_path) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.infolist()), 39)
            self.assertTrue(all(item.filename.startswith("SLE_Bcell_Submission_Package/") for item in archive.infolist()))


if __name__ == "__main__":
    unittest.main()
