# RP v3 G2B PowerShell regime-argument hotfix

Date: 2026-10-10

Scope: command-line wrapper and provenance only

Scientific state: unchanged; G2B remains not run and real WP2 remains locked

## Trigger

The documented nested `powershell -File` command supplied
`-Regimes R0,R1,R2,R3,R4`. Windows PowerShell passed that token to the script
as one string. Parameter-level `ValidateSet` therefore compared the complete
comma-delimited token with each allowed single regime and stopped during
binding.

The failure occurred before tests, output-root initialization, simulation or
adjudication. No G2B attempt was executed and no scientific output was created
or modified.

## Repair

`audit_tools/run_rp_v3_g2b_full.ps1` now:

1. accepts either a comma-separated token from `powershell.exe -File` or a
   true string array from direct PowerShell invocation;
2. splits, trims, uppercases and de-duplicates regime identifiers;
3. applies an explicit `R0`-`R4` allow-list before any test or simulation;
4. rejects an empty set and retains the requirement that final adjudication
   includes all five regimes.

The full-run runbook now uses the exact nested invocation tested on Windows.
No Python analysis code, estimator, bootstrap kernel, seed, scenario, truth,
target, threshold or adjudication rule was changed.

## Required regression

- invoke the wrapper through `powershell -File` with
  `-Regimes R0,R1,R2,R3,R4 -ValidateOnly`;
- confirm all G2/G2B tests pass;
- confirm no outer attempt is written;
- test explicit rejection of an invalid regime;
- refresh the wrapper qualification hash and freeze integrity manifest;
- retain `PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED`.

## Regression result

- The exact nested `powershell -File` form with
  `-Regimes R0,R1,R2,R3,R4 -ValidateOnly` completed successfully.
- Parent G2 plus G2B implementation tests passed 30/30.
- Direct invocation with a true five-element PowerShell array also passed
  30/30, confirming both supported calling forms normalize identically.
- The wrapper reported that no G2B outer attempt was executed and real WP2
  remained locked.
- Neither the requested full-run directory nor the invalid-probe directory was
  created.
- `R0,R9` failed before testing or simulation with an explicit allow-list
  error.
- The repaired CRLF-normalized wrapper SHA-256 is
  `044cea3be601b10de48c89cd682fddfe205d858062038f6f4b23f86a90da3a33`.

## Next stage

After regression passes, rerun the documented full command. The next
scientific gate remains
`G2B_FULL_SYNTHETIC_EXECUTION_AND_INDEPENDENT_ADJUDICATION`; PASS or HOLD still
requires a separate post-G2B review and cannot automatically unlock real WP2.
