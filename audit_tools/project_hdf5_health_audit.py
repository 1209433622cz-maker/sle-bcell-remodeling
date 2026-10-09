#!/usr/bin/env python3
"""Validate all HDF5/H5AD containers in a workspace using h5py."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

import h5py


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--inventory",
        type=Path,
        help="Optional FILE_INVENTORY.csv used to avoid re-traversing long Windows paths.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    suffixes = {".h5", ".hdf5", ".h5ad"}
    if args.inventory:
        with args.inventory.open("r", encoding="utf-8-sig", newline="") as handle:
            inventory_rows = list(csv.DictReader(handle))
        paths = [
            root / row["relative_path"]
            for row in inventory_rows
            if Path(row["relative_path"]).suffix.lower() in suffixes
        ]
    else:
        discovered: list[Path] = []
        for current_root, dirnames, filenames in __import__("os").walk(root):
            dirnames[:] = [name for name in dirnames if name != ".git"]
            current = Path(current_root)
            discovered.extend(
                current / filename
                for filename in filenames
                if Path(filename).suffix.lower() in suffixes
            )
        paths = discovered
    paths.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    rows: list[dict[str, object]] = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        try:
            with h5py.File(path, "r") as handle:
                root_keys = list(handle.keys())
                object_count = 0

                def visitor(_name: str) -> None:
                    nonlocal object_count
                    object_count += 1

                handle.visit(visitor)
                detail = (
                    f"root_keys={','.join(root_keys[:20])}; objects={object_count}; "
                    f"attrs={len(handle.attrs)}"
                )
            status = "PASS"
        except Exception as exc:
            status = "FAIL"
            detail = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "relative_path": rel,
                "bytes": path.stat().st_size,
                "status": status,
                "detail": detail,
            }
        )
        print(f"[hdf5] {len(rows)}/{len(paths)} {status} {rel}", flush=True)

    csv_path = output / "HDF5_HEALTH_CHECKS.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["relative_path", "bytes", "status", "detail"]
        )
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "created_at": datetime.now().astimezone().isoformat(),
        "files": len(rows),
        "pass": sum(row["status"] == "PASS" for row in rows),
        "fail": sum(row["status"] == "FAIL" for row in rows),
    }
    (output / "HDF5_AUDIT_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 1 if summary["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
