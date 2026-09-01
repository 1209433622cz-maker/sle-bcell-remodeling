#!/usr/bin/env python3
"""Regression tests for the scientific-presentation semantic stop gate."""

from __future__ import annotations

import hashlib
import inspect
import json
import unittest
from pathlib import Path

import phase17_c8s_01_build_supplementary_figures as supplementary_figures


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_scientific_stop_gate/20260901_canonical_source_s4b_refreeze"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class ScientificStopGateTests(unittest.TestCase):
    def test_s4_title_override_is_backward_compatible(self) -> None:
        parameter = inspect.signature(supplementary_figures.build_s4).parameters["panel_b_title"]
        self.assertEqual(parameter.default, "Primary null is stable to covariance and cell policy")

    def test_final_status_is_locked(self) -> None:
        status = json.loads(
            (RUN / "04_FINAL_SCIENTIFIC_PRESENTATION_STOP_GATE_STATUS.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(status["status"], "SCIENTIFIC_PRESENTATION_STOP_GATE_LOCKED")
        self.assertTrue(all(status["checks"].values()))
        self.assertFalse(status["scientific_estimates_changed"])
        self.assertFalse(status["source_data_changed"])

    def test_historical_stop_gate_sources_match_the_recorded_hashes(self) -> None:
        status = json.loads(
            (RUN / "04_FINAL_SCIENTIFIC_PRESENTATION_STOP_GATE_STATUS.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            sha256(RUN / "sources/Manuscript_scientific_stop_gate.md"),
            status["canonical_sources"]["root_manuscript_sha256"],
        )
        self.assertEqual(
            sha256(RUN / "sources/Supplementary_Information_scientific_stop_gate.md"),
            status["canonical_sources"]["root_supplement_sha256"],
        )

    def test_s4_source_data_remains_frozen(self) -> None:
        source = RUN / "figures/source_data/Supplementary_Figure_S4_source_data.csv"
        self.assertEqual(
            sha256(source),
            "7BA2660E5A50ADCF28407BCC92A91C791576DD69A9A1ABA9618DEB045C3A4E19",
        )


if __name__ == "__main__":
    unittest.main()
