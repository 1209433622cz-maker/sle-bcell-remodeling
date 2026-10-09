# RP v3 WP2 effect-free preflight advisor review

**Created:** 2026-10-10T03:09:20+08:00
**Decision:** `PASS_WP2_EFFECT_FREE_PREFLIGHT__HOLD_G2_EXECUTION_IMPLEMENTATION_REQUIRED`

## What passed

- The canonical 68-donor population remains 31 controls and 37 source-defined
  managed-SLE donors; the four-column base design is rank 4/4.
- All five frozen A1 bins are observed for every donor, with a minimum of
  30 cells per donor-bin.
- Gene counts, full captured-library totals and cell counts exactly partition
  the parent A0 sufficient statistics.
- Captured-UMI reconstruction recovers pooled CPM to a maximum absolute error of
  1.137e-13.
- Cell fractions and captured-UMI fractions are measurably different: median
  absolute difference 0.015954,
  maximum 0.093275.
- Four frozen cell-fraction ILR coordinates produce an 8/8 full-rank optional
  conditional design. Five raw fractions plus an intercept remain closure
  redundant (rank 8/9).
- No disease coefficient, disease-stratified expression summary or new IFN score
  was calculated in this gate.

## Scientific adjudication

The WP1 fixed-profile mixture and the new cell-reference reconstruction are
distinct measurement targets. The latter preserves observed captured UMI per
cell and therefore still combines biological RNA output with capture efficiency;
it is not an absolute-RNA or causal cell-composition estimand. The five bins are
frozen intervals of the continuous A1 axis, not validated hard B-cell subtypes.

The target, 25-cell scenario and numerical-acceptance registries are frozen now,
before G2 results. This does not complete the execution contract. The supplied
external candidate contains no simulation generator, independently implemented
truth engine or truth-precision receipt. The project-side preflight now binds
the validated sufficient counts, branch assignment, result-blind geometry
calibration and runtime receipt; the three genuinely missing execution hashes
remain null in `10_G2_IMPLEMENTATION_CONTRACT.json`.

## Next gate

Proceed to `G2_GENERATOR_TRUTH_ENGINE_AND_TECHNICAL_PILOT`. The technical pilot
must prove raw/sufficient-count observation equivalence, independent nonlinear
truth calculation, exact attempt accounting, resumability and the actual paired
bootstrap interval implementation. Only then may the G2 execution contract be
hash-completed. WP2 real effects, WP4, manuscript/figure replacement, submission,
Release and Zenodo remain on hold.
