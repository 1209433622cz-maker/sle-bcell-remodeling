#!/usr/bin/env python3
"""Integrate the S3/S5 display prune without reopening frozen analyses."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text
import numpy as np
import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "phase17_v7/npj_sba_reference_terminology_lock/"
    "20260901_reference_terminology_s6_refreeze"
)
RUN = (
    ROOT
    / "phase17_v7/npj_sba_integrated_reader_refreeze/"
    "20260901_s3_s5_reader_path_refreeze"
)
RECEIVED = ROOT / "00_project_management/integrated_reader_prune_2026-09-01/received"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
SOURCE_HASHES = {
    "Figure1_source_data.csv": "F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805",
    "Supplementary_Figure_S3_source_data.csv": "133E973C2753F4946A24739C049308152299A915A3FC6754B30AD0521F979C96",
    "Figure3_source_data.csv": "DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8",
    "Supplementary_Figure_S5_source_data.csv": "F6682D636C1FF3A1784E0B9E8AEFF5C5D1BB075176312E87FCB938F65C4DA897",
}

MM = 1 / 25.4
COLORS = {
    "blue": "#2C6EAD",
    "red": "#C43C39",
    "teal": "#238B8E",
    "gold": "#E69F00",
    "purple": "#7B6BA8",
    "grey": "#777777",
    "light": "#C8CED4",
    "dark": "#222222",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_reset(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to((ROOT / "phase17_v7").resolve()):
        raise RuntimeError(f"Refusing to reset path outside phase17_v7: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; observed {count}")
    return text.replace(old, new, 1)


def require_arial() -> str:
    try:
        path = font_manager.findfont("Arial", fallback_to_default=False)
    except Exception as exc:
        raise RuntimeError(f"Arial is required for the display refreeze: {exc}") from exc
    if "arial" not in Path(path).name.lower():
        raise RuntimeError(f"Resolved font is not Arial: {path}")
    return path


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 6,
            "axes.titlesize": 7,
            "axes.labelsize": 6,
            "axes.linewidth": 0.6,
            "axes.titlepad": 3,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "xtick.major.width": 0.5,
            "ytick.major.width": 0.5,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "legend.fontsize": 6,
            "lines.linewidth": 0.8,
            "patch.linewidth": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def style_axis(axis: plt.Axes) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(direction="out")


def panel_label(axis: plt.Axes, label: str, *, x: float = -0.13) -> None:
    axis.text(
        x,
        1.04,
        label,
        transform=axis.transAxes,
        fontsize=8,
        fontweight="bold",
        va="bottom",
        ha="left",
    )


def save_exact(figure: plt.Figure, output_pdf: Path, width_mm: float, height_mm: float) -> dict[str, object]:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    figure.set_size_inches(width_mm * MM, height_mm * MM, forward=True)
    figure.canvas.draw()
    visible_sizes = [
        float(item.get_fontsize())
        for item in figure.findobj(match=Text)
        if item.get_visible() and item.get_text().strip()
    ]
    minimum_size = min(visible_sizes)
    if minimum_size < 6.0:
        raise RuntimeError(f"Visible text below 6 pt in {output_pdf.name}: {minimum_size:.2f}")
    figure.savefig(output_pdf, bbox_inches=None, pad_inches=0)
    png = output_pdf.with_suffix(".png")
    figure.savefig(png, dpi=600, bbox_inches=None, pad_inches=0)
    plt.close(figure)
    page = PdfReader(output_pdf).pages[0]
    return {
        "pdf": output_pdf.relative_to(ROOT).as_posix(),
        "png": png.relative_to(ROOT).as_posix(),
        "pdf_sha256": sha256(output_pdf),
        "png_sha256": sha256(png),
        "width_mm": float(page.mediabox.width) * 25.4 / 72.0,
        "height_mm": float(page.mediabox.height) * 25.4 / 72.0,
        "minimum_visible_text_pt": minimum_size,
    }


def copy_frozen_objects() -> None:
    shutil.copytree(BASE / "figures", RUN / "figures")
    figure_dir = RUN / "figures/figures"
    for pattern in (
        "Supplementary_Figure_S3_*.pdf",
        "Supplementary_Figure_S3_*.png",
        "Supplementary_Figure_S5_*.pdf",
        "Supplementary_Figure_S5_*.png",
    ):
        for path in figure_dir.glob(pattern):
            path.unlink()


def integrate_sources() -> tuple[Path, Path, dict[str, object]]:
    source_dir = RUN / "sources"
    source_dir.mkdir(parents=True)
    manuscript_base = BASE / "sources/Manuscript_reference_terminology_s6_refreeze.md"
    supplement_base = BASE / "sources/Supplementary_Information_reference_terminology_s6_refreeze.md"
    manuscript_text = manuscript_base.read_text(encoding="utf-8")
    supplement_text = supplement_base.read_text(encoding="utf-8")

    manuscript_text = replace_once(
        manuscript_text,
        "which B-cell features survive increasingly stringent reconstruction and validation, and which remain cohort-specific, representation-dependent or mechanistically unproven.",
        "which B-cell features survive increasingly stringent reconstruction and replication tests, and which remain cohort-specific, representation-dependent or mechanistically unproven.",
        "Introduction evidence-hierarchy sentence",
    )
    manuscript_text = replace_once(
        manuscript_text,
        "Retaining the failed reconstruction and calibration criteria narrows, rather than weakens, the conclusion: the data support a bounded interferon association, not a universal B-cell taxonomy, generalized B_ASC expansion, causal regulator, unique upstream stimulus or established clinical utility.",
        "Retaining the failed reconstruction and calibration criteria narrows, rather than weakens, the conclusion: the data support a bounded process-level interferon association within explicit identity and transfer limits.",
        "final Discussion boundary sentence",
    )
    supplement_text = replace_once(
        supplement_text,
        "## Supplementary Figure S3 | Disease-blind identity adjudication\n\n**a,** Median and worst-case mapped ARI for five-, four-, three- and two-level policies across frozen-representation resamples. **b,** Median and minimum cluster Jaccard values show localization of failure to fine-state membership. **c,** Mean transition matrix from original resolution-0.4 clusters to mapped reference clusters. **d,** Minimum-to-median Jaccard intervals for the B_CONV and B_ASC analysis states across 20 frozen-representation resamples. Highly variable genes, principal components and Harmony coordinates were not recomputed in this figure.",
        "## Supplementary Figure S3 | Fine-state failure and transition structure\n\n**a,** Median and minimum cluster Jaccard values localize instability to fine-state membership across the five-, four- and three-state policies considered before broad adjudication. **b,** Mean transition matrix from original resolution-0.4 clusters to mapped reference clusters across frozen-representation resamples. These diagnostics explain the transition to the broad B_CONV/B_ASC analysis scaffold; broad-state pass criteria are shown in Fig. 1 and end-to-end reconstruction is shown in Supplementary Fig. S9. Highly variable genes, principal components and Harmony coordinates were not recomputed in this figure.",
        "Supplementary Figure S3 legend",
    )
    supplement_text = replace_once(
        supplement_text,
        "**a,** Numbers of filterByExpr-tested and BH-significant genes across seven GSE174188 branches. **b,** Common and median tagwise edgeR dispersions. **c,** Mitochondrial, ribosomal, haemoglobin and immunoglobulin fractions among increasingly long primary ranked lists. **d,** IFN/ISG effects and 95% confidence intervals across frozen branches.",
        "**a,** Numbers of filterByExpr-tested and BH-significant genes across seven GSE174188 branches. **b,** Common and median tagwise edgeR dispersions. **c,** Mitochondrial, ribosomal, haemoglobin and immunoglobulin fractions among increasingly long primary ranked lists. IFN/ISG estimates across the frozen GSE174188 branches are owned by Fig. 3b and are not repeated here.",
        "Supplementary Figure S5 legend",
    )

    manuscript = source_dir / "Manuscript_integrated_reader_refreeze.md"
    supplement = source_dir / "Supplementary_Information_integrated_reader_refreeze.md"
    manuscript.write_text(manuscript_text, encoding="utf-8", newline="\n")
    supplement.write_text(supplement_text, encoding="utf-8", newline="\n")
    candidate_main = (RECEIVED / "Manuscript_integrated_reader_prune_candidate.md").read_text(encoding="utf-8")
    candidate_supp = (RECEIVED / "Supplementary_Information_integrated_reader_prune_candidate.md").read_text(encoding="utf-8")
    checks = {
        "manuscript_matches_reviewed_candidate": manuscript_text == candidate_main,
        "supplement_matches_reviewed_candidate": supplement_text == candidate_supp,
        "manuscript_only_two_replacements": sum(
            1 for left, right in zip(manuscript_base.read_text(encoding="utf-8").splitlines(), manuscript_text.splitlines()) if left != right
        ) == 2,
        "supplement_only_s3_s5_legend_replacements": sum(
            1 for left, right in zip(supplement_base.read_text(encoding="utf-8").splitlines(), supplement_text.splitlines()) if left != right
        ) == 3,
    }
    return manuscript, supplement, checks


def verify_exact_duplicates() -> dict[str, object]:
    source_dir = RUN / "figures/source_data"
    figure1 = pd.read_csv(source_dir / "Figure1_source_data.csv")
    s3 = pd.read_csv(source_dir / "Supplementary_Figure_S3_source_data.csv")
    figure3 = pd.read_csv(source_dir / "Figure3_source_data.csv")
    s5 = pd.read_csv(source_dir / "Supplementary_Figure_S5_source_data.csv")
    policy_map = {
        "five_state": "5-state",
        "four_state_platelet_overlay_merged": "4-state",
        "three_state_identity_core": "3-state",
        "two_compartment_asc_vs_conventional": "2-compartment",
    }
    s3a_cells: list[bool] = []
    for row in s3.loc[s3["panel"].eq("a")].itertuples():
        category = policy_map[row.policy]
        median = figure1.loc[
            figure1["panel"].eq("b")
            & figure1["series"].eq("median mapped ARI")
            & figure1["category"].eq(category)
        ].iloc[0]
        minimum = figure1.loc[
            figure1["panel"].eq("b")
            & figure1["series"].eq("minimum mapped ARI")
            & figure1["category"].eq(category)
        ].iloc[0]
        s3a_cells.extend(
            [
                row.median_mapped_ari == median.estimate,
                row.minimum_mapped_ari == minimum.estimate,
                row.median_mapping_agreement == median.secondary_value,
                row.minimum_mapping_agreement == minimum.secondary_value,
            ]
        )

    s3d_cells: list[bool] = []
    state_map = {0: "B_CONV", 3: "B_ASC"}
    for row in s3.loc[s3["panel"].eq("d")].itertuples():
        category = state_map[int(row.reference_state)]
        median = figure1.loc[
            figure1["panel"].eq("d")
            & figure1["series"].eq("median Jaccard")
            & figure1["category"].eq(category)
        ].iloc[0]
        minimum = figure1.loc[
            figure1["panel"].eq("d")
            & figure1["series"].eq("minimum Jaccard")
            & figure1["category"].eq(category)
        ].iloc[0]
        s3d_cells.extend(
            [
                row.median_jaccard == median.estimate,
                row.minimum_jaccard == minimum.estimate,
                row.median_recall == median.secondary_value,
                row.minimum_recall == minimum.secondary_value,
            ]
        )

    columns = ["analysis_name", "effect", "ci_low", "ci_high", "q_value_primary4"]
    figure3b = figure3.loc[figure3["panel"].eq("b"), columns].sort_values("analysis_name").reset_index(drop=True)
    s5d = s5.loc[s5["panel"].eq("d"), columns].sort_values("analysis_name").reset_index(drop=True)
    return {
        "s3a_vs_figure1b_exact": all(s3a_cells) and len(s3a_cells) == 16,
        "s3a_compared_cells": len(s3a_cells),
        "s3d_vs_figure1d_exact": all(s3d_cells) and len(s3d_cells) == 8,
        "s3d_compared_cells": len(s3d_cells),
        "s5d_vs_figure3b_exact": figure3b.equals(s5d),
        "s5d_compared_rows": len(figure3b),
        "s5d_compared_columns": columns,
    }


def build_s3(source: Path, output_pdf: Path) -> dict[str, object]:
    frame = pd.read_csv(source)
    cluster = frame.loc[frame["panel"].eq("b")].copy()
    transitions = frame.loc[frame["panel"].eq("c")].copy()
    figure, axes = plt.subplots(1, 2, gridspec_kw={"wspace": 0.34})

    axis = axes[0]
    labels = {
        "five_state": "5-state",
        "four_state_platelet_overlay_merged": "4-state",
        "three_state_identity_core": "3-state",
    }
    y_value = 0.0
    ticks: list[float] = []
    tick_labels: list[str] = []
    for policy in ("five_state", "four_state_platelet_overlay_merged", "three_state_identity_core"):
        subset = cluster.loc[cluster["policy"].eq(policy)].sort_values("reference_state")
        for row in subset.itertuples():
            axis.plot([row.minimum_jaccard, row.median_jaccard], [y_value, y_value], color=COLORS["light"], lw=1.0)
            axis.scatter(row.median_jaccard, y_value, s=13, marker="o", color=COLORS["teal"], zorder=3)
            axis.scatter(row.minimum_jaccard, y_value, s=13, marker="x", color=COLORS["red"], linewidths=0.8, zorder=3)
            ticks.append(y_value)
            tick_labels.append(f"{labels[policy]} C{int(row.reference_state)}")
            y_value += 1
        y_value += 0.55
    axis.axvline(0.60, ls="--", lw=0.6, color=COLORS["grey"])
    axis.set_xlim(-0.03, 1.02)
    axis.set_xlabel("Cluster Jaccard")
    axis.set_yticks(ticks, tick_labels)
    axis.invert_yaxis()
    axis.set_title("Failure localizes to fine-state membership", loc="left")
    axis.plot([], [], "o", color=COLORS["teal"], ms=3.2, label="Median")
    axis.plot([], [], "x", color=COLORS["red"], ms=3.2, label="Minimum")
    axis.legend(
        frameon=False,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.19),
        borderaxespad=0,
    )
    style_axis(axis)
    panel_label(axis, "a")

    axis = axes[1]
    clusters = sorted(
        set(transitions["reference_cluster"].dropna().astype(int))
        | set(transitions["mapped_reference_cluster"].dropna().astype(int))
    )
    matrix = np.zeros((max(clusters) + 1, max(clusters) + 1), dtype=float)
    for row in transitions.itertuples():
        matrix[int(row.reference_cluster), int(row.mapped_reference_cluster)] = float(row.fraction_of_reference_cluster)
    image = axis.imshow(matrix, cmap="Blues", vmin=0, vmax=1, aspect="equal")
    axis.set_xlabel("Mapped reference cluster")
    axis.set_ylabel("Original reference cluster")
    axis.set_xticks(range(matrix.shape[1]))
    axis.set_yticks(range(matrix.shape[0]))
    axis.set_title("Mean r=0.4 transition matrix", loc="left")
    colorbar = figure.colorbar(image, ax=axis, fraction=0.046, pad=0.03)
    colorbar.set_label("Mean fraction", fontsize=6)
    colorbar.ax.tick_params(labelsize=6, width=0.5, length=2.5)
    panel_label(axis, "b")
    figure.subplots_adjust(left=0.13, right=0.94, bottom=0.21, top=0.90)
    return save_exact(figure, output_pdf, 170, 86)


def build_s5(source: Path, output_pdf: Path) -> dict[str, object]:
    frame = pd.read_csv(source)
    models = frame.loc[frame["source_table"].eq("model_summary")].copy()
    ranked = frame.loc[frame["panel"].eq("c")].copy().sort_values("rank_cutoff")
    order = [
        "primary_base",
        "primary_min20",
        "primary_min100",
        "primary_residual_risk_negative",
        "validation_full",
        "validation_nonoverlap",
        "flare_full",
    ]
    label_map = {
        "primary_base": "Primary",
        "primary_min20": ">=20",
        "primary_min100": ">=100",
        "primary_residual_risk_negative": "Risk-negative",
        "validation_full": "Internal",
        "validation_nonoverlap": "Nonoverlap",
        "flare_full": "Flare",
    }
    models["analysis_name"] = pd.Categorical(models["analysis_name"], categories=order, ordered=True)
    models = models.sort_values("analysis_name")
    labels = [label_map[str(value)] for value in models["analysis_name"].astype(object)]
    x = np.arange(len(models))

    figure = plt.figure()
    grid = figure.add_gridspec(2, 2, height_ratios=[1, 1.05], hspace=0.54, wspace=0.33)
    axis_a = figure.add_subplot(grid[0, 0])
    axis_b = figure.add_subplot(grid[0, 1])
    axis_c = figure.add_subplot(grid[1, :])

    axis_a.bar(x, models["tested_genes"], color=COLORS["light"], width=0.72, label="Tested")
    axis_a.bar(x, models["fdr_0_05_genes"], color=COLORS["red"], width=0.72, label="BH q<0.05")
    axis_a.set_ylabel("Genes")
    axis_a.set_xticks(x, labels, rotation=35, ha="right")
    axis_a.set_title("filterByExpr-tested and significant genes", loc="left")
    axis_a.legend(frameon=False, ncol=2, loc="upper left")
    style_axis(axis_a)
    panel_label(axis_a, "a")

    axis_b.plot(x, models["common_dispersion"], marker="o", markersize=2.8, color=COLORS["blue"], label="Common")
    axis_b.plot(x, models["median_tagwise_dispersion"], marker="s", markersize=2.8, color=COLORS["gold"], label="Median tagwise")
    axis_b.set_ylabel("Dispersion")
    axis_b.set_xticks(x, labels, rotation=35, ha="right")
    axis_b.set_title("edgeR dispersion diagnostics", loc="left")
    axis_b.legend(frameon=False, ncol=2, loc="upper left")
    style_axis(axis_b)
    panel_label(axis_b, "b")

    metric_style = [
        ("mitochondrial_fraction", COLORS["red"], "o", "Mitochondrial"),
        ("ribosomal_fraction", COLORS["blue"], "s", "Ribosomal"),
        ("hemoglobin_fraction", COLORS["gold"], "^", "Haemoglobin"),
        ("immunoglobulin_fraction", COLORS["teal"], "D", "Immunoglobulin"),
    ]
    for metric, color, marker, label in metric_style:
        axis_c.plot(
            ranked["rank_cutoff"],
            100 * ranked[metric],
            marker=marker,
            markersize=2.8,
            color=color,
            label=label,
        )
    axis_c.set_xlabel("Top-ranked genes")
    axis_c.set_ylabel("Technical-family fraction (%)")
    axis_c.set_title("Ranked-list technical-family audit", loc="left")
    axis_c.legend(frameon=False, ncol=4, loc="upper left")
    style_axis(axis_c)
    panel_label(axis_c, "c", x=-0.055)
    figure.subplots_adjust(left=0.09, right=0.98, bottom=0.13, top=0.93)
    return save_exact(figure, output_pdf, 170, 104)


def write_panel_mapping() -> Path:
    output = RUN / "S3_S5_DISPLAY_PANEL_MAPPING.csv"
    rows = [
        ["S3a", "", "display-pruned; exact duplicate; evidence owner Figure 1b"],
        ["S3b", "S3a", "retained and renumbered"],
        ["S3c", "S3b", "retained and renumbered"],
        ["S3d", "", "display-pruned; exact duplicate; evidence owner Figure 1d"],
        ["S5a", "S5a", "retained"],
        ["S5b", "S5b", "retained"],
        ["S5c", "S5c", "retained"],
        ["S5d", "", "display-pruned; exact duplicate; evidence owner Figure 3b"],
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["frozen_source_panel", "final_display_panel", "action"])
        writer.writerows(rows)
    return output


def validate_decision_matrix() -> dict[str, object]:
    input_path = RECEIVED / "FINAL_INTEGRATED_READER_PANEL_DECISION_MATRIX.csv"
    output = RUN / input_path.name
    shutil.copy2(input_path, output)
    rows = list(csv.DictReader(input_path.open(encoding="utf-8-sig", newline="")))
    main = [row for row in rows if row["tier"] == "Main"]
    pruned = [row["object"] for row in rows if row["decision"] == "PRUNE_FROM_DISPLAY__EXACT_DUPLICATE"]
    return {
        "path": output.relative_to(ROOT).as_posix(),
        "rows": len(rows),
        "main_21_keep": len(main) == 21 and all(row["decision"] == "KEEP" for row in main),
        "exactly_three_pruned_panels": pruned
        == ["Supplementary Figure S3a", "Supplementary Figure S3d", "Supplementary Figure S5d"],
    }


def write_manifest() -> Path:
    output = RUN / "SOURCE_REDRAW_FILE_MANIFEST.csv"
    rows = []
    for path in sorted(candidate for candidate in RUN.rglob("*") if candidate.is_file() and candidate != output):
        rows.append([path.relative_to(ROOT).as_posix(), path.stat().st_size, sha256(path)])
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["relative_path", "bytes", "sha256"])
        writer.writerows(rows)
    return output


def main() -> None:
    arial = require_arial()
    configure_style()
    safe_reset(RUN)
    copy_frozen_objects()
    manuscript, supplement, source_checks = integrate_sources()
    duplicate_checks = verify_exact_duplicates()
    if not all(
        duplicate_checks[name]
        for name in ("s3a_vs_figure1b_exact", "s3d_vs_figure1d_exact", "s5d_vs_figure3b_exact")
    ):
        raise RuntimeError(f"Display-prune duplicate assertions failed: {duplicate_checks}")

    figure_dir = RUN / "figures/figures"
    source_dir = RUN / "figures/source_data"
    s3 = build_s3(
        source_dir / "Supplementary_Figure_S3_source_data.csv",
        figure_dir / "Supplementary_Figure_S3_fine_state_failure_transition_structure.pdf",
    )
    s5 = build_s5(
        source_dir / "Supplementary_Figure_S5_source_data.csv",
        figure_dir / "Supplementary_Figure_S5_pseudobulk_ranked_list_diagnostics.pdf",
    )
    mapping = write_panel_mapping()
    decision_matrix = validate_decision_matrix()
    source_hash_checks = {
        name: sha256(source_dir / name) == expected
        for name, expected in SOURCE_HASHES.items()
    }
    checks = {
        **source_checks,
        **{name: bool(value) for name, value in duplicate_checks.items() if name.endswith("_exact")},
        "all_four_frozen_source_hashes_unchanged": all(source_hash_checks.values()),
        "s3_width_170mm": abs(float(s3["width_mm"]) - 170.0) <= 0.15,
        "s5_width_170mm": abs(float(s5["width_mm"]) - 170.0) <= 0.15,
        "s3_two_display_panels": s3["minimum_visible_text_pt"] >= 6.0,
        "s5_three_display_panels": s5["minimum_visible_text_pt"] >= 6.0,
        "decision_matrix_valid": decision_matrix["rows"] == 62
        and decision_matrix["main_21_keep"]
        and decision_matrix["exactly_three_pruned_panels"],
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Integrated-reader source redraw failed: {failed}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_S3_S5_SOURCE_REDRAW_AND_TEXT_INTEGRATION_DOCUMENT_REBUILD_REQUIRED",
        "checks": checks,
        "duplicate_verification": duplicate_checks,
        "source_hash_checks": source_hash_checks,
        "arial_path": arial,
        "figures": {"S3": s3, "S5": s5},
        "sources": {
            manuscript.name: {"bytes": manuscript.stat().st_size, "sha256": sha256(manuscript)},
            supplement.name: {"bytes": supplement.stat().st_size, "sha256": sha256(supplement)},
        },
        "panel_mapping": mapping.relative_to(ROOT).as_posix(),
        "panel_decision_matrix": decision_matrix,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_changed": False,
        "display_panels_pruned": ["S3a", "S3d", "S5d"],
        "main_panels": {"keep": 21, "modify": 0, "replace": 0},
        "supplementary_panels": {"keep_or_renumber": 38, "prune_exact_duplicate": 3, "replace": 0},
        "submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "00_SOURCE_REDRAW_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_manifest()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
