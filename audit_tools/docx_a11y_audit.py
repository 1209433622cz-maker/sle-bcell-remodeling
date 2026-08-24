#!/usr/bin/env python3
"""Portable high-value DOCX accessibility audit using only the standard library."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "wp": WP}
NONDESCRIPTIVE = {"click here", "here", "link", "this link"}
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)


def qn(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def text_of(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.iter(qn(W, "t"))).strip()


def story_parts(archive: zipfile.ZipFile) -> list[str]:
    parts = ["word/document.xml"]
    parts.extend(
        name
        for name in archive.namelist()
        if re.fullmatch(r"word/(?:header|footer)\d+\.xml", name)
    )
    return parts


def finding(severity: str, kind: str, message: str, **context: object) -> dict[str, object]:
    return {"severity": severity, "kind": kind, "message": message, "context": context}


def audit(path: Path) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as archive:
        for part in story_parts(archive):
            root = ET.fromstring(archive.read(part))
            last_heading: int | None = None
            for paragraph in root.iter(qn(W, "p")):
                style = paragraph.find("w:pPr/w:pStyle", NS)
                value = style.get(qn(W, "val"), "") if style is not None else ""
                match = re.fullmatch(r"Heading\s*(\d+)", value)
                if match:
                    level = int(match.group(1))
                    if last_heading is not None and level > last_heading + 1:
                        findings.append(
                            finding(
                                "medium",
                                "heading_skip",
                                f"Heading level jumped from {last_heading} to {level}",
                                part=part,
                                text=text_of(paragraph)[:120],
                            )
                        )
                    last_heading = level

            for doc_property in root.iter(qn(WP, "docPr")):
                if not (doc_property.get("descr", "").strip() or doc_property.get("title", "").strip()):
                    findings.append(
                        finding(
                            "high",
                            "image_missing_alt",
                            "Image missing alt text",
                            part=part,
                            name=doc_property.get("name", ""),
                        )
                    )

            for table in root.iter(qn(W, "tbl")):
                first_row = table.find("w:tr", NS)
                if first_row is not None and first_row.find("w:trPr/w:tblHeader", NS) is None:
                    findings.append(
                        finding(
                            "medium",
                            "table_no_header_row",
                            "Table first row is not marked as a header",
                            part=part,
                        )
                    )

            for hyperlink in root.iter(qn(W, "hyperlink")):
                visible = text_of(hyperlink)
                if visible.lower() in NONDESCRIPTIVE:
                    findings.append(
                        finding(
                            "medium",
                            "hyperlink_nondescriptive",
                            f"Non-descriptive hyperlink text: {visible}",
                            part=part,
                        )
                    )
                if URL_RE.fullmatch(visible):
                    findings.append(
                        finding(
                            "low",
                            "hyperlink_raw_url",
                            "Hyperlink display text is a raw URL",
                            part=part,
                            text=visible[:120],
                        )
                    )

    return {
        "file": str(path),
        "counts": {
            severity: sum(item["severity"] == severity for item in findings)
            for severity in ("high", "medium", "low")
        },
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out_json", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.input)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    if any(report["counts"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
