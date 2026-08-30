import csv
import hashlib
import json
import unittest
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates"
)
RECOMMENDED = RUN / "recommended_scientific_candidate"
BASELINE = (
    ROOT
    / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
)
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def pdf_text(path: Path) -> str:
    return " ".join((page.extract_text() or "") for page in PdfReader(path).pages)


class MainFigureRefinementTests(unittest.TestCase):
    def test_exact_package_remains_the_confirmed_baseline(self) -> None:
        self.assertEqual(
            sha256(PACKAGE),
            "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1",
        )

    def test_all_candidates_reuse_frozen_source_data(self) -> None:
        status = json.loads((RUN / "00_CANDIDATE_BUILD_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "PASS_SOURCE_DRIVEN_CANDIDATES_READY_FOR_VISUAL_ADJUDICATION")
        self.assertFalse(status["scientific_estimates_changed"])
        for candidate in status["candidates"]:
            source_name = f"{candidate['panel'][:-1]}_source_data.csv"
            baseline = BASELINE / "figures/source_data" / source_name
            self.assertEqual(candidate["source_sha256"], sha256(baseline))
            self.assertTrue(candidate["all_assertions_pass"])
            self.assertTrue(candidate["single_page"])
            self.assertAlmostEqual(candidate["width_mm"], 170.0, places=1)

    def test_recommended_figures_expose_the_selected_semantics(self) -> None:
        status = json.loads(
            (RECOMMENDED / "00_RECOMMENDED_CANDIDATE_STATUS.json").read_text(encoding="utf-8")
        )
        self.assertEqual(status["selection"]["Figure1"]["candidate"], "Figure1A_workflow_scope")
        self.assertEqual(status["selection"]["Figure5"]["candidate"], "Figure5B_quantitative_matrix")
        figure1 = pdf_text(RECOMMENDED / "figures/Figure1_disease_blind_identity_scope.pdf")
        figure5 = pdf_text(RECOMMENDED / "figures/Figure5_regulatory_evidence.pdf")
        for token in ("Workflow and identity scope", "broad-compartment analyses", "fine-state assignments"):
            self.assertIn(token, figure1)
        for token in ("Quantitative evidence summary", "6/6 positive", "12/12 in each donor", "observational convergence"):
            self.assertIn(token, figure5)

    def test_candidate_manuscript_changes_only_two_legend_clauses(self) -> None:
        baseline = (BASELINE / "sources/Manuscript.md").read_text(encoding="utf-8")
        candidate = (
            RECOMMENDED / "sources/Manuscript_figure_refinement_candidate.md"
        ).read_text(encoding="utf-8")
        with (RECOMMENDED / "01_TEXT_EDIT_LEDGER.csv").open(
            "r", encoding="utf-8-sig", newline=""
        ) as handle:
            ledger = list(csv.DictReader(handle))
        self.assertEqual(len(ledger), 2)
        restored = candidate
        for row in ledger:
            self.assertEqual(row["scientific_estimate_changed"], "False")
            self.assertEqual(restored.count(row["new_text"]), 1)
            restored = restored.replace(row["new_text"], row["old_text"], 1)
        self.assertEqual(restored, baseline)


if __name__ == "__main__":
    unittest.main()
