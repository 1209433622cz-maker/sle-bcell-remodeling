"""Regression tests for the npj Systems Biology and Applications target refreeze."""

import csv
import json
import os
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(
    os.environ.get(
        "NPJ_SBA_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_target_refreeze/20260830_target_specific_refreeze",
    )
).resolve()
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications"
TITLE = (
    "Disease-blind reconstruction distinguishes reproducible interferon remodeling from "
    "unstable B-cell state assignments in systemic lupus erythematosus"
)


class NpjSbaTargetRefreezeTests(unittest.TestCase):
    def test_title_and_abstract_limits(self):
        status = json.loads((RUN / "00_TARGET_SOURCE_BUILD_STATUS.json").read_text(encoding="utf-8"))
        manuscript = (RUN / "sources/Manuscript.md").read_text(encoding="utf-8")
        self.assertEqual(manuscript.splitlines()[0], f"# {TITLE}")
        self.assertEqual(status["title_words"], 15)
        self.assertLessEqual(status["abstract_words"], 150)

    def test_scientific_boundaries_are_locked(self):
        status = json.loads((RUN / "00_TARGET_SOURCE_BUILD_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["R1_decision"], "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY")
        self.assertEqual(status["C9R_decision"], "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED")
        self.assertFalse(status["corrected_external_outcome_unlock_authorized"])
        self.assertFalse(status["scientific_reanalysis"])

    def test_target_structure_and_supplement_policy(self):
        manuscript = (RUN / "sources/Manuscript.md").read_text(encoding="utf-8")
        supplement = (RUN / "sources/Supplementary_Information.md").read_text(encoding="utf-8")
        self.assertNotIn("## Background", manuscript)
        self.assertNotIn("## Conclusions", manuscript)
        self.assertNotIn("Supplementary Methods", supplement)
        self.assertNotIn("Additional file", manuscript + supplement)

    def test_figure_sources_are_byte_identical(self):
        status = json.loads((RUN / "01_NPJ_FIGURE_RENDER_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["figure_count"], 15)
        self.assertTrue(status["source_tables_byte_identical"])
        self.assertTrue(all(row["byte_identical_to_corrected_candidate"] for row in status["source_data"].values()))
        self.assertTrue(status["artifact_postflight_all_pass"])
        self.assertTrue(
            all(all(row["checks"].values()) for row in status["artifact_postflight"].values())
        )

    def test_statistics_map_contains_frozen_holds(self):
        with (RUN / "npj_statistics_reporting_map.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 12)
        decisions = {row["claim_id"]: row["decision"] for row in rows}
        self.assertEqual(decisions["R1"], "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY")
        self.assertEqual(decisions["C9R"], "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED")

    def test_statistics_map_claims_match_machine_decisions(self):
        with (RUN / "npj_statistics_reporting_map.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = {row["claim_id"]: row for row in csv.DictReader(handle)}
        expected = {
            "R1": "End-to-end broad-state reproducibility did not meet the frozen state-specific criterion because B_ASC median Jaccard was below 0.95",
            "C3_PRIMARY": "The primary B_ASC composition analysis did not support a difference in source-defined managed SLE",
            "C5_GENOMEWIDE": "Genome-wide cross-dataset effect concordance was weak (Spearman rho=0.026)",
            "C9R": "Corrected source-label-independent mapping did not satisfy the frozen calibration gate; no corrected disease outcome was estimated",
            "TF_DEPLETION": "Narrow 12-gene depletion retained support, whereas broader M5911 depletion did not support overlap-independent STAT1/STAT2 regulation",
        }
        self.assertEqual({key: rows[key]["claim"] for key in expected}, expected)

    def test_reader_facing_hardening_is_locked(self):
        manuscript = (RUN / "sources/Manuscript.md").read_text(encoding="utf-8")
        self.assertIn("Running title: Reproducible IFN remodeling in SLE B cells", manuscript)
        self.assertIn("source-label-defined IFN/ISG replication", manuscript)
        self.assertNotIn("neither interferon activity nor plasmablast biology is novel", manuscript)
        self.assertNotIn("## Conclusions", manuscript)

    def test_package_metadata_does_not_authorize_submission(self):
        metadata = json.loads((PACKAGE / "06_Integrity/PACKAGE_METADATA.json").read_text(encoding="utf-8"))
        self.assertFalse(metadata["exact_package_author_approved"])
        self.assertFalse(metadata["submission_authorized"])
        self.assertFalse(metadata["apc_commitment_authorized"])


if __name__ == "__main__":
    unittest.main()
