# RP v3 next-stage contract after full-G2 HOLD

## Gate name

`RP_V3_G2_HOLD_DIAGNOSTIC_AND_AMENDMENT_GATE`

## Objective

Determine whether the WP2 interval procedure has one defensible, prospectively
specified repair. The current G2 result remains the canonical assessment of the
frozen percentile-bootstrap implementation.

## Permitted work

1. Diagnose undercoverage using synthetic outputs and mathematical properties of
   the interval construction.
2. Compare candidate interval constructions only in a clearly labelled
   development sandbox that cannot read real WP2 responses.
3. Select at most one replacement on methodological grounds, then freeze its
   code, estimands, scenario grid, thresholds, random-stream namespace and
   adjudicator before any full G2B execution.
4. Re-run all 25 registered scenarios with 2,000 outer attempts and 2,000 paired
   bootstrap attempts per supported outer attempt, preserving support stops and
   all failure rows.

## Prohibited work

- loading, fitting or previewing real WP2 disease responses;
- relaxing the frozen bias, coverage, type-I or numerical thresholds;
- deleting or reclassifying adverse scenarios after seeing results;
- changing targets, truth values or the applicable/boundary domain split to
  obtain PASS;
- overwriting the current G2 output or describing it as passed;
- proceeding to manuscript claims, WP4, submission or release work.

## Exit states

- `HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION`: no single defensible repair
  is frozen; real WP2 effects stay locked and the research question is narrowed.
- `PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED`: one amended method is
  frozen and ready for full synthetic execution.
- Only a complete G2B PASS followed by an independent post-G2B review may produce
  an unlock recommendation. Unlock is never automatic.
