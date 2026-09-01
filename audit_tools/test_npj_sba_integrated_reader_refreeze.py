"""Regression tests for the S3/S5 integrated reader-path scientific refreeze."""

from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_integrated_reader_refreeze/"
    "20260901_s3_s5_reader_path_refreeze"
)
MANUSCRIPT = RUN / "sources/Manuscript_integrated_reader_refreeze.md"
SUPPLEMENT = RUN / "sources/Supplementary_Information_integrated_reader_refreeze.md"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
SOURCE_HASHES = {
    "Figure1_source_data.csv": "F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805",
    "Supplementary_Figure_S3_source_data.csv": "133E973C2753F4946A24739C049308152299A915A3FC6754B30AD0521F979C96",
    "Figure3_source_data.csv": "DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8",
    "Supplementary_Figure_S5_source_data.csv": "F6682D636C1FF3A1784E0B9E8AEFF5C5D1BB075176312E87FCB938F65C4DA897",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class IntegratedReaderRefreezeTests(unittest.TestCase):
    def test_final_lock_status(self) -> None:
        status = json.loads(
            (RUN / "04_FINAL_INTEGRATED_READER_REFREEZE_STATUS.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            status["status"],
            "INTEGRATED_READER_PATH_AND_DISPLAY_PRUNE_SCIENTIFIC_REFREEZE_LOCKED",
        )
        self.assertTrue(all(status["checks"].values()))
        self.assertFalse(status["scientific_estimates_changed"])
        self.assertFalse(status["source_data_changed"])
        self.assertEqual(status["main_panels"], {"keep": 21, "modify": 0, "replace": 0})
        self.assertEqual(status["supplementary_panels"]["final_display"], 38)
        self.assertEqual(status["supplementary_panels"]["pruned_exact_duplicates"], 3)

    def test_exact_source_hashes_and_package_boundary(self) -> None:
        for name, expected in SOURCE_HASHES.items():
            self.assertEqual(sha256(RUN / "figures/source_data" / name), expected)
        self.assertEqual(sha256(PACKAGE), PACKAGE_SHA256)

    def test_textual_reader_path(self) -> None:
        manuscript = MANUSCRIPT.read_text(encoding="utf-8")
        supplement = SUPPLEMENT.read_text(encoding="utf-8")
        self.assertIn("reconstruction and replication tests", manuscript)
        self.assertIn(
            "bounded process-level interferon association within explicit identity and transfer limits",
            manuscript,
        )
        self.assertNotIn("not a universal B-cell taxonomy, generalized B_ASC expansion", manuscript)
        self.assertIn("Fine-state failure and transition structure", supplement)
        self.assertIn("broad-state pass criteria are shown in Fig. 1", supplement)
        self.assertIn("end-to-end reconstruction is shown in Supplementary Fig. S9", supplement)
        self.assertIn("owned by Fig. 3b and are not repeated here", supplement)
        self.assertNotIn("Disease-blind identity adjudication", supplement)
        self.assertNotIn("IFN/ISG effects and 95% confidence intervals across frozen branches", supplement)

    def test_panel_matrix_and_mapping(self) -> None:
        with (RUN / "FINAL_INTEGRATED_READER_PANEL_DECISION_MATRIX.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            matrix = list(csv.DictReader(handle))
        self.assertEqual(len(matrix), 62)
        self.assertEqual(
            sum(row["tier"] == "Main" and row["decision"] == "KEEP" for row in matrix),
            21,
        )
        pruned = [row["object"] for row in matrix if row["decision"].startswith("PRUNE_FROM_DISPLAY")]
        self.assertEqual(
            pruned,
            [
                "Supplementary Figure S3a",
                "Supplementary Figure S3d",
                "Supplementary Figure S5d",
            ],
        )
        with (RUN / "S3_S5_DISPLAY_PANEL_MAPPING.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            mapping = list(csv.DictReader(handle))
        self.assertEqual(mapping[1]["final_display_panel"], "S3a")
        self.assertEqual(mapping[2]["final_display_panel"], "S3b")
        self.assertEqual(mapping[7]["final_display_panel"], "")


if __name__ == "__main__":
    unittest.main()
