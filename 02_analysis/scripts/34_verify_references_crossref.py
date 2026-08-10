from __future__ import annotations

import json
import re
import time
from html import unescape
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_BIB = PROJECT_ROOT / "01_manuscript" / "references_working_v1.bib"
OUT_DIR = PROJECT_ROOT / "04_submission" / "reference_verification"
OUT_BIB = PROJECT_ROOT / "01_manuscript" / "references_verified_crossref_2026-07-09.bib"
OUT_CSV = OUT_DIR / "reference_verification_crossref_2026-07-09.csv"
OUT_MD = OUT_DIR / "reference_verification_crossref_2026-07-09.md"

USER_AGENT = "sle-bcell-manuscript-reference-audit/1.0 (mailto:metadata-audit@example.com)"


def parse_bib_entries(text: str) -> list[dict[str, str]]:
    entries = []
    for match in re.finditer(r"@(?P<type>\w+)\{(?P<key>[^,]+),(?P<body>.*?)\n\}", text, flags=re.S):
        body = match.group("body")
        fields = {}
        for field_match in re.finditer(r"\n\s*(?P<field>\w+)\s*=\s*\{(?P<value>.*?)\},?", body, flags=re.S):
            value = re.sub(r"\s+", " ", field_match.group("value")).strip()
            fields[field_match.group("field").lower()] = value
        entries.append({"entry_type": match.group("type"), "key": match.group("key"), **fields})
    return entries


def fetch_crossref(doi: str) -> dict:
    url = f"https://api.crossref.org/works/{quote(doi, safe='')}"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["message"]


def first(items: list | None, default: str = "") -> str:
    if not items:
        return default
    value = items[0]
    if isinstance(value, str):
        return value
    return str(value)


def published_year(message: dict) -> str:
    for field in ["published-print", "published-online", "published", "created", "deposited"]:
        parts = message.get(field, {}).get("date-parts")
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def author_string(message: dict, max_authors: int | None = None) -> str:
    authors = []
    for author in message.get("author", []):
        family = author.get("family", "").strip()
        given = author.get("given", "").strip()
        literal = author.get("name", "").strip()
        if family and given:
            authors.append(f"{family}, {given}")
        elif family:
            authors.append(family)
        elif literal:
            authors.append(literal)
    if max_authors is not None and len(authors) > max_authors:
        return " and ".join(authors[:max_authors] + ["others"])
    return " and ".join(authors)


def clean_latex(value: str) -> str:
    value = clean_crossref_text(value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def clean_crossref_text(value: str) -> str:
    value = unescape(str(value))
    value = re.sub(r"m\s*<sup>\s*6\s*</sup>\s*A", "m6A", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return re.sub(r"\s+", " ", value).strip()


def bib_field(name: str, value: str | None, comma: bool = True) -> str | None:
    if value is None or value == "":
        return None
    ending = "," if comma else ""
    return f"  {name} = {{{clean_latex(str(value))}}}{ending}"


def build_bib_entry(key: str, message: dict) -> str:
    fields = [
        bib_field("author", author_string(message)),
        bib_field("title", first(message.get("title"))),
        bib_field("journal", first(message.get("container-title"))),
        bib_field("year", published_year(message)),
        bib_field("volume", message.get("volume", "")),
        bib_field("number", message.get("issue", "")),
        bib_field("pages", message.get("page", "")),
        bib_field("publisher", message.get("publisher", "")),
        bib_field("doi", message.get("DOI", "")),
        bib_field("url", message.get("URL", "")),
    ]
    kept = [field for field in fields if field is not None]
    return "@article{" + key + ",\n" + "\n".join(kept) + "\n}\n"


def same_normalized(left: str, right: str) -> bool:
    normalize = lambda value: re.sub(r"\W+", "", value or "").lower()
    return normalize(clean_crossref_text(left)) == normalize(clean_crossref_text(right))


def write_md(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Crossref Reference Verification",
        "",
        "Date: 2026-07-09",
        "",
        "This author-side audit compares local BibTeX skeleton fields with DOI metadata returned by Crossref.",
        "",
        "| Key | DOI | Status | Local title matches | Local journal matches | Crossref title | Crossref journal | Year |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {key} | {doi} | {status} | {title_match} | {journal_match} | {cr_title} | {cr_journal} | {year} |".format(
                **{k: str(v).replace("|", "\\|") for k, v in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Verified BibTeX was written to `01_manuscript/references_verified_crossref_2026-07-09.bib`.",
            "- Publisher pages should still be checked for final journal-specific reference style before submission.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    entries = parse_bib_entries(INPUT_BIB.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    bib_entries = [
        "% Verified from Crossref DOI metadata on 2026-07-09.",
        "% Final journal style and author truncation rules still require target-specific formatting.",
        "",
    ]
    for entry in entries:
        doi = entry.get("doi", "").strip()
        if not doi:
            rows.append(
                {
                    "key": entry["key"],
                    "doi": "",
                    "status": "missing_doi",
                    "title_match": "",
                    "journal_match": "",
                    "cr_title": "",
                    "cr_journal": "",
                    "year": "",
                }
            )
            continue
        try:
            message = fetch_crossref(doi)
            cr_title = clean_crossref_text(first(message.get("title")))
            cr_journal = clean_crossref_text(first(message.get("container-title")))
            row = {
                "key": entry["key"],
                "doi": doi,
                "status": "ok",
                "title_match": same_normalized(entry.get("title", ""), cr_title),
                "journal_match": same_normalized(entry.get("journal", ""), cr_journal),
                "cr_title": cr_title,
                "cr_journal": cr_journal,
                "year": published_year(message),
            }
            rows.append(row)
            bib_entries.append(build_bib_entry(entry["key"], message))
            time.sleep(0.25)
        except Exception as exc:  # noqa: BLE001 - audit should keep going.
            rows.append(
                {
                    "key": entry["key"],
                    "doi": doi,
                    "status": f"error: {exc}",
                    "title_match": "",
                    "journal_match": "",
                    "cr_title": "",
                    "cr_journal": "",
                    "year": "",
                }
            )
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    write_md(OUT_MD, rows)
    OUT_BIB.write_text("\n".join(bib_entries).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_BIB}")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
