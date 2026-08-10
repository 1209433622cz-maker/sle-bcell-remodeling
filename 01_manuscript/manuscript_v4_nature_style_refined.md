# A donor-aware single-cell atlas and independent validation identify an ABC/APC-like B-cell program in systemic lupus erythematosus

## Abstract

**Background:** B-cell dysregulation is a defining feature of systemic lupus erythematosus (SLE), yet the donor-level B-cell states that are reproducible across large public single-cell resources remain incompletely resolved.

**Methods:** We performed a donor-aware analysis of the Perez/GSE174188 CELLxGENE object, comprising 1,263,676 immune cells from 261 donors [@Perez2022]. Standardized annotations yielded 152,981 B-lineage cells from 259 donors. Because the CELLxGENE `X` matrix was preprocessed/scaled, state mapping used available low-dimensional representations, whereas marker refinement, donor-state expression summaries, and program scoring used count-like `adata.raw.X` where available. Findings were evaluated using donor-level abundance testing, sensitivity analysis excluding a platelet/ambient-RNA-high cluster, covariate-adjusted and centered log-ratio compositional models, donor-state pseudobulk, literature-informed signatures, independent validation in GSE135779 and GSE163121, and external B-lineage reference analysis in OneK1K/GSE196830 [@NeharBelaid2020; @Bhamidipati2021; @Yazar2022].

**Results:** SLE was associated with expansion of an activated naive-like B-cell state and an atypical ABC/APC-like state, together with reduction of a memory-like state. These directions persisted after excluding the platelet/ambient-RNA-high cluster, adjusting for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count, and applying a centered log-ratio compositional analysis. In the fully adjusted compositional model, the ABC/APC-like association remained positive (beta 0.400; FDR 0.00397). Donor-state pseudobulk and literature-informed signatures linked this state to ABC/DN2, ZEB2-associated, APC/HLA, EBV/APC-like, IFN/ISG, and age-associated/atypical B-cell biology [@Jenks2018; @Wang2018; @Dai2024; @Younis2025; @Zeng2025]. In GSE135779, 32,179 metadata-defined B-subcluster cells from 56 donor/sample names independently supported SLE-associated IFN/ISG activity, the ZEB2/TBX21/ITGAX axis, and an expanded ABC/APC-high B-cell tail. OneK1K placed the prioritized programs in a 129,579-cell external B-lineage reference framework.

**Conclusions:** SLE B-cell remodeling is marked by an atypical ABC/APC-like program with antigen-presentation, ABC/DN2-associated, ZEB2/TBX21/ITGAX-axis, and interferon-linked features. Independent disease validation and external reference context strengthen this model while preserving the observational boundaries of public-data single-cell analysis.

## Introduction

Systemic lupus erythematosus is driven in part by B-cell abnormalities that include autoreactive activation, autoantibody production, antigen presentation, interferon responsiveness, and altered memory or plasmablast differentiation [@Tipton2015; @Perez2022]. Single-cell RNA sequencing has refined this view by resolving disease-associated immune states, but treating cells as independent replicates can inflate evidence. For heterogeneous human cohorts, donor-aware inference and replicate-level aggregation are essential [@Crowell2020; @Squair2021]: a transcriptional state is most convincing when it is supported by donor-level abundance, donor-state expression, robustness to covariates and compositional constraints, and independent replication.

Several B-cell concepts are especially relevant to SLE, including activated-naive and DN2 cells connected through extrafollicular differentiation, CD11c-high/T-bet-positive autoreactive B cells, ZEB2-associated atypical B cells, APC-like B-cell programs, interferon-stimulated B cells, EBV-linked antigen-presenting autoreactive B cells, and age-associated B-cell biology [@Jenks2018; @Wang2018; @Sanz2019; @Dai2024; @Younis2025; @Zeng2025]. These concepts overlap but are not identical. A central challenge is therefore not simply to label one cluster as "ABC" or "APC", but to test whether a donor-level SLE-associated B-cell state carries a coherent, reproducible program across multiple evidence layers.

Here, we reanalyzed the public Perez/GSE174188 SLE CELLxGENE resource using a donor-aware B-lineage workflow [@Perez2022]. We separated the study into discovery, validation, and reference-context layers. Perez/GSE174188 served as the discovery cohort; GSE135779 served as the main independent SLE validation cohort, with GSE163121 as smaller directional support; and OneK1K/GSE196830 served as a large external B-lineage reference resource [@NeharBelaid2020; @Bhamidipati2021; @Yazar2022]. This design tests not only whether an ABC/APC-like state is detectable, but whether its disease association and transcriptional axes remain credible under donor-aware and cross-dataset scrutiny.

## Results

### A donor-aware B-lineage atlas defines the discovery framework

The Perez/GSE174188 CELLxGENE object contained 1,263,676 immune cells from 261 donors [@Perez2022]. We selected standardized `B cell` and `plasmablast` annotations, yielding 152,981 B-lineage cells from 259 donors, including 99 normal donors and 160 SLE donors. Initial matrix inspection showed that the CELLxGENE `X` values were preprocessed/scaled, including negative values. We therefore used provided PCA/UMAP representations for state mapping and used count-like `adata.raw.X` for raw-count marker refinement and donor-state expression summaries.

Leiden clustering resolved resting naive B cells, an activated SLE-naive-like state, memory-like states, an atypical ABC/APC-like state, a plasmablast/ASC state, and one small platelet/ambient-RNA-high cluster. The main donor-level disease remodeling pattern consisted of activated SLE-naive-like expansion, ABC/APC-like expansion, and memory-like B-cell reduction. Plasmablasts were transcriptionally well defined but were not the dominant donor-level abundance signal (Figs. 1 and 2; Supplementary Tables S1-S4).

### QC sensitivity separates biological signal from platelet/ambient RNA

Ranked raw-count markers identified a small B-lineage cluster enriched for platelet or ambient RNA-associated genes, including `PPBP`, `PF4`, `NRGN`, `TUBB1`, `RGS18`, `CAVIN2`, `GNG11`, and `SPARC`. We therefore treated this cluster as QC-limited and excluded it from central biological claims. Sensitivity analysis showed that the activated SLE-naive-like expansion, memory-like reduction, and ABC/APC-like expansion persisted directionally after excluding the flagged cluster from denominator calculations (Supplementary Fig. S1 and Supplementary Table S9).

### Donor-state expression supports an ABC/APC-like identity

Donor-state pseudobulk analysis linked the ABC/APC-like state to multiple biologically coherent programs. In paired within-donor comparisons against the mean of other retained B-cell states, the ABC/APC-like state showed higher ABC ranked program expression (delta 0.861; FDR 1.47e-26), ABC/DN2 expression (delta 0.441; FDR 1.47e-26), APC/HLA expression (delta 0.401; FDR 1.47e-26), and modest IFN-response expression (delta 0.051; FDR 2.29e-11; 153 paired donors). These results support the "ABC/APC-like" label as a composite program rather than a claim of a single canonical lineage identity (Fig. 3 and Supplementary Table S5).

### Covariate models preserve the core donor-level remodeling pattern

Because donor age and metadata composition differed between normal and SLE groups, we fit donor-level abundance models using unadjusted, demographic-adjusted, and full-adjusted specifications. In the full model adjusted for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count, the activated SLE-naive-like state remained expanded (beta 0.1491; FDR 2.41e-10), memory-like B I remained reduced (beta -0.0999; FDR 9.66e-07), and the ABC/APC-like state remained expanded (beta 0.0175; FDR 2.22e-02; Fig. 4 and Supplementary Table S6).

### Compositional analysis confirms the remodeling directions

Because donor-level state fractions are constrained to a constant sum, we next tested whether the core associations were robust to compositional analysis [@Buttner2021]. After excluding the flagged QC state, adding a 0.5-cell count-scale pseudocount, and applying a donor-wise centered log-ratio (CLR) transformation across seven retained states, the fully adjusted model again supported activated SLE-naive-like expansion (beta 0.668; FDR 8.12e-07), memory-like I reduction (beta -0.594; FDR 1.45e-08), and ABC/APC-like expansion (beta 0.400; FDR 3.97e-03). All three directions remained stable with pseudocounts of 0.1, 0.5, and 1.0, and the ABC/APC-like association remained significant throughout (FDR range 0.00238-0.0143). Thus, the central abundance pattern was not dependent on modeling each raw fraction in isolation (Supplementary Fig. S4 and Supplementary Table S13).

### Literature-informed signatures converge on atypical and antigen-presentation biology

Manually curated, literature-informed signature analysis supported the ABC/APC-like state from an independent biological angle. The focus state ranked first among refined B-cell states for ABC/DN2 core, ABC-low-naive-context, ZEB2-linked ABC, APC/HLA B-cell, EBV/APC-like B-cell, and age-associated/atypical B-cell panels [@Jenks2018; @Wang2018; @Sanz2019; @Dai2024; @Younis2025; @Zeng2025]. The TLR7/FTO innate-axis panel was not focus-state specific, so it is best treated as broader mechanistic context rather than a state-defining feature [@Zeng2025] (Fig. 5 and Supplementary Tables S7 and S8).

### Independent SLE validation supports the IFN and ZEB2/TBX21/ITGAX axes

We next tested whether the prioritized programs generalized beyond the discovery cohort. GSE163121 yielded 25,037 B cells from two healthy control and three SLE samples and was treated as directional validation because of its small donor count [@Bhamidipati2021]. SLE samples showed directionally higher ZEB2/TBX21/ITGAX-axis scores, IFN/ISG scores, and ABC/APC-high fractions, but did not reproduce a global APC/HLA increase (Supplementary Fig. S3 and Supplementary Table S10).

GSE135779 provided the main independent validation layer [@NeharBelaid2020]. After matching metadata-defined B-subcluster cells to processed matrices, 32,179 B-subcluster cells from 56 donor/sample names were retained, including 16 healthy control and 40 SLE donor/sample names. Donor/sample-level testing validated IFN/ISG activity in SLE B-subcluster cells (delta 0.2810; FDR 8.72e-04) and the ZEB2/TBX21/ITGAX axis (delta 0.0351; FDR 4.48e-02). A modest Plasmablast/ASC score increase also reached statistical support (delta 0.0246; FDR 4.48e-02), but was treated as a secondary differentiation signal because validation cells were selected using a broad metadata-defined B-subcluster label. The ABC/APC-high B-subcluster fraction was higher in SLE (delta 0.0567; FDR 7.88e-02). ABC/DN2, ABC/APC-focus, FCRL-axis, and APC/HLA scores were directionally higher in SLE but did not reach FDR < 0.05 in the all-donor/sample analysis. Thus, GSE135779 validates the IFN and ZEB2/TBX21/ITGAX components of the model and supports an expanded high-scoring ABC/APC-like tail, while APC/HLA should be described as directionally supportive rather than independently decisive (Fig. 6 and Supplementary Table S11).

### OneK1K provides external B-lineage reference context

To test whether the prioritized programs mapped onto a large independent B-lineage reference structure, we analyzed OneK1K/GSE196830 [@Yazar2022]. The CELLxGENE H5AD contained 1,248,980 PBMCs and 35,528 features. We identified 129,579 B-lineage-like cells across 981 donors, including naive B cells, memory B cells, transitional stage B cells, and plasmablasts. All current manuscript genes were present.

OneK1K showed broad HLA/CD74 and APC/HLA program expression in non-plasmablast B cells, the expected plasmablast/ASC enrichment in plasmablasts, and the highest mean ZEB2/TBX21/ITGAX-axis score in transitional B cells. These data were not used to estimate SLE-vs-control effects because OneK1K is not a matched disease-validation cohort. Instead, they provide external reference context for the compartmental plausibility of the programs prioritized in discovery and validation (Fig. 7/Extended Data Fig. 1 and Supplementary Table S12).

## Discussion

This study identifies an expanded atypical ABC/APC-like B-cell state as a candidate component of SLE B-cell remodeling. The claim is supported across donor-level abundance, raw-count markers, QC sensitivity, covariate-adjusted and CLR compositional models, donor-state pseudobulk, literature-informed signatures, independent SLE validation, and external B-lineage reference context. This evidence stack is stronger than a cluster-labeling analysis alone, because each layer addresses a different reviewer concern: disease association, technical artifact, covariate imbalance, compositional dependence, biological identity, cross-dataset generalization, and reference plausibility.

The model is intentionally composite. The focus state is not presented as a pure DN2 lineage, pure APC population, or plasmablast precursor. Instead, it combines FCRL, ZEB2/TBX21/ITGAX, antigen-presentation, ABC/DN2-associated, and interferon-linked features. This framing is important because GSE135779 validates IFN/ISG activity and the ZEB2/TBX21/ITGAX axis more strongly than it validates the global APC/HLA score. The discovery data support APC/HLA robustly, but independent validation suggests that antigen-presentation biology should be framed as part of the ABC/APC-like program rather than as a fully replicated disease-wide effect.

The results also argue against a purely plasmablast-centric interpretation of this cohort. Plasmablasts are clearly resolved, and OneK1K confirms their expected antibody-secreting-cell program, but the dominant donor-level discovery signals were activated naive-like expansion, memory-like reduction, and ABC/APC-like expansion. This does not diminish plasmablast biology in SLE; rather, it positions the ABC/APC-like state as an additional disease-associated B-cell program that may contribute to antigen presentation and inflammatory amplification.

Several limitations remain. The study relies on public processed datasets and is observational. The primary CELLxGENE `X` matrix was preprocessed/scaled, requiring careful separation of embedding-based state mapping from raw-count expression summaries. CLR coefficients are relative to the geometric mean abundance of retained states and cannot establish absolute cell-number changes. Validation was performed using public cohorts rather than prospective samples, and not every composite program component replicated equally across datasets. OneK1K provides reference context rather than disease validation. Future studies should test whether the ABC/APC-like state has antigen specificity, genetic regulation, treatment-response relevance, or functional antigen-presenting capacity in prospective SLE cohorts and perturbational systems.

Overall, the data support a donor-aware model in which SLE B-cell remodeling includes activated naive-like expansion, memory-like redistribution, and an atypical ABC/APC-like program marked by FCRL genes, ZEB2/TBX21/ITGAX activity, antigen-presentation features, and interferon-linked activation.

## Methods

### Discovery dataset and B-lineage extraction

We analyzed the public Perez/GSE174188 CELLxGENE H5AD object [@Perez2022]. B-lineage cells were selected using standardized `cell_type` annotations. Cells annotated as `B cell` or `plasmablast` were retained.

### Matrix handling and state mapping

The H5AD `X` matrix contained preprocessed/scaled values and was not treated as raw counts. Available PCA/UMAP representations were used for first-pass state mapping. Count-like analyses, including marker refinement, donor-state pseudobulk expression, and literature-informed signatures, used `adata.raw.X`.

### Marker refinement, abundance testing, and QC sensitivity

Raw-count marker summaries were calculated from `adata.raw.X`, normalized to counts per 10,000, and transformed as log1p(CP10K). Donor-level state abundance was calculated as the fraction of each donor's B-lineage cells assigned to each refined state. Normal and SLE donor fractions were compared using Mann-Whitney U tests with Benjamini-Hochberg correction. Sensitivity analysis repeated donor-level tests after excluding the flagged platelet/ambient-RNA-high cluster.

### Donor-state pseudobulk and literature signatures

Cells were aggregated by donor, disease group, disease state, and refined B-cell state so that biological donors, rather than cells, defined the inferential units [@Crowell2020; @Squair2021]. Marker-gene counts were summed from `adata.raw.X`, normalized by total raw counts across all genes in the donor-state group, and transformed as log1p(CP10K). Program scores were calculated as the mean marker-level log1p(CP10K) value. Donor-state groups with fewer than 10 cells were excluded from focus-state comparisons. For each feature, the focus-state score was paired within donor with the mean score across that donor's other retained B-cell states; paired differences were tested using two-sided Wilcoxon signed-rank tests with Benjamini-Hochberg correction across features. Literature-informed panels were manually curated from the cited biological literature and prespecified compartment controls; they were not treated as verbatim published or independently validated signatures. Gene-level membership, source type, citation keys, DOI mappings, and provenance notes are reported in Supplementary Table S8. Panels were scored as positive-marker means or, for signed panels, positive-marker mean minus negative-marker mean and tested using the same paired-donor framework.

### Covariate sensitivity

Donor-level covariate sensitivity used OLS models with HC3 robust standard errors. Model tiers included unadjusted disease-only, demographic-adjusted, and full-adjusted specifications. The full model adjusted for age, sex, self-reported ethnicity, simplified processing cohort, and log10 donor B-lineage cell count. Continuous covariates were centered and scaled before model fitting to improve numerical conditioning.

### Compositional abundance sensitivity

To evaluate constant-sum dependence in donor-level state fractions, we excluded the platelet/ambient-RNA-high QC state and constructed a donor-by-state count matrix for seven retained states. Counts were smoothed with a 0.5-cell pseudocount, converted to retained-state proportions, and transformed as CLR values by subtracting each donor's mean log proportion across retained states [@Buttner2021]. For comparison, raw fractions and CLR outcomes were modeled using the same unadjusted, demographic-adjusted, and full-adjusted OLS specifications with HC3 robust standard errors. Benjamini-Hochberg correction was applied across seven states within each analysis and model tier. Pseudocount sensitivity repeated the fully adjusted CLR analysis using count-scale values of 0.1, 0.5, and 1.0.

### Independent SLE validation

GSE163121 processed supplementary matrices were downloaded from GEO and parsed into a B-cell AnnData object [@Bhamidipati2021]. Counts were normalized to log1p(CP10K), and program scores were compared between sample-level healthy control and SLE groups. Because this dataset contains only five donors, it was treated as directional validation.

For GSE135779, processed Matrix Market files were downloaded from GEO and aligned to extended cell-level metadata from associated analysis resources [@NeharBelaid2020]. Metadata-defined B-subcluster cells were matched to processed matrices within sample using core barcode sequences. Counts were normalized to log1p(CP10K). Donor/sample-level mean scores and ABC/APC-high fractions were compared between healthy control and SLE groups using Mann-Whitney U tests with Benjamini-Hochberg correction across metrics and strata.

### OneK1K reference analysis

The OneK1K/GSE196830 CELLxGENE H5AD was downloaded and inspected [@Yazar2022]. B-lineage-like cells were selected from `cell_type` annotations. Target-gene raw counts from `X` were normalized as log1p(CP10K) using the full-library `nCount_RNA` metadata column. Program scores were summarized by cell type and donor. OneK1K was used as external immune-reference context and not as SLE-vs-control validation.

## Data availability

This study used public processed single-cell data from Perez/GSE174188, GSE135779, GSE163121, and OneK1K/GSE196830 [@Perez2022; @NeharBelaid2020; @Bhamidipati2021; @Yazar2022]. No new human participant data were generated. Large source H5AD and RAW archive files are not redistributed in this project package; scripts and runbooks document how to obtain and regenerate the analyses from public sources.

## Code availability

Analysis scripts are stored under `02_analysis/scripts`. Environment files and runbooks are stored under `02_analysis`. Figure-specific outputs and tables are stored under `03_results`. Submission planning, QC, and reproducibility files are stored under `04_submission`.

## Ethics statement

This work is a secondary analysis of publicly available de-identified data and did not involve new recruitment, intervention, or generation of new human subject data.

## Author contributions

Placeholder: add author initials and contribution details before submission.

## Competing interests

Placeholder: declare competing interests before submission.

## Figure legends

Figure 1. Dataset overview and B-lineage analysis guardrails.

Figure 2. Donor-aware B-cell state atlas and SLE-associated remodeling.

Figure 3. Donor-state expression evidence supports an atypical ABC/APC-like B-cell state.

Figure 4. Covariate sensitivity supports robust donor-level B-cell remodeling.

Figure 5. Literature-informed signatures link the ABC/APC-like state to atypical, antigen-presentation, and interferon biology.

Figure 6. GSE135779 provides independent validation of SLE B-cell program remodeling.

Figure 7 or Extended Data Figure 1. OneK1K B-lineage reference context for prioritized SLE B-cell programs.

Supplementary Figure S4. Compositional sensitivity of donor-level B-cell state abundance.

## References

Reference metadata are maintained in `references_working_v1.bib`, with Crossref-verified metadata in `references_verified_crossref_2026-07-09.bib`. Final reference style should be adapted after target-journal selection.
