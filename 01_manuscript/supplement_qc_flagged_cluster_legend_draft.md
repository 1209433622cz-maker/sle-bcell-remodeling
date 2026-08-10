# Supplementary Figure S1. QC of the platelet/ambient-RNA-high B-cell cluster

**a,** UMAP visualization highlighting the flagged platelet/ambient-RNA-high B-cell cluster within the B-lineage atlas. Other B-lineage cells are shown in light grey.

**b,** Top raw-count ranked markers for the flagged cluster. The highest-ranked genes included platelet or ambient RNA-associated markers such as `PPBP`, `PF4`, `NRGN`, `TUBB1`, `RGS18`, `CAVIN2`, `GNG11`, and `SPARC`, supporting QC-limited interpretation of this cluster.

**c,** Selected B-cell identity and platelet/ambient marker expression in the flagged cluster. The cluster retained B-cell identity marker expression, including `MS4A1`, `CD79A`, and `CD74`, but also showed detectable platelet/ambient marker expression. Bar height represents mean log1p(CP10K) expression from `adata.raw.X`; percentage labels indicate the fraction of cells expressing each marker.

**d,** Donor-level abundance of the flagged cluster in normal and SLE donors. Although this cluster was statistically higher in SLE donors (FDR 5.10e-05), its marker profile argues against treating it as a central biological B-cell state.

**e,** Sensitivity analysis after excluding the flagged cluster. Activated SLE-naive-like expansion, memory-like B-cell reduction, and ABC/APC-like expansion remained directionally stable.
