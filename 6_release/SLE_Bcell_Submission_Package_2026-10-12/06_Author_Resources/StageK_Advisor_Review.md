# RP v4 Stage K advisor review

## Decision

`PASS_STAGE_K_LIMITED_SOURCE_INTEGRATION__HOLD_SUBMISSION_AND_EXTERNAL_OUTCOMES`

## Evidence ownership

Stage I and RP v3 WP1 use the same 68 donors, the same `delta_profile`
estimand, the same outcome definition and the same four-column design. Their
point estimates differ by approximately `6.94e-18`, so they are not two
independent positive findings.

The Stage K integration therefore treats Stage I as an uncertainty
re-estimation for the existing measurement-rule contrast. The paired
percentile interval is retained as the earlier WP1 analysis; the HC3-t(64)
interval is retained as the G2C-qualified procedure within the tested synthetic
domains. The nominal Stage I P value remains explicitly outcome-exposed.

## Bounded manuscript integration

- Methods: exact score operators, donor design, HC3-t(64) procedure and
  simulation-qualification boundary.
- Discussion: measurement-rule sensitivity only; no mediation, cell-intrinsic
  mechanism, clinical calibration or independent confirmation claim.
- Supplementary Table S10: both intervals shown side by side for one frozen
  contrast.
- Source Data: two full-precision rows with `SAME_DONORS_SAME_ESTIMAND`.
- Figures 1-5 and Supplementary Figures S1-S10: unchanged.

No Stage I computation was rerun. No submission package, GitHub Release or
Zenodo record was changed.

## Next gate

`RPV4_STAGE_L__EXTERNAL_COHORT_UNIQUE_QUESTION_AND_RAW_COUNT_GATE`

The next scientific question must add independent clinical information rather
than repeat the same 68-donor contrast. Raw external data, external outcomes and
submission remain closed until their prospective gates pass.
