# Figure 3. Donor-aware expression supports an atypical ABC/APC-like B-cell state in SLE

**a,** UMAP visualization of the B-lineage atlas highlighting the atypical ABC/APC-like B-cell state. Other B-cell states are shown in light grey and the platelet/ambient-RNA-high cluster is shown as a flagged QC state.

**b,** Paired donor-state pseudobulk scores for the ABC/APC-like state versus each donor's mean of other retained states. Scores used count-like `adata.raw.X`, donor-state aggregation, full-library CP10K normalization, and log1p transformation. Groups with fewer than 10 cells and the flagged state were excluded. Two-sided Wilcoxon signed-rank tests across 153 paired donors were Benjamini-Hochberg corrected. Deltas were 0.861 for ABC ranked, 0.441 for ABC/DN2, 0.401 for APC/HLA (all FDR 1.47e-26), and 0.051 for IFN response (FDR 2.29e-11).

**c,** Donor-level ABC/APC-like abundance. Each point is one donor. The state was expanded in SLE in the original test (FDR 2.67e-05) and after flagged-state exclusion (FDR 1.68e-05).

**d,** Top paired pseudobulk marker effects. Bars show mean within-donor log1p(CP10K) differences between the focus and comparator states; positive effects included `FCRL5`, `FCRL3`, `ZEB2`, B-cell markers, and HLA class II genes.

**e,** Descriptive ABC/APC-like program summaries by clinical state among groups passing the 10-cell threshold. The treated group contained four donor-state observations and warrants caution.
