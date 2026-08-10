#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
6013RP-wyf 项目全量只读清点与可重复性审计工具

用途：
1. 对项目目录进行完整文件清点、目录统计和类型归类；
2. 查找重复文件、空文件、大文件、缓存/归档文件；
3. 检查 Python / R / Shell 代码语法；
4. 扫描脚本中的绝对路径、相对文件引用和疑似缺失输入；
5. 对单细胞数据、metadata、manuscript、figure、supplement 等资产专项建表；
6. 可选读取 H5AD、图像、PDF、Notebook 的轻量元数据；
7. 输出 Markdown 总报告及 CSV/JSON 结果，便于后续人工或 ChatGPT 继续核查。

脚本只读取项目内容；所有输出写入 <项目>\\_project_audit\\<时间戳>。
默认不会修改、移动或删除原项目文件。
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import tokenize
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Optional

SCRIPT_VERSION = "1.0.0"

COMPOUND_SUFFIXES = (
    ".fastq.gz", ".fq.gz", ".vcf.gz", ".bed.gz", ".mtx.gz",
    ".tar.gz", ".tar.bz2", ".tar.xz", ".csv.gz", ".tsv.gz",
)

CODE_EXTS = {
    ".py", ".r", ".rmd", ".qmd", ".ps1", ".sh", ".bash", ".zsh",
    ".ipynb", ".jl", ".m", ".sql", ".bat", ".cmd",
}
TEXT_EXTS = CODE_EXTS | {
    ".txt", ".md", ".rst", ".csv", ".tsv", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".conf", ".xml", ".html", ".htm", ".tex",
    ".gmt", ".bed", ".vcf", ".log",
}
TABLE_EXTS = {
    ".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".feather",
    ".ods", ".csv.gz", ".tsv.gz",
}
SINGLE_CELL_EXTS = {
    ".h5ad", ".h5", ".hdf5", ".loom", ".rds", ".rdata", ".mtx",
    ".mtx.gz", ".fastq.gz", ".fq.gz", ".bam", ".cram",
}
FIGURE_EXTS = {
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".svg", ".pdf", ".eps",
}
DOCUMENT_EXTS = {
    ".doc", ".docx", ".pdf", ".ppt", ".pptx", ".tex", ".md", ".rtf",
}
ARCHIVE_EXTS = {
    ".zip", ".7z", ".rar", ".tar", ".tar.gz", ".gz", ".bz2", ".xz",
}
CRITICAL_HASH_EXTS = (
    CODE_EXTS | TABLE_EXTS | FIGURE_EXTS | DOCUMENT_EXTS |
    {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".gmt", ".h5ad", ".rds"}
)

SKIP_TEXT_DIR_NAMES = {
    ".git", ".svn", ".hg", "__pycache__", ".ipynb_checkpoints",
    "node_modules", ".venv", "venv", "env", "renv", "packrat",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".idea", ".vscode",
    "_project_audit",
}
CACHE_OR_BUILD_NAMES = {
    "__pycache__", ".ipynb_checkpoints", ".cache", "cache", "caches",
    "tmp", "temp", "logs", "log", "build", "dist", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "node_modules", ".venv", "venv",
    "renv", "packrat",
}

PATH_FILE_EXT_RE = (
    r"(?:csv|tsv|txt|xlsx|xls|parquet|feather|h5ad|h5|hdf5|loom|"
    r"rds|rdata|mtx(?:\.gz)?|fastq(?:\.gz)?|fq(?:\.gz)?|bam|cram|"
    r"vcf(?:\.gz)?|bed(?:\.gz)?|gmt|json|yaml|yml|toml|pkl|pickle|"
    r"joblib|png|jpg|jpeg|tif|tiff|svg|eps|pdf|docx|pptx|zip|7z|"
    r"tar(?:\.gz)?|gz)"
)
QUOTED_PATH_RE = re.compile(
    rf"""(?P<quote>["'])(?P<path>[^"'<>|\r\n]+?\.{PATH_FILE_EXT_RE})(?P=quote)""",
    re.IGNORECASE,
)
WINDOWS_ABS_RE = re.compile(
    r"""(?<![A-Za-z0-9_])([A-Za-z]:[\\/][^"'<>|\r\n]+)"""
)
WSL_ABS_RE = re.compile(
    r"""(?<![A-Za-z0-9_])(/mnt/[A-Za-z]/[^"'<>|\r\n]+)"""
)
URL_RE = re.compile(r"^(?:https?|ftp)://", re.IGNORECASE)
DYNAMIC_TOKEN_RE = re.compile(r"[\$\{\}\*\?%]|<[^>]+>")

SINGLE_CELL_KEYWORDS = {
    "h5ad", "seurat", "scanpy", "anndata", "cellranger", "10x",
    "matrix", "barcodes", "features", "genes", "counts", "raw_count",
    "filtered_feature", "raw_feature", "metadata", "meta_data",
    "donor", "patient", "sample", "clinical", "sledai", "cohort", "batch",
    "cluster", "annotation", "celltype", "cell_type", "bcell", "b_cell",
    "pseudobulk", "scoda", "sccomp", "muscat", "edger", "deseq",
    "marker", "deg", "differential", "gsea", "pathway", "trajectory",
    "cellchat", "nichenet", "scrublet", "doublet", "ambient", "soupx",
}
MANUSCRIPT_KEYWORDS = {
    "manuscript", "article", "paper", "draft", "revision", "revised",
    "response", "cover_letter", "coverletter", "title_page",
}
FIGURE_KEYWORDS = {
    "figure", "fig", "panel", "suppfig", "supplementary_figure",
    "graphical_abstract", "workflow",
}
SUPPLEMENT_KEYWORDS = {
    "supplement", "supplementary", "additional_file", "source_data",
    "source-data", "extended_data",
}
SENSITIVE_NAME_PATTERNS = (
    ".env", "credential", "credentials", "secret", "secrets", "token",
    "apikey", "api_key", "private_key", "id_rsa", "password", "passwd",
)

EXPECTED_ROLES = [
    ("原始/计数层数据", ("raw", "count", "matrix", "h5ad", "rds", "10x")),
    ("供体/样本 metadata", ("metadata", "meta_data", "clinical", "donor", "sample_info")),
    ("分析代码", ("script", "code", "analysis", ".py", ".r")),
    ("环境锁定文件", ("environment.yml", "requirements.txt", "renv.lock", "conda", "dockerfile")),
    ("主手稿", ("manuscript", "article", "paper", ".docx", ".tex")),
    ("主图", ("figure", "fig", "main_figure")),
    ("补充材料", ("supplement", "additional_file", "extended_data")),
    ("结果表/源数据", ("result", "source_data", "source-data", "table")),
    ("运行记录/workflow", ("workflow", "runbook", "readme", "log")),
]


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def human_size(num: int | float) -> str:
    value = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(value) < 1024.0 or unit == "PB":
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} PB"


def compound_suffix(path: Path) -> str:
    name = path.name.lower()
    for suffix in COMPOUND_SUFFIXES:
        if name.endswith(suffix):
            return suffix
    return path.suffix.lower() or "[no_extension]"


def safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


def is_hidden_path(rel: Path) -> bool:
    return any(part.startswith(".") for part in rel.parts if part not in (".", ".."))


def top_dir(rel: Path) -> str:
    if len(rel.parts) <= 1:
        return "[project_root]"
    return rel.parts[0]


def classify_file(path: Path) -> str:
    ext = compound_suffix(path)
    name = path.name.lower()
    full = str(path).lower()

    if ext in CODE_EXTS:
        return "code"
    if ext in SINGLE_CELL_EXTS or any(k in name for k in SINGLE_CELL_KEYWORDS):
        return "single_cell_or_bioinformatics"
    if ext in TABLE_EXTS:
        return "table"
    if ext in FIGURE_EXTS or any(k in name for k in FIGURE_KEYWORDS):
        return "figure"
    if ext in DOCUMENT_EXTS or any(k in name for k in MANUSCRIPT_KEYWORDS):
        return "document"
    if ext in ARCHIVE_EXTS:
        return "archive"
    if any(part.lower() in CACHE_OR_BUILD_NAMES for part in path.parts):
        return "cache_or_build"
    if ext in {".log", ".out", ".err"}:
        return "log"
    if any(k in full for k in SUPPLEMENT_KEYWORDS):
        return "supplement"
    return "other"


def sha256_file(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, default=str)


def read_text_safely(path: Path, max_bytes: int) -> tuple[Optional[str], str]:
    try:
        if path.stat().st_size > max_bytes:
            return None, "skipped_too_large"
        try:
            with tokenize.open(path) as handle:
                return handle.read(), "ok"
        except Exception:
            raw = path.read_bytes()
            for encoding in ("utf-8-sig", "utf-8", "gb18030", "cp1252", "latin-1"):
                try:
                    return raw.decode(encoding), f"ok:{encoding}"
                except UnicodeDecodeError:
                    continue
            return None, "decode_failed"
    except Exception as exc:
        return None, f"read_failed:{type(exc).__name__}:{exc}"


def clean_reference(raw: str) -> str:
    value = raw.strip().strip(" \t,;)]}")
    value = value.replace("\\\\", "\\")
    # 去除常见参数尾部，但保留路径中的空格
    for marker in (" --", " -"):
        if marker in value and not re.match(r"^[A-Za-z]:[\\/]", value):
            value = value.split(marker, 1)[0].strip()
    return value


def wsl_to_windows(value: str) -> Optional[Path]:
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", value)
    if not match:
        return None
    drive = match.group(1).upper()
    tail = match.group(2).replace("/", "\\")
    return Path(f"{drive}:\\{tail}")


def resolve_reference(ref: str, source: Path, root: Path) -> tuple[str, str, str]:
    if URL_RE.match(ref):
        return "url", "", ""
    if DYNAMIC_TOKEN_RE.search(ref):
        return "dynamic_or_template", "", ""

    candidates: list[Path] = []
    normalized = os.path.expandvars(os.path.expanduser(ref))

    if re.match(r"^[A-Za-z]:[\\/]", normalized):
        candidates.append(Path(normalized))
    elif normalized.startswith("/mnt/"):
        converted = wsl_to_windows(normalized)
        if converted is not None:
            candidates.append(converted)
        candidates.append(Path(normalized))
    elif normalized.startswith("/"):
        candidates.append(Path(normalized))
    else:
        candidates.extend([source.parent / normalized, root / normalized])

    seen: set[str] = set()
    unique_candidates: list[Path] = []
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique_candidates.append(candidate)

    for candidate in unique_candidates:
        try:
            if candidate.exists():
                return "exists", str(candidate), ""
        except OSError:
            pass

    resolved = " | ".join(str(p) for p in unique_candidates)
    return "missing", resolved, "candidate_not_found"


def inspect_notebook(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "status": "not_checked",
        "cell_count": "",
        "code_cells": "",
        "markdown_cells": "",
        "error_outputs": "",
        "has_execution_counts": "",
        "message": "",
    }
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        cells = obj.get("cells", [])
        code_cells = [c for c in cells if c.get("cell_type") == "code"]
        markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
        error_outputs = 0
        executed = 0
        for cell in code_cells:
            if cell.get("execution_count") is not None:
                executed += 1
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    error_outputs += 1
        result.update({
            "status": "ok",
            "cell_count": len(cells),
            "code_cells": len(code_cells),
            "markdown_cells": len(markdown_cells),
            "error_outputs": error_outputs,
            "has_execution_counts": executed,
        })
    except Exception as exc:
        result.update(status="error", message=f"{type(exc).__name__}: {exc}")
    return result


def inspect_h5ad(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "status": "not_checked",
        "reader": "",
        "n_obs": "",
        "n_vars": "",
        "obs_columns": "",
        "var_columns": "",
        "layers": "",
        "obsm_keys": "",
        "uns_keys": "",
        "has_raw": "",
        "message": "",
    }
    try:
        import anndata as ad  # type: ignore
        adata = ad.read_h5ad(path, backed="r")
        result.update({
            "status": "ok",
            "reader": "anndata_backed",
            "n_obs": int(adata.n_obs),
            "n_vars": int(adata.n_vars),
            "obs_columns": " | ".join(map(str, list(adata.obs.columns))),
            "var_columns": " | ".join(map(str, list(adata.var.columns))),
            "layers": " | ".join(map(str, list(adata.layers.keys()))),
            "obsm_keys": " | ".join(map(str, list(adata.obsm.keys()))),
            "uns_keys": " | ".join(map(str, list(adata.uns.keys()))),
            "has_raw": adata.raw is not None,
        })
        try:
            adata.file.close()
        except Exception:
            pass
        return result
    except ImportError:
        pass
    except Exception as exc:
        result["message"] = f"anndata_failed:{type(exc).__name__}:{exc}"

    try:
        import h5py  # type: ignore
        with h5py.File(path, "r") as handle:
            n_obs = ""
            n_vars = ""
            if "obs" in handle and "_index" in handle["obs"]:
                n_obs = int(handle["obs"]["_index"].shape[0])
            if "var" in handle and "_index" in handle["var"]:
                n_vars = int(handle["var"]["_index"].shape[0])
            result.update({
                "status": "partial",
                "reader": "h5py",
                "n_obs": n_obs,
                "n_vars": n_vars,
                "obs_columns": " | ".join(handle["obs"].keys()) if "obs" in handle else "",
                "var_columns": " | ".join(handle["var"].keys()) if "var" in handle else "",
                "layers": " | ".join(handle["layers"].keys()) if "layers" in handle else "",
                "obsm_keys": " | ".join(handle["obsm"].keys()) if "obsm" in handle else "",
                "uns_keys": " | ".join(handle["uns"].keys()) if "uns" in handle else "",
                "has_raw": "raw" in handle,
            })
        return result
    except ImportError:
        result.update(
            status="skipped",
            reader="",
            message=(result["message"] + " | " if result["message"] else "")
            + "未安装 anndata/h5py，仅记录文件本身。",
        )
    except Exception as exc:
        result.update(
            status="error",
            reader="h5py",
            message=(result["message"] + " | " if result["message"] else "")
            + f"h5py_failed:{type(exc).__name__}:{exc}",
        )
    return result


def inspect_image(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "status": "not_checked",
        "format": "",
        "width_px": "",
        "height_px": "",
        "dpi_x": "",
        "dpi_y": "",
        "mode": "",
        "message": "",
    }
    try:
        from PIL import Image  # type: ignore
        with Image.open(path) as image:
            width, height = image.size
            dpi = image.info.get("dpi", ("", ""))
            if not isinstance(dpi, (tuple, list)):
                dpi = ("", "")
            result.update({
                "status": "ok",
                "format": image.format or "",
                "width_px": width,
                "height_px": height,
                "dpi_x": dpi[0] if len(dpi) > 0 else "",
                "dpi_y": dpi[1] if len(dpi) > 1 else "",
                "mode": image.mode,
            })
    except ImportError:
        result.update(status="skipped", message="未安装 Pillow。")
    except Exception as exc:
        result.update(status="error", message=f"{type(exc).__name__}: {exc}")
    return result


def inspect_pdf(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "status": "not_checked",
        "pages": "",
        "encrypted": "",
        "message": "",
    }
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        result.update(
            status="ok",
            pages=len(reader.pages),
            encrypted=bool(reader.is_encrypted),
        )
    except ImportError:
        result.update(status="skipped", message="未安装 pypdf。")
    except Exception as exc:
        result.update(status="error", message=f"{type(exc).__name__}: {exc}")
    return result


def build_tree(root: Path, excluded_root: Path, max_depth: int, max_entries: int) -> str:
    lines = [str(root)]
    count = 0

    def walk(current: Path, prefix: str, depth: int) -> None:
        nonlocal count
        if depth > max_depth or count >= max_entries:
            return
        try:
            entries = sorted(
                [p for p in current.iterdir() if not _is_within(p, excluded_root)],
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except Exception as exc:
            lines.append(prefix + f"[无法访问: {type(exc).__name__}: {exc}]")
            return

        for idx, entry in enumerate(entries):
            if count >= max_entries:
                lines.append(prefix + "└── [达到 tree-max-entries，已截断]")
                return
            count += 1
            connector = "└── " if idx == len(entries) - 1 else "├── "
            marker = "/" if entry.is_dir() else ""
            lines.append(prefix + connector + entry.name + marker)
            if entry.is_dir() and depth < max_depth:
                extension = "    " if idx == len(entries) - 1 else "│   "
                walk(entry, prefix + extension, depth + 1)

    walk(root, "", 1)
    return "\n".join(lines) + "\n"


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False


def find_executable(names: Iterable[str]) -> Optional[str]:
    for name in names:
        resolved = shutil.which(name)
        if resolved:
            return resolved
    return None


def markdown_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]], limit: int = 20) -> str:
    if not rows:
        return "_无记录_"
    subset = rows[:limit]
    header = "| " + " | ".join(title for _, title in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, sep]
    for row in subset:
        values = []
        for key, _ in columns:
            value = str(row.get(key, "")).replace("|", "\\|").replace("\n", " ")
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append(f"\n_仅显示前 {limit} 条；完整结果见 CSV。_")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="6013RP-wyf 项目全量只读清点与可重复性审计"
    )
    parser.add_argument(
        "--root",
        default=r"H:\cuhk-2025fALL\6013RP-wyf",
        help="项目根目录，默认 H:\\cuhk-2025fALL\\6013RP-wyf",
    )
    parser.add_argument(
        "--output-root",
        default="",
        help="审计输出根目录；默认 <root>\\_project_audit",
    )
    parser.add_argument(
        "--hash-mode",
        choices=("none", "smart", "all"),
        default="smart",
        help="none=不计算；smart=关键文件及同尺寸候选；all=阈值内全部文件",
    )
    parser.add_argument(
        "--max-hash-gb",
        type=float,
        default=20.0,
        help="单文件哈希上限，默认 20 GB",
    )
    parser.add_argument(
        "--max-text-mb",
        type=float,
        default=20.0,
        help="脚本引用扫描和语法检查的单文本文件上限，默认 20 MB",
    )
    parser.add_argument(
        "--large-file-gb",
        type=float,
        default=1.0,
        help="大文件阈值，默认 1 GB",
    )
    parser.add_argument(
        "--tree-depth",
        type=int,
        default=6,
        help="目录树最大深度，默认 6",
    )
    parser.add_argument(
        "--tree-max-entries",
        type=int,
        default=10000,
        help="目录树最大条目数，默认 10000",
    )
    parser.add_argument(
        "--skip-r-parse",
        action="store_true",
        help="跳过 Rscript parse 语法检查",
    )
    parser.add_argument(
        "--skip-h5ad",
        action="store_true",
        help="跳过 H5AD 轻量元数据读取",
    )
    parser.add_argument(
        "--skip-media",
        action="store_true",
        help="跳过图像/PDF元数据读取",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示更详细进度",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser()
    try:
        root = root.resolve()
    except Exception:
        root = Path(os.path.abspath(str(root)))

    if not root.exists() or not root.is_dir():
        print(f"[ERROR] 项目目录不存在或不是目录：{root}", file=sys.stderr)
        return 2

    output_base = (
        Path(args.output_root).expanduser()
        if args.output_root
        else root / "_project_audit"
    )
    output_base.mkdir(parents=True, exist_ok=True)
    stamp = now_stamp()
    output_dir = output_base / stamp
    output_dir.mkdir(parents=True, exist_ok=False)

    print(f"[INFO] 项目根目录：{root}")
    print(f"[INFO] 审计输出目录：{output_dir}")
    print("[INFO] 开始只读扫描……")

    start_time = time.time()
    errors: list[dict[str, Any]] = []
    file_rows: list[dict[str, Any]] = []
    dir_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"file_count": 0, "total_bytes": 0, "dir_count": 0}
    )
    file_paths: list[Path] = []

    for current_str, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current = Path(current_str)

        # 永久排除审计输出目录，避免结果递归进入下一次扫描
        dirs[:] = [
            d for d in dirs
            if not _is_within(current / d, output_base)
        ]

        rel_current = Path(".") if current == root else current.relative_to(root)
        current_key = str(rel_current)
        dir_stats[current_key]["dir_count"] += len(dirs)

        for filename in files:
            path = current / filename
            if _is_within(path, output_base):
                continue
            try:
                stat = path.stat()
                rel = path.relative_to(root)
                ext = compound_suffix(path)
                category = classify_file(path)
                row = {
                    "relative_path": str(rel),
                    "absolute_path": str(path),
                    "name": path.name,
                    "extension": ext,
                    "category": category,
                    "top_directory": top_dir(rel),
                    "parent_directory": str(rel.parent),
                    "depth": len(rel.parts) - 1,
                    "size_bytes": int(stat.st_size),
                    "size_human": human_size(stat.st_size),
                    "modified_time": dt.datetime.fromtimestamp(
                        stat.st_mtime, tz=dt.datetime.now().astimezone().tzinfo
                    ).isoformat(timespec="seconds"),
                    "created_time": dt.datetime.fromtimestamp(
                        stat.st_ctime, tz=dt.datetime.now().astimezone().tzinfo
                    ).isoformat(timespec="seconds"),
                    "is_hidden": is_hidden_path(rel),
                    "is_symlink": path.is_symlink(),
                    "sha256": "",
                    "hash_status": "not_requested",
                }
                file_rows.append(row)
                file_paths.append(path)

                # 把文件计入其所有父目录汇总
                for i in range(0, len(rel.parts)):
                    parent_key = "." if i == 0 else str(Path(*rel.parts[:i]))
                    dir_stats[parent_key]["file_count"] += 1
                    dir_stats[parent_key]["total_bytes"] += stat.st_size
            except Exception as exc:
                errors.append({
                    "stage": "stat",
                    "path": str(path),
                    "error": f"{type(exc).__name__}: {exc}",
                })

    print(f"[INFO] 已发现 {len(file_rows):,} 个文件。")

    # 目录、扩展名及分类汇总
    extension_counter: dict[str, dict[str, int]] = defaultdict(
        lambda: {"file_count": 0, "total_bytes": 0}
    )
    category_counter: dict[str, dict[str, int]] = defaultdict(
        lambda: {"file_count": 0, "total_bytes": 0}
    )
    for row in file_rows:
        extension_counter[row["extension"]]["file_count"] += 1
        extension_counter[row["extension"]]["total_bytes"] += row["size_bytes"]
        category_counter[row["category"]]["file_count"] += 1
        category_counter[row["category"]]["total_bytes"] += row["size_bytes"]

    extension_rows = sorted(
        [
            {
                "extension": ext,
                "file_count": values["file_count"],
                "total_bytes": values["total_bytes"],
                "total_size": human_size(values["total_bytes"]),
            }
            for ext, values in extension_counter.items()
        ],
        key=lambda x: (-x["total_bytes"], x["extension"]),
    )
    category_rows = sorted(
        [
            {
                "category": category,
                "file_count": values["file_count"],
                "total_bytes": values["total_bytes"],
                "total_size": human_size(values["total_bytes"]),
            }
            for category, values in category_counter.items()
        ],
        key=lambda x: (-x["total_bytes"], x["category"]),
    )
    directory_rows = sorted(
        [
            {
                "relative_directory": directory,
                "direct_subdirectory_count": values["dir_count"],
                "recursive_file_count": values["file_count"],
                "recursive_total_bytes": values["total_bytes"],
                "recursive_total_size": human_size(values["total_bytes"]),
            }
            for directory, values in dir_stats.items()
        ],
        key=lambda x: (-x["recursive_total_bytes"], x["relative_directory"]),
    )

    # 哈希
    size_groups: dict[int, list[int]] = defaultdict(list)
    for idx, row in enumerate(file_rows):
        size_groups[row["size_bytes"]].append(idx)

    max_hash_bytes = int(args.max_hash_gb * (1024 ** 3))
    smart_always_bytes = 64 * 1024 * 1024
    hash_indices: list[int] = []
    if args.hash_mode != "none":
        for idx, row in enumerate(file_rows):
            ext = row["extension"]
            size = row["size_bytes"]
            duplicate_size_candidate = len(size_groups[size]) > 1 and size > 0
            should_hash = False
            if size <= max_hash_bytes:
                if args.hash_mode == "all":
                    should_hash = True
                elif (
                    size <= smart_always_bytes
                    or ext in CRITICAL_HASH_EXTS
                    or duplicate_size_candidate
                ):
                    should_hash = True
            if should_hash:
                hash_indices.append(idx)
            else:
                file_rows[idx]["hash_status"] = (
                    "skipped_over_limit" if size > max_hash_bytes else "skipped_by_mode"
                )

    if hash_indices:
        print(f"[INFO] 计算 SHA-256：{len(hash_indices):,} 个文件。")
        for pos, idx in enumerate(hash_indices, start=1):
            path = Path(file_rows[idx]["absolute_path"])
            try:
                file_rows[idx]["sha256"] = sha256_file(path)
                file_rows[idx]["hash_status"] = "ok"
            except Exception as exc:
                file_rows[idx]["hash_status"] = f"error:{type(exc).__name__}:{exc}"
                errors.append({
                    "stage": "hash",
                    "path": str(path),
                    "error": f"{type(exc).__name__}: {exc}",
                })
            if args.verbose and (pos % 100 == 0 or pos == len(hash_indices)):
                print(f"  [HASH] {pos:,}/{len(hash_indices):,}")
    else:
        print("[INFO] 未请求或没有符合条件的 SHA-256 计算。")

    # 重复文件
    hash_groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in file_rows:
        if row["sha256"]:
            hash_groups[(row["size_bytes"], row["sha256"])].append(row)

    duplicate_rows: list[dict[str, Any]] = []
    duplicate_group_id = 0
    for (size, digest), group in sorted(
        hash_groups.items(), key=lambda item: (-item[0][0], item[0][1])
    ):
        if len(group) < 2:
            continue
        duplicate_group_id += 1
        for row in group:
            duplicate_rows.append({
                "duplicate_group": duplicate_group_id,
                "group_file_count": len(group),
                "size_bytes": size,
                "size_human": human_size(size),
                "sha256": digest,
                "relative_path": row["relative_path"],
                "absolute_path": row["absolute_path"],
            })

    # 特殊清单
    large_threshold = int(args.large_file_gb * (1024 ** 3))
    largest_rows = sorted(file_rows, key=lambda x: x["size_bytes"], reverse=True)
    large_rows = [r for r in largest_rows if r["size_bytes"] >= large_threshold]
    empty_rows = [r for r in file_rows if r["size_bytes"] == 0]

    cache_archive_rows: list[dict[str, Any]] = []
    for row in file_rows:
        path_parts_lower = [p.lower() for p in Path(row["relative_path"]).parts]
        reasons = []
        if row["extension"] in ARCHIVE_EXTS:
            reasons.append("archive")
        if any(part in CACHE_OR_BUILD_NAMES for part in path_parts_lower):
            reasons.append("cache_or_build")
        if row["name"].lower().endswith((".tmp", ".temp", ".bak", ".old", "~")):
            reasons.append("temporary_or_backup")
        if reasons:
            cache_archive_rows.append({
                "relative_path": row["relative_path"],
                "size_bytes": row["size_bytes"],
                "size_human": row["size_human"],
                "reason": " | ".join(sorted(set(reasons))),
            })

    sensitive_rows = []
    for row in file_rows:
        lower_name = row["name"].lower()
        if any(pattern in lower_name for pattern in SENSITIVE_NAME_PATTERNS):
            sensitive_rows.append({
                "relative_path": row["relative_path"],
                "size_human": row["size_human"],
                "reason": "文件名可能包含密钥、令牌或凭据；仅报告路径，不读取内容。",
            })

    # 代码语法检查
    max_text_bytes = int(args.max_text_mb * 1024 * 1024)
    python_syntax_rows: list[dict[str, Any]] = []
    python_files = [
        Path(r["absolute_path"]) for r in file_rows if r["extension"] == ".py"
    ]
    print(f"[INFO] Python 语法检查：{len(python_files):,} 个文件。")
    for path in python_files:
        row = {
            "relative_path": safe_rel(path, root),
            "status": "",
            "line": "",
            "column": "",
            "message": "",
        }
        try:
            if path.stat().st_size > max_text_bytes:
                row.update(status="skipped_too_large", message=f">{args.max_text_mb} MB")
            else:
                with tokenize.open(path) as handle:
                    source = handle.read()
                ast.parse(source, filename=str(path))
                row["status"] = "ok"
        except SyntaxError as exc:
            row.update(
                status="syntax_error",
                line=exc.lineno or "",
                column=exc.offset or "",
                message=exc.msg,
            )
        except Exception as exc:
            row.update(status="error", message=f"{type(exc).__name__}: {exc}")
        python_syntax_rows.append(row)

    r_syntax_rows: list[dict[str, Any]] = []
    r_files = [
        Path(r["absolute_path"])
        for r in file_rows
        if r["extension"] in {".r", ".rmd", ".qmd"}
    ]
    rscript = find_executable(("Rscript", "Rscript.exe"))
    if args.skip_r_parse:
        rscript = None
    print(
        f"[INFO] R 语法检查：{len(r_files):,} 个文件；"
        + ("已找到 Rscript。" if rscript else "未执行（未找到 Rscript 或已跳过）。")
    )
    for path in r_files:
        row = {
            "relative_path": safe_rel(path, root),
            "status": "",
            "message": "",
        }
        if not rscript:
            row.update(status="skipped", message="Rscript unavailable or skipped")
        elif path.stat().st_size > max_text_bytes:
            row.update(status="skipped_too_large", message=f">{args.max_text_mb} MB")
        else:
            try:
                r_path = str(path).replace("\\", "/").replace("'", "\\'")
                proc = subprocess.run(
                    [rscript, "-e", f"parse(file='{r_path}')"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                )
                if proc.returncode == 0:
                    row["status"] = "ok"
                else:
                    message = (proc.stderr or proc.stdout).strip()
                    row.update(status="parse_error", message=message[-4000:])
            except Exception as exc:
                row.update(status="error", message=f"{type(exc).__name__}: {exc}")
        r_syntax_rows.append(row)

    shell_syntax_rows: list[dict[str, Any]] = []
    bash = find_executable(("bash", "bash.exe"))
    shell_files = [
        Path(r["absolute_path"])
        for r in file_rows
        if r["extension"] in {".sh", ".bash"}
    ]
    print(
        f"[INFO] Shell 语法检查：{len(shell_files):,} 个文件；"
        + ("已找到 bash。" if bash else "未执行（未找到 bash）。")
    )
    for path in shell_files:
        row = {
            "relative_path": safe_rel(path, root),
            "status": "",
            "message": "",
        }
        if not bash:
            row.update(status="skipped", message="bash unavailable")
        else:
            try:
                proc = subprocess.run(
                    [bash, "-n", str(path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                )
                if proc.returncode == 0:
                    row["status"] = "ok"
                else:
                    row.update(
                        status="syntax_error",
                        message=(proc.stderr or proc.stdout).strip()[-4000:],
                    )
            except Exception as exc:
                row.update(status="error", message=f"{type(exc).__name__}: {exc}")
        shell_syntax_rows.append(row)

    # Notebook
    notebook_rows = [
        inspect_notebook(Path(r["absolute_path"]))
        for r in file_rows
        if r["extension"] == ".ipynb"
    ]
    for row in notebook_rows:
        row["path"] = safe_rel(Path(row["path"]), root)

    # 引用和硬编码路径扫描
    reference_rows: list[dict[str, Any]] = []
    hardcoded_rows: list[dict[str, Any]] = []
    text_scan_rows: list[dict[str, Any]] = []
    seen_ref_records: set[tuple[str, str, str]] = set()

    scan_candidates = []
    for row in file_rows:
        ext = row["extension"]
        rel_parts = {p.lower() for p in Path(row["relative_path"]).parts}
        if ext in TEXT_EXTS and not (rel_parts & SKIP_TEXT_DIR_NAMES):
            scan_candidates.append(Path(row["absolute_path"]))

    print(f"[INFO] 脚本/文本路径引用扫描：{len(scan_candidates):,} 个文件。")
    for path in scan_candidates:
        text, read_status = read_text_safely(path, max_text_bytes)
        text_scan_rows.append({
            "relative_path": safe_rel(path, root),
            "status": read_status,
            "size_human": human_size(path.stat().st_size) if path.exists() else "",
        })
        if text is None:
            continue

        candidates: list[tuple[str, str]] = []
        for match in QUOTED_PATH_RE.finditer(text):
            candidates.append(("quoted_path", match.group("path")))
        for match in WINDOWS_ABS_RE.finditer(text):
            candidates.append(("windows_absolute", match.group(1)))
        for match in WSL_ABS_RE.finditer(text):
            candidates.append(("wsl_absolute", match.group(1)))

        for kind, raw_ref in candidates:
            ref = clean_reference(raw_ref)
            if not ref or len(ref) > 1000:
                continue
            key = (safe_rel(path, root), kind, ref)
            if key in seen_ref_records:
                continue
            seen_ref_records.add(key)
            status, resolved, note = resolve_reference(ref, path, root)
            record = {
                "source_file": safe_rel(path, root),
                "reference_kind": kind,
                "reference": ref,
                "status": status,
                "resolved_candidates": resolved,
                "note": note,
            }
            reference_rows.append(record)
            if kind in {"windows_absolute", "wsl_absolute"}:
                hardcoded_rows.append(record.copy())

    missing_reference_rows = [r for r in reference_rows if r["status"] == "missing"]
    dynamic_reference_rows = [
        r for r in reference_rows if r["status"] == "dynamic_or_template"
    ]

    # 单细胞和文稿/图件专项资产
    single_cell_rows: list[dict[str, Any]] = []
    document_figure_rows: list[dict[str, Any]] = []
    for row in file_rows:
        rel_lower = row["relative_path"].lower()
        name_lower = row["name"].lower()
        ext = row["extension"]

        sc_reasons = []
        if ext in SINGLE_CELL_EXTS:
            sc_reasons.append(f"extension:{ext}")
        matches = sorted(k for k in SINGLE_CELL_KEYWORDS if k in rel_lower)
        if matches:
            sc_reasons.append("keywords:" + ",".join(matches[:12]))
        if sc_reasons:
            if any(k in rel_lower for k in ("metadata", "clinical", "donor", "sample")):
                asset_type = "metadata_or_clinical"
            elif ext in {".h5ad", ".h5", ".hdf5", ".loom", ".rds", ".rdata"}:
                asset_type = "single_cell_object"
            elif ext in {".mtx", ".mtx.gz", ".fastq.gz", ".fq.gz", ".bam", ".cram"}:
                asset_type = "raw_or_count_data"
            elif ext in CODE_EXTS:
                asset_type = "analysis_code"
            elif ext in TABLE_EXTS:
                asset_type = "result_or_intermediate_table"
            else:
                asset_type = "related_asset"
            single_cell_rows.append({
                "relative_path": row["relative_path"],
                "asset_type": asset_type,
                "extension": ext,
                "size_human": row["size_human"],
                "modified_time": row["modified_time"],
                "reason": " | ".join(sc_reasons),
            })

        doc_reasons = []
        if ext in DOCUMENT_EXTS:
            doc_reasons.append(f"document_extension:{ext}")
        if ext in FIGURE_EXTS:
            doc_reasons.append(f"figure_extension:{ext}")
        if any(k in rel_lower for k in MANUSCRIPT_KEYWORDS):
            doc_reasons.append("manuscript_keyword")
        if any(k in rel_lower for k in FIGURE_KEYWORDS):
            doc_reasons.append("figure_keyword")
        if any(k in rel_lower for k in SUPPLEMENT_KEYWORDS):
            doc_reasons.append("supplement_keyword")
        if doc_reasons:
            if any(k in rel_lower for k in MANUSCRIPT_KEYWORDS):
                asset_type = "manuscript_or_submission"
            elif any(k in rel_lower for k in SUPPLEMENT_KEYWORDS):
                asset_type = "supplement_or_source_data"
            elif ext in FIGURE_EXTS:
                asset_type = "figure"
            else:
                asset_type = "document"
            document_figure_rows.append({
                "relative_path": row["relative_path"],
                "asset_type": asset_type,
                "extension": ext,
                "size_human": row["size_human"],
                "modified_time": row["modified_time"],
                "reason": " | ".join(doc_reasons),
            })

    # H5AD、图片、PDF 轻量检查
    h5ad_rows: list[dict[str, Any]] = []
    if not args.skip_h5ad:
        h5ad_paths = [
            Path(r["absolute_path"])
            for r in file_rows
            if r["extension"] == ".h5ad"
        ]
        print(f"[INFO] H5AD 轻量元数据检查：{len(h5ad_paths):,} 个文件。")
        for path in h5ad_paths:
            result = inspect_h5ad(path)
            result["path"] = safe_rel(Path(result["path"]), root)
            h5ad_rows.append(result)

    image_rows: list[dict[str, Any]] = []
    pdf_rows: list[dict[str, Any]] = []
    if not args.skip_media:
        image_paths = [
            Path(r["absolute_path"])
            for r in file_rows
            if r["extension"] in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
        ]
        pdf_paths = [
            Path(r["absolute_path"])
            for r in file_rows
            if r["extension"] == ".pdf"
        ]
        print(
            f"[INFO] 媒体元数据检查：图片 {len(image_paths):,}，PDF {len(pdf_paths):,}。"
        )
        for path in image_paths:
            result = inspect_image(path)
            result["path"] = safe_rel(Path(result["path"]), root)
            image_rows.append(result)
        for path in pdf_paths:
            result = inspect_pdf(path)
            result["path"] = safe_rel(Path(result["path"]), root)
            pdf_rows.append(result)

    # 预期角色检查：使用全部相对路径和文件名进行宽松命中，避免强绑定某种目录命名
    searchable = "\n".join(r["relative_path"].lower() for r in file_rows)
    expected_rows = []
    for role, needles in EXPECTED_ROLES:
        matched = []
        for row in file_rows:
            text = row["relative_path"].lower()
            if any(needle in text for needle in needles):
                matched.append(row["relative_path"])
        expected_rows.append({
            "expected_role": role,
            "status": "FOUND" if matched else "NOT_FOUND",
            "match_count": len(matched),
            "examples": " | ".join(matched[:10]),
            "note": (
                "宽松关键词命中，不等同于内容真实性确认。"
                if matched
                else "需要人工确认是否采用其他命名，或确实缺失。"
            ),
        })

    # Git 和环境
    environment_lines = [
        f"audit_timestamp={iso_now()}",
        f"script_version={SCRIPT_VERSION}",
        f"project_root={root}",
        f"output_directory={output_dir}",
        f"platform={platform.platform()}",
        f"python_executable={sys.executable}",
        f"python_version={sys.version.replace(os.linesep, ' ')}",
        f"hostname={platform.node()}",
        f"hash_mode={args.hash_mode}",
        f"max_hash_gb={args.max_hash_gb}",
        f"max_text_mb={args.max_text_mb}",
    ]
    for exe_name in ("git", "Rscript", "bash", "pandoc", "quarto", "conda"):
        environment_lines.append(f"{exe_name}={find_executable((exe_name, exe_name + '.exe')) or 'NOT_FOUND'}")

    git_status_text = "Git repository not detected.\n"
    git_dir = root / ".git"
    git_exe = find_executable(("git", "git.exe"))
    if git_dir.exists() and git_exe:
        commands = [
            ("status", [git_exe, "-C", str(root), "status", "--short", "--branch"]),
            ("remote", [git_exe, "-C", str(root), "remote", "-v"]),
            ("last_commit", [git_exe, "-C", str(root), "log", "-1", "--decorate", "--stat"]),
        ]
        chunks = []
        for title, command in commands:
            try:
                proc = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=60,
                )
                chunks.append(f"### {title}\n{proc.stdout.strip()}\n")
            except Exception as exc:
                chunks.append(f"### {title}\nERROR: {type(exc).__name__}: {exc}\n")
        git_status_text = "\n".join(chunks)

    # 输出 CSV/JSON/TXT
    manifest_fields = [
        "relative_path", "absolute_path", "name", "extension", "category",
        "top_directory", "parent_directory", "depth", "size_bytes", "size_human",
        "modified_time", "created_time", "is_hidden", "is_symlink", "sha256",
        "hash_status",
    ]
    write_csv(output_dir / "01_file_manifest.csv", file_rows, manifest_fields)
    write_csv(
        output_dir / "02_directory_summary.csv",
        directory_rows,
        [
            "relative_directory", "direct_subdirectory_count",
            "recursive_file_count", "recursive_total_bytes", "recursive_total_size",
        ],
    )
    write_csv(
        output_dir / "03_extension_summary.csv",
        extension_rows,
        ["extension", "file_count", "total_bytes", "total_size"],
    )
    write_csv(
        output_dir / "04_category_summary.csv",
        category_rows,
        ["category", "file_count", "total_bytes", "total_size"],
    )
    write_csv(
        output_dir / "05_largest_files.csv",
        largest_rows,
        manifest_fields,
    )
    write_csv(
        output_dir / "06_large_files_over_threshold.csv",
        large_rows,
        manifest_fields,
    )
    write_csv(
        output_dir / "07_duplicate_files.csv",
        duplicate_rows,
        [
            "duplicate_group", "group_file_count", "size_bytes", "size_human",
            "sha256", "relative_path", "absolute_path",
        ],
    )
    write_csv(
        output_dir / "08_empty_files.csv",
        empty_rows,
        manifest_fields,
    )
    write_csv(
        output_dir / "09_python_syntax.csv",
        python_syntax_rows,
        ["relative_path", "status", "line", "column", "message"],
    )
    write_csv(
        output_dir / "10_R_syntax.csv",
        r_syntax_rows,
        ["relative_path", "status", "message"],
    )
    write_csv(
        output_dir / "11_shell_syntax.csv",
        shell_syntax_rows,
        ["relative_path", "status", "message"],
    )
    write_csv(
        output_dir / "12_notebook_audit.csv",
        notebook_rows,
        [
            "path", "status", "cell_count", "code_cells", "markdown_cells",
            "error_outputs", "has_execution_counts", "message",
        ],
    )
    write_csv(
        output_dir / "13_all_path_references.csv",
        reference_rows,
        [
            "source_file", "reference_kind", "reference", "status",
            "resolved_candidates", "note",
        ],
    )
    write_csv(
        output_dir / "14_missing_path_references.csv",
        missing_reference_rows,
        [
            "source_file", "reference_kind", "reference", "status",
            "resolved_candidates", "note",
        ],
    )
    write_csv(
        output_dir / "15_hardcoded_absolute_paths.csv",
        hardcoded_rows,
        [
            "source_file", "reference_kind", "reference", "status",
            "resolved_candidates", "note",
        ],
    )
    write_csv(
        output_dir / "16_dynamic_path_references.csv",
        dynamic_reference_rows,
        [
            "source_file", "reference_kind", "reference", "status",
            "resolved_candidates", "note",
        ],
    )
    write_csv(
        output_dir / "17_text_scan_status.csv",
        text_scan_rows,
        ["relative_path", "status", "size_human"],
    )
    write_csv(
        output_dir / "18_single_cell_assets.csv",
        single_cell_rows,
        [
            "relative_path", "asset_type", "extension", "size_human",
            "modified_time", "reason",
        ],
    )
    write_csv(
        output_dir / "19_manuscript_figure_assets.csv",
        document_figure_rows,
        [
            "relative_path", "asset_type", "extension", "size_human",
            "modified_time", "reason",
        ],
    )
    write_csv(
        output_dir / "20_h5ad_metadata.csv",
        h5ad_rows,
        [
            "path", "status", "reader", "n_obs", "n_vars", "obs_columns",
            "var_columns", "layers", "obsm_keys", "uns_keys", "has_raw", "message",
        ],
    )
    write_csv(
        output_dir / "21_image_metadata.csv",
        image_rows,
        [
            "path", "status", "format", "width_px", "height_px",
            "dpi_x", "dpi_y", "mode", "message",
        ],
    )
    write_csv(
        output_dir / "22_pdf_metadata.csv",
        pdf_rows,
        ["path", "status", "pages", "encrypted", "message"],
    )
    write_csv(
        output_dir / "23_expected_structure_check.csv",
        expected_rows,
        ["expected_role", "status", "match_count", "examples", "note"],
    )
    write_csv(
        output_dir / "24_cache_archive_candidates.csv",
        cache_archive_rows,
        ["relative_path", "size_bytes", "size_human", "reason"],
    )
    write_csv(
        output_dir / "25_sensitive_filename_candidates.csv",
        sensitive_rows,
        ["relative_path", "size_human", "reason"],
    )
    write_csv(
        output_dir / "26_audit_errors.csv",
        errors,
        ["stage", "path", "error"],
    )

    tree_text = build_tree(
        root=root,
        excluded_root=output_base,
        max_depth=max(1, args.tree_depth),
        max_entries=max(100, args.tree_max_entries),
    )
    (output_dir / "27_project_tree.txt").write_text(tree_text, encoding="utf-8")
    (output_dir / "28_environment.txt").write_text(
        "\n".join(environment_lines) + "\n", encoding="utf-8"
    )
    (output_dir / "29_git_status.txt").write_text(git_status_text, encoding="utf-8")

    summary_json = {
        "audit_timestamp": iso_now(),
        "script_version": SCRIPT_VERSION,
        "project_root": str(root),
        "output_directory": str(output_dir),
        "file_count": len(file_rows),
        "directory_count": len(dir_stats),
        "total_bytes": sum(r["size_bytes"] for r in file_rows),
        "total_size": human_size(sum(r["size_bytes"] for r in file_rows)),
        "large_file_count": len(large_rows),
        "empty_file_count": len(empty_rows),
        "duplicate_group_count": duplicate_group_id,
        "duplicate_file_count": len(duplicate_rows),
        "missing_reference_count": len(missing_reference_rows),
        "hardcoded_absolute_path_count": len(hardcoded_rows),
        "python_syntax_error_count": sum(
            r["status"] == "syntax_error" for r in python_syntax_rows
        ),
        "r_parse_error_count": sum(
            r["status"] == "parse_error" for r in r_syntax_rows
        ),
        "shell_syntax_error_count": sum(
            r["status"] == "syntax_error" for r in shell_syntax_rows
        ),
        "single_cell_asset_count": len(single_cell_rows),
        "manuscript_figure_asset_count": len(document_figure_rows),
        "h5ad_count": len(h5ad_rows),
        "audit_error_count": len(errors),
        "elapsed_seconds": round(time.time() - start_time, 2),
    }
    write_json(output_dir / "30_audit_summary.json", summary_json)

    # Markdown 总报告
    py_errors = [r for r in python_syntax_rows if r["status"] == "syntax_error"]
    r_errors = [r for r in r_syntax_rows if r["status"] == "parse_error"]
    shell_errors = [r for r in shell_syntax_rows if r["status"] == "syntax_error"]
    missing_roles = [r for r in expected_rows if r["status"] != "FOUND"]

    report = f"""# 6013RP-wyf 项目全量清点与可重复性审计

- 审计时间：{summary_json["audit_timestamp"]}
- 脚本版本：{SCRIPT_VERSION}
- 项目根目录：`{root}`
- 输出目录：`{output_dir}`
- 运行原则：**只读扫描，不修改原项目内容**

## 1. 总体规模

| 指标 | 数值 |
| --- | ---: |
| 文件总数 | {len(file_rows):,} |
| 目录记录数 | {len(dir_stats):,} |
| 项目总大小 | {summary_json["total_size"]} |
| ≥ {args.large_file_gb:g} GB 的大文件 | {len(large_rows):,} |
| 空文件 | {len(empty_rows):,} |
| 重复文件组 | {duplicate_group_id:,} |
| 重复文件条目 | {len(duplicate_rows):,} |
| 单细胞/生信相关资产 | {len(single_cell_rows):,} |
| 手稿/图件/补充材料资产 | {len(document_figure_rows):,} |
| 审计过程错误 | {len(errors):,} |
| 用时 | {summary_json["elapsed_seconds"]:.2f} 秒 |

## 2. 需要优先人工复核的风险

1. **疑似缺失路径引用：{len(missing_reference_rows):,} 条。**  
   正则扫描会有少量误报，但它能快速暴露脚本中已经移动、未提供或路径拼接错误的输入文件。

2. **硬编码 Windows/WSL 绝对路径：{len(hardcoded_rows):,} 条。**  
   建议后续统一改为项目根目录参数、配置文件或相对路径，避免换机器后失效。

3. **代码语法问题：**
   - Python syntax error：{len(py_errors):,}
   - R parse error：{len(r_errors):,}
   - Shell syntax error：{len(shell_errors):,}

4. **空文件：{len(empty_rows):,} 个；缓存、压缩包或备份候选：{len(cache_archive_rows):,} 个。**

5. **角色级宽松检查未命中：{len(missing_roles):,} 项。**  
   该检查仅根据名称和路径判断；“FOUND”不代表数据真实性或方法正确，“NOT_FOUND”也可能只是命名不同。

## 3. 项目类型构成

{markdown_table(category_rows, [("category", "类别"), ("file_count", "文件数"), ("total_size", "总大小")], limit=30)}

## 4. 扩展名构成（按体积）

{markdown_table(extension_rows, [("extension", "扩展名"), ("file_count", "文件数"), ("total_size", "总大小")], limit=30)}

## 5. 最大文件

{markdown_table(largest_rows, [("relative_path", "相对路径"), ("size_human", "大小"), ("category", "类别"), ("modified_time", "修改时间")], limit=30)}

## 6. 预期项目角色检查

{markdown_table(expected_rows, [("expected_role", "角色"), ("status", "状态"), ("match_count", "命中数"), ("examples", "示例")], limit=30)}

## 7. Python 语法错误

{markdown_table(py_errors, [("relative_path", "文件"), ("line", "行"), ("column", "列"), ("message", "错误")], limit=50)}

## 8. R 解析错误

{markdown_table(r_errors, [("relative_path", "文件"), ("message", "错误")], limit=50)}

## 9. 疑似缺失的路径引用

{markdown_table(missing_reference_rows, [("source_file", "来源脚本"), ("reference", "引用路径"), ("resolved_candidates", "尝试解析位置")], limit=50)}

## 10. 重复文件

{markdown_table(duplicate_rows, [("duplicate_group", "组"), ("size_human", "大小"), ("relative_path", "文件")], limit=50)}

## 11. 单细胞专项检查建议

本次脚本会建立 `18_single_cell_assets.csv` 和 `20_h5ad_metadata.csv`。后续方法学重构应优先确认：

1. 原始计数层是否真实存在，是否仍保留 `raw counts`、基因名和细胞条形码；
2. donor、sample、library、processing cohort、disease、SLEDAI、treatment 等字段能否一一对应；
3. 同一 donor 是否多次采样或跨多个 library/cohort，统计模型的独立单位是否正确；
4. discovery 与 validation 数据能否使用冻结的状态模型映射；
5. 现有图表和手稿数字是否都能追溯到脚本、源表和输入对象。

## 12. 建议你回传给我的文件

为便于继续推进，优先将本次生成的整个审计目录压缩后上传。至少应包含：

- `00_AUDIT_SUMMARY.md`
- `01_file_manifest.csv`
- `14_missing_path_references.csv`
- `15_hardcoded_absolute_paths.csv`
- `18_single_cell_assets.csv`
- `19_manuscript_figure_assets.csv`
- `20_h5ad_metadata.csv`
- `23_expected_structure_check.csv`
- `27_project_tree.txt`
- `30_audit_summary.json`

## 13. 输出文件索引

- `01_file_manifest.csv`：所有文件、大小、时间、类别、SHA-256
- `02_directory_summary.csv`：目录递归规模
- `03_extension_summary.csv`：扩展名统计
- `04_category_summary.csv`：资产类别统计
- `05_largest_files.csv`：按体积排序的完整清单
- `07_duplicate_files.csv`：内容完全相同的文件
- `09_python_syntax.csv` / `10_R_syntax.csv` / `11_shell_syntax.csv`
- `14_missing_path_references.csv`：疑似缺失输入/输出引用
- `15_hardcoded_absolute_paths.csv`：硬编码绝对路径
- `18_single_cell_assets.csv`：单细胞、生信、metadata 相关资产
- `19_manuscript_figure_assets.csv`：手稿、图件、补充材料
- `20_h5ad_metadata.csv`：H5AD 的维度、obs/var/layers/obsm/uns
- `21_image_metadata.csv`：图片像素和 DPI
- `22_pdf_metadata.csv`：PDF 页数
- `23_expected_structure_check.csv`：角色级结构检查
- `27_project_tree.txt`：目录树
- `28_environment.txt`：运行环境
- `29_git_status.txt`：Git 状态
- `30_audit_summary.json`：机器可读摘要

## 14. 限制说明

- 路径引用使用静态正则扫描，动态拼接路径可能被标记为 `dynamic_or_template`，少量普通字符串可能误判为文件路径。
- H5AD 只做 backed/轻量元数据读取，不加载表达矩阵到内存。
- `FOUND` 只代表名称或路径命中，不能替代原始数据真实性、统计方法和生物学结论的人工复核。
- 哈希模式 `{args.hash_mode}` 下，超过 {args.max_hash_gb:g} GB 的单文件不会计算 SHA-256。
"""
    (output_dir / "00_AUDIT_SUMMARY.md").write_text(report, encoding="utf-8")

    # 每次运行自动生成独立 workflow
    workflow = f"""# Workflow：6013RP-wyf 项目清点

- 时间：{summary_json["audit_timestamp"]}
- 项目：`{root}`
- 审计脚本版本：{SCRIPT_VERSION}
- 输出：`{output_dir}`

## 已执行

1. 递归文件与目录清点；
2. 文件类别、扩展名、大小和修改时间汇总；
3. `{args.hash_mode}` 模式 SHA-256 与重复文件识别；
4. Python / R / Shell 静态语法检查；
5. 脚本中的相对路径、Windows 路径和 WSL 路径扫描；
6. 单细胞数据、metadata、手稿、主图和补充材料专项归类；
7. H5AD、Notebook、图片和 PDF 轻量元数据检查；
8. Git 和运行环境记录。

## 关键计数

- 文件：{len(file_rows):,}
- 总大小：{summary_json["total_size"]}
- 疑似缺失引用：{len(missing_reference_rows):,}
- 重复组：{duplicate_group_id:,}
- Python 语法错误：{len(py_errors):,}
- R 解析错误：{len(r_errors):,}
- 单细胞相关资产：{len(single_cell_rows):,}

## 下一步

将本次审计目录压缩并上传，用于建立“原始输入—分析脚本—结果表—图件—手稿陈述”的全链路追踪矩阵，再决定 Phase 17/v7 重跑的实际入口。
"""
    (output_dir / "31_WORKFLOW_RECORD.md").write_text(workflow, encoding="utf-8")

    # 写 latest 指针，便于找到最近一次结果
    latest_text = (
        f"latest_audit={output_dir}\n"
        f"summary={output_dir / '00_AUDIT_SUMMARY.md'}\n"
        f"timestamp={summary_json['audit_timestamp']}\n"
    )
    (output_base / "_LATEST_AUDIT.txt").write_text(latest_text, encoding="utf-8")

    print("[SUCCESS] 审计完成。")
    print(f"[SUCCESS] 总报告：{output_dir / '00_AUDIT_SUMMARY.md'}")
    print(f"[SUCCESS] 最近结果指针：{output_base / '_LATEST_AUDIT.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
