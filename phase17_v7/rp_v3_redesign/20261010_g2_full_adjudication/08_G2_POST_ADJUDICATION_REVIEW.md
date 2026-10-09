# RP v3 full-G2 post-adjudication review

## Decision

**HOLD_G2_APPLICABLE_DOMAIN**

The complete 25-scenario grid was adjudicated under the frozen binding
`5546f5931069f2d09b784b0d365fa58c433a38c6e8edb5e7f5a55329585bfbf3`. The grid contains 50,000 outer attempts,
60,106,000 paired-bootstrap fits and no numerical failures.
Real WP2 effects were not loaded or fitted.

The applicable domain contains 150 target-scenario cells. Of these,
90 passed and 60
were held. None of the ten targets passed all 15 required applicable scenarios,
so no target is recommended for unlock and `WP2_REAL_EFFECT_UNLOCK` remains false.

## Failure anatomy

- Truth precision: 150/150 applicable cells passed.
- Numerical stability: 150/150 applicable cells passed.
- Bias: 149/150 passed. The single failure was
  `C0_R4 / beta_bin_3`.
- Coverage: 91/150 passed and
  59/150 failed. Among failed cells, 59 had a
  Wilson lower bound below 0.925 and 0 had an upper bound above 0.975.
- Exact-null type-I error: 10/10
  registered cells passed.

The dominant defect is therefore interval undercoverage, not truth imprecision,
false-positive inflation at the registered exact nulls, support replenishment or
numerical instability. Small disease coefficients in real data cannot override
this simulation result.

## Boundary regimes

R1 (`rarity_support`) and R3 (`adjacent_mislabeling`) remain mandatory reported
stress domains. They do not enter the applicable-domain conjunction and cannot
be converted into PASS rows. Across the full grid, 19,947
outer attempts stopped for prespecified support reasons; these are reported
rather than replenished.

## Scientific interpretation

The current paired percentile-bootstrap implementation does not satisfy the
predeclared G2 coverage contract across the applicable domain. RP v3 therefore
does not authorize estimation or interpretation of real WP2 disease effects
with this implementation. This HOLD is an informative result about the proposed
estimation route, not a failure to obtain a preferred biological direction.

## Next stage

Proceed only to `RP_V3_G2_HOLD_DIAGNOSTIC_AND_AMENDMENT_GATE`. This stage may
diagnose the interval procedure and prospectively freeze one scientifically
justified replacement implementation. It may not relax acceptance thresholds,
remove adverse scenarios, inspect real WP2 responses or overwrite this HOLD.
Any amended G2B must use a new versioned binding, the unchanged target/scenario
contract, fresh random streams and a complete new adjudication before a separate
unlock review can even be considered.
