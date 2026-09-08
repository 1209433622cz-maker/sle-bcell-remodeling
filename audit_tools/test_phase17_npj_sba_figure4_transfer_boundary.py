#!/usr/bin/env python3
"""Regression tests for the Figure 4 transfer-boundary source rerender."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_figure4_transfer_boundary/20260907_source_rerender_gate"
CURRENT = ROOT / "phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Figure4TransferBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.integration = json.loads((RUN / "05_FIGURE4_TRANSFER_BOUNDARY_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))

    def test_integration_passed(self) -> None:
        self.assertEqual(self.integration["failed_checks"], [])
        self.assertTrue(all(self.integration["checks"].values()))

    def test_frozen_source_hashes(self) -> None:
        expected = {
            "Figure4_source_data.csv": "F3604F40DAEDB0DD01617BB223A8762323C8AAC7F16185292367B9A13FEC4755",
            "Figure5_source_data.csv": "A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B",
            "Supplementary_Figure_S7_source_data.csv": "A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6",
            "Supplementary_Figure_S8_source_data.csv": "FF4309EBAF761A0563F018AE1BE07212EF2CB2241E79DF12C374BCB1426A60FF",
            "Supplementary_Figure_S9_source_data.csv": "D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3",
            "Supplementary_Figure_S10_source_data.csv": "26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2",
        }
        for name, value in expected.items():
            self.assertEqual(sha256(RUN / "source_inputs" / name), value, name)

    def test_required_elastic_net_calibration_is_exact(self) -> None:
        with (RUN / "01_FIGURE4_CALIBRATION_DERIVATION.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = {row["metric"]: row for row in csv.DictReader(handle)}
        expected = {
            "Coverage": (0.941958, 0.80, "criterion met"),
            "B_CONV precision": (0.996450, 0.90, "criterion met"),
            "B_ASC precision": (0.885210, 0.90, "criterion not met"),
        }
        self.assertEqual(set(rows), set(expected))
        for metric, (observed, criterion, status) in expected.items():
            self.assertAlmostEqual(float(rows[metric]["observed"]), observed, places=6)
            self.assertAlmostEqual(float(rows[metric]["criterion"]), criterion, places=6)
            self.assertEqual(rows[metric]["status"], status)

    def test_only_figure4_assets_changed(self) -> None:
        manifest = RUN / "07_FIGURE_ASSET_MANIFEST.csv"
        if not manifest.exists():
            self.skipTest("Final asset manifest not written yet")
        with manifest.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        changed = {Path(row["relative_path"]).name for row in rows if row["changed"].lower() == "true"}
        self.assertEqual(len(rows), 45)
        self.assertEqual(changed, {
            "Figure4_independent_ifn_replication.pdf",
            "Figure4_independent_ifn_replication.png",
            "Figure4_source_data.csv",
        })

    def test_root_text_and_supplement_are_locked(self) -> None:
        self.assertEqual(sha256(ROOT / "01_manuscript/Manuscript.md"), sha256(CURRENT / "sources/Manuscript_scientific_presentation_freeze.md"))
        self.assertEqual(sha256(ROOT / "01_manuscript/Supplementary_Information.md"), sha256(CURRENT / "sources/Supplementary_Information_scientific_presentation_freeze.md"))

    def test_submission_package_is_unchanged(self) -> None:
        self.assertEqual(sha256(PACKAGE), "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1")

    def test_final_status_and_manifest_when_present(self) -> None:
        status_path = RUN / "08_FIGURE4_TRANSFER_BOUNDARY_REFREEZE_STATUS.json"
        manifest_path = RUN / "09_FINAL_FILE_MANIFEST.csv"
        if not status_path.exists() or not manifest_path.exists():
            self.skipTest("Final Figure 4 status not written yet")
        status = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "SCIENTIFIC_FIGURE4_TRANSFER_BOUNDARY_PROMOTION_REFREEZE")
        self.assertEqual(status["failed_checks"], [])
        self.assertTrue(all(status["checks"].values()))
        with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(status["final_manifest"]["rows"], len(rows))
        for row in rows:
            target = ROOT / row["relative_path"]
            self.assertTrue(target.is_file(), row["relative_path"])
            self.assertEqual(target.stat().st_size, int(row["bytes"]), row["relative_path"])
            self.assertEqual(sha256(target), row["sha256"], row["relative_path"])


if __name__ == "__main__":
    unittest.main()
