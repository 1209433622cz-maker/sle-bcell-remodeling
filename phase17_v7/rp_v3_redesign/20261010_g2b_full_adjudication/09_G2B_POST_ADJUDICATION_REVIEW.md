# RP v3 full G2B post-adjudication review

**Date:** 2026-10-10  
**Binding:** `ce40a673df8c051e4eb7036292fe5827eb6ce8b552ee56964affc61d1fa25d0c`  
**Decision:** `HOLD_G2B_APPLICABLE_DOMAIN`  
**Scope decision:** `HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION`

## Executive decision

The registered G2B grid is complete and computationally valid. The single
prospectively frozen HC3 bootstrap-t amendment materially reduced the original
coverage deficit, but it did not satisfy the ten-target applicable-domain
conjunction. Real WP2 disease effects remain locked. The interval-development
branch is closed under the RP v3 stopping rule.

This is not a software failure and not an incomplete run. It is a valid
negative operating-characteristic result.

## Execution and integrity

- 25/25 registered scenarios completed.
- 2,000 outer attempts were accounted for in every scenario.
- 2,000/2,000 chunks are complete and hash-bound.
- 50,000 outer attempts produced 500,000 target-level rows.
- 30,056 objects received an interval; 19,944 reached a prespecified support
  stop; no numerical failure occurred.
- All 60,112,000 attempted inner bootstrap draws succeeded.
- The canonical raw run contains 6,004 files and 17,994,581 bytes; the three
  independently regenerated adjudication files bring the local run root to
  6,007 files and 18,077,293 bytes.
- The formal adjudication and a fresh independent readjudication are
  byte-identical for all three official files.
- Real WP2 responses were neither loaded nor fitted.

An interruption left an empty `C1_R4/chunk_1276_1300` directory. The empty
directory was moved to local quarantine, and only that registered range was
recomputed. No existing payload was overwritten. The resumed wrapper then
completed all remaining scenarios and formal adjudication.

## Applicable-domain result

R0, R2 and R4 remain the frozen applicable domain. R1 and R3 remain mandatory
reported support/stress boundaries and do not enter the applicable conjunction.

Among the 150 applicable target-scenario rows:

| Outcome | Count |
|---|---:|
| PASS | 133 |
| HOLD | 17 |
| Bias failures | 6 |
| Coverage failures | 11 |
| Exact-null type-I failures | 1 |
| Truth-precision failures | 0 |
| Numerical failures | 0 |

The type-I failure overlaps a coverage failure at `C0_R0 / delta_profile`; it
is not an additional eighteenth HOLD row.

Four targets passed all 15 applicable scenarios: `beta_bin_1`, `beta_bin_5`,
`beta_S_cellref` and `beta_S_profile`. Six did not: `beta_B`, `beta_bin_2`,
`beta_bin_3`, `beta_bin_4`, `delta_cellref` and `delta_profile`. The frozen gate
requires the complete target set, so target-wise cherry-picking is not an
authorized unlock path.

## G2 to G2B comparison

G2B improved the applicable-domain result from 90/150 to 133/150 PASS rows.
Coverage failures fell from 59 to 11. This demonstrates that the amended
interval addressed much of the percentile-bootstrap undercoverage.

The improvement is not a PASS:

- applicable HOLD rows remain 17/150;
- six bias failures appeared in the independent stage-121 Monte Carlo sample;
- `delta_profile` worsened from 8/15 to 6/15 PASS and retained nine coverage
  failures plus one overlapping exact-null type-I failure;
- no target-specific exception was predeclared for partial unlock;
- the final machine-readable decision explicitly sets
  `recommended_for_post_G2B_unlock_review=false` and
  `WP2_REAL_EFFECT_UNLOCK=false`.

The point estimator was unchanged. The additional bias failures therefore must
not be described as caused by the interval replacement; they show that the
independent Monte Carlo namespace exposed near-threshold point-estimator
behavior that was not sufficient for the frozen conjunction.

## Scientific interpretation

The result supports a narrower conclusion than originally planned: the current
data/operator/design combination does not justify the full WP2 decomposition of
disease effects under the prespecified operating-characteristic standard. This
does not invalidate WP1, the historical process-level B_CONV IFN/ISG result, or
the permanent identity, transfer and mechanistic boundaries.

G2B must not be used to select a favorable subset of targets, relax thresholds,
drop R2/R4 stress scenarios, change seeds or inspect real WP2 coefficients.
Negative identifiability is a valid RP v3 result.

## Final authorization state

```text
G2: HOLD_G2_APPLICABLE_DOMAIN
G2B: HOLD_G2B_APPLICABLE_DOMAIN
WP2 real-effect fitting: LOCKED
WP4: HOLD_CONDITIONAL
manuscript replacement: HOLD
submission: HOLD
GitHub Release / Zenodo update: HOLD
```

The next permitted stage is
`RP_V3_SCOPE_CONTRACTION_AND_WP3_RESULT_BLIND_GO_NO_GO`, governed by
`10_G2B_SCOPE_CONTRACTION_CONTRACT.md`.
