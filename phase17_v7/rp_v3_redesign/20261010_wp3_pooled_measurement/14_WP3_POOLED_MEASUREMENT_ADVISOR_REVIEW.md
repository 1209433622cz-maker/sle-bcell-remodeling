# RP v3 WP3 pooled measurement advisor review

**Date:** 2026-10-10

**Decision:** `PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION`

## Review basis

The received independent-review ZIP was treated as evidence, not as an
automatically accepted result. Its 94 manifested payloads and 31 focused tests
passed. The package was replayed on Windows, followed by 4,389 independent
scalar comparisons. Nine of eleven result files were byte-identical across the
candidate Linux run and the Windows replay. The remaining two differed only in
floating-point serialization or values at a maximum absolute difference of
`8.88e-16`. This supports numerical equivalence, not cross-platform byte
identity.

All 16 packaged input copies matched current canonical files in size and
SHA-256. The project-side implementation then used those live canonical inputs
and the complete local Stage 0B source operator, rather than the package's
function excerpt. The Stage 0B operator SHA-256 is
`13a5ea7bf395968cd95317e9ce49344290e22c41bec8d2d4068fc5b221676853`.

## Project-side verification

- 13/13 focused boundary tests passed.
- 25/25 real-input, source-closure and operator checks passed.
- 4,389/4,389 independent scalar comparisons passed; maximum absolute error
  was `1.776e-15` against a tolerance of `1e-11`.
- A second project-side run regenerated all 13 machine outputs byte-for-byte.
- Analytical outputs contained no disease, cohort, donor-name, age, treatment
  or activity fields.
- The canonical and external-candidate tables agreed exactly except for a
  maximum `8.88e-16` floating-point difference in the 648-row gene/LOO table.

The source-parity incident in the external review remains part of provenance.
Its first real attempt computed scores in memory and then stopped before writing
results because a vectorized reduction differed from the frozen row-wise source
operator by at most `3.33e-16`. The exact source operation was restored; the
criterion was not relaxed. The canonical project implementation directly
checks the complete frozen source operator and reproduces the final result.

## Scientific result

Across all 54 prespecified source-label B_CONV donor pseudobulks:

- pooled `T_frozen` versus `T_rank` Spearman correlation was `0.985744`;
- maximum and mean absolute between-transform rank displacement were `6` and
  `2.111`, respectively;
- the 12 leave-one-gene-out correlations with full `T_frozen` ranged from
  `0.995883` to `0.999161`;
- the largest leave-one-gene-out rank displacement was `6` after omitting
  `OAS2`; the lowest correlation was `0.995883` after omitting `LY6E`;
- `IFIT1`, `IFIT3` and `OAS2` were detected in 47/54, 52/54 and 53/54 donor
  pseudobulks; the other nine genes were detected in 54/54;
- the frozen 18,873-symbol rank background represented 95.09%-96.69% of each
  eligible full measured library, confirming why it must not replace the full
  32,738-feature denominator used by `T_frozen`.

These results add one bounded measurement fact beyond Stage 0B computability:
the prespecified 12-gene ordering is stable to the alternate frozen transform
and to every single-gene omission in this pooled external object set.

## Boundary of the PASS

This is not external disease validation. Disease labels were not loaded and no
HC/SLE, childhood/adult, treatment or activity summary was generated. No disease
coefficient, confidence interval, P value, ROC curve, threshold or clinical
calibration was calculated. `T_frozen` remains primary and `T_rank` remains a
sensitivity transform; neither was selected from the observed result.

The result does not validate cross-platform equivalence, source-label-
independent transfer, a biomarker, a causal mechanism or a new manuscript
claim. WP2 remains closed after G2B, WP3 disease-outcome execution remains
unauthorized, WP4 remains conditional HOLD, and manuscript/submission/release
objects remain unchanged.

## Decision

The limited WP3 measurement question is complete and technically accepted.
Further prefit loops, transform searches or disease-effect estimation are not
scientifically justified under RP v3.

```text
current: PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION
WP2_REAL_EFFECT_UNLOCK: false
WP3_OUTCOME_EXECUTION_AUTHORIZED: false
WP4: HOLD_CONDITIONAL
submission: HOLD
next: RP_V3_AUTHOR_SCOPE_CLOSURE_DECISION
```
