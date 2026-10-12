"""Verify selected public assets without downloading data or fitting models."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
FOLDERS = tuple(f"{n}_{name}" for n, name in enumerate(
    ("admin", "data", "code", "results", "figures", "manuscript", "release", "report")
))
REPORT = "7_report/scientific_narrative_reaudit_2026-10-12"
NAVIGATION = (
    "README.md", "0_admin/MASTER_INDEX.md", "0_admin/REPOSITORY_PUBLICATION_POLICY.md",
    *(f"{folder}/README.md" for folder in FOLDERS),
    "4_figures/Supplementary/README.md", "3_results/scientific_summary/README.md",
    f"{REPORT}/README.md", "4_figures/Fig1/README.md",
)
MANIFEST = "0_admin/PUBLIC_ASSET_MANIFEST.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_asset(root: Path, value: str) -> Path:
    if not value or "\\" in value or re.match(r"^[A-Za-z]:", value):
        raise ValueError(f"Invalid repository path: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != value:
        raise ValueError(f"Unsafe or noncanonical repository path: {value!r}")
    root = root.resolve()
    target = (root / value).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Path escapes repository: {value!r}")
    return target


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_manifest(root: Path, rows: list[dict]) -> list[str]:
    if not rows:
        return ["Empty public asset manifest"]
    errors, seen = [], set()
    for row in rows:
        try:
            value = row["path"]
            path = safe_asset(root, value)
            if value in seen:
                raise ValueError(f"Duplicate manifest path: {value}")
            seen.add(value)
            size = int(row["bytes"])
            expected = row["sha256"]
            if size < 0 or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError(f"Invalid size/hash metadata: {value}")
            if not path.is_file():
                raise ValueError(f"Missing file: {value}")
            if path.stat().st_size != size or sha256(path) != expected:
                raise ValueError(f"Size/hash mismatch: {value}")
        except (ValueError, KeyError, OSError) as exc:
            errors.append(str(exc))
    return errors


def markdown_targets(text: str) -> list[str]:
    # Selected navigation documents use ordinary inline links, not nested targets.
    return re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text)


def validate_links(root: Path, documents: tuple[str, ...]) -> tuple[int, list[str]]:
    count, errors = 0, []
    for value in documents:
        path = safe_asset(root, value)
        if not path.is_file():
            errors.append(f"Missing navigation document: {value}")
            continue
        for target in markdown_targets(path.read_text(encoding="utf-8-sig")):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            count += 1
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(root.resolve()) or not destination.exists():
                errors.append(f"Broken/unsafe local link: {value} -> {target}")
    return count, errors


def gate_boundary_errors(gate: dict) -> list[str]:
    errors = []
    if not str(gate.get("decision", "")).startswith("PASS_STAGE_M_"):
        errors.append("Current Stage M decision missing")
    flags = ("raw_download_started", "external_outcome_fitted", "expression_outcome_accessed")
    if any(gate.get("checks", {}).get(flag) is not False for flag in flags):
        errors.append("Stage M contains an unlocked or missing external-outcome flag")
    unlocks = gate.get("automatic_unlocks", {})
    required = ("raw_download", "count_reconstruction", "external_outcomes", "submission")
    if any(unlocks.get(flag) is not False for flag in required):
        errors.append("Stage M automatic-unlock boundary changed")
    return errors


def verify(root: Path) -> dict:
    root = root.resolve()
    errors = []
    for folder in FOLDERS:
        if not (root / folder / "README.md").is_file():
            errors.append(f"Required folder/README absent: {folder}")
    try:
        rows = read_csv(root / MANIFEST)
        errors.extend(validate_manifest(root, rows))
        required = set(NAVIGATION) | {"CITATION.cff", "3_results/current/StageM_Gate.json"}
        missing = required - {row.get("path") for row in rows}
        if missing:
            errors.append(f"Required manifest coverage absent: {sorted(missing)}")
    except (OSError, csv.Error) as exc:
        rows = []
        errors.append(f"Cannot read public manifest: {exc}")
    links, link_errors = validate_links(root, NAVIGATION)
    errors.extend(link_errors)
    try:
        copies = read_csv(root / "4_figures/Supplementary/SUPPLEMENTARY_SOURCE_COPY_MANIFEST.csv")
        expected_names = {f"Supplementary_Figure_S{n}_source_data.csv" for n in range(1, 11)}
        if len(copies) != 10 or {PurePosixPath(r["path"]).name for r in copies} != expected_names:
            errors.append("Supplementary source-copy coverage is not exactly S1-S10")
        for row in copies:
            published, original = safe_asset(root, row["path"]), safe_asset(root, row["source_path"])
            if sha256(published) != row["sha256"] or sha256(original) != row["sha256"]:
                errors.append(f"Supplementary source-copy identity failed: {row['path']}")
        a, b = root / "CITATION.cff", root / "0_admin/CITATION.cff"
        if a.read_bytes() != b.read_bytes() or 'doi: "10.5281/zenodo.22151739"' not in a.read_text(encoding="utf-8"):
            errors.append("Citation copies/retained DOI disagree")
        gate = json.loads((root / "3_results/current/StageM_Gate.json").read_text(encoding="utf-8-sig"))
        errors.extend(gate_boundary_errors(gate))
        qa = json.loads((root / REPORT / "FINAL_CANDIDATE_QA.json").read_text(encoding="utf-8-sig"))
        if qa.get("pass") != qa.get("checks") or qa.get("hold") != 0 or qa.get("author_candidate_review_required") is not True:
            errors.append("Saved scientific candidate qualification/approval boundary changed")
        protected = json.loads((root / REPORT / "PROTECTED_ASSET_INVENTORY.json").read_text(encoding="utf-8-sig"))
        if len(protected) != 45:
            errors.append("Protected scientific asset inventory is not 45 objects")
        errors.extend(validate_manifest(root, protected))
        candidate = read_csv(root / REPORT / "CANDIDATE_DELIVERABLE_MANIFEST.csv")
        errors.extend(validate_manifest(root, candidate))
    except (OSError, KeyError, ValueError, csv.Error) as exc:
        errors.append(f"Critical source/state validation failed: {exc}")
    return {"status": "PASS" if not errors else "FAIL", "manifest_assets": len(rows),
            "navigation_local_links": links, "required_folders": list(FOLDERS),
            "errors": errors, "scientific_pipeline_rerun": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = verify(args.root)
    output = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(output, end="")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(output, encoding="utf-8")
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
