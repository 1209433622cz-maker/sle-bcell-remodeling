# RP v4 Stage I single real delta-profile action record

**Date:** 2026-10-11

**Decision:** `PASS_STAGE_I_WRITE_ONCE_EXECUTION__POSITIVE_DELTA_PROFILE_ASSOCIATION__HOLD_AUTOMATIC_UNLOCK`

## Authorization and immutable execution

The human user explicitly confirmed joint approval by Zhi Chen and Teng Qi of
all six conditions in the commit-bound Stage I decision form and authorized one
write-once execution. The authorization bound:

- Git commit `b413ce09fae520eef0a7a781ee71ddece7606be0`;
- input-manifest SHA-256
  `38174638ebcd927276e8d845a1a27041cf17017cd8088cfd6eb5401d66e213f0`;
- execution-script SHA-256
  `bfaec257573be85c972edb72bb29f441a2e4fcd681402ee59d1528c43f91071d`;
- qualified `D:\bioinfor\python.exe`; and
- the exact two-author order `Zhi Chen`, `Teng Qi`.

The clean synchronized worktree was verified before execution. The result
directory did not exist. The existing Stage I runner was called once. No preview
fit, fallback, donor removal, threshold change or selective rerun occurred.

## Result

The sole estimand was:

`delta_profile = b_X[T0(fixed-profile mixture)] - b_X[T0(pooled counts)]`.

The frozen donor-level OLS/HC3/t(64) result was:

| Quantity | Value |
|---|---:|
| Donors | 68 |
| Controls | 31 |
| Managed-SLE | 37 |
| Point estimate | 0.034925002 |
| HC3 standard error | 0.011558535 |
| t statistic | 3.021577 |
| Two-sided P value | 0.003612459 |
| 95% CI | 0.011834175 to 0.058015829 |
| Maximum leverage | 0.104567146 |

The interval lies above zero. Under the frozen sign convention, the
managed-SLE versus control association is approximately 0.035 T0 score units
greater under the fixed-profile measurement rule than under pooled counts.

## Scientific interpretation

This is evidence that the observed disease association is sensitive to the
prespecified expression-mixing/measurement rule. It is not a causal mediation
proportion, a cell-intrinsic disease effect, proof of the latent measurement
mechanism or validation of the other historical estimands.

The result should not be paraphrased as a percentage of the SLE effect, as
composition explaining the IFN signal, or as proof that pooled counts are
incorrect. It quantifies one prespecified difference between two observed
measurement rules on one frozen support and design.

## Output-only independent audit

The postrun audit does not import the response-construction or estimator code
and does not refit the coefficient. It verifies only the immutable output and
its algebra: authorization, result, receipt, input, code and runtime hashes;
support and leverage; required and forbidden fields; t/P/CI identities; and
all continuing scope locks. No donor-level response vector is exported.

Final verification results:

- output-only postrun checks: 28/28 PASS;
- canonical integrity manifest: 6/6 payload files matched size and SHA-256;
- focused postrun tests: 5/5 PASS;
- combined RP v4 regression and adversarial suite: 77/77 PASS;
- Python compilation and PowerShell parser checks: PASS; and
- postrun coefficient refit: false.

## Outputs

- canonical Stage I result and receipt under
  `phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/`;
- exact author authorization copy;
- independent output audit, machine-readable gate, advisor review and manifest;
- postrun audit source, tests and Windows entry point; and
- this action record.

## Next stage

Proceed to:

`RPV4_STAGE_J__SCIENTIFIC_INTEGRATION_SCOPE_AND_AUTHOR_REVIEW`

Stage J should decide whether this result is incorporated into the redesigned
manuscript as bounded measurement-rule sensitivity evidence, and identify its
exact claim owner and figure or table location. It must not reopen the model,
fit additional targets, unlock external outcomes or convert the association
into a causal claim.
