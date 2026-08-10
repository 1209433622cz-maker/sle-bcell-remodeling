# Manuscript v7 scientific blueprint

## Status

This is the active writing scaffold for the raw-count reanalysis. It is not a
results manuscript and must not inherit unsupported v6 effect sizes, P values,
state names or validation claims.

## Working title

**Donor- and cohort-resolved single-cell analysis separates compositional and
transcriptional B-cell remodeling in systemic lupus erythematosus**

Short title: **Cohort-resolved B-cell remodeling in SLE**

## One-sentence advance

A hierarchy-aware single-cell framework separates changes in B-cell-state
abundance from disease-associated transcription within disease-blind states and
tests which layer reproduces in an independent SLE dataset.

## Central hypothesis

SLE B-cell remodeling comprises two separable processes: altered occupancy of
neutral B-cell states and altered transcription within those same states. These
processes need not occur in the same state or replicate to the same degree.

## Claim boundaries

### Claims the study may make if supported

- A neutral B-cell state is reproducibly reconstructed from discovery raw
  counts.
- The relative abundance of a frozen state differs between SLE and controls
  within a cohort that contains both groups.
- Within a frozen state, sample-level pseudobulk expression differs between SLE
  and controls.
- A frozen state mapper or signature reproduces a prespecified direction in an
  independent dataset.
- A transcription factor or pathway is a candidate regulator supported by
  convergent observational evidence.

### Claims the study must not make without new evidence

- A disease-enriched cluster is a novel pathogenic lineage.
- A cell-level P value represents donor-level replication.
- Harmony removes confounding or proves biological equivalence.
- OneK1K validates an SLE state.
- Literature overlap, regulon score or colocalization failure proves causality.
- ZEB2/TBX21/FTO is mechanistically causal in this dataset.

## Abstract logic

### Background

State that SLE B-cell abnormalities may reflect both composition and
state-internal activation, but these are often conflated by outcome-informed
annotation, cell-level inference and heterogeneous cohorts.

### Methods

State the discovery hierarchy, disease-blind reconstruction, cohort-specific
sample-level composition, sample-by-state pseudobulk and frozen external
mapping. Do not list every software package.

### Results

Use four quantitative sentences only after analysis freeze:

1. dataset and state reconstruction;
2. primary cohort composition;
3. within-state transcription/pathway result;
4. independent validation and its boundary.

### Conclusion

Conclude at the process level: composition and transcription are separable and
show different reproducibility. Avoid causal language.

## Results architecture

### 1. Study hierarchy defines the valid disease contrasts

Purpose: establish the inferential frame before showing a UMAP.

Required content:

- donors, samples, libraries and processing cohorts;
- repeated donors and bridge samples;
- disease-by-cohort common-support matrix;
- hard-QC retention by cohort and disease;
- declaration that cohort 4 is primary and cohort 3 exploratory.

Primary take-home sentence template:

> The dataset provided broad support for disease-blind state discovery but only
> processing cohort 4 provided adequate within-cohort support for the primary
> SLE-control comparison.

### 2. Raw-count reconstruction identifies stable neutral B-cell states

Required content:

- full-library doublet diagnostics and decision;
- unintegrated versus Harmony batch diagnostics;
- bridge-sample concordance as within-sample technical replication;
- B-lineage extraction completeness against the full PBMC source;
- identity stability after excluding strong ISG and other nuisance programs;
- multi-resolution and resampling stability;
- neutral marker dictionary and uncertainty;
- sample/donor/library coverage for each frozen state;
- contaminant/doublet-like states separated from biological states.

Do not reveal disease enrichment until labels are frozen.

### 3. SLE alters B-cell-state composition within supported cohorts

Required content:

- sample-level composition overview;
- cohort 4 beta-binomial effect sizes with intervals and FDR;
- cohort 3 effects displayed separately as exploratory;
- bridge samples excluded from the primary disease coefficient;
- a global compositional test before state-specific interpretation;
- one-sample-per-donor, singlet-policy and compositional-model sensitivity;
- no pooled coefficient across unsupported cohorts.

The text must report absolute sample numbers and median cells per sample-state,
not only cell totals.

### 4. State-internal transcription is distinct from state abundance

Required content:

- sample-by-state pseudobulk design and inclusion counts;
- within-state SLE-control effect estimates in cohort 4;
- ranked enrichment and regulon support;
- direct comparison of composition effect versus within-state transcription;
- explicit separation of state markers from disease DE genes.

Preferred conceptual result: identify which signals are composition-dominant,
transcription-dominant, concordant or unsupported. This framework remains
publishable even if no ABC-like abundance change replicates.

### 5. Frozen external mapping distinguishes reproducible from cohort-specific signals

Required content:

- discovery-only mapper/signature training;
- donor-stratified cross-validation and uncertainty/abstention;
- external mapping quality before disease comparison;
- childhood and adult GSE135779 strata estimated separately before any meta-effect;
- sample-level external abundance and expression tests;
- prespecified direction, effect and interval;
- negative findings reported alongside positive findings.

GSE135779 is the main external test. GSE163121 is directional only. OneK1K
provides healthy reference context and belongs in the supplement unless it
answers a specific reviewer-facing question.

Robustness analyses are attached to the result they protect rather than forming
a sixth main Results section. Doublet-policy and HVG sensitivities accompany
state reconstruction; alternative composition models accompany Figure 3;
pseudobulk thresholds and influence diagnostics accompany Figure 4; mapping
uncertainty accompanies Figure 5. Remaining generalizability boundaries belong
in Discussion and Extended Data.

The 11 repeated donors support a secondary paired analysis only after the five
main results are frozen. Paired changes may strengthen within-person evidence
but cannot be interpreted as treatment causality.

## Discussion architecture

1. Open with the principal process-level result, not the most visually striking
   state.
2. Explain why composition and within-state expression answer different
   biological questions.
3. Compare robust interferon evidence with more limited ABC/ZEB2 evidence.
4. Explain how cohort-resolved inference changes interpretation of the Perez
   resource.
5. Discuss external replication honestly, including abstentions and negative
   findings.
6. End with a forward-looking experimental hypothesis, not a causal claim.

## Methods ordering

1. Study resources and ethics/data access
2. Source-object integrity and metadata hierarchy
3. Raw-count extraction and hard QC
4. Complete-library doublet scoring
5. Disease-blind normalization, HVGs and representation learning
6. State stability, annotation and outcome-lock protocol
7. Sample-level composition analysis
8. Sample-by-state pseudobulk differential expression
9. Pathway and regulon analysis
10. Frozen external mapping and validation
11. Sensitivity analyses
12. Reproducibility, software and source data

## Statistical reporting contract

- Define every `n` as donors, samples, libraries or cells.
- State the experimental unit in every figure legend containing a P value.
- Report effect size, interval and exact P value where practical.
- State the FDR family and correction method.
- Display individual biological samples in abundance plots.
- Do not use stars without exact values in Source Data.
- Do not interpret descriptive cell-level percentages as inferential evidence.
- Use `relative abundance` or `compositional shift` unless external absolute
  blood counts support absolute expansion or depletion.
- Distinguish confirmatory cohort 4 tests from exploratory cohort 3 tests.
- Preserve negative and inconclusive validation results.

## Writing contract

- Use neutral state names until all evidence is frozen.
- Prefer `associated with`, `consistent with` and `prioritizes` over causal
  verbs.
- Reserve `replicated` for a frozen external test with the same direction.
- Reserve `validated` for a prespecified external analysis with acceptable
  mapping quality and statistical support.
- Keep the main text near 5,000 words for Nature Communications compatibility;
  move implementation detail and secondary datasets to Methods/Supplement.
- Build Results around questions and decisions, not a catalogue of plots.

## Figure-to-text map

| Figure | Result section | One job |
|---|---|---|
| 1 | Study hierarchy | prove the valid inferential design |
| 2 | State reconstruction | prove neutral states are technically and biologically stable |
| 3 | Composition | quantify cohort-resolved sample-level abundance changes |
| 4 | Transcription | quantify within-state disease programs and contrast them with composition |
| 5 | External validation | show what reproduces and what does not |

## Freeze checkpoints

### Freeze A: cells and representation

- approve full-library doublet policy;
- freeze the bridge-sample role and B-lineage extraction completeness result;
- freeze included cells, HVGs, PCs, correction factor and neighbor settings;
- approve the ISG-excluded identity-stability sensitivity;
- save checksums and software lock.

### Freeze B: neutral states

- approve resolution/stability;
- freeze state IDs, names, markers and excluded technical states;
- export discovery reference/mapping object.

### Freeze C: outcomes and inference

- unlock disease metadata;
- run prespecified composition and pseudobulk models;
- freeze testing families before inspecting external outcomes.

### Freeze D: external validation

- apply frozen mapper/signatures;
- record mapping uncertainty and exclusions;
- freeze final claim ladder and manuscript title.

## Current placeholders that must remain unresolved

- final number and names of neutral B-cell states;
- main composition effect sizes and FDR values;
- within-state DE genes/pathways;
- external replication status;
- final journal and title strength.

Filling any of these from v6 would contaminate the v7 outcome lock.
