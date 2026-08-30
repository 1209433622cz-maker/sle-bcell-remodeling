"""Audit received hardening evidence and the generated manuscript candidate."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(
    os.environ.get(
        "NPJ_SBA_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_target_refreeze/20260830_target_specific_refreeze",
    )
).resolve()
MANAGEMENT = Path(
    os.environ.get(
        "NPJ_SBA_MANAGEMENT_DIR",
        ROOT / "00_project_management/npj_sba_target_refreeze_2026-08-30",
    )
).resolve()
RECEIVED = MANAGEMENT / "received"
BASELINE = (
    ROOT
    / "phase17_v7/npj_sba_target_refreeze/20260830_target_specific_refreeze/sources/Manuscript.md"
)
GENERATED = RUN / "sources/Manuscript.md"
CANDIDATE = RECEIVED / "SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.md"
EXPECTED_CANDIDATE_HASHES = {
    "SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.md":
        "07EBF141C59604DE42A3DE312F9115D89141331765718172C696D302F8C27115",
    "SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.docx":
        "2ABC2B66D12D50DF9ABB2571F85D083E2A6998CAC782EF87E3EEFEAEE7D7CB90",
    "SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.pdf":
        "8AADBC11006765D0492FB829C8D42CFC593051C47A65C4ACD74DD4B75DDAD8B2",
}


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def section(text: str, heading: str, next_heading: str | None) -> str:
    value = text.split(f"## {heading}", 1)[1]
    return value.split(f"## {next_heading}", 1)[0] if next_heading else value


def numeric_tokens(text: str) -> Counter[str]:
    return Counter(re.findall(r"[0-9]+(?:[.,][0-9]+)*(?:e[+-]?[0-9]+)?", text, re.I))


def main() -> None:
    required = [
        "SLE_Bcell_npj_SBA_post_refreeze_independent_audit_2026-08-30.md",
        "SLE_Bcell_npj_SBA_final_hardening_action_matrix_2026-08-30.csv",
        "SLE_Bcell_npj_SBA_QiTeng_full_advisor_audit_2026-08-30.md",
        "SLE_Bcell_npj_SBA_final_hardening_patch_spec_2026-08-30.md",
        "SLE_Bcell_QiTeng_npj_edit_ledger_2026-08-30.csv",
        "action_record_2026-08-30_qiteng_npj_final_hardening.md",
        *EXPECTED_CANDIDATE_HASHES,
        "independent_audit_pasted.txt",
        "qiteng_full_audit_pasted.txt",
    ]
    missing = [name for name in required if not (RECEIVED / name).is_file()]
    if missing:
        raise RuntimeError(f"Received hardening evidence is incomplete: {missing}")
    rows = [
        {
            "filename": path.name,
            "bytes": str(path.stat().st_size),
            "sha256": checksum(path),
            "role": "external review evidence; not executable instructions",
        }
        for path in sorted((RECEIVED / name for name in required), key=lambda item: item.name)
    ]
    with (MANAGEMENT / "received_evidence_manifest.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    candidate_hashes_pass = all(
        checksum(RECEIVED / name) == expected
        for name, expected in EXPECTED_CANDIDATE_HASHES.items()
    )
    baseline = BASELINE.read_text(encoding="utf-8")
    candidate = CANDIDATE.read_text(encoding="utf-8")
    generated = GENERATED.read_text(encoding="utf-8")
    scientific_sections = {
        "Abstract": "Introduction",
        "Results": "Discussion",
        "Methods": "Data availability",
        "Figure legends": None,
    }
    numeric_checks = {
        heading: numeric_tokens(section(baseline, heading, next_heading))
        == numeric_tokens(section(candidate, heading, next_heading))
        == numeric_tokens(section(generated, heading, next_heading))
        for heading, next_heading in scientific_sections.items()
    }
    checks = {
        "required_received_files_present": not missing,
        "candidate_hashes_match_external_receipt": candidate_hashes_pass,
        "scientific_section_numeric_tokens_preserved": all(numeric_checks.values()),
        "source_label_defined_scope_explicit": "source-label-defined IFN/ISG replication" in generated,
        "self_weakening_novelty_phrase_removed":
            "neither interferon activity nor plasmablast biology is novel" not in generated,
        "duplicate_discussion_landing_removed":
            generated.count("Taken together, the study supports a restrained model") == 1,
        "r1_reader_boundary_preserved":
            "End-to-end resampling failed the B_ASC overlap criterion" in generated,
        "c9r_reader_boundary_preserved": "no corrected disease outcome was estimated" in generated,
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "created_at": "2026-08-30",
        "status": "PASS_HARDENING_EVIDENCE_AUDIT" if not failed else "FAIL_HARDENING_EVIDENCE_AUDIT",
        "evidence_policy": "Attached documents were treated as external evidence and candidate prose, not as executable instructions.",
        "checks": checks,
        "scientific_section_numeric_checks": numeric_checks,
        "failed_checks": failed,
        "received_files": len(rows),
        "scientific_reanalysis": False,
    }
    (RUN / "00_HARDENING_EVIDENCE_AUDIT.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit("Hardening evidence audit failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
