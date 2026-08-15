# MBI6013 Research Proposal

## Independent validation and regulatory prioritization of interferon remodeling in systemic lupus erythematosus B cells

**Outcome-integrated version 15**
**Date:** 15 August 2026
**Study type:** secondary analysis of public human transcriptomic data
**Governance status:** Gates C1-C5B completed; Gate C6A claim freeze completed; regulatory effects remain locked pending Gate C6B

## Project summary

Systemic lupus erythematosus (SLE) is associated with B-cell dysregulation and a
prominent type I interferon response. Single-cell data can distinguish changes in
cellular abundance from changes in gene expression within a stable compartment, but
only when disease labels, technical cohorts and biological replication are handled
explicitly. This project reanalyses public SLE single-cell data through a sequence of
audited, pre-effect gates.

The completed analysis establishes three findings. First, disease-blind resampling
supports two broad B-lineage identity compartments, conventional B cells (`B_CONV`)
and antibody-secreting cells (`B_ASC`), but does not support a hard naive-memory
subtype partition for outcome inference. Second, primary sample-level `B_ASC`
composition is null and cannot serve as the central claim. Third, a frozen type I
interferon/interferon-stimulated-gene (IFN/ISG) program is increased within `B_CONV`
in GSE174188 and independently replicated in GSE135779.

The remaining proposal is therefore focused rather than exploratory. It will test
whether the replicated IFN program is accompanied by prespecified STAT1, STAT2, IRF7
and IRF9 target activity and by orthogonal IFN perturbation evidence. This work will
prioritize a regulatory hypothesis while maintaining association rather than
causation as the interpretive boundary.

## 1. Background and significance

SLE is a heterogeneous autoimmune disease in which loss of B-cell tolerance,
autoantibody production, nucleic-acid sensing and type I interferon signalling
interact across patients and disease stages. Peripheral B-cell abnormalities include
changes in naive and memory compartments, antibody-secreting cells and
CD11c-positive or double-negative populations. These labels are biologically useful,
but their boundaries differ across studies and may not be stable in every dataset.

Two inferential problems are especially important. Cells from the same donor are not
independent disease replicates, and a change in the relative abundance of a cell
compartment is not the same as a transcriptional change within that compartment.
Sample-level composition and sample-by-compartment pseudobulk therefore answer
different questions. In addition, processing cohorts may be imbalanced for disease,
so a pooled disease coefficient can absorb technical structure even when a large
number of cells is available.

The Perez et al. GSE174188 resource provides extensive donor and technical coverage,
but its hierarchy includes repeated donors, biological samples split across
libraries, bridge samples and disease imbalance across processing cohorts.
GSE135779 provides an independent SLE cohort with childhood and adult strata, but its
source annotation and available covariates differ from GSE174188. A defensible
cross-dataset claim must therefore be frozen at the program level and cannot assume
exact transfer of fine B-cell subtypes.

Type I IFN signalling provides a biologically plausible focus because the ISGF3
complex and related interferon regulatory factors can coordinate canonical
interferon-stimulated genes. Nevertheless, enrichment of TF targets in observational
disease contrasts does not demonstrate that a TF caused the disease state. Curated
regulons and public perturbation datasets can supply convergent evidence, but causal
language requires a relevant intervention with adequate biological replication.

## 2. Central hypothesis and aims

### Central hypothesis

SLE is associated with a reproducible IFN/ISG transcriptional shift within a
disease-blind broad conventional-B compartment, whereas fine-grained identity and
abundance changes are less reproducible. A prespecified interferon-centred regulator
family should show concordant target activity across the same donor-level contrasts
if it contributes to the observed program.

### Aim 1. Reconstruct disease-blind B-lineage identity from audited raw counts

**Status:** completed.

Raw-count integrity, metadata hierarchy, complete-library doublet risk, technical
mixing, bridge-sample behavior, marker support and graph resampling were audited
before disease outcomes were joined. The original fine-grained state solution failed
the stability gate. A two-compartment model (`B_CONV` and `B_ASC`) reproduced in
20/20 resamples, with minimum mapped adjusted Rand index 0.990 and minimum state
median Jaccard index 0.991.

**Binding interpretation:** `B_CONV` is a broad conventional-B analog. Naive-memory
structure is continuous within this compartment; hard naive, memory and atypical
composition labels are prohibited.

### Aim 2. Separate SLE-associated composition from within-compartment transcription

**Status:** completed.

Sample-cohort composition models did not support a primary `B_ASC` difference
(odds ratio 0.947, 95% confidence interval 0.636-1.410; P=0.787). A flare estimate
was nominally positive but did not survive the frozen three-contrast correction
(q=0.0845). Composition is therefore secondary.

Raw counts were then aggregated into sample-cohort `B_CONV` pseudobulks. The frozen
IFN/ISG program was increased in the primary GSE174188 contrast (effect 0.837,
95% confidence interval 0.525-1.148; q=2.98 x 10^-6) and in a donor-nonoverlap
internal contrast (effect 1.086; q=3.61 x 10^-4). Naive-to-memory and APC/HLA were
retained as supporting internal axes, while the atypical/low-naive program was null.

### Aim 3. Test the frozen IFN/ISG program in an independent SLE dataset

**Status:** completed.

GSE135779 source files, metadata, source labels, support thresholds and program genes
were frozen before external disease effects were calculated. The childhood contrast
included 11 controls and 32 SLE donors and replicated the IFN/ISG direction
(effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined
contrast was similar (effect 0.996; q=1.31 x 10^-6). All donor-deletion and
source-label omission estimates remained positive. The adult estimate was positive
but underpowered. Cross-dataset correlation across all shared tested genes was low
(Spearman rho=0.026), establishing a program-specific rather than transcriptome-wide
result.

### Aim 4. Test a frozen interferon-centred regulatory hypothesis

**Status:** planned under Gate C6B; no regulator effect has been inspected.

The exact regulator family, negative controls, network resource, ranked-statistic
inputs, multiplicity rule and acceptance thresholds will be frozen before analysis.
The primary family is STAT1, STAT2, IRF7 and IRF9. The same GSE174188 primary,
GSE174188 donor-nonoverlap and GSE135779 childhood contrasts will be used. Curated
TF-target evidence will be complemented by an exact type I IFN response signature
and a small public perturbation dataset used only within its replication limits.

**Expected outcome:** either convergent regulator activity that justifies a carefully
qualified regulatory framing, or a negative result that leaves the independently
replicated IFN program intact and removes regulator language from the main paper.

## 3. Completed evidence base

### 3.1 Source and design integrity

The GSE174188 B-lineage source contained 152,981 cells and 30,172 genes. Frozen hard
quality control retained 150,402 cells. Metadata resolved 259 donors, 271 biological
samples, 88 libraries and four processing cohorts. Disease common support was
adequate for a primary managed-SLE versus normal contrast in processing cohort 4,
an internal processing-cohort-2 contrast and a secondary processing-cohort-3 flare
contrast. Cohorts without both disease groups were not used to estimate a disease
coefficient.

### 3.2 Disease-blind identity

The initial five-state solution failed resampling stability, with the instability
localized mainly to conventional-B subdivisions. Transition reconstruction did not
erase this negative result. It justified only `B_CONV` versus `B_ASC`, supported by
20 resamples and an orthogonal antibody-secreting marker panel. Protected outcomes
were unlocked only for two-compartment composition and prespecified continuous
programs within `B_CONV`.

### 3.3 Composition boundary

The primary `B_ASC` model converged and all mandatory sensitivity and leave-one-out
fits retained its direction, but its confidence interval included the null. This
combination is scientifically useful: model stability does not create a biological
effect where the estimate provides no support. The result is retained as a negative
boundary and secondary context.

### 3.4 Transcriptional discovery and internal replication

The primary `B_CONV` pseudobulk design included 89 sample-cohort strata with at least
50 cells. Gene-level edgeR and frozen HC3 program analyses were qualified before
real effects were unlocked. IFN/ISG was the only program that combined primary
support, internal multiplicity-supported replication, threshold stability,
residual-risk stability, leave-one-out stability and ranked-gene coherence.

### 3.5 Independent replication and specificity

GSE135779 childhood, adult and combined matrices were frozen before model fitting.
The childhood IFN estimate remained positive across 43 donor deletions and eight
source-label omissions. Platelet/ambient, ASC/UPR and pan-B controls were much smaller
than the IFN effect. Ten frozen IFN genes were jointly tested in both primary
datasets, and all ten were positive in both. In contrast, broad tested-gene effects
had rho=0.026, and the non-IFN programs did not reproduce consistently.

## 4. Research design for Gate C6B

### 4.1 Pre-effect governance

Gate C6B will be split into resource qualification and effect analysis. Resource
retrieval, file hashes, organism, gene-identifier convention, regulator nodes,
complex-handling policy and target coverage will be recorded first. Synthetic and
permutation checks will qualify the method. Real disease-ranked statistics will not
be scored until all pre-effect checks pass.

### 4.2 Frozen contrasts

The confirmatory contrasts will be:

1. GSE174188 primary processing-cohort-4 `B_CONV`;
2. GSE174188 donor-nonoverlap processing-cohort-2 `B_CONV`; and
3. GSE135779 childhood broad conventional-B.

GSE174188 full internal validation, GSE135779 combined and support-threshold variants
will be sensitivities. Adult GSE135779 will remain directional only. No contrast may
be selected or discarded after regulator effects are viewed.

### 4.3 Curated TF-target analysis

The primary network will be human CollecTRI retrieved through the OmniPath service
and frozen by SHA-256. Only the prespecified IFN-centred family and a prespecified
non-IFN control family will enter confirmatory multiplicity. Regulator activity will
be estimated from complete ranked gene statistics, not from lists selected by an
FDR threshold. Target-direction weights will be retained, and regulators below the
frozen minimum target coverage will be marked unavailable rather than silently
redefined.

### 4.4 Orthogonal IFN-response evidence

The exact MSigDB Hallmark interferon-alpha response set will provide an external
response signature with a traceable identifier and version. A public human B-cell or
PBMC IFN perturbation dataset may be used for direction only if donor replication is
insufficient. Perturbation evidence will be interpreted according to cell context,
IFN type, exposure time and biological replication; it will not be used to claim
that an observational SLE contrast identifies a unique upstream cause.

### 4.5 Multiplicity and acceptance

Multiplicity will include all nominated IFN and negative-control regulator activities
in the three confirmatory contrasts. An upper-Q1 regulatory framing will require
concordant positive activity for the prespecified IFN family in all three contrasts,
survival of the frozen correction and failure of the negative-control family to show
the same pattern. Donor influence, target coverage and technical-family enrichment
must remain acceptable. Failure at any step will return the manuscript to a strong
descriptive IFN-remodeling conclusion.

## 5. Potential difficulties and alternatives

**Regulon coverage differs across gene universes.** Each regulator must meet a frozen
minimum target count in every confirmatory contrast. A missing regulator will be
reported as unavailable rather than replaced after results are known.

**TF complexes are represented inconsistently.** The handling of STAT1-STAT2-IRF9
complexes versus individual subunits will be frozen after no-effect resource
inspection. Primary and sensitivity encodings will be declared before disease-ranked
statistics are scored.

**Public perturbation data lack replication or B-cell specificity.** Such datasets
will provide descriptive direction or literature context only. They cannot satisfy
the confirmatory regulatory gate by themselves.

**Regulator activity is null despite strong IFN genes.** The IFN/ISG program result
does not depend on a regulator analysis. Null regulator evidence will be reported and
mechanistic wording removed.

**Regulator activity is broad rather than IFN-specific.** A matched non-IFN control
family and technical gene families will test whether many regulons rise together.
Broad nonspecific activation will not pass the gate.

## 6. Milestones and decision gates

| Gate | Deliverable | Status or pass criterion |
|---|---|---|
| C2B4 | disease-blind two-compartment identity | completed; outcome scope frozen |
| C3A | sample-level composition | completed; central composition claim rejected |
| C4B | GSE174188 pseudobulk and programs | completed; IFN prioritized |
| C5A-C5B | pre-effect external freeze and GSE135779 test | completed; IFN independently replicated |
| C6A | claim matrix, manuscript and figure architecture | completed when all claims trace to frozen outputs |
| C6B-1 | resource and software qualification | exact hashes, coverage and synthetic checks pass |
| C6B-2 | frozen regulator and perturbation analyses | prespecified cross-dataset criteria pass or fail transparently |
| C7 | submission manuscript and source-data package | every main-text number and panel maps to a frozen source |

## 7. Expected impact

The project provides a reproducible framework for distinguishing B-cell identity,
relative abundance and within-compartment transcription in heterogeneous public
single-cell studies. Its SLE contribution is already bounded and substantive: a
frozen IFN/ISG program replicates across independent datasets despite low
genome-wide effect agreement, while unsupported subtype and composition claims are
removed. Gate C6B will determine whether the paper can add a convergent regulatory
layer or should remain a rigorous multi-cohort descriptive study.

## 8. Claim and writing boundaries

- Use broad conventional-B compartment, not a hard naive/memory subtype.
- Describe relative abundance, not absolute expansion or depletion.
- Reserve independent replication for the GSE135779 IFN/ISG result.
- Describe the adult result as positive but underpowered.
- State that replication is program-specific and genome-wide agreement is low.
- Treat TF-target enrichment as candidate regulatory evidence.
- Preserve association rather than causation in the title, abstract and conclusion.

## References

1. Perez RK et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. *Science*. 2022. doi:10.1126/science.abf1970.
2. Nehar-Belaid D et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. *Nature Immunology*. 2020. doi:10.1038/s41590-020-0743-0.
3. Crowell HL et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. *Nature Communications*. 2020. doi:10.1038/s41467-020-19894-4.
4. Squair JW et al. Confronting false discoveries in single-cell differential expression. *Nature Communications*. 2021. doi:10.1038/s41467-021-25960-2.
5. Buttner M et al. scCODA is a Bayesian model for compositional single-cell data analysis. *Nature Communications*. 2021. doi:10.1038/s41467-021-27150-6.
6. Badia-I-Mompel P et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. *Bioinformatics Advances*. 2022. doi:10.1093/bioadv/vbac016.
7. Muller-Dott S et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. *Nucleic Acids Research*. 2023. doi:10.1093/nar/gkad841.
8. Liberzon A et al. The Molecular Signatures Database Hallmark Gene Set Collection. *Cell Systems*. 2015. doi:10.1016/j.cels.2015.12.004.
