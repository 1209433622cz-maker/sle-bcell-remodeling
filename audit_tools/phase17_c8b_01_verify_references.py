#!/usr/bin/env python3
"""Verify the Gate C8B DOI set, including the 2026 Sayadi SLE study."""

from __future__ import annotations

import json
from pathlib import Path

import phase17_c8r_02_verify_references as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8B" / "20260821_editorial_literature_preflight"
OUT_DIR = RUN_DIR / "references"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = RUN_DIR
    base.OUT_DIR = OUT_DIR
    base.REFERENCES = [
        *base.REFERENCES,
        (
            31,
            "10.1016/j.jaut.2026.103575",
            "persistent interferon signature",
        ),
    ]
    base.main()

    renames = {
        "reference_verification_gateC8R.csv": "reference_verification_gateC8B.csv",
        "crossref_raw_gateC8R.json": "crossref_raw_gateC8B.json",
        "references_gateC8R_vancouver.md": "references_gateC8B_vancouver.md",
        "reference_verification_gateC8R.md": "reference_verification_gateC8B.md",
    }
    for old_name, new_name in renames.items():
        source = OUT_DIR / old_name
        target = OUT_DIR / new_name
        if target.exists():
            target.unlink()
        source.replace(target)

    report_path = OUT_DIR / "reference_verification_gateC8B.md"
    report = report_path.read_text(encoding="utf-8")
    report = report.replace("Gate C8R", "Gate C8B")
    report = report.replace("Verified: 20 August 2026", "Verified: 21 August 2026")
    report = report.replace("reference count after adding GEO and repository records: 30", "reference count: 31")
    report += (
        "\n## New direct-context record\n\n"
        "- PMID: 42119160\n"
        "- DOI: 10.1016/j.jaut.2026.103575\n"
        "- Use boundary: external biological context only; not independent replication of the frozen B_CONV program.\n"
    )
    report_path.write_text(report, encoding="utf-8", newline="\n")

    rows = (OUT_DIR / "reference_verification_gateC8B.csv").read_text(encoding="utf-8").splitlines()
    status = {
        "created_at": "2026-08-21",
        "decision": "PASS" if len(rows) == 28 and all(line.endswith(",PASS") for line in rows[1:]) else "HOLD",
        "doi_records": len(rows) - 1,
        "manuscript_references": 31,
        "new_reference_doi": "10.1016/j.jaut.2026.103575",
        "new_reference_pmid": "42119160",
        "claim_boundary": "external biological context; not independent replication",
    }
    (RUN_DIR / "01_GATE_C8B_REFERENCE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))
    if status["decision"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
