#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 17 Gate C1-00: freeze and verify authoritative inputs.

Read-only for source files. Produces SHA-256, H5AD structure and sampled
raw-count integrity checks. It never modifies the source H5AD.
"""

from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

def sha256_file(path: Path, block=16 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(block)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def decode(x: Any) -> str:
    return x.decode("utf-8", errors="replace") if isinstance(x, bytes) else str(x)

def inspect_h5ad(path: Path) -> dict:
    import h5py
    import numpy as np
    result = {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "n_obs": "",
        "n_vars": "",
        "has_raw": False,
        "raw_x_encoding": "",
        "raw_x_shape": "",
        "raw_sample_min": "",
        "raw_sample_max": "",
        "raw_sample_integer_fraction": "",
        "raw_sample_nonnegative": "",
        "obs_columns": "",
        "raw_var_columns": "",
        "status": "ok",
        "message": "",
    }
    try:
        with h5py.File(path, "r") as f:
            obs = f.get("obs")
            raw = f.get("raw")
            raw_var = raw.get("var") if raw is not None else None
            idx_key = decode(obs.attrs.get("_index", "_index")) if obs is not None else "_index"
            if obs is not None and idx_key in obs:
                result["n_obs"] = int(obs[idx_key].shape[0])
            if raw_var is not None:
                vkey = decode(raw_var.attrs.get("_index", "_index"))
                if vkey in raw_var:
                    result["n_vars"] = int(raw_var[vkey].shape[0])
            result["has_raw"] = raw is not None and "X" in raw
            result["obs_columns"] = " | ".join(sorted(obs.keys())) if obs is not None else ""
            result["raw_var_columns"] = " | ".join(sorted(raw_var.keys())) if raw_var is not None else ""
            if not result["has_raw"]:
                raise RuntimeError("raw/X is missing")

            x = raw["X"]
            result["raw_x_encoding"] = decode(x.attrs.get("encoding-type", ""))
            shape = x.attrs.get("shape", "")
            result["raw_x_shape"] = "x".join(map(str, shape)) if hasattr(shape, "__len__") else str(shape)

            if hasattr(x, "keys") and "data" in x:
                data = x["data"][: min(200000, x["data"].shape[0])]
            else:
                data = x[: min(200, x.shape[0]), : min(200, x.shape[1])].ravel()
            data = np.asarray(data)
            data = data[np.isfinite(data)]
            if data.size:
                result["raw_sample_min"] = float(data.min())
                result["raw_sample_max"] = float(data.max())
                result["raw_sample_integer_fraction"] = float(
                    np.mean(np.isclose(data, np.round(data), atol=1e-8))
                )
                result["raw_sample_nonnegative"] = bool(np.all(data >= 0))
    except Exception as exc:
        result["status"] = "error"
        result["message"] = f"{type(exc).__name__}: {exc}"
    return result

def resolve_project_path(root: Path, value: str) -> Path:
    """Resolve Windows- or POSIX-style project-relative paths."""
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    normalized = value.replace("\\", os.sep).replace("/", os.sep)
    return root / normalized

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=r"H:\cuhk-2025fALL\6013RP-wyf")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument(
        "--discovery",
        default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad",
    )
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    source = resolve_project_path(root, args.discovery)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    if not source.is_file():
        print(f"[ERROR] Missing discovery H5AD: {source}", file=sys.stderr)
        return 2

    result = inspect_h5ad(source)
    with (output / "00_input_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(result.keys()))
        w.writeheader()
        w.writerow(result)
    (output / "00_input_manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    passed = (
        result["status"] == "ok"
        and result["has_raw"]
        and result["raw_sample_nonnegative"] is True
        and float(result["raw_sample_integer_fraction"] or 0) >= 0.999
    )
    summary = f"""# Gate C1-00 input freeze

- Time: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}
- Source: `{source}`
- SHA-256: `{result['sha256']}`
- n_obs: {result['n_obs']}
- n_vars: {result['n_vars']}
- raw/X present: {result['has_raw']}
- raw sample integer fraction: {result['raw_sample_integer_fraction']}
- raw sample nonnegative: {result['raw_sample_nonnegative']}
- Gate: {'PASS' if passed else 'FAIL'}

The source file was read only and was not modified.
"""
    (output / "00_INPUT_FREEZE_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)
    return 0 if passed else 3

if __name__ == "__main__":
    raise SystemExit(main())
