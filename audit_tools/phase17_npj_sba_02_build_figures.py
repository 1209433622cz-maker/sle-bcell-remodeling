"""Rerender all publication figures from frozen source tables under the npj SBA contract."""

from __future__ import annotations

import hashlib
import json
import numbers
import os
from pathlib import Path
import shutil
import subprocess
import sys

import fitz
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(
    os.environ.get(
        "NPJ_SBA_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_target_refreeze/20260830_target_specific_refreeze",
    )
).resolve()
BASELINE = ROOT / "phase17_v7/post_gateC9/20260828_corrected_candidate/source_data"
C9 = ROOT / "phase17_v7/gateC9R/20260828_normalization_correction"
FIGURES = RUN / "figures"
PORTAL = RUN / "portal_figures"
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def standard_name(path: Path) -> str:
    name = path.name
    if name.startswith("Figure"):
        number = name.removeprefix("Figure").split("_", 1)[0]
        return f"Figure_{number}.pdf"
    if name.startswith("Supplementary_Figure_S"):
        number = name.removeprefix("Supplementary_Figure_S").split("_", 1)[0]
        return f"Supplementary_Figure_S{number}.pdf"
    raise ValueError(f"Unexpected figure: {name}")


def audit_exported_pdf(path: Path) -> dict:
    """Inspect the exported artifact rather than trusting Matplotlib object state."""

    document = fitz.open(path)
    if len(document) != 1:
        raise RuntimeError(f"Figure postflight expected one page: {path.name}")
    page = document[0]
    spans = [
        span
        for block in page.get_text("dict")["blocks"]
        if block.get("type") == 0
        for line in block["lines"]
        for span in line["spans"]
        if span["text"].strip()
    ]
    if not spans:
        raise RuntimeError(f"Figure postflight found no visible text: {path.name}")
    font_names = sorted({span["font"] for span in spans})
    font_sizes = [float(span["size"]) for span in spans]
    incompatible_fonts = [
        name for name in font_names if "Arial" not in name and "Helvetica" not in name
    ]
    page_rect = page.rect
    clipped_text = [
        span["text"]
        for span in spans
        if span["bbox"][0] < -0.5
        or span["bbox"][1] < -0.5
        or span["bbox"][2] > page_rect.width + 0.5
        or span["bbox"][3] > page_rect.height + 0.5
    ]
    widths = [
        float(drawing["width"])
        for drawing in page.get_drawings()
        if isinstance(drawing.get("width"), numbers.Real) and drawing["width"] > 0
    ]
    if not widths:
        raise RuntimeError(f"Figure postflight found no positive vector line widths: {path.name}")
    checks = {
        "single_page": len(document) == 1,
        "arial_or_helvetica_compatible": not incompatible_fonts,
        "all_visible_text_8pt": min(font_sizes) >= 7.95 and max(font_sizes) <= 8.05,
        "minimum_positive_line_width_1pt": min(widths) >= 0.99,
        "all_text_within_page": not clipped_text,
    }
    if not all(checks.values()):
        raise RuntimeError(
            f"Exported figure contract failed for {path.name}: "
            f"{[name for name, passed in checks.items() if not passed]}"
        )
    return {
        "checks": checks,
        "font_names": font_names,
        "minimum_visible_text_pt": round(min(font_sizes), 3),
        "maximum_visible_text_pt": round(max(font_sizes), 3),
        "minimum_positive_line_width_pt": round(min(widths), 3),
        "visible_text_spans": len(spans),
        "vector_drawings_with_positive_width": len(widths),
    }


def main() -> None:
    if FIGURES.exists():
        shutil.rmtree(FIGURES)
    if PORTAL.exists():
        shutil.rmtree(PORTAL)
    env = os.environ.copy()
    env["NPJ_SBA_STYLE"] = "1"
    env["MPLBACKEND"] = "Agg"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "audit_tools/phase17_postc9_01_build_review_figures.py"),
            "--output-dir",
            str(FIGURES),
            "--c9-dir",
            str(C9),
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )
    generated_sources = sorted((FIGURES / "source_data").glob("*.csv"))
    if len(generated_sources) != 15:
        raise RuntimeError(f"Expected 15 figure source tables, found {len(generated_sources)}")
    source_audit = {}
    for current in generated_sources:
        prior = BASELINE / current.name
        if not prior.is_file():
            raise RuntimeError(f"Frozen baseline source is missing: {current.name}")
        same = sha256(current) == sha256(prior)
        if not same:
            raise RuntimeError(f"Frozen source data changed during npj rerender: {current.name}")
        source_audit[current.name] = {
            "sha256": sha256(current),
            "byte_identical_to_corrected_candidate": True,
        }
    pdfs = sorted((FIGURES / "figures").glob("*.pdf"))
    if len(pdfs) != 15:
        raise RuntimeError(f"Expected 15 vector PDFs, found {len(pdfs)}")
    PORTAL.mkdir(parents=True)
    dimensions = {}
    artifact_postflight = {}
    observed_names = set()
    for pdf in pdfs:
        reader = PdfReader(pdf)
        if len(reader.pages) != 1:
            raise RuntimeError(f"Figure is not a single-page vector PDF: {pdf.name}")
        page = reader.pages[0]
        width = float(page.mediabox.width) * 25.4 / 72
        height = float(page.mediabox.height) * 25.4 / 72
        if abs(width - 170.0) > 0.25 or height > 230:
            raise RuntimeError(f"Figure dimensions out of contract: {pdf.name} {width:.2f} x {height:.2f} mm")
        target_name = standard_name(pdf)
        if target_name in observed_names:
            raise RuntimeError(f"Duplicate standardized figure name: {target_name}")
        observed_names.add(target_name)
        shutil.copy2(pdf, PORTAL / target_name)
        artifact_postflight[target_name] = audit_exported_pdf(PORTAL / target_name)
        dimensions[target_name] = {
            "width_mm": round(width, 3),
            "height_mm": round(height, 3),
            "bytes": pdf.stat().st_size,
            "sha256": sha256(pdf),
        }
    expected = {f"Figure_{number}.pdf" for number in range(1, 6)} | {
        f"Supplementary_Figure_S{number}.pdf" for number in range(1, 11)
    }
    if observed_names != expected:
        raise RuntimeError(f"Figure inventory differs: {sorted(observed_names ^ expected)}")
    status = {
        "created_at": "2026-08-30",
        "status": "PASS_NPJ_SBA_SOURCE_RERENDER_ARTIFACT_CONTRACT_PENDING_VISUAL_REVIEW",
        "figure_count": 15,
        "main_figures": 5,
        "supplementary_figures": 10,
        "format": "single-page vector PDF",
        "width_mm": 170.0,
        "style_contract": {
            "font_family": "Arial",
            "target_visible_text_pt": 8.0,
            "panel_labels": "bold lower-case 8 pt",
            "minimum_positive_line_width_pt": 1.0,
            "color_mode": "RGB",
            "background": "white",
        },
        "source_tables_byte_identical": True,
        "source_data": source_audit,
        "figures": dimensions,
        "artifact_postflight": artifact_postflight,
        "artifact_postflight_all_pass": all(
            all(row["checks"].values()) for row in artifact_postflight.values()
        ),
        "scientific_reanalysis": False,
        "plotted_numeric_values_changed": False,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "corrected_external_outcome_unlock_authorized": False,
    }
    (RUN / "01_NPJ_FIGURE_RENDER_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: status[key] for key in ("status", "figure_count", "source_tables_byte_identical", "scientific_reanalysis")}, indent=2))


if __name__ == "__main__":
    main()
