# Figure architecture v7: Nature-style scientific and visual QC

Current Figure 1 design draft: `03_results/phase17_v7_figure1_study_design_2026-08-10/figures/figure1_v7_study_design.pdf`  
Technical QC: `03_results/phase17_v7_figure1_study_design_2026-08-10/FIGURE1_TECHNICAL_QC.md`  
Legend draft: `01_manuscript/figure1_v7_legend_draft_2026-08-10.md`

## Governing principle

Each main figure must answer one scientific question and carry one claim. A
UMAP is supporting geometry, not a result by itself. Every inferential panel
must expose biological samples and state the experimental unit.

## Production specification

- Final width: 183 mm for multi-panel main figures; use 89 mm only for a truly
  simple single-column figure.
- Maximum final height: 170 mm, including panel labels and legends inside the
  artwork boundary.
- Typeface: Arial or Helvetica, 5-7 pt at final size; use 7 pt for axes where
  space permits.
- Panel labels: lowercase bold `a`, `b`, `c`, placed consistently at the upper
  left without punctuation.
- Background: white. No gradients, shadows, decorative boxes or colored panel
  backgrounds.
- Lines: at least 1 pt at final size. Axes should be restrained and consistent.
- Color: colorblind-safe Okabe-Ito-derived palette. Disease uses a stable pair;
  processing cohorts use a distinct four-color categorical set; neutral states
  use a separate categorical palette.
- Export: PDF/SVG for vector line art and text; 600 dpi TIFF/PNG only for
  raster-heavy panels. Embed fonts.
- Legends: concise, declarative and self-contained; define `n`, statistical
  test, sidedness, correction and summary bars.
- Source Data: one tidy table per figure, with panel identifiers and unrounded
  values.

Official reference:
https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/

## Main Figure 1: The dataset hierarchy defines valid inference

**Claim:** Broad state discovery is possible, but direct SLE-control inference
must be cohort resolved.

Proposed layout: 183 mm x 145 mm, two rows.

| Panel | Content | Design/QC requirement |
|---|---|---|
| a | compact study flow from source to v7 gates | show counts at donor, sample, library and cell levels |
| b | donor-sample-library hierarchy | use a restrained alluvial/network schematic; bridge samples visible |
| c | disease by processing-cohort sample counts | sample counts, not cell counts; label absent/common support |
| d | hard-QC retention by cohort and disease | dot-and-interval or compact bars; denominator visible |
| e | primary/exploratory/non-comparable contrast map | three clearly labeled inference tiers |

Do not include a UMAP in Figure 1. The point is design validity.

## Main Figure 2: Disease-blind reconstruction yields stable neutral states

**Claim:** Neutral B-cell states are recoverable after raw-count reconstruction
and are not driven by a single library, sample or donor.

Proposed layout: 183 mm x 165 mm, three rows.

| Panel | Content | Design/QC requirement |
|---|---|---|
| a | unintegrated UMAP by processing cohort | same coordinates/limits and point order policy as panel b |
| b | Harmony UMAP by frozen neutral state | rasterized points, vector labels; no disease information |
| c | canonical-marker dot plot | symbols rather than Ensembl IDs; biological marker groups separated |
| d | resolution and resampling stability | ARI/NMI and state-wise Jaccard/assignment probability |
| e | state coverage | donors, samples and libraries per state; flag technical dominance |
| f | doublet/contaminant diagnostics | score/rate summary and mixed-lineage enrichment |

Avoid printing 88 library colors in the main figure. Put the full library UMAP
and rate distributions in Supplementary Figure 2.

## Main Figure 3: Cohort-resolved compositional remodeling

**Claim:** SLE-associated abundance changes are estimated from biological
samples within supported cohorts.

Proposed layout: 183 mm x 150 mm.

| Panel | Content | Design/QC requirement |
|---|---|---|
| a | sample-level state compositions in cohort 4 | stacked overview only; samples ordered and group-labeled |
| b | primary cohort 4 state effects | forest plot of log-odds/ratio with 95% interval and FDR |
| c | raw sample distributions for prioritized states | dots for samples, donor linkage only when repeated |
| d | cohort 3 exploratory effects | separate forest column; never visually pooled with primary |
| e | sensitivity matrix | sign/effect stability across donor, doublet and minimum-cell rules |

No cell-level violin plots with inferential P values. Do not use asterisks as the
only statistical annotation.

## Main Figure 4: Within-state transcription differs from composition

**Claim:** Disease-associated expression within frozen states is a distinct
axis of B-cell remodeling.

Proposed layout: 183 mm x 165 mm.

| Panel | Content | Design/QC requirement |
|---|---|---|
| a | pseudobulk design and included sample-state strata | display samples and minimum-cell gate |
| b | within-state disease DE | compact effect-size heat map or faceted volcano for supported states |
| c | ranked pathway enrichment | NES with intervals/FDR; fixed direction convention |
| d | regulon/candidate regulator evidence | observational wording; no causal arrows |
| e | composition versus transcription quadrant | effect-size summary identifying concordant and discordant states |

The marker genes defining a state must not be presented as disease DE unless
they pass the within-state disease model.

## Main Figure 5: Frozen external mapping tests reproducibility

**Claim:** External data discriminate robust disease programs from
cohort-specific discovery findings.

Proposed layout: 183 mm x 155 mm.

| Panel | Content | Design/QC requirement |
|---|---|---|
| a | discovery-only mapping workflow | train, cross-validate, freeze, apply; outcome labels absent from training |
| b | donor-stratified discovery CV | confusion/probability calibration and abstention rate |
| c | external mapping quality | canonical markers and prediction uncertainty before group comparison |
| d | external abundance effects | sample-level forest plot |
| e | external within-state/signature effects | same direction convention as Figure 4 |
| f | replication scorecard | replicated, directionally consistent, inconclusive, not replicated |

The scorecard must include negative results. A validation threshold cannot be
re-estimated from validation controls.

## Supplementary figures

| Figure | Required content |
|---|---|
| S1 | source integrity, raw-count properties and complete hard-QC distributions |
| S2 | per-library doublet scores/rates, thresholds, full library UMAPs and mixed-lineage diagnostics |
| S3 | HVG recurrence, PCA diagnostics, unintegrated/Harmony mixing metrics and bridge-sample checks |
| S4 | full resolution tree, resampling stability and alternate integration sensitivities |
| S5 | complete neutral marker dot plots, ranked markers and annotation confidence |
| S6 | full composition models, covariates, one-sample-per-donor and scCODA/CLR sensitivity |
| S7 | complete pseudobulk QC, mean-variance, sample influence and pathway results |
| S8 | GSE163121 directional evidence, OneK1K healthy context and negative regulatory/genetic evidence |

## Panel acceptance checklist

- The panel has a single stated question.
- Disease labels were not used upstream of the declared outcome unlock.
- All displayed `n` values identify their level.
- Sample-level data are visible for inferential comparisons.
- Effect sizes and intervals are present; FDR family is defined.
- Colors carry the same meaning across all figures.
- Long gene/state labels fit at final 183 mm width.
- Axis labels remain legible at 100% final size.
- No rasterized text, clipped legends or overlapping panel labels.
- PDF fonts are embedded and editable.
- Source Data reproduces the plotted values exactly.
- Caption distinguishes confirmatory, exploratory and descriptive panels.

## Existing figures disposition

The existing six main figures passed basic resolution/font checks but are not
scientifically reusable as the v7 main set. They should remain frozen as v6
provenance. Selected code patterns may be reused, but panels must be regenerated
from frozen v7 tables. The old signature-heavy Figure 5 is repetitive, and the
old external-validation Figure 6 does not demonstrate frozen state replication;
both require complete redesign rather than cosmetic editing.
