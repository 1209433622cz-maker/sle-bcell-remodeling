# Next-stage decision: fit frozen Gate C3A abundance models

## Advisor decision

Gate C3 protected-metadata joining and design freezing passed. The three model
matrices were created before any disease effect estimate was viewed. Gate C3A may
now estimate `B_ASC` abundance effects within the exact frozen scope.

## Primary objective

Fit `C3A_PRIMARY_C4_MANAGED_VS_NORMAL` using 43 normal and 47 managed cohort-4
sample strata. Model `asc_cells` out of `total_cells` with an overdispersed count
likelihood and fixed effects for managed status, centered age and ethnicity.

Report, in order:

1. adjusted effect size and 95% confidence interval;
2. model dispersion and convergence diagnostics;
3. absolute model-adjusted proportions for interpretability; and
4. the prespecified p-value, without using it as the sole evidence criterion.

## Required internal replication

Apply the frozen cohort-2 European-American female matrix without changing its
restriction or covariates. This set contains 21 normal and 43 managed strata. It is
an internal directional replication with substantial age imbalance, not an
independent validation dataset.

The primary result is considered internally concordant only when cohort-2 direction
matches cohort 4. A non-significant but directionally consistent estimate should be
reported honestly with its confidence interval.

## Secondary analysis

Fit the cohort-3 flare-versus-normal matrix (18 normal, 16 flare) with centered age
and ethnicity adjustment. This is a secondary disease-activity analysis. Cohort-3
treated and managed groups remain descriptive because only five and four eligible
strata are available.

## Mandatory sensitivities

- Repeat the abundance workflow at minimum B-cell thresholds 20 and 100.
- Exclude the 30 explicit non-B `ct_cov` cells.
- Exclude residual doublet automatic calls.
- Evaluate ASC presence and positive abundance as a two-part sensitivity.
- Confirm that no result depends on a single high-depth or high-ASC sample.

## Decision after Gate C3A

If cohort 4 is supported and cohort 2 is directionally concordant, proceed to
sample-level continuous-program analysis and B-cell pseudobulk expression, while
prioritizing independent dataset validation.

If the primary effect is unsupported or direction reverses, do not manufacture a
composition claim. Shift the main analysis to prespecified continuous programs and
pseudobulk transcription, retaining abundance as a negative or secondary result.

## Publication position

Even a successful Gate C3A result is not sufficient for an upper-Q1 manuscript.
Independent validation, cohort-aware pseudobulk biology and external regulatory or
mechanistic evidence remain required before the central claim and final journal are
selected.
