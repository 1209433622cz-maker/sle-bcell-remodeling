#!/usr/bin/env python3
"""Verify and format the Gate C8R DOI reference set using Crossref metadata."""

from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8R" / "20260820_pre_submission_repair"
OUT_DIR = RUN_DIR / "references"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCES = [
    (1, "10.1126/science.abf1970", "Single-cell RNA-seq"),
    (2, "10.1038/s41590-020-0743-0", "Mapping systemic lupus"),
    (3, "10.1038/s41467-020-19894-4", "muscat detects"),
    (4, "10.1038/s41467-021-25960-2", "Confronting false discoveries"),
    (5, "10.1038/s41467-021-27150-6", "scCODA"),
    (6, "10.1186/s13059-017-1382-0", "SCANPY"),
    (7, "10.1038/s41592-019-0619-0", "Fast, sensitive and accurate integration"),
    (8, "10.1038/s41598-019-41695-z", "From Louvain to Leiden"),
    (9, "10.1093/bioinformatics/btp616", "edgeR"),
    (10, "10.1093/bioadv/vbac016", "decoupleR"),
    (11, "10.1093/nar/gkad841", "Expanding the coverage"),
    (12, "10.1016/j.cels.2015.12.004", "Molecular Signatures Database"),
    (13, "10.4049/jimmunol.0902314", "Major differences"),
    (18, "10.1186/s13073-023-01237-9", "molecular endotypes of SLE"),
    (19, "10.1016/j.jaut.2025.103438", "Interferon signatures fuel"),
    (20, "10.1016/j.cell.2016.03.008", "Personalized Immunomonitoring"),
    (21, "10.1038/s41590-019-0398-x", "immune cell landscape"),
    (22, "10.1016/j.immuni.2018.08.015", "Distinct Effector B Cells"),
    (23, "10.1002/art.38628", "Modular Transcriptional Repertoire"),
    (24, "10.1002/art.42157", "Phenotype Among Antigen"),
    (25, "10.3389/fimmu.2020.498703", "FOXM1 Induction"),
    (26, "10.1093/nar/gks461", "competitive gene set test"),
    (27, "10.1093/bioinformatics/btq401", "ROAST"),
    (28, "10.1093/nar/gkv007", "limma powers"),
    (29, "10.1186/gb-2014-15-2-r29", "voom"),
    (30, "10.4049/jimmunol.2100339", "Plasma Cell Differentiation"),
]


def clean(value: object) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    text = html.unescape(str(value or ""))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()


def query_crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SLE-Bcell-GateC8R-reference-audit/1.0 (mailto:repository-audit@example.invalid)",
            "Accept": "application/json",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)["message"]
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Crossref query failed for {doi}: {last_error}")


def author_text(message: dict, max_authors: int = 6) -> str:
    authors = message.get("author") or []
    personal = [author for author in authors if clean(author.get("family"))]
    names = []
    for author in personal[:max_authors]:
        family = clean(author.get("family"))
        given = clean(author.get("given"))
        initials = "".join(part[0] for part in re.findall(r"[^\W\d_]+", given, flags=re.UNICODE))
        names.append(f"{family} {initials}".strip())
    if len(authors) > max_authors:
        names.append("et al")
    return ", ".join(names)


def published_year(message: dict) -> str:
    for key in ("published-print", "published-online", "published", "issued"):
        parts = (message.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def vancouver(message: dict) -> str:
    authors = author_text(message)
    title = clean(message.get("title"))
    journal = clean(message.get("container-title"))
    year = published_year(message)
    volume = clean(message.get("volume"))
    issue = clean(message.get("issue"))
    pages = clean(message.get("page") or message.get("article-number"))
    doi = clean(message.get("DOI"))
    locator = year
    if volume:
        locator += f";{volume}"
    if issue:
        locator += f"({issue})"
    if pages:
        locator += f":{pages}"
    citation = f"{authors}. {title}. {journal}. {locator}. doi:{doi}."
    return (
        citation.replace("–", "-")
        .replace("—", "-")
        .replace("‐", "-")
        .replace("α", "alpha")
        .replace("β", "beta")
        .replace("λ", "lambda")
    )


def main() -> None:
    rows = []
    citations = []
    raw = {}
    for order, doi, token in REFERENCES:
        message = query_crossref(doi)
        raw[doi] = message
        title = clean(message.get("title"))
        returned_doi = clean(message.get("DOI")).lower()
        token_match = token.lower() in title.lower()
        doi_match = returned_doi == doi.lower()
        rows.append(
            {
                "order": order,
                "doi": doi,
                "expected_title_token": token,
                "crossref_title": title,
                "first_author": next(
                    (
                        clean(author.get("family"))
                        for author in (message.get("author") or [])
                        if clean(author.get("family"))
                    ),
                    clean((message.get("author") or [{}])[0].get("name")),
                ),
                "journal": clean(message.get("container-title")),
                "year": published_year(message),
                "volume": clean(message.get("volume")),
                "issue": clean(message.get("issue")),
                "pages": clean(message.get("page") or message.get("article-number")),
                "status": "PASS" if token_match and doi_match else "FAIL",
            }
        )
        citations.append((order, vancouver(message)))
        time.sleep(0.1)

    csv_path = OUT_DIR / "reference_verification_gateC8R.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT_DIR / "crossref_raw_gateC8R.json").write_text(
        json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "references_gateC8R_vancouver.md").write_text(
        "\n".join(f"{order}. {citation}" for order, citation in citations) + "\n",
        encoding="utf-8",
    )

    passed = sum(row["status"] == "PASS" for row in rows)
    report = [
        "# Gate C8R reference verification",
        "",
        "- Verified: 20 August 2026",
        "- Source: Crossref REST API",
        f"- Decision: {'PASS' if passed == len(rows) else 'HOLD'} ({passed}/{len(rows)} DOI records)",
        "- Manuscript reference count after adding GEO and repository records: 30",
        "",
        "| No. | DOI | First author | Year | Status |",
        "|---:|---|---|---:|---|",
    ]
    report.extend(
        f"| {row['order']} | `{row['doi']}` | {row['first_author']} | {row['year']} | {row['status']} |"
        for row in rows
    )
    (OUT_DIR / "reference_verification_gateC8R.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )

    decision = "PASS" if passed == len(rows) else "HOLD"
    print(json.dumps({"decision": decision, "passed": passed, "total": len(rows)}, indent=2))
    if decision != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
