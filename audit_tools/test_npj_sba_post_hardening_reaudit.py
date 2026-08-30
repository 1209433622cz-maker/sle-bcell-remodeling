"""Regression tests for the npj SBA post-hardening text-freeze reaudit."""

import json
import os
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(
    os.environ.get(
        "NPJ_SBA_POST_HARDENING_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_post_hardening_reaudit/20260830_qiteng_text_freeze",
    )
).resolve()


class NpjSbaPostHardeningReauditTests(unittest.TestCase):
    def test_readme_describes_r1_hold_correctly(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("End-to-end resampling did not meet the frozen", readme)
        self.assertIn("B_ASC median Jaccard was 0.930, below 0.95", readme)
        self.assertNotIn("End-to-end resampling formally holds", readme)

    def test_readme_uses_the_exact_current_target_title(self):
        readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
        title = (
            "Disease-blind reconstruction distinguishes reproducible interferon remodeling "
            "from unstable B-cell state assignments in systemic lupus erythematosus"
        )
        self.assertIn(title, readme)

    def test_reaudit_passes_without_scientific_or_manuscript_change(self):
        status = json.loads((RUN / "00_POST_HARDENING_FULL_REAUDIT.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "PASS_NPJ_SBA_POST_HARDENING_REAUDIT_TEXT_FREEZE")
        self.assertFalse(status["scientific_reanalysis_performed"])
        self.assertFalse(status["manuscript_rewritten"])
        self.assertEqual(status["failed_checks"], [])

    def test_qiteng_gate_recommends_text_freeze(self):
        status = json.loads((RUN / "01_QITENG_Q1_TEXT_FREEZE_AUDIT.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "PASS_QITENG_Q1_TEXT_FREEZE")
        self.assertTrue(status["text_freeze_recommended"])
        self.assertFalse(status["broad_prose_rewrite_authorized"])
        self.assertEqual(status["evidence_tiers"]["process_level_ifn"], "E2_ROBUST_ASSOCIATION")
        self.assertEqual(status["evidence_tiers"]["causal_mechanism"], "NOT_ESTABLISHED")

    def test_visual_reaudit_covers_all_figures(self):
        status = json.loads((RUN / "02_FIGURE_VISUAL_REAUDIT.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "PASS_FIFTEEN_FIGURE_VISUAL_REAUDIT")
        self.assertTrue(status["all_15_figures_reviewed"])
        self.assertTrue(status["high_risk_figure5_reviewed"])
        self.assertTrue(status["high_risk_supplementary_s8_reviewed"])
        self.assertFalse(status["clipping_overlap_missing_labels"])
        self.assertEqual(len(status["figures"]), 15)

    def test_authorization_and_institutional_receipts_remain_pending(self):
        status = json.loads((RUN / "00_POST_HARDENING_FULL_REAUDIT.json").read_text(encoding="utf-8"))
        self.assertTrue(status["checks"]["exact_file_author_approval_pending"])
        self.assertTrue(status["checks"]["official_jcr_q1_receipt_pending"])
        self.assertTrue(status["checks"]["institutional_apc_receipt_pending"])
        self.assertTrue(status["checks"]["submission_not_authorized"])
        self.assertFalse(status["submission_authorized"])


if __name__ == "__main__":
    unittest.main()
