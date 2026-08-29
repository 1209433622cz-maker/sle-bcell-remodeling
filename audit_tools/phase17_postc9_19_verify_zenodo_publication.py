"""Verify the public Zenodo release against the frozen local upload files."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
UPLOAD = ROOT / "04_submission/zenodo_release/upload"
RELEASE = ROOT / "00_project_management/qiteng_r2_release_2026-08-29"
RECORD_ID = "22151739"
DOI = "10.5281/zenodo.22151739"
CONCEPT_DOI = "10.5281/zenodo.22086891"
OLD_RECORD_ID = 22086892
TITLE = "SLE B-cell remodeling analysis: code, source data and reproducible release"
USER_AGENT = "SLE-Bcell-release-verifier/1.0"


def checksum(path, algorithm):
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_url(url, limit=None):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read() if limit is None else response.read(limit)
        return {
            "status": response.status,
            "final_url": response.geturl(),
            "content_type": response.headers.get("Content-Type"),
            "data": data,
        }


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RELEASE / "zenodo_publication_verification.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    require(
        output.is_relative_to((ROOT / "00_project_management").resolve()),
        "Receipt must remain in project management",
    )

    record_response = read_url(f"https://zenodo.org/api/records/{RECORD_ID}")
    require(record_response["status"] == 200, "Public record API is not accessible")
    record = json.loads(record_response["data"].decode("utf-8"))
    metadata = record["metadata"]
    require(record["id"] == int(RECORD_ID), "Public record ID differs")
    require(record["doi"] == DOI and metadata["doi"] == DOI, "Public DOI differs")
    require(record["conceptdoi"] == CONCEPT_DOI, "Concept DOI differs")
    require(record["status"] == "published" and record["submitted"] is True, "Record is not published")
    require(metadata["title"] == TITLE, "Public title differs")
    require(metadata["publication_date"] == "2026-08-29", "Publication date differs")
    require(metadata["version"] == "1.1.0", "Version differs")
    require(metadata["access_right"] == "open", "Record is not open access")
    require(metadata["language"] == "eng", "Language differs")
    require(metadata["resource_type"]["type"] == "software", "Resource type differs")
    description = metadata["description"]
    for phrase in (
        "R1 HOLD",
        "C9R HOLD",
        "no corrected external disease effects were estimated",
        "not causal binding",
        "not a journal submission or a peer-reviewed article",
    ):
        require(phrase in description, "Missing public scientific boundary: " + phrase)
    expected_creators = [
        {
            "name": "Chen, Zhi",
            "affiliation": "School of Medicine, The Chinese University of Hong Kong, Shenzhen",
            "orcid": "0009-0001-0072-5576",
        },
        {
            "name": "Qi, Teng",
            "affiliation": "School of Medicine, The Chinese University of Hong Kong, Shenzhen",
            "orcid": "0009-0007-7648-4776",
        },
    ]
    require(metadata["creators"] == expected_creators, "Public creator metadata differs")
    expected_keywords = [
        "systemic lupus erythematosus",
        "B cells",
        "single-cell RNA sequencing",
        "pseudobulk",
        "interferon",
        "reproducibility",
    ]
    require(metadata["keywords"] == expected_keywords, "Public keywords differ")
    require(
        metadata["custom"]["code:codeRepository"]
        == "https://github.com/1209433622cz-maker/sle-bcell-remodeling",
        "Repository URL differs",
    )

    expected_names = {"Research_Archive.zip", "Source_Code.zip", "SHA256SUMS.txt"}
    require({item["key"] for item in record["files"]} == expected_names, "Public file inventory differs")
    public_files = {}
    for item in record["files"]:
        path = UPLOAD / item["key"]
        local_size = path.stat().st_size
        local_md5 = checksum(path, "md5")
        local_sha256 = checksum(path, "sha256").upper()
        require(item["size"] == local_size, "Public file size differs: " + item["key"])
        require(item["checksum"] == "md5:" + local_md5, "Public MD5 differs: " + item["key"])
        public_files[item["key"]] = {
            "bytes": local_size,
            "public_md5": item["checksum"],
            "local_sha256": local_sha256,
            "download_url": item["links"]["self"],
        }

    sums_response = read_url(
        next(item["links"]["self"] for item in record["files"] if item["key"] == "SHA256SUMS.txt")
    )
    require(sums_response["status"] == 200, "Public checksum file is not downloadable")
    require(
        sums_response["data"] == (UPLOAD / "SHA256SUMS.txt").read_bytes(),
        "Public checksum file content differs",
    )
    checksum_lines = (UPLOAD / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines()
    require(len(checksum_lines) == 2, "Unexpected SHA256SUMS line count")
    for line in checksum_lines:
        sha256, name = line.split("  ", 1)
        require(public_files[name]["local_sha256"] == sha256, "SHA256SUMS differs: " + name)

    versions_response = read_url(f"https://zenodo.org/api/records/{RECORD_ID}/versions")
    versions = json.loads(versions_response["data"].decode("utf-8"))["hits"]["hits"]
    version_ids = [item["id"] for item in versions]
    require(int(RECORD_ID) in version_ids and OLD_RECORD_ID in version_ids, "Version chain is incomplete")
    require(versions[0]["id"] == int(RECORD_ID), "New record is not the latest version")

    public_html = read_url(f"https://zenodo.org/records/{RECORD_ID}")["data"].decode("utf-8")
    require("Creative Commons Attribution 4.0 International" in public_html, "CC BY 4.0 is not public")
    require("MIT License" in public_html, "MIT license is not public")
    doi_response = read_url(f"https://doi.org/{DOI}", limit=4096)
    require(doi_response["status"] == 200, "DOI did not resolve")
    require(
        doi_response["final_url"].rstrip("/") == f"https://zenodo.org/records/{RECORD_ID}",
        "DOI resolved to an unexpected URL",
    )

    receipt = {
        "verified_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_PUBLIC_ZENODO_RELEASE_VERIFIED",
        "record_id": RECORD_ID,
        "doi": DOI,
        "concept_doi": CONCEPT_DOI,
        "version": "1.1.0",
        "publication_date": "2026-08-29",
        "access_right": "open",
        "title": TITLE,
        "creators_verified": len(expected_creators),
        "keywords_verified": len(expected_keywords),
        "licenses_verified_in_public_html": ["CC-BY-4.0", "MIT"],
        "scientific_boundaries_verified": ["R1 HOLD", "C9R HOLD", "no corrected external outcomes"],
        "public_files": public_files,
        "public_checksum_file_content_verified": True,
        "version_chain_record_ids": version_ids,
        "new_record_is_latest_version": True,
        "doi_resolution": doi_response["final_url"],
        "old_record_deleted": False,
        "github_release_created": False,
        "journal_submission": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
