# Disease-blind single-cell reconstruction distinguishes unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus

Article type: Research

Authors: Zhi Chen [1] and Teng Qi [1,*]

Affiliation 1: School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen 518172, China

Corresponding author: Teng Qi, School of Medicine, The Chinese University of Hong Kong, Shenzhen, MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China; tengqi@link.cuhk.edu.cn

ORCID identifiers: Zhi Chen, https://orcid.org/0009-0001-0072-5576; Teng Qi, https://orcid.org/0009-0007-7648-4776

Author emails: Zhi Chen, zhichen1@link.cuhk.edu.cn; Teng Qi, tengqi@link.cuhk.edu.cn

Running title: Replicated IFN remodeling in SLE B cells

## Abstract

**Background:** Single-cell studies of systemic lupus erythematosus (SLE) can conflate cell identity, abundance and transcription when state labels are outcome-informed or cells are treated as biological replicates. We asked which layer of B-cell remodeling remains defensible after disease-blind reconstruction and biological-unit-aware validation.

**Methods:** We reanalysed public single-cell transcriptomic datasets using donor- and cohort-resolved inference. In GSE174188, disease-blind B-lineage reconstruction preceded sample-level composition and raw-count pseudobulk analyses. A frozen-representation identity policy was challenged by 20 end-to-end resampling replicates that recomputed highly variable genes, principal components, Harmony, neighbour graphs and Leiden clusters; observed boundary exchanges were then propagated through the prespecified composition and IFN/ISG models. The IFN/ISG program was evaluated in a source-label-defined conventional-B analog in independent GSE135779 and complemented by prespecified regulatory, response-set and perturbational analyses.

**Results:** Among 150,402 GSE174188 B-lineage cells, frozen-representation resampling supported broad conventional-B (B_CONV) and antibody-secreting-cell (B_ASC) compartments but not stable fine-grained naive/memory assignments. End-to-end resampling retained high global concordance yet missed the prespecified B_ASC overlap criterion (median Jaccard 0.930 versus 0.95), restricting the partition to an analysis scaffold. Propagating observed boundary exchanges preserved both the primary B_ASC composition null and the B_CONV IFN/ISG effects. The primary B_ASC odds ratio was 0.947 (95% confidence interval 0.636-1.410; P=0.787). By contrast, the IFN/ISG program was higher in the primary GSE174188 contrast (effect 0.837; q=2.98 x 10^-6), the donor-nonoverlap internal contrast (effect 1.086; q=3.61 x 10^-4) and independent GSE135779 childhood donors (11 controls and 32 SLE; effect 1.042; q=2.98 x 10^-6). All ten jointly tested IFN genes were positive despite weak genome-wide agreement (Spearman rho=0.026). Corrected source-label-independent mapping failed reference calibration; no corrected external disease effect was estimated. STAT1/STAT2 evidence remained directionally concordant across ULM, CAMERA and FRY, while broader M5911 depletion attenuated discovery STAT2 and limited claims of overlap-independent regulation.

**Conclusions:** These cohorts support a process-level IFN association through disease-blind discovery and source-label-defined external replication, while the tested hard state assignments retain stability and transfer limits. Regulatory evidence is convergent but observational and does not establish a causal regulator or unique upstream stimulus.

## Keywords

systemic lupus erythematosus; B cells; single-cell RNA sequencing; pseudobulk; interferon; independent validation; transcription-factor activity; reproducibility

## Background

Single-cell profiling has sharpened the cellular resolution of SLE, but it also creates a basic inferential problem: disease effects can be attached to a cell-state label before the stability of that label, the relevant biological replicate and the cohort structure have been established. Peripheral-blood studies have described naive, memory, double-negative, CD11c-positive and antibody-secreting B-cell populations together with prominent interferon responses [1-4]. Yet cell-level tests can inflate precision when donors rather than cells are the experimental units [5,6], and compositional changes are intrinsically coupled because expansion of one compartment alters the observed fractions of the others [7]. The biological interpretation of a single-cell disease signal therefore depends on both the molecular effect and the inferential layer at which it is claimed.

This distinction is especially important in SLE because neither interferon activity nor plasmablast biology is novel, and both vary with disease context. Longitudinal paediatric immunomonitoring linked plasmablast signatures to disease activity [8], modular adult studies resolved heterogeneous interferon activation thresholds [9], and deep phenotyping identified a higher-activity subgroup with an increased plasmablast-to-memory ratio and Sm/RNP autoantibodies [10]. Large transcriptomic studies likewise support multiple molecular endotypes rather than a single uniform SLE state [11]. More recent single-cell data show persistent interferon activity even during low disease activity and antimalarial treatment, with additional variation by polygenic-risk burden [12]. Tissue single-cell studies extend this heterogeneity to inflamed renal immune niches [13], while experimental studies support the capacity of several interferon classes to promote B-cell activation or plasma-cell differentiation [14-16]. Together, these observations argue against treating either B-cell abundance or an interferon-responsive state as context-free disease features.

A remaining question is therefore not whether interferon is involved in SLE, but which layer of B-cell remodeling remains reproducible after identity formation is separated from disease labels and inference is anchored to biological samples or donors. Public SLE datasets make this question non-trivial: samples are distributed across processing cohorts, some donors recur across samples or cohorts, clinical covariates are incomplete, and external datasets provide different annotation schemes and gene universes. Under these conditions, outcome-informed clustering or pooled cell-level tests can blur technical structure, composition and within-cell-state transcription.

We addressed this problem with a staged secondary analysis in which source integrity, metadata hierarchy and disease-by-cohort support were evaluated before disease effects were estimated. B-lineage identity was reconstructed while disease fields were protected, fine-grained and broad identity policies were explicitly stress-tested, and only the retained disease-blind scaffold was carried into sample-level composition and raw-count pseudobulk analyses. The central transcriptional result was then tested in independent GSE135779 and challenged by identity-uncertainty propagation, cross-dataset gene-level comparison and prespecified regulatory and response-based analyses. The intended contribution is thus an evidence hierarchy: to distinguish the B-cell features that survive increasingly stringent reconstruction and validation from those that remain cohort-specific, representation-dependent or mechanistically unproven.

## Methods

### Study design and data resources

This study was a secondary analysis of public human transcriptomic data. GSE174188 [1,17] served as the discovery resource for disease-blind B-lineage reconstruction, sample-level composition, within-compartment transcription and internal robustness analyses. GSE135779 [2,18] served as the independent SLE validation dataset. CollecTRI and MSigDB provided independently curated regulatory and response priors, and GSE23307 [19,20] provided paired IFN-beta perturbation profiles from primary B cells of healthy donors. Resources that did not contribute to the central replication question were excluded from the active manuscript.

### Source integrity, metadata hierarchy and hard quality control

Source paths, SHA-256 hashes, matrix dimensions and matrix encodings were fixed before analysis. Metadata were reconciled at donor, biological-sample, technical-library and processing-cohort levels. Hard quality control required at least 500 total counts, at least 200 detected genes, no more than 10% mitochondrial counts, no more than 1% haemoglobin counts, no more than 0.5% platelet-marker counts and detection of at least one B-lineage marker. Each excluded cell retained a reason-level record. Disease fields were stored separately and were not used during identity reconstruction.

### Disease-blind representation and identity adjudication

Residual doublet risk was evaluated per complete library. Raw counts were retained for pseudobulk analyses, whereas normalized log expression was used for recurrent highly variable gene selection, principal-component analysis and neighbour-graph construction. Unintegrated Scanpy [21] and Harmony-adjusted [22] representations were compared using technical mixing, biological marker conservation, bridge samples and coverage across donors, samples and libraries. Identity-policy selection used 20 within-library resamples containing 80% of cells from the frozen 50-dimensional Harmony representation. The fine-grained solution failed the prespecified stability criteria and was retained as a negative result. Transition reconstruction instead supported a broad B_CONV/B_ASC partition after marker and frozen-representation stability checks, with disease information still protected.

### End-to-end identity sensitivity and uncertainty propagation

To test whether the broad partition survived reconstruction of the representation itself, we repeated within-library 80% resampling 20 times from the raw matrix. Each replicate independently filtered genes, selected 3,000 recurrent highly variable genes from a 7,000-gene candidate pool, recalculated 50 principal components, reran Harmony, reconstructed 15-nearest-neighbour graphs and reran Leiden [23] at resolutions 0.4, 0.6 and 0.8. Replicate clusters were mapped to the frozen reference by maximum cell overlap. The unchanged broad-state criteria were median and minimum mapped adjusted Rand indices of at least 0.95 and 0.90, median and minimum mapping agreement of at least 0.995 and 0.990, and minimum state-median Jaccard of at least 0.95.

Uncertainty propagation used only assignment exchanges observed in these end-to-end replicates. For each replicate, sampled cells that switched between B_CONV and B_ASC were changed in the full frozen partition, whereas unsampled cells retained their frozen assignment. No sample, gene, threshold or model was reselected. The beta-binomial composition models were refitted under the original eligibility rules and designs. Boundary-cell raw counts were added to or subtracted from the frozen B_CONV pseudobulks before TMM log-counts-per-million normalization, scoring of the frozen 12-gene IFN/ISG program and HC3 inference. These analyses quantify same-data sensitivity to identity uncertainty; they are not independent validation.

### Sample-level composition

Cells were aggregated by biological sample and processing cohort, with the sample-cohort stratum as the experimental unit and donor-aware sensitivity analyses for repeated samples. Models were restricted to prespecified processing cohorts with case-control common support and to strata containing at least 50 frozen B cells. The primary comparison was processing-cohort-4 source-metadata managed SLE versus normal, adjusted for age and ethnicity. Internal processing-cohort-2 and secondary processing-cohort-3 analyses of the source-metadata flare category were estimated separately. Bridge strata were not pooled to create an otherwise unsupported disease coefficient. Model-based and sandwich uncertainty, threshold analyses, one-sample-per-donor fits and leave-one-out diagnostics were retained.

### Raw-count pseudobulk and gene-level inference

Raw counts were summed by sample-cohort stratum within B_CONV, combining technical-library contributions only after cell-ID and count-conservation checks. Strata with at least 50 cells defined the primary analysis; 20- and 100-cell thresholds and a residual-doublet-risk-negative branch were prespecified sensitivities. Genes were filtered with edgeR [24] filterByExpr, libraries were TMM-normalized, and robust quasi-likelihood models were fitted with the prespecified contrast-specific covariates. Benjamini-Hochberg adjustment was applied across tested genes within each contrast, while complete feature tables retained untested genes with explicit status flags.

### Frozen program inference

Program membership and direction were fixed before disease effects were estimated. Duplicate gene symbols were summed before TMM log-counts-per-million normalization. Within each contrast, genes were standardized across pseudobulks and each program score was calculated as the mean positive-arm score minus the mean negative-arm score. Disease effects and 95% confidence intervals were estimated with linear models using HC3 sandwich covariance. The confirmatory family comprised naive-to-memory, atypical/low-naive, APC/HLA and IFN/ISG programs, with Benjamini-Hochberg correction across these four tests. Ranked competitive enrichment and gene-direction coherence were treated as secondary support.

### Independent GSE135779 validation

GSE135779 source files, metadata versions, donor availability, source-label support and availability of the frozen program genes were evaluated before disease effects were inspected. The external identity scope was deliberately broad: a conventional-B analog assembled from eight source B-cell labels, without transferring hard naive/memory identities. Childhood, adult and combined model matrices and minimum-cell sensitivities were fixed before model fitting. Real matrices were first used only for dimension and count-conservation qualification, and synthetic null and signal data were used to qualify the statistical engine. Gene- and program-level analyses then followed the GSE174188 framework where permitted by the external gene universe.

### Reference-calibrated external mapping sensitivity

We additionally asked whether B-lineage selection in GSE135779 could be reconstructed without source-provided cell labels. Sample-wise quality control and Leiden clustering of all external matrices preceded selection with prespecified B-lineage and exclusion-marker modules. Elastic-net logistic regression and Pearson nearest-centroid mapping provided two algorithmically distinct broad-state mappers using the same GSE174188 reference and common feature space. Donor-grouped reference cross-validation evaluated regularization and candidate confidence thresholds under prespecified state-specific eligibility criteria. Eligibility required at least 80% reference-cell coverage and at least 90% precision for each state; high overall accuracy alone was insufficient. The reference training set contained 13,000 B_CONV and 1,300 B_ASC cells from 258 donors. These folds calibrated mapping performance and were not independent validation of the full feature-selection and tuning pipeline.

A post-unblinding audit identified incompatible normalization denominators between the original reference and external feature matrices: selected-feature totals were used in the reference, whereas full-library totals were used externally. We therefore recomputed the reference with full-library log1p(CP10K) normalization before feature subsetting and reran all matrices without changing the selection rules, candidate grids or eligibility thresholds. Diagnostic fallback thresholds were not permitted to determine eligibility for disease-effect analysis. Inputs, code, predictions and protected-metadata identity were verified by hashes. Because the original sensitivity outcomes had already been observed, this correction was treated as a technical repair rather than a new prospective analysis. Failure of the corrected calibration criterion prevented disease-effect estimation, and the original sensitivity outcome was excluded from supporting evidence.

### Influence, specificity and cross-dataset analyses

The childhood IFN/ISG model was repeated after removing each donor in turn. Dependence on source annotation was assessed by omitting each of the eight contributing B-cell labels without reselecting donors. Platelet/ambient, ASC/UPR and pan-B programs were prespecified specificity controls. Cross-dataset gene analysis was restricted to genes passing the respective filters in both primary datasets; the shared IFN subset was evaluated separately from genome-wide effect correlation.

### Prespecified TF-target activity

Human CollecTRI interactions [25,26] were retrieved from OmniPath on 15 August 2026 and fixed by raw SHA-256 98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1. Only exact individual-TF source symbols were used. Consensus stimulation and inhibition were encoded as +1 and -1; ambiguous target directions were excluded, and duplicate same-sign edges were collapsed. The confirmatory family comprised STAT1, STAT2, IRF7, IRF9, E2F1, FOXM1, MYC and MYBL2 across the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts.

For each tested Ensembl feature, the ranked statistic was sign(logFC) * sqrt(F) from the robust edgeR quasi-likelihood model. Features were mapped to uppercase gene symbols, with statistics averaged when multiple tested Ensembl features mapped to the same symbol. For each regulator and contrast, a univariate linear model with an intercept regressed the gene-level statistic on signed target weight. The slope, standard error, two-sided P value and 95% confidence interval were independently reproduced by direct matrix algebra. Benjamini-Hochberg correction was applied once across all 24 confirmatory regulator-by-contrast tests. For each core STAT1/STAT2 model, influence analysis removed each matched target in turn, and 100 deterministic analyses resampled 80% of matched targets.

### Correlation-aware STAT1/STAT2 sensitivity

Because genes within a regulon are correlated, the rank-based ULM results were supplemented by a correlation-aware sensitivity that retained the same regulators, signed CollecTRI targets, contrasts, model matrices and filterByExpr backgrounds. Pseudobulk counts were collapsed to gene symbols and transformed with voom precision weights [27,28]. Expression rows for inhibitory targets were sign-reversed so that a positive set direction retained the signed-regulon interpretation. CAMERA [29] estimated inter-gene correlation from model residuals and performed a competitive rank test, whereas FRY [30] provided a rotation-based directional test. Benjamini-Hochberg adjustment was applied separately across the six STAT1/STAT2 regulator-by-contrast tests for each method. Matched-target counts were required to equal those in the ULM analysis; no target, regulator, contrast or background was reselected after the sensitivity results were examined.

### STAT1/STAT2 IFN-overlap-depletion sensitivity

A post-freeze sensitivity evaluated whether STAT1/STAT2 results were reducible to genes shared with interferon-response programs. Branch A removed the 12 frozen positive-arm IFN/ISG genes from the signed regulon targets; branch B removed all 97 members of MSigDB M5911. Ranked statistics, tested-gene backgrounds, CollecTRI signs, contrasts and model matrices were otherwise unchanged. ULM, CAMERA and FRY were rerun within each branch, and ULM leave-one-target analysis was performed only when at least ten targets remained. Benjamini-Hochberg adjustment was applied separately within each branch and method across the six core regulator-by-contrast tests. Interpretation jointly considered direction, ULM attenuation and confidence intervals, target retention, corrected q values and cross-method consistency rather than a binary significance rule.

### Orthogonal interferon-response analyses

The MSigDB [31] 2026.1.Hs Hallmark set HALLMARK_INTERFERON_ALPHA_RESPONSE (M5911; 97 fixed member genes) was tested against each complete ranked contrast. Preranked enrichment used 10,000 deterministic gene-label permutations; normalized enrichment scores and descriptive three-contrast q values were reported outside the 24-test TF family.

GSE23307 [19,20] GPL6104 profiles comprised paired untreated and IFN-beta-exposed primary B cells from two healthy donors. Platform annotation was fixed before effects were calculated. Twenty-one probes mapping to the 12 frozen IFN/ISG positive-arm genes were transformed as log2(x+1), collapsed to one value per gene and sample by the median, and differenced within donor. The donor summary was the mean paired effect across the 12 genes. Direction and gene concordance were descriptive; no inferential P value was calculated at n=2. Only log2(x+1)-transformed GSE23307 values contributed to the reported results, figures and claims.

### Statistical analysis and multiplicity

This retrospective secondary analysis included all eligible public biological units after the prespecified quality-control, support and mapping rules; no prospective sample-size or power calculation was performed. Analysis sizes are reported with the corresponding results and figure panels. Unless explicitly described as directional, tests were two-sided and intervals were 95% confidence intervals. The primary B_ASC composition model used a beta-binomial Wald test with Benjamini-Hochberg correction across the three prespecified base contrasts; covariance and two-part models were sensitivity analyses reported with nominal P values. Gene-level robust edgeR quasi-likelihood tests used Benjamini-Hochberg correction across filterByExpr-tested genes within each contrast. Frozen-program linear models used HC3 covariance and Benjamini-Hochberg correction across the four prespecified programs within each analysis. Ranked program-arm CAMERA results were corrected within each corresponding analysis.

The CollecTRI activity analysis used two-sided target-slope tests and one global Benjamini-Hochberg family across eight regulators and three confirmatory contrasts (24 tests). STAT1/STAT2 CAMERA and FRY sensitivities used positive-direction tests with separate six-test Benjamini-Hochberg families for each method. Each IFN-overlap-depletion branch contributed separate six-test post-freeze sensitivity families for ULM, CAMERA and FRY; these did not replace the original 24-test regulator family. M5911 used a positive-direction weighted preranked test with 10,000 deterministic gene-label permutations per contrast and a descriptive Benjamini-Hochberg correction across three contrasts. The paired GSE23307 experiment contained two donors and therefore carried no inferential P value. Statistical significance was defined as q<0.05 only within the stated confirmatory family; nominal and descriptive results were not promoted to confirmatory evidence. The complete multiplicity map, full gene-level tables and sanitized design matrices are provided in Additional file 4.

### Generative AI assistance

OpenAI Codex was used for code drafting, workflow documentation, language editing and development of quality-control checks. All computations were executed locally against fixed inputs, and numerical results were taken from machine-generated analysis outputs rather than generated by the language model. The authors remain responsible for the scripts, results, interpretations and revised text. No AI system is listed as an author.

### Reproducibility and provenance

Analyses were organized in timestamped run directories with immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 manifests. Disease effects were estimated only after input, design and statistical-engine qualification. Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version.

## Results

### Disease-blind reconstruction supports a scaffold with state-specific stability limits

The authoritative GSE174188 B-lineage source contained 152,981 cells and 30,172 genes. Prespecified hard-quality-control rules retained 150,402 cells, representing 259 donors, 271 biological samples, 88 technical libraries and four processing cohorts. Repeated donors and samples spanning processing cohorts were explicitly resolved in the metadata hierarchy. Because disease-by-cohort support was uneven, the full disease-blind cell set was available for identity reconstruction, whereas disease effects were restricted to prespecified contrasts with common support.

Complete-library doublet diagnostics, recurrent highly variable gene selection, unintegrated and Harmony representations, bridge-sample checks and marker coverage were evaluated before disease fields were joined. The initial five-state identity solution failed the prespecified resampling criteria and was retained as a negative result rather than relabelled as a successful subtype analysis. Transition reconstruction instead supported a two-compartment B_CONV/B_ASC model, with naive-memory structure represented as a continuous program within B_CONV and platelet-associated expression retained as a technical overlay.

Within the frozen 50-dimensional Harmony representation, the broad partition passed all five criteria across 20 graph resamples: the minimum mapped adjusted Rand index was 0.990, the minimum mapping agreement was 0.9998 and the minimum state-median Jaccard was 0.991. B_ASC marker support was complete for DERL3, JCHAIN, MZB1, TNFRSF17 and XBP1. These results justified the broad partition for the prespecified disease analyses, but they did not address uncertainty introduced by rebuilding the representation itself (Fig. 1).

The end-to-end sensitivity provided that stricter test. All 20 replicates completed and all 20 Harmony runs converged. Global concordance remained high: median and minimum mapped adjusted Rand indices were 0.963 and 0.930, and median and minimum mapping agreements were 0.99937 and 0.99877. The minimum state-median Jaccard was 0.930, however, below the unchanged 0.95 criterion, so the prespecified end-to-end reproducibility requirement was not met. The failure was confined to B_ASC (median Jaccard 0.930; minimum 0.872), whereas B_CONV remained highly concordant (median 0.99936; minimum 0.99876). A median of 76 of 120,320 sampled cells exchanged broad-state assignment per replicate (Supplementary Fig. S9).

Propagating these observed exchanges did not alter the disease-level conclusions. Across the 20 perturbed partitions, primary composition odds ratios ranged from 0.896 to 0.967 and every confidence interval included one. The primary B_CONV IFN/ISG effect ranged from 0.836 to 0.845, and the donor-nonoverlap effect from 1.059 to 1.087; all 40 estimates remained positive with confidence intervals above zero. Thus, the end-to-end sensitivity preserved the frozen disease effects while preventing a stronger taxonomy-level interpretation. We therefore use B_CONV/B_ASC as a disease-blind analysis scaffold rather than a universally reproducible cell taxonomy.

### The primary B_ASC abundance contrast lacks statistical support

After the broad scaffold was fixed, outcomes were joined and composition was analysed at the sample-cohort level, with at least 50 eligible B cells per stratum and no cell-level disease test. In the primary processing-cohort-4 comparison, B_ASC relative abundance showed no statistically supported difference between source-defined managed SLE and controls: the conditional odds ratio was 0.947 (95% confidence interval 0.636-1.410; P=0.787), with adjusted fractions of 1.61% in controls and 1.52% in source-defined managed SLE. The interval does not establish equivalent abundance or exclude an increase. The HC1 sandwich analysis was concordant (95% confidence interval 0.651-1.376; P=0.774), and none of the 90 leave-one-sample-out fits generated evidence that reversed the primary interpretation.

Internal analyses did not convert this null result into a general composition claim. The internal validation estimate remained below one (odds ratio 0.772), as did the explicit donor-nonoverlap estimate (odds ratio 0.591; n=53). A secondary flare contrast was positive (odds ratio 2.303; nominal P=0.0282) but did not survive the prespecified three-contrast correction (q=0.0845). B_ASC abundance therefore provides contextual heterogeneity and an explicit negative boundary; it is not the central disease signal in this analysis.

### IFN/ISG is the most consistently supported of the four prespecified B_CONV programs

The transcriptional analysis retained 89 primary B_CONV pseudobulks, comprising 43 reference and 46 SLE strata and 59,873,385 UMI counts. The difference from the 90 composition strata arose because one source-defined managed-SLE stratum contained 44 B_CONV cells after compartment assignment and did not meet the prespecified 50-cell B_CONV threshold. Gene-level inference used TMM normalization, filterByExpr, robust edgeR quasi-likelihood models and within-contrast Benjamini-Hochberg correction; the four prespecified programs were tested separately from TMM log-counts-per-million values with HC3 uncertainty.

The IFN/ISG program was substantially higher in the primary SLE contrast (effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6). The effect remained positive at 20- and 100-cell support thresholds, after excluding residual-doublet-risk calls, and in all 89 leave-one-sample-out fits. Gene-level support was coherent: all ten tested positive-arm genes had the expected direction, competitive enrichment was approximately q=2 x 10^-6, and leading signals included USP18, IFI44L, EPSTI1, IFIT3, MX1, IFI6, OAS2, ISG15 and STAT1.

The same program was higher in the full internal GSE174188 validation contrast (effect 0.856; q=0.00462) and in the prespecified donor-nonoverlap subset (effect 1.086; q=3.61 x 10^-4). Because both analyses originate from the same accession, they are internal replication rather than independent validation.

Other prespecified programs were less consistent. The naive-to-memory axis was lower in the primary SLE contrast (effect -0.541; q=0.0213) and APC/HLA was higher (effect 0.268; q=0.0213), but neither retained multiplicity-supported internal validation. The atypical/low-naive program was null in the primary contrast (effect -0.057; q=0.748). These results leave IFN/ISG as the only program with consistent support across the prespecified discovery and internal robustness sequence.

### Independent GSE135779 replicates IFN/ISG despite low genome-wide concordance

GSE135779 source matrices, metadata and program-gene availability were qualified before disease effects were estimated. The external identity scope was intentionally limited to a broad conventional-B analog assembled from source B-cell labels; hard naive/memory identities were not transferred. Statistical-engine behavior was qualified with count-conservation checks and synthetic null and signal data before the real disease contrasts were evaluated.

The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 mapped cells per donor. The frozen IFN/ISG program was higher in SLE (effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined childhood-adult analysis included 54 donors (16 controls and 38 SLE) and produced a similar estimate (effect 0.996, 95% confidence interval 0.655-1.337; q=1.31 x 10^-6). For the combined analysis, minimum-support sensitivities remained positive at 20 cells (effect 0.965; q=6.75 x 10^-7) and 100 cells (effect 0.939; q=4.06 x 10^-6).

The adult-only estimate was also positive (effect 0.968) but imprecise (95% confidence interval -0.123 to 2.060; q=0.291) because only five controls and six SLE donors were available. It is therefore directionally compatible rather than confirmatory. Across 43 childhood donor-deletion fits, IFN/ISG effects ranged from 0.987 to 1.094. Omitting each of the eight contributing source B-cell labels retained the same 43 donors and yielded effects from 1.019 to 1.051, arguing against dependence on any single contributing source label.

The IFN signal was also distinguishable from several alternative program-level explanations. In the childhood contrast, platelet/ambient, ASC/UPR and pan-B control effects were 0.049, 0.221 and -0.232, respectively, compared with 1.042 for IFN/ISG. All 12 available frozen IFN-arm genes were positive, ranked enrichment had a camera FDR of 1.85 x 10^-7, and all ten IFN genes jointly tested in the primary GSE174188 and childhood GSE135779 analyses were positive in both datasets.

Gene-level concordance was weak across the shared tested gene set. Among 4,410 shared tested genes, the cross-dataset effect correlation was only Spearman rho=0.026. The external evidence therefore supports replication of a prespecified IFN program but does not establish a globally shared SLE transcriptomic state. Consistent with that distinction, the GSE135779 atypical/low-naive score was positive (effect 1.191; q=5.10 x 10^-4) although the corresponding GSE174188 result was null; it is an external-only observation rather than a replication result. Conversely, the GSE174188 naive-to-memory and APC/HLA signals were null externally.

### Corrected external remapping does not satisfy the prespecified calibration criterion

The corrected source-label-independent mapping sensitivity processed all 56 GSE135779 matrices (363,083 cells), retained 353,527 cells after quality control and selected 36,630 B-lineage candidates without parsing source cell labels or disease fields. No elastic-net confidence candidate satisfied all prespecified calibration requirements. At the diagnostic threshold of 0.95, 94.20% of reference cells were retained, with B_CONV precision of 99.64% but B_ASC precision of 88.52%, below the required 90%. Although the centroid mapper met its precision and coverage criteria, it was not permitted to replace the required elastic-net mapper after inspection of the results. Corrected external disease outcomes were therefore not estimated (Supplementary Table S9 and Fig. S10). This failed calibration leaves the independent primary replication source-label-defined: it neither negates the IFN association nor establishes source-label-independent replication.

### Convergent regulatory and response evidence remains observational

We next asked whether the replicated transcriptional program was accompanied by a coherent regulatory pattern. The prespecified analysis included STAT1, STAT2, IRF7 and IRF9 as IFN-centred regulators, E2F1, FOXM1, MYC and MYBL2 as proliferation specificity comparators, and the three confirmatory contrasts described above. Signed CollecTRI target activity was evaluated in one global Benjamini-Hochberg family of 24 tests.

STAT1 and STAT2 activity estimates were positive and globally significant in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. At least three of the four IFN-centred regulators were positive in every contrast, with no globally significant opposite-direction IFN regulator. The proliferation specificity comparators did not reproduce a positive globally significant pattern across all three contrasts. Every leave-one-target estimate for the core STAT1 and STAT2 models remained positive, and all core models were positive in 100 deterministic 80%-target resamples, arguing against dependence on a single target or small target subset.

Correlation-aware testing preserved the overall direction while exposing one explicit exception. Matched-target counts were reproduced for all six core tests (STAT1: 98, 129 and 161; STAT2: 14, 19 and 20). CAMERA was positive in all six tests and Benjamini-Hochberg significant in five; discovery STAT2 was the exception (inter-gene correlation 0.1225; CAMERA q=0.1355). FRY remained positive and significant for that contrast (q=4.91 x 10^-5) and was positive and Benjamini-Hochberg significant in all six core tests. The regulator result is therefore cross-contrast concordance with a defined CAMERA limitation, not universal significance across methods.

Overlap-depletion analyses further constrained interpretation. After removal of the 12 frozen IFN/ISG positive-arm genes, all six ULM estimates retained positive 95% confidence intervals and six-test q<0.05; CAMERA remained positive in six of six and significant in five, while FRY remained positive and significant in all six. At least 78.6% of matched targets remained, and the minimum ULM slope retained 53.5% of baseline. Removing all M5911 genes produced stronger attenuation: all 18 method-level directions remained positive, but ULM passed correction in five of six tests, CAMERA in two of six and FRY in five of six. Discovery STAT2 retained only 8 of 14 targets and had a ULM slope of 0.391 (95% confidence interval -0.745 to 1.526; q=0.500), CAMERA q=0.623 and FRY q=0.099. All 11 depleted models eligible for leave-one-target analysis preserved direction. The STAT1/STAT2 signal is therefore not reducible to the 12 core program genes, but it remains partly coupled to the broader interferon-response transcriptome.

Two additional analyses provided response-level context rather than causal proof. The MSigDB Hallmark interferon-alpha response set M5911 was positively enriched in all three ranked contrasts (normalized enrichment scores 3.187, 3.050 and 3.527; 10,000 gene-label permutations per contrast). In GSE23307 primary B cells exposed ex vivo to IFN-beta, all 12 genes in the frozen positive arm increased in each of two healthy donors, with mean paired log2(x+1) effects of 3.294 and 3.666. No inferential P value was calculated at n=2.

Taken together, these layers support an IFN-centred interpretation of the replicated program while defining its evidential ceiling. CollecTRI activity is inferred from observational disease-ranked statistics, M5911 is a response signature, and GSE23307 is a small healthy-donor perturbation. None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE.

## Discussion

The central finding of this study is not a new B-cell taxonomy but a difference in reproducibility across biological layers. Fine-grained B-cell state assignments did not satisfy the prespecified stability criteria, and even the broad B_CONV/B_ASC partition failed one state-specific end-to-end criterion because B_ASC membership was less reproducible than the global partition metrics suggested. Retaining that failure changed the interpretation of the study: B_CONV/B_ASC is used as an analysis scaffold, not as a transferable taxonomy. Within that bounded scaffold, assignment uncertainty did not alter the primary B_ASC composition null or the positive B_CONV IFN/ISG effects. The supported result is a process-level interferon association within these inferential limits; neither a disease-defining cell-state label nor generalized B_ASC expansion was established.

This hierarchy helps reconcile the present results with established SLE B-cell biology. Interferon activation, plasmablast expansion and activated B-cell phenotypes have all been reported previously, but their prominence varies with disease activity, molecular endotype and treatment context [3,4,8-12]. The higher plasmablast-to-memory ratio reported in patients with greater activity and Sm/RNP autoantibodies [10], for example, is compatible with our secondary positive flare estimate and does not conflict with the null primary comparison in the source-defined managed-SLE group. Likewise, functional studies showing that several interferon classes can promote B-cell activation or plasma-cell differentiation [14-16] support biological plausibility without implying that a particular ligand or fine cell state explains the present observational association. The contribution here is therefore not the rediscovery of interferon involvement, but the identification of an inferential level at which that involvement remains reproducible across heterogeneous datasets.

The independent GSE135779 analysis strengthens that process-level interpretation while also defining its limits. The childhood cohort reproduced the frozen IFN/ISG program, donor-deletion and source-label-omission analyses retained the direction, and all ten jointly tested IFN genes were positive in both primary datasets. Yet the genome-wide effect correlation was only rho=0.026. These observations are not contradictory: a transcriptome-wide correlation asks whether thousands of gene effects agree across cohorts that differ in age structure, source annotation, processing, covariates and gene universe, whereas the program analysis asks whether a prespecified coherent biological response retains direction and statistical support. The data support the latter but do not establish the stronger claim of a globally shared disease transcriptome. Importantly, a corrected attempt to reconstruct the external mapping without source labels failed its prespecified B_ASC calibration criterion, and no corrected disease outcome was estimated. Independent replication therefore remains tied to the prespecified source-label-defined broad B-cell analog rather than demonstrating de novo taxonomy transfer.

The regulatory analyses add a second layer of convergence but do not change the evidence class of the study. STAT1 and STAT2 were positive across the three confirmatory contrasts in the prespecified ULM family, and leave-one-target and target-resampling diagnostics argued against a single-target artefact. CAMERA and FRY retained the overall direction while making the limitation of discovery STAT2 explicit. The overlap-depletion results further sharpen that interpretation: removing the 12 core IFN genes did not abolish the regulatory signal, but broader M5911 depletion materially weakened discovery STAT2. Thus, the observed regulatory pattern is not merely a restatement of the 12-gene program, yet it remains partly embedded in the broader interferon-response transcriptome. M5911 enrichment and the two-donor GSE23307 perturbation provide orthogonal response context, not independent proof of in vivo regulation. Collectively, these analyses justify an IFN-centred regulatory interpretation but not direct binding, a unique ligand or causal initiation by STAT1/STAT2.

The analysis also narrows several tempting but unsupported narratives. The naive-to-memory and APC/HLA programs provide internal context but do not independently reproduce in GSE135779. The external atypical/low-naive signal cannot be called replication because the corresponding GSE174188 result was null. High global concordance of the broad B_CONV scaffold does not establish a discrete IFN-high subtype, and the primary composition null should not be displaced by the secondary flare contrast. These negative and non-generalizing results are consequential: they prevent a heterogeneous set of secondary signals from being promoted to co-equal disease features and keep the manuscript centred on the program supported in the prespecified discovery, internal and source-label-defined external analyses.

The present results have a plausible but still prospective translational implication. A continuous B_CONV IFN/ISG score could be more portable than a hard cell-state label in settings where cohort composition and annotation differ, and it could eventually contribute to molecular stratification or pharmacodynamic monitoring. The current data do not establish a predictive biomarker, a treatment-selection rule, a clinical cutoff or patient benefit. Those questions require prospective treatment-annotated cohorts, longitudinal sampling, assay calibration and prespecified evaluation of discrimination, calibration and clinical utility. A decisive next step would be to test whether the within-B_CONV IFN program predicts longitudinal activity or response to interferon-pathway therapy independently of B-cell composition and conventional clinical covariates.

Several limitations define the remaining evidence gap. Public metadata did not provide a common set of sex, treatment and detailed clinical covariates across all contrasts. End-to-end resampling failed the B_ASC overlap criterion, and propagation of observed assignment exchanges remains a same-data sensitivity rather than proof of taxonomy transfer. The adult external stratum was small, two adult metadata donors lacked corresponding source matrices, and the GSE174188 internal validation remains accession-internal despite removal of donor overlap. External replication relies on source labels to define a broad conventional-B analog; after correcting a normalization mismatch, the source-label-independent remapping sensitivity failed its B_ASC reference-calibration criterion and therefore did not estimate a corrected disease effect. CollecTRI results depend on curated prior knowledge and gene coverage, correlation-aware and overlap-depletion analyses reuse the same disease contrasts, and discovery STAT2 remains the explicit CAMERA exception. The GSE23307 perturbation comprises only two healthy donors. These constraints leave direct binding, matched patient perturbation, prospective clinical validation and transferable state taxonomy unresolved.

Taken together, the study supports a restrained model of SLE B-cell remodeling: the prespecified IFN/ISG association was reproduced across these cohorts, whereas the tested hard state policies had defined stability and transfer limits. These are distinct assessments, not a common-scale comparison of reproducibility. Retaining failed stability and calibration criteria limits the scope of the replicated process-level association and keeps mechanistic and clinical claims within the available evidence.

## Conclusions

SLE is associated with an IFN/ISG transcriptional shift supported in disease-blind GSE174188 B_CONV analyses and independently replicated in a source-label-defined GSE135779 conventional-B analog. The tested state assignments retained stability limits, and corrected source-label-independent mapping failed calibration without estimating a disease effect. Same-data uncertainty propagation and qualified regulatory and response analyses support this bounded process-level interpretation; they do not establish a universal taxonomy, generalized B_ASC expansion, causal regulator, unique upstream stimulus or clinical utility.

## List of abbreviations

ASC: antibody-secreting cell; CAMERA: correlation-adjusted mean-rank gene-set test; B_ASC: disease-blind antibody-secreting-cell compartment; B_CONV: disease-blind broad conventional-B compartment; FDR: false discovery rate; FRY: fast rotation gene-set test; GEO: Gene Expression Omnibus; HC1/HC3: heteroskedasticity-consistent covariance estimators; IFN: interferon; ISG: interferon-stimulated gene; NES: normalized enrichment score; SLE: systemic lupus erythematosus; TF: transcription factor; TMM: trimmed mean of M values; UMI: unique molecular identifier.

## Declarations

### Ethics approval and consent to participate

This secondary study used only publicly available, de-identified human transcriptomic datasets and involved no participant recruitment, intervention or collection of new specimens. No additional ethics approval was required for this secondary analysis. Ethics approval and consent procedures for the source studies are reported in the original publications [1,2,19].

### Consent for publication

Not applicable; the manuscript contains no identifiable individual participant information.

### Availability of data and materials

The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [17,18,20]. The project repository is https://github.com/1209433622cz-maker/sle-bcell-remodeling; an initial immutable snapshot is archived at doi:10.5281/zenodo.22086892 [32]. That snapshot predates the end-to-end reconstruction and corrected external-mapping audits. A matching version-specific archive of the revised code, decisions, source data and SHA-256 records is required before submission. Original project code is licensed under the MIT License; original manuscript text, composite figures, project documentation and project-generated derived source-data tables are licensed under CC BY 4.0. These licences do not relicense GEO, CELLxGENE or other third-party source material. Large recomputable matrices are not duplicated from their source repositories.

### Competing interests

The authors declare that they have no competing interests.

### Funding

This research received no specific funding.

### Authors' contributions

ZC: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft. TQ: Conceptualization, Methodology, Project administration, Validation, Writing - review and editing. Both authors approved the preceding reviewed snapshot. Final approval of these exact refined manuscript files is pending.

### Acknowledgements

Not applicable.

### Use of generative artificial intelligence

Generative artificial intelligence tools, including OpenAI Codex and ChatGPT, were used to assist with code development, reproducibility checks, language editing and preparation of submission materials. The authors are responsible for verifying the revised analyses, code, text, references, figures and source data before submission and retain full responsibility for the work. Generative artificial intelligence was not used to create or alter primary research data.

## Additional files

Additional file 1 (.docx): Supplementary information. Extended evidence-boundary and reproducibility tables supporting the disease-blind reconstruction, sample-level composition, pseudobulk replication and regulatory analyses.

Additional file 2 (.zip): Figure source data. Machine-readable CSV files underlying Figures 1-5 and Supplementary Figures S1-S10, with a SHA-256 manifest.

Additional file 3 (.zip): Regulator sensitivity. Baseline correlation-aware STAT1/STAT2 tests, post-freeze IFN-overlap-depletion results, leave-one-target diagnostics, Figure S8 Source Data, qualified decision records and a SHA-256 manifest.

Additional file 4 (.zip): Full statistical results. Complete gene-level results for 12 frozen model branches, composition and program tables, regulator and orthogonal results, end-to-end identity robustness and boundary-propagation outputs, corrected external-mapping calibration diagnostics, sanitized design matrices, the statistical-family map and SHA-256 provenance manifests. The calibration extension contains no corrected external disease-effect estimates.

## Figure legends

### Figure 1 | Disease-blind reconstruction defines the permissible identity scope

a, Study design and evidence hierarchy. GSE174188 B-lineage cells passed hard quality control before construction of a disease-blind B_CONV/B_ASC analysis scaffold and separation into B_ASC composition and B_CONV pseudobulk/program analyses. GSE174188 internal validation and GSE135779 independent replication are displayed in parallel, followed by three interpretation-only evidence classes. b, Median mapped adjusted Rand index and minimum-to-median interval for each candidate identity policy across 20 within-library resamples of the frozen 50-dimensional Harmony representation; policies are discrete alternatives and are not connected as a trajectory. The short dashed segment applies only to the two-compartment minimum-ARI criterion of 0.90. c, Mapped adjusted Rand index and mapping agreement in each frozen-representation two-compartment graph resample; the dashed horizontal guide marks the minimum mapping-agreement criterion of 0.990. d, Minimum and median state Jaccard indices from the same frozen-representation analysis for B_CONV and B_ASC, with antibody-secreting marker support; the dashed vertical guide marks the minimum state-median Jaccard criterion of 0.95. Panels b-d do not recompute highly variable genes, principal components or Harmony; the end-to-end sensitivity is reported in Supplementary Fig. S9. Cell-level summaries define assignment stability and are not disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

a, Observed B_ASC fractions for exactly 43 control and 47 managed-SLE sample-cohort strata in the primary composition contrast; diamonds and bars show adjusted fractions and 95% confidence intervals. b, Primary, internal, donor-nonoverlap and secondary flare conditional odds ratios. c, Frozen primary estimate and mandatory minimum-cell, explicit non-B and residual-doublet sensitivities. d, Conditional odds ratios after each of 90 primary sample deletions; the horizontal line is the full estimate. The flare contrast is secondary and did not pass the frozen three-contrast false-discovery-rate rule.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

a, Effects and 95% confidence intervals for the four frozen programs in the primary contrast. b, IFN/ISG estimates across primary support thresholds, residual-risk restriction, internal replication, donor-nonoverlap internal replication and the secondary flare contrast. c, Gene-level log2 fold changes for the frozen IFN positive arm in the primary and donor-nonoverlap contrasts. A dagger marks genes not tested at gene level in either contrast; a double dagger marks genes not tested in the primary contrast. Filtered values are absent rather than zero or imputed. d, IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity families in the primary and donor-nonoverlap contrasts. Program intervals use HC3 uncertainty; confirmatory q values use the frozen four-program family.

### Figure 4 | GSE135779 independently replicates the frozen IFN/ISG program

a, Standardized IFN/ISG effects for childhood, combined, adult and support-threshold external analyses. b, Standardized discovery and internal GSE174188 effects beside independent GSE135779 effects. c, Effects for 4,410 genes tested in both primary datasets, with ten jointly tested frozen IFN genes highlighted; all ten were positive in both datasets despite Spearman rho=0.026 genome-wide. d, Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Sequential display labels 1-8 correspond to the original source codes retained in Figure 4 Source Data. Donors are the biological units in GSE135779; the adult estimate is directional only.

### Figure 5 | Convergent observational evidence supports IFN-centred regulation

a, Three parallel interpretation branches for the replicated IFN/ISG program: same-data regulator robustness, curated M5911 response-set concordance and separate GSE23307 perturbational context. Equal branch weight does not imply causal ordering; the bottom boundary states that no causal regulator or unique upstream ligand is established. b, Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. c, Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation specificity comparators. Asterisks indicate global 24-test q<0.05. d, M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. e, Mean paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells from two healthy donors; labels show positive genes. The GSE23307 panel is descriptive at n=2 and carries no inferential P value.

## References

1. Perez RK, Gordon MG, Subramaniam M, Kim MC, Hartoularos GC, Targ S, et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. Science. 2022;376(6589):eabf1970. doi:10.1126/science.abf1970.

2. Nehar-Belaid D, Hong S, Marches R, Chen G, Bolisetty M, Baisch J, et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. Nature Immunology. 2020;21(9):1094-1106. doi:10.1038/s41590-020-0743-0.

3. Jenks SA, Cashman KS, Zumaquero E, Marigorta UM, Patel AV, Wang X, et al. Distinct Effector B Cells Induced by Unregulated Toll-like Receptor 7 Contribute to Pathogenic Responses in Systemic Lupus Erythematosus. Immunity. 2018;49(4):725-739.e6. doi:10.1016/j.immuni.2018.08.015.

4. Szelinski F, Stefanski AL, Schrezenmeier E, Rincon-Arevalo H, Wiedemann A, Reiter K, et al. Plasmablast-like Phenotype Among Antigen-Experienced CXCR5 - CD19 low B Cells in Systemic Lupus Erythematosus. Arthritis & Rheumatology. 2022;74(9):1556-1568. doi:10.1002/art.42157.

5. Crowell HL, Soneson C, Germain PL, Calini D, Collin L, Raposo C, et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. Nature Communications. 2020;11(1):6077. doi:10.1038/s41467-020-19894-4.

6. Squair JW, Gautier M, Kathe C, Anderson MA, James ND, Hutson TH, et al. Confronting false discoveries in single-cell differential expression. Nature Communications. 2021;12(1):5692. doi:10.1038/s41467-021-25960-2.

7. Büttner M, Ostner J, Müller CL, Theis FJ, Schubert B. scCODA is a Bayesian model for compositional single-cell data analysis. Nature Communications. 2021;12(1):6876. doi:10.1038/s41467-021-27150-6.

8. Banchereau R, Hong S, Cantarel B, Baldwin N, Baisch J, Edens M, et al. Personalized Immunomonitoring Uncovers Molecular Networks that Stratify Lupus Patients. Cell. 2016;165(3):551-565. doi:10.1016/j.cell.2016.03.008.

9. Chiche L, Jourde-Chiche N, Whalen E, Presnell S, Gersuk V, Dang K, et al. Modular Transcriptional Repertoire Analyses of Adults With Systemic Lupus Erythematosus Reveal Distinct Type I and Type II Interferon Signatures. Arthritis & Rheumatology. 2014;66(6):1583-1595. doi:10.1002/art.38628.

10. van Dooren HJ, Atisha-Fregoso Y, Dorjée AL, Huizinga TWJ, Mackay M, Aranow C, et al. Interferon signatures fuel B cell hyperactivity and plasmablast expansion in systemic lupus erythematosus. Journal of Autoimmunity. 2025;154:103438. doi:10.1016/j.jaut.2025.103438.

11. Hubbard EL, Bachali P, Kingsmore KM, He Y, Catalina MD, Grammer AC, et al. Analysis of transcriptomic features reveals molecular endotypes of SLE with clinical implications. Genome Medicine. 2023;15(1):84. doi:10.1186/s13073-023-01237-9.

12. Sayadi A, Eloranta M-L, Oparina N, Wallgren M, Skoglund E, Frodlund M, et al. Single-cell RNA-seq reveals a persistent interferon signature in immune cells from systemic lupus erythematosus patients with high versus low polygenic risk scores despite antimalarial treatment. Journal of Autoimmunity. 2026;161:103575. doi:10.1016/j.jaut.2026.103575.

13. Arazi A, Rao DA, Berthier CC, Davidson A, Liu Y, Hoover PJ, et al. The immune cell landscape in kidneys of patients with lupus nephritis. Nature Immunology. 2019;20(7):902-914. doi:10.1038/s41590-019-0398-x.

14. Akita K, Yasaka K, Shirai T, Ishii T, Harigae H, Fujii H. Interferon alpha Enhances B Cell Activation Associated With FOXM1 Induction: Potential Novel Therapeutic Strategy for Targeting the Plasmablasts of Systemic Lupus Erythematosus. Frontiers in Immunology. 2021;11:498703. doi:10.3389/fimmu.2020.498703.

15. Barnas JL, Albrecht J, Meednu N, Alzamareh DF, Baker C, McDavid A, et al. B Cell Activation and Plasma Cell Differentiation Are Promoted by IFN-lambda in Systemic Lupus Erythematosus. The Journal of Immunology. 2021;207(11):2660-2672. doi:10.4049/jimmunol.2100339.

16. Faheem Z, Boukhaled GM, Nassar C, Manion K, Kim M, Bonilla D, et al. Type I interferons enhance B cell activation and promote differentiation of double negative 2 cells in SLE. Lupus Science & Medicine. 2026;13(1):e002042. doi:10.1136/lupus-2026-002042.

17. National Center for Biotechnology Information. Gene Expression Omnibus series GSE174188. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188. Accessed 21 Aug 2026.

18. National Center for Biotechnology Information. Gene Expression Omnibus series GSE135779. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779. Accessed 21 Aug 2026.

19. van Boxel-Dezaire AHH, Zula JA, Xu Y, Ransohoff RM, Jacobberger JW, Stark GR. Major Differences in the Responses of Primary Human Leukocyte Subsets to IFN-beta. The Journal of Immunology. 2010;185(10):5888-5899. doi:10.4049/jimmunol.0902314.

20. National Center for Biotechnology Information. Gene Expression Omnibus series GSE23307. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE23307. Accessed 21 Aug 2026.

21. Wolf FA, Angerer P, Theis FJ. SCANPY: large-scale single-cell gene expression data analysis. Genome Biology. 2018;19(1):15. doi:10.1186/s13059-017-1382-0.

22. Korsunsky I, Millard N, Fan J, Slowikowski K, Zhang F, Wei K, et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nature Methods. 2019;16(12):1289-1296. doi:10.1038/s41592-019-0619-0.

23. Traag VA, Waltman L, van Eck NJ. From Louvain to Leiden: guaranteeing well-connected communities. Scientific Reports. 2019;9(1):5233. doi:10.1038/s41598-019-41695-z.

24. Robinson MD, McCarthy DJ, Smyth GK. edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. Bioinformatics. 2010;26(1):139-140. doi:10.1093/bioinformatics/btp616.

25. Badia-i-Mompel P, Vélez Santiago J, Braunger J, Geiss C, Dimitrov D, Müller-Dott S, et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. Bioinformatics Advances. 2022;2(1):vbac016. doi:10.1093/bioadv/vbac016.

26. Müller-Dott S, Tsirvouli E, Vazquez M, Ramirez Flores RO, Badia-i-Mompel P, Fallegger R, et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. Nucleic Acids Research. 2023;51(20):10934-10949. doi:10.1093/nar/gkad841.

27. Ritchie ME, Phipson B, Wu D, Hu Y, Law CW, Shi W, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Research. 2015;43(7):e47-e47. doi:10.1093/nar/gkv007.

28. Law CW, Chen Y, Shi W, Smyth GK. voom: precision weights unlock linear model analysis tools for RNA-seq read counts. Genome Biology. 2014;15(2):R29. doi:10.1186/gb-2014-15-2-r29.

29. Wu D, Smyth GK. Camera: a competitive gene set test accounting for inter-gene correlation. Nucleic Acids Research. 2012;40(17):e133-e133. doi:10.1093/nar/gks461.

30. Wu D, Lim E, Vaillant F, Asselin-Labat ML, Visvader JE, Smyth GK. ROAST: rotation gene set tests for complex microarray experiments. Bioinformatics. 2010;26(17):2176-2182. doi:10.1093/bioinformatics/btq401.

31. Liberzon A, Birger C, Thorvaldsdóttir H, Ghandi M, Mesirov JP, Tamayo P. The Molecular Signatures Database Hallmark Gene Set Collection. Cell Systems. 2015;1(6):417-425. doi:10.1016/j.cels.2015.12.004.

32. Chen Z, Qi T. SLE B-cell remodeling analysis: code, source data and reproducible release. Zenodo. 2026. doi:10.5281/zenodo.22086892.
