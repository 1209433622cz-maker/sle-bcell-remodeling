import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from audit_tools.rp_v4_stageM_01_raw_pipeline_freeze import (
    EXPECTED_BASES,
    EXPECTED_SRA_MB,
    RUNINFO_SHA256,
    nfcore_samplesheet,
    paired_sle_design,
    reconcile_runs,
    run_simulation,
    sha256,
    verify_manifest,
)


WORKSPACE = Path(__file__).resolve().parents[1]
STAGE_L = WORKSPACE / "phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate"
RUNINFO = (
    WORKSPACE
    / "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/source_metadata/PRJNA1093470_RunInfo.csv"
)
STAGE_M = WORKSPACE / "phase17_v7/rp_v4_redesign/20261011_stageM_raw_pipeline_freeze"


class StageMTests(unittest.TestCase):
    def test_stage_l_manifest(self):
        rows, passed = verify_manifest(STAGE_L, "13_INTEGRITY_MANIFEST.csv")
        self.assertTrue(passed)
        self.assertEqual(len(rows), 12)

    def test_run_reconciliation_and_disease_blind_sheet(self):
        runs, libraries, totals = reconcile_runs(RUNINFO, STAGE_L / "02_GSE262846_SAMPLE_PATIENT_MAP.csv")
        self.assertEqual(sha256(RUNINFO), RUNINFO_SHA256)
        self.assertEqual(len(runs), 176)
        self.assertEqual(len(libraries), 88)
        self.assertEqual(totals["bases"], EXPECTED_BASES)
        self.assertEqual(totals["sra_size_mb"], EXPECTED_SRA_MB)
        self.assertTrue(totals["all_libraries_have_two_runs"])
        sheet = nfcore_samplesheet(runs)
        forbidden = {"patient_id", "disease", "sledai", "activity_class", "cell_type", "effect"}
        self.assertFalse(forbidden & set(sheet[0]))
        self.assertEqual(len(sheet), 176)
        self.assertEqual(len({row["sample"] for row in sheet}), 88)

    def test_design_geometry(self):
        x, records, geometry = paired_sle_design(STAGE_L / "02_GSE262846_SAMPLE_PATIENT_MAP.csv")
        self.assertEqual(x.shape, (26, 3))
        self.assertEqual(len(records), 26)
        self.assertEqual(geometry["n_active"], 12)
        self.assertEqual(geometry["n_inactive"], 14)
        self.assertEqual(geometry["rank"], 3)
        self.assertEqual(geometry["residual_df"], 23)
        self.assertEqual(
            geometry["batch_activity_cells"],
            {"active_batch2": 5, "active_batch3": 7, "inactive_batch2": 7, "inactive_batch3": 7},
        )

    def test_simulation_is_deterministic_and_passes(self):
        x, _, _ = paired_sle_design(STAGE_L / "02_GSE262846_SAMPLE_PATIENT_MAP.csv")
        rows_a, gate_a = run_simulation(x)
        rows_b, gate_b = run_simulation(x)
        self.assertEqual(rows_a, rows_b)
        self.assertEqual(gate_a, gate_b)
        self.assertTrue(gate_a["pass"])
        self.assertEqual(len(rows_a), 8)
        self.assertTrue(all(np.isfinite(row["mean_hc3_se"]) for row in rows_a))

    def test_runinfo_hash_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            altered = Path(temp) / "RunInfo.csv"
            altered.write_bytes(RUNINFO.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                reconcile_runs(altered, STAGE_L / "02_GSE262846_SAMPLE_PATIENT_MAP.csv")

    def test_storage_gate_excludes_wsl_virtual_capacity(self):
        runtime = json.loads((STAGE_M / "07_RUNTIME_STORAGE_PREFLIGHT.json").read_text(encoding="utf-8"))
        self.assertIn("host filesystem volumes only", runtime["storage_readiness_rule"])
        self.assertFalse(runtime["storage_ready"])
        self.assertLess(runtime["largest_host_volume_free_bytes"], runtime["minimum_scratch_bytes"])


if __name__ == "__main__":
    unittest.main()
