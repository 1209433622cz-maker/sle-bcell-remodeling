"""Regression tests for C9 normalization and fail-closed outcome access."""

from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd
from scipy import sparse

from phase17_c9_common import normalize_log_cp10k, sha256_file
from phase17_c9_01_prefreeze_label_agnostic_mapping import (
    calibrate_confidence, confidence_calibration_passed,
    require_empty_run_directory, validate_run_scope,
)
from phase17_c9_02_unlock_outcomes_and_review import (
    validate_unlock_decision, verify_metadata_binding,
)


class NormalizationTests(unittest.TestCase):
    def test_feature_subsetting_preserves_full_library_normalization(self):
        counts = sparse.csr_matrix([[1, 3, 16], [2, 8, 90], [0, 0, 0]])
        totals = np.asarray(counts.sum(axis=1)).ravel()
        observed = normalize_log_cp10k(counts[:, :2], library_totals=totals)
        expected = normalize_log_cp10k(counts)[:, :2]
        np.testing.assert_allclose(observed.toarray(), expected.toarray())
        self.assertFalse(np.allclose(normalize_log_cp10k(counts[:, :2]).toarray(), expected.toarray()))

    def test_zero_library_remains_zero_and_input_is_unchanged(self):
        counts = sparse.csr_matrix([[0, 0], [1, 3]])
        original = counts.copy()
        actual = normalize_log_cp10k(counts).toarray()
        np.testing.assert_array_equal(actual[0], [0, 0])
        np.testing.assert_allclose(actual[1], np.log1p([2500, 7500]), rtol=1e-6)
        np.testing.assert_array_equal(counts.toarray(), original.toarray())

    def test_invalid_counts_and_denominators_rejected(self):
        for data in ([[1, -1]], [[np.nan, 1]], [[np.inf, 1]]):
            with self.assertRaises(ValueError):
                normalize_log_cp10k(sparse.csr_matrix(data))
        counts = sparse.csr_matrix([[2, 4]])
        for totals in ([1], [np.nan], [-1], [0, 6], [[6]]):
            with self.assertRaises(ValueError):
                normalize_log_cp10k(counts, library_totals=totals)


class FreezeTests(unittest.TestCase):
    def test_failed_calibration_cannot_pass_gate(self):
        _, audit = calibrate_confidence(
            np.array([0, 0, 1, 1]), np.array([0, 1, 1, 1]),
            np.array([0.96] * 4), np.array([0.7, 0.95]),
        )
        self.assertFalse(confidence_calibration_passed(audit))
        self.assertTrue(audit["diagnostic_fallback_only"].all())

    def test_valid_calibration_selects_smallest_eligible_threshold(self):
        threshold, audit = calibrate_confidence(
            np.array([0, 1]), np.array([0, 1]), np.array([0.96, 0.97]), np.array([0.7, 0.95]),
        )
        self.assertEqual(threshold, 0.7)
        self.assertTrue(confidence_calibration_passed(audit))

    def test_partial_formal_run_rejected(self):
        with self.assertRaises(ValueError):
            validate_run_scope(False, 4)
        with self.assertRaises(ValueError):
            validate_run_scope(True, 0)
        validate_run_scope(True, 4)
        validate_run_scope(False, None)

    def test_legacy_pass_is_not_unlock_authorization(self):
        with self.assertRaises(RuntimeError):
            validate_unlock_decision({
                "decision": "PASS_C9A_PREFREEZE_OUTCOME_UNLOCK_AUTHORIZED",
                "outcome_unlock_authorized": True,
            })

    def test_failed_gate_is_rejected_even_if_pass_label_is_set(self):
        decision = {
            "decision": "PASS_C9A_PREFREEZE_OUTCOME_UNLOCK_AUTHORIZED",
            "outcome_unlock_authorized": True,
            "normalization_contract": "full_library_cp10k_before_feature_subsetting",
            "checks": {key: True for key in (
                "elastic_confidence_calibration_eligible", "centroid_confidence_calibration_eligible",
                "all_expected_samples_processed", "all_cells_reconciled")},
        }
        validate_unlock_decision(decision)
        decision["checks"]["elastic_confidence_calibration_eligible"] = False
        with self.assertRaises(RuntimeError):
            validate_unlock_decision(decision)

    def test_metadata_substitution_and_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "Meta_caSLE_processed_08092021_small.csv"
            other = root / "different.csv"
            first.touch()
            other.touch()
            manifest = pd.DataFrame([{
                "path": first.name, "filename": first.name,
                "protected_metadata": True, "sha256": sha256_file(first),
            }])
            verify_metadata_binding(first, manifest, root)
            with self.assertRaises(RuntimeError):
                verify_metadata_binding(other, manifest, root)
            with self.assertRaises(RuntimeError):
                require_empty_run_directory(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
