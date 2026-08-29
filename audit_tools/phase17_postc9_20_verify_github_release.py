"""Verify the public GitHub v1.1.0 release and its frozen assets."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
UPLOAD = ROOT / "04_submission/zenodo_release/upload"
RELEASE = ROOT / "00_project_management/qiteng_r2_release_2026-08-29"
REPOSITORY = "1209433622cz-maker/sle-bcell-remodeling"
TAG = "v1.1.0"
CONTENT_COMMIT = "f1859ff8498d5569a1d5027b36ed18c8b7c7536f"
TITLE = "SLE B-cell remodeling reproducibility release"
USER_AGENT = "SLE-Bcell-release-verifier/1.0"


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(url):
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise ValueError(f"Unexpected HTTP status {response.status}: {url}")
        return json.loads(response.read().decode("utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=RELEASE / "github_release_verification.json"
    )
    args = parser.parse_args()
    output = args.output.resolve()
    require(
        output.is_relative_to((ROOT / "00_project_management").resolve()),
        "Receipt must remain in project management",
    )

    api_root = f"https://api.github.com/repos/{REPOSITORY}"
    release = read_json(f"{api_root}/releases/tags/{TAG}")
    require(release["tag_name"] == TAG, "Release tag differs")
    require(release["name"] == TITLE, "Release title differs")
    require(release["draft"] is False, "Release remains a draft")
    require(release["prerelease"] is False, "Release is marked as a prerelease")
    require(release["html_url"].endswith(f"/releases/tag/{TAG}"), "Release URL differs")
    for phrase in (
        "10.5281/zenodo.22151739",
        CONTENT_COMMIT,
        "R1 remains HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY",
        "C9R remains HOLD_C9A_PREFREEZE_REVIEW_REQUIRED",
        "no corrected external disease effects were estimated",
        "now resolves to a tombstone",
    ):
        require(phrase in release["body"], "Missing release boundary: " + phrase)

    expected = {}
    for name in ("Research_Archive.zip", "Source_Code.zip", "SHA256SUMS.txt"):
        path = UPLOAD / name
        expected[name] = {"bytes": path.stat().st_size, "sha256": checksum(path)}
    assets = {asset["name"]: asset for asset in release["assets"]}
    require(set(assets) == set(expected), "Release asset inventory differs")
    verified_assets = {}
    for name, local in expected.items():
        asset = assets[name]
        require(asset["state"] == "uploaded", "Asset is not uploaded: " + name)
        require(asset["size"] == local["bytes"], "Asset size differs: " + name)
        require(
            asset.get("digest") == "sha256:" + local["sha256"],
            "Asset SHA-256 differs: " + name,
        )
        verified_assets[name] = {
            "bytes": asset["size"],
            "sha256": local["sha256"].upper(),
            "download_url": asset["browser_download_url"],
        }

    ref = read_json(f"{api_root}/git/ref/tags/{TAG}")
    require(ref["object"]["type"] == "tag", "Release tag is not annotated")
    tag = read_json(ref["object"]["url"])
    require(tag["object"]["type"] == "commit", "Annotated tag does not target a commit")
    require(tag["object"]["sha"] == CONTENT_COMMIT, "Annotated tag targets a different commit")
    latest = read_json(f"{api_root}/releases/latest")
    require(latest["id"] == release["id"], "v1.1.0 is not the latest GitHub release")

    receipt = {
        "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_PUBLIC_GITHUB_RELEASE_VERIFIED",
        "repository": f"https://github.com/{REPOSITORY}",
        "release_id": release["id"],
        "release_url": release["html_url"],
        "tag": TAG,
        "annotated_tag_object": ref["object"]["sha"],
        "content_commit": tag["object"]["sha"],
        "title": TITLE,
        "draft": False,
        "prerelease": False,
        "latest_release": True,
        "scientific_boundaries_verified": [
            "R1 HOLD",
            "C9R HOLD",
            "no corrected external outcomes",
        ],
        "assets": verified_assets,
        "zenodo_doi": "10.5281/zenodo.22151739",
        "old_zenodo_tombstone_doi": "10.5281/zenodo.22086892",
        "journal_submission": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
