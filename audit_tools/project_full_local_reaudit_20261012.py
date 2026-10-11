#!/usr/bin/env python3
"""Perform a full current-workspace audit, including the organized view."""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from project_organization_20261012 import (
    duplicate_tables,
    git_ignored,
    git_tracked,
    inspect_one,
    summarize_inventory,
    write_csv,
)


DATE = "2026-10-12"
OUTPUT_REL = "9_version/full_local_reaudit_2026-10-12"


def scan_files(root: Path) -> list[Path]:
    files: list[Path] = []
    output = (root / OUTPUT_REL).resolve()
    for current, directories, names in os.walk(root):
        current_path = Path(current)
        directories[:] = [
            name
            for name in directories
            if name != ".git" and (current_path / name).resolve() != output
        ]
        files.extend(current_path / name for name in names)
    return sorted(files)


def value_role(relative_path: str) -> str:
    path = relative_path.lower()
    if path.startswith("6_release/sle_bcell_submission_package_2026-10-12"):
        return "current_submission_package"
    if path == "6_release/sle_bcell_submission_package_2026-10-12.zip":
        return "current_submission_package"
    if path.startswith("5_manuscript/current/") or "20261011_stagek_limited_integration" in path:
        return "current_stagek_manuscript"
    if path.startswith("4_figures/fig") and "/canonical/" in path:
        return "current_main_figure"
    if path.startswith("4_figures/supplementary/current/"):
        return "current_supplementary_figure"
    if any(token in path for token in ["stageg_final_synthetic", "stagei_single_real", "stagel_external_cohort", "stagem_raw_pipeline"]):
        return "rp_v4_decisive_evidence"
    if path.startswith("7_report/action_records/") or path.startswith("05_record/"):
        return "work_and_action_record"
    if path.startswith("0_admin/") or path in {"readme.md", "reproducibility.md", "citation.cff", "license"}:
        return "governance_and_navigation"
    if path.startswith("8_archive/github_repository_recreation_2026-10-12/"):
        return "github_recreation_backup"
    if path.startswith("9_version/"):
        return "inventory_and_integrity"
    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = root / OUTPUT_REL
    output.mkdir(parents=True, exist_ok=True)

    print("[1/5] Enumerating current local project files...", flush=True)
    files = scan_files(root)
    rel_paths = [path.relative_to(root).as_posix() for path in files]
    tracked = git_tracked(root)
    ignored = git_ignored(root, [path for path in rel_paths if path not in tracked])
    print(f"      Files discovered: {len(files):,}", flush=True)

    print("[2/5] Hashing and validating file contents...", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(lambda path: inspect_one(root, path, tracked, ignored), files))

    print("[3/5] Resolving duplicate groups...", flush=True)
    duplicate_rows, duplicate_lookup = duplicate_tables(rows)
    for row in rows:
        group, copies = duplicate_lookup.get(str(row["relative_path"]), ("", 1))
        row["duplicate_group"] = group
        row["duplicate_copies"] = copies
        row["value_role"] = value_role(str(row["relative_path"]))

    fields = list(rows[0])
    write_csv(output / f"FULL_LOCAL_FILE_INVENTORY_{DATE}.csv", rows, fields=fields)
    write_csv(output / f"TOP_LEVEL_SIZE_SUMMARY_{DATE}.csv", summarize_inventory(rows, "top_level"))
    write_csv(output / f"FILE_TYPE_SUMMARY_{DATE}.csv", summarize_inventory(rows, "extension"))
    write_csv(output / f"GIT_STATE_SUMMARY_{DATE}.csv", summarize_inventory(rows, "git_state"))
    write_csv(output / f"CONTENT_CHECK_SUMMARY_{DATE}.csv", summarize_inventory(rows, "content_check"))
    write_csv(output / f"DUPLICATE_GROUPS_{DATE}.csv", duplicate_rows)
    write_csv(
        output / f"CONTENT_CHECK_EXCEPTIONS_{DATE}.csv",
        [row for row in rows if row["content_check"] != "PASS"],
        fields=fields,
    )
    write_csv(
        output / f"VALUABLE_ASSET_REGISTER_{DATE}.csv",
        [row for row in rows if row["value_role"]],
        fields=fields,
    )

    print("[4/5] Building value and storage summaries...", flush=True)
    role_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    for row in rows:
        if row["value_role"]:
            role_counts[str(row["value_role"])]["files"] += 1
            role_counts[str(row["value_role"])]["bytes"] += int(row["bytes"])
    redundant_bytes = sum(int(row["redundant_bytes"]) for row in duplicate_rows)
    holds = [row for row in rows if row["content_check"] == "HOLD"]
    failures = [row for row in rows if row["content_check"] == "FAIL"]
    status = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "HOLD_CONTENT_FAILURES_PRESENT",
        "scope": "all regular project files except .git internals and this audit output directory",
        "files": len(rows),
        "bytes": sum(int(row["bytes"]) for row in rows),
        "gib": round(sum(int(row["bytes"]) for row in rows) / (1024**3), 6),
        "tracked": sum(row["git_state"] == "tracked" for row in rows),
        "ignored_local": sum(row["git_state"] == "ignored_local" for row in rows),
        "untracked": sum(row["git_state"] == "untracked" for row in rows),
        "content_pass": sum(row["content_check"] == "PASS" for row in rows),
        "content_hold": len(holds),
        "content_fail": len(failures),
        "duplicate_groups": len(duplicate_rows),
        "theoretical_redundant_bytes": redundant_bytes,
        "valuable_asset_roles": dict(sorted(role_counts.items())),
    }
    (output / f"FULL_LOCAL_AUDIT_STATUS_{DATE}.json").write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    readme = [
        "# Full local workspace reaudit",
        "",
        f"Date: {DATE}",
        "",
        "Scope: all regular project files except .git internals and this audit output directory.",
        "",
        f"- Files: {status['files']:,}",
        f"- Bytes: {status['bytes']:,} ({status['gib']:.3f} GiB)",
        f"- Content PASS/HOLD/FAIL: {status['content_pass']:,}/{status['content_hold']:,}/{status['content_fail']:,}",
        f"- Duplicate groups: {status['duplicate_groups']:,}",
        f"- Theoretical redundant bytes: {status['theoretical_redundant_bytes']:,}",
        f"- Decision: {status['status']}",
        "",
        "The full inventory records original path, SHA-256, size, Git state, content validation, lifecycle, value tier, visual ownership, duplicate group and value role.",
    ]
    (output / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8", newline="\n")
    print("[5/5] Full current-workspace audit complete.", flush=True)
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
