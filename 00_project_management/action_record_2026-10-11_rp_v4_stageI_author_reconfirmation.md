# RP v4 Stage I joint-author reconfirmation

**Date:** 2026-10-11

## Author statement received

The user explicitly reported that Zhi Chen and Teng Qi jointly approve every
condition in the RP v4 Stage I template.

## Six conditions reconfirmed

1. Approve the exact 68-donor design containing 31 controls and 37
   source-defined managed-SLE donors.
2. Approve the single `delta_profile` estimand.
3. Approve the single donor-level OLS method with HC3 variance and a two-sided
   t(64) interval.
4. Approve one write-once result with no preview, fallback or selective rerun.
5. Acknowledge that the result is an association/measurement-rule sensitivity,
   not causal mediation or a cell-intrinsic disease effect.
6. Acknowledge that the result does not automatically unlock another target,
   external outcome, WP4, manuscript replacement or submission.

## Binding and interpretation

This statement is recorded as a post-execution reconfirmation. The original
Stage I authorization and its one permitted execution already completed under
the exact bound commit, runtime, input manifest and execution-script hash.

The reconfirmation is bound to:

- Stage I template SHA-256:
  `9775f2930b6ea2a1262b6adf2418c9cad6e6a7433a2e4fc7e7e5cbb94f4eece6`;
- executed author GO SHA-256:
  `9d8a74cda21f6a72cce91660abd3c8bbb6d13274d235aff98a58b62179a109ae`;
- Stage I result SHA-256:
  `068c7492406575c61445680b31cf83db17506842f11be0e269629eaa03a754c1`;
- Stage I integrity-manifest SHA-256:
  `731340905b94934ee0d889c228c2a39e95c5387655f17ed1ddd6e1c5294cd32e`.

It does not create a new authorization token and cannot be used to run Stage I
again. `new_execution_authorized=false` and `rerun_permitted=false` are
recorded explicitly.

## Project state

No scientific result, manuscript, figure, Source Data file, Stage I output or
current gate was changed. The active state remains:

`PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION`

The next gate remains:

`RPV4_STAGE_M__RAW_RECONSTRUCTION_AUTHORIZATION_AND_DISEASE_BLIND_COUNT_PIPELINE_FREEZE`
