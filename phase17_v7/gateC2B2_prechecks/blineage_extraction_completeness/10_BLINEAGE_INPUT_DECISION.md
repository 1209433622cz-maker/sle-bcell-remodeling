# B-lineage candidate refinement and input decision

**Decision:** `SOURCE_B_LABELS_PRIMARY_WITH_CANDIDATE_MAPPING_SENSITIVITY`

- Initial strict candidates outside source B labels: 4,711
- Candidates supported by at least two core B-receptor genes: 768 (16.30%)
- Core-BCR-supported candidates with low non-B signal: 57 (1.21%)
- Core-BCR-supported candidates relative to the 152,981-cell source B-lineage input: 0.50%
- Candidates with a plasma-like program, retained as context rather than identity evidence: 1,096
- Disease or outcome fields used: none

## Binding decision

The original strict rule is deliberately sensitive and is not sufficiently
specific for automatic relabeling because shared APC and supporting B genes can
be detected in dendritic populations. Plasma-associated genes are also kept
separate from identity because they are prominent among source pDC labels. The primary Gate C2B2 input
therefore remains the source `B cell` plus `plasmablast` definition after hard
QC. Refined candidates are retained as a prespecified mapping sensitivity and
must be projected onto the disease-blind state graph. Expansion is authorized
only if core-identity-supported candidates form a coherent B-cell population
rather than dispersed APC or mixed-lineage profiles.
