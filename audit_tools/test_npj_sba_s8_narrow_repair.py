import hashlib
import json
from pathlib import Path
import unittest

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
REPAIR = ROOT / "phase17_v7/npj_sba_s8_narrow_repair/20260830_source_replot_rebuild"
SOURCE_SHA = "26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class S8NarrowRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repair = json.loads((REPAIR / "01_S8_SOURCE_REPLOT_STATUS.json").read_text(encoding="utf-8"))
        cls.pagination = json.loads((RUN / "07_SUPPLEMENT_PAGINATION_AUDIT.json").read_text(encoding="utf-8"))

    def test_source_data_remains_frozen(self):
        source = RUN / "figures/source_data/Supplementary_Figure_S8_source_data.csv"
        self.assertEqual(sha256(source), SOURCE_SHA)
        self.assertTrue(self.repair["source_data"]["byte_identical_to_frozen_baseline"])
        self.assertFalse(self.repair["scientific_reanalysis"])
        self.assertFalse(self.repair["plotted_numeric_values_changed"])

    def test_repaired_figure_dimensions_and_scope(self):
        self.assertEqual(self.repair["status"], "PASS_S8_SOURCE_REPLOT_LAYOUT_ONLY")
        self.assertEqual(self.repair["figure"]["width_mm"], 170.0)
        self.assertEqual(self.repair["figure"]["height_mm"], 155.0)
        expected = [
            "figures/Supplementary_Figure_S8_overlap_depletion.pdf",
            "figures/Supplementary_Figure_S8_overlap_depletion.png",
        ]
        self.assertEqual(
            self.repair["authorized_changed_figure_artifacts"],
            expected,
        )
        self.assertTrue(
            set(self.repair["changed_figure_artifacts"]).issubset(expected)
        )
        self.assertEqual(
            sorted(self.repair["figure"]["artifact_postflight"]["checks"].values()),
            [
                True,
                True,
                True,
                True,
                True,
            ],
        )

    def test_both_renderers_keep_all_supplementary_figures_together(self):
        self.assertEqual(self.pagination["status"], "PASS_SUPPLEMENT_PAGINATION_COHERENCE")
        self.assertTrue(all(self.pagination["checks"].values()))
        self.assertTrue(self.pagination["wps"]["figures"]["S8"]["same_page"])
        self.assertTrue(self.pagination["libreoffice"]["figures"]["S8"]["same_page"])

    def test_both_renderers_embed_the_expected_s1_to_s10_figures(self):
        for renderer in ("wps", "libreoffice"):
            self.assertTrue(self.pagination[renderer]["all_expected_figure_fingerprints_match"])
            for number in range(1, 11):
                figure_id = f"S{number}"
                identity = self.pagination[renderer]["figures"][figure_id]["image_identity"]
                self.assertEqual(identity["best_source_match"], figure_id)
                self.assertTrue(identity["expected_figure_match"])
                self.assertLessEqual(identity["normalized_mae_to_expected"], 0.01)
                self.assertGreaterEqual(identity["identity_margin"], 0.05)

    def test_supplement_is_single_17_page_pdf(self):
        path = RUN / "documents/Supplementary_Information.pdf"
        self.assertEqual(len(PdfReader(path).pages), 17)


if __name__ == "__main__":
    unittest.main()
