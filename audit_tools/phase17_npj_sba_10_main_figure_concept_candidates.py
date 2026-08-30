#!/usr/bin/env python3
"""Build source-driven Figure 1a and Figure 5a concept candidates."""

from __future__ import annotations

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
BASELINE = (
    ROOT
    / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
)
RUN_DIR = (
    ROOT
    / "phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates"
)
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
ATTACHMENT = Path(
    r"C:\Users\Administrator\.codex\attachments\a3f5e785-e002-4272-9848-16cd8408cb7c\pasted-text.txt"
)
EXPECTED_PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_size_mm(path: Path) -> tuple[float, float]:
    page = PdfReader(path).pages[0]
    return (
        float(page.mediabox.width) * 25.4 / 72.0,
        float(page.mediabox.height) * 25.4 / 72.0,
    )


def pdf_text(path: Path) -> str:
    return " ".join((page.extract_text() or "") for page in PdfReader(path).pages)


def build_figure1_variant(name: str, variant: str) -> dict[str, object]:
    output = RUN_DIR / name
    figure_dir = output / "figures"
    source_dir = output / "source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    base.ASSERTIONS.clear()
    base.build_figure1(
        ROOT,
        figure_dir,
        source_dir,
        graphical_validation_workflow=True,
        publication_source_data=True,
        explicit_threshold_semantics=True,
        nature_evidence_hierarchy=True,
        panel_a_variant=variant,
    )
    pdf = figure_dir / "Figure1_disease_blind_identity_scope.pdf"
    text = pdf_text(pdf)
    return {
        "candidate": name,
        "panel": "Figure1a",
        "variant": variant,
        "pdf": pdf.relative_to(ROOT).as_posix(),
        "png": pdf.with_suffix(".png").relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source_dir / "Figure1_source_data.csv"),
        "assertions": len(base.ASSERTIONS),
        "all_assertions_pass": all(row["pass"] for row in base.ASSERTIONS),
        "semantic_boundary_present": (
            "fine-state assignments" in text.lower()
            or "fine states not assigned" in text.lower()
        ),
    }


def build_figure5_variant(name: str, variant: str) -> dict[str, object]:
    output = RUN_DIR / name
    figure_dir = output / "figures"
    source_dir = output / "source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    base.ASSERTIONS.clear()
    base.build_figure5(
        ROOT,
        figure_dir,
        source_dir,
        proliferation_specificity_comparators=True,
        parallel_evidence_branches=True,
        three_evidence_branches=True,
        panel_a_variant=variant,
    )
    pdf = figure_dir / "Figure5_regulatory_evidence.pdf"
    text = pdf_text(pdf)
    return {
        "candidate": name,
        "panel": "Figure5a",
        "variant": variant,
        "pdf": pdf.relative_to(ROOT).as_posix(),
        "png": pdf.with_suffix(".png").relative_to(ROOT).as_posix(),
        "source_sha256": sha256(source_dir / "Figure5_source_data.csv"),
        "assertions": len(base.ASSERTIONS),
        "all_assertions_pass": all(row["pass"] for row in base.ASSERTIONS),
        "semantic_boundary_present": all(
            token in text.lower()
            for token in ("observational", "causal", "unique")
        ),
    }


def main() -> None:
    if sha256(PACKAGE) != EXPECTED_PACKAGE_SHA256:
        raise RuntimeError("Exact-package SHA-256 no longer matches the author-confirmed baseline")
    if RUN_DIR.exists():
        shutil.rmtree(RUN_DIR)
    RUN_DIR.mkdir(parents=True)
    evidence_dir = RUN_DIR / "evidence"
    evidence_dir.mkdir()
    shutil.copy2(ATTACHMENT, evidence_dir / "external_review_pasted_text.txt")

    os.environ["NPJ_SBA_STYLE"] = "1"
    base.configure_style()
    base.set_output_width_mm(170.0)

    candidates = [
        build_figure1_variant("Figure1A_workflow_scope", "workflow_scope"),
        build_figure1_variant("Figure1B_evidence_matrix", "evidence_matrix"),
        build_figure5_variant("Figure5A_convergence_boundary", "convergence_boundary"),
        build_figure5_variant("Figure5B_quantitative_matrix", "quantitative_matrix"),
    ]

    baseline_hashes = {
        "Figure1_source_data.csv": sha256(BASELINE / "figures/source_data/Figure1_source_data.csv"),
        "Figure5_source_data.csv": sha256(BASELINE / "figures/source_data/Figure5_source_data.csv"),
    }
    for candidate in candidates:
        expected = baseline_hashes[f"{candidate['panel'][:-1]}_source_data.csv"]
        if candidate["source_sha256"] != expected:
            raise RuntimeError(f"Frozen source data changed in {candidate['candidate']}")
        width_mm, height_mm = pdf_size_mm(ROOT / str(candidate["pdf"]))
        candidate["width_mm"] = round(width_mm, 3)
        candidate["height_mm"] = round(height_mm, 3)
        candidate["single_page"] = len(PdfReader(ROOT / str(candidate["pdf"])).pages) == 1
        if abs(width_mm - 170.0) > 0.15 or height_mm > 225.0:
            raise RuntimeError(f"Publication dimensions failed for {candidate['candidate']}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SOURCE_DRIVEN_CANDIDATES_READY_FOR_VISUAL_ADJUDICATION",
        "exact_package_sha256_confirmed": EXPECTED_PACKAGE_SHA256,
        "exact_package_modified": False,
        "author_confirmations_recorded": {
            "order": ["Zhi Chen", "Teng Qi"],
            "corresponding_author": "Teng Qi",
            "identity_email_orcid_affiliation": "AUTHOR_CONFIRMED_CORRECT",
            "author_contributions": "AUTHOR_CONFIRMED_ACCURATE",
            "funding": "NONE_CONFIRMED",
            "competing_interests": "NONE_CONFIRMED",
            "ai_disclosure": "AUTHOR_CONFIRMED_COMPLETE_ACCURATE",
            "new_human_subjects_or_restricted_identifiable_data": "NONE_CONFIRMED",
        },
        "baseline_source_sha256": baseline_hashes,
        "attachment_sha256": sha256(ATTACHMENT),
        "scientific_estimates_changed": False,
        "rerun_scope": "source-driven redraw only; no biological model refit",
        "candidates": candidates,
    }
    (RUN_DIR / "00_CANDIDATE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
