from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np


TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from rp_v3_wp2_kernels import (  # noqa: E402
    composition_geometry,
    freeze_ready,
    frozen_score,
    ilr_basis,
    ilr_positive,
    rank_no_lapack,
    wilson_interval,
)


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.counts = np.array(
            [
                [[10, 5], [20, 4], [15, 7]],
                [[8, 6], [18, 6], [17, 8]],
            ],
            dtype=float,
        )
        self.totals = np.array([[1000, 1800, 1200], [900, 1700, 1400]], dtype=float)
        self.cells = np.array([[30, 40, 30], [25, 45, 30]], dtype=float)
        self.pi = np.array([0.3, 0.4, 0.3])

    def test_01_captured_umi_identity(self):
        result = composition_geometry(self.counts, self.totals, self.cells, self.pi)
        np.testing.assert_allclose(result["pooled_cpm"], result["q_reconstructed_cpm"])

    def test_02_cell_and_umi_weights_are_distinct(self):
        result = composition_geometry(self.counts, self.totals, self.cells, self.pi)
        self.assertFalse(np.allclose(result["p_cell"], result["q_umi"]))

    def test_03_equal_capture_makes_weights_equal(self):
        totals = self.cells * 50
        result = composition_geometry(self.counts, totals, self.cells, self.pi)
        np.testing.assert_allclose(result["p_cell"], result["q_umi"])

    def test_04_missing_bin_fails(self):
        cells = self.cells.copy()
        cells[0, 1] = 0
        with self.assertRaises(ValueError):
            composition_geometry(self.counts, self.totals, cells, self.pi)

    def test_05_invalid_reference_fails(self):
        with self.assertRaises(ValueError):
            composition_geometry(self.counts, self.totals, self.cells, [0.2, 0.3, 0.4])

    def test_06_frozen_score(self):
        score = frozen_score([[0.5, 1.5]], [0.0, 1.0], [1.0, 2.0])
        self.assertEqual(score.shape, (1,))


class CoordinateTests(unittest.TestCase):
    def test_07_ilr_basis_is_orthonormal(self):
        basis = ilr_basis(5)
        np.testing.assert_allclose(basis @ basis.T, np.eye(4), atol=1e-12)

    def test_08_ilr_rejects_zero_without_pseudocount(self):
        with self.assertRaises(ValueError):
            ilr_positive([[0.0, 0.5, 0.5]])

    def test_09_rank_detects_closure(self):
        composition = np.array([[0.2, 0.3, 0.5], [0.1, 0.4, 0.5], [0.3, 0.2, 0.5]])
        design = np.c_[np.ones(3), composition]
        self.assertEqual(rank_no_lapack(design), 2)


class ContractTests(unittest.TestCase):
    def test_10_wilson_zero_is_not_zero_width(self):
        low, high = wilson_interval(0, 2000)
        self.assertAlmostEqual(low, 0.0, places=15)
        self.assertGreater(high, 0.0)

    def test_11_incomplete_contract_stays_locked(self):
        result = freeze_ready({"approved_for_execution": True})
        self.assertFalse(result["ready"])
        self.assertFalse(result["WP2_REAL_EFFECT_UNLOCK"])

    def test_12_current_prefit_is_effect_free(self):
        status_path = (
            ROOT
            / "phase17_v7"
            / "rp_v3_redesign"
            / "20261010_wp2_effect_free_prefit_v1"
            / "04_PREFIT_STATUS.json"
        )
        if not status_path.exists():
            self.skipTest("Canonical WP2 prefit has not been generated")
        status = json.loads(status_path.read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "PASS_STRUCTURAL_PREFIT_ONLY")
        self.assertFalse(status["real_disease_effects_fitted"])
        self.assertFalse(status["WP2_REAL_EFFECT_UNLOCK"])
        self.assertEqual(status["G2"], "NOT_EXECUTED")


if __name__ == "__main__":
    unittest.main()
