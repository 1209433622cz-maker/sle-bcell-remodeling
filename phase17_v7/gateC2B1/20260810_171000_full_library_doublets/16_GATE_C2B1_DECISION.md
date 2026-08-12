# Gate C2B1 final decision

**Decision:** PASS_TO_C2B2_WITH_DUAL_BRANCH

- Complete-library runs: 88
- Hard-QC cells scored: 150,402
- Automatic residual-risk calls: 1,972 (1.31%)
- Maximum library rate: 6.49% in `e16d2c39-bfd1-4fb1-8ed6-ad6b16f3652e` (493 cells)
- Automatic second-round exclusion authorized: no

## Programmatic checks

- [PASS] all_library_runs_ok: 88/88 libraries have status=ok
- [PASS] score_rows_complete: 150,402 score rows for 150,402 H5AD cells
- [PASS] score_cell_ids_unique: unique score cell IDs: 150,402
- [PASS] score_cell_ids_match_h5ad: score and H5AD cell-ID sets compared exactly
- [PASS] source_indices_match_h5ad: unique score indices match the retained H5AD source-index set; range 0-152,980
- [PASS] predicted_totals_reconcile: cell table=1,972; library table=1,972
- [PASS] checkpoint_pairs_complete: score/summary checkpoint pairs=88/88
- [PASS] no_protected_outcomes: protected-like columns=none
- [PASS] no_extreme_library_rate: libraries above 20%=0
- [PASS] weak_key_metric_correlations: maximum absolute key Spearman rho=0.046
- [PASS] modest_rna_content_shift: median UMI fold=1.104; gene fold=1.078
- [PASS] no_mixed_lineage_enrichment: median max non-B fraction delta=-0.000004

## Binding decision

Gate C2B1 passes to C2B2 with two prespecified branches. The primary branch
retains all 150,402 hard-QC cells because the source workflow already performed
doublet handling and the residual calls show only modest RNA-content shifts,
no mixed-lineage enrichment and no strong key-metric correlation. The
high-confidence-singlet branch excludes the 1,972 automatic residual-risk calls
for sensitivity analysis only. The 493-cell maximum-rate library is flagged for
state-graph localization, not automatic removal. Final exclusion policy remains
locked until disease-blind cluster localization at Gate C2B3.
