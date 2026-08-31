"""Regression tests for the reference-terminology and S6 scientific refreeze."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_reference_terminology_lock/"
    "20260901_reference_terminology_s6_refreeze"
)
MANUSCRIPT = RUN / "sources/Manuscript_reference_terminology_s6_refreeze.md"
SUPPLEMENT = RUN / "sources/Supplementary_Information_reference_terminology_s6_refreeze.md"
S6_SOURCE = RUN / "figures/source_data/Supplementary_Figure_S6_source_data.csv"
S6_SOURCE_SHA256 = "A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class ReferenceTerminologyS6RefreezeTests(unittest.TestCase):
    def test_final_lock_status(self) -> None:
        status = json.loads((RUN / "04_FINAL_REFERENCE_TERMINOLOGY_S6_STATUS.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "REFERENCE_TERMINOLOGY_AND_S6_SCIENTIFIC_REFREEZE_LOCKED")
        self.assertTrue(all(status["checks"].values()))
        self.assertFalse(status["scientific_estimates_changed"])
        self.assertFalse(status["source_data_changed"])

    def test_reference_sequence(self) -> None:
        text = MANUSCRIPT.read_text(encoding="utf-8")
        body, tail = text.split("## References\n", 1)
        references = tail.split("## Figure legends\n", 1)[0]
        numbers = [int(value) for value in re.findall(r"(?m)^(\d+)\. ", references)]
        self.assertEqual(numbers, list(range(1, 34)))
        cited_values: set[int] = set()
        for match in re.findall(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
            for item in match.split(","):
                item = item.strip()
                if "-" in item:
                    start, end = [int(value.strip()) for value in item.split("-", 1)]
                    cited_values.update(range(start, end + 1))
                else:
                    cited_values.add(int(item))
        cited = sorted(cited_values)
        self.assertEqual(cited, list(range(1, 34)))
        self.assertIn("From reads to genes to pathways", references)
        self.assertIn("The Molecular Signatures Database (MSigDB) hallmark gene set collection", references)

    def test_evidence_terminology(self) -> None:
        manuscript = MANUSCRIPT.read_text(encoding="utf-8")
        supplement = SUPPLEMENT.read_text(encoding="utf-8")
        self.assertIn("biological-unit-aware inference", manuscript)
        self.assertIn("internal replication estimate", manuscript)
        self.assertIn("independent SLE replication dataset", manuscript)
        self.assertIn("support an IFN-centred regulatory context", manuscript)
        self.assertIn("Project administration, Validation", manuscript)
        self.assertIn("prospective clinical validation", manuscript)
        self.assertIn("Discovery and internal replication", supplement)
        self.assertIn("GSE135779 replication and robustness diagnostics", supplement)
        self.assertNotIn("Independent-validation diagnostics", supplement)

    def test_s6_source_and_decision(self) -> None:
        self.assertEqual(sha256(S6_SOURCE), S6_SOURCE_SHA256)
        with (RUN / "SUPPLEMENTARY_FIGURE_REFERENCE_TERMINOLOGY_DECISION_MATRIX.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 10)
        self.assertEqual([row["figure"] for row in rows if row["decision"] != "KEEP"], ["S6"])
        self.assertEqual(rows[5]["decision"], "MODIFY_SOURCE_REDRAW")


if __name__ == "__main__":
    unittest.main()
