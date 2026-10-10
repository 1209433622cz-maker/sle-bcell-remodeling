from __future__ import annotations

import csv
import gzip
import hashlib
import json
import tempfile
import unittest
import warnings
from pathlib import Path

import numpy as np
import statsmodels.api as sm

from audit_tools import rp_v3_g2_adjudicate as old_adjudicator
from audit_tools import rp_v3_g2_estimation as parent
from audit_tools.rp_v3_g2_generator import generate, load_model, scenarios, stream
from audit_tools.rp_v3_g2b_adjudicate import (
    ADJUDICABLE_REGIMES,
    MIN_SUPPORTED_FOR_COVERAGE_GATE,
    adjudicate_target,
    load_truth,
    wilson,
)
from audit_tools.rp_v3_g2b_full_runner import (
    G2B_STAGE,
    PARENT_FREEZE_DIR,
    PREFIT_DIR,
    REPO_ROOT,
    binding,
    run_chunk,
)
from audit_tools.rp_v3_g2b_studentized import (
    ATTEMPTS,
    EXPECTED_PARENT_SHA256,
    paired_studentized,
    weighted_hc3,
)


class G2BImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent_freeze = REPO_ROOT / PARENT_FREEZE_DIR.relative_to(REPO_ROOT)
        cls.prefit = REPO_ROOT / PREFIT_DIR.relative_to(REPO_ROOT)
        cls.model = load_model(cls.parent_freeze / "02_G2_CALIBRATION_MODEL.json")
        cls.scenarios = scenarios(
            cls.prefit / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv"
        )
        cls.data = generate(cls.model, cls.scenarios[0], 0, 1, stage=G2B_STAGE)
        cls.Y = parent.responses(cls.data, cls.model)
        cls.output = paired_studentized(
            cls.data["X"],
            cls.Y,
            stream(0, 1, 5, stage=G2B_STAGE),
            data_kind="SIMULATED_ONLY",
        )

    def test_01_parent_estimator_is_byte_frozen(self):
        path = REPO_ROOT / "audit_tools" / "rp_v3_g2_estimation.py"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), EXPECTED_PARENT_SHA256)

    def test_02_binding_is_complete_and_uses_stage121(self):
        bound = binding()
        self.assertEqual(bound["schema"], "RP_V3_G2B_FULL_1.0")
        self.assertEqual(bound["stage"], 121)
        self.assertFalse(bound["real_effects_permitted"])
        self.assertFalse(bound["automatic_unlock_permitted"])
        self.assertEqual(bound["scenario_count"], 25)
        self.assertEqual(bound["target_count"], 10)

    def test_03_stage121_is_reproducible_and_disjoint(self):
        first = generate(self.model, self.scenarios[0], 0, 1, stage=G2B_STAGE)
        second = generate(self.model, self.scenarios[0], 0, 1, stage=G2B_STAGE)
        old = generate(self.model, self.scenarios[0], 0, 1, stage=21)
        development = generate(self.model, self.scenarios[0], 0, 1, stage=41)
        np.testing.assert_array_equal(first["categories"], second["categories"])
        self.assertFalse(np.array_equal(first["categories"], old["categories"]))
        self.assertFalse(np.array_equal(first["categories"], development["categories"]))

    def test_04_exact_attempt_count_and_no_failures(self):
        self.assertEqual(self.output["attempted"], ATTEMPTS)
        self.assertEqual(self.output["failures"], 0)
        self.assertEqual(self.output["gate"], "TECHNICAL_INTERVAL_COMPUTED")

    def test_05_real_responses_are_rejected(self):
        with self.assertRaises(PermissionError):
            paired_studentized(self.data["X"], self.Y, data_kind="REAL")

    def test_06_attempt_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            paired_studentized(
                self.data["X"],
                self.Y,
                np.random.default_rng(1),
                data_kind="SIMULATED_ONLY",
                attempts=1999,
            )

    def test_07_point_and_bootstrap_coefficients_match_parent(self):
        reference = parent.paired_bootstrap(
            self.data["X"], self.Y, stream(0, 1, 5, stage=G2B_STAGE)
        )
        np.testing.assert_array_equal(self.output["indices"], reference["indices"])
        np.testing.assert_allclose(self.output["point"], reference["point"], atol=1e-12)
        np.testing.assert_allclose(
            self.output["estimates"], reference["estimates"], atol=1e-11
        )

    def test_08_hc3_matches_explicit_expanded_rows(self):
        X = self.data["X"]
        for bootstrap_id in (0, 399, 799, 1199, 1599, 1999):
            indices = self.output["indices"][bootstrap_id]
            for target in range(10):
                fit = sm.OLS(self.Y[indices, target], X[indices]).fit(cov_type="HC3")
                self.assertAlmostEqual(
                    fit.params[1], self.output["estimates"][bootstrap_id, target], 11
                )
                self.assertAlmostEqual(
                    fit.bse[1], self.output["se_star_HC3"][bootstrap_id, target], 11
                )

    def test_09_paired_delta_uses_own_hc3_studentizer(self):
        fit = sm.OLS(self.Y[:, 1] - self.Y[:, 0], self.data["X"]).fit(cov_type="HC3")
        self.assertAlmostEqual(self.output["point"][2], self.output["point"][1] - self.output["point"][0], 12)
        self.assertAlmostEqual(fit.bse[1], self.output["se_point_HC3"][2], 12)

    def test_10_inverse_quantile_interval_is_exact(self):
        studentized = (
            self.output["estimates"] - self.output["point"]
        ) / self.output["se_star_HC3"]
        quantiles = np.quantile(studentized, [0.025, 0.975], axis=0, method="linear")
        expected = np.column_stack(
            [
                self.output["point"] - quantiles[1] * self.output["se_point_HC3"],
                self.output["point"] - quantiles[0] * self.output["se_point_HC3"],
            ]
        )
        np.testing.assert_allclose(self.output["interval"], expected, atol=1e-12)

    def test_11_invalid_weights_are_rejected(self):
        fractional = np.full((1, 68), 1.5)
        with self.assertRaises(ValueError):
            weighted_hc3(self.data["X"], self.Y, fractional)
        negative = np.ones((1, 68))
        negative[0, 0] = -1
        with self.assertRaises(ValueError):
            weighted_hc3(self.data["X"], self.Y, negative)

    def test_12_all_invalid_draws_fail_closed_without_warning(self):
        arm0 = np.flatnonzero(self.data["X"][:, 1] == 0)[0]
        arm1 = np.flatnonzero(self.data["X"][:, 1] == 1)[0]
        indices = np.tile(np.r_[np.repeat(arm0, 31), np.repeat(arm1, 37)], (2000, 1))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = paired_studentized(
                self.data["X"], self.Y, data_kind="SIMULATED_ONLY", indices=indices
            )
        self.assertEqual(caught, [])
        self.assertEqual(result["failures"], 2000)
        self.assertTrue(np.isnan(result["interval"]).all())
        self.assertIsNone(result["max_bootstrap_leverage"])
        self.assertEqual(result["gate"], "HOLD_NUMERICAL_IMPLEMENTATION")

    def test_13_no_unlock_is_emitted_by_kernel(self):
        self.assertFalse(self.output["G2B_PASS"])
        self.assertFalse(self.output["WP2_REAL_EFFECT_UNLOCK"])

    def test_14_full_runner_chunk_is_complete_and_reusable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "g2b"
            first = run_chunk(root, "C0_R0", 1, 1)
            second = run_chunk(root, "C0_R0", 1, 1)
            self.assertFalse(first["reused"])
            self.assertTrue(second["reused"])
            self.assertEqual(first["stage"], 121)
            chunk = root / "C0_R0" / "chunk_0001_0001"
            with gzip.open(
                chunk / "attempt_targets.csv.gz", "rt", encoding="utf-8", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 10)
            self.assertEqual({row["status"] for row in rows}, {"INTERVAL_COMPUTED"})
            self.assertEqual({int(row["inner_attempted"]) for row in rows}, {2000})

    def test_15_old_g2_binding_is_rejected(self):
        from audit_tools.rp_v3_g2_full_runner import binding as old_binding

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "g2b"
            root.mkdir()
            (root / "run_binding.json").write_text(
                json.dumps(old_binding(), indent=2) + "\n", encoding="utf-8"
            )
            with self.assertRaises(RuntimeError):
                run_chunk(root, "C0_R0", 1, 1)

    def test_16_nonempty_unbound_output_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "g2b"
            root.mkdir()
            (root / "orphan.txt").write_text("orphan", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                run_chunk(root, "C0_R0", 1, 1)

    def test_17_truth_and_domain_contract_are_unchanged(self):
        truth = load_truth(self.parent_freeze / "04_G2_TRUTH_TABLE.csv")
        self.assertEqual(len(truth), 250)
        self.assertEqual(
            ADJUDICABLE_REGIMES,
            {"baseline", "depth_imbalance", "RNA_capture_content"},
        )
        self.assertEqual(MIN_SUPPORTED_FOR_COVERAGE_GATE, 274)

    def test_18_adjudicator_is_rule_equivalent_to_original(self):
        scenario = {
            "scenario_id": "C0_R0",
            "truth_structure": "null",
            "regime": "baseline",
            "domain_classification": "REQUIRED_CORE",
        }
        points = np.linspace(-1.0, 1.0, 2000)
        rows = [
            {
                "target_id": "beta_B",
                "status": "INTERVAL_COMPUTED",
                "point": str(value),
                "ci_lower": "-2" if index <= 1900 else "0.1",
                "ci_upper": "2" if index <= 1900 else "0.2",
            }
            for index, value in enumerate(points, start=1)
        ]
        truth = {
            "truth": 0.0,
            "truth_mcse": 0.0,
            "truth_precision_pass": True,
            "true_null_registered": True,
            "truth_basis": "EXACT_ARM_SYMMETRY",
        }
        self.assertEqual(
            adjudicate_target(scenario, "beta_B", rows, truth),
            old_adjudicator.adjudicate_target(scenario, "beta_B", rows, truth),
        )
        self.assertEqual(wilson(1900, 2000), old_adjudicator.wilson(1900, 2000))

    def test_19_boundary_fixture_cannot_pass(self):
        scenario = {
            "scenario_id": "C0_R3",
            "truth_structure": "null",
            "regime": "adjacent_mislabeling",
            "domain_classification": "MISLABEL_STRESS",
        }
        rows = [
            {"target_id": "beta_B", "status": "SUPPORT_STOP"}
            for _ in range(2000)
        ]
        truth = {
            "truth": 0.0,
            "truth_mcse": 0.0,
            "truth_precision_pass": True,
            "true_null_registered": True,
            "truth_basis": "EXACT_ARM_SYMMETRY",
        }
        result = adjudicate_target(scenario, "beta_B", rows, truth)
        self.assertEqual(result["decision"], "BOUNDARY_REPORTED")
        self.assertFalse(result["applicable_domain"])

    def test_20_frozen_registry_hashes_are_unchanged(self):
        expected = {
            self.parent_freeze / "02_G2_CALIBRATION_MODEL.json": "ecc817549566c1a423237d488313efdba3684965e5c30ff2aa89fc6dc3d7fa0f",
            self.parent_freeze / "04_G2_TRUTH_TABLE.csv": "52e2847c1aa6e38c4a6260b695a806e201d24ffa5e287ef6d5589f0ebe00d15a",
            self.prefit / "07_WP2_G2_TARGET_REGISTRY.csv": "f3e5fabf339aa3d6add44c77c8a263ee753e6da8f8d622d2c2d31f025acdd6f7",
            self.prefit / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv": "d12b2d63edb10df4ef4eb420654e53515c63d5b82696034478f4d1cbd3c51c30",
            self.prefit / "09_G2_ACCEPTANCE_TABLE_FROZEN_FOR_IMPLEMENTATION.csv": "5b2d60e574ac6b92e4c3b9acb00d9c1372261b1be83ab045c2c1192ce625b24e",
        }
        for path, digest in expected.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
