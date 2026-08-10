# Results Draft - Phase 3 Working Version

## Donor-State Pseudobulk Analysis Prioritizes An Atypical ABC/APC-Like B-Cell State

To strengthen the disease-associated state model, we next performed donor-state pseudobulk expression analysis for curated B-cell, ABC/DN2, antigen-presentation, IFN-response, activation, memory, naive, plasmablast, and platelet/ambient marker programs. Expression was calculated from count-like `adata.raw.X` after aggregating cells by donor and refined B-cell state, using log1p(CP10K) expression summaries. Donor-state groups with fewer than 10 cells were excluded from program comparisons.

The atypical ABC/APC-like B-cell state showed strong donor-aware enrichment for ABC-associated and antigen-presentation programs compared with other retained B-cell states. The ABC ranked program was higher in the focus state (delta 0.871; FDR 6.38e-93), as was the ABC/DN2 program (delta 0.448; FDR 1.30e-92) and the APC/HLA program (delta 0.413; FDR 3.65e-83). IFN-response markers were also modestly higher (delta 0.084; FDR 2.98e-07), whereas the platelet/ambient marker program was not significantly elevated after correction in the focus-state comparison.

Top donor-state marker effects included `FCRL5`, `FCRL3`, `ZEB2`, `MS4A1`, `CD19`, `TNFRSF1B`, `CD74`, `HLA-DQA1`, `HLA-DRB1`, `HLA-DPB1`, and `HLA-DPA1`, together with inflammatory or activation-linked genes such as `HSPB1`, `RGS2`, `MAP3K8`, `FGR`, and `NR4A2`. This marker pattern supports interpretation of the state as an atypical ABC/APC-like B-cell population rather than a plasmablast endpoint or a platelet/ambient artifact.

Consistent with the donor-level abundance analysis, the ABC/APC-like state was expanded in SLE donors compared with normal donors. The original donor-level test showed a higher mean fraction in SLE donors (0.0549) than normal donors (0.0259; FDR 2.67e-05). This signal remained significant after excluding the flagged platelet/ambient-RNA-high state from the denominator (SLE mean fraction 0.0562; normal mean fraction 0.0263; FDR 1.68e-05).

Within the ABC/APC-like state, disease-state summaries suggested that ABC and APC/HLA programs were retained across SLE strata, while IFN-response expression was highest in flare donor-states. These within-SLE disease-state patterns should be treated as descriptive at this stage because some strata, particularly treated SLE, include few donor-state observations.

## Working Manuscript Claim

The Phase 3 result supports a central claim for the manuscript: SLE is associated with expansion of an atypical ABC/APC-like B-cell state that carries donor-aware ABC/DN2 and antigen-presentation programs. This provides a stronger mechanistic anchor than a purely abundance-based atlas result and positions the ABC/APC-like state as the main pathogenic candidate for downstream interpretation.

## Methods-Ready Notes

Donor-state pseudobulk summaries were calculated from `adata.raw.X` using curated marker genes present in the H5AD object. For each donor-state group, marker-gene counts were summed and normalized by the aggregated total raw counts across all genes for the same donor-state group, then transformed as log1p(CP10K). Program scores were calculated as the mean of marker-level log1p(CP10K) values within each curated program. Comparisons between the ABC/APC-like state and other retained states used Mann-Whitney U tests with Benjamini-Hochberg correction across marker genes or programs. The flagged platelet/ambient-RNA-high state was excluded from the comparator for the main focus-state tests.

## Limitations To Preserve In The Draft

- The program analysis is marker-set focused and should not be presented as genome-wide differential expression.
- Clinical disease-state comparisons are descriptive until stronger covariate-aware or validation analysis is added.
- The analysis supports an association between SLE and an ABC/APC-like B-cell state, but does not establish causality.
