#!/usr/bin/env python3
"""Back up GitHub repository metadata, releases, assets and Git refs before recreation."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "1209433622cz-maker/sle-bcell-remodeling"
OUTPUT = ROOT / "8_archive" / "github_repository_recreation_2026-10-12"
RELEASES = ("v1.0.0", "v1.1.0")


def run(args: list[str], *, cwd: Path = ROOT) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8")
    return result.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    metadata_fields = ",".join(
        [
            "nameWithOwner",
            "visibility",
            "isPrivate",
            "defaultBranchRef",
            "url",
            "description",
            "createdAt",
            "updatedAt",
            "repositoryTopics",
            "homepageUrl",
            "hasIssuesEnabled",
            "hasProjectsEnabled",
            "hasWikiEnabled",
            "licenseInfo",
            "stargazerCount",
            "forkCount",
        ]
    )
    repository = json.loads(run(["gh", "repo", "view", REPOSITORY, "--json", metadata_fields]))
    releases = []
    for tag in RELEASES:
        payload = json.loads(
            run(
                [
                    "gh",
                    "release",
                    "view",
                    tag,
                    "--repo",
                    REPOSITORY,
                    "--json",
                    "tagName,name,body,isDraft,isPrerelease,publishedAt,assets",
                ]
            )
        )
        releases.append(payload)
        release_dir = OUTPUT / "releases" / tag
        release_dir.mkdir(parents=True, exist_ok=True)
        write_text(release_dir / "RELEASE_NOTES.md", payload["body"])
        write_text(release_dir / "RELEASE_METADATA.json", json.dumps(payload, indent=2, ensure_ascii=False))
        subprocess.run(
            ["gh", "release", "download", tag, "--repo", REPOSITORY, "--dir", str(release_dir), "--clobber"],
            cwd=ROOT,
            check=True,
        )

    issues = json.loads(
        run(["gh", "issue", "list", "--repo", REPOSITORY, "--state", "all", "--limit", "1000", "--json", "number,title,state,url"])
    )
    pull_requests = json.loads(
        run(["gh", "pr", "list", "--repo", REPOSITORY, "--state", "all", "--limit", "1000", "--json", "number,title,state,url"])
    )
    snapshot = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "repository": repository,
        "issues": issues,
        "pull_requests": pull_requests,
        "releases": releases,
    }
    write_text(OUTPUT / "GITHUB_REPOSITORY_METADATA_BEFORE_DELETE.json", json.dumps(snapshot, indent=2, ensure_ascii=False))
    write_text(OUTPUT / "REMOTE_REFS_BEFORE_DELETE.txt", run(["git", "ls-remote", "--heads", "--tags", "origin"]))
    write_text(OUTPUT / "LOCAL_REFS_BEFORE_DELETE.txt", run(["git", "show-ref", "--heads", "--tags"]))

    bundle = OUTPUT / "sle-bcell-remodeling_before_remote_recreation.bundle"
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=ROOT, check=True)
    bundle_verification = run(["git", "bundle", "verify", str(bundle)])
    write_text(OUTPUT / "GIT_BUNDLE_VERIFICATION.txt", bundle_verification)

    manifest_path = OUTPUT / "BACKUP_SHA256.csv"
    files = sorted(path for path in OUTPUT.rglob("*") if path.is_file() and path != manifest_path)
    rows = [
        {
            "relative_path": path.relative_to(OUTPUT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "bytes", "sha256"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    status = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_GITHUB_REPOSITORY_PREDELETE_BACKUP",
        "repository": REPOSITORY,
        "head": run(["git", "rev-parse", "HEAD"]).strip(),
        "release_count": len(releases),
        "release_asset_count": sum(len(release["assets"]) for release in releases),
        "issue_count": len(issues),
        "pull_request_count": len(pull_requests),
        "bundle": bundle.relative_to(ROOT).as_posix(),
        "bundle_bytes": bundle.stat().st_size,
        "manifest_files": len(rows),
    }
    write_text(OUTPUT / "BACKUP_STATUS.json", json.dumps(status, indent=2, ensure_ascii=False))
    print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
