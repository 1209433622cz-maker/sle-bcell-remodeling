# Figure 7. OneK1K B-lineage reference context for prioritized SLE B-cell programs

OneK1K/GSE196830 was used as an external PBMC immune-reference resource to contextualize the B-cell programs prioritized in the discovery and disease-validation analyses. B-lineage-like cells were identified from the CELLxGENE `cell_type` annotation and included naive B cells, memory B cells, transitional stage B cells, and plasmablasts.

**a,** Heatmap showing standardized mean program scores across OneK1K B-lineage compartments. Scores were calculated from target-gene raw counts in `X` after log1p(CP10K) normalization using the full-library `nCount_RNA` metadata column. Program scores are displayed as z-scores across B-lineage compartments for visualization.

**b,** Dot plot showing marker-gene expression across OneK1K B-lineage compartments. Color indicates mean log1p(CP10K) expression and dot size indicates the percentage of cells with detectable expression.

This analysis is intended as external immune-reference context rather than SLE-vs-control validation, because OneK1K is not a matched SLE case-control cohort.
