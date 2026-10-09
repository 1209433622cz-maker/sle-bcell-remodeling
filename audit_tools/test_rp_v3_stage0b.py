#!/usr/bin/env python3
"""Independent file-level checks for the RP v3 Stage 0B freeze."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase17_v7/rp_v3_redesign/20261009_stage0b"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


class Stage0BTests(unittest.TestCase):
    def test_gate_status(self):
        status = json.loads((OUT / "14_STAGE0B_GATE_STATUS.json").read_text(encoding="utf-8"))
        run_status = json.loads((OUT / "00_STAGE0B_RUN_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["g0_overall"], "PASS_G0")
        self.assertEqual(status["g1"], "PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY")
        self.assertFalse(status["disease_effects_inspected"])
        self.assertTrue(all(item["pass"] for item in status["checks"]))
        self.assertEqual(run_status["run_phase"], "COMPLETE")
        self.assertEqual(run_status["g1"], status["g1"])

    def test_a1_support_and_reference_composition(self):
        dictionary = pd.read_csv(OUT / "02_A1_CONTINUOUS_AXIS_DICTIONARY.csv")
        support = pd.read_csv(OUT / "08_A1_BIN_SUPPORT_SUMMARY.csv")
        pi_ref = pd.read_csv(OUT / "09_PI_REF.csv")
        self.assertEqual(len(dictionary), 14)
        self.assertEqual((dictionary["sign"] > 0).sum(), 7)
        self.assertEqual((dictionary["sign"] < 0).sum(), 7)
        self.assertTrue(support["structural_support_pass"].all())
        self.assertTrue(support["future_arm_support_pass"].all())
        self.assertGreaterEqual(support["supported_donors"].min(), 20)
        self.assertAlmostEqual(float(pi_ref["pi_ref"].sum()), 1.0, places=12)

    def test_a2_structure(self):
        summary = json.loads((OUT / "10_A2_STRUCTURAL_TRIAL_SUMMARY.json").read_text(encoding="utf-8"))
        contract = json.loads((OUT / "03_A2_REPRESENTATION_CONTRACT.json").read_text(encoding="utf-8"))
        self.assertEqual((summary["cells"], summary["features"]), (150_402, 3_000))
        self.assertEqual(summary["strong_isg_features"], 0)
        self.assertGreaterEqual(summary["a0_vs_a2_adjusted_rand_index"], 0.70)
        self.assertEqual(summary["clusters_r0_4"], 5)
        self.assertIn("16,357-gene", contract["normalization"])

    def test_score_contracts(self):
        diagnostics = pd.read_csv(OUT / "12_SCORE_TRANSFER_TECHNICAL_DIAGNOSTICS.csv")
        self.assertEqual(
            set(diagnostics["score"]),
            {"T0_discovery", "T_frozen_external", "T_rank_discovery", "T_rank_external"},
        )
        self.assertTrue((diagnostics["program_genes_present"] == 12).all())
        self.assertTrue((diagnostics["finite_fraction"] == 1.0).all())
        self.assertTrue((diagnostics["background_genes"] == 18_873).all())

    def test_simulation_outputs(self):
        simulation = pd.read_csv(OUT / "13_SIMULATION_TECHNICAL_RESULTS.csv", keep_default_na=False)
        self.assertEqual(simulation["scenario"].nunique(), 5)
        self.assertIn("null_effect", set(simulation["scenario"]))
        self.assertEqual(simulation["estimand"].nunique(), 5)
        self.assertLessEqual(simulation["bias"].abs().max(), 0.06)
        self.assertGreaterEqual(simulation["empirical_95pct_coverage"].min(), 0.90)
        self.assertLessEqual(simulation["empirical_95pct_coverage"].max(), 0.99)

    def test_integrity_manifest(self):
        manifest = pd.read_csv(OUT / "15_STAGE0B_INTEGRITY_MANIFEST.csv")
        self.assertGreaterEqual(len(manifest), 20)
        failures = []
        for row in manifest.itertuples(index=False):
            path = OUT / row.file
            if not path.is_file() or sha256_file(path) != row.sha256:
                failures.append(row.file)
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
