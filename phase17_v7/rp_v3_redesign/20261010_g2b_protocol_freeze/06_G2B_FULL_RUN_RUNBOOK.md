# RP v3 full-G2B runbook

Run from the repository root in Windows PowerShell. G2B is synthetic-only and
uses a new output directory. Do not point it at the original `g2_full_runs`
directory.

## 1. Fast validation only

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"

& .\audit_tools\run_rp_v3_g2b_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2b_full_runs\20261010_stage121_full `
  -ValidateOnly
```

Expected: 30/30 parent-G2 plus G2B implementation tests pass and no outer
attempt is written.

## 2. Complete execution and adjudication

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_rp_v3_g2b_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2b_full_runs\20261010_stage121_full `
  -Regimes R0,R1,R2,R3,R4 `
  -ChunkSize 25 `
  -Adjudicate
```

The wrapper normalizes both the comma-separated form above and a true
PowerShell array supplied during direct invocation. Invalid or empty regime
sets fail before any synthetic attempt is started.

This executes 25 scenarios and 50,000 outer attempts. Each supported object
receives exactly 2,000 paired inner draws. Runtime can be long; keep the terminal
open and prevent sleep.

## 3. Resume after interruption

Rerun the exact same command. Complete chunks are hash-verified and reused.
Partial, orphaned, corrupted, old-stage or old-method chunks fail closed and
must be preserved for diagnosis; the script does not delete and silently rerun
them.

## 4. Required completion evidence

- `run_binding.json` has schema `RP_V3_G2B_FULL_1.0`, stage 121 and binding
  `ce40a673df8c051e4eb7036292fe5827eb6ce8b552ee56964affc61d1fa25d0c`;
- every scenario contains attempts 1-2000 exactly once;
- adjudication writes 250 target-scenario rows and 25 accounting rows;
- the final JSON reports either `PASS_G2B_APPLICABLE_DOMAIN` or
  `HOLD_G2B_APPLICABLE_DOMAIN`;
- `WP2_REAL_EFFECT_UNLOCK` remains false in either case until a separate review.

## 5. Stop rules

Do not change the method, seed, truth, targets, scenarios or thresholds after
partial or complete results are visible. Do not pool stage-41 development data
or stage-21 G2 data with G2B. A HOLD ends interval-method development and moves
the project to RP v3 scope contraction.
