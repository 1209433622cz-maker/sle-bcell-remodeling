#!/usr/bin/env python3
"""Build and audit a gene-level Figure 5e replacement candidate."""

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

import pandas as pd
from pypdf import PdfReader

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = (
    ROOT
    / "phase17_v7/npj_sba_full_main_figure_refinement/20260831_figure5e_and_figures2to4_adjudication"
)
BASELINE_RUN = (
    ROOT
    / "phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates/recommended_scientific_candidate"
)
GENE_SOURCE = ROOT / "phase17_v7/gateC6B/20260815_regulatory_evidence/17_GSE23307_LOG2P1_PAIRED_GENE_EFFECTS.csv"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
EXPECTED_PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    if sha256(PACKAGE) != EXPECTED_PACKAGE_SHA256:
        raise RuntimeError("Exact package changed before Figure 5e candidate construction")
    if RUN_DIR.exists():
        shutil.rmtree(RUN_DIR)
    figure_dir = RUN_DIR / "Figure5E_paired_gene_dot/figures"
    source_dir = RUN_DIR / "Figure5E_paired_gene_dot/source_data"
    figure_dir.mkdir(parents=True)
    source_dir.mkdir(parents=True)

    os.environ["NPJ_SBA_STYLE"] = "1"
    base.configure_style()
    base.set_output_width_mm(170.0)
    base.ASSERTIONS.clear()
    base.build_figure5(
        ROOT,
        figure_dir,
        source_dir,
        proliferation_specificity_comparators=True,
        parallel_evidence_branches=True,
        three_evidence_branches=True,
        panel_a_variant="quantitative_matrix",
        panel_e_variant="paired_gene_dot",
    )

    candidate_source = source_dir / "Figure5_source_data.csv"
    baseline_source = BASELINE_RUN / "source_data/Figure5_source_data.csv"
    candidate_rows = csv_rows(candidate_source)
    baseline_rows = csv_rows(baseline_source)
    if candidate_rows[: len(baseline_rows)] != baseline_rows:
        raise RuntimeError("Original 29 Figure 5 Source Data rows changed")
    appended = candidate_rows[len(baseline_rows) :]
    if len(appended) != 24:
        raise RuntimeError(f"Expected 24 appended gene-level rows, found {len(appended)}")

    frozen_genes = pd.read_csv(GENE_SOURCE)
    observed = {
        (row["category"].split("|", 1)[0], row["category"].split("|", 1)[1]): float(row["estimate"])
        for row in appended
    }
    expected = {
        (str(row.donor_id), str(row.gene_symbol)): float(row.paired_log2p1_effect)
        for row in frozen_genes.itertuples()
    }
    if observed != expected:
        raise RuntimeError("Appended Figure 5e rows do not reproduce the frozen paired-gene table")

    pdf = figure_dir / "Figure5_regulatory_evidence.pdf"
    page = PdfReader(pdf).pages[0]
    width_mm = float(page.mediabox.width) * 25.4 / 72.0
    height_mm = float(page.mediabox.height) * 25.4 / 72.0
    text = " ".join((item.extract_text() or "") for item in PdfReader(pdf).pages)
    semantic_tokens = (
        "Quantitative evidence summary",
        "IFN-beta paired gene effects",
        "n=2; descriptive",
        "observational convergence",
    )
    if not all(token in text for token in semantic_tokens):
        raise RuntimeError("Figure 5e candidate is missing required semantic labels")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FIGURE5E_GENE_LEVEL_CANDIDATE_READY_FOR_VISUAL_ADJUDICATION",
        "exact_package_sha256": EXPECTED_PACKAGE_SHA256,
        "exact_package_modified": False,
        "baseline_figure5_source_sha256": sha256(baseline_source),
        "candidate_figure5_source_sha256": sha256(candidate_source),
        "frozen_gene_source": GENE_SOURCE.relative_to(ROOT).as_posix(),
        "frozen_gene_source_sha256": sha256(GENE_SOURCE),
        "original_rows_preserved": len(baseline_rows),
        "declared_gene_rows_appended": len(appended),
        "all_gene_effects_positive": bool((frozen_genes["paired_log2p1_effect"] > 0).all()),
        "donors": int(frozen_genes["donor_id"].nunique()),
        "genes_per_donor": sorted(frozen_genes.groupby("donor_id").size().astype(int).tolist()),
        "panel_data_assertions": len(base.ASSERTIONS),
        "panel_data_assertions_pass": all(row["pass"] for row in base.ASSERTIONS),
        "pdf_sha256": sha256(pdf),
        "png_sha256": sha256(pdf.with_suffix(".png")),
        "width_mm": round(width_mm, 3),
        "height_mm": round(height_mm, 3),
        "scientific_estimates_changed": False,
        "new_inference_added": False,
    }
    (RUN_DIR / "00_FIGURE5E_CANDIDATE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
