# Results Draft - Phase 10 External Validation

## Independent B-Cell Validation In GSE163121

To add an independent validation layer, we analyzed GSE163121, a public single-cell RNA-seq dataset of B cells isolated from PBMCs of healthy controls and SLE patients. The processed GEO supplementary matrices included two healthy control samples and three SLE samples, yielding 25,037 B cells and 33,694 genes after parsing.

We scored the same marker programs used in the primary analysis using log1p(CP10K)-normalized counts. Because the validation cohort contained only five donors, we treated these results as directional validation and boundary evidence rather than a fully powered replication analysis.

The SLE samples showed directionally higher ZEB2/TBX21/ITGAX-axis scores (SLE minus HC delta 0.1330; sample-level p=0.8; FDR=0.8) and IFN/ISG scores (delta 0.1228; p=0.2; FDR=0.5). A tail-based ABC/APC-focus analysis, using the 95th percentile of healthy-control cells as a threshold, also showed a higher SLE ABC/APC-high fraction (delta 0.0668; p=0.8; FDR=0.8). Marker-level summaries were consistent with this boundary interpretation: `ZEB2`, `ITGAX`, `TBX21`, and `ISG15` were higher in SLE B cells, whereas `CD74`, `HLA-DRA`, and the global APC/HLA score were not increased.

Thus, GSE163121 provides independent support for SLE B-cell activation along the ZEB2/TBX21/ITGAX and IFN axes, but it does not fully reproduce the broader ABC/APC-like composite observed in the Perez/GSE174188 discovery analysis.

## GSE135779 Provides Larger Independent Validation

We next analyzed GSE135779 as the main upper-Q1 validation cohort. The GEO series describes approximately 276,000 PBMCs from 33 childhood SLE donors and 11 matched controls, plus an adult validation cohort of 8 adult SLE patients and 6 adult controls. The processed RAW tar was downloaded, inspected, and parsed alongside the extended cell-level metadata.

After matching metadata-defined B-subcluster cells to the processed matrices, 32,179 B-subcluster cells from 56 donor/sample names were retained, including 16 healthy control and 40 SLE donors. Program-gene coverage was strong: 9/9 ABC/APC-focus genes, 7/7 ABC/DN2 genes, 7/7 APC/HLA genes, and 10/10 IFN/ISG genes were present.

All-donor donor-level testing showed strong validation of IFN/ISG activity in SLE B-subcluster cells (delta 0.2810; FDR 8.72e-04) and significant validation of the ZEB2/TBX21/ITGAX axis (delta 0.0351; FDR 4.48e-02). The ABC/APC-high B-subcluster fraction was also higher in SLE (delta 0.0567; FDR 7.88e-02). ABC/DN2 core score, ABC/APC-focus score, FCRL-axis score, and APC/HLA score were directionally higher in SLE but did not reach FDR < 0.05 in the all-donor analysis.

Cohort-stratified analyses showed directionally consistent SLE-positive effects in both childhood and adult strata. The childhood stratum drove the strongest IFN/ISG validation, whereas the adult stratum supported the ZEB2/TBX21/ITGAX-axis direction. These results support the central model that SLE B-cell remodeling includes increased IFN/ISG activity, a ZEB2/TBX21/ITGAX-associated axis, and an expanded high-scoring ABC/APC-like B-cell tail. APC/HLA should be described as directionally supportive rather than independently decisive in this validation cohort.
