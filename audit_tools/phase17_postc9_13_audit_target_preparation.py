"""Read-only candidate audit for journal selection; writes only its audit receipt."""

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import re

from verify_review_bundle import archive_entries, sha256, verify_bundle


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_SHA = "D87F83BEBE281E748E54DF0736E34B38E1CB0FF83C746C934B43E730373BA150"


def section(text, name):
    match = re.search(r"(?m)^## " + re.escape(name) + r"\s*\n", text)
    if match is None:
        raise ValueError("Missing section: " + name)
    following = text[match.end():]
    return re.split(r"(?m)^## ", following, maxsplit=1)[0].strip()


def word_count(text):
    text = re.sub(r"(?m)^#{1,6}[^\n]*", "", text)
    text = re.sub(r"(?m)^\*\*[^*\n]+:\*\*\s*", "", text)
    return len(text.replace("*", "").replace("`", "").split())


def calibration_summary(rows):
    results = []
    for mapper in sorted({row["mapper"] for row in rows}):
        subset = [row for row in rows if row["mapper"] == mapper]
        for row in subset:
            values = [float(row[key]) for key in ("coverage", "B_CONV_precision", "B_ASC_precision")]
            if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values):
                raise ValueError("Invalid frozen calibration metric")
            eligible = values[0] >= .80 and values[1] >= .90 and values[2] >= .90
            if row["eligible"] not in {"True", "False"} or eligible != (row["eligible"] == "True"):
                raise ValueError("Recorded calibration eligibility differs from the frozen rule")
        selected = [row for row in subset if row["selected"] == "True"]
        if len(selected) != 1:
            raise ValueError("Expected one diagnostic selected candidate per mapper")
        row = selected[0]
        results.append({
            "mapper": mapper, "candidates": len(subset),
            "eligible_candidates": sum(item["eligible"] == "True" for item in subset),
            "selected_threshold": float(row["threshold"]),
            "selected_coverage": float(row["coverage"]),
            "selected_B_CONV_precision": float(row["B_CONV_precision"]),
            "selected_B_ASC_precision": float(row["B_ASC_precision"]),
            "selected_eligible": row["eligible"] == "True",
            "diagnostic_fallback_only": row["diagnostic_fallback_only"] == "True",
        })
    if {row["mapper"] for row in results} != {"elastic_net", "nearest_centroid"}:
        raise ValueError("Unexpected mapper set")
    return results


def file_record(path):
    content = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(content), "sha256": sha256(content)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "00_project_management") or output.suffix != ".json":
        raise ValueError("Write the receipt inside project management, not manuscript or package paths")
    bundle = ROOT / "04_submission/corrected_candidate"
    archive = bundle.with_suffix(".zip")
    if sha256(archive.read_bytes()) != CANDIDATE_SHA:
        raise ValueError("The pinned corrected candidate changed")
    verification = verify_bundle(bundle)
    entries = archive_entries(archive.read_bytes())
    for name, data in entries.items():
        if (bundle / name).read_bytes() != data:
            raise ValueError("ZIP and expanded candidate differ: " + name)
    with (bundle / "SOURCE_PROVENANCE.csv").open(encoding="utf-8-sig", newline="") as handle:
        provenance = list(csv.DictReader(handle))
    for row in provenance:
        path = (ROOT / row["source_path"]).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Source provenance escapes the workspace")
        content = path.read_bytes()
        if len(content) != int(row["bytes"]) or sha256(content) != row["sha256"]:
            raise ValueError("Current source drift: " + row["source_path"])
    manuscript = (ROOT / "01_manuscript/Manuscript.md").read_text(encoding="utf-8-sig")
    draft = (ROOT / "00_project_management/author_confirmation_2026-08-28/Journal_Format_Draft.md").read_text(encoding="utf-8-sig")
    c9 = ROOT / "phase17_v7/gateC9R/20260828_normalization_correction"
    with (c9 / "17_FILE_INTEGRITY_MANIFEST.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = {row["filename"]: row for row in csv.DictReader(handle)}
    checked = []
    for name in ("07_MAPPER_CONFIDENCE_CALIBRATION.csv", "15_GATE_C9A_PREFREEZE_DECISION.json"):
        record = file_record(c9 / name)
        if record["bytes"] != int(manifest[name]["size_bytes"]) or record["sha256"] != manifest[name]["sha256"]:
            raise ValueError("Frozen calibration artifact changed: " + name)
        checked.append(record)
    with (c9 / "07_MAPPER_CONFIDENCE_CALIBRATION.csv").open(encoding="utf-8-sig", newline="") as handle:
        calibration = calibration_summary(list(csv.DictReader(handle)))
    gate = json.loads((c9 / "15_GATE_C9A_PREFREEZE_DECISION.json").read_text(encoding="utf-8"))
    if gate["decision"] != "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED" or gate["outcome_unlock_authorized"] is not False:
        raise ValueError("Frozen C9R boundary changed")
    receipt = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_UNCHANGED_CANDIDATE_TARGET_PREPARATION_AUDIT",
        "candidate": file_record(archive), "verification": verification,
        "source_provenance_rows_unchanged": len(provenance),
        "current_manuscript_words": {
            "Title": len(manuscript.splitlines()[0].removeprefix("# ").split()),
            **{name: word_count(section(manuscript, name)) for name in ("Abstract", "Background", "Methods", "Results", "Discussion")},
        },
        "unapplied_format_draft_words": {
            name: word_count(section(draft, name)) for name in ("Candidate Title", "Candidate Abstract")
        },
        "word_count_method": "Whitespace tokens, excluding Markdown headings and leading bold structured-abstract labels; hyphenated tokens count once. This is not the journal portal word counter.",
        "calibration_source_files": checked,
        "calibration_candidates": calibration,
        "s10_decision": "RETAIN_CURRENT_FIGURE; two-axis frontier alone omits B_CONV precision and the separate primary-mapper requirement",
        "new_numerical_analysis": False, "new_document_or_figure_render": False,
        "target_journal": None, "q1_verified": False,
        "submission_authorized": False,
        "scope": "Existing bytes, manuscript length and frozen calibration-table interpretation, not independent scientific review or JCR evidence verification",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
