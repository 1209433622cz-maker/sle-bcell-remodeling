from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from audit_tools.rp_v3_g2_adjudicate import (
    ADJUDICABLE_REGIMES,
    MIN_SUPPORTED_FOR_COVERAGE_GATE,
    adjudicate_target,
    load_truth,
    wilson,
)
from audit_tools.rp_v3_g2_estimation import TARGETS, responses
from audit_tools.rp_v3_g2_full_runner import FREEZE_DIR, PREFIT_DIR, REPO_ROOT, run_chunk
from audit_tools.rp_v3_g2_generator import FULL_STAGE, generate, load_model, scenarios


class G2ImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = REPO_ROOT / FREEZE_DIR.relative_to(REPO_ROOT)
        cls.prefit = REPO_ROOT / PREFIT_DIR.relative_to(REPO_ROOT)
        cls.model = load_model(cls.freeze / "02_G2_CALIBRATION_MODEL.json")
        cls.scenarios = scenarios(cls.prefit / "08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv")

    def test_01_promoted_candidate_hashes_are_exact(self):
        expected = {
            "rp_v3_g2_generator.py": "1a6a2bfd46fc9f9dee9ac27a31c3a7091cfacf29fa1d68b5252832bd76c4d615",
            "rp_v3_g2_estimation.py": "0973b83fca955fa76d1d9fb47cd8792138ea7ff3b9c2dce1b873f6931b3f6b40",
            "rp_v3_g2_truth.py": "b9193fdc63431da130bf8135ffbabb669ada9ec6e37db184b09666f36784199f",
        }
        for name, digest in expected.items():
            path = REPO_ROOT / "audit_tools" / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_02_model_is_outcome_free_and_complete(self):
        self.assertEqual(self.model["template_n"].shape, (68, 5))
        self.assertEqual(self.model["template_probs"].shape, (68, 5, 13))
        self.assertFalse(self.model["true_template_labels_present"])
        self.assertTrue(np.allclose(self.model["template_probs"].sum(axis=2), 1.0))

    def test_03_registry_is_unchanged(self):
        self.assertEqual(len(self.scenarios), 25)
        self.assertEqual({row["regime"] for row in self.scenarios}, {
            "baseline", "rarity_support", "depth_imbalance", "adjacent_mislabeling", "RNA_capture_content"
        })
        self.assertEqual(ADJUDICABLE_REGIMES, {"baseline", "depth_imbalance", "RNA_capture_content"})

    def test_04_truth_table_is_complete_and_depth_null_is_not_forced_zero(self):
        truth = load_truth(self.freeze / "04_G2_TRUTH_TABLE.csv")
        self.assertEqual(len(truth), 250)
        self.assertAlmostEqual(truth[("C0_R2", "beta_B")]["truth"], -0.0977960260359306)
        self.assertFalse(truth[("C0_R2", "beta_B")]["true_null_registered"])
        self.assertTrue(truth[("C0_R0", "beta_B")]["true_null_registered"])

    def test_05_minimum_coverage_sample_size_is_mathematically_derived(self):
        self.assertEqual(MIN_SUPPORTED_FOR_COVERAGE_GATE, 274)
        for n in range(1, MIN_SUPPORTED_FOR_COVERAGE_GATE):
            self.assertFalse(any(wilson(k, n)[0] >= 0.925 and wilson(k, n)[1] <= 0.975 for k in range(n + 1)))
        self.assertTrue(any(
            wilson(k, MIN_SUPPORTED_FOR_COVERAGE_GATE)[0] >= 0.925
            and wilson(k, MIN_SUPPORTED_FOR_COVERAGE_GATE)[1] <= 0.975
            for k in range(MIN_SUPPORTED_FOR_COVERAGE_GATE + 1)
        ))

    def test_06_real_responses_are_blocked(self):
        with self.assertRaises(PermissionError):
            responses({"data_kind": "REAL"}, self.model)

    def test_07_full_stage_is_distinct_and_reproducible(self):
        first = generate(self.model, self.scenarios[0], 0, 1, stage=FULL_STAGE)
        second = generate(self.model, self.scenarios[0], 0, 1, stage=FULL_STAGE)
        self.assertTrue(np.array_equal(first["categories"], second["categories"]))
        self.assertEqual(first["support_status"], "SUPPORTED")

    def test_08_one_attempt_chunk_is_complete_and_reusable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            first = run_chunk(root, "C0_R0", 1, 1)
            second = run_chunk(root, "C0_R0", 1, 1)
            self.assertFalse(first["reused"])
            self.assertTrue(second["reused"])
            chunk = root / "C0_R0" / "chunk_0001_0001"
            with gzip.open(chunk / "attempt_targets.csv.gz", "rt", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 10)
            self.assertEqual({row["target_id"] for row in rows}, set(TARGETS))
            self.assertEqual({row["status"] for row in rows}, {"INTERVAL_COMPUTED"})
            self.assertEqual({int(row["inner_attempted"]) for row in rows}, {2000})

    def test_09_adjudicator_passes_well_calibrated_applicable_fixture(self):
        scenario = {
            "scenario_id": "C0_R0", "truth_structure": "null", "regime": "baseline",
            "domain_classification": "REQUIRED_CORE",
        }
        point = np.linspace(-1.0, 1.0, 2000)
        rows = []
        for i, value in enumerate(point, start=1):
            covered = i <= 1900
            rows.append({
                "target_id": "beta_B", "status": "INTERVAL_COMPUTED", "point": str(value),
                "ci_lower": "-2" if covered else "0.1", "ci_upper": "2" if covered else "0.2",
            })
        truth = {
            "truth": 0.0, "truth_mcse": 0.0, "truth_precision_pass": True,
            "true_null_registered": True, "truth_basis": "EXACT_ARM_SYMMETRY",
        }
        result = adjudicate_target(scenario, "beta_B", rows, truth)
        self.assertEqual(result["decision"], "PASS_TARGET_SCENARIO")
        self.assertAlmostEqual(result["coverage"], 0.95)
        self.assertAlmostEqual(result["type_i"], 0.05)

    def test_10_boundary_fixture_never_becomes_pass(self):
        scenario = {
            "scenario_id": "C0_R3", "truth_structure": "null", "regime": "adjacent_mislabeling",
            "domain_classification": "MISLABEL_STRESS",
        }
        rows = [{"target_id": "beta_B", "status": "SUPPORT_STOP"} for _ in range(2000)]
        truth = {
            "truth": 0.0, "truth_mcse": 0.0, "truth_precision_pass": True,
            "true_null_registered": True, "truth_basis": "EXACT_ARM_SYMMETRY",
        }
        result = adjudicate_target(scenario, "beta_B", rows, truth)
        self.assertEqual(result["decision"], "BOUNDARY_REPORTED")
        self.assertFalse(result["applicable_domain"])


if __name__ == "__main__":
    unittest.main()
