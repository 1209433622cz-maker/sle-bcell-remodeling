from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import statsmodels.api as sm

import rp_v3_g2_generator as parent_generator
from rp_v3_g2_estimation import responses
from rp_v4_g2c_generator import (
    data_digest,
    generate,
    load_inputs,
    scenario_ids,
    shifted_transition,
    stream,
)
from rp_v4_g2c_hc3t import CRITICAL_VALUE, interval
from rp_v4_g2c_truth import transition as independent_transition
from rp_v4_g2c_truth import truth_pilot
from rp_v4_stageD_sra_plan import plan


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_C = REPO_ROOT / "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze"
CALIBRATION = REPO_ROOT / "phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/02_G2_CALIBRATION_MODEL.json"


class StageDTechnicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows, cls.model = load_inputs(
            STAGE_C / "05_G2C_FINAL_DGP_REGISTRY.csv", CALIBRATION
        )

    def test_01_registered_grid(self) -> None:
        self.assertEqual([row["scenario_id"] for row in self.rows], scenario_ids())
        self.assertEqual(len(self.rows), 40)
        self.assertEqual(
            sum(row["adjudication_role"] == "APPLICABLE_CONJUNCTION" for row in self.rows),
            30,
        )

    def test_02_final_stream_refused(self) -> None:
        with self.assertRaises(PermissionError):
            stream(25, 1, 0, stage=141)

    def test_03_old_generator_counter_parity(self) -> None:
        original_seed = parent_generator.OUTER_SEED
        try:
            parent_generator.OUTER_SEED = 2026101004
            for index in range(25):
                legacy = {
                    **self.rows[index],
                    **{
                        key: float(value)
                        for key, value in self.rows[index]["params"].items()
                    },
                }
                old = parent_generator.generate(
                    self.model, legacy, index, 1, stage=131
                )
                new = generate(self.model, self.rows[index], index, 1)
                self.assertEqual(
                    parent_generator.data_digest(old),
                    data_digest(new),
                    self.rows[index]["scenario_id"],
                )
        finally:
            parent_generator.OUTER_SEED = original_seed

    def test_04_gamma_poisson_shape(self) -> None:
        result = generate(self.model, self.rows[25], 25, 1)
        self.assertEqual(result["categories"].shape, (68, 5, 13))
        self.assertTrue(np.all(result["categories"] >= 0))
        self.assertTrue(np.array_equal(result["flow"].sum(axis=1), result["n"]))

    def test_05_correlated_capture_is_deterministic(self) -> None:
        first = generate(self.model, self.rows[26], 26, 1)
        second = generate(self.model, self.rows[26], 26, 1)
        third = generate(self.model, self.rows[26], 26, 2)
        self.assertEqual(data_digest(first), data_digest(second))
        self.assertNotEqual(data_digest(first), data_digest(third))

    def test_06_nonadjacent_transition(self) -> None:
        matrix = shifted_transition()
        self.assertTrue(np.allclose(matrix.sum(axis=1), 1.0))
        self.assertTrue(np.allclose(matrix.diagonal(), 0.92))
        self.assertTrue(
            np.allclose(
                independent_transition("NONADJACENT_LABEL_CONTAMINATION", 0.0),
                matrix,
            )
        )

    def test_07_registry_tamper_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "registry.csv"
            changed.write_bytes(
                (STAGE_C / "05_G2C_FINAL_DGP_REGISTRY.csv").read_bytes() + b" "
            )
            with self.assertRaises(ValueError):
                load_inputs(changed, CALIBRATION)

    def test_08_real_response_refused(self) -> None:
        synthetic = generate(self.model, self.rows[25], 25, 1)
        outcome = responses(synthetic, self.model)
        with self.assertRaises(PermissionError):
            interval(synthetic["X"], outcome, data_kind="REAL_WP2")

    def test_09_hc3_matches_statsmodels(self) -> None:
        for index in (0, 5, 25, 26, 28, 29, 32, 33, 37, 38):
            synthetic = None
            for attempt_id in range(1, 21):
                candidate = generate(self.model, self.rows[index], index, attempt_id)
                if candidate["support_status"] == "SUPPORTED":
                    synthetic = candidate
                    break
            if synthetic is None:
                continue
            outcome = responses(synthetic, self.model)
            observed = interval(
                synthetic["X"], outcome, data_kind="SIMULATED_ONLY"
            )
            fitted = sm.OLS(outcome[:, 2], synthetic["X"]).fit(cov_type="HC3")
            self.assertAlmostEqual(observed["point"], fitted.params[1], places=11)
            self.assertAlmostEqual(
                observed["standard_error_HC3"], fitted.bse[1], places=10
            )
            self.assertAlmostEqual(
                observed["ci_lower"],
                fitted.params[1] - CRITICAL_VALUE * fitted.bse[1],
                places=10,
            )

    def test_10_delta_algebra(self) -> None:
        for index in (0, 25, 26, 28, 32):
            synthetic = generate(self.model, self.rows[index], index, 1)
            if synthetic["support_status"] == "SUPPORTED":
                outcome = responses(synthetic, self.model)
                self.assertTrue(
                    np.allclose(outcome[:, 2], outcome[:, 1] - outcome[:, 0], atol=2e-14)
                )

    def test_11_oracle_has_no_estimator_import(self) -> None:
        source = (REPO_ROOT / "audit_tools/rp_v4_g2c_truth.py").read_text()
        self.assertNotIn("rp_v4_g2c_generator", source)
        self.assertNotIn("rp_v4_g2c_hc3t", source)
        self.assertNotIn("rp_v3_g2_estimation", source)

    def test_12_exact_null_truth(self) -> None:
        result = truth_pilot(
            self.model, self.rows[25], 25, effort_per_arm=1088, batches=16
        )
        self.assertEqual(result["truth"], 0.0)
        self.assertEqual(result["status"], "TECHNICAL_PRECISION_PASS")
        self.assertFalse(result["final_stage_142_consumed"])

    def test_13_sra_plan_is_plan_only(self) -> None:
        source = STAGE_C / "source_metadata"
        if not all((source / f"{project}_RunInfo.csv").is_file() for project in ("PRJNA1093470", "PRJNA484963")):
            self.skipTest("Ignored official RunInfo inputs are not restored")
        with tempfile.TemporaryDirectory() as directory:
            receipt = plan(source, Path(directory) / "plan")
            self.assertEqual(receipt["runs"], 261)
            self.assertFalse(receipt["download_started"])
            self.assertFalse(receipt["disease_activity_results_inspected"])

    def test_14_sra_plan_refuses_overwrite(self) -> None:
        source = STAGE_C / "source_metadata"
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "plan"
            destination.mkdir()
            with self.assertRaises(FileExistsError):
                plan(source, destination)

    def test_15_stage_c_contract_remains_locked(self) -> None:
        contract = json.loads(
            (STAGE_C / "04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json").read_text()
        )
        seed = json.loads(
            (STAGE_C / "06_G2C_FINAL_SEED_AND_COMPUTE_CONTRACT.json").read_text()
        )
        self.assertEqual(contract["estimand_id"], "delta_profile")
        self.assertEqual(contract["degrees_of_freedom"], 64)
        self.assertIsNone(contract["fallback_method"])
        self.assertFalse(contract["real_effects_permitted"])
        self.assertEqual(seed["final_outer_stage"], 141)
        self.assertEqual(seed["final_truth_stage"], 142)
        self.assertFalse(seed["final_execution_authorized"])

    def test_16_support_stop_is_not_estimated(self) -> None:
        synthetic = generate(self.model, self.rows[27], 27, 1)
        if synthetic["support_status"] == "SUPPORT_STOP":
            self.assertLess(synthetic["min_observed_cells"], 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
