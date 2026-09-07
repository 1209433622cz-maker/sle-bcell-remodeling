# Disease-blind reconstruction distinguishes reproducible interferon remodeling from less stable B-cell state assignments in systemic lupus erythematosus

Article type: Article

Authors: Zhi Chen [1] and Teng Qi [1,*]

Affiliation 1: School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen 518172, China

Corresponding author: Teng Qi, School of Medicine, The Chinese University of Hong Kong, Shenzhen, MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China; tengqi@link.cuhk.edu.cn

ORCID identifiers: Zhi Chen, https://orcid.org/0009-0001-0072-5576; Teng Qi, https://orcid.org/0009-0007-7648-4776

Author emails: Zhi Chen, zhichen1@link.cuhk.edu.cn; Teng Qi, tengqi@link.cuhk.edu.cn

Running title: Reproducible IFN remodeling in SLE B cells

## Abstract

Single-cell disease studies can conflate cell identity, abundance and transcription when unstable annotations are treated as fixed biological states. We reanalysed public systemic lupus erythematosus datasets using disease-blind B-lineage reconstruction and biological-unit-aware inference. Among 150,402 discovery B-lineage cells, end-to-end resampling failed a prespecified antibody-secreting-cell overlap criterion, restricting broad B-cell compartments to an analysis scaffold; propagating observed assignment exchanges did not change the primary composition interpretation or the positive conventional-B IFN/ISG effect. The IFN/ISG program replicated in independent GSE135779 childhood donors using a source-label-defined broad B-cell analogue despite weak genome-wide concordance. Corrected source-label-independent remapping failed prespecified calibration, so no corrected external disease effect was estimated. STAT1/STAT2 analyses provided convergent but observational support and weakened after broader interferon-gene depletion. Thus, reproducibility was stronger for a process-level interferon program than for hard state assignments, without establishing a universal taxonomy, causal regulator or clinical utility.

## Introduction

Single-cell profiling has sharpened the cellular resolution of SLE, but it also creates a basic inferential problem: disease effects can be attached to a cell-state label before the stability of that label, the relevant biological replicate and the cohort structure have been established. Peripheral-blood studies have described naive, memory, double-negative, CD11c-positive and antibody-secreting B-cell populations together with prominent interferon responses [1-4]. Yet cell-level tests can inflate precision when donors rather than cells are the experimental units [5,6], and compositional changes are intrinsically coupled because expansion of one compartment alters the observed fractions of the others [7]. The biological interpretation of a single-cell disease signal therefore depends on both the molecular effect and the inferential layer at which it is claimed.

This distinction is especially important in SLE because interferon activity and plasmablast biology are well established yet strongly context dependent. Longitudinal paediatric immunomonitoring linked plasmablast signatures to disease activity [8], modular adult studies resolved heterogeneous interferon activation thresholds [9], and deep phenotyping identified a higher-activity subgroup with an increased plasmablast-to-memory ratio and Sm/RNP autoantibodies [10]. Large transcriptomic studies likewise support multiple molecular endotypes rather than a single uniform SLE state [11]. More recent single-cell data show persistent interferon activity even during low disease activity and antimalarial treatment, with additional variation by polygenic-risk burden [12]. Tissue single-cell studies extend this heterogeneity to inflamed renal immune niches [13], while experimental studies support the capacity of several interferon classes to promote B-cell activation or plasma-cell differentiation [14-16]. Together, these observations argue against treating either B-cell abundance or an interferon-responsive state as context-free disease features.

A remaining question is therefore not whether interferon is involved in SLE, but which layer of B-cell remodeling remains reproducible after identity formation is separated from disease labels and inference is anchored to biological samples or donors. Public SLE datasets make this question non-trivial: samples are distributed across processing cohorts, some donors recur across samples or cohorts, clinical covariates are incomplete, and external datasets provide different annotation schemes and gene universes. Under these conditions, outcome-informed clustering or pooled cell-level tests can blur technical structure, composition and within-cell-state transcription.

We addressed this problem with a staged secondary analysis in which source integrity, metadata hierarchy and disease-by-cohort support were evaluated before disease effects were estimated. B-lineage identity was reconstructed while disease fields were protected, fine-grained and broad identity policies were explicitly stress-tested, and only the retained disease-blind scaffold was carried into sample-level composition and raw-count pseudobulk analyses. The central transcriptional result was then tested in the independent GSE135779 cohort using a source-label-defined broad B-cell analogue and challenged by identity-uncertainty propagation, cross-dataset gene-level comparison and prespecified regulatory and response-based analyses. This design tests an evidence hierarchy: which B-cell features survive increasingly stringent reconstruction and replication tests, and which remain cohort-specific, representation-dependent or mechanistically unproven (Supplementary Tables S1 and S2).

## Results

### Disease-blind reconstruction supports a scaffold with state-specific stability limits

The GSE174188 B-lineage source matrix contained 152,981 cells and 30,172 genes. Prespecified hard-quality-control rules retained 150,402 cells, representing 259 donors, 271 biological samples, 88 technical libraries and four processing cohorts. Repeated donors and samples spanning processing cohorts were explicitly resolved in the metadata hierarchy. Because disease-by-cohort support was uneven, the full disease-blind cell set was available for identity reconstruction, whereas disease effects were restricted to prespecified contrasts with common support (Supplementary Fig. S1).

Complete-library doublet diagnostics, recurrent highly variable gene selection, unintegrated and Harmony representations, bridge-sample checks and marker coverage were evaluated before disease fields were joined (Supplementary Fig. S2). The initial five-state identity solution failed the prespecified resampling criteria and was retained as a negative result rather than relabelled as a successful subtype analysis. Transition reconstruction instead supported a two-compartment B_CONV/B_ASC model, with naive-memory structure represented as a continuous program within B_CONV and platelet-associated expression retained as a technical overlay (Supplementary Fig. S3).

Within the frozen 50-dimensional Harmony representation, the broad partition passed all five criteria across 20 graph resamples: the minimum mapped adjusted Rand index was 0.990, the minimum mapping agreement was 0.9998 and the minimum state-median Jaccard was 0.991. B_ASC marker support was complete for DERL3, JCHAIN, MZB1, TNFRSF17 and XBP1. These results justified the broad partition for the prespecified disease analyses, but they did not address uncertainty introduced by rebuilding the representation itself (Fig. 1a-c).

The end-to-end sensitivity provided that stricter test. All 20 replicates completed and all 20 Harmony runs converged. Global concordance remained high: median and minimum mapped adjusted Rand indices were 0.963 and 0.930, and median and minimum mapping agreements were 0.99937 and 0.99877. The minimum state-median Jaccard was 0.930, however, below the unchanged 0.95 criterion, so the prespecified end-to-end reproducibility requirement was not met. The failure was confined to B_ASC (median Jaccard 0.930; minimum 0.872), whereas B_CONV remained highly concordant (median 0.99936; minimum 0.99876; Fig. 1d; Supplementary Fig. S4). A median of 76 of 120,320 sampled cells exchanged broad-state assignment per replicate.

Propagating these observed exchanges did not alter the disease-level conclusions. Across the 20 perturbed partitions, primary composition odds ratios ranged from 0.896 to 0.967 and every confidence interval included one. The primary B_CONV IFN/ISG effect ranged from 0.836 to 0.845, and the donor-nonoverlap effect from 1.059 to 1.087; all 40 estimates remained positive with confidence intervals above zero. Thus, the end-to-end sensitivity preserved the frozen disease effects while preventing a stronger taxonomy-level interpretation. We therefore use B_CONV/B_ASC as a disease-blind analysis scaffold rather than a universally reproducible cell taxonomy.

### The primary B_ASC abundance contrast lacks statistical support

After the broad scaffold was fixed, outcomes were joined and composition was analysed at the sample-cohort level, with at least 50 eligible B cells per stratum and no cell-level disease test. In the primary processing-cohort-4 comparison, B_ASC relative abundance showed no statistically supported difference between source-defined managed SLE and controls: the conditional odds ratio was 0.947 (95% confidence interval 0.636-1.410; P=0.787), with adjusted fractions of 1.61% in controls and 1.52% in source-defined managed SLE. The interval does not establish equivalent abundance or exclude an increase. The HC1 sandwich analysis was concordant (95% confidence interval 0.651-1.376; P=0.774), and none of the 90 leave-one-sample-out fits generated evidence that reversed the primary interpretation (Fig. 2a-d; Supplementary Fig. S5).

Internal analyses did not convert this null result into a general composition claim. The internal replication estimate remained below one (odds ratio 0.772), as did the explicit donor-nonoverlap estimate (odds ratio 0.591; n=53). A secondary flare contrast was positive (odds ratio 2.303; nominal P=0.0282) but did not survive the prespecified three-contrast correction (q=0.0845). B_ASC abundance therefore provides contextual heterogeneity and an explicit negative boundary; it is not the central disease signal in this analysis.

### IFN/ISG is the most consistently supported of the four prespecified B_CONV programs

The transcriptional analysis retained 89 primary B_CONV pseudobulks, comprising 43 control and 46 source-defined managed-SLE strata and 59,873,385 UMI counts. The difference from the 90 composition strata arose because one source-defined managed-SLE stratum contained 44 B_CONV cells after compartment assignment and did not meet the prespecified 50-cell B_CONV threshold. Gene-level inference used TMM normalization, filterByExpr, robust edgeR quasi-likelihood models and within-contrast Benjamini-Hochberg correction; the four prespecified programs were tested separately from TMM log-counts-per-million values with HC3 uncertainty.

The IFN/ISG program was substantially higher in the primary SLE contrast (effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6). The effect remained positive at 20- and 100-cell support thresholds, after excluding residual-doublet-risk calls, and in all 89 leave-one-sample-out fits. Gene-level support was coherent: all ten tested positive-arm genes had the expected direction, competitive enrichment was approximately q=2 x 10^-6, and leading signals included USP18, IFI44L, EPSTI1, IFIT3, MX1, IFI6, OAS2, ISG15 and STAT1 (Fig. 3a-c; Supplementary Fig. S6).

The same program was higher in the full internal GSE174188 replication contrast (effect 0.856; q=0.00462) and in the prespecified donor-nonoverlap subset (effect 1.086; q=3.61 x 10^-4). Because both analyses originate from the same accession, they provide internal replication rather than independent replication.

Other prespecified programs were less consistent. The naive-to-memory axis was lower in the primary SLE contrast (effect -0.541; q=0.0213) and APC/HLA was higher (effect 0.268; q=0.0213), but neither was multiplicity-supported in the internal replication analysis. The atypical/low-naive program was null in the primary contrast (effect -0.057; q=0.748). These results leave IFN/ISG as the only program with consistent support across the prespecified discovery and internal robustness sequence (Fig. 3d).

### Independent GSE135779 provides source-label-defined IFN/ISG replication despite low genome-wide concordance

GSE135779 source matrices, metadata and program-gene availability were checked before disease effects were estimated. The external identity scope was intentionally limited to a broad conventional-B analogue assembled from source B-cell labels; hard naive/memory identities were not transferred. Count conservation and synthetic null and signal datasets were used to verify the statistical implementation before the real disease contrasts were evaluated.

The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 eligible cells in the source-label-defined broad-B analogue per donor. The frozen IFN/ISG program was higher in SLE (effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined childhood-adult analysis included 54 donors (16 controls and 38 SLE) and produced a similar estimate (effect 0.996, 95% confidence interval 0.655-1.337; q=1.31 x 10^-6). For the combined analysis, minimum-support sensitivities remained positive at 20 cells (effect 0.965; q=6.75 x 10^-7) and 100 cells (effect 0.939; q=4.06 x 10^-6) (Fig. 4a,b; Supplementary Fig. S7).

The adult-only estimate was also positive (effect 0.968) but imprecise (95% confidence interval -0.123 to 2.060; q=0.291) because only five controls and six SLE donors were available. It is therefore directionally compatible rather than confirmatory. Across 43 childhood donor-deletion fits, IFN/ISG effects ranged from 0.987 to 1.094. Omitting each of the eight contributing source B-cell labels retained the same 43 donors and yielded effects from 1.019 to 1.051, arguing against dependence on any single contributing source label.

The IFN signal was also distinguishable from several alternative program-level explanations. In the childhood contrast, platelet/ambient, ASC/UPR and pan-B control effects were 0.049, 0.221 and -0.232, respectively, compared with 1.042 for IFN/ISG. All 12 available frozen IFN-arm genes were positive, ranked enrichment had a CAMERA FDR of 1.85 x 10^-7, and all ten IFN genes jointly tested in the primary GSE174188 and childhood GSE135779 analyses were positive in both datasets (Fig. 4c,d).

Gene-level concordance was weak across the shared tested gene set. Among 4,410 shared tested genes, the cross-dataset effect correlation was only Spearman rho=0.026. The external evidence therefore supports replication of a prespecified IFN program but does not establish a globally shared SLE transcriptomic state. Consistent with that distinction, the GSE135779 atypical/low-naive score was positive (effect 1.191; q=5.10 x 10^-4) although the corresponding GSE174188 result was null; it is an external-only observation rather than a replication result. Conversely, the GSE174188 naive-to-memory and APC/HLA signals were null externally.

### Corrected source-label-independent remapping does not satisfy the prespecified calibration criterion

The corrected source-label-independent mapping sensitivity processed all 56 GSE135779 matrices (363,083 cells), retained 353,527 cells after quality control and selected 36,630 B-lineage candidates without parsing source cell labels or disease fields. No elastic-net confidence candidate satisfied all prespecified calibration requirements. At the diagnostic threshold of 0.95, 94.20% of reference cells were retained, with B_CONV precision of 99.64% but B_ASC precision of 88.52%, below the required 90%. Although the centroid mapper met its precision and coverage criteria, it was not permitted to replace the required elastic-net mapper after inspection of the results. Corrected external disease outcomes were therefore not estimated (Supplementary Table S9 and Supplementary Fig. S8). This failed calibration leaves the independent primary replication source-label-defined: it neither negates the IFN association nor establishes source-label-independent replication.

### Convergent regulatory and response evidence remains observational

We next asked whether the replicated transcriptional program was accompanied by a coherent regulatory pattern. The prespecified analysis included STAT1, STAT2, IRF7 and IRF9 as IFN-centred regulators, E2F1, FOXM1, MYC and MYBL2 as proliferation specificity comparators, and the three confirmatory contrasts described above. Signed CollecTRI target activity was evaluated in one global Benjamini-Hochberg family of 24 tests.

STAT1 and STAT2 activity estimates were positive and globally significant in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. At least three of the four IFN-centred regulators were positive in every contrast, with no globally significant opposite-direction IFN regulator. The proliferation specificity comparators did not reproduce a positive globally significant pattern across all three contrasts (Fig. 5a-c). Every leave-one-target estimate for the core STAT1 and STAT2 models remained positive, and all core models were positive in 100 deterministic 80%-target resamples, arguing against dependence on a single target or small target subset.

Correlation-aware testing preserved the overall direction while exposing one explicit exception. Matched-target counts were reproduced for all six core tests (STAT1: 98, 129 and 161; STAT2: 14, 19 and 20). CAMERA was positive in all six tests and Benjamini-Hochberg significant in five; discovery STAT2 was the exception (inter-gene correlation 0.1225; CAMERA q=0.1355). FRY remained positive and significant for that contrast (q=4.91 x 10^-5) and was positive and Benjamini-Hochberg significant in all six core tests. The regulator result is therefore cross-contrast concordance with a defined CAMERA limitation, not universal significance across methods (Supplementary Fig. S9; Supplementary Table S4a).

Overlap-depletion analyses further constrained interpretation. After removal of the 12 frozen IFN/ISG positive-arm genes, all six ULM estimates retained positive 95% confidence intervals and six-test q<0.05; CAMERA remained positive in six of six and significant in five, while FRY remained positive and significant in all six. At least 78.6% of matched targets remained, and the minimum ULM slope retained 53.5% of baseline. Removing all M5911 genes produced stronger attenuation: all 18 method-level directions remained positive, but ULM passed correction in five of six tests, CAMERA in two of six and FRY in five of six. Discovery STAT2 retained only 8 of 14 targets and had a ULM slope of 0.391 (95% confidence interval -0.745 to 1.526; q=0.500), CAMERA q=0.623 and FRY q=0.099. All 11 depleted models eligible for leave-one-target analysis preserved direction. The STAT1/STAT2 signal is therefore not reducible to the 12 core program genes, but it remains partly coupled to the broader interferon-response transcriptome (Supplementary Fig. S10; Supplementary Table S4b).

Two additional analyses provided response-level context rather than causal proof. The MSigDB Hallmark interferon-alpha response set M5911 was positively enriched in all three ranked contrasts (normalized enrichment scores 3.187, 3.050 and 3.527; 10,000 gene-label permutations per contrast). In GSE23307 primary B cells exposed ex vivo to IFN-beta, all 12 genes in the frozen positive arm increased in each of two healthy donors, with mean paired log2(x+1) effects of 3.294 and 3.666. No inferential P value was calculated at n=2 (Fig. 5d,e).

Taken together, these layers support an IFN-centred interpretation of the replicated program while defining its evidential ceiling, with principal quantitative anchors summarized in Supplementary Table S3. CollecTRI activity is inferred from observational disease-ranked statistics, M5911 is a response signature, and GSE23307 is a small healthy-donor perturbation. None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE.

## Discussion

The central finding of this study is a difference in reproducibility across biological layers, not a new B-cell taxonomy. Fine-state assignments were unsupported, and the retained broad scaffold still carried a B_ASC-specific end-to-end limitation. Preserving that failure constrained B_CONV/B_ASC to an analysis scaffold rather than a transferable taxonomy. Within this scope, assignment uncertainty did not change the primary B_ASC composition interpretation or the direction of B_CONV IFN/ISG effects. The supported result is therefore a process-level interferon association within explicit identity limits, not a disease-defining cell-state label or generalized B_ASC expansion.

This hierarchy helps reconcile the present results with established SLE B-cell biology. Interferon activation, plasmablast expansion and activated B-cell phenotypes have all been reported previously, but their prominence varies with disease activity, molecular endotype and treatment context [3,4,8-12]. The higher plasmablast-to-memory ratio reported in patients with greater activity and Sm/RNP autoantibodies [10], for example, is compatible with our secondary positive flare estimate and does not conflict with the primary comparison, which lacked statistical support in the source-defined managed-SLE group. Likewise, functional studies showing that several interferon classes can promote B-cell activation or plasma-cell differentiation [14-16] support biological plausibility without implying that a particular ligand or fine cell state explains the present observational association. The contribution here is therefore not the rediscovery of interferon involvement, but the identification of an inferential level at which that involvement remains reproducible across heterogeneous datasets.

The independent, source-label-defined GSE135779 analysis strengthens that process-level interpretation while also defining its limits. The childhood IFN/ISG result remained positive under donor and source-label omission, and all ten jointly tested IFN genes were concordant across the two primary datasets. Yet the genome-wide effect correlation was only rho=0.026. These observations are not contradictory: transcriptome-wide correlation asks whether thousands of gene effects agree across cohorts that differ in age structure, annotation, processing, covariates and gene universe, whereas the program analysis asks whether a prespecified coherent response retains direction and statistical support. The data support the latter, not a globally shared disease transcriptome. Corrected source-label-independent remapping then failed its prespecified B_ASC calibration criterion, so independent replication remains tied to the broad source-label-defined analogue rather than demonstrating de novo taxonomy transfer.

The regulatory analyses add a second layer of convergence but do not change the evidence class of the study. STAT1 and STAT2 were positive across the three confirmatory contrasts in the prespecified ULM family, and leave-one-target and target-resampling diagnostics argued against a single-target artefact. CAMERA and FRY retained the overall direction while making the limitation of discovery STAT2 explicit. The overlap-depletion results further sharpen that interpretation: removing the 12 core IFN genes did not abolish the regulatory signal, but broader M5911 depletion materially weakened discovery STAT2. Thus, the observed regulatory pattern is not merely a restatement of the 12-gene program, yet it remains partly embedded in the broader interferon-response transcriptome. M5911 enrichment and the two-donor GSE23307 perturbation provide orthogonal response context, not independent proof of in vivo regulation. Collectively, these analyses support an IFN-centred regulatory context but not direct binding, a unique ligand or causal initiation by STAT1/STAT2.

The analysis also narrows several tempting but unsupported narratives. The naive-to-memory and APC/HLA programs provide internal context but do not independently reproduce in GSE135779. The external atypical/low-naive signal cannot be called replication because the corresponding GSE174188 result was null. High global concordance of the broad B_CONV scaffold does not establish a discrete IFN-high subtype, and the absence of statistical support in the primary composition contrast should not be displaced by the secondary flare contrast. These negative and non-generalizing results are consequential: they prevent a heterogeneous set of secondary signals from being promoted to co-equal disease features and keep the manuscript centred on the program supported in the prespecified discovery, internal and source-label-defined external analyses.

The present results have a plausible but still prospective translational implication. A continuous B_CONV IFN/ISG score could be more portable than a hard cell-state label in settings where cohort composition and annotation differ, and it could eventually contribute to molecular stratification or pharmacodynamic monitoring. The current data do not establish a predictive biomarker, a treatment-selection rule, a clinical cutoff or patient benefit. Those questions require prospective treatment-annotated cohorts, longitudinal sampling, assay calibration and prespecified evaluation of discrimination, calibration and clinical utility. A decisive next step would be to test whether the within-B_CONV IFN program predicts longitudinal activity or response to interferon-pathway therapy independently of B-cell composition and conventional clinical covariates.

Several limitations define the remaining evidence gap. Public metadata did not provide a common set of sex, treatment and detailed clinical covariates across all contrasts. End-to-end resampling failed the B_ASC overlap criterion, so propagation of observed assignment exchanges remains a same-data sensitivity rather than evidence of taxonomy transfer. The adult external stratum was small, two adult metadata donors lacked corresponding source matrices, and the GSE174188 donor-nonoverlap replication remains accession-internal. External replication therefore depends on source labels; after correction of the normalization mismatch, source-label-independent remapping failed B_ASC calibration and no corrected disease effect was estimated. Regulatory analyses reuse the same disease contrasts and depend on curated priors and gene coverage, with discovery STAT2 remaining the explicit CAMERA exception. GSE23307 includes only two healthy donors. Direct binding, matched patient perturbation, prospective clinical validation and transferable state taxonomy therefore remain unresolved.

Taken together, the study supports a restrained model of SLE B-cell remodeling: a prespecified IFN/ISG transcriptional shift is reproducible at the process level across the analysed cohorts, whereas the tested hard state assignments retain defined stability and transfer limits. Retaining the failed reconstruction and calibration criteria narrows, rather than weakens, the conclusion: the data support a bounded process-level interferon association within explicit identity and transfer limits.

## Methods

### Study design and data resources

This study was a secondary analysis of public human transcriptomic data. GSE174188 [1,17] served as the discovery resource for disease-blind B-lineage reconstruction, sample-level composition, within-compartment transcription and internal robustness analyses. GSE135779 [2,18] served as the independent SLE replication dataset. CollecTRI and MSigDB provided independently curated regulatory and response priors, and GSE23307 [19,20] provided paired IFN-beta perturbation profiles from primary B cells of healthy donors. Resources that did not contribute to the central replication question were excluded from the active manuscript.

### Source integrity, metadata hierarchy and hard quality control

Source paths, SHA-256 hashes, matrix dimensions and matrix encodings were fixed before analysis. Metadata were reconciled at donor, biological-sample, technical-library and processing-cohort levels. Hard quality control required at least 500 total counts, at least 200 detected genes, no more than 10% mitochondrial counts, no more than 1% haemoglobin counts, no more than 0.5% platelet-marker counts and detection of at least one B-lineage marker. Each excluded cell retained a reason-level record. Disease fields were stored separately and were not used during identity reconstruction.

### Disease-blind representation and identity adjudication

Residual doublet risk was evaluated per complete library. Raw counts were retained for pseudobulk analyses, whereas normalized log expression was used for recurrent highly variable gene selection, principal-component analysis and neighbour-graph construction. Unintegrated Scanpy [21] and Harmony-adjusted [22] representations were compared using technical mixing, biological marker conservation, bridge samples and coverage across donors, samples and libraries. Identity-policy selection used 20 within-library resamples containing 80% of cells from the frozen 50-dimensional Harmony representation. The fine-grained solution failed the prespecified stability criteria and was retained as a negative result. Transition reconstruction instead supported a broad B_CONV/B_ASC partition after marker and frozen-representation stability checks, with disease information still protected.

### End-to-end identity sensitivity and uncertainty propagation

To test whether the broad partition survived reconstruction of the representation itself, we repeated within-library 80% resampling 20 times from the raw matrix. Each replicate independently filtered genes, selected 3,000 recurrent highly variable genes from a 7,000-gene candidate pool, recalculated 50 principal components, reran Harmony, reconstructed 15-nearest-neighbour graphs and reran Leiden [23] at resolutions 0.4, 0.6 and 0.8. Replicate clusters were mapped to the frozen reference by maximum cell overlap. The unchanged broad-state criteria were median and minimum mapped adjusted Rand indices of at least 0.95 and 0.90, median and minimum mapping agreement of at least 0.995 and 0.990, and minimum state-median Jaccard of at least 0.95.

Uncertainty propagation used only assignment exchanges observed in these end-to-end replicates. For each replicate, sampled cells that switched between B_CONV and B_ASC were changed in the full frozen partition, whereas unsampled cells retained their frozen assignment. No sample, gene, threshold or model was reselected. The beta-binomial composition models were refitted under the original eligibility rules and designs. Boundary-cell raw counts were added to or subtracted from the frozen B_CONV pseudobulks before TMM log-counts-per-million normalization, scoring of the frozen 12-gene IFN/ISG program and HC3 inference. These analyses quantify same-data sensitivity to identity uncertainty; they are not independent replication.

### Sample-level composition

Cells were aggregated by biological sample and processing cohort, with the sample-cohort stratum as the experimental unit and donor-aware sensitivity analyses for repeated samples. Models were restricted to prespecified processing cohorts with case-control common support and to strata containing at least 50 frozen B cells. The primary comparison was processing-cohort-4 source-defined managed SLE versus normal, adjusted for age and ethnicity. Internal processing-cohort-2 and secondary processing-cohort-3 analyses of the source-defined flare category were estimated separately. Bridge strata were not pooled to create an otherwise unsupported disease coefficient. Model-based and sandwich uncertainty, threshold analyses, one-sample-per-donor fits and leave-one-out diagnostics were retained.

### Raw-count pseudobulk and gene-level inference

Raw counts were summed by sample-cohort stratum within B_CONV, combining technical-library contributions only after cell-ID and count-conservation checks. Strata with at least 50 cells defined the primary analysis; 20- and 100-cell thresholds and a residual-doublet-risk-negative branch were prespecified sensitivities. Genes were filtered with edgeR [24,25] filterByExpr, libraries were TMM-normalized, and robust quasi-likelihood models were fitted with the prespecified contrast-specific covariates. Benjamini-Hochberg adjustment was applied across tested genes within each contrast, while complete feature tables retained untested genes with explicit status flags.

### Frozen program inference

Program membership and direction were fixed before disease effects were estimated. Duplicate gene symbols were summed before TMM log-counts-per-million normalization. Within each contrast, genes were standardized across pseudobulks and each program score was calculated as the mean positive-arm score minus the mean negative-arm score. Disease effects and 95% confidence intervals were estimated with linear models using HC3 sandwich covariance. The confirmatory family comprised naive-to-memory, atypical/low-naive, APC/HLA and IFN/ISG programs, with Benjamini-Hochberg correction across these four tests. Ranked competitive enrichment and gene-direction coherence were treated as secondary support.

### Source-label-defined GSE135779 replication

GSE135779 source files, metadata versions, donor availability, source-label support and availability of the frozen program genes were evaluated before disease effects were inspected. The external identity scope was deliberately broad: a conventional-B analogue assembled from eight source B-cell labels, without transferring hard naive/memory identities. Childhood, adult and combined model matrices and minimum-cell sensitivities were fixed before model fitting. Before disease-effect modelling, real matrices were used to verify dimensions and count conservation, and synthetic null and signal data were used to test the statistical implementation. Gene- and program-level analyses then followed the GSE174188 framework where permitted by the external gene universe.

### Reference-calibrated external mapping sensitivity

We additionally asked whether B-lineage selection in GSE135779 could be reconstructed without source-provided cell labels. Sample-wise quality control and Leiden clustering of all external matrices preceded selection with prespecified B-lineage and exclusion-marker modules. Elastic-net logistic regression and Pearson nearest-centroid mapping provided two algorithmically distinct broad-state mappers using the same GSE174188 reference and common feature space. Donor-grouped reference cross-validation evaluated regularization and candidate confidence thresholds under prespecified state-specific eligibility criteria. Eligibility required at least 80% reference-cell coverage and at least 90% precision for each state; high overall accuracy alone was insufficient. The reference training set contained 13,000 B_CONV and 1,300 B_ASC cells from 258 donors. These folds calibrated mapping performance and were not independent validation of the full feature-selection and tuning pipeline.

A post-unblinding audit identified incompatible normalization denominators between the original reference and external feature matrices: selected-feature totals were used in the reference, whereas full-library totals were used externally. We therefore recomputed the reference with full-library log1p(CP10K) normalization before feature subsetting and reran all matrices without changing the selection rules, candidate grids or eligibility thresholds. Diagnostic fallback thresholds were not permitted to determine eligibility for disease-effect analysis. Inputs, code, predictions and protected-metadata identity were verified by hashes. Because the original sensitivity outcomes had already been observed, this correction was treated as a technical repair rather than a new prospective analysis. Failure of the corrected calibration criterion prevented disease-effect estimation, and the original sensitivity outcome was excluded from supporting evidence.

### Influence, specificity and cross-dataset analyses

The childhood IFN/ISG model was repeated after removing each donor in turn. Dependence on source annotation was assessed by omitting each of the eight contributing B-cell labels without reselecting donors. Platelet/ambient, ASC/UPR and pan-B programs were prespecified specificity controls. Cross-dataset gene analysis was restricted to genes passing the respective filters in both primary datasets; the shared IFN subset was evaluated separately from genome-wide effect correlation.

### Prespecified TF-target activity

Human CollecTRI interactions [26,27] were retrieved from OmniPath on 15 August 2026 and fixed by raw SHA-256 98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1. Only exact individual-TF source symbols were used. Consensus stimulation and inhibition were encoded as +1 and -1; ambiguous target directions were excluded, and duplicate same-sign edges were collapsed. The confirmatory family comprised STAT1, STAT2, IRF7, IRF9, E2F1, FOXM1, MYC and MYBL2 across the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts.

For each tested Ensembl feature, the ranked statistic was sign(logFC) * sqrt(F) from the robust edgeR quasi-likelihood model. Features were mapped to uppercase gene symbols, with statistics averaged when multiple tested Ensembl features mapped to the same symbol. For each regulator and contrast, a univariate linear model with an intercept regressed the gene-level statistic on signed target weight. The slope, standard error, two-sided P value and 95% confidence interval were independently reproduced by direct matrix algebra. Benjamini-Hochberg correction was applied once across all 24 confirmatory regulator-by-contrast tests. For each core STAT1/STAT2 model, influence analysis removed each matched target in turn, and 100 deterministic analyses resampled 80% of matched targets.

### Correlation-aware STAT1/STAT2 sensitivity

Because genes within a regulon are correlated, the rank-based ULM results were supplemented by a correlation-aware sensitivity that retained the same regulators, signed CollecTRI targets, contrasts, model matrices and filterByExpr backgrounds. Pseudobulk counts were collapsed to gene symbols and transformed with voom precision weights [28,29]. Expression rows for inhibitory targets were sign-reversed so that a positive set direction retained the signed-regulon interpretation. CAMERA [30] estimated inter-gene correlation from model residuals and performed a competitive rank test, whereas FRY [28,31] provided a fast self-contained approximation to the directional mroast/ROAST gene-set test. Benjamini-Hochberg adjustment was applied separately across the six STAT1/STAT2 regulator-by-contrast tests for each method. Matched-target counts were required to equal those in the ULM analysis; no target, regulator, contrast or background was reselected after the sensitivity results were examined.

### STAT1/STAT2 IFN-overlap-depletion sensitivity

A post-freeze sensitivity evaluated whether STAT1/STAT2 results were reducible to genes shared with interferon-response programs. Branch A removed the 12 frozen positive-arm IFN/ISG genes from the signed regulon targets; branch B removed all 97 members of MSigDB M5911. Ranked statistics, tested-gene backgrounds, CollecTRI signs, contrasts and model matrices were otherwise unchanged. ULM, CAMERA and FRY were rerun within each branch, and ULM leave-one-target analysis was performed only when at least ten targets remained. Benjamini-Hochberg adjustment was applied separately within each branch and method across the six core regulator-by-contrast tests. Interpretation jointly considered direction, ULM attenuation and confidence intervals, target retention, corrected q values and cross-method consistency rather than a binary significance rule.

### Orthogonal interferon-response analyses

The MSigDB [32] 2026.1.Hs Hallmark set HALLMARK_INTERFERON_ALPHA_RESPONSE (M5911; 97 fixed member genes) was tested against each complete ranked contrast. Preranked enrichment used 10,000 deterministic gene-label permutations; normalized enrichment scores and descriptive three-contrast q values were reported outside the 24-test TF family.

GSE23307 [19,20] GPL6104 profiles comprised paired untreated and IFN-beta-exposed primary B cells from two healthy donors. Platform annotation was fixed before effects were calculated. Twenty-one probes mapping to the 12 frozen IFN/ISG positive-arm genes were transformed as log2(x+1), collapsed to one value per gene and sample by the median, and differenced within donor. The donor summary was the mean paired effect across the 12 genes. Gene-level paired effects were retained for descriptive display; donor means served only as summaries, and no inferential test treated genes as biological replicates. Direction and gene concordance were descriptive; no inferential P value was calculated at n=2. Only log2(x+1)-transformed GSE23307 values contributed to the reported results, figures and claims.

### Statistical analysis and multiplicity

This retrospective secondary analysis included all eligible public biological units after the prespecified quality-control, support and mapping rules; no prospective sample-size or power calculation was performed. Analysis sizes are reported with the corresponding results and figure panels. Unless explicitly described as directional, tests were two-sided and intervals were 95% confidence intervals. The primary B_ASC composition model used a beta-binomial Wald test with Benjamini-Hochberg correction across the three prespecified base contrasts; covariance and two-part models were sensitivity analyses reported with nominal P values. Gene-level robust edgeR quasi-likelihood tests used Benjamini-Hochberg correction across filterByExpr-tested genes within each contrast. Frozen-program linear models used HC3 covariance and Benjamini-Hochberg correction across the four prespecified programs within each analysis. Ranked program-arm CAMERA results were corrected within each corresponding analysis.

The CollecTRI activity analysis used two-sided target-slope tests and one global Benjamini-Hochberg family across eight regulators and three confirmatory contrasts (24 tests). STAT1/STAT2 CAMERA and FRY sensitivities used positive-direction tests with separate six-test Benjamini-Hochberg families for each method. Each IFN-overlap-depletion branch contributed separate six-test post-freeze sensitivity families for ULM, CAMERA and FRY; these did not replace the original 24-test regulator family. M5911 used a positive-direction weighted preranked test with 10,000 deterministic gene-label permutations per contrast and a descriptive Benjamini-Hochberg correction across three contrasts. The paired GSE23307 experiment contained two donors and therefore carried no inferential P value. Statistical significance was defined as q<0.05 only within the stated confirmatory family; nominal and descriptive results were not promoted to confirmatory evidence. The complete multiplicity map, full gene-level tables and sanitized design matrices are provided in Supplementary Data 3.

### Generative AI assistance

OpenAI Codex was used for code drafting, workflow documentation, language editing and development of quality-control checks. All computations were executed locally against fixed inputs, and numerical results were taken from machine-generated analysis outputs rather than generated by the language model. The authors remain responsible for the scripts, results, interpretations and revised text. No AI system is listed as an author.

### Reproducibility and provenance

Analyses were organized in timestamped run directories with immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 manifests (Supplementary Tables S5-S8). Disease effects were estimated only after input, design and statistical-implementation verification. Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version.

### Ethics and consent

This secondary study used only publicly available, de-identified human transcriptomic datasets and involved no participant recruitment, intervention or collection of new specimens. No additional ethics approval was required for this secondary analysis. Ethics approval and consent procedures for the source studies are reported in the original publications [1,2,19]. Consent for publication was not applicable because no identifiable participant information was used.

## Data availability

The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [17,18,20]. Project-generated figure source data and complete statistical results are included as Supplementary Data 1-3 and in the version-specific reproducibility archive at https://doi.org/10.5281/zenodo.22151739 [33]. Large recomputable matrices are not duplicated from their source repositories. Third-party GEO and CELLxGENE data remain subject to their source terms.

## Code availability

Analysis code, executable decision records, environment specifications and restoration instructions are available at https://github.com/1209433622cz-maker/sle-bcell-remodeling (release v1.1.0; frozen scientific content commit f1859ff8498d5569a1d5027b36ed18c8b7c7536f) and are archived at https://doi.org/10.5281/zenodo.22151739 [33]. Original project code is licensed under the MIT License.

## Acknowledgements

This study received no funding.

## Author contributions

Z.C.: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft. T.Q.: Conceptualization, Methodology, Project administration, Validation, Writing - review and editing.

## Competing interests

The authors declare no competing interests.

## References

1. Perez, R. K. et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. Science **376**, eabf1970 (2022). https://doi.org/10.1126/science.abf1970.

2. Nehar-Belaid, D. et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. Nat. Immunol. **21**, 1094-1106 (2020). https://doi.org/10.1038/s41590-020-0743-0.

3. Jenks, S. A. et al. Distinct Effector B Cells Induced by Unregulated Toll-like Receptor 7 Contribute to Pathogenic Responses in Systemic Lupus Erythematosus. Immunity **49**, 725-739.e6 (2018). https://doi.org/10.1016/j.immuni.2018.08.015.

4. Szelinski, F. et al. Plasmablast-like Phenotype Among Antigen-Experienced CXCR5 - CD19 low B Cells in Systemic Lupus Erythematosus. Arthritis Rheumatol. **74**, 1556-1568 (2022). https://doi.org/10.1002/art.42157.

5. Crowell, H. L. et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. Nat. Commun. **11**, 6077 (2020). https://doi.org/10.1038/s41467-020-19894-4.

6. Squair, J. W. et al. Confronting false discoveries in single-cell differential expression. Nat. Commun. **12**, 5692 (2021). https://doi.org/10.1038/s41467-021-25960-2.

7. Büttner, M., Ostner, J., Müller, C. L., Theis, F. J. & Schubert, B. scCODA is a Bayesian model for compositional single-cell data analysis. Nat. Commun. **12**, 6876 (2021). https://doi.org/10.1038/s41467-021-27150-6.

8. Banchereau, R. et al. Personalized Immunomonitoring Uncovers Molecular Networks that Stratify Lupus Patients. Cell **165**, 551-565 (2016). https://doi.org/10.1016/j.cell.2016.03.008.

9. Chiche, L. et al. Modular Transcriptional Repertoire Analyses of Adults With Systemic Lupus Erythematosus Reveal Distinct Type I and Type II Interferon Signatures. Arthritis Rheumatol. **66**, 1583-1595 (2014). https://doi.org/10.1002/art.38628.

10. van Dooren, H. J. et al. Interferon signatures fuel B cell hyperactivity and plasmablast expansion in systemic lupus erythematosus. J. Autoimmun. **154**, 103438 (2025). https://doi.org/10.1016/j.jaut.2025.103438.

11. Hubbard, E. L. et al. Analysis of transcriptomic features reveals molecular endotypes of SLE with clinical implications. Genome Med. **15**, 84 (2023). https://doi.org/10.1186/s13073-023-01237-9.

12. Sayadi, A. et al. Single-cell RNA-seq reveals a persistent interferon signature in immune cells from systemic lupus erythematosus patients with high versus low polygenic risk scores despite antimalarial treatment. J. Autoimmun. **161**, 103575 (2026). https://doi.org/10.1016/j.jaut.2026.103575.

13. Arazi, A. et al. The immune cell landscape in kidneys of patients with lupus nephritis. Nat. Immunol. **20**, 902-914 (2019). https://doi.org/10.1038/s41590-019-0398-x.

14. Akita, K. et al. Interferon alpha Enhances B Cell Activation Associated With FOXM1 Induction: Potential Novel Therapeutic Strategy for Targeting the Plasmablasts of Systemic Lupus Erythematosus. Front. Immunol. **11**, 498703 (2021). https://doi.org/10.3389/fimmu.2020.498703.

15. Barnas, J. L. et al. B Cell Activation and Plasma Cell Differentiation Are Promoted by IFN-lambda in Systemic Lupus Erythematosus. J. Immunol. **207**, 2660-2672 (2021). https://doi.org/10.4049/jimmunol.2100339.

16. Faheem, Z. et al. Type I interferons enhance B cell activation and promote differentiation of double negative 2 cells in SLE. Lupus Sci. Med. **13**, e002042 (2026). https://doi.org/10.1136/lupus-2026-002042.

17. National Center for Biotechnology Information. Gene Expression Omnibus series GSE174188. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188 (accessed 21 Aug 2026).

18. National Center for Biotechnology Information. Gene Expression Omnibus series GSE135779. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779 (accessed 21 Aug 2026).

19. van Boxel-Dezaire, A. H. H. et al. Major Differences in the Responses of Primary Human Leukocyte Subsets to IFN-beta. J. Immunol. **185**, 5888-5899 (2010). https://doi.org/10.4049/jimmunol.0902314.

20. National Center for Biotechnology Information. Gene Expression Omnibus series GSE23307. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE23307 (accessed 21 Aug 2026).

21. Wolf, F. A., Angerer, P. & Theis, F. J. SCANPY: large-scale single-cell gene expression data analysis. Genome Biol. **19**, 15 (2018). https://doi.org/10.1186/s13059-017-1382-0.

22. Korsunsky, I. et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nat. Methods **16**, 1289-1296 (2019). https://doi.org/10.1038/s41592-019-0619-0.

23. Traag, V. A., Waltman, L. & van Eck, N. J. From Louvain to Leiden: guaranteeing well-connected communities. Sci. Rep. **9**, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z.

24. Robinson, M. D., McCarthy, D. J. & Smyth, G. K. edgeR: a Bioconductor package for differential expression analysis of digital gene expression data. Bioinformatics **26**, 139-140 (2010). https://doi.org/10.1093/bioinformatics/btp616.

25. Chen, Y., Lun, A. T. L. & Smyth, G. K. From reads to genes to pathways: differential expression analysis of RNA-Seq experiments using Rsubread and the edgeR quasi-likelihood pipeline. F1000Res. **5**, 1438 (2016). https://doi.org/10.12688/f1000research.8987.2.

26. Badia-i-Mompel, P. et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. Bioinform. Adv. **2**, vbac016 (2022). https://doi.org/10.1093/bioadv/vbac016.

27. Müller-Dott, S. et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. Nucleic Acids Res. **51**, 10934-10949 (2023). https://doi.org/10.1093/nar/gkad841.

28. Ritchie, M. E. et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Res. **43**, e47-e47 (2015). https://doi.org/10.1093/nar/gkv007.

29. Law, C. W., Chen, Y., Shi, W. & Smyth, G. K. voom: precision weights unlock linear model analysis tools for RNA-seq read counts. Genome Biol. **15**, R29 (2014). https://doi.org/10.1186/gb-2014-15-2-r29.

30. Wu, D. & Smyth, G. K. Camera: a competitive gene set test accounting for inter-gene correlation. Nucleic Acids Res. **40**, e133-e133 (2012). https://doi.org/10.1093/nar/gks461.

31. Wu, D. et al. ROAST: rotation gene set tests for complex microarray experiments. Bioinformatics **26**, 2176-2182 (2010). https://doi.org/10.1093/bioinformatics/btq401.

32. Liberzon, A. et al. The Molecular Signatures Database (MSigDB) hallmark gene set collection. Cell Syst. **1**, 417-425 (2015). https://doi.org/10.1016/j.cels.2015.12.004.

33. Chen, Z. & Qi, T. SLE B-cell remodeling analysis: code, source data and reproducible release. Zenodo https://doi.org/10.5281/zenodo.22151739 (2026).

## Figure legends

### Figure 1 | Disease-blind reconstruction defines a bounded analysis scaffold

a, Disease-blind B_CONV/B_ASC adjudication preceded sample-cohort analyses; hard fine states were not used. b, Median/minimum mapped ARI across 20 within-library fixed 50-dimensional Harmony resamples; dashed segment, minimum-ARI criterion 0.90. c, Fixed-representation minimum-to-median state Jaccard; dashed guide, criterion 0.95. B_ASC markers 5/5; minimum sample support 1.00. d, End-to-end minimum-to-median state Jaccard across 20 rebuilds; B_ASC below 0.95, B_CONV concordant. Panels b/c fix the representation; d recomputes highly variable genes, principal components and Harmony. Supplementary Fig. S4 provides replicate diagnostics/downstream propagation. Cell metrics are not disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

a, Observed B_ASC fractions for 43 control and 47 managed-SLE sample-cohort strata, with adjusted fractions and 95% confidence intervals. b, Primary, internal, donor-nonoverlap and secondary flare conditional odds ratios. c, Primary estimate and prespecified minimum-cell, explicit non-B and residual-doublet sensitivities. d, Conditional odds ratios after each of 90 primary sample deletions; the horizontal line is the full estimate. The flare contrast was secondary and did not pass the prespecified three-contrast correction.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

a, Effects and 95% confidence intervals for the four prespecified B_CONV programs in the primary contrast. b, IFN/ISG estimates across support thresholds, residual-risk restriction, internal replication, donor-nonoverlap internal replication and the secondary flare contrast. c, Gene-level log2 fold changes for the prespecified IFN positive arm in the primary and donor-nonoverlap contrasts. A dagger marks genes not tested in either contrast; a double dagger marks genes not tested in the primary contrast. Filtered values are absent rather than zero or imputed. d, IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity families in the primary and donor-nonoverlap contrasts. Program intervals use HC3 uncertainty; program q values use the prespecified four-program family.

### Figure 4 | GSE135779 provides source-label-defined replication of the IFN/ISG program

a, Standardized IFN/ISG effects for childhood, combined, adult and support-threshold GSE135779 analyses. b, Standardized GSE174188 discovery/internal effects beside source-label-defined GSE135779 effects. c, Effects for 4,410 genes tested in both primary datasets, highlighting the ten jointly tested IFN genes; all ten were positive despite genome-wide Spearman rho=0.026. d, Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Display labels 1-8 map to the source codes in Figure 4 Source Data. Donors are the biological units; the adult estimate is directional only.

### Figure 5 | Convergent observational evidence supports an IFN-centred regulatory context

a, Evidence classes and interpretive roles for the replicated IFN/ISG program. ULM STAT1/STAT2 provides confirmatory observational evidence across three contrasts, M5911 provides response-set concordance and GSE23307 provides descriptive IFN-beta perturbational context. These layers show observational convergence but do not establish a causal regulator, direct binding or a unique upstream stimulus. b, Core STAT1/STAT2 and extended IRF7/IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. c, Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation comparators; asterisks denote global 24-test q<0.05. d, M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. e, Paired log2(x+1) effects for the 12-gene IFN positive arm in two IFN-beta-exposed healthy donors; same-gene points are connected for display only, all 24 effects were positive and no inferential P value was calculated at n=2.
