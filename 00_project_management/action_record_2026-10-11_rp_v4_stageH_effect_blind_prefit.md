# RP v4 Stage H effect-blind real-data applicability preflight

**Date:** 2026-10-11
**Stage:** `RPV4_STAGE_H__REAL_DATA_APPLICABILITY_AND_EFFECT_BLIND_PREFLIGHT`
**Decision:** `PASS_STAGE_H_EFFECT_BLIND_APPLICABILITY__HOLD_STAGE_I_AUTHOR_SIGNOFF`

## Purpose and authorization boundary

This round followed the Stage G contract after final synthetic G2C validation.
It was authorized to bind and inspect real-input support, design and measurement
geometry only. It was not authorized to construct, inspect, fit or preview the
real disease response, coefficient, P value or interval.

The work did not open external disease/activity outcomes, S2 tuning, WP4,
manuscript replacement, submission, GitHub Release or Zenodo.

## Canonical inputs bound

The Stage H input manifest binds the following classes of objects by byte size
and SHA-256:

- frozen 68-donor common-support set and four-column design;
- A1 donor-bin raw sufficient counts, frozen T0 reference and `pi_ref`;
- effect-blind WP2 geometry and composition coordinates;
- G2 calibration model and Stage C single-estimand/DGP contracts;
- Stage G final synthetic gate and metric summary;
- the prospective Stage I single-result execution script.

No file from the WP1 result directory and no real-effect table was included in
the binding manifest.

## Effect-blind checks performed

The canonical preflight returned 9/9 support/design PASS:

1. 68 unique common-support donors;
2. 31 control and 37 managed-SLE donors;
3. four-column design rank 4;
4. zero design missingness;
5. zero geometry missingness;
6. 68/68 donor-design joins aligned;
7. minimum donor-bin support 30 cells;
8. maximum outcome-blind leverage 0.104567146293265;
9. real effect fit not performed.

It also returned 9/9 synthetic-applicability PASS:

- real design versus synthetic design: exact identity;
- real cell template versus 68 x 5 calibration template: exact identity;
- captured-UMI-per-cell rate maximum absolute difference: `4.55e-13`;
- regularized 12-gene-plus-background probabilities: exact identity;
- `pi_ref`: identity within `1e-15`;
- all 340 donor-bin supports at least 30 cells;
- maximum leverage identical to the frozen anchor and below 1;
- cell-composition closure error at most `3.33e-16`;
- captured-UMI-composition closure error at most `3.33e-16`.

Observed cells ranged from 30 to 946 per donor-bin. Full captured libraries
ranged from 18,671 to 2,333,206 UMI. Captured UMI per cell had 5th, median and
95th percentiles of 678.53, 1,618.07 and 2,528.95.

## Applicability interpretation

No observed support, leverage, library or mixture-geometry extrapolation was
detected because the real input is the exact calibration anchor used by the
synthetic generator. This is strong evidence that the validated procedure was
tested around the actual observable design and measurement geometry.

This conclusion is deliberately bounded. Aggregate real inputs cannot prove
that the unknown latent overdispersion, capture-correlation or label-contamination
mechanism equals one of the simulated DGPs. Stage G's near-limit cases remain
part of the interpretation: C4_X3 bias ratio 0.098054 against 0.10 and C0_X3
Wilson coverage upper bound 0.972152 against 0.975.

## Frozen real estimand and execution

Only `delta_profile` is retained:

`T0(fixed-profile mixture) - T0(pooled counts)` at donor level, followed by the
`is_managed` coefficient in the unchanged four-column OLS design, HC3 influence
variance and a two-sided t(64) interval.

The interpretation is an association difference between two observed
measurement/mixing rules. It is not a causal mediation proportion and not a
cell-intrinsic disease effect.

The prospective Stage I script writes exactly one result JSON and one receipt.
It exports no donor-level response and contains no fallback or alternate target.
Authorization is checked before response construction. The unsigned canonical
template was tested and rejected without creating an output directory.

## Verification performed

- Stage H focused tests: 5/5 PASS.
- Combined RP v4 G2C/Stage A/D/E2/F2/H regression and adversarial suite:
  66/66 PASS under the repository `PYTHONPATH` contract.
- Canonical support/design audit: 9/9 PASS.
- Canonical applicability comparison: 9/9 PASS.
- Stage H integrity manifest: 10/10 files matched size and SHA-256.
- Search for populated point estimate, P value or interval fields in Stage H
  outputs: zero occurrences.
- Git diff whitespace check: PASS before documentation integration.

## Files created

- `audit_tools/rp_v4_stageH_effect_blind_prefit.py`
- `audit_tools/rp_v4_stageI_real_delta_profile.py`
- `audit_tools/run_rp_v4_stageH_preflight.ps1`
- `audit_tools/test_rp_v4_stageH.py`
- `phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/`
- this action record and synchronized repository navigation documents.

## Next-stage decision

Proceed only to:

`RPV4_STAGE_I__AUTHOR_SIGNOFF_AND_SINGLE_REAL_DELTA_PROFILE_EXECUTION`

Before any fit, Zhi Chen and Teng Qi must issue a new exact authorization that
binds the post-Stage-H Git commit, input-manifest SHA-256
`38174638ebcd927276e8d845a1a27041cf17017cd8088cfd6eb5401d66e213f0`,
execution-script SHA-256
`bfaec257573be85c972edb72bb29f441a2e4fcd681402ee59d1528c43f91071d`
and `D:\bioinfor\python.exe`.

After approval, the result must be executed once and reported whether positive,
null or imprecise. No preview, donor removal, threshold change, fallback,
alternate target or selective rerun is allowed. All downstream scientific and
submission decisions require a separate post-result review.
