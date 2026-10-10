# G2B single-method integration and binding review

## Decision

`PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED`

The external diagnostic package is accepted as a technically credible input,
not as a G2B result. Its 901 manifested payloads passed hash and size checks;
42 external tests and the complete 150-object Windows development replay passed.
The project-side implementation is now independently namespaced, hash-bound and
qualified for the full synthetic G2B run.

The canonical full-G2 decision remains `HOLD_G2_APPLICABLE_DOMAIN`. G2B is
`NOT_RUN`; no real WP2 outcome has been read or fitted.

## Independent findings

The candidate correctly isolates the main full-G2 failure as interval
undercoverage: 59/150 applicable target-scenario cells failed coverage, while
only one failed the unchanged point-bias gate. Changing the interval cannot
repair that bias failure. R1 and R3 remain boundary domains and cannot be
reclassified by the amendment.

The weighted HC3 implementation is algebraically and numerically consistent
with explicit bootstrap row expansion. On Windows, 4,500 independent
statsmodels fits agreed to at most `1.47e-14` for coefficients and `4.00e-15`
for HC3 standard errors. Across Linux and Windows development runs, counts,
designs, templates, bootstrap indices and success masks were exact; the largest
interval-endpoint difference was `2.66e-15`.

The development comparison does not demonstrate that coverage is repaired.
Only 100 fresh development outer objects were generated, and the ten targets
within an object are correlated. It justifies a single prospectively frozen
full G2B test.

## Canonical integration

- `rp_v3_g2b_studentized.py` implements the sole interval amendment and rejects
  non-simulated responses.
- `rp_v3_g2b_full_runner.py` forces stage 121, preserves every support stop and
  failure row, and refuses old or unbound output roots.
- `rp_v3_g2b_adjudicate.py` independently applies the unchanged G2 bias,
  Wilson coverage, exact-null type-I, numerical and domain rules.
- `run_rp_v3_g2b_full.ps1` provides validation-only, resumable chunk execution
  and complete-grid adjudication modes.

The canonical tests explicitly compare the new adjudicator with the original
G2 rules, prove that stage 121 differs from stages 21 and 41, verify point and
bootstrap coefficient identity with the parent estimator, and require
fail-closed behavior without the external candidate's all-NaN warning.

## Scientific boundary

This gate does not improve the biological evidence and does not change the
manuscript. It qualifies one synthetic validation procedure. A G2B PASS would
only support a separate post-G2B unlock review; it would not create an automatic
real-effect or submission authorization. A G2B HOLD requires scope contraction,
not another interval search.

## Next action

Run the complete 25-scenario stage-121 grid once, with all original thresholds
and the frozen truth table. Preserve the original G2 outputs and the new G2B
run separately. When the full runner completes, use the bound adjudicator and
then perform a separate advisor review before deciding whether any real WP2
effect may be computed.
