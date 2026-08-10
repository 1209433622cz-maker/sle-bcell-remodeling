# Figure 1. Dataset overview and B-lineage analysis workflow

**a,** Overview of the analysis workflow. We used the public Perez/GSE174188 CELLxGENE H5AD object containing 1,263,676 immune cells from 261 donors. B-lineage cells were selected using the standardized `cell_type` annotation (`B cell` or `plasmablast`), yielding 152,981 B-lineage cells from 259 donors. State mapping used the provided PCA/UMAP representation because the CELLxGENE `X` matrix is scaled/preprocessed, while marker refinement used the count-like `adata.raw.X` matrix.

**b,** Major cell-type composition in the source CELLxGENE object. B cells represented 151,570 cells in the source object, with plasmablasts additionally captured during B-lineage extraction.

**c,** Donor counts by disease in the full source object and B-lineage subset. The source object included 99 normal donors and 162 SLE donors; after B-lineage extraction, 99 normal donors and 160 SLE donors retained B-lineage cells.

**d,** Composition of the B-lineage subset. The subset consisted of 151,570 B cells and 1,411 plasmablasts.

**e,** Sizes of marker-refined B-cell states used for downstream analysis. Refined labels distinguish resting naive B cells, activated SLE-naive-like B cells, memory-like states, atypical ABC/APC-like B cells, a flagged platelet/ambient-high cluster, and plasmablast/antibody-secreting cells.

**f,** Analysis guardrails. The scaled/preprocessed `X` matrix was not treated as raw counts; marker refinement used `adata.raw.X`; and a small platelet/ambient-high cluster was excluded from central biological claims. Donor-level state-fraction testing used 99 normal and 160 SLE donors.
