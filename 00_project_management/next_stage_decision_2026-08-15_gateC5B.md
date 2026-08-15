# Next-stage decision: Gate C5B frozen GSE135779 external inference

## Advisor decision

Gate C5A passed source, metadata, identity, pseudobulk, program and design review
without inspecting an external disease coefficient. Gate C5B is authorized to test
the exact frozen external hypotheses using only C5A-approved objects.

No legacy GSE135779 effect table, alternate metadata merge, revised B-cell mapping
or post-effect program edit may enter the confirmatory analysis.

## Mandatory input lock

Gate C5B must consume:

- the C5A PASS decision;
- `07_EXTERNAL_PSEUDOBULK_COUNTS.npz`;
- `08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv`;
- `09_EXTERNAL_GENE_UNIVERSE.csv.gz`;
- the exact C5A program dictionary and gene-availability tables; and
- the five frozen model matrices.

Before fitting real disease effects, export genes-by-samples integer matrices for
each analysis and verify dimensions, sample order, gene order, row sums and column
sums after R import. Reuse the qualified edgeR/limma engine from C4B, but record a
new C5B session manifest and reject any version or import failure.

## Frozen analyses

### Primary independent endpoint

`GSE135779_CHILDHOOD_MIN50_BCONV_SLE_VS_HC`

- 43 donors: 11 HC and 32 SLE;
- source-defined `B_CONV_ANALOG` pseudobulk;
- minimum 50 matched B cells;
- design: intercept plus SLE; and
- inferential unit: one donor/sample.

### Combined complementary estimate

`GSE135779_COMBINED_MIN50_BCONV_SLE_VS_HC`

- 54 donors: 16 HC and 38 SLE;
- design: intercept, SLE and adult-stratum indicator; and
- no unobserved sex or treatment covariate imputation.

### Secondary and threshold analyses

- adult >=50: 11 donors, 5 HC and 6 SLE, secondary only;
- combined >=20: 56 donors, 16 HC and 40 SLE; and
- combined >=100: 51 donors, 16 HC and 35 SLE.

The adult estimate cannot replace the childhood primary. Threshold analyses are
sensitivity tests, not opportunities to select the most favorable result.

## Statistical contract

Gene-level inference uses edgeR TMM normalization, `filterByExpr`, robust dispersion
estimation and robust quasi-likelihood testing. Preserve Ensembl as the unique key,
retain a full ranked table and apply BH across all tested genes within each contrast.

Program scores must reproduce the C4B formula exactly: duplicate symbols summed,
TMM logCPM, within-analysis gene z scores, signed-arm aggregation and HC3 sandwich
uncertainty. The confirmatory family is exactly:

- naive-to-memory;
- atypical/low-naive;
- APC/HLA; and
- IFN/ISG.

Apply BH across these four coefficients separately for each frozen analysis. The
principal IFN/ISG direction is positive in SLE, using the exact 12-gene dictionary.

## Required stability and specificity analyses

- leave one donor out for the IFN/ISG coefficient and frozen IFN genes;
- leave one source `B-caSC` label out using the label-level pseudobulks;
- confirm that the result is stable at >=20 and >=100 B-cell support;
- compare childhood, adult and combined directions with uncertainty;
- review PC/ASC, platelet/ambient, pan-B and activation/stress programs;
- quantify mitochondrial, ribosomal, hemoglobin and immunoglobulin representation
  among leading ranked genes; and
- report missing sex, treatment and detailed clinical covariates as limitations.

Source-label omission may test robustness but may not redefine hard naive/memory
identities. PC/ASC rows remain controls and cannot be merged into B_CONV.

## External acceptance rule

External replication passes only if:

- IFN/ISG is positive and passes BH across four programs in the childhood primary
  or combined complementary analysis;
- childhood and combined estimates are directionally compatible;
- the small adult estimate does not show persuasive reversal;
- all donor-deletion estimates remain positive and no donor causes a material
  qualitative change;
- source-label omission does not reveal dependence on a single `B-caSC` label;
- frozen IFN genes and ranked evidence are coherent; and
- platelet, ASC/UPR, technical families and pan-B identity do not provide a more
  plausible explanation.

A positive but multiplicity-nonsignificant result is directional support only. A
reversed, donor-driven or source-label-driven result fails external replication and
forces the manuscript claim back to internal GSE174188 evidence.

## Figure target

The Gate C5B analysis figure should use a restrained four-panel layout:

1. childhood, combined and adult IFN/ISG forest;
2. GSE174188 discovery/internal validation versus GSE135779 external effects;
3. frozen IFN-gene effect coherence; and
4. donor and source-label influence/specificity.

Do not add another generic volcano plot. Show confidence intervals, sample counts,
effect scales and the prespecified multiplicity result directly in the panels.

## Decision after Gate C5B

If the external test passes, freeze the manuscript's central claim as independently
replicated SLE-associated IFN remodeling in broad conventional B cells. Then update
the main text and figures and evaluate only regulatory evidence that directly
explains the replicated IFN program.

If it fails, preserve C4B as a robust internal result, lower the external language
and stop presenting the study as an upper-Q1 mechanistic manuscript.

## Immediate next action

Build the C5B matrix exporter and no-effect software/import qualification stage.
Real GSE135779 coefficients remain locked until all imported dimensions and count
sums match the C5A frozen objects exactly.
