#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a compact, self-contained Phase 17 review package for the 6013RP-wyf project.

The script is read-only with respect to the project. It selects analysis code,
manuscripts, compact result tables/figures, lightweight metadata, the latest audit,
and the latest submission package while excluding H5AD files, raw archives,
per-cell giant tables, node_modules, caches and build directories.

Default project:
    H:\cuhk-2025fALL\6013RP-wyf
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Iterable

VERSION = "1.0.0"

EXCLUDED_DIR_NAMES = {
    "__pycache__", "node_modules", ".git", ".svn", ".hg",
    ".ipynb_checkpoints", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".cache", "cache", "tmp", "temp",
    ".artifact_work_supp_tables",
    ".artifact_work_manuscript_render_2026-07-31",
    "_build_advisor_report_2026-07-31",
    "_project_audit",
    "audit_tools",
}

EXCLUDED_SUFFIXES = {
    ".h5ad", ".h5", ".hdf5", ".loom", ".rds", ".rdata",
    ".tar", ".7z", ".rar", ".bam", ".cram",
    ".fastq", ".fq", ".pyc", ".pyo", ".node", ".dll", ".exe",
}

EXCLUDED_COMPOUND_SUFFIXES = {
    ".fastq.gz", ".fq.gz", ".tar.gz", ".tar.bz2", ".tar.xz",
    ".tsv.gz", ".csv.gz", ".vcf.gz", ".bed.gz",
}

EXCLUDED_NAME_PATTERNS = {
    ".inspect.ndjson",
    "bcell_obs_scores.csv",
    "bcell_obs_scores_labeled.csv",
}

CORE_ROOTS = {
    "00_project_management",
    "01_manuscript",
    "02_analysis",
    "03_results",
}

SUBMISSION_INCLUDE_PREFIXES = (
    "04_submission/package_genome_medicine_2026-07-31",
    "04_submission/outputs/manuscript_2026-07-31",
    "04_submission/outputs/cover_letter_2026-07-31",
    "04_submission/outputs/supplementary_tables_2026-07-27",
    "04_submission/advisor_report_2026-07-31/selected_results",
    "04_submission/figure_quality_qc",
    "04_submission/manuscript_numeric_qc",
    "04_submission/manuscript_structure_qc",
    "04_submission/reference_verification",
)

SUBMISSION_ROOT_FILES = {
    "README.md",
    "advisor_full_project_audit_v4_2026-07-27.md",
    "author_completion_form_2026-07-31.md",
    "cover_letter_genome_medicine_v3_AUTHOR_COMPLETION_REQUIRED_2026-07-31.md",
    "data_code_availability_v1.md",
    "final_package_verification_2026-07-31.md",
    "genome_medicine_target_alignment_2026-07-22.md",
    "journal_shortlist_upper_q1_2026-07-09.md",
    "journal_strategy.md",
    "journal_target_decision_matrix_v1.md",
    "submission_readiness_and_next_stage_v5_2026-07-31.md",
}

DATA_ALLOWED_SUFFIXES = {
    ".csv", ".tsv", ".txt", ".json", ".yaml", ".yml", ".md",
    ".pdf", ".xlsx", ".xls", ".gmt", ".bib",
}

def stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")

def norm_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()

def compound_suffix(name: str) -> str:
    lower = name.lower()
    for suffix in sorted(EXCLUDED_COMPOUND_SUFFIXES, key=len, reverse=True):
        if lower.endswith(suffix):
            return suffix
    return Path(lower).suffix

def sha256(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(block_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def inside_excluded_dir(rel: Path) -> bool:
    return any(part.lower() in {x.lower() for x in EXCLUDED_DIR_NAMES} for part in rel.parts)

def should_exclude_by_name(path: Path) -> str | None:
    lower = path.name.lower()
    if any(lower.endswith(x.lower()) for x in EXCLUDED_NAME_PATTERNS):
        return "excluded_large_or_inspection_table"
    comp = compound_suffix(lower)
    if comp in EXCLUDED_COMPOUND_SUFFIXES:
        return f"excluded_compound_suffix:{comp}"
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return f"excluded_suffix:{path.suffix.lower()}"
    return None

def latest_audit_dir(root: Path) -> Path | None:
    base = root / "_project_audit"
    if not base.exists():
        return None
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name[:8].isdigit()]
    return sorted(dirs)[-1] if dirs else None

def collect_files(root: Path, max_result_mb: float, max_data_mb: float) -> tuple[list[Path], list[dict]]:
    selected: list[Path] = []
    excluded: list[dict] = []
    max_result = int(max_result_mb * 1024 * 1024)
    max_data = int(max_data_mb * 1024 * 1024)

    def consider(path: Path, size_limit: int | None, reason_prefix: str) -> None:
        rel = path.relative_to(root)
        if inside_excluded_dir(rel):
            excluded.append({"relative_path": rel.as_posix(), "reason": "excluded_directory"})
            return
        name_reason = should_exclude_by_name(path)
        if name_reason:
            excluded.append({"relative_path": rel.as_posix(), "reason": name_reason})
            return
        try:
            size = path.stat().st_size
        except OSError as exc:
            excluded.append({"relative_path": rel.as_posix(), "reason": f"stat_error:{exc}"})
            return
        if size_limit is not None and size > size_limit:
            excluded.append({
                "relative_path": rel.as_posix(),
                "reason": f"{reason_prefix}_over_limit:{size}bytes",
            })
            return
        selected.append(path)

    for root_name in CORE_ROOTS:
        base = root / root_name
        if not base.exists():
            excluded.append({"relative_path": root_name, "reason": "required_root_missing"})
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            limit = max_result if root_name == "03_results" else None
            consider(path, limit, "result_file")

    # Lightweight Data metadata and source descriptors only.
    data_root = root / "Data"
    if data_root.exists():
        for path in data_root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in DATA_ALLOWED_SUFFIXES:
                excluded.append({
                    "relative_path": path.relative_to(root).as_posix(),
                    "reason": "data_file_type_not_selected",
                })
                continue
            consider(path, max_data, "data_file")

    # Latest submission package and current QC only.
    sub_root = root / "04_submission"
    if sub_root.exists():
        for path in sub_root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            rel_lower = rel.lower()
            root_file = path.parent == sub_root and path.name in SUBMISSION_ROOT_FILES
            prefixed = any(rel_lower.startswith(prefix.lower()) for prefix in SUBMISSION_INCLUDE_PREFIXES)
            if root_file or prefixed:
                consider(path, max_result, "submission_file")

    audit = latest_audit_dir(root)
    if audit:
        for path in audit.rglob("*"):
            if path.is_file():
                selected.append(path)

    # De-duplicate and sort.
    unique = {str(p.resolve()).lower(): p for p in selected}
    return sorted(unique.values(), key=lambda p: norm_rel(p, root).lower()), excluded

def main() -> int:
    ap = argparse.ArgumentParser(description="Build compact Phase 17 review package")
    ap.add_argument("--root", default=r"H:\cuhk-2025fALL\6013RP-wyf")
    ap.add_argument("--output-dir", default="")
    ap.add_argument("--max-result-mb", type=float, default=30.0)
    ap.add_argument("--max-data-mb", type=float, default=25.0)
    ap.add_argument("--no-zip", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"[ERROR] Project root not found: {root}", file=sys.stderr)
        return 2

    output_base = Path(args.output_dir).expanduser() if args.output_dir else root / "_phase17_review_pack"
    output_base.mkdir(parents=True, exist_ok=True)
    run_dir = output_base / stamp()
    payload = run_dir / "payload"
    payload.mkdir(parents=True, exist_ok=False)

    selected, excluded = collect_files(root, args.max_result_mb, args.max_data_mb)
    print(f"[INFO] Selected {len(selected):,} files.")

    manifest: list[dict] = []
    total_bytes = 0
    for i, src in enumerate(selected, 1):
        rel = src.relative_to(root)
        dst = payload / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        size = dst.stat().st_size
        total_bytes += size
        manifest.append({
            "relative_path": rel.as_posix(),
            "size_bytes": size,
            "sha256": sha256(dst),
        })
        if i % 250 == 0 or i == len(selected):
            print(f"[COPY] {i:,}/{len(selected):,}")

    with (run_dir / "included_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["relative_path", "size_bytes", "sha256"])
        w.writeheader()
        w.writerows(manifest)

    with (run_dir / "excluded_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["relative_path", "reason"])
        w.writeheader()
        w.writerows(excluded)

    summary = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "version": VERSION,
        "project_root": str(root),
        "run_directory": str(run_dir),
        "included_files": len(manifest),
        "included_bytes": total_bytes,
        "included_gb": round(total_bytes / 1024**3, 4),
        "excluded_records": len(excluded),
        "max_result_mb": args.max_result_mb,
        "max_data_mb": args.max_data_mb,
    }
    (run_dir / "review_pack_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    workflow = f"""# Phase 17 review-pack workflow

- Created: {summary['created_at']}
- Project root: `{root}`
- Included files: {len(manifest):,}
- Included size: {total_bytes / 1024**2:.2f} MB
- Excluded records: {len(excluded):,}

## Selection policy

Included:
- `00_project_management`, `01_manuscript`, `02_analysis`;
- compact `03_results` files;
- lightweight `Data` metadata/source descriptors;
- latest Genome Medicine package and current QC;
- latest `_project_audit` output.

Excluded:
- H5AD and other large analysis objects;
- raw archives and compressed GWAS/FASTQ files;
- per-cell giant score tables;
- node_modules, artifact caches and build directories;
- files larger than configured limits.

This package is intended for scientific and reproducibility review, not for rerunning the full pipeline.
"""
    (run_dir / "WORKFLOW_REVIEW_PACK.md").write_text(workflow, encoding="utf-8")

    zip_path = run_dir.with_suffix(".zip")
    if not args.no_zip:
        print(f"[INFO] Creating ZIP: {zip_path}")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for path in sorted(run_dir.rglob("*")):
                if path.is_file():
                    zf.write(path, arcname=f"{run_dir.name}/{path.relative_to(run_dir).as_posix()}")
        print(f"[SUCCESS] ZIP: {zip_path}")
    else:
        print(f"[SUCCESS] Folder: {run_dir}")

    (output_base / "_LATEST_REVIEW_PACK.txt").write_text(
        f"run_dir={run_dir}\nzip={zip_path if not args.no_zip else ''}\n",
        encoding="utf-8",
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
