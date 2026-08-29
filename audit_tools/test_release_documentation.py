"""Regression tests for release-documentation truth and the JCR selection gate."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from phase17_postc9_21_verify_release_documentation import (
    C9R_HOLD,
    CURRENT_DOI,
    OLD_DOI,
    R1_HOLD,
    RELEASE_TAG,
    checksum,
    verify_documentation,
)


class ReleaseDocumentationTests(unittest.TestCase):
    def fixture(self, root):
        selection = root / "00_project_management/jcr_q1_journal_selection_2026-08-29"
        received = selection / "received"
        readiness_dir = root / "00_project_management/qiteng_r2_freeze_2026-08-29"
        received.mkdir(parents=True)
        readiness_dir.mkdir(parents=True)
        boundary = f"{CURRENT_DOI} {OLD_DOI} {RELEASE_TAG} Journal submission remains unauthorized."
        (root / "README.md").write_text(boundary, encoding="utf-8")
        (root / "REPRODUCIBILITY.md").write_text(boundary, encoding="utf-8")
        status = {
            "status": "CONDITIONAL_FIT_LEAD_SET_OFFICIAL_JCR_AND_APC_EVIDENCE_PENDING",
            "selected_target": None,
            "official_jcr_profile_export_obtained": False,
            "all_categories_rank_denominator_quartile_verified": False,
            "institutional_apc_coverage_verified": False,
            "target_specific_manuscript_adaptation_started": False,
            "submission_authorized": False,
            "apc_commitment_authorized": False,
            "new_scientific_analysis_performed": False,
            "R1_decision": R1_HOLD,
            "C9R_decision": C9R_HOLD,
            "corrected_external_outcome_unlock_authorized": False,
        }
        sources = {
            "jcr": {"release": 2026, "data_year": 2025, "rank_and_quartile_verified": False},
            "selected_target": None,
            "scientific_changes_performed": False,
            "journals": [{"jcr_q1_verified": False}, {"jcr_q1_verified": False}],
        }
        readiness = {
            "journal_selection": {
                "selected_target": None,
                "jcr_q1_eligibility_verified": False,
                "target_specific_adaptation_started": False,
            },
            "remaining_not_completed": {"journal_submission": False},
        }
        (selection / "journal_selection_status.json").write_text(json.dumps(status), encoding="utf-8")
        (selection / "official_source_snapshot.json").write_text(json.dumps(sources), encoding="utf-8")
        (readiness_dir / "publication_readiness.json").write_text(json.dumps(readiness), encoding="utf-8")
        rows = []
        for index in range(3):
            path = received / f"evidence_{index}.txt"
            path.write_bytes(f"evidence {index}".encode("ascii"))
            rows.append({"path": f"received/{path.name}", "bytes": path.stat().st_size, "sha256": checksum(path)})
        (selection / "received_evidence_manifest.json").write_text(json.dumps({"files": rows}), encoding="utf-8")
        return selection, status, sources

    def test_valid_unresolved_gate_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root)
            result = verify_documentation(root)
            self.assertIsNone(result["selected_target"])
            self.assertFalse(result["jcr_q1_verified"])

    def test_stale_release_statement_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root)
            with (root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write(" Administrative DOI integration is pending")
            with self.assertRaises(ValueError):
                verify_documentation(root)

    def test_premature_target_selection_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            selection, status, _ = self.fixture(root)
            changed = copy.deepcopy(status)
            changed["selected_target"] = "npj Systems Biology and Applications"
            (selection / "journal_selection_status.json").write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_documentation(root)

    def test_jcr_q1_overclaim_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            selection, _, sources = self.fixture(root)
            changed = copy.deepcopy(sources)
            changed["journals"][0]["jcr_q1_verified"] = True
            (selection / "official_source_snapshot.json").write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_documentation(root)

    def test_received_evidence_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            selection, _, _ = self.fixture(root)
            (selection / "received/evidence_0.txt").write_text("changed", encoding="ascii")
            with self.assertRaises(ValueError):
                verify_documentation(root)


if __name__ == "__main__":
    unittest.main()
