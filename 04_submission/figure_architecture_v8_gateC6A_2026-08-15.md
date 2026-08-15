# Figure architecture v8: Gate C6A claim-integrated Nature-style design

**Date:** 15 August 2026
**Status:** binding scientific architecture; final journal dimensions remain unfrozen

## Governing narrative

The main figures must follow the inferential sequence rather than the chronological
analysis log:

1. define what comparisons and identities are valid;
2. show that composition is not the central result;
3. establish the GSE174188 within-compartment IFN signal;
4. demonstrate independent, program-specific GSE135779 replication; and
5. add a regulator figure only if Gate C6B passes.

The visual center of the paper is the transition from Figure 3 to Figure 4. No panel
may imply a hard naive/memory subtype, genome-wide replication or causal regulation.

## Production specification

- Build vector-first PDF artwork with embedded fonts and editable text.
- Export review PNGs at 300 dpi and archival TIFF only after journal selection.
- Use Arial or an equivalent sans-serif font consistently; 7-9 pt at final size.
- Use sentence-case panel titles and bold lower-case panel letters outside axes.
- Use a colorblind-safe palette with disease colors held constant across figures.
- Reserve saturated red for IFN/ISG emphasis; use charcoal and teal for references
  and secondary estimates; use neutral gray for unavailable or inconclusive results.
- Encode direction with position and intervals, not color alone.
- Show individual biological samples whenever a distribution is inferential.
- State the biological unit, exact n, interval definition and multiplicity family in
  every inferential legend.
- Avoid nested cards, decorative gradients, 3D effects and generic volcano plots.
- Keep axes, panel baselines and inter-panel gutters aligned across the figure set.

## Figure 1 | Study hierarchy and disease-blind identity scope

**One job:** prove the valid inferential design before presenting disease effects.

### Panels

- **a, Study flow:** GSE174188 discovery/internal validation and GSE135779
  independent validation, with protected-outcome locks marked explicitly.
- **b, Metadata hierarchy:** donors, samples, libraries, processing cohorts and
  bridge relations.
- **c, Common support:** disease-by-processing-cohort sample matrix with primary,
  internal, secondary and discovery-only roles.
- **d, Cell retention:** source cells, hard-QC retained cells and residual-risk
  sensitivity branch.
- **e, Identity adjudication:** C2B3 fine-state HOLD leading to the C2B4 `B_CONV` /
  `B_ASC` solution, including 20/20 resampling support and the minimum stability
  metrics.
- **f, Marker scope:** compact marker evidence for `B_ASC`, continuous
  naive-memory structure in `B_CONV` and platelet overlay as QC only.

### Acceptance

- Disease is absent from identity panels.
- The failed fine-state gate remains visible rather than being retrospectively
  erased.
- Cell counts are descriptive; no cell-level P value appears.

## Figure 2 | Sample-level composition is secondary

**One job:** demonstrate why `B_ASC` abundance is not the central claim.

### Panels

- **a, Sample distribution:** jittered sample-level `B_ASC` fractions for the primary
  contrast, with adjusted means shown separately.
- **b, Primary estimate:** model and HC1 intervals around odds ratio 0.947.
- **c, Contrast forest:** primary, internal validation, donor-nonoverlap and flare
  estimates, with confirmatory versus secondary status encoded by fill.
- **d, Robustness:** mandatory variants and 90 leave-one-out estimates.

### Acceptance

- Use sample-cohort strata as points; never display cells as replicates.
- Label the flare q=0.0845 and its secondary status directly.
- The title and caption state the null primary result without defensive language.
- If journal space is limited, Figure 2 may become Extended Data, but the negative
  primary estimate must remain in the main text.

## Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG

**One job:** establish the frozen within-compartment discovery and internal evidence.

### Panels

- **a, Pseudobulk support:** primary, threshold, residual-risk, internal validation
  and donor-nonoverlap sample counts.
- **b, Four-program forest:** naive-to-memory, atypical/low-naive, APC/HLA and IFN/ISG
  in the primary contrast with the common four-program BH family.
- **c, IFN replication forest:** primary, full internal, donor-nonoverlap, minimum-
  cell and residual-risk estimates.
- **d, Ranked coherence:** compact IFN-arm effect strip or dot plot with camera
  enrichment; do not use a generic volcano.
- **e, Specificity controls:** platelet/ambient, ASC/UPR and pan-B effects shown as
  controls rather than competing biological programs.

### Acceptance

- Separate state markers from disease-associated genes visually and in the legend.
- Label GSE174188 validation as internal.
- Naive-to-memory and APC/HLA are supporting axes; atypical/low-naive is negative.
- The central annotation reports effect 0.837 and q=2.98 x 10^-6.

## Figure 4 | Independent GSE135779 IFN replication

**One job:** show independent replication, influence stability and its precise
boundary.

### Binding candidate

Use `phase17_v7/gateC5B/20260815_gse135779_external_validation/figures/gate_c5b_gse135779_independent_ifn_validation.pdf` as the current candidate.

### Panels

- **a, External forest:** childhood, combined, adult, minimum-20 and minimum-100
  IFN/ISG effects.
- **b, Cross-dataset forest:** GSE174188 primary/internal estimates beside GSE135779
  independent estimates.
- **c, Gene context:** all shared tested genes with frozen IFN genes highlighted,
  representative labels and Spearman rho=0.026.
- **d, Influence:** 43 donor deletions and eight source-label omissions relative to
  the full childhood estimate.

### Acceptance

- Childhood n=43 and combined n=54 are printed or available in the panel source data.
- Adult n=11 is gray and labelled directional/underpowered.
- The phrase `program-specific replication` is visually explicit.
- Source-label omission is not described as independent replication.
- The caption states donors as biological units and HC3 intervals.

## Conditional Figure 5 | Prespecified regulatory evidence

**Status:** locked; do not create effect panels before Gate C6B passes.

**One job if authorized:** test whether the replicated IFN program is accompanied by
specific, cross-dataset STAT1/STAT2/IRF7/IRF9 target activity rather than broad
nonspecific regulator enrichment.

### Provisional panels

- **a, Frozen evidence design:** regulator family, negative controls, resources and
  confirmatory contrasts.
- **b, Regulator activity:** effects and multiplicity-adjusted intervals across the
  three confirmatory contrasts.
- **c, Specificity:** IFN family versus negative-control family and technical gene
  families.
- **d, Orthogonal response:** exact IFN perturbation signature, with context and
  replication limits stated.

### Gate

Figure 5 enters the main paper only after frozen cross-dataset direction,
multiplicity, target-coverage and influence criteria pass. Otherwise the manuscript
ends with Figure 4 and regulator discussion remains a future hypothesis.

## Extended Data and Supplementary plan

- **Extended Data 1:** source integrity, metadata exceptions and complete-library
  doublet diagnostics.
- **Extended Data 2:** unintegrated/Harmony comparison and bridge-sample diagnostics.
- **Extended Data 3:** fine-state instability, transition reconstruction and
  two-compartment sensitivity.
- **Extended Data 4:** full composition diagnostics and alternative sample policies.
- **Extended Data 5:** gene-level model diagnostics, full ranked IFN evidence and
  threshold sensitivities.
- **Extended Data 6:** GSE135779 source-label support, matrix qualification and all
  four external programs.
- **Extended Data 7:** GSE163121 directional boundary and OneK1K healthy context,
  only if they answer a specific generalizability question.
- **Supplementary Tables:** full gene results, program dictionaries, model matrices,
  influence results and claim-to-evidence mapping.

## Cross-figure quality-control checklist

- One visual question per panel and one scientific job per figure.
- No panel title overstates its evidence tier.
- All n values define donors, samples, sample-cohort strata, libraries or cells.
- All P and q values identify the experimental unit and correction family.
- Confidence intervals have consistent line weight, cap size and reference lines.
- Disease colors, cohort labels and direction conventions are identical throughout.
- Negative and inconclusive findings use equal typographic weight to positive ones.
- Panel letters and legends remain legible at final two-column width.
- Raster review at desktop and page scale shows no overlaps, clipping or tiny labels.
- Source Data can recreate every plotted point without reading values from artwork.

## Disposition of older figures

- The previous v6 ABC/APC-like figure sequence is historical and must not supply
  titles, labels or effect values.
- The v7 Figure 1 design artwork may be reused only after updating the identity and
  gate status to C2B4-C5B.
- Gate-specific diagnostic figures remain audit artifacts unless explicitly promoted
  above.
- The Gate C5B four-panel figure is the only current main-figure candidate already
  aligned with the C6A claim hierarchy.
