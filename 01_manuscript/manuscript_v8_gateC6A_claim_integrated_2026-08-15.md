# Disease-blind single-cell reconstruction identifies independently replicated interferon remodeling in conventional B cells in systemic lupus erythematosus

**Version:** Gate C6A claim-integrated working manuscript v8
**Date:** 15 August 2026
**Status:** scientific-content draft; not journal-formatted; references, author list and declarations remain to be finalized

## Abstract

Systemic lupus erythematosus (SLE) alters both the abundance and transcriptional
state of peripheral B cells, but these layers can be conflated by outcome-informed
annotation, cell-level inference and technically imbalanced cohorts. We performed a
donor- and cohort-resolved reanalysis of public single-cell RNA-sequencing data,
using disease-blind identity reconstruction before any case-control comparison.
From 150,402 hard-quality-control B-lineage cells in GSE174188, resampling supported
two broad identity compartments, conventional B cells (`B_CONV`) and
antibody-secreting cells (`B_ASC`), while finer naive-memory partitions were not
stable enough for hard compositional inference. Sample-level analysis did not
support a primary SLE-associated difference in relative `B_ASC` abundance
(odds ratio 0.947, 95% confidence interval 0.636-1.410; P=0.787). In contrast,
sample-by-compartment pseudobulk analysis identified a prespecified type I
interferon/interferon-stimulated-gene (IFN/ISG) shift within `B_CONV` in the primary
GSE174188 contrast (standardized effect 0.837, 95% confidence interval
0.525-1.148; four-program false-discovery-rate q=2.98 x 10^-6), with support in a
donor-nonoverlap internal contrast (effect 1.086; q=3.61 x 10^-4). The frozen IFN/ISG
program replicated in independent GSE135779 childhood donors (11 controls and 32
SLE; effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6) and in the
combined childhood-adult analysis (effect 0.996; q=1.31 x 10^-6). The adult-only
estimate was positive but imprecise. Donor-deletion and source-label omission
analyses preserved the external direction. Genome-wide cross-dataset effect
agreement was low (Spearman rho=0.026), whereas all ten jointly tested frozen IFN
genes were positive in both datasets. These results support program-specific,
independently replicated IFN remodeling within a broad conventional-B compartment,
while separating it from unsupported subtype, composition and causal claims.

## Introduction

Systemic lupus erythematosus is a heterogeneous autoimmune disease involving loss
of B-cell tolerance, autoantibody production and sustained innate immune activation.
Peripheral-blood studies have described changes in naive, memory,
double-negative, CD11c-positive and antibody-secreting B-cell populations, together
with prominent type I interferon responses. The biological importance of these
observations is clear, but their statistical interpretation is not always
straightforward. A larger fraction of cells assigned to a state and increased gene
expression within that state are different phenomena, and neither cells from the
same individual nor technical libraries from the same sample are independent
biological replicates.

Public SLE single-cell resources add a second challenge. Samples can be distributed
across processing cohorts, donors may contribute repeated samples, and disease
groups may lack common support within some technical strata. Outcome-informed
cluster labels or pooled cell-level tests can therefore produce strong-looking
signals that combine biology with design structure. Independent validation can
compound this problem if state labels, support thresholds or signatures are
re-estimated after external disease effects have been viewed.

We addressed these issues with a staged analysis. Raw-count integrity, metadata
hierarchy and disease-by-cohort support were audited first. B-lineage identity was
then reconstructed while protected disease fields remained separate. Only after a
disease-blind identity model was frozen were sample-level composition and
within-compartment transcription tested. The primary expression result was carried
forward to independent GSE135779 under a pre-effect mapping and analysis contract.

The analysis was designed to distinguish robust process-level biology from visually
appealing but unstable subtype narratives. We show that a fine-grained hard
naive-memory partition is not reproducible enough for outcome inference and that
`B_ASC` composition is not a central disease result. Instead, the reproducible
cross-dataset signal is a type I IFN/ISG transcriptional shift within a disease-blind
broad conventional-B compartment.

## Results

### A disease-blind two-compartment model defines the permissible biological scope

The authoritative GSE174188 B-lineage source contained 152,981 cells and 30,172
genes. Frozen hard-quality-control rules retained 150,402 cells. Metadata audits
resolved 259 donors, 271 biological samples, 88 technical libraries and four
processing cohorts, including repeated donors and samples spanning processing
cohorts. Disease-by-cohort common support was not uniform, so discovery of identity
could use the full disease-blind cell set whereas disease coefficients were
restricted to prespecified supported contrasts.

Complete-library doublet diagnostics, recurrent highly variable gene selection,
unintegrated and Harmony representations, bridge-sample checks and marker coverage
were reviewed before outcome access. The initial five-state identity solution did
not satisfy the prespecified resampling thresholds. This negative result was
preserved rather than relabelled as a successful subtype analysis. Transition
reconstruction supported a two-level model comprising `B_CONV` and `B_ASC`, with
naive-memory structure retained as a continuous program within `B_CONV` and
platelet-associated expression retained as a technical overlay.

The two-compartment solution reproduced in all 20 resampling runs. The minimum
mapped adjusted Rand index was 0.990, minimum mapping agreement was 0.9998 and the
minimum state median Jaccard index was 0.991. `B_ASC` identity was independently
supported by DERL3, JCHAIN, MZB1, TNFRSF17 and XBP1. These results authorize broad
conventional-B and antibody-secreting compartments, but not hard naive, memory or
atypical publication subtypes.

### B_ASC composition is secondary rather than the central disease signal

Protected outcomes were joined only after the two-compartment freeze. Composition
was estimated at the sample-cohort level, with a minimum of 50 eligible B cells per
stratum and no cell-level disease test. In the primary processing-cohort-4 contrast,
the conditional odds ratio for `B_ASC` relative abundance was 0.947 (95% confidence
interval 0.636-1.410; P=0.787). Adjusted fractions were 1.61% in controls and 1.52%
in managed SLE. The HC1 sandwich audit was concordant (95% confidence interval
0.651-1.376; P=0.774), and all 90 leave-one-sample-out estimates retained the same
direction without generating statistical support.

The internal validation estimate was also below one (odds ratio 0.772), as was the
explicit donor-nonoverlap estimate (odds ratio 0.591; n=53), but neither converted
the null primary result into a central composition claim. A secondary flare contrast
was positive (odds ratio 2.303; nominal P=0.0282) but did not survive the frozen
three-contrast correction (q=0.0845). Accordingly, abundance results provide
context for the transcriptional analysis and a transparent negative boundary, not
evidence for a generally expanded `B_ASC` compartment.

### Within-B_CONV transcription identifies a reproducible IFN/ISG program

Raw counts were aggregated into sample-cohort `B_CONV` pseudobulks after technical
library contributions from the same stratum were combined. The primary analysis
included 89 pseudobulks, comprising 43 reference and 46 SLE strata, and retained
59,873,385 UMI counts. Gene-level inference used TMM normalization,
`filterByExpr`, robust edgeR quasi-likelihood models and Benjamini-Hochberg
correction within each contrast. A separately frozen four-program family was tested
from TMM log-counts-per-million values using positive-minus-negative standardized
scores and HC3 uncertainty.

The prespecified IFN/ISG program was higher in SLE in the primary contrast
(effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6). The effect was
positive at 20- and 100-cell support thresholds, after residual-doublet-risk calls
were excluded, and in all 89 leave-one-sample-out fits. Ranked-gene evidence was
coherent, with all ten tested genes in the expected arm direction and competitive
enrichment at approximately q=2 x 10^-6. Leading genes included USP18, IFI44L,
EPSTI1, IFIT3, MX1, IFI6, OAS2, ISG15 and STAT1.

The IFN/ISG program was also higher in the full internal GSE174188 validation
contrast (effect 0.856; q=0.00462) and in the prespecified donor-nonoverlap subset
(effect 1.086; q=3.61 x 10^-4). These strata belong to the same accession and are
therefore described as internal replication, not an independent cohort.

Two other frozen programs provided more limited GSE174188 context. The
naive-to-memory axis was lower in the primary SLE contrast (effect -0.541;
q=0.0213), and the APC/HLA program was higher (effect 0.268; q=0.0213), but neither
had multiplicity-supported internal validation. The atypical/low-naive program was
null in the primary contrast (effect -0.057; q=0.748). These axes are not co-equal
with IFN/ISG and were not used to redefine the identity compartment.

### Independent GSE135779 analysis replicates IFN remodeling but not a genome-wide state

GSE135779 source matrices and metadata were audited before any disease effect was
calculated. The mapping contract authorized only a broad conventional-B analog
constructed from source B-cell labels; it did not authorize transfer of hard
naive-memory identities. Matrix import and edgeR behavior were qualified with
count-conservation checks and synthetic null and signal data before the real
external contrasts were unlocked.

The primary childhood analysis included 43 donors (11 controls and 32 SLE) with at
least 50 mapped cells per donor. The frozen IFN/ISG program was higher in SLE
(effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined
childhood-adult analysis included 54 donors (16 controls and 38 SLE) and yielded a
similar estimate (effect 0.996, 95% confidence interval 0.655-1.337;
q=1.31 x 10^-6). Results remained positive at minimum support thresholds of 20
(effect 0.965; q=6.75 x 10^-7) and 100 cells (effect 0.939; q=4.06 x 10^-6).

The adult-only estimate was positive (effect 0.968) but imprecise (95% confidence
interval -0.123 to 2.060; q=0.291) because it contained five controls and six SLE
donors. It is therefore directionally compatible rather than confirmatory. Across
43 childhood donor-deletion fits, IFN/ISG effects ranged from 0.987 to 1.094.
Omitting each of the eight source B-cell labels in turn retained the same 43 donors
and produced effects from 1.019 to 1.051, excluding dependence on a single source
label.

Specificity analyses separated the IFN signal from several alternative explanations.
In the childhood contrast, the platelet/ambient, ASC/UPR and pan-B control effects
were 0.049, 0.221 and -0.232, respectively, compared with 1.042 for IFN/ISG. All 12
available frozen IFN-arm genes were positive, and ranked enrichment had a camera FDR
of 1.85 x 10^-7. Ten IFN genes were jointly tested in the primary GSE174188 and
childhood GSE135779 analyses, and all ten were positive in both.

This coherence did not extend across the complete tested transcriptome. Among 4,410
shared tested genes, cross-dataset effect correlation was only Spearman rho=0.026.
Thus, the evidence supports program-specific IFN replication across heterogeneous
cohorts, not a globally shared disease transcriptome. The GSE135779
atypical/low-naive score was positive (effect 1.191; q=5.10 x 10^-4), but the
corresponding GSE174188 result was null; it is retained as an external-only
observation rather than replication. Conversely, the GSE174188 naive-to-memory and
APC/HLA signals were null externally.

## Discussion

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
the stronger former interpretation.

The results also narrow several common SLE B-cell narratives. The naive-to-memory and
APC/HLA axes are useful internal context but do not independently reproduce in
GSE135779. The external atypical/low-naive signal cannot be labelled replication
because it was absent in GSE174188. Likewise, stable broad `B_CONV` identity does not
establish a discrete IFN-high subtype: interferon is treated as a continuous
within-compartment program.

The analysis has limitations. Public metadata did not provide a common set of sex,
treatment and detailed clinical covariates across all contrasts. The adult external
stratum was small, and two adult metadata donors lacked corresponding source
matrices. The GSE174188 internal validation is not independent of the accession even
after donor overlap is removed. The conventional-B mapping in GSE135779 relies on
source labels and supports a broad analog rather than exact identity transfer.
Finally, transcription-factor target enrichment, if subsequently supported, remains
observational. The current inference is association rather than causation.

The next analytical question is deliberately narrower than an open regulator search:
whether prespecified STAT1, STAT2, IRF7 and IRF9 target activity follows the frozen
IFN result across the same contrasts and is absent from nominated negative controls.
That analysis requires its own pre-effect resource and multiplicity contract. Until
it passes, the defensible advance is a multi-cohort descriptive result: independently
replicated IFN transcriptional remodeling within a disease-blind broad
conventional-B compartment.

## Methods

### Study design and data resources

The study was a secondary analysis of public human transcriptomic data. GSE174188
was used for disease-blind B-lineage reconstruction, sample-level composition,
within-compartment transcriptional analysis and internal validation. GSE135779 was
the independent SLE validation dataset. GSE163121 was reserved for directional
boundary analysis and OneK1K for healthy reference context; neither contributes to
the central replication claim reported here.

### Source integrity, metadata hierarchy and hard quality control

Source paths, SHA-256 hashes, matrix dimensions and matrix encodings were frozen
before analysis. Metadata keys were audited at donor, biological-sample, technical-
library and processing-cohort levels. Hard-quality-control thresholds were at least
500 total counts, at least 200 detected genes, no more than 10% mitochondrial counts,
no more than 1% haemoglobin counts, no more than 0.5% platelet-marker counts and
detection of at least one B-lineage marker. Each excluded cell retained a reason-level
record. Protected disease fields were stored separately during reconstruction.

### Disease-blind representation and identity freeze

Residual doublet risk was evaluated per complete library. Raw counts were retained
for pseudobulk, whereas normalized log expression was used for recurrent highly
variable gene selection, principal components and neighbor graphs. Unintegrated and
Harmony-adjusted representations were compared using technical mixing, biological
marker conservation, bridge samples and coverage across donors, samples and
libraries. Leiden solutions were evaluated across resolutions and 20 cell-resampling
runs. Failure of the fine-grained solution was retained. A two-compartment solution
was reconstructed from resampling transitions and approved only after marker and
stability checks while disease remained blinded.

### Sample-level composition

Cells were aggregated by biological sample and processing cohort. The experimental
unit was the sample-cohort stratum, with donor-aware sensitivity analyses for
repeated samples. Models were restricted to prespecified processing cohorts with
case-control common support and to strata with at least 50 frozen B cells. The
primary comparison was processing cohort 4 managed SLE versus normal, adjusted for
age and ethnicity. Internal processing-cohort-2 and secondary processing-cohort-3
flare analyses were estimated separately. Bridge strata were not used to manufacture
a pooled disease coefficient. Model, sandwich, threshold, one-sample-per-donor and
leave-one-out diagnostics were retained.

### Raw-count pseudobulk and gene-level inference

Raw counts were summed by sample-cohort stratum within `B_CONV`, combining technical
library contributions only after cell-ID and count conservation checks. Strata with
at least 50 cells were primary; 20- and 100-cell thresholds and a residual-risk-
negative cell branch were prespecified sensitivities. Genes were filtered with
edgeR `filterByExpr`, libraries were TMM-normalized, and robust quasi-likelihood
models were fitted with the frozen contrast-specific covariates. Benjamini-Hochberg
adjustment was applied over tested genes within each contrast. Full feature tables
retained untested genes with explicit flags.

### Frozen program inference

Program membership and direction were frozen before disease effects. Duplicate gene
symbols were summed before TMM log-counts-per-million normalization. Within each
contrast, genes were standardized across pseudobulks and program scores were computed
as the mean positive-arm score minus the mean negative-arm score. Disease effects and
95% confidence intervals used linear models with HC3 sandwich uncertainty. The
confirmatory family comprised naive-to-memory, atypical/low-naive, APC/HLA and
IFN/ISG programs; Benjamini-Hochberg correction was applied across these four tests.
Ranked competitive enrichment and gene-direction coherence were secondary support.

### Independent GSE135779 validation

GSE135779 source files, metadata versions, donor availability, source-label support
and frozen program-gene availability were audited without inspecting disease effects.
The external identity scope was a broad conventional-B analog formed from eight
source B-cell labels. Childhood, adult and combined model matrices and minimum-cell
sensitivities were frozen before model fitting. Real matrices were imported for
dimension and count-conservation qualification only; synthetic null and signal data
qualified the statistical engine before the real disease coefficients were
unlocked. Gene and program methods then matched the GSE174188 framework where the
different gene universe allowed.

### Influence, specificity and cross-dataset analyses

The childhood IFN/ISG model was repeated after deleting each donor. Source-label
dependence was assessed by omitting each of the eight contributing labels without
reselecting donors. Platelet/ambient, ASC/UPR and pan-B families were prespecified as
controls. Cross-dataset gene analysis was restricted to genes passing the respective
filters in both primary datasets; the shared IFN subset was reported separately from
the genome-wide rank correlation.

### Reproducibility and governance

Every gate used timestamped run directories, immutable source objects, deterministic
seeds, environment records, machine-readable decisions and SHA-256 integrity
manifests. Real effects were calculated only after input, design and statistical-
engine qualification. Earlier manuscripts and figures were retained for provenance
but were not used as numerical sources for this version.

## Figure legends

### Figure 1 | Audited study hierarchy and disease-blind B-lineage reconstruction

**a,** Dataset roles and outcome-lock sequence. **b,** Donor, sample, library and
processing-cohort hierarchy. **c,** Disease-by-cohort common-support matrix defining
permissible contrasts. **d,** Hard-quality-control retention. **e,** Disease-blind
two-compartment stability and marker support. Identity panels contain descriptive
cell-level summaries; no cell is treated as a disease replicate.

### Figure 2 | Sample-level B_ASC composition is not the central SLE result

**a,** Per-sample `B_ASC` relative abundance in the primary contrast. **b,** Adjusted
primary effect with model and HC1 intervals. **c,** Primary, internal validation,
donor-nonoverlap and flare contrasts. **d,** Mandatory sensitivity and leave-one-out
diagnostics. Odds ratios use sample-cohort strata as experimental units. The flare
result is secondary and does not pass the frozen three-contrast FDR rule.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

**a,** Frozen pseudobulk design and sample support. **b,** Four confirmatory program
effects in the primary contrast. **c,** IFN/ISG effects across primary, internal
validation, donor-nonoverlap and support sensitivities. **d,** Ranked IFN-gene
coherence and leading genes. Effects are SLE minus reference standardized program
scores; intervals use HC3 uncertainty and q values use the frozen four-program
Benjamini-Hochberg family.

### Figure 4 | GSE135779 independently replicates the frozen IFN/ISG program

**a,** Childhood, combined, adult and support-threshold IFN/ISG estimates. **b,**
GSE174188 discovery/internal estimates beside independent GSE135779 estimates.
**c,** Shared tested-gene effects, with the frozen IFN genes highlighted and the
genome-wide Spearman correlation reported as context. **d,** Childhood donor-deletion
and source-label omission estimates. Effects are standardized program-score
differences; donors are the biological units in GSE135779.

## Data and code availability

All source accessions are public. Analysis code, machine-readable decisions, compact
source-data tables and figure outputs are versioned in the project repository. Large
recomputable matrices remain local with SHA-256 records and scripted regeneration.

## References

References will be resolved from `references_verified_crossref_2026-07-09.bib` after
the C6B decision and journal-format freeze. The numerical and analytical claims in
this draft derive only from the frozen C2B4, C3A, C4B and C5B project outputs.
