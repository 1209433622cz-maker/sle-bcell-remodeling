# RP v4 Stage I advisor review

## Decision

`PASS_STAGE_I_WRITE_ONCE_EXECUTION__POSITIVE_DELTA_PROFILE_ASSOCIATION__HOLD_AUTOMATIC_UNLOCK`

The two authors approved all six frozen conditions, and the exact write-once
runner produced one `delta_profile` result under the bound commit and qualified
Windows runtime. No donor-level response was exported, no other historical
target or external outcome was fitted, and no fallback or selective rerun was
performed.

## Result

- Point estimate: `0.034925002` T0 score units
- HC3 standard error: `0.011558535`
- Two-sided t(64) 95% CI: `0.011834175` to `0.058015829`
- Two-sided P value: `0.003612459`

The interval is above zero. Under the frozen sign convention, the managed-SLE
versus control association is approximately 0.035 T0 score units greater for
the fixed-profile mixture rule than for the pooled-count rule. This supports a
real-data measurement/mixing-rule sensitivity result. It is not a mediation
proportion, a causal cell-intrinsic effect, proof of a latent data-generating
mechanism, or permission to inspect additional targets.

## Independent output audit

All 28 output-only integrity and algebra checks passed. The
audit verified the authorization, input, execution-code, runtime, result and
receipt hashes; support and leverage; t statistic, P value and interval
identities; and all scope locks. It did not reconstruct the response or refit
the coefficient.

## Next stage

Proceed to `RPV4_STAGE_J__SCIENTIFIC_INTEGRATION_SCOPE_AND_AUTHOR_REVIEW`.
Stage J should decide whether this bounded sensitivity result belongs in the
revised manuscript and, if so, its exact claim owner and figure/table location.
It must not reopen the estimator, fit other targets, unlock external outcomes
or treat the result as causal.
