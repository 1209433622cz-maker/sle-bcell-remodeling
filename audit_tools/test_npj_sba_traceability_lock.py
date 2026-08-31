from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_traceability_lock/"
    "20260831_final_scientific_object_lock"
)
PRIOR = (
    ROOT
    / "phase17_v7/npj_sba_scientific_presentation_freeze/"
    "20260831_reader_path_and_legend_economy"
)
SOURCE_DATA = PRIOR / "figures/source_data"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def one(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    matched = [row for row in rows if all(row.get(key) == value for key, value in criteria.items())]
    if len(matched) != 1:
        raise AssertionError(f"Expected one row for {criteria}; found {len(matched)}")
    return matched[0]


class TraceabilityLockTests(unittest.TestCase):
    def test_exact_submission_package_is_unchanged(self) -> None:
        self.assertEqual(sha256(PACKAGE), PACKAGE_SHA)

    def test_final_matrix_has_24_pass_objects(self) -> None:
        rows = read_csv(RUN / "FINAL_CORE_CLAIM_NUMERICAL_TRACEABILITY_MATRIX.csv")
        self.assertEqual([row["claim_id"] for row in rows], [f"C{i:02d}" for i in range(1, 25)])
        self.assertTrue(all(row["status"].startswith("PASS") for row in rows))
        self.assertEqual(one(rows, claim_id="C23")["status"], "PASS_FIXED_EXACT_UNIT")
        self.assertEqual(one(rows, claim_id="C24")["status"], "PASS_FIXED_PROVENANCE_SCOPE")

    def test_source_patch_is_exactly_reversible(self) -> None:
        prior = (
            PRIOR / "sources/Supplementary_Information_scientific_presentation_freeze_candidate.md"
        ).read_text(encoding="utf-8")
        final = (RUN / "sources/Supplementary_Information_final_scientific_lock.md").read_text(
            encoding="utf-8"
        )
        rows = read_csv(RUN / "sources/TRACEABILITY_SOURCE_EDIT_LEDGER.csv")
        forward = prior
        for row in rows:
            self.assertEqual(forward.count(row["old_text"]), 1)
            forward = forward.replace(row["old_text"], row["new_text"], 1)
        self.assertEqual(forward, final)
        reverse = final
        for row in reversed(rows):
            self.assertEqual(reverse.count(row["new_text"]), 1)
            reverse = reverse.replace(row["new_text"], row["old_text"], 1)
        self.assertEqual(reverse, prior)

    def test_table_s6_s7_objects_are_exact(self) -> None:
        text = (RUN / "sources/Supplementary_Information_final_scientific_lock.md").read_text(
            encoding="utf-8"
        )
        unit = "Sample-cohort pseudobulk (GSE174188); donor pseudobulk (GSE135779)"
        self.assertEqual(text.count(unit), 2)
        self.assertNotIn("Donor/sample pseudobulk", text)
        self.assertIn(
            "version-specific archive of the released analysis code, Source Data and statistical outputs",
            text,
        )
        self.assertNotIn("matches the frozen manuscript, figures and statistical outputs", text)

    def test_all_source_data_and_figures_are_hash_locked(self) -> None:
        source_rows = read_csv(RUN / "SOURCE_DATA_FINAL_LOCK_MANIFEST.csv")
        figure_rows = read_csv(RUN / "FIGURE_FINAL_LOCK_MANIFEST.csv")
        self.assertEqual(len(source_rows), 15)
        self.assertEqual(len(figure_rows), 30)
        for row in source_rows + figure_rows:
            path = ROOT / row["repository_path"]
            self.assertTrue(path.is_file())
            self.assertEqual(str(path.stat().st_size), row["bytes"])
            self.assertEqual(sha256(path), row["sha256"])

    def test_core_numerical_objects_match_source_data(self) -> None:
        figure1 = read_csv(SOURCE_DATA / "Figure1_source_data.csv")
        ari = one(figure1, panel="b", series="minimum mapped ARI", category="2-compartment")
        jaccard = one(figure1, panel="d", series="median Jaccard", category="B_ASC")
        self.assertAlmostEqual(float(ari["estimate"]), 0.9902066569784328)
        self.assertAlmostEqual(float(ari["secondary_value"]), 0.9998337765957448)
        self.assertAlmostEqual(float(jaccard["estimate"]), 0.9913709736725989)

        figure2 = read_csv(SOURCE_DATA / "Figure2_source_data.csv")
        composition = one(
            [row for row in figure2 if row["odds_ratio"]],
            analysis_id="C3A_PRIMARY_C4_MANAGED_VS_NORMAL",
            variant="frozen_base50",
        )
        self.assertAlmostEqual(float(composition["odds_ratio"]), 0.9466531606629468)
        self.assertAlmostEqual(float(composition["p_value"]), 0.7872791209333905)
        self.assertEqual((composition["reference_n"], composition["exposed_n"]), ("43.0", "47.0"))

        figure3 = read_csv(SOURCE_DATA / "Figure3_source_data.csv")
        ifn_rows = [
            row
            for row in figure3
            if row["analysis_name"] == "primary_base"
            and row["program_id"] == "IFN_ISG"
            and row["effect"]
        ]
        self.assertTrue(ifn_rows)
        self.assertTrue(all(abs(float(row["effect"]) - 0.836556476435973) < 1e-12 for row in ifn_rows))
        self.assertTrue(all(abs(float(row["q_value_primary4"]) - 2.9770041796839e-6) < 1e-15 for row in ifn_rows))

        figure4 = read_csv(SOURCE_DATA / "Figure4_source_data.csv")
        childhood = one(
            [row for row in figure4 if row["effect"]],
            analysis_name="childhood_min50",
            program_id="IFN_ISG",
        )
        self.assertAlmostEqual(float(childhood["effect"]), 1.04175695248946)
        self.assertAlmostEqual(float(childhood["q_value_primary4"]), 2.97551134813137e-6)

    def test_regulatory_and_boundary_objects_match_source_data(self) -> None:
        figure5 = read_csv(SOURCE_DATA / "Figure5_source_data.csv")
        stat_rows = [
            row
            for row in figure5
            if row["series"] == "regulator_activity"
            and row["category"].split("|")[-1] in {"STAT1", "STAT2"}
        ]
        self.assertEqual(len(stat_rows), 6)
        self.assertTrue(all(float(row["estimate"]) > 0 and float(row["q_value"]) < 0.05 for row in stat_rows))
        m5911 = [row for row in figure5 if row["series"] == "MSigDB_M5911_NES"]
        self.assertEqual(len(m5911), 3)
        self.assertTrue(all(float(row["estimate"]) > 3.0 for row in m5911))
        donor_genes = [row for row in figure5 if row["series"] == "GSE23307_paired_gene_log2p1_effect"]
        self.assertEqual(len(donor_genes), 24)
        self.assertTrue(all(float(row["estimate"]) > 0 for row in donor_genes))

        s9 = read_csv(SOURCE_DATA / "Supplementary_Figure_S9_source_data.csv")
        minimum_ari = one(s9, record_type="threshold_audit", metric="Minimum mapped ARI")
        minimum_state = one(s9, record_type="threshold_audit", metric="Minimum state\nmedian Jaccard")
        self.assertAlmostEqual(float(minimum_ari["observed"]), 0.929696806592458)
        self.assertAlmostEqual(float(minimum_state["observed"]), 0.9303233364573572)
        self.assertEqual(minimum_state["pass"], "False")

        s10 = read_csv(SOURCE_DATA / "Supplementary_Figure_S10_source_data.csv")
        elastic = one(s10, mapper="elastic_net", threshold="0.95")
        self.assertAlmostEqual(float(elastic["coverage"]), 0.941958041958042)
        self.assertAlmostEqual(float(elastic["B_ASC_precision"]), 0.8852097130242825)
        self.assertEqual(elastic["eligible"], "False")

    def test_every_panel_is_retained_without_new_analysis(self) -> None:
        main_rows = read_csv(RUN / "MAIN_PANEL_FINAL_TRACEABILITY_DECISION_MATRIX.csv")
        supplementary_rows = read_csv(
            RUN / "SUPPLEMENTARY_FIGURE_FINAL_TRACEABILITY_DECISION_MATRIX.csv"
        )
        self.assertEqual(len(main_rows), 21)
        self.assertEqual(len(supplementary_rows), 10)
        self.assertTrue(all(row["decision"] == "KEEP" for row in main_rows + supplementary_rows))
        status = json.loads(
            (RUN / "00_TRACEABILITY_LOCK_INTEGRATION_STATUS.json").read_text(encoding="utf-8")
        )
        self.assertEqual(status["scientific_object_decision"]["new_analysis"], 0)
        self.assertFalse(status["figures_changed"])

    def test_documents_and_dual_render_qa_pass(self) -> None:
        build = json.loads((RUN / "01_DOCUMENT_BUILD_STATUS.json").read_text(encoding="utf-8"))
        final = json.loads((RUN / "04_FINAL_TRACEABILITY_LOCK_STATUS.json").read_text(encoding="utf-8"))
        self.assertTrue(all(all(group.values()) for group in build["checks"].values()))
        self.assertTrue(all(final["checks"].values()))
        self.assertEqual(final["status"], "FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCKED")
        supplement = Document(RUN / "documents/Supplementary_Information_final_scientific_lock.docx")
        self.assertEqual(len(supplement.inline_shapes), 10)


if __name__ == "__main__":
    unittest.main()
