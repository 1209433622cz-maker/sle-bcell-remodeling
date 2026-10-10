# RP v4 Stage D canonical advisor review

## Decision

`PASS_RPV4_STAGE_D_CANONICAL_TECHNICAL_IMPLEMENTATION__HOLD_STAGE_E_AUTHOR_SIGNOFF_AND_FINAL_G2C`

The external candidate is accepted as evidence input after independent ZIP,
manifest, Stage C byte-binding and numerical replay checks. It is not accepted
as a self-authorizing gate. The project-side implementation uses the canonical
Stage C HC3-t kernel rather than promoting the candidate's duplicate kernel.

## Verified technical result

- 22/22 project-side Stage C + Stage D tests passed under `D:\bioinfor\python.exe`.
- The 24-attempt shifted-DGP pilot reproduced 18 supported attempts, six
  prespecified support stops and zero numerical failures.
- Interrupted 4-attempt execution followed by resume to eight attempts matched
  a fresh eight-attempt run in 28/28
  files byte for byte.
- Three selected development-stage oracle cases passed the technical precision
  check. This is not the complete stage-142 truth table and is not a G2C result.
- The SRA plan contains 261 runs and 171 experiments (297.574 GB reported SRA
  payload) and did not download, align or inspect disease/activity outcomes.

## Runtime boundary

`D:\bioinfor\python.exe` is the only Windows runtime qualified in this gate.
The `sle-bcell` Miniforge environment terminates on the X2 Cholesky path with
native code `0xC06D007F`; it must not be used for final G2C unless separately
repaired and requalified.

## Interpretation boundary

Stage D establishes implementation feasibility, deterministic checkpointing and
technical oracle precision for three selected cases. It does not establish bias,
coverage, type-I control or domain-wide G2C performance. Stages 141 and 142,
real WP2 responses, external disease/activity outcomes, manuscript replacement,
submission, Release and Zenodo remain locked.

## Next stage

Proceed to `RPV4_STAGE_E__AUTHOR_SIGNOFF_AND_FINAL_G2C_PREFLIGHT`. The next gate
must bind an exact author approval receipt, implement and test the full stage-142
truth runner plus stage-141 runner/adjudicator, verify fail-closed checkpointing,
and perform a dry preflight without consuming either final random namespace.
Only a later explicit `GO_FOR_FULL_SYNTHETIC_G2C` may start the final run.
