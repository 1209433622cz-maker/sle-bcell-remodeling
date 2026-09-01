#!/usr/bin/env python3
"""Regression tests for the role-aware Nature/npj artwork micropass."""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_nature_artwork_micropass/20260901_role_aware_typography_refreeze"


class NatureArtworkMicropassTests(unittest.TestCase):
    def test_final_maintenance_freeze_is_locked(self) -> None:
        status = json.loads(
            (RUN / "07_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(status["status"], "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE")
        self.assertTrue(all(status["checks"].values()))
        self.assertFalse(status["scientific_estimates_changed"])
        self.assertFalse(status["source_data_changed"])
        self.assertEqual(status["new_panels"], 0)
        self.assertEqual(status["replacement_panels"], 0)

    def test_root_sources_match_latest_scientific_sources(self) -> None:
        self.assertEqual(
            (ROOT / "01_manuscript/Manuscript.md").read_bytes(),
            (RUN / "sources/Manuscript_nature_artwork_micropass.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "01_manuscript/Supplementary_Information.md").read_bytes(),
            (RUN / "sources/Supplementary_Information_nature_artwork_micropass.md").read_bytes(),
        )

    def test_twelve_redraws_and_three_exact_keeps_are_audited(self) -> None:
        with (RUN / "01_ARTWORK_TYPOGRAPHY_AUDIT.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        after = [row for row in rows if row["stage"] == "after"]
        redraw = [row for row in after if row["action"] == "SOURCE_REDRAW_TYPOGRAPHY_ONLY"]
        exact = [row for row in after if row["action"] == "KEEP_EXACT"]
        self.assertEqual(len(redraw), 12)
        self.assertEqual(len(exact), 3)
        self.assertTrue(all(int(row["font_size_levels"]) >= 3 for row in redraw))
        self.assertTrue(all(float(row["minimum_font_pt"]) >= 5.5 for row in redraw))
        self.assertTrue(all(float(row["maximum_font_pt"]) <= 8.0 for row in redraw))


if __name__ == "__main__":
    unittest.main()
