# Phase 17 Gate C2B1: full-library doublet diagnostics

This gate replaces the non-freezable doublet calls from the 20,000-cell smoke
sample. It extracts every cell passing the frozen hard-QC rules from the
authoritative `raw/X`, keeps protected outcomes outside the working AnnData,
and runs Scrublet independently on each complete technical library. Because the
Perez source workflow already included donor demultiplexing and doublet
handling, this is a residual doublet-risk diagnostic rather than an automatic
second deletion pass.

## Environment

Use the tested Windows environment:

`C:\ProgramData\miniforge3\envs\sle-bcell-v7\python.exe`

The environment uses OpenBLAS because the earlier `sle-bcell` environment
crashed during native PCA/matrix operations on this Windows installation.

## Run

From the project root in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1
```

If interrupted, resume the same run directory so completed library cell-score
and threshold checkpoints are reused:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1 `
  -ResumeRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B1\YYYYMMDD_HHMMSS_full_library_doublets"
```

## Binding stop rule

Completion of this runner does not authorize doublet exclusion. Review
`05_full_library_doublet_summary.csv`, `06_full_cell_doublet_scores.csv.gz`,
the diagnostic figures, `08_GATE_C2B1_DOUBLET_REVIEW.md` and
`15_GATE_C2B1_RESIDUAL_DOUBLET_ASSESSMENT.md` first. The multimetric review
tests associations with RNA content and B/non-B marker fractions without
accessing protected outcomes. The full raw object is not modified by automatic
Scrublet calls. Carry `all-hard-QC` as the primary branch and a reviewed
`high-confidence-singlet` branch as sensitivity.
