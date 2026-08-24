# Supplementary information

## Disease-blind single-cell reconstruction separates unstable B-cell states from reproducible interferon remodeling in systemic lupus erythematosus

**Version:** Pre-submission release-portability preflight, 25 August 2026

**Authors:** Zhi Chen and Teng Qi

## Supplementary overview

This release-portability preflight inherits the frozen reviewer-facing evidence and statistical traceability without changing upstream estimates. It adds seven supplementary figures reconstructed from frozen Gate C2B1-C8R outputs, corrected Figure 5 machine-readable panel labels, a unified multiplicity map and a complete statistical-results archive. Every main and supplementary panel has a machine-readable source table and hard data assertions.

## Supplementary Methods 1 | Prespecification and outcome protection

The workflow used prespecified stages for source integrity, hard quality control, disease-blind identity reconstruction, sample-level composition, within-compartment pseudobulk analysis, independent validation and external regulatory evidence. Protected disease fields were separated during identity reconstruction. Disease effects were estimated only after the relevant inputs, mappings, contrasts and statistical methods had been recorded. Each stage retained a machine-readable decision and SHA-256 integrity manifest.

## Supplementary Methods 2 | Identity stability boundary

The initial five-state model failed the prespecified resampling thresholds. Repair analyses evaluated four-, three- and two-level mappings without consulting disease labels. Only the broad B_CONV/B_ASC solution met all stability criteria across 20 resampling runs. Fine naive-memory structure was therefore retained as continuous transcriptional context rather than a hard publication subtype. This negative boundary is part of the result, not a quality-control artifact to be removed.

## Supplementary Methods 3 | Biological units and contrast hierarchy

GSE174188 composition and expression analyses used sample-by-processing-cohort strata; donor-aware sensitivities addressed repeated samples. GSE135779 used donors as biological units. Primary, internal, donor-nonoverlap, secondary flare, childhood, combined and adult contrasts remained separate. No bridge stratum was used to manufacture a pooled disease coefficient, and internal GSE174188 estimates were not described as independent validation.

## Supplementary Methods 4 | Robustness and specificity

Prespecified sensitivity analyses varied minimum cell support, excluded residual-doublet-risk cells, deleted samples or donors one at a time, omitted source labels and compared platelet/ambient, ASC/UPR and pan-B control programs. The TF-target family used one global correction across 24 tests. STAT1 and STAT2 core results underwent leave-one-target and deterministic 80% target-resampling analyses. The GSE23307 two-donor perturbation remained descriptive.

## Supplementary Methods 5 | Correlation-aware regulator sensitivity

The sensitivity reused frozen STAT1/STAT2 signed targets, model matrices, contrasts and tested-gene backgrounds. Voom precision weights fed CAMERA with residual-estimated inter-gene correlation and FRY directional rotation tests. BH adjustment was applied across six core tests within each method. Exact agreement with frozen ULM matched-target counts was mandatory. This was post-audit robustness testing and not independent replication.

## Supplementary Table S1 | Dataset roles and inferential units

| Resource | Role | Biological unit | Active scope |
|---|---|---|---|
| GSE174188 | Discovery and internal validation | Sample-cohort stratum; donor sensitivities | Disease-blind B_CONV/B_ASC identity, composition and B_CONV transcription |
| GSE135779 | Independent SLE validation | Donor | Broad conventional-B analog; childhood primary |
| CollecTRI/OmniPath | Curated regulator prior | Ranked genes within contrast | Prespecified eight-regulator, three-contrast family |
| MSigDB M5911 | Orthogonal response prior | Ranked genes within contrast | Hallmark interferon-alpha response enrichment |
| GSE23307 | Orthogonal perturbation support | Paired profile within donor | Descriptive IFN-beta response, n=2 donors |

## Supplementary Table S2 | Claim boundaries

| Supported | Not supported |
|---|---|
| Broad disease-blind B_CONV and B_ASC identity | Stable hard naive, memory or atypical subtypes |
| Null primary B_ASC relative-abundance result | General B_ASC expansion in SLE |
| Replicated IFN/ISG remodeling within B_CONV | Genome-wide shared disease transcriptome |
| Convergent STAT1/STAT2 target activity | Causal TF activation or direct binding |
| IFN-centred response evidence | A unique initiating IFN ligand in SLE |

## Supplementary Table S3 | Frozen quantitative anchors

| Analysis | Frozen result |
|---|---|
| Identity stability | minimum mapped ARI 0.990; minimum agreement 0.9998; minimum median Jaccard 0.991 |
| Primary B_ASC composition | 43 controls and 47 source-defined managed SLE; odds ratio 0.947; 95% CI 0.636-1.410; P=0.787 |
| GSE174188 primary IFN/ISG | effect 0.837; 95% CI 0.525-1.148; q=2.98 x 10^-6 |
| GSE174188 donor-nonoverlap IFN/ISG | effect 1.086; q=3.61 x 10^-4 |
| GSE135779 childhood IFN/ISG | effect 1.042; 95% CI 0.681-1.402; q=2.98 x 10^-6 |
| Cross-dataset genome-wide agreement | 4,410 genes; Spearman rho=0.026 |
| M5911 enrichment | NES 3.187, 3.050 and 3.527 |
| GSE23307 perturbation | donor effects 3.294 and 3.666; 12/12 genes positive in each |

## Supplementary Table S4 | Correlation-aware core-regulator sensitivity

| Contrast | Regulator | Matched targets | Inter-gene correlation | CAMERA BH q | FRY BH q |
|---|---|---:|---:|---:|---:|
| GSE174188 primary | STAT1 | 98 | 0.0362 | 0.0263 | 6.043e-06 |
| GSE174188 primary | STAT2 | 14 | 0.1225 | 0.1355 | 4.909e-05 |
| GSE174188 donor-nonoverlap | STAT1 | 129 | 0.0209 | 0.0263 | 8.49e-06 |
| GSE174188 donor-nonoverlap | STAT2 | 19 | 0.1191 | 0.0263 | 4.277e-07 |
| GSE135779 childhood | STAT1 | 161 | 0.0301 | 0.0263 | 2.685e-05 |
| GSE135779 childhood | STAT2 | 20 | 0.1223 | 0.03026 | 1.231e-05 |

CAMERA and FRY directions were positive in all six tests. CAMERA passed BH correction in five of six; the explicit exception was GSE174188 primary STAT2 (q=0.1355). FRY passed BH correction in all six.

## Supplementary Table S5 | Main-figure source-data map

| Figure | Frozen gate | Machine-readable source |
|---|---|---|
| Figure 1 | C2B4 identity freeze; C8S annotation repair | Figure1_source_data.csv |
| Figure 2 | C3A composition decision; asserted 43/47 groups | Figure2_source_data.csv |
| Figure 3 | C4B transcription; explicit filtered-gene symbols | Figure3_source_data.csv |
| Figure 4 | C5B independent validation | Figure4_source_data.csv |
| Figure 5 | C6B regulatory evidence; corrected D/E source labels | Figure5_source_data.csv |

## Supplementary Table S6 | Reproducibility record

| Component | Frozen record |
|---|---|
| Main-panel assertions | `phase17_v7/gateC8BR/20260825_release_portability_preflight/02_PANEL_DATA_ASSERTIONS.json` |
| Supplementary-panel assertions | `phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/03_SUPPLEMENTARY_PANEL_DATA_ASSERTIONS.json` |
| Correlation-aware sensitivity | `phase17_v7/gateC8R/20260820_pre_submission_repair/03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv` |
| Full statistical archive | `Additional_file_4_Full_Statistical_Results_GateC8S.zip` |
| Active manuscript source | `01_manuscript/manuscript_v14_genome_medicine_release_preflight_2026-08-25.md` |
| Public repository | `https://github.com/1209433622cz-maker/sle-bcell-remodeling` |
| Immutable release | Open-source licence and archive DOI remain author actions before portal submission |

## Supplementary Table S7 | Statistical tests and multiplicity families

| Result family | Biological unit | Test or estimator | Sidedness | Multiplicity | Role |
|---|---|---|---|---|---|
| B_ASC composition | Sample-cohort stratum | Beta-binomial Wald | Two-sided | BH across three frozen base contrasts | Primary composition inference |
| Gene-level expression | Donor/sample pseudobulk | edgeR robust quasi-likelihood F | Two-sided | BH within tested genes per contrast | Gene-level inference |
| Four frozen programs | Donor/sample pseudobulk | OLS with HC3 | Two-sided | BH across four programs per analysis | Program inference |
| TF-target activity | Ranked gene statistics | Signed-target slope t test | Two-sided | Global BH across 24 tests | Confirmatory regulatory evidence |
| STAT1/STAT2 sensitivity | Ranked gene statistics | CAMERA and FRY | Positive-direction | Separate BH families of six per method | Correlation-aware sensitivity |
| M5911 | Ranked gene statistics | 10,000-permutation preranked test | Positive-direction | Descriptive BH across three contrasts | Orthogonal support |
| GSE23307 | Paired donor | Mean paired log2(x+1) effect | Not tested | None; n=2 | Descriptive perturbation |

## Supplementary Table S8 | Full statistical-results archive map

| Directory | Contents | Files |
|---|---|---:|
| gene_level_results | Complete filterByExpr gene results for GSE174188 and GSE135779 branches | 12 |
| sanitized_design_matrices | Direct-identifier-free analysis designs | 12 |
| composition | Frozen coefficients, contrasts, predictions, sensitivities, leave-one-out and diagnostics | 8 |
| transcription | Program, ranked-list, influence and concordance results | 18 |
| regulatory_and_orthogonal | ULM, target influence, CAMERA/FRY, M5911 and GSE23307 summaries | 9 |
| statistical_framework | Machine-readable test and multiplicity map | 1 |

## Supplementary Figure S1 | Source integrity and hard-quality-control diagnostics

**a,** Hard-QC failure fractions by processing cohort and disease group. **b,** Residual-risk call fraction versus cells per library, coloured by the library median score. **c,** Percent and exact number of retained risk-negative cells and sensitivity-only residual-risk calls among 150,402 hard-QC B-lineage cells. **d,** Median, 95th-percentile and threshold residual-risk scores for all 88 libraries.

[[SUPPLEMENTARY_FIGURE:S1]]

## Supplementary Figure S2 | Representation and bridge diagnostics

**a,** Same-group neighbourhood concentration before and after Harmony adjustment. **b,** Cross-cohort bridge-pair cosine-distance distributions. **c,** Disease-blind branch concordance across Leiden resolutions for residual-risk-negative and strong-ISG-excluded branches; the vertical guide marks the primary resolution. **d,** Biological marker-module localization across the five fine clusters considered before stability adjudication.

[[SUPPLEMENTARY_FIGURE:S2]]

## Supplementary Figure S3 | Disease-blind identity adjudication

**a,** Median and worst-case mapped ARI for five-, four-, three- and two-level policies across resamples. **b,** Median and minimum cluster Jaccard values show localization of failure to fine-state membership. **c,** Mean transition matrix from original resolution-0.4 clusters to mapped reference clusters. **d,** Minimum-to-median Jaccard intervals for the final B_CONV and B_ASC states across 20 disease-blind resamples.

[[SUPPLEMENTARY_FIGURE:S3]]

## Supplementary Figure S4 | Composition-model diagnostics

**a,** Total and zero-ASC sample-cohort strata in the three base contrasts. **b,** Primary B_ASC odds ratios under support, explicit non-B and residual-risk policies using observed-information and HC1 covariance. **c,** Firth-logistic ASC-presence sensitivity. **d,** Positive-only abundance sensitivity using HC3 uncertainty. The two-part models are sensitivity analyses and do not replace the frozen beta-binomial primary model.

[[SUPPLEMENTARY_FIGURE:S4]]

## Supplementary Figure S5 | Pseudobulk and ranked-list diagnostics

**a,** Numbers of filterByExpr-tested and BH-significant genes across seven GSE174188 branches. **b,** Common and median tagwise edgeR dispersions. **c,** Mitochondrial, ribosomal, haemoglobin and immunoglobulin fractions among increasingly long primary ranked lists. **d,** IFN/ISG effects and 95% confidence intervals across frozen branches.

[[SUPPLEMENTARY_FIGURE:S5]]

## Supplementary Figure S6 | Independent-validation diagnostics

**a,** Control and SLE donor counts across the five GSE135779 models. **b,** Four-program childhood estimates. **c,** Childhood IFN/ISG estimates after omission of each source B-cell label. **d,** Full childhood program effects and ranges across donor-deletion analyses.

[[SUPPLEMENTARY_FIGURE:S6]]

## Supplementary Figure S7 | Correlation-aware regulator sensitivity

**a,** CAMERA and FRY six-test BH concordance for STAT1 and STAT2. Dashed guides indicate q=0.05. **b,** CAMERA residual-estimated inter-gene correlations. **c,** Exact CAMERA and FRY BH q values. **d,** Matched signed-target counts, which equal the frozen ULM family (STAT1: 98, 129 and 161; STAT2: 14, 19 and 20).

[[SUPPLEMENTARY_FIGURE:S7]]

## Supplementary note on superseded artifacts

Earlier manuscripts and packages remain for provenance but are not active submission sources. Gate C8R repaired the Figure 2a group mapping and added correlation-aware sensitivity. Gate C8S corrected the machine-readable Figure 5 source-data panel assignment; Gate C8B refines the Figure 5c specificity-comparator wording and adds current literature context: M5911 rows are panel d and GSE23307 donor rows are panel e. No plotted value or upstream estimate changed. Previous fine hard-subtype and untransformed GSE23307 artifacts remain superseded and excluded from active claims.
