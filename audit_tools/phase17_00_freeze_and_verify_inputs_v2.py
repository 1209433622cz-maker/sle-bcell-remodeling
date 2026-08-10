#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, json, os
from pathlib import Path
from typing import Any

def decode(x: Any) -> str:
    return x.decode("utf-8", errors="replace") if isinstance(x, bytes) else str(x)

def resolve(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else root / value.replace("\\", os.sep).replace("/", os.sep)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(16 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--discovery", default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad")
    args = ap.parse_args()

    import h5py, numpy as np
    root = Path(args.project_root).resolve()
    src = resolve(root, args.discovery)
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    if not src.is_file():
        raise FileNotFoundError(src)

    result = {
        "path": str(src), "size_bytes": src.stat().st_size, "sha256": sha256(src),
        "n_obs": "", "n_vars": "", "has_raw": False, "raw_encoding": "",
        "raw_integer_fraction": "", "raw_nonnegative": "", "status": "ok", "message": ""
    }
    try:
        with h5py.File(src, "r") as f:
            obs, raw = f["obs"], f["raw"]
            idx = decode(obs.attrs.get("_index", "_index"))
            result["n_obs"] = int(obs[idx].shape[0])
            var = raw["var"]
            vidx = decode(var.attrs.get("_index", "_index"))
            result["n_vars"] = int(var[vidx].shape[0]) if hasattr(var[vidx], "shape") else ""
            x = raw["X"]
            result["has_raw"] = True
            result["raw_encoding"] = decode(x.attrs.get("encoding-type", ""))
            data = x["data"][:min(200000, x["data"].shape[0])] if hasattr(x, "keys") and "data" in x else x[:100, :100].ravel()
            data = np.asarray(data); data = data[np.isfinite(data)]
            result["raw_integer_fraction"] = float(np.mean(np.isclose(data, np.round(data), atol=1e-8)))
            result["raw_nonnegative"] = bool(np.all(data >= 0))
    except Exception as exc:
        result["status"] = "error"; result["message"] = f"{type(exc).__name__}: {exc}"

    with (out / "00_input_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=result.keys()); w.writeheader(); w.writerow(result)
    (out / "00_input_manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = result["status"] == "ok" and result["has_raw"] and result["raw_nonnegative"] is True and float(result["raw_integer_fraction"] or 0) >= 0.999
    summary = f"""# Gate C1-00 input freeze v2

- Time: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}
- Source: `{src}`
- SHA-256: `{result['sha256']}`
- n_obs: {result['n_obs']}
- n_vars: {result['n_vars']}
- raw/X present: {result['has_raw']}
- raw sample integer fraction: {result['raw_integer_fraction']}
- raw sample nonnegative: {result['raw_nonnegative']}
- Gate: {'PASS' if passed else 'FAIL'}

Source was read only.
"""
    (out / "00_INPUT_FREEZE_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)
    return 0 if passed else 3

if __name__ == "__main__":
    raise SystemExit(main())
