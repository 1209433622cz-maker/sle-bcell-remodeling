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

## Completed cell-policy gate

Gate C2B1 completed 88/88 complete-library residual-risk runs and reconciled
150,402/150,402 hard-QC cells. Its frozen decision is:

- primary: all 150,402 hard-QC cells;
- sensitivity: exclude the 1,972 automatic residual-risk calls;
- automatic second-round deletion: not authorized before state-graph localization.

The binding report is
`phase17_v7/gateC2B1/20260810_171000_full_library_doublets/16_GATE_C2B1_DECISION.md`.

## Active gate

The current analysis gate is full disease-blind representation learning:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B2_full_representation.ps1 `
  -ResumeRunDir ".\phase17_v7\gateC2B2\20260812_full_representation"
```

The run freezes library-aware recurrent HVGs before fitting three independently
checkpointed branches: all-hard-QC primary, residual-risk-negative and strong-
ISG-excluded. The primary branch retains both an
unintegrated graph and a Harmony graph adjusted by technical library. Formal
review must include technical mixing, cross-cohort bridge samples, marker
conservation, branch concordance and residual-risk localization.

An immunoglobulin-dominance representation sensitivity is explicitly non-evaluable:
the source raw feature space lacks canonical immunoglobulin constant genes and
contains only three bona fide IG-prefix V/OR loci. Proxy genes are not substituted.

The full-PBMC B-lineage completeness audit can be reconstructed separately:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_blineage_extraction_audit.ps1
```

Its binding decision retains source B-lineage labels as the primary input and
uses refined outside-label candidates for mapping sensitivity only.

## Outcome lock

Disease, disease state and `ct_cov` are excluded from working objects used for
representation learning and state definition. Protected outcomes are joined
only after cells, representation and neutral states pass their freeze gates.

## Release policy

The GitHub repository is a private working repository during analysis. A public
release, source-data package and archival DOI should be created only after
manuscript freeze, data-license review and removal of non-shareable metadata.
