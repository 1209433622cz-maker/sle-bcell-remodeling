"""Verify all indexed Git blobs, independent of checkout newline conversion."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from build_public_navigation import GENERATED
from verify_repository import ROOT, read_csv, safe_asset


def git_objects(root: Path) -> dict[str, str]:
    result = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=root,
                            check=True, capture_output=True)
    objects = {}
    for entry in result.stdout.decode("utf-8").split("\0"):
        if not entry:
            continue
        metadata, path = entry.split("\t", 1)
        mode, oid, stage = metadata.split()
        if stage != "0" or mode == "160000":
            raise ValueError(f"Unmerged path or unsupported submodule: {path}")
        if path not in GENERATED:
            objects[path] = oid
    return objects


def verify_inventory(root: Path, rows: list[dict] | None = None) -> dict:
    errors, checked, total = [], 0, 0
    try:
        root = root.resolve()
        if rows is None:
            rows = read_csv(root / "0_admin/PUBLIC_REPOSITORY_INDEX.csv")
        if not rows:
            raise ValueError("Empty Git inventory")
        objects = git_objects(root)
        seen, valid = set(), []
        for row in rows:
            path = row["path"]
            safe_asset(root, path)
            if path in seen:
                raise ValueError(f"Duplicate inventory path: {path}")
            seen.add(path)
            size, digest = int(row["bytes"]), row["sha256"]
            if size < 0 or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError(f"Invalid inventory metadata: {path}")
            if objects.get(path) != row["git_blob"]:
                errors.append(f"Git object identity changed: {path}")
            else:
                valid.append(row)
        if seen != objects.keys():
            errors.append(f"Inventory coverage mismatch: missing={len(objects.keys() - seen)}, extra={len(seen - objects.keys())}")
        cache = {}
        with subprocess.Popen(["git", "cat-file", "--batch"], cwd=root,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE) as reader:
            for row in valid:
                oid = row["git_blob"]
                if oid not in cache:
                    reader.stdin.write((oid + "\n").encode("ascii"))
                    reader.stdin.flush()
                    header = reader.stdout.readline().decode("ascii").split()
                    if len(header) != 3 or header[0] != oid or header[1] != "blob":
                        raise ValueError(f"Invalid Git blob response: {row['path']}")
                    size = remaining = int(header[2])
                    digest = hashlib.sha256()
                    while remaining:
                        chunk = reader.stdout.read(min(remaining, 1024 * 1024))
                        if not chunk:
                            raise ValueError("Truncated Git blob")
                        digest.update(chunk)
                        remaining -= len(chunk)
                    if reader.stdout.read(1) != b"\n":
                        raise ValueError("Invalid Git blob boundary")
                    cache[oid] = size, digest.hexdigest()
                size, digest = cache[oid]
                if size != int(row["bytes"]) or digest != row["sha256"]:
                    errors.append(f"Git blob size/hash mismatch: {row['path']}")
                checked += 1
                total += size
            reader.stdin.close()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    return {"status": "FAIL" if errors else "PASS", "indexed_payloads_checked": checked,
            "indexed_bytes": total, "errors": errors, "scope": "Git index blob bytes, not checkout EOL bytes",
            "self_exclusions": sorted(GENERATED), "scientific_pipeline_rerun": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = verify_inventory(args.root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
