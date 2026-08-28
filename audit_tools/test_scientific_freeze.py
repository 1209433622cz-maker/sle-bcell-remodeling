"""Regression checks for permanent HOLD and exact scientific text boundaries."""

import copy
from pathlib import Path
import tempfile
import unittest

from phase17_postc9_16_verify_scientific_freeze import (
    C9R_HOLD, R1_HOLD, SECTIONS, digest, require_confirmation,
    require_holds, safe_path, scientific_hashes, verify_manifest,
)


class ScientificFreezeTests(unittest.TestCase):
    def confirmation(self):
        return {
            "status": "AUTHOR_CONFIRMED_SCIENTIFIC_BASELINE",
            "record_type": "USER_MESSAGE_REPORTING_AUTHOR_CONFIRMATION",
            "authors": ["Zhi Chen", "Teng Qi"],
            **{key: True for key in ("scientific_body_confirmed", "author_declarations_confirmed",
                                     "ethics_statement_confirmed", "R1_never_rescue_pass", "C9R_hold_retained")},
            **{key: False for key in ("independently_collected_signatures", "submission_authorized",
                                      "apc_commitment_authorized", "corrected_external_outcome_unlock_authorized")},
        }

    def holds(self):
        return ({"status": "PASS_TECHNICAL_AUDIT", "r1_decision": R1_HOLD,
                 "checks": {"formal_hold_retained": True}},
                {"decision": C9R_HOLD, "outcome_unlock_authorized": False,
                 "reference_model": {"elastic_calibration_eligible": False,
                                     "centroid_calibration_eligible": True}})

    def manuscript(self):
        return "# Title\n\n" + "\n\n".join("## " + name + "\n\nEffect 0.947." for name in SECTIONS)

    def test_confirmation_does_not_invent_signatures_or_submission(self):
        valid = self.confirmation()
        require_confirmation(valid)
        for key in ("independently_collected_signatures", "submission_authorized",
                    "corrected_external_outcome_unlock_authorized", "apc_commitment_authorized"):
            with self.assertRaises(ValueError):
                require_confirmation({**valid, key: True})

    def test_hold_confirmation_cannot_be_omitted(self):
        for key in ("R1_never_rescue_pass", "C9R_hold_retained"):
            with self.assertRaises(ValueError):
                require_confirmation({**self.confirmation(), key: False})

    def test_technical_pass_does_not_override_scientific_hold(self):
        require_holds(*self.holds())

    def test_rescue_pass_and_outcome_unlock_are_rejected(self):
        r1, c9r = self.holds()
        with self.assertRaises(ValueError):
            require_holds({**r1, "r1_decision": "PASS"}, c9r)
        for changed in ({**c9r, "decision": "PASS"}, {**c9r, "outcome_unlock_authorized": True}):
            with self.assertRaises(ValueError):
                require_holds(r1, changed)
        changed = copy.deepcopy(c9r)
        changed["reference_model"]["elastic_calibration_eligible"] = True
        with self.assertRaises(ValueError):
            require_holds(r1, changed)

    def test_administrative_doi_changes_do_not_change_scientific_hashes(self):
        text = self.manuscript()
        self.assertEqual(scientific_hashes(text + "\n\n## Declarations\n\nDOI old"),
                         scientific_hashes(text + "\n\n## Declarations\n\nDOI new"))

    def test_changed_claim_or_title_changes_scientific_hash(self):
        text = self.manuscript()
        for changed in (text.replace("0.947", "1.100", 1), text.replace("# Title", "# Changed title", 1),
                        text.replace("Effect 0.947.", "Causal effect 0.947.", 1)):
            self.assertNotEqual(scientific_hashes(text), scientific_hashes(changed))

    def test_missing_section_fails(self):
        with self.assertRaises(ValueError):
            scientific_hashes("# Title\n\n## Abstract\n\nOnly an abstract")

    def test_manifest_tamper_and_duplicate_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "data.txt").write_bytes(b"frozen")
            rows = [{"path": "data.txt", "bytes": 6, "sha256": digest(b"frozen")}]
            self.assertEqual(verify_manifest(root, rows), 1)
            with self.assertRaises(ValueError):
                verify_manifest(root, rows + rows)
            (root / "data.txt").write_bytes(b"edited")
            with self.assertRaises(ValueError):
                verify_manifest(root, rows)

    def test_path_escape_fails(self):
        for value in ("../secret", "C:/secret", "/secret", "a\\b"):
            with self.assertRaises(ValueError):
                safe_path(Path.cwd(), value)


if __name__ == "__main__":
    unittest.main()
