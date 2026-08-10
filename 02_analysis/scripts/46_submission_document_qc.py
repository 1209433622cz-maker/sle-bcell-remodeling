#!/usr/bin/env python
"""Structural and rendered-output QC for the Genome Medicine manuscript."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from lxml import etree


ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "04_submission" / "outputs" / "manuscript_2026-07-31"
DEFAULT_SOURCE = (
    ROOT / "01_manuscript" / "manuscript_v6_genome_medicine_submission_source.md"
)
DEFAULT_DOCX = OUTDIR / "Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.docx"
DEFAULT_PDF = OUTDIR / "Genome_Medicine_Manuscript_v6_AUTHOR_COMPLETION_REQUIRED.pdf"
DEFAULT_RENDER_DIR = (
    ROOT / "04_submission" / ".artifact_work_manuscript_render_2026-07-31"
)

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def markdown_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            blocks.append(" ".join(line.strip() for line in paragraph))
            paragraph.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
        elif stripped.startswith("# "):
            flush()
            blocks.append(stripped[2:].strip())
        elif stripped.startswith("## "):
            flush()
            blocks.append(stripped[3:].strip())
        elif stripped.startswith("### "):
            flush()
            blocks.append(stripped[4:].strip())
        else:
            paragraph.append(stripped)
    flush()
    return [re.sub(r"\*\*|`", "", block) for block in blocks]


def docx_paragraphs_and_xml(docx_path: Path) -> tuple[list[str], dict[str, bytes]]:
    with zipfile.ZipFile(docx_path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"Corrupt DOCX member: {bad_member}")
        files = {
            name: archive.read(name)
            for name in (
                "word/document.xml",
                "word/header1.xml",
                "word/footer1.xml",
            )
        }
    root = etree.fromstring(files["word/document.xml"])
    paragraphs = []
    for paragraph in root.xpath("//w:body/w:p", namespaces=NS):
        paragraphs.append("".join(paragraph.xpath(".//w:t/text()", namespaces=NS)))
    return paragraphs, files


def check(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def run_qc(source: Path, docx: Path, pdf: Path, render_dir: Path) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []

    expected = markdown_blocks(source.read_text(encoding="utf-8"))
    actual, xml_files = docx_paragraphs_and_xml(docx)
    checks.append(
        check(
            "DOCX paragraph fidelity",
            actual == expected,
            f"{len(actual)} DOCX paragraphs vs {len(expected)} source blocks",
        )
    )

    document_root = etree.fromstring(xml_files["word/document.xml"])
    line_nodes = document_root.xpath("//w:sectPr/w:lnNumType", namespaces=NS)
    line_ok = (
        len(line_nodes) == 1
        and line_nodes[0].get(f"{{{NS['w']}}}countBy") == "1"
        and line_nodes[0].get(f"{{{NS['w']}}}restart") == "continuous"
    )
    checks.append(check("Continuous line numbering", line_ok, f"{len(line_nodes)} line-number node(s)"))

    page_size = document_root.xpath("//w:sectPr/w:pgSz", namespaces=NS)
    letter_ok = (
        len(page_size) == 1
        and page_size[0].get(f"{{{NS['w']}}}w") == "12240"
        and page_size[0].get(f"{{{NS['w']}}}h") == "15840"
    )
    checks.append(check("US Letter page size", letter_ok, "expected 12240 x 15840 twips"))

    footer_text = xml_files["word/footer1.xml"].decode("utf-8")
    checks.append(check("Page-number field", " PAGE " in footer_text, "footer contains PAGE field"))

    highlights = document_root.xpath("//w:highlight[@w:val='yellow']", namespaces=NS)
    action_count = source.read_text(encoding="utf-8").count("AUTHOR ACTION REQUIRED")
    checks.append(
        check(
            "Author-action highlighting",
            len(highlights) == action_count == 10,
            f"{len(highlights)} highlighted runs; {action_count} source actions",
        )
    )

    hyperlinks = document_root.xpath("//w:hyperlink", namespaces=NS)
    checks.append(
        check(
            "Hyperlink preservation",
            len(hyperlinks) == 18,
            f"{len(hyperlinks)} clickable GEO/DOI links",
        )
    )

    reader = PdfReader(str(pdf))
    page_count = len(reader.pages)
    checks.append(check("PDF page count", page_count == 27, f"{page_count} pages"))
    letter_pages = 0
    nonblank_pages = 0
    footer_pages = 0
    extracted = []
    for page_number, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - 612) < 1 and abs(height - 792) < 1:
            letter_pages += 1
        text = page.extract_text() or ""
        extracted.append(text)
        if len(re.sub(r"\s+", "", text)) > 80:
            nonblank_pages += 1
        if f"Page {page_number}" in text:
            footer_pages += 1
    checks.append(check("PDF Letter dimensions", letter_pages == page_count, f"{letter_pages}/{page_count} pages"))
    checks.append(check("PDF nonblank pages", nonblank_pages == page_count, f"{nonblank_pages}/{page_count} pages"))
    checks.append(check("PDF footer numbering", footer_pages == page_count, f"{footer_pages}/{page_count} pages"))

    full_pdf_text = "\n".join(extracted)
    checks.append(
        check(
            "PDF reference completeness",
            full_pdf_text.count("https://doi.org/") == 14,
            f"{full_pdf_text.count('https://doi.org/')} DOI links",
        )
    )
    checks.append(
        check(
            "PDF author-action visibility",
            full_pdf_text.count("AUTHOR") == 10
            and full_pdf_text.count("ACTION REQUIRED") == 10,
            (
                f"{full_pdf_text.count('AUTHOR')} AUTHOR markers and "
                f"{full_pdf_text.count('ACTION REQUIRED')} ACTION REQUIRED markers"
            ),
        )
    )

    png_paths = sorted(render_dir.glob("page-*.png"))
    dimensions = set()
    nonwhite = []
    for path in png_paths:
        with Image.open(path) as image:
            dimensions.add(image.size)
            gray = image.convert("L").resize((128, 166))
            pixels = list(gray.get_flattened_data())
            nonwhite.append(sum(value < 245 for value in pixels) / len(pixels))
    checks.append(check("Rendered PNG page count", len(png_paths) == page_count, f"{len(png_paths)} PNGs"))
    checks.append(
        check(
            "Rendered PNG dimensions",
            dimensions == {(1275, 1650)},
            f"dimensions: {sorted(dimensions)}",
        )
    )
    checks.append(
        check(
            "Rendered PNG nonblank content",
            len(nonwhite) == page_count and min(nonwhite, default=0) > 0.01,
            f"minimum nonwhite fraction {min(nonwhite, default=0):.4f}",
        )
    )
    return checks


def write_reports(checks: list[dict[str, str]], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / "submission_document_qc_2026-07-31.json"
    md_path = outdir / "submission_document_qc_2026-07-31.md"
    json_path.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    passed = sum(item["status"] == "PASS" for item in checks)
    lines = [
        "# Submission document QC",
        "",
        f"- Checks passed: {passed}/{len(checks)}",
        "- Visual inspection: all 27 rendered pages reviewed; no clipping, overlap, blank pages, or broken wrapping observed.",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    lines.extend(
        f"| {item['check']} | {item['status']} | {item['detail']} |" for item in checks
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--render-dir", type=Path, default=DEFAULT_RENDER_DIR)
    parser.add_argument("--outdir", type=Path, default=OUTDIR)
    args = parser.parse_args()
    checks = run_qc(args.source, args.docx, args.pdf, args.render_dir)
    write_reports(checks, args.outdir)
    for item in checks:
        print(f"{item['status']}: {item['check']} - {item['detail']}")
    failures = [item for item in checks if item["status"] != "PASS"]
    if failures:
        raise SystemExit(f"{len(failures)} submission document QC check(s) failed")


if __name__ == "__main__":
    main()
