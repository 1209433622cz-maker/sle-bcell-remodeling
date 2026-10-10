# RP v3 G2B single-method amendment specification

## Status and evidence identity

This is a prospective freeze for one post-G2 interval amendment. It follows the
canonical `HOLD_G2_APPLICABLE_DOMAIN` result and does not replace, erase or
reinterpret that result. The G2B method has not yet undergone the complete
25-scenario operating-characteristic run.

Current state:

```text
PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED
```

## Only permitted replacement

The sole replacement is an equal-tailed, case/control-stratified paired donor
pairs bootstrap-t interval using an HC3 studentizer. The OLS point estimator,
the ten response targets and the paired donor resampling law are unchanged.
No BCa, basic, symmetric-t, wild-bootstrap, calibrated multiplier or second
candidate may be substituted after G2B results are inspected.

For target `j` and paired bootstrap draw `b`:

```text
t*_bj = (beta*_bj - beta_hat_j) / se*_HC3,bj
CI_j  = [beta_hat_j - q_0.975(t*) se_HC3,j,
         beta_hat_j - q_0.025(t*) se_HC3,j]
```

Quantiles use linear interpolation. Delta targets are fitted to the paired
response difference and receive their own HC3 standard error; independent-SE
addition is prohibited.

## Expanded-row HC3 contract

Each donor is one original observation. A donor selected more than once in a
pairs bootstrap is represented as repeated empirical rows. Frequency-weighted
calculation must be numerically equivalent to explicit row expansion:

```text
sum_i w_i * v_i^2 * e_i^2 / (1 - h_i)^2
```

where `h_i` is the per-appearance leverage. The meat must not use `w_i^2`,
leverage must not be replaced by `w_i h_i`, and repeated draws must not be
collapsed into a cluster sandwich by original donor identity.

## Objects that remain frozen

- generator, calibration model, target and scenario registries;
- nonlinear scoring, `T0`, `pi_ref` and the ten targets;
- all 25 scenarios and the R0/R2/R4 applicable versus R1/R3 boundary split;
- independent oracle truth values and truth-precision receipts;
- 2,000 outer attempts per scenario and 2,000 inner paired bootstraps per
  supported outer attempt;
- original bias, Wilson coverage, exact-null type-I and numerical gates;
- support-stop rules, complete failure accounting and no replenishment.

Changing the interval cannot repair a point-estimator bias failure. The full
G2B adjudicator must therefore apply every original gate unchanged.

## Numerical and random-stream freeze

The shared inner draw is invalid if any target has a nonfinite fit, deficient
rank, active leverage at least `1 - 1e-10`, or HC3 standard error at most
`1e-12`. More than 20 invalid inner draws places that outer attempt in
`HOLD_NUMERICAL_IMPLEMENTATION`; there is no fallback interval and no
replenishment.

G2B uses stage `121` with outer seed base `2026101002`. This is disjoint from
pilot stage 11, original full-G2 stage 21 and development stage 41. Development
attempts and the original G2 attempts are not pooled with G2B.

## Interpretation and stop rule

G2B remains synthetic validation. It cannot access real WP2 responses and
cannot automatically unlock them. A complete G2B PASS only creates a
recommendation for a separate post-G2B review. If the single frozen amendment
fails, the next action is `HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION`,
not another interval search, threshold relaxation or seed change.

## Methodological basis

The amendment is motivated by the higher-order role of studentization in
bootstrap confidence intervals and by finite-sample leverage corrections for
heteroskedastic OLS covariance estimation. These method papers motivate the
design but do not guarantee calibration under this project's empirical-template
data-generating process:

- Hall P. Theoretical Comparison of Bootstrap Confidence Intervals. *Annals of
  Statistics*. 1988;16:927-953. DOI: 10.1214/aos/1176350933.
- MacKinnon JG, White H. Some heteroskedasticity-consistent covariance matrix
  estimators with improved finite sample properties. *Journal of Econometrics*.
  1985;29:305-325. DOI: 10.1016/0304-4076(85)90158-7.
