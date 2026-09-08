#!/usr/bin/env python3
"""Regression tests for the Figure 5 regulatory-ceiling source integration."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration"
CURRENT = ROOT / "phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Figure5RegulatoryCeilingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.integration = json.loads(
            (RUN / "05_FIGURE5_REGULATORY_CEILING_INTEGRATION_STATUS.json").read_text(encoding="utf-8")
        )

    def test_integration_and_document_build_passed(self) -> None:
        build = json.loads((RUN / "06_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(self.integration["failed_checks"], [])
        self.assertEqual(build["failed_checks"], [])
        self.assertTrue(all(self.integration["checks"].values()))
        self.assertTrue(all(build["checks"].values()))

    def test_frozen_source_hashes_are_exact(self) -> None:
        expected = {
            "Figure5_source_data.csv": "A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B",
            "Supplementary_Figure_S9_source_data.csv": "D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3",
            "Supplementary_Figure_S10_source_data.csv": "26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2",
        }
        for name, value in expected.items():
            self.assertEqual(sha256(RUN / "source_inputs" / name), value, name)

    def test_depletion_values_and_single_exception_are_exact(self) -> None:
        with (RUN / "01_FIGURE5_DEPLETION_DERIVATION.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 12)
        arm = [row for row in rows if row["branch"] == "frozen_ifn12_depleted"]
        m5911 = [row for row in rows if row["branch"] == "m5911_depleted"]
        self.assertEqual(len(arm), 6)
        self.assertEqual(len(m5911), 6)
        self.assertTrue(all(float(row["ci_low"]) > 0 for row in arm))
        crossing = [row for row in m5911 if float(row["ci_low"]) <= 0]
        self.assertEqual([(row["contrast"], row["regulator"]) for row in crossing], [("gse174188_primary", "STAT2")])
        self.assertAlmostEqual(float(crossing[0]["estimate"]), 0.390657714569951, places=12)
        self.assertAlmostEqual(float(crossing[0]["ci_low"]), -0.745046177194798, places=12)
        self.assertAlmostEqual(float(crossing[0]["ci_high"]), 1.5263616063347, places=12)
        self.assertAlmostEqual(float(crossing[0]["q_value"]), 0.500111148687377, places=12)

    def test_figure5_source_ownership_is_complete(self) -> None:
        with (RUN / "figures/source_data/Figure5_source_data.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 65)
        self.assertEqual(sum(row["panel"] == "D" and row["series"] == "ULM_IFN_overlap_depletion" for row in rows), 12)
        self.assertEqual(sum(row["panel"] == "A" and row["series"] == "MSigDB_M5911_NES" for row in rows), 3)
        self.assertEqual(sum(row["panel"] == "D" and row["series"] == "MSigDB_M5911_NES" for row in rows), 0)

    def test_only_figure5_assets_changed_when_manifest_present(self) -> None:
        manifest = RUN / "07_FIGURE_ASSET_MANIFEST.csv"
        if not manifest.exists():
            self.skipTest("Final Figure 5 asset manifest not written yet")
        with manifest.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        changed = {Path(row["relative_path"]).name for row in rows if row["changed"].lower() == "true"}
        self.assertEqual(len(rows), 45)
        self.assertEqual(changed, {"Figure5_regulatory_evidence.pdf", "Figure5_regulatory_evidence.png", "Figure5_source_data.csv"})

    def test_root_text_supplement_and_package_are_locked(self) -> None:
        self.assertEqual(sha256(ROOT / "01_manuscript/Manuscript.md"), sha256(CURRENT / "sources/Manuscript_scientific_presentation_freeze.md"))
        self.assertEqual(sha256(ROOT / "01_manuscript/Supplementary_Information.md"), sha256(CURRENT / "sources/Supplementary_Information_scientific_presentation_freeze.md"))
        self.assertEqual(sha256(PACKAGE), "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1")

    def test_final_status_and_manifest_when_present(self) -> None:
        status_path = RUN / "08_FIGURE5_REGULATORY_CEILING_REFREEZE_STATUS.json"
        manifest_path = RUN / "09_FINAL_FILE_MANIFEST.csv"
        if not status_path.exists() or not manifest_path.exists():
            self.skipTest("Final Figure 5 status not written yet")
        status = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "SCIENTIFIC_FIGURE5_REGULATORY_CEILING_REFREEZE")
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
