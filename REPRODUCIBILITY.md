# Reproducibility and repository scope

## Repository boundary

This repository contains analysis code, active scientific-design documents,
environment locks and lightweight audit outputs. Raw/processed H5AD objects,
per-cell exports, public-dataset archives, literature PDFs, course documents and
legacy submission builds are intentionally excluded from Git.

No repository checkout alone is sufficient to reproduce numerical results. The
required public data must be retrieved from their original accessions and
validated against the local provenance/checksum records before analysis.

## Public data resources

- GSE174188: discovery PBMC/B-lineage source.
- GSE135779: main external SLE validation, analysed as childhood and adult strata.
- GSE163121: small directional validation only.
- GSE196830 / OneK1K: healthy reference context only.

## Environment reconstruction

The tested Windows environment is `sle-bcell-v7` with Python 3.11 and OpenBLAS.

Exact Windows conda packages:

```powershell
conda create -n sle-bcell-v7-repro --file .\audit_tools\environment_phase17_v7_explicit_win64_2026-08-10.txt
conda activate sle-bcell-v7-repro
python -m pip install -r .\audit_tools\environment_phase17_v7_pip_freeze_2026-08-10.txt
python .\02_analysis\scripts\01_check_scanpy_env.py
```

The resolved environment export is available at
`audit_tools/environment_phase17_v7_resolved_2026-08-10.yml`. The explicit
Windows spec is preferred for exact local reconstruction.

## Active gate

The current analysis gate is complete-library residual doublet-risk review:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1 `
  -ResumeRunDir ".\phase17_v7\gateC2B1\20260810_171000_full_library_doublets"
```

This run does not automatically exclude predicted cells. It preserves paired
per-library score/threshold checkpoints and produces a multimetric residual-risk
review. The primary branch remains all hard-QC cells; a high-confidence-singlet
branch is sensitivity only.

The full-PBMC B-lineage completeness audit is prepared separately:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_blineage_extraction_audit.ps1
```

## Outcome lock

Disease, disease state and `ct_cov` are excluded from working objects used for
representation learning and state definition. Protected outcomes are joined
only after cells, representation and neutral states pass their freeze gates.

## Release policy

The GitHub repository is a private working repository during analysis. A public
release, source-data package and archival DOI should be created only after
manuscript freeze, data-license review and removal of non-shareable metadata.
