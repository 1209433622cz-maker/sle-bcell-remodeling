#!/usr/bin/env python3
"""Audit, classify, and build the organized project view and submission package.

The existing analysis tree is intentionally preserved because many frozen
contracts bind relative paths and exact hashes. The new top-level directories
are a curated navigation and delivery layer. Every pre-existing local file is
recorded in the inventory, while only current canonical assets are copied into
the organized view.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import tarfile
import warnings
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import h5py
import numpy as np
from PIL import Image
from pypdf import PdfReader


DATE = "2026-10-12"
ORGANIZED_DIRS = [
    "0_admin",
    "1_data",
    "2_code",
    "3_results",
    "4_figures",
    "5_manuscript",
    "6_release",
    "7_report",
    "8_archive",
    "8_reference",
    "9_version",
]

TEXT_EXTENSIONS = {
    ".bib",
    ".cff",
    ".csv",
    ".diff",
    ".dot",
    ".gitattributes",
    ".gitignore",
    ".json",
    ".jsonl",
    ".md",
    ".patch",
    ".ps1",
    ".py",
    ".r",
    ".sh",
    ".svg",
    ".tex",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}
IMAGE_EXTENSIONS = {".bmp", ".eps", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".tif", ".tiff"}
CODE_EXTENSIONS = {".py", ".ps1", ".r", ".sh", ".ipynb"}
DATA_EXTENSIONS = {
    ".bam",
    ".bai",
    ".cram",
    ".fastq",
    ".fq",
    ".h5",
    ".h5ad",
    ".hdf5",
    ".loom",
    ".mtx",
    ".npy",
    ".npz",
    ".rds",
    ".sra",
}


def io_path(path: Path) -> Path:
    """Return a Windows long-path-safe view without changing catalog paths."""
    if os.name != "nt":
        return path
    absolute = str(path.resolve())
    if absolute.startswith("\\\\?\\"):
        return path
    if absolute.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + absolute.lstrip("\\"))
    return Path("\\\\?\\" + absolute)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        if columns:
            writer.writeheader()
            writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def copy_file(root: Path, source: str, destination: str) -> dict[str, object]:
    src = root / source
    dst = root / destination
    if not src.is_file():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if sha256(src) != sha256(dst):
        raise ValueError(f"copy hash mismatch: {source}")
    return {
        "organized_path": destination.replace("\\", "/"),
        "source_path": source.replace("\\", "/"),
        "bytes": dst.stat().st_size,
        "sha256": sha256(dst),
    }


def git_tracked(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    return {item.replace("\\", "/") for item in result.stdout.decode("utf-8").split("\0") if item}


def git_ignored(root: Path, paths: list[str]) -> set[str]:
    payload = ("\0".join(paths) + "\0").encode("utf-8")
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "check-ignore", "-z", "--stdin"],
        cwd=root,
        input=payload,
        capture_output=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return {item.replace("\\", "/") for item in result.stdout.decode("utf-8").split("\0") if item}


def scan_files(root: Path) -> list[Path]:
    excluded = {".git", *ORGANIZED_DIRS}
    files: list[Path] = []
    for current, directories, names in os.walk(root):
        current_path = Path(current)
        if current_path == root:
            directories[:] = [name for name in directories if name not in excluded]
        if current_path == root / "tmp":
            directories[:] = [
                name
                for name in directories
                if not name.startswith("submission_verify_20261012_")
                and not name.startswith("lo_cover_20261012_")
            ]
            names[:] = [
                name
                for name in names
                if not name.startswith("cover_letter_20261012_")
                and not name.startswith("lo_cover_")
            ]
        directories[:] = [name for name in directories if name != ".git"]
        files.extend(current_path / name for name in names)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().lower())


def explicit_figure(rel: str) -> tuple[str, str]:
    lower = rel.lower()
    supplementary = re.search(r"supplementary[_\s-]*figure[_\s-]*s(10|[1-9])(?:\D|$)", lower)
    if supplementary:
        return f"Supplementary_S{supplementary.group(1)}", ""
    main = re.search(r"(?:^|[/_\s-])(?:figure|fig)[_\s-]*([1-8])(?:[a-z])?(?:\D|$)", lower)
    if not main:
        main = re.search(r"(?:^|/)figure([1-8])(?:[a-z_\-/]|$)", lower)
    associated = f"Fig{main.group(1)}" if main else ""
    page_render = bool(
        re.search(r"(?:^|[/_-])page[-_ ]?\d+", lower)
        or any(token in lower for token in ["contact_sheet", "contact-", "render", "thumbnail", "montage"])
    )
    comparison = any(token in lower for token in ["comparison", "compare", "proof", "crop", "visual_qa"])
    if page_render:
        return "Manuscript_or_QA_Page_Render", associated
    if comparison or "/qa/" in lower or "\\qa\\" in lower:
        return "Figure_QA_or_Comparison", associated
    if associated:
        return associated, associated
    if lower.startswith("paper/") and lower.endswith(".pdf"):
        return "Reference_Paper_PDF", ""
    if any(token in lower for token in ["manuscript", "supplementary_information", "cover_letter"]):
        return "Document_PDF_or_Render", ""
    if lower.startswith("phase17_v7/") or lower.startswith("03_results/"):
        return "Unnumbered_Scientific_Visual", ""
    return "Administrative_or_Other_Visual", ""


def is_figure_pdf(rel: str) -> bool:
    lower = rel.lower()
    if not lower.endswith(".pdf"):
        return False
    return bool(
        re.search(r"(?:supplementary[_\s-]*figure[_\s-]*s(?:10|[1-9])|(?:figure|fig)[_\s-]*[1-8])", lower)
        or "/figures/" in lower
        or "/figures_review/" in lower
        or re.search(r"(?:^|[/_-])[^/]*figure\.pdf$", lower)
        or "layout_proof.pdf" in lower
    )


def content_type(rel: str, extension: str) -> str:
    lower = rel.lower()
    name = Path(rel).name.lower()
    if extension in IMAGE_EXTENSIONS:
        visual, _ = explicit_figure(rel)
        return "qa_render_image" if "Render" in visual or "QA" in visual else "scientific_or_admin_image"
    if is_figure_pdf(rel):
        return "figure_pdf"
    if extension == ".pdf":
        return "reference_pdf" if lower.startswith("paper/") else "document_pdf"
    if extension == ".docx":
        return "manuscript_or_report_docx"
    if extension in CODE_EXTENSIONS:
        return "analysis_or_audit_code"
    if extension in DATA_EXTENSIONS or lower.endswith((".fastq.gz", ".csv.gz", ".tsv.gz", ".mtx.gz")):
        return "scientific_data"
    if extension in {".zip", ".7z", ".tar", ".gz", ".tgz"}:
        return "archive_or_compressed_payload"
    if extension in {".csv", ".tsv"}:
        return "source_data_or_manifest" if any(token in lower for token in ["source_data", "manifest", "matrix"]) else "tabular_result"
    if extension == ".jsonl":
        return "simulation_or_checkpoint_records"
    if extension in {".json", ".yaml", ".yml"}:
        return "configuration_or_receipt"
    if extension in {".md", ".txt"}:
        if "action_record" in name or any(token in name for token in ["audit", "review", "report"]):
            return "report_or_action_record"
        return "documentation"
    return "other"


def primary_bucket(rel: str, kind: str) -> str:
    lower = rel.lower()
    top = rel.split("/", 1)[0]
    if top == "PAPER" or extension_of(rel) == ".bib":
        return "8_reference"
    if top == "Data" or kind == "scientific_data":
        return "1_data"
    if top in {"audit_tools", "02_analysis", ".github"} or kind == "analysis_or_audit_code":
        return "2_code"
    if top == "04_submission" or any(token in lower for token in ["zenodo", "submission_package", "journal_submission"]):
        return "6_release"
    if top == "01_manuscript" or kind in {"manuscript_or_report_docx", "document_pdf"}:
        return "5_manuscript"
    if kind in {"scientific_or_admin_image", "figure_pdf", "qa_render_image"}:
        return "4_figures"
    if top == "03_results" or top == "phase17_v7":
        if kind == "report_or_action_record":
            return "7_report"
        return "3_results"
    if top in {"00_project_management", "05_Record"} or kind == "report_or_action_record":
        return "7_report"
    if top == "tmp" or "__pycache__" in lower or extension_of(rel) in {".pyc", ".tmp", ".log"}:
        return "8_archive"
    if top.endswith(".zip") or kind == "archive_or_compressed_payload":
        return "8_archive"
    if any(token in lower for token in ["manifest", "checksum", "sha256", "release_notes"]):
        return "9_version"
    return "0_admin"


def lifecycle(rel: str, git_state: str, kind: str) -> tuple[str, str]:
    lower = rel.lower()
    canonical_tokens = [
        "20261011_stagei_single_real_delta_profile",
        "20261011_stagek_limited_integration",
        "20261011_stagel_external_cohort_gate",
        "20261011_stagem_raw_pipeline_freeze",
        "20260929_reader_language_hard_negative/artwork",
        "20260908_final_cross_document",
    ]
    if any(token in lower for token in canonical_tokens):
        return "current_canonical", "P0"
    if kind == "qa_render_image" or any(token in lower for token in ["/qa/", "document_pages", "render_"]):
        return "qa_or_recomputable_render", "P3"
    if lower.startswith("tmp/") or "__pycache__" in lower or extension_of(rel) in {".pyc", ".tmp", ".log"}:
        return "cache_or_temporary", "P3"
    if lower.startswith("paper/"):
        return "reference_literature", "P1"
    if git_state == "tracked":
        return "retained_reproducibility_record", "P1"
    if kind in {"scientific_data", "archive_or_compressed_payload"}:
        return "local_only_large_or_archive", "P2"
    return "local_historical_or_duplicate", "P2"


def extension_of(rel: str) -> str:
    lower = rel.lower()
    for suffix in [".tar.gz", ".fastq.gz", ".csv.gz", ".tsv.gz", ".mtx.gz"]:
        if lower.endswith(suffix):
            return suffix
    return Path(lower).suffix


def validate_text(path: Path, extension: str) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    if extension == ".json":
        payload = json.loads(text)
        return "PASS", f"json_type={type(payload).__name__}"
    if extension == ".jsonl":
        count = 0
        for line in text.splitlines():
            if line.strip():
                json.loads(line)
                count += 1
        return "PASS", f"jsonl_records={count}"
    if extension in {".csv", ".tsv"}:
        delimiter = "\t" if extension == ".tsv" else ","
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            header = next(reader, [])
            rows = sum(1 for _ in reader)
        return "PASS", f"rows={rows}; columns={len(header)}"
    if extension == ".svg":
        if "<svg" not in text[:4096].lower():
            raise ValueError("SVG root not found")
        return "PASS", f"utf8_chars={len(text)}; svg_root=present"
    return "PASS", f"utf8_chars={len(text)}"


def validate_file(path: Path, rel: str) -> tuple[str, str]:
    extension = extension_of(rel)
    try:
        if extension in TEXT_EXTENSIONS or extension in {".csv", ".tsv"}:
            return validate_text(path, extension)
        if extension in {".zip", ".docx", ".xlsx"}:
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                if bad:
                    raise ValueError(f"CRC failure: {bad}")
                names = archive.namelist()
                if extension == ".docx" and "word/document.xml" not in names:
                    raise ValueError("word/document.xml missing")
                return "PASS", f"zip_members={len(names)}; crc=ok"
        if extension == ".pdf":
            with path.open("rb") as handle:
                pages = len(PdfReader(handle, strict=False).pages)
            return "PASS", f"pdf_pages={pages}"
        if extension in IMAGE_EXTENSIONS - {".svg", ".eps"}:
            with Image.open(path) as image:
                size = image.size
                image.verify()
            return "PASS", f"image={size[0]}x{size[1]}"
        if extension == ".eps":
            with path.open("rb") as handle:
                prefix = handle.read(64)
            if b"%!PS" not in prefix:
                raise ValueError("EPS/PostScript header missing")
            return "PASS", "eps_header=ok"
        if extension in {".gz", ".tar.gz", ".fastq.gz", ".csv.gz", ".tsv.gz", ".mtx.gz"}:
            total = 0
            with gzip.open(path, "rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    total += len(block)
            return "PASS", f"gzip_crc=ok; decompressed_bytes={total}"
        if extension in {".tar", ".tgz"}:
            with tarfile.open(path, "r:*") as archive:
                return "PASS", f"tar_members={len(archive.getmembers())}"
        if extension in {".h5", ".h5ad", ".hdf5"}:
            with h5py.File(path, "r") as handle:
                keys = sorted(handle.keys())
            return "PASS", f"hdf5_root_keys={';'.join(keys[:20])}"
        if extension == ".npy":
            array = np.load(path, mmap_mode="r", allow_pickle=False)
            return "PASS", f"npy_shape={array.shape}; dtype={array.dtype}"
        if extension == ".npz":
            with np.load(path, allow_pickle=False) as archive:
                return "PASS", f"npz_arrays={len(archive.files)}"
        with path.open("rb") as handle:
            handle.read(1)
        return "PASS", "readable_binary_or_untyped"
    except UnicodeDecodeError as exc:
        return "HOLD", f"utf8_decode_error={exc}"
    except Exception as exc:  # noqa: BLE001 - the audit must record every failure
        return "FAIL", f"{type(exc).__name__}: {exc}"


def inspect_one(root: Path, path: Path, tracked: set[str], ignored: set[str]) -> dict[str, object]:
    rel = path.relative_to(root).as_posix()
    readable_path = io_path(path)
    extension = extension_of(rel)
    kind = content_type(rel, extension)
    state = "tracked" if rel in tracked else ("ignored_local" if rel in ignored else "untracked")
    visual_class, associated = explicit_figure(rel) if extension in IMAGE_EXTENSIONS or is_figure_pdf(rel) else ("", "")
    status, detail = validate_file(readable_path, rel)
    life, tier = lifecycle(rel, state, kind)
    stat = readable_path.stat()
    return {
        "relative_path": rel,
        "top_level": rel.split("/", 1)[0],
        "extension": extension or "[none]",
        "bytes": stat.st_size,
        "mib": round(stat.st_size / (1024 * 1024), 6),
        "modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "sha256": sha256(readable_path),
        "git_state": state,
        "content_type": kind,
        "organized_bucket": primary_bucket(rel, kind),
        "lifecycle": life,
        "value_tier": tier,
        "visual_class": visual_class,
        "associated_main_figure": associated,
        "content_check": status,
        "content_check_detail": detail,
    }


def summarize_inventory(rows: list[dict[str, object]], key: str) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)
    total_bytes = sum(int(row["bytes"]) for row in rows)
    return [
        {
            key: name,
            "files": len(items),
            "bytes": sum(int(item["bytes"]) for item in items),
            "gib": round(sum(int(item["bytes"]) for item in items) / (1024**3), 6),
            "percent_bytes": round(100 * sum(int(item["bytes"]) for item in items) / total_bytes, 4)
            if total_bytes
            else 0,
        }
        for name, items in sorted(grouped.items(), key=lambda pair: sum(int(item["bytes"]) for item in pair[1]), reverse=True)
    ]


def duplicate_tables(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, tuple[str, int]]]:
    by_hash: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_hash[str(row["sha256"])].append(row)
    groups: list[dict[str, object]] = []
    lookup: dict[str, tuple[str, int]] = {}
    index = 0
    for digest, items in sorted(by_hash.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        if len(items) < 2:
            continue
        index += 1
        group = f"DUP{index:05d}"
        canonical = sorted(
            items,
            key=lambda item: (
                {"P0": 0, "P1": 1, "P2": 2, "P3": 3}[str(item["value_tier"])],
                0 if item["git_state"] == "tracked" else 1,
                len(str(item["relative_path"])),
                str(item["relative_path"]),
            ),
        )[0]
        for item in items:
            lookup[str(item["relative_path"])] = (group, len(items))
        groups.append(
            {
                "duplicate_group": group,
                "sha256": digest,
                "copies": len(items),
                "bytes_each": items[0]["bytes"],
                "redundant_bytes": int(items[0]["bytes"]) * (len(items) - 1),
                "preferred_retained_path": canonical["relative_path"],
                "all_paths": " | ".join(str(item["relative_path"]) for item in items),
            }
        )
    return groups, lookup


def make_readmes(root: Path) -> None:
    contents = {
        "0_admin": "Project governance, licenses, citation metadata and the master navigation index.",
        "1_data": "Data manifests and compact current inputs. Large canonical data remain at their frozen source paths and are indexed rather than duplicated.",
        "2_code": "Current entry-point code copies and the complete code inventory. Frozen source paths remain authoritative for execution.",
        "3_results": "Current decision objects and indexes for all historical result files.",
        "4_figures": "Canonical main figures, supplementary figures and a complete visual-asset classification. Fig6-Fig8 are reserved because the current manuscript has five main figures.",
        "5_manuscript": "Latest Stage K manuscript and Supplementary Information copies with source receipts.",
        "6_release": "Current pre-submission master package, package manifest, verifier and release index. No journal submission is implied.",
        "7_report": "Current action record and indexes of all reports, reviews and work logs.",
        "8_archive": "Archive catalog and cleanup candidates. Bound or referenced historical files are not moved or deleted.",
        "8_reference": "Literature and reference catalog. Local PDFs remain in PAPER to preserve prior paths.",
        "9_version": "Full inventories, integrity results, duplicate groups, Git state and organization receipts.",
    }
    for directory, description in contents.items():
        target = root / directory
        target.mkdir(parents=True, exist_ok=True)
        (target / "README.md").write_text(
            f"# {directory}\n\n{description}\n\n"
            "This directory is part of the 12 October 2026 organized project view. "
            "See `0_admin/MASTER_INDEX.md` and `9_version/inventory/` for provenance.\n",
            encoding="utf-8",
            newline="\n",
        )


def copy_canonical_assets(root: Path) -> list[dict[str, object]]:
    copies: list[dict[str, object]] = []
    mappings = {
        "0_admin/CITATION.cff": "CITATION.cff",
        "0_admin/LICENSE": "LICENSE",
        "0_admin/LICENSE_CONTENT_CC_BY_4.0.md": "LICENSE_CONTENT_CC_BY_4.0.md",
        "0_admin/LICENSE_SCOPE.md": "LICENSE_SCOPE.md",
        "0_admin/REPRODUCIBILITY.md": "REPRODUCIBILITY.md",
        "1_data/manifests/StageM_Disease_Blind_Run_Map.csv": "phase17_v7/rp_v4_redesign/20261011_stageM_raw_pipeline_freeze/02_DISEASE_BLIND_RUN_MAP.csv",
        "1_data/manifests/StageM_Library_Run_Accounting.csv": "phase17_v7/rp_v4_redesign/20261011_stageM_raw_pipeline_freeze/03_LIBRARY_RUN_ACCOUNTING.csv",
        "1_data/manifests/StageM_Reference_Annotation_Manifest.csv": "phase17_v7/rp_v4_redesign/20261011_stageM_raw_pipeline_freeze/05_REFERENCE_ANNOTATION_MANIFEST.csv",
        "2_code/current_stageM/rp_v4_stageM_01_raw_pipeline_freeze.py": "audit_tools/rp_v4_stageM_01_raw_pipeline_freeze.py",
        "2_code/current_stageM/run_rp_v4_stageM.ps1": "audit_tools/run_rp_v4_stageM.ps1",
        "2_code/current_stageM/test_rp_v4_stageM.py": "audit_tools/test_rp_v4_stageM.py",
        "3_results/current/StageI_Gate.json": "phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/04_STAGE_I_GATE_STATUS.json",
        "3_results/current/StageI_Result.json": "phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/01_SINGLE_REAL_DELTA_PROFILE_RESULT.json",
        "3_results/current/StageK_Gate.json": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/02_STAGE_K_GATE_STATUS.json",
        "3_results/current/StageK_Source_Data.csv": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/01_STAGE_K_SOURCE_DATA.csv",
        "3_results/current/StageL_Gate.json": "phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/10_STAGE_L_GATE_STATUS.json",
        "3_results/current/StageM_Gate.json": "phase17_v7/rp_v4_redesign/20261011_stageM_raw_pipeline_freeze/13_STAGE_M_GATE_STATUS.json",
        "5_manuscript/current/Manuscript.docx": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Manuscript_StageK_Limited_Integration.docx",
        "5_manuscript/current/Manuscript.pdf": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Manuscript_StageK_Limited_Integration.pdf",
        "5_manuscript/current/Supplementary_Information.docx": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Supplementary_Information_StageK_S10.docx",
        "5_manuscript/current/Supplementary_Information.pdf": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Supplementary_Information_StageK_S10.pdf",
        "5_manuscript/current/Cover_Letter_npj_SBA.docx": "01_manuscript/submission_current/Cover_Letter_npj_SBA_2026-10-12.docx",
        "5_manuscript/current/Cover_Letter_npj_SBA.pdf": "01_manuscript/submission_current/Cover_Letter_npj_SBA_2026-10-12.pdf",
        "5_manuscript/current/Cover_Letter_npj_SBA.md": "01_manuscript/submission_current/Cover_Letter_npj_SBA_2026-10-12.md",
        "7_report/current/StageK_Advisor_Review.md": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/03_STAGE_K_ADVISOR_REVIEW.md",
        "7_report/current/StageL_Advisor_Review.md": "phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/11_STAGE_L_ADVISOR_REVIEW.md",
        "7_report/current/StageM_Advisor_Review.md": "phase17_v7/rp_v4_redesign/20261011_stageM_raw_pipeline_freeze/14_STAGE_M_ADVISOR_REVIEW.md",
    }
    for destination, source in mappings.items():
        copies.append(copy_file(root, source, destination))

    figure_pdf_root = "phase17_v7/npj_sba_qiteng_round3/20260929_reader_language_hard_negative/candidate/SLE_Bcell_Submission_Package/Figures"
    figure_png_root = "phase17_v7/npj_sba_qiteng_round3/20260929_reader_language_hard_negative/artwork/supplementary_figures"
    source_root = "phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document/figures/source_data"
    round3_source_root = "phase17_v7/npj_sba_qiteng_round3/20260929_reader_language_hard_negative/artwork/source_data"
    canonical_names = {
        1: "Figure1_disease_blind_identity_scope",
        2: "Figure2_sample_level_composition",
        3: "Figure3_gse174188_bconv_transcription",
        4: "Figure4_independent_ifn_replication",
        5: "Figure5_regulatory_evidence",
    }
    for number, name in canonical_names.items():
        copies.append(copy_file(root, f"{figure_pdf_root}/Figure_{number}.pdf", f"4_figures/Fig{number}/canonical/Figure_{number}.pdf"))
        copies.append(copy_file(root, f"{figure_png_root}/{name}.png", f"4_figures/Fig{number}/canonical/Figure_{number}.png"))
        data_root = round3_source_root if number in {2, 3} else source_root
        copies.append(copy_file(root, f"{data_root}/Figure{number}_source_data.csv", f"4_figures/Fig{number}/source_data/Figure_{number}_source_data.csv"))

    supplementary_source = "phase17_v7/npj_sba_qiteng_round3/20260929_reader_language_hard_negative/artwork/supplementary_figures"
    for source in sorted((root / supplementary_source).glob("Supplementary_Figure_S*.*")):
        rel = source.relative_to(root).as_posix()
        copies.append(copy_file(root, rel, f"4_figures/Supplementary/{source.name}"))
    return copies


def build_submission_package(root: Path) -> tuple[Path, list[dict[str, object]]]:
    package = root / "6_release" / f"SLE_Bcell_Submission_Package_{DATE}"
    package.mkdir(parents=True, exist_ok=True)
    sources = {
        "01_Manuscript/Manuscript.docx": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Manuscript_StageK_Limited_Integration.docx",
        "01_Manuscript/Manuscript.pdf": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Manuscript_StageK_Limited_Integration.pdf",
        "03_Supplementary_Information/Supplementary_Information.docx": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Supplementary_Information_StageK_S10.docx",
        "03_Supplementary_Information/Supplementary_Information.pdf": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/documents/Supplementary_Information_StageK_S10.pdf",
        "04_Supplementary_Data/Supplementary_Data_1_Figure_Source_Data.zip": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Supplementary_Data/Supplementary_Data_1_Figure_Source_Data.zip",
        "04_Supplementary_Data/Supplementary_Data_2_Regulator_Sensitivity.zip": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Supplementary_Data/Supplementary_Data_2_Regulator_Sensitivity.zip",
        "04_Supplementary_Data/Supplementary_Data_3_Full_Statistical_Results.zip": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Supplementary_Data/Supplementary_Data_3_Full_Statistical_Results.zip",
        "04_Supplementary_Data/Supplementary_Data_4_Measurement_Rule_Sensitivity.csv": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/01_STAGE_K_SOURCE_DATA.csv",
        "05_Cover_Letter/DRAFT_npj_SBA_Cover_Letter.docx": "01_manuscript/submission_current/Cover_Letter_npj_SBA_2026-10-12.docx",
        "05_Cover_Letter/DRAFT_npj_SBA_Cover_Letter.pdf": "01_manuscript/submission_current/Cover_Letter_npj_SBA_2026-10-12.pdf",
        "05_Cover_Letter/DRAFT_npj_SBA_Cover_Letter.md": "01_manuscript/submission_current/Cover_Letter_npj_SBA_2026-10-12.md",
        "06_Author_Resources/Authors_and_Declarations.docx": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Author_Resources/Authors_and_Declarations.docx",
        "06_Author_Resources/Authors_and_Declarations.pdf": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Author_Resources/Authors_and_Declarations.pdf",
        "06_Author_Resources/Authors_and_Declarations.md": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Author_Resources/Authors_and_Declarations.md",
        "06_Author_Resources/Reporting_Information.md": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Author_Resources/Reporting_Information.md",
        "06_Author_Resources/Source_Provenance_20260929.json": "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package/Author_Resources/Source_Provenance.json",
        "06_Author_Resources/StageK_Gate.json": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/02_STAGE_K_GATE_STATUS.json",
        "06_Author_Resources/StageK_Advisor_Review.md": "phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/03_STAGE_K_ADVISOR_REVIEW.md",
    }
    records: list[dict[str, object]] = []
    for destination, source in sources.items():
        records.append(copy_file(root, source, f"{package.relative_to(root).as_posix()}/{destination}"))
    figure_source = root / "4_figures"
    for number in range(1, 6):
        for extension in [".pdf", ".png"]:
            src = figure_source / f"Fig{number}/canonical/Figure_{number}{extension}"
            dst = package / "02_Figures" / f"Figure_{number}{extension}"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            records.append(
                {
                    "organized_path": dst.relative_to(root).as_posix(),
                    "source_path": src.relative_to(root).as_posix(),
                    "bytes": dst.stat().st_size,
                    "sha256": sha256(dst),
                }
            )
    for src in sorted((root / "4_figures/Supplementary").glob("*.pdf")):
        dst = package / "03_Supplementary_Information" / "Separate_Supplementary_Figures" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        records.append(
            {
                "organized_path": dst.relative_to(root).as_posix(),
                "source_path": src.relative_to(root).as_posix(),
                "bytes": dst.stat().st_size,
                "sha256": sha256(dst),
            }
        )
    readme = """# SLE B-cell remodeling pre-submission master package

Status: `PRE_SUBMISSION_MASTER_PACKAGE__NOT_SUBMITTED`.

The scientific core is current through RP v4 Stage K. The manuscript and
Supplementary Information include the bounded measurement-rule sensitivity;
Figures 1-5 retain the QiTeng reader-language freeze. Stage L/M external-cohort
work has not produced or unlocked an external outcome and is not inserted here.

The cover letter is the title-synchronized npj Systems Biology and Applications
draft dated 12 October 2026. Reconfirm the target journal before upload. If
another SCI Q2 journal is selected, adapt only journal-facing metadata and
formatting; do not alter the frozen scientific claims or figures.

Suggested upload objects are the DOCX manuscript, five PDF main figures, the
single Supplementary Information PDF, four Supplementary Data files and the
target-confirmed cover letter. Separate Supplementary Figure PDFs are retained
for portals that request individual files; they are already embedded in the
Supplementary Information.
"""
    (package / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    verifier = """#!/usr/bin/env python3
import csv, hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = Path(__file__).with_name("SHA256SUMS.csv")
rows = list(csv.DictReader(manifest.open(encoding="utf-8-sig", newline="")))
for row in rows:
    path = root / row["path"]
    if not path.is_file() or path.stat().st_size != int(row["bytes"]):
        raise SystemExit(f"size/missing failure: {row['path']}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != row["sha256"]:
        raise SystemExit(f"hash failure: {row['path']}")
print(f"PASS: {len(rows)} package payload files verified")
"""
    integrity = package / "07_Integrity"
    integrity.mkdir(parents=True, exist_ok=True)
    (integrity / "verify_package.py").write_text(verifier, encoding="utf-8", newline="\n")
    payloads = []
    for path in sorted(package.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.csv":
            continue
        payloads.append(
            {
                "path": path.relative_to(package).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    write_csv(integrity / "SHA256SUMS.csv", payloads)
    archive = root / "6_release" / f"SLE_Bcell_Submission_Package_{DATE}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for path in sorted(package.rglob("*")):
            if path.is_file():
                handle.write(path, arcname=f"{package.name}/{path.relative_to(package).as_posix()}")
    with zipfile.ZipFile(archive) as handle:
        if handle.testzip() is not None:
            raise ValueError("submission ZIP CRC failed")
    write_json(
        root / "6_release" / "SUBMISSION_PACKAGE_STATUS.json",
        {
            "schema": "SLE_BCELL_SUBMISSION_MASTER_PACKAGE_1.0",
            "created_on": DATE,
            "status": "PRE_SUBMISSION_MASTER_PACKAGE__NOT_SUBMITTED",
            "package_directory": package.relative_to(root).as_posix(),
            "package_files_excluding_manifest": len(payloads),
            "zip": archive.relative_to(root).as_posix(),
            "zip_bytes": archive.stat().st_size,
            "zip_sha256": sha256(archive),
            "scientific_text_baseline": "RPv4 Stage K limited integration",
            "figure_baseline": "QiTeng 2026-09-29 reader-language freeze",
            "external_outcome_included": False,
            "submitted": False,
        },
    )
    return archive, records


def write_master_index(root: Path, inventory_count: int, visual_count: int) -> None:
    text = f"""# SLE B-cell remodeling organized project index

This is the non-destructive organized view created on {DATE}. The frozen
analysis backend remains in its original paths because contracts, manifests and
scripts bind those paths. The view contains canonical copies and complete
indexes rather than silently relocating or deleting scientific evidence.

## Directory map

- `0_admin`: governance, licenses, citation and this index.
- `1_data`: compact data manifests; large data stay accession/hash managed.
- `2_code`: current runnable entry points and the code inventory.
- `3_results`: current gate/result copies and result inventory.
- `4_figures`: current Figures 1-5, reserved Fig6-Fig8 directories,
  Supplementary Figures S1-S10 and all {visual_count:,} classified visual assets.
- `5_manuscript`: current Stage K manuscript and Supplementary Information.
- `6_release`: complete pre-submission master package and verifier.
- `7_report`: work records, reviews and report index.
- `8_archive`: archive and cleanup-candidate index; no bound evidence deleted.
- `8_reference`: literature catalog.
- `9_version`: {inventory_count:,}-file baseline inventory, SHA-256, content
  checks, duplicate groups and organization receipts.

## Scientific status

The stable positive claim remains reproducible process-level B_CONV IFN/ISG
remodeling, bounded by identity, transfer and mechanistic ceilings. RP v4 Stage
I is a measurement-rule sensitivity for the same 68-donor estimand, not an
independent replication. Stage M froze the disease-blind raw-count workflow but
raw reconstruction remains blocked by runtime, physical storage and separate
two-author download authorization.
"""
    (root / "0_admin/MASTER_INDEX.md").write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.workspace.resolve()
    print("[1/5] Scanning the immutable baseline tree...", flush=True)
    files = scan_files(root)
    print(f"      Discovered {len(files):,} baseline files.", flush=True)
    rel_paths = [path.relative_to(root).as_posix() for path in files]
    tracked = git_tracked(root)
    ignored = git_ignored(root, [path for path in rel_paths if path not in tracked])
    logging.getLogger("pypdf").setLevel(logging.CRITICAL)
    warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)
    print(f"[2/5] Hashing and validating content with {args.workers} workers...", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(lambda path: inspect_one(root, path, tracked, ignored), files))

    print("[3/5] Resolving duplicates, value tiers, and figure ownership...", flush=True)
    duplicate_rows, duplicate_lookup = duplicate_tables(rows)
    for row in rows:
        group, count = duplicate_lookup.get(str(row["relative_path"]), ("", 1))
        row["duplicate_group"] = group
        row["duplicate_copies"] = count

    print("[4/5] Building the non-destructive organized view and package...", flush=True)
    make_readmes(root)
    inventory_root = root / "9_version/inventory"
    write_csv(inventory_root / f"WORKSPACE_FILE_INVENTORY_{DATE}.csv", rows)
    write_csv(inventory_root / f"DIRECTORY_SIZE_SUMMARY_{DATE}.csv", summarize_inventory(rows, "top_level"))
    write_csv(inventory_root / f"FILE_TYPE_SUMMARY_{DATE}.csv", summarize_inventory(rows, "extension"))
    write_csv(inventory_root / f"ORGANIZED_BUCKET_SUMMARY_{DATE}.csv", summarize_inventory(rows, "organized_bucket"))
    write_csv(inventory_root / f"CONTENT_CHECK_SUMMARY_{DATE}.csv", summarize_inventory(rows, "content_check"))
    write_csv(inventory_root / f"DUPLICATE_GROUPS_{DATE}.csv", duplicate_rows)

    visuals = [row for row in rows if row["visual_class"]]
    write_csv(inventory_root / f"VISUAL_ASSET_CATALOG_{DATE}.csv", visuals)
    reports = [row for row in rows if row["organized_bucket"] == "7_report"]
    write_csv(root / "7_report" / f"REPORT_AND_WORK_RECORD_INDEX_{DATE}.csv", reports)
    references = [row for row in rows if row["organized_bucket"] == "8_reference"]
    write_csv(root / "8_reference" / f"REFERENCE_INDEX_{DATE}.csv", references)
    code = [row for row in rows if row["organized_bucket"] == "2_code"]
    write_csv(root / "2_code" / f"CODE_INDEX_{DATE}.csv", code)
    data = [row for row in rows if row["organized_bucket"] == "1_data"]
    write_csv(root / "1_data" / f"DATA_INDEX_{DATE}.csv", data)
    results = [row for row in rows if row["organized_bucket"] == "3_results"]
    write_csv(root / "3_results" / f"RESULT_INDEX_{DATE}.csv", results)
    archive = [row for row in rows if row["organized_bucket"] == "8_archive" or row["value_tier"] == "P3"]
    write_csv(root / "8_archive" / f"ARCHIVE_AND_CLEANUP_CANDIDATE_INDEX_{DATE}.csv", archive)

    for number in range(1, 9):
        target = root / "4_figures" / f"Fig{number}"
        target.mkdir(parents=True, exist_ok=True)
        matching = [row for row in visuals if row["visual_class"] == f"Fig{number}" or row["associated_main_figure"] == f"Fig{number}"]
        write_csv(target / f"ALL_MATCHING_ASSETS_Fig{number}.csv", matching, fields=list(rows[0]))
        status = "ACTIVE_CURRENT_MANUSCRIPT_FIGURE" if number <= 5 else "RESERVED_NOT_USED_IN_CURRENT_MANUSCRIPT"
        (target / "README.md").write_text(
            f"# Figure {number}\n\nStatus: `{status}`.\n\n"
            "`canonical/` contains the current delivery copy when active; `source_data/` contains the associated machine-readable source table. "
            "The matching-assets CSV indexes historical candidates and QA without duplicating them.\n",
            encoding="utf-8",
            newline="\n",
        )
    supplementary_dir = root / "4_figures/Supplementary"
    supplementary_dir.mkdir(parents=True, exist_ok=True)
    supplementary_rows = [row for row in visuals if str(row["visual_class"]).startswith("Supplementary_")]
    write_csv(supplementary_dir / "ALL_SUPPLEMENTARY_ASSETS.csv", supplementary_rows)
    qa_dir = root / "4_figures/QA_Renders"
    qa_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        qa_dir / "ALL_QA_RENDER_ASSETS.csv",
        [row for row in visuals if row["visual_class"] in {"Manuscript_or_QA_Page_Render", "Figure_QA_or_Comparison"}],
    )
    other_dir = root / "4_figures/Other_Visuals"
    other_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        other_dir / "ALL_OTHER_VISUAL_ASSETS.csv",
        [row for row in visuals if row["visual_class"] not in {f"Fig{i}" for i in range(1, 9)} and not str(row["visual_class"]).startswith("Supplementary_") and row["visual_class"] not in {"Manuscript_or_QA_Page_Render", "Figure_QA_or_Comparison"}],
    )

    copy_records = copy_canonical_assets(root)
    package_zip, package_records = build_submission_package(root)
    write_csv(root / "9_version" / f"ORGANIZED_COPY_PROVENANCE_{DATE}.csv", copy_records + package_records)
    write_master_index(root, len(rows), len(visuals))

    failures = [row for row in rows if row["content_check"] == "FAIL"]
    holds = [row for row in rows if row["content_check"] == "HOLD"]
    status = {
        "schema": "SLE_BCELL_FULL_WORKSPACE_ORGANIZATION_1.0",
        "created_on": DATE,
        "baseline_files": len(rows),
        "baseline_bytes": sum(int(row["bytes"]) for row in rows),
        "tracked_files": sum(row["git_state"] == "tracked" for row in rows),
        "ignored_local_files": sum(row["git_state"] == "ignored_local" for row in rows),
        "untracked_files": sum(row["git_state"] == "untracked" for row in rows),
        "visual_assets": len(visuals),
        "duplicate_groups": len(duplicate_rows),
        "content_pass": sum(row["content_check"] == "PASS" for row in rows),
        "content_hold": len(holds),
        "content_fail": len(failures),
        "organized_directories": ORGANIZED_DIRS,
        "legacy_paths_moved": 0,
        "legacy_paths_deleted": 0,
        "submission_package_zip": package_zip.relative_to(root).as_posix(),
        "submission_package_zip_sha256": sha256(package_zip),
        "decision": "PASS_NONDESTRUCTIVE_ORGANIZED_VIEW__REVIEW_RECORDED_CONTENT_EXCEPTIONS",
    }
    write_json(root / "9_version" / f"ORGANIZATION_STATUS_{DATE}.json", status)
    write_csv(
        root / "9_version/inventory" / f"CONTENT_CHECK_EXCEPTIONS_{DATE}.csv",
        failures + holds,
        fields=list(rows[0]),
    )
    print("[5/5] Organization and package build complete.", flush=True)
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
