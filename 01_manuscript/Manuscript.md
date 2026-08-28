# Disease-blind single-cell reconstruction separates unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus

**Article type:** Research

**Authors:** Zhi Chen [1] and Teng Qi [1,*]

**Affiliation 1:** School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen 518172, China

**Corresponding author:** Teng Qi, School of Medicine, The Chinese University of Hong Kong, Shenzhen, MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China; tengqi@link.cuhk.edu.cn

**ORCID identifiers:** Zhi Chen, https://orcid.org/0009-0001-0072-5576; Teng Qi, https://orcid.org/0009-0007-7648-4776

**Author emails:** Zhi Chen, zhichen1@link.cuhk.edu.cn; Teng Qi, tengqi@link.cuhk.edu.cn

**Running title:** Replicated IFN remodeling in SLE B cells

## Abstract

**Background:** SLE alters both the abundance and transcriptional state of peripheral B cells, but these layers can be conflated by outcome-informed annotation, cell-level inference and technically imbalanced cohorts.

**Methods:** We reanalysed single-cell RNA-sequencing data with donor- and cohort-resolved inference. Disease-blind B-lineage reconstruction in GSE174188 preceded sample-level composition and compartment pseudobulk testing. Frozen-representation policy selection was followed by 20 end-to-end replicates that recomputed highly variable genes, principal components, Harmony, neighbour graphs and Leiden clusters. Observed boundary exchanges were propagated through frozen composition and IFN/ISG models. The IFN/ISG program was evaluated in independent GSE135779, followed by prespecified regulator, response-set and perturbational analyses.

**Results:** Among 150,402 GSE174188 B-lineage cells, frozen-representation resampling supported broad conventional-B (B_CONV) and antibody-secreting-cell (B_ASC) compartments but not stable naive/memory assignments. End-to-end resampling retained global concordance but missed the prespecified B_ASC state-overlap criterion (median Jaccard 0.930 versus 0.95), so the partition was retained only as an analysis scaffold. Boundary propagation preserved the primary B_ASC composition null (odds-ratio range 0.896-0.967; all intervals included one) and both GSE174188 B_CONV IFN/ISG effects. The frozen primary B_ASC estimate was 0.947 (95% confidence interval 0.636-1.410; P=0.787). Within B_CONV, the IFN/ISG program increased in the primary contrast (effect 0.837; q=2.98 x 10^-6), a donor-nonoverlap internal contrast (effect 1.086; q=3.61 x 10^-4) and independent GSE135779 childhood donors (11 controls and 32 SLE; effect 1.042; q=2.98 x 10^-6). All ten IFN genes were positive despite low genome-wide agreement (Spearman rho=0.026). STAT1 and STAT2 activities were positive and globally significant in all three ULM contrasts. CAMERA retained positive direction in all six core tests and BH significance in five; FRY retained both in all six. Broader M5911 depletion attenuated discovery STAT2, preventing an overlap-independent regulatory claim.

**Conclusions:** SLE shows independently replicated IFN remodeling within a disease-blind conventional-B analysis scaffold, with convergent but observational regulatory evidence. The results do not establish a universally reproducible taxonomy, discrete subtype, causal regulator or unique upstream stimulus.

## Keywords

systemic lupus erythematosus; B cells; single-cell RNA sequencing; pseudobulk; interferon; independent validation; transcription-factor activity; reproducibility

## Background

Systemic lupus erythematosus (SLE) is a heterogeneous autoimmune disease involving loss of B-cell tolerance, autoantibody production and sustained innate immune activation. Peripheral-blood single-cell studies have described changes in naive, memory, double-negative, CD11c-positive and antibody-secreting B-cell populations together with prominent interferon responses [1,2,22,24]. Tissue single-cell data and B-cell-focused experiments further connect interferon-responsive states with local inflammation, B-cell activation and plasma-cell differentiation [21,25,30].

Neither an interferon signature nor plasmablast biology is novel in SLE. Longitudinal paediatric immunomonitoring linked a plasmablast signature to disease activity [20], modular adult studies resolved heterogeneous interferon activation thresholds [23], and a recent deep-phenotyping study found that a high plasmablast-to-memory ratio marked a subgroup enriched for higher activity and Sm/RNP autoantibodies [19]. Large transcriptomic analyses likewise identify multiple molecular endotypes that are not uniformly represented across datasets [18]. These findings make cohort structure and disease context central to interpretation: a null primary composition estimate in the source-defined `managed` SLE category need not contradict plasmablast expansion in clinically enriched subgroups. Recent single-cell profiling of 16 women with SLE in low disease activity on antimalarial treatment further showed that interferon activity varied with polygenic-risk burden across several immune compartments [31]. That study reinforces the need to separate persistent interferon-responsive state from disease activity and treatment context, but it did not test our disease-blind B_CONV program and is therefore contextual rather than replication evidence.

Single-cell disease studies are particularly vulnerable to pseudoreplication when cells, rather than donors or biological samples, are treated as independent units [3,4]. Composition introduces an additional constraint because an increase in one compartment changes the observed fractions of all others [5]. Public SLE resources also distribute samples across processing cohorts, include repeated donors and provide uneven disease-group support within technical strata. Outcome-informed cluster labels or pooled cell-level tests can therefore combine biology with design structure.

We addressed these problems through a staged secondary analysis. Raw-count integrity, metadata hierarchy and disease-by-cohort support were audited first. B-lineage identity was reconstructed while protected disease fields remained separate. Only after a disease-blind identity model was frozen were sample-level composition and within-compartment transcription tested. The primary expression result was then carried into independent GSE135779 under a prespecified mapping and analysis plan finalized before disease-effect estimation.

The intended advance is therefore not rediscovery of interferon activity in SLE. We ask which biological layer remains defensible after disease-blind state definition, sample- or donor-level inference, donor-nonoverlap internal testing, independent-cohort validation and external regulatory and perturbational checks. This design distinguishes a reproducible within-compartment process from unstable subtype labels, cohort-specific abundance effects and causal claims that the available observational data cannot support.

## Methods

### Study design and data resources

The study was a secondary analysis of public human transcriptomic data. GSE174188 [1,14] was used for disease-blind B-lineage reconstruction, sample-level composition, within-compartment transcriptional analysis and internal validation. GSE135779 [2,15] was the independent SLE validation dataset. CollecTRI and MSigDB supplied independently curated regulatory and response priors, and GSE23307 [13,16] supplied paired IFN-beta perturbation profiles from healthy-donor primary B cells. Resources not contributing to the central replication claim were excluded from the active manuscript.

### Source integrity, metadata hierarchy and hard quality control

Source paths, SHA-256 hashes, matrix dimensions and matrix encodings were frozen before analysis. Metadata keys were audited at donor, biological-sample, technical library and processing-cohort levels. Hard-quality-control thresholds were at least 500 total counts, at least 200 detected genes, no more than 10% mitochondrial counts, no more than 1% haemoglobin counts, no more than 0.5% platelet-marker counts and detection of at least one B-lineage marker. Each excluded cell retained a reason-level record. Protected disease fields were stored separately during reconstruction.

### Disease-blind representation, identity adjudication and end-to-end sensitivity

Residual doublet risk was evaluated per complete library. Raw counts were retained for pseudobulk, whereas normalized log expression was used for recurrent highly variable gene selection, principal components and neighbour graphs. Unintegrated Scanpy [6] and Harmony-adjusted [7] representations were compared using technical mixing, biological marker conservation, bridge samples and coverage across donors, samples and libraries. Initial policy selection used 20 within-library 80% cell resamples of the frozen 50-dimensional Harmony representation. Failure of the fine-grained solution was retained. Transition reconstruction supported a two-compartment B_CONV/B_ASC analysis partition after marker and frozen-representation stability checks while disease remained blinded.

An end-to-end disease-blind sensitivity then repeated within-library 80% resampling 20 times from the raw matrix. Each replicate independently filtered genes, selected 3,000 recurrent highly variable genes from a 7,000-gene candidate pool, recalculated 50 principal components, reran Harmony, reconstructed 15-nearest-neighbour graphs and reran Leiden [8] at resolutions 0.4, 0.6 and 0.8. Replicate clusters were mapped to the frozen reference by maximum cell overlap. The unchanged broad-state criteria were median and minimum mapped adjusted Rand indices of at least 0.95 and 0.90, median and minimum mapping agreement of at least 0.995 and 0.990, and minimum state-median Jaccard of at least 0.95.

For uncertainty propagation, only sampled cells observed to exchange B_CONV/B_ASC assignment in each replicate were changed in the full frozen partition; unsampled cells retained their frozen assignment. No sample, gene, threshold or model was reselected. The beta-binomial composition models were refitted with frozen eligibility and designs. Boundary-cell raw counts were added to or subtracted from frozen B_CONV pseudobulks before TMM log-counts-per-million normalization, frozen 12-gene IFN/ISG scoring and HC3 inference. These analyses were same-data sensitivities, not independent validation.

### Sample-level composition

Cells were aggregated by biological sample and processing cohort. The experimental unit was the sample-cohort stratum, with donor-aware sensitivity analyses for repeated samples. Models were restricted to prespecified processing cohorts with case-control common support and to strata with at least 50 frozen B cells. The primary comparison was processing cohort 4 source-metadata `managed` SLE versus `normal`, adjusted for age and ethnicity. Internal processing-cohort-2 and secondary processing-cohort-3 analyses of the source-metadata `flare` category were estimated separately. Bridge strata were not used to manufacture a pooled disease coefficient. Model, sandwich, threshold, one-sample-per-donor and leave-one-out diagnostics were retained.

### Raw-count pseudobulk and gene-level inference

Raw counts were summed by sample-cohort stratum within `B_CONV`, combining technical library contributions only after cell-ID and count conservation checks. Strata with at least 50 cells were primary; 20- and 100-cell thresholds and a residual-doublet-risk-negative cell branch were prespecified sensitivities. Genes were filtered with edgeR [9] `filterByExpr`, libraries were TMM-normalized, and robust quasi-likelihood models were fitted with the frozen contrast-specific covariates. Benjamini-Hochberg adjustment was applied over tested genes within each contrast. Full feature tables retained untested genes with explicit flags.

### Frozen program inference

Program membership and direction were frozen before disease effects. Duplicate gene symbols were summed before TMM log-counts-per-million normalization. Within each contrast, genes were standardized across pseudobulks and program scores were computed as the mean positive-arm score minus the mean negative-arm score. Disease effects and 95% confidence intervals used linear models with HC3 sandwich uncertainty. The confirmatory family comprised naive-to-memory, atypical/low-naive, APC/HLA and IFN/ISG programs; Benjamini-Hochberg correction was applied across these four tests. Ranked competitive enrichment and gene-direction coherence were secondary support.

### Independent GSE135779 validation

GSE135779 source files, metadata versions, donor availability, source-label support and frozen program-gene availability were audited without inspecting disease effects. The external identity scope was a broad conventional-B analog formed from eight source B-cell labels. Childhood, adult and combined model matrices and minimum-cell sensitivities were frozen before model fitting. Real matrices were imported for dimension and count-conservation qualification only; synthetic null and signal data qualified the statistical engine before disease effects were estimated. Gene and program methods then matched the GSE174188 framework where the different gene universe allowed.

### Reference-calibrated external mapping sensitivity

We additionally assessed whether external B-lineage selection could avoid the source-provided cell labels. Sample-wise quality control and Leiden clustering of all GSE135779 matrices preceded selection using frozen B-lineage and exclusion-marker modules. Two algorithmically distinct broad-state mappers, elastic-net logistic regression and Pearson nearest-centroid mapping, shared the GSE174188 reference and common features. Reference donor-grouped cross-validation selected regularization and confidence thresholds. Eligibility required at least 80% reference-cell coverage and at least 90% precision for each state; high overall accuracy alone was insufficient. The training subset contained 13,000 B_CONV and 1,300 B_ASC cells from 258 donors. These folds calibrated mapping and were not independent validation of the complete feature-selection and tuning pipeline.

A post-unblinding audit identified incompatible normalization denominators: selected-feature totals in the reference versus full-library totals externally. We corrected the reference to full-library log1p(CP10K) before feature subsetting and reran all matrices without changing selection rules, candidate grids or eligibility thresholds. Diagnostic fallback thresholds were prohibited from authorizing outcome access. Inputs, code, predictions and protected-metadata identity were checked by hashes. Original sensitivity outcomes had already been seen; this was a technical correction, not a new prospective preregistration. Failed calibration precluded corrected disease-effect estimation, and the original sensitivity was excluded from supporting evidence.

### Influence, specificity and cross-dataset analyses

The childhood IFN/ISG model was repeated after deleting each donor. Source-label dependence was assessed by omitting each of the eight contributing labels without reselecting donors. Platelet/ambient, ASC/UPR and pan-B families were prespecified as controls. Cross-dataset gene analysis was restricted to genes passing the respective filters in both primary datasets; the shared IFN subset was reported separately from the genome-wide rank correlation.

### Prespecified TF-target activity

Human CollecTRI interactions [10,11] were retrieved from OmniPath on 15 August 2026 and frozen by raw SHA-256 `98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1`. Only exact individual-TF source symbols were used. Consensus stimulation and inhibition were encoded as +1 and -1, respectively; ambiguous target directions were excluded, and duplicate same-sign edges were collapsed. The confirmatory family comprised STAT1, STAT2, IRF7, IRF9, E2F1, FOXM1, MYC and MYBL2 in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts.

For every tested Ensembl feature, the ranked statistic was `sign(logFC) * sqrt(F)` from the frozen robust edgeR quasi-likelihood result. Features were mapped to uppercase symbols, and statistics were averaged when multiple tested Ensembl features mapped to one symbol. For each regulator and contrast, a univariate linear model with an intercept regressed the gene-level statistic on the signed target weight. The slope, standard error, two-sided P value and 95% confidence interval were reproduced independently by direct matrix algebra. Benjamini-Hochberg correction was applied once across all 24 confirmatory tests. For each core regulator and contrast, influence analysis deleted each matched target in turn, and 100 deterministic analyses resampled 80% of matched targets.

### Correlation-aware STAT1/STAT2 sensitivity

Because genes within a regulon are correlated, the primary rank-based ULM results were supplemented by a correlation-aware sensitivity analysis that did not alter the frozen regulators, signed CollecTRI targets, contrasts, model matrices or `filterByExpr` backgrounds. Pseudobulk counts were collapsed to gene symbols and transformed with voom precision weights [28,29]. Expression rows for inhibitory targets were sign-reversed so that positive set direction retained the frozen signed-regulon interpretation. For STAT1 and STAT2 in each of the three confirmatory contrasts, CAMERA estimated inter-gene correlation from model residuals and performed a competitive rank test [26], while FRY supplied a rotation-based directional test [27]. Benjamini-Hochberg adjustment was applied separately across the six core regulator-contrast tests for each method. Target counts were required to match the frozen ULM analysis exactly; no target, regulator, contrast or background was reselected after inspecting the sensitivity results.

### STAT1/STAT2 IFN-overlap-depletion sensitivity

A post-freeze sensitivity tested whether the STAT1/STAT2 results were reducible to genes shared with interferon-response programs. Branch A removed the 12 frozen positive-arm IFN/ISG genes from the signed regulon targets; branch B removed all 97 members of MSigDB M5911. The same ranked statistics, tested-gene backgrounds, CollecTRI signs, contrasts and model matrices were retained without target re-selection. ULM, CAMERA and FRY were rerun in each branch. ULM leave-one-target analysis was performed only when at least ten targets remained. BH adjustment was applied separately within each depletion branch and method across the six core regulator-by-contrast tests. Interpretation jointly considered direction, ULM attenuation and confidence intervals, target retention, corrected q values and cross-method consistency rather than a binary P-value rule.

### Orthogonal interferon-response analyses

MSigDB [12] human release 2026.1.Hs Hallmark set `HALLMARK_INTERFERON_ALPHA_RESPONSE` (systematic identifier M5911; 97 frozen member genes) was tested against each complete ranked contrast. Preranked enrichment used 10,000 deterministic gene-label permutations, with normalized enrichment scores and descriptive three-contrast q values reported outside the 24-test TF family.

GSE23307 [13,16] GPL6104 microarray profiles comprised paired untreated and IFN-beta-exposed primary B cells from two healthy donors. Platform annotation was frozen before effects were calculated. Twenty-one probes mapping to the 12 frozen IFN/ISG positive-arm genes were transformed as log2(x+1), collapsed to one value per gene and sample by the median, and differenced within donor. The donor summary was the mean paired effect across 12 genes. Direction and gene concordance were descriptive; no inferential P value was calculated at n=2. Only log2(x+1)-transformed GSE23307 values contributed to the reported results, figures and claims.

### Statistical analysis and multiplicity

This retrospective secondary analysis used all eligible public biological units after frozen quality-control, support and mapping rules; no prospective sample-size or power calculation was performed. Exact analysis sizes are reported with the corresponding results and figure panels. Unless explicitly identified as directional, hypothesis tests were two-sided and intervals were 95% confidence intervals. The primary B_ASC composition model used a beta-binomial Wald test with Benjamini-Hochberg (BH) correction across the three frozen base contrasts; covariance and two-part models were sensitivity analyses with nominal P values. Gene-level robust edgeR quasi-likelihood tests used BH correction across `filterByExpr`-tested genes within each contrast. Frozen-program linear models used HC3 covariance and BH correction across the four prespecified programs within each analysis. Ranked program-arm CAMERA results were corrected within each frozen analysis.

The CollecTRI activity analysis used two-sided target-slope tests and one global BH family across eight regulators and three confirmatory contrasts (24 tests). The STAT1/STAT2 CAMERA and FRY analyses used positive-direction sensitivity tests with separate BH families of six tests for each method. The two overlap-depletion branches used six additional post-freeze sensitivity families, one per branch and method, each containing the six core regulator-by-contrast tests; these did not replace the original 24-test family. M5911 used a positive-direction weighted preranked test with 10,000 deterministic gene-label permutations per contrast and a descriptive BH correction across three contrasts. The paired GSE23307 experiment had two donors and no inferential P value. Statistical significance was defined as q<0.05 only within the stated confirmatory family; nominal and descriptive results were not promoted to confirmatory evidence. The complete family map, full gene-level tables and sanitized design matrices are provided in Additional file 4.

### Generative AI assistance

OpenAI Codex was used during project development for code drafting, workflow documentation, language editing and generation of quality-control checks. All computations were executed locally against frozen inputs; numerical results were read from machine-generated analysis outputs rather than generated by the language model. The authors remain accountable for reviewing the scripts, outputs, interpretations and revised text before final approval. No AI system is listed as an author.

### Reproducibility and governance

Analyses used timestamped run directories, immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 integrity manifests. Disease effects were calculated only after input, design and statistical engine qualification. Earlier manuscripts and figures were retained for provenance but were not used as numerical sources for this version.

## Results

### End-to-end reconstruction narrows the two-compartment model to an analysis scaffold

The authoritative GSE174188 B-lineage source contained 152,981 cells and 30,172 genes. Frozen hard-quality-control rules retained 150,402 cells. Metadata audits resolved 259 donors, 271 biological samples, 88 technical libraries and four processing cohorts, including repeated donors and samples spanning processing cohorts. Disease-by-cohort common support was not uniform, so discovery of identity could use the full disease-blind cell set whereas disease coefficients were restricted to prespecified supported contrasts.

Complete-library doublet diagnostics, recurrent highly variable gene selection, unintegrated and Harmony representations, bridge-sample checks and marker coverage were reviewed before outcome access. The initial five-state identity solution did not satisfy the prespecified resampling thresholds. This negative result was preserved rather than relabelled as a successful subtype analysis. Transition reconstruction supported a two-level model comprising `B_CONV` and `B_ASC`, with naive-memory structure retained as a continuous program within `B_CONV` and platelet-associated expression retained as a technical overlay.

Within the frozen 50-dimensional Harmony representation, the two-compartment policy passed all five criteria across 20 graph resamples: minimum mapped adjusted Rand index 0.990, minimum mapping agreement 0.9998 and minimum state-median Jaccard 0.991. `B_ASC` marker support was complete for DERL3, JCHAIN, MZB1, TNFRSF17 and XBP1. These results supported use of the broad partition for the frozen analyses but did not test uncertainty introduced by recomputing the representation (Fig. 1).

The end-to-end sensitivity completed all 20 replicates and all 20 Harmony runs converged. Four global criteria passed: median and minimum mapped adjusted Rand indices were 0.963 and 0.930, and median and minimum mapping agreements were 0.99937 and 0.99877. The minimum state-median Jaccard was 0.930, however, below the unchanged 0.95 criterion; the formal result was therefore HOLD. The failure was localized to `B_ASC` (median Jaccard 0.930; minimum 0.872), whereas `B_CONV` remained highly concordant (median 0.99936; minimum 0.99876). A median of 76 among 120,320 sampled cells changed broad-state assignment per replicate (Supplementary Fig. S9).

Propagation of those observed boundary exchanges retained the primary composition null: replicate-specific odds ratios ranged from 0.896 to 0.967 and all 20 confidence intervals included one. The primary B_CONV IFN/ISG effect ranged from 0.836 to 0.845, and the donor-nonoverlap effect ranged from 1.059 to 1.087; all 40 estimates were positive with confidence intervals above zero. Thus, the sensitivity did not overturn the frozen disease results, but it prevented a stronger taxonomy-level claim. B_CONV/B_ASC is consequently described as a disease-blind analysis scaffold rather than a universally reproducible cell taxonomy.

### B_ASC composition is secondary rather than the central disease signal

Protected outcomes were joined only after the two-compartment freeze. Composition was estimated at the sample-cohort level, with a minimum of 50 eligible B cells per stratum and no cell-level disease test. In the primary processing-cohort-4 contrast, the conditional odds ratio for `B_ASC` relative abundance was 0.947 (95% confidence interval 0.636-1.410; P=0.787). Adjusted fractions were 1.61% in controls and 1.52% in managed SLE. The HC1 sandwich audit was concordant (95% confidence interval 0.651-1.376; P=0.774), and all 90 leave-one-sample-out estimates retained the same direction without generating statistical support.

The internal validation estimate was also below one (odds ratio 0.772), as was the explicit donor-nonoverlap estimate (odds ratio 0.591; n=53), but neither converted the null primary result into a central composition claim. A secondary flare contrast was positive (odds ratio 2.303; nominal P=0.0282) but did not survive the frozen three-contrast correction (q=0.0845). Accordingly, abundance results provide context for the transcriptional analysis and a transparent negative boundary, not evidence for a generally expanded `B_ASC` compartment.

### Within-B_CONV transcription identifies a reproducible IFN/ISG program

Raw counts were aggregated into sample-cohort `B_CONV` pseudobulks after technical library contributions from the same stratum were combined. One source-defined managed-SLE composition stratum contained 44 `B_CONV` cells after compartment assignment and therefore did not meet the prespecified 50-cell `B_CONV` threshold for transcriptional analysis. The primary analysis consequently included 89 pseudobulks, comprising 43 reference and 46 SLE strata, and retained 59,873,385 UMI counts. Gene-level inference used TMM normalization, `filterByExpr`, robust edgeR quasi-likelihood models and Benjamini-Hochberg correction within each contrast. A separately frozen four-program family was tested from TMM log-counts-per-million values using positive-minus-negative standardized scores and HC3 uncertainty.

The prespecified IFN/ISG program was higher in SLE in the primary contrast (effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6). The effect was positive at 20- and 100-cell support thresholds, after residual-doublet-risk calls were excluded, and in all 89 leave-one-sample-out fits. Ranked-gene evidence was coherent, with all ten tested genes in the expected arm direction and competitive enrichment at approximately q=2 x 10^-6. Leading genes included USP18, IFI44L, EPSTI1, IFIT3, MX1, IFI6, OAS2, ISG15 and STAT1.

The IFN/ISG program was also higher in the full internal GSE174188 validation contrast (effect 0.856; q=0.00462) and in the prespecified donor-nonoverlap subset (effect 1.086; q=3.61 x 10^-4). These strata belong to the same accession and are therefore described as internal replication, not an independent cohort.

Two other frozen programs provided more limited GSE174188 context. The naive-to-memory axis was lower in the primary SLE contrast (effect -0.541; q=0.0213), and the APC/HLA program was higher (effect 0.268; q=0.0213), but neither had multiplicity-supported internal validation. The atypical/low-naive program was null in the primary contrast (effect -0.057; q=0.748). These axes are not co-equal with IFN/ISG and were not used to redefine the identity compartment.

### Independent GSE135779 analysis replicates IFN remodeling but not a genome-wide state

GSE135779 source matrices and metadata were audited before any disease effect was calculated. The prespecified external mapping allowed only a broad conventional-B analog constructed from source B-cell labels; hard naive-memory identities were not transferred. Matrix import and edgeR behavior were qualified with count-conservation checks and synthetic null and signal data before external disease effects were estimated.

The primary childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 mapped cells per donor. The frozen IFN/ISG program was higher in SLE (effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined childhood-adult analysis included 54 donors (16 controls and 38 SLE) and yielded a similar estimate (effect 0.996, 95% confidence interval 0.655-1.337; q=1.31 x 10^-6). Results remained positive at minimum support thresholds of 20 (effect 0.965; q=6.75 x 10^-7) and 100 cells (effect 0.939; q=4.06 x 10^-6).

The adult-only estimate was positive (effect 0.968) but imprecise (95% confidence interval -0.123 to 2.060; q=0.291) because it contained five controls and six SLE donors. It is therefore directionally compatible rather than confirmatory. Across 43 childhood donor-deletion fits, IFN/ISG effects ranged from 0.987 to 1.094. Omitting each of the eight source B-cell labels in turn retained the same 43 donors and produced effects from 1.019 to 1.051, excluding dependence on a single source label.

Specificity analyses separated the IFN signal from several alternative explanations. In the childhood contrast, the platelet/ambient, ASC/UPR and pan-B control effects were 0.049, 0.221 and -0.232, respectively, compared with 1.042 for IFN/ISG. All 12 available frozen IFN-arm genes were positive, and ranked enrichment had a camera FDR of 1.85 x 10^-7. Ten IFN genes were jointly tested in the primary GSE174188 and childhood GSE135779 analyses, and all ten were positive in both.

This coherence did not extend across the complete tested transcriptome. Among 4,410 shared tested genes, cross-dataset effect correlation was only Spearman rho=0.026. Thus, the evidence supports program-specific IFN replication across heterogeneous cohorts, not a globally shared disease transcriptome. The GSE135779 atypical/low-naive score was positive (effect 1.191; q=5.10 x 10^-4), but the corresponding GSE174188 result was null; it is retained as an external-only observation rather than replication. Conversely, the GSE174188 naive-to-memory and APC/HLA signals were null externally.

### External mapping did not meet its reference-calibration gate

The corrected sensitivity processed all 56 external matrices (363,083 cells), retaining 353,527 cells after quality control and selecting 36,630 B-lineage candidates without parsing source cell labels or disease fields. No elastic-net confidence candidate met all frozen calibration requirements. The diagnostic threshold of 0.95 retained 94.20% of reference cells, with B_CONV precision 99.64% but B_ASC precision 88.52%, below 90%. The centroid calibration met the precision and coverage criteria, but did not replace the required elastic-net mapper. Corrected external disease outcomes were therefore not estimated (Supplementary Table S9 and Fig. S10). This limitation leaves the independent primary replication source-label-defined; it neither demonstrates failure of the IFN association nor establishes source-label-independent replication.

### Prespecified regulatory and perturbational evidence converges on the IFN response

We next tested whether the replicated transcriptional program was accompanied by a prespecified regulatory pattern. The regulator analysis was specified before regulator effects were inspected and included four IFN-centred regulators (STAT1, STAT2, IRF7 and IRF9), four proliferation specificity comparators (E2F1, FOXM1, MYC and MYBL2), and the three confirmatory contrasts used above. Signed CollecTRI target activity was evaluated in one global Benjamini-Hochberg family of 24 tests.

STAT1 and STAT2 activity estimates were positive and globally significant in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. At least three of the four IFN-centred regulators were positive in every contrast, with no globally significant opposite-direction IFN regulator. The proliferation specificity comparators did not reproduce a positive globally significant pattern across all three contrasts. Every leave-one-target estimate for the core STAT1 and STAT2 models retained the positive direction, and each core model remained positive in all 100 deterministic 80%-target resamples. These diagnostics argue against a result driven by one target gene or a small target subset.

The correlation-aware analysis reproduced the exact frozen matched-target counts for all six core tests (STAT1: 98, 129 and 161; STAT2: 14, 19 and 20). CAMERA retained the expected positive direction in six of six tests and passed the six-test BH threshold in five. The exception was discovery-cohort STAT2 (estimated inter-gene correlation 0.1225; CAMERA q=0.1355), for which FRY remained positive and significant (q=4.91 x 10^-5). FRY was positive and BH-significant in all six core tests. Thus, the sensitivity supports cross-contrast convergence while explicitly precluding a claim that every core test was significant under CAMERA.

After removal of the 12 frozen IFN/ISG positive-arm genes, all six ULM estimates retained positive 95% confidence intervals and dedicated six-test q<0.05; CAMERA remained positive in six of six and significant in five, while FRY remained positive and significant in all six. At least 78.6% of matched targets were retained, and the minimum ULM slope was 53.5% of its baseline value. After removal of all M5911 genes, all 18 method-level directions remained positive, but support attenuated: ULM passed correction in five of six tests, CAMERA in two of six and FRY in five of six. Discovery STAT2 retained 8 of 14 targets and had ULM slope 0.391 (95% confidence interval -0.745 to 1.526; q=0.500), CAMERA q=0.623 and FRY q=0.099. All 11 depleted models eligible for leave-one-target analysis preserved direction. The signal is therefore not reducible to the 12 core program genes, but it remains partly coupled to the broader interferon-response transcriptome.

A curated response-set analysis and a separate perturbational context were directionally concordant. The exact MSigDB Hallmark interferon-alpha response set M5911 was positively enriched in all three ranked contrasts (normalized enrichment scores 3.187, 3.050 and 3.527; 10,000 gene-label permutations per contrast). In GSE23307 primary human B cells exposed to IFN-beta, the frozen 12-gene positive arm increased for all 12 genes in each of two healthy donors. Mean paired log2(x+1) effects were 3.294 and 3.666. No inferential P value was calculated for this two-donor experiment.

The three layers therefore support an IFN-centred regulatory interpretation of the replicated program, but they do not identify a unique initiating ligand or establish causation in SLE. CollecTRI activity is inferred from observational disease-ranked statistics, M5911 is a response signature, and GSE23307 is a small ex vivo perturbation in healthy-donor B cells.

## Discussion

This study identifies a reproducible level of SLE B-cell biology by separating identity, composition and transcription before testing disease effects. Fine-grained hard B-cell state assignments failed frozen-representation resampling, and end-to-end reconstruction further showed that the broad B_CONV/B_ASC partition missed its prespecified B_ASC overlap criterion despite high global concordance. We therefore use the partition as an analysis scaffold, not a universally reproducible taxonomy. Within that bounded scope, primary `B_ASC` relative abundance did not differ between managed SLE and controls, and observed broad-state boundary exchanges did not change that null result. The central result instead arose within `B_CONV`: a frozen IFN/ISG program was supported in the primary GSE174188 contrast, an internal donor-nonoverlap contrast and independent GSE135779, and remained positive when end-to-end boundary exchanges were propagated.

This result refines, rather than challenges, established SLE interferon biology. Prior studies show IFN heterogeneity across molecular endotypes [18,20,23], link activated B-cell and plasmablast phenotypes to specific disease contexts [19,22,24], and demonstrate that several interferon classes can promote B-cell activation or plasma-cell differentiation [25,30]. In particular, the reported plasmablast expansion in patients with higher activity and Sm/RNP autoantibodies [19] is compatible with our secondary positive flare estimate and our null primary managed-SLE estimate. The contribution here is the identification of the layer that survives a disease-blind, biological-replicate-aware and cross-cohort validation sequence, not a claim that interferon involvement itself is newly discovered. Persistent IFN activity in antimalarial-treated patients with low disease activity stratified by polygenic risk [31] is likewise consistent with context-dependent interferon remodeling; because neither cohort nor frozen program is shared, it remains external biological context rather than independent validation of our effect. Recent functional evidence links type I interferon exposure to B-cell activation and DN2 differentiation in SLE [32]. This supports the biological plausibility of interferon-responsive fine states, while our resampling result addresses a different question: whether a disease-blind hard fine-grained partition is stable enough to serve as a disease-inference unit in a heterogeneous public dataset.

The low cross-dataset genome-wide correlation is not a contradiction of the frozen program result. The two accessions differ in age structure, source annotation, sample processing, gene universe and available covariates. A broad correlation asks whether thousands of effect estimates agree despite these differences; the frozen program test asks whether a prespecified coherent biological response has the same direction and statistical support. The data support the latter and explicitly reject the stronger transcriptome-wide interpretation.

The regulator analysis adds convergence without changing that inferential level. The primary ULM family found positive, globally corrected STAT1 and STAT2 activity in all three contrasts, and target-deletion and target-resampling diagnostics preserved direction. The correlation-aware analysis was directionally concordant in every core test, but CAMERA supported five of six tests after correction while FRY supported six of six; discovery-cohort STAT2 was the transparent CAMERA exception. Narrow 12-gene overlap depletion retained broad support, whereas M5911 depletion exposed substantial attenuation and a low-coverage discovery STAT2 model. Because these tests reuse the same contrasts and regulons, they are robustness analyses rather than new biological replication. M5911 enrichment and paired IFN-beta exposure provide curated response-set concordance and a separate perturbational context. Together, these layers make an IFN-centred regulatory framing more credible than a gene-list description alone, while not proving overlap-independent regulation, initiation of the in vivo state by STAT1 or STAT2, a unique IFN ligand, or direct TF binding.

The results also narrow several common SLE B-cell narratives. The naive-to-memory and APC/HLA axes are useful internal context but do not independently reproduce in GSE135779. The external atypical/low-naive signal cannot be labelled replication because it was absent in GSE174188. Likewise, high global concordance of a broad `B_CONV` scaffold does not establish a discrete IFN-high subtype or a fixed cell taxonomy: interferon is treated as a continuous within-compartment program. The primary composition result remains a transparent negative boundary rather than being displaced by the secondary flare estimate.

From a precision-medicine perspective, the continuous B_CONV IFN/ISG score could eventually contribute to molecular stratification or pharmacodynamic monitoring, particularly where bulk or compositional readouts obscure a cell-intrinsic response. The present study does not establish a predictive biomarker, treatment-selection rule, clinical cutoff or patient benefit. Those uses require prospective treatment-annotated cohorts, longitudinal sampling, assay calibration and prespecified evaluation of discrimination and clinical utility.

The analysis has limitations. Public metadata did not provide a common set of sex, treatment and detailed clinical covariates across all contrasts. End-to-end resampling failed the B_ASC state-overlap criterion, and propagation of the observed exchanges is a same-data sensitivity rather than proof of taxonomy transfer. The adult external stratum was small, and two adult metadata donors lacked corresponding source matrices. The GSE174188 internal validation is not independent of the accession even after donor overlap is removed. The conventional-B mapping in GSE135779 relies on source labels and supports a broad analog rather than exact identity transfer. CollecTRI target activity depends on curated prior knowledge and gene coverage; the correlation-aware and overlap-depletion sensitivities do not create independent data. One discovery STAT2 CAMERA baseline test did not pass correction, and the M5911-depleted discovery STAT2 model retained only eight targets with an interval spanning zero. The GSE23307 perturbation contains only two donors and was therefore interpreted descriptively. Direct binding, matched patient perturbation and prospective clinical validation remain outside the current evidence.

## Conclusions

The defensible advance is specific: SLE is associated with an independently replicated IFN transcriptional shift within a disease-blind conventional-B analysis scaffold. Prespecified regulator activity, correlation-aware sensitivity testing, external response-set enrichment and a small healthy-donor perturbation provide convergent but non-causal support. The study identifies which remodeling layer survives sequential design and validation constraints; it does not establish a universally reproducible taxonomy, discrete subtype, universal plasmablast expansion, causal regulator or unique upstream ligand.

## List of abbreviations

**ASC:** antibody-secreting cell; **CAMERA:** correlation-adjusted mean-rank gene-set test; **B_ASC:** disease-blind antibody-secreting-cell compartment; **B_CONV:** disease-blind broad conventional-B compartment; **FDR:** false discovery rate; **FRY:** fast rotation gene-set test; **GEO:** Gene Expression Omnibus; **HC1/HC3:** heteroskedasticity-consistent covariance estimators; **IFN:** interferon; **ISG:** interferon-stimulated gene; **NES:** normalized enrichment score; **SLE:** systemic lupus erythematosus; **TF:** transcription factor; **TMM:** trimmed mean of M values; **UMI:** unique molecular identifier.

## Declarations

### Ethics approval and consent to participate

This secondary study used only publicly available, de-identified human transcriptomic datasets and involved no participant recruitment, intervention or collection of new specimens. No additional ethics approval was required for this secondary analysis. Ethics approval and consent procedures for the source studies are reported in the original publications [1,2,13].

### Consent for publication

Not applicable; the manuscript contains no identifiable individual participant information.

### Availability of data and materials

The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [14-16]. The project repository is https://github.com/1209433622cz-maker/sle-bcell-remodeling; an initial immutable snapshot is archived at doi:10.5281/zenodo.22086892 [17]. That snapshot predates the end-to-end reconstruction and corrected external-mapping audits. A matching version-specific archive of the revised code, decisions, source data and SHA-256 records is required before submission. Original project code is licensed under the MIT License; original manuscript text, composite figures, project documentation and project-generated derived source-data tables are licensed under CC BY 4.0. These licences do not relicense GEO, CELLxGENE or other third-party source material. Large recomputable matrices are not duplicated from their source repositories.

### Competing interests

The authors declare that they have no competing interests.

### Funding

This research received no specific funding.

### Authors' contributions

ZC: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft. TQ: Conceptualization, Methodology, Project administration, Validation, Writing - review and editing. Both authors approved the earlier materials. Renewed final approval of the corrected manuscript and supporting materials is pending.

### Acknowledgements

Not applicable.

### Use of generative artificial intelligence

Generative artificial intelligence tools, including OpenAI Codex and ChatGPT, were used to assist with code development, reproducibility checks, language editing and preparation of submission materials. The authors are responsible for verifying the revised analyses, code, text, references, figures and source data before submission and retain full responsibility for the work. Generative artificial intelligence was not used to create or alter primary research data.

## Additional files

**Additional file 1 (.docx):** Supplementary information. Extended governance, evidence-boundary and reproducibility tables supporting the disease-blind reconstruction, sample-level composition, pseudobulk replication and regulatory analyses.

**Additional file 2 (.zip):** Figure source data. Machine-readable CSV files underlying Figures 1-5 and Supplementary Figures S1-S10, with a SHA-256 manifest.

**Additional file 3 (.zip):** Regulator sensitivity. Baseline correlation-aware STAT1/STAT2 tests, post-freeze IFN-overlap-depletion results, leave-one-target diagnostics, Figure S8 Source Data, qualified decision records and a SHA-256 manifest.

**Additional file 4 (.zip):** Full statistical results. Complete gene-level results for 12 frozen model branches, composition and program tables, regulator and orthogonal results, end-to-end identity robustness and boundary-propagation outputs, corrected external-mapping calibration diagnostics, sanitized design matrices, the statistical-family map and SHA-256 provenance manifests. The calibration extension contains no corrected external disease-effect estimates.

## Figure legends

### Figure 1 | Disease-blind reconstruction defines the permissible identity scope

**a,** Study design and evidence hierarchy. GSE174188 B-lineage cells passed hard quality control before construction of a disease-blind `B_CONV`/`B_ASC` analysis scaffold and separation into `B_ASC` composition and `B_CONV` pseudobulk/program analyses. GSE174188 internal validation and GSE135779 independent replication are displayed in parallel, followed by three interpretation-only evidence classes. **b,** Median mapped adjusted Rand index and minimum-to-median interval for each candidate identity policy across 20 within-library resamples of the frozen 50-dimensional Harmony representation; policies are discrete alternatives and are not connected as a trajectory. The short dashed segment applies only to the two-compartment minimum-ARI criterion of 0.90. **c,** Mapped adjusted Rand index and mapping agreement in each frozen-representation two-compartment graph resample; the dashed horizontal guide marks the minimum mapped-ARI criterion of 0.990. **d,** Minimum and median state Jaccard indices from the same frozen-representation analysis for `B_CONV` and `B_ASC`, with antibody-secreting marker support; the dashed vertical guide marks the minimum state-median Jaccard criterion of 0.95. Panels b-d do not recompute highly variable genes, principal components or Harmony; the end-to-end sensitivity is reported in Supplementary Fig. S9. Cell-level summaries define assignment stability and are not disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

**a,** Observed `B_ASC` fractions for exactly 43 control and 47 managed-SLE sample-cohort strata in the primary composition contrast; diamonds and bars show adjusted fractions and 95% confidence intervals. **b,** Primary, internal, donor-nonoverlap and secondary flare conditional odds ratios. **c,** Frozen primary estimate and mandatory minimum-cell, explicit non-B and residual-doublet sensitivities. **d,** Conditional odds ratios after each of 90 primary sample deletions; the horizontal line is the full estimate. The flare contrast is secondary and did not pass the frozen three-contrast false-discovery-rate rule.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

**a,** Effects and 95% confidence intervals for the four frozen programs in the primary contrast. **b,** IFN/ISG estimates across primary support thresholds, residual-risk restriction, internal replication, donor-nonoverlap internal replication and the secondary flare contrast. **c,** Gene-level log2 fold changes for the frozen IFN positive arm in the primary and donor-nonoverlap contrasts. A dagger marks genes not tested at gene level in either contrast; a double dagger marks genes not tested in the primary contrast. Filtered values are absent rather than zero or imputed. **d,** IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity families in the primary and donor-nonoverlap contrasts. Program intervals use HC3 uncertainty; confirmatory q values use the frozen four-program family.

### Figure 4 | GSE135779 independently replicates the frozen IFN/ISG program

**a,** Standardized IFN/ISG effects for childhood, combined, adult and support-threshold external analyses. **b,** Standardized discovery and internal GSE174188 effects beside independent GSE135779 effects. **c,** Effects for 4,410 genes tested in both primary datasets, with ten jointly tested frozen IFN genes highlighted; all ten were positive in both datasets despite Spearman rho=0.026 genome-wide. **d,** Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Sequential display labels 1-8 correspond to the original source codes retained in Figure 4 Source Data. Donors are the biological units in GSE135779; the adult estimate is directional only.

### Figure 5 | Convergent observational evidence supports IFN-centred regulation

**a,** Three parallel interpretation branches for the replicated IFN/ISG program: same-data regulator robustness, curated M5911 response-set concordance and separate GSE23307 perturbational context. Equal branch weight does not imply causal ordering; the bottom boundary states that no causal regulator or unique upstream ligand is established. **b,** Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. **c,** Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation specificity comparators. Asterisks indicate global 24-test q<0.05. **d,** M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. **e,** Mean paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells from two healthy donors; labels show positive genes. The GSE23307 panel is descriptive at n=2 and carries no inferential P value.

## References

1. Perez RK, Gordon MG, Subramaniam M, Kim MC, Hartoularos GC, Targ S, et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. Science. 2022;376(6589):eabf1970. doi:10.1126/science.abf1970.
2. Nehar-Belaid D, Hong S, Marches R, Chen G, Bolisetty M, Baisch J, et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. Nature Immunology. 2020;21(9):1094-1106. doi:10.1038/s41590-020-0743-0.
3. Crowell HL, Soneson C, Germain PL, Calini D, Collin L, Raposo C, et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. Nature Communications. 2020;11(1):6077. doi:10.1038/s41467-020-19894-4.
4. Squair JW, Gautier M, Kathe C, Anderson MA, James ND, Hutson TH, et al. Confronting false discoveries in single-cell differential expression. Nature Communications. 2021;12(1):5692. doi:10.1038/s41467-021-25960-2.
5. Büttner M, Ostner J, Müller CL, Theis FJ, Schubert B. scCODA is a Bayesian model for compositional single-cell data analysis. Nature Communications. 2021;12(1):6876. doi:10.1038/s41467-021-27150-6.
6. Wolf FA, Angerer P, Theis FJ. SCANPY: large-scale single-cell gene expression data analysis. Genome Biology. 2018;19(1):15. doi:10.1186/s13059-017-1382-0.
7. Korsunsky I, Millard N, Fan J, Slowikowski K, Zhang F, Wei K, et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nature Methods. 2019;16(12):1289-1296. doi:10.1038/s41592-019-0619-0.
8. Traag VA, Waltman L, van Eck NJ. From Louvain to Leiden: guaranteeing well-connected communities. Scientific Reports. 2019;9(1):5233. doi:10.1038/s41598-019-41695-z.
9. Robinson MD, McCarthy DJ, Smyth GK. edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. Bioinformatics. 2010;26(1):139-140. doi:10.1093/bioinformatics/btp616.
10. Badia-i-Mompel P, Vélez Santiago J, Braunger J, Geiss C, Dimitrov D, Müller-Dott S, et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. Bioinformatics Advances. 2022;2(1):vbac016. doi:10.1093/bioadv/vbac016.
11. Müller-Dott S, Tsirvouli E, Vazquez M, Ramirez Flores RO, Badia-i-Mompel P, Fallegger R, et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. Nucleic Acids Research. 2023;51(20):10934-10949. doi:10.1093/nar/gkad841.
12. Liberzon A, Birger C, Thorvaldsdóttir H, Ghandi M, Mesirov JP, Tamayo P. The Molecular Signatures Database Hallmark Gene Set Collection. Cell Systems. 2015;1(6):417-425. doi:10.1016/j.cels.2015.12.004.
13. van Boxel-Dezaire AHH, Zula JA, Xu Y, Ransohoff RM, Jacobberger JW, Stark GR. Major Differences in the Responses of Primary Human Leukocyte Subsets to IFN-beta. The Journal of Immunology. 2010;185(10):5888-5899. doi:10.4049/jimmunol.0902314.
14. National Center for Biotechnology Information. Gene Expression Omnibus series GSE174188. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188. Accessed 21 Aug 2026.
15. National Center for Biotechnology Information. Gene Expression Omnibus series GSE135779. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779. Accessed 21 Aug 2026.
16. National Center for Biotechnology Information. Gene Expression Omnibus series GSE23307. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE23307. Accessed 21 Aug 2026.
17. Chen Z, Qi T. SLE B-cell remodeling analysis: code, source data and reproducible release. Zenodo. 2026. doi:10.5281/zenodo.22086892.
18. Hubbard EL, Bachali P, Kingsmore KM, He Y, Catalina MD, Grammer AC, et al. Analysis of transcriptomic features reveals molecular endotypes of SLE with clinical implications. Genome Medicine. 2023;15(1):84. doi:10.1186/s13073-023-01237-9.
19. van Dooren HJ, Atisha-Fregoso Y, Dorjée AL, Huizinga TWJ, Mackay M, Aranow C, et al. Interferon signatures fuel B cell hyperactivity and plasmablast expansion in systemic lupus erythematosus. Journal of Autoimmunity. 2025;154:103438. doi:10.1016/j.jaut.2025.103438.
20. Banchereau R, Hong S, Cantarel B, Baldwin N, Baisch J, Edens M, et al. Personalized Immunomonitoring Uncovers Molecular Networks that Stratify Lupus Patients. Cell. 2016;165(3):551-565. doi:10.1016/j.cell.2016.03.008.
21. Arazi A, Rao DA, Berthier CC, Davidson A, Liu Y, Hoover PJ, et al. The immune cell landscape in kidneys of patients with lupus nephritis. Nature Immunology. 2019;20(7):902-914. doi:10.1038/s41590-019-0398-x.
22. Jenks SA, Cashman KS, Zumaquero E, Marigorta UM, Patel AV, Wang X, et al. Distinct Effector B Cells Induced by Unregulated Toll-like Receptor 7 Contribute to Pathogenic Responses in Systemic Lupus Erythematosus. Immunity. 2018;49(4):725-739.e6. doi:10.1016/j.immuni.2018.08.015.
23. Chiche L, Jourde-Chiche N, Whalen E, Presnell S, Gersuk V, Dang K, et al. Modular Transcriptional Repertoire Analyses of Adults With Systemic Lupus Erythematosus Reveal Distinct Type I and Type II Interferon Signatures. Arthritis & Rheumatology. 2014;66(6):1583-1595. doi:10.1002/art.38628.
24. Szelinski F, Stefanski AL, Schrezenmeier E, Rincon-Arevalo H, Wiedemann A, Reiter K, et al. Plasmablast-like Phenotype Among Antigen-Experienced CXCR5 - CD19 low B Cells in Systemic Lupus Erythematosus. Arthritis & Rheumatology. 2022;74(9):1556-1568. doi:10.1002/art.42157.
25. Akita K, Yasaka K, Shirai T, Ishii T, Harigae H, Fujii H. Interferon alpha Enhances B Cell Activation Associated With FOXM1 Induction: Potential Novel Therapeutic Strategy for Targeting the Plasmablasts of Systemic Lupus Erythematosus. Frontiers in Immunology. 2021;11:498703. doi:10.3389/fimmu.2020.498703.
26. Wu D, Smyth GK. Camera: a competitive gene set test accounting for inter-gene correlation. Nucleic Acids Research. 2012;40(17):e133-e133. doi:10.1093/nar/gks461.
27. Wu D, Lim E, Vaillant F, Asselin-Labat ML, Visvader JE, Smyth GK. ROAST: rotation gene set tests for complex microarray experiments. Bioinformatics. 2010;26(17):2176-2182. doi:10.1093/bioinformatics/btq401.
28. Ritchie ME, Phipson B, Wu D, Hu Y, Law CW, Shi W, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Research. 2015;43(7):e47-e47. doi:10.1093/nar/gkv007.
29. Law CW, Chen Y, Shi W, Smyth GK. voom: precision weights unlock linear model analysis tools for RNA-seq read counts. Genome Biology. 2014;15(2):R29. doi:10.1186/gb-2014-15-2-r29.
30. Barnas JL, Albrecht J, Meednu N, Alzamareh DF, Baker C, McDavid A, et al. B Cell Activation and Plasma Cell Differentiation Are Promoted by IFN-lambda in Systemic Lupus Erythematosus. The Journal of Immunology. 2021;207(11):2660-2672. doi:10.4049/jimmunol.2100339.
31. Sayadi A, Eloranta M-L, Oparina N, Wallgren M, Skoglund E, Frodlund M, et al. Single-cell RNA-seq reveals a persistent interferon signature in immune cells from systemic lupus erythematosus patients with high versus low polygenic risk scores despite antimalarial treatment. Journal of Autoimmunity. 2026;161:103575. doi:10.1016/j.jaut.2026.103575.
32. Faheem Z, Boukhaled GM, Nassar C, Manion K, Kim M, Bonilla D, et al. Type I interferons enhance B cell activation and promote differentiation of double negative 2 cells in SLE. Lupus Science & Medicine. 2026;13(1):e002042. doi:10.1136/lupus-2026-002042.
