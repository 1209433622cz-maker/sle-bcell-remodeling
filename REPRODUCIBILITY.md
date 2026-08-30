# Reproducibility and repository scope

## Current correction status

The original C9 PASS is superseded. Corrected calibration processed all 56
external matrices but B_ASC reference precision was 0.885210, below 0.90.
No corrected disease outcome was estimated. The R1 identity HOLD also remains.
The corrected, author-confirmed QiTeng R2 materials are preserved in the public
Zenodo archive [doi:10.5281/zenodo.22151739](https://doi.org/10.5281/zenodo.22151739)
and matching [GitHub v1.1.0 release](https://github.com/1209433622cz-maker/sle-bcell-remodeling/releases/tag/v1.1.0).
The initial DOI `10.5281/zenodo.22086892` now resolves to a citation-preserving
tombstone after administrative replacement. This public release is a
reproducibility archive, not authorization to submit to a journal.

## Current public release

The GitHub release contains the same `Research_Archive.zip`, `Source_Code.zip`
and `SHA256SUMS.txt` bytes verified on Zenodo. The annotated `v1.1.0` tag peels
to content commit `f1859ff8498d5569a1d5027b36ed18c8b7c7536f`. Public checks are recorded in:

- `00_project_management/qiteng_r2_release_2026-08-29/zenodo_publication_verification.json`
- `00_project_management/qiteng_r2_release_2026-08-29/github_release_verification.json`

The `governance/author_freeze.json` embedded inside the immutable Research
Archive is a pre-publication authorization receipt and therefore records the
state before publication and old-record deletion. It must not be rewritten in
the published ZIP. Current administrative truth is represented by the two
post-release verification files above and the updated receipt on `main` at
`00_project_management/qiteng_r2_freeze_2026-08-29/author_freeze.json`.

## Current npj SBA submission candidate

The selected first-submission target is npj Systems Biology and Applications
(`Article`). The bounded target adaptation is separate from the immutable public
reproducibility release and performed no scientific reanalysis. Its current gate
is `PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED`; R1 and corrected C9R
remain HOLD, and no corrected external disease outcome was unlocked.

Run the complete target hardening workflow from the repository root:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_npj_sba_final_hardening.ps1
```

The final run is
`phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening`.
The generated ZIP is deliberately ignored by Git; its tracked receipt records
20 verified files, deterministic double-build identity and SHA-256
`F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`.

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
commands. GSE135779's 1.30 GB RAW archive and metadata were restored for the
completed correction. They remain local and are not part of a Git checkout.

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

The single-cell workflow was run in a Python 3.11 environment. The corrected
C9 execution records its actual packages in `04_EXECUTION_PROVENANCE.json`;
the older lock files below describe the earlier analysis environment, not an
independently requalified correction environment.
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

Earlier releases used a dedicated submission environment. The correction figures
were rebuilt with the installed Python 3.13.7 plotting runtime (NumPy 2.3.3,
pandas 2.3.3, Matplotlib 3.10.7), and DOCX generation used the bundled document
runtime. The final npj SBA documents were rendered independently with WPS and
LibreOffice. Both produced 31 manuscript pages, 18 supplementary pages and one
cover-letter page; all 50 pages from each renderer were visually reviewed, page
bounds and unresolved markers passed, and the three DOCX accessibility audits
reported zero high, medium and low findings. Historical locks:

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
11. Five main and ten supplementary figures, manuscript numbers and legends
    were regenerated from frozen or declared sensitivity tables and guarded by
    exact panel-data assertions.
12. Complete statistical outputs were packaged with sanitized design matrices,
    a unified test-family map, 101 end-to-end identity robustness files,
    file-level provenance and deterministic hashes.
13. An audit found mismatched reference/external normalization denominators and
    an ineligible calibration fallback in C9. Full-library normalization and
    fail-closed outcome access were corrected without changing candidate grids
    or gates. The complete run retained calibration HOLD. Original outcomes had
    already been seen; the correction is not a prospective preregistration.
14. A separate arithmetic implementation recounted all 72 confidence candidates
    from 14,300 OOF records, confirmed donor separation in five folds, and
    reproduced the failed calibration. This is not external model validation.

## Historical correction review bundle

The historical generated bundle is `04_submission/corrected_candidate.zip`.
The user explicitly confirmed the reviewed materials for both authors and their
consideration of the external feedback and disposition, then specifically
approved the manuscript and cover letter. The evidence receipt binds the
preserved `author_review.zip` and the two then-current Markdown hashes.
The current candidate separately integrates the Figure 1 threshold-label and
legend correction, repairs interpretation-node spacing and qualifies the
single-label omission claim. The verifier checks the exact prose delta and
reconstructs the prior approval scope using retained original files. Its
candidate-approval field records that review snapshot; unchanged statistics and
other figures retain their bytes. The later QiTeng R2 scientific baseline and
public release are governed by their own confirmation and verification receipts.
External reviewer identity remains unverified. Journal choice, target-formatted
exact files and actual submission remain separate decisions. Both older review
ZIPs remain immutable; use their own bundled verifiers for their schemas.

The user specified JCR Q1 and selected npj Systems Biology and Applications as
the first-submission target. Figure 1c now labels the 0.990 guide as the minimum
mapping-agreement criterion in both the candidate figure and manuscript legend.
All figure source tables remain byte-identical. The earlier approved snapshot is
preserved unchanged. Integrity and semantic checks do not grant final approval,
establish a journal's quartile, or authorize a DOI release or submission.

The historical release builders are retired on the current branch: they rewrite
canonical prose and delete the previous package. Do not use them for this review.
The new builder writes only a new, empty output directory and checks source hashes.
For the historical correction-review bundle only, build with:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\build_correction_review.ps1
```

The builder assembles already-rendered, hash-verified documents and figures; it
does not perform numerical inference or automatically approve release. See its
parameters for the document and audit directories. A checkout requires the
retained historical statistical archive and the local review documents.

The extracted bundle can be checked from any directory, without site packages:

```powershell
python -I -S .\04_submission\corrected_candidate\verify_review_bundle.py `
  --bundle .\04_submission\corrected_candidate
```

This checks file closure, sizes, hashes, nested statistical archives and claim
boundaries, not biological validity or a fresh recomputation. Large matrices,
reference-cell predictions and per-cell external predictions remain local.

## Historical review artifacts versus current release

- Current main-figure assertions: 42 scientific/data checks plus five typography
  checks, 47/47 in total; these are not 47 separate scientific tests.
- Supplementary-figure panel-data assertions: legacy 29/29 plus separate S8
  (36 rows) and S9 (128 rows; 8/8 checks) contracts.
- Reference DOI identities independently resolved: 28/28.
- Numbered manuscript references: 32.
- The historical complete statistical results archive preserves the frozen source archive
  and deterministically adds 101 reviewer-facing end-to-end identity and
  boundary-propagation files; its internal 163-row manifest validates exactly.
- The current archive preserves those 163 files byte-for-byte and adds 20
  calibration records plus one scope note, for 184 manifest payloads.
- Main and supplementary DOCX files use numbered journal-style citations,
  embedded figure markers, explicit table titles, full-width tables, US Letter
  pages, 1-inch margins, Times New Roman text and double-spaced manuscript body
  text.
- The historical package contains separate `portal_upload_required` and
  `portal_upload_optional` directories plus a filename and hash map.
- The earlier WPS release had 32 manuscript pages, 17 supplementary pages and
  one cover-letter page. Current page counts and accessibility results are
  computed afresh and included in the correction-review evidence; these old
  counts are not acceptance criteria for the revised documents.

## Author and portal boundary

The recorded author identities, declarations and licences are retained. QiTeng R2
is the confirmed scientific baseline and its journal-neutral reproducibility
archive is public. The npj SBA target-specific title, abstract, layout, figures,
supplement and cover letter have passed technical hardening, but their exact
DOCX/PDF/package hashes still require a new final approval from both authors.
The official current JCR Q1 profile and institutional APC/OA receipt also remain
pending. Technical bundle or release verification does not authorize portal
upload, APC commitment or journal submission.
