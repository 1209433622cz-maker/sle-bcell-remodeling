#!/usr/bin/env python3
"""Regression tests for the localized Supplementary Table S4 reader-path repair."""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase17_v7/npj_sba_nature_artwork_micropass/20260901_role_aware_typography_refreeze"
RUN = ROOT / "phase17_v7/npj_sba_supplementary_table_reader_path/20260901_s4_reader_path_refreeze"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): sha256(path)
        for path in sorted(item for item in directory.rglob("*") if item.is_file())
    }


class SupplementaryTableReaderPathTests(unittest.TestCase):
    def test_final_maintenance_freeze_is_locked(self) -> None:
        status = json.loads(
            (RUN / "07_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(status["status"], "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE")
        self.assertTrue(all(status["checks"].values()))
        self.assertFalse(status["scientific_estimates_changed"])
        self.assertFalse(status["figures_changed"])
        self.assertFalse(status["source_data_changed"])
        self.assertEqual(status["new_panels"], 0)
        self.assertEqual(status["replacement_panels"], 0)
        self.assertEqual(status["manual_visual_qa"]["contact_sheets_inspected"], 6)
        self.assertEqual(status["manual_visual_qa"]["rendered_pages_inspected"], 32)
        self.assertTrue(status["manual_visual_qa"]["s4_ab_hierarchy_clear_at_page_scale"])
        self.assertFalse(status["manual_visual_qa"]["blank_pages_found"])
        self.assertFalse(status["manual_visual_qa"]["clipping_or_overlap_found"])

    def test_historical_sources_remain_immutable(self) -> None:
        self.assertEqual(
            sha256(RUN / "sources/Manuscript_scientific_maintenance_freeze.md"),
            "9A70A71A82ECFCCD5B6D65ABC5418D83E214521297663CD83878E3D2E7E25A27",
        )
        self.assertEqual(
            sha256(RUN / "sources/Supplementary_Information_s4_reader_path_micropass.md"),
            "0E2C43BD591115767B4B90BE6852071D340C79F02E64CAFF2BB9EDE69283C96B",
        )

    def test_reader_facing_numbering_is_unambiguous(self) -> None:
        source = (ROOT / "01_manuscript/Supplementary_Information.md").read_text(
            encoding="utf-8"
        )
        numbers = [
            int(value)
            for value in re.findall(r"(?m)^## Supplementary Table S(\d+) \|", source)
        ]
        self.assertEqual(numbers, list(range(1, 10)))
        self.assertNotIn("Supplementary Table S4B", source)
        self.assertIn("**a, Correlation-aware core-regulator sensitivity**", source)
        self.assertIn("**b, IFN-overlap-depletion summary**", source)
        self.assertNotIn("asserted 43/47 primary groups", source)

    def test_figures_and_source_data_are_byte_identical(self) -> None:
        self.assertEqual(hashes(RUN / "figures/figures"), hashes(BASE / "figures/figures"))
        self.assertEqual(hashes(RUN / "figures/source_data"), hashes(BASE / "figures/source_data"))


if __name__ == "__main__":
    unittest.main()
