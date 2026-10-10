from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from audit_tools.rp_v4_stageH_effect_blind_prefit import EXECUTION_SCRIPT, run, sha256_file
from audit_tools.rp_v4_stageI_real_delta_profile import execute


class StageHEffectBlindPrefitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "stageH"
        cls.gate = run(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_gate_passes_without_authorizing_or_fitting_effect(self):
        self.assertEqual(
            self.gate["decision"],
            "PASS_STAGE_H_EFFECT_BLIND_APPLICABILITY__HOLD_STAGE_I_AUTHOR_SIGNOFF",
        )
        self.assertTrue(self.gate["effect_blind"])
        self.assertFalse(self.gate["real_response_loaded"])
        self.assertFalse(self.gate["real_disease_coefficient_fitted"])
        self.assertFalse(self.gate["stage_I_execution_authorized"])

    def test_design_support_and_applicability_are_complete(self):
        audit = pd.read_csv(self.output / "02_EFFECT_BLIND_SUPPORT_AND_DESIGN_AUDIT.csv")
        applicability = pd.read_csv(self.output / "04_SYNTHETIC_APPLICABILITY_COMPARISON.csv")
        self.assertEqual(len(audit), 9)
        self.assertEqual(len(applicability), 9)
        self.assertTrue(audit["pass"].all())
        self.assertTrue(audit["effect_blind"].all())
        self.assertTrue(applicability["pass"].all())
        self.assertEqual(float(applicability.loc[applicability.check == "design_anchor_identity", "observed"].iloc[0]), 0.0)
        self.assertEqual(float(applicability.loc[applicability.check == "cell_template_identity", "observed"].iloc[0]), 0.0)

    def test_signoff_template_is_unissued_and_binds_execution_code(self):
        signoff = json.loads((self.output / "07_STAGE_I_AUTHOR_SIGNOFF_TEMPLATE.json").read_text(encoding="utf-8"))
        self.assertEqual(signoff["approved_by"], [])
        self.assertIsNone(signoff["approved_at"])
        self.assertFalse(signoff["GO_FOR_SINGLE_REAL_DELTA_PROFILE"])
        self.assertEqual(signoff["execution_script_sha256"], sha256_file(EXECUTION_SCRIPT))

    def test_integrity_manifest_covers_every_prior_output(self):
        manifest = pd.read_csv(self.output / "11_INTEGRITY_MANIFEST.csv")
        self.assertEqual(len(manifest), 10)
        self.assertEqual(
            set(manifest["path"]),
            {
                "01_REAL_INPUT_BINDING_MANIFEST.csv",
                "02_EFFECT_BLIND_SUPPORT_AND_DESIGN_AUDIT.csv",
                "03_REAL_GEOMETRY_SUMMARY.json",
                "04_SYNTHETIC_APPLICABILITY_COMPARISON.csv",
                "05_SINGLE_REAL_ESTIMAND_CONTRACT.json",
                "06_WRITE_ONCE_RESULT_SCHEMA.json",
                "07_STAGE_I_AUTHOR_SIGNOFF_TEMPLATE.json",
                "08_STAGE_H_GATE_STATUS.json",
                "09_STAGE_H_ADVISOR_REVIEW.md",
                "10_STAGE_I_EXECUTION_CONTRACT.md",
            },
        )
        for row in manifest.to_dict("records"):
            path = self.output / row["path"]
            self.assertEqual(path.stat().st_size, int(row["bytes"]))
            self.assertEqual(sha256_file(path), row["sha256"])

    def test_stage_i_fails_before_output_without_new_author_go(self):
        authorization = self.output / "07_STAGE_I_AUTHOR_SIGNOFF_TEMPLATE.json"
        result = Path(self.temp.name) / "forbidden_stageI"
        with self.assertRaises(PermissionError):
            execute(authorization, self.output / "01_REAL_INPUT_BINDING_MANIFEST.csv", result)
        self.assertFalse(result.exists())


if __name__ == "__main__":
    unittest.main()
