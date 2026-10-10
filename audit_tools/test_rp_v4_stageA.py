from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).with_name("rp_v4_stageA_01_freeze.py")
SPEC = importlib.util.spec_from_file_location("rp_v4_stageA", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RPV4StageATests(unittest.TestCase):
    def test_bool_value_is_strict(self):
        self.assertTrue(MODULE.bool_value(True))
        self.assertTrue(MODULE.bool_value("TRUE"))
        self.assertFalse(MODULE.bool_value(False))
        self.assertFalse(MODULE.bool_value("false"))

    def test_failure_class_separates_bias_from_coverage(self):
        coverage = pd.Series({"coverage_pass": False, "bias_pass": True, "type_i_pass": True})
        bias = pd.Series({"coverage_pass": True, "bias_pass": False, "type_i_pass": None})
        both = pd.Series({"coverage_pass": False, "bias_pass": False, "type_i_pass": False})
        self.assertEqual(MODULE.failure_class(coverage), "INTERVAL_UNDERCOVERAGE")
        self.assertEqual(MODULE.failure_class(bias), "POINT_BIAS_GATE_ONLY")
        self.assertEqual(MODULE.failure_class(both), "COVERAGE_AND_POINT_BIAS__OVERLAPPING_TYPE_I")

    def test_score_contract_does_not_admit_s2(self):
        scores = {row["score_id"]: row for row in MODULE.score_rows()}
        self.assertEqual(scores["S0_T_frozen"]["stageA_decision"], "RETAIN")
        self.assertEqual(scores["S1_T_rank"]["stageA_decision"], "RETAIN_AS_SENSITIVITY")
        self.assertEqual(scores["S2_detection_capture_robust"]["stageA_decision"], "NOT_ADMITTED_TO_V4C")

    def test_miniml_parser_counts_samples(self):
        xml = b'''<?xml version="1.0"?>
        <MINiML xmlns="http://www.ncbi.nlm.nih.gov/geo/info/MINiML">
          <Sample iid="GSM1"><Title>HC.1.rN</Title></Sample>
          <Sample iid="GSM2"><Title>SLE.2.rN</Title></Sample>
          <Series iid="GSE1"><Title>Example</Title></Series>
        </MINiML>'''
        import io
        import tarfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.tgz"
            with tarfile.open(path, "w:gz") as archive:
                info = tarfile.TarInfo("x.xml")
                info.size = len(xml)
                archive.addfile(info, io.BytesIO(xml))
            samples, title = MODULE.miniml_samples(path)
            self.assertEqual(len(samples), 2)
            self.assertEqual(title, "Example")

    def test_source_contains_no_real_effect_model(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("statsmodels", source)
        self.assertNotIn("sm.OLS", source)
        self.assertIn('"G2C_FINAL_EXECUTION_AUTHORIZED": False', source)
        self.assertIn('"NEW_COHORT_OUTCOME_EXECUTION_AUTHORIZED": False', source)


if __name__ == "__main__":
    unittest.main()
