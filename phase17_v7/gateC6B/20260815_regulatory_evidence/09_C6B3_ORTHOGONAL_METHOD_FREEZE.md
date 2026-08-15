# Gate C6B-3 orthogonal method freeze

## `PASS_GATE_C6B3_ORTHOGONAL_METHOD_FREEZE`

No GSE23307 expression values or M5911 enrichment effects were inspected.

## Checks

- [PASS] all_12_genes_mapped
- [PASS] mapping_has_21_probes
- [PASS] matrix_header_has_six_samples
- [PASS] four_paired_bcell_samples_present
- [PASS] external_freeze_expression_blind

## Frozen scoring

- 12 genes, 21 probes, median probe aggregation within gene.
- Paired IFN-beta minus control effects are averaged across the 12 genes per donor.
- M5911 uses weighted preranked GSEA with 10,000 deterministic label permutations.
- Both layers are supportive and cannot rescue a failed 24-test regulator family.
