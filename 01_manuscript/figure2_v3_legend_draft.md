# Figure 2. Refined B-cell state remodeling in systemic lupus erythematosus

**a,** UMAP of 152,981 Perez/GSE174188 B-lineage cells colored by marker-refined state. Leiden clusters were relabeled using public metadata, raw-count markers, and donor-level disease tests. One platelet/ambient-RNA-high cluster was flagged for QC.

**b,** Raw-count marker dot plot. Color indicates mean log1p(CP10K) expression from `adata.raw.X`; size indicates the expressing-cell fraction. The ABC/APC-like state expressed `FCRL5`, `FCRL3`, `ZEB2`, `CD74`, and HLA class II genes. The activated SLE-naive-like state retained `TCL1A` with `CD69`, `JUNB`, and `FOS`; the flagged cluster expressed `PPBP`, `PF4`, and `TUBB1`.

**c,** Donor-level abundance of selected states. Each point is one donor; boxes summarize fractions of B-lineage cells. FDR values are from two-sided Mann-Whitney U tests with Benjamini-Hochberg correction across states.

**d,** Sensitivity analysis comparing SLE-normal mean-fraction differences before and after excluding the flagged state. Activated SLE-naive-like expansion, memory-like B I reduction, and ABC/APC-like expansion remained significant.
