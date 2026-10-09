import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


MODULE_PATH = Path(__file__).with_name("rp_v3_wp1_02_fit_annotation_sensitivity.py")
SPEC = importlib.util.spec_from_file_location("rp_v3_wp1", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WP1Tests(unittest.TestCase):
    def test_t0_score_matches_manual_calculation(self):
        counts = np.array([[10.0, 20.0]])
        totals = np.array([1_000_000.0])
        means = np.array([0.0, 0.0])
        sds = np.array([1.0, 2.0])
        expected = (np.log2(10.5) + np.log2(20.5) / 2) / 2
        self.assertAlmostEqual(MODULE.t0_score(counts, totals, means, sds)[0], expected)

    def test_expression_reconstruction_precedes_log(self):
        counts = np.array([[[1.0], [9.0]]])
        totals = np.array([[1_000_000.0, 1_000_000.0]])
        weights = np.array([0.5, 0.5])
        reconstructed = MODULE.reconstruct_a1_score(counts, totals, weights, np.array([0.0]), np.array([1.0]))[0]
        score_first = np.mean(np.log2(np.array([1.0, 9.0]) + 0.5))
        self.assertAlmostEqual(reconstructed, np.log2(5.5))
        self.assertNotAlmostEqual(reconstructed, score_first)

    def test_invalid_pi_ref_stops(self):
        with self.assertRaises(ValueError):
            MODULE.reconstruct_a1_score(
                np.ones((1, 2, 1)), np.ones((1, 2)), np.array([0.2, 0.2]),
                np.array([0.0]), np.array([1.0]),
            )

    def test_design_rank(self):
        full = np.array([[1, 0, -1, 0], [1, 0, 1, 1], [1, 1, -2, 0], [1, 1, 2, 1]], dtype=float)
        deficient = np.c_[np.ones(4), [0, 1, 0, 1], [1, 0, 1, 0]]
        self.assertEqual(MODULE.design_rank(full), 4)
        self.assertEqual(MODULE.design_rank(deficient), 2)

    def test_ols_coefficient(self):
        x = np.c_[np.ones(6), [0, 0, 0, 1, 1, 1], [-2, 0, 2, -2, 0, 2], [0, 1, 0, 1, 0, 1]]
        beta = np.array([0.5, 1.25, -0.1, 0.2])
        y = x @ beta
        self.assertAlmostEqual(MODULE.ols_coefficient(y, x), 1.25)

    def test_percentile_interval_ignores_failed_rows(self):
        low, high = MODULE.percentile_interval(pd.Series([0.0, 1.0, 2.0, np.nan]))
        self.assertAlmostEqual(low, 0.05)
        self.assertAlmostEqual(high, 1.95)


if __name__ == "__main__":
    unittest.main(verbosity=2)
