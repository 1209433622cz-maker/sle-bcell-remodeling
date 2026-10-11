from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from audit_tools.rp_v4_stageI_postrun_freeze import freeze, sha256_file, validate


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile"
AUTHORIZATION = CANONICAL / "00_STAGE_I_AUTHOR_GO.json"


class StageIPostrunFreezeTests(unittest.TestCase):
    def copy_two_file_output(self, root: Path) -> Path:
        output = root / "stageI"
        output.mkdir()
        for name in ["01_SINGLE_REAL_DELTA_PROFILE_RESULT.json", "02_SINGLE_REAL_DELTA_PROFILE_RECEIPT.json"]:
            shutil.copy2(CANONICAL / name, output / name)
        return output

    def test_canonical_output_passes_without_refit(self):
        audit = validate(CANONICAL, AUTHORIZATION)
        self.assertEqual(audit["interval_class"], "positive")
        self.assertFalse(audit["refit_performed"])
        self.assertEqual(audit["checks_passed"], audit["checks_total"])

    def test_freeze_adds_authorization_gate_review_and_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.copy_two_file_output(Path(temp))
            gate = freeze(output, AUTHORIZATION)
            self.assertTrue(gate["decision"].startswith("PASS_STAGE_I_WRITE_ONCE_EXECUTION"))
            manifest = (output / "06_INTEGRITY_MANIFEST.csv").read_text(encoding="utf-8")
            self.assertEqual(manifest.count("\n"), 7)
            self.assertEqual(sha256_file(output / "00_STAGE_I_AUTHOR_GO.json"), sha256_file(AUTHORIZATION))

    def test_result_tamper_is_rejected_by_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.copy_two_file_output(Path(temp))
            result_path = output / "01_SINGLE_REAL_DELTA_PROFILE_RESULT.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["point_estimate"] += 0.01
            result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(output, AUTHORIZATION)

    def test_authorization_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = self.copy_two_file_output(root)
            authorization = root / "authorization.json"
            value = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
            value["approve_write_once_result_and_no_preview"] = False
            authorization.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(output, authorization)

    def test_freeze_refuses_noncanonical_extra_file(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.copy_two_file_output(Path(temp))
            (output / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                freeze(output, AUTHORIZATION)


if __name__ == "__main__":
    unittest.main()
