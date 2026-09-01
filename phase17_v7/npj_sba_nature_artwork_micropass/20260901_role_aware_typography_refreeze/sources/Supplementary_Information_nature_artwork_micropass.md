# Supplementary information

## Disease-blind reconstruction distinguishes reproducible interferon remodeling from less stable B-cell state assignments in systemic lupus erythematosus

**Authors:** Zhi Chen and Teng Qi

## Supplementary overview

This single Supplementary Information file contains Tables S1-S9 and Figures S1-S10 supporting the main Article. All analytical methods required to interpret the work are reported in the main manuscript. Machine-readable figure source data, regulator sensitivity results and complete statistical outputs are supplied separately as Supplementary Data 1-3. Original external-mapping sensitivity outcomes are superseded, and no corrected disease effect was estimated after calibration failed.

## Supplementary Table S1 | Dataset roles and inferential units

| Resource | Role | Biological unit | Active scope |
|---|---|---|---|
| GSE174188 | Discovery and internal replication | Sample-cohort stratum; donor sensitivities | Disease-blind B_CONV/B_ASC analysis scaffold, composition and B_CONV transcription |
| GSE135779 | Independent SLE replication | Donor | Broad conventional-B analogue; childhood primary |
| CollecTRI/OmniPath | Curated regulator prior | Ranked genes within contrast | Prespecified eight-regulator, three-contrast family |
| MSigDB M5911 | Orthogonal response prior | Ranked genes within contrast | Hallmark interferon-alpha response enrichment |
| GSE23307 | Orthogonal perturbation support | Paired profile within donor | Descriptive IFN-beta response, n=2 donors |

## Supplementary Table S2 | Claim boundaries

| Supported | Not supported |
|---|---|
| Disease-blind B_CONV/B_ASC analysis scaffold with quantified boundary sensitivity | Universally reproducible B_CONV/B_ASC taxonomy or stable hard naive, memory or atypical subtypes |
| Primary B_ASC contrast lacks statistical support | General B_ASC expansion in SLE |
| Replicated IFN/ISG remodeling within B_CONV | Genome-wide shared disease transcriptome |
| ULM STAT1/STAT2 activity concordant across three contrasts | Causal TF activation or direct binding |
| IFN-centred response evidence | A unique initiating IFN ligand in SLE |

## Supplementary Table S3 | Quantitative anchors and prespecified boundaries

| Analysis | Result |
|---|---|
| Frozen-representation identity policy | minimum mapped ARI 0.990; minimum agreement 0.9998; minimum state-median Jaccard 0.991 |
| End-to-end identity sensitivity | prespecified criterion not met; minimum mapped ARI 0.930; minimum agreement 0.9988; B_ASC median Jaccard 0.930 below 0.95 criterion |
| Boundary propagation | primary B_ASC odds-ratio range 0.896-0.967, all intervals include one; primary B_CONV IFN/ISG range 0.836-0.845, all intervals above zero |
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

## Supplementary Table S4B | IFN-overlap-depletion summary

| Depletion | Method | Positive direction | Dedicated q<0.05 | Main qualification |
|---|---|---:|---:|---|
| Frozen 12-gene IFN/ISG arm | ULM | 6/6 | 6/6 | Minimum slope retention 53.5%; all 95% confidence intervals above zero |
| Frozen 12-gene IFN/ISG arm | CAMERA | 6/6 | 5/6 | Discovery STAT2 q=0.326 |
| Frozen 12-gene IFN/ISG arm | FRY | 6/6 | 6/6 | Direction and corrected support retained |
| M5911 | ULM | 6/6 | 5/6 | Discovery STAT2 retained 8/14 targets; slope 0.391, 95% CI -0.745 to 1.526; q=0.500 |
| M5911 | CAMERA | 6/6 | 2/6 | Broad attenuation across contrasts; discovery STAT2 q=0.623 |
| M5911 | FRY | 6/6 | 5/6 | Discovery STAT2 q=0.099 |

All 11 depleted ULM models retaining at least ten targets preserved direction in every leave-one-target analysis. These sensitivities support robustness beyond the narrow 12-gene arm but not independence from the broader interferon-response transcriptome.

## Supplementary Table S5 | Selected figure source-data map

| Figure | Evidence basis | Machine-readable source |
|---|---|---|
| Figure 1 | Disease-blind identity stability and two-compartment adjudication | Figure1_source_data.csv |
| Figure 2 | Sample-level composition and asserted 43/47 primary groups | Figure2_source_data.csv |
| Figure 3 | Raw-count pseudobulk transcription with explicit tested-gene symbols | Figure3_source_data.csv |
| Figure 4 | Source-label-defined GSE135779 replication and influence analyses | Figure4_source_data.csv |
| Figure 5 | Regulatory and orthogonal response evidence | Figure5_source_data.csv |
| Supplementary Figure S8 | STAT1/STAT2 IFN-overlap-depletion sensitivity | Supplementary_Figure_S8_source_data.csv |
| Supplementary Figure S9 | End-to-end identity boundary and downstream propagation | Supplementary_Figure_S9_source_data.csv |
| Supplementary Figure S10 | Corrected reference calibration and unresolved external transfer | Supplementary_Figure_S10_source_data.csv |

## Supplementary Table S6 | Reproducibility record

| Component | Reader-accessible record |
|---|---|
| Main and supplementary figure data | Supplementary Data 1 with SHA-256 manifest |
| Complete statistical results | Supplementary Data 3 with 12 gene-level branches and 12 sanitized design matrices |
| Correlation-aware sensitivity | Supplementary Data 2 |
| End-to-end identity and boundary propagation | Supplementary Data 3, `identity_robustness/` |
| Analysis code and decisions | `https://github.com/1209433622cz-maker/sle-bcell-remodeling` |
| Environment reconstruction | Pinned scientific and release environments documented in `REPRODUCIBILITY.md` |
| Version-specific archive | Zenodo https://doi.org/10.5281/zenodo.22151739; version-specific archive of the released analysis code, Source Data and statistical outputs |

## Supplementary Table S7 | Statistical tests and multiplicity families

| Result family | Biological unit | Test or estimator | Sidedness | Multiplicity | Role |
|---|---|---|---|---|---|
| B_ASC composition | Sample-cohort stratum | Beta-binomial Wald | Two-sided | BH across three frozen base contrasts | Primary composition inference |
| Gene-level expression | Sample-cohort pseudobulk (GSE174188); donor pseudobulk (GSE135779) | edgeR robust quasi-likelihood F | Two-sided | BH within tested genes per contrast | Gene-level inference |
| Four frozen programs | Sample-cohort pseudobulk (GSE174188); donor pseudobulk (GSE135779) | OLS with HC3 | Two-sided | BH across four programs per analysis | Program inference |
| TF-target activity | Ranked gene statistics | Signed-target slope t test | Two-sided | Global BH across 24 tests | Confirmatory regulatory evidence |
| STAT1/STAT2 sensitivity | Ranked gene statistics | CAMERA and FRY | Positive-direction | Separate BH families of six per method | Correlation-aware sensitivity |
| STAT1/STAT2 overlap depletion | Ranked gene statistics and pseudobulk counts | ULM, CAMERA and FRY | Two-sided ULM; positive-direction CAMERA/FRY | Separate BH family of six per branch and method | Post-freeze sensitivity |
| End-to-end identity reproducibility | Cell resample within technical library | ARI, AMI, mapping agreement, state Jaccard and recall | Not tested | Five unchanged threshold criteria | Disease-blind robustness boundary |
| Broad-state boundary propagation | Sample-cohort stratum | Frozen beta-binomial and TMM logCPM/HC3 models | Two-sided intervals | No new multiplicity family; same-data sensitivity | Assignment-uncertainty sensitivity |
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
| identity_robustness | Aggregate and replicate-level end-to-end identity metrics, boundary propagation results and integrity records | 101 |
| external_mapping_calibration | Corrected feature and parameter tables, full confidence-calibration family, aggregate selection diagnostics, provenance, arithmetic recount and publication boundary | 20 |

## Supplementary Table S9 | Reference-calibrated external mapping boundary

| Component | Corrected diagnostic | Interpretation |
|---|---|---|
| External input | 56 matrices; 363,083 cells | Complete source matrix coverage |
| External QC and selection | 353,527 QC-passing cells; 36,630 B-lineage candidates | No source labels or disease fields parsed |
| Reference training | 13,000 B_CONV and 1,300 B_ASC; 258 donors; 601 features | Both algorithms share reference and features |
| Normalization | Full-library log1p(CP10K) before feature subsetting in both datasets | Corrects reference feature-only denominator |
| Elastic-net calibration | Diagnostic threshold 0.95; coverage 0.941958; B_CONV precision 0.996450; B_ASC precision 0.885210 | No eligible candidate: state precision must be at least 0.90 and coverage at least 0.80 |
| Centroid calibration | Margin 0.117767; coverage 0.95; B_CONV precision 0.992374; B_ASC precision 1.0 | Eligible, but cannot replace required primary mapper |
| Mean reference-fold balanced accuracy | Elastic net 0.960569; centroid 0.950293 | Calibration diagnostics; not independent performance estimates |
| Outcome policy | Corrected disease outcomes not estimated | No corrected effect, confidence interval, P or q value exists |
| Prior outcome exposure | Original sensitivity outcomes were known before correction | Post-outcome correction; not prospective validation |
| Evidence boundary | Primary GSE135779 replication remains source-label-defined | Superseded uncorrected outcomes excluded from supporting evidence |

Full candidate calibration, donor-grouped cross-validation, reference normalization
audit and corrected input/prediction hashes are retained with the analysis code.
The original source-label-defined pseudobulk effect is a standardized HC3 model
estimate; the unexecuted sensitivity would instead compare donor mean cell-level
log1p(CP10K) scores. They are different estimands and must not be compared as effect
attenuation. No new multiplicity family was evaluated after corrected calibration failed.

## Supplementary Figure S1 | Source integrity and hard-quality-control diagnostics

**a,** Hard-QC failure fractions by processing cohort and disease group. **b,** Residual-risk call fraction versus cells per library, coloured by the library median score. **c,** Percent and exact number of retained risk-negative cells and sensitivity-only residual-risk calls among 150,402 hard-QC B-lineage cells. **d,** Median, 95th-percentile and threshold residual-risk scores for all 88 libraries.

[[SUPPLEMENTARY_FIGURE:S1]]

## Supplementary Figure S2 | Representation and bridge diagnostics

**a,** Same-group neighbourhood concentration before and after Harmony adjustment. **b,** Cross-cohort bridge-pair cosine-distance distributions. **c,** Disease-blind branch concordance across Leiden resolutions for residual-risk-negative and strong-ISG-excluded branches; the vertical guide marks the primary resolution. **d,** Biological marker-module localization across the five fine clusters considered before stability adjudication.

[[SUPPLEMENTARY_FIGURE:S2]]

## Supplementary Figure S3 | Fine-state failure and transition structure

**a,** Median and minimum cluster Jaccard values localize instability to fine-state membership across the five-, four- and three-state policies considered before broad adjudication. **b,** Mean transition matrix from original resolution-0.4 clusters to mapped reference clusters across frozen-representation resamples. These diagnostics explain the transition to the broad B_CONV/B_ASC analysis scaffold; broad-state pass criteria are shown in Fig. 1 and end-to-end reconstruction is shown in Supplementary Fig. S9. Highly variable genes, principal components and Harmony coordinates were not recomputed in this figure.

[[SUPPLEMENTARY_FIGURE:S3]]

## Supplementary Figure S4 | Composition-model diagnostics

**a,** Total and zero-ASC sample-cohort strata in the three base contrasts. **b,** Primary B_ASC odds ratios under support, explicit non-B and residual-risk policies using observed-information and HC1 covariance. **c,** Firth-logistic ASC-presence sensitivity. **d,** Positive-only abundance sensitivity using HC3 uncertainty. Panels c-d use logarithmic ratio axes with the null fixed at one; the two-part models are sensitivity analyses and do not replace the frozen beta-binomial primary model.

[[SUPPLEMENTARY_FIGURE:S4]]

## Supplementary Figure S5 | Pseudobulk and ranked-list diagnostics

**a,** Numbers of filterByExpr-tested and BH-significant genes across seven GSE174188 branches. **b,** Common and median tagwise edgeR dispersions. **c,** Mitochondrial, ribosomal, haemoglobin and immunoglobulin fractions among increasingly long primary ranked lists. IFN/ISG estimates across the frozen GSE174188 branches are owned by Fig. 3b and are not repeated here.

[[SUPPLEMENTARY_FIGURE:S5]]

## Supplementary Figure S6 | GSE135779 replication and robustness diagnostics

**a,** Control and SLE donor counts across the five GSE135779 models. **b,** Four-program childhood estimates. **c,** Childhood IFN/ISG estimates after omission of each source B-cell label. **d,** Full childhood program effects and ranges across donor-deletion analyses.

[[SUPPLEMENTARY_FIGURE:S6]]

## Supplementary Figure S7 | Correlation-aware regulator sensitivity

**a,** CAMERA and FRY six-test BH concordance for STAT1 and STAT2. Dashed guides indicate q=0.05. **b,** CAMERA residual-estimated inter-gene correlations. **c,** Exact CAMERA and FRY BH q values. **d,** Matched signed-target counts, which equal the frozen ULM family (STAT1: 98, 129 and 161; STAT2: 14, 19 and 20).

[[SUPPLEMENTARY_FIGURE:S7]]

## Supplementary Figure S8 | STAT1/STAT2 IFN-overlap-depletion sensitivity

**a,** ULM slopes and 95% confidence intervals after removal of the frozen 12-gene IFN/ISG positive arm. **b,** Corresponding estimates after removal of all 97 M5911 genes; discovery STAT2 retains eight targets and its interval crosses zero. Labels report remaining matched targets. **c,** Exact branch- and method-specific Benjamini-Hochberg q values across the six regulator-by-contrast tests. **d,** Percentage of frozen matched targets retained after each depletion. All method-level directions remain positive, but M5911 depletion produces substantial attenuation and does not support an overlap-independent interpretation.

[[SUPPLEMENTARY_FIGURE:S8]]

## Supplementary Figure S9 | End-to-end reconstruction exposes a B_ASC-specific boundary without changing the disease conclusions

**a,** Observed values and prespecified criteria for five end-to-end two-compartment checks; four met their criteria and minimum state-median Jaccard did not. **b,** State Jaccard across 20 complete reconstruction replicates localizes the unmet overlap criterion to B_ASC, while B_CONV remains above 0.95. **c,** Counts of sampled cells exchanged across the B_CONV/B_ASC boundary. **d,** Primary B_ASC composition odds ratios and 95% confidence intervals after each observed boundary exchange; the dashed guide marks one and the orange line marks the frozen estimate. **e,** Primary and donor-nonoverlap B_CONV IFN/ISG effects after boundary-cell raw counts were propagated through frozen TMM logCPM and HC3 models; dotted lines mark the frozen effects. All propagation analyses reuse GSE174188 and quantify assignment sensitivity rather than independent replication.

[[SUPPLEMENTARY_FIGURE:S9]]

## Supplementary Figure S10 | Reference calibration limits source-label-independent external transfer

**a,** Median and interquartile range of full-library divided by selected-feature
counts among 13,000 B_CONV and 1,300 B_ASC reference training cells. This ratio
quantifies the legacy pre-log scaling discrepancy; corrected mapping uses
full-library denominators in both datasets. **b,** Per-state precision at the
diagnostic elastic-net and eligible centroid thresholds. Mapper colour is held
constant across panels b-d, marker shape distinguishes B_CONV from B_ASC, and the
dashed line is the unchanged 0.90 state-precision criterion. **c,** Reference-cell
coverage at those thresholds; the dashed line is the unchanged 0.80 criterion.
**d,** Balanced accuracy in each of five donor-grouped reference calibration
folds; black horizontal bars show fold means. No eligibility guide is drawn
because balanced accuracy is diagnostic only. These folds select model and
threshold parameters, not independent performance estimates. The elastic-net
B_ASC precision failure prevents outcome access; centroid success is not a
replacement analysis. No corrected external disease result is shown.

[[SUPPLEMENTARY_FIGURE:S10]]
