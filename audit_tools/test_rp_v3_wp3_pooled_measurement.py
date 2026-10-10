from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse


MODULE_PATH = Path(__file__).with_name("rp_v3_wp3_02_pooled_measurement.py")
SPEC = importlib.util.spec_from_file_location("rp_v3_wp3_measurement", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class WP3PooledMeasurementTests(unittest.TestCase):
    def test_duplicate_symbols_are_summed(self):
        matrix = sparse.csr_matrix(np.asarray([[1, 2, 4]], dtype=np.int64))
        observed = MODULE.aggregate_symbols(matrix, ["A", "A", "B"], ["A", "B"])
        np.testing.assert_array_equal(observed.toarray(), [[3, 4]])

    def test_duplicate_rank_background_is_rejected(self):
        matrix = sparse.csr_matrix(np.asarray([[1, 2]], dtype=np.int64))
        with self.assertRaisesRegex(ValueError, "duplicate rank"):
            MODULE.aggregate_symbols(matrix, ["A", "B"], ["A", "A"])

    def test_missing_rank_background_is_rejected(self):
        matrix = sparse.csr_matrix(np.asarray([[1, 2]], dtype=np.int64))
        with self.assertRaisesRegex(ValueError, "missing measured"):
            MODULE.aggregate_symbols(matrix, ["A", "B"], ["A", "C"])

    def test_float_counts_are_rejected(self):
        matrix = sparse.csr_matrix(np.asarray([[1.0, 2.0]]))
        with self.assertRaisesRegex(ValueError, "integer"):
            MODULE.validate_counts(matrix)

    def test_negative_counts_are_rejected(self):
        matrix = sparse.csr_matrix(np.asarray([[1, -1]], dtype=np.int64))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            MODULE.validate_counts(matrix)

    def test_full_library_denominator_changes_frozen_only(self):
        program = np.asarray([[5, 10]], dtype=np.int64)
        means = np.zeros(2)
        sds = np.ones(2)
        _, _, smaller = MODULE.frozen_scores(program, np.asarray([100]), means, sds)
        _, _, larger = MODULE.frozen_scores(program, np.asarray([200]), means, sds)
        self.assertNotEqual(smaller[0], larger[0])

    def test_average_ties_divided_by_background_size(self):
        ranks, score = MODULE.rank_scores(np.asarray([[0, 0, 2, 2]]), [0, 2])
        np.testing.assert_array_equal(ranks, [[1.5 / 4, 3.5 / 4]])
        self.assertEqual(score[0], (1.5 / 4 + 3.5 / 4) / 2)

    def test_rank_correlation_identity_and_inverse(self):
        self.assertAlmostEqual(MODULE.rank_concordance(np.arange(5), np.arange(5)), 1.0)
        self.assertAlmostEqual(MODULE.rank_concordance(np.arange(5), np.arange(4, -1, -1)), -1.0)

    def test_constant_rank_correlation_stops(self):
        with self.assertRaisesRegex(ValueError, "constant"):
            MODULE.rank_concordance(np.ones(4), np.arange(4))

    def test_blind_schema_rejects_group_field(self):
        frame = pd.DataFrame(
            {
                "blind_key": ["D001"],
                "pseudobulk_row": [1],
                "cell_count": [50],
                "library_size_umi": [100],
                "disease_group": ["HC"],
            }
        )
        with self.assertRaisesRegex(ValueError, "handoff columns"):
            MODULE.validate_blind_handoff(frame)

    def test_quantiles_use_linear_interpolation(self):
        observed = MODULE.pooled_quantiles(np.asarray([0.0, 10.0]))
        self.assertEqual(observed["q05"], 0.5)
        self.assertEqual(observed["median"], 5.0)

    def test_writers_are_lf_and_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            MODULE.write_csv(pd.DataFrame({"x": [1.25]}), root / "x.csv")
            MODULE.write_json({"b": 2, "a": 1}, root / "x.json")
            self.assertEqual((root / "x.csv").read_bytes(), b"x\n1.25\n")
            self.assertEqual((root / "x.json").read_bytes(), b'{\n  "a": 1,\n  "b": 2\n}\n')

    def test_source_contains_no_inferential_model_call(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("sm.OLS", source)
        self.assertNotIn("linregress", source)
        self.assertNotIn("roc_auc", source)
        self.assertIn('"disease_labels_loaded": False', source)
        self.assertIn('"WP3_OUTCOME_EXECUTION_AUTHORIZED": False', source)


if __name__ == "__main__":
    unittest.main()
