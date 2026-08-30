import csv
import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_full_main_figure_refinement/20260831_figure5e_and_figures2to4_adjudication"
)
RECOMMENDED = RUN / "recommended_full_main_figure_set"
BASELINE = ROOT / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
PRIOR_CANDIDATE = (
    ROOT
    / "phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates"
    / "recommended_scientific_candidate/sources/Manuscript_figure_refinement_candidate.md"
)
GENE_SOURCE = ROOT / "phase17_v7/gateC6B/20260815_regulatory_evidence/17_GSE23307_LOG2P1_PAIRED_GENE_EFFECTS.csv"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def pdf_text(path: Path) -> str:
    return " ".join((page.extract_text() or "") for page in PdfReader(path).pages)


class FullMainFigureRefinementTests(unittest.TestCase):
    def test_exact_package_remains_the_confirmed_baseline(self) -> None:
        self.assertEqual(
            sha256(PACKAGE),
            "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1",
        )

    def test_figures2to4_were_rebuilt_from_unchanged_source_data(self) -> None:
        status = json.loads((RECOMMENDED / "00_FULL_MAIN_FIGURE_CANDIDATE_STATUS.json").read_text(encoding="utf-8"))
        self.assertTrue(status["figures2to4_rebuilt_from_frozen_inputs"]["assertions_pass"])
        self.assertEqual(status["figures2to4_rebuilt_from_frozen_inputs"]["assertions"], 29)
        for figure in ("Figure2", "Figure3", "Figure4"):
            candidate = RECOMMENDED / "source_data" / f"{figure}_source_data.csv"
            baseline = BASELINE / "figures/source_data" / f"{figure}_source_data.csv"
            self.assertEqual(sha256(candidate), sha256(baseline))

    def test_figure5e_exposes_frozen_gene_level_effects_without_inference(self) -> None:
        status = json.loads((RUN / "00_FIGURE5E_CANDIDATE_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["frozen_gene_source_sha256"], sha256(GENE_SOURCE))
        self.assertEqual(status["original_rows_preserved"], 29)
        self.assertEqual(status["declared_gene_rows_appended"], 24)
        self.assertTrue(status["all_gene_effects_positive"])
        self.assertFalse(status["new_inference_added"])

        source = pd.read_csv(RECOMMENDED / "source_data/Figure5_source_data.csv")
        gene_rows = source.loc[source["series"] == "GSE23307_paired_gene_log2p1_effect"]
        self.assertEqual(len(gene_rows), 24)
        self.assertEqual(gene_rows["category"].str.split("|").str[0].nunique(), 2)
        self.assertTrue((gene_rows["estimate"] > 0).all())
        figure = pdf_text(RECOMMENDED / "figures/Figure5_regulatory_evidence.pdf")
        for token in ("IFN-beta paired gene effects", "n=2; descriptive", "IFN-beta minus control"):
            self.assertIn(token, figure)

    def test_panel_adjudication_and_manuscript_change_are_narrow(self) -> None:
        with (RECOMMENDED / "01_PANEL_DECISION_MATRIX.csv").open("r", encoding="utf-8-sig", newline="") as handle:
            decisions = {(row["figure"], row["panel"]): row["decision"] for row in csv.DictReader(handle)}
        self.assertEqual(decisions[("Figure1", "a")], "REPLACE_SELECTED")
        self.assertEqual(decisions[("Figure5", "a")], "REPLACE_SELECTED")
        self.assertEqual(decisions[("Figure5", "e")], "REPLACE_SELECTED")
        for key in (("Figure2", "a-d"), ("Figure3", "a-d"), ("Figure4", "a-d")):
            self.assertEqual(decisions[key], "RETAIN")

        prior = PRIOR_CANDIDATE.read_text(encoding="utf-8")
        candidate = (RECOMMENDED / "sources/Manuscript_full_main_figure_candidate.md").read_text(encoding="utf-8")
        old = (
            "e, Mean paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta "
            "exposure in primary B cells from two healthy donors; labels show positive genes. The "
            "GSE23307 panel is descriptive at n=2 and carries no inferential P value."
        )
        new = (
            "e, Gene-level paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo "
            "IFN-beta exposure in primary B cells from each of two healthy donors. Points for the same "
            "gene are connected only to aid donor comparison; all 24 donor-gene effects were positive. "
            "The GSE23307 panel is descriptive at n=2 and carries no inferential P value."
        )
        self.assertEqual(prior.count(old), 1)
        self.assertEqual(candidate.count(new), 1)
        self.assertEqual(candidate.replace(new, old, 1), prior)

    def test_candidate_document_render_passes(self) -> None:
        status = json.loads((RECOMMENDED / "04_CANDIDATE_MANUSCRIPT_RENDER_QA.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "PASS_CANDIDATE_MANUSCRIPT_RENDER_AND_VISUAL_QA")
        self.assertEqual(status["page_count"], 32)
        self.assertTrue(all(status["checks"].values()))
        self.assertFalse(status["scientific_estimates_changed"])
        self.assertFalse(status["exact_submission_package_modified"])


if __name__ == "__main__":
    unittest.main()
