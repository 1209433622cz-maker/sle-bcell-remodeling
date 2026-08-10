# Results Draft v1 - Figures 1 To 3

## Dataset Overview And Analysis Guardrails

We constructed a B-lineage atlas from the public Perez/GSE174188 CELLxGENE H5AD object, which contained 1,263,676 immune cells from 261 donors. B-lineage cells were selected using the standardized `cell_type` annotation and included cells annotated as `B cell` or `plasmablast`. This yielded 152,981 B-lineage cells from 259 donors, including 99 normal donors and 160 donors with systemic lupus erythematosus (SLE).

Initial inspection showed that the CELLxGENE `X` matrix contained preprocessed/scaled values, including negative values. We therefore used the provided PCA/UMAP representation for first-pass state mapping and used the count-like `adata.raw.X` matrix for marker refinement and donor-state expression summaries. This separation between visualization/state mapping and count-based expression analysis was used as a core guardrail throughout the analysis.

## Refined B-Cell State Atlas

Leiden clustering of the B-lineage subset resolved eight preliminary states spanning resting naive B cells, an activated SLE-naive-like state, memory-like states, an atypical ABC/APC-like state, a plasmablast/antibody-secreting cell state, and one small cluster flagged for platelet/ambient-RNA-high markers. Cluster labels were refined using public cell-type metadata, raw-count marker summaries, ranked state markers, donor-level disease tests, and sensitivity analysis.

The refined atlas supported multiple disease-associated changes in the B-cell compartment. The strongest donor-level abundance signal was an activated SLE-naive-like B-cell state, which was expanded in SLE donors compared with normal donors. This state retained naive-associated markers such as `TCL1A`, `VPREB3`, `CXCR4`, and `CD79B`, while also showing activation or immediate-early genes including `CD69`, `DUSP1`, `JUNB`, and `FOS`.

SLE was also associated with expansion of an atypical ABC/APC-like B-cell state. This state expressed ABC-like and antigen-presentation markers including `FCRL5`, `FCRL3`, `ZEB2`, `MS4A1`, `CD74`, `HLA-DRA`, `HLA-DRB1`, and `HLA-DPB1`. At the donor level, the state was increased in SLE donors compared with normal donors and remained significant after excluding the flagged platelet/ambient-RNA-high cluster from the denominator.

In contrast, a memory-like B-cell state was reduced in SLE at the donor level, supporting a broader model of compartment redistribution rather than a single expanded endpoint population. Plasmablasts were transcriptionally well defined by markers including `MZB1`, `JCHAIN`, `XBP1`, and `TNFRSF17`, but donor-level abundance testing did not support plasmablast expansion as the dominant disease-associated signal in this cohort.

## Platelet/Ambient-RNA-High Cluster As A QC-Limited State

Raw-count ranked marker analysis identified a small cluster initially within the B-lineage atlas that was dominated by platelet or ambient RNA-associated genes, including `PPBP`, `PF4`, `NRGN`, `TUBB1`, `RGS18`, `CAVIN2`, `GNG11`, and `SPARC`. Because this profile could reflect ambient RNA, platelet association, or doublet-like contamination rather than a clean B-cell state, we flagged the cluster and excluded it from central biological interpretation.

Sensitivity analysis showed that the main disease-associated signals were not dependent on this flagged cluster. The activated SLE-naive-like state, memory-like B-cell reduction, and atypical ABC/APC-like B-cell expansion remained directionally stable after exclusion. This supports treating the flagged cluster as a QC guardrail rather than as a primary disease result.

## Donor-State Pseudobulk Evidence For The ABC/APC-Like State

To strengthen the central disease-associated state model, we performed donor-state pseudobulk expression analysis using curated marker programs. Cells were aggregated by donor and refined B-cell state, marker-gene counts were normalized by total raw counts across all genes in each donor-state group, and expression was summarized as log1p(CP10K). Donor-state groups with fewer than 10 cells were excluded from program comparisons.

The atypical ABC/APC-like state showed strong donor-aware enrichment for ABC-associated and antigen-presentation programs compared with other retained B-cell states. The ABC ranked program was higher in the focus state (delta 0.871; FDR 6.38e-93), as was the ABC/DN2 program (delta 0.448; FDR 1.30e-92) and the APC/HLA program (delta 0.413; FDR 3.65e-83). IFN-response markers were also modestly higher (delta 0.084; FDR 2.98e-07), whereas activation, memory, naive, and plasmablast programs did not define the focus state.

The same state was expanded in SLE donors at the abundance level. In the original donor-level test, SLE donors had a higher mean fraction of ABC/APC-like B cells than normal donors (0.0549 versus 0.0259; FDR 2.67e-05). This remained significant after excluding the flagged platelet/ambient-RNA-high state from the denominator (0.0562 versus 0.0263; FDR 1.68e-05).

Within the ABC/APC-like state, disease-state summaries suggested that ABC and APC/HLA programs were retained across SLE strata, while IFN-response expression was highest among flare donor-states. These disease-state patterns are descriptive at this stage because some strata, especially treated SLE, include few donor-state observations.

## Working Results Summary

Together, Figures 1 to 3 support a coherent B-cell remodeling model in SLE. The strongest manuscript-level claim is that SLE expands an atypical ABC/APC-like B-cell state that carries donor-aware ABC/DN2 and antigen-presentation programs. A second robust disease-associated signal is expansion of an activated SLE-naive-like state, accompanied by redistribution or depletion of a memory-like B-cell state. Plasmablasts are transcriptionally clear but are not the dominant donor-level abundance signal in this cohort.

This result structure is suitable for a Q1/Q2-style manuscript if the claims remain donor-aware, the flagged cluster is handled transparently, and disease-state findings are framed as descriptive unless further covariate-aware or validation analysis is added.
