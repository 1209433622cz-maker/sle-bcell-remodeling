# Advisor-level full project reassessment

**Date:** 10 August 2026  
**Target tier:** SCI Q1; journal not yet locked  
**Current submission decision:** NO-GO  
**Active analysis generation:** v7 / Phase 17

## Executive judgement

The project has a strong public-data foundation, a reproducible audit trail and
a biologically important question. It is not yet submission-ready because the
current v6 claims and figures were built on an analysis design that does not
fully respect the sample-donor-library hierarchy, common support across
processing cohorts, disease-blind state definition or the distinction between
cell-state identity and disease-associated differential expression.

The project should continue, but as a principled v7 reanalysis from the
authoritative raw counts. The defensible central question is:

> Does SLE remodel peripheral B cells primarily by changing the abundance of
> neutral B-cell states, by changing transcription within those states, or by
> both processes in cohort-reproducible ways?

This question is narrower than the old mechanistic proposal and substantially
stronger statistically. It also creates a coherent path from study design to
state reconstruction, composition, within-state expression and frozen external
validation.

## Evidence baseline

### Authoritative discovery source

- File: `Data/processed/GSE174188_perez_cellxgene/bcell_subset_full.h5ad`
- Authoritative matrix: `raw/X`
- Source SHA256: `fbd4692e033a57412fcc9dfe761180a9e4bdae37c4fda8f5ecc2e28fde46371b`
- Audited source dimensions: 152,981 B-lineage cells and 30,172 genes
- Matrix properties: non-negative, integer-valued raw counts
- Metadata hierarchy: 259 donors, 271 biological samples, 88 technical
  libraries and four processing cohorts
- Repeated structure: 11 donors contribute more than one sample; samples are
  multiplexed across libraries; 53 samples bridge processing cohorts

### Full v7 hard-QC extraction

- New file: `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad`
- Output SHA256: `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5`
- Dimensions: 150,402 cells by 30,172 genes
- Protected-field check: `disease`, `disease_state` and `ct_cov` are absent
  from the working AnnData
- Raw-count check: sampled non-zero values are non-negative integers

### Gate C2A smoke evidence

The 20,000-cell disease-blind smoke run supports full representation learning,
but it does not freeze doublet calls or final cell states.

- Provisional embedding retained 16,996 cells after smoke-only Scrublet calls.
- Harmony reduced mean same-library neighbor fraction from 0.0670 to 0.0146,
  same-processing-cohort fraction from 0.6655 to 0.4318 and same-sample
  fraction from 0.0443 to 0.0168.
- At Leiden resolution 0.6, seven clusters were recovered. Every cluster
  included at least 97 donors and 72 libraries; the maximum contribution of a
  single library was 4.4%.
- Neutral marker modules recovered naive-like, memory-like, atypical-like,
  plasmablast-like and platelet-contaminated structures.
- Adjacent-resolution adjusted Rand indices ranged from 0.251 to 0.674. This
  supports biological recoverability but is insufficient to freeze resolution.
- Smoke Scrublet predicted 15.0% doublets overall; the median library rate was
  14.8%, the maximum was 43.7%, and 17 libraries exceeded 20%.

The doublet rates are rejected for freezing because balanced smoke sampling
preceded per-library Scrublet. Complete libraries must be scored first.

## Findings that invalidate direct v6 submission

### 1. Representation is not B-cell de novo reconstruction

The main v6 landscape inherited source PBMC PCA/UMAP coordinates. It therefore
cannot establish a B-cell-specific state architecture reconstructed from the
audited raw counts. The v7 analysis must rebuild HVGs, PCA, neighbor graphs,
UMAP and Leiden clusters within the B-cell compartment.

### 2. State labels are partly outcome-informed

Labels such as `SLE-naive-like` embed disease knowledge into the state
definition and then reuse those states in disease comparisons. This creates a
double-dipping risk. v7 labels must be neutral and frozen using markers,
coverage and stability before disease outcomes are unlocked.

### 3. Disease and processing cohort lack global common support

In the ambiguity-free subset of donors represented by exactly one biological
sample and one processing cohort (n = 195), the disease distribution is:

| Processing cohort | Normal | SLE | Interpretation |
|---|---:|---:|---|
| 1 | 28 | 0 | no direct disease contrast |
| 2 | 1 | 87 | no credible direct disease contrast |
| 3 | 5 | 8 | exploratory contrast only |
| 4 | 41 | 25 | primary direct comparison |

A pooled disease coefficient with cohort dummy variables cannot repair the
absence of overlap. Cohort 4 is the primary disease comparison; cohort 3 is an
exploratory replication; cohorts 1 and 2 contribute state discovery and
technical assessment only.

### 4. The old abundance model uses the wrong aggregation level

Prior donor aggregation merged repeated biological samples. The biological
unit is the sample, with donor correlation handled explicitly. Library is a
technical unit and processing cohort is a design/selection factor, not a
substitute for biological replication.

### 5. The old pseudobulk contrast is not disease differential expression

The prior `focus state versus mean of other states within donor` contrast tests
cell-state identity. It does not test SLE versus control within a fixed state.
v7 needs sample-by-frozen-state raw-count pseudobulk and a disease coefficient
within supported cohorts.

### 6. External validation supports less than the current narrative claims

GSE135779 robustly supports interferon activation and provides limited or
borderline support for the ZEB2 axis. Existing scoring did not map a frozen
discovery state and recalculated an HC-derived threshold inside validation.
It therefore does not independently replicate an expanded ABC/APC-like state.
GSE163121 has only two controls and three SLE samples and is directional only.
OneK1K is a healthy population reference, not SLE replication. Existing
colocalization is negative or insufficient and cannot support causal mechanism.

## Binding v7 analysis design

### Disease-blind state reconstruction

1. Apply frozen hard QC to `raw/X`.
2. Run Scrublet on every complete technical library before sampling or graph
   construction. Preserve automatic scores and thresholds for review.
3. Select HVGs with library-aware recurrence; report genes selected across
   libraries and sensitivity to the HVG rule.
4. Generate unintegrated PCA/neighbors/UMAP and a Harmony representation using
   technical library as the correction factor.
5. Assess batch mixing alongside biological conservation; an integrated plot
   alone is not evidence of successful correction.
6. Evaluate multiple Leiden resolutions with marker coherence, minimum
   sample/donor/library coverage, adjacent-resolution agreement and resampled
   assignment stability.
7. Freeze neutral labels and a marker dictionary before joining protected
   outcomes.

### Composition analysis

- Unit: biological sample.
- Primary contrast: SLE versus normal within processing cohort 4.
- Exploratory contrast: same effect within cohort 3.
- Primary per-state model: beta-binomial mixed model on state counts versus all
  other B cells, with disease and prespecified covariates and a donor random
  intercept where repeated samples occur.
- Global test: sample-level multivariate compositional test.
- Sensitivities: one sample per donor; minimum cell-count thresholds; all
  hard-QC cells versus approved singlets; centered-log-ratio or scCODA analysis.
- Report effect sizes and confidence/credible intervals. Cell-level tests are
  prohibited as inferential disease tests.

### State-internal transcription analysis

- Aggregate raw counts by biological sample and frozen state after summing
  technical library contributions.
- Require a prespecified minimum number of cells per sample-state stratum.
- Use TMM/voom-dream or an equivalent pseudobulk model with donor correlation.
- Estimate SLE versus normal within cohort 4; cohort 3 remains exploratory.
- Control FDR within a clearly declared testing family.
- Use ranked-gene enrichment and regulon activity as supporting evidence.
- Separate `state marker`, `disease DE`, `pathway activity` and `candidate
  regulator` in all text and figures.

### External validation

- Train or construct the state mapper using discovery data only.
- Use donor-stratified cross-validation and an explicit abstention/uncertainty
  rule before applying the mapper externally.
- Freeze signatures, coefficients, direction and any threshold in discovery.
- In GSE135779, test mapped state abundance and within-state signature activity
  at sample level.
- Treat GSE163121 as directional and OneK1K as healthy reference context.
- Use external regulatory literature to prioritize hypotheses, not to claim
  causal validation.

## Claim ladder

| Claim | Evidence required | Current status |
|---|---|---|
| Audited raw B-cell dataset is analysis-ready | checksum, dimensions, raw-count and metadata audits | supported |
| Neutral B-cell states are reproducible | full-data reconstruction, markers, coverage, resampling stability | pending |
| SLE changes state abundance | sample-level within-cohort model and sensitivity analyses | pending |
| SLE changes transcription within state | sample-by-state pseudobulk disease DE | pending |
| A signal replicates externally | frozen mapper/signature and sample-level external test | pending |
| ZEB2/TBX21 or another factor is a candidate regulator | convergent DE/regulon/literature support | possible, not yet established |
| A regulator is causal | perturbation or strong causal-genetic evidence | not supported by this project |

## Manuscript architecture

The v7 Results should follow the evidence order rather than the chronology of
analyses:

1. Study hierarchy and common-support constraints.
2. Disease-blind reconstruction and stability of neutral B-cell states.
3. Cohort-resolved compositional remodeling.
4. State-internal transcriptional remodeling and pathway/regulon support.
5. Frozen external mapping and replication.
6. Robustness, generalizability boundaries and negative evidence.

The working title is:

**Donor- and cohort-resolved single-cell analysis separates compositional and
transcriptional B-cell remodeling in systemic lupus erythematosus**

## Journal-position judgement

Nature Communications is a stretch target only if the full v7 analysis reveals
a coherent, independently replicated advance rather than a better reanalysis of
one cohort. Its stated criterion is an important advance of significance to
specialists. Genome Medicine is currently the best-aligned primary target if
the disease-genomics and external-validation story succeeds. Communications
Biology is a credible Q1-tier fallback for a technically strong secondary-data
analysis with clear biological insight.

Journal choice must remain conditional until Figures 3-5 are frozen. Quartile
status should be checked against the institution's current JCR/Scopus category
at submission rather than inferred from historical metrics.

## Current decision and next gate

**Gate C2A representation:** GO  
**Smoke doublet calls:** NO-GO for freeze  
**Gate C2B-01 full raw preparation:** PASS  
**Current manuscript submission:** NO-GO

The immediate next objective is Gate C2B1: complete-library Scrublet scoring
for all 150,402 hard-QC-passing cells, followed by rate/distribution and
mixed-lineage-marker review. Only after that decision should the full v7 graph,
neutral states and publication figures be generated.

## Authoritative supporting files

- `audit_tools/6013RP_gateC1_final_review_2026-08-06.md`
- `audit_tools/phase17_c2a_03_review_smoke.py`
- `phase17_v7/gateC2A/20260810_164012_smoke/16_GATE_C2A_DECISION.md`
- `audit_tools/run_6013RP_phase17_gateC2B1_full_doublets.ps1`
- `04_submission/figure_architecture_v7_nature_style_2026-08-10.md`
- `01_manuscript/manuscript_v7_scientific_blueprint_2026-08-10.md`

## Official journal and figure references

- Nature Communications aims: https://www.nature.com/ncomms/ncomms/aims
- Nature Communications article guidance: https://www.nature.com/ncomms/submit/article
- Nature Research figure guide: https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/
- Genome Medicine aims and scope: https://link.springer.com/journal/13073/aims-and-scope
- Communications Biology aims and criteria: https://www.nature.com/commsbio/aims
