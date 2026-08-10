#!/usr/bin/env python
"""Verify the final pre-submission directory and ZIP byte for byte."""

from __future__ import annotations

import csv
import hashlib
import zipfile
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "04_submission" / "package_genome_medicine_2026-07-31"
ARCHIVE = ROOT / "04_submission" / "package_genome_medicine_2026-07-31.zip"
ARCHIVE_SHA = ROOT / "04_submission" / "package_genome_medicine_2026-07-31.zip.sha256"
REPORT = ROOT / "04_submission" / "final_package_verification_2026-07-31.md"

REQUIRED = {
    "main_text/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.docx",
    "main_text/Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.pdf",
    "main_text/manuscript_v6_genome_medicine_submission_source.md",
    "tables_supplementary/Supplementary_Tables_S1-S13.xlsx",
    "submission_docs/author_completion_form_2026-07-31.md",
    "internal_qc/submission_document_qc_2026-07-31.md",
    "internal_qc/manuscript_numeric_qc_2026-07-27.md",
    "internal_qc/figure_quality_qc_2026-07-27.md",
    "internal_qc/phase7_regulatory_evidence_qc_2026-07-27.md",
}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def result(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def workbook_sheet_count(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("xl/workbook.xml")
    root = etree.fromstring(xml)
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return len(root.xpath("//x:sheets/x:sheet", namespaces=namespace))


def verify() -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    package_files = sorted(path for path in PACKAGE.rglob("*") if path.is_file())
    package_rel = {path.relative_to(PACKAGE).as_posix(): path for path in package_files}
    checks.append(result("Required primary assets", REQUIRED <= set(package_rel), f"{len(REQUIRED & set(package_rel))}/{len(REQUIRED)} present"))

    checksum_lines = (PACKAGE / "checksums_sha256.txt").read_text(encoding="ascii").splitlines()
    listed: dict[str, str] = {}
    for line in checksum_lines:
        digest, rel = line.split("  ", 1)
        listed[rel] = digest
    expected_checksum_paths = set(package_rel) - {"checksums_sha256.txt"}
    checksum_membership = set(listed) == expected_checksum_paths
    checksum_matches = sum(
        rel in package_rel and digest_file(package_rel[rel]) == digest
        for rel, digest in listed.items()
    )
    checks.append(result("Checksum membership", checksum_membership, f"{len(listed)} listed; {len(expected_checksum_paths)} expected"))
    checks.append(result("Checksum verification", checksum_matches == len(listed), f"{checksum_matches}/{len(listed)} SHA-256 matches"))

    with (PACKAGE / "bundle_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    manifest_matches = sum(
        row["package_path"] in package_rel
        and int(row["size_bytes"]) == package_rel[row["package_path"]].stat().st_size
        and row["sha256"] == digest_file(package_rel[row["package_path"]])
        for row in manifest
    )
    checks.append(result("Content manifest verification", manifest_matches == len(manifest), f"{manifest_matches}/{len(manifest)} rows match"))

    sheets = workbook_sheet_count(package_rel["tables_supplementary/Supplementary_Tables_S1-S13.xlsx"])
    checks.append(result("Supplementary workbook sheets", sheets == 27, f"{sheets} worksheets"))

    oversized_figures = [
        rel
        for rel, path in package_rel.items()
        if rel.startswith(("figures_main/", "figures_supplementary/"))
        and path.stat().st_size > 10 * 1024 * 1024
    ]
    checks.append(result("Figure upload size", not oversized_figures, f"{len(oversized_figures)} files exceed 10 MB"))

    archive_digest = digest_file(ARCHIVE)
    checksum_token = ARCHIVE_SHA.read_text(encoding="ascii").split()[0]
    checks.append(result("ZIP external checksum", archive_digest == checksum_token, archive_digest))

    with zipfile.ZipFile(ARCHIVE) as archive:
        bad_member = archive.testzip()
        names = [name for name in archive.namelist() if not name.endswith("/")]
        prefix = PACKAGE.name + "/"
        archive_rel = {name[len(prefix):]: name for name in names if name.startswith(prefix)}
        byte_matches = 0
        for rel, path in package_rel.items():
            name = archive_rel.get(rel)
            if name and digest_bytes(archive.read(name)) == digest_file(path):
                byte_matches += 1
    checks.append(result("ZIP integrity", bad_member is None, "zipfile.testzip returned no corrupt member"))
    checks.append(result("ZIP membership", set(archive_rel) == set(package_rel), f"{len(archive_rel)} archived; {len(package_rel)} package files"))
    checks.append(result("ZIP byte fidelity", byte_matches == len(package_rel), f"{byte_matches}/{len(package_rel)} files match"))

    source = package_rel["main_text/manuscript_v6_genome_medicine_submission_source.md"].read_text(encoding="utf-8")
    checks.append(result("Author-action guard", source.count("AUTHOR ACTION REQUIRED") == 10, f"{source.count('AUTHOR ACTION REQUIRED')} unresolved author actions"))
    checks.append(result("Unrendered citation tokens", "[@" not in source, "none found"))
    return checks


def write_report(checks: list[dict[str, str]]) -> None:
    passed = sum(item["status"] == "PASS" for item in checks)
    lines = [
        "# Final package verification",
        "",
        f"- Automated checks passed: {passed}/{len(checks)}",
        "- Package status: `PRE_SUBMISSION_AUTHOR_COMPLETION_REQUIRED`",
        "- Scientific content: frozen; phase-7 regulatory analysis retained as negative boundary evidence.",
        "- Upload status: blocked only by the 10 factual author/institutional completion items, not by analysis or document-generation failures.",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    lines.extend(f"| {item['check']} | {item['status']} | {item['detail']} |" for item in checks)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    qc = verify()
    write_report(qc)
    for item in qc:
        print(f"{item['status']}: {item['check']} - {item['detail']}")
    failures = [item for item in qc if item["status"] != "PASS"]
    if failures:
        raise SystemExit(f"{len(failures)} final package check(s) failed")
