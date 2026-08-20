#!/usr/bin/env python3
"""Build labelled contact sheets from final-page PNG render sets."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--pages-per-sheet", type=int, default=9)
    parser.add_argument("--thumbnail-width", type=int, default=420)
    args = parser.parse_args()

    pages = sorted(args.directory.glob("final-page-*.png"))
    if not pages:
        raise RuntimeError(f"No final-page PNG files found in {args.directory}")
    outputs = []
    for start in range(0, len(pages), args.pages_per_sheet):
        batch = pages[start : start + args.pages_per_sheet]
        thumbnails = []
        for page in batch:
            with Image.open(page) as image:
                image = image.convert("RGB")
                scale = args.thumbnail_width / image.width
                thumbnail = image.resize(
                    (args.thumbnail_width, round(image.height * scale)),
                    Image.Resampling.LANCZOS,
                )
            canvas = Image.new("RGB", (thumbnail.width + 20, thumbnail.height + 42), "white")
            canvas.paste(thumbnail, (10, 26))
            ImageDraw.Draw(canvas).text((10, 7), page.stem, fill="black")
            thumbnails.append(canvas)

        columns = 3 if len(thumbnails) > 1 else 1
        rows = (len(thumbnails) + columns - 1) // columns
        cell_width = max(image.width for image in thumbnails)
        cell_height = max(image.height for image in thumbnails)
        sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), (230, 230, 230))
        for index, thumbnail in enumerate(thumbnails):
            sheet.paste(thumbnail, ((index % columns) * cell_width, (index // columns) * cell_height))
        output = args.directory / f"contact_sheet_{args.label}_{start + 1:02d}-{start + len(batch):02d}.png"
        sheet.save(output, optimize=True)
        outputs.append(output)

    print("\n".join(str(path) for path in outputs))


if __name__ == "__main__":
    main()
