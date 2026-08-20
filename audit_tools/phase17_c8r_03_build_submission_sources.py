#!/usr/bin/env python3
"""Build Gate C8R manuscript and submission sources from the frozen Gate C8 draft."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8R" / "20260820_pre_submission_repair"
SOURCE = ROOT / "01_manuscript" / "manuscript_v10_genome_medicine_submission_2026-08-20.md"
MANUSCRIPT = ROOT / "01_manuscript" / "manuscript_v11_genome_medicine_gateC8R_2026-08-20.md"
SUPPLEMENT = ROOT / "01_manuscript" / "supplementary_information_v2_gateC8R_2026-08-20.md"
SUBMISSION = ROOT / "04_submission"
CORRELATION_CSV = RUN_DIR / "03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv"
REFERENCE_MD = RUN_DIR / "references" / "references_gateC8R_vancouver.md"


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


def checked_references() -> str:
    records: dict[int, str] = {}
    for line in REFERENCE_MD.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(\d+)\.\s+(.+)$", line.strip())
        if match:
            records[int(match.group(1))] = match.group(2)
    records.update(
        {
            14: "National Center for Biotechnology Information. Gene Expression Omnibus series GSE174188. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188. Accessed 20 Aug 2026.",
            15: "National Center for Biotechnology Information. Gene Expression Omnibus series GSE135779. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779. Accessed 20 Aug 2026.",
            16: "National Center for Biotechnology Information. Gene Expression Omnibus series GSE23307. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE23307. Accessed 20 Aug 2026.",
            17: "SLE B-cell remodeling analysis repository. GitHub. https://github.com/1209433622cz-maker/sle-bcell-remodeling. Accessed 20 Aug 2026.",
        }
    )
    missing = [number for number in range(1, 31) if number not in records]
    if missing:
        raise RuntimeError(f"Missing reference numbers: {missing}")
    return "\n".join(f"{number}. {records[number]}" for number in range(1, 31))


def build_manuscript() -> tuple[str, int]:
    manuscript = SOURCE.read_text(encoding="utf-8-sig")
    source_placeholders = manuscript.count("[[")
    manuscript = replace_once(
        manuscript,
        "**Version:** Gate C8 Genome Medicine submission draft v10",
        "**Version:** Gate C8R Genome Medicine pre-submission repair v11",
        "version line",
    )

    abstract = """**Background:** SLE alters both the abundance and transcriptional state of peripheral B cells, but these layers can be conflated by outcome-informed annotation, cell-level inference and technically imbalanced cohorts.

**Methods:** We performed a donor- and cohort-resolved reanalysis of public single-cell RNA-sequencing data. B-lineage identity was reconstructed without disease labels in GSE174188 before sample-level composition and sample-by-compartment pseudobulk testing. A frozen program was evaluated in independent GSE135779, followed by a prespecified 24-test CollecTRI family, correlation-aware STAT1/STAT2 sensitivity tests, MSigDB M5911 enrichment and paired IFN-beta perturbation profiles from GSE23307.

**Results:** Among 150,402 quality-controlled GSE174188 B-lineage cells, resampling supported broad conventional-B (B_CONV) and antibody-secreting-cell (B_ASC) compartments but not stable hard naive-memory subtypes. Primary B_ASC relative abundance was not associated with SLE (odds ratio 0.947, 95% confidence interval 0.636-1.410; P=0.787). Within B_CONV, the prespecified IFN/ISG program increased in the primary contrast (effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6), a donor-nonoverlap internal contrast (effect 1.086; q=3.61 x 10^-4) and independent GSE135779 childhood donors (11 controls and 32 SLE; effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). All ten jointly tested IFN genes were positive despite low genome-wide agreement (Spearman rho=0.026). STAT1 and STAT2 target activities were positive and globally significant in all three contrasts under the primary ULM analysis. Correlation-aware CAMERA retained the positive direction in all six core tests and BH significance in five; FRY retained direction and BH significance in all six. M5911 was enriched in all contrasts, and IFN-beta exposure increased all 12 frozen genes in each of two healthy-donor profiles.

**Conclusions:** SLE shows independently replicated IFN remodeling within a disease-blind broad conventional-B compartment, with convergent but observational regulatory evidence. The results do not establish a discrete subtype, causal regulator or unique upstream stimulus."""
    if words(abstract) > 350:
        raise RuntimeError(f"Structured abstract exceeds 350 words: {words(abstract)}")
    manuscript = replace_section(manuscript, "## Abstract", "## Keywords", abstract)

    background = """Systemic lupus erythematosus (SLE) is a heterogeneous autoimmune disease involving loss of B-cell tolerance, autoantibody production and sustained innate immune activation. Peripheral-blood single-cell studies have described changes in naive, memory, double-negative, CD11c-positive and antibody-secreting B-cell populations together with prominent interferon responses [1,2,22,24]. Tissue single-cell data and B-cell-focused experiments further connect interferon-responsive states with local inflammation, B-cell activation and plasma-cell differentiation [21,25,30].

Neither an interferon signature nor plasmablast biology is novel in SLE. Longitudinal paediatric immunomonitoring linked a plasmablast signature to disease activity [20], modular adult studies resolved heterogeneous interferon activation thresholds [23], and a recent deep-phenotyping study found that a high plasmablast-to-memory ratio marked a subgroup enriched for higher activity and Sm/RNP autoantibodies [19]. Large transcriptomic analyses likewise identify multiple molecular endotypes that are not uniformly represented across datasets [18]. These findings make cohort structure and disease context central to interpretation: a null primary composition estimate in managed SLE need not contradict plasmablast expansion in clinically enriched subgroups.

Single-cell disease studies are particularly vulnerable to pseudoreplication when cells, rather than donors or biological samples, are treated as independent units [3,4]. Composition introduces an additional constraint because an increase in one compartment changes the observed fractions of all others [5]. Public SLE resources also distribute samples across processing cohorts, include repeated donors and provide uneven disease-group support within technical strata. Outcome-informed cluster labels or pooled cell-level tests can therefore combine biology with design structure.

We addressed these problems through a staged secondary analysis. Raw-count integrity, metadata hierarchy and disease-by-cohort support were audited first. B-lineage identity was reconstructed while protected disease fields remained separate. Only after a disease-blind identity model was frozen were sample-level composition and within-compartment transcription tested. The primary expression result was then carried into independent GSE135779 under a pre-effect mapping and analysis contract.

The intended advance is therefore not rediscovery of interferon activity in SLE. We ask which biological layer remains defensible after disease-blind state definition, sample- or donor-level inference, donor-nonoverlap internal testing, independent-cohort validation and external regulatory and perturbational checks. This design distinguishes a reproducible within-compartment process from unstable subtype labels, cohort-specific abundance effects and causal claims that the available observational data cannot support."""
    manuscript = replace_section(manuscript, "## Background", "## Methods", background)

    sensitivity_methods = """### Correlation-aware STAT1/STAT2 sensitivity

Because genes within a regulon are correlated, the primary rank-based ULM results were supplemented by a post-audit sensitivity analysis that did not alter the frozen regulators, signed CollecTRI targets, contrasts, model matrices or `filterByExpr` backgrounds. Pseudobulk counts were collapsed to gene symbols and transformed with voom precision weights [28,29]. Expression rows for inhibitory targets were sign-reversed so that positive set direction retained the frozen signed-regulon interpretation. For STAT1 and STAT2 in each of the three confirmatory contrasts, CAMERA estimated inter-gene correlation from model residuals and performed a competitive rank test [26], while FRY supplied a rotation-based directional test [27]. Benjamini-Hochberg adjustment was applied separately across the six core regulator-contrast tests for each method. Target counts were required to match the frozen ULM analysis exactly; no target, regulator, contrast or background was reselected after inspecting the sensitivity results."""
    manuscript = replace_once(
        manuscript,
        "### Orthogonal interferon-response analyses",
        sensitivity_methods + "\n\n### Orthogonal interferon-response analyses",
        "orthogonal-analysis heading",
    )

    regulator_result = """STAT1 and STAT2 activity estimates were positive and globally significant in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. At least three of the four IFN-centred regulators were positive in every contrast, with no globally significant opposite-direction IFN regulator. The proliferation controls did not reproduce a positive globally significant pattern across all three contrasts. Every leave-one-target estimate for the core STAT1 and STAT2 models retained the positive direction, and each core model remained positive in all 100 deterministic 80%-target resamples. These diagnostics argue against a result driven by one target gene or a small target subset.

The correlation-aware analysis reproduced the exact frozen matched-target counts for all six core tests (STAT1: 98, 129 and 161; STAT2: 14, 19 and 20). CAMERA retained the expected positive direction in six of six tests and passed the six-test BH threshold in five. The exception was discovery-cohort STAT2 (estimated inter-gene correlation 0.1225; CAMERA q=0.1355), for which FRY remained positive and significant (q=4.91 x 10^-5). FRY was positive and BH-significant in all six core tests. Thus, the sensitivity supports cross-contrast convergence while explicitly precluding a claim that every core test was significant under CAMERA."""
    old_regulator_result = """STAT1 and STAT2 activity estimates were positive and globally significant in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. At least three of the four IFN-centred regulators were positive in every contrast, with no globally significant opposite-direction IFN regulator. The proliferation controls did not reproduce a positive globally significant pattern across all three contrasts. Every leave-one-target estimate for the core STAT1 and STAT2 models retained the positive direction, and each core model remained positive in all 100 deterministic 80%-target resamples. These diagnostics argue against a result driven by one target gene or a small target subset."""
    manuscript = replace_once(manuscript, old_regulator_result, regulator_result, "regulator result")

    discussion = """This study identifies a reproducible level of SLE B-cell biology by separating identity, composition and transcription before testing disease effects. Fine-grained hard B-cell states were not stable under the prespecified disease-blind resampling contract, and the repaired model deliberately stopped at two broad compartments. Within that permissible scope, primary `B_ASC` relative abundance did not differ between managed SLE and controls. The central result instead arose within `B_CONV`: a frozen IFN/ISG program was supported in the primary GSE174188 contrast, an internal donor-nonoverlap contrast and independent GSE135779.

This result refines, rather than challenges, established SLE interferon biology. Prior studies show IFN heterogeneity across molecular endotypes [18,20,23], link activated B-cell and plasmablast phenotypes to specific disease contexts [19,22,24], and demonstrate that several interferon classes can promote B-cell activation or plasma-cell differentiation [25,30]. In particular, the reported plasmablast expansion in patients with higher activity and Sm/RNP autoantibodies [19] is compatible with our secondary positive flare estimate and our null primary managed-SLE estimate. The contribution here is the identification of the layer that survives a disease-blind, biological-replicate-aware and cross-cohort validation sequence, not a claim that interferon involvement itself is newly discovered.

The low cross-dataset genome-wide correlation is not a contradiction of the frozen program result. The two accessions differ in age structure, source annotation, sample processing, gene universe and available covariates. A broad correlation asks whether thousands of effect estimates agree despite these differences; the frozen program test asks whether a prespecified coherent biological response has the same direction and statistical support. The data support the latter and explicitly reject the stronger transcriptome-wide interpretation.

The regulator analysis adds convergence without changing that inferential level. The primary ULM family found positive, globally corrected STAT1 and STAT2 activity in all three contrasts, and target-deletion and target-resampling diagnostics preserved direction. The correlation-aware analysis was directionally concordant in every core test, but CAMERA supported five of six tests after correction while FRY supported six of six; discovery-cohort STAT2 was the transparent CAMERA exception. Because these tests reuse the same contrasts and regulons, they are robustness analyses rather than new biological replication. M5911 enrichment and paired IFN-beta exposure provide evidence from resources that were not constructed from the SLE contrasts. Together, these layers make an IFN-centred regulatory framing more credible than a gene-list description alone, while not proving that STAT1 or STAT2 initiated the in vivo state, distinguishing a unique IFN ligand, or demonstrating direct TF binding.

The results also narrow several common SLE B-cell narratives. The naive-to-memory and APC/HLA axes are useful internal context but do not independently reproduce in GSE135779. The external atypical/low-naive signal cannot be labelled replication because it was absent in GSE174188. Likewise, stable broad `B_CONV` identity does not establish a discrete IFN-high subtype: interferon is treated as a continuous within-compartment program. The primary composition result remains a transparent negative boundary rather than being displaced by the secondary flare estimate.

The analysis has limitations. Public metadata did not provide a common set of sex, treatment and detailed clinical covariates across all contrasts. The adult external stratum was small, and two adult metadata donors lacked corresponding source matrices. The GSE174188 internal validation is not independent of the accession even after donor overlap is removed. The conventional-B mapping in GSE135779 relies on source labels and supports a broad analog rather than exact identity transfer. CollecTRI target activity depends on curated prior knowledge and gene coverage; the correlation-aware sensitivity does not create independent data, and one discovery STAT2 CAMERA test did not pass correction. The GSE23307 perturbation contains only two donors and was therefore interpreted descriptively. Direct binding, matched patient perturbation and prospective clinical validation remain outside the current evidence."""
    manuscript = replace_section(manuscript, "## Discussion", "## Conclusions", discussion)

    conclusion = """The defensible advance is specific: SLE is associated with an independently replicated IFN transcriptional shift within a disease-blind broad conventional-B compartment. Prespecified regulator activity, correlation-aware sensitivity testing, external response-set enrichment and a small healthy-donor perturbation provide convergent but non-causal support. The study identifies which remodeling layer survives sequential design and validation constraints; it does not establish a discrete subtype, universal plasmablast expansion, causal regulator or unique upstream ligand."""
    manuscript = replace_section(manuscript, "## Conclusions", "## List of abbreviations", conclusion)
    manuscript = replace_once(
        manuscript,
        "**ASC:** antibody-secreting cell;",
        "**ASC:** antibody-secreting cell; **CAMERA:** correlation-adjusted mean-rank gene-set test;",
        "abbreviation line",
    )
    manuscript = replace_once(
        manuscript,
        "**FDR:** false discovery rate;",
        "**FDR:** false discovery rate; **FRY:** fast rotation gene-set test;",
        "FDR abbreviation",
    )
    manuscript = replace_once(
        manuscript,
        "frozen for this draft at commit `05d5d60`.",
        "maintained in the Gate C8R source tree and will be frozen at the final public release commit.",
        "repository version statement",
    )
    manuscript = replace_once(
        manuscript,
        "**Additional file 2 (.zip):** Figure source data. Machine-readable CSV files underlying Figures 1-5, with a SHA-256 manifest.",
        "**Additional file 2 (.zip):** Figure source data. Machine-readable CSV files underlying Figures 1-5, with a SHA-256 manifest.\n\n**Additional file 3 (.zip):** Correlation-aware regulator sensitivity. Six STAT1/STAT2 CAMERA and FRY tests, the qualified decision record and a SHA-256 manifest.",
        "additional-file list",
    )

    legends = """### Figure 1 | Disease-blind reconstruction defines the permissible identity scope

**a,** Audited GSE174188 hierarchy, hard-quality-control retention and separation of disease-blind identity reconstruction from sample-level outcome inference. **b,** Median mapped adjusted Rand index and minimum-to-median interval for each candidate identity policy across 20 resamples; policies are discrete alternatives and are not connected as a trajectory. **c,** Mapped adjusted Rand index and mapping agreement in each two-compartment resampling run. **d,** Minimum and median state Jaccard indices for `B_CONV` and `B_ASC`, with frozen antibody-secreting marker support. Cell-level summaries define identity stability and are not disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

**a,** Observed `B_ASC` fractions for exactly 43 control and 47 managed-SLE sample-cohort strata in the primary composition contrast; diamonds and bars show adjusted fractions and 95% confidence intervals. **b,** Primary, internal, donor-nonoverlap and secondary flare conditional odds ratios. **c,** Frozen primary estimate and mandatory minimum-cell, explicit non-B and residual-doublet sensitivities. **d,** Conditional odds ratios after each of 90 primary sample deletions; the horizontal line is the full estimate. The flare contrast is secondary and did not pass the frozen three-contrast false-discovery-rate rule.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

**a,** Effects and 95% confidence intervals for the four frozen programs in the primary contrast. **b,** IFN/ISG estimates across primary support thresholds, residual-risk restriction, internal replication, donor-nonoverlap internal replication and the secondary flare contrast. **c,** Gene-level log2 fold changes for the frozen IFN positive arm in the primary and donor-nonoverlap contrasts. IFIT1 and IFIT2 were filtered from the primary gene-level test, and IFIT1 was filtered from the donor-nonoverlap test; these absences are marked rather than imputed. **d,** IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity families in the primary and donor-nonoverlap contrasts. Program intervals use HC3 uncertainty; confirmatory q values use the frozen four-program family.

### Figure 4 | GSE135779 independently replicates the frozen IFN/ISG program

**a,** Standardized IFN/ISG effects for childhood, combined, adult and support-threshold external analyses. **b,** Standardized discovery and internal GSE174188 effects beside independent GSE135779 effects. **c,** Effects for 4,410 genes tested in both primary datasets, with ten jointly tested frozen IFN genes highlighted; all ten were positive in both datasets despite Spearman rho=0.026 genome-wide. **d,** Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Donors are the biological units in GSE135779; the adult estimate is directional only.

### Figure 5 | Convergent observational evidence supports IFN-centred regulation

**a,** Prespecified three-contrast, eight-regulator design, global 24-test Benjamini-Hochberg family and core target-robustness analyses. **b,** Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. **c,** Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation controls. Asterisks indicate global 24-test q<0.05. **d,** M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. **e,** Mean paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells from two healthy donors; labels show positive genes. The GSE23307 panel is descriptive at n=2 and carries no inferential P value."""
    manuscript = replace_section(manuscript, "## Figure legends", "## References", legends)
    reference_start = manuscript.index("## References")
    manuscript = manuscript[:reference_start] + "## References\n\n" + checked_references() + "\n"

    if manuscript.count("[[") != source_placeholders:
        raise RuntimeError("Author-controlled placeholder count changed during C8R source build")
    before_refs = manuscript[: manuscript.index("## References")]
    for number in range(18, 31):
        if not any(
            re.search(rf"(?:^|\D){number}(?:\D|$)", citation)
            for citation in re.findall(r"\[([^\]]+)\]", before_refs)
        ):
            raise RuntimeError(f"New reference {number} is not cited in manuscript text")
    reference_lines = re.findall(r"^(\d+)\.\s", section(manuscript, "## References", None), flags=re.M)
    if [int(value) for value in reference_lines] != list(range(1, 31)):
        raise RuntimeError("Reference numbering is not exactly 1-30")
    required = [
        "43 control and 47 managed-SLE",
        "CAMERA q=0.1355",
        "FRY remained positive and significant (q=4.91 x 10^-5)",
        "Spearman rho=0.026",
        "The intended advance is therefore not rediscovery of interferon activity in SLE.",
    ]
    missing = [token for token in required if token not in manuscript]
    if missing:
        raise RuntimeError(f"Missing C8R manuscript anchors: {missing}")
    return manuscript, words(abstract)


def build_supplement() -> str:
    with CORRELATION_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 6:
        raise RuntimeError(f"Expected six correlation-aware rows, found {len(rows)}")
    labels = {
        "gse174188_primary": "GSE174188 primary",
        "gse174188_internal_nonoverlap": "GSE174188 donor-nonoverlap",
        "gse135779_childhood": "GSE135779 childhood",
    }
    table_rows = []
    for row in rows:
        table_rows.append(
            "| {contrast} | {regulator} | {targets} | {corr:.4f} | {camera} | {fry} |".format(
                contrast=labels[row["contrast"]],
                regulator=row["regulator"],
                targets=row["matched_signed_targets"],
                corr=float(row["camera_inter_gene_correlation"]),
                camera=f"{float(row['camera_q_core6']):.4g}",
                fry=f"{float(row['fry_q_core6']):.4g}",
            )
        )
    correlation_table = "\n".join(table_rows)
    return f"""# Supplementary information

## Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence in systemic lupus erythematosus B cells

**Version:** Gate C8R, 20 August 2026

**Authors:** Zhi Chen and Teng Qi

## Supplementary overview

This file documents the prespecified governance, identity boundary, inferential units, validation hierarchy and reproducibility assets supporting the main manuscript. Gate C8R corrects the Figure 2a control-group rendering, applies explicit panel-data assertions, adds a correlation-aware STAT1/STAT2 sensitivity and updates the narrative without altering frozen upstream estimates.

## Supplementary Methods 1 | Gate governance and outcome protection

The workflow used sequential gates for source integrity, hard quality control, disease-blind identity reconstruction, sample-level composition, within-compartment pseudobulk analysis, independent validation and external regulatory evidence. Protected disease fields were separated during identity reconstruction. Real outcome effects were unlocked only after the relevant input, mapping, contrast and statistical-engine contracts had been recorded. Each gate retained a machine-readable decision and SHA-256 integrity manifest.

## Supplementary Methods 2 | Identity stability boundary

The initial five-state model failed the prespecified resampling thresholds. Repair analyses evaluated four-, three- and two-level mappings without consulting disease labels. Only the broad B_CONV/B_ASC solution met all stability criteria across 20 resampling runs. Fine naive-memory structure was therefore retained as continuous transcriptional context rather than a hard publication subtype. This negative boundary is part of the result, not a quality-control artifact to be removed.

## Supplementary Methods 3 | Biological units and contrast hierarchy

GSE174188 composition and expression analyses used sample-by-processing-cohort strata; donor-aware sensitivities addressed repeated samples. GSE135779 used donors as the biological units. Primary, internal, donor-nonoverlap, secondary flare, childhood, combined and adult contrasts remained separate. No bridge stratum was used to manufacture a pooled disease coefficient, and internal GSE174188 estimates were not described as independent validation.

## Supplementary Methods 4 | Robustness and specificity

Prespecified sensitivity analyses varied minimum cell support, excluded residual-doublet-risk cells, deleted samples or donors one at a time, omitted source labels and compared platelet/ambient, ASC/UPR and pan-B control programs. The TF-target family used one global correction across 24 tests. STAT1 and STAT2 core results underwent leave-one-target and deterministic 80% target-resampling analyses. The GSE23307 two-donor perturbation remained descriptive.

## Supplementary Methods 5 | Correlation-aware regulator sensitivity

The Gate C8R sensitivity reused frozen STAT1/STAT2 signed targets, model matrices, contrasts and tested-gene backgrounds. Voom precision weights fed CAMERA with residual-estimated inter-gene correlation and FRY directional rotation tests. BH adjustment was applied across six core tests within each method. Exact agreement with frozen ULM matched-target counts was mandatory. The analysis was post-audit robustness testing and did not constitute independent replication.

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
{correlation_table}

CAMERA and FRY directions were positive in all six tests. CAMERA passed BH correction in five of six; the explicit exception was GSE174188 primary STAT2 (q=0.1355). FRY passed BH correction in all six.

## Supplementary Table S5 | Figure and source-data map

| Figure | Frozen gate | Machine-readable source |
|---|---|---|
| Figure 1 | C2B4 identity freeze; C8R render repair | Figure1_source_data.csv |
| Figure 2 | C3A composition decision; C8R group-map repair | Figure2_source_data.csv |
| Figure 3 | C4B transcription; C8R label clarification | Figure3_source_data.csv |
| Figure 4 | C5B replication; C8R axis clarification | Figure4_source_data.csv |
| Figure 5 | C6B regulatory framing; C8R hierarchy clarification | Figure5_source_data.csv |

## Supplementary Table S6 | Reproducibility contract

| Component | Frozen record |
|---|---|
| C8R panel-data assertions | `phase17_v7/gateC8R/20260820_pre_submission_repair/02_PANEL_DATA_ASSERTIONS.json` |
| Correlation-aware sensitivity | `phase17_v7/gateC8R/20260820_pre_submission_repair/03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv` |
| Correlation-aware decision | `phase17_v7/gateC8R/20260820_pre_submission_repair/04_CORRELATION_AWARE_STAT1_STAT2_DECISION.json` |
| Active manuscript source | `01_manuscript/manuscript_v11_genome_medicine_gateC8R_2026-08-20.md` |
| Public repository | `https://github.com/1209433622cz-maker/sle-bcell-remodeling` |
| Immutable release | Author-controlled licence and archive DOI remain required before portal submission |

## Supplementary note on superseded artifacts

Earlier manuscripts, Gate C7 figures and the Gate C8 package remain in the repository for provenance but are not active submission sources. Figure 2a in Gate C8 omitted control points because the plotting layer expected `normal` while the frozen source encoded controls as `na`; Gate C8R maps the frozen values explicitly and asserts 43 controls, 47 managed-SLE strata and 90 total points before rendering. No composition estimate changed. The previous ABC/APC-like hard-subtype narrative and untransformed GSE23307 outputs remain superseded and excluded from every active claim, figure and submission file.
"""


def build_auxiliary_sources() -> dict[str, Path]:
    old_cover = (SUBMISSION / "cover_letter_genome_medicine_gateC8_AUTHOR_COMPLETION_REQUIRED_2026-08-20.md").read_text(encoding="utf-8")
    old_advance = """The principal advance is a deliberately bounded and reproducible result. Fine naive-memory partitions were not stable enough for hard outcome inference, and primary antibody-secreting-cell relative abundance was null. In contrast, a type I IFN/ISG program within broad conventional B cells reproduced in GSE174188 discovery, a donor-nonoverlap internal contrast and independent GSE135779 childhood donors. STAT1 and STAT2 target activities reproduced across all three contrasts under one prespecified 24-test correction family and remained positive under target-deletion and resampling analyses. Independent M5911 enrichment and paired IFN-beta perturbation profiles supplied orthogonal response evidence. We explicitly do not claim a discrete IFN-high subtype, causal regulator, direct TF binding or unique upstream ligand."""
    new_advance = """The principal advance is not rediscovery of interferon involvement in SLE, but a deliberately bounded identification of the remodeling layer that survives sequential safeguards. Fine naive-memory partitions were not stable enough for hard outcome inference, and primary antibody-secreting-cell relative abundance was null. In contrast, a type I IFN/ISG program within broad conventional B cells reproduced in GSE174188 discovery, a donor-nonoverlap internal contrast and independent GSE135779 childhood donors. STAT1 and STAT2 target activities were positive and globally significant under the prespecified ULM family; correlation-aware CAMERA supported five of six core tests after correction and FRY supported six of six, with the discovery STAT2 CAMERA exception reported explicitly. Independent M5911 enrichment and paired IFN-beta perturbation profiles supplied orthogonal response evidence. We do not claim a discrete IFN-high subtype, universal plasmablast expansion, causal regulator, direct TF binding or unique upstream ligand."""
    cover = replace_once(old_cover, old_advance, new_advance, "cover-letter advance")
    cover_path = SUBMISSION / "cover_letter_genome_medicine_gateC8R_AUTHOR_COMPLETION_REQUIRED_2026-08-20.md"
    cover_path.write_text(cover, encoding="utf-8")

    form = (SUBMISSION / "author_completion_form_gateC8_2026-08-20.md").read_text(encoding="utf-8")
    form = form.replace("Gate C8", "Gate C8R")
    form = replace_once(
        form,
        "Complete and approve every hard-stop field before portal submission.",
        "Gate C8R scientific and technical repair is complete. Complete and approve every hard-stop field before portal submission.",
        "author-form opening",
    )
    form_path = SUBMISSION / "author_completion_form_gateC8R_2026-08-20.md"
    form_path.write_text(form, encoding="utf-8")

    target = (SUBMISSION / "journal_target_decision_gateC8_2026-08-20.md").read_text(encoding="utf-8")
    target = target.replace("Gate C8", "Gate C8R")
    target = replace_once(
        target,
        "## Genome Medicine requirements frozen into Gate C8R",
        "## Gate C8R evidence update\n\nThe Figure 2a group-map defect has been repaired with exact panel-data assertions, the five-figure visual system has been harmonized, the literature position has been expanded to 30 references and STAT1/STAT2 now has a correlation-aware sensitivity. The reach ceiling remains limited by the absence of matched patient perturbation, direct binding and prospective clinical validation.\n\n## Genome Medicine requirements frozen into Gate C8R",
        "target requirements heading",
    )
    target_path = SUBMISSION / "journal_target_decision_gateC8R_2026-08-20.md"
    target_path.write_text(target, encoding="utf-8")

    checklist = (SUBMISSION / "reporting_checklist_gateC8_2026-08-20.md").read_text(encoding="utf-8")
    checklist = checklist.replace("Gate C8", "Gate C8R")
    checklist = replace_once(
        checklist,
        "- [x] Five active figures map to frozen gates and source data.",
        "- [x] Five active figures map to frozen gates and source data.\n- [x] Figure 2a contains exactly 43 control and 47 managed-SLE observations.\n- [x] All five figures pass panel-data assertions and the 5-point minimum text-size rule.\n- [x] Correlation-aware STAT1/STAT2 sensitivity is reported with its discovery STAT2 CAMERA exception.",
        "scientific checklist",
    )
    checklist = replace_once(
        checklist,
        "- [x] Figure source-data ZIP and checksum manifest.",
        "- [x] Figure source-data ZIP and checksum manifest.\n- [x] Correlation-aware regulator-sensitivity ZIP and checksum manifest.",
        "file checklist",
    )
    checklist_path = SUBMISSION / "reporting_checklist_gateC8R_2026-08-20.md"
    checklist_path.write_text(checklist, encoding="utf-8")
    return {
        "cover": cover_path,
        "author_form": form_path,
        "target": target_path,
        "checklist": checklist_path,
    }


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manuscript, abstract_words = build_manuscript()
    supplement = build_supplement()
    MANUSCRIPT.write_text(manuscript, encoding="utf-8")
    SUPPLEMENT.write_text(supplement, encoding="utf-8")
    auxiliary = build_auxiliary_sources()
    status = {
        "created_at": "2026-08-20",
        "status": "PASS_C8R_SUBMISSION_SOURCES_BUILT",
        "manuscript": MANUSCRIPT.relative_to(ROOT).as_posix(),
        "supplement": SUPPLEMENT.relative_to(ROOT).as_posix(),
        "auxiliary_sources": {key: path.relative_to(ROOT).as_posix() for key, path in auxiliary.items()},
        "abstract_words": abstract_words,
        "manuscript_words": words(manuscript),
        "reference_count": 30,
        "doi_records_verified": 26,
        "author_controlled_placeholders": manuscript.count("[[") + auxiliary["cover"].read_text(encoding="utf-8").count("[["),
        "correlation_aware_summary": {
            "camera_positive": 6,
            "camera_bh_significant": 5,
            "fry_positive": 6,
            "fry_bh_significant": 6,
            "explicit_exception": "GSE174188 primary STAT2 CAMERA q=0.1355",
        },
    }
    (RUN_DIR / "05_GATE_C8R_SOURCE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
