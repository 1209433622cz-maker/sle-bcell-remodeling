#!/usr/bin/env python
"""Build the 2026-07-31 Genome Medicine pre-submission package.

The script starts from the verified 2026-07-27 package, overlays the current
submission manuscript and audit assets, then regenerates manifests and hashes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "04_submission" / "package_genome_medicine_2026-07-27"
TARGET = ROOT / "04_submission" / "package_genome_medicine_2026-07-31"
ARCHIVE = ROOT / "04_submission" / "package_genome_medicine_2026-07-31.zip"

OVERLAYS = {
    "01_manuscript/manuscript_v6_genome_medicine_submission_source.md": (
        "main_text/manuscript_v6_genome_medicine_submission_source.md",
        "primary_manuscript_source",
    ),
    "04_submission/outputs/manuscript_2026-07-31/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.docx": (
        "main_text/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.docx",
        "primary_manuscript_editable",
    ),
    "04_submission/outputs/manuscript_2026-07-31/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.pdf": (
        "main_text/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.pdf",
        "primary_manuscript_review_pdf",
    ),
    "04_submission/author_completion_form_2026-07-31.md": (
        "submission_docs/author_completion_form_2026-07-31.md",
        "author_completion",
    ),
    "04_submission/cover_letter_genome_medicine_v3_AUTHOR_COMPLETION_REQUIRED_2026-07-31.md": (
        "submission_docs/cover_letter_genome_medicine_v3_AUTHOR_COMPLETION_REQUIRED_2026-07-31.md",
        "cover_letter_source",
    ),
    "04_submission/outputs/cover_letter_2026-07-31/Genome_Medicine_Cover_Letter_v3_AUTHOR_COMPLETION_REQUIRED.docx": (
        "submission_docs/Genome_Medicine_Cover_Letter_v3_AUTHOR_COMPLETION_REQUIRED.docx",
        "cover_letter_editable",
    ),
    "04_submission/outputs/cover_letter_2026-07-31/Genome_Medicine_Cover_Letter_v3_AUTHOR_COMPLETION_REQUIRED.pdf": (
        "submission_docs/Genome_Medicine_Cover_Letter_v3_AUTHOR_COMPLETION_REQUIRED.pdf",
        "cover_letter_review_pdf",
    ),
    "04_submission/submission_package_checklist_v4_2026-07-31.md": (
        "submission_docs/submission_package_checklist_v4_2026-07-31.md",
        "submission_checklist",
    ),
    "04_submission/submission_readiness_and_next_stage_v5_2026-07-31.md": (
        "submission_docs/submission_readiness_and_next_stage_v5_2026-07-31.md",
        "submission_decision",
    ),
    "04_submission/outputs/manuscript_2026-07-31/submission_document_qc_2026-07-31.md": (
        "internal_qc/submission_document_qc_2026-07-31.md",
        "document_qc",
    ),
    "04_submission/outputs/manuscript_2026-07-31/submission_document_qc_2026-07-31.json": (
        "internal_qc/submission_document_qc_2026-07-31.json",
        "document_qc",
    ),
    "04_submission/advisor_full_project_audit_v4_2026-07-27.md": (
        "submission_docs/advisor_full_project_audit_v4_2026-07-27.md",
        "advisor_audit",
    ),
    "04_submission/phase7_regulatory_evidence_audit_2026-07-27.md": (
        "internal_qc/phase7_regulatory_evidence_audit_2026-07-27.md",
        "regulatory_boundary_audit",
    ),
    "04_submission/phase7_regulatory_evidence_qc_2026-07-27.md": (
        "internal_qc/phase7_regulatory_evidence_qc_2026-07-27.md",
        "regulatory_boundary_qc",
    ),
    "04_submission/phase7_regulatory_evidence_qc_2026-07-27.csv": (
        "internal_qc/phase7_regulatory_evidence_qc_2026-07-27.csv",
        "regulatory_boundary_qc",
    ),
    "02_analysis/RUNBOOK_phase7_regulatory_evidence.md": (
        "analysis_code/RUNBOOK_phase7_regulatory_evidence.md",
        "analysis_runbook",
    ),
}

for script_number in range(40, 50):
    matches = sorted((ROOT / "02_analysis" / "scripts").glob(f"{script_number}_*.py"))
    for match in matches:
        OVERLAYS[str(match.relative_to(ROOT)).replace("\\", "/")] = (
            f"analysis_code/scripts/{match.name}",
            "analysis_script",
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def role_for(path: Path, overlay_roles: dict[str, str]) -> str:
    rel = path.relative_to(TARGET).as_posix()
    if rel in overlay_roles:
        return overlay_roles[rel]
    top = rel.split("/", 1)[0]
    return {
        "analysis_code": "analysis_code",
        "figures_main": "main_figure",
        "figures_supplementary": "supplementary_figure",
        "internal_qc": "internal_qc",
        "main_text": "manuscript_support",
        "references": "reference_source",
        "submission_docs": "submission_document",
        "tables_supplementary": "supplementary_table",
    }.get(top, "package_metadata")


def write_readme(path: Path) -> None:
    lines = [
        "# Genome Medicine pre-submission package",
        "",
        "Prepared 31 July 2026 from frozen analysis outputs.",
        "",
        "## Primary files",
        "",
        "- `main_text/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.docx`: editable submission manuscript with continuous line numbers and page numbers.",
        "- `main_text/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.pdf`: 27-page author-review rendering.",
        "- `main_text/manuscript_v6_genome_medicine_submission_source.md`: reproducible manuscript source with Vancouver references.",
        "- `figures_main`: Figures 1-6 in PDF and PNG formats.",
        "- `figures_supplementary`: Supplementary Figures S1-S4 in PDF and PNG formats.",
        "- `tables_supplementary/Supplementary_Tables_S1-S13.xlsx`: machine-readable supplementary workbook.",
        "- `submission_docs/Genome_Medicine_Cover_Letter_v3_AUTHOR_COMPLETION_REQUIRED.docx`: editable one-page cover letter.",
        "",
        "## Submission status",
        "",
        "The scientific analysis, numerical claims, figures, references, manuscript structure, and rendered manuscript have passed the recorded QC checks. This package is not yet upload-ready because the manuscript contains 10 highlighted `AUTHOR ACTION REQUIRED` items covering authorship, affiliations, corresponding-author details, ethics confirmation, code deposition, competing interests, funding, contributions, acknowledgements, and AI-disclosure confirmation.",
        "",
        "Complete `submission_docs/author_completion_form_2026-07-31.md`, replace every highlighted action in the DOCX, and rerun the document and package QC before journal upload.",
        "",
        "## Internal-only material",
        "",
        "Files under `internal_qc` and most files under `analysis_code` document provenance and should not be uploaded unless requested. The phase-7 colocalization analysis is negative boundary evidence and is intentionally excluded from the manuscript's positive claims.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(replace_generated: bool = False) -> dict[str, object]:
    if not BASE.is_dir():
        raise FileNotFoundError(f"Base package not found: {BASE}")
    if TARGET.exists():
        marker = TARGET / "package_build_summary.json"
        safe_target = (
            TARGET.resolve().parent == (ROOT / "04_submission").resolve()
            and TARGET.name == "package_genome_medicine_2026-07-31"
            and marker.is_file()
            and '"status": "PRE_SUBMISSION_AUTHOR_COMPLETION_REQUIRED"'
            in marker.read_text(encoding="utf-8")
        )
        if not replace_generated or not safe_target:
            raise FileExistsError(f"Target already exists; refusing to overwrite: {TARGET}")
        shutil.rmtree(TARGET)
        for generated in (ARCHIVE, ARCHIVE.with_suffix(".zip.sha256")):
            if generated.exists():
                generated.unlink()
    missing = [source for source in OVERLAYS if not (ROOT / source).is_file()]
    if missing:
        raise FileNotFoundError("Missing overlay files:\n" + "\n".join(missing))

    shutil.copytree(BASE, TARGET)
    overlay_roles: dict[str, str] = {}
    for source_rel, (target_rel, role) in OVERLAYS.items():
        source = ROOT / source_rel
        destination = TARGET / target_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        overlay_roles[target_rel] = role

    for stale in ("bundle_manifest.csv", "bundle_manifest.md", "checksums_sha256.txt"):
        stale_path = TARGET / stale
        if stale_path.exists():
            stale_path.unlink()
    write_readme(TARGET / "README.md")

    content_files = sorted(path for path in TARGET.rglob("*") if path.is_file())
    rows = []
    for path in content_files:
        rel = path.relative_to(TARGET).as_posix()
        rows.append(
            {
                "package_path": rel,
                "role": role_for(path, overlay_roles),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    manifest_csv = TARGET / "bundle_manifest.csv"
    with manifest_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    total_bytes = sum(int(row["size_bytes"]) for row in rows)
    role_counts: dict[str, int] = {}
    for row in rows:
        role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1
    manifest_md = TARGET / "bundle_manifest.md"
    lines = [
        "# Genome Medicine package manifest",
        "",
        f"- Content files: {len(rows)}",
        f"- Content size: {total_bytes / (1024 * 1024):.2f} MB",
        "- Missing required overlays: 0",
        "",
        "## Role counts",
        "",
    ]
    lines.extend(f"- `{role}`: {count}" for role, count in sorted(role_counts.items()))
    lines.extend(
        [
            "",
            "## Integrity",
            "",
            "Every content file has a SHA-256 digest in `bundle_manifest.csv`; all package metadata files except `checksums_sha256.txt` are additionally covered by `checksums_sha256.txt`.",
        ]
    )
    manifest_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    static_summary = {
        "package": TARGET.name,
        "base_package": BASE.name,
        "overlay_files": len(OVERLAYS),
        "content_manifest_rows": len(rows),
        "status": "PRE_SUBMISSION_AUTHOR_COMPLETION_REQUIRED",
    }
    (TARGET / "package_build_summary.json").write_text(
        json.dumps(static_summary, indent=2), encoding="utf-8"
    )

    checksum_path = TARGET / "checksums_sha256.txt"
    checksum_lines = []
    for path in sorted(path for path in TARGET.rglob("*") if path.is_file()):
        if path == checksum_path:
            continue
        checksum_lines.append(f"{sha256(path)}  {path.relative_to(TARGET).as_posix()}")
    checksum_path.write_text("\n".join(checksum_lines) + "\n", encoding="ascii")

    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(path for path in TARGET.rglob("*") if path.is_file()):
            archive.write(path, arcname=f"{TARGET.name}/{path.relative_to(TARGET).as_posix()}")

    archive_digest = sha256(ARCHIVE)
    archive_checksum_path = ARCHIVE.with_suffix(".zip.sha256")
    archive_checksum_path.write_text(
        f"{archive_digest}  {ARCHIVE.name}\n", encoding="ascii"
    )
    result = {
        **static_summary,
        "package": str(TARGET),
        "package_files": sum(1 for path in TARGET.rglob("*") if path.is_file()),
        "checksum_rows": len(checksum_lines),
        "package_bytes": sum(path.stat().st_size for path in TARGET.rglob("*") if path.is_file()),
        "archive": str(ARCHIVE),
        "archive_bytes": ARCHIVE.stat().st_size,
        "archive_sha256": archive_digest,
        "archive_checksum_file": str(archive_checksum_path),
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace-generated",
        action="store_true",
        help="Replace only a previously generated package carrying the expected safety marker.",
    )
    args = parser.parse_args()
    print(json.dumps(build(replace_generated=args.replace_generated), indent=2))
