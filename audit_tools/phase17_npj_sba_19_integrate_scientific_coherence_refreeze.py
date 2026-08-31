#!/usr/bin/env python3
"""Build the claim-ordered scientific coherence candidate from frozen evidence."""

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

import phase17_npj_sba_16_integrate_selected_supplementary_refinement as prior
import phase17_postc9_01_build_review_figures as postc9


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_scientific_coherence_refreeze/20260831_claim_order_reader_boundaries"
FIGURE_ROOT = RUN / "figures"
FIGURE_DIR = FIGURE_ROOT / "figures"
SOURCE_DIR = FIGURE_ROOT / "source_data"
SOURCE_OUTPUT = RUN / "sources"
PRIOR_RUN = (
    ROOT
    / "phase17_v7/npj_sba_selected_supplementary_refinement/"
    "20260831_s4_s10_semantic_harmonization"
)
R1 = ROOT / "phase17_v7/round6_q1_robustness/20260827_r1_hold_integration"
C9 = ROOT / "phase17_v7/gateC9R/20260828_normalization_correction"
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
    prior.RUN = RUN
    prior.FIGURE_ROOT = FIGURE_ROOT
    prior.FIGURE_DIR = FIGURE_DIR
    prior.SOURCE_DIR = SOURCE_DIR
    prior.SOURCE_OUTPUT = SOURCE_OUTPUT
    assertions = prior.build_all_figures()

    environment = os.environ.copy()
    environment["NPJ_SBA_STYLE"] = "1"
    environment.setdefault("MPLBACKEND", "Agg")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "audit_tools/phase17_round6_06_build_identity_hold_figure.py"),
            "--integration-dir",
            str(R1),
            "--output-dir",
            str(FIGURE_ROOT),
            "--reader-facing-criteria",
        ],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    postc9.build_s10(
        C9,
        FIGURE_DIR,
        SOURCE_DIR,
        semantic_harmonization=True,
        reader_facing_criterion_labels=True,
    )
    return assertions


def build_manuscript() -> tuple[Path, list[dict[str, str]]]:
    source = PRIOR_RUN / "sources/Manuscript_scientific_harmonization_candidate.md"
    text = source.read_text(encoding="utf-8")
    old_abstract = (
        "Single-cell disease studies can conflate cell identity, abundance and transcription when unstable annotations are treated as fixed biological states. We reanalysed public systemic lupus erythematosus datasets using disease-blind B-lineage reconstruction and donor-aware inference. Among 150,402 discovery B-lineage cells, end-to-end resampling failed a prespecified antibody-secreting-cell overlap criterion, restricting broad B-cell compartments to an analysis scaffold, yet propagation of observed assignment exchanges preserved the primary composition null and conventional-B IFN/ISG effect. The IFN/ISG program replicated in independent GSE135779 childhood donors using a source-label-defined broad B-cell analogue despite weak genome-wide concordance. Corrected source-label-independent remapping failed prespecified calibration, so no corrected external disease effect was estimated. STAT1/STAT2 analyses provided convergent but observational support and weakened after broader interferon-gene depletion. These results separate reproducible process-level interferon remodeling from less stable hard state assignments without establishing a universal B-cell taxonomy, causal regulator or clinical utility."
    )
    new_abstract = (
        "Single-cell disease studies can conflate cell identity, abundance and transcription when unstable annotations are treated as fixed biological states. We reanalysed public systemic lupus erythematosus datasets using disease-blind B-lineage reconstruction and donor-aware inference. Among 150,402 discovery B-lineage cells, end-to-end resampling failed a prespecified antibody-secreting-cell overlap criterion, restricting broad B-cell compartments to an analysis scaffold; propagating observed assignment exchanges did not change the primary composition interpretation or the positive conventional-B IFN/ISG effect. The IFN/ISG program replicated in independent GSE135779 childhood donors using a source-label-defined broad B-cell analogue despite weak genome-wide concordance. Corrected source-label-independent remapping failed prespecified calibration, so no corrected external disease effect was estimated. STAT1/STAT2 analyses provided convergent but observational support and weakened after broader interferon-gene depletion. Thus, reproducibility was stronger for a process-level interferon program than for hard state assignments, without establishing a universal taxonomy, causal regulator or clinical utility."
    )
    old_discussion_opening = (
        "The central finding of this study is not a new B-cell taxonomy but a difference in reproducibility across biological layers. Fine-grained B-cell state assignments did not satisfy the prespecified stability criteria, and even the broad B_CONV/B_ASC partition failed one state-specific end-to-end criterion because B_ASC membership was less reproducible than the global partition metrics suggested. Retaining that failure changed the interpretation of the study: B_CONV/B_ASC is used as an analysis scaffold, not as a transferable taxonomy. Within that bounded scaffold, assignment uncertainty did not alter the primary B_ASC composition null or the positive B_CONV IFN/ISG effects. The supported result is a process-level interferon association within these inferential limits; neither a disease-defining cell-state label nor generalized B_ASC expansion was established."
    )
    new_discussion_opening = (
        "The central finding of this study is a difference in reproducibility across biological layers, not a new B-cell taxonomy. Fine-state assignments were unsupported, and the retained broad scaffold still carried a B_ASC-specific end-to-end limitation. Preserving that failure constrained B_CONV/B_ASC to an analysis scaffold rather than a transferable taxonomy. Within this scope, assignment uncertainty did not change the primary B_ASC composition interpretation or the direction of B_CONV IFN/ISG effects. The supported result is therefore a process-level interferon association within explicit identity limits, not a disease-defining cell-state label or generalized B_ASC expansion."
    )
    old_external_discussion = (
        "The independent, source-label-defined GSE135779 analysis strengthens that process-level interpretation while also defining its limits. The childhood cohort reproduced the frozen IFN/ISG program, donor-deletion and source-label-omission analyses retained the direction, and all ten jointly tested IFN genes were positive in both primary datasets. Yet the genome-wide effect correlation was only rho=0.026. These observations are not contradictory: a transcriptome-wide correlation asks whether thousands of gene effects agree across cohorts that differ in age structure, source annotation, processing, covariates and gene universe, whereas the program analysis asks whether a prespecified coherent biological response retains direction and statistical support. The data support the latter but do not establish the stronger claim of a globally shared disease transcriptome. Importantly, a corrected attempt to reconstruct the external mapping without source labels failed its prespecified B_ASC calibration criterion, and no corrected disease outcome was estimated. Independent replication therefore remains tied to the prespecified source-label-defined broad B-cell analogue rather than demonstrating de novo taxonomy transfer."
    )
    new_external_discussion = (
        "The independent, source-label-defined GSE135779 analysis strengthens that process-level interpretation while also defining its limits. The childhood IFN/ISG result remained positive under donor and source-label omission, and all ten jointly tested IFN genes were concordant across the two primary datasets. Yet the genome-wide effect correlation was only rho=0.026. These observations are not contradictory: transcriptome-wide correlation asks whether thousands of gene effects agree across cohorts that differ in age structure, annotation, processing, covariates and gene universe, whereas the program analysis asks whether a prespecified coherent response retains direction and statistical support. The data support the latter, not a globally shared disease transcriptome. Corrected source-label-independent remapping then failed its prespecified B_ASC calibration criterion, so independent replication remains tied to the broad source-label-defined analogue rather than demonstrating de novo taxonomy transfer."
    )
    edits = [
        (
            "Title claim calibration",
            "TITLE",
            "Distinguish comparative reproducibility from an absolute claim that biological states are unstable.",
            "# Disease-blind reconstruction distinguishes reproducible interferon remodeling from unstable B-cell state assignments in systemic lupus erythematosus",
            "# Disease-blind reconstruction distinguishes reproducible interferon remodeling from less stable B-cell state assignments in systemic lupus erythematosus",
        ),
        (
            "Abstract result and landing calibration",
            "ABSTRACT",
            "Replace equivalence-prone null language and close on the single comparative contribution.",
            old_abstract,
            new_abstract,
        ),
        (
            "Source and QC evidence owner",
            "RESULTS",
            "Point the first source-support claim to its diagnostic owner.",
            "disease effects were restricted to prespecified contrasts with common support.",
            "disease effects were restricted to prespecified contrasts with common support (Supplementary Fig. S1).",
        ),
        (
            "Representation evidence owner",
            "RESULTS",
            "Point representation checks to their first evidence owner.",
            "marker coverage were evaluated before disease fields were joined.",
            "marker coverage were evaluated before disease fields were joined (Supplementary Fig. S2).",
        ),
        (
            "Identity adjudication evidence owner",
            "RESULTS",
            "Point the two-compartment transition claim to its diagnostic owner.",
            "platelet-associated expression retained as a technical overlay.",
            "platelet-associated expression retained as a technical overlay (Supplementary Fig. S3).",
        ),
        (
            "Figure 1 panel ownership",
            "RESULTS",
            "Resolve the broad figure callout to the panels owning the stated metrics.",
            "introduced by rebuilding the representation itself (Fig. 1).",
            "introduced by rebuilding the representation itself (Fig. 1a-d).",
        ),
        (
            "Composition evidence owners",
            "RESULTS",
            "Attach composition and sensitivity claims to main and supplementary evidence owners.",
            "none of the 90 leave-one-sample-out fits generated evidence that reversed the primary interpretation.",
            "none of the 90 leave-one-sample-out fits generated evidence that reversed the primary interpretation (Fig. 2a-d; Supplementary Fig. S4).",
        ),
        (
            "IFN discovery evidence owners",
            "RESULTS",
            "Attach program, gene and robustness claims to their displays.",
            "leading signals included USP18, IFI44L, EPSTI1, IFIT3, MX1, IFI6, OAS2, ISG15 and STAT1.",
            "leading signals included USP18, IFI44L, EPSTI1, IFIT3, MX1, IFI6, OAS2, ISG15 and STAT1 (Fig. 3a-c; Supplementary Fig. S5).",
        ),
        (
            "Program-specificity evidence owner",
            "RESULTS",
            "Expose the panel owning the negative specificity boundary.",
            "only program with consistent support across the prespecified discovery and internal robustness sequence.",
            "only program with consistent support across the prespecified discovery and internal robustness sequence (Fig. 3d).",
        ),
        (
            "External effect evidence owners",
            "RESULTS",
            "Attach external effects and support sensitivities to their displays.",
            "100 cells (effect 0.939; q=4.06 x 10^-6).",
            "100 cells (effect 0.939; q=4.06 x 10^-6) (Fig. 4a,b; Supplementary Fig. S6).",
        ),
        (
            "External gene and influence evidence owner",
            "RESULTS",
            "Attach cross-dataset gene concordance to its display.",
            "all ten IFN genes jointly tested in the primary GSE174188 and childhood GSE135779 analyses were positive in both datasets.",
            "all ten IFN genes jointly tested in the primary GSE174188 and childhood GSE135779 analyses were positive in both datasets (Fig. 4c,d).",
        ),
        (
            "External remapping heading precision",
            "HEADING",
            "Name the source-label-independent sensitivity explicitly.",
            "### Corrected external remapping does not satisfy the prespecified calibration criterion",
            "### Corrected source-label-independent remapping does not satisfy the prespecified calibration criterion",
        ),
        (
            "S10 evidence owner terminology",
            "RESULTS",
            "Use an unambiguous supplementary figure callout.",
            "(Supplementary Table S9 and Fig. S10)",
            "(Supplementary Table S9 and Supplementary Fig. S10)",
        ),
        (
            "Regulator evidence owner",
            "RESULTS",
            "Attach ULM and specificity claims to the panels that own them.",
            "The proliferation specificity comparators did not reproduce a positive globally significant pattern across all three contrasts.",
            "The proliferation specificity comparators did not reproduce a positive globally significant pattern across all three contrasts (Fig. 5a-c).",
        ),
        (
            "Correlation-aware evidence owner",
            "RESULTS",
            "Attach the CAMERA limitation to its detailed display.",
            "not universal significance across methods.",
            "not universal significance across methods (Supplementary Fig. S7).",
        ),
        (
            "Overlap-depletion evidence owner",
            "RESULTS",
            "Attach the broader-interferon coupling boundary to its detailed display.",
            "it remains partly coupled to the broader interferon-response transcriptome.",
            "it remains partly coupled to the broader interferon-response transcriptome (Supplementary Fig. S8).",
        ),
        (
            "Response evidence owner",
            "RESULTS",
            "Attach orthogonal response context to its panels.",
            "No inferential P value was calculated at n=2.",
            "No inferential P value was calculated at n=2 (Fig. 5d,e).",
        ),
        (
            "Discussion opening compression",
            "DISCUSSION",
            "Keep the main interpretive delta while removing repeated metric narration.",
            old_discussion_opening,
            new_discussion_opening,
        ),
        (
            "External-replication discussion compression",
            "DISCUSSION",
            "Preserve the program-versus-transcriptome contrast and calibration boundary with less repetition.",
            old_external_discussion,
            new_external_discussion,
        ),
        (
            "Discussion primary-composition interpretation",
            "DISCUSSION",
            "Avoid treating a non-significant primary contrast as a proven null effect.",
            "is compatible with our secondary positive flare estimate and does not conflict with the null primary comparison in the source-defined managed-SLE group.",
            "is compatible with our secondary positive flare estimate and does not conflict with the primary comparison, which lacked statistical support in the source-defined managed-SLE group.",
        ),
        (
            "Discussion negative-result boundary",
            "DISCUSSION",
            "Describe the primary composition evidence by its supported inferential state.",
            "and the primary composition null should not be displaced by the secondary flare contrast.",
            "and the absence of statistical support in the primary composition contrast should not be displaced by the secondary flare contrast.",
        ),
        (
            "Figure 1 legend scope",
            "LEGEND",
            "Describe the retained analytical scope without implying a validated identity taxonomy.",
            "### Figure 1 | Disease-blind reconstruction defines the permissible identity scope",
            "### Figure 1 | Disease-blind reconstruction defines the retained analysis scope",
        ),
    ]
    text, ledger = apply_edits(text, edits, "Manuscript")
    output = SOURCE_OUTPUT / "Manuscript_scientific_coherence_refreeze_candidate.md"
    output.write_text(text, encoding="utf-8", newline="\n")
    return output, ledger


def build_supplement() -> tuple[Path, list[dict[str, str]]]:
    source = PRIOR_RUN / "sources/Supplementary_Information_scientific_harmonization_candidate.md"
    text = source.read_text(encoding="utf-8")
    old_s9 = (
        "**a,** Observed values and unchanged criteria for the five formal end-to-end two-compartment checks; four passed and minimum state-median Jaccard produced HOLD. **b,** State Jaccard across 20 complete reconstruction replicates shows that the formal failure is localized to B_ASC, while B_CONV remains above the 0.95 criterion. **c,** Counts of sampled cells exchanged across the B_CONV/B_ASC boundary. **d,** Primary B_ASC composition odds ratios and 95% confidence intervals after each observed boundary exchange; the dashed guide marks one and the orange line marks the frozen estimate. **e,** Primary and donor-nonoverlap B_CONV IFN/ISG effects after boundary-cell raw counts were propagated through frozen TMM logCPM and HC3 models; dotted lines mark the frozen effects. All propagation analyses reuse GSE174188 and quantify assignment sensitivity rather than independent replication."
    )
    new_s9 = (
        "**a,** Observed values and prespecified criteria for five end-to-end two-compartment checks; four met their criteria and minimum state-median Jaccard did not. **b,** State Jaccard across 20 complete reconstruction replicates localizes the unmet overlap criterion to B_ASC, while B_CONV remains above 0.95. **c,** Counts of sampled cells exchanged across the B_CONV/B_ASC boundary. **d,** Primary B_ASC composition odds ratios and 95% confidence intervals after each observed boundary exchange; the dashed guide marks one and the orange line marks the frozen estimate. **e,** Primary and donor-nonoverlap B_CONV IFN/ISG effects after boundary-cell raw counts were propagated through frozen TMM logCPM and HC3 models; dotted lines mark the frozen effects. All propagation analyses reuse GSE174188 and quantify assignment sensitivity rather than independent replication."
    )
    edits = [
        (
            "S1 external analogue terminology",
            "TABLE",
            "Use the manuscript's British-English terminology.",
            "Broad conventional-B analog; childhood primary",
            "Broad conventional-B analogue; childhood primary",
        ),
        (
            "S2 composition boundary",
            "TABLE",
            "Avoid treating a non-significant contrast as proof of a null or equivalence.",
            "| Null primary B_ASC relative-abundance result | General B_ASC expansion in SLE |",
            "| Primary B_ASC contrast lacks statistical support | General B_ASC expansion in SLE |",
        ),
        (
            "S2 regulator method ownership",
            "TABLE",
            "Name ULM as the method owning the concordant activity estimate.",
            "| Convergent STAT1/STAT2 target activity | Causal TF activation or direct binding |",
            "| ULM STAT1/STAT2 activity concordant across three contrasts | Causal TF activation or direct binding |",
        ),
        (
            "S3 reader-facing title",
            "TABLE_HEADING",
            "Replace internal freeze vocabulary with the scientific role of the table.",
            "## Supplementary Table S3 | Frozen quantitative anchors",
            "## Supplementary Table S3 | Quantitative anchors and prespecified boundaries",
        ),
        (
            "S3 reader-facing column",
            "TABLE",
            "Remove internal freeze vocabulary from a reader-facing column heading.",
            "| Analysis | Frozen result |",
            "| Analysis | Result |",
        ),
        (
            "S3 end-to-end boundary",
            "TABLE",
            "State the unmet criterion directly instead of exposing workflow status terminology.",
            "| End-to-end identity sensitivity | formal HOLD; minimum mapped ARI 0.930; minimum agreement 0.9988; B_ASC median Jaccard 0.930 below 0.95 criterion |",
            "| End-to-end identity sensitivity | prespecified criterion not met; minimum mapped ARI 0.930; minimum agreement 0.9988; B_ASC median Jaccard 0.930 below 0.95 criterion |",
        ),
        (
            "S9 prior-outcome boundary",
            "TABLE",
            "Describe chronology without internal preregistration jargon.",
            "| Prior outcome exposure | Original sensitivity outcomes were known before correction | Technical correction, not new prospective preregistration |",
            "| Prior outcome exposure | Original sensitivity outcomes were known before correction | Post-outcome correction; not prospective validation |",
        ),
        (
            "S9 evidence boundary",
            "TABLE",
            "Describe evidence ownership rather than publication workflow state.",
            "| Publication boundary | Primary GSE135779 replication remains source-label-defined | Original C9 PASS and effect estimates excluded from supporting evidence |",
            "| Evidence boundary | Primary GSE135779 replication remains source-label-defined | Superseded uncorrected outcomes excluded from supporting evidence |",
        ),
        (
            "S9 figure legend criterion language",
            "LEGEND",
            "Synchronize the legend with the reader-facing source replot.",
            old_s9,
            new_s9,
        ),
        (
            "S10 source-label terminology",
            "FIGURE_HEADING",
            "Match the manuscript's source-label-independent sensitivity terminology.",
            "## Supplementary Figure S10 | Reference calibration limits source-label-agnostic external transfer",
            "## Supplementary Figure S10 | Reference calibration limits source-label-independent external transfer",
        ),
    ]
    text, ledger = apply_edits(text, edits, "Supplementary Information")
    output = SOURCE_OUTPUT / "Supplementary_Information_scientific_coherence_refreeze_candidate.md"
    output.write_text(text, encoding="utf-8", newline="\n")
    return output, ledger


def write_ledger(rows: list[dict[str, str]]) -> Path:
    output = SOURCE_OUTPUT / "SCIENTIFIC_COHERENCE_EDIT_LEDGER.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output


def main() -> None:
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-confirmed exact package changed before scientific refinement")
    if RUN.exists():
        shutil.rmtree(RUN)
    FIGURE_DIR.mkdir(parents=True)
    SOURCE_DIR.mkdir(parents=True)
    SOURCE_OUTPUT.mkdir(parents=True)

    main_assertions, supplementary_assertions = build_all_figures()
    manuscript, manuscript_ledger = build_manuscript()
    supplement, supplement_ledger = build_supplement()
    ledger = write_ledger(manuscript_ledger + supplement_ledger)

    prior.RUN = RUN
    prior.FIGURE_DIR = FIGURE_DIR
    prior.SOURCE_DIR = SOURCE_DIR
    source_status, figure_status = prior.audit_sources_and_figures()

    decisions = [
        ("Main", "Figure 1a", "KEEP", "Retained-scope workflow is scientifically aligned; legend terminology is refined."),
        ("Main", "Figures 1b-d and 2-5", "KEEP", "Distinct evidence ownership and no material visual defect."),
        ("Supplement", "S1-S8", "KEEP", "Each panel retains a nonredundant QC, robustness or sensitivity role."),
        ("Supplement", "S9a,b,d", "MODIFY_SELECTED", "Replace internal PASS/HOLD/null labels with prespecified-criterion and inference language."),
        ("Supplement", "S9c,e", "KEEP", "Boundary exchange and IFN propagation displays remain interpretable."),
        ("Supplement", "S10b,c", "MODIFY_SELECTED", "Replace gate/pass titles with explicit precision and coverage criteria."),
        ("Supplement", "S10a,d", "KEEP", "Normalization and diagnostic-fold roles remain clear."),
    ]
    with (RUN / "01_PANEL_DECISION_MATRIX.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["set", "panel", "decision", "rationale"])
        writer.writerows(decisions)

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SCIENTIFIC_COHERENCE_REFREEZE_BUILT_RENDER_QA_REQUIRED",
        "figure_count": len(figure_status),
        "source_data_count": len(source_status),
        "source_data": source_status,
        "figures": figure_status,
        "selected_figure_changes": [
            "S9 prespecified-criterion terminology",
            "S10 reader-facing calibration criteria",
        ],
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
            "all_new_text_present": True,
        },
        "main_builder_assertions": len(main_assertions),
        "main_builder_assertions_pass": all(row["pass"] for row in main_assertions),
        "supplementary_builder_assertions": len(supplementary_assertions),
        "supplementary_builder_assertions_pass": all(
            row["pass"] for row in supplementary_assertions
        ),
        "external_proof_policy": (
            "External manuscript, supplement, PDFs and ledger were independently audited as proposals. "
            "The final candidate is regenerated from the repository baseline; the external ledger was not reused."
        ),
        "scientific_estimates_changed": False,
        "source_data_changed": False,
        "new_inference_added": False,
        "exact_submission_package_modified": False,
        "exact_submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "00_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({
        "status": status["status"],
        "figures": len(figure_status),
        "source_data": len(source_status),
        "ledger_rows": status["canonical_ledger"]["rows"],
        "package_sha256": status["exact_submission_package_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
