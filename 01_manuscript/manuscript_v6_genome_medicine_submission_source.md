# A donor-aware single-cell atlas and independent validation identify an ABC/APC-like B-cell program in systemic lupus erythematosus

**Article type:** Research

**Authors:** [AUTHOR ACTION REQUIRED: enter each author's full name in publication order]

**Affiliations:** [AUTHOR ACTION REQUIRED: enter numbered institutional addresses for all authors]

**Corresponding author:** [AUTHOR ACTION REQUIRED: enter name, full postal address, and email]

**Running title:** Donor-aware SLE B-cell remodeling

## Abstract

**Background:** B-cell dysregulation is a defining feature of systemic lupus erythematosus (SLE), yet the donor-level B-cell states that are reproducible across large public single-cell resources remain incompletely resolved.

**Methods:** We performed a donor-aware analysis of the Perez/GSE174188 CELLxGENE object, comprising 1,263,676 immune cells from 261 donors. Standardized annotations yielded 152,981 B-lineage cells from 259 donors. Because the CELLxGENE `X` matrix was preprocessed/scaled, state mapping used available low-dimensional representations, whereas marker refinement, donor-state expression summaries, and program scoring used count-like `adata.raw.X` where available. Findings were evaluated using donor-level abundance testing, sensitivity analysis excluding a platelet/ambient-RNA-high cluster, covariate-adjusted and centered log-ratio compositional models, donor-state pseudobulk, literature-informed signatures, independent validation in GSE135779 and GSE163121, and external B-lineage reference analysis in OneK1K/GSE196830.

**Results:** SLE was associated with expansion of an activated naive-like B-cell state and an atypical ABC/APC-like state, together with reduction of a memory-like state. These directions persisted after excluding the platelet/ambient-RNA-high cluster, adjusting for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count, and applying a centered log-ratio compositional analysis. In the fully adjusted compositional model, the ABC/APC-like association remained positive (beta 0.400; FDR 0.00397). Donor-state pseudobulk and literature-informed signatures linked this state to ABC/DN2, ZEB2-associated, APC/HLA, EBV/APC-like, IFN/ISG, and age-associated/atypical B-cell biology. In GSE135779, 32,179 metadata-defined B-subcluster cells from 56 donor/sample names independently supported SLE-associated IFN/ISG activity, the ZEB2/TBX21/ITGAX axis, and an expanded ABC/APC-high B-cell tail. OneK1K placed the prioritized programs in a 129,579-cell external B-lineage reference framework.

**Conclusions:** SLE B-cell remodeling is marked by an atypical ABC/APC-like program with antigen-presentation, ABC/DN2-associated, ZEB2/TBX21/ITGAX-axis, and interferon-linked features. Independent disease validation and external reference context strengthen this model while preserving the observational boundaries of public-data single-cell analysis.

## Keywords

systemic lupus erythematosus; B cells; single-cell RNA sequencing; donor-aware analysis; atypical B cells; independent validation

## Background

Systemic lupus erythematosus is driven in part by B-cell abnormalities that include autoreactive activation, autoantibody production, antigen presentation, interferon responsiveness, and altered memory or plasmablast differentiation [1, 2]. Single-cell RNA sequencing has refined this view by resolving disease-associated immune states, but treating cells as independent replicates can inflate evidence. For heterogeneous human cohorts, donor-aware inference and replicate-level aggregation are essential [3, 4]: a transcriptional state is most convincing when it is supported by donor-level abundance, donor-state expression, robustness to covariates and compositional constraints, and independent replication.

Several B-cell concepts are especially relevant to SLE, including activated-naive and DN2 cells connected through extrafollicular differentiation, CD11c-high/T-bet-positive autoreactive B cells, ZEB2-associated atypical B cells, APC-like B-cell programs, interferon-stimulated B cells, EBV-linked antigen-presenting autoreactive B cells, and age-associated B-cell biology [5, 6, 7, 8, 9, 10]. These concepts overlap but are not identical. A central challenge is therefore not simply to label one cluster as "ABC" or "APC", but to test whether a donor-level SLE-associated B-cell state carries a coherent, reproducible program across multiple evidence layers.

Here, we reanalyzed the public Perez/GSE174188 SLE CELLxGENE resource using a donor-aware B-lineage workflow [2]. We separated the study into discovery, validation, and reference-context layers. Perez/GSE174188 served as the discovery cohort; GSE135779 served as the main independent SLE validation cohort, with GSE163121 as smaller directional support; and OneK1K/GSE196830 served as a large external B-lineage reference resource [11, 12, 13]. This design tests not only whether an ABC/APC-like state is detectable, but whether its disease association and transcriptional axes remain credible under donor-aware and cross-dataset scrutiny.

## Methods

### Study design

This was a secondary observational analysis of public single-cell transcriptomic datasets organized into a discovery cohort, independent disease-validation cohorts, and an external B-lineage reference cohort. All donors and cells meeting the dataset-specific inclusion criteria were retained; no prospective sample-size calculation, randomization, or blinding was applicable. Biological donors, or donor/sample names where that was the highest-resolution identifier available, defined the inferential units. All tests were two-sided. The normal or healthy-control group was the reference, and Benjamini-Hochberg false-discovery-rate (FDR) correction was applied over the explicitly stated family of tests.

### Discovery dataset and B-lineage extraction

We analyzed the public Perez/GSE174188 CELLxGENE H5AD object [2]. B-lineage cells were selected using standardized `cell_type` annotations. Cells annotated as `B cell` or `plasmablast` were retained.

### Matrix handling and state mapping

The H5AD `X` matrix contained preprocessed/scaled values, including negative values, and was not treated as raw counts. For the B-lineage subset, a 15-nearest-neighbor graph was constructed from the source `X_pca` representation. Leiden clustering was performed at resolution 0.6, and the source `X_umap` representation was retained for visualization. No additional batch correction was applied. Count-like analyses, including marker refinement, donor-state pseudobulk expression, and literature-informed signatures, used `adata.raw.X`. Preliminary clusters were converted to manuscript state labels using source annotations, curated marker programs, raw-count marker summaries, ranked state markers, donor-level disease tests, and QC sensitivity; these labels were therefore treated as descriptive state definitions rather than externally trained cell-type predictions.

### Marker refinement, abundance testing, and QC sensitivity

Raw-count marker summaries were calculated from `adata.raw.X`, normalized to counts per 10,000, and transformed as log1p(CP10K). For ranked-marker annotation, up to 3,000 cells per state were selected using random seed 13, genes detected in fewer than 20 selected cells were removed, and the top 100 genes per state were ranked with Scanpy's variance-overestimating t-test after CP10K normalization and log1p transformation; Benjamini-Hochberg-adjusted values were retained. These cell-level marker results were used for annotation, not for disease-level inference. Donor-level state abundance was calculated as the fraction of each donor's B-lineage cells assigned to each refined state. Normal and SLE donor fractions were compared using two-sided Mann-Whitney U tests with Benjamini-Hochberg correction across states. Sensitivity analysis repeated donor-level tests after excluding the flagged platelet/ambient-RNA-high cluster from state counts and denominators.

### Donor-state pseudobulk and literature signatures

Cells were aggregated by donor, disease group, disease state, and refined B-cell state so that biological donors, rather than cells, defined the inferential units [3, 4]. Marker-gene counts were summed from `adata.raw.X`, normalized by total raw counts across all genes in the donor-state group, and transformed as log1p(CP10K). Program scores were calculated as the mean marker-level log1p(CP10K) value. Donor-state groups with fewer than 10 cells were excluded from focus-state comparisons. For each feature, the focus-state score was paired within donor with the mean score across that donor's other retained B-cell states; paired differences were tested using two-sided Wilcoxon signed-rank tests with Benjamini-Hochberg correction across features. Literature-informed panels were manually curated from the cited biological literature and prespecified compartment controls; they were not treated as verbatim published or independently validated signatures. Gene-level membership, source type, citation keys, DOI mappings, and provenance notes are reported in Supplementary Table S8. Panels were scored as positive-marker means or, for signed panels, positive-marker mean minus negative-marker mean and tested using the same paired-donor framework.

### Covariate sensitivity

Donor-level covariate sensitivity used ordinary least-squares (OLS) models with HC3 robust standard errors. Model tiers included an unadjusted disease-only model, a demographic model adjusted for age, sex, and self-reported ethnicity, and a full model additionally adjusted for simplified processing cohort and log10 donor B-lineage cell count. Continuous covariates were centered and scaled; categorical covariates were dummy encoded with one reference level. Models used complete cases for the variables in each specification. Benjamini-Hochberg correction was applied across the eight B-cell states within each model tier.

### Compositional abundance sensitivity

To evaluate constant-sum dependence in donor-level state fractions, we excluded the platelet/ambient-RNA-high QC state and constructed a donor-by-state count matrix for seven retained states. Counts were smoothed with a 0.5-cell pseudocount, converted to retained-state proportions, and transformed as CLR values by subtracting each donor's mean log proportion across retained states [14]. For comparison, raw fractions and CLR outcomes were modeled using the same unadjusted, demographic-adjusted, and full-adjusted OLS specifications with HC3 robust standard errors. Benjamini-Hochberg correction was applied across seven states within each analysis and model tier. Pseudocount sensitivity repeated the fully adjusted CLR analysis using count-scale values of 0.1, 0.5, and 1.0.

### Independent SLE validation

GSE163121 processed supplementary matrices were downloaded from GEO and parsed into a B-cell AnnData object [12]. Counts were normalized to log1p(CP10K), program scores were averaged within sample, and healthy-control and SLE samples were compared using two-sided Mann-Whitney U tests with Benjamini-Hochberg correction across program and high-fraction metrics. The ABC/APC-high threshold was the pooled healthy-control cell-level 95th percentile of the ABC/APC-focus score. Because this dataset contains only five donors, it was treated as directional validation.

For GSE135779, processed Matrix Market files were downloaded from GEO and aligned to extended cell-level metadata from the associated analysis resources [11]. Metadata-defined B-subcluster cells were matched to processed matrices within sample using the core barcode sequence preceding the dash. Counts were normalized to log1p(CP10K), and scores were averaged within donor/sample name. The ABC/APC-high threshold was the pooled healthy-control B-subcluster cell-level 95th percentile of the ABC/APC-focus score; the fraction above this fixed threshold was then calculated for each donor/sample name. Healthy-control and SLE donor/sample summaries were compared using two-sided Mann-Whitney U tests in all-donor/sample, childhood, and adult strata. Benjamini-Hochberg correction was applied across all program, high-fraction, and stratum tests. The all-donor/sample analysis was prespecified as the primary validation comparison; age-stratified results were supportive.

### OneK1K reference analysis

The OneK1K/GSE196830 CELLxGENE H5AD was downloaded and inspected [13]. B-lineage-like cells were selected from standardized `cell_type` annotations, retaining naive B cells, memory B cells, transitional-stage B cells, and plasmablasts. Target-gene raw counts from `X` were normalized as log1p(CP10K) using the full-library `nCount_RNA` metadata column. Program scores were calculated as the mean expression of available marker genes and summarized by cell type and donor. OneK1K was used only as external immune-reference context and not for SLE-versus-control inference.

### Software and reproducibility

Analyses were run in Python 3.11 using Scanpy 1.11.5, AnnData 0.12.17, pandas 2.3.3, NumPy 2.4.6, SciPy 1.17.1, statsmodels 0.14.6, Matplotlib 3.11.0, seaborn 0.13.2, scikit-learn 1.9.0, igraph 1.0.0, and leidenalg 0.12.0. Deterministic seeds are specified in the analysis scripts where subsampling was used. Scripts, runbooks, intermediate QC summaries, numerical consistency checks, and figure checks are retained with the submission archive.

### Generative AI-assisted tools

Generative AI-assisted tools supported code drafting, documentation, manuscript organization, and language editing. No generative AI system is listed as an author. All analysis scripts, outputs, scientific interpretations, and final text were reviewed by the authors, who retain full accountability for the work. [AUTHOR ACTION REQUIRED: confirm this disclosure accurately describes the final workflow before submission.]

## Results

### A donor-aware B-lineage atlas defines the discovery framework

The Perez/GSE174188 CELLxGENE object contained 1,263,676 immune cells from 261 donors [2]. We selected standardized `B cell` and `plasmablast` annotations, yielding 152,981 B-lineage cells from 259 donors, including 99 normal donors and 160 SLE donors. Initial matrix inspection showed that the CELLxGENE `X` values were preprocessed/scaled, including negative values. We therefore used provided PCA/UMAP representations for state mapping and used count-like `adata.raw.X` for raw-count marker refinement and donor-state expression summaries.

Leiden clustering resolved resting naive B cells, an activated SLE-naive-like state, memory-like states, an atypical ABC/APC-like state, a plasmablast/ASC state, and one small platelet/ambient-RNA-high cluster. The main donor-level disease remodeling pattern consisted of activated SLE-naive-like expansion, ABC/APC-like expansion, and memory-like B-cell reduction. Plasmablasts were transcriptionally well defined but were not the dominant donor-level abundance signal (Figs. 1 and 2; Supplementary Tables S1-S4).

### QC sensitivity separates biological signal from platelet/ambient RNA

Ranked raw-count markers identified a small B-lineage cluster enriched for platelet or ambient RNA-associated genes, including `PPBP`, `PF4`, `NRGN`, `TUBB1`, `RGS18`, `CAVIN2`, `GNG11`, and `SPARC`. We therefore treated this cluster as QC-limited and excluded it from central biological claims. Sensitivity analysis showed that the activated SLE-naive-like expansion, memory-like reduction, and ABC/APC-like expansion persisted directionally after excluding the flagged cluster from denominator calculations (Supplementary Fig. S1 and Supplementary Table S9).

### Donor-state expression supports an ABC/APC-like identity

Donor-state pseudobulk analysis linked the ABC/APC-like state to multiple biologically coherent programs. In paired within-donor comparisons against the mean of other retained B-cell states, the ABC/APC-like state showed higher ABC ranked program expression (delta 0.861; FDR 1.47e-26), ABC/DN2 expression (delta 0.441; FDR 1.47e-26), APC/HLA expression (delta 0.401; FDR 1.47e-26), and modest IFN-response expression (delta 0.051; FDR 2.29e-11; 153 paired donors). These results support the "ABC/APC-like" label as a composite program rather than a claim of a single canonical lineage identity (Fig. 3 and Supplementary Table S5).

### Covariate models preserve the core donor-level remodeling pattern

Because donor age and metadata composition differed between normal and SLE groups, we fit donor-level abundance models using unadjusted, demographic-adjusted, and full-adjusted specifications. In the full model adjusted for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count, the activated SLE-naive-like state remained expanded (beta 0.1491; FDR 2.41e-10), memory-like B I remained reduced (beta -0.0999; FDR 9.66e-07), and the ABC/APC-like state remained expanded (beta 0.0175; FDR 2.22e-02; Fig. 4 and Supplementary Table S6).

### Compositional analysis confirms the remodeling directions

Because donor-level state fractions are constrained to a constant sum, we next tested whether the core associations were robust to compositional analysis [14]. After excluding the flagged QC state, adding a 0.5-cell count-scale pseudocount, and applying a donor-wise centered log-ratio (CLR) transformation across seven retained states, the fully adjusted model again supported activated SLE-naive-like expansion (beta 0.668; FDR 8.12e-07), memory-like I reduction (beta -0.594; FDR 1.45e-08), and ABC/APC-like expansion (beta 0.400; FDR 3.97e-03). All three directions remained stable with pseudocounts of 0.1, 0.5, and 1.0, and the ABC/APC-like association remained significant throughout (FDR range 0.00238-0.0143). Thus, the central abundance pattern was not dependent on modeling each raw fraction in isolation (Supplementary Fig. S4 and Supplementary Table S13).

### Literature-informed signatures converge on atypical and antigen-presentation biology

Manually curated, literature-informed signature analysis supported the ABC/APC-like state from an independent biological angle. The focus state ranked first among refined B-cell states for ABC/DN2 core, ABC-low-naive-context, ZEB2-linked ABC, APC/HLA B-cell, EBV/APC-like B-cell, and age-associated/atypical B-cell panels [5, 6, 7, 8, 9, 10]. The TLR7/FTO innate-axis panel was not focus-state specific, so it is best treated as broader mechanistic context rather than a state-defining feature [10] (Fig. 5 and Supplementary Tables S7 and S8).

### Independent SLE validation supports the IFN and ZEB2/TBX21/ITGAX axes

We next tested whether the prioritized programs generalized beyond the discovery cohort. GSE163121 yielded 25,037 B cells from two healthy control and three SLE samples and was treated as directional validation because of its small donor count [12]. SLE samples showed directionally higher ZEB2/TBX21/ITGAX-axis scores, IFN/ISG scores, and ABC/APC-high fractions, but did not reproduce a global APC/HLA increase (Supplementary Fig. S3 and Supplementary Table S10).

GSE135779 provided the main independent validation layer [11]. After matching metadata-defined B-subcluster cells to processed matrices, 32,179 B-subcluster cells from 56 donor/sample names were retained, including 16 healthy control and 40 SLE donor/sample names. Donor/sample-level testing validated IFN/ISG activity in SLE B-subcluster cells (delta 0.2810; FDR 8.72e-04) and the ZEB2/TBX21/ITGAX axis (delta 0.0351; FDR 4.48e-02). A modest Plasmablast/ASC score increase also reached statistical support (delta 0.0246; FDR 4.48e-02), but was treated as a secondary differentiation signal because validation cells were selected using a broad metadata-defined B-subcluster label. The ABC/APC-high B-subcluster fraction was higher in SLE (delta 0.0567; FDR 7.88e-02). ABC/DN2, ABC/APC-focus, FCRL-axis, and APC/HLA scores were directionally higher in SLE but did not reach FDR < 0.05 in the all-donor/sample analysis. Thus, GSE135779 validates the IFN and ZEB2/TBX21/ITGAX components of the model and supports an expanded high-scoring ABC/APC-like tail, while APC/HLA should be described as directionally supportive rather than independently decisive (Fig. 6 and Supplementary Table S11).

### OneK1K provides external B-lineage reference context

To test whether the prioritized programs mapped onto a large independent B-lineage reference structure, we analyzed OneK1K/GSE196830 [13]. The CELLxGENE H5AD contained 1,248,980 PBMCs and 35,528 features. We identified 129,579 B-lineage-like cells across 981 donors, including naive B cells, memory B cells, transitional stage B cells, and plasmablasts. All current manuscript genes were present.

OneK1K showed broad HLA/CD74 and APC/HLA program expression in non-plasmablast B cells, the expected plasmablast/ASC enrichment in plasmablasts, and the highest mean ZEB2/TBX21/ITGAX-axis score in transitional B cells. These data were not used to estimate SLE-vs-control effects because OneK1K is not a matched disease-validation cohort. Instead, they provide external reference context for the compartmental plausibility of the programs prioritized in discovery and validation (Supplementary Fig. S2 and Supplementary Table S12).

## Discussion

This study identifies an expanded atypical ABC/APC-like B-cell state as a candidate component of SLE B-cell remodeling. The claim is supported across donor-level abundance, raw-count markers, QC sensitivity, covariate-adjusted and CLR compositional models, donor-state pseudobulk, literature-informed signatures, independent SLE validation, and external B-lineage reference context. This evidence stack is stronger than a cluster-labeling analysis alone, because each layer addresses a different reviewer concern: disease association, technical artifact, covariate imbalance, compositional dependence, biological identity, cross-dataset generalization, and reference plausibility.

The model is intentionally composite. The focus state is not presented as a pure DN2 lineage, pure APC population, or plasmablast precursor. Instead, it combines FCRL, ZEB2/TBX21/ITGAX, antigen-presentation, ABC/DN2-associated, and interferon-linked features. This framing is important because GSE135779 validates IFN/ISG activity and the ZEB2/TBX21/ITGAX axis more strongly than it validates the global APC/HLA score. The discovery data support APC/HLA robustly, but independent validation suggests that antigen-presentation biology should be framed as part of the ABC/APC-like program rather than as a fully replicated disease-wide effect.

The results also argue against a purely plasmablast-centric interpretation of this cohort. Plasmablasts are clearly resolved, and OneK1K confirms their expected antibody-secreting-cell program, but the dominant donor-level discovery signals were activated naive-like expansion, memory-like reduction, and ABC/APC-like expansion. This does not diminish plasmablast biology in SLE; rather, it positions the ABC/APC-like state as an additional disease-associated B-cell program that may contribute to antigen presentation and inflammatory amplification.

Several limitations remain. The study relies on public processed datasets and is observational. The primary CELLxGENE `X` matrix was preprocessed/scaled, requiring careful separation of embedding-based state mapping from raw-count expression summaries. CLR coefficients are relative to the geometric mean abundance of retained states and cannot establish absolute cell-number changes. Validation was performed using public cohorts rather than prospective samples, and not every composite program component replicated equally across datasets. OneK1K provides reference context rather than disease validation. Future studies should test whether the ABC/APC-like state has antigen specificity, genetic regulation, treatment-response relevance, or functional antigen-presenting capacity in prospective SLE cohorts and perturbational systems.

## Conclusions

Overall, the data support a donor-aware model in which SLE B-cell remodeling includes activated naive-like expansion, memory-like redistribution, and an atypical ABC/APC-like program marked by FCRL genes, ZEB2/TBX21/ITGAX activity, antigen-presentation features, and interferon-linked activation.

## List of abbreviations

ABC, age-associated B cell; APC, antigen-presenting cell; ASC, antibody-secreting cell; CLR, centered log-ratio; CP10K, counts per 10,000; FDR, false discovery rate; GEO, Gene Expression Omnibus; HC, healthy control; IFN, interferon; ISG, interferon-stimulated gene; OLS, ordinary least squares; PBMC, peripheral blood mononuclear cell; SLE, systemic lupus erythematosus.

## Declarations

### Ethics approval and consent to participate

This study was a secondary analysis of publicly available de-identified human data and involved no new participant recruitment, intervention, or access to direct identifiers. Ethics approval and informed consent for the primary studies were reported by the original investigators. [AUTHOR ACTION REQUIRED: confirm with the corresponding institution whether this secondary analysis is exempt from additional review or requires a waiver statement; add the committee name and reference number if applicable.]

### Consent for publication

Not applicable.

### Availability of data and materials

The public datasets analyzed in this study are available from the NCBI Gene Expression Omnibus under accession numbers GSE174188 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188), GSE135779 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779), GSE163121 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE163121), and GSE196830 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE196830), with corresponding CELLxGENE resources used where stated. Analysis-ready results are included in Supplementary Tables S1-S13. Large source H5AD and RAW archives are not redistributed because they remain available from the source repositories. Reproducible analysis scripts are included in the submission archive. [AUTHOR ACTION REQUIRED: before submission, archive the final code and compact derived data in a persistent public repository and insert its DOI or stable URL here.]

### Competing interests

[AUTHOR ACTION REQUIRED: enter the authors' financial and non-financial competing-interest declaration, or state "The authors declare that they have no competing interests".]

### Funding

[AUTHOR ACTION REQUIRED: list every grant and funder, award numbers, recipient initials, and the funders' roles; state explicitly if the funders had no role.]

### Authors' contributions

[AUTHOR ACTION REQUIRED: provide contribution statements using author initials and CRediT roles. End with confirmation that all authors read and approved the final manuscript.]

### Acknowledgements

[AUTHOR ACTION REQUIRED: acknowledge eligible non-author contributors with permission, or state "Not applicable".]

### Authors' information

Not applicable.

## Figure legends

### Figure 1. Dataset overview and B-lineage analysis workflow

**a,** Overview of the analysis workflow. We used the public Perez/GSE174188 CELLxGENE H5AD object containing 1,263,676 immune cells from 261 donors. B-lineage cells were selected using the standardized `cell_type` annotation (`B cell` or `plasmablast`), yielding 152,981 B-lineage cells from 259 donors. State mapping used the provided PCA/UMAP representation because the CELLxGENE `X` matrix is scaled/preprocessed, while marker refinement used the count-like `adata.raw.X` matrix.

**b,** Major cell-type composition in the source CELLxGENE object. B cells represented 151,570 cells in the source object, with plasmablasts additionally captured during B-lineage extraction.

**c,** Donor counts by disease in the full source object and B-lineage subset. The source object included 99 normal donors and 162 SLE donors; after B-lineage extraction, 99 normal donors and 160 SLE donors retained B-lineage cells.

**d,** Composition of the B-lineage subset. The subset consisted of 151,570 B cells and 1,411 plasmablasts.

**e,** Sizes of marker-refined B-cell states used for downstream analysis. Refined labels distinguish resting naive B cells, activated SLE-naive-like B cells, memory-like states, atypical ABC/APC-like B cells, a flagged platelet/ambient-high cluster, and plasmablast/antibody-secreting cells.

**f,** Analysis guardrails. The scaled/preprocessed `X` matrix was not treated as raw counts; marker refinement used `adata.raw.X`; and a small platelet/ambient-high cluster was excluded from central biological claims. Donor-level state-fraction testing used 99 normal and 160 SLE donors.

### Figure 2. Refined B-cell state remodeling in systemic lupus erythematosus

**a,** UMAP of 152,981 Perez/GSE174188 B-lineage cells colored by marker-refined state. Leiden clusters were relabeled using public metadata, raw-count markers, and donor-level disease tests. One platelet/ambient-RNA-high cluster was flagged for QC.

**b,** Raw-count marker dot plot. Color indicates mean log1p(CP10K) expression from `adata.raw.X`; size indicates the expressing-cell fraction. The ABC/APC-like state expressed `FCRL5`, `FCRL3`, `ZEB2`, `CD74`, and HLA class II genes. The activated SLE-naive-like state retained `TCL1A` with `CD69`, `JUNB`, and `FOS`; the flagged cluster expressed `PPBP`, `PF4`, and `TUBB1`.

**c,** Donor-level abundance of selected states. Each point is one donor; boxes summarize fractions of B-lineage cells. FDR values are from two-sided Mann-Whitney U tests with Benjamini-Hochberg correction across states.

**d,** Sensitivity analysis comparing SLE-normal mean-fraction differences before and after excluding the flagged state. Activated SLE-naive-like expansion, memory-like B I reduction, and ABC/APC-like expansion remained significant.

### Figure 3. Donor-aware expression supports an atypical ABC/APC-like B-cell state in SLE

**a,** UMAP visualization of the B-lineage atlas highlighting the atypical ABC/APC-like B-cell state. Other B-cell states are shown in light grey and the platelet/ambient-RNA-high cluster is shown as a flagged QC state.

**b,** Paired donor-state pseudobulk scores for the ABC/APC-like state versus each donor's mean of other retained states. Scores used count-like `adata.raw.X`, donor-state aggregation, full-library CP10K normalization, and log1p transformation. Groups with fewer than 10 cells and the flagged state were excluded. Two-sided Wilcoxon signed-rank tests across 153 paired donors were Benjamini-Hochberg corrected. Deltas were 0.861 for ABC ranked, 0.441 for ABC/DN2, 0.401 for APC/HLA (all FDR 1.47e-26), and 0.051 for IFN response (FDR 2.29e-11).

**c,** Donor-level ABC/APC-like abundance. Each point is one donor. The state was expanded in SLE in the original test (FDR 2.67e-05) and after flagged-state exclusion (FDR 1.68e-05).

**d,** Top paired pseudobulk marker effects. Bars show mean within-donor log1p(CP10K) differences between the focus and comparator states; positive effects included `FCRL5`, `FCRL3`, `ZEB2`, B-cell markers, and HLA class II genes.

**e,** Descriptive ABC/APC-like program summaries by clinical state among groups passing the 10-cell threshold. The treated group contained four donor-state observations and warrants caution.

### Figure 4. Covariate sensitivity supports donor-level B-cell state remodeling in SLE

**a,** Donor age distribution in the B-lineage subset. Age was parsed from the CELLxGENE `development_stage` metadata. Normal donors and SLE donors showed age imbalance, motivating covariate-adjusted sensitivity analysis.

**b,** Categorical covariate balance. Bars show the SLE-minus-normal difference in donor proportions for processing-cohort and self-reported-ethnicity categories. Donors represented in multiple processing cohorts were collapsed into a `multiple` category.

**c,** Disease-effect sensitivity for three core states. Points and lines show SLE coefficients and 95% confidence intervals from unadjusted, demographic-adjusted, and full models. The full model included age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count. Continuous covariates were centered and scaled. All three effects remained directionally stable.

**d,** Signed adjusted significance across all states and models. Positive values indicate higher fractions in SLE and negative values lower fractions; values are signed -log10(FDR), Benjamini-Hochberg corrected within each model.

In the full model, SLE coefficients were 0.1491 for activated SLE-naive-like (FDR 2.41e-10), -0.0999 for memory-like B I (FDR 9.66e-07), and 0.0175 for ABC/APC-like cells (95% CI 0.0045-0.0305; FDR 2.22e-02).

### Figure 5. Literature-informed signatures support the ABC/APC-like state identity

**a,** Heatmap of literature-informed B-cell signatures across refined B-cell states. Scores were calculated from donor-state pseudobulk expression using count-like `adata.raw.X`. Values are row-scaled z-scores across states. The atypical ABC/APC-like B-cell state showed high ABC/DN2, ZEB2-linked ABC, APC/HLA, EBV/APC-like, and age-associated/atypical B-cell signatures.

**b,** Mean paired donor differences between the ABC/APC-like state and each donor's mean of other retained states for pathogenic or mechanistically prioritized signatures. The flagged state and donor-state groups with fewer than 10 cells were excluded; 153 donors were paired. Differences were tested by two-sided Wilcoxon signed-rank tests with Benjamini-Hochberg correction. Deltas were 0.924 for age-associated/atypical, 0.845 for ABC-low-naive-context, 0.685 for ZEB2-linked ABC, 0.441 for ABC/DN2, 0.401 for APC/HLA, and 0.258 for EBV/APC-like signatures (all FDR 1.27e-26). IFN/ISG was modestly higher (delta 0.043; FDR 1.28e-09); TLR7/FTO was not focus-state specific (delta -0.007; FDR 0.137).

**c,** Mean paired donor differences for naive, memory, plasmablast/ASC, and platelet/ambient control signatures. These controls define expected negative or non-specific relationships with the focus state.

**d,** Specificity rank across refined states. Rank 1 denotes the highest mean score. The ABC/APC-like state ranked first for ABC/DN2, ABC-low-naive-context, ZEB2-linked ABC, APC/HLA, EBV/APC-like, and age-associated signatures.

### Figure 6. GSE135779 provides large independent validation of SLE B-cell program remodeling

**a,** Overview of the independent validation cohort. GSE135779 contains childhood and adult SLE/control PBMC cohorts. Processed Matrix Market files from GEO were parsed and aligned to the extended cell-level metadata. Metadata-defined B-subcluster cells were retained for validation.

**b,** Number of healthy control and SLE donor/sample names represented in adult and childhood strata after matrix-metadata matching.

**c,** Donor/sample-level mean B-subcluster program scores. Programs were scored using log1p(CP10K) expression across present marker genes. The all-donor/sample analysis showed directionally higher ABC/APC-focus, ABC/DN2, APC/HLA, ZEB2/TBX21/ITGAX-axis, and IFN/ISG scores in SLE. The prespecified focus axes with strongest support were IFN/ISG and ZEB2/TBX21/ITGAX. A modest Plasmablast/ASC increase, not shown in this panel, is reported in Supplementary Table S11 and treated as a secondary differentiation signal (delta 0.0246; FDR 4.48e-02).

**d,** Fraction of B-subcluster cells exceeding the healthy-control 95th percentile for the ABC/APC-focus score. SLE donor/sample names showed a higher ABC/APC-high B-subcluster fraction in the all-donor/sample analysis.

**e,** Marker expression summary in metadata-defined B-subcluster cells. Dot color indicates mean log1p(CP10K) expression and dot size indicates the fraction of cells with nonzero expression.

This independent validation supports a model in which SLE B-cell remodeling includes increased IFN/ISG activity, a ZEB2/TBX21/ITGAX-associated axis, and a larger high-scoring ABC/APC-like B-cell tail. APC/HLA score differences were directionally positive but not statistically significant in this validation cohort, and should be described as supportive but not independently decisive.

## Supplementary figure legends

### Supplementary Figure S1. QC of the platelet/ambient-RNA-high B-cell cluster

**a,** UMAP visualization highlighting the flagged platelet/ambient-RNA-high B-cell cluster within the B-lineage atlas. Other B-lineage cells are shown in light grey.

**b,** Top raw-count ranked markers for the flagged cluster. The highest-ranked genes included platelet or ambient RNA-associated markers such as `PPBP`, `PF4`, `NRGN`, `TUBB1`, `RGS18`, `CAVIN2`, `GNG11`, and `SPARC`, supporting QC-limited interpretation of this cluster.

**c,** Selected B-cell identity and platelet/ambient marker expression in the flagged cluster. The cluster retained B-cell identity marker expression, including `MS4A1`, `CD79A`, and `CD74`, but also showed detectable platelet/ambient marker expression. Bar height represents mean log1p(CP10K) expression from `adata.raw.X`; percentage labels indicate the fraction of cells expressing each marker.

**d,** Donor-level abundance of the flagged cluster in normal and SLE donors. Although this cluster was statistically higher in SLE donors (FDR 5.10e-05), its marker profile argues against treating it as a central biological B-cell state.

**e,** Sensitivity analysis after excluding the flagged cluster. Activated SLE-naive-like expansion, memory-like B-cell reduction, and ABC/APC-like expansion remained directionally stable.

### Supplementary Figure S2. OneK1K reference context for prioritized SLE B-cell programs

OneK1K/GSE196830 was used as an external PBMC immune-reference resource to contextualize the B-cell programs prioritized in the discovery and disease-validation analyses. B-lineage-like cells were identified from the CELLxGENE `cell_type` annotation and included naive B cells, memory B cells, transitional stage B cells, and plasmablasts.

**a,** Heatmap showing standardized mean program scores across OneK1K B-lineage compartments. Scores were calculated from target-gene raw counts in `X` after log1p(CP10K) normalization using the full-library `nCount_RNA` metadata column. Program scores are displayed as z-scores across B-lineage compartments for visualization.

**b,** Dot plot showing marker-gene expression across OneK1K B-lineage compartments. Color indicates mean log1p(CP10K) expression and dot size indicates the percentage of cells with detectable expression.

This analysis is intended as external immune-reference context rather than SLE-vs-control validation, because OneK1K is not a matched SLE case-control cohort.

### Supplementary Figure S3. Directional B-cell validation in GSE163121

**a,** Overview of the independent validation dataset. GSE163121 contains single-cell RNA-seq of B cells isolated from PBMCs from two healthy controls and three SLE patients. CellRanger filtered matrices were downloaded from GEO and parsed into an AnnData object for program scoring.

**b,** Number of B cells recovered per sample after parsing the processed matrices.

**c,** Sample-level mean program scores across selected B-cell programs. Scores were calculated as mean log1p(CP10K) expression across present genes in each curated program. The small donor count limits formal statistical power.

**d,** Fraction of B cells exceeding the healthy-control 95th percentile for the ABC/APC-focus composite score. This tail-based analysis asks whether SLE samples contain a larger high-scoring compartment even when whole-sample mean scores are heterogeneous.

**e,** Marker expression by disease group for selected ABC/DN2, APC/HLA, B-cell identity, IFN/ISG, and plasmablast-associated markers. Dot color indicates mean log1p(CP10K) expression and dot size indicates fraction of cells with nonzero expression.

This dataset is interpreted as directional external validation and boundary evidence. It supports higher SLE B-cell expression of the ZEB2/TBX21/ITGAX and IFN axes, but does not show a global increase in APC/HLA score. Because GSE163121 includes only five donors, the result should not be treated as a fully powered donor-level replication cohort.

### Supplementary Figure S4. Compositional sensitivity of donor-level B-cell state abundance

**a,** Donor-level centered log-ratio (CLR) abundance distributions for the three core disease-associated states. Counts for seven retained states were smoothed with a 0.5-cell pseudocount after excluding the platelet/ambient-RNA-high QC state, converted to retained-state proportions, and transformed donor-wise. Points represent donors; boxes summarize normal and SLE distributions.

**b,** Fully adjusted SLE coefficients and 95% confidence intervals for CLR abundance across all seven retained states. Models used HC3 robust standard errors and adjusted for age, sex, self-reported ethnicity, simplified processing cohort, and log10 donor B-lineage cell count. Bold labels denote the three prespecified core states.

**c,** Direction and significance across raw-fraction and CLR models. Colors show signed -log10(FDR), with positive values indicating higher abundance in SLE and negative values lower abundance. FDR values were Benjamini-Hochberg corrected across seven states within each analysis and model tier.

The fully adjusted CLR coefficients were 0.668 for activated SLE-naive-like cells (FDR 8.12e-07), -0.594 for memory-like I cells (FDR 1.45e-08), and 0.400 for ABC/APC-like cells (FDR 3.97e-03). Directions were unchanged with count-scale pseudocounts of 0.1, 0.5, and 1.0.

## References

1. Tipton CM, Fucile CF, Darce J, Chida A, Ichikawa T, Gregoretti I, et al. Diversity, cellular origin and autoreactivity of antibody-secreting cell population expansions in acute systemic lupus erythematosus. Nature Immunology. 2015;16:755-765. https://doi.org/10.1038/ni.3175.

2. Perez RK, Gordon MG, Subramaniam M, Kim MC, Hartoularos GC, Targ S, et al. Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus. Science. 2022;376. https://doi.org/10.1126/science.abf1970.

3. Crowell HL, Soneson C, Germain PL, Calini D, Collin L, Raposo C, et al. muscat detects subpopulation-specific state transitions from multi-sample multi-condition single-cell transcriptomics data. Nature Communications. 2020;11:6077. https://doi.org/10.1038/s41467-020-19894-4.

4. Squair JW, Gautier M, Kathe C, Anderson MA, James ND, Hutson TH, et al. Confronting false discoveries in single-cell differential expression. Nature Communications. 2021;12:5692. https://doi.org/10.1038/s41467-021-25960-2.

5. Jenks SA, Cashman KS, Zumaquero E, Marigorta UM, Patel AV, Wang X, et al. Distinct Effector B Cells Induced by Unregulated Toll-like Receptor 7 Contribute to Pathogenic Responses in Systemic Lupus Erythematosus. Immunity. 2018;49:725-739.e6. https://doi.org/10.1016/j.immuni.2018.08.015.

6. Wang S, Wang J, Kumar V, Karnell JL, Naiman B, Gross PS, et al. IL-21 drives expansion and plasma cell differentiation of autoreactive CD11chiT-bet+ B cells in SLE. Nature Communications. 2018;9:1758. https://doi.org/10.1038/s41467-018-03750-7.

7. Sanz I, Wei C, Jenks SA, Cashman KS, Tipton C, Woodruff MC, et al. Challenges and Opportunities for Consistent Classification of Human B Cell and Plasma Cell Populations. Frontiers in Immunology. 2019;10:2458. https://doi.org/10.3389/fimmu.2019.02458.

8. Dai D, Gu S, Han X, Ding H, Jiang Y, Zhang X, et al. The transcription factor ZEB2 drives the formation of age-associated B cells. Science. 2024;383:413-421. https://doi.org/10.1126/science.adf8531.

9. Younis S, Moutusy SI, Rasouli S, Jahanbani S, Pandit M, Wu X, et al. Epstein-Barr virus reprograms autoreactive B cells as antigen-presenting cells in systemic lupus erythematosus. Science Translational Medicine. 2025;17. https://doi.org/10.1126/scitranslmed.ady0210.

10. Zeng Q, Li L, Li X, Qin L, Feng T, Zhu Y, et al. The m6A demethylase FTO links TLR7 to mitochondrial oxidation driving age-associated B cell formation in systemic lupus erythematosus. Science Translational Medicine. 2025;17. https://doi.org/10.1126/scitranslmed.adu6015.

11. Nehar-Belaid D, Hong S, Marches R, Chen G, Bolisetty M, Baisch J, et al. Mapping systemic lupus erythematosus heterogeneity at the single-cell level. Nature Immunology. 2020;21:1094-1106. https://doi.org/10.1038/s41590-020-0743-0.

12. Bhamidipati K, Silberstein JL, Chaichian Y, Baker MC, Lanz TV, Zia A, et al. CD52 Is Elevated on B cells of SLE Patients and Regulates B Cell Function. Frontiers in Immunology. 2021;11. https://doi.org/10.3389/fimmu.2020.626820.

13. Yazar S, Alquicira-Hernandez J, Wing K, Senabouth A, Gordon MG, Andersen S, et al. Single-cell eQTL mapping identifies cell type-specific genetic control of autoimmune disease. Science. 2022;376. https://doi.org/10.1126/science.abf3041.

14. Büttner M, Ostner J, Müller CL, Theis FJ, Schubert B. scCODA is a Bayesian model for compositional single-cell data analysis. Nature Communications. 2021;12:6876. https://doi.org/10.1038/s41467-021-27150-6.
