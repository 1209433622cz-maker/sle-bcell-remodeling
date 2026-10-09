from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/rp_v3_redesign/20261009_stage0"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RUN / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class RpV3Stage0FreezeTest(unittest.TestCase):
    def test_gate_status_is_honest(self) -> None:
        status = json.loads((RUN / "08_STAGE0_GATE_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["submission_status"], "HOLD_SUBMISSION")
        self.assertEqual(status["g0a_input_recovery"], "PASS")
        self.assertEqual(status["g0b_protocol_freeze"], "HOLD")
        self.assertEqual(status["g0_overall"], "HOLD_G0_PROTOCOL_FREEZE")
        self.assertEqual(status["g1_precheck"], "HOLD_DEFINITION_AND_IDENTIFIABILITY_TRIAL_REQUIRED")
        self.assertEqual(status["wp4"], "HOLD_CONDITIONAL")
        self.assertTrue(all(check["pass"] for check in status["checks"]))

    def test_manifest_and_unit_counts(self) -> None:
        manifest = read_csv("01_input_manifest.csv")
        self.assertEqual(len(manifest), 21)
        self.assertTrue(all(row["exists"] == "True" for row in manifest))
        self.assertTrue(all(len(row["sha256"]) == 64 for row in manifest))

        units = {(row["dataset"], row["level"]): row for row in read_csv("02_unit_registry.csv")}
        self.assertEqual(units[("GSE174188", "cell")]["n"], "150402")
        self.assertEqual(units[("GSE174188", "donor")]["n"], "259")
        self.assertEqual(units[("GSE174188", "primary B_CONV pseudobulk")]["n"], "89")
        self.assertEqual(units[("GSE135779", "raw sample/donor")]["n"], "56")
        self.assertEqual(units[("GSE135779", "primary childhood model")]["n"], "43")

    def test_docx_and_branch_boundaries(self) -> None:
        status = json.loads((RUN / "08_STAGE0_GATE_STATUS.json").read_text(encoding="utf-8"))
        review = status["docx_review"]
        self.assertEqual(review["tracked_insertions"], 0)
        self.assertEqual(review["tracked_deletions"], 0)
        self.assertFalse(review["comments_xml"])
        self.assertEqual(review["rendered_pages"], 36)

        branches = {row["branch"]: row for row in read_csv("05_branch_registry.csv")}
        self.assertEqual(branches["A0"]["status"], "FROZEN_HISTORICAL")
        self.assertEqual(branches["A2"]["status"], "HISTORICAL_SPEC_AVAILABLE_REBUILD_REQUIRED")
        self.assertEqual(branches["WP4"]["status"], "HOLD_CONDITIONAL")

    def test_open_parameters_remain_open(self) -> None:
        parameters = {row["field"]: row for row in read_csv("06_parameter_freeze.csv")}
        for field in ("state_support_threshold", "T0", "T_frozen", "T_rank", "pi_ref"):
            self.assertEqual(parameters[field]["status"], "OPEN")
        self.assertEqual(parameters["interpretive_margin_delta"]["status"], "NO_MARGIN")


if __name__ == "__main__":
    unittest.main()
