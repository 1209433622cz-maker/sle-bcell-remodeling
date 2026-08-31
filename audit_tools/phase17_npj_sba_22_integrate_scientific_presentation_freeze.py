#!/usr/bin/env python3
"""Build the reader-path and legend-economy scientific presentation candidate."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

import phase17_c7_01_build_main_figures as main_figures
import phase17_npj_sba_19_integrate_scientific_coherence_refreeze as prior_stage


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_scientific_presentation_freeze/"
    "20260831_reader_path_and_legend_economy"
)
FIGURE_ROOT = RUN / "figures"
FIGURE_DIR = FIGURE_ROOT / "figures"
SOURCE_DIR = FIGURE_ROOT / "source_data"
SOURCE_OUTPUT = RUN / "sources"
PRIOR_RUN = (
    ROOT
    / "phase17_v7/npj_sba_scientific_coherence_refreeze/"
    "20260831_claim_order_reader_boundaries"
)
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_text(path: Path) -> str:
    return "\n".join((page.extract_text() or "") for page in PdfReader(path).pages)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} block; found {count}")
    return text.replace(old, new, 1)


def apply_edits(
    text: str,
    edits: list[tuple[str, str, str, str, str]],
    scope: str,
) -> tuple[str, list[dict[str, str]]]:
    ledger = []
    for label, object_type, rationale, old, new in edits:
        text = replace_once(text, old, new, label)
        ledger.append(
            {
                "scope": scope,
                "edit": label,
                "object_type": object_type,
                "rationale": rationale,
                "old_text": old,
                "new_text": new,
                "scientific_estimate_changed": "False",
            }
        )
    return text, ledger


def build_all_figures() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    prior_stage.RUN = RUN
    prior_stage.FIGURE_ROOT = FIGURE_ROOT
    prior_stage.FIGURE_DIR = FIGURE_DIR
    prior_stage.SOURCE_DIR = SOURCE_DIR
    prior_stage.SOURCE_OUTPUT = SOURCE_OUTPUT
    assertions = prior_stage.build_all_figures()

    os.environ["NPJ_SBA_STYLE"] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")
    main_figures.configure_style()
    main_figures.set_output_width_mm(170.0)
    main_figures.build_figure1(
        ROOT,
        FIGURE_DIR,
        SOURCE_DIR,
        graphical_validation_workflow=True,
        publication_source_data=True,
        explicit_threshold_semantics=True,
        nature_evidence_hierarchy=True,
        panel_a_variant="reader_path_units",
        retained_scaffold_language=True,
    )
    main_figures.build_figure5(
        ROOT,
        FIGURE_DIR,
        SOURCE_DIR,
        proliferation_specificity_comparators=True,
        three_evidence_branches=True,
        panel_a_variant="interpretive_roles",
        panel_e_variant="paired_gene_dot",
        evidence_ownership_language=True,
    )
    return assertions


def legend_blocks() -> tuple[str, str]:
    old = """## Figure legends

### Figure 1 | Disease-blind reconstruction defines the retained analysis scope

a, Disease-blind workflow and identity scope. The GSE174188 B-lineage input was subjected to disease-blind resampling to define the permissible B_CONV/B_ASC scaffold shown in b-d. The scaffold was then separated into sample-level B_ASC composition and donor-aware B_CONV pseudobulk analyses. The diagram distinguishes the retained broad-compartment analyses from hard fine-state assignments, which were not retained for disease-effect inference. b, Median mapped adjusted Rand index and minimum-to-median interval for each candidate identity policy across 20 within-library resamples of the frozen 50-dimensional Harmony representation; policies are discrete alternatives and are not connected as a trajectory. The short dashed segment applies only to the two-compartment minimum-ARI criterion of 0.90. c, Mapped adjusted Rand index and mapping agreement in each frozen-representation two-compartment graph resample; the dashed horizontal guide marks the minimum mapping-agreement criterion of 0.990. d, Minimum and median state Jaccard indices from the same frozen-representation analysis for B_CONV and B_ASC, with antibody-secreting marker support; the dashed vertical guide marks the minimum state-median Jaccard criterion of 0.95. Panels b-d do not recompute highly variable genes, principal components or Harmony; the end-to-end sensitivity is reported in Supplementary Fig. S9. Cell-level summaries define assignment stability and are not disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

a, Observed B_ASC fractions for exactly 43 control and 47 managed-SLE sample-cohort strata in the primary composition contrast; diamonds and bars show adjusted fractions and 95% confidence intervals. b, Primary, internal, donor-nonoverlap and secondary flare conditional odds ratios. c, Frozen primary estimate and mandatory minimum-cell, explicit non-B and residual-doublet sensitivities. d, Conditional odds ratios after each of 90 primary sample deletions; the horizontal line is the full estimate. The flare contrast is secondary and did not pass the frozen three-contrast false-discovery-rate rule.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

a, Effects and 95% confidence intervals for the four frozen programs in the primary contrast. b, IFN/ISG estimates across primary support thresholds, residual-risk restriction, internal replication, donor-nonoverlap internal replication and the secondary flare contrast. c, Gene-level log2 fold changes for the frozen IFN positive arm in the primary and donor-nonoverlap contrasts. A dagger marks genes not tested at gene level in either contrast; a double dagger marks genes not tested in the primary contrast. Filtered values are absent rather than zero or imputed. d, IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity families in the primary and donor-nonoverlap contrasts. Program intervals use HC3 uncertainty; confirmatory q values use the frozen four-program family.

### Figure 4 | GSE135779 provides source-label-defined replication of the frozen IFN/ISG program

a, Standardized IFN/ISG effects for childhood, combined, adult and support-threshold external analyses. b, Standardized discovery and internal GSE174188 effects beside source-label-defined independent GSE135779 effects. c, Effects for 4,410 genes tested in both primary datasets, with ten jointly tested frozen IFN genes highlighted; all ten were positive in both datasets despite Spearman rho=0.026 genome-wide. d, Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Sequential display labels 1-8 correspond to the original source codes retained in Figure 4 Source Data. Donors are the biological units in GSE135779; the adult estimate is directional only.

### Figure 5 | Convergent observational evidence supports IFN-centred regulation

a, Quantitative summary of three evidence classes for the replicated IFN/ISG program. ULM STAT1/STAT2 activity was positive and passed the global 24-test q<0.05 criterion in all six regulator-by-contrast tests; M5911 normalized enrichment scores exceeded 3.0 in all three contrasts; and all 12 frozen positive-arm genes increased in each of two IFN-beta-exposed donors. The regulator family provides confirmatory observational evidence, M5911 provides orthogonal response-set concordance and GSE23307 provides descriptive perturbational context. Together these layers support observational convergence but not a causal regulator, direct binding or a uniquely upstream ligand. b, Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. c, Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation specificity comparators. Asterisks indicate global 24-test q<0.05. d, M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. e, Gene-level paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells from each of two healthy donors. Points for the same gene are connected only to aid donor comparison; all 24 donor-gene effects were positive. The GSE23307 panel is descriptive at n=2 and carries no inferential P value.
"""
    new = """## Figure legends

### Figure 1 | Disease-blind reconstruction defines a bounded analysis scaffold

a, Inference workflow and identity scope. Disease-blind identity stress tests defined B_CONV/B_ASC as an analysis scaffold. Disease fields were joined only after identity adjudication; B_ASC composition and B_CONV transcription were then analysed at the sample-cohort stratum. Hard fine-state assignments were not used for disease inference. b, Median mapped adjusted Rand index and minimum-to-median interval for candidate identity policies across 20 within-library resamples of the fixed 50-dimensional Harmony representation; the dashed segment marks the two-compartment minimum-ARI criterion of 0.90. c, Mapped adjusted Rand index and mapping agreement for each two-compartment resample; the dashed guide marks the 0.990 minimum-agreement criterion. d, Minimum and median state Jaccard indices for B_CONV and B_ASC with B_ASC marker support; the dashed guide marks the 0.95 state-median criterion. Panels b-d hold the representation fixed; end-to-end reconstruction is shown in Supplementary Fig. S9. Cell-level stability metrics are not disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

a, Observed B_ASC fractions for 43 control and 47 managed-SLE sample-cohort strata, with adjusted fractions and 95% confidence intervals. b, Primary, internal, donor-nonoverlap and secondary flare conditional odds ratios. c, Primary estimate and prespecified minimum-cell, explicit non-B and residual-doublet sensitivities. d, Conditional odds ratios after each of 90 primary sample deletions; the horizontal line is the full estimate. The flare contrast was secondary and did not pass the prespecified three-contrast correction.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

a, Effects and 95% confidence intervals for the four prespecified B_CONV programs in the primary contrast. b, IFN/ISG estimates across support thresholds, residual-risk restriction, internal replication, donor-nonoverlap internal replication and the secondary flare contrast. c, Gene-level log2 fold changes for the prespecified IFN positive arm in the primary and donor-nonoverlap contrasts. A dagger marks genes not tested in either contrast; a double dagger marks genes not tested in the primary contrast. Filtered values are absent rather than zero or imputed. d, IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity families in the primary and donor-nonoverlap contrasts. Program intervals use HC3 uncertainty; program q values use the prespecified four-program family.

### Figure 4 | GSE135779 provides source-label-defined replication of the IFN/ISG program

a, Standardized IFN/ISG effects for childhood, combined, adult and support-threshold GSE135779 analyses. b, Standardized GSE174188 discovery/internal effects beside source-label-defined GSE135779 effects. c, Effects for 4,410 genes tested in both primary datasets, highlighting the ten jointly tested IFN genes; all ten were positive despite genome-wide Spearman rho=0.026. d, Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Display labels 1-8 map to the source codes in Figure 4 Source Data. Donors are the biological units; the adult estimate is directional only.

### Figure 5 | Convergent observational evidence supports an IFN-centred regulatory context

a, Evidence classes and interpretive roles for the replicated IFN/ISG program. ULM STAT1/STAT2 provides confirmatory observational evidence across three contrasts, M5911 provides response-set concordance and GSE23307 provides descriptive IFN-beta perturbational context. These layers show observational convergence but do not establish a causal regulator, direct binding or a unique upstream stimulus. b, Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. c, Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation comparators; asterisks denote global 24-test q<0.05. d, M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. e, Paired log2(x+1) effects for the 12-gene IFN positive arm in two IFN-beta-exposed healthy donors; same-gene points are connected for display only, all 24 effects were positive and no inferential P value was calculated at n=2.
"""
    return old, new


def build_manuscript() -> tuple[Path, list[dict[str, str]]]:
    source = PRIOR_RUN / "sources/Manuscript_scientific_coherence_refreeze_candidate.md"
    text = source.read_text(encoding="utf-8")
    old_legends, new_legends = legend_blocks()
    edits = [
        (
            "Main-figure legend economy and unit synchronization",
            "LEGEND_SET",
            "Compress display repetition while retaining panel purpose, inferential unit, test semantics and claim boundary.",
            old_legends,
            new_legends,
        )
    ]
    text, ledger = apply_edits(text, edits, "Manuscript")
    output = SOURCE_OUTPUT / "Manuscript_scientific_presentation_freeze_candidate.md"
    output.write_text(text, encoding="utf-8", newline="\n")
    return output, ledger


def build_supplement() -> tuple[Path, list[dict[str, str]]]:
    source = PRIOR_RUN / "sources/Supplementary_Information_scientific_coherence_refreeze_candidate.md"
    text = source.read_text(encoding="utf-8")
    edits = [
        (
            "Supplementary title synchronization",
            "TITLE",
            "Use the exact comparative title approved in the main manuscript.",
            "# Supplementary information\n\n## Disease-blind reconstruction distinguishes reproducible interferon remodeling from unstable B-cell state assignments in systemic lupus erythematosus",
            "# Supplementary information\n\n## Disease-blind reconstruction distinguishes reproducible interferon remodeling from less stable B-cell state assignments in systemic lupus erythematosus",
        ),
        (
            "Corrected-calibration boundary language",
            "TABLE_NOTE",
            "Replace the final internal workflow-state term with the scientific event that stopped outcome estimation.",
            "No new multiplicity family was evaluated after the calibration HOLD.",
            "No new multiplicity family was evaluated after corrected calibration failed.",
        ),
    ]
    text, ledger = apply_edits(text, edits, "Supplementary Information")
    output = SOURCE_OUTPUT / "Supplementary_Information_scientific_presentation_freeze_candidate.md"
    output.write_text(text, encoding="utf-8", newline="\n")
    return output, ledger


def write_ledger(rows: list[dict[str, str]]) -> Path:
    output = SOURCE_OUTPUT / "SCIENTIFIC_PRESENTATION_EDIT_LEDGER.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output


def write_panel_decisions() -> Path:
    decisions = [
        ("Figure 1", "a", "MODIFY", "Correct sample-cohort units and expose identity-to-disease reader path."),
        ("Figure 1", "b", "KEEP", "Policy comparison retains unique identity-stability ownership."),
        ("Figure 1", "c", "KEEP", "Replicate-wise broad-partition stability remains necessary."),
        ("Figure 1", "d", "KEEP", "State-specific Jaccard and marker support remain necessary."),
    ]
    for figure in (2, 3, 4):
        for panel in "abcd":
            decisions.append(
                (f"Figure {figure}", panel, "KEEP", "No numerical, semantic or legibility defect demonstrated.")
            )
    decisions.extend(
        [
            ("Figure 5", "a", "MODIFY", "Separate multiplicity metadata from parallel interpretive roles."),
            ("Figure 5", "b", "KEEP", "Owns core and extended IFN-regulator estimates."),
            ("Figure 5", "c", "KEEP", "Owns proliferation-specificity comparators."),
            ("Figure 5", "d", "KEEP", "Owns M5911 response-set enrichment."),
            ("Figure 5", "e", "KEEP", "Owns descriptive two-donor IFN-beta response context."),
        ]
    )
    output = RUN / "01_MAIN_PANEL_FINAL_DECISION_MATRIX.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["figure", "panel", "decision", "rationale"])
        writer.writerows(decisions)
    return output


def word_count(text: str) -> int:
    return len(text.replace("\n", " ").split())


def main() -> None:
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-confirmed exact package changed before scientific presentation refinement")
    if RUN.exists():
        shutil.rmtree(RUN)
    FIGURE_DIR.mkdir(parents=True)
    SOURCE_DIR.mkdir(parents=True)
    SOURCE_OUTPUT.mkdir(parents=True)

    main_assertions, supplementary_assertions = build_all_figures()
    manuscript, manuscript_ledger = build_manuscript()
    supplement, supplement_ledger = build_supplement()
    ledger = write_ledger(manuscript_ledger + supplement_ledger)
    panel_matrix = write_panel_decisions()

    prior_stage.prior.RUN = RUN
    prior_stage.prior.FIGURE_DIR = FIGURE_DIR
    prior_stage.prior.SOURCE_DIR = SOURCE_DIR
    source_status, figure_status = prior_stage.prior.audit_sources_and_figures()
    prior_sources = PRIOR_RUN / "figures/source_data"
    prior_source_identity = {
        path.name: sha256(path) == sha256(prior_sources / path.name)
        for path in sorted(SOURCE_DIR.glob("*.csv"))
    }
    if not all(prior_source_identity.values()):
        raise RuntimeError("At least one Source Data file changed relative to the prior scientific candidate")

    figure1_text = pdf_text(FIGURE_DIR / "Figure1_disease_blind_identity_scope.pdf")
    figure5_text = pdf_text(FIGURE_DIR / "Figure5_regulatory_evidence.pdf")
    figure1_compact = "".join(figure1_text.split())
    figure_semantics = {
        "figure1_sample_cohort_composition": "B_ASCsample-cohortfractions" in figure1_compact,
        "figure1_sample_cohort_pseudobulk": "B_CONVsample-cohortpseudobulk" in figure1_compact,
        "figure1_identity_adjudication": "identityadjudication" in figure1_compact,
        "figure1_old_donor_unit_absent": "donor pseudobulk" not in figure1_text,
        "figure5_interpretive_role_header": "Interpretive role" in figure5_text,
        "figure5_confirmatory_observational": "confirmatory" in figure5_text and "observational" in figure5_text,
        "figure5_response_set_concordance": "response-set" in figure5_text and "concordance" in figure5_text,
        "figure5_causal_boundary": all(
            token in figure5_text for token in ("causal regulator", "direct binding", "unique upstream stimulus")
        ),
        "figure5_old_role_absent": "global 24-test family" not in figure5_text,
    }
    if not all(figure_semantics.values()):
        failed = [name for name, passed in figure_semantics.items() if not passed]
        raise RuntimeError(f"Reader-facing figure semantics failed: {failed}")

    old_legends, new_legends = legend_blocks()
    legend_counts = {"prior_words": word_count(old_legends), "candidate_words": word_count(new_legends)}
    legend_counts["reduction_percent"] = round(
        100 * (legend_counts["prior_words"] - legend_counts["candidate_words"]) / legend_counts["prior_words"],
        1,
    )

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SCIENTIFIC_PRESENTATION_SOURCE_BUILD_RENDER_QA_REQUIRED",
        "figure_count": len(figure_status),
        "source_data_count": len(source_status),
        "source_data": source_status,
        "source_data_byte_identical_to_prior_candidate": prior_source_identity,
        "figures": figure_status,
        "main_panel_decisions": {"modify": 2, "keep": 19, "path": panel_matrix.relative_to(ROOT).as_posix()},
        "selected_source_replots": ["Figure 1a", "Figure 5a"],
        "figure_semantics": figure_semantics,
        "legend_economy": legend_counts,
        "manuscript": {
            "path": manuscript.relative_to(ROOT).as_posix(),
            "sha256": sha256(manuscript),
            "edits": len(manuscript_ledger),
        },
        "supplementary_information": {
            "path": supplement.relative_to(ROOT).as_posix(),
            "sha256": sha256(supplement),
            "edits": len(supplement_ledger),
        },
        "canonical_ledger": {
            "path": ledger.relative_to(ROOT).as_posix(),
            "sha256": sha256(ledger),
            "rows": len(manuscript_ledger) + len(supplement_ledger),
            "exact_forward_and_reverse_verification_required": True,
        },
        "main_builder_assertions": len(main_assertions),
        "main_builder_assertions_pass": all(row["pass"] for row in main_assertions),
        "supplementary_builder_assertions": len(supplementary_assertions),
        "supplementary_builder_assertions_pass": all(row["pass"] for row in supplementary_assertions),
        "external_candidate_audit": {
            "accepted_as_authority": False,
            "useful_findings": ["Figure 1a unit defect", "Figure 5a role-column defect", "legend repetition"],
            "rejected_defects": [
                "Conceptual ledger was not exactly reversible",
                "Supplied Supplementary candidate retained the old unstable title despite its audit claiming synchronization",
                "Identity freeze wording was replaced by reader-facing identity adjudication",
            ],
        },
        "scientific_estimates_changed": False,
        "source_data_changed": False,
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
                "figures": len(figure_status),
                "source_data": len(source_status),
                "main_panels": status["main_panel_decisions"],
                "legend_economy": legend_counts,
                "package_sha256": status["exact_submission_package_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
