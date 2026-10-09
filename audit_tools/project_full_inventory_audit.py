#!/usr/bin/env python3
"""Create a repository-wide, content-aware file inventory and health audit.

The audit is intentionally read-only with respect to scientific inputs. It writes
only machine-readable reports to the requested output directory.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


TEXT_EXTENSIONS = {
    ".bib",
    ".cfg",
    ".css",
    ".csv",
    ".env",
    ".gitattributes",
    ".gitignore",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".log",
    ".md",
    ".ps1",
    ".py",
    ".r",
    ".rst",
    ".sh",
    ".tex",
    ".toml",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".gif", ".webp"}
OFFICE_EXTENSIONS = {".docx", ".xlsx", ".pptx"}
HDF5_EXTENSIONS = {".h5", ".hdf5", ".h5ad"}
ABSOLUTE_PATH_RE = re.compile(
    r"(?i)(?:[A-Z]:\\(?:Users|ProgramData|cuhk-|bioinfor)[^\s\"'<>|]*)"
)
SENSITIVE_NAME_RE = re.compile(
    r"(?i)(?:credential|secret|token|password|private[_-]?key|\.pem$|\.pfx$|\.key$)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--large-mib", type=float, default=10.0)
    parser.add_argument("--duplicate-min-mib", type=float, default=1.0)
    return parser.parse_args()


def run_git(root: Path, args: list[str]) -> tuple[int, bytes, str]:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr.decode("utf-8", "replace")


def nul_paths(root: Path, args: list[str]) -> tuple[set[str], str]:
    code, stdout, stderr = run_git(root, args)
    if code != 0:
        return set(), stderr
    paths = {
        value.decode("utf-8", "surrogateescape").replace("\\", "/")
        for value in stdout.split(b"\0")
        if value
    }
    return paths, stderr


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp1252"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("text", raw, 0, min(1, len(raw)), "unsupported encoding")


def validate_csv(path: Path, delimiter: str) -> dict[str, Any]:
    rows = 0
    max_columns = 0
    header_columns = 0
    with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        for row in reader:
            rows += 1
            max_columns = max(max_columns, len(row))
            if rows == 1:
                header_columns = len(row)
    return {
        "status": "PASS",
        "detail": f"rows={rows}; header_columns={header_columns}; max_columns={max_columns}",
        "rows": rows,
        "columns": header_columns,
    }


def validate_zip(path: Path, suffix: str) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        bad_member = archive.testzip()
        required_ok = True
        if suffix == ".docx":
            required_ok = "word/document.xml" in names
        elif suffix == ".xlsx":
            required_ok = "xl/workbook.xml" in names
        elif suffix == ".pptx":
            required_ok = "ppt/presentation.xml" in names
        if bad_member:
            return {
                "status": "FAIL",
                "detail": f"CRC failure: {bad_member}; members={len(names)}",
            }
        if not required_ok:
            return {
                "status": "FAIL",
                "detail": f"missing required OOXML part; members={len(names)}",
            }
        return {"status": "PASS", "detail": f"members={len(names)}; CRC=ok"}


def validate_pdf(path: Path) -> dict[str, Any]:
    from pypdf import PdfReader

    reader = PdfReader(str(path), strict=False)
    encrypted = bool(reader.is_encrypted)
    pages = len(reader.pages) if not encrypted else -1
    return {
        "status": "PASS" if not encrypted else "WARN",
        "detail": f"pages={pages}; encrypted={encrypted}",
        "pages": pages,
    }


def validate_image(path: Path) -> dict[str, Any]:
    from PIL import Image

    with Image.open(path) as image:
        width, height = image.size
        mode = image.mode
        image.verify()
    return {
        "status": "PASS",
        "detail": f"{width}x{height}; mode={mode}",
        "width": width,
        "height": height,
    }


def validate_npz(path: Path) -> dict[str, Any]:
    import numpy as np

    with np.load(path, allow_pickle=False) as archive:
        names = list(archive.files)
        shapes = [f"{name}:{tuple(archive[name].shape)}" for name in names[:8]]
    suffix = "" if len(names) <= 8 else f"; +{len(names) - 8} more"
    return {
        "status": "PASS",
        "detail": f"arrays={len(names)}; {'; '.join(shapes)}{suffix}",
    }


def validate_tar(path: Path) -> dict[str, Any]:
    with tarfile.open(path, "r:*") as archive:
        count = sum(1 for _ in archive)
    return {"status": "PASS", "detail": f"members={count}"}


def validate_gzip(path: Path) -> dict[str, Any]:
    decompressed = 0
    with gzip.open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            decompressed += len(chunk)
    return {"status": "PASS", "detail": f"gzip_crc=ok; decompressed_bytes={decompressed}"}


def validate_file(path: Path, suffix: str) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "NOT_APPLICABLE", "detail": "binary/unchecked format"}
    try:
        if path.stat().st_size == 0:
            return {"status": "WARN", "detail": "empty file"}
        if suffix == ".json":
            with path.open("r", encoding="utf-8-sig") as handle:
                value = json.load(handle)
            return {"status": "PASS", "detail": f"JSON root={type(value).__name__}"}
        if suffix == ".csv":
            return validate_csv(path, ",")
        if suffix == ".tsv":
            return validate_csv(path, "\t")
        if suffix == ".py":
            source, encoding = decode_text(path)
            compile(source, str(path), "exec")
            return {
                "status": "PASS",
                "detail": f"Python syntax=ok; encoding={encoding}; lines={source.count(chr(10)) + 1}",
            }
        if suffix in TEXT_EXTENSIONS or path.name in {"LICENSE", "README", "Makefile"}:
            text, encoding = decode_text(path)
            return {
                "status": "PASS",
                "detail": f"encoding={encoding}; lines={text.count(chr(10)) + 1}",
            }
        if suffix in {".zip", *OFFICE_EXTENSIONS}:
            return validate_zip(path, suffix)
        if suffix == ".pdf":
            return validate_pdf(path)
        if suffix in IMAGE_EXTENSIONS:
            return validate_image(path)
        if suffix == ".npz":
            return validate_npz(path)
        if suffix in {".tar", ".tgz"} or path.name.lower().endswith(".tar.gz"):
            return validate_tar(path)
        if suffix == ".gz":
            return validate_gzip(path)
        if suffix in HDF5_EXTENSIONS:
            return {
                "status": "DEFERRED",
                "detail": "HDF5 validation delegated to project_hdf5_health_audit.py",
            }
    except Exception as exc:  # Every failure belongs in the audit, not on stderr only.
        result = {"status": "FAIL", "detail": f"{type(exc).__name__}: {exc}"}
    return result


def text_findings(path: Path, suffix: str) -> list[dict[str, str]]:
    if suffix not in TEXT_EXTENSIONS and path.name not in {"LICENSE", "README", "Makefile"}:
        return []
    try:
        text, _ = decode_text(path)
    except Exception:
        return []
    findings: list[dict[str, str]] = []
    matches = sorted(set(ABSOLUTE_PATH_RE.findall(text)))
    if matches:
        findings.append(
            {
                "finding_type": "ABSOLUTE_WINDOWS_PATH",
                "severity": "REVIEW",
                "detail": (
                    f"count={len(matches)}; values redacted from the public audit because "
                    "they are machine-specific"
                ),
            }
        )
    if SENSITIVE_NAME_RE.search(path.name):
        findings.append(
            {
                "finding_type": "SENSITIVE_FILENAME",
                "severity": "REVIEW",
                "detail": "filename matches credential/secret/key pattern; content not reported",
            }
        )
    return findings


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    tracked, tracked_err = nul_paths(root, ["ls-files", "-z"])
    untracked, untracked_err = nul_paths(root, ["ls-files", "--others", "--exclude-standard", "-z"])
    ignored, ignored_err = nul_paths(
        root, ["ls-files", "--others", "--ignored", "--exclude-standard", "-z"]
    )

    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        current = Path(current_root)
        dirnames[:] = [name for name in dirnames if name != ".git"]
        if current == output or output in current.parents:
            dirnames[:] = []
            continue
        for filename in filenames:
            path = current / filename
            if path.is_file():
                files.append(path)
    files.sort(key=lambda value: value.relative_to(root).as_posix().lower())

    inventory: list[dict[str, Any]] = []
    health: list[dict[str, Any]] = []
    portability: list[dict[str, Any]] = []
    directory_bytes: Counter[str] = Counter()
    directory_files: Counter[str] = Counter()
    extension_bytes: Counter[str] = Counter()
    extension_files: Counter[str] = Counter()
    hash_groups: defaultdict[tuple[int, str], list[str]] = defaultdict(list)
    status_counts: Counter[str] = Counter()

    for index, path in enumerate(files, start=1):
        rel = path.relative_to(root).as_posix()
        stat = path.stat()
        suffix = path.suffix.lower() or "[no extension]"
        top_level = rel.split("/", 1)[0]
        if rel in tracked:
            git_state = "tracked"
        elif rel in ignored:
            git_state = "ignored-local"
        elif rel in untracked:
            git_state = "untracked"
        else:
            git_state = "outside-git-index-view"

        digest = sha256_file(path)
        validation = validate_file(path, path.suffix.lower())
        status_counts[validation["status"]] += 1
        row = {
            "relative_path": rel,
            "top_level": top_level,
            "extension": suffix,
            "bytes": stat.st_size,
            "mib": f"{stat.st_size / (1024 * 1024):.6f}",
            "sha256": digest,
            "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "git_state": git_state,
            "path_length": len(str(path)),
            "validation_status": validation["status"],
            "validation_detail": validation["detail"],
        }
        inventory.append(row)
        health.append(
            {
                "relative_path": rel,
                "extension": suffix,
                "bytes": stat.st_size,
                "status": validation["status"],
                "detail": validation["detail"],
            }
        )
        directory_bytes[top_level] += stat.st_size
        directory_files[top_level] += 1
        extension_bytes[suffix] += stat.st_size
        extension_files[suffix] += 1
        if stat.st_size >= int(args.duplicate_min_mib * 1024 * 1024):
            hash_groups[(stat.st_size, digest)].append(rel)

        if len(str(path)) > 240:
            portability.append(
                {
                    "relative_path": rel,
                    "finding_type": "LONG_WINDOWS_PATH",
                    "severity": "HIGH" if len(str(path)) >= 260 else "REVIEW",
                    "detail": f"absolute_path_length={len(str(path))}",
                }
            )
        for finding in text_findings(path, path.suffix.lower()):
            portability.append({"relative_path": rel, **finding})

        if index % 250 == 0 or index == len(files):
            print(f"[inventory] {index}/{len(files)} files", flush=True)

    directory_rows = [
        {
            "top_level": name,
            "files": directory_files[name],
            "bytes": directory_bytes[name],
            "gib": f"{directory_bytes[name] / (1024 ** 3):.6f}",
            "percent_bytes": f"{100 * directory_bytes[name] / max(1, sum(directory_bytes.values())):.3f}",
        }
        for name in sorted(directory_bytes, key=directory_bytes.get, reverse=True)
    ]
    extension_rows = [
        {
            "extension": name,
            "files": extension_files[name],
            "bytes": extension_bytes[name],
            "gib": f"{extension_bytes[name] / (1024 ** 3):.6f}",
        }
        for name in sorted(extension_bytes, key=extension_bytes.get, reverse=True)
    ]
    large_rows = sorted(
        [row for row in inventory if int(row["bytes"]) >= int(args.large_mib * 1024 * 1024)],
        key=lambda row: int(row["bytes"]),
        reverse=True,
    )
    duplicate_rows: list[dict[str, Any]] = []
    duplicate_group = 0
    reclaimable_bytes = 0
    for (size, digest), paths in sorted(hash_groups.items(), key=lambda item: item[0][0], reverse=True):
        if len(paths) < 2:
            continue
        duplicate_group += 1
        reclaimable_bytes += size * (len(paths) - 1)
        for rel in sorted(paths):
            duplicate_rows.append(
                {
                    "group": duplicate_group,
                    "bytes_each": size,
                    "mib_each": f"{size / (1024 * 1024):.6f}",
                    "copies": len(paths),
                    "sha256": digest,
                    "relative_path": rel,
                }
            )

    inventory_fields = [
        "relative_path",
        "top_level",
        "extension",
        "bytes",
        "mib",
        "sha256",
        "modified_utc",
        "git_state",
        "path_length",
        "validation_status",
        "validation_detail",
    ]
    write_csv(output / "FILE_INVENTORY.csv", inventory, inventory_fields)
    write_csv(
        output / "FORMAT_HEALTH_CHECKS.csv",
        health,
        ["relative_path", "extension", "bytes", "status", "detail"],
    )
    write_csv(
        output / "DIRECTORY_SIZE_SUMMARY.csv",
        directory_rows,
        ["top_level", "files", "bytes", "gib", "percent_bytes"],
    )
    write_csv(
        output / "EXTENSION_SUMMARY.csv",
        extension_rows,
        ["extension", "files", "bytes", "gib"],
    )
    write_csv(output / "LARGE_FILE_REGISTER.csv", large_rows, inventory_fields)
    write_csv(
        output / "DUPLICATE_LARGE_FILE_GROUPS.csv",
        duplicate_rows,
        ["group", "bytes_each", "mib_each", "copies", "sha256", "relative_path"],
    )
    write_csv(
        output / "PORTABILITY_FINDINGS.csv",
        portability,
        ["relative_path", "finding_type", "severity", "detail"],
    )

    summary = {
        "created_at": datetime.now().astimezone().isoformat(),
        "root": ".",
        "scope": "all regular files except .git and this audit output directory",
        "files": len(inventory),
        "bytes": sum(int(row["bytes"]) for row in inventory),
        "gib": sum(int(row["bytes"]) for row in inventory) / (1024 ** 3),
        "git_states": dict(Counter(row["git_state"] for row in inventory)),
        "validation_statuses": dict(status_counts),
        "large_files": len(large_rows),
        "duplicate_groups_ge_threshold": duplicate_group,
        "potential_duplicate_reclaimable_bytes": reclaimable_bytes,
        "portability_findings": len(portability),
        "long_paths_over_240": sum(
            1 for row in portability if row["finding_type"] == "LONG_WINDOWS_PATH"
        ),
        "git_command_stderr": {
            "tracked": tracked_err.strip(),
            "untracked": untracked_err.strip(),
            "ignored": ignored_err.strip(),
        },
        "thresholds": {
            "large_mib": args.large_mib,
            "duplicate_min_mib": args.duplicate_min_mib,
        },
    }
    (output / "AUDIT_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
