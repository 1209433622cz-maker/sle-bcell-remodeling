"""Verify the author-confirmed QiTeng R2 baseline without changing science."""

import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from phase17_postc9_14_audit_refined_manuscript import normalized, section


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "00_project_management/qiteng_r2_freeze_2026-08-29"
SECTIONS = ("Abstract", "Background", "Methods", "Results", "Discussion",
            "Conclusions", "List of abbreviations", "Figure legends")
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def safe_path(root, value):
    path = PurePosixPath(value)
    if not value or "\\" in value or ":" in value or path.is_absolute() or ".." in path.parts:
        raise ValueError("Unsafe evidence path")
    result = (root / value).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError("Evidence path escapes the workspace")
    return result


def scientific_hashes(text):
    title = re.search(r"(?m)^# ([^\n]+)$", text)
    if title is None:
        raise ValueError("Missing manuscript title")
    values = {"Title": title[1], **{name: section(text, name) for name in SECTIONS}}
    return {name: digest(normalized(value).encode("utf-8")) for name, value in values.items()}


def require_confirmation(record):
    if record["status"] != "AUTHOR_CONFIRMED_SCIENTIFIC_BASELINE":
        raise ValueError("Scientific baseline has not been confirmed")
    if record["authors"] != ["Zhi Chen", "Teng Qi"]:
        raise ValueError("Author identities differ from the confirmed scope")
    for key in ("scientific_body_confirmed", "author_declarations_confirmed",
                "ethics_statement_confirmed", "R1_never_rescue_pass", "C9R_hold_retained"):
        if record[key] is not True:
            raise ValueError("Missing author confirmation: " + key)
    for key in ("independently_collected_signatures", "submission_authorized",
                "apc_commitment_authorized", "corrected_external_outcome_unlock_authorized"):
        if record[key] is not False:
            raise ValueError("Confirmation exceeds the user-reported scope: " + key)
    if record["record_type"] != "USER_MESSAGE_REPORTING_AUTHOR_CONFIRMATION":
        raise ValueError("Unrecognized confirmation evidence type")


def require_holds(r1, c9r):
    if r1["r1_decision"] != R1_HOLD or r1["checks"]["formal_hold_retained"] is not True:
        raise ValueError("R1 HOLD was changed")
    if c9r["decision"] != C9R_HOLD or c9r["outcome_unlock_authorized"] is not False:
        raise ValueError("C9R HOLD or outcome boundary was changed")
    if c9r["reference_model"]["elastic_calibration_eligible"] is not False:
        raise ValueError("The primary mapper failure was changed")


def verify_manifest(root, rows):
    names = [row["path"] for row in rows]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate frozen evidence path")
    for row in rows:
        data = safe_path(root, row["path"]).read_bytes()
        if len(data) != int(row["bytes"]) or digest(data) != row["sha256"]:
            raise ValueError("Frozen evidence changed: " + row["path"])
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate-markdown", type=Path,
                        help="Also compare a future administrative update against the scientific sections")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "00_project_management") or output.suffix != ".json":
        raise ValueError("Audit receipt must stay in project management")
    record = json.loads((FREEZE / "author_freeze.json").read_text(encoding="utf-8-sig"))
    require_confirmation(record)
    evidence = safe_path(ROOT, record["confirmation_evidence"]["path"])
    if digest(evidence.read_bytes()) != record["confirmation_evidence"]["sha256"]:
        raise ValueError("Author confirmation evidence changed")
    manifest = FREEZE / "frozen_evidence_manifest.csv"
    if digest(manifest.read_bytes()) != record["evidence_manifest_sha256"]:
        raise ValueError("Frozen manifest changed")
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    count = verify_manifest(ROOT, rows)
    if count != 21:
        raise ValueError("Unexpected frozen evidence inventory")
    manuscript = safe_path(ROOT, record["baseline_markdown"])
    baseline_hashes = scientific_hashes(manuscript.read_text(encoding="utf-8-sig"))
    if baseline_hashes != record["scientific_section_sha256"]:
        raise ValueError("Scientific baseline sections changed")
    r1 = json.loads(safe_path(ROOT, record["R1_decision_path"]).read_text(encoding="utf-8-sig"))
    c9r = json.loads(safe_path(ROOT, record["C9R_decision_path"]).read_text(encoding="utf-8-sig"))
    require_holds(r1, c9r)
    candidate = None
    if args.candidate_markdown:
        data = args.candidate_markdown.read_bytes()
        if scientific_hashes(data.decode("utf-8-sig")) != baseline_hashes:
            raise ValueError("Candidate scientific text differs from the approved baseline")
        candidate = {"name": args.candidate_markdown.name, "sha256": digest(data)}
    receipt = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FREEZE_INTEGRITY_NOT_SCIENTIFIC_GATE_PASS",
        "author_confirmation_sha256": digest((FREEZE / "author_freeze.json").read_bytes()),
        "evidence_manifest_sha256": record["evidence_manifest_sha256"],
        "frozen_evidence_files": count, "scientific_sections": len(baseline_hashes),
        "R1_decision": r1["r1_decision"], "C9R_decision": c9r["decision"],
        "corrected_external_outcome_unlock_authorized": False,
        "candidate_administrative_update": candidate,
        "zenodo_publication": {
            "record_id": record.get("new_zenodo_record_id"),
            "doi": record.get("new_zenodo_doi"),
            "published": record.get("new_zenodo_published", False),
            "publicly_verified": record.get("new_zenodo_publication_verified", False),
            "old_record_deleted": record.get("old_zenodo_deleted", False),
        },
        "scope": "Integrity and user-confirmed scope only; no new scientific analysis, independent signatures, old-record deletion or journal submission",
        "submission_authorized": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
