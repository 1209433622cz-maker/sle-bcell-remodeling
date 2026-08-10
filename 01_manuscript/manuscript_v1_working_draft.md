# Donor-aware single-cell analysis identifies an expanded ABC/APC-like B-cell state in systemic lupus erythematosus

## Abstract

**Background:** B-cell dysregulation is central to systemic lupus erythematosus (SLE), but the donor-level disease-associated B-cell states captured in large public single-cell datasets remain incompletely resolved.

**Objective:** To define disease-associated B-lineage cell states in SLE and prioritize candidate pathogenic B-cell programs using a donor-aware single-cell analysis framework.

**Methods:** We analyzed the public Perez/GSE174188 CELLxGENE H5AD object containing 1,263,676 immune cells from 261 donors. B-lineage cells were selected using standardized cell-type annotations, yielding 152,981 B-lineage cells from 259 donors. Because the CELLxGENE `X` matrix was preprocessed/scaled, state mapping used available low-dimensional representations, while marker refinement and donor-state expression summaries used count-like `adata.raw.X`. Refined B-cell states were assessed using raw-count marker programs, donor-level abundance tests, flagged-cluster sensitivity analysis, covariate-adjusted donor-level modeling, and literature-informed signature validation.

**Results:** SLE was associated with expansion of an activated naive-like B-cell state and an atypical ABC/APC-like B-cell state, together with reduction or redistribution of a memory-like B-cell state. The ABC/APC-like state remained expanded in SLE after excluding a platelet/ambient-RNA-high QC cluster and after adjustment for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count. Donor-state pseudobulk and literature-informed signature analyses linked this state to ABC/DN2, ZEB2-associated, APC/HLA, EBV/APC-like, IFN/ISG, and age-associated/atypical B-cell biology. Plasmablasts were transcriptionally well defined but were not the dominant donor-level abundance signal in this cohort.

**Conclusions:** This donor-aware analysis supports a model in which SLE B-cell remodeling is anchored by expansion of an atypical ABC/APC-like state with antigen-presentation and ABC/DN2-associated programs. These findings nominate the ABC/APC-like state as a candidate pathogenic B-cell population for further validation.

## Introduction

SLE is a heterogeneous autoimmune disease in which B-cell dysregulation contributes to autoantibody production, antigen presentation, inflammatory amplification, and tissue injury [@Perez2022]. A state-resolved analysis of B cells may help clarify which B-cell compartments are most consistently remodeled in SLE.

Prior work has highlighted ABC/DN2-like B cells, plasmablasts, interferon-responsive B cells, antigen-presenting B cells, and atypical or age-associated B-cell programs as disease-relevant compartments [@Dai2024; @Zeng2025; @Younis2025]. However, public single-cell datasets require donor-aware analysis to avoid overinterpreting single-cell-level differences as disease-level effects.

Here, we used the public Perez/GSE174188 CELLxGENE object to construct a donor-aware B-lineage analysis focused on SLE-associated state remodeling [@Perez2022]. We combined atlas-level state refinement, raw-count marker support, donor-level abundance testing, covariate sensitivity, and literature-informed signature validation.

## Results

### Dataset Overview And Analysis Guardrails

We constructed a B-lineage atlas from the public Perez/GSE174188 CELLxGENE H5AD object, which contained 1,263,676 immune cells from 261 donors [@Perez2022]. B-lineage cells were selected using the standardized `cell_type` annotation and included cells annotated as `B cell` or `plasmablast`. This yielded 152,981 B-lineage cells from 259 donors, including 99 normal donors and 160 donors with SLE.

Initial inspection showed that the CELLxGENE `X` matrix contained preprocessed/scaled values, including negative values. We therefore used the provided PCA/UMAP representation for first-pass state mapping and used the count-like `adata.raw.X` matrix for marker refinement and donor-state expression summaries.

### Refined B-Cell State Atlas

Leiden clustering of the B-lineage subset resolved eight preliminary states spanning resting naive B cells, an activated SLE-naive-like state, memory-like states, an atypical ABC/APC-like state, a plasmablast/ASC state, and one small cluster flagged for platelet/ambient-RNA-high markers. Cluster labels were refined using public cell-type metadata, raw-count marker summaries, ranked state markers, donor-level disease tests, and sensitivity analysis.

The strongest donor-level abundance signal was an activated SLE-naive-like B-cell state, which retained naive-associated markers such as `TCL1A`, `VPREB3`, `CXCR4`, and `CD79B`, while also showing activation or immediate-early genes including `CD69`, `DUSP1`, `JUNB`, and `FOS`. SLE was also associated with expansion of an atypical ABC/APC-like B-cell state expressing `FCRL5`, `FCRL3`, `ZEB2`, `MS4A1`, `CD74`, and HLA class II genes. In contrast, a memory-like B-cell state was reduced in SLE. Plasmablasts were transcriptionally clear but were not the dominant donor-level abundance signal.

### Flagged Platelet/Ambient-RNA-High Cluster

Raw-count ranked marker analysis identified a small B-lineage cluster dominated by platelet or ambient RNA-associated genes, including `PPBP`, `PF4`, `NRGN`, `TUBB1`, `RGS18`, `CAVIN2`, `GNG11`, and `SPARC`. We therefore flagged this cluster and excluded it from central biological interpretation. Sensitivity analysis showed that the activated SLE-naive-like expansion, memory-like B-cell reduction, and ABC/APC-like expansion remained directionally stable after excluding the flagged cluster.

### Donor-State Pseudobulk Evidence

Donor-state pseudobulk analysis strengthened the central ABC/APC-like interpretation. The ABC/APC-like state showed higher ABC ranked program expression (delta 0.871; FDR 6.38e-93), ABC/DN2 program expression (delta 0.448; FDR 1.30e-92), APC/HLA program expression (delta 0.413; FDR 3.65e-83), and modest IFN-response expression (delta 0.084; FDR 2.98e-07) compared with other retained B-cell states.

### Covariate Sensitivity

Donor metadata showed age and covariate imbalance between normal and SLE groups. We therefore fit donor-level abundance models using unadjusted, demographic-adjusted, and full-adjusted specifications. In the full model adjusted for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count, the activated SLE-naive-like state remained expanded (beta 0.1491; FDR 2.41e-10), memory-like B I remained reduced (beta -0.0999; FDR 9.66e-07), and the ABC/APC-like state remained expanded (beta 0.0175; FDR 2.22e-02).

### Literature-Informed Signature Validation

Literature-informed signature validation supported the ABC/APC-like identity of the central state. The focus state ranked first among refined B-cell states for ABC/DN2 core, ABC-low-naive-context, ZEB2-linked ABC, APC/HLA B-cell, EBV/APC-like B-cell, and age-associated/atypical B-cell signatures [@Dai2024; @Younis2025; @Zeng2025]. The TLR7/FTO innate-axis signature was not focus-state specific and should be framed as broader mechanistic context rather than a state-defining feature [@Zeng2025].

## Discussion

This donor-aware analysis identifies an expanded atypical ABC/APC-like B-cell state as a central candidate in SLE B-cell remodeling. The result is supported by raw-count markers, donor-level abundance testing, sensitivity analysis excluding a flagged platelet/ambient-RNA-high cluster, covariate-adjusted donor-level models, donor-state pseudobulk programs, and literature-informed signature validation.

The findings support a B-cell remodeling model rather than a purely plasmablast-centric model. Plasmablasts are clearly identified, but the dominant donor-level disease signals are the activated SLE-naive-like expansion, ABC/APC-like expansion, and memory-like B-cell reduction.

The ABC/APC-like state links several disease-relevant concepts: ABC/DN2-like B-cell biology, ZEB2-associated atypical B-cell programs, antigen presentation, EBV/APC-like framing, interferon responsiveness, and age-associated/atypical B-cell features [@Dai2024; @Younis2025; @Perez2022]. At the same time, the current analysis preserves boundaries: TLR7/FTO biology is not focus-state specific in this dataset, disease-state summaries are descriptive, and the study remains observational [@Zeng2025].

Limitations include reliance on a public processed dataset, potential residual confounding, marker-based rather than perturbational validation, and the need for formal external dataset replication. Future work should test whether the ABC/APC-like state is reproducible across independent SLE cohorts and whether it has antigen-specific, genetic, or therapeutic-response relevance, potentially using immune genetic and multi-omic references [@Yazar2022; @Yin2026].

## Methods Summary

B-lineage cells were selected from the public CELLxGENE H5AD using standardized cell-type annotations. State mapping used available PCA/UMAP representations because `X` contained preprocessed/scaled values. Raw-count marker summaries, donor-state pseudobulk programs, and literature-informed signature validation used count-like `adata.raw.X`.

Donor-level abundance was tested using donor fractions for each refined B-cell state. Mann-Whitney U tests with Benjamini-Hochberg correction were used for unadjusted donor-level state comparisons. Covariate sensitivity used OLS models with HC3 robust standard errors. Full models adjusted for age, sex, self-reported ethnicity, simplified processing cohort, and log10 donor B-lineage cell count.

Literature-informed signature validation used donor-state pseudobulk scores for curated marker sets. Positive-marker signatures were scored as the mean log1p(CP10K) across available marker genes. Signed signatures were scored as positive-marker mean minus negative-marker mean. Donor-state groups with fewer than 10 cells were excluded from focus-state comparisons.

## Figure Legends

Figure 1. Dataset overview and B-lineage analysis workflow.

Figure 2. Refined B-cell state remodeling in SLE.

Figure 3. Donor-aware expression evidence supports an atypical ABC/APC-like B-cell state in SLE.

Figure 4. Covariate sensitivity supports robust donor-level B-cell state remodeling in SLE.

Figure 5. Literature-informed signature validation supports the ABC/APC-like identity of the SLE-associated B-cell state.

## Working References

Reference metadata are maintained in `references_working_v1.bib`. Citation keys in this draft are working placeholders that should be verified before submission.
