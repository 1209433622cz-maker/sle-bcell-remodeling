from __future__ import annotations

import unittest
import csv
import json
from pathlib import Path

import numpy as np

from rp_v4_g2c_hc3t import CRITICAL_VALUE, DF, ESTIMAND, interval


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_C = REPO_ROOT / "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze"


class G2CHC3TTests(unittest.TestCase):
    def setUp(self) -> None:
        disease = np.r_[np.zeros(31), np.ones(37)]
        age = np.linspace(-1, 1, 68)
        sex = np.tile([0.0, 1.0], 34)
        self.X = np.column_stack([np.ones(68), disease, age, sex])
        phase = np.arange(68, dtype=float)
        self.Y = np.column_stack(
            [
                (0.03 + 0.01 * j) * disease
                + 0.1 * age
                + np.sin(phase + j) * 0.02
                for j in range(10)
            ]
        )

    def test_registered_contract(self) -> None:
        result = interval(self.X, self.Y, data_kind="SIMULATED_ONLY")
        self.assertEqual(result["estimand"], ESTIMAND)
        self.assertEqual(result["df"], DF)
        self.assertAlmostEqual(result["critical_value"], CRITICAL_VALUE)
        self.assertLess(result["ci_lower"], result["point"])
        self.assertGreater(result["ci_upper"], result["point"])
        self.assertFalse(result["WP2_REAL_EFFECT_UNLOCK"])

    def test_rejects_real_responses(self) -> None:
        with self.assertRaises(PermissionError):
            interval(self.X, self.Y, data_kind="REAL")

    def test_rejects_changed_design(self) -> None:
        with self.assertRaises(ValueError):
            interval(self.X[:-1], self.Y[:-1], data_kind="SIMULATED_ONLY")


class StageCContractTests(unittest.TestCase):
    def test_gate_remains_fail_closed(self) -> None:
        gate = json.loads((STAGE_C / "11_RPV4_STAGE_C_GATE_STATUS.json").read_text())
        self.assertEqual(gate["checks_passed"], gate["checks_total"])
        self.assertEqual(gate["G2C_forward_validation"], "NOT_RUN")
        self.assertEqual(gate["WP2_REAL_EFFECT"], "LOCKED")
        self.assertEqual(gate["EXTERNAL_DISEASE_ACTIVITY_OUTCOMES"], "LOCKED")
        self.assertFalse(gate["final_G2C_authorized"])

    def test_final_registry_is_complete(self) -> None:
        with (STAGE_C / "05_G2C_FINAL_DGP_REGISTRY.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 40)
        self.assertEqual(sum(row["family"] == "OLD_COMPARABLE" for row in rows), 25)
        self.assertEqual(sum(row["family"] == "PRESPECIFIED_SHIFT" for row in rows), 15)
        self.assertEqual(sum(row["adjudication_role"] == "APPLICABLE_CONJUNCTION" for row in rows), 30)
        self.assertTrue(all(int(row["outer_attempts"]) == 4000 for row in rows))

    def test_external_manifest_is_outcome_locked(self) -> None:
        with (STAGE_C / "07_EXTERNAL_RAW_INPUT_MANIFEST.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual({row["accession"] for row in rows}, {"GSE262846", "GSE118254"})
        self.assertEqual(sum(int(row["runs"]) for row in rows), 261)
        self.assertTrue(all(row["outcome_unlock"] == "False" for row in rows))
        self.assertTrue(all("POTENTIALLY_OVERLAPPING" in row["provenance_decision"] for row in rows))


if __name__ == "__main__":
    unittest.main()
