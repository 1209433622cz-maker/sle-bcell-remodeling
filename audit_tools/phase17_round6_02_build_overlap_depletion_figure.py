#!/usr/bin/env python3
"""Build the Round 6 overlap-depletion supplementary figure from frozen outputs."""

from __future__ import annotations

import json
import argparse
import os
from datetime import datetime
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7/round6_q1_robustness/20260825_overlap_depletion"
RESULT_PATH = RUN_DIR / "01_OVERLAP_DEPLETION_RESULTS.csv"
FIGURE_DIR = RUN_DIR / "figures"
SOURCE_DIR = RUN_DIR / "source_data"
WIDTH_MM = 170.0

COLORS = {
    "STAT1": "#2C6EAD",
    "STAT2": "#009E73",
    "ifn12": "#D55E00",
    "m5911": "#7B6BA8",
    "dark": "#222222",
}
CONTRAST_LABELS = {
    "gse174188_primary": "Discovery",
    "gse174188_internal_nonoverlap": "Internal nonoverlap",
    "gse135779_childhood": "Childhood replication",
}
BRANCH_LABELS = {
    "frozen_ifn12_depleted": "Frozen 12-gene IFN/ISG depletion",
    "m5911_depleted": "M5911 depletion",
}


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6.2,
            "ytick.labelsize": 6.2,
            "legend.fontsize": 6.2,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(
        -0.12,
        1.04,
        label,
        transform=axis.transAxes,
        fontsize=8,
        fontweight="bold",
        va="bottom",
        ha="left",
    )


def style_axis(axis: plt.Axes) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(width=0.7, length=3)


def forest(axis: plt.Axes, rows: pd.DataFrame, label: str, title: str) -> None:
    rows = rows.copy()
    rows["contrast_order"] = rows["contrast"].map(
        {"gse174188_primary": 0, "gse174188_internal_nonoverlap": 1, "gse135779_childhood": 2}
    )
    rows["regulator_order"] = rows["regulator"].map({"STAT1": 0, "STAT2": 1})
    rows = rows.sort_values(["contrast_order", "regulator_order"])
    y = np.arange(len(rows))[::-1]
    for y_value, (_, row) in zip(y, rows.iterrows(), strict=True):
        axis.errorbar(
            row["estimate"],
            y_value,
            xerr=[[row["estimate"] - row["ci_low"]], [row["ci_high"] - row["estimate"]]],
            fmt="o",
            color=COLORS[row["regulator"]],
            ecolor=COLORS[row["regulator"]],
            markersize=3.4,
            elinewidth=0.85,
            capsize=1.5,
        )
        axis.text(
            row["ci_high"] + 0.05,
            y_value,
            f"{int(row['matched_targets_after'])} targets",
            fontsize=5.2,
            va="center",
            color="#555555",
        )
    axis.axvline(0, color="#666666", lw=0.65, ls="--")
    for separator in (1.5, 3.5):
        axis.axhline(separator, color="#E5E5E5", lw=0.55)
    axis.set_yticks(
        y,
        [f"{CONTRAST_LABELS[row.contrast]}  {row.regulator}" for row in rows.itertuples()],
    )
    axis.set_xlabel("ULM activity slope (95% CI)")
    axis.set_title(title, loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, label)


def main() -> None:
    global FIGURE_DIR, SOURCE_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=RUN_DIR)
    output_dir = parser.parse_args().output_dir.resolve()
    FIGURE_DIR = output_dir / "figures"
    SOURCE_DIR = output_dir / "source_data"
    configure_style()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    results = pd.read_csv(RESULT_PATH)

    if len(results) != 54:
        raise RuntimeError(f"Expected 54 total rows; found {len(results)}")
    depleted = results.loc[results["branch"].ne("baseline")].copy()
    if len(depleted) != 36 or not depleted["expected_direction"].all():
        raise RuntimeError("Depletion result count or direction assertion failed")
    ulm = depleted.loc[depleted["method"].eq("ULM")].copy()
    if len(ulm) != 12:
        raise RuntimeError("Expected 12 depleted ULM rows")

    source_path = SOURCE_DIR / "Supplementary_Figure_S8_source_data.csv"
    depleted.to_csv(source_path, index=False, lineterminator="\n")

    if os.environ.get("NPJ_SBA_STYLE") == "1":
        figure = plt.figure(figsize=(WIDTH_MM / 25.4, 215 / 25.4), constrained_layout=True)
        grid = figure.add_gridspec(3, 2, height_ratios=(1.0, 0.82, 0.92))
        axes = np.empty((2, 2), dtype=object)
        axes[0, 0] = figure.add_subplot(grid[0, 0])
        axes[0, 1] = figure.add_subplot(grid[0, 1])
        axes[1, 0] = figure.add_subplot(grid[1, :])
        axes[1, 1] = figure.add_subplot(grid[2, :])
    else:
        figure, axes = plt.subplots(2, 2, figsize=(WIDTH_MM / 25.4, 6.25), constrained_layout=True)
    forest(
        axes[0, 0],
        ulm.loc[ulm["branch"].eq("frozen_ifn12_depleted")],
        "a",
        "ULM after frozen 12-gene depletion",
    )
    forest(
        axes[0, 1],
        ulm.loc[ulm["branch"].eq("m5911_depleted")],
        "b",
        "ULM after M5911 depletion",
    )

    axis = axes[1, 0]
    q_table = depleted.pivot_table(
        index=["branch", "method"],
        columns=["contrast", "regulator"],
        values="q_value",
        aggfunc="first",
    )
    row_order = [
        (branch, method)
        for branch in ("frozen_ifn12_depleted", "m5911_depleted")
        for method in ("ULM", "CAMERA", "FRY")
    ]
    column_order = [
        (contrast, regulator)
        for contrast in ("gse174188_primary", "gse174188_internal_nonoverlap", "gse135779_childhood")
        for regulator in ("STAT1", "STAT2")
    ]
    q_table = q_table.reindex(index=pd.MultiIndex.from_tuples(row_order), columns=pd.MultiIndex.from_tuples(column_order))
    matrix = -np.log10(np.clip(q_table.to_numpy(float), 1e-12, 1.0))
    image = axis.imshow(matrix, cmap="viridis", aspect="auto", vmin=0, vmax=4)
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            q_value = q_table.iloc[row_index, column_index]
            red, green, blue, _ = image.cmap(image.norm(matrix[row_index, column_index]))
            luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
            color = "#111111" if luminance > 0.5 else "white"
            axis.text(column_index, row_index, f"{q_value:.2g}", ha="center", va="center", fontsize=5.0, color=color)
    axis.set_xticks(
        np.arange(len(column_order)),
        [f"{CONTRAST_LABELS[c].split()[0]}\n{r}" for c, r in column_order],
        rotation=35,
        ha="right",
    )
    axis.set_yticks(
        np.arange(len(row_order)),
        [f"{'12-gene' if b == 'frozen_ifn12_depleted' else 'M5911'} | {m}" for b, m in row_order],
    )
    axis.set_title("Dedicated six-test BH q values", loc="left", pad=4)
    panel_label(axis, "c")
    colorbar = figure.colorbar(image, ax=axis, fraction=0.045, pad=0.03)
    colorbar.set_label("-log10(q)", fontsize=6)
    colorbar.ax.tick_params(labelsize=5.5, width=0.6, length=2)

    axis = axes[1, 1]
    retention = ulm.copy()
    retention["label"] = retention["contrast"].map(CONTRAST_LABELS) + "  " + retention["regulator"]
    label_order = [
        f"{CONTRAST_LABELS[contrast]}  {regulator}"
        for contrast in ("gse174188_primary", "gse174188_internal_nonoverlap", "gse135779_childhood")
        for regulator in ("STAT1", "STAT2")
    ]
    y_positions = np.arange(len(label_order))[::-1]
    offsets = {"frozen_ifn12_depleted": 0.10, "m5911_depleted": -0.10}
    for branch, color, marker in (
        ("frozen_ifn12_depleted", COLORS["ifn12"], "o"),
        ("m5911_depleted", COLORS["m5911"], "s"),
    ):
        selected = retention.loc[retention["branch"].eq(branch)].set_index("label").reindex(label_order)
        axis.scatter(
            selected["target_retention_fraction"] * 100,
            y_positions + offsets[branch],
            s=22,
            marker=marker,
            color=color,
            edgecolors="none",
            label="12-gene depletion" if branch == "frozen_ifn12_depleted" else "M5911 depletion",
            zorder=3,
        )
    axis.axvline(100, color="#777777", lw=0.65, ls="--")
    axis.set_xlim(50, 103)
    axis.set_yticks(y_positions, label_order)
    axis.set_xlabel("Frozen targets retained (%)")
    axis.set_title("Regulon target retention", loc="left", pad=4)
    axis.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17))
    style_axis(axis)
    panel_label(axis, "d")

    stem = "Supplementary_Figure_S8_overlap_depletion"
    from publication_style_contract import apply_publication_style
    apply_publication_style(figure)
    pdf_path = FIGURE_DIR / f"{stem}.pdf"
    png_path = FIGURE_DIR / f"{stem}.png"
    figure.savefig(pdf_path)
    figure.savefig(png_path, dpi=600)
    plt.close(figure)

    page = PdfReader(pdf_path).pages[0]
    width_mm = float(page.mediabox.width) * 25.4 / 72
    height_mm = float(page.mediabox.height) * 25.4 / 72
    if abs(width_mm - WIDTH_MM) > 0.2:
        raise RuntimeError(f"Unexpected supplementary figure width: {width_mm:.3f} mm")
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "analysis_source_date": "2026-08-25",
        "status": "PASS_ROUND6_SUPPLEMENTARY_FIGURE_S8_BUILT",
        "figure_pdf": pdf_path.relative_to(ROOT).as_posix(),
        "figure_png": png_path.relative_to(ROOT).as_posix(),
        "source_data": source_path.relative_to(ROOT).as_posix(),
        "width_mm": round(width_mm, 3),
        "height_mm": round(height_mm, 3),
        "source_rows": len(depleted),
        "all_depleted_directions_up": True,
    }
    (output_dir / "06_SUPPLEMENTARY_FIGURE_S8_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
