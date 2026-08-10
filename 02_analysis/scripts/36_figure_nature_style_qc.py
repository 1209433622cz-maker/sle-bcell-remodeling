from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "04_submission" / "figure_quality_qc"
OUT_CSV = OUT_DIR / "figure_quality_qc_2026-07-27.csv"
OUT_MD = OUT_DIR / "figure_quality_qc_2026-07-27.md"
CONTACT_SHEET = OUT_DIR / "figure_contact_sheet_2026-07-27.png"


@dataclass(frozen=True)
class FigureAsset:
    figure: str
    role: str
    png: Path
    expected_pdf: bool = True


FIGURES = [
    FigureAsset(
        "Figure 1",
        "Dataset overview and guardrails",
        PROJECT_ROOT / "03_results" / "figure1_dataset_overview" / "figures" / "figure1_dataset_overview.png",
    ),
    FigureAsset(
        "Figure 2",
        "B-cell atlas and remodeling",
        PROJECT_ROOT / "03_results" / "first_pass_bcell_full" / "figures" / "figure2_v3_refined_bcell_state_atlas.png",
    ),
    FigureAsset(
        "Figure 3",
        "ABC/APC-like pseudobulk identity",
        PROJECT_ROOT / "03_results" / "figure3_abc_apc_focus" / "figures" / "figure3_v1_abc_apc_focus.png",
    ),
    FigureAsset(
        "Figure 4",
        "Covariate robustness",
        PROJECT_ROOT / "03_results" / "figure4_covariate_sensitivity" / "figures" / "figure4_v1_covariate_sensitivity.png",
    ),
    FigureAsset(
        "Figure 5",
        "Literature-informed signatures",
        PROJECT_ROOT / "03_results" / "figure5_literature_signature_validation" / "figures" / "figure5_v1_literature_signature_validation.png",
    ),
    FigureAsset(
        "Figure 6",
        "Independent GSE135779 validation",
        PROJECT_ROOT / "03_results" / "gse135779_bcell_validation" / "figures" / "figure6_gse135779_large_cohort_validation.png",
    ),
    FigureAsset(
        "Supplementary Figure S2",
        "OneK1K B-lineage reference context",
        PROJECT_ROOT / "03_results" / "onek1k_bcell_reference_context" / "figures" / "figure7_candidate_onek1k_bcell_reference_context.png",
    ),
    FigureAsset(
        "Supplementary Figure S1",
        "Flagged platelet/ambient-high QC",
        PROJECT_ROOT / "03_results" / "supplement_qc_flagged_cluster" / "figures" / "supplement_qc_flagged_cluster.png",
    ),
    FigureAsset(
        "Supplementary Figure S3",
        "Directional GSE163121 validation",
        PROJECT_ROOT / "03_results" / "gse163121_bcell_validation" / "figures" / "figure6_gse163121_independent_bcell_validation.png",
    ),
    FigureAsset(
        "Supplementary Figure S4",
        "Compositional abundance sensitivity",
        PROJECT_ROOT / "03_results" / "compositional_abundance_sensitivity" / "figures" / "supplementary_figure_s4_compositional_sensitivity.png",
    ),
]


def inspect_pdf(path: Path) -> tuple[float | None, float | None, bool]:
    if not path.exists():
        return None, None, False
    data = path.read_bytes()
    match = re.search(
        rb"/MediaBox\s*\[\s*0(?:\.0+)?\s+0(?:\.0+)?\s+([0-9.]+)\s+([0-9.]+)\s*\]",
        data,
    )
    if match is None:
        width_mm = height_mm = None
    else:
        width_mm = float(match.group(1)) * 25.4 / 72
        height_mm = float(match.group(2)) * 25.4 / 72
    return width_mm, height_mm, b"/FontFile2" in data


def inspect_figure(asset: FigureAsset) -> dict[str, object]:
    pdf_path = asset.png.with_suffix(".pdf")
    pdf_width_mm, pdf_height_mm, truetype_embedded = inspect_pdf(pdf_path)
    row: dict[str, object] = {
        "figure": asset.figure,
        "role": asset.role,
        "png_path": str(asset.png.relative_to(PROJECT_ROOT)),
        "png_exists": asset.png.exists(),
        "pdf_exists": pdf_path.exists(),
        "pdf_width_mm": round(pdf_width_mm, 1) if pdf_width_mm else None,
        "pdf_height_mm": round(pdf_height_mm, 1) if pdf_height_mm else None,
        "truetype_embedded": truetype_embedded,
        "size_bytes": 0,
        "width_px": 0,
        "height_px": 0,
        "aspect_ratio": None,
        "dpi_x": None,
        "dpi_y": None,
        "qc_flag": "missing_png",
        "recommendation": "Regenerate figure.",
    }
    if not asset.png.exists():
        return row
    with Image.open(asset.png) as img:
        width, height = img.size
        dpi = img.info.get("dpi", (None, None))
    row.update(
        {
            "size_bytes": asset.png.stat().st_size,
            "width_px": width,
            "height_px": height,
            "aspect_ratio": round(width / height, 3),
            "dpi_x": round(float(dpi[0]), 1) if dpi[0] else None,
            "dpi_y": round(float(dpi[1]), 1) if dpi[1] else None,
        }
    )
    flags = []
    if width < 2400 or height < 1600:
        flags.append("low_pixel_dimension")
    if row["dpi_x"] and float(row["dpi_x"]) < 300:
        flags.append("low_dpi")
    if asset.expected_pdf and not row["pdf_exists"]:
        flags.append("missing_pdf")
    if pdf_width_mm and pdf_width_mm > 183.0:
        flags.append("pdf_too_wide")
    if pdf_height_mm and pdf_height_mm > 170.0:
        flags.append("pdf_too_tall")
    if row["pdf_exists"] and not truetype_embedded:
        flags.append("truetype_font_not_detected")
    if asset.png.stat().st_size > 10 * 1024 * 1024 or (pdf_path.exists() and pdf_path.stat().st_size > 10 * 1024 * 1024):
        flags.append("file_over_10mb")
    if width / height > 2.2:
        flags.append("very_wide")
    if height / width > 1.6:
        flags.append("very_tall")
    if not flags:
        row["qc_flag"] = "pass_nature_technical_qc"
        row["recommendation"] = "Keep; inspect panel hierarchy and 100% label readability manually."
    else:
        row["qc_flag"] = ";".join(flags)
        row["recommendation"] = "Regenerate or export PDF/vector version; inspect panel spacing and text size."
    return row


def make_contact_sheet(rows: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for row in rows:
        png = PROJECT_ROOT / str(row["png_path"])
        if not png.exists():
            continue
        with Image.open(png) as img:
            img = img.convert("RGB")
            img.thumbnail((520, 380), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (560, 450), "white")
            canvas.paste(img, ((560 - img.width) // 2, 20))
            draw = ImageDraw.Draw(canvas)
            label = (
                f"{row['figure']} | {row['width_px']}x{row['height_px']} | "
                f"{row['pdf_width_mm']}x{row['pdf_height_mm']} mm | {row['qc_flag']}"
            )
            draw.text((20, 410), label[:92], fill="black")
            thumbs.append(canvas)
    if not thumbs:
        return
    cols = 2
    rows_n = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 560, rows_n * 450), "white")
    for idx, thumb in enumerate(thumbs):
        x = (idx % cols) * 560
        y = (idx // cols) * 450
        sheet.paste(thumb, (x, y))
    sheet.save(CONTACT_SHEET, dpi=(220, 220))


def write_md(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Figure Quality QC - Nature-Style Technical Audit",
        "",
        "Date: 2026-07-27",
        "",
        "This audit checks objective figure-export properties and flags likely Nature-style production issues. It does not replace manual scientific review of panel content.",
        "",
        f"- Contact sheet: `{CONTACT_SHEET.relative_to(PROJECT_ROOT)}`.",
        "",
        "| Figure | Role | PNG | PDF | Pixels | PDF mm | DPI | TrueType | QC flag | Recommendation |",
        "|---|---|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        dpi = f"{row['dpi_x']} x {row['dpi_y']}" if row["dpi_x"] else "not embedded"
        lines.append(
            f"| {row['figure']} | {row['role']} | {row['png_exists']} | {row['pdf_exists']} | "
            f"{row['width_px']} x {row['height_px']} | {row['pdf_width_mm']} x {row['pdf_height_mm']} | "
            f"{dpi} | {row['truetype_embedded']} | {row['qc_flag']} | {row['recommendation']} |"
        )
    lines.extend(
        [
            "",
            "## Advisor-Level Interpretation",
            "",
            "- All main figures should have PNG plus PDF/vector export before journal formatting.",
            "- Figure 6 and Supplementary Figures S2-S4 must remain visually integrated with Figures 1-5.",
            "- Use a restrained Nature-like style: white background, compact panel lettering, minimal gridlines, color-blind-safe disease colors, and no oversized titles.",
            "- Nature technical targets used here are <=183 mm width, <=170 mm height, 5-7 pt body text, 8 pt panel labels, embedded TrueType fonts, and files below 10 MB.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [inspect_figure(asset) for asset in FIGURES]
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    write_md(rows)
    make_contact_sheet(rows)
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {CONTACT_SHEET}")
    print(
        pd.DataFrame(rows)[
            ["figure", "width_px", "height_px", "pdf_width_mm", "pdf_height_mm", "truetype_embedded", "qc_flag"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
