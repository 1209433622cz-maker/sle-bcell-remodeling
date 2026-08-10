# Figure 6. Independent B-cell validation in GSE163121 provides directional and boundary evidence for SLE-associated B-cell programs

**A.** Overview of the independent validation dataset. GSE163121 contains single-cell RNA-seq of B cells isolated from PBMCs from two healthy controls and three SLE patients. CellRanger filtered matrices were downloaded from GEO and parsed into an AnnData object for program scoring.

**B.** Number of B cells recovered per sample after parsing the processed matrices.

**C.** Sample-level mean program scores across selected B-cell programs. Scores were calculated as mean log1p(CP10K) expression across present genes in each curated program. The small donor count limits formal statistical power.

**D.** Fraction of B cells exceeding the healthy-control 95th percentile for the ABC/APC-focus composite score. This tail-based analysis asks whether SLE samples contain a larger high-scoring compartment even when whole-sample mean scores are heterogeneous.

**E.** Marker expression by disease group for selected ABC/DN2, APC/HLA, B-cell identity, IFN/ISG, and plasmablast-associated markers. Dot color indicates mean log1p(CP10K) expression and dot size indicates fraction of cells with nonzero expression.

This dataset is interpreted as directional external validation and boundary evidence. It supports higher SLE B-cell expression of the ZEB2/TBX21/ITGAX and IFN axes, but does not show a global increase in APC/HLA score. Because GSE163121 includes only five donors, the result should not be treated as a fully powered donor-level replication cohort.
