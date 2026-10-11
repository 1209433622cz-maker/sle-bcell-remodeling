#!/usr/bin/env python3
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
