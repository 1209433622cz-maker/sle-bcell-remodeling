#!/usr/bin/env python3
"""Verify the Gate C8BR DOI set, including both 2026 SLE context studies."""

from __future__ import annotations

import json
from pathlib import Path

import phase17_c8r_02_verify_references as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BR" / "20260825_release_portability_preflight"
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
        (
            32,
            "10.1136/lupus-2026-002042",
            "promote differentiation of double negative 2 cells",
        ),
    ]
    base.main()

    renames = {
        "reference_verification_gateC8R.csv": "reference_verification_gateC8BR.csv",
        "crossref_raw_gateC8R.json": "crossref_raw_gateC8BR.json",
        "references_gateC8R_vancouver.md": "references_gateC8BR_vancouver.md",
        "reference_verification_gateC8R.md": "reference_verification_gateC8BR.md",
    }
    for old_name, new_name in renames.items():
        source = OUT_DIR / old_name
        target = OUT_DIR / new_name
        if target.exists():
            target.unlink()
        source.replace(target)

    report_path = OUT_DIR / "reference_verification_gateC8BR.md"
    report = report_path.read_text(encoding="utf-8")
    report = report.replace("Gate C8R", "Gate C8BR")
    report = report.replace("Verified: 20 August 2026", "Verified: 25 August 2026")
    report = report.replace("reference count after adding GEO and repository records: 30", "reference count: 32")
    report += (
        "\n## Current direct-context records\n\n"
        "- Sayadi et al.: PMID 42119160; DOI 10.1016/j.jaut.2026.103575. External biological context only; not independent replication of the frozen B_CONV program.\n"
        "- Faheem et al.: PMID 42373139; DOI 10.1136/lupus-2026-002042. Functional DN2/IFN context only; not evidence that fine-grained hard partitions are stable in the analysed public datasets.\n"
    )
    report_path.write_text(report, encoding="utf-8", newline="\n")

    rows = (OUT_DIR / "reference_verification_gateC8BR.csv").read_text(encoding="utf-8").splitlines()
    status = {
        "created_at": "2026-08-25",
        "decision": "PASS" if len(rows) == 29 and all(line.endswith(",PASS") for line in rows[1:]) else "HOLD",
        "doi_records": len(rows) - 1,
        "manuscript_references": 32,
        "context_references": [
            {"doi": "10.1016/j.jaut.2026.103575", "pmid": "42119160", "role": "context only"},
            {"doi": "10.1136/lupus-2026-002042", "pmid": "42373139", "role": "functional DN2/IFN context only"},
        ],
        "claim_boundary": "neither 2026 study is independent replication of the frozen B_CONV program",
    }
    (RUN_DIR / "01_GATE_C8BR_REFERENCE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))
    if status["decision"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
