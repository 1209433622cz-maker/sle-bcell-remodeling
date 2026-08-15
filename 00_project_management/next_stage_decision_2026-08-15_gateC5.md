# Next-stage decision: Gate C5 independent SLE validation

## Advisor decision

Gate C4B passed with a robust, internally replicated B_CONV IFN/ISG signal. The next
scientific bottleneck is no longer discovery significance; it is genuinely
independent disease replication with the exact frozen program and appropriate
donor-level inference.

Proceed to `Gate C5A`, a disease-effect-blind source and design freeze for GSE135779.
Do not reuse the old external effect estimates as confirmatory results.

## Local asset status

The principal validation assets are already local:

- `GSE135779_RAW.tar`: 1,299,783,680 bytes;
- GSE135779 gene table and two metadata files;
- 112 outer tar entries: 56 Matrix Market and 56 TSV files;
- prior successful feasibility parse: 32,179 matched B-subcluster cells, 32,738 genes,
  and 56 matched donors/samples (16 HC and 40 SLE);
- GSE163121 RAW tar: 95,979,520 bytes; five donors only; and
- OneK1K H5AD: 4,434,273,970 bytes, 1,248,980 cells, 981 B-lineage donors.

No new large download is required to begin Gate C5.

## Why the previous external outputs are not the final validation

Earlier GSE135779 work was useful and showed a positive 10-gene IFN score, but it
predates the Gate C4A/C4B freeze. It differs in program membership, normalization,
covariate handling and acceptance criteria. Using it unchanged would introduce a
post-discovery mismatch.

Treat all existing GSE135779, GSE163121 and OneK1K figures and effect tables as
feasibility or legacy candidates. The source data may be reused; the confirmatory
statistics and figures must be regenerated.

## Gate C5A: disease-blind source and mapping freeze

Before inspecting new external disease effects:

1. hash and inventory every GSE135779 source file and all 112 tar members;
2. reconstruct the exact matrix-to-metadata join and explain the difference between
   58 metadata donors and 56 matrix-matched donors;
3. prove raw-count integer status, gene uniqueness and per-sample count conservation;
4. freeze B_CONV-analog inclusion using source B-subcluster labels without disease
   enrichment information;
5. exclude plasma-cell/ASC labels from the B_CONV primary analysis and keep them as
   an identity/control layer;
6. freeze the childhood and adult strata, sex and any usable metadata covariates;
7. freeze the exact four C4A confirmatory programs and all QC/identity programs;
8. document gene coverage separately for positive and negative arms; and
9. write a pre-effect contract with no external disease coefficients.

If fewer than 80% of either signed arm is available, that program cannot be used as
a direct score replication without a predeclared fallback.

## Gate C5B: frozen independent inference

### Primary external endpoint

The central endpoint is the exact 12-gene `IFN_ISG` program in conventional B-cell
pseudobulks. Use donor/sample as the inferential unit, TMM logCPM, within-contrast
gene z scores and HC3 uncertainty, matching C4B.

Test all four frozen confirmatory programs and apply BH across four external program
coefficients. The IFN/ISG direction is predeclared as positive in SLE.

### Cohort design

- Primary powered stratum: childhood SLE versus childhood healthy controls.
- Prespecified secondary stratum: adult SLE versus adult healthy controls.
- Combined estimate: model with disease and age-stratum indicator, plus sex or other
  source covariates only if complete and frozen in C5A.
- Heterogeneity: report disease-by-age-stratum interaction or a two-stratum
  meta-analytic heterogeneity statistic.
- Do not sum the childhood-only and childhood-plus-adult metadata files as separate
  observations.

### Gene-level evidence

Run donor-level edgeR TMM robust quasi-likelihood on the B_CONV analog. Preserve
Ensembl/gene identifiers, use `filterByExpr`, report complete ranked tables and BH
within each contrast. Evaluate the 13 frozen IFN genes first, then ranked pathway
coherence. Do not require broad genome-wide correlation as the central criterion.

### Required sensitivities

- minimum B-cell support thresholds chosen before effects;
- childhood-only, adult-only and combined estimates;
- source B-subcluster leave-one-label-out review;
- leave-one-donor-out IFN program estimates;
- exclusion of plasma/ASC-like labels;
- platelet, mitochondrial, ribosomal, hemoglobin and immunoglobulin audits;
- pan-B identity program review; and
- treatment/clinical-variable limitations stated explicitly if unavailable.

## External acceptance criteria

The C4B IFN/ISG claim advances only if:

- the external IFN program is positive and survives the frozen four-program BH rule
  in the primary or combined GSE135779 test;
- the result is directionally compatible in the adult stratum, while acknowledging
  its smaller sample size;
- no single donor or B-subcluster label drives the estimate;
- frozen IFN genes and ranked pathway evidence are coherent;
- platelet/ASC and major technical families do not explain the effect; and
- the pan-B identity sensitivity does not eliminate the IFN interpretation.

If the external IFN result is positive but does not pass multiplicity, retain it as
directional validation and lower the manuscript claim. If it reverses direction or
is donor-driven, C4B remains an internal result only and an upper-Q1 central claim is
not authorized.

## Supporting datasets

GSE163121 has only two controls and three SLE donors. Rerun the exact frozen score,
but use it solely for directional compatibility and boundary evidence.

OneK1K is a healthy reference, not SLE replication. Recompute only the exact frozen
programs and use donor-aware cell-type summaries to establish compartment specificity
and expected B-lineage context.

## Figure target

The preferred external-validation figure is a compact four-panel composition:

1. GSE135779 childhood/adult/combined IFN program forest;
2. discovery, internal validation and independent validation effect comparison;
3. frozen IFN-gene cross-dataset effect panel; and
4. donor/subcluster influence or specificity panel.

Avoid a second generic volcano plot and do not recycle the legacy external figure.

## Decision after Gate C5

If GSE135779 passes, freeze the manuscript's central biological claim as
SLE-associated conventional-B-cell IFN remodeling, with naive-to-memory and APC/HLA
as supporting axes. Then proceed to regulatory evidence only if it directly explains
the replicated IFN program.

If GSE135779 does not pass, stop upper-Q1 escalation and position the work as a
carefully bounded multi-cohort descriptive analysis.

## Immediate next action

Build and run the Gate C5A disease-blind GSE135779 source/mapping/design audit. The
first output must be a pre-effect freeze contract; no new external disease-effect
coefficient may be inspected before that contract passes.
