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

The cleaned local workspace retains the formal 150,402-cell raw-count H5AD and
the frozen primary representation used by the current R1 workflows, but not the
larger public source cache. `Data/README.md` records the exact restoration
commands. GSE135779 metadata are present locally; its 1.30 GB RAW archive must
be restored before the planned label-agnostic external mapping sensitivity.

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

The single-cell and figure workflow was run in a pinned Python 3.11 environment.
The correlation-aware regulator sensitivity was run with R 4.6.0, edgeR 4.10.1
and limma 3.68.4. The tracked analysis locks are:

- `audit_tools/environment_analysis_win64.txt`
- `audit_tools/environment_analysis_python.txt`
- `audit_tools/environment_analysis.yml`

Exact Windows reconstruction:

```powershell
conda create -n sle-bcell-analysis `
  --file .\audit_tools\environment_analysis_win64.txt
conda activate sle-bcell-analysis
python -m pip install `
  -r .\audit_tools\environment_analysis_python.txt
python .\02_analysis\scripts\01_check_scanpy_env.py
```

### Release and document environment

The journal-facing build uses the dedicated `sle-bcell-submission` environment.
WPS Office is the authoritative DOCX rendering backend on the release workstation;
LibreOffice provides an independent portability render during final review. Its
tracked locks are:

- `audit_tools/environment_submission.yml`
- `audit_tools/environment_submission_win64.txt`

Recreate or refresh the document environment with the stable entry point:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\create_submission_environment.ps1
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
5. The permissible frozen identity scope was therefore reduced to a broad
   `B_CONV`/`B_ASC` analysis scaffold. Fine-grained naive/memory subtype labels
   were not used as hard inferential identities.
6. A separate end-to-end sensitivity recomputed gene filtering, recurrent HVGs,
   PCA, Harmony, neighbour graphs and Leiden clustering in 20 within-library
   80% resamples. All runs converged and four global criteria passed, but B_ASC
   median Jaccard was 0.930323, below the unchanged 0.95 state-overlap criterion.
   The formal decision is `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`.
7. Observed broad-state exchanges were propagated without changing sample or
   gene eligibility. Primary B_ASC odds ratios ranged from 0.896 to 0.967 and
   all intervals included one. Primary and donor-nonoverlap B_CONV IFN/ISG
   effects remained positive with every interval above zero. This is same-data
   sensitivity, not independent replication.
8. Protected metadata were joined only after identity freeze. Composition was
   analysed at sample level and transcription with raw-count pseudobulk at the
   biological-sample or donor level.
9. The discovery IFN/ISG program was frozen before donor-nonoverlap and
   GSE135779 tests.
10. STAT1/STAT2 regulators, signed CollecTRI targets, contrasts, backgrounds and
   designs were frozen before CAMERA and FRY sensitivity analyses.
11. Five main and nine supplementary figures, manuscript numbers and legends
    were regenerated from frozen or declared sensitivity tables and guarded by
    exact panel-data assertions.
12. Complete statistical outputs were packaged with sanitized design matrices,
    a unified test-family map, 101 end-to-end identity robustness files,
    file-level provenance and deterministic hashes.

## Submission package rebuild

The current author-facing rebuild is:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\build_submission_package.ps1 `
  -Doi "10.5281/zenodo.22086892"
```

Use `-Mode PortableCore` for a portable build that stops before the WPS review.
The default full mode uses WPS Office and performs page-by-page raster and
accessibility checks before the deterministic package archive is created.

## Frozen release assertions

- Main-figure panel-data assertions: 46/46.
- Supplementary-figure panel-data assertions: legacy 29/29 plus separate S8
  (36 rows) and S9 (128 rows; 8/8 checks) contracts.
- Reference DOI identities independently resolved: 28/28.
- Numbered manuscript references: 32.
- The complete statistical results archive preserves the frozen source archive
  and deterministically adds 101 reviewer-facing end-to-end identity and
  boundary-propagation files; its internal 163-row manifest validates exactly.
- Main and supplementary DOCX files use numbered journal-style citations,
  embedded figure markers, explicit table titles, full-width tables, US Letter
  pages, 1-inch margins, Times New Roman text and double-spaced manuscript body
  text.
- The package contains separate `portal_upload_required` and
  `portal_upload_optional` directories plus a filename and hash map.
- The final WPS render contains 32 manuscript pages, 17 supplementary pages and
  one cover-letter page; all three DOCX accessibility audits report zero high,
  medium or low findings.

## Author and portal boundary

The authors have completed ethics, competing-interests, funding, CRediT,
acknowledgement, originality, approval, correspondence and licence decisions.
The DOI is public and resolves to the archived release. The pipeline verifies
the local submission package but does not perform the final journal submission;
the corresponding author must still review the portal metadata and generated
submission PDF before the irreversible submit action.
