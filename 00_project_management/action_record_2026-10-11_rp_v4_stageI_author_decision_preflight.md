# RP v4 Stage I author-decision preflight action record

**Date:** 2026-10-11

**Scope:** post-Stage-H exact-baseline verification and unsigned two-author decision packet

**Scientific effect status:** not loaded, not constructed and not fitted

**Decision:** `READY_FOR_EXPLICIT_TWO_AUTHOR_DECISION__STAGE_I_NOT_AUTHORIZED`

## Purpose

This round continued RP v4 without treating a general instruction to continue
as the separate, explicit approval required from both named authors for the
single real `delta_profile` execution. The work was therefore restricted to an
effect-firewalled author-decision preflight.

The preflight creates a precise approval object only after checking the clean,
synchronized `main` branch, the Stage H integrity manifest, the frozen real
input manifest, the exact Stage I execution script and the qualified Windows
runtime. It then passes an intentionally unsigned draft to the real runner and
requires rejection before response construction.

## Implemented controls

1. Added `audit_tools/rp_v4_stageI_author_preflight.py`.
2. Added six regression tests in
   `audit_tools/test_rp_v4_stageI_author_preflight.py`.
3. Added the Windows entry point
   `audit_tools/run_rp_v4_stageI_author_preflight.ps1`.
4. Required `main`, a clean worktree and equality of `HEAD` and its upstream
   before generating the local decision packet.
5. Rechecked all 10 Stage H controlled files and the exact SHA-256 values of
   the real-input binding manifest and Stage I execution script.
6. Rechecked `D:\bioinfor\python.exe` against the Stage F2 qualified runtime,
   including executable hash and Python, NumPy, SciPy and statsmodels versions.
7. Generated an unsigned GO draft with every approval field false and both
   author identities absent.
8. Confirmed that the real Stage I runner rejects that draft before creating a
   result directory.
9. Kept the generated author packet under the Git-ignored `_software_tests`
   tree. This permits it to bind the final pushed commit without creating a
   self-referential commit-hash problem.

## Frozen author decision

Both Zhi Chen and Teng Qi must explicitly approve all six conditions before
the single real execution can start:

1. the only estimand is `delta_profile`;
2. the only method is donor-level OLS with HC3 variance and a two-sided t(64)
   interval;
3. support is exactly 68 donors, 31 controls and 37 managed-SLE donors;
4. execution is write-once, with no preview, fallback, donor removal, threshold
   change or selective rerun;
5. the result is an association difference between measurement/mixing rules,
   not causal mediation or a cell-intrinsic disease effect; and
6. it does not unlock the other historical targets, external outcomes, WP4,
   manuscript replacement or submission.

## Validation plan and finalization order

The new focused suite passed 6/6 tests. The combined RP v4 G2C, Stage A, Stage
D, Stage E2, Stage F2, Stage H and Stage I author-preflight suite passed 72/72
tests with no skip or failure. Static Python compilation also passed.

After the
tracked files are committed and pushed, the one-command Windows preflight is
run once from the clean synchronized branch. The resulting local packet records
the final Git commit, exact hashes, runtime identity and fail-closed receipt.
The final command output and test totals are reported in the user-facing round
summary; the generated packet itself is intentionally not committed.

## Scientific interpretation

No new biological result is produced in this round. Stage G remains a bounded
synthetic validation of one procedure, and Stage H remains the effect-blind
applicability gate. The permanent historical identity, transfer and mechanistic
ceilings are unchanged.

## Next stage

The next gate remains:

`RPV4_STAGE_I__EXPLICIT_TWO_AUTHOR_GO_OR_CLOSE_REAL_EXECUTION`

If both named authors explicitly approve the exact six-condition form, one
write-once `delta_profile` fit may be executed under the bound commit and
qualified runtime. If either author does not approve, the real execution closes
and Stage G is retained as methods evidence only.
