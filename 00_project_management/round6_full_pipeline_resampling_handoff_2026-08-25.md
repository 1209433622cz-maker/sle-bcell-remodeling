# Round 6 full-pipeline disease-blind identity resampling handoff

Date: 2026-08-25
Status: ready for the 150,402-cell scientific run
Interpretation lock: no manuscript identity claim may be updated until the full output is reviewed

## Purpose

This is the pending R1 robustness analysis. Each of 20 within-library 80% resamples starts again from hard-QC raw counts and recomputes gene filtering, normalization, highly variable genes, scaling, PCA, Harmony, neighbour graphs and Leiden clustering. It tests whether the broad `B_CONV`/`B_ASC` identity boundary survives end-to-end reconstruction rather than only graph rebuilding from a frozen embedding.

## Frozen inputs and executable

- Raw counts: `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad`
- Raw shape: 150,402 cells x 30,172 genes
- Raw SHA-256: `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5`
- Frozen reference: `phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad`
- Reference SHA-256: `594A040FC483973B38B744D5D0E526633D7F1C91F2544D34C28D35F2084E3AFB`
- Analysis environment: `C:\ProgramData\miniforge3\envs\sle-bcell\python.exe`
- Analysis script: `audit_tools/phase17_round6_03_full_pipeline_identity_resampling.py`
- Analysis-script SHA-256: `7A28EB02C49F0B2C951180D83438D82FF1E4D83E7D7CC345BFA7987040A9A960`
- Wrapper: `audit_tools/run_6013RP_round6_full_pipeline_identity_resampling.ps1`
- Wrapper SHA-256: `5B1B386229DB89AEAB535153FE436AD03A431748E36B3F644977BD1AE273CE13`

The run contract records the current analysis-script SHA-256 and software versions. Editing the script or changing a parameter invalidates prior replicate checkpoints by design.

## Exact full-run command

Open PowerShell and run:

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"

powershell -ExecutionPolicy Bypass `
  -File ".\audit_tools\run_6013RP_round6_full_pipeline_identity_resampling.ps1" `
  -OutputDir ".\phase17_v7\round6_q1_robustness\20260825_full_pipeline_identity_resampling" `
  -Replicates 20 `
  -ResampleFraction 0.8 `
  -MaxCells 0 `
  -HarmonyMaxIter 50
```

`MaxCells 0` is mandatory for the scientific run. A positive value produces test mode and cannot update the manuscript.

## Resource and interruption guidance

- Close memory-intensive applications before starting. Scaling 3,000 HVGs temporarily creates a dense matrix, so 32 GB RAM or more is preferred.
- Keep the computer awake and connected to power. The task is CPU- and memory-intensive but writes compact checkpoint outputs rather than another large H5AD.
- An interruption is recoverable. Rerun the exact same command; completed replicates will print `[RESUME]` and will not be recomputed.
- Do not delete a completed `replicate_###` directory and do not change parameters while the run is active.

## Monitoring

In another PowerShell window:

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"

Get-ChildItem `
  ".\phase17_v7\round6_q1_robustness\20260825_full_pipeline_identity_resampling" `
  -Recurse -Filter 00_REPLICATE_STATUS.json |
  Measure-Object
```

The count should progress to 20. A replicate is complete only when its `00_REPLICATE_STATUS.json` says `"status": "COMPLETE"`.

## Expected final outputs

- `00_RUN_CONTRACT.json`
- `01_ALL_REPLICATE_METRICS.csv`
- `02_ALL_STATE_METRICS.csv`
- `03_BRANCH_RESOLUTION_SUMMARY.csv`
- `04_STATE_SUMMARY.csv`
- `05_FULL_PIPELINE_RESAMPLING_STATUS.json`
- `replicate_001` through `replicate_020`, each with status, metrics, selected-HVG and compressed r=0.4 assignment records

## Decision rule

The scientific run can return `PASS_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY` only when all 20 replicates are complete, every Harmony run converges and the unchanged C2B4 thresholds all pass:

- median mapped ARI at least 0.95;
- minimum mapped ARI at least 0.90;
- median mapping agreement at least 0.995;
- minimum mapping agreement at least 0.990;
- minimum state median Jaccard at least 0.95.

A `HOLD` is a valid scientific outcome. It would retain the frozen-embedding result while preventing a stronger end-to-end stability claim; it must not be repaired by threshold changes or selective replicate removal.

## Software qualification already completed

Two 5,000-cell test-mode replicates completed with 3,996 sampled cells each. Both Harmony runs converged under the final 50-iteration cap, all outputs were generated, and rerunning the same command resumed both checkpoints. Their identity metrics are explicitly non-scientific and are excluded from manuscript interpretation.

## Return point

After the command finishes, report only that the run completed or paste the final `05_FULL_PIPELINE_RESAMPLING_STATUS.json`. The next audit will verify every checkpoint, recompute summaries from replicate-level files and decide whether R1 becomes Supplementary Figure S9 or a qualified negative boundary.
