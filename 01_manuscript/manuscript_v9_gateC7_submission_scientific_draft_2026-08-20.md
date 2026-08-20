# Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence in systemic lupus erythematosus B cells

**Version:** Gate C7 submission-scientific draft v9
**Date:** 20 August 2026
**Status:** Gate C7 scientific and five-figure freeze; journal formatting, author metadata and declarations remain to be finalized

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
subtype, causal regulator or unique upstream stimulus.

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
broad conventional-B compartment. We then tested a prespecified IFN-centred
TF-target family and two orthogonal response resources to ask whether this replicated
program had convergent regulatory support without converting association into a
causal claim.

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


### Prespecified regulatory and perturbational evidence converges on the IFN response

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
perturbation in healthy-donor B cells.

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
differential-expression result and narrower than a causal mechanism claim.

## Methods

### Study design and data resources

The study was a secondary analysis of public human transcriptomic data. GSE174188
was used for disease-blind B-lineage reconstruction, sample-level composition,
within-compartment transcriptional analysis and internal validation. GSE135779 was
the independent SLE validation dataset. CollecTRI and MSigDB supplied independently
curated regulatory and response priors, and GSE23307 supplied paired IFN-beta
perturbation profiles from healthy-donor primary B cells. GSE163121 was reserved for
directional boundary analysis and OneK1K for healthy reference context; neither
contributes to the central replication claim reported here.

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


### Prespecified TF-target activity

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
active result, figure and claim.

### Reproducibility and governance

Every gate used timestamped run directories, immutable source objects, deterministic
seeds, environment records, machine-readable decisions and SHA-256 integrity
manifests. Real effects were calculated only after input, design and statistical-
engine qualification. Earlier manuscripts and figures were retained for provenance
but were not used as numerical sources for this version.

## Figure legends

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
descriptive at n=2.

## Data and code availability

GSE174188, GSE135779 and GSE23307 are public Gene Expression Omnibus accessions.
Analysis code, machine-readable decisions, compact source-data tables, figure PDFs
and 600-dpi PNGs are versioned in the project repository. Large recomputable
matrices remain local with SHA-256 records and scripted regeneration. Figure-level
source data and a claim-to-number crosswalk are frozen under Gate C7.

## References

1. Perez RK et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. *Science*. 2022. doi:10.1126/science.abf1970.
2. Nehar-Belaid D et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. *Nature Immunology*. 2020. doi:10.1038/s41590-020-0743-0.
3. Crowell HL et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. *Nature Communications*. 2020. doi:10.1038/s41467-020-19894-4.
4. Squair JW et al. Confronting false discoveries in single-cell differential expression. *Nature Communications*. 2021. doi:10.1038/s41467-021-25960-2.
5. Buttner M et al. scCODA is a Bayesian model for compositional single-cell data analysis. *Nature Communications*. 2021. doi:10.1038/s41467-021-27150-6.
6. Badia-I-Mompel P et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. *Bioinformatics Advances*. 2022. doi:10.1093/bioadv/vbac016.
7. Muller-Dott S et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. *Nucleic Acids Research*. 2023. doi:10.1093/nar/gkad841.
8. Liberzon A et al. The Molecular Signatures Database Hallmark Gene Set Collection. *Cell Systems*. 2015. doi:10.1016/j.cels.2015.12.004.
9. van Boxel-Dezaire AHH et al. Major differences in the responses of primary human leukocyte subsets to IFN-beta. *Journal of Immunology*. 2010;185:5888-5899. doi:10.4049/jimmunol.0902314.
