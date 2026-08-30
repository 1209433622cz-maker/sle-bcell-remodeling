#!/usr/bin/env python3
"""Build Gate C8S manuscript, supplement and submission source files."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8S" / "20260821_supplementary_traceability_freeze"
SOURCE = ROOT / "01_manuscript" / "manuscript_v11_genome_medicine_gateC8R_2026-08-20.md"
MANUSCRIPT = ROOT / "01_manuscript" / "manuscript_v12_genome_medicine_gateC8S_2026-08-21.md"
SUPPLEMENT = ROOT / "01_manuscript" / "supplementary_information_v3_gateC8S_2026-08-21.md"
SUBMISSION = ROOT / "04_submission"
CORRELATION_CSV = ROOT / "phase17_v7" / "gateC8R" / "20260820_pre_submission_repair" / "03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv"
OLD_TITLE = "Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence in systemic lupus erythematosus B cells"
TITLE = "Disease-blind single-cell reconstruction separates unstable B-cell states from reproducible interferon remodeling in systemic lupus erythematosus"


def words(text: str) -> int:
    clean = re.sub(r"[`*_#|\[\]]", " ", text)
    return len(re.findall(r"\b[\w'-]+\b", clean))


def section(text: str, start: str, end: str | None) -> str:
    begin = text.index(start) + len(start)
    finish = text.index(end, begin) if end else len(text)
    return text[begin:finish].strip()


def replace_section(text: str, start: str, end: str, body: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise RuntimeError(f"Section boundary is not unique: {start!r} -> {end!r}")
    begin = text.index(start) + len(start)
    finish = text.index(end, begin)
    return text[:begin] + "\n\n" + body.strip() + "\n\n" + text[finish:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {text.count(old)}")
    return text.replace(old, new, 1)


def build_manuscript() -> tuple[str, int]:
    manuscript = SOURCE.read_text(encoding="utf-8-sig")
    source_placeholders = manuscript.count("[[")
    manuscript = replace_once(manuscript, f"# {OLD_TITLE}", f"# {TITLE}", "manuscript title")
    manuscript = replace_once(
        manuscript,
        "**Version:** Gate C8R Genome Medicine pre-submission repair v11",
        "**Version:** Gate C8S supplementary evidence and traceability freeze v12, 21 August 2026",
        "version line",
    )
    manuscript = replace_once(manuscript, "**Date:** 20 August 2026", "**Date:** 21 August 2026", "manuscript date")

    statistical_methods = """### Statistical analysis and multiplicity

This retrospective secondary analysis used all eligible public biological units after frozen quality-control, support and mapping rules; no prospective sample-size or power calculation was performed. Exact analysis sizes are reported with the corresponding results and figure panels. Unless explicitly identified as directional, hypothesis tests were two-sided and intervals were 95% confidence intervals. The primary B_ASC composition model used a beta-binomial Wald test with Benjamini-Hochberg (BH) correction across the three frozen base contrasts; covariance and two-part models were sensitivity analyses with nominal P values. Gene-level robust edgeR quasi-likelihood tests used BH correction across `filterByExpr`-tested genes within each contrast. Frozen-program linear models used HC3 covariance and BH correction across the four prespecified programs within each analysis. Ranked program-arm CAMERA results were corrected within each frozen analysis.

The CollecTRI activity analysis used two-sided target-slope tests and one global BH family across eight regulators and three confirmatory contrasts (24 tests). The post-audit STAT1/STAT2 CAMERA and FRY analyses were prespecified positive-direction sensitivity tests with separate BH families of six tests for each method. M5911 used a positive-direction weighted preranked test with 10,000 deterministic gene-label permutations per contrast and a descriptive BH correction across three contrasts. The paired GSE23307 experiment had two donors and no inferential P value. Statistical significance was defined as q<0.05 only within the stated confirmatory family; nominal and descriptive results were not promoted to confirmatory evidence. The complete family map, full gene-level tables and sanitized design matrices are provided in Additional file 4."""
    manuscript = replace_once(
        manuscript,
        "### Generative AI assistance",
        statistical_methods + "\n\n### Generative AI assistance",
        "generative-AI heading",
    )

    old_discussion = section(manuscript, "## Discussion", "## Conclusions")
    precision_paragraph = """From a precision-medicine perspective, the continuous B_CONV IFN/ISG score could eventually contribute to molecular stratification or pharmacodynamic monitoring, particularly where bulk or compositional readouts obscure a cell-intrinsic response. The present study does not establish a predictive biomarker, treatment-selection rule, clinical cutoff or patient benefit. Those uses require prospective treatment-annotated cohorts, longitudinal sampling, assay calibration and prespecified evaluation of discrimination and clinical utility."""
    limitation_anchor = "The analysis has limitations."
    if old_discussion.count(limitation_anchor) != 1:
        raise RuntimeError("Discussion limitation anchor is not unique")
    new_discussion = old_discussion.replace(limitation_anchor, precision_paragraph + "\n\n" + limitation_anchor, 1)
    manuscript = replace_section(manuscript, "## Discussion", "## Conclusions", new_discussion)

    manuscript = replace_once(
        manuscript,
        "Analysis scripts, machine-readable decisions and compact derived source-data tables are available in the project repository [17], maintained in the Gate C8R source tree and will be frozen at the final public release commit.",
        "Analysis scripts, machine-readable decisions and derived source-data tables are available in the public project repository [17]. Gate C8S is the current canonical analysis state; an open-source licence and immutable archive DOI remain required for the final citable release.",
        "repository availability statement",
    )
    manuscript = replace_once(
        manuscript,
        "**Additional file 3 (.zip):** Correlation-aware regulator sensitivity. Six STAT1/STAT2 CAMERA and FRY tests, the qualified decision record and a SHA-256 manifest.",
        "**Additional file 3 (.zip):** Correlation-aware regulator sensitivity. Six STAT1/STAT2 CAMERA and FRY tests, the qualified decision record and a SHA-256 manifest.\n\n**Additional file 4 (.zip):** Full statistical results. Complete gene-level results for 12 frozen model branches, composition and program tables, regulator and orthogonal results, sanitized design matrices, the statistical-family map and SHA-256 provenance manifests.",
        "additional-file list",
    )

    legends = section(manuscript, "## Figure legends", "## References")
    legends = legends.replace(
        "IFIT1 and IFIT2 were filtered from the primary gene-level test, and IFIT1 was filtered from the donor-nonoverlap test; these absences are marked rather than imputed.",
        "A dagger marks genes not tested at gene level in either contrast; a double dagger marks genes not tested in the primary contrast. Filtered values are absent rather than zero or imputed.",
    )
    manuscript = replace_section(manuscript, "## Figure legends", "## References", legends)
    manuscript = manuscript.replace("Accessed 20 Aug 2026.", "Accessed 21 Aug 2026.")

    if manuscript.count("[[") != source_placeholders:
        raise RuntimeError("Author-controlled placeholder count changed during C8S source build")
    abstract_words = words(section(manuscript, "## Abstract", "## Keywords"))
    if abstract_words > 350:
        raise RuntimeError("Structured abstract exceeds 350 words")
    references = [int(value) for value in re.findall(r"^(\d+)\.\s", section(manuscript, "## References", None), flags=re.M)]
    if references != list(range(1, 31)):
        raise RuntimeError("Reference numbering is not exactly 1-30")
    required = [
        TITLE,
        "### Statistical analysis and multiplicity",
        "one global BH family across eight regulators and three confirmatory contrasts (24 tests)",
        "does not establish a predictive biomarker",
        "**Additional file 4 (.zip):** Full statistical results.",
        "CAMERA supported five of six tests after correction",
        "Spearman rho=0.026",
    ]
    missing = [token for token in required if token not in manuscript]
    if missing:
        raise RuntimeError(f"Missing C8S manuscript anchors: {missing}")
    return manuscript, abstract_words


def correlation_table() -> str:
    with CORRELATION_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 6:
        raise RuntimeError(f"Expected six correlation-aware rows, found {len(rows)}")
    labels = {
        "gse174188_primary": "GSE174188 primary",
        "gse174188_internal_nonoverlap": "GSE174188 donor-nonoverlap",
        "gse135779_childhood": "GSE135779 childhood",
    }
    return "\n".join(
        "| {contrast} | {regulator} | {targets} | {corr:.4f} | {camera:.4g} | {fry:.4g} |".format(
            contrast=labels[row["contrast"]],
            regulator=row["regulator"],
            targets=row["matched_signed_targets"],
            corr=float(row["camera_inter_gene_correlation"]),
            camera=float(row["camera_q_core6"]),
            fry=float(row["fry_q_core6"]),
        )
        for row in rows
    )


def build_supplement() -> str:
    corr = correlation_table()
    return f"""# Supplementary information

## {TITLE}

**Version:** Gate C8S, 21 August 2026

**Authors:** Zhi Chen and Teng Qi

## Supplementary overview

Gate C8S freezes reviewer-facing supplementary evidence and statistical traceability without changing upstream estimates. It adds seven supplementary figures reconstructed from frozen Gate C2B1-C8R outputs, corrected Figure 5 machine-readable panel labels, a unified multiplicity map and a complete statistical-results archive. Every main and supplementary panel has a machine-readable source table and hard data assertions.

## Supplementary Methods 1 | Gate governance and outcome protection

The workflow used sequential gates for source integrity, hard quality control, disease-blind identity reconstruction, sample-level composition, within-compartment pseudobulk analysis, independent validation and external regulatory evidence. Protected disease fields were separated during identity reconstruction. Real outcome effects were unlocked only after the relevant input, mapping, contrast and statistical-engine contracts had been recorded. Each gate retained a machine-readable decision and SHA-256 integrity manifest.

## Supplementary Methods 2 | Identity stability boundary

The initial five-state model failed the prespecified resampling thresholds. Repair analyses evaluated four-, three- and two-level mappings without consulting disease labels. Only the broad B_CONV/B_ASC solution met all stability criteria across 20 resampling runs. Fine naive-memory structure was therefore retained as continuous transcriptional context rather than a hard publication subtype. This negative boundary is part of the result, not a quality-control artifact to be removed.

## Supplementary Methods 3 | Biological units and contrast hierarchy

GSE174188 composition and expression analyses used sample-by-processing-cohort strata; donor-aware sensitivities addressed repeated samples. GSE135779 used donors as biological units. Primary, internal, donor-nonoverlap, secondary flare, childhood, combined and adult contrasts remained separate. No bridge stratum was used to manufacture a pooled disease coefficient, and internal GSE174188 estimates were not described as independent validation.

## Supplementary Methods 4 | Robustness and specificity

Prespecified sensitivity analyses varied minimum cell support, excluded residual-doublet-risk cells, deleted samples or donors one at a time, omitted source labels and compared platelet/ambient, ASC/UPR and pan-B control programs. The TF-target family used one global correction across 24 tests. STAT1 and STAT2 core results underwent leave-one-target and deterministic 80% target-resampling analyses. The GSE23307 two-donor perturbation remained descriptive.

## Supplementary Methods 5 | Correlation-aware regulator sensitivity

The sensitivity reused frozen STAT1/STAT2 signed targets, model matrices, contrasts and tested-gene backgrounds. Voom precision weights fed CAMERA with residual-estimated inter-gene correlation and FRY directional rotation tests. BH adjustment was applied across six core tests within each method. Exact agreement with frozen ULM matched-target counts was mandatory. This was post-audit robustness testing and not independent replication.

## Supplementary Table S1 | Dataset roles and inferential units

| Resource | Role | Biological unit | Active scope |
|---|---|---|---|
| GSE174188 | Discovery and internal validation | Sample-cohort stratum; donor sensitivities | Disease-blind B_CONV/B_ASC identity, composition and B_CONV transcription |
| GSE135779 | Independent SLE validation | Donor | Broad conventional-B analog; childhood primary |
| CollecTRI/OmniPath | Curated regulator prior | Ranked genes within contrast | Prespecified eight-regulator, three-contrast family |
| MSigDB M5911 | Orthogonal response prior | Ranked genes within contrast | Hallmark interferon-alpha response enrichment |
| GSE23307 | Orthogonal perturbation support | Paired profile within donor | Descriptive IFN-beta response, n=2 donors |

## Supplementary Table S2 | Claim boundaries

| Supported | Not supported |
|---|---|
| Broad disease-blind B_CONV and B_ASC identity | Stable hard naive, memory or atypical subtypes |
| Null primary B_ASC relative-abundance result | General B_ASC expansion in SLE |
| Replicated IFN/ISG remodeling within B_CONV | Genome-wide shared disease transcriptome |
| Convergent STAT1/STAT2 target activity | Causal TF activation or direct binding |
| IFN-centred response evidence | A unique initiating IFN ligand in SLE |

## Supplementary Table S3 | Frozen quantitative anchors

| Analysis | Frozen result |
|---|---|
| Identity stability | minimum mapped ARI 0.990; minimum agreement 0.9998; minimum median Jaccard 0.991 |
| Primary B_ASC composition | 43 controls and 47 managed SLE; odds ratio 0.947; 95% CI 0.636-1.410; P=0.787 |
| GSE174188 primary IFN/ISG | effect 0.837; 95% CI 0.525-1.148; q=2.98 x 10^-6 |
| GSE174188 donor-nonoverlap IFN/ISG | effect 1.086; q=3.61 x 10^-4 |
| GSE135779 childhood IFN/ISG | effect 1.042; 95% CI 0.681-1.402; q=2.98 x 10^-6 |
| Cross-dataset genome-wide agreement | 4,410 genes; Spearman rho=0.026 |
| M5911 enrichment | NES 3.187, 3.050 and 3.527 |
| GSE23307 perturbation | donor effects 3.294 and 3.666; 12/12 genes positive in each |

## Supplementary Table S4 | Correlation-aware core-regulator sensitivity

| Contrast | Regulator | Matched targets | Inter-gene correlation | CAMERA BH q | FRY BH q |
|---|---|---:|---:|---:|---:|
{corr}

CAMERA and FRY directions were positive in all six tests. CAMERA passed BH correction in five of six; the explicit exception was GSE174188 primary STAT2 (q=0.1355). FRY passed BH correction in all six.

## Supplementary Table S5 | Main-figure source-data map

| Figure | Frozen gate | Machine-readable source |
|---|---|---|
| Figure 1 | C2B4 identity freeze; C8S annotation repair | Figure1_source_data.csv |
| Figure 2 | C3A composition decision; asserted 43/47 groups | Figure2_source_data.csv |
| Figure 3 | C4B transcription; explicit filtered-gene symbols | Figure3_source_data.csv |
| Figure 4 | C5B independent validation | Figure4_source_data.csv |
| Figure 5 | C6B regulatory evidence; corrected D/E source labels | Figure5_source_data.csv |

## Supplementary Table S6 | Reproducibility contract

| Component | Frozen record |
|---|---|
| Main-panel assertions | `phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/02_PANEL_DATA_ASSERTIONS.json` |
| Supplementary-panel assertions | `phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/03_SUPPLEMENTARY_PANEL_DATA_ASSERTIONS.json` |
| Correlation-aware sensitivity | `phase17_v7/gateC8R/20260820_pre_submission_repair/03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv` |
| Full statistical archive | `Additional_file_4_Full_Statistical_Results_GateC8S.zip` |
| Active manuscript source | `01_manuscript/manuscript_v12_genome_medicine_gateC8S_2026-08-21.md` |
| Public repository | `https://github.com/1209433622cz-maker/sle-bcell-remodeling` |
| Immutable release | Open-source licence and archive DOI remain author actions before portal submission |

## Supplementary Table S7 | Statistical tests and multiplicity families

| Result family | Biological unit | Test or estimator | Sidedness | Multiplicity | Role |
|---|---|---|---|---|---|
| B_ASC composition | Sample-cohort stratum | Beta-binomial Wald | Two-sided | BH across three frozen base contrasts | Primary composition inference |
| Gene-level expression | Donor/sample pseudobulk | edgeR robust quasi-likelihood F | Two-sided | BH within tested genes per contrast | Gene-level inference |
| Four frozen programs | Donor/sample pseudobulk | OLS with HC3 | Two-sided | BH across four programs per analysis | Program inference |
| TF-target activity | Ranked gene statistics | Signed-target slope t test | Two-sided | Global BH across 24 tests | Confirmatory regulatory evidence |
| STAT1/STAT2 sensitivity | Ranked gene statistics | CAMERA and FRY | Positive-direction | Separate BH families of six per method | Correlation-aware sensitivity |
| M5911 | Ranked gene statistics | 10,000-permutation preranked test | Positive-direction | Descriptive BH across three contrasts | Orthogonal support |
| GSE23307 | Paired donor | Mean paired log2(x+1) effect | Not tested | None; n=2 | Descriptive perturbation |

## Supplementary Table S8 | Full statistical-results archive map

| Directory | Contents | Files |
|---|---|---:|
| gene_level_results | Complete filterByExpr gene results for GSE174188 and GSE135779 branches | 12 |
| sanitized_design_matrices | Direct-identifier-free analysis designs | 12 |
| composition | Frozen coefficients, contrasts, predictions, sensitivities, leave-one-out and diagnostics | 8 |
| transcription | Program, ranked-list, influence and concordance results | 18 |
| regulatory_and_orthogonal | ULM, target influence, CAMERA/FRY, M5911 and GSE23307 summaries | 9 |
| statistical_framework | Machine-readable test and multiplicity map | 1 |

## Supplementary Figure S1 | Source integrity and hard-quality-control diagnostics

**a,** Hard-QC failure fractions by processing cohort and disease group. **b,** Residual-risk call fraction versus cells per library, coloured by the library median score. **c,** Percent and exact number of retained risk-negative cells and sensitivity-only residual-risk calls among 150,402 hard-QC B-lineage cells. **d,** Median, 95th-percentile and threshold residual-risk scores for all 88 libraries.

[[SUPPLEMENTARY_FIGURE:S1]]

## Supplementary Figure S2 | Representation and bridge diagnostics

**a,** Same-group neighbourhood concentration before and after Harmony adjustment. **b,** Cross-cohort bridge-pair cosine-distance distributions. **c,** Disease-blind branch concordance across Leiden resolutions for residual-risk-negative and strong-ISG-excluded branches; the vertical guide marks the primary resolution. **d,** Biological marker-module localization across the five fine clusters considered before stability adjudication.

[[SUPPLEMENTARY_FIGURE:S2]]

## Supplementary Figure S3 | Disease-blind identity adjudication

**a,** Median and worst-case mapped ARI for five-, four-, three- and two-level policies across resamples. **b,** Median and minimum cluster Jaccard values show localization of failure to fine-state membership. **c,** Mean transition matrix from original resolution-0.4 clusters to mapped reference clusters. **d,** Minimum-to-median Jaccard intervals for the final B_CONV and B_ASC states across 20 disease-blind resamples.

[[SUPPLEMENTARY_FIGURE:S3]]

## Supplementary Figure S4 | Composition-model diagnostics

**a,** Total and zero-ASC sample-cohort strata in the three base contrasts. **b,** Primary B_ASC odds ratios under support, explicit non-B and residual-risk policies using observed-information covariance (blue) and HC1 covariance (red). **c,** Firth-logistic ASC-presence sensitivity. **d,** Positive-only abundance sensitivity using HC3 uncertainty. The two-part models are sensitivity analyses and do not replace the frozen beta-binomial primary model.

[[SUPPLEMENTARY_FIGURE:S4]]

## Supplementary Figure S5 | Pseudobulk and ranked-list diagnostics

**a,** Numbers of filterByExpr-tested and BH-significant genes across seven GSE174188 branches. **b,** Common and median tagwise edgeR dispersions. **c,** Mitochondrial, ribosomal, haemoglobin and immunoglobulin fractions among increasingly long primary ranked lists. **d,** IFN/ISG effects and 95% confidence intervals across frozen branches.

[[SUPPLEMENTARY_FIGURE:S5]]

## Supplementary Figure S6 | Independent-validation diagnostics

**a,** Control and SLE donor counts across the five GSE135779 models. **b,** Four-program childhood estimates. **c,** Childhood IFN/ISG estimates after omission of each source B-cell label. **d,** Full childhood program effects and ranges across donor-deletion analyses.

[[SUPPLEMENTARY_FIGURE:S6]]

## Supplementary Figure S7 | Correlation-aware regulator sensitivity

**a,** CAMERA and FRY six-test BH concordance for STAT1 and STAT2. Dashed guides indicate q=0.05. **b,** CAMERA residual-estimated inter-gene correlations. **c,** Exact CAMERA and FRY BH q values. **d,** Matched signed-target counts, which equal the frozen ULM family (STAT1: 98, 129 and 161; STAT2: 14, 19 and 20).

[[SUPPLEMENTARY_FIGURE:S7]]

## Supplementary note on superseded artifacts

Earlier manuscripts and packages remain for provenance but are not active submission sources. Gate C8R repaired the Figure 2a group mapping and added correlation-aware sensitivity. Gate C8S additionally corrects the machine-readable Figure 5 source-data panel assignment: M5911 rows are panel d and GSE23307 donor rows are panel e. No plotted value or upstream estimate changed. Previous fine hard-subtype and untransformed GSE23307 artifacts remain superseded and excluded from active claims.
"""


def build_auxiliary_sources() -> dict[str, Path]:
    title_sentence = f'Please consider our Research article, "{OLD_TITLE}", for publication in Genome Medicine.'
    cover = (SUBMISSION / "cover_letter_genome_medicine_gateC8R_AUTHOR_COMPLETION_REQUIRED_2026-08-20.md").read_text(encoding="utf-8")
    cover = replace_once(cover, title_sentence, f'Please consider our Research article, "{TITLE}", for publication in Genome Medicine.', "cover title")
    cover = cover.replace("Gate C8R", "Gate C8S")
    cover = cover.replace("20 August 2026", "21 August 2026")
    cover = cover.replace(
        "Teng Qi\nSchool of Medicine\nThe Chinese University of Hong Kong, Shenzhen\nMED Start-up Building, 2001 Longxiang Boulevard\nLonggang District, Shenzhen 518172, China\ntengqi@link.cuhk.edu.cn",
        "Teng Qi\n\nSchool of Medicine, The Chinese University of Hong Kong, Shenzhen\n\nMED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China\n\nEmail: tengqi@link.cuhk.edu.cn",
    )
    cover = cover.replace("Editors\nGenome Medicine", "Editors, Genome Medicine")
    cover = replace_once(
        cover,
        "All datasets are public and are cited by accession. Scripts, machine-readable decisions, figure source data and integrity manifests are versioned in the accompanying repository.",
        "All datasets are public and are cited by accession. Scripts, machine-readable decisions, figure source data and integrity manifests are versioned in the accompanying repository. The submission includes five 600-dpi main figures, seven supplementary figures, machine-readable source data, a complete statistical-results archive, supplementary information and a separate six-test regulator-sensitivity attachment.",
        "cover package statement",
    )
    cover_path = SUBMISSION / "cover_letter_genome_medicine_gateC8S_AUTHOR_COMPLETION_REQUIRED_2026-08-21.md"
    cover_path.write_text(cover, encoding="utf-8", newline="\n")

    form = (SUBMISSION / "author_completion_form_gateC8R_2026-08-20.md").read_text(encoding="utf-8")
    form = form.replace("Gate C8R", "Gate C8S")
    form_path = SUBMISSION / "author_completion_form_gateC8S_2026-08-21.md"
    form_path.write_text(form, encoding="utf-8", newline="\n")

    target = (SUBMISSION / "journal_target_decision_gateC8R_2026-08-20.md").read_text(encoding="utf-8")
    target = target.replace("Gate C8R", "Gate C8S")
    old_update = "The Figure 2a group-map defect has been repaired with exact panel-data assertions, the five-figure visual system has been harmonized, the literature position has been expanded to 30 references and STAT1/STAT2 now has a correlation-aware sensitivity. The reach ceiling remains limited by the absence of matched patient perturbation, direct binding and prospective clinical validation."
    new_update = "Gate C8S adds seven reviewer-facing supplementary figures, corrected Figure 5 source-data labels, a unified statistical/multiplicity section and a deterministic complete-results archive with 12 full gene-level branches and 12 sanitized design matrices. The scientific evidence ceiling is unchanged: matched patient perturbation, direct binding and prospective clinical validation are still absent. Genome Medicine remains the best-fit first submission; a higher-risk upper-Q1 route would require new experimental or prospective evidence rather than more retrospective polishing."
    target = replace_once(target, old_update, new_update, "target evidence update")
    target_path = SUBMISSION / "journal_target_decision_gateC8S_2026-08-21.md"
    target_path.write_text(target, encoding="utf-8", newline="\n")

    checklist = (SUBMISSION / "reporting_checklist_gateC8R_2026-08-20.md").read_text(encoding="utf-8")
    checklist = checklist.replace("Gate C8R", "Gate C8S")
    checklist = replace_once(
        checklist,
        "- [x] Correlation-aware regulator-sensitivity ZIP and checksum manifest.",
        "- [x] Correlation-aware regulator-sensitivity ZIP and checksum manifest.\n- [x] Seven supplementary figures with machine-readable source data and panel assertions.\n- [x] Full statistical-results ZIP with 12 complete gene-level branches, 12 sanitized design matrices and SHA-256 manifests.\n- [x] Unified statistical-test and multiplicity map in the manuscript and Supplementary Table S7.",
        "checklist evidence files",
    )
    checklist_path = SUBMISSION / "reporting_checklist_gateC8S_2026-08-21.md"
    checklist_path.write_text(checklist, encoding="utf-8", newline="\n")
    return {"cover": cover_path, "author_form": form_path, "target": target_path, "checklist": checklist_path}


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manuscript, abstract_words = build_manuscript()
    supplement = build_supplement()
    MANUSCRIPT.write_text(manuscript, encoding="utf-8", newline="\n")
    SUPPLEMENT.write_text(supplement, encoding="utf-8", newline="\n")
    auxiliary = build_auxiliary_sources()
    status = {
        "created_at": "2026-08-21",
        "status": "PASS_C8S_SUBMISSION_SOURCES_BUILT",
        "manuscript": MANUSCRIPT.relative_to(ROOT).as_posix(),
        "supplement": SUPPLEMENT.relative_to(ROOT).as_posix(),
        "auxiliary_sources": {key: path.relative_to(ROOT).as_posix() for key, path in auxiliary.items()},
        "abstract_words": abstract_words,
        "manuscript_words": words(manuscript),
        "reference_count": 30,
        "main_figures": 5,
        "supplementary_figures": 7,
        "supplementary_tables": 8,
        "author_controlled_placeholders": manuscript.count("[[") + auxiliary["cover"].read_text(encoding="utf-8").count("[["),
        "full_statistical_archive_declared": True,
        "figure5_source_panel_mapping": {"d": "M5911", "e": "GSE23307"},
    }
    (RUN_DIR / "06_GATE_C8S_SOURCE_BUILD_STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
