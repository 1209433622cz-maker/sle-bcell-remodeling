"""Require every supplementary figure heading and embedded figure to share a PDF page."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re

from pypdf import PdfReader


def painted_image_count(container, resources=None) -> int:
    resources = resources or container.get("/Resources")
    if resources is None:
        return 0
    resources = resources.get_object()
    xobjects = resources.get("/XObject")
    if xobjects is None:
        return 0
    contents = container.get_contents()
    if contents is None:
        return 0
    invoked = re.findall(rb"/([^\s/<>{}\[\]()%]+)\s+Do\b", contents.get_data())
    lookup = xobjects.get_object()
    count = 0
    for raw_name in invoked:
        name = "/" + raw_name.decode("latin-1")
        if name not in lookup:
            continue
        item = lookup[name].get_object()
        subtype = item.get("/Subtype")
        if subtype == "/Image":
            count += 1
        elif subtype == "/Form":
            count += painted_image_count(item, item.get("/Resources") or resources)
    return count


def inspect(path: Path) -> dict:
    reader = PdfReader(path)
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append(
            {
                "page": index,
                "text": " ".join((page.extract_text() or "").split()),
                "images": painted_image_count(page),
            }
        )
    figures = {}
    for number in range(1, 11):
        figure_id = f"S{number}"
        pattern = re.compile(rf"Supplementary Figure {figure_id}\s*\|")
        heading_pages = [row for row in pages if pattern.search(row["text"])]
        heading_page = heading_pages[-1] if heading_pages else None
        figures[figure_id] = {
            "heading_page": heading_page["page"] if heading_page else None,
            "image_count_on_heading_page": heading_page["images"] if heading_page else 0,
            "same_page": bool(heading_page and heading_page["images"] >= 1),
        }
    return {
        "pdf": str(path),
        "pages": len(reader.pages),
        "figures": figures,
        "all_heading_figure_pairs_same_page": all(row["same_page"] for row in figures.values()),
        "s8_same_page": figures["S8"]["same_page"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wps-pdf", type=Path, required=True)
    parser.add_argument("--libreoffice-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    wps = inspect(args.wps_pdf.resolve())
    libreoffice = inspect(args.libreoffice_pdf.resolve())
    checks = {
        "wps_17_pages": wps["pages"] == 17,
        "libreoffice_17_pages": libreoffice["pages"] == 17,
        "wps_all_supplementary_figures_same_page": wps["all_heading_figure_pairs_same_page"],
        "libreoffice_all_supplementary_figures_same_page": libreoffice["all_heading_figure_pairs_same_page"],
        "wps_s8_same_page": wps["s8_same_page"],
        "libreoffice_s8_same_page": libreoffice["s8_same_page"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SUPPLEMENT_PAGINATION_COHERENCE" if not failed else "HOLD_SUPPLEMENT_PAGINATION_REPAIR_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "wps": wps,
        "libreoffice": libreoffice,
    }
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
