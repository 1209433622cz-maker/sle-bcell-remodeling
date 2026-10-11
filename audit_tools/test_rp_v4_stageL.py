import argparse
import tempfile
import unittest
from pathlib import Path

from audit_tools.rp_v4_stageL_01_external_gate import (
    cross_assay_rows,
    patient_rows,
    sample_rows,
    stage_k_manifest,
)


WORKSPACE = Path(__file__).resolve().parents[1]
STAGE_K = WORKSPACE / "phase17_v7/rp_v4_redesign/_software_tests/20261011_stageK_external_candidate/SLE_StageK"
GSE262846 = WORKSPACE / "phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/source_metadata/GSE262846_family.xml.tgz"
GSE263716 = WORKSPACE / "phase17_v7/rp_v4_redesign/_software_tests/20261011_stageL_metadata/source_metadata/GSE263716_family.xml.tgz"


class StageLTests(unittest.TestCase):
    def test_stage_k_manifest(self):
        rows, passed = stage_k_manifest(STAGE_K)
        self.assertTrue(passed)
        self.assertEqual(len(rows), 18)

    def test_rna_identity_and_pairing(self):
        samples, metadata = sample_rows(GSE262846, "RNA")
        patients = patient_rows(samples)
        paired_sle = [row for row in patients if row["disease"] == "SLE" and row["paired_rN_T1T2"]]
        self.assertEqual(len(samples), 88)
        self.assertEqual(len(patients), 45)
        self.assertEqual(sum(row["paired_rN_T1T2"] for row in patients), 43)
        self.assertEqual(len(paired_sle), 26)
        self.assertEqual(sum(row["activity_class"] == "active" for row in paired_sle), 12)
        self.assertEqual(sum(row["activity_class"] == "inactive" for row in paired_sle), 14)
        self.assertEqual(sum(not row["title_contains_patient_id"] for row in samples), 1)
        self.assertEqual(metadata["pubmed_id"], "")

    def test_atac_overlap_and_visit_boundary(self):
        rna_samples, _ = sample_rows(GSE262846, "RNA")
        atac_samples, _ = sample_rows(GSE263716, "ATAC")
        cross = cross_assay_rows(patient_rows(rna_samples), patient_rows(atac_samples))
        overlap = [row for row in cross if row["in_rna"] and row["in_atac"]]
        discordant = [row for row in overlap if not row["sledai_exact_match"]]
        self.assertEqual(len(atac_samples), 62)
        self.assertEqual(len(overlap), 36)
        self.assertEqual({row["patient_id"] for row in discordant}, {"1655", "3651"})
        self.assertTrue(all(not row["same_visit_supported"] for row in discordant))

    def test_patient_rows_reject_internal_metadata_conflict(self):
        rows = [
            {"patient_id": "1", "disease": "SLE", "sledai": 6.0, "activity_class": "active", "sex": "F", "race": "AA", "batch": "2", "cell_type": "rN", "gsm": "A"},
            {"patient_id": "1", "disease": "SLE", "sledai": 2.0, "activity_class": "inactive", "sex": "F", "race": "AA", "batch": "2", "cell_type": "T1T2", "gsm": "B"},
        ]
        with self.assertRaises(ValueError):
            patient_rows(rows)


if __name__ == "__main__":
    unittest.main()
