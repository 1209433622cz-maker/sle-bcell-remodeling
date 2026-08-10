# Results Draft - Phase 2 Working Version

## 1. A B-Lineage Atlas Captures Major B-Cell Compartments In SLE And Healthy Donors

We first constructed a B-lineage atlas from the Perez/GSE174188 single-cell dataset using the public CELLxGENE H5AD object. B-lineage cells were selected using the standardized `cell_type` annotation and included 152,981 cells, comprising 151,570 B cells and 1,411 plasmablasts. The B-lineage subset represented 259 donors, including 160 donors with systemic lupus erythematosus and 99 normal donors.

Because the CELLxGENE `X` matrix contains preprocessed/scaled values, including negative values, we used the provided PCA/UMAP embeddings for first-pass state mapping and preserved raw-count-compatible analyses for `adata.raw.X`. Leiden clustering of the B-lineage subset identified eight preliminary transcriptional states spanning naive-like, memory-like, atypical/ABC-like, and plasmablast/plasma-cell compartments.

## 2. Raw-Count Marker Refinement Supports An Atypical ABC/APC-Like B-Cell State

Marker refinement using `adata.raw.X` identified an atypical B-cell state with strong ABC-like and antigen-presenting features. This state was enriched for `FCRL5`, `FCRL3`, `ZEB2`, `CD74`, `HLA-DRA`, `HLA-DRB1`, `HLA-DPB1`, and `MS4A1`. The same state was supported by the source `ct_cov` annotation among cells with non-missing `ct_cov`, where it was dominated by `B_atypical` cells.

At the donor level, this atypical ABC/APC-like state was significantly expanded in SLE compared with normal donors. The mean donor fraction was higher in SLE than in normal donors in the original analysis and remained significant after excluding a flagged platelet/ambient-RNA-high cluster. This indicates that the atypical ABC/APC-like B-cell signal is not explained by the flagged small cluster.

Working interpretation: this state is the central pathogenic B-cell candidate in the current dataset and should anchor the main disease-associated B-cell result.

## 3. SLE Is Associated With Expansion Of An Activated Naive-Like B-Cell State

The strongest donor-level abundance signal was observed in a naive-like B-cell state enriched in SLE. Raw-count marker ranking showed high expression of `TCL1A`, `VPREB3`, `CXCR4`, `CD79B`, and activation/immediate-early genes including `CD69`, `DUSP1`, `JUNB`, and `FOS`.

This state should be described conservatively as an activated SLE-enriched naive-like B-cell state rather than overinterpreted as a fully distinct lineage. Its robust donor-level association suggests that SLE remodels the naive-like compartment, potentially reflecting disease-associated activation or altered maturation state.

## 4. Memory-Like B-Cell Compartments Are Redistributed In SLE

Memory-like B-cell states showed evidence of disease-associated redistribution. One memory-like state was reduced in SLE at donor level and remained significant after sensitivity analysis. Raw-count markers supporting memory-like identity included `GPR183`, `LTB`, `CD1C`, and `ARHGAP24`.

A second memory-like state showed markers including `TNFRSF13B`, `AIM2`, `BLK`, and `LTB`, but did not show a strong donor-level disease difference. Together, these findings support the broader conclusion that SLE B-cell remodeling involves multiple compartments rather than a single expanded endpoint state.

## 5. A Small Naive-Like Cluster Is Flagged By Platelet/Ambient RNA Markers

Raw-count marker ranking identified a small cluster previously labeled as a naive-like state that was dominated by platelet or ambient RNA-associated markers, including `PPBP`, `PF4`, `NRGN`, `TUBB1`, `RGS18`, `CAVIN2`, `GNG11`, and `SPARC`.

Although this cluster carries B-cell metadata and retains B-cell marker expression, it should not be used as a central biological SLE-expanded B-cell state without further QC. We therefore treat it as a flagged platelet/ambient-RNA-high B-cell cluster and use sensitivity analysis to ensure that the main disease-associated signals remain stable after its exclusion.

## 6. Plasmablasts Form A Clear Endpoint But Are Not Significantly Expanded At Donor Level

The plasmablast/plasma-cell state was transcriptionally clear, with strong expression of `MZB1`, `JCHAIN`, `XBP1`, `TNFRSF17`, `HSP90B1`, and `FKBP11`. This supports accurate identification of the antibody-secreting endpoint compartment.

However, donor-level abundance testing did not show a significant SLE-associated expansion of this state in the first-pass analysis. Therefore, plasmablasts should be shown as an expected B-cell endpoint, but the manuscript should avoid claiming that plasmablast expansion is the primary disease signal in this cohort.

## Working Summary

The emerging result is that SLE reshapes the B-cell compartment through expansion of atypical ABC/APC-like and activated naive-like states, together with redistribution of memory-like compartments. This state-focused view is stronger than a simple plasmablast-centric interpretation and is better aligned with the donor-level abundance tests and raw-count marker refinement.
