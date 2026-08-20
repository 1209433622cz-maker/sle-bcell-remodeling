# Reproducibility and repository scope

## Repository boundary

This repository contains analysis code, study-design documents, environment
locks, machine-readable gate decisions, compact source data and publication
figures. Raw or processed H5AD objects, original public archives, per-cell
exports, literature PDFs and generated submission packages are intentionally
excluded from Git.

A checkout alone is therefore not sufficient to recompute the study. Public
data must be retrieved from the cited accessions and reconciled against the
tracked provenance and checksum records before analysis. No patient-level
outcome is used during disease-blind identity learning.

## Frozen data resources

- `GSE174188`: discovery PBMC/B-lineage source and donor-nonoverlap internal
  validation.
- `GSE135779`: independent SLE validation, with childhood donors as the primary
  confirmatory stratum and adult donors treated as directional context.
- `GSE23307`: two-donor paired primary B-cell IFN-beta perturbation used only as
  descriptive orthogonal response evidence.

The final manuscript does not treat the GSE174188 internal donor split as an
independent cohort and does not assign an inferential P value to the two-donor
GSE23307 experiment.

## Environments

The single-cell and figure workflow was tested in `sle-bcell-v7` with Python
3.11. The correlation-aware sensitivity was tested with R 4.6.0, edgeR 4.10.1
and limma 3.68.4. Document generation and audit use the bundled Codex Python
runtime; WPS Office is the authoritative DOCX rendering backend on this
workstation.

Exact Windows conda reconstruction:

```powershell
conda create -n sle-bcell-v7-repro `
  --file .\audit_tools\environment_phase17_v7_explicit_win64_2026-08-10.txt
conda activate sle-bcell-v7-repro
python -m pip install `
  -r .\audit_tools\environment_phase17_v7_pip_freeze_2026-08-10.txt
python .\02_analysis\scripts\01_check_scanpy_env.py
```

The resolved environment is
`audit_tools/environment_phase17_v7_resolved_2026-08-10.yml`. The explicit
Windows package specification is the exact local reconstruction path.

## Frozen inferential sequence

1. Hard-QC and library reconciliation retained 150,402/150,402 cells across
   88/88 libraries. The 1,972 residual-risk calls remained sensitivity-only.
2. Disease-blind recurrent-HVG representations were reviewed before outcomes
   were unlocked.
3. Resampling did not support the original five fine states as hard inferential
   identities. The permissible frozen scope was reduced to broad `B_CONV` and
   `B_ASC` compartments.
4. Protected metadata were joined only after identity freeze. Composition was
   analysed at sample level and transcription with raw-count pseudobulk at the
   biological-sample or donor level.
5. The discovery IFN/ISG program was frozen before donor-nonoverlap and
   GSE135779 tests.
6. STAT1/STAT2 regulators, signed CollecTRI targets, contrasts, backgrounds and
   designs were frozen before CAMERA and FRY sensitivity analyses.
7. Five main and seven supplementary figures, manuscript numbers and legends
   were regenerated from frozen tables and guarded by exact panel-data
   assertions.
8. Complete statistical outputs were packaged with sanitized design matrices,
   a unified test-family map, file-level provenance and deterministic hashes.

## Gate C8S rebuild

The complete local rebuild is:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8S_submission_package.ps1
```

The runner executes these tracked components in order:

- `audit_tools/phase17_c7_01_build_main_figures.py`
- `audit_tools/phase17_c8s_01_build_supplementary_figures.py`
- `audit_tools/phase17_c8s_02_build_full_statistical_archive.py`
- `audit_tools/phase17_c8s_03_build_submission_sources.py`
- `audit_tools/phase17_c8s_04_build_documents.py`
- `audit_tools/render_docx_with_wps.ps1`
- bundled `a11y_audit.py`
- `audit_tools/phase17_c8s_05_final_submission_audit.py`

The correlation-aware regulator sensitivity and DOI metadata verification remain
frozen Gate C8R inputs; C8S does not recompute or relabel those estimates.

For a quick package-only rebuild from already verified scientific outputs:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8S_submission_package.ps1 `
  -SkipMainFigureBuild `
  -SkipSupplementaryFigureBuild `
  -SkipStatisticalArchiveBuild
```

## Automated locks

- Main-figure assertions: 46/46 must pass, including the Figure 2a group counts
  and the corrected Figure 5 panel-d/panel-e machine-readable mapping.
- Supplementary-figure assertions: 29/29 must pass across S1-S7.
- Figures: exactly five main and seven supplementary PDF/600-dpi PNG pairs;
  visible figure text must be at least 5 pt.
- Correlation-aware core family: six tests with exact target counts
  `98/14/129/19/161/20`; CAMERA direction 6/6 and BH significance 5/6; FRY
  direction and BH significance 6/6.
- References: 26 DOI records must pass metadata verification; the manuscript
  contains 30 references in total.
- Main DOCX: double spacing, continuous line numbers, page numbering and
  odd/even running headers.
- Full statistical archive: 12 complete gene-level branches, 12 sanitized design
  matrices, 63 payload files, no direct identifiers and a deterministic SHA-256.
- Supplement: eight tables with explicit OOXML table width, grid, cell-width and
  indent geometry, plus seven embedded figures.
- WPS page review: 27 manuscript pages, 12 supplementary pages and 1 cover page.
- Accessibility: zero high-, medium- or low-severity findings in all three DOCX
  reports.
- Packaging: every package file is listed in `MANIFEST_SHA256.csv`; the final
  ZIP is rebuilt twice from the same frozen package tree with fixed entry order,
  timestamps and permissions, and the two SHA-256 hashes must match.

## Release policy

The GitHub repository is currently public. It is not yet the final citable
release: complete the data-license review, confirm that no non-shareable metadata
are tracked, add an open-source licence and create an immutable Zenodo or
equivalent DOI. The DOI and final release commit must then replace the visible
manuscript and cover-letter placeholders before portal submission.
