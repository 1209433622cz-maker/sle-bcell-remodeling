#!/usr/bin/env python3
"""Build non-destructive, nested catalog views for the organized project folders."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-10-12"
INVENTORY = ROOT / "9_version" / "inventory" / f"WORKSPACE_FILE_INVENTORY_{DATE}.csv"
MASTER_CATALOG = ROOT / "9_version" / "inventory" / f"SUBFOLDER_CLASSIFICATION_{DATE}.csv"
STATUS_JSON = ROOT / "9_version" / "release_state" / f"SUBFOLDER_ORGANIZATION_STATUS_{DATE}.json"
TAXONOMY_MD = ROOT / "0_admin" / f"SUBFOLDER_TAXONOMY_{DATE}.md"
HASH_MANIFEST = ROOT / "9_version" / "hashes_integrity" / f"SUBFOLDER_ORGANIZATION_SHA256_{DATE}.csv"


TAXONOMY = {
    "0_admin": {
        "citation_licensing": "Citation metadata, licenses, ORCID records and reuse terms.",
        "governance_reproducibility": "Governance, frozen contracts, reproducibility rules and approval records.",
        "status_navigation": "Project indexes, README files, current-state summaries and planning records.",
        "other_admin": "Administrative records not covered by the named groups.",
    },
    "1_data": {
        "raw_inputs": "Raw or accession-level inputs retained locally or referenced by manifests.",
        "processed_matrices": "Processed matrices and serialized analysis objects.",
        "external_cohorts": "External cohort inputs and cohort-specific metadata.",
        "metadata_design": "Sample metadata, donor maps, run tables and design matrices.",
        "manifests_checksums": "File manifests, checksums, download receipts and accounting tables.",
        "derived_tables": "Derived data tables that are not final result objects.",
    },
    "2_code": {
        "current_stageM": "Current RP v4 Stage M code snapshot and execution entry points.",
        "tests": "Unit, regression, adversarial and integrity tests.",
        "windows_runners": "PowerShell and Windows execution wrappers.",
        "environments": "Environment specifications, dependency locks and workflow configuration.",
        "audit_quality_control": "Audit, verification, packaging and quality-control utilities.",
        "analysis_workflows": "Primary scientific analysis and figure-generation code.",
        "legacy_support": "Historical or supporting code retained for provenance.",
    },
    "3_results": {
        "rp_v4": "RP v4 staged redesign outputs and adjudication records.",
        "rp_v3": "RP v3 redesign outputs retained for evidence reconciliation.",
        "simulations": "Synthetic simulation, truth and interval-evaluation outputs.",
        "identity_reconstruction": "Identity, clustering, mapping and reconstruction results.",
        "composition": "Composition and abundance inference outputs.",
        "transcription": "Pseudobulk, program-score and gene-level transcriptional outputs.",
        "external_validation": "External cohort transfer, replication and calibration results.",
        "regulatory": "Regulator, pathway and depletion-sensitivity outputs.",
        "diagnostics_qc": "Diagnostic, preflight, QA and integrity outputs.",
        "other_historical_results": "Other retained result objects and historical evidence.",
    },
    "5_manuscript": {
        "current_scientific_text": "Current manuscript and supplement candidates.",
        "source_text_markdown": "Editable Markdown and source-text artifacts.",
        "supplementary_materials": "Supplementary information, tables and related source files.",
        "cover_letters": "Cover letters and journal-facing correspondence drafts.",
        "author_declarations": "Author metadata, declarations, contributions and approvals.",
        "render_layout_qa": "Rendered proofs and document-layout quality assurance.",
        "historical_manuscripts": "Superseded manuscript versions retained for provenance.",
    },
    "6_release": {
        "current_submission": "Current complete submission package and its package-level checks.",
        "submission_candidates": "Earlier journal-facing or submission candidate packages.",
        "github_zenodo": "GitHub, Zenodo, DOI and public-release records.",
        "journal_portal": "Journal portal forms, portal-ready files and upload records.",
        "integrity_manifests": "Release manifests, checksums and integrity receipts.",
        "historical_releases": "Historical release artifacts retained for provenance.",
    },
    "7_report": {
        "action_records": "Chronological action records for completed work rounds.",
        "advisor_reviews": "Advisor-level reviews, decisions and gate reports.",
        "method_audits": "Methodological, statistical and reproducibility audits.",
        "figure_audits": "Figure, panel, typography and visual-readability audits.",
        "release_audits": "Submission, release, portability and package audits.",
        "project_management": "Project summaries, matrices, plans and progress reports.",
        "other_reports": "Other retained reports and evidence records.",
    },
    "8_archive": {
        "cache_temporary": "Caches and temporary artifacts that may be regenerated.",
        "qa_recomputable": "Recomputable QA outputs and transient render products.",
        "duplicate_candidates": "Redundant copies identified for later reviewed cleanup.",
        "superseded_versions": "Superseded versions retained until an explicit deletion decision.",
        "large_local_archives": "Large local archives or downloads retained outside the release package.",
        "other_archive_candidates": "Other low-priority archive candidates.",
    },
    "8_reference": {
        "primary_literature": "Primary literature and supporting publications.",
        "bibliography": "Bibliographic databases, reference lists and citation exports.",
        "dataset_documentation": "Dataset descriptions, accessions and source documentation.",
        "methods_guidance": "Method, reporting and journal-format guidance.",
        "other_references": "Other retained reference material.",
    },
    "9_version": {
        "inventory": "Workspace-wide file inventories and classification tables.",
        "hashes_integrity": "Hash manifests, integrity checks and package verification records.",
        "git_history": "Git commit, branch and synchronization records.",
        "copy_provenance": "Copy-source maps and provenance relationships.",
        "release_state": "Machine-readable current-state and release-status records.",
    },
}


def has(text: str, *terms: str) -> bool:
    return any(term in text for term in terms)


def classify(bucket: str, path: str, extension: str, lifecycle: str, value_tier: str) -> str:
    p = path.lower().replace("\\", "/")
    name = Path(p).name
    ext = extension.lower()

    if bucket == "0_admin":
        if has(p, "license", "citation", "orcid", "reuse"):
            return "citation_licensing"
        if has(p, "reproduc", "govern", "contract", "ethic", "approval", "author_sign", "freeze"):
            return "governance_reproducibility"
        if has(name, "readme", "index", "status", "plan", "proposal", "matrix", "register"):
            return "status_navigation"
        return "other_admin"

    if bucket == "1_data":
        if has(p, "gse135779", "gse262846", "gse118254", "gse23307", "external", "sra", "runinfo"):
            return "external_cohorts"
        if has(p, "manifest", "checksum", "sha256", "download", "accounting", "inventory"):
            return "manifests_checksums"
        if has(p, "metadata", "meta_data", "sample", "donor", "design", "phenotype", "clinical"):
            return "metadata_design"
        if ext in {".h5ad", ".h5", ".hdf5", ".loom", ".npz", ".npy", ".rds", ".mtx"} or has(p, "processed", "normalized", "pseudobulk"):
            return "processed_matrices"
        if ext in {".fastq", ".fq", ".sra", ".bam", ".cram", ".tar", ".gz"} or has(p, "raw", "source_data"):
            return "raw_inputs"
        return "derived_tables"

    if bucket == "2_code":
        if "rp_v4_stagem" in p or "stage_m" in p:
            return "current_stageM"
        if has(p, "/test", "test_", "_test.", "regression", "adversarial"):
            return "tests"
        if ext == ".ps1" or has(p, "powershell", "windows_runner", "run_"):
            return "windows_runners"
        if has(p, "environment", "conda", "requirements", "docker", "nextflow", "workflow", "pyproject", "renv"):
            return "environments"
        if has(p, "audit", "verify", "validator", "validate", "preflight", "integrity", "package", "render", "check_"):
            return "audit_quality_control"
        if has(p, "02_analysis", "analysis", "figure", "plot", "model", "fit_", "score", "pseudobulk"):
            return "analysis_workflows"
        return "legacy_support"

    if bucket == "3_results":
        if has(p, "rp_v4", "stagef", "stageg", "stageh", "stagei", "stagej", "stagek", "stagel", "stagem"):
            return "rp_v4"
        if has(p, "rp_v3", "g2b", "wp1", "wp2", "wp3"):
            return "rp_v3"
        if has(p, "simulation", "synthetic", "truth", "oracle", "coverage", "type_i", "bias"):
            return "simulations"
        if has(p, "identity", "cluster", "mapping", "jaccard", "ari", "reconstruction", "representation"):
            return "identity_reconstruction"
        if has(p, "composition", "fraction", "abundance", "beta_binomial"):
            return "composition"
        if has(p, "external", "replication", "transfer", "calibration", "gse135779", "gse262846", "gse118254"):
            return "external_validation"
        if has(p, "regulat", "stat1", "stat2", "ulm", "camera", "fry", "m5911", "depletion", "pathway"):
            return "regulatory"
        if has(p, "pseudobulk", "transcript", "expression", "program", "deg", "gene_"):
            return "transcription"
        if has(p, "diagnostic", "preflight", "qc", "audit", "integrity", "validation", "check"):
            return "diagnostics_qc"
        return "other_historical_results"

    if bucket == "5_manuscript":
        if has(p, "supplement", "table_s", "figure_s", "source_data"):
            return "supplementary_materials"
        if has(p, "cover_letter", "cover letter", "editor_letter"):
            return "cover_letters"
        if has(p, "author", "contribution", "declaration", "competing", "funding", "ethics", "orcid", "affiliation"):
            return "author_declarations"
        if has(p, "render", "proof", "accessibility", "a11y", "layout", "wps", "libreoffice"):
            return "render_layout_qa"
        if ext == ".md" or has(p, "source", "markdown"):
            return "source_text_markdown"
        if has(p, "stagek", "current", "scientific_presentation_freeze", "qiteng") and ext in {".docx", ".pdf"}:
            return "current_scientific_text"
        return "historical_manuscripts"

    if bucket == "6_release":
        if has(p, "github", "zenodo", "doi", "release"):
            return "github_zenodo"
        if has(p, "portal", "submission_system", "upload"):
            return "journal_portal"
        if has(p, "manifest", "sha", "checksum", "integrity", "receipt"):
            return "integrity_manifests"
        if has(p, "submission", "package", "journal", "npj", "cover_letter"):
            return "submission_candidates"
        return "historical_releases"

    if bucket == "7_report":
        if has(p, "action_record", "工作记录", "行动记录"):
            return "action_records"
        if has(p, "advisor", "导师", "gate", "decision", "裁决"):
            return "advisor_reviews"
        if has(p, "figure", "panel", "typography", "readability", "artwork"):
            return "figure_audits"
        if has(p, "release", "submission", "zenodo", "github", "package", "portability"):
            return "release_audits"
        if has(p, "method", "statistic", "reproduc", "scientific", "claim", "traceability", "audit"):
            return "method_audits"
        if has(p, "project", "progress", "summary", "matrix", "plan", "roadmap", "management", "阶段"):
            return "project_management"
        return "other_reports"

    if bucket == "8_archive":
        if has(p, "cache", "__pycache__", ".pytest_cache", "temp", "tmp"):
            return "cache_temporary"
        if has(p, "render", "qa", "proof", "preview", "screenshot"):
            return "qa_recomputable"
        if value_tier == "P3" or "duplicate" in lifecycle or has(p, "copy", "复制"):
            return "duplicate_candidates"
        if has(p, "old", "legacy", "superseded", "obsolete", "backup", "archive"):
            return "superseded_versions"
        if ext in {".zip", ".7z", ".rar", ".tar", ".gz"}:
            return "large_local_archives"
        return "other_archive_candidates"

    if bucket == "8_reference":
        if ext in {".bib", ".ris", ".nbib"} or has(p, "bibliograph", "reference_list", "references."):
            return "bibliography"
        if has(p, "gse", "geo", "dataset", "accession", "runinfo", "sra"):
            return "dataset_documentation"
        if has(p, "method", "guideline", "nature", "npj", "reporting", "checklist"):
            return "methods_guidance"
        if ext == ".pdf" or has(p, "paper", "literature", "article"):
            return "primary_literature"
        return "other_references"

    if bucket == "9_version":
        if has(p, "inventory", "classification", "catalog"):
            return "inventory"
        if has(p, "hash", "sha", "integrity", "checksum"):
            return "hashes_integrity"
        if has(p, "git", "commit", "branch", "sync"):
            return "git_history"
        if has(p, "provenance", "copy_source", "source_map"):
            return "copy_provenance"
        return "release_state"

    raise ValueError(f"Unsupported bucket: {bucket}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    with INVENTORY.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    source_fields = list(rows[0])
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    master_rows: list[dict[str, str]] = []
    bucket_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    excluded_figures = 0

    for row in rows:
        bucket = row["organized_bucket"]
        if bucket == "4_figures":
            excluded_figures += 1
            continue
        if bucket not in TAXONOMY:
            raise ValueError(f"Inventory row has unsupported organized bucket: {bucket}")
        category = classify(
            bucket,
            row["relative_path"],
            row["extension"],
            row["lifecycle"],
            row["value_tier"],
        )
        if category not in TAXONOMY[bucket]:
            raise ValueError(f"Unknown category {bucket}/{category}")
        enriched = dict(row)
        enriched["subfolder_category"] = category
        enriched["catalog_path"] = f"{bucket}/{category}/FILE_CATALOG_{DATE}.csv"
        grouped[(bucket, category)].append(enriched)
        master_rows.append(enriched)
        bucket_counts[bucket] += 1
        category_counts[f"{bucket}/{category}"] += 1

    fields = source_fields + ["subfolder_category", "catalog_path"]
    write_csv(MASTER_CATALOG, master_rows, fields)

    taxonomy_lines = [
        "# Project subfolder taxonomy",
        "",
        f"Generated: {DATE}",
        "",
        "This is a non-destructive navigation layer over the frozen project workspace. Original analysis paths are not moved or renamed. Each baseline inventory row outside 4_figures is assigned to exactly one topic catalog. 4_figures retains its existing Fig1-Fig8 organization.",
        "",
    ]

    for bucket, categories in TAXONOMY.items():
        index_lines = [
            f"# {bucket} subfolder index",
            "",
            f"Generated: {DATE}",
            "",
            "These folders are catalog views. The source paths in each CSV remain the authoritative locations; no frozen source file was moved.",
            "",
            "| Subfolder | Files | Purpose |",
            "|---|---:|---|",
        ]
        taxonomy_lines.extend([f"## {bucket}", "", "| Subfolder | Files | Purpose |", "|---|---:|---|"])
        for category, description in categories.items():
            category_rows = grouped.get((bucket, category), [])
            category_dir = ROOT / bucket / category
            catalog_path = category_dir / f"FILE_CATALOG_{DATE}.csv"
            write_csv(catalog_path, category_rows, fields)
            total_bytes = sum(int(row["bytes"]) for row in category_rows)
            readme = (
                f"# {category.replace('_', ' ').title()}\n\n"
                f"{description}\n\n"
                f"- Catalog date: {DATE}\n"
                f"- Baseline files: {len(category_rows):,}\n"
                f"- Baseline bytes: {total_bytes:,}\n"
                f"- Source paths moved: 0\n"
                f"- File catalog: FILE_CATALOG_{DATE}.csv\n\n"
                "The CSV is the authoritative navigation view for this category. It records the original relative path, SHA-256, lifecycle, value tier and audit status.\n"
            )
            write_text(category_dir / "README.md", readme)
            rel = f"{category}/FILE_CATALOG_{DATE}.csv"
            index_lines.append(f"| [{category}]({rel}) | {len(category_rows):,} | {description} |")
            taxonomy_lines.append(f"| {category} | {len(category_rows):,} | {description} |")
        index_lines.extend(
            [
                "",
                f"Bucket total: **{bucket_counts[bucket]:,} baseline files**.",
                "",
                "See the workspace-wide classification in ../9_version/inventory/SUBFOLDER_CLASSIFICATION_2026-10-12.csv.",
            ]
        )
        write_text(ROOT / bucket / "SUBFOLDER_INDEX.md", "\n".join(index_lines))
        taxonomy_lines.append("")

    package_root = ROOT / "6_release" / "SLE_Bcell_Submission_Package_2026-10-12"
    package_rows: list[dict[str, str | int]] = []
    if package_root.exists():
        for path in sorted(p for p in package_root.rglob("*") if p.is_file()):
            package_rows.append(
                {
                    "relative_path": path.relative_to(package_root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    package_manifest = ROOT / "6_release" / "current_submission" / f"PACKAGE_CONTENTS_{DATE}.csv"
    write_csv(package_manifest, package_rows, ["relative_path", "bytes", "sha256"])
    package_zip = ROOT / "6_release" / f"SLE_Bcell_Submission_Package_{DATE}.zip"
    package_readme = [
        "# Current submission package",
        "",
        f"Canonical assembled package date: {DATE}",
        "",
        f"- Directory: ../SLE_Bcell_Submission_Package_{DATE}",
        f"- ZIP: ../SLE_Bcell_Submission_Package_{DATE}.zip",
        f"- Payload files: {len(package_rows)}",
    ]
    if package_zip.exists():
        package_readme.extend(
            [
                f"- ZIP bytes: {package_zip.stat().st_size:,}",
                f"- ZIP SHA-256: {sha256(package_zip)}",
            ]
        )
    package_readme.extend(
        [
            f"- Package content catalog: PACKAGE_CONTENTS_{DATE}.csv",
            "",
            "This pointer does not authorize submission or alter the scientific freeze state.",
        ]
    )
    write_text(ROOT / "6_release" / "current_submission" / "README.md", "\n".join(package_readme))

    cleanup_rows = [row for row in rows if row["value_tier"] == "P3"]
    cleanup_fields = source_fields + ["cleanup_view_note"]
    cleanup_enriched = []
    for row in cleanup_rows:
        copy = dict(row)
        copy["cleanup_view_note"] = "Non-exclusive P3 review view; deletion requires separate explicit approval."
        cleanup_enriched.append(copy)
    p3_review = ROOT / "8_archive" / "duplicate_candidates" / f"P3_CLEANUP_REVIEW_VIEW_{DATE}.csv"
    write_csv(
        p3_review,
        cleanup_enriched,
        cleanup_fields,
    )

    status = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_NON_DESTRUCTIVE_SUBFOLDER_ORGANIZATION",
        "source_inventory": str(INVENTORY.relative_to(ROOT)).replace("\\", "/"),
        "source_inventory_rows": len(rows),
        "targeted_rows": len(master_rows),
        "excluded_existing_figure_rows": excluded_figures,
        "unclassified_targeted_rows": 0,
        "source_paths_moved": 0,
        "source_paths_renamed": 0,
        "target_buckets": list(TAXONOMY),
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "current_submission_payload_files": len(package_rows),
        "p3_cleanup_review_rows": len(cleanup_rows),
        "organization_hash_manifest": str(HASH_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
    }
    write_text(STATUS_JSON, json.dumps(status, indent=2, ensure_ascii=False))
    write_text(TAXONOMY_MD, "\n".join(taxonomy_lines))

    hash_targets = [MASTER_CATALOG, TAXONOMY_MD, STATUS_JSON, package_manifest, p3_review]
    hash_targets.extend(ROOT / bucket / "SUBFOLDER_INDEX.md" for bucket in TAXONOMY)
    for bucket, categories in TAXONOMY.items():
        for category in categories:
            category_dir = ROOT / bucket / category
            hash_targets.extend(
                [
                    category_dir / "README.md",
                    category_dir / f"FILE_CATALOG_{DATE}.csv",
                ]
            )
    hash_rows = []
    for path in sorted(set(hash_targets)):
        hash_rows.append(
            {
                "relative_path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    write_csv(HASH_MANIFEST, hash_rows, ["relative_path", "bytes", "sha256"])

    if len(master_rows) + excluded_figures != len(rows):
        raise RuntimeError("Classification accounting mismatch")
    if sum(bucket_counts.values()) != len(master_rows):
        raise RuntimeError("Bucket accounting mismatch")

    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
