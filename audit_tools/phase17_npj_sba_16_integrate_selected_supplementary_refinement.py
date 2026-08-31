#!/usr/bin/env python3
"""Integrate selected S4/S10 replots and narrow claim-ownership language."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

import phase17_c7_01_build_main_figures as main_figures
import phase17_c8s_01_build_supplementary_figures as supplementary_figures
import phase17_npj_sba_02_build_figures as figure_audit
import phase17_postc9_01_build_review_figures as postc9


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_selected_supplementary_refinement/20260831_s4_s10_semantic_harmonization"
)
FIGURE_ROOT = RUN / "figures"
FIGURE_DIR = FIGURE_ROOT / "figures"
SOURCE_DIR = FIGURE_ROOT / "source_data"
SOURCE_OUTPUT = RUN / "sources"
FINAL_BASELINE = ROOT / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
PRIOR_CANDIDATE = (
    ROOT
    / "phase17_v7/npj_sba_full_main_figure_refinement/20260831_figure5e_and_figures2to4_adjudication"
    / "recommended_full_main_figure_set"
)
C9 = ROOT / "phase17_v7/gateC9R/20260828_normalization_correction"
R1 = ROOT / "phase17_v7/round6_q1_robustness/20260827_r1_hold_integration"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} block; found {count}")
    return text.replace(old, new, 1)


def build_all_figures() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    os.environ["NPJ_SBA_STYLE"] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")
    main_figures.ASSERTIONS.clear()
    main_figures.configure_style()
    main_figures.set_output_width_mm(170.0)
    supplementary_figures.ASSERTIONS.clear()
    supplementary_figures.configure_style()

    main_figures.build_figure1(
        ROOT,
        FIGURE_DIR,
        SOURCE_DIR,
        graphical_validation_workflow=True,
        publication_source_data=True,
        explicit_threshold_semantics=True,
        nature_evidence_hierarchy=True,
        panel_a_variant="workflow_scope",
        retained_scaffold_language=True,
    )
    main_figures.build_figure2(ROOT, FIGURE_DIR, SOURCE_DIR)
    main_figures.build_figure3(ROOT, FIGURE_DIR, SOURCE_DIR)
    main_figures.build_figure4(ROOT, FIGURE_DIR, SOURCE_DIR, reader_facing_source_labels=True)
    main_figures.build_figure5(
        ROOT,
        FIGURE_DIR,
        SOURCE_DIR,
        proliferation_specificity_comparators=True,
        three_evidence_branches=True,
        panel_a_variant="quantitative_matrix",
        panel_e_variant="paired_gene_dot",
        evidence_ownership_language=True,
    )

    supplementary_figures.build_s1(ROOT, FIGURE_DIR, SOURCE_DIR)
    supplementary_figures.build_s2(ROOT, FIGURE_DIR, SOURCE_DIR)
    supplementary_figures.build_s3(ROOT, FIGURE_DIR, SOURCE_DIR)
    supplementary_figures.build_s4(
        ROOT,
        FIGURE_DIR,
        SOURCE_DIR,
        log_ratio_two_part=True,
    )
    supplementary_figures.build_s5(ROOT, FIGURE_DIR, SOURCE_DIR)
    supplementary_figures.build_s6(ROOT, FIGURE_DIR, SOURCE_DIR)
    supplementary_figures.build_s7(ROOT, FIGURE_DIR, SOURCE_DIR)

    environment = os.environ.copy()
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "audit_tools/phase17_round6_02_build_overlap_depletion_figure.py"),
            "--output-dir",
            str(FIGURE_ROOT),
        ],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "audit_tools/phase17_round6_06_build_identity_hold_figure.py"),
            "--integration-dir",
            str(R1),
            "--output-dir",
            str(FIGURE_ROOT),
        ],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    postc9.build_s10(C9, FIGURE_DIR, SOURCE_DIR, semantic_harmonization=True)
    return list(main_figures.ASSERTIONS), list(supplementary_figures.ASSERTIONS)


def build_manuscript_candidate() -> tuple[Path, list[dict[str, str]]]:
    source = PRIOR_CANDIDATE / "sources/Manuscript_full_main_figure_candidate.md"
    text = source.read_text(encoding="utf-8")
    replacements = [
        (
            "Results source-matrix wording",
            "The authoritative GSE174188 B-lineage source contained 152,981 cells and 30,172 genes.",
            "The GSE174188 B-lineage source matrix contained 152,981 cells and 30,172 genes.",
        ),
        (
            "Results external-validation implementation wording",
            "GSE135779 source matrices, metadata and program-gene availability were qualified before disease effects were estimated. The external identity scope was intentionally limited to a broad conventional-B analog assembled from source B-cell labels; hard naive/memory identities were not transferred. Statistical-engine behavior was qualified with count-conservation checks and synthetic null and signal data before the real disease contrasts were evaluated.",
            "GSE135779 source matrices, metadata and program-gene availability were checked before disease effects were estimated. The external identity scope was intentionally limited to a broad conventional-B analogue assembled from source B-cell labels; hard naive/memory identities were not transferred. Count conservation and synthetic null and signal datasets were used to verify the statistical implementation before the real disease contrasts were evaluated.",
        ),
        (
            "CAMERA capitalization",
            "ranked enrichment had a camera FDR of 1.85 x 10^-7",
            "ranked enrichment had a CAMERA FDR of 1.85 x 10^-7",
        ),
        (
            "Discussion British-English terminology",
            "source-label-defined broad B-cell analog rather than demonstrating de novo taxonomy transfer",
            "source-label-defined broad B-cell analogue rather than demonstrating de novo taxonomy transfer",
        ),
        (
            "Methods external-validation implementation wording",
            "The external identity scope was deliberately broad: a conventional-B analog assembled from eight source B-cell labels, without transferring hard naive/memory identities. Childhood, adult and combined model matrices and minimum-cell sensitivities were fixed before model fitting. Real matrices were first used only for dimension and count-conservation qualification, and synthetic null and signal data were used to qualify the statistical engine.",
            "The external identity scope was deliberately broad: a conventional-B analogue assembled from eight source B-cell labels, without transferring hard naive/memory identities. Childhood, adult and combined model matrices and minimum-cell sensitivities were fixed before model fitting. Before disease-effect modelling, real matrices were used to verify dimensions and count conservation, and synthetic null and signal data were used to test the statistical implementation.",
        ),
        (
            "GSE23307 anti-pseudoreplication boundary",
            "The donor summary was the mean paired effect across the 12 genes. Direction and gene concordance were descriptive; no inferential P value was calculated at n=2.",
            "The donor summary was the mean paired effect across the 12 genes. Gene-level paired effects were retained for descriptive display; donor means served only as summaries, and no inferential test treated genes as biological replicates. Direction and gene concordance were descriptive; no inferential P value was calculated at n=2.",
        ),
        (
            "Reproducibility implementation wording",
            "Disease effects were estimated only after input, design and statistical-engine qualification.",
            "Disease effects were estimated only after input, design and statistical-implementation verification.",
        ),
        (
            "Figure 1a evidence-boundary legend",
            "The diagram distinguishes the authorized broad-compartment analyses from hard fine-state assignments, which were not authorized.",
            "The diagram distinguishes the retained broad-compartment analyses from hard fine-state assignments, which were not retained for disease-effect inference.",
        ),
        (
            "Figure 5a method ownership legend",
            "STAT1/STAT2 were positive and passed the global 24-test q<0.05 criterion in all six regulator-by-contrast tests; M5911 normalized enrichment scores exceeded 3.0 in all three contrasts; and all 12 genes increased in each of two IFN-beta-exposed donors.",
            "ULM STAT1/STAT2 activity was positive and passed the global 24-test q<0.05 criterion in all six regulator-by-contrast tests; M5911 normalized enrichment scores exceeded 3.0 in all three contrasts; and all 12 frozen positive-arm genes increased in each of two IFN-beta-exposed donors.",
        ),
    ]
    ledger = []
    for label, old, new in replacements:
        text = replace_once(text, old, new, label)
        ledger.append(
            {
                "edit": label,
                "old_text": old,
                "new_text": new,
                "scientific_estimate_changed": "False",
            }
        )
    output = SOURCE_OUTPUT / "Manuscript_scientific_harmonization_candidate.md"
    output.write_text(text, encoding="utf-8", newline="\n")
    with (SOURCE_OUTPUT / "Manuscript_scientific_harmonization_edit_ledger.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)
    return output, ledger


def build_supplement_candidate() -> tuple[Path, list[dict[str, str]]]:
    source = FINAL_BASELINE / "sources/Supplementary_Information.md"
    text = source.read_text(encoding="utf-8")
    old_s4 = (
        "**a,** Total and zero-ASC sample-cohort strata in the three base contrasts. **b,** Primary B_ASC odds ratios under support, explicit non-B and residual-risk policies using observed-information and HC1 covariance. **c,** Firth-logistic ASC-presence sensitivity. **d,** Positive-only abundance sensitivity using HC3 uncertainty. The two-part models are sensitivity analyses and do not replace the frozen beta-binomial primary model."
    )
    new_s4 = (
        "**a,** Total and zero-ASC sample-cohort strata in the three base contrasts. **b,** Primary B_ASC odds ratios under support, explicit non-B and residual-risk policies using observed-information and HC1 covariance. **c,** Firth-logistic ASC-presence sensitivity. **d,** Positive-only abundance sensitivity using HC3 uncertainty. Panels c-d use logarithmic ratio axes with the null fixed at one; the two-part models are sensitivity analyses and do not replace the frozen beta-binomial primary model."
    )
    old_s10 = """**a,** Median and interquartile range of full-library divided by selected-feature
counts among 13,000 B_CONV and 1,300 B_ASC reference training cells. This ratio
quantifies the legacy pre-log scaling discrepancy; corrected mapping uses
full-library denominators in both datasets. **b,** Per-state precision at the
diagnostic elastic-net and eligible centroid thresholds; the dashed line is the
unchanged 0.90 criterion. **c,** Reference-cell coverage at those thresholds; the
dashed line is the unchanged 0.80 criterion. **d,** Balanced accuracy in each of
five donor-grouped reference calibration folds. These folds select model and
threshold parameters, not independent performance estimates. The elastic-net
B_ASC precision failure prevents outcome access; centroid success is not a
replacement analysis. No corrected external disease result is shown."""
    new_s10 = """**a,** Median and interquartile range of full-library divided by selected-feature
counts among 13,000 B_CONV and 1,300 B_ASC reference training cells. This ratio
quantifies the legacy pre-log scaling discrepancy; corrected mapping uses
full-library denominators in both datasets. **b,** Per-state precision at the
diagnostic elastic-net and eligible centroid thresholds. Mapper colour is held
constant across panels b-d, marker shape distinguishes B_CONV from B_ASC, and the
dashed line is the unchanged 0.90 state-precision criterion. **c,** Reference-cell
coverage at those thresholds; the dashed line is the unchanged 0.80 criterion.
**d,** Balanced accuracy in each of five donor-grouped reference calibration
folds; black horizontal bars show fold means. No eligibility guide is drawn
because balanced accuracy is diagnostic only. These folds select model and
threshold parameters, not independent performance estimates. The elastic-net
B_ASC precision failure prevents outcome access; centroid success is not a
replacement analysis. No corrected external disease result is shown."""
    changes = [
        ("S4 log-axis legend", old_s4, new_s4),
        ("S10 semantic-encoding legend", old_s10, new_s10),
    ]
    ledger = []
    for label, old, new in changes:
        text = replace_once(text, old, new, label)
        ledger.append({"edit": label, "old_text": old, "new_text": new})
    output = SOURCE_OUTPUT / "Supplementary_Information_scientific_harmonization_candidate.md"
    output.write_text(text, encoding="utf-8", newline="\n")
    return output, ledger


def audit_sources_and_figures() -> tuple[dict[str, object], dict[str, object]]:
    expected_sources = {f"Figure{index}_source_data.csv" for index in range(1, 6)} | {
        f"Supplementary_Figure_S{index}_source_data.csv" for index in range(1, 11)
    }
    generated = {path.name for path in SOURCE_DIR.glob("*.csv")}
    if generated != expected_sources:
        raise RuntimeError(f"Source-data inventory differs: {sorted(generated ^ expected_sources)}")

    source_status = {}
    for name in sorted(expected_sources):
        current = SOURCE_DIR / name
        if name == "Figure1_source_data.csv":
            baseline = PRIOR_CANDIDATE / "source_data" / name
        elif name == "Figure5_source_data.csv":
            baseline = PRIOR_CANDIDATE / "source_data" / name
        else:
            baseline = FINAL_BASELINE / "figures/source_data" / name
        if sha256(current) != sha256(baseline):
            raise RuntimeError(f"Frozen Source Data changed: {name}")
        source_status[name] = {"sha256": sha256(current), "byte_identical": True}

    pdfs = sorted(FIGURE_DIR.glob("*.pdf"))
    if len(pdfs) != 15:
        raise RuntimeError(f"Expected 15 figure PDFs; found {len(pdfs)}")
    figure_status = {}
    for path in pdfs:
        reader = PdfReader(path)
        width_mm = float(reader.pages[0].mediabox.width) * 25.4 / 72.0
        height_mm = float(reader.pages[0].mediabox.height) * 25.4 / 72.0
        if len(reader.pages) != 1 or abs(width_mm - 170.0) > 0.25 or height_mm > 230.0:
            raise RuntimeError(f"Figure dimension contract failed: {path.name}")
        postflight = figure_audit.audit_exported_pdf(path)
        figure_status[path.name] = {
            "sha256": sha256(path),
            "width_mm": round(width_mm, 3),
            "height_mm": round(height_mm, 3),
            "postflight": postflight,
        }
    return source_status, figure_status


def main() -> None:
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-confirmed exact package hash changed before refinement")
    if RUN.exists():
        shutil.rmtree(RUN)
    FIGURE_DIR.mkdir(parents=True)
    SOURCE_DIR.mkdir(parents=True)
    SOURCE_OUTPUT.mkdir(parents=True)

    main_assertions, supplementary_assertions = build_all_figures()
    manuscript, manuscript_ledger = build_manuscript_candidate()
    supplement, supplement_ledger = build_supplement_candidate()
    source_status, figure_status = audit_sources_and_figures()

    decisions = [
        ("Main", "Figure1a", "MODIFY_SELECTED", "Replace audit-style authorization wording with retained-scaffold language."),
        ("Main", "Figure1b-d", "KEEP", "Identity metrics retain distinct evidence ownership."),
        ("Main", "Figure2-4", "KEEP", "No semantic or information-density defect identified."),
        ("Main", "Figure5a", "MODIFY_SELECTED", "Name ULM as the method owning the six-test result."),
        ("Main", "Figure5b-e", "KEEP", "Data selection and numerical content remain frozen."),
        ("Supplement", "S1-S3", "KEEP", "Distinct QC, representation and identity-adjudication roles."),
        ("Supplement", "S4a-b", "KEEP", "Current displays own zero-ASC and covariance/cell-policy diagnostics."),
        ("Supplement", "S4c-d", "MODIFY_SELECTED", "Log-ratio axes reveal all intervals without truncation."),
        ("Supplement", "S5-S9", "KEEP", "No material semantic or information-density defect identified."),
        ("Supplement", "S10a-d", "REPLACE_SELECTED", "Unify mapper/state encoding and remove a non-gating balanced-accuracy guide."),
    ]
    with (RUN / "01_PANEL_DECISION_MATRIX.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["set", "panel", "decision", "rationale"])
        writer.writerows(decisions)

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SELECTED_SUPPLEMENTARY_REPLOT_AND_SEMANTIC_HARMONIZATION_BUILT",
        "selected_figure_changes": ["Figure1a language", "Figure5a ULM ownership", "S4c-d log ratio", "S10a-d semantic redesign"],
        "frozen_figures": ["Figure1b-d", "Figure2-4", "Figure5b-e", "S1-S3", "S4a-b", "S5-S9"],
        "main_builder_assertions": len(main_assertions),
        "main_builder_assertions_pass": all(row["pass"] for row in main_assertions),
        "supplementary_builder_assertions": len(supplementary_assertions),
        "supplementary_builder_assertions_pass": all(row["pass"] for row in supplementary_assertions),
        "source_data": source_status,
        "figures": figure_status,
        "manuscript": {
            "path": manuscript.relative_to(ROOT).as_posix(),
            "sha256": sha256(manuscript),
            "narrow_edits": len(manuscript_ledger),
        },
        "supplementary_information": {
            "path": supplement.relative_to(ROOT).as_posix(),
            "sha256": sha256(supplement),
            "legend_edits": len(supplement_ledger),
        },
        "external_proof_policy": "External PDFs were inspected as proposals but not copied or used as numerical sources.",
        "scientific_estimates_changed": False,
        "new_inference_added": False,
        "exact_submission_package_modified": False,
        "exact_submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "00_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "status": status["status"],
                "figure_count": len(figure_status),
                "source_count": len(source_status),
                "manuscript_edits": len(manuscript_ledger),
                "package_sha256": status["exact_submission_package_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
