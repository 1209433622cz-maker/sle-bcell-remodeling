from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_selected_supplementary_refinement/"
    "20260831_s4_s10_semantic_harmonization"
)
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
EXPECTED_PACKAGE_SHA = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest().upper()


def pdf_text(path: Path) -> str:
    return "\n".join((page.extract_text() or "") for page in PdfReader(path).pages)


class SelectedSupplementaryRefinementTests(unittest.TestCase):
    def test_exact_submission_package_is_unchanged(self) -> None:
        self.assertEqual(sha256(PACKAGE), EXPECTED_PACKAGE_SHA)

    def test_all_source_data_remain_byte_identical(self) -> None:
        status = json.loads((RUN / "00_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(len(status["source_data"]), 15)
        self.assertTrue(all(item["byte_identical"] for item in status["source_data"].values()))

    def test_selected_figure_semantics_and_geometry_pass(self) -> None:
        status = json.loads((RUN / "00_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(len(status["figures"]), 15)
        self.assertTrue(all(item["width_mm"] == 170.0 for item in status["figures"].values()))
        self.assertTrue(
            all(all(item["postflight"]["checks"].values()) for item in status["figures"].values())
        )
        figure1 = pdf_text(RUN / "figures/figures/Figure1_disease_blind_identity_scope.pdf")
        figure5 = pdf_text(RUN / "figures/figures/Figure5_regulatory_evidence.pdf")
        s4 = pdf_text(RUN / "figures/figures/Supplementary_Figure_S4_composition_diagnostics.pdf")
        s10 = pdf_text(RUN / "figures/figures/Supplementary_Figure_S10_reference_calibration_boundary.pdf")
        self.assertIn("Retained analysis", figure1)
        self.assertIn("hard fine-state assignments unsupported", figure1)
        self.assertIn("ULM STAT1/STAT2", figure5)
        self.assertGreaterEqual(s4.count("log scale"), 2)
        self.assertIn("state-precision criterion", s10)
        self.assertIn("coverage criterion", s10)
        self.assertIn("Donor-grouped folds (diagnostic only)", s10)

    def test_s4_and_s10_replots_preserve_numeric_source_rows(self) -> None:
        s4 = pd.read_csv(RUN / "figures/source_data/Supplementary_Figure_S4_source_data.csv")
        s10 = pd.read_csv(RUN / "figures/source_data/Supplementary_Figure_S10_source_data.csv")
        self.assertGreater(len(s4), 0)
        self.assertGreater(len(s10), 0)
        self.assertTrue(s4.select_dtypes(include="number").notna().any().any())
        self.assertTrue(s10.select_dtypes(include="number").notna().any().any())

    def test_manuscript_edit_ledger_is_narrow_and_non_numeric(self) -> None:
        ledger = pd.read_csv(RUN / "sources/Manuscript_scientific_harmonization_edit_ledger.csv")
        self.assertEqual(len(ledger), 9)
        self.assertFalse(ledger["scientific_estimate_changed"].astype(bool).any())
        manuscript = (RUN / "sources/Manuscript_scientific_harmonization_candidate.md").read_text(
            encoding="utf-8"
        )
        for row in ledger.itertuples(index=False):
            self.assertIn(row.new_text, manuscript)

    def test_candidate_documents_pass_structural_and_render_qa(self) -> None:
        build = json.loads((RUN / "02_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
        render = json.loads((RUN / "03_RENDER_QA_STATUS.json").read_text(encoding="utf-8"))
        self.assertTrue(all(all(group.values()) for group in build["checks"].values()))
        self.assertTrue(all(all(group.values()) for group in render["checks"].values()))
        self.assertEqual(
            render["documents"]["Manuscript_scientific_harmonization_candidate.pdf"]["pages"], 32
        )
        self.assertEqual(
            render["documents"]["Supplementary_Information_scientific_harmonization_candidate.pdf"]["pages"],
            16,
        )
        supplement = Document(
            RUN / "documents/Supplementary_Information_scientific_harmonization_candidate.docx"
        )
        self.assertEqual(len(supplement.inline_shapes), 10)


if __name__ == "__main__":
    unittest.main()
