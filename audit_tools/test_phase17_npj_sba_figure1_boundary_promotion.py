#!/usr/bin/env python3
"""Regression tests for the source-driven Figure 1 boundary promotion."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_figure1_boundary_promotion/20260902_source_rerender_gate"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Figure1BoundaryPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.integration = json.loads((RUN / "00_FIGURE1_BOUNDARY_PROMOTION_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
        cls.final = json.loads((RUN / "08_FIGURE1_BOUNDARY_PROMOTION_REFREEZE_STATUS.json").read_text(encoding="utf-8"))

    def test_integration_and_refreeze_passed(self) -> None:
        self.assertEqual(self.integration["failed_checks"], [])
        self.assertEqual(self.final["failed_checks"], [])
        self.assertEqual(self.final["status"], "SCIENTIFIC_FIGURE1_BOUNDARY_PROMOTION_REFREEZE")
        self.assertTrue(all(self.final["checks"].values()))

    def test_frozen_source_hashes(self) -> None:
        self.assertEqual(
            sha256(RUN / "source_inputs/Figure1_source_data_frozen_input.csv"),
            "F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805",
        )
        self.assertEqual(
            sha256(RUN / "source_inputs/Supplementary_Figure_S4_source_data_frozen_input.csv"),
            "46EE840F86CA33AA4F5FCE0A37EEFCB4DB23831533BBFA20400BAE50744F5D42",
        )

    def test_jaccard_derivation_is_exact(self) -> None:
        expected = {
            ("frozen", "B_CONV"): (0.9998323301084824, 0.999924551078872),
            ("frozen", "B_ASC"): (0.9810964083175804, 0.9913709736725989),
            ("end_to_end", "B_CONV"): (0.9987595755736964, 0.9993629961060673),
            ("end_to_end", "B_ASC"): (0.8717504332755632, 0.9303233364573571),
        }
        with (RUN / "01_FIGURE1_JACCARD_DERIVATION.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 4)
        for row in rows:
            observed = (float(row["minimum_jaccard"]), float(row["median_jaccard"]))
            target = expected[(row["reconstruction_depth"], row["state"])]
            self.assertAlmostEqual(observed[0], target[0], places=12)
            self.assertAlmostEqual(observed[1], target[1], places=12)
            self.assertEqual(float(row["state_median_criterion"]), 0.95)

    def test_only_figure1_assets_changed(self) -> None:
        with (RUN / "06_FIGURE_ASSET_MANIFEST.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        changed = {Path(row["relative_path"]).name for row in rows if row["changed"].lower() == "true"}
        self.assertEqual(len(rows), 45)
        self.assertEqual(changed, {
            "Figure1_disease_blind_identity_scope.pdf",
            "Figure1_disease_blind_identity_scope.png",
            "Figure1_source_data.csv",
        })

    def test_root_text_and_supplement_are_locked(self) -> None:
        self.assertEqual(
            sha256(ROOT / "01_manuscript/Manuscript.md"),
            sha256(RUN / "sources/Manuscript_figure1_boundary_promotion.md"),
        )
        self.assertEqual(
            sha256(ROOT / "01_manuscript/Supplementary_Information.md"),
            sha256(RUN / "sources/Supplementary_Information_unchanged.md"),
        )

    def test_submission_package_is_unchanged(self) -> None:
        self.assertEqual(
            sha256(PACKAGE),
            "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1",
        )

    def test_final_manifest_is_self_consistent(self) -> None:
        with (RUN / "09_FINAL_FILE_MANIFEST.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 82)
        for row in rows:
            path = ROOT / row["relative_path"]
            self.assertTrue(path.is_file(), row["relative_path"])
            self.assertEqual(path.stat().st_size, int(row["bytes"]), row["relative_path"])
            self.assertEqual(sha256(path), row["sha256"], row["relative_path"])


if __name__ == "__main__":
    unittest.main()
