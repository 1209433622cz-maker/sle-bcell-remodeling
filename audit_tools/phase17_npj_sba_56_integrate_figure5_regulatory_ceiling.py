#!/usr/bin/env python3
"""Integrate the Figure 5 regulatory ceiling from locked source data."""

from __future__ import annotations

import csv
import difflib
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
os.environ.setdefault("NPJ_SBA_STYLE", "1")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "phase17_v7/npj_sba_figure4_transfer_boundary/20260907_source_rerender_gate"
RUN = ROOT / "phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration"
RECEIVED = ROOT / "00_project_management/figure5_regulatory_ceiling_2026-09-08/received"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
SOURCE_HASHES = {
    "Figure5_source_data.csv": "A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B",
    "Supplementary_Figure_S9_source_data.csv": "D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3",
    "Supplementary_Figure_S10_source_data.csv": "26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2",
}
EXTERNAL_INPUTS = {
    "SOURCE_HASH_PROVENANCE.txt": Path(r"C:\Users\Administrator\Downloads\SOURCE_HASH_PROVENANCE (2).txt"),
    "Figure5d_regulatory_ceiling_candidate_source_values.csv": Path(r"C:\Users\Administrator\Downloads\Figure5d_regulatory_ceiling_candidate_source_values.csv"),
    "FIGURE5_REGULATORY_CEILING_GATE_DECISION.csv": Path(r"C:\Users\Administrator\Downloads\FIGURE5_REGULATORY_CEILING_GATE_DECISION.csv"),
    "action_record_2026-09-07_figure5_regulatory_ceiling_source_rerender_gate.md": Path(r"C:\Users\Administrator\Downloads\action_record_2026-09-07_figure5_regulatory_ceiling_source_rerender_gate.md"),
    "Figure5_full_170mm_regulatory_ceiling_candidate_v2.pdf": Path(r"C:\Users\Administrator\Downloads\Figure5_full_170mm_regulatory_ceiling_candidate_v2.pdf"),
    "Figure5d_halfwidth_8pt_readability_gate.pdf": Path(r"C:\Users\Administrator\Downloads\Figure5d_halfwidth_8pt_readability_gate.pdf"),
    "Figure5d_halfwidth_8pt_readability_gate.png": Path(r"C:\Users\Administrator\Downloads\Figure5d_halfwidth_8pt_readability_gate.png"),
    "Figure5_full_170mm_regulatory_ceiling_candidate_v2.png": Path(r"C:\Users\Administrator\Downloads\Figure5_full_170mm_regulatory_ceiling_candidate_v2.png"),
    "pasted_figure5_regulatory_ceiling_review_2026-09-07.txt": Path(r"C:\Users\Administrator\.codex\attachments\7c3b096d-5731-48fa-8d04-7c9b5a9639df\pasted-text.txt"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_size_mm(path: Path) -> tuple[float, float]:
    page = PdfReader(path).pages[0]
    return float(page.mediabox.width) * 25.4 / 72.0, float(page.mediabox.height) * 25.4 / 72.0


def require_within_workspace(path: Path) -> None:
    if ROOT.resolve() not in path.resolve().parents:
        raise RuntimeError(f"Refusing to modify path outside workspace: {path}")


def archive_inputs() -> list[dict[str, object]]:
    RECEIVED.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for name, source in EXTERNAL_INPUTS.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        target = RECEIVED / name
        shutil.copy2(source, target)
        if source.read_bytes() != target.read_bytes():
            raise RuntimeError(f"External input was not archived byte-identically: {name}")
        rows.append({"file": name, "bytes": target.stat().st_size, "sha256": sha256(target)})
    return rows


def lock_sources() -> dict[str, str]:
    source_dir = PARENT / "figures/source_data"
    observed: dict[str, str] = {}
    for name, expected in SOURCE_HASHES.items():
        digest = sha256(source_dir / name)
        if digest != expected:
            raise RuntimeError(f"Frozen source hash changed for {name}: {digest}")
        observed[name] = digest
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Submission package no longer matches the author-confirmed SHA-256")
    return observed


def load_depletion_rows() -> pd.DataFrame:
    source = pd.read_csv(PARENT / "figures/source_data/Supplementary_Figure_S10_source_data.csv")
    rows = source.loc[
        source["method"].eq("ULM")
        & source["regulator"].isin(["STAT1", "STAT2"])
        & source["contrast"].isin([
            "gse174188_primary",
            "gse174188_internal_nonoverlap",
            "gse135779_childhood",
        ])
    ].copy()
    if len(rows) != 12:
        raise RuntimeError(f"Expected 12 frozen ULM depletion rows, found {len(rows)}")

    candidate = pd.read_csv(EXTERNAL_INPUTS["Figure5d_regulatory_ceiling_candidate_source_values.csv"])
    if len(candidate) != 12:
        raise RuntimeError(f"Expected 12 external candidate rows, found {len(candidate)}")
    keys = ["contrast", "regulator", "branch"]
    fields = ["estimate", "ci_low", "ci_high", "q_value", "matched_targets_after", "attenuation_ratio_vs_baseline"]
    joined = rows.merge(candidate, on=keys, suffixes=("_source", "_candidate"), validate="one_to_one")
    for field in fields:
        delta = np.abs(joined[f"{field}_source"].astype(float) - joined[f"{field}_candidate"].astype(float))
        if float(delta.max()) > 1e-12:
            raise RuntimeError(f"External candidate differs from frozen S10 for {field}: {float(delta.max())}")

    branch_a = rows.loc[rows["branch"].eq("frozen_ifn12_depleted")]
    branch_b = rows.loc[rows["branch"].eq("m5911_depleted")]
    if len(branch_a) != 6 or len(branch_b) != 6:
        raise RuntimeError("Depletion branch coverage changed")
    if not ((branch_a["ci_low"] > 0).all() and int((branch_b["ci_low"] > 0).sum()) == 5):
        raise RuntimeError("Expected six positive branch-A intervals and five positive branch-B intervals")
    exception = branch_b.loc[branch_b["ci_low"] <= 0]
    if len(exception) != 1 or exception.iloc[0]["contrast"] != "gse174188_primary" or exception.iloc[0]["regulator"] != "STAT2":
        raise RuntimeError("Discovery STAT2 is no longer the sole M5911-depletion CI-cross-zero exception")
    return rows


def build_figure5(depletion: pd.DataFrame) -> tuple[Path, Path, Path]:
    frozen_path = PARENT / "figures/source_data/Figure5_source_data.csv"
    frozen = pd.read_csv(frozen_path)
    regulators = frozen.loc[frozen["panel"].isin(["B", "C"])].copy()
    regulators[["contrast", "regulator"]] = regulators["category"].str.split("|", expand=True)
    regulators["family"] = np.where(regulators["panel"].eq("B"), "IFN_confirmatory", "proliferation_control")
    regulators = regulators.rename(columns={"estimate": "slope", "q_value": "q_value_global24", "n_or_targets": "matched_targets"})
    gsea = frozen.loc[frozen["series"].eq("MSigDB_M5911_NES")].copy()
    donor = frozen.loc[frozen["series"].eq("GSE23307_mean_paired_log2p1_effect")].copy()
    genes = frozen.loc[frozen["series"].eq("GSE23307_paired_gene_log2p1_effect")].copy()
    genes[["donor_id", "gene_symbol"]] = genes["category"].str.split("|", expand=True)
    genes = genes.rename(columns={"estimate": "paired_log2p1_effect"})

    if len(regulators) != 24 or len(gsea) != 3 or len(donor) != 2 or len(genes) != 24:
        raise RuntimeError("Frozen Figure 5 panel-source counts changed")
    if not (gsea["estimate"].astype(float) > 3).all():
        raise RuntimeError("Frozen M5911 evidence summary changed")

    figure_dir = RUN / "figures/figures"
    source_dir = RUN / "figures/source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)

    preserved = frozen.copy()
    preserved.loc[preserved["series"].eq("MSigDB_M5911_NES"), "panel"] = "A"
    preserved["evidence_owner"] = preserved["panel"].map({
        "A": "Figure 5a evidence summary; Supplementary Table S3 quantitative detail",
        "B": "Figure 5b",
        "C": "Figure 5c",
        "E": "Figure 5e",
    })
    depletion_source = pd.DataFrame({
        "panel": "D",
        "series": "ULM_IFN_overlap_depletion",
        "category": depletion["contrast"].astype(str) + "|" + depletion["regulator"].astype(str) + "|" + depletion["branch"].astype(str),
        "estimate": depletion["estimate"],
        "ci_low": depletion["ci_low"],
        "ci_high": depletion["ci_high"],
        "p_value": depletion["p_value"],
        "q_value": depletion["q_value"],
        "n_or_targets": depletion["matched_targets_after"],
        "branch": depletion["branch"],
        "contrast": depletion["contrast"],
        "regulator": depletion["regulator"],
        "matched_targets_before": depletion["matched_targets_before"],
        "removed_targets": depletion["removed_targets"],
        "matched_targets_after": depletion["matched_targets_after"],
        "target_retention_fraction": depletion["target_retention_fraction"],
        "baseline_ulm_slope": depletion["baseline_ulm_slope"],
        "attenuation_ratio_vs_baseline": depletion["attenuation_ratio_vs_baseline"],
        "ci_excludes_zero": depletion["ci_excludes_zero"],
        "evidence_owner": "Figure 5d ULM summary; Supplementary Fig. S10 and Table S4b full audit",
    })
    source = pd.concat([preserved, depletion_source], ignore_index=True, sort=False)
    source_path = source_dir / "Figure5_source_data.csv"
    source.to_csv(source_path, index=False, lineterminator="\n")

    base.ASSERTIONS.clear()
    base.configure_style()
    base.set_output_width_mm(170.0)
    figure = plt.figure(figsize=(7.09, 8.8), constrained_layout=True)
    grid = figure.add_gridspec(3, 2, height_ratios=[0.82, 2.05, 1.17], width_ratios=[1.08, 0.92])
    design_axis = figure.add_subplot(grid[0, :])
    ifn_axis = figure.add_subplot(grid[1, 0])
    control_axis = figure.add_subplot(grid[1, 1])
    depletion_axis = figure.add_subplot(grid[2, 0])
    donor_axis = figure.add_subplot(grid[2, 1])

    design_axis.set_axis_off()
    base.panel_label(design_axis, "a", x=-0.09, y=1.08)
    design_axis.set_title("Evidence classes and interpretive roles", loc="left", pad=4, fontsize=8.2)
    x_positions = (0.02, 0.27, 0.55, 0.78)
    for x_value, header in zip(x_positions, ("Evidence", "Coverage", "Observed result", "Interpretive role"), strict=True):
        design_axis.text(x_value, 0.89, header, transform=design_axis.transAxes, fontweight="bold", va="center", fontsize=7.4)
    matrix_rows = (
        (0.67, "ULM STAT1/STAT2", "3 contrasts", "6/6 positive;\n24-test q<0.05", "confirmatory\nobservational", base.COLORS["internal"]),
        (0.43, "M5911", "3 contrasts", "3/3 NES >3.0", "response-set\nconcordance", base.COLORS["external"]),
        (0.19, "IFN-beta", "2 donors", "12/12 positive\nin each donor", "descriptive\ncontext", base.COLORS["purple"]),
    )
    for y_value, evidence, coverage, result, role, color in matrix_rows:
        design_axis.plot([0.01, 0.98], [y_value + 0.105, y_value + 0.105], transform=design_axis.transAxes, color="#DDDDDD", lw=0.55)
        design_axis.plot([0.015, 0.015], [y_value - 0.075, y_value + 0.075], transform=design_axis.transAxes, color=color, lw=1.3)
        design_axis.text(x_positions[0] + 0.025, y_value, evidence, transform=design_axis.transAxes, va="center", fontweight="bold", fontsize=7.2)
        design_axis.text(x_positions[1], y_value, coverage, transform=design_axis.transAxes, va="center", fontsize=7.1)
        design_axis.text(x_positions[2], y_value, result, transform=design_axis.transAxes, va="center", fontsize=7.1)
        design_axis.text(x_positions[3], y_value, role, transform=design_axis.transAxes, va="center", fontsize=7.1)
    design_axis.text(0.98, 0.015, "Boundary: observational convergence; no causal regulator, direct binding or unique upstream stimulus", transform=design_axis.transAxes, ha="right", va="bottom", color="#444444", fontweight="bold", fontsize=7.1)

    contrast_short = {
        "gse174188_primary": "Discovery",
        "gse174188_internal_nonoverlap": "Nonoverlap",
        "gse135779_childhood": "Childhood",
    }
    regulator_colors = {"STAT1": "#2C6EAD", "STAT2": "#009E73", "IRF7": "#7B6BA8", "IRF9": "#D55E00", "E2F1": "#666666", "FOXM1": "#999999", "MYC": "#333333", "MYBL2": "#BBBBBB"}

    def regulator_forest(axis: plt.Axes, names: list[str], label: str, title: str) -> None:
        selected = regulators.loc[regulators["regulator"].isin(names)].copy()
        selected["contrast_order"] = selected["contrast"].map({key: index for index, key in enumerate(contrast_short)})
        selected["regulator_order"] = selected["regulator"].map({name: index for index, name in enumerate(names)})
        selected = selected.sort_values(["contrast_order", "regulator_order"])
        role = {"STAT1": "core", "STAT2": "core", "IRF7": "extended", "IRF9": "extended"}
        selected["label"] = [f"{contrast_short[c]}  {r}{f' ({role[r]})' if r in role else ''}" for c, r in zip(selected["contrast"], selected["regulator"], strict=True)]
        selected["color"] = selected["regulator"].map(regulator_colors)
        base.forest(axis, selected, "label", "slope", "ci_low", "ci_high", "color")
        for separator in (3.5, 7.5):
            axis.axhline(separator, color="#DDDDDD", lw=0.55, zorder=0)
        if names == ["STAT1", "STAT2", "IRF7", "IRF9"]:
            for separator in (1.5, 5.5, 9.5):
                axis.axhline(separator, color="#E8E8E8", lw=0.45, ls=":", zorder=0)
        for y_value, (_, row) in zip(np.arange(len(selected))[::-1], selected.iterrows(), strict=True):
            if float(row["q_value_global24"]) < 0.05:
                axis.text(float(row["ci_high"]) + 0.06, y_value, "*", fontsize=6.5, va="center")
        axis.set_xlabel("Regulator activity slope (95% CI)")
        axis.set_title(title, loc="left", pad=4)
        base.panel_label(axis, label)

    regulator_forest(ifn_axis, ["STAT1", "STAT2", "IRF7", "IRF9"], "b", "Core and extended IFN regulators")
    regulator_forest(control_axis, ["E2F1", "FOXM1", "MYC", "MYBL2"], "c", "Prespecified proliferation\nspecificity comparators")

    order = [(contrast, regulator) for contrast in contrast_short for regulator in ("STAT1", "STAT2")]
    y_by_key = {key: len(order) - 1 - index for index, key in enumerate(order)}
    branches = (
        ("frozen_ifn12_depleted", 0.11, "o", base.COLORS["internal"], "12-gene arm removed"),
        ("m5911_depleted", -0.11, "s", base.COLORS["secondary"], "M5911 removed"),
    )
    for branch, offset, marker, color, label in branches:
        selected = depletion.loc[depletion["branch"].eq(branch)]
        for index, (_, row) in enumerate(selected.iterrows()):
            y_value = y_by_key[(row["contrast"], row["regulator"])] + offset
            depletion_axis.errorbar(float(row["estimate"]), y_value, xerr=[[float(row["estimate"] - row["ci_low"])], [float(row["ci_high"] - row["estimate"])]] , fmt=marker, color=color, ms=3.5, lw=0.9, capsize=1.8, label=label if index == 0 else None, zorder=3)
    depletion_axis.axvline(0, color="#777777", lw=0.7, ls="--", zorder=0)
    labels = [f"{contrast_short[c]} {r}" for c, r in order]
    depletion_axis.set_yticks([y_by_key[key] for key in order], labels)
    depletion_axis.set_xlim(-0.9, 3.55)
    depletion_axis.set_xlabel("ULM slope after depletion (95% CI)")
    depletion_axis.set_title("IFN-overlap depletion", loc="left", pad=4)
    depletion_axis.legend(loc="upper right", bbox_to_anchor=(1.0, 1.17), ncol=2, frameon=False, fontsize=5.5, handlelength=1.3, columnspacing=0.9)
    exception = depletion.loc[(depletion["branch"].eq("m5911_depleted")) & depletion["contrast"].eq("gse174188_primary") & depletion["regulator"].eq("STAT2")].iloc[0]
    depletion_axis.annotate("Discovery STAT2\n95% CI crosses 0", xy=(float(exception["estimate"]), y_by_key[("gse174188_primary", "STAT2")] - 0.11), xytext=(1.55, 3.55), textcoords="data", fontsize=5.5, ha="left", va="center", arrowprops={"arrowstyle": "->", "lw": 0.65, "color": "#222222"})
    base.style_axis(depletion_axis)
    base.panel_label(depletion_axis, "d", x=-0.08, y=1.08)

    gene_order = genes.loc[genes["donor_id"].eq("HI1"), "gene_symbol"].tolist()
    pivot = genes.pivot(index="gene_symbol", columns="donor_id", values="paired_log2p1_effect").loc[gene_order]
    y_values = np.arange(len(gene_order))[::-1]
    for y_value, (_, row) in zip(y_values, pivot.iterrows(), strict=True):
        donor_axis.plot([row["HI1"], row["HI2"]], [y_value, y_value], color="#C7CCD1", lw=0.7, zorder=1)
    donor_axis.scatter(pivot["HI1"], y_values + 0.09, s=13, color="#CC6666", linewidths=0, label="HI1", zorder=3)
    donor_axis.scatter(pivot["HI2"], y_values - 0.09, s=13, color=base.COLORS["purple"], linewidths=0, label="HI2", zorder=3)
    donor_axis.axvline(0, color="#777777", lw=0.7, ls="--")
    donor_axis.set_yticks(y_values, gene_order)
    donor_axis.set_xlim(0, 6.2)
    donor_axis.set_xlabel("IFN-beta minus control (log2[x+1])")
    donor_axis.set_title("IFN-beta paired gene effects", loc="left", pad=4)
    donor_axis.legend(frameon=False, fontsize=6, loc="upper left")
    donor_axis.text(0.98, 0.03, "n=2; descriptive", transform=donor_axis.transAxes, ha="right", va="bottom", color="#555555")
    base.style_axis(donor_axis)
    base.panel_label(donor_axis, "e", x=-0.08, y=1.08)
    control_axis.text(0.98, -0.19, "* global 24-test BH q<0.05", transform=control_axis.transAxes, ha="right", va="top", fontsize=5.8, color="#444444")

    base.save_figure(figure, figure_dir, "Figure5_regulatory_evidence")
    return figure_dir / "Figure5_regulatory_evidence.pdf", figure_dir / "Figure5_regulatory_evidence.png", source_path


def comparison_sheet(output: Path) -> None:
    paths = [
        PARENT / "figures/figures/Figure5_regulatory_evidence.png",
        RUN / "figures/figures/Figure5_regulatory_evidence.png",
    ]
    images = [Image.open(path).convert("RGB") for path in paths]
    target_height = min(image.height for image in images)
    images = [image.resize((round(image.width * target_height / image.height), target_height)) for image in images]
    width = sum(image.width for image in images)
    header = 72
    canvas = Image.new("RGB", (width, target_height + header), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    labels = ("Prior frozen Figure 5", "Regulatory-ceiling candidate")
    x = 0
    for image, label in zip(images, labels, strict=True):
        draw.text((x + 30, 18), label, fill="black", font=font)
        canvas.paste(image, (x, header))
        x += image.width
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def patch_manuscript() -> tuple[str, str, list[dict[str, str]]]:
    before = (PARENT / "sources/Manuscript_figure4_transfer_boundary.md").read_text(encoding="utf-8")
    old_context = "Two additional analyses provided response-level context rather than causal proof. The MSigDB Hallmark interferon-alpha response set M5911 was positively enriched in all three ranked contrasts (normalized enrichment scores 3.187, 3.050 and 3.527; 10,000 gene-label permutations per contrast). In GSE23307 primary B cells exposed ex vivo to IFN-beta, all 12 genes in the frozen positive arm increased in each of two healthy donors, with mean paired log2(x+1) effects of 3.294 and 3.666. No inferential P value was calculated at n=2 (Fig. 5d,e)."
    new_context = "Two additional analyses provided response-level context rather than causal proof. The MSigDB Hallmark interferon-alpha response set M5911 was positively enriched in all three ranked contrasts (normalized enrichment scores 3.187, 3.050 and 3.527; 10,000 gene-label permutations per contrast; Fig. 5a and Supplementary Table S3). In GSE23307 primary B cells exposed ex vivo to IFN-beta, all 12 genes in the frozen positive arm increased in each of two healthy donors, with mean paired log2(x+1) effects of 3.294 and 3.666. No inferential P value was calculated at n=2 (Fig. 5e)."
    old_legend = "a, Evidence classes and interpretive roles for the replicated IFN/ISG program. ULM STAT1/STAT2 provides confirmatory observational evidence across three contrasts, M5911 provides response-set concordance and GSE23307 provides descriptive IFN-beta perturbational context. These layers show observational convergence but do not establish a causal regulator, direct binding or a unique upstream stimulus. b, Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. c, Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation comparators; asterisks denote global 24-test q<0.05. d, M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. e, Paired log2(x+1) effects for the 12-gene IFN positive arm in two IFN-beta-exposed healthy donors; same-gene points are connected for display only, all 24 effects were positive and no inferential P value was calculated at n=2."
    new_legend = "a, Evidence classes and interpretive roles. ULM STAT1/STAT2 is confirmatory observational evidence across three contrasts; M5911 and GSE23307 provide response-set and descriptive perturbational context, respectively. None establishes causality, direct binding or a unique upstream stimulus. b, Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI slopes across discovery, donor-nonoverlap and childhood contrasts. c, Prespecified proliferation comparators; asterisks, global 24-test q<0.05. d, Post-freeze ULM sensitivity after removal of the 12-gene IFN/ISG arm or 97-gene M5911 set (95% CIs). Discovery STAT2 crossed zero only after M5911 removal; full ULM/CAMERA/FRY results are in Supplementary Fig. S10 and Supplementary Table S4b. e, Paired log2(x+1) effects for the 12-gene IFN arm in two IFN-beta-exposed donors; lines link identical genes, all effects were positive and no P value was calculated (n=2)."
    replacements = [
        (
            "F5-XREF-1",
            "Promote overlap-depletion ceiling to Figure 5d",
            "(Supplementary Fig. S10; Supplementary Table S4b).",
            "(Fig. 5d; Supplementary Fig. S10; Supplementary Table S4b).",
        ),
        (
            "F5-XREF-2",
            "Reassign M5911 summary to panel 5a and GSE23307 display to panel 5e",
            old_context,
            new_context,
        ),
        (
            "F5-LEGEND",
            "Synchronize Figure 5d and restore full-legend page economy",
            old_legend,
            new_legend,
        ),
    ]
    after = before
    ledger: list[dict[str, str]] = []
    for edit_id, purpose, old, new in replacements:
        if after.count(old) != 1:
            raise RuntimeError(f"Expected one manuscript anchor for {edit_id}, found {after.count(old)}")
        after = after.replace(old, new)
        ledger.append({"edit_id": edit_id, "purpose": purpose, "before": old, "after": new, "scientific_value_changed": "False"})
    return before, after, ledger


def write_panel_matrix() -> None:
    with (PARENT / "02_PANEL_DECISION_MATRIX.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row["object"] == "Figure 5d":
            row["scientific_decision"] = "SOURCE_REPLACEMENT"
            row["artwork_action"] = "S10_ULM_REGULATORY_CEILING_SUMMARY"
            row["rationale"] = "Main-text claim ceiling; old M5911 summary retained in Figure 5a provenance and Supplementary Table S3."
    with (RUN / "02_PANEL_DECISION_MATRIX.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source_hashes = lock_sources()
    external_manifest = archive_inputs()
    if RUN.exists():
        require_within_workspace(RUN)
        shutil.rmtree(RUN)
    shutil.copytree(PARENT / "figures", RUN / "figures")
    (RUN / "source_inputs").mkdir(parents=True)
    for name in SOURCE_HASHES:
        shutil.copy2(PARENT / "figures/source_data" / name, RUN / "source_inputs" / name)

    depletion = load_depletion_rows()
    figure_pdf, figure_png, source_data = build_figure5(depletion)
    comparison_sheet(RUN / "qa/Figure5_current_vs_regulatory_ceiling.png")
    before, after, ledger = patch_manuscript()
    sources = RUN / "sources"
    sources.mkdir(parents=True)
    before_path = sources / "Manuscript_before_figure5_regulatory_ceiling.md"
    manuscript_path = sources / "Manuscript_figure5_regulatory_ceiling.md"
    supplement_path = sources / "Supplementary_Information_unchanged.md"
    before_path.write_text(before, encoding="utf-8", newline="\n")
    manuscript_path.write_text(after, encoding="utf-8", newline="\n")
    shutil.copy2(PARENT / "sources/Supplementary_Information_unchanged.md", supplement_path)
    (ROOT / "01_manuscript/Manuscript.md").write_text(after, encoding="utf-8", newline="\n")

    with (RUN / "00_EXTERNAL_INPUT_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(external_manifest[0]))
        writer.writeheader()
        writer.writerows(external_manifest)
    depletion.to_csv(RUN / "01_FIGURE5_DEPLETION_DERIVATION.csv", index=False, lineterminator="\n")
    with (RUN / "03_TEXT_EDIT_LEDGER.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)
    diff = "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile="Manuscript_before_figure5_regulatory_ceiling.md", tofile="Manuscript_figure5_regulatory_ceiling.md"))
    (RUN / "04_MANUSCRIPT_FIGURE5_REGULATORY_CEILING.diff").write_text(diff, encoding="utf-8", newline="\n")
    write_panel_matrix()

    asset_changes: list[str] = []
    for directory in ("figures", "source_data"):
        for path in (RUN / "figures" / directory).glob("*"):
            if path.is_file() and sha256(path) != sha256(PARENT / "figures" / directory / path.name):
                asset_changes.append(path.name)
    width_mm, height_mm = pdf_size_mm(figure_pdf)
    figure_text = " ".join((PdfReader(figure_pdf).pages[0].extract_text() or "").split())
    output_source = pd.read_csv(source_data)
    old_figure5 = before.split("### Figure 5 |", 1)[1]
    new_figure5 = after.split("### Figure 5 |", 1)[1]
    checks = {
        "source_hashes_locked": source_hashes == SOURCE_HASHES,
        "external_candidate_values_reproduced": len(depletion) == 12,
        "six_ifn12_intervals_exclude_zero": int((depletion.loc[depletion["branch"].eq("frozen_ifn12_depleted"), "ci_low"] > 0).sum()) == 6,
        "discovery_stat2_is_only_m5911_ci_exception": int((depletion.loc[depletion["branch"].eq("m5911_depleted"), "ci_low"] <= 0).sum()) == 1,
        "figure5_is_single_page_170mm": len(PdfReader(figure_pdf).pages) == 1 and abs(width_mm - 170.0) < 0.05,
        "canonical_panel_labels_not_clipped_in_source_layout": all(token in figure_text for token in ("Discovery STAT1 (core)", "Childhood IRF9 (extended)", "Discovery E2F1")),
        "new_panel_d_semantics_present": all(token in figure_text for token in ("IFN-overlap depletion", "12-gene arm removed", "M5911 removed", "95% CI crosses 0")),
        "old_panel_d_title_removed": "M5911 enrichment" not in figure_text,
        "source_data_has_65_rows": len(output_source) == 65,
        "m5911_rows_reassigned_to_panel_a": len(output_source.loc[(output_source["panel"] == "A") & output_source["series"].eq("MSigDB_M5911_NES")]) == 3,
        "new_panel_d_has_12_ulm_rows": len(output_source.loc[(output_source["panel"] == "D") & output_source["series"].eq("ULM_IFN_overlap_depletion")]) == 12,
        "only_three_figure_assets_changed": sorted(asset_changes) == sorted(["Figure5_regulatory_evidence.pdf", "Figure5_regulatory_evidence.png", "Figure5_source_data.csv"]),
        "three_exact_text_operations": len(ledger) == 3,
        "overlap_depletion_claim_owner_promoted": "Fig. 5d; Supplementary Fig. S10; Supplementary Table S4b" in after,
        "m5911_and_gse23307_owners_separated": "Fig. 5a and Supplementary Table S3" in after and "n=2 (Fig. 5e)" in after,
        "figure5d_legend_synchronized": "Post-freeze ULM sensitivity after removal" in new_figure5,
        "supplementary_information_unchanged": sha256(ROOT / "01_manuscript/Supplementary_Information.md") == sha256(supplement_path),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FIGURE5_REGULATORY_CEILING_CANONICAL_INTEGRATION_DOCX_REQUIRED" if not failed else "HOLD_FIGURE5_REGULATORY_CEILING_REVIEW_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "source_sha256": source_hashes,
        "figure5": {
            "pdf": figure_pdf.relative_to(ROOT).as_posix(),
            "pdf_sha256": sha256(figure_pdf),
            "png": figure_png.relative_to(ROOT).as_posix(),
            "png_sha256": sha256(figure_png),
            "source_data": source_data.relative_to(ROOT).as_posix(),
            "source_data_sha256": sha256(source_data),
            "width_mm": round(width_mm, 2),
            "height_mm": round(height_mm, 2),
            "panel_d": "SOURCE_REPLACEMENT_FROM_LOCKED_S10_ULM",
        },
        "changed_assets": sorted(asset_changes),
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "multiplicity_families_changed": False,
        "supplementary_figures_s9_s10_changed": False,
        "submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "05_FIGURE5_REGULATORY_CEILING_INTEGRATION_STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Figure 5 integration checks failed: {failed}")


if __name__ == "__main__":
    main()
