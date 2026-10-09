# RP v3 WP1 annotation-sensitivity review

## Gate decision

**PASS_WP1_ANNOTATION_SENSITIVITY_REVIEW_REQUIRED**

The first disease-effect fit was performed only after the dated prefit contract passed. All three branches use the same 68 donors, the same frozen four-column design and the original 43-control T0 reference.

## Estimates

| Estimand | Estimate | Paired bootstrap 95% CI |
|---|---:|---:|
| beta_A0 | 1.037152 | 0.598263 to 1.477349 |
| beta_A1 | 1.072077 | 0.630517 to 1.518759 |
| beta_A2 | 1.037718 | 0.598753 to 1.477793 |
| delta beta A1 - A0 | 0.034925 | 0.013789 to 0.057130 |
| delta beta A2 - A0 | 0.000567 | 0.000000 to 0.001424 |

Bootstrap completion was 2000/2000; failure rate 0.000%. No formal p value, multiplicity claim, equivalence margin or causal interpretation is introduced.

## Interpretation boundary

`beta_A1` is estimated after common-composition reconstruction on the linear CPM scale and therefore combines identity-axis representation with composition standardization. Its delta from A0 is not a pure annotation effect and is not a mediated fraction. A2 excludes the historical strong-ISG feature list but retains LY6E, so it is not a fully IFN12-excluded representation.

WP1 does not unlock WP4, manuscript replacement or submission. The next gate is a result-blind full G2 simulation that exactly reproduces the final A1 operator, 68-donor support/missingness process and paired bootstrap estimator.
