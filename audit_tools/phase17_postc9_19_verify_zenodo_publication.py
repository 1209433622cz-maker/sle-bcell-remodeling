"""Verify the public Zenodo release against the frozen local upload files."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
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


def read_url(url, limit=None, allowed_statuses=(200,)):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        response = urllib.request.urlopen(request, timeout=60)
    except urllib.error.HTTPError as error:
        if error.code not in allowed_statuses:
            raise
        response = error
    with response:
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
    require(int(RECORD_ID) in version_ids, "Current record is absent from the live version list")
    require(OLD_RECORD_ID not in version_ids, "Deleted record remains in the live version list")
    require(versions[0]["id"] == int(RECORD_ID), "New record is not the latest version")

    old_api_response = read_url(
        f"https://zenodo.org/api/records/{OLD_RECORD_ID}", allowed_statuses=(410,)
    )
    require(old_api_response["status"] == 410, "Old record API is not a tombstone")
    old_payload = json.loads(old_api_response["data"].decode("utf-8"))
    require(old_payload["message"] == "Record deleted", "Unexpected tombstone message")
    old_tombstone = old_payload["tombstone"]
    require(old_tombstone["is_visible"] is True, "Old tombstone is not publicly visible")
    require(
        old_tombstone["removal_reason"]["id"] == "retracted",
        "Unexpected old-record removal reason",
    )
    require(
        old_tombstone["deletion_policy"]["id"] == "grace-period-v1",
        "Unexpected old-record deletion policy",
    )
    require(
        f"10.5281/zenodo.{OLD_RECORD_ID}" in old_tombstone["citation_text"],
        "Old tombstone does not retain its DOI citation",
    )

    public_html = read_url(f"https://zenodo.org/records/{RECORD_ID}")["data"].decode("utf-8")
    require("Creative Commons Attribution 4.0 International" in public_html, "CC BY 4.0 is not public")
    require("MIT License" in public_html, "MIT license is not public")
    doi_response = read_url(f"https://doi.org/{DOI}", limit=4096)
    require(doi_response["status"] == 200, "DOI did not resolve")
    require(
        doi_response["final_url"].rstrip("/") == f"https://zenodo.org/records/{RECORD_ID}",
        "DOI resolved to an unexpected URL",
    )
    concept_doi_response = read_url(f"https://doi.org/{CONCEPT_DOI}", limit=4096)
    require(
        concept_doi_response["final_url"].rstrip("/")
        == f"https://zenodo.org/records/{RECORD_ID}",
        "Concept DOI did not resolve to the current version",
    )
    old_doi_response = read_url(
        f"https://doi.org/10.5281/zenodo.{OLD_RECORD_ID}",
        limit=4096,
        allowed_statuses=(410,),
    )
    require(old_doi_response["status"] == 410, "Old DOI did not resolve as deleted")
    require(
        old_doi_response["final_url"].rstrip("/")
        == f"https://zenodo.org/records/{OLD_RECORD_ID}",
        "Old DOI resolved to an unexpected tombstone URL",
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
        "concept_doi_resolution": concept_doi_response["final_url"],
        "old_record_deleted": True,
        "old_record_api_status": old_api_response["status"],
        "old_record_tombstone_visible": old_tombstone["is_visible"],
        "old_record_removal_reason": old_tombstone["removal_reason"]["id"],
        "old_record_deletion_policy": old_tombstone["deletion_policy"]["id"],
        "old_record_citation_retained": True,
        "old_record_removal_timestamp": old_tombstone["removal_date"],
        "old_doi_resolution": old_doi_response["final_url"],
        "journal_submission": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
