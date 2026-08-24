# Reproducibility and repository scope

## Repository boundary

This repository contains analysis code, study-design documents, environment
locks, machine-readable decisions, compact source data and publication
figures. Raw or processed H5AD objects, original public archives, per-cell
exports, literature PDFs and generated submission packages are intentionally
excluded from Git.

A checkout alone is therefore not sufficient to recompute the study. Public
data must be retrieved from the cited accessions and reconciled against the
tracked provenance and checksum records before analysis. No patient-level
outcome was used during disease-blind identity learning.

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

## Two environment layers

The scientific analysis and the release build are locked separately so that a
future reader can distinguish numerical inference from document rendering.

### Scientific analysis environment

The single-cell and figure workflow was run in `sle-bcell-v7` with Python 3.11.
The correlation-aware regulator sensitivity was run with R 4.6.0, edgeR 4.10.1
and limma 3.68.4. The tracked analysis locks are:

- `audit_tools/environment_phase17_v7_explicit_win64_2026-08-10.txt`
- `audit_tools/environment_phase17_v7_pip_freeze_2026-08-10.txt`
- `audit_tools/environment_phase17_v7_resolved_2026-08-10.yml`

Exact Windows reconstruction:

```powershell
conda create -n sle-bcell-v7-repro `
  --file .\audit_tools\environment_phase17_v7_explicit_win64_2026-08-10.txt
conda activate sle-bcell-v7-repro
python -m pip install `
  -r .\audit_tools\environment_phase17_v7_pip_freeze_2026-08-10.txt
python .\02_analysis\scripts\01_check_scanpy_env.py
```

### Release and document environment

The journal-facing build uses the dedicated `sle-bcell-c8br-release` environment,
LibreOffice headless rendering for portable checks, and WPS Office as the
authoritative DOCX rendering backend on the release workstation. Its tracked
locks are:

- `audit_tools/environment_gateC8BR_release_2026-08-25.yml`
- `audit_tools/environment_gateC8BR_release_explicit_win64_2026-08-25.txt`

Recreate or refresh the release environment with:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\00_create_gateC8BR_release_env.ps1
```

## Frozen inferential sequence

1. Hard QC and library reconciliation retained 150,402/150,402 cells across
   88/88 libraries. The 1,972 residual-risk calls remained sensitivity-only.
2. Disease-blind recurrent-HVG representations were reviewed before outcomes
   were unlocked.
3. Identity stability was tested in the frozen 50-dimensional
   `X_pca_harmony` space. Twenty 80% resamples were drawn without replacement
   within each `library_uuid`. HVG selection, PCA and Harmony were not
   recomputed. For each resample, a 15-nearest-neighbour graph and Leiden
   partitions at resolutions 0.4, 0.6 and 0.8 were recomputed. The base seed
   was 20260806; sampling used `20260806 + 1000 + r` and graph/clustering used
   `20260806 + r` for zero-based replicate `r`.
4. Resampled clusters were mapped to the corresponding full-data reference
   cluster by maximum cell overlap. Stability was evaluated with ARI, AMI,
   majority-mapping agreement, state Jaccard and state recall. Five-, four-
   and three-state interpretations did not satisfy the predeclared joint
   stability thresholds. A two-compartment model reconstructed from the frozen
   transition map passed stricter thresholds: median/minimum mapped ARI
   0.995553/0.990207, median/minimum mapping agreement 0.999925/0.999834 and
   minimum state median Jaccard 0.991371. Required ASC markers `DERL3`,
   `JCHAIN`, `MZB1`, `TNFRSF17` and `XBP1` each had sample support 1.0.
5. The permissible frozen identity scope was therefore reduced to broad
   `B_CONV` and `B_ASC` compartments. Fine-grained naive/memory subtype labels
   were not used as hard inferential identities.
6. Protected metadata were joined only after identity freeze. Composition was
   analysed at sample level and transcription with raw-count pseudobulk at the
   biological-sample or donor level.
7. The discovery IFN/ISG program was frozen before donor-nonoverlap and
   GSE135779 tests.
8. STAT1/STAT2 regulators, signed CollecTRI targets, contrasts, backgrounds and
   designs were frozen before CAMERA and FRY sensitivity analyses.
9. Five main and seven supplementary figures, manuscript numbers and legends
   were regenerated from frozen tables and guarded by exact panel-data
   assertions.
10. Complete statistical outputs were packaged with sanitized design matrices,
    a unified test-family map, file-level provenance and deterministic hashes.

## Journal-facing prefreeze rebuild

The active local rebuild is:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8BRP_journal_facing_prefreeze.ps1
```

Use `-PortableCore` for a fully portable build that stops after LibreOffice
checks. The default full mode also uses WPS Office and performs page-by-page
raster and accessibility checks before the deterministic package archive is
created.

## Frozen release assertions

- Main-figure panel-data assertions: 46/46.
- Supplementary-figure panel-data assertions: 29/29.
- Reference DOI identities independently resolved: 28/28.
- Numbered manuscript references: 32.
- The complete statistical results archive is byte-identical to the Gate C8S
  frozen source archive.
- Main and supplementary DOCX files use numbered journal-style citations,
  embedded figure markers, explicit table titles, full-width tables, US Letter
  pages, 1-inch margins, Times New Roman text and double-spaced manuscript body
  text.
- The release package contains a clean `portal_upload_preview` directory and a
  filename map, but it is deliberately marked `DO NOT UPLOAD` until the author
  completion matrix is signed.

## Author-controlled release boundary

The pipeline cannot truthfully complete ethics, competing-interests, funding,
CRediT contribution, acknowledgement, all-author originality/approval,
correspondence-address approval, publication-licence or APC decisions. It also
does not mint a repository DOI. These remain explicit author actions. Portal
submission is unauthorized until every mandatory item is resolved and the
final package is re-audited.
