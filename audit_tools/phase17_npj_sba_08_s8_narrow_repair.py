"""Replot only Supplementary Figure S8 from frozen data and verify the narrow repair."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from pypdf import PdfReader

from phase17_npj_sba_02_build_figures import audit_exported_pdf


ROOT = Path(__file__).resolve().parents[1]
RUN = Path(
    os.environ.get(
        "NPJ_SBA_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening",
    )
).resolve()
REPAIR_RUN = Path(
    os.environ.get(
        "NPJ_SBA_S8_REPAIR_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_s8_narrow_repair/20260830_source_replot_rebuild",
    )
).resolve()
BASELINE = ROOT / "phase17_v7/post_gateC9/20260828_corrected_candidate/source_data"
STEM = "Supplementary_Figure_S8_overlap_depletion"
SOURCE_NAME = "Supplementary_Figure_S8_source_data.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def figure_inventory() -> dict[str, str]:
    return {
        path.relative_to(RUN / "figures").as_posix(): sha256(path)
        for path in sorted((RUN / "figures/figures").glob("*.pdf"))
        + sorted((RUN / "figures/figures").glob("*.png"))
    }


def main() -> None:
    REPAIR_RUN.mkdir(parents=True, exist_ok=True)
    before = figure_inventory()
    source_path = RUN / "figures/source_data" / SOURCE_NAME
    baseline_path = BASELINE / SOURCE_NAME
    before_source_sha = sha256(source_path)
    if before_source_sha != sha256(baseline_path):
        raise RuntimeError("Pre-repair S8 source data differs from the frozen corrected candidate")

    env = os.environ.copy()
    env["NPJ_SBA_STYLE"] = "1"
    env["MPLBACKEND"] = "Agg"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "audit_tools/phase17_round6_02_build_overlap_depletion_figure.py"),
            "--output-dir",
            str(RUN / "figures"),
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )

    pdf = RUN / "figures/figures" / f"{STEM}.pdf"
    png = RUN / "figures/figures" / f"{STEM}.png"
    after_source_sha = sha256(source_path)
    if after_source_sha != before_source_sha:
        raise RuntimeError("S8 source data changed during the layout-only source replot")

    page = PdfReader(pdf).pages[0]
    width_mm = float(page.mediabox.width) * 25.4 / 72
    height_mm = float(page.mediabox.height) * 25.4 / 72
    if abs(width_mm - 170.0) > 0.05 or abs(height_mm - 155.0) > 0.05:
        raise RuntimeError(f"Unexpected repaired S8 dimensions: {width_mm:.3f} x {height_mm:.3f} mm")
    postflight = audit_exported_pdf(pdf)
    shutil.copy2(pdf, RUN / "portal_figures/Supplementary_Figure_S8.pdf")

    after = figure_inventory()
    changed = sorted(name for name in before if before[name] != after.get(name))
    expected_changed = sorted([f"figures/{STEM}.pdf", f"figures/{STEM}.png"])
    if not set(changed).issubset(expected_changed) or set(after) != set(before):
        raise RuntimeError(f"Unexpected figure inventory change: {changed}")

    figure_status_path = RUN / "01_NPJ_FIGURE_RENDER_STATUS.json"
    figure_status = json.loads(figure_status_path.read_text(encoding="utf-8"))
    figure_status["created_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    figure_status["status"] = "PASS_NPJ_SBA_S8_LAYOUT_REPAIR_SOURCE_DATA_FROZEN"
    figure_status["figures"]["Supplementary_Figure_S8.pdf"] = {
        "width_mm": round(width_mm, 3),
        "height_mm": round(height_mm, 3),
        "bytes": pdf.stat().st_size,
        "sha256": sha256(pdf),
    }
    figure_status["artifact_postflight"]["Supplementary_Figure_S8.pdf"] = postflight
    figure_status["artifact_postflight_all_pass"] = all(
        all(row["checks"].values()) for row in figure_status["artifact_postflight"].values()
    )
    figure_status["source_tables_byte_identical"] = True
    figure_status["scientific_reanalysis"] = False
    figure_status["plotted_numeric_values_changed"] = False
    figure_status["layout_only_repair"] = "Supplementary Figure S8: 170 x 215 mm to 170 x 155 mm"
    figure_status_path.write_text(json.dumps(figure_status, indent=2) + "\n", encoding="utf-8")

    result = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_S8_SOURCE_REPLOT_LAYOUT_ONLY",
        "source_data": {
            "rows": 36,
            "sha256_before": before_source_sha,
            "sha256_after": after_source_sha,
            "byte_identical_to_frozen_baseline": True,
        },
        "figure": {
            "pdf": pdf.relative_to(ROOT).as_posix(),
            "png": png.relative_to(ROOT).as_posix(),
            "width_mm": round(width_mm, 3),
            "height_mm": round(height_mm, 3),
            "pdf_sha256": sha256(pdf),
            "png_sha256": sha256(png),
            "artifact_postflight": postflight,
        },
        "changed_figure_artifacts": changed,
        "authorized_changed_figure_artifacts": expected_changed,
        "unchanged_figure_artifacts": len(before) - len(changed),
        "scientific_reanalysis": False,
        "plotted_numeric_values_changed": False,
        "manuscript_changed": False,
        "public_release_changed": False,
    }
    (REPAIR_RUN / "01_S8_SOURCE_REPLOT_STATUS.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
