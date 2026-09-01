#!/usr/bin/env python3
"""Regression tests for the Supplementary Table claim-owner micropass."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_supplementary_table_claim_owner/20260902_semantic_micropass"
PARENT = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order"
CURRENT = ROOT / "phase17_v7/npj_sba_figure1_boundary_promotion/20260902_source_rerender_gate"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SupplementaryTableClaimOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main = (ROOT / "01_manuscript/Manuscript.md").read_text(encoding="utf-8")
        cls.supplement = (ROOT / "01_manuscript/Supplementary_Information.md").read_text(encoding="utf-8")
        cls.integration = json.loads((RUN / "00_CLAIM_OWNER_MICROPASS_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))

    def test_integration_passed(self) -> None:
        self.assertEqual(self.integration["failed_checks"], [])
        self.assertTrue(all(self.integration["checks"].values()))

    def test_root_main_matches_current_scientific_candidate(self) -> None:
        self.assertEqual(
            sha256(ROOT / "01_manuscript/Manuscript.md"),
            sha256(CURRENT / "sources/Manuscript_figure1_boundary_promotion.md"),
        )

    def test_supplement_remains_immutable(self) -> None:
        self.assertEqual(
            sha256(ROOT / "01_manuscript/Supplementary_Information.md"),
            sha256(PARENT / "sources/Supplementary_Information_first_citation_order_refreeze.md"),
        )

    def test_s3_claim_owner_is_quantitative_synthesis(self) -> None:
        self.assertIn("principal quantitative anchors summarized in Supplementary Table S3", self.main)
        self.assertNotIn("causal regulation in SLE (Supplementary Table S3)", self.main)

    def test_s4_subowners_are_exact(self) -> None:
        self.assertEqual(self.main.count("Supplementary Fig. S9; Supplementary Table S4a"), 1)
        self.assertEqual(self.main.count("Supplementary Fig. S10; Supplementary Table S4b"), 1)
        self.assertNotIn("Supplementary Table S4)", self.main)

    def test_s5_s8_owner_is_reproducibility_sentence(self) -> None:
        self.assertEqual(self.main.count("SHA-256 manifests (Supplementary Tables S5-S8)"), 1)
        self.assertNotIn("present version (Supplementary Tables S5-S8)", self.main)

    def test_frozen_assets_unchanged(self) -> None:
        with (RUN / "04_FROZEN_FIGURE_AND_SOURCE_DATA_MANIFEST.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 45)
        self.assertTrue(all(row["unchanged"].lower() == "true" for row in rows))
        self.assertTrue(all(row["sha256_before"] == row["sha256_after"] for row in rows))

    def test_all_panels_remain_kept(self) -> None:
        with (RUN / "05_PANEL_DECISION_MATRIX.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len([row for row in rows if row["tier"] == "Main"]), 21)
        self.assertEqual(len([row for row in rows if row["tier"] == "Supplementary"]), 38)

    def test_final_status_when_present(self) -> None:
        path = RUN / "08_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json"
        if not path.exists():
            self.skipTest("Final render status not written yet")
        status = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE")
        self.assertEqual(status["failed_checks"], [])
        self.assertTrue(all(status["checks"].values()))

    def test_final_manifest_when_present(self) -> None:
        path = RUN / "09_FINAL_FILE_MANIFEST.csv"
        if not path.exists():
            self.skipTest("Final manifest not written yet")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        relative_paths = {row["relative_path"] for row in rows}
        self.assertNotIn(
            "phase17_v7/npj_sba_supplementary_table_claim_owner/20260902_semantic_micropass/08_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json",
            relative_paths,
        )
        self.assertEqual(
            len([item for item in relative_paths if "_contact_" in item and item.endswith(".png")]),
            12,
        )
        self.assertEqual(
            len([item for item in relative_paths if item.endswith("document_render_audit.json")]),
            2,
        )
        for row in rows:
            target = ROOT / row["relative_path"]
            self.assertTrue(target.is_file(), row["relative_path"])
            self.assertEqual(target.stat().st_size, int(row["bytes"]), row["relative_path"])
            self.assertEqual(sha256(target), row["sha256"], row["relative_path"])


if __name__ == "__main__":
    unittest.main()
