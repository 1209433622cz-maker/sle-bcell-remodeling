#!/usr/bin/env python3
"""Rerender Figure 1 so the main figure owns the end-to-end identity boundary."""

from __future__ import annotations

import csv
import difflib
import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ["NPJ_SBA_STYLE"] = "1"

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

import phase17_c7_01_build_main_figures as artwork


ROOT = Path(__file__).resolve().parents[1]
PARENT_FIGURES = (
    ROOT
    / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order/figures"
)
PARENT_TEXT = (
    ROOT
    / "phase17_v7/npj_sba_supplementary_table_claim_owner/20260902_semantic_micropass"
)
RUN = ROOT / "phase17_v7/npj_sba_figure1_boundary_promotion/20260902_source_rerender_gate"
RECEIVED = ROOT / "00_project_management/figure1_boundary_promotion_2026-09-02/received"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
FIGURE1_SOURCE_SHA256 = "F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805"
S4_SOURCE_SHA256 = "46EE840F86CA33AA4F5FCE0A37EEFCB4DB23831533BBFA20400BAE50744F5D42"
MARKER_DECISION = ROOT / "phase17_v7/gateC2B4/20260815_two_level_state_repair/06_GATE_C2B4_ADVISOR_DECISION.json"

EXTERNAL_INPUTS = {
    Path("C:/Users/Administrator/Downloads/Figure1_candidate_state_jaccard_source_values.csv"):
        "Figure1_candidate_state_jaccard_source_values.csv",
    Path("C:/Users/Administrator/Downloads/SOURCE_HASH_PROVENANCE.txt"):
        "SOURCE_HASH_PROVENANCE.txt",
    Path("C:/Users/Administrator/Downloads/action_record_2026-09-02_figure1_boundary_promotion_hostile_audit.md"):
        "action_record_2026-09-02_figure1_boundary_promotion_hostile_audit.md",
    Path("C:/Users/Administrator/Downloads/PANEL_REOPEN_DECISION_MATRIX.csv"):
        "PANEL_REOPEN_DECISION_MATRIX.csv",
    Path("C:/Users/Administrator/Downloads/FIGURE1_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE.md"):
        "FIGURE1_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE.md",
    Path("C:/Users/Administrator/Downloads/Figure1_boundary_promotion_candidate_v3.png"):
        "Figure1_boundary_promotion_candidate_v3.png",
    Path("C:/Users/Administrator/.codex/attachments/f9833dc2-639c-48e7-b5c2-687873b3b3b0/pasted-text.txt"):
        "pasted_figure1_boundary_promotion_review_2026-09-02.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_text(path: Path) -> str:
    return " ".join((page.extract_text() or "") for page in PdfReader(path).pages)


def write_diff(path: Path, before: str, after: str) -> None:
    payload = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="Manuscript_before_figure1_boundary_promotion.md",
            tofile="Manuscript_after_figure1_boundary_promotion.md",
        )
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


def archive_external_inputs() -> dict[str, dict[str, object]]:
    RECEIVED.mkdir(parents=True, exist_ok=True)
    archived: dict[str, dict[str, object]] = {}
    for source, name in EXTERNAL_INPUTS.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = RECEIVED / name
        shutil.copy2(source, destination)
        archived[name] = {
            "source": str(source),
            "archived": destination.relative_to(ROOT).as_posix(),
            "bytes": destination.stat().st_size,
            "sha256": sha256(destination),
            "byte_identical": sha256(source) == sha256(destination),
        }
    return archived


def summarize_jaccard(
    figure1_source: pd.DataFrame, s4_source: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    frozen = figure1_source.loc[
        figure1_source["panel"].astype(str).eq("d")
        & figure1_source["series"].isin(["minimum Jaccard", "median Jaccard"])
    ].copy()
    frozen["kind"] = frozen["series"].str.replace(" Jaccard", "", regex=False).str.lower()
    frozen_summary = frozen.pivot(index="category", columns="kind", values="estimate").reset_index()
    frozen_summary = frozen_summary.rename(columns={"category": "state"})

    end_rows = s4_source.loc[s4_source["record_type"].eq("state_jaccard")].copy()
    end_rows["jaccard"] = pd.to_numeric(end_rows["jaccard"])
    end_summary = (
        end_rows.groupby("reference_state", sort=False)["jaccard"]
        .agg(minimum="min", median="median")
        .reset_index()
        .rename(columns={"reference_state": "state"})
    )
    order = pd.CategoricalDtype(["B_CONV", "B_ASC"], ordered=True)
    for frame in (frozen_summary, end_summary):
        frame["state"] = frame["state"].astype(order)
        frame.sort_values("state", inplace=True)
        frame["state"] = frame["state"].astype(str)
        frame.reset_index(drop=True, inplace=True)
    return frozen_summary, end_summary


def assert_summary_values(frozen: pd.DataFrame, end_to_end: pd.DataFrame) -> None:
    expected = {
        ("frozen", "B_CONV", "minimum"): 0.9998323301084824,
        ("frozen", "B_CONV", "median"): 0.999924551078872,
        ("frozen", "B_ASC", "minimum"): 0.9810964083175804,
        ("frozen", "B_ASC", "median"): 0.9913709736725989,
        ("end_to_end", "B_CONV", "minimum"): 0.9987595755736964,
        ("end_to_end", "B_CONV", "median"): 0.9993629961060673,
        ("end_to_end", "B_ASC", "minimum"): 0.8717504332755632,
        ("end_to_end", "B_ASC", "median"): 0.9303233364573571,
    }
    frames = {"frozen": frozen, "end_to_end": end_to_end}
    for (depth, state, metric), value in expected.items():
        actual = float(frames[depth].loc[frames[depth]["state"].eq(state), metric].iloc[0])
        if not np.isclose(actual, value, atol=1e-12, rtol=0):
            raise RuntimeError(f"Unexpected {depth} {state} {metric}: {actual} != {value}")


def build_source_data(
    original: pd.DataFrame, frozen: pd.DataFrame, end_to_end: pd.DataFrame
) -> pd.DataFrame:
    retained = original.loc[original["panel"].astype(str).isin(["a", "b"])].copy()
    rows = retained.to_dict("records")
    for panel, depth, frame in (("c", "fixed representation", frozen), ("d", "end-to-end reconstruction", end_to_end)):
        for _, row in frame.iterrows():
            for metric in ("minimum", "median"):
                rows.append(
                    {
                        "panel": panel,
                        "series": f"{metric} Jaccard",
                        "category": row["state"],
                        "estimate": float(row[metric]),
                        "secondary_value": 0.95,
                        "detail": f"{depth}; state-median criterion=0.95",
                    }
                )
    rows.append(
        {
            "panel": "c",
            "series": "B_ASC marker support",
            "category": "DERL3|JCHAIN|MZB1|TNFRSF17|XBP1",
            "estimate": 5,
            "secondary_value": 1.0,
            "detail": "required markers present; minimum required-marker sample support",
        }
    )
    return pd.DataFrame(rows, columns=original.columns)


def draw_panel_a(axis: plt.Axes) -> None:
    axis.set_axis_off()
    artwork.panel_label(axis, "a", x=-0.06, y=1.03)
    axis.set_title("Inference workflow and identity scope", loc="left", pad=4)
    node_style = {
        "transform": axis.transAxes,
        "ha": "center",
        "va": "center",
        "linespacing": 1.08,
        "bbox": {"boxstyle": "round,pad=0.20", "facecolor": "white", "linewidth": 0.8},
    }
    for x_value, label, color in (
        (0.18, "Input\n150,402 B-lineage cells", artwork.COLORS["internal"]),
        (0.70, "Disease-blind identity\nstress tests (b-d)", artwork.COLORS["secondary"]),
    ):
        style = dict(node_style)
        style["bbox"] = dict(node_style["bbox"], edgecolor=color)
        axis.text(x_value, 0.83, label, fontsize=6.85, **style)
    axis.annotate("", xy=(0.52, 0.83), xytext=(0.35, 0.83), xycoords=axis.transAxes,
                  arrowprops={"arrowstyle": "-|>", "lw": 0.75, "color": artwork.COLORS["dark"]})
    style = dict(node_style)
    style["bbox"] = dict(node_style["bbox"], edgecolor=artwork.COLORS["teal"])
    axis.text(0.50, 0.65, "Retained analysis scaffold: B_CONV / B_ASC", fontsize=6.9,
              fontweight="bold", **style)
    axis.annotate("", xy=(0.55, 0.70), xytext=(0.67, 0.77), xycoords=axis.transAxes,
                  arrowprops={"arrowstyle": "-|>", "lw": 0.75, "color": artwork.COLORS["dark"]})
    style = dict(node_style)
    style["bbox"] = dict(node_style["bbox"], edgecolor=artwork.COLORS["dark"])
    axis.text(0.50, 0.49, "Disease fields joined after identity adjudication", fontsize=6.75,
              fontweight="bold", **style)
    axis.annotate("", xy=(0.50, 0.55), xytext=(0.50, 0.60), xycoords=axis.transAxes,
                  arrowprops={"arrowstyle": "-|>", "lw": 0.75, "color": artwork.COLORS["dark"]})
    for x_value, label, color in (
        (0.27, "Composition\nB_ASC sample-cohort\nfractions", artwork.COLORS["sle"]),
        (0.73, "Transcription\nB_CONV sample-cohort\npseudobulk", artwork.COLORS["ifn"]),
    ):
        style = dict(node_style)
        style["bbox"] = dict(node_style["bbox"], edgecolor=color)
        axis.text(x_value, 0.30, label, fontsize=6.15, **style)
    for end in ((0.32, 0.38), (0.68, 0.38)):
        axis.annotate("", xy=end, xytext=(0.50, 0.44), xycoords=axis.transAxes,
                      arrowprops={"arrowstyle": "-|>", "lw": 0.75, "color": artwork.COLORS["dark"]})
    axis.text(0.50, 0.11, "Retained: broad-compartment disease analyses", transform=axis.transAxes,
              ha="center", va="center", fontsize=7.15, fontweight="bold", color=artwork.COLORS["teal"])
    axis.text(0.50, 0.015, "Boundary: hard fine-state assignments unsupported", transform=axis.transAxes,
              ha="center", va="center", fontsize=6.8, fontweight="bold", color="#555555")


def draw_panel_b(axis: plt.Axes, source: pd.DataFrame) -> None:
    categories = ["5-state", "4-state", "3-state", "2-compartment"]
    minimum = source.loc[(source["panel"].astype(str) == "b") & (source["series"] == "minimum mapped ARI")]
    median = source.loc[(source["panel"].astype(str) == "b") & (source["series"] == "median mapped ARI")]
    minimum = minimum.set_index("category").loc[categories]
    median = median.set_index("category").loc[categories]
    x_values = np.arange(4)
    for x_value, low, high in zip(x_values, minimum["estimate"], median["estimate"], strict=True):
        axis.plot([x_value, x_value], [low, high], color=artwork.COLORS["light"], lw=1.0, zorder=1)
    axis.scatter(x_values, median["estimate"], marker="o", color=artwork.COLORS["internal"], s=14,
                 label="Median ARI", zorder=3)
    axis.scatter(x_values, minimum["estimate"], marker="D", color=artwork.COLORS["secondary"], s=12,
                 label="Minimum ARI", zorder=3)
    axis.hlines(0.90, 2.62, 3.38, color="#666666", lw=0.7, ls="--")
    axis.text(3.34, 0.884, "2-compartment minimum-ARI criterion", fontsize=5.5,
              ha="right", va="top", color="#555555")
    axis.set_xticks(x_values, categories, rotation=25, ha="right")
    axis.set_ylabel("Mapped adjusted Rand index")
    axis.set_ylim(0.28, 1.03)
    axis.legend(frameon=False, fontsize=6, loc="lower left")
    axis.set_title("Fixed-representation policy selection", loc="left", pad=4)
    artwork.style_axis(axis)
    artwork.panel_label(axis, "b")


def draw_jaccard_panel(axis: plt.Axes, frame: pd.DataFrame, *, panel: str, title: str, marker_note: bool) -> None:
    y_values = {"B_CONV": 1, "B_ASC": 0}
    for _, row in frame.iterrows():
        y_value = y_values[row["state"]]
        axis.plot([row["minimum"], row["median"]], [y_value, y_value], color="#8A8A8A", lw=1.0, zorder=1)
        axis.plot(row["minimum"], y_value, "D", color=artwork.COLORS["secondary"], ms=3.4, zorder=3)
        axis.plot(row["median"], y_value, "o", color=artwork.COLORS["internal"], ms=3.8, zorder=3)
        label = f"{float(row['minimum']):.4f}-{float(row['median']):.4f}"
        if row["state"] == "B_CONV":
            axis.text(0.9998, y_value, label, ha="right", va="bottom", fontsize=5.5, color="#333333")
        elif marker_note:
            axis.text(float(row["median"]) + 0.002, y_value, label, ha="left", va="center", fontsize=5.5, color="#333333")
        else:
            axis.text(float(row["median"]) - 0.002, y_value + 0.08, label, ha="right", va="center", fontsize=5.5, color="#333333")
    axis.axvline(0.95, color="#666666", lw=0.7, ls="--")
    axis.text(0.9515, 1.24, "state-median criterion", fontsize=5.5, ha="left", va="top", color="#555555")
    axis.set_yticks([1, 0], ["B_CONV", "B_ASC"])
    axis.set_ylim(-0.5, 1.45)
    axis.set_xlim(0.86, 1.002)
    axis.set_xlabel("State Jaccard (minimum to median)")
    if marker_note:
        axis.text(0.862, -0.36, "B_ASC marker support: 5/5; minimum sample support = 1.00",
                  fontsize=5.5, ha="left", va="center", color="#555555",
                  bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.8})
    else:
        axis.text(0.862, -0.36, "B_ASC median 0.930 < 0.95 criterion",
                  fontsize=5.5, ha="left", va="center", color=artwork.COLORS["sle"], fontweight="bold")
    axis.set_title(title, loc="left", pad=4)
    artwork.style_axis(axis)
    artwork.panel_label(axis, panel)


def render_figure(source: pd.DataFrame, frozen: pd.DataFrame, end_to_end: pd.DataFrame) -> tuple[Path, Path]:
    figure_dir = RUN / "figures/figures"
    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.45), constrained_layout=True)
    draw_panel_a(axes[0, 0])
    draw_panel_b(axes[0, 1], source)
    draw_jaccard_panel(
        axes[1, 0], frozen, panel="c", title="Fixed representation: overlap criterion met", marker_note=True
    )
    draw_jaccard_panel(
        axes[1, 1], end_to_end, panel="d", title="End-to-end reconstruction: B_ASC criterion not met", marker_note=False
    )
    artwork.ASSERTIONS.clear()
    artwork.set_output_width_mm(170.0)
    artwork.save_figure(figure, figure_dir, "Figure1_disease_blind_identity_scope")
    return (
        figure_dir / "Figure1_disease_blind_identity_scope.pdf",
        figure_dir / "Figure1_disease_blind_identity_scope.png",
    )


def comparison_sheet(current: Path, candidate: Path, output: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in (current, candidate)]
    target_width = 1800
    resized = [image.resize((target_width, round(image.height * target_width / image.width))) for image in images]
    header = 70
    canvas = Image.new("RGB", (target_width * 2, max(image.height for image in resized) + header), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except OSError:
        font = ImageFont.load_default()
    draw.text((30, 18), "Current frozen Figure 1", fill="black", font=font)
    draw.text((target_width + 30, 18), "Boundary-promotion source rerender", fill="black", font=font)
    for index, image in enumerate(resized):
        canvas.paste(image, (index * target_width, header))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def patch_manuscript() -> tuple[str, str, list[dict[str, str]]]:
    parent = PARENT_TEXT / "sources/Manuscript_claim_owner_semantic_micropass.md"
    before = parent.read_text(encoding="utf-8")
    replacements = [
        (
            "F1-XREF-1",
            "Fixed-representation result points only to Figure 1a-c",
            "(Fig. 1a-d).",
            "(Fig. 1a-c).",
        ),
        (
            "F1-XREF-2",
            "Promote the end-to-end boundary to Figure 1d while retaining S4 detail ownership",
            "The failure was confined to B_ASC (median Jaccard 0.930; minimum 0.872), whereas B_CONV remained highly concordant (median 0.99936; minimum 0.99876). A median of 76 of 120,320 sampled cells exchanged broad-state assignment per replicate (Supplementary Fig. S4).",
            "The failure was confined to B_ASC (median Jaccard 0.930; minimum 0.872), whereas B_CONV remained highly concordant (median 0.99936; minimum 0.99876; Fig. 1d; Supplementary Fig. S4). A median of 76 of 120,320 sampled cells exchanged broad-state assignment per replicate.",
        ),
        (
            "F1-LEGEND",
            "Synchronize Figure 1c/d ownership with the source rerender",
            "a, Inference workflow and identity scope. Disease-blind identity stress tests defined B_CONV/B_ASC as an analysis scaffold. Disease fields were joined only after identity adjudication; B_ASC composition and B_CONV transcription were then analysed at the sample-cohort stratum. Hard fine-state assignments were not used for disease inference. b, Median mapped adjusted Rand index and minimum-to-median interval for candidate identity policies across 20 within-library resamples of the fixed 50-dimensional Harmony representation; the dashed segment marks the two-compartment minimum-ARI criterion of 0.90. c, Mapped adjusted Rand index and mapping agreement for each two-compartment resample; the dashed guide marks the 0.990 minimum-agreement criterion. d, Minimum and median state Jaccard indices for B_CONV and B_ASC with B_ASC marker support; the dashed guide marks the 0.95 state-median criterion. Panels b-d hold the representation fixed; end-to-end reconstruction is shown in Supplementary Fig. S4. Cell-level stability metrics are not disease replicates.",
            "a, Disease-blind B_CONV/B_ASC adjudication preceded sample-cohort analyses; hard fine states were not used. b, Median/minimum mapped ARI across 20 within-library fixed 50-dimensional Harmony resamples; dashed segment, minimum-ARI criterion 0.90. c, Fixed-representation minimum-to-median state Jaccard; dashed guide, criterion 0.95. B_ASC markers 5/5; minimum sample support 1.00. d, End-to-end minimum-to-median state Jaccard across 20 rebuilds; B_ASC below 0.95, B_CONV concordant. Panels b/c fix the representation; d recomputes highly variable genes, principal components and Harmony. Supplementary Fig. S4 provides replicate diagnostics/downstream propagation. Cell metrics are not disease replicates.",
        ),
    ]
    after = before
    ledger: list[dict[str, str]] = []
    for edit_id, purpose, old, new in replacements:
        if after.count(old) != 1:
            raise RuntimeError(f"Expected one manuscript anchor for {edit_id}, found {after.count(old)}")
        after = after.replace(old, new)
        ledger.append({
            "edit_id": edit_id,
            "purpose": purpose,
            "before": old,
            "after": new,
            "scientific_value_changed": "False",
        })
    return before, after, ledger


def write_panel_matrix() -> Path:
    source = PARENT_FIGURES.parent / "02_PANEL_DECISION_MATRIX.csv"
    rows = list(csv.DictReader(source.open(encoding="utf-8-sig", newline="")))
    updates = {
        "Figure 1a": ("KEEP", "SOURCE_RERENDER_SAME_ROLE", "Workflow role retained; rerendered only because the composite figure changed."),
        "Figure 1b": ("KEEP", "SOURCE_RERENDER_SAME_ROLE", "Policy-selection role and frozen values retained."),
        "Figure 1c": ("KEEP_RELOCATED", "CURRENT_1D_TO_1C", "Frozen state-Jaccard summary replaces the redundant replicate-series slot."),
        "Figure 1d": ("SOURCE_REPLACEMENT", "S4_BOUNDARY_SUMMARY", "End-to-end B_ASC overlap boundary promoted from frozen S4 Source Data."),
    }
    for row in rows:
        if row["object"] in updates:
            row["scientific_decision"], row["artwork_action"], row["rationale"] = updates[row["object"]]
    output = RUN / "02_PANEL_DECISION_MATRIX.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output


def main() -> None:
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-confirmed submission package changed")
    if RUN.exists():
        shutil.rmtree(RUN)
    RUN.mkdir(parents=True)
    archived_inputs = archive_external_inputs()

    shutil.copytree(PARENT_FIGURES, RUN / "figures")
    source_inputs = RUN / "source_inputs"
    source_inputs.mkdir()
    original_source = PARENT_FIGURES / "source_data/Figure1_source_data.csv"
    s4_source_path = PARENT_FIGURES / "source_data/Supplementary_Figure_S4_source_data.csv"
    if sha256(original_source) != FIGURE1_SOURCE_SHA256 or sha256(s4_source_path) != S4_SOURCE_SHA256:
        raise RuntimeError("Frozen Figure 1 or S4 source hash changed")
    shutil.copy2(original_source, source_inputs / "Figure1_source_data_frozen_input.csv")
    shutil.copy2(s4_source_path, source_inputs / "Supplementary_Figure_S4_source_data_frozen_input.csv")
    shutil.copy2(MARKER_DECISION, source_inputs / MARKER_DECISION.name)

    original = pd.read_csv(original_source)
    s4 = pd.read_csv(s4_source_path)
    frozen, end_to_end = summarize_jaccard(original, s4)
    assert_summary_values(frozen, end_to_end)
    candidate_values = pd.read_csv(RECEIVED / "Figure1_candidate_state_jaccard_source_values.csv")
    independently_derived = pd.concat(
        [
            frozen.assign(reconstruction_depth="frozen"),
            end_to_end.assign(reconstruction_depth="end_to_end"),
        ],
        ignore_index=True,
    ).rename(columns={"state": "state", "minimum": "minimum_jaccard", "median": "median_jaccard"})
    independently_derived["state_median_criterion"] = 0.95
    independently_derived = independently_derived[
        ["reconstruction_depth", "state", "minimum_jaccard", "median_jaccard", "state_median_criterion"]
    ]
    candidate_values = candidate_values[independently_derived.columns]
    if not candidate_values["reconstruction_depth"].equals(independently_derived["reconstruction_depth"]):
        raise RuntimeError("External candidate depth ordering differs from independent derivation")
    if not candidate_values["state"].equals(independently_derived["state"]):
        raise RuntimeError("External candidate state ordering differs from independent derivation")
    for column in ("minimum_jaccard", "median_jaccard", "state_median_criterion"):
        if not np.allclose(candidate_values[column], independently_derived[column], atol=1e-12, rtol=0):
            raise RuntimeError(f"External candidate values disagree in {column}")
    independently_derived.to_csv(RUN / "01_FIGURE1_JACCARD_DERIVATION.csv", index=False, lineterminator="\n")

    new_source = build_source_data(original, frozen, end_to_end)
    new_source_path = RUN / "figures/source_data/Figure1_source_data.csv"
    new_source.to_csv(new_source_path, index=False, lineterminator="\n")
    pdf_path, png_path = render_figure(new_source, frozen, end_to_end)

    current_png = PARENT_FIGURES / "figures/Figure1_disease_blind_identity_scope.png"
    comparison_sheet(current_png, png_path, RUN / "qa/Figure1_current_vs_boundary_promotion.png")
    text = pdf_text(pdf_path)
    width_mm = float(PdfReader(pdf_path).pages[0].mediabox.width) * 25.4 / 72.0
    marker_decision = json.loads(MARKER_DECISION.read_text(encoding="utf-8"))
    figure_checks = {
        "single_page_pdf": len(PdfReader(pdf_path).pages) == 1,
        "width_170_mm": abs(width_mm - 170.0) < 0.15,
        "all_panel_labels_present": all(re.search(rf"\b{label}\b", text) for label in "abcd"),
        "fixed_boundary_title_present": "Fixed representation: overlap criterion met" in text,
        "end_to_end_boundary_title_present": "End-to-end reconstruction: B_ASC criterion not met" in text,
        "shared_criterion_present": text.count("state-median criterion") == 2,
        "marker_support_source_pass": marker_decision["checks"]["asc_marker_panel"]["pass"] and marker_decision["checks"]["asc_marker_sample_support"]["pass"],
        "publication_style_assertions_pass": all(row["pass"] for row in artwork.ASSERTIONS),
    }

    before, after, ledger = patch_manuscript()
    sources = RUN / "sources"
    sources.mkdir()
    (sources / "Manuscript_before_figure1_boundary_promotion.md").write_text(before, encoding="utf-8", newline="\n")
    candidate_manuscript = sources / "Manuscript_figure1_boundary_promotion.md"
    candidate_manuscript.write_text(after, encoding="utf-8", newline="\n")
    parent_supplement = PARENT_TEXT / "sources/Supplementary_Information_unchanged.md"
    shutil.copy2(parent_supplement, sources / "Supplementary_Information_unchanged.md")
    root_main = ROOT / "01_manuscript/Manuscript.md"
    root_supplement = ROOT / "01_manuscript/Supplementary_Information.md"
    allowed_root_hashes = {hashlib.sha256(before.encode()).hexdigest().upper(), hashlib.sha256(after.encode()).hexdigest().upper()}
    if sha256(root_main) not in allowed_root_hashes:
        previous_legend = (
            "a, Disease-blind B_CONV/B_ASC adjudication preceded sample-cohort B_ASC composition and B_CONV transcription; hard fine states were not used. b, Median and minimum mapped adjusted Rand index across 20 within-library resamples of the fixed 50-dimensional Harmony representation; the dashed segment marks the two-compartment minimum-ARI criterion of 0.90. c, Fixed-representation minimum-to-median state Jaccard; the dashed guide marks 0.95. B_ASC marker support was 5/5, with minimum sample support of 1.00. d, End-to-end minimum-to-median state Jaccard across 20 rebuilds; B_ASC did not meet 0.95, whereas B_CONV remained concordant. Panels b and c hold the representation fixed; d recomputes highly variable genes, principal components and Harmony. Supplementary Fig. S4 provides replicate-level diagnostics and downstream propagation. Cell-level metrics are not disease replicates."
        )
        new_legend = after.split("### Figure 1 |", 1)[1].split("\n\n### Figure 2 |", 1)[0].split("\n\n", 1)[1]
        normalized_root = root_main.read_text(encoding="utf-8").replace(previous_legend, new_legend)
        if hashlib.sha256(normalized_root.encode()).hexdigest().upper() != hashlib.sha256(after.encode()).hexdigest().upper():
            raise RuntimeError("Root manuscript is outside the exact parent/candidate boundary")
    if sha256(root_supplement) != sha256(parent_supplement):
        raise RuntimeError("Root Supplementary Information drifted")
    root_main.write_text(after, encoding="utf-8", newline="\n")
    write_diff(RUN / "04_MANUSCRIPT_FIGURE1_BOUNDARY_PROMOTION.diff", before, after)
    with (RUN / "03_TEXT_EDIT_LEDGER.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)
    panel_matrix = write_panel_matrix()

    frozen_assets = sorted((RUN / "figures/figures").glob("*")) + sorted((RUN / "figures/source_data").glob("*.csv"))
    changed_assets = []
    for path in frozen_assets:
        parent = PARENT_FIGURES / path.relative_to(RUN / "figures")
        if sha256(path) != sha256(parent):
            changed_assets.append(path.name)
    displayed_jaccard = new_source.loc[
        new_source["series"].isin(["minimum Jaccard", "median Jaccard"])
    ].copy()
    displayed_c = displayed_jaccard.loc[displayed_jaccard["panel"].astype(str).eq("c"), "estimate"].astype(float)
    displayed_d = displayed_jaccard.loc[displayed_jaccard["panel"].astype(str).eq("d"), "estimate"].astype(float)
    expected_c = frozen[["minimum", "median"]].to_numpy(dtype=float).ravel()
    expected_d = end_to_end[["minimum", "median"]].to_numpy(dtype=float).ravel()
    checks = {
        "external_inputs_archived_byte_identically": all(item["byte_identical"] for item in archived_inputs.values()),
        "frozen_source_hashes_match": sha256(original_source) == FIGURE1_SOURCE_SHA256 and sha256(s4_source_path) == S4_SOURCE_SHA256,
        "external_candidate_values_independently_confirmed": True,
        "new_figure_source_contains_only_verified_summaries": (
            np.allclose(np.sort(displayed_c), np.sort(expected_c), atol=1e-12, rtol=0)
            and np.allclose(np.sort(displayed_d), np.sort(expected_d), atol=1e-12, rtol=0)
        ),
        "only_figure1_pdf_png_and_source_changed": sorted(changed_assets) == sorted([
            "Figure1_disease_blind_identity_scope.pdf",
            "Figure1_disease_blind_identity_scope.png",
            "Figure1_source_data.csv",
        ]),
        "figure_render_checks_pass": all(figure_checks.values()),
        "three_exact_text_operations": len(ledger) == 3,
        "fixed_result_points_to_figure1_a_c": "itself (Fig. 1a-c)." in after,
        "end_to_end_result_points_to_figure1d_and_s4": "Fig. 1d; Supplementary Fig. S4" in after,
        "supplementary_information_unchanged": sha256(root_supplement) == sha256(parent_supplement),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FIGURE1_BOUNDARY_PROMOTION_SOURCE_RERENDER_DOCX_REQUIRED" if not failed else "HOLD_FIGURE1_BOUNDARY_PROMOTION",
        "checks": checks,
        "failed_checks": failed,
        "figure_checks": figure_checks,
        "archived_inputs": archived_inputs,
        "source_hashes": {"Figure1_source_data.csv": FIGURE1_SOURCE_SHA256, "Supplementary_Figure_S4_source_data.csv": S4_SOURCE_SHA256},
        "source_data_values_changed": False,
        "statistical_models_rerun": False,
        "figure1_redrawn_from_frozen_sources": True,
        "current_figure1c_source_preserved": (source_inputs / "Figure1_source_data_frozen_input.csv").relative_to(ROOT).as_posix(),
        "changed_assets": changed_assets,
        "panel_matrix": panel_matrix.relative_to(ROOT).as_posix(),
        "manuscript": candidate_manuscript.relative_to(ROOT).as_posix(),
        "figure": {"pdf": pdf_path.relative_to(ROOT).as_posix(), "png": png_path.relative_to(ROOT).as_posix(), "width_mm": round(width_mm, 3)},
        "submission_package_sha256": sha256(PACKAGE),
        "submission_package_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
    }
    (RUN / "00_FIGURE1_BOUNDARY_PROMOTION_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (RUN / ".gitignore").write_text("qa/lo_render/\nqa/wps_pages/*/\nqa/lo_pages/*/\n", encoding="ascii", newline="\n")
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Figure 1 integration checks failed: {failed}")


if __name__ == "__main__":
    main()
