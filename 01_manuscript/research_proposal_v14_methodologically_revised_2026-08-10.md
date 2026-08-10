# MBI6013 Research Proposal

## Donor- and cohort-resolved single-cell analysis of compositional and transcriptional B-cell remodeling in systemic lupus erythematosus

**Methodologically revised version 14**  
**Date:** 10 August 2026  
**Study type:** secondary analysis of public human single-cell transcriptomic data

## Project overview

Systemic lupus erythematosus (SLE) is associated with altered B-cell
differentiation, interferon activation and expansion of antibody-secreting and
atypical B-cell compartments. Single-cell studies can resolve these processes,
but two biologically different phenomena are often conflated: changes in the
relative abundance of B-cell states and changes in gene expression within the
same state. In addition, cell-level inference, outcome-informed annotation and
imbalanced technical cohorts can produce apparently strong but poorly
generalizable disease signals.

This project will reanalyse a large public SLE single-cell dataset from audited
raw counts using a donor-, sample-, library- and cohort-resolved design. B-cell
states will be reconstructed and annotated without access to disease outcomes.
After those states are frozen, SLE-associated composition and within-state
transcription will be estimated separately at the biological-sample level.
Discovery definitions will then be applied without refitting to an independent
SLE dataset. The project is designed to produce an honest hierarchy of robust,
cohort-specific and inconclusive findings rather than to force all evidence
into a single pathogenic-cell narrative.

## 1. Background and significance

SLE is a heterogeneous autoimmune disease in which loss of B-cell tolerance,
autoantibody production, innate immune sensing and type I interferon signalling
interact across patients and disease stages. Peripheral B-cell abnormalities
include changes in naive and memory compartments, expansion of plasmablasts and
antibody-secreting cells, and enrichment of CD11c-high, T-bet-positive or
double-negative phenotypes [1-4]. These populations are biologically relevant,
but their nomenclature and boundaries vary across studies [5]. A transcriptional
cluster should therefore not be labelled pathogenic merely because it is
enriched in cases or resembles a literature signature.

Perez et al. profiled more than 1.2 million peripheral blood mononuclear cells
from SLE cases and controls and demonstrated cell-type-specific disease and
genetic associations [1]. The resource is unusually valuable for B-cell
analysis because it includes many donors, samples and multiplexed libraries.
The same complexity also creates a statistical challenge: technical processing
cohorts are not uniformly balanced for disease, some donors contribute repeated
samples, and biological samples are distributed across multiple libraries.
Pooled cell-level tests or a single cohort-adjusted disease coefficient can
therefore confound disease with design structure.

Single-cell disease analysis also requires a sharp distinction between
composition and cell-intrinsic state. An increased number of cells expressing
an interferon program may result from expansion of an interferon-high state,
upregulation of interferon genes within several stable states, or both.
Subpopulation-specific pseudobulk methods were developed precisely because
cells from the same individual are not independent replicates [6,7]. Likewise,
cell-state abundance is compositional: an increase in one state necessarily
changes the relative abundance of others, motivating sample-level models and
compositional sensitivity analyses [8].

Mechanistic studies nominate plausible regulators of atypical or age-associated
B-cell programs. ZEB2 is required for age-associated B-cell differentiation,
and TLR7-FTO-linked metabolic regulation can promote this fate [2,3]. These
studies provide valuable biological priors. However, overlap with a ZEB2 or
TBX21 signature in observational single-cell data does not establish causal
regulation. The proposed work will therefore treat pathway and regulon evidence
as hypothesis prioritization and reserve causal language for perturbational or
strong causal-genetic evidence.

The significance of the project lies in its inferential separation of three
questions: which B-cell states can be reconstructed without disease knowledge;
which of those states change in abundance within cohorts that support a direct
case-control contrast; and which states change transcription internally. This
framework can clarify apparently conflicting B-cell findings and can remain
informative even when a visually distinctive state fails external replication.

## 2. Central hypothesis and specific aims

### Central hypothesis

SLE remodels peripheral B cells through separable changes in the abundance of
neutral B-cell states and in transcription within those states. The two layers
will show different magnitudes and different degrees of external
reproducibility.

### Aim 1. Reconstruct stable, disease-blind B-cell states from audited raw counts

**Rationale.** Outcome-informed labels and inherited whole-PBMC embeddings can
make disease enrichment circular. A de novo B-cell representation is required
before disease comparisons.

**Approach.** Hard-QC-passing B cells will be extracted from the authoritative
raw counts, with a full-PBMC marker audit checking extraction completeness.
Residual doublet risk will be scored per complete library without automatic
re-deletion. PCA, unintegrated and Harmony-adjusted graphs, UMAP and Leiden
clustering will be rebuilt within B cells. Neutral states will be frozen using
markers, biological/technical coverage, bridge-sample concordance and
resampling; an ISG-excluded reconstruction will test identity stability while
disease fields remain physically separated.

**Expected outcome.** A reproducible neutral B-cell reference with explicit
state uncertainty, technical-contaminant flags and a frozen mapping object for
external data.

### Aim 2. Separate SLE-associated composition from within-state transcription

**Rationale.** State abundance and state-internal expression represent distinct
biological processes and require different sample-level models.

**Approach.** State counts will be aggregated by biological sample for
cohort-resolved compositional models. Raw counts will be aggregated by sample
and frozen state for pseudobulk SLE-control differential expression. The main
contrast will be restricted to strict single-processing-cohort samples in the
processing cohort with adequate case-control support; a second supported cohort
will be analysed separately as exploratory. A global composition test will
precede state-specific effects.
Pathway and regulon analyses will be applied to ranked within-state disease
effects, not to state-marker contrasts.

**Expected outcome.** A state-by-process map that distinguishes
composition-dominant, transcription-dominant, concordant and unsupported B-cell
signals in SLE.

### Aim 3. Test frozen discovery states and signatures in independent SLE data

**Rationale.** Recomputing labels or thresholds inside validation data can
convert validation into a second discovery analysis.

**Approach.** A discovery-only classifier or reference-mapping model will be
evaluated by donor-stratified cross-validation and frozen with an uncertainty
rule. It will then be applied to GSE135779 without refitting to disease labels.
Mapped state abundance and prespecified within-state/signature effects will be
tested separately in childhood and adult strata before any combined estimate.
GSE163121 will provide directional evidence only because
of its small sample size, and OneK1K will be used only as healthy reference
context.

**Expected outcome.** A transparent replication scorecard separating replicated,
directionally consistent, inconclusive and non-replicated findings.

## 3. Preliminary data and feasibility

No original wet-lab data are claimed. All results below arise from local audits
and disease-blind feasibility analyses of public data.

### 3.1 Authoritative discovery object

The B-cell source object contains 152,981 cells and 30,172 genes. The audited
`raw/X` matrix is non-negative and integer-valued. Metadata identify 259 donors,
271 biological samples, 88 technical libraries and four processing cohorts.
Eleven donors have repeated samples, all samples are multiplexed across multiple
libraries, and 53 samples bridge processing cohorts. These observations define
the sample as the biological unit, the donor as a correlation unit and the
library as a technical unit.

### 3.2 Common-support audit

Disease is strongly imbalanced across processing cohorts. In the ambiguity-free
subset of donors represented by exactly one biological sample and one processing
cohort (n = 195), normal/SLE counts are 28/0, 1/87, 5/8 and 41/25 in cohorts
1-4, respectively. Cohort 4 is the primary direct comparison, cohort 3 is
exploratory, and cohorts 1-2 are discovery-only strata. This programmatically
reproduced audit prevents a misleading pooled disease effect.

### 3.3 Full raw-count preparation

Frozen hard-QC rules retained 150,402 cells and all 30,172 genes in a new
disease-blind full object. The object contains only source cell index, donor,
sample, library and processing cohort. Disease, disease state and `ct_cov` are
stored separately. A read-back audit confirmed integer raw counts and no
protected-field leakage.

### 3.4 Disease-blind smoke reconstruction

A 20,000-cell smoke analysis recovered coherent naive-like, memory-like,
atypical-like and plasmablast-like marker structure. Harmony reduced local
same-library, same-sample and same-processing-cohort neighbor fractions. At a
diagnostic Leiden resolution of 0.6, all seven provisional clusters were
represented across many donors and libraries. This supports feasibility of a
full representation rebuild.

The smoke run also exposed an important failure mode: Scrublet was applied after
balanced sampling and predicted an implausibly high median doublet fraction of
14.8% per library. These calls have been rejected for freezing. The corrected
workflow now runs Scrublet on complete libraries before any sampling or graph
construction. This negative result demonstrates that the gate system is
preventing an analysis artifact from entering the manuscript.

## 4. Research design and methods

### 4.1 Data resources

| Role | Resource | Intended use | Interpretive boundary |
|---|---|---|---|
| Discovery | Perez et al., GSE174188 [1] | state reconstruction, composition and within-state DE | disease contrasts restricted by cohort support |
| Main validation | GSE135779 [9] | frozen state mapping and sample-level replication | no threshold refitting in validation |
| Directional validation | GSE163121 | direction and marker context | two controls and three SLE samples; not confirmatory |
| Healthy reference | OneK1K [10] | B-cell maturation and population context | not SLE replication |
| Mechanistic context | ZEB2, FTO/TLR7 and EBV/APC studies [2,3,11] | candidate-regulator interpretation | observational overlap is not causality |

### 4.2 Source integrity and quality control

The source path, SHA256 checksum, matrix dimensions, matrix encoding and
metadata dictionaries will be recorded before analysis. Hard-QC thresholds are
frozen at at least 500 total counts, at least 200 detected genes, no more than
10% mitochondrial counts, no more than 1% haemoglobin counts, no more than 0.5%
platelet-marker counts, and detection of at least one B-lineage marker. Every
cell receives a reason-level QC record; no source file is overwritten.

These thresholds are intentionally conservative because the source object is an
already extracted B-cell compartment. A lightweight full-PBMC B-marker audit
will test whether a material B-like population was excluded by source labels.
Distributional plots and state-specific
retention will be examined to ensure that plasmablasts or other high-RNA states
are not preferentially removed. The all-hard-QC branch will remain available
for sensitivity analysis.

### 4.3 Complete-library doublet assessment

Because the source workflow already applied donor demultiplexing and doublet
handling, Scrublet will be rerun per complete library only as a residual-risk
diagnostic with a prespecified expected rate and deterministic seed. Cell scores, automatic
thresholds, predicted rates and failures will be retained. Automatic calls will
not be applied until rate distributions and mixed-lineage marker enrichment are
reviewed. Analyses will compare approved singlets with all hard-QC cells. A
library with an extreme rate will trigger diagnostic review rather than an
arbitrary rate cap.

### 4.4 Disease-blind representation and batch assessment

Library-aware recurrent highly variable gene selection will be performed on normalized
log expression while preserving raw counts for pseudobulk. PCA and a neighbor
graph will first be generated without integration. Harmony will then adjust the
PCA representation using technical library. Both representations will be
retained.

Integration quality will be evaluated with local neighbor mixing for library,
sample and processing cohort, bridge-sample consistency and conservation of
known B-cell marker structure. Harmony will not be used to infer disease effects
or to erase processing-cohort restrictions. A representation will pass only if
technical mixing improves without collapsing biologically coherent rare states.
An otherwise matched reconstruction excluding strong interferon-stimulated
genes will test whether state identity is stable rather than merely an IFN
activation gradient.

### 4.5 State definition and freeze

Leiden clustering will be evaluated across a prespecified resolution grid.
Candidate states must satisfy four criteria: coherent canonical markers,
representation across biological samples and donors, absence of dominance by a
single library, and assignment stability under cell resampling or graph
perturbation. Platelet-, erythroid- or mixed-lineage-enriched clusters will be
flagged as technical/contaminant states rather than forced into B-cell biology.

Neutral names such as `naive`, `memory`, `atypical-like` and `plasmablast` may
be assigned only after marker review. Disease-enriched names are prohibited.
State IDs, names, marker sets, excluded states and the external mapping model
will be versioned and frozen before protected outcomes are joined.

### 4.6 Cohort-resolved composition

For each biological sample, the number of cells in every frozen state and the
total number of eligible B cells will be calculated. The primary per-state
analysis will use a beta-binomial mixed model of state versus other-B-cell
counts within processing cohort 4, with disease and prespecified covariates and
a donor random intercept for repeated samples where identifiable. A global
sample-level compositional test will precede state-specific interpretation.

Bridge samples will be reserved for technical concordance and excluded from the
primary disease coefficient. Processing cohort 3 will be analysed separately as
exploratory. Cohorts 1 and 2
will not contribute a direct disease coefficient. Sensitivities will retain one
sample per donor, vary minimum cell requirements, compare approved singlets
with all hard-QC cells, and use a centered-log-ratio or Bayesian compositional
method such as scCODA [8]. Effects, intervals and false-discovery-rate-adjusted
P values will be reported; cells will never be treated as independent disease
replicates.

### 4.7 Sample-by-state pseudobulk differential expression

Raw counts will be summed by biological sample and frozen state after technical
library contributions from the same sample are combined. Sample-state strata
must meet a prespecified minimum cell count. Lowly expressed genes will be
filtered using pseudobulk expression, followed by TMM normalization and a
voom-dream or equivalent model that accounts for donor correlation. The primary
cohort 4 disease coefficient and the exploratory cohort 3 coefficient will be
estimated separately.

This contrast tests SLE versus control within a fixed state. State-versus-state
marker tests will be retained only for annotation. Multiple testing families
will be declared before results are interpreted. Sample influence, mean-variance
fit and residual diagnostics will be inspected.

### 4.8 Pathway and regulatory interpretation

Gene-set enrichment will use ranked within-state disease effects and curated
Hallmark, Gene Ontology and immune pathways. Regulon activity may be estimated
with a curated resource such as DoRothEA/decoupleR. Candidate regulators will be
ranked by convergence across within-state DE, regulon activity, external
direction and published mechanistic evidence. This ranking will generate testable
hypotheses; it will not be described as genetic or experimental validation.

### 4.9 Frozen external validation

A state mapper will be trained exclusively in discovery data using intersecting
genes. Donor-stratified cross-validation will quantify class discrimination,
calibration and uncertainty. Low-confidence cells will be assigned `unmapped`
rather than forced into a discovery state. All coefficients, marker signatures,
directions and thresholds will be frozen before external outcomes are examined.

In GSE135779, mapping quality will first be evaluated without disease
comparison. Childhood and adult strata will then be estimated separately for
sample-level state abundance and within-state or signature effects using the
same direction convention as discovery, followed by compatibility assessment
or a prespecified meta-effect where justified. A finding
will be termed replicated only if mapping quality is acceptable, the direction
was prespecified and the external sample-level estimate supports that direction.
Otherwise it will be classified as directional, inconclusive or not replicated.

### 4.10 Reproducibility and outcome lock

The workflow uses timestamped run directories, immutable source objects,
checksums, deterministic seeds, environment files and tidy Source Data tables.
Analysis proceeds through four freezes: cells/representation, neutral states,
discovery outcomes and external validation. Protected outcomes are joined only
after the neutral-state freeze. Existing v6 outputs remain archived for
provenance and will not be overwritten or manually altered to match v7.

## 5. Expected results and interpretation

The expected primary contribution is not necessarily the discovery of a new
B-cell subtype. Rather, the study should reveal whether prominent SLE B-cell
signals are driven by abundance, within-state activation or both. A robust
interferon-associated transcriptional signal may reproduce even if an
atypical-like abundance effect is cohort specific. Conversely, a stable
composition change may occur without a large within-state transcriptional
effect. Either outcome would clarify the level at which SLE remodels B cells.

The highest-impact outcome would combine a stable neutral state, a supported
cohort 4 composition or within-state effect, a directionally consistent cohort
3 estimate and frozen external replication in GSE135779. A negative external
result will still be informative if the mapper is well calibrated and the
discovery design is rigorous, because it will delimit generalizability and
prevent a cohort-specific observation from being promoted as universal.

## 6. Potential difficulties and alternatives

**Extreme doublet rates.** Automatic thresholds may fail in individual
libraries. Scores and mixed-lineage enrichment will be reviewed, and all-hard-QC
and approved-singlet branches will be compared. Rates will not be clipped to a
desired value.

**Over-integration.** Harmony may remove real biology. Unintegrated and Harmony
representations will be compared, bridge samples will provide technical
diagnostics, and final states must retain marker coherence in both views.

**Rare states.** A rare cluster may lack enough sample-state strata for
pseudobulk. It may be merged only when marker and stability evidence support a
broader state; otherwise it will remain descriptive and excluded from formal
disease DE.

**Residual cohort confounding.** No global pooled disease coefficient will be
used. Primary and exploratory cohorts will be reported separately, and cohorts
without both groups will not estimate disease effects.

**Repeated donors and incomplete covariates.** Mixed models and one-sample-per-
donor sensitivity will address repeated samples. Covariates will be included
only when measured consistently and supported within the analysis cohort; they
will not be imputed merely to obtain a more complex model.

A paired repeated-donor analysis may follow the core freeze but will not be
interpreted as treatment-causal because time, activity and therapy may co-vary.

**External mapping failure.** Low-confidence cells will be allowed to abstain.
If exact state transfer is not supported, validation will be restricted to
frozen gene-set activity and clearly described as program-level rather than
state-level replication.

**No mechanistic validation.** Public observational data cannot establish
causality. The final study will prioritize a short regulator list for future
perturbation in primary B cells or appropriate models.

## 7. Milestones and decision gates

| Phase | Deliverable | Pass criterion |
|---|---|---|
| Gate C2B1 | complete-library doublet diagnostics | interpretable rate/score distributions and approved cell policy |
| Gate C2B2 | full disease-blind representation | improved technical mixing with conserved B-cell biology |
| Gate C2C | frozen neutral states | marker coherence, broad coverage and resampling stability |
| Gate C3 | composition and pseudobulk outcomes | valid cohort-specific sample-level models and diagnostics |
| Gate C4 | independent validation | frozen mapping quality and prespecified replication scorecard |
| Manuscript freeze | five main figures, Source Data and v7 text | every claim linked to a frozen table and analysis unit |

## 8. Expected impact

The proposed work will provide a reusable framework for separating cellular
composition from state-internal disease biology in complex public single-cell
datasets. For SLE, it will clarify which B-cell observations are robust across
samples and cohorts, which are mainly transcriptional, and which remain
context-dependent. The resulting claim hierarchy should be suitable for a
high-quality genomics or computational-biology journal and will define a focused
set of hypotheses for future functional validation.

## References

1. Perez RK et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. *Science*. 2022. doi:10.1126/science.abf1970.
2. Dai D et al. The transcription factor ZEB2 drives the formation of age-associated B cells. *Science*. 2024. doi:10.1126/science.adf8531.
3. Zeng Q et al. The m6A demethylase FTO links TLR7 to mitochondrial oxidation driving age-associated B cell formation in systemic lupus erythematosus. *Science Translational Medicine*. 2025. doi:10.1126/scitranslmed.adu6015.
4. Jenks SA et al. Distinct effector B cells induced by unregulated Toll-like receptor 7 contribute to pathogenic responses in systemic lupus erythematosus. *Immunity*. 2018. doi:10.1016/j.immuni.2018.08.015.
5. Sanz I et al. Challenges and opportunities for consistent classification of human B cell and plasma cell populations. *Frontiers in Immunology*. 2019. doi:10.3389/fimmu.2019.02458.
6. Crowell HL et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. *Nature Communications*. 2020. doi:10.1038/s41467-020-19894-4.
7. Squair JW et al. Confronting false discoveries in single-cell differential expression. *Nature Communications*. 2021. doi:10.1038/s41467-021-25960-2.
8. Buttner M et al. scCODA is a Bayesian model for compositional single-cell data analysis. *Nature Communications*. 2021. doi:10.1038/s41467-021-27150-6.
9. Nehar-Belaid D et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. *Nature Immunology*. 2020. doi:10.1038/s41590-020-0743-0.
10. Yazar S et al. Single-cell eQTL mapping identifies cell type-specific genetic control of autoimmune disease. *Science*. 2022. doi:10.1126/science.abf3041.
11. Younis S et al. Epstein-Barr virus reprograms autoreactive B cells as antigen-presenting cells in systemic lupus erythematosus. *Science Translational Medicine*. 2025. doi:10.1126/scitranslmed.ady0210.
