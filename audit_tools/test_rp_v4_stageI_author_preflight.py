from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from audit_tools.rp_v4_stageI_author_preflight import (
    BINDING,
    EXECUTION_SCRIPT,
    git,
    run,
    sha256_file,
)


class StageIAuthorPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "stageI_author_preflight"
        cls.gate = run(cls.output, enforce_clean=False)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_gate_is_ready_for_decision_but_not_authorized(self):
        self.assertEqual(
            self.gate["decision"],
            "READY_FOR_EXPLICIT_TWO_AUTHOR_DECISION__STAGE_I_NOT_AUTHORIZED",
        )
        self.assertFalse(self.gate["author_GO_issued"])
        self.assertFalse(self.gate["stage_I_execution_authorized"])
        self.assertFalse(self.gate["real_response_loaded"])
        self.assertFalse(self.gate["real_disease_coefficient_fitted"])

    def test_draft_is_unsigned_and_bound_to_exact_current_code(self):
        draft = json.loads((self.output / "02_STAGE_I_AUTHOR_GO_DRAFT.json").read_text(encoding="utf-8"))
        self.assertEqual(draft["approved_by"], [])
        self.assertIsNone(draft["approved_at"])
        self.assertFalse(draft["GO_FOR_SINGLE_REAL_DELTA_PROFILE"])
        self.assertEqual(draft["binding_git_commit"], git("rev-parse", "HEAD"))
        self.assertEqual(draft["input_binding_manifest_sha256"], sha256_file(BINDING))
        self.assertEqual(draft["execution_script_sha256"], sha256_file(EXECUTION_SCRIPT))

    def test_eight_technical_checks_pass_and_author_go_remains_open(self):
        with (self.output / "03_STAGE_I_AUTHOR_PREFLIGHT_CHECKS.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 9)
        self.assertEqual(sum(row["pass"] == "True" for row in rows), 8)
        author_row = next(row for row in rows if row["check"] == "author_GO_issued")
        self.assertEqual(author_row["pass"], "False")

    def test_unsigned_draft_fails_before_response_or_output(self):
        receipt = json.loads((self.output / "04_UNSIGNED_FAIL_CLOSED_RECEIPT.json").read_text(encoding="utf-8"))
        self.assertTrue(receipt["pass"])
        self.assertEqual(receipt["exception"], "PermissionError")
        self.assertFalse(receipt["result_directory_created"])
        self.assertFalse(receipt["real_response_loaded"])
        self.assertFalse(receipt["real_disease_coefficient_fitted"])
        self.assertFalse((self.output / "forbidden_unsigned_result").exists())

    def test_baseline_records_qualified_runtime_without_outcome_access(self):
        baseline = json.loads((self.output / "01_POST_STAGE_H_EXACT_BASELINE.json").read_text(encoding="utf-8"))
        self.assertEqual(Path(baseline["runtime"]["python_executable"]).resolve(), Path(r"D:\bioinfor\python.exe").resolve())
        self.assertFalse(baseline["real_response_loaded"])
        self.assertFalse(baseline["real_disease_coefficient_fitted"])

    def test_integrity_manifest_covers_all_prior_packet_files(self):
        with (self.output / "08_INTEGRITY_MANIFEST.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 7)
        self.assertEqual(
            {row["path"] for row in rows},
            {
                "01_POST_STAGE_H_EXACT_BASELINE.json",
                "02_STAGE_I_AUTHOR_GO_DRAFT.json",
                "03_STAGE_I_AUTHOR_PREFLIGHT_CHECKS.csv",
                "04_UNSIGNED_FAIL_CLOSED_RECEIPT.json",
                "05_STAGE_I_AUTHOR_DECISION_FORM.md",
                "06_STAGE_I_AUTHOR_PREFLIGHT_GATE.json",
                "07_STAGE_I_AUTHOR_PREFLIGHT_ADVISOR_REVIEW.md",
            },
        )
        for row in rows:
            path = self.output / row["path"]
            self.assertEqual(path.stat().st_size, int(row["bytes"]))
            self.assertEqual(sha256_file(path), row["sha256"])


if __name__ == "__main__":
    unittest.main()
