#!/usr/bin/env python3
"""Assemble the five-figure scientific candidate after panel adjudication."""

from __future__ import annotations

import csv
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

from pypdf import PdfReader

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = (
    ROOT
    / "phase17_v7/npj_sba_full_main_figure_refinement/20260831_figure5e_and_figures2to4_adjudication"
)
FINAL_BASELINE = (
    ROOT
    / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
)
PRIOR_CANDIDATE = (
    ROOT
    / "phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates/recommended_scientific_candidate"
)
REBUILT = RUN_DIR / "rebuilt_figures2to4"
RECOMMENDED = RUN_DIR / "recommended_full_main_figure_set"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label} block, found {count}")
    return text.replace(old, new, 1)


def pdf_size_mm(path: Path) -> tuple[float, float]:
    page = PdfReader(path).pages[0]
    return (
        float(page.mediabox.width) * 25.4 / 72.0,
        float(page.mediabox.height) * 25.4 / 72.0,
    )


def rebuild_figures2to4() -> dict[str, object]:
    if REBUILT.exists():
        shutil.rmtree(REBUILT)
    figure_dir = REBUILT / "figures"
    source_dir = REBUILT / "source_data"
    figure_dir.mkdir(parents=True)
    source_dir.mkdir(parents=True)
    base.ASSERTIONS.clear()
    base.build_figure2(ROOT, figure_dir, source_dir)
    base.build_figure3(ROOT, figure_dir, source_dir)
    base.build_figure4(ROOT, figure_dir, source_dir, reader_facing_source_labels=True)
    hashes: dict[str, str] = {}
    for number in (2, 3, 4):
        name = f"Figure{number}_source_data.csv"
        current = source_dir / name
        baseline = FINAL_BASELINE / "figures/source_data" / name
        if sha256(current) != sha256(baseline):
            raise RuntimeError(f"Rebuilt {name} differs from the frozen baseline")
        hashes[name] = sha256(current)
    return {
        "assertions": len(base.ASSERTIONS),
        "assertions_pass": all(row["pass"] for row in base.ASSERTIONS),
        "source_sha256": hashes,
    }


def copy_pair(source_dir: Path, target_dir: Path, stem: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for extension in ("pdf", "png"):
        source = source_dir / f"{stem}.{extension}"
        target = target_dir / source.name
        shutil.copy2(source, target)
        result[f"{extension}_sha256"] = sha256(target)
    return result


def main() -> None:
    os.environ["NPJ_SBA_STYLE"] = "1"
    base.configure_style()
    base.set_output_width_mm(170.0)
    rebuild_status = rebuild_figures2to4()

    if RECOMMENDED.exists():
        shutil.rmtree(RECOMMENDED)
    figure_dir = RECOMMENDED / "figures"
    source_dir = RECOMMENDED / "source_data"
    manuscript_dir = RECOMMENDED / "sources"
    for directory in (figure_dir, source_dir, manuscript_dir):
        directory.mkdir(parents=True, exist_ok=True)

    stems = {
        1: "Figure1_disease_blind_identity_scope",
        2: "Figure2_sample_level_composition",
        3: "Figure3_gse174188_bconv_transcription",
        4: "Figure4_independent_ifn_replication",
        5: "Figure5_regulatory_evidence",
    }
    figure_sources = {
        1: PRIOR_CANDIDATE / "figures",
        2: REBUILT / "figures",
        3: REBUILT / "figures",
        4: REBUILT / "figures",
        5: RUN_DIR / "Figure5E_paired_gene_dot/figures",
    }
    source_sources = {
        1: PRIOR_CANDIDATE / "source_data",
        2: REBUILT / "source_data",
        3: REBUILT / "source_data",
        4: REBUILT / "source_data",
        5: RUN_DIR / "Figure5E_paired_gene_dot/source_data",
    }

    figure_status: dict[str, dict[str, object]] = {}
    for number, stem in stems.items():
        entry: dict[str, object] = copy_pair(figure_sources[number], figure_dir, stem)
        source_name = f"Figure{number}_source_data.csv"
        shutil.copy2(source_sources[number] / source_name, source_dir / source_name)
        entry["source_data_sha256"] = sha256(source_dir / source_name)
        width_mm, height_mm = pdf_size_mm(figure_dir / f"{stem}.pdf")
        entry["width_mm"] = round(width_mm, 3)
        entry["height_mm"] = round(height_mm, 3)
        if abs(width_mm - 170.0) > 0.15 or height_mm > 225.0:
            raise RuntimeError(f"Figure {number} violates final-size dimensions")
        figure_status[f"Figure{number}"] = entry

    prior_manuscript = PRIOR_CANDIDATE / "sources/Manuscript_figure_refinement_candidate.md"
    manuscript = prior_manuscript.read_text(encoding="utf-8")
    old_figure5e = (
        "e, Mean paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells from two healthy donors; labels show positive genes. The GSE23307 panel is descriptive at n=2 and carries no inferential P value."
    )
    new_figure5e = (
        "e, Gene-level paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells from each of two healthy donors. Points for the same gene are connected only to aid donor comparison; all 24 donor-gene effects were positive. The GSE23307 panel is descriptive at n=2 and carries no inferential P value."
    )
    manuscript = replace_once(manuscript, old_figure5e, new_figure5e, "Figure 5e legend")
    candidate_manuscript = manuscript_dir / "Manuscript_full_main_figure_candidate.md"
    candidate_manuscript.write_text(manuscript, encoding="utf-8", newline="\n")

    decisions = [
        ("Figure1", "a", "REPLACE_SELECTED", "Workflow and identity scope replaces the text-only evidence hierarchy."),
        ("Figure1", "b-d", "RETAIN", "Policy selection, replicate stability and state-specific Jaccard own distinct identity evidence."),
        ("Figure2", "a-d", "RETAIN", "Observed distribution, contrast synthesis, mandatory sensitivity and deletion influence are complementary."),
        ("Figure3", "a-d", "RETAIN", "Program ranking, robustness, gene direction and specificity controls are nonredundant."),
        ("Figure4", "a-d", "RETAIN", "External estimates, cross-cohort comparison, gene-level boundary and influence checks are nonredundant."),
        ("Figure5", "a", "REPLACE_SELECTED", "Quantitative matrix replaces equal-weight text branches."),
        ("Figure5", "b-d", "RETAIN", "Regulator forests and M5911 enrichment remain the direct numerical evidence."),
        ("Figure5", "e", "REPLACE_SELECTED", "Frozen 24-row paired-gene display replaces two donor means without adding inference."),
    ]
    with (RECOMMENDED / "01_PANEL_DECISION_MATRIX.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["figure", "panel", "decision", "rationale"])
        writer.writerows(decisions)

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FULL_MAIN_FIGURE_SCIENTIFIC_CANDIDATE_ASSEMBLED",
        "figures": figure_status,
        "figures2to4_rebuilt_from_frozen_inputs": rebuild_status,
        "selected_replacements": ["Figure1a", "Figure5a", "Figure5e"],
        "retained_panels": ["Figure1b-d", "Figure2a-d", "Figure3a-d", "Figure4a-d", "Figure5b-d"],
        "figure5_original_rows_preserved": 29,
        "figure5_declared_gene_rows_appended": 24,
        "prior_manuscript_sha256": sha256(prior_manuscript),
        "candidate_manuscript_sha256": sha256(candidate_manuscript),
        "manuscript_change_this_round": "Figure 5e legend only",
        "scientific_estimates_changed": False,
        "new_inference_added": False,
        "exact_submission_package_modified": False,
    }
    (RECOMMENDED / "00_FULL_MAIN_FIGURE_CANDIDATE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
