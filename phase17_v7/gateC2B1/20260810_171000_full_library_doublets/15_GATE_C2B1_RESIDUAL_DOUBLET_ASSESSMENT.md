# Gate C2B1 residual doublet multimetric assessment

**Status:** REVIEW REQUIRED; no exclusion mask has been frozen or applied.

- Hard-QC cells reviewed: 150,402
- Cells with residual Scrublet scores: 150,402
- Automatic residual-risk calls: 1,972 (1.31%)
- Protected outcome fields in the working object: none

## Strongest score associations

- total_counts: Spearman rho 0.046 (n = 150,402)
- fraction_b_lineage: Spearman rho 0.036 (n = 150,402)
- detected_genes: Spearman rho 0.029 (n = 150,402)
- fraction_erythroid: Spearman rho -0.026 (n = 150,402)

## Binding interpretation

This pass evaluates residual doublet risk after the source workflow; automatic
calls do not by themselves justify a second deletion step. Review library-level
extremes, RNA-content association, mixed-lineage marker fractions and, after
Gate C2B2, localization in the disease-blind state graph.

Carry `all-hard-QC` as the primary branch. Define a high-confidence-singlet
sensitivity branch only after the multimetric and cluster-localization review,
and report whether composition and within-state conclusions are robust to it.
