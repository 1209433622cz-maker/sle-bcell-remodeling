from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd


DATE = "20 August 2026"
RUN_REL = Path("phase17_v7/gateC7/20260820_manuscript_figure_integration")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Gate C7 manuscript and proposal from frozen evidence.")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


def section_replace(text: str, start: str, end: str, replacement: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[:start_index] + replacement.rstrip() + "\n\n" + text[end_index:]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def manuscript_abstract() -> str:
    return """## Abstract

Systemic lupus erythematosus (SLE) alters both the abundance and transcriptional
state of peripheral B cells, but these layers can be conflated by outcome-informed
annotation, cell-level inference and technically imbalanced cohorts. We performed a
donor- and cohort-resolved reanalysis of public single-cell RNA-sequencing data,
using disease-blind identity reconstruction before any case-control comparison.
From 150,402 hard-quality-control B-lineage cells in GSE174188, resampling supported
two broad identity compartments, conventional B cells (`B_CONV`) and
antibody-secreting cells (`B_ASC`), while finer naive-memory partitions were not
stable enough for hard compositional inference. Sample-level analysis did not
support a primary SLE-associated difference in relative `B_ASC` abundance (odds
ratio 0.947, 95% confidence interval 0.636-1.410; P=0.787). In contrast,
sample-by-compartment pseudobulk analysis identified a prespecified type I
interferon/interferon-stimulated-gene (IFN/ISG) shift within `B_CONV` in the primary
GSE174188 contrast (standardized effect 0.837, 95% confidence interval 0.525-1.148;
four-program false-discovery-rate q=2.98 x 10^-6) and a donor-nonoverlap internal
contrast (effect 1.086; q=3.61 x 10^-4). The frozen program replicated in independent
GSE135779 childhood donors (11 controls and 32 SLE; effect 1.042, 95% confidence
interval 0.681-1.402; q=2.98 x 10^-6). Genome-wide cross-dataset agreement was low
(Spearman rho=0.026), whereas all ten jointly tested IFN genes were positive in both
datasets. Under a prespecified 24-test CollecTRI contract, STAT1 and STAT2 target
activities were positive and globally significant in all three confirmatory
contrasts and robust to target deletion and resampling. The exact MSigDB M5911
response was enriched in all three contrasts (normalized enrichment scores
3.050-3.527), and paired IFN-beta exposure in GSE23307 increased all 12 frozen genes
in each of two healthy-donor B-cell profiles. These results support independently
replicated IFN remodeling with convergent observational regulatory evidence within
a disease-blind broad conventional-B compartment, without establishing a discrete
subtype, causal regulator or unique upstream stimulus."""


def regulatory_results() -> str:
    return """### Prespecified regulatory and perturbational evidence converges on the IFN response

We next tested whether the replicated transcriptional program was accompanied by a
prespecified regulatory pattern. The contract was frozen before real regulator
effects were inspected and included four IFN-centred regulators (STAT1, STAT2, IRF7
and IRF9), four proliferation controls (E2F1, FOXM1, MYC and MYBL2), and the three
confirmatory contrasts used above. Signed CollecTRI target activity was evaluated in
one global Benjamini-Hochberg family of 24 tests.

STAT1 and STAT2 activity estimates were positive and globally significant in the
GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts.
At least three of the four IFN-centred regulators were positive in every contrast,
with no globally significant opposite-direction IFN regulator. The proliferation
controls did not reproduce a positive globally significant pattern across all three
contrasts. Every leave-one-target estimate for the core STAT1 and STAT2 models
retained the positive direction, and each core model remained positive in all 100
deterministic 80%-target resamples. These diagnostics argue against a result driven
by one target gene or a small target subset.

Two independently defined response layers were directionally concordant. The exact
MSigDB Hallmark interferon-alpha response set M5911 was positively enriched in all
three ranked contrasts (normalized enrichment scores 3.187, 3.050 and 3.527;
10,000 gene-label permutations per contrast). In GSE23307 primary human B cells exposed
to IFN-beta, the frozen 12-gene positive arm increased for all 12 genes in each of
two healthy donors. Mean paired log2(x+1) effects were 3.294 and 3.666. No
inferential P value was calculated for this two-donor experiment.

The three layers therefore support an IFN-centred regulatory interpretation of the
replicated program, but they do not identify a unique initiating ligand or establish
causation in SLE. CollecTRI activity is inferred from observational disease-ranked
statistics, M5911 is a response signature, and GSE23307 is a small ex vivo
perturbation in healthy-donor B cells."""


def discussion() -> str:
    return """## Discussion

This study identifies a reproducible level of SLE B-cell biology by separating
identity, composition and transcription before testing disease effects. Fine-grained
hard B-cell states were not stable under the prespecified disease-blind resampling
contract, and the repaired model deliberately stopped at two broad compartments.
Within that permissible scope, primary `B_ASC` relative abundance did not differ
between SLE and controls. The central result instead arose within `B_CONV`: a frozen
type I IFN/ISG program was supported in the primary GSE174188 contrast, an internal
donor-nonoverlap contrast and independent GSE135779.

The low cross-dataset genome-wide correlation is not a contradiction of the frozen
program result. The two accessions differ in age structure, source annotation,
sample processing, gene universe and available covariates. A broad correlation asks
whether thousands of effect estimates agree despite these differences; the frozen
program test asks whether a prespecified coherent biological response has the same
direction and statistical support. The data support the latter and explicitly reject
the stronger transcriptome-wide interpretation.

The regulator analysis adds convergence without changing that inferential level.
STAT1 and STAT2 target activities reproduced across the same discovery, internal
donor-nonoverlap and independent childhood contrasts, survived global correction,
and were insensitive to individual-target deletion and target resampling. M5911
enrichment and paired IFN-beta exposure provide evidence from resources that were
not constructed from the SLE contrasts. Together, these findings make an
IFN-centred regulatory framing more credible than a gene-list description alone.
They do not prove that STAT1 or STAT2 initiated the in vivo state, distinguish
IFN-alpha from IFN-beta as the disease stimulus, or demonstrate direct TF binding.

The results also narrow several common SLE B-cell narratives. The naive-to-memory
and APC/HLA axes are useful internal context but do not independently reproduce in
GSE135779. The external atypical/low-naive signal cannot be labelled replication
because it was absent in GSE174188. Likewise, stable broad `B_CONV` identity does not
establish a discrete IFN-high subtype: interferon is treated as a continuous
within-compartment program. The primary composition result remains a transparent
negative boundary rather than being displaced by the secondary flare estimate.

The analysis has limitations. Public metadata did not provide a common set of sex,
treatment and detailed clinical covariates across all contrasts. The adult external
stratum was small, and two adult metadata donors lacked corresponding source
matrices. The GSE174188 internal validation is not independent of the accession even
after donor overlap is removed. The conventional-B mapping in GSE135779 relies on
source labels and supports a broad analog rather than exact identity transfer.
CollecTRI target activity depends on curated prior knowledge and gene coverage; the
GSE23307 perturbation contains only two donors and was therefore interpreted
descriptively. Direct binding, matched patient perturbation and prospective clinical
validation remain outside the current evidence.

The defensible advance is therefore specific: SLE is associated with an
independently replicated IFN transcriptional shift within a disease-blind broad
conventional-B compartment, accompanied by convergent IFN-centred regulatory and
perturbational evidence. This conclusion is stronger than a single-cohort
differential-expression result and narrower than a causal mechanism claim."""


def regulatory_methods() -> str:
    return """### Prespecified TF-target activity

Human CollecTRI interactions were retrieved from OmniPath on 15 August 2026 and
frozen by raw SHA-256
`98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1`.
Only exact individual-TF source symbols were used. Consensus stimulation and
inhibition were encoded as +1 and -1, respectively; ambiguous target directions
were excluded, and duplicate same-sign edges were collapsed. The confirmatory
family comprised STAT1, STAT2, IRF7, IRF9, E2F1, FOXM1, MYC and MYBL2 in the
GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts.

For every tested Ensembl feature, the ranked statistic was
`sign(logFC) * sqrt(F)` from the frozen robust edgeR quasi-likelihood result.
Features were mapped to uppercase symbols, and statistics were averaged when
multiple tested Ensembl features mapped to one symbol. For each regulator and
contrast, a univariate linear model with an intercept regressed the gene-level
statistic on the signed target weight. The slope, standard error, two-sided P value
and 95% confidence interval were reproduced independently by direct matrix algebra.
Benjamini-Hochberg correction was applied once across all 24 confirmatory tests.
For each core regulator and contrast, influence analysis deleted each matched target
in turn, and 100 deterministic analyses resampled 80% of matched targets.

### Orthogonal interferon-response analyses

MSigDB human release 2026.1.Hs Hallmark set
`HALLMARK_INTERFERON_ALPHA_RESPONSE` (systematic identifier M5911; 97 frozen member
genes) was tested against each complete ranked contrast. Preranked enrichment used
10,000 deterministic gene-label permutations, with normalized enrichment
scores and descriptive three-contrast q values reported outside the 24-test TF
family.

GSE23307 GPL6104 microarray profiles comprised paired untreated and IFN-beta-exposed
primary B cells from two healthy donors. Platform annotation was frozen before
effects were calculated. Twenty-one probes mapping to the 12 frozen IFN/ISG
positive-arm genes were transformed as log2(x+1), collapsed to one value per gene
and sample by the median, and differenced within donor. The donor summary was the
mean paired effect across 12 genes. Direction and gene concordance were descriptive;
no inferential P value was calculated at n=2. Earlier untransformed GSE23307 files
were retained solely as superseded audit artifacts and were excluded from every
active result, figure and claim."""


def figure_legends() -> str:
    return """## Figure legends

### Figure 1 | Disease-blind reconstruction defines the permissible identity scope

**a,** Audited GSE174188 hierarchy, hard-quality-control retention and separation of
identity reconstruction from outcome inference. **b,** Median and minimum mapped
adjusted Rand indices for five-, four-, three-state and repaired two-compartment
policies across disease-blind resampling. **c,** Mapped adjusted Rand index and
mapping agreement in each of 20 two-compartment resampling runs. **d,** Minimum and
median state Jaccard indices for `B_CONV` and `B_ASC`; the frozen antibody-secreting
marker support is shown. Cell-level summaries define identity stability and are not
used as disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

**a,** Observed `B_ASC` fractions for 43 control and 47 managed-SLE sample-cohort
strata in the primary contrast; diamonds and bars show adjusted fractions and 95%
confidence intervals. **b,** Primary, internal, donor-nonoverlap and secondary flare
conditional odds ratios. **c,** Frozen primary estimate and mandatory minimum-cell,
explicit non-B and residual-doublet sensitivities. **d,** Conditional odds ratios
after each of 90 primary sample deletions; the horizontal line is the full estimate.
The flare contrast is secondary and did not pass the frozen three-contrast
false-discovery-rate rule.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

**a,** Effects and 95% confidence intervals for the four frozen programs in the
primary contrast. **b,** IFN/ISG estimates across primary support thresholds,
residual-risk restriction, internal replication, donor-nonoverlap internal
replication and the secondary flare contrast. **c,** Gene-level log2 fold changes
for the frozen IFN positive arm in the primary and donor-nonoverlap contrasts.
**d,** IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity
families in the primary and donor-nonoverlap contrasts. Program intervals use HC3
uncertainty; confirmatory q values use the frozen four-program family.

### Figure 4 | GSE135779 independently replicates the frozen IFN/ISG program

**a,** Childhood, combined, adult and support-threshold external IFN/ISG estimates.
**b,** Discovery and internal GSE174188 estimates beside independent GSE135779
estimates. **c,** Effects for 4,410 genes tested in both primary datasets, with ten
jointly tested frozen IFN genes highlighted; all ten were positive in both datasets
despite low genome-wide correlation. **d,** Full childhood estimate, range across 43
donor deletions and estimates after omission of each of eight source B-cell labels.
Donors are the biological units in GSE135779; the adult estimate is directional
only.

### Figure 5 | Convergent observational evidence supports IFN-centred regulation

**a,** Prespecified three-contrast, eight-regulator design, global 24-test
Benjamini-Hochberg family and core target-robustness analyses. **b,** STAT1, STAT2,
IRF7 and IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188
donor-nonoverlap and GSE135779 childhood contrasts. **c,** Prespecified E2F1,
FOXM1, MYC and MYBL2 proliferation controls. Asterisks indicate global 24-test
q<0.05. **d,** M5911 Hallmark interferon-alpha response normalized enrichment
scores from 10,000 gene-label permutations per contrast. **e,** Mean paired log2(x+1) effects
for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells
from two healthy donors; labels show positive genes. The perturbation panel is
descriptive at n=2."""


def build_manuscript(root: Path) -> tuple[Path, Path]:
    source_path = root / "01_manuscript/manuscript_v8_gateC6A_claim_integrated_2026-08-15.md"
    text = source_path.read_text(encoding="utf-8")
    text = text.replace(
        "# Disease-blind single-cell reconstruction identifies independently replicated interferon remodeling in conventional B cells in systemic lupus erythematosus",
        "# Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence in systemic lupus erythematosus B cells",
        1,
    )
    text = text.replace("**Version:** Gate C6A claim-integrated working manuscript v8", "**Version:** Gate C7 submission-scientific draft v9", 1)
    text = text.replace("**Date:** 15 August 2026", f"**Date:** {DATE}", 1)
    text = text.replace(
        "**Status:** scientific-content draft; not journal-formatted; references, author list and declarations remain to be finalized",
        "**Status:** Gate C7 scientific and five-figure freeze; journal formatting, author metadata and declarations remain to be finalized",
        1,
    )
    text = section_replace(text, "## Abstract", "## Introduction", manuscript_abstract())
    old_intro_end = """The analysis was designed to distinguish robust process-level biology from visually
appealing but unstable subtype narratives. We show that a fine-grained hard
naive-memory partition is not reproducible enough for outcome inference and that
`B_ASC` composition is not a central disease result. Instead, the reproducible
cross-dataset signal is a type I IFN/ISG transcriptional shift within a disease-blind
broad conventional-B compartment."""
    new_intro_end = old_intro_end + """ We then tested a prespecified IFN-centred
TF-target family and two orthogonal response resources to ask whether this replicated
program had convergent regulatory support without converting association into a
causal claim."""
    if old_intro_end not in text:
        raise RuntimeError("Manuscript introduction anchor not found")
    text = text.replace(old_intro_end, new_intro_end, 1)
    text = text.replace("\n## Discussion\n", "\n\n" + regulatory_results() + "\n\n## Discussion\n", 1)
    text = section_replace(text, "## Discussion", "## Methods", discussion())
    old_study = """The study was a secondary analysis of public human transcriptomic data. GSE174188
was used for disease-blind B-lineage reconstruction, sample-level composition,
within-compartment transcriptional analysis and internal validation. GSE135779 was
the independent SLE validation dataset. GSE163121 was reserved for directional
boundary analysis and OneK1K for healthy reference context; neither contributes to
the central replication claim reported here."""
    new_study = """The study was a secondary analysis of public human transcriptomic data. GSE174188
was used for disease-blind B-lineage reconstruction, sample-level composition,
within-compartment transcriptional analysis and internal validation. GSE135779 was
the independent SLE validation dataset. CollecTRI and MSigDB supplied independently
curated regulatory and response priors, and GSE23307 supplied paired IFN-beta
perturbation profiles from healthy-donor primary B cells. GSE163121 was reserved for
directional boundary analysis and OneK1K for healthy reference context; neither
contributes to the central replication claim reported here."""
    if old_study not in text:
        raise RuntimeError("Manuscript study-design anchor not found")
    text = text.replace(old_study, new_study, 1)
    text = text.replace("\n### Reproducibility and governance\n", "\n\n" + regulatory_methods() + "\n\n### Reproducibility and governance\n", 1)
    text = section_replace(text, "## Figure legends", "## Data and code availability", figure_legends())
    data_section = """## Data and code availability

GSE174188, GSE135779 and GSE23307 are public Gene Expression Omnibus accessions.
Analysis code, machine-readable decisions, compact source-data tables, figure PDFs
and 600-dpi PNGs are versioned in the project repository. Large recomputable
matrices remain local with SHA-256 records and scripted regeneration. Figure-level
source data and a claim-to-number crosswalk are frozen under Gate C7."""
    text = section_replace(text, "## Data and code availability", "## References", data_section)
    references = """## References

1. Perez RK et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. *Science*. 2022. doi:10.1126/science.abf1970.
2. Nehar-Belaid D et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. *Nature Immunology*. 2020. doi:10.1038/s41590-020-0743-0.
3. Crowell HL et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. *Nature Communications*. 2020. doi:10.1038/s41467-020-19894-4.
4. Squair JW et al. Confronting false discoveries in single-cell differential expression. *Nature Communications*. 2021. doi:10.1038/s41467-021-25960-2.
5. Buttner M et al. scCODA is a Bayesian model for compositional single-cell data analysis. *Nature Communications*. 2021. doi:10.1038/s41467-021-27150-6.
6. Badia-I-Mompel P et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. *Bioinformatics Advances*. 2022. doi:10.1093/bioadv/vbac016.
7. Muller-Dott S et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. *Nucleic Acids Research*. 2023. doi:10.1093/nar/gkad841.
8. Liberzon A et al. The Molecular Signatures Database Hallmark Gene Set Collection. *Cell Systems*. 2015. doi:10.1016/j.cels.2015.12.004.
9. van Boxel-Dezaire AHH et al. Major differences in the responses of primary human leukocyte subsets to IFN-beta. *Journal of Immunology*. 2010;185:5888-5899. doi:10.4049/jimmunol.0902314."""
    text = text[: text.index("## References")] + references + "\n"

    output_path = root / "01_manuscript/manuscript_v9_gateC7_submission_scientific_draft_2026-08-20.md"
    legends_path = root / "01_manuscript/main_figure_legends_v9_gateC7_2026-08-20.md"
    write_text(output_path, text)
    write_text(legends_path, figure_legends())
    return output_path, legends_path


def proposal_text() -> str:
    return """# MBI6013 Research Proposal

## Independently replicated interferon remodeling with convergent regulatory evidence in systemic lupus erythematosus B cells

**Outcome-integrated version 16**
**Date:** 20 August 2026
**Study type:** secondary analysis of public human transcriptomic data
**Governance status:** Gates C1-C7 scientific integration completed; all central claims remain noncausal

## Project summary

This project separates B-cell identity, relative abundance and within-compartment
transcription in public systemic lupus erythematosus (SLE) single-cell data. The
analysis was organized as sequential pre-effect gates: source integrity and metadata
hierarchy; disease-blind identity reconstruction; sample-level composition;
sample-by-compartment pseudobulk transcription; independent dataset validation; and
prespecified regulatory and perturbational convergence.

Four findings are complete. First, disease-blind resampling supports two broad
B-lineage compartments, conventional B cells (`B_CONV`) and antibody-secreting cells
(`B_ASC`), while finer hard naive-memory states are insufficiently stable for
outcome inference. Second, the primary sample-level `B_ASC` composition contrast is
null. Third, a frozen type I interferon/interferon-stimulated-gene (IFN/ISG) program
within `B_CONV` replicates from GSE174188 into independent GSE135779. Fourth,
prespecified STAT1/STAT2 target activity, exact M5911 enrichment and a small paired
IFN-beta B-cell perturbation dataset converge on the same response. The project
supports an observational IFN-centred regulatory framing, not a new subtype, a
unique upstream stimulus or causation.

## 1. Background and significance

SLE is a heterogeneous autoimmune disease involving loss of B-cell tolerance,
autoantibody production and sustained innate immune activation. Single-cell studies
can distinguish abundance changes from transcriptional changes only when donors,
samples, libraries and processing cohorts are represented correctly. Cells from one
donor are not independent disease replicates, and disease-informed annotation can
make identity itself depend on the outcome being tested.

GSE174188 provides extensive B-lineage coverage but includes repeated donors,
technical library structure, bridge samples and disease imbalance across processing
cohorts. GSE135779 provides an independent SLE cohort with childhood and adult
strata, but its source labels and gene universe differ. Exact hard-subtype transfer
would therefore be stronger than the available evidence. A broad conventional-B
compartment and frozen continuous programs provide a more reproducible target.

Type I IFN is biologically plausible in SLE, yet observational target enrichment
does not demonstrate which ligand initiated the state or whether a transcription
factor directly bound the nominated genes. Curated regulons and perturbation data
can add convergence if they are frozen before effect inspection and interpreted
within their replication limits.

## 2. Central hypothesis and completed aims

### Central hypothesis

SLE is associated with a reproducible IFN/ISG transcriptional shift within a
disease-blind broad conventional-B compartment. Prespecified IFN-centred target
activity and orthogonal interferon-response resources should be concordant if this
program reflects biologically coherent IFN regulation. The completed results support
this hypothesis at an observational, noncausal level.

### Aim 1. Reconstruct disease-blind B-lineage identity from audited raw counts

**Status:** completed.

The GSE174188 source contained 152,981 B-lineage cells and 30,172 genes. Hard quality
control retained 150,402 cells. The initial five-state policy failed the frozen
resampling gate. A repaired two-compartment model (`B_CONV`, `B_ASC`) reproduced in
20/20 resamples, with minimum mapped adjusted Rand index 0.990 and minimum state
median Jaccard index 0.991. Hard naive, memory and atypical composition labels remain
prohibited.

### Aim 2. Separate SLE-associated composition from within-compartment transcription

**Status:** completed.

The primary `B_ASC` composition contrast was unsupported (odds ratio 0.947, 95%
confidence interval 0.636-1.410; P=0.787). A secondary flare estimate did not survive
the frozen three-contrast correction (q=0.0845). In contrast, the frozen IFN/ISG
program was higher in GSE174188 primary `B_CONV` pseudobulks (effect 0.837, 95%
confidence interval 0.525-1.148; q=2.98 x 10^-6) and in the donor-nonoverlap internal
contrast (effect 1.086; q=3.61 x 10^-4).

### Aim 3. Test the frozen IFN/ISG program in an independent SLE dataset

**Status:** completed.

GSE135779 childhood donors independently replicated IFN/ISG (11 controls, 32 SLE;
effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined
estimate was 0.996 (q=1.31 x 10^-6), while the adult-only estimate was positive but
underpowered. Forty-three donor deletions and eight source-label omissions retained
the childhood direction. All ten jointly tested IFN genes were positive in both
primary datasets despite low genome-wide agreement (4,410 genes; rho=0.026).

### Aim 4. Test a frozen interferon-centred regulatory hypothesis

**Status:** completed; Gate C6B passed for noncausal regulatory framing.

STAT1 and STAT2 CollecTRI activity estimates were positive and global-24-test
significant in all three confirmatory contrasts. Core estimates retained direction
after every target deletion and in all 100 deterministic 80%-target resamples. The
proliferation-control family did not reproduce a positive globally significant
three-contrast pattern. M5911 was positively enriched in all three contrasts (NES
3.187, 3.050 and 3.527). In paired GSE23307 IFN-beta-exposed B cells, all 12 frozen
genes increased in each of two donors; mean log2(x+1) effects were 3.294 and 3.666.

## 3. Completed design and analytical methods

### 3.1 Source governance and experimental units

Source paths, dimensions, encodings and SHA-256 values were frozen. Metadata were
resolved at donor, biological-sample, technical-library and processing-cohort
levels. Protected disease fields remained separate during identity reconstruction.
Composition used sample-cohort strata; GSE174188 transcription used sample-cohort
`B_CONV` pseudobulks; GSE135779 used donor-level broad conventional-B pseudobulks.

### 3.2 Identity and composition

Identity representations were evaluated with marker conservation, technical mixing,
bridge coverage and 20 disease-blind resamples. Failure of fine states was retained.
Composition used supported cohort-specific conditional-binomial models, minimum 50
cells per stratum, HC1 checks, threshold sensitivities and leave-one-sample-out
analysis. No cell-level disease test was used.

### 3.3 Pseudobulk transcription and frozen programs

Raw counts were summed within biological units after count conservation. edgeR used
`filterByExpr`, TMM normalization and robust quasi-likelihood models. Frozen program
scores were computed from standardized TMM log-counts per million and tested with
HC3 linear models. Benjamini-Hochberg correction was applied across four
confirmatory programs. Support-threshold, residual-risk and leave-one-out branches
were prespecified.

### 3.4 Independent validation

GSE135779 source labels, donor availability, program genes and minimum-cell designs
were frozen before disease effects were calculated. Synthetic null and signal data
qualified the engine. Donor-deletion, source-label omission, technical-family and
shared-tested-gene analyses distinguished stable program replication from broad
transcriptome concordance.

### 3.5 Regulatory and orthogonal response analysis

Human CollecTRI was frozen from OmniPath. For each tested feature, the ranked
statistic was `sign(logFC) * sqrt(F)`; duplicate uppercase gene symbols were averaged.
A linear model with an intercept estimated the activity slope on signed target
weights. Eight regulators across three contrasts formed one 24-test global
Benjamini-Hochberg family. Core STAT1/STAT2 models underwent leave-one-target and
100 x 80% target-resampling analyses.

MSigDB 2026.1.Hs M5911 used 10,000 deterministic gene-label permutations per ranked contrast.
GSE23307 paired untreated and IFN-beta-exposed primary B-cell probes were transformed
as log2(x+1), median-collapsed to 12 genes and differenced within two donors. No
inferential P value was calculated at n=2. Superseded untransformed outputs are
audit-only and excluded from active evidence.

## 4. Completed evidence chain and claim hierarchy

| Layer | Result | Publication role |
|---|---|---|
| Identity | `B_CONV`/`B_ASC` pass; fine states fail | foundation and scope boundary |
| Composition | primary `B_ASC` null | negative boundary |
| Discovery | GSE174188 IFN/ISG positive | central association |
| Internal replication | donor-nonoverlap IFN/ISG positive | within-accession support |
| Independent replication | GSE135779 childhood IFN/ISG positive | central external evidence |
| Regulatory convergence | STAT1/STAT2 target activity reproduced | central noncausal support |
| Orthogonal response | M5911 and two-donor IFN-beta direction | supportive convergence |

The main paper is ordered in this inferential sequence. Each stronger claim depends
on the earlier scope boundary and cannot be used to retroactively redefine identity.

## 5. Limitations and alternatives

Public covariates are incomplete and differ across accessions. Adult GSE135779 is
underpowered. Source-label mapping supports a broad analog, not exact subtype
transfer. GSE174188 internal validation remains within the same accession. Regulon
activity depends on prior-network coverage and is not direct binding evidence.
GSE23307 has only two donors and a healthy ex vivo context. These limitations are
handled by preserving cohort-specific designs, reporting negative boundaries,
using independent program-level replication and prohibiting causal language.

Prospective patient sampling, matched clinical covariates, direct chromatin or
binding assays and replicated perturbation of patient-derived B cells would be
needed to advance from convergent regulation to mechanism.

## 6. Milestones and decision gates

| Gate | Deliverable | Final status |
|---|---|---|
| C2B4 | disease-blind two-compartment identity | passed; scope frozen |
| C3A | sample-level composition | passed; central composition claim rejected |
| C4B | GSE174188 pseudobulk and programs | passed; IFN prioritized |
| C5A-C5B | independent GSE135779 validation | passed; IFN replicated |
| C6A | claim and number freeze | passed |
| C6B | regulatory and orthogonal evidence | passed; noncausal framing authorized |
| C7 | five main figures and manuscript integration | completed by v9/v16 package |
| C8 | journal-specific submission package | next stage |

## 7. Expected impact

The project provides a reproducible framework for distinguishing identity,
composition and transcription in heterogeneous public single-cell studies. Its SLE
advance is a tightly bounded but substantive result: an independently replicated
IFN program within broad conventional B cells, supported by prespecified
cross-dataset regulatory activity and orthogonal response evidence despite low
genome-wide concordance. Transparent negative results prevent unstable subtype and
composition narratives from inflating the conclusion.

## 8. Binding writing boundaries

- Use broad conventional-B compartment, not a hard naive, memory or atypical subtype.
- Describe relative `B_ASC` abundance, not absolute expansion or depletion.
- Reserve independent replication for GSE135779 IFN/ISG.
- Describe the adult estimate as positive but underpowered.
- State that replication is program-specific and genome-wide agreement is low.
- Use convergent observational IFN-centred regulatory evidence.
- Do not claim direct binding, a unique IFN ligand, mechanism, causality or a new subtype.
- Cite only corrected log2(x+1) GSE23307 outputs 16-20; files 10-14 are superseded audit artifacts.

## References

1. Perez RK et al. *Science*. 2022. doi:10.1126/science.abf1970.
2. Nehar-Belaid D et al. *Nature Immunology*. 2020. doi:10.1038/s41590-020-0743-0.
3. Crowell HL et al. *Nature Communications*. 2020. doi:10.1038/s41467-020-19894-4.
4. Squair JW et al. *Nature Communications*. 2021. doi:10.1038/s41467-021-25960-2.
5. Badia-I-Mompel P et al. *Bioinformatics Advances*. 2022. doi:10.1093/bioadv/vbac016.
6. Muller-Dott S et al. *Nucleic Acids Research*. 2023. doi:10.1093/nar/gkad841.
7. Liberzon A et al. *Cell Systems*. 2015. doi:10.1016/j.cels.2015.12.004.
8. van Boxel-Dezaire AHH et al. *Journal of Immunology*. 2010;185:5888-5899. doi:10.4049/jimmunol.0902314.
"""


def build_crosswalks(root: Path, run_dir: Path) -> tuple[Path, Path, Path]:
    old_claims = pd.read_csv(root / "phase17_v7/gateC6A/20260815_claim_integration/01_CLAIM_TO_EVIDENCE_MATRIX.csv")
    rows = old_claims.to_dict("records")
    for row in rows:
        if row["claim_id"] == "C6A-11":
            row.update(
                {
                    "claim_id": "C7-11",
                    "tier": "central_support",
                    "claim": "Prespecified IFN-centred regulator activity converges across all three confirmatory contrasts.",
                    "status": "authorized_noncausal",
                    "evidence": "STAT1 and STAT2 positive and global-q significant in all three contrasts; core target deletion and 100x80% resampling pass.",
                    "analysis_unit": "tested-gene ranked statistics within three frozen donor/sample-level contrasts",
                    "source": "phase17_v7/gateC6B/20260815_regulatory_evidence/24_GATE_C6B_FINAL_AUDIT.json",
                    "allowed_wording": "convergent observational IFN-centred regulatory evidence",
                    "prohibited_wording": "mechanistic validation; causal regulator; unique upstream stimulus",
                    "manuscript_location": "Results 5; Discussion; Figure 5",
                }
            )
        else:
            row["claim_id"] = row["claim_id"].replace("C6A-", "C7-")
    rows.extend(
        [
            {
                "claim_id": "C7-12",
                "tier": "orthogonal_support",
                "claim": "The exact M5911 IFN response is positively enriched in all three confirmatory contrasts.",
                "status": "authorized_supporting_only",
                "evidence": "NES 3.187, 3.050 and 3.527; 10,000 gene-label permutations per contrast.",
                "analysis_unit": "complete ranked tested-gene tables",
                "source": "phase17_v7/gateC6B/20260815_regulatory_evidence/19_MSIGDB_M5911_PRERANKED_GSEA.csv",
                "allowed_wording": "orthogonal response-signature convergence",
                "prohibited_wording": "independent patient cohort; causal IFN-alpha proof",
                "manuscript_location": "Results 5; Figure 5d",
            },
            {
                "claim_id": "C7-13",
                "tier": "orthogonal_support",
                "claim": "IFN-beta exposure increases the frozen 12-gene arm in primary B cells from both GSE23307 donors.",
                "status": "authorized_descriptive_only",
                "evidence": "12/12 positive in HI1 and HI2; mean paired log2(x+1) effects 3.294 and 3.666.",
                "analysis_unit": "paired gene effect within two healthy donors",
                "source": "phase17_v7/gateC6B/20260815_regulatory_evidence/18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv",
                "allowed_wording": "small paired perturbational direction",
                "prohibited_wording": "powered validation; SLE patient replication; inferential significance",
                "manuscript_location": "Results 5; Figure 5e",
            },
            {
                "claim_id": "C7-14",
                "tier": "binding_boundary",
                "claim": "Regulatory convergence does not establish direct binding, a unique initiating ligand or causation in SLE.",
                "status": "required_boundary",
                "evidence": "Observational target activity; response-set enrichment; healthy-donor perturbation n=2.",
                "analysis_unit": "cross-layer interpretation",
                "source": "phase17_v7/gateC6B/20260815_regulatory_evidence/24_GATE_C6B_FINAL_AUDIT.json",
                "allowed_wording": "observational noncausal regulatory evidence",
                "prohibited_wording": "STAT1/STAT2 causes SLE B-cell remodeling",
                "manuscript_location": "Abstract; Results 5; Discussion",
            },
        ]
    )
    claim_path = run_dir / "02_CLAIM_NUMBER_CROSSWALK.csv"
    pd.DataFrame(rows).to_csv(claim_path, index=False, quoting=csv.QUOTE_MINIMAL)

    figure_rows = [
        ["Figure1", "a-d", "identity scope and stability", "gateC2B4; gateC3 metadata", "Figure1_source_data.csv", "C7-01;C7-02"],
        ["Figure2", "a-d", "sample-level B_ASC composition", "gateC3A", "Figure2_source_data.csv", "C7-03"],
        ["Figure3", "a-d", "GSE174188 B_CONV transcription", "gateC4B; gateC5B cross-gene table", "Figure3_source_data.csv", "C7-04;C7-05;C7-09"],
        ["Figure4", "a-d", "independent GSE135779 IFN replication", "gateC5B", "Figure4_source_data.csv", "C7-06;C7-07;C7-08;C7-10"],
        ["Figure5", "a-e", "noncausal regulatory convergence", "gateC6B corrected active outputs", "Figure5_source_data.csv", "C7-11;C7-12;C7-13;C7-14"],
    ]
    figure_path = run_dir / "03_FIGURE_SOURCE_CROSSWALK.csv"
    pd.DataFrame(
        figure_rows,
        columns=["figure", "panels", "inference", "frozen_gate_sources", "gateC7_source_data", "claim_ids"],
    ).to_csv(figure_path, index=False)

    old_numbers = pd.read_csv(root / "phase17_v7/gateC6A/20260815_claim_integration/02_MANUSCRIPT_NUMERIC_SOURCE.csv")
    new_numbers = pd.DataFrame(
        [
            ["c6b_m5911_discovery_nes", 3.186802649601297, "3.187", "phase17_v7/gateC6B/20260815_regulatory_evidence/19_MSIGDB_M5911_PRERANKED_GSEA.csv", "normalized_enrichment_score", "orthogonal support"],
            ["c6b_m5911_nonoverlap_nes", 3.0498612816254838, "3.050", "phase17_v7/gateC6B/20260815_regulatory_evidence/19_MSIGDB_M5911_PRERANKED_GSEA.csv", "normalized_enrichment_score", "orthogonal support"],
            ["c6b_m5911_childhood_nes", 3.5271419267951707, "3.527", "phase17_v7/gateC6B/20260815_regulatory_evidence/19_MSIGDB_M5911_PRERANKED_GSEA.csv", "normalized_enrichment_score", "orthogonal support"],
            ["c6b_gse23307_hi1_mean", 3.293570512080079, "3.294", "phase17_v7/gateC6B/20260815_regulatory_evidence/18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv", "mean_paired_log2p1_effect", "descriptive perturbation"],
            ["c6b_gse23307_hi2_mean", 3.665668905432541, "3.666", "phase17_v7/gateC6B/20260815_regulatory_evidence/18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv", "mean_paired_log2p1_effect", "descriptive perturbation"],
            ["c6b_confirmatory_tests", 24, "24", "phase17_v7/gateC6B/20260815_regulatory_evidence/24_GATE_C6B_FINAL_AUDIT.json", "confirmatory_exact_24_unique", "multiplicity family"],
        ],
        columns=old_numbers.columns,
    )
    numeric_path = run_dir / "04_MANUSCRIPT_NUMERIC_SOURCE.csv"
    pd.concat([old_numbers, new_numbers], ignore_index=True).to_csv(numeric_path, index=False)
    return claim_path, figure_path, numeric_path


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    run_dir = root / RUN_REL
    run_dir.mkdir(parents=True, exist_ok=True)
    manuscript_path, legends_path = build_manuscript(root)
    proposal_path = root / "01_manuscript/research_proposal_v16_gateC7_completed_2026-08-20.md"
    write_text(proposal_path, proposal_text())
    claim_path, figure_path, numeric_path = build_crosswalks(root, run_dir)
    status = {
        "created_at": "2026-08-20",
        "status": "C7_TEXT_AND_CROSSWALKS_BUILT_AUDIT_REQUIRED",
        "manuscript": manuscript_path.relative_to(root).as_posix(),
        "research_proposal": proposal_path.relative_to(root).as_posix(),
        "figure_legends": legends_path.relative_to(root).as_posix(),
        "claim_crosswalk": claim_path.relative_to(root).as_posix(),
        "figure_crosswalk": figure_path.relative_to(root).as_posix(),
        "numeric_source": numeric_path.relative_to(root).as_posix(),
        "claim_boundary": "convergent observational IFN-centred regulatory evidence; noncausal",
    }
    write_text(run_dir / "05_TEXT_INTEGRATION_STATUS.json", json.dumps(status, indent=2))
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
