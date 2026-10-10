from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse


MODULE_PATH = Path(__file__).with_name("rp_v3_wp3_01_effect_free_prefit.py")
SPEC = importlib.util.spec_from_file_location("rp_v3_wp3_prefit", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class WP3EffectFreePrefitTests(unittest.TestCase):
    def test_duplicate_left_join_is_rejected(self):
        left = pd.DataFrame({"id": [1, 1]})
        right = pd.DataFrame({"id": [1]})
        with self.assertRaisesRegex(ValueError, "duplicate left"):
            MODULE.safe_unique_join(left, right, ["id"])

    def test_duplicate_right_join_is_rejected(self):
        left = pd.DataFrame({"id": [1]})
        right = pd.DataFrame({"id": [1, 1]})
        with self.assertRaisesRegex(ValueError, "duplicate right"):
            MODULE.safe_unique_join(left, right, ["id"])

    def test_unmatched_join_is_rejected(self):
        left = pd.DataFrame({"id": [1]})
        right = pd.DataFrame({"id": [2]})
        with self.assertRaisesRegex(ValueError, "unmatched"):
            MODULE.safe_unique_join(left, right, ["id"])

    def test_float_counts_are_rejected(self):
        matrix = sparse.csr_matrix(np.asarray([[1.0, 2.0]]))
        with self.assertRaisesRegex(ValueError, "integer"):
            MODULE.validate_counts(matrix, pd.Series([3]))

    def test_negative_counts_are_rejected(self):
        matrix = sparse.csr_matrix(np.asarray([[1, -1]], dtype=np.int64))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            MODULE.validate_counts(matrix, pd.Series([0]))

    def test_denominator_mismatch_is_rejected(self):
        matrix = sparse.csr_matrix(np.asarray([[1, 2]], dtype=np.int64))
        with self.assertRaisesRegex(ValueError, "denominator"):
            MODULE.validate_counts(matrix, pd.Series([4]))

    def test_writers_are_lf_and_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "x.csv"
            json_path = root / "x.json"
            MODULE.write_csv(pd.DataFrame({"a": [1]}), csv_path)
            MODULE.write_json({"a": 1}, json_path)
            self.assertEqual(csv_path.read_bytes(), b"a\n1\n")
            self.assertEqual(json_path.read_bytes(), b'{\n  "a": 1\n}\n')

    def test_stage0b_rank_operator_is_exact(self):
        workspace = Path(__file__).resolve().parents[1]
        path = workspace / "audit_tools/rp_v3_stage0b_02_minimal_trial.py"
        MODULE.verify_rank_operator(path)

    def test_gate_schema_never_authorizes_outcomes(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"WP3_OUTCOME_EXECUTION_AUTHORIZED": False', source)
        self.assertIn('"real_IFN_scores_generated": False', source)
        self.assertNotIn("sm.OLS", source)
        self.assertNotIn("linregress", source)


if __name__ == "__main__":
    unittest.main()
