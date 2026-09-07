#!/usr/bin/env python3
"""Promote the corrected external-transfer calibration boundary into Figure 4d."""

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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "phase17_v7/npj_sba_figure1_boundary_promotion/20260902_source_rerender_gate"
RUN = ROOT / "phase17_v7/npj_sba_figure4_transfer_boundary/20260907_source_rerender_gate"
RECEIVED = ROOT / "00_project_management/figure4_transfer_boundary_2026-09-07/received"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
SOURCE_HASHES = {
    "Figure4_source_data.csv": "F3604F40DAEDB0DD01617BB223A8762323C8AAC7F16185292367B9A13FEC4755",
    "Figure5_source_data.csv": "A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B",
    "Supplementary_Figure_S7_source_data.csv": "A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6",
    "Supplementary_Figure_S8_source_data.csv": "FF4309EBAF761A0563F018AE1BE07212EF2CB2241E79DF12C374BCB1426A60FF",
    "Supplementary_Figure_S9_source_data.csv": "D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3",
    "Supplementary_Figure_S10_source_data.csv": "26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2",
}
EXTERNAL_INPUTS = {
    "SOURCE_HASH_PROVENANCE.txt": Path(r"C:\Users\Administrator\Downloads\SOURCE_HASH_PROVENANCE (1).txt"),
    "FIGURE4_EXTERNAL_TRANSFER_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE.md": Path(r"C:\Users\Administrator\Downloads\FIGURE4_EXTERNAL_TRANSFER_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE.md"),
    "PROPOSED_TEXT_SYNC_LEDGER.csv": Path(r"C:\Users\Administrator\Downloads\PROPOSED_TEXT_SYNC_LEDGER.csv"),
    "FULL_MAIN_FIGURE_CLAIM_DENSITY_PANEL_MATRIX.csv": Path(r"C:\Users\Administrator\Downloads\FULL_MAIN_FIGURE_CLAIM_DENSITY_PANEL_MATRIX.csv"),
    "action_record_2026-09-02_full_main_figure_claim_density_hostile_read.md": Path(r"C:\Users\Administrator\Downloads\action_record_2026-09-02_full_main_figure_claim_density_hostile_read.md"),
    "Figure5d_candidate_depletion_values.csv": Path(r"C:\Users\Administrator\Downloads\Figure5d_candidate_depletion_values.csv"),
    "Figure5d_overlap_depletion_boundary_candidate_v2.pdf": Path(r"C:\Users\Administrator\Downloads\Figure5d_overlap_depletion_boundary_candidate_v2.pdf"),
    "Figure5d_overlap_depletion_boundary_candidate_v2.png": Path(r"C:\Users\Administrator\Downloads\Figure5d_overlap_depletion_boundary_candidate_v2.png"),
    "Figure4d_candidate_calibration_gate_values.csv": Path(r"C:\Users\Administrator\Downloads\Figure4d_candidate_calibration_gate_values.csv"),
    "Figure4d_transfer_calibration_boundary_candidate_v3.pdf": Path(r"C:\Users\Administrator\Downloads\Figure4d_transfer_calibration_boundary_candidate_v3.pdf"),
    "Figure4d_transfer_calibration_boundary_candidate_v3.png": Path(r"C:\Users\Administrator\Downloads\Figure4d_transfer_calibration_boundary_candidate_v3.png"),
    "pasted_full_main_figure_claim_density_review_2026-09-02.txt": Path(r"C:\Users\Administrator\.codex\attachments\46364e05-f5a3-4f75-bc83-aa286567da17\pasted-text.txt"),
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
        path = source_dir / name
        digest = sha256(path)
        if digest != expected:
            raise RuntimeError(f"Frozen source hash changed for {name}: {digest}")
        observed[name] = digest
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Submission package no longer matches the author-confirmed frozen SHA-256")
    return observed


def calibration_rows() -> pd.DataFrame:
    source = pd.read_csv(PARENT / "figures/source_data/Supplementary_Figure_S8_source_data.csv")
    row = source.loc[(source["panel"] == "b-c") & (source["mapper"] == "elastic_net")]
    if len(row) != 1:
        raise RuntimeError(f"Expected one corrected elastic-net calibration row, found {len(row)}")
    record = row.iloc[0]
    metrics = [
        ("Coverage", float(record["coverage"]), 0.80),
        ("B_CONV precision", float(record["B_CONV_precision"]), 0.90),
        ("B_ASC precision", float(record["B_ASC_precision"]), 0.90),
    ]
    rows = pd.DataFrame(metrics, columns=["metric", "observed", "criterion"])
    rows["margin"] = rows["observed"] - rows["criterion"]
    rows["status"] = np.where(rows["margin"] >= 0, "criterion met", "criterion not met")
    rows.insert(0, "panel", "d")
    rows["mapper"] = "required corrected elastic_net"
    rows["corrected_disease_effect_estimated"] = False

    external = pd.read_csv(EXTERNAL_INPUTS["Figure4d_candidate_calibration_gate_values.csv"])
    for _, candidate in external.iterrows():
        match = rows.loc[rows["metric"] == candidate["metric"]]
        if len(match) != 1:
            raise RuntimeError(f"External candidate metric not found in frozen source: {candidate['metric']}")
        for field in ("observed", "criterion", "margin"):
            if abs(float(match.iloc[0][field]) - float(candidate[field])) > 1e-12:
                raise RuntimeError(f"External candidate value mismatch: {candidate['metric']} {field}")
    return rows


def build_figure4(calibration: pd.DataFrame) -> tuple[Path, Path, Path]:
    source_path = PARENT / "figures/source_data/Figure4_source_data.csv"
    frozen = pd.read_csv(source_path)
    panel_a = frozen.loc[frozen["panel"] == "a"].copy().sort_values("order")
    panel_b = frozen.loc[frozen["panel"] == "b"].copy().sort_values("order")
    panel_c = frozen.loc[frozen["panel"] == "c"].copy()
    panel_c["is_frozen_ifn_gene"] = panel_c["is_frozen_ifn_gene"].astype(str).str.lower().eq("true")
    highlighted = panel_c.loc[panel_c["is_frozen_ifn_gene"]].copy()
    if len(panel_a) != 5 or len(panel_b) != 6 or len(panel_c) != 4410 or len(highlighted) != 10:
        raise RuntimeError("Frozen Figure 4 panel ownership counts changed")
    if int((highlighted["gse174188_logFC"].astype(float).gt(0) & highlighted["gse135779_logFC"].astype(float).gt(0)).sum()) != 10:
        raise RuntimeError("Frozen IFN-gene concordance changed")

    figure_dir = RUN / "figures/figures"
    source_dir = RUN / "figures/source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)

    source_rows = []
    for frame in (panel_a, panel_b, panel_c, calibration):
        source_rows.append(frame.copy())
    pd.concat(source_rows, ignore_index=True, sort=False).to_csv(
        source_dir / "Figure4_source_data.csv", index=False, lineterminator="\n"
    )

    base.ASSERTIONS.clear()
    base.configure_style()
    base.set_output_width_mm(170.0)
    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.75), constrained_layout=True)

    base.forest(axes[0, 0], panel_a, "label", "effect", "ci_low", "ci_high", "color")
    axes[0, 0].set_xlabel("Standardized IFN/ISG effect")
    axes[0, 0].set_title("Source-label-defined GSE135779 replication", loc="left", pad=4)
    axes[0, 0].text(
        0.98, 0.03, "Adult: directional only", transform=axes[0, 0].transAxes,
        ha="right", fontsize=6, color=base.COLORS["neutral"]
    )
    base.panel_label(axes[0, 0], "a")

    base.forest(axes[0, 1], panel_b, "label", "effect", "ci_low", "ci_high", "color")
    axes[0, 1].set_xlabel("Standardized IFN/ISG effect")
    axes[0, 1].set_title("Discovery vs external", loc="left", pad=4)
    base.panel_label(axes[0, 1], "b")

    axis = axes[1, 0]
    non_ifn = panel_c.loc[~panel_c["is_frozen_ifn_gene"]]
    axis.scatter(
        non_ifn["gse174188_logFC"], non_ifn["gse135779_logFC"], s=4,
        color=base.COLORS["light"], alpha=0.38, linewidths=0, rasterized=True
    )
    axis.scatter(
        highlighted["gse174188_logFC"], highlighted["gse135779_logFC"], s=18,
        color=base.COLORS["sle"], edgecolor="white", linewidth=0.35, zorder=3
    )
    for _, row in highlighted.nlargest(3, "gse135779_logFC").iterrows():
        axis.annotate(
            row["gene_symbol"], (row["gse174188_logFC"], row["gse135779_logFC"]),
            xytext=(3, 2), textcoords="offset points", fontsize=5.5
        )
    rho = float(panel_c[["gse174188_logFC", "gse135779_logFC"]].corr(method="spearman").iloc[0, 1])
    axis.axhline(0, color="#777777", lw=0.6)
    axis.axvline(0, color="#777777", lw=0.6)
    axis.text(
        0.03, 0.96,
        f"Shared tested genes: {len(panel_c):,}\nSpearman rho={rho:.3f}\nIFN genes positive: 10/10",
        transform=axis.transAxes, va="top", fontsize=6.2
    )
    axis.set_xlabel("GSE174188 discovery log2 fold change")
    axis.set_ylabel("GSE135779 childhood log2 fold change")
    axis.set_title("Program-specific, not genome-wide, coherence", loc="left", pad=4)
    base.style_axis(axis)
    base.panel_label(axis, "c")

    axis = axes[1, 1]
    rows = calibration.reset_index(drop=True)
    y = np.arange(len(rows))[::-1]
    pass_color = base.COLORS["internal"]
    fail_color = base.COLORS["sle"]
    for y_value, (_, row) in zip(y, rows.iterrows(), strict=True):
        margin = float(row["margin"])
        color = pass_color if margin >= 0 else fail_color
        axis.plot([0, margin], [y_value, y_value], color=color, lw=1.2, zorder=2)
        axis.scatter([margin], [y_value], s=28, color=color, edgecolor="white", linewidth=0.4, zorder=3)
        relation = ">=" if margin >= 0 else "<"
        label_x = margin + 0.008 if margin >= 0 else 0.012
        axis.text(
            label_x, y_value, f"{float(row['observed']):.3f} {relation} {float(row['criterion']):.2f}",
            ha="left", va="center", fontsize=6.1, color="#222222"
        )
    axis.axvline(0, color="#666666", lw=0.7, ls="--", zorder=1)
    axis.set_xlim(-0.035, 0.225)
    axis.set_ylim(-0.72, 2.55)
    axis.set_yticks(y, rows["metric"])
    axis.set_xlabel("Observed minus prespecified criterion")
    axis.set_title("Required elastic-net calibration", loc="left", pad=4)
    axis.text(
        0.02, 0.025, "B_ASC criterion not met\nNo corrected effect estimated",
        transform=axis.transAxes, ha="left", va="bottom", fontsize=5.7,
        color=fail_color
    )
    base.style_axis(axis)
    base.panel_label(axis, "d")

    base.save_figure(figure, figure_dir, "Figure4_independent_ifn_replication")
    pdf = figure_dir / "Figure4_independent_ifn_replication.pdf"
    png = figure_dir / "Figure4_independent_ifn_replication.png"
    return pdf, png, source_dir / "Figure4_source_data.csv"


def comparison_sheet(current: Path, candidate: Path, output: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in (current, candidate)]
    width = max(image.width for image in images)
    images = [image.resize((width, round(image.height * width / image.width))) for image in images]
    header = 70
    canvas = Image.new("RGB", (width * 2, max(image.height for image in images) + header), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    draw.text((30, 18), "Prior frozen Figure 4", fill="black", font=font)
    draw.text((width + 30, 18), "Transfer-boundary candidate", fill="black", font=font)
    for index, image in enumerate(images):
        canvas.paste(image, (index * width, header))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def patch_manuscript() -> tuple[str, str, list[dict[str, str]]]:
    before = (PARENT / "sources/Manuscript_figure1_boundary_promotion.md").read_text(encoding="utf-8")
    replacements = [
        (
            "F4-XREF-1",
            "Move donor/source-label influence ownership to Supplementary Figure S7",
            "Omitting each of the eight contributing source B-cell labels retained the same 43 donors and yielded effects from 1.019 to 1.051, arguing against dependence on any single contributing source label.",
            "Omitting each of the eight contributing source B-cell labels retained the same 43 donors and yielded effects from 1.019 to 1.051, arguing against dependence on any single contributing source label (Supplementary Fig. S7).",
        ),
        (
            "F4-XREF-2",
            "Restrict gene-level coherence ownership to Figure 4c",
            "both datasets (Fig. 4c,d).",
            "both datasets (Fig. 4c).",
        ),
        (
            "F4-XREF-3",
            "Promote corrected calibration failure to Figure 4d",
            "Corrected external disease outcomes were therefore not estimated (Supplementary Table S9 and Supplementary Fig. S8).",
            "Corrected external disease outcomes were therefore not estimated (Fig. 4d; Supplementary Table S9 and Supplementary Fig. S8).",
        ),
        (
            "F4-LEGEND",
            "Synchronize Figure 4d ownership with the source rerender",
            "a, Standardized IFN/ISG effects for childhood, combined, adult and support-threshold GSE135779 analyses. b, Standardized GSE174188 discovery/internal effects beside source-label-defined GSE135779 effects. c, Effects for 4,410 genes tested in both primary datasets, highlighting the ten jointly tested IFN genes; all ten were positive despite genome-wide Spearman rho=0.026. d, Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Display labels 1-8 map to the source codes in Figure 4 Source Data. Donors are the biological units; the adult estimate is directional only.",
            "a, Standardized IFN/ISG effects for childhood, combined, adult and support-threshold GSE135779 analyses. b, GSE174188 discovery/internal effects beside source-label-defined GSE135779 effects. c, Effects for 4,410 shared tested genes; all ten IFN genes were positive despite genome-wide Spearman rho=0.026. d, Required corrected elastic-net calibration, displayed as observed minus criterion. Coverage and B_CONV precision passed; B_ASC precision was 0.885 (<0.90), so no corrected external disease effect was estimated. Dashed line, criterion equality. Supplementary Figs. S7/S8 retain full influence/remapping diagnostics. Donors are biological units; the adult estimate is directional only.",
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


def write_panel_matrix() -> None:
    source = PARENT / "02_PANEL_DECISION_MATRIX.csv"
    rows = list(csv.DictReader(source.open(encoding="utf-8-sig", newline="")))
    for row in rows:
        if row["object"] == "Figure 4d":
            row["scientific_decision"] = "SOURCE_REPLACEMENT"
            row["artwork_action"] = "S8_REQUIRED_MAPPER_CALIBRATION_SUMMARY"
            row["rationale"] = (
                "Corrected source-label-independent calibration is an Abstract-level boundary; "
                "S7 retains the complete donor/source-label influence diagnostics."
            )
    output = RUN / "02_PANEL_DECISION_MATRIX.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
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
    (RUN / "sources").mkdir(parents=True)
    (RUN / "source_inputs").mkdir(parents=True)
    (RUN / "qa").mkdir(parents=True)
    (RUN / ".gitignore").write_text(
        "qa/lo_render/\nqa/wps_pages/*/\nqa/lo_pages/*/\n", encoding="utf-8", newline="\n"
    )

    for name in SOURCE_HASHES:
        shutil.copy2(PARENT / "figures/source_data" / name, RUN / "source_inputs" / name)
    with (RUN / "00_EXTERNAL_INPUT_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(external_manifest)

    calibration = calibration_rows()
    calibration.to_csv(RUN / "01_FIGURE4_CALIBRATION_DERIVATION.csv", index=False, lineterminator="\n")
    pdf, png, figure_source = build_figure4(calibration)
    width_mm, height_mm = pdf_size_mm(pdf)
    comparison_sheet(
        PARENT / "figures/figures/Figure4_independent_ifn_replication.png",
        png,
        RUN / "qa/Figure4_current_vs_transfer_boundary.png",
    )

    before, after, ledger = patch_manuscript()
    before_path = RUN / "sources/Manuscript_before_figure4_transfer_boundary.md"
    after_path = RUN / "sources/Manuscript_figure4_transfer_boundary.md"
    supplement_path = RUN / "sources/Supplementary_Information_unchanged.md"
    before_path.write_text(before, encoding="utf-8", newline="\n")
    after_path.write_text(after, encoding="utf-8", newline="\n")
    supplement = (ROOT / "01_manuscript/Supplementary_Information.md").read_text(encoding="utf-8")
    supplement_path.write_text(supplement, encoding="utf-8", newline="\n")
    with (RUN / "03_TEXT_EDIT_LEDGER.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)
    diff = "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile="Manuscript_before_figure4_transfer_boundary.md",
        tofile="Manuscript_figure4_transfer_boundary.md",
    ))
    (RUN / "04_MANUSCRIPT_FIGURE4_TRANSFER_BOUNDARY.diff").write_text(diff, encoding="utf-8", newline="\n")
    write_panel_matrix()

    parent_assets = [p for group in ("figures", "source_data") for p in (PARENT / "figures" / group).glob("*") if p.is_file()]
    changed = []
    for parent_path in parent_assets:
        candidate_path = RUN / "figures" / parent_path.parent.name / parent_path.name
        if sha256(parent_path) != sha256(candidate_path):
            changed.append(parent_path.name)
    checks = {
        "source_hashes_locked": source_hashes == SOURCE_HASHES,
        "external_candidate_values_reproduced": len(calibration) == 3,
        "required_mapper_is_elastic_net": set(calibration["mapper"]) == {"required corrected elastic_net"},
        "coverage_passes": abs(float(calibration.loc[calibration["metric"] == "Coverage", "margin"].iloc[0]) - 0.14195804195804196) < 1e-12,
        "bconv_precision_passes": abs(float(calibration.loc[calibration["metric"] == "B_CONV precision", "margin"].iloc[0]) - 0.09644950871108915) < 1e-12,
        "basc_precision_fails": abs(float(calibration.loc[calibration["metric"] == "B_ASC precision", "margin"].iloc[0]) + 0.014790286975717493) < 1e-12,
        "figure4_is_single_page_170mm": len(PdfReader(pdf).pages) == 1 and abs(width_mm - 170.0) < 0.15,
        "only_three_figure_assets_changed": sorted(changed) == sorted([
            "Figure4_independent_ifn_replication.pdf",
            "Figure4_independent_ifn_replication.png",
            "Figure4_source_data.csv",
        ]),
        "four_exact_text_operations": len(ledger) == 4,
        "figure4c_is_gene_coherence_owner": "both datasets (Fig. 4c)." in after,
        "figure4d_is_calibration_owner": "Fig. 4d; Supplementary Table S9 and Supplementary Fig. S8" in after,
        "s7_retains_influence_owner": "single contributing source label (Supplementary Fig. S7)." in after,
        "figure5_text_unchanged": before.split("### Figure 5 |", 1)[1] == after.split("### Figure 5 |", 1)[1],
        "supplementary_information_unchanged": sha256(ROOT / "01_manuscript/Supplementary_Information.md") == sha256(supplement_path),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FIGURE4_TRANSFER_BOUNDARY_SOURCE_RERENDER_DOCX_REQUIRED" if not failed else "HOLD_FIGURE4_TRANSFER_BOUNDARY_REVIEW_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "source_sha256": source_hashes,
        "figure4": {
            "pdf": pdf.relative_to(ROOT).as_posix(),
            "pdf_sha256": sha256(pdf),
            "png": png.relative_to(ROOT).as_posix(),
            "png_sha256": sha256(png),
            "source_data": figure_source.relative_to(ROOT).as_posix(),
            "source_data_sha256": sha256(figure_source),
            "width_mm": round(width_mm, 3),
            "height_mm": round(height_mm, 3),
            "panel_d": "SOURCE_REPLACEMENT_FROM_LOCKED_S8_REQUIRED_ELASTIC_NET",
        },
        "changed_assets": changed,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "mapping_thresholds_changed": False,
        "mapper_substitution_authorized": False,
        "figure5_candidate_status": "ARCHIVED_DEFERRED_TO_ISOLATED_NEXT_GATE",
        "submission_package_sha256": PACKAGE_SHA256,
    }
    (RUN / "05_FIGURE4_TRANSFER_BOUNDARY_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    if failed:
        raise RuntimeError(f"Figure 4 integration checks failed: {failed}")
    (ROOT / "01_manuscript/Manuscript.md").write_text(after, encoding="utf-8", newline="\n")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
