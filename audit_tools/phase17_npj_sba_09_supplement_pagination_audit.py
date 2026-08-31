"""Require every supplementary figure heading and embedded figure to share a PDF page."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

from PIL import Image, ImageChops, ImageStat
from pypdf import PdfReader


FINGERPRINT_SIZE = (128, 128)
MAX_EXPECTED_NORMALIZED_MAE = 0.01
MIN_IDENTITY_MARGIN = 0.05
MAX_ASPECT_RATIO_DELTA = 0.01


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def normalized_mae(left: Image.Image, right: Image.Image) -> float:
    left_rgb = left.convert("RGB").resize(FINGERPRINT_SIZE, Image.Resampling.LANCZOS)
    right_rgb = right.convert("RGB").resize(FINGERPRINT_SIZE, Image.Resampling.LANCZOS)
    difference = ImageChops.difference(left_rgb, right_rgb)
    return sum(ImageStat.Stat(difference).mean) / (3 * 255)


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


def directly_painted_image_names(page) -> list[str]:
    resources = page.get("/Resources")
    contents = page.get_contents()
    if resources is None or contents is None:
        return []
    xobjects = resources.get_object().get("/XObject")
    if xobjects is None:
        return []
    lookup = xobjects.get_object()
    names = []
    for raw_name in re.findall(rb"/([^\s/<>{}\[\]()%]+)\s+Do\b", contents.get_data()):
        name = "/" + raw_name.decode("latin-1")
        if name in lookup and lookup[name].get_object().get("/Subtype") == "/Image":
            names.append(name)
    return names


def load_expected_sources(source_dir: Path) -> dict[str, dict]:
    sources = {}
    for number in range(1, 11):
        figure_id = f"S{number}"
        matches = sorted(source_dir.glob(f"Supplementary_Figure_{figure_id}_*.png"))
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected exactly one source PNG for {figure_id}, found {len(matches)} in {source_dir}"
            )
        path = matches[0]
        with Image.open(path) as image:
            sources[figure_id] = {
                "path": path,
                "sha256": sha256(path),
                "image": image.convert("RGB"),
                "pixel_dimensions": [image.width, image.height],
            }
    return sources


def identify_painted_figure(page, expected_id: str, sources: dict[str, dict]) -> dict:
    names = directly_painted_image_names(page)
    result = {
        "painted_image_resources": names,
        "expected_source": str(sources[expected_id]["path"]),
        "expected_source_sha256": sources[expected_id]["sha256"],
        "expected_pixel_dimensions": sources[expected_id]["pixel_dimensions"],
        "embedded_pixel_dimensions": None,
        "embedded_image_sha256": None,
        "normalized_mae_to_expected": None,
        "best_source_match": None,
        "second_best_normalized_mae": None,
        "identity_margin": None,
        "aspect_ratio_delta": None,
        "expected_figure_match": False,
    }
    if len(names) != 1:
        return result

    image_file = page.images[names[0]]
    embedded = image_file.image.convert("RGB")
    scores = sorted(
        (normalized_mae(source["image"], embedded), figure_id)
        for figure_id, source in sources.items()
    )
    expected_score = next(score for score, figure_id in scores if figure_id == expected_id)
    identity_margin = scores[1][0] - scores[0][0]
    expected = sources[expected_id]["image"]
    aspect_ratio_delta = abs(
        expected.width / expected.height - embedded.width / embedded.height
    )
    result.update(
        {
            "embedded_pixel_dimensions": [embedded.width, embedded.height],
            "embedded_image_sha256": hashlib.sha256(image_file.data).hexdigest().upper(),
            "normalized_mae_to_expected": round(expected_score, 8),
            "best_source_match": scores[0][1],
            "second_best_normalized_mae": round(scores[1][0], 8),
            "identity_margin": round(identity_margin, 8),
            "aspect_ratio_delta": round(aspect_ratio_delta, 8),
            "expected_figure_match": (
                scores[0][1] == expected_id
                and expected_score <= MAX_EXPECTED_NORMALIZED_MAE
                and identity_margin >= MIN_IDENTITY_MARGIN
                and aspect_ratio_delta <= MAX_ASPECT_RATIO_DELTA
            ),
        }
    )
    return result


def inspect(path: Path, sources: dict[str, dict]) -> dict:
    reader = PdfReader(path)
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append(
            {
                "page": index,
                "text": " ".join((page.extract_text() or "").split()),
                "images": painted_image_count(page),
                "page_object": page,
            }
        )
    figures = {}
    for number in range(1, 11):
        figure_id = f"S{number}"
        pattern = re.compile(rf"Supplementary Figure {figure_id}\s*\|")
        heading_pages = [row for row in pages if pattern.search(row["text"])]
        heading_page = heading_pages[-1] if heading_pages else None
        identity = (
            identify_painted_figure(heading_page["page_object"], figure_id, sources)
            if heading_page
            else None
        )
        figures[figure_id] = {
            "heading_page": heading_page["page"] if heading_page else None,
            "image_count_on_heading_page": heading_page["images"] if heading_page else 0,
            "same_page": bool(heading_page and heading_page["images"] >= 1),
            "image_identity": identity,
        }
    return {
        "pdf": str(path),
        "pages": len(reader.pages),
        "figures": figures,
        "all_heading_figure_pairs_same_page": all(row["same_page"] for row in figures.values()),
        "all_expected_figure_fingerprints_match": all(
            row["image_identity"] and row["image_identity"]["expected_figure_match"]
            for row in figures.values()
        ),
        "s8_same_page": figures["S8"]["same_page"],
        "s8_expected_figure_match": figures["S8"]["image_identity"]["expected_figure_match"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wps-pdf", type=Path, required=True)
    parser.add_argument("--libreoffice-pdf", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-pages", type=int, default=17)
    args = parser.parse_args()
    sources = load_expected_sources(args.source_dir.resolve())
    wps = inspect(args.wps_pdf.resolve(), sources)
    libreoffice = inspect(args.libreoffice_pdf.resolve(), sources)
    checks = {
        f"wps_{args.expected_pages}_pages": wps["pages"] == args.expected_pages,
        f"libreoffice_{args.expected_pages}_pages": libreoffice["pages"] == args.expected_pages,
        "wps_all_supplementary_figures_same_page": wps["all_heading_figure_pairs_same_page"],
        "libreoffice_all_supplementary_figures_same_page": libreoffice["all_heading_figure_pairs_same_page"],
        "wps_s8_same_page": wps["s8_same_page"],
        "libreoffice_s8_same_page": libreoffice["s8_same_page"],
        "wps_all_expected_figure_fingerprints_match": wps["all_expected_figure_fingerprints_match"],
        "libreoffice_all_expected_figure_fingerprints_match": libreoffice["all_expected_figure_fingerprints_match"],
        "wps_s8_expected_figure_match": wps["s8_expected_figure_match"],
        "libreoffice_s8_expected_figure_match": libreoffice["s8_expected_figure_match"],
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
