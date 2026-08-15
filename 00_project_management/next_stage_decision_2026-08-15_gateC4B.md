# Next-stage decision: Gate C4B B_CONV transcription models

## Advisor decision

Gate C4A passed all raw-count, per-gene conservation, support, program and design
checks. Gate C4B may estimate disease-associated transcription only within frozen
`B_CONV` pseudobulks and the exact pre-effect program dictionary.

B_ASC gene-level disease pseudobulk is prohibited because independent-sample cell
support is inadequate.

## Stage 0: qualify the statistical engine

The current Windows machine has neither R/edgeR nor a validated Python
negative-binomial pseudobulk engine (`pydeseq2` and `diffxpy` are absent). No
expression effect should be opened until this dependency gap is resolved.

Preferred route:

1. install an isolated, version-locked R environment;
2. install edgeR and limma from Bioconductor;
3. record `sessionInfo()`, package versions and repository sources;
4. export analysis-specific integer count matrices from the frozen NPZ without
   changing rows, genes or counts;
5. verify exported row/column sums against Gate C4A hashes; and
6. run a synthetic negative-binomial recovery test with known null and non-null
   genes before discovery coefficients are inspected.

An alternative engine is acceptable only after effect-size, null-calibration and
ranking concordance against edgeR on a software-test matrix. Cell-level Wilcoxon,
ordinary per-gene OLS and unmoderated ad hoc negative-binomial loops are not valid
substitutes.

## Frozen primary analysis

Analysis ID: `C4B_PRIMARY_C4_BCONV_MANAGED_VS_NORMAL`

- 43 normal and 46 managed cohort-4 pseudobulks;
- all hard-QC cells as the primary branch;
- minimum 50 B_CONV cells;
- managed status, centered age and Asian-ethnicity indicator;
- edgeR TMM normalization, `filterByExpr`, robust quasi-likelihood; and
- sample-cohort pseudobulk as the inferential unit.

Required sensitivities:

- minimum B_CONV thresholds 20 and 100;
- residual-risk-negative branch;
- leave-one-sample-out review for prioritized programs/genes;
- immunoglobulin-family exclusion for pathway and ranked-summary robustness; and
- explicit review of mitochondrial, ribosomal, hemoglobin, platelet and
  activation/stress families.

## Frozen internal validation

Analysis ID: `C4B_VALIDATION_C2_BCONV_EUROPEAN_FEMALE`

- 21 normal and 43 managed cohort-2 European-American female pseudobulks;
- centered age adjustment;
- full frozen set plus a nonoverlap sensitivity containing 21 normal and 33
  managed donors; and
- directional internal replication, not an independent cohort.

Primary gene/program directions must be evaluated in validation without changing
gene sets, filters or covariates after seeing the primary result.

## Frozen secondary flare analysis

Analysis ID: `C4B_SECONDARY_C3_BCONV_FLARE_VS_NORMAL`

- 18 normal and 16 flare cohort-3 pseudobulks;
- centered age and European-ethnicity adjustment; and
- secondary interpretation regardless of nominal significance.

The previous B_ASC abundance result motivates this contrast but does not authorize
ASC gene-level modeling or allow flare to replace the managed-state primary test.

## Program-level inference

The four primary programs are:

- naive-to-memory axis;
- atypical/low-naive axis;
- APC/HLA program; and
- IFN/ISG program.

Scores must follow the Gate C4A formula exactly. Report adjusted mean differences,
95% confidence intervals, HC3/sandwich uncertainty and BH q values across these
four coefficients.

Activation/stress and TLR7/innate are secondary context. Platelet/ambient, ASC/UPR
and pan-B programs are QC/identity controls and cannot become central findings.

## Gene-level and pathway inference

For each frozen contrast:

- preserve Ensembl IDs as the unique gene key and feature names as annotations;
- apply a pre-effect expression filter;
- report log2 fold change, abundance, test statistic, P value and BH FDR;
- retain a complete ranked table, not only significant genes;
- test pathway/program coherence from ranked statistics;
- flag QC and immunoglobulin families rather than deleting inconvenient results;
  and
- report cross-cohort effect correlation and directional concordance with
  uncertainty.

Repeated volcano plots are not the target layout. Preferred Nature-style outputs
are a compact program forest, a primary/validation effect-size comparison, a
ranked pathway heatmap and a limited annotated gene panel.

## Gate C4B manuscript acceptance criteria

A B_CONV transcriptional result can become central only if:

- the primary cohort-4 program family survives its frozen multiplicity rule;
- effect direction is concordant in full and nonoverlap cohort-2 validation;
- the result is stable across B_CONV thresholds and the dual QC branches;
- no single sample drives the effect;
- gene-level and ranked-pathway evidence is biologically coherent; and
- QC/identity programs do not explain the signal.

If only the secondary flare contrast is positive, it remains hypothesis-generating.
If no primary program meets these criteria, the manuscript must retain a negative
managed-state conclusion and cannot be positioned as an upper-Q1 mechanistic
paper.

## Decision after Gate C4B

If Gate C4B passes, proceed to Gate C5 independent validation:

- GSE135779 as the principal SLE validation layer with age-stratified analysis;
- GSE163121 as small B-cell-specific directional support; and
- GSE196830/OneK1K as healthy immune-reference context, not SLE replication.

Only a coherent Gate C4B result that transfers to an independent SLE dataset can
restore a realistic upper-Q1 central claim. Regulatory evidence should follow the
replicated program, not precede it.

## Immediate next action

Create the reproducible edgeR/limma environment installer and Gate C4B software
qualification suite. Do not fit the frozen disease coefficients until environment,
matrix-import, null-calibration and synthetic-effect recovery checks all pass.
