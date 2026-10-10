# RP v4 Stage H effect-blind real-data applicability contract

Stage H is limited to
`RPV4_STAGE_H__REAL_DATA_APPLICABILITY_AND_EFFECT_BLIND_PREFLIGHT`.

Required work before any real coefficient may be fitted:

1. Bind the exact canonical WP1/WP2 count, design and donor objects by SHA-256.
2. Reconfirm the 68-donor common-support set, four-column rank, metadata joins,
   missingness, leverage and minimum-support conditions without exposing the
   disease coefficient or outcome contrast.
3. Freeze one real estimand only: the disease-coefficient difference between
   the fixed-profile mixture score and pooled-count score (`delta_profile`).
4. Demonstrate that real-data support, leverage, library and mixture geometry
   lie within the prespecified synthetic applicability envelope; report any
   extrapolation rather than removing donors or changing thresholds.
5. Freeze one OLS/HC3/t(64) execution script and a write-once result schema.
6. Obtain a new author approval after the effect-blind preflight.

Stage H may not inspect, fit or preview the real disease coefficient, P value or
interval. It may not unlock the other nine historical targets, external disease
or activity outcomes, S2 outcome tuning, WP4, manuscript replacement,
submission, Release or Zenodo. Failure of real-data applicability retains the
synthetic result as a methods finding and closes real `delta_profile` execution.
