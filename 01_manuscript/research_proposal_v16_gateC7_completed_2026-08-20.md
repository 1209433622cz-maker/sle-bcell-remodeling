# MBI6013 Research Proposal

## Independently replicated interferon remodeling with convergent regulatory evidence in systemic lupus erythematosus B cells

**Outcome-integrated version 16**
**Date:** 20 August 2026
**Study type:** secondary analysis of public human transcriptomic data
**Governance status:** Gates C1-C7 scientific integration completed; all central claims remain noncausal

## Version provenance

This outcome-integrated RP is a completed-study record, not a prospective
preregistration. The frozen pre-outcome methodological provenance remains
`research_proposal_v14_methodologically_revised_2026-08-10.md` and its dated
DOCX/PDF renderings. Gate C8S manuscript v12 is the canonical submission report
for final numerical, supplementary and statistical-traceability details. These
documents have distinct roles and should remain versioned rather than merged or
silently overwritten.

## Project summary

This project separates B-cell identity, relative abundance and within-compartment
transcription in public systemic lupus erythematosus (SLE) single-cell data. The
analysis was organized as sequential pre-effect gates: source integrity and metadata
hierarchy; disease-blind identity reconstruction; sample-level composition;
sample-by-compartment pseudobulk transcription; independent dataset validation; and
prespecified regulatory and perturbational convergence.

Four findings are complete. First, disease-blind resampling supports two broad
B-lineage compartments, conventional B cells (`B_CONV`) and antibody-secreting cells
(`B_ASC`), while finer hard naive-memory states are insufficiently stable for
outcome inference. Second, the primary sample-level `B_ASC` composition contrast is
null. Third, a frozen type I interferon/interferon-stimulated-gene (IFN/ISG) program
within `B_CONV` replicates from GSE174188 into independent GSE135779. Fourth,
prespecified STAT1/STAT2 target activity, exact M5911 enrichment and a small paired
IFN-beta B-cell perturbation dataset converge on the same response. The project
supports an observational IFN-centred regulatory framing, not a new subtype, a
unique upstream stimulus or causation.

## 1. Background and significance

SLE is a heterogeneous autoimmune disease involving loss of B-cell tolerance,
autoantibody production and sustained innate immune activation. Single-cell studies
can distinguish abundance changes from transcriptional changes only when donors,
samples, libraries and processing cohorts are represented correctly. Cells from one
donor are not independent disease replicates, and disease-informed annotation can
make identity itself depend on the outcome being tested.

GSE174188 provides extensive B-lineage coverage but includes repeated donors,
technical library structure, bridge samples and disease imbalance across processing
cohorts. GSE135779 provides an independent SLE cohort with childhood and adult
strata, but its source labels and gene universe differ. Exact hard-subtype transfer
would therefore be stronger than the available evidence. A broad conventional-B
compartment and frozen continuous programs provide a more reproducible target.

Type I IFN is biologically plausible in SLE, yet observational target enrichment
does not demonstrate which ligand initiated the state or whether a transcription
factor directly bound the nominated genes. Curated regulons and perturbation data
can add convergence if they are frozen before effect inspection and interpreted
within their replication limits.

## 2. Central hypothesis and completed aims

### Central hypothesis

SLE is associated with a reproducible IFN/ISG transcriptional shift within a
disease-blind broad conventional-B compartment. Prespecified IFN-centred target
activity and orthogonal interferon-response resources should be concordant if this
program reflects biologically coherent IFN regulation. The completed results support
this hypothesis at an observational, noncausal level.

### Aim 1. Reconstruct disease-blind B-lineage identity from audited raw counts

**Status:** completed.

The GSE174188 source contained 152,981 B-lineage cells and 30,172 genes. Hard quality
control retained 150,402 cells. The initial five-state policy failed the frozen
resampling gate. A repaired two-compartment model (`B_CONV`, `B_ASC`) reproduced in
20/20 resamples, with minimum mapped adjusted Rand index 0.990 and minimum state
median Jaccard index 0.991. Hard naive, memory and atypical composition labels remain
prohibited.

### Aim 2. Separate SLE-associated composition from within-compartment transcription

**Status:** completed.

The primary `B_ASC` composition contrast was unsupported (odds ratio 0.947, 95%
confidence interval 0.636-1.410; P=0.787). A secondary flare estimate did not survive
the frozen three-contrast correction (q=0.0845). In contrast, the frozen IFN/ISG
program was higher in GSE174188 primary `B_CONV` pseudobulks (effect 0.837, 95%
confidence interval 0.525-1.148; q=2.98 x 10^-6) and in the donor-nonoverlap internal
contrast (effect 1.086; q=3.61 x 10^-4).

### Aim 3. Test the frozen IFN/ISG program in an independent SLE dataset

**Status:** completed.

GSE135779 childhood donors independently replicated IFN/ISG (11 controls, 32 SLE;
effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined
estimate was 0.996 (q=1.31 x 10^-6), while the adult-only estimate was positive but
underpowered. Forty-three donor deletions and eight source-label omissions retained
the childhood direction. All ten jointly tested IFN genes were positive in both
primary datasets despite low genome-wide agreement (4,410 genes; rho=0.026).

### Aim 4. Test a frozen interferon-centred regulatory hypothesis

**Status:** completed; Gate C6B passed for noncausal regulatory framing.

STAT1 and STAT2 CollecTRI activity estimates were positive and global-24-test
significant in all three confirmatory contrasts. Core estimates retained direction
after every target deletion and in all 100 deterministic 80%-target resamples. The
proliferation-control family did not reproduce a positive globally significant
three-contrast pattern. M5911 was positively enriched in all three contrasts (NES
3.187, 3.050 and 3.527). In paired GSE23307 IFN-beta-exposed B cells, all 12 frozen
genes increased in each of two donors; mean log2(x+1) effects were 3.294 and 3.666.

## 3. Completed design and analytical methods

### 3.1 Source governance and experimental units

Source paths, dimensions, encodings and SHA-256 values were frozen. Metadata were
resolved at donor, biological-sample, technical-library and processing-cohort
levels. Protected disease fields remained separate during identity reconstruction.
Composition used sample-cohort strata; GSE174188 transcription used sample-cohort
`B_CONV` pseudobulks; GSE135779 used donor-level broad conventional-B pseudobulks.

### 3.2 Identity and composition

Identity representations were evaluated with marker conservation, technical mixing,
bridge coverage and 20 disease-blind resamples. Failure of fine states was retained.
Composition used supported cohort-specific conditional-binomial models, minimum 50
cells per stratum, HC1 checks, threshold sensitivities and leave-one-sample-out
analysis. No cell-level disease test was used.

### 3.3 Pseudobulk transcription and frozen programs

Raw counts were summed within biological units after count conservation. edgeR used
`filterByExpr`, TMM normalization and robust quasi-likelihood models. Frozen program
scores were computed from standardized TMM log-counts per million and tested with
HC3 linear models. Benjamini-Hochberg correction was applied across four
confirmatory programs. Support-threshold, residual-risk and leave-one-out branches
were prespecified.

### 3.4 Independent validation

GSE135779 source labels, donor availability, program genes and minimum-cell designs
were frozen before disease effects were calculated. Synthetic null and signal data
qualified the engine. Donor-deletion, source-label omission, technical-family and
shared-tested-gene analyses distinguished stable program replication from broad
transcriptome concordance.

### 3.5 Regulatory and orthogonal response analysis

Human CollecTRI was frozen from OmniPath. For each tested feature, the ranked
statistic was `sign(logFC) * sqrt(F)`; duplicate uppercase gene symbols were averaged.
A linear model with an intercept estimated the activity slope on signed target
weights. Eight regulators across three contrasts formed one 24-test global
Benjamini-Hochberg family. Core STAT1/STAT2 models underwent leave-one-target and
100 x 80% target-resampling analyses.

MSigDB 2026.1.Hs M5911 used 10,000 deterministic gene-label permutations per ranked contrast.
GSE23307 paired untreated and IFN-beta-exposed primary B-cell probes were transformed
as log2(x+1), median-collapsed to 12 genes and differenced within two donors. No
inferential P value was calculated at n=2. Superseded untransformed outputs are
audit-only and excluded from active evidence.

## 4. Completed evidence chain and claim hierarchy

| Layer | Result | Publication role |
|---|---|---|
| Identity | `B_CONV`/`B_ASC` pass; fine states fail | foundation and scope boundary |
| Composition | primary `B_ASC` null | negative boundary |
| Discovery | GSE174188 IFN/ISG positive | central association |
| Internal replication | donor-nonoverlap IFN/ISG positive | within-accession support |
| Independent replication | GSE135779 childhood IFN/ISG positive | central external evidence |
| Regulatory convergence | STAT1/STAT2 target activity reproduced | central noncausal support |
| Orthogonal response | M5911 and two-donor IFN-beta direction | supportive convergence |

The main paper is ordered in this inferential sequence. Each stronger claim depends
on the earlier scope boundary and cannot be used to retroactively redefine identity.

## 5. Limitations and alternatives

Public covariates are incomplete and differ across accessions. Adult GSE135779 is
underpowered. Source-label mapping supports a broad analog, not exact subtype
transfer. GSE174188 internal validation remains within the same accession. Regulon
activity depends on prior-network coverage and is not direct binding evidence.
GSE23307 has only two donors and a healthy ex vivo context. These limitations are
handled by preserving cohort-specific designs, reporting negative boundaries,
using independent program-level replication and prohibiting causal language.

Prospective patient sampling, matched clinical covariates, direct chromatin or
binding assays and replicated perturbation of patient-derived B cells would be
needed to advance from convergent regulation to mechanism.

## 6. Milestones and decision gates

| Gate | Deliverable | Final status |
|---|---|---|
| C2B4 | disease-blind two-compartment identity | passed; scope frozen |
| C3A | sample-level composition | passed; central composition claim rejected |
| C4B | GSE174188 pseudobulk and programs | passed; IFN prioritized |
| C5A-C5B | independent GSE135779 validation | passed; IFN replicated |
| C6A | claim and number freeze | passed |
| C6B | regulatory and orthogonal evidence | passed; noncausal framing authorized |
| C7 | five main figures and manuscript integration | completed by v9/v16 package |
| C8 | journal-specific submission package | next stage |

## 7. Expected impact

The project provides a reproducible framework for distinguishing identity,
composition and transcription in heterogeneous public single-cell studies. Its SLE
advance is a tightly bounded but substantive result: an independently replicated
IFN program within broad conventional B cells, supported by prespecified
cross-dataset regulatory activity and orthogonal response evidence despite low
genome-wide concordance. Transparent negative results prevent unstable subtype and
composition narratives from inflating the conclusion.

## 8. Binding writing boundaries

- Use broad conventional-B compartment, not a hard naive, memory or atypical subtype.
- Describe relative `B_ASC` abundance, not absolute expansion or depletion.
- Reserve independent replication for GSE135779 IFN/ISG.
- Describe the adult estimate as positive but underpowered.
- State that replication is program-specific and genome-wide agreement is low.
- Use convergent observational IFN-centred regulatory evidence.
- Do not claim direct binding, a unique IFN ligand, mechanism, causality or a new subtype.
- Cite only corrected log2(x+1) GSE23307 outputs 16-20; files 10-14 are superseded audit artifacts.

## References

1. Perez RK et al. *Science*. 2022. doi:10.1126/science.abf1970.
2. Nehar-Belaid D et al. *Nature Immunology*. 2020. doi:10.1038/s41590-020-0743-0.
3. Crowell HL et al. *Nature Communications*. 2020. doi:10.1038/s41467-020-19894-4.
4. Squair JW et al. *Nature Communications*. 2021. doi:10.1038/s41467-021-25960-2.
5. Badia-I-Mompel P et al. *Bioinformatics Advances*. 2022. doi:10.1093/bioadv/vbac016.
6. Muller-Dott S et al. *Nucleic Acids Research*. 2023. doi:10.1093/nar/gkad841.
7. Liberzon A et al. *Cell Systems*. 2015. doi:10.1016/j.cels.2015.12.004.
8. van Boxel-Dezaire AHH et al. *Journal of Immunology*. 2010;185:5888-5899. doi:10.4049/jimmunol.0902314.
