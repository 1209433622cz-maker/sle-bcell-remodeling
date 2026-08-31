from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

from docx import Document
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_scientific_coherence_refreeze/20260831_claim_order_reader_boundaries"
PRIOR = (
    ROOT
    / "phase17_v7/npj_sba_selected_supplementary_refinement/"
    "20260831_s4_s10_semantic_harmonization/sources"
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


class ScientificCoherenceRefreezeTests(unittest.TestCase):
    def test_exact_submission_package_is_unchanged(self) -> None:
        self.assertEqual(sha256(PACKAGE), PACKAGE_SHA)

    def test_all_figures_and_source_data_pass(self) -> None:
        status = json.loads((RUN / "00_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["figure_count"], 15)
        self.assertEqual(status["source_data_count"], 15)
        self.assertTrue(all(row["byte_identical"] for row in status["source_data"].values()))
        self.assertTrue(
            all(all(row["postflight"]["checks"].values()) for row in status["figures"].values())
        )

    def test_s9_and_s10_use_reader_facing_criteria(self) -> None:
        s9 = pdf_text(RUN / "figures/figures/Supplementary_Figure_S9_identity_boundary_and_propagation.pdf")
        s10 = pdf_text(RUN / "figures/figures/Supplementary_Figure_S10_reference_calibration_boundary.pdf")
        self.assertIn("Four global criteria met; state overlap not met", s9)
        self.assertIn("Composition inference unchanged", s9)
        self.assertNotIn("formal HOLD", s9)
        self.assertIn("Elastic-net B_ASC precision below criterion", s10)
        self.assertIn("Coverage criterion met by both mappers", s10)

    def test_canonical_ledger_is_exactly_reversible(self) -> None:
        with (RUN / "sources/SCIENTIFIC_COHERENCE_EDIT_LEDGER.csv").open(
            encoding="utf-8-sig"
        ) as handle:
            ledger = list(csv.DictReader(handle))
        cases = (
            (
                "Manuscript",
                PRIOR / "Manuscript_scientific_harmonization_candidate.md",
                RUN / "sources/Manuscript_scientific_coherence_refreeze_candidate.md",
            ),
            (
                "Supplementary Information",
                PRIOR / "Supplementary_Information_scientific_harmonization_candidate.md",
                RUN / "sources/Supplementary_Information_scientific_coherence_refreeze_candidate.md",
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

    def test_reader_facing_text_boundaries_are_consistent(self) -> None:
        manuscript = (RUN / "sources/Manuscript_scientific_coherence_refreeze_candidate.md").read_text(
            encoding="utf-8"
        )
        supplement = (
            RUN / "sources/Supplementary_Information_scientific_coherence_refreeze_candidate.md"
        ).read_text(encoding="utf-8")
        self.assertIn("less stable B-cell state assignments", manuscript)
        self.assertIn("absence of statistical support in the primary composition contrast", manuscript)
        self.assertNotIn("primary composition null", manuscript)
        self.assertNotIn("formal HOLD", supplement)
        self.assertNotIn("C9 PASS", supplement)
        self.assertIn("prespecified criterion not met", supplement)

    def test_documents_and_dual_render_qa_pass(self) -> None:
        build = json.loads((RUN / "02_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
        render = json.loads((RUN / "05_DUAL_RENDER_FINAL_QA_STATUS.json").read_text(encoding="utf-8"))
        self.assertTrue(all(all(group.values()) for group in build["checks"].values()))
        self.assertTrue(all(render["checks"].values()))
        self.assertEqual(
            render["documents"]["Manuscript_scientific_coherence_refreeze_candidate.pdf"]["pages"],
            32,
        )
        self.assertEqual(
            render["documents"]["Supplementary_Information_scientific_coherence_refreeze_candidate.pdf"]["pages"],
            16,
        )
        supplement = Document(
            RUN / "documents/Supplementary_Information_scientific_coherence_refreeze_candidate.docx"
        )
        self.assertEqual(len(supplement.inline_shapes), 10)


if __name__ == "__main__":
    unittest.main()
