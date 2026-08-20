# Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence in systemic lupus erythematosus B cells

**Article type:** Research

**Authors:** Zhi Chen [1] and Teng Qi [1,*]

**Affiliation 1:** School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen 518172, China

**Corresponding author:** Teng Qi, School of Medicine, The Chinese University of Hong Kong, Shenzhen, MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China; tengqi@link.cuhk.edu.cn

**ORCID identifiers:** Zhi Chen, https://orcid.org/0009-0001-0072-5576; Teng Qi, https://orcid.org/0009-0007-7648-4776

**Author emails:** Zhi Chen, zhichen1@link.cuhk.edu.cn; Teng Qi, tengqi@link.cuhk.edu.cn

**Running title:** Replicated IFN remodeling in SLE B cells

**Version:** Gate C8 Genome Medicine submission draft v10

**Date:** 20 August 2026

## Abstract

**Background:** SLE alters both the abundance and transcriptional state of peripheral B cells, but these layers can be conflated by outcome-informed annotation, cell-level inference and technically imbalanced cohorts.

**Methods:** We performed a donor- and cohort-resolved reanalysis of public single-cell RNA-sequencing data. B-lineage identity was reconstructed without disease labels in GSE174188 before sample-level composition and sample-by-compartment pseudobulk testing. A frozen program was evaluated in independent GSE135779, followed by a prespecified 24-test CollecTRI family, MSigDB M5911 enrichment and paired IFN-beta perturbation profiles from GSE23307.

**Results:** Among 150,402 quality-controlled GSE174188 B-lineage cells, resampling supported broad conventional-B (B_CONV) and antibody-secreting-cell (B_ASC) compartments but not stable hard naive-memory subtypes. Primary B_ASC relative abundance was not associated with SLE (odds ratio 0.947, 95% confidence interval 0.636-1.410; P=0.787). Within B_CONV, the prespecified IFN/ISG program increased in the primary contrast (effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6), a donor-nonoverlap internal contrast (effect 1.086; q=3.61 x 10^-4) and independent GSE135779 childhood donors (11 controls and 32 SLE; effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). All ten jointly tested IFN genes were positive despite low genome-wide agreement (Spearman rho=0.026). STAT1 and STAT2 target activities were positive and globally significant in all three contrasts and robust to target deletion and resampling. M5911 was enriched in all contrasts, and IFN-beta exposure increased all 12 frozen genes in each of two healthy-donor profiles.

**Conclusions:** SLE shows independently replicated IFN remodeling within a disease-blind broad conventional-B compartment, with convergent observational regulatory evidence. The results do not establish a discrete subtype, causal regulator or unique upstream stimulus.

## Keywords

systemic lupus erythematosus; B cells; single-cell RNA sequencing; pseudobulk; interferon; independent validation; transcription-factor activity; reproducibility

## Background

Systemic lupus erythematosus (SLE) is a heterogeneous autoimmune disease involving loss of B-cell tolerance, autoantibody production and sustained innate immune activation. Peripheral-blood single-cell studies have described changes in naive, memory, double-negative, CD11c-positive and antibody-secreting B-cell populations together with prominent type I interferon responses [1,2]. However, a larger fraction of cells assigned to a state and increased gene expression within that state are biologically distinct phenomena.

Single-cell disease studies are particularly vulnerable to pseudoreplication when cells, rather than donors or biological samples, are treated as independent units [3,4]. Composition introduces an additional constraint because an increase in one compartment changes the observed fractions of all others [5]. Public SLE resources also distribute samples across processing cohorts, include repeated donors and provide uneven disease-group support within technical strata. Outcome-informed cluster labels or pooled cell-level tests can therefore combine biology with design structure.

We addressed these problems through a staged secondary analysis. Raw-count integrity, metadata hierarchy and disease-by-cohort support were audited first. B-lineage identity was reconstructed while protected disease fields remained separate. Only after a disease-blind identity model was frozen were sample-level composition and within-compartment transcription tested. The primary expression result was then carried into independent GSE135779 under a pre-effect mapping and analysis contract.

The analysis was designed to distinguish robust process-level biology from unstable subtype narratives. We tested whether fine B-cell partitions were reproducible enough for hard outcome inference, whether antibody-secreting-cell abundance represented a primary disease result and whether a frozen transcriptional program replicated across datasets. Finally, we used a prespecified TF-target family and two orthogonal response resources to evaluate convergent regulatory support without converting association into a causal claim.

## Methods

### Study design and data resources

The study was a secondary analysis of public human transcriptomic data. GSE174188 [1,14] was used for disease-blind B-lineage reconstruction, sample-level composition, within-compartment transcriptional analysis and internal validation. GSE135779 [2,15] was the independent SLE validation dataset. CollecTRI and MSigDB supplied independently curated regulatory and response priors, and GSE23307 [13,16] supplied paired IFN-beta perturbation profiles from healthy-donor primary B cells. Resources not contributing to the central replication claim were excluded from the active manuscript.

### Source integrity, metadata hierarchy and hard quality control

Source paths, SHA-256 hashes, matrix dimensions and matrix encodings were frozen before analysis. Metadata keys were audited at donor, biological-sample, technical- library and processing-cohort levels. Hard-quality-control thresholds were at least 500 total counts, at least 200 detected genes, no more than 10% mitochondrial counts, no more than 1% haemoglobin counts, no more than 0.5% platelet-marker counts and detection of at least one B-lineage marker. Each excluded cell retained a reason-level record. Protected disease fields were stored separately during reconstruction.

### Disease-blind representation and identity freeze

Residual doublet risk was evaluated per complete library. Raw counts were retained for pseudobulk, whereas normalized log expression was used for recurrent highly variable gene selection, principal components and neighbor graphs. Unintegrated Scanpy [6] and Harmony-adjusted [7] representations were compared using technical mixing, biological marker conservation, bridge samples and coverage across donors, samples and libraries. Leiden [8] solutions were evaluated across resolutions and 20 cell-resampling runs. Failure of the fine-grained solution was retained. A two-compartment solution was reconstructed from resampling transitions and approved only after marker and stability checks while disease remained blinded.

### Sample-level composition

Cells were aggregated by biological sample and processing cohort. The experimental unit was the sample-cohort stratum, with donor-aware sensitivity analyses for repeated samples. Models were restricted to prespecified processing cohorts with case-control common support and to strata with at least 50 frozen B cells. The primary comparison was processing cohort 4 managed SLE versus normal, adjusted for age and ethnicity. Internal processing-cohort-2 and secondary processing-cohort-3 flare analyses were estimated separately. Bridge strata were not used to manufacture a pooled disease coefficient. Model, sandwich, threshold, one-sample-per-donor and leave-one-out diagnostics were retained.

### Raw-count pseudobulk and gene-level inference

Raw counts were summed by sample-cohort stratum within `B_CONV`, combining technical library contributions only after cell-ID and count conservation checks. Strata with at least 50 cells were primary; 20- and 100-cell thresholds and a residual-doublet-risk-negative cell branch were prespecified sensitivities. Genes were filtered with edgeR [9] `filterByExpr`, libraries were TMM-normalized, and robust quasi-likelihood models were fitted with the frozen contrast-specific covariates. Benjamini-Hochberg adjustment was applied over tested genes within each contrast. Full feature tables retained untested genes with explicit flags.

### Frozen program inference

Program membership and direction were frozen before disease effects. Duplicate gene symbols were summed before TMM log-counts-per-million normalization. Within each contrast, genes were standardized across pseudobulks and program scores were computed as the mean positive-arm score minus the mean negative-arm score. Disease effects and 95% confidence intervals used linear models with HC3 sandwich uncertainty. The confirmatory family comprised naive-to-memory, atypical/low-naive, APC/HLA and IFN/ISG programs; Benjamini-Hochberg correction was applied across these four tests. Ranked competitive enrichment and gene-direction coherence were secondary support.

### Independent GSE135779 validation

GSE135779 source files, metadata versions, donor availability, source-label support and frozen program-gene availability were audited without inspecting disease effects. The external identity scope was a broad conventional-B analog formed from eight source B-cell labels. Childhood, adult and combined model matrices and minimum-cell sensitivities were frozen before model fitting. Real matrices were imported for dimension and count-conservation qualification only; synthetic null and signal data qualified the statistical engine before the real disease coefficients were unlocked. Gene and program methods then matched the GSE174188 framework where the different gene universe allowed.

### Influence, specificity and cross-dataset analyses

The childhood IFN/ISG model was repeated after deleting each donor. Source-label dependence was assessed by omitting each of the eight contributing labels without reselecting donors. Platelet/ambient, ASC/UPR and pan-B families were prespecified as controls. Cross-dataset gene analysis was restricted to genes passing the respective filters in both primary datasets; the shared IFN subset was reported separately from the genome-wide rank correlation.

### Prespecified TF-target activity

Human CollecTRI interactions [10,11] were retrieved from OmniPath on 15 August 2026 and frozen by raw SHA-256 `98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1`. Only exact individual-TF source symbols were used. Consensus stimulation and inhibition were encoded as +1 and -1, respectively; ambiguous target directions were excluded, and duplicate same-sign edges were collapsed. The confirmatory family comprised STAT1, STAT2, IRF7, IRF9, E2F1, FOXM1, MYC and MYBL2 in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts.

For every tested Ensembl feature, the ranked statistic was `sign(logFC) * sqrt(F)` from the frozen robust edgeR quasi-likelihood result. Features were mapped to uppercase symbols, and statistics were averaged when multiple tested Ensembl features mapped to one symbol. For each regulator and contrast, a univariate linear model with an intercept regressed the gene-level statistic on the signed target weight. The slope, standard error, two-sided P value and 95% confidence interval were reproduced independently by direct matrix algebra. Benjamini-Hochberg correction was applied once across all 24 confirmatory tests. For each core regulator and contrast, influence analysis deleted each matched target in turn, and 100 deterministic analyses resampled 80% of matched targets.

### Orthogonal interferon-response analyses

MSigDB [12] human release 2026.1.Hs Hallmark set `HALLMARK_INTERFERON_ALPHA_RESPONSE` (systematic identifier M5911; 97 frozen member genes) was tested against each complete ranked contrast. Preranked enrichment used 10,000 deterministic gene-label permutations, with normalized enrichment scores and descriptive three-contrast q values reported outside the 24-test TF family.

GSE23307 [13,16] GPL6104 microarray profiles comprised paired untreated and IFN-beta-exposed primary B cells from two healthy donors. Platform annotation was frozen before effects were calculated. Twenty-one probes mapping to the 12 frozen IFN/ISG positive-arm genes were transformed as log2(x+1), collapsed to one value per gene and sample by the median, and differenced within donor. The donor summary was the mean paired effect across 12 genes. Direction and gene concordance were descriptive; no inferential P value was calculated at n=2. Earlier untransformed GSE23307 files were retained solely as superseded audit artifacts and were excluded from every active result, figure and claim.

### Generative AI assistance

OpenAI Codex was used during project development for code drafting, workflow documentation, language editing and generation of quality-control checks. All computations were executed locally against frozen inputs; numerical results were read from machine-generated analysis outputs rather than generated by the language model. The authors reviewed the scripts, outputs, interpretations and final text and remain accountable for the work. No AI system is listed as an author.

### Reproducibility and governance

Every gate used timestamped run directories, immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 integrity manifests. Real effects were calculated only after input, design and statistical- engine qualification. Earlier manuscripts and figures were retained for provenance but were not used as numerical sources for this version.

## Results

### A disease-blind two-compartment model defines the permissible biological scope

The authoritative GSE174188 B-lineage source contained 152,981 cells and 30,172 genes. Frozen hard-quality-control rules retained 150,402 cells. Metadata audits resolved 259 donors, 271 biological samples, 88 technical libraries and four processing cohorts, including repeated donors and samples spanning processing cohorts. Disease-by-cohort common support was not uniform, so discovery of identity could use the full disease-blind cell set whereas disease coefficients were restricted to prespecified supported contrasts.

Complete-library doublet diagnostics, recurrent highly variable gene selection, unintegrated and Harmony representations, bridge-sample checks and marker coverage were reviewed before outcome access. The initial five-state identity solution did not satisfy the prespecified resampling thresholds. This negative result was preserved rather than relabelled as a successful subtype analysis. Transition reconstruction supported a two-level model comprising `B_CONV` and `B_ASC`, with naive-memory structure retained as a continuous program within `B_CONV` and platelet-associated expression retained as a technical overlay.

The two-compartment solution reproduced in all 20 resampling runs. The minimum mapped adjusted Rand index was 0.990, minimum mapping agreement was 0.9998 and the minimum state median Jaccard index was 0.991. `B_ASC` identity was independently supported by DERL3, JCHAIN, MZB1, TNFRSF17 and XBP1. These results authorize broad conventional-B and antibody-secreting compartments, but not hard naive, memory or atypical publication subtypes.

### B_ASC composition is secondary rather than the central disease signal

Protected outcomes were joined only after the two-compartment freeze. Composition was estimated at the sample-cohort level, with a minimum of 50 eligible B cells per stratum and no cell-level disease test. In the primary processing-cohort-4 contrast, the conditional odds ratio for `B_ASC` relative abundance was 0.947 (95% confidence interval 0.636-1.410; P=0.787). Adjusted fractions were 1.61% in controls and 1.52% in managed SLE. The HC1 sandwich audit was concordant (95% confidence interval 0.651-1.376; P=0.774), and all 90 leave-one-sample-out estimates retained the same direction without generating statistical support.

The internal validation estimate was also below one (odds ratio 0.772), as was the explicit donor-nonoverlap estimate (odds ratio 0.591; n=53), but neither converted the null primary result into a central composition claim. A secondary flare contrast was positive (odds ratio 2.303; nominal P=0.0282) but did not survive the frozen three-contrast correction (q=0.0845). Accordingly, abundance results provide context for the transcriptional analysis and a transparent negative boundary, not evidence for a generally expanded `B_ASC` compartment.

### Within-B_CONV transcription identifies a reproducible IFN/ISG program

Raw counts were aggregated into sample-cohort `B_CONV` pseudobulks after technical library contributions from the same stratum were combined. The primary analysis included 89 pseudobulks, comprising 43 reference and 46 SLE strata, and retained 59,873,385 UMI counts. Gene-level inference used TMM normalization, `filterByExpr`, robust edgeR quasi-likelihood models and Benjamini-Hochberg correction within each contrast. A separately frozen four-program family was tested from TMM log-counts-per-million values using positive-minus-negative standardized scores and HC3 uncertainty.

The prespecified IFN/ISG program was higher in SLE in the primary contrast (effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6). The effect was positive at 20- and 100-cell support thresholds, after residual-doublet-risk calls were excluded, and in all 89 leave-one-sample-out fits. Ranked-gene evidence was coherent, with all ten tested genes in the expected arm direction and competitive enrichment at approximately q=2 x 10^-6. Leading genes included USP18, IFI44L, EPSTI1, IFIT3, MX1, IFI6, OAS2, ISG15 and STAT1.

The IFN/ISG program was also higher in the full internal GSE174188 validation contrast (effect 0.856; q=0.00462) and in the prespecified donor-nonoverlap subset (effect 1.086; q=3.61 x 10^-4). These strata belong to the same accession and are therefore described as internal replication, not an independent cohort.

Two other frozen programs provided more limited GSE174188 context. The naive-to-memory axis was lower in the primary SLE contrast (effect -0.541; q=0.0213), and the APC/HLA program was higher (effect 0.268; q=0.0213), but neither had multiplicity-supported internal validation. The atypical/low-naive program was null in the primary contrast (effect -0.057; q=0.748). These axes are not co-equal with IFN/ISG and were not used to redefine the identity compartment.

### Independent GSE135779 analysis replicates IFN remodeling but not a genome-wide state

GSE135779 source matrices and metadata were audited before any disease effect was calculated. The mapping contract authorized only a broad conventional-B analog constructed from source B-cell labels; it did not authorize transfer of hard naive-memory identities. Matrix import and edgeR behavior were qualified with count-conservation checks and synthetic null and signal data before the real external contrasts were unlocked.

The primary childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 mapped cells per donor. The frozen IFN/ISG program was higher in SLE (effect 1.042, 95% confidence interval 0.681-1.402; q=2.98 x 10^-6). The combined childhood-adult analysis included 54 donors (16 controls and 38 SLE) and yielded a similar estimate (effect 0.996, 95% confidence interval 0.655-1.337; q=1.31 x 10^-6). Results remained positive at minimum support thresholds of 20 (effect 0.965; q=6.75 x 10^-7) and 100 cells (effect 0.939; q=4.06 x 10^-6).

The adult-only estimate was positive (effect 0.968) but imprecise (95% confidence interval -0.123 to 2.060; q=0.291) because it contained five controls and six SLE donors. It is therefore directionally compatible rather than confirmatory. Across 43 childhood donor-deletion fits, IFN/ISG effects ranged from 0.987 to 1.094. Omitting each of the eight source B-cell labels in turn retained the same 43 donors and produced effects from 1.019 to 1.051, excluding dependence on a single source label.

Specificity analyses separated the IFN signal from several alternative explanations. In the childhood contrast, the platelet/ambient, ASC/UPR and pan-B control effects were 0.049, 0.221 and -0.232, respectively, compared with 1.042 for IFN/ISG. All 12 available frozen IFN-arm genes were positive, and ranked enrichment had a camera FDR of 1.85 x 10^-7. Ten IFN genes were jointly tested in the primary GSE174188 and childhood GSE135779 analyses, and all ten were positive in both.

This coherence did not extend across the complete tested transcriptome. Among 4,410 shared tested genes, cross-dataset effect correlation was only Spearman rho=0.026. Thus, the evidence supports program-specific IFN replication across heterogeneous cohorts, not a globally shared disease transcriptome. The GSE135779 atypical/low-naive score was positive (effect 1.191; q=5.10 x 10^-4), but the corresponding GSE174188 result was null; it is retained as an external-only observation rather than replication. Conversely, the GSE174188 naive-to-memory and APC/HLA signals were null externally.

### Prespecified regulatory and perturbational evidence converges on the IFN response

We next tested whether the replicated transcriptional program was accompanied by a prespecified regulatory pattern. The contract was frozen before real regulator effects were inspected and included four IFN-centred regulators (STAT1, STAT2, IRF7 and IRF9), four proliferation controls (E2F1, FOXM1, MYC and MYBL2), and the three confirmatory contrasts used above. Signed CollecTRI target activity was evaluated in one global Benjamini-Hochberg family of 24 tests.

STAT1 and STAT2 activity estimates were positive and globally significant in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. At least three of the four IFN-centred regulators were positive in every contrast, with no globally significant opposite-direction IFN regulator. The proliferation controls did not reproduce a positive globally significant pattern across all three contrasts. Every leave-one-target estimate for the core STAT1 and STAT2 models retained the positive direction, and each core model remained positive in all 100 deterministic 80%-target resamples. These diagnostics argue against a result driven by one target gene or a small target subset.

Two independently defined response layers were directionally concordant. The exact MSigDB Hallmark interferon-alpha response set M5911 was positively enriched in all three ranked contrasts (normalized enrichment scores 3.187, 3.050 and 3.527; 10,000 gene-label permutations per contrast). In GSE23307 primary human B cells exposed to IFN-beta, the frozen 12-gene positive arm increased for all 12 genes in each of two healthy donors. Mean paired log2(x+1) effects were 3.294 and 3.666. No inferential P value was calculated for this two-donor experiment.

The three layers therefore support an IFN-centred regulatory interpretation of the replicated program, but they do not identify a unique initiating ligand or establish causation in SLE. CollecTRI activity is inferred from observational disease-ranked statistics, M5911 is a response signature, and GSE23307 is a small ex vivo perturbation in healthy-donor B cells.

## Discussion

This study identifies a reproducible level of SLE B-cell biology by separating identity, composition and transcription before testing disease effects. Fine-grained hard B-cell states were not stable under the prespecified disease-blind resampling contract, and the repaired model deliberately stopped at two broad compartments. Within that permissible scope, primary `B_ASC` relative abundance did not differ between SLE and controls. The central result instead arose within `B_CONV`: a frozen type I IFN/ISG program was supported in the primary GSE174188 contrast, an internal donor-nonoverlap contrast and independent GSE135779.

The low cross-dataset genome-wide correlation is not a contradiction of the frozen program result. The two accessions differ in age structure, source annotation, sample processing, gene universe and available covariates. A broad correlation asks whether thousands of effect estimates agree despite these differences; the frozen program test asks whether a prespecified coherent biological response has the same direction and statistical support. The data support the latter and explicitly reject the stronger transcriptome-wide interpretation.

The regulator analysis adds convergence without changing that inferential level. STAT1 and STAT2 target activities reproduced across the same discovery, internal donor-nonoverlap and independent childhood contrasts, survived global correction, and were insensitive to individual-target deletion and target resampling. M5911 enrichment and paired IFN-beta exposure provide evidence from resources that were not constructed from the SLE contrasts. Together, these findings make an IFN-centred regulatory framing more credible than a gene-list description alone. They do not prove that STAT1 or STAT2 initiated the in vivo state, distinguish IFN-alpha from IFN-beta as the disease stimulus, or demonstrate direct TF binding.

The results also narrow several common SLE B-cell narratives. The naive-to-memory and APC/HLA axes are useful internal context but do not independently reproduce in GSE135779. The external atypical/low-naive signal cannot be labelled replication because it was absent in GSE174188. Likewise, stable broad `B_CONV` identity does not establish a discrete IFN-high subtype: interferon is treated as a continuous within-compartment program. The primary composition result remains a transparent negative boundary rather than being displaced by the secondary flare estimate.

The analysis has limitations. Public metadata did not provide a common set of sex, treatment and detailed clinical covariates across all contrasts. The adult external stratum was small, and two adult metadata donors lacked corresponding source matrices. The GSE174188 internal validation is not independent of the accession even after donor overlap is removed. The conventional-B mapping in GSE135779 relies on source labels and supports a broad analog rather than exact identity transfer. CollecTRI target activity depends on curated prior knowledge and gene coverage; the GSE23307 perturbation contains only two donors and was therefore interpreted descriptively. Direct binding, matched patient perturbation and prospective clinical validation remain outside the current evidence.

## Conclusions

The defensible advance is therefore specific: SLE is associated with an independently replicated IFN transcriptional shift within a disease-blind broad conventional-B compartment, accompanied by convergent IFN-centred regulatory and perturbational evidence. This conclusion is stronger than a single-cohort differential-expression result and narrower than a causal mechanism claim.

## List of abbreviations

**ASC:** antibody-secreting cell; **B_ASC:** disease-blind antibody-secreting-cell compartment; **B_CONV:** disease-blind broad conventional-B compartment; **FDR:** false discovery rate; **GEO:** Gene Expression Omnibus; **HC1/HC3:** heteroskedasticity-consistent covariance estimators; **IFN:** interferon; **ISG:** interferon-stimulated gene; **NES:** normalized enrichment score; **SLE:** systemic lupus erythematosus; **TF:** transcription factor; **TMM:** trimmed mean of M values; **UMI:** unique molecular identifier.

## Declarations

### Ethics approval and consent to participate

This secondary study used publicly available, de-identified human transcriptomic data and recruited no participants or new specimens. [[AUTHOR/INSTITUTION CONFIRMATION REQUIRED: state whether additional institutional review was not required, exempt or waived; provide committee name and reference number if applicable.]] Ethics approval and consent procedures for the source studies are reported in the original publications [1,2,13].

### Consent for publication

Not applicable; the manuscript contains no identifiable individual participant information.

### Availability of data and materials

The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [14-16]. Analysis scripts, machine-readable decisions and compact derived source-data tables are available in the project repository [17], frozen for this draft at commit `05d5d60`. [[PRE-SUBMISSION ACTION REQUIRED: add an open-source licence and an immutable Zenodo or equivalent archive DOI.]] Large recomputable matrices are not duplicated from their source repositories.

### Competing interests

[[AUTHOR COMPLETION REQUIRED: either declare all financial and non-financial competing interests by author initials or state, after all-author confirmation, that the authors declare no competing interests.]]

### Funding

[[AUTHOR COMPLETION REQUIRED: list funder names, grant numbers, recipient initials and funder roles, or state that the research received no specific funding.]]

### Authors' contributions

[[AUTHOR COMPLETION REQUIRED: map author initials to CRediT roles and confirm that all authors read and approved the final manuscript.]]

### Acknowledgements

[[AUTHOR COMPLETION REQUIRED: list contributors with permission, or state "Not applicable".]]

### Authors' information

Zhi Chen is an MSc student in Bioinformatics at The Chinese University of Hong Kong, Shenzhen. His research focuses on multi-omics integration, clinical cancer research and analysis of the tumour microenvironment. He holds a BSc in Biomedical Sciences from Queen Mary University of London and an MB in Clinical Medicine from Nanchang University. Teng Qi is an MSc student in Bioinformatics at The Chinese University of Hong Kong, Shenzhen.

## Additional files

**Additional file 1 (.docx):** Supplementary information. Extended governance, evidence-boundary and reproducibility tables supporting the disease-blind reconstruction, sample-level composition, pseudobulk replication and regulatory analyses.

**Additional file 2 (.zip):** Figure source data. Machine-readable CSV files underlying Figures 1-5, with a SHA-256 manifest.

## Figure legends

### Figure 1 | Disease-blind reconstruction defines the permissible identity scope

**a,** Audited GSE174188 hierarchy, hard-quality-control retention and separation of identity reconstruction from outcome inference. **b,** Median and minimum mapped adjusted Rand indices for five-, four-, three-state and repaired two-compartment policies across disease-blind resampling. **c,** Mapped adjusted Rand index and mapping agreement in each of 20 two-compartment resampling runs. **d,** Minimum and median state Jaccard indices for `B_CONV` and `B_ASC`; the frozen antibody-secreting marker support is shown. Cell-level summaries define identity stability and are not used as disease replicates.

### Figure 2 | Sample-level analysis does not support primary B_ASC enrichment

**a,** Observed `B_ASC` fractions for 43 control and 47 managed-SLE sample-cohort strata in the primary contrast; diamonds and bars show adjusted fractions and 95% confidence intervals. **b,** Primary, internal, donor-nonoverlap and secondary flare conditional odds ratios. **c,** Frozen primary estimate and mandatory minimum-cell, explicit non-B and residual-doublet sensitivities. **d,** Conditional odds ratios after each of 90 primary sample deletions; the horizontal line is the full estimate. The flare contrast is secondary and did not pass the frozen three-contrast false-discovery-rate rule.

### Figure 3 | GSE174188 B_CONV transcription prioritizes IFN/ISG remodeling

**a,** Effects and 95% confidence intervals for the four frozen programs in the primary contrast. **b,** IFN/ISG estimates across primary support thresholds, residual-risk restriction, internal replication, donor-nonoverlap internal replication and the secondary flare contrast. **c,** Gene-level log2 fold changes for the frozen IFN positive arm in the primary and donor-nonoverlap contrasts. **d,** IFN/ISG and prespecified platelet/ambient, ASC/UPR and pan-B specificity families in the primary and donor-nonoverlap contrasts. Program intervals use HC3 uncertainty; confirmatory q values use the frozen four-program family.

### Figure 4 | GSE135779 independently replicates the frozen IFN/ISG program

**a,** Childhood, combined, adult and support-threshold external IFN/ISG estimates. **b,** Discovery and internal GSE174188 estimates beside independent GSE135779 estimates. **c,** Effects for 4,410 genes tested in both primary datasets, with ten jointly tested frozen IFN genes highlighted; all ten were positive in both datasets despite low genome-wide correlation. **d,** Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Donors are the biological units in GSE135779; the adult estimate is directional only.

### Figure 5 | Convergent observational evidence supports IFN-centred regulation

**a,** Prespecified three-contrast, eight-regulator design, global 24-test Benjamini-Hochberg family and core target-robustness analyses. **b,** STAT1, STAT2, IRF7 and IRF9 CollecTRI activity slopes in the GSE174188 primary, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts. **c,** Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation controls. Asterisks indicate global 24-test q<0.05. **d,** M5911 Hallmark interferon-alpha response normalized enrichment scores from 10,000 gene-label permutations per contrast. **e,** Mean paired log2(x+1) effects for the 12-gene IFN positive arm after ex vivo IFN-beta exposure in primary B cells from two healthy donors; labels show positive genes. The perturbation panel is descriptive at n=2.

## References

1. Perez RK, Gordon MG, Subramaniam M, Kim MC, Hartoularos GC, Targ S, et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. Science. 2022;376(6589):eabf1970. doi:10.1126/science.abf1970.
2. Nehar-Belaid D, Hong S, Marches R, Chen G, Bolisetty M, Baisch J, et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. Nature Immunology. 2020;21(9):1094-1106. doi:10.1038/s41590-020-0743-0.
3. Crowell HL, Soneson C, Germain PL, Calini D, Collin L, Raposo C, et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. Nature Communications. 2020;11(1):6077. doi:10.1038/s41467-020-19894-4.
4. Squair JW, Gautier M, Kathe C, Anderson MA, James ND, Hutson TH, et al. Confronting false discoveries in single-cell differential expression. Nature Communications. 2021;12(1):5692. doi:10.1038/s41467-021-25960-2.
5. Büttner M, Ostner J, Müller CL, Theis FJ, Schubert B. scCODA is a Bayesian model for compositional single-cell data analysis. Nature Communications. 2021;12(1):6876. doi:10.1038/s41467-021-27150-6.
6. Wolf FA, Angerer P, Theis FJ. SCANPY: large-scale single-cell gene expression data analysis. Genome Biology. 2018;19(1):15. doi:10.1186/s13059-017-1382-0.
7. Korsunsky I, Millard N, Fan J, Slowikowski K, Zhang F, Wei K, et al. Fast, sensitive and accurate integration of single-cell data with Harmony. Nature Methods. 2019;16(12):1289-1296. doi:10.1038/s41592-019-0619-0.
8. Traag VA, Waltman L, van Eck NJ. From Louvain to Leiden: guaranteeing well-connected communities. Scientific Reports. 2019;9(1):5233. doi:10.1038/s41598-019-41695-z.
9. Robinson MD, McCarthy DJ, Smyth GK. edgeR : a Bioconductor package for differential expression analysis of digital gene expression data. Bioinformatics. 2010;26(1):139-140. doi:10.1093/bioinformatics/btp616.
10. Badia-i-Mompel P, Vélez Santiago J, Braunger J, Geiss C, Dimitrov D, Müller-Dott S, et al. decoupleR: ensemble of computational methods to infer biological activities from omics data. Bioinformatics Advances. 2022;2(1):vbac016. doi:10.1093/bioadv/vbac016.
11. Müller-Dott S, Tsirvouli E, Vazquez M, Ramirez Flores RO, Badia-i-Mompel P, Fallegger R, et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. Nucleic Acids Research. 2023;51(20):10934-10949. doi:10.1093/nar/gkad841.
12. Liberzon A, Birger C, Thorvaldsdóttir H, Ghandi M, Mesirov JP, Tamayo P. The Molecular Signatures Database Hallmark Gene Set Collection. Cell Systems. 2015;1(6):417-425. doi:10.1016/j.cels.2015.12.004.
13. van Boxel-Dezaire AHH, Zula JA, Xu Y, Ransohoff RM, Jacobberger JW, Stark GR. Major Differences in the Responses of Primary Human Leukocyte Subsets to IFN-beta. The Journal of Immunology. 2010;185(10):5888-5899. doi:10.4049/jimmunol.0902314.
14. National Center for Biotechnology Information. Gene Expression Omnibus series GSE174188. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188. Accessed 20 Aug 2026.
15. National Center for Biotechnology Information. Gene Expression Omnibus series GSE135779. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779. Accessed 20 Aug 2026.
16. National Center for Biotechnology Information. Gene Expression Omnibus series GSE23307. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE23307. Accessed 20 Aug 2026.
17. SLE B-cell remodeling analysis repository. GitHub. https://github.com/1209433622cz-maker/sle-bcell-remodeling. Accessed 20 Aug 2026.
