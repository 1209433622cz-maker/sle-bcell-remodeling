# RP v3 G2 generator, truth engine and execution-freeze review

**Date:** 2026-10-10
**Decision:** `PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2`

## Scope reviewed

This review independently examined the received technical candidate rather than inheriting its PASS label. The review covered the 934-file bundle manifest, generator and estimator source, independent truth engine, 25-scenario and 10-target tables, all 50 pilot attempts, 60,000 inner bootstrap fits, checkpoint/resume behavior, truth-precision ladders and the proposed scientific domain.

No new real WP2 disease coefficient was computed. The manuscript, figures, submission package, GitHub Release and Zenodo record were not opened for replacement.

## Technical findings

1. The received archive contains 934/934 registered payloads with no missing, altered or unregistered payload.
2. The candidate's 48/48 component tests pass under the local Windows Python 3.13.7 / NumPy 2.3.3 runtime.
3. An independent local rerun reproduced all 50 pilot attempt statuses: 30 interval-computed attempts and 20 prespecified support stops. All 60,000 inner paired bootstrap fits succeeded and resume reused all 50 checkpoints without replenishment.
4. All 50 cell-count arrays, all 50 thirteen-category count arrays, all 50 design arrays, all 50 template-index arrays and all 30 bootstrap-index arrays were byte-identical across Linux and Windows.
5. Platform-dependent floating-point reductions were limited to at most `8.88e-16` in responses and point estimates and `2.22e-16` in interval endpoints. No gate, support decision or attempt status changed.
6. The local independent truth rerun reproduced all 25 scenario statuses and final effort levels. All 250 target-scenario truths met the frozen MCSE rule. The maximum cross-platform truth difference was `1.11e-16`; support probabilities were identical.
7. The promoted generator, estimator and truth-engine bytes retain the independently audited candidate hashes. The full scheduler and adjudicator add fail-closed chunk binding, complete outer-attempt accounting and compact deterministic checkpoints without granting access to real WP2 responses.

## Scientific interpretation of the DGP

The generator is acceptable for the declared G2 question, with explicit limits. It samples whole five-bin donor templates without source disease labels, retains the twelve program genes plus the full remaining-library category, and applies the same nonlinear score operator as WP2. This preserves empirical joint template heterogeneity but does not recreate the unknown biological covariance, cell-level overdispersion or annotation retraining process.

Truth is defined on the observed measurement scale conditional on the registered support rule. This matters because a depth-only perturbation can induce a nonzero coefficient after finite-count sampling and `log2(CPM + 0.5)`. C0_R2 is therefore not a false-positive scenario for a latent zero; its independently integrated observed truth must be used. The same rule applies to arm-specific capture perturbations.

R1 and R3 are retained as mandatory boundary domains. Their low whole-replicate support is not repaired by donor deletion, redraw, bin merging or zero filling. They report where the complete five-bin estimator ceases to be broadly applicable. R0, R2 and R4 form the applicable performance domain for bias, coverage and registered true-null type-I adjudication.

The minimum of 274 supported attempts for a performance decision is fixed before full G2. It follows from the already frozen Wilson coverage rule: below 274, no integer coverage count can place the 95% Wilson interval wholly within `[0.925, 0.975]`.

## Gate decision

The three previously empty implementation fields now have real, independently checked objects: the sufficient-count generator, the independent nonlinear truth engine and the truth-precision receipt. The local runtime, full scheduler, adjudicator, target/scenario/acceptance registries, calibration object and domain policy are all hash-bound.

This authorizes **synthetic full-G2 execution only**. It is not a G2 PASS and does not unlock WP2 real effects. Current state:

- `G2=NOT_RUN`;
- `WP2_REAL_EFFECT_UNLOCK=false`;
- `WP4=HOLD_CONDITIONAL`;
- manuscript/figure replacement, submission, Release and Zenodo remain HOLD.

## Next stage

Proceed to `G2_FULL_EXECUTION_R0_CORE_FIRST` using the frozen full-run stage and 2,000 x 2,000 procedure. R0 should be executed first as an operational checkpoint, but all 25 scenarios must ultimately run before final adjudication. R1/R3 failures must remain visible and must not be averaged away or reclassified after results are known.
