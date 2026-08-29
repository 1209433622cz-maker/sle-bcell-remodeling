"""Regression checks for the journal-neutral current submission package."""

import csv
import hashlib
from pathlib import Path
import tempfile
import unittest

from phase17_postc9_22_build_journal_neutral_cover_letter import validate_source
from phase17_postc9_23_build_current_submission_package import (
    C9R_HOLD,
    R1_HOLD,
    archive_entries,
    metadata,
    safe_relative,
    verify_manifest,
)


class CurrentSubmissionPackageTests(unittest.TestCase):
    def test_inventory_has_five_main_and_ten_supplementary_figures(self):
        targets = set(archive_entries().values())
        self.assertEqual(sum(path.startswith("03_Main_Figures/") for path in targets), 5)
        self.assertEqual(sum(path.startswith("04_Supplementary_Figures/") for path in targets), 10)

    def test_metadata_cannot_imply_selection_or_submission(self):
        value = metadata("a" * 40)
        self.assertIsNone(value["selected_target"])
        for key in (
            "jcr_q1_verified",
            "institutional_apc_coverage_verified",
            "exact_package_author_approved",
            "submission_authorized",
            "apc_commitment_authorized",
            "corrected_external_outcome_unlock_authorized",
        ):
            self.assertFalse(value[key])
        self.assertEqual(value["R1_decision"], R1_HOLD)
        self.assertEqual(value["C9R_decision"], C9R_HOLD)

    def test_cover_source_rejects_stale_journal_or_doi(self):
        valid = (
            "Disease-blind single-cell reconstruction distinguishes unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus "
            "10.5281/zenodo.22151739 permanent R1 HOLD C9R HOLD no corrected external disease outcome was estimated "
            "five vector main figures ten supplementary figures not under consideration by another journal"
        )
        validate_source(valid)
        for stale in (" Genome Medicine", " 10.5281/zenodo.22086892", " matching revised archive remains required"):
            with self.assertRaises(ValueError):
                validate_source(valid + stale)

    def test_safe_relative_rejects_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for value in ("../outside", "C:/outside", "/outside"):
                with self.assertRaises(ValueError):
                    safe_relative(root, value)

    def test_manifest_tamper_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            integrity = root / "07_Integrity"
            integrity.mkdir()
            data = root / "file.txt"
            data.write_bytes(b"original")
            row = {
                "relative_path": "file.txt",
                "bytes": str(data.stat().st_size),
                "sha256": hashlib.sha256(data.read_bytes()).hexdigest().upper(),
            }
            with (integrity / "FILE_MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=row)
                writer.writeheader()
                writer.writerow(row)
            self.assertEqual(verify_manifest(root), 1)
            data.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                verify_manifest(root)


if __name__ == "__main__":
    unittest.main()
