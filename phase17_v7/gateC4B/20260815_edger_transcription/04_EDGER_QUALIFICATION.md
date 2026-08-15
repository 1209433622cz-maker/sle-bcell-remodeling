# Gate C4B edgeR/limma qualification

- Status: `PASS_C4B_EDGER_QUALIFICATION`
- Real disease effects inspected: **no**
- R: `R version 4.6.0 (2026-04-24 ucrt)`
- edgeR: `4.10.1`; limma: `3.68.4`

| Check | Pass | Detail |
|---|---:|---|
| matrix_dimensions | PASS | 30172 x 89 |
| matrix_column_sums | PASS | R import versus frozen sample libraries |
| matrix_gene_sums | PASS | R import versus Python-exported per-gene sums |
| matrix_integer_nonnegative | PASS | 911,010 nonzero entries |
| null_type1 | PASS | P<0.05 fraction 0.0553 <= 0.0800 |
| null_bias | PASS | median log2FC 0.0011; |value| <= 0.10 |
| signal_effect_recovery | PASS | median recovered log2FC 1.1967 >= 0.80 |
| signal_direction | PASS | sign concordance 1.0000 >= 0.95 |
| signal_sensitivity | PASS | BH sensitivity 1.0000 >= 0.80 |
| signal_empirical_fdr | PASS | empirical FDR 0.0654 <= 0.10 |

The real primary matrix was imported only for dimension and count-conservation checks. No disease coefficient was fitted before this qualification decision.
