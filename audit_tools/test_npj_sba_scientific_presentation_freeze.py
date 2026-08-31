from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

from docx import Document
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_scientific_presentation_freeze/"
    "20260831_reader_path_and_legend_economy"
)
PRIOR = (
    ROOT
    / "phase17_v7/npj_sba_scientific_coherence_refreeze/"
    "20260831_claim_order_reader_boundaries"
)
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def pdf_text(path: Path) -> str:
    return "\n".join((page.extract_text() or "") for page in PdfReader(path).pages)


class ScientificPresentationFreezeTests(unittest.TestCase):
    def test_exact_submission_package_is_unchanged(self) -> None:
        self.assertEqual(sha256(PACKAGE), PACKAGE_SHA)

    def test_all_figures_and_source_data_pass(self) -> None:
        status = json.loads((RUN / "00_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["figure_count"], 15)
        self.assertEqual(status["source_data_count"], 15)
        self.assertTrue(all(status["source_data_byte_identical_to_prior_candidate"].values()))
        self.assertTrue(all(row["byte_identical"] for row in status["source_data"].values()))
        self.assertTrue(all(all(row["postflight"]["checks"].values()) for row in status["figures"].values()))

    def test_only_figure1_and_figure5_raster_exports_changed(self) -> None:
        new_figures = RUN / "figures/figures"
        prior_figures = PRIOR / "figures/figures"
        changed = {
            path.name
            for path in new_figures.glob("*.png")
            if sha256(path) != sha256(prior_figures / path.name)
        }
        self.assertEqual(
            changed,
            {"Figure1_disease_blind_identity_scope.png", "Figure5_regulatory_evidence.png"},
        )

    def test_main_panel_decisions_are_two_modify_nineteen_keep(self) -> None:
        with (RUN / "01_MAIN_PANEL_FINAL_DECISION_MATRIX.csv").open(encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 21)
        self.assertEqual(sum(row["decision"] == "MODIFY" for row in rows), 2)
        self.assertEqual(sum(row["decision"] == "KEEP" for row in rows), 19)
        modified = {(row["figure"], row["panel"]) for row in rows if row["decision"] == "MODIFY"}
        self.assertEqual(modified, {("Figure 1", "a"), ("Figure 5", "a")})

    def test_replotted_panel_semantics_are_reader_facing_and_exact(self) -> None:
        figure1 = "".join(
            pdf_text(RUN / "figures/figures/Figure1_disease_blind_identity_scope.pdf").split()
        )
        figure5 = "".join(pdf_text(RUN / "figures/figures/Figure5_regulatory_evidence.pdf").split())
        self.assertIn("B_ASCsample-cohortfractions", figure1)
        self.assertIn("B_CONVsample-cohortpseudobulk", figure1)
        self.assertIn("identityadjudication", figure1)
        self.assertNotIn("donorpseudobulk", figure1)
        self.assertIn("Interpretiverole", figure5)
        self.assertIn("confirmatoryobservational", figure5)
        self.assertIn("response-setconcordance", figure5)
        self.assertNotIn("global24-testfamily", figure5)

    def test_canonical_ledger_is_exactly_reversible(self) -> None:
        with (RUN / "sources/SCIENTIFIC_PRESENTATION_EDIT_LEDGER.csv").open(
            encoding="utf-8-sig"
        ) as handle:
            ledger = list(csv.DictReader(handle))
        cases = (
            (
                "Manuscript",
                PRIOR / "sources/Manuscript_scientific_coherence_refreeze_candidate.md",
                RUN / "sources/Manuscript_scientific_presentation_freeze_candidate.md",
            ),
            (
                "Supplementary Information",
                PRIOR / "sources/Supplementary_Information_scientific_coherence_refreeze_candidate.md",
                RUN / "sources/Supplementary_Information_scientific_presentation_freeze_candidate.md",
            ),
        )
        for scope, baseline, candidate in cases:
            rows = [row for row in ledger if row["scope"] == scope]
            forward = baseline.read_text(encoding="utf-8")
            for row in rows:
                self.assertEqual(forward.count(row["old_text"]), 1)
                forward = forward.replace(row["old_text"], row["new_text"], 1)
            self.assertEqual(forward, candidate.read_text(encoding="utf-8"))
            reverse = candidate.read_text(encoding="utf-8")
            for row in reversed(rows):
                self.assertEqual(reverse.count(row["new_text"]), 1)
                reverse = reverse.replace(row["new_text"], row["old_text"], 1)
            self.assertEqual(reverse, baseline.read_text(encoding="utf-8"))

    def test_cross_document_reader_boundaries_are_synchronized(self) -> None:
        manuscript = (RUN / "sources/Manuscript_scientific_presentation_freeze_candidate.md").read_text(
            encoding="utf-8"
        )
        supplement = (
            RUN / "sources/Supplementary_Information_scientific_presentation_freeze_candidate.md"
        ).read_text(encoding="utf-8")
        title = (
            "Disease-blind reconstruction distinguishes reproducible interferon remodeling from less stable "
            "B-cell state assignments in systemic lupus erythematosus"
        )
        self.assertIn(title, manuscript)
        self.assertIn(title, supplement)
        self.assertIn("after corrected calibration failed", supplement)
        self.assertNotIn("calibration HOLD", supplement)
        self.assertIn("supports an IFN-centred regulatory context", manuscript)

    def test_documents_and_dual_render_qa_pass(self) -> None:
        build = json.loads((RUN / "02_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
        render = json.loads((RUN / "05_DUAL_RENDER_FINAL_QA_STATUS.json").read_text(encoding="utf-8"))
        self.assertTrue(all(all(group.values()) for group in build["checks"].values()))
        self.assertTrue(all(render["checks"].values()))
        self.assertEqual(
            render["documents"]["Manuscript_scientific_presentation_freeze_candidate.pdf"]["pages"],
            31,
        )
        self.assertEqual(
            render["documents"]["Supplementary_Information_scientific_presentation_freeze_candidate.pdf"]["pages"],
            16,
        )
        supplement = Document(
            RUN / "documents/Supplementary_Information_scientific_presentation_freeze_candidate.docx"
        )
        self.assertEqual(len(supplement.inline_shapes), 10)


if __name__ == "__main__":
    unittest.main()
