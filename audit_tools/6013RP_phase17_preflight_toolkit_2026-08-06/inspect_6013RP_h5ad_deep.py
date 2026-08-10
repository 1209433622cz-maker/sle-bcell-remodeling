#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backed/lightweight deep inspection of all H5AD files in 6013RP-wyf.

Requires h5py. anndata is optional. The script does not load full expression
matrices into RAM and does not modify H5AD files.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

CANDIDATE_META_PATTERNS = (
    "donor", "patient", "subject", "sample", "library", "batch", "cohort",
    "disease", "condition", "status", "sledai", "treatment", "therapy",
    "sex", "gender", "age", "ethnicity", "cell_type", "celltype",
    "cluster", "leiden", "annotation", "study", "dataset",
)

def decode(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)

def attr(group, name: str, default=""):
    try:
        return decode(group.attrs.get(name, default))
    except Exception:
        return default

def get_index_length(group) -> int | None:
    if group is None:
        return None
    key = group.attrs.get("_index", "_index")
    key = decode(key)
    if key in group:
        return int(group[key].shape[0])
    if "_index" in group:
        return int(group["_index"].shape[0])
    return None

def list_keys(handle, key: str) -> list[str]:
    return sorted(list(handle[key].keys())) if key in handle else []

def read_categorical(group, key: str):
    obj = group[key]
    encoding = attr(obj, "encoding-type")
    if hasattr(obj, "keys") and "codes" in obj and "categories" in obj:
        codes = obj["codes"][:]
        cats = [decode(x) for x in obj["categories"][:]]
        counts = Counter()
        missing = 0
        for code in codes:
            i = int(code)
            if i < 0:
                missing += 1
            elif i < len(cats):
                counts[cats[i]] += 1
        return counts, missing, "categorical"
    return None

def read_vector_counts(group, key: str, max_unique: int = 5000):
    obj = group[key]
    cat = read_categorical(group, key)
    if cat:
        return cat
    if not hasattr(obj, "shape") or len(obj.shape) != 1:
        return Counter(), 0, "not_vector"
    arr = obj[:]
    counts = Counter()
    missing = 0
    for value in arr:
        if isinstance(value, float) and math.isnan(value):
            missing += 1
        else:
            counts[decode(value)] += 1
            if len(counts) > max_unique:
                return Counter(), missing, "too_many_unique"
    return counts, missing, "vector"

def inspect_matrix(group, label: str) -> dict[str, Any]:
    if group is None:
        return {"matrix": label, "present": False}
    result = {
        "matrix": label,
        "present": True,
        "encoding_type": attr(group, "encoding-type"),
        "encoding_version": attr(group, "encoding-version"),
        "shape": "",
        "dtype": "",
        "sample_min": "",
        "sample_max": "",
        "sample_integer_fraction": "",
        "sample_nonnegative": "",
        "message": "",
    }
    try:
        if hasattr(group, "shape"):
            result["shape"] = "x".join(map(str, group.shape))
            result["dtype"] = str(group.dtype)
            flat = group
            sample = flat[: min(10000, flat.shape[0])] if len(flat.shape) == 1 else flat[: min(100, flat.shape[0]), : min(100, flat.shape[1])]
        elif hasattr(group, "keys") and "data" in group:
            shape = group.attrs.get("shape", "")
            try:
                result["shape"] = "x".join(map(str, shape))
            except Exception:
                result["shape"] = decode(shape)
            data = group["data"]
            result["dtype"] = str(data.dtype)
            sample = data[: min(10000, data.shape[0])]
        else:
            result["message"] = "unsupported_matrix_layout"
            return result

        import numpy as np
        values = np.asarray(sample).ravel()
        values = values[np.isfinite(values)]
        if values.size:
            result["sample_min"] = float(values.min())
            result["sample_max"] = float(values.max())
            result["sample_integer_fraction"] = float(np.mean(np.isclose(values, np.round(values), atol=1e-8)))
            result["sample_nonnegative"] = bool(np.all(values >= 0))
    except Exception as exc:
        result["message"] = f"{type(exc).__name__}: {exc}"
    return result

def inspect_file(path: Path, root: Path, h5py) -> tuple[dict, list[dict], list[dict]]:
    summary = {
        "relative_path": path.relative_to(root).as_posix(),
        "size_gb": round(path.stat().st_size / 1024**3, 4),
        "status": "ok",
        "n_obs": "",
        "n_vars": "",
        "obs_columns": "",
        "var_columns": "",
        "layers": "",
        "obsm": "",
        "uns": "",
        "has_raw": False,
        "x_encoding": "",
        "message": "",
    }
    metadata_rows: list[dict] = []
    matrix_rows: list[dict] = []

    try:
        with h5py.File(path, "r") as f:
            obs = f.get("obs")
            var = f.get("var")
            summary["n_obs"] = get_index_length(obs) or ""
            summary["n_vars"] = get_index_length(var) or ""
            obs_keys = sorted(obs.keys()) if obs is not None else []
            var_keys = sorted(var.keys()) if var is not None else []
            summary["obs_columns"] = " | ".join(obs_keys)
            summary["var_columns"] = " | ".join(var_keys)
            summary["layers"] = " | ".join(list_keys(f, "layers"))
            summary["obsm"] = " | ".join(list_keys(f, "obsm"))
            summary["uns"] = " | ".join(list_keys(f, "uns"))
            summary["has_raw"] = "raw" in f
            summary["x_encoding"] = attr(f["X"], "encoding-type") if "X" in f else ""

            matrix_rows.append({
                "relative_path": summary["relative_path"],
                **inspect_matrix(f.get("X"), "X"),
            })
            if "raw" in f and "X" in f["raw"]:
                matrix_rows.append({
                    "relative_path": summary["relative_path"],
                    **inspect_matrix(f["raw"].get("X"), "raw/X"),
                })
            if "layers" in f:
                for key in sorted(f["layers"].keys()):
                    matrix_rows.append({
                        "relative_path": summary["relative_path"],
                        **inspect_matrix(f["layers"].get(key), f"layers/{key}"),
                    })

            if obs is not None:
                candidates = [
                    key for key in obs_keys
                    if any(pattern in key.lower() for pattern in CANDIDATE_META_PATTERNS)
                ]
                for key in candidates:
                    try:
                        counts, missing, mode = read_vector_counts(obs, key)
                        top = counts.most_common(100)
                        metadata_rows.append({
                            "relative_path": summary["relative_path"],
                            "column": key,
                            "read_mode": mode,
                            "n_unique": len(counts) if counts else "",
                            "missing_count": missing,
                            "top_value_counts_json": json.dumps(top, ensure_ascii=False),
                            "message": "",
                        })
                    except Exception as exc:
                        metadata_rows.append({
                            "relative_path": summary["relative_path"],
                            "column": key,
                            "read_mode": "error",
                            "n_unique": "",
                            "missing_count": "",
                            "top_value_counts_json": "",
                            "message": f"{type(exc).__name__}: {exc}",
                        })
    except Exception as exc:
        summary["status"] = "error"
        summary["message"] = f"{type(exc).__name__}: {exc}"
    return summary, metadata_rows, matrix_rows

def write_csv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def main() -> int:
    ap = argparse.ArgumentParser(description="Deep backed H5AD inspection")
    ap.add_argument("--root", default=r"H:\cuhk-2025fALL\6013RP-wyf")
    ap.add_argument("--output-dir", default="")
    args = ap.parse_args()

    try:
        import h5py
        import numpy
    except ImportError as exc:
        print("[ERROR] h5py and numpy are required.", file=sys.stderr)
        print("Install with: python -m pip install h5py numpy", file=sys.stderr)
        return 3

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"[ERROR] Project root not found: {root}", file=sys.stderr)
        return 2

    output_base = Path(args.output_dir).expanduser() if args.output_dir else root / "_phase17_h5ad_audit"
    run_dir = output_base / dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)

    paths = sorted(
        [p for p in root.rglob("*.h5ad") if "_project_audit" not in p.parts and "_phase17_" not in str(p)],
        key=lambda p: str(p).lower(),
    )
    print(f"[INFO] Found {len(paths)} H5AD files.")

    summaries, meta_rows, matrix_rows = [], [], []
    for i, path in enumerate(paths, 1):
        print(f"[H5AD] {i}/{len(paths)} {path}")
        summary, metadata, matrices = inspect_file(path, root, h5py)
        summaries.append(summary)
        meta_rows.extend(metadata)
        matrix_rows.extend(matrices)

    write_csv(
        run_dir / "01_h5ad_summary.csv",
        summaries,
        ["relative_path", "size_gb", "status", "n_obs", "n_vars", "obs_columns",
         "var_columns", "layers", "obsm", "uns", "has_raw", "x_encoding", "message"],
    )
    write_csv(
        run_dir / "02_h5ad_candidate_metadata_counts.csv",
        meta_rows,
        ["relative_path", "column", "read_mode", "n_unique", "missing_count",
         "top_value_counts_json", "message"],
    )
    write_csv(
        run_dir / "03_h5ad_matrix_sampling.csv",
        matrix_rows,
        ["relative_path", "matrix", "present", "encoding_type", "encoding_version",
         "shape", "dtype", "sample_min", "sample_max", "sample_integer_fraction",
         "sample_nonnegative", "message"],
    )

    report = f"""# H5AD deep audit

- Time: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}
- Project: `{root}`
- H5AD files: {len(paths)}
- Successful: {sum(x['status'] == 'ok' for x in summaries)}
- Failed: {sum(x['status'] != 'ok' for x in summaries)}

## Outputs

- `01_h5ad_summary.csv`
- `02_h5ad_candidate_metadata_counts.csv`
- `03_h5ad_matrix_sampling.csv`

The matrix check uses small samples only. Integer-like values are evidence about
a candidate count layer, not a formal proof that every matrix element is raw count data.
"""
    (run_dir / "00_H5AD_AUDIT_SUMMARY.md").write_text(report, encoding="utf-8")
    (run_dir / "WORKFLOW_H5AD_AUDIT.md").write_text(report, encoding="utf-8")
    (output_base / "_LATEST_H5AD_AUDIT.txt").write_text(
        f"run_dir={run_dir}\n", encoding="utf-8"
    )
    print(f"[SUCCESS] {run_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
