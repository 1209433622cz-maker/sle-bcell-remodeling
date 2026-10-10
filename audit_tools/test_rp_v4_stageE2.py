from __future__ import annotations

import json
import csv
import tempfile
import unittest
from pathlib import Path

from audit_tools import rp_v4_g2c_generator as stage_d_generator
from audit_tools import rp_v4_g2c_truth as stage_d_truth
from audit_tools import rp_v4_stageE2_adjudicator as adjudicator
from audit_tools import rp_v4_stageE2_adjudicate_run as adjudicate_run
from audit_tools import rp_v4_stageE2_generator as stage_e_generator
from audit_tools import rp_v4_stageE2_truth as stage_e_truth
from audit_tools.rp_v4_stageE2_common import ExecutionAuthorization
from audit_tools.rp_v4_stageE2_runner import run as run_outer


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "phase17_v7"
    / "rp_v4_redesign"
    / "20261010_stageC_single_g2c_external_input_protocol_freeze"
    / "05_G2C_FINAL_DGP_REGISTRY.csv"
)
MODEL = (
    ROOT
    / "phase17_v7"
    / "rp_v3_redesign"
    / "20261010_g2_implementation_freeze"
    / "02_G2_CALIBRATION_MODEL.json"
)
OLD_TRUTH = (
    ROOT
    / "phase17_v7"
    / "rp_v3_redesign"
    / "20261010_g2_implementation_freeze"
    / "04_G2_TRUTH_TABLE.csv"
)


def authorization(stage: int, purpose: str, final: bool = False):
    return ExecutionAuthorization(stage=stage, purpose=purpose, final=final)


def attempt(
    attempt_id: int,
    *,
    point: float = 0.0,
    lower: float = -1.0,
    upper: float = 1.0,
    status: str = "SUPPORTED",
):
    row = {
        "scenario_id": "C0_X1",
        "scenario_index": 25,
        "attempt_id": attempt_id,
        "stage": 141,
        "seed_base": 2026101004,
        "data_kind": "SIMULATED_ONLY",
        "input_digest": "a" * 64,
        "status": status,
        "real_effects_fitted": False,
    }
    if status == "SUPPORTED":
        row["synthetic_HC3_t"] = {
            "estimand": "delta_profile",
            "point": point,
            "ci_lower": lower,
            "ci_upper": upper,
            "standard_error_HC3": 0.2,
        }
    return row


def oracle():
    return {
        "scenario_id": "C0_X1",
        "truth": 0.0,
        "truth_mcse": 0.0,
        "typical_coefficient_se": 0.2,
        "precision_pass": True,
        "exact_null_registered": True,
    }


class GeneratorAndTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.model = stage_e_generator.load_inputs(REGISTRY, MODEL)

    def test_stage_e_generator_matches_frozen_algorithm(self):
        old_stage = stage_d_generator.DEVELOPMENT_STAGE
        stage_d_generator.DEVELOPMENT_STAGE = 132
        try:
            for scenario_id in ("C0_X1", "C1_X2", "C2_X3"):
                index = next(
                    i for i, row in enumerate(self.rows) if row["scenario_id"] == scenario_id
                )
                expected = stage_d_generator.generate(
                    self.model, self.rows[index], index, 2, stage=132
                )
                observed = stage_e_generator.generate(
                    self.model,
                    self.rows[index],
                    index,
                    2,
                    authorization(132, "outer"),
                )
                self.assertEqual(
                    stage_d_generator.data_digest(expected),
                    stage_e_generator.data_digest(observed),
                )
        finally:
            stage_d_generator.DEVELOPMENT_STAGE = old_stage

    def test_generator_rejects_truth_token(self):
        with self.assertRaises(PermissionError):
            stage_e_generator.generate(
                self.model, self.rows[25], 25, 1, authorization(132, "truth")
            )

    def test_truth_batch_matches_frozen_stage131_algorithm(self):
        scenario = self.rows[26]
        expected = stage_d_truth._coupled_batch(
            self.model, scenario, 26, 0, 64
        )
        observed = stage_e_truth._coupled_batch(
            self.model,
            scenario,
            26,
            0,
            64,
            authorization(131, "truth"),
        )
        self.assertEqual(expected, observed)

    def test_truth_rejects_outer_token(self):
        with self.assertRaises(PermissionError):
            stage_e_truth._rng(25, 0, authorization(132, "outer"))


class RunnerTests(unittest.TestCase):
    def test_qualification_resume_is_stable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "outer"
            first = run_outer(
                registry_path=REGISTRY,
                calibration_model_path=MODEL,
                output=output,
                mode="qualification",
                selected_scenarios=("C0_X1",),
                qualification_attempts=2,
            )
            second = run_outer(
                registry_path=REGISTRY,
                calibration_model_path=MODEL,
                output=output,
                mode="qualification",
                resume=True,
                selected_scenarios=("C0_X1",),
                qualification_attempts=2,
            )
            self.assertEqual(first["attempts"], 2)
            self.assertEqual(second["reused_chunks"], 1)
            self.assertFalse(second["final_G2C_adjudicated"])

    def test_final_requires_exact_code_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(PermissionError):
                run_outer(
                    registry_path=REGISTRY,
                    calibration_model_path=MODEL,
                    output=Path(temporary) / "final",
                    mode="final",
                )


class AdjudicatorTests(unittest.TestCase):
    def test_missing_attempt_rejected(self):
        with self.assertRaises(ValueError):
            adjudicator.validate_attempts([attempt(1)], "C0_X1", 25)

    def test_duplicate_attempt_rejected(self):
        rows = [attempt(i) for i in range(1, 4001)]
        rows[-1]["attempt_id"] = 1
        with self.assertRaises(ValueError):
            adjudicator.validate_attempts(rows, "C0_X1", 25)

    def test_real_data_rejected(self):
        rows = [attempt(i) for i in range(1, 4001)]
        rows[0]["data_kind"] = "REAL"
        with self.assertRaises(PermissionError):
            adjudicator.validate_attempts(rows, "C0_X1", 25)

    def test_boundary_is_reported_without_performance_claim(self):
        rows = [attempt(i, status="SUPPORT_STOP") for i in range(1, 4001)]
        scenario = {
            "scenario_id": "C0_X1",
            "scenario_index": 25,
            "adjudication_role": "MANDATORY_BOUNDARY_REPORT",
        }
        result = adjudicator.adjudicate_one(rows, scenario, oracle())
        self.assertEqual(result["status"], "BOUNDARY_REPORTED")

    def test_excess_numerical_failure_holds(self):
        rows = [attempt(i) for i in range(1, 4001)]
        for row in rows[:41]:
            row["status"] = "NUMERICAL_FAILURE"
            row.pop("synthetic_HC3_t")
        scenario = {
            "scenario_id": "C0_X1",
            "scenario_index": 25,
            "adjudication_role": "APPLICABLE_CONJUNCTION",
        }
        result = adjudicator.adjudicate_one(rows, scenario, oracle())
        self.assertEqual(result["status"], "HOLD_NUMERICAL_FAILURE")

    def test_truth_precision_rejected(self):
        value = oracle()
        value["truth_mcse"] = 0.01
        scenario = {
            "scenario_id": "C0_X1",
            "scenario_index": 25,
            "adjudication_role": "APPLICABLE_CONJUNCTION",
        }
        with self.assertRaises(ValueError):
            adjudicator.adjudicate_one(
                [attempt(i) for i in range(1, 4001)], scenario, value
            )

    def test_wilson_reference(self):
        lower, upper = adjudicator.wilson_interval(3800, 4000)
        self.assertGreater(lower, 0.94)
        self.assertLess(upper, 0.96)

    def test_full_conjunction_requires_boundary_integrity(self):
        registry = []
        results = []
        for index in range(40):
            role = "APPLICABLE_CONJUNCTION" if index < 30 else "MANDATORY_BOUNDARY_REPORT"
            scenario_id = f"S{index}"
            registry.append(
                {"scenario_id": scenario_id, "adjudication_role": role}
            )
            results.append(
                {
                    "scenario_id": scenario_id,
                    "domain": role,
                    "n_attempts": 4000,
                    "oracle_precision_pass": True,
                    "status": "PASS" if index < 30 else "BOUNDARY_REPORTED",
                }
            )
        self.assertTrue(
            adjudicator.full_conjunction(results, registry)[
                "g2c_synthetic_applicable_conjunction_pass"
            ]
        )
        results[-1]["status"] = "HOLD_NUMERICAL_FAILURE"
        self.assertFalse(
            adjudicator.full_conjunction(results, registry)[
                "g2c_synthetic_applicable_conjunction_pass"
            ]
        )

    def test_driver_rejects_nonfinal_shifted_truth(self):
        registry = adjudicate_run.load_registry(REGISTRY)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "shifted.csv"
            fieldnames = [
                "scenario_id",
                "truth",
                "truth_mcse",
                "typical_coefficient_se",
                "precision_pass",
                "exact_null_registered",
                "truth_basis",
                "stage",
                "final",
            ]
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for structure in range(5):
                    for stress in range(1, 4):
                        writer.writerow(
                            {
                                "scenario_id": f"C{structure}_X{stress}",
                                "truth": 0.0,
                                "truth_mcse": 0.0,
                                "typical_coefficient_se": 0.2,
                                "precision_pass": True,
                                "exact_null_registered": structure == 0,
                                "truth_basis": "TEST_ONLY",
                                "stage": 132,
                                "final": False,
                            }
                        )
            with self.assertRaises(ValueError):
                adjudicate_run.load_oracles(OLD_TRUTH, path, registry)


if __name__ == "__main__":
    unittest.main()
