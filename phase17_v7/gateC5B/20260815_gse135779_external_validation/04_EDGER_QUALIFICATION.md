# Gate C5B edgeR/limma qualification

- Status: `PASS_C5B_EDGER_QUALIFICATION`
- Real external disease effects inspected: **no**
- R: `R version 4.6.0 (2026-04-24 ucrt)`
- edgeR: `4.10.1`; limma: `3.68.4`

| Check | Pass | Detail |
|---|---:|---|
| all_frozen_imports | PASS | 5 main plus 8 source-label matrices |
| null_type1 | PASS | P<0.05 fraction 0.0553 <= 0.0800 |
| null_bias | PASS | median log2FC 0.0011; |value| <= 0.10 |
| signal_effect_recovery | PASS | median recovered log2FC 1.1967 >= 0.80 |
| signal_direction | PASS | sign concordance 1.0000 >= 0.95 |
| signal_sensitivity | PASS | BH sensitivity 1.0000 >= 0.80 |
| signal_empirical_fdr | PASS | empirical FDR 0.0654 <= 0.10 |

All 13 real matrices were imported only for dimensions and count conservation. No real disease coefficient was fitted before this decision.
