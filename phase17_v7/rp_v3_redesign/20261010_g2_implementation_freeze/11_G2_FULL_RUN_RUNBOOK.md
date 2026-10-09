# RP v3 full-G2 local runbook

Run from the repository root. The workflow is synthetic-only and does not read real WP2 response values.

## 1. R0 core execution

Use a persistent output directory. The command is resumable: completed chunks are hash-verified and reused, while partial or altered chunks fail closed.

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"

powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_rp_v3_g2_full.ps1 `
  -Python "D:\bioinfor\python.exe" `
  -OutputRoot "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\rp_v3_redesign\g2_full_runs\20261010_full" `
  -Regimes R0 `
  -ChunkSize 25
```

R0 comprises five scenarios and 10,000 outer attempts. Each supported outer attempt runs the actual 2,000 paired bootstrap resamples jointly for all ten targets. Runtime depends on storage and CPU; the technical pilot suggests minutes to tens of minutes, not seconds. Do not interrupt by deleting a partial chunk. Preserve it for diagnosis and use a new output directory if the fail-closed check requests one.

## 2. Complete the remaining registered grid

After R0 finishes, reuse the same output root. Existing R0 chunks will be verified and reused.

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_rp_v3_g2_full.ps1 `
  -Python "D:\bioinfor\python.exe" `
  -OutputRoot "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\rp_v3_redesign\g2_full_runs\20261010_full" `
  -Regimes R0,R1,R2,R3,R4 `
  -ChunkSize 25 `
  -Adjudicate
```

The final command requires all 50,000 outer attempt IDs. It writes compact attempt-target summaries rather than billions of inner-bootstrap coefficients. Random streams are counter-addressed, so chunk size and resume boundaries do not change simulated attempts.

## 3. Read the decision

Only this file can grant a synthetic G2 decision:

```text
phase17_v7/rp_v3_redesign/g2_full_runs/20261010_full/adjudication/03_G2_FINAL_DECISION.json
```

Do not infer PASS from a zero process exit, a completed R0 run, a truth receipt or populated hashes. WP2 real effects remain locked unless the complete adjudicator returns `PASS_G2_APPLICABLE_DOMAIN` and the project performs a separate post-G2 review.

## Non-negotiable rules

- Do not change seeds, target definitions, scenario strengths, support threshold, 2,000 outer attempts or 2,000 inner bootstraps.
- Do not refill failed or unsupported attempts.
- Do not delete R1 or R3 because support is low.
- Do not relabel C0_R2/C0_R4 as observed-score true nulls.
- Do not run real WP2 coefficients from these synthetic-only modules.
