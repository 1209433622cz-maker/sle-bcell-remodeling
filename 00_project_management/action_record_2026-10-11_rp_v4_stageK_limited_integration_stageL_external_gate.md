# RP v4 Stage K limited integration and Stage L external-cohort gate

**Date:** 2026-10-11

**Starting Git baseline:** `23a2cabd816e783df63d20ba2b67fcc4163e0adf`

**Final scientific gate:** `PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION`

## Scope

This round had two bounded objectives:

1. independently verify and canonically integrate the author-approved Stage K
   uncertainty-method sensitivity without reopening Stage I or changing any
   figure; and
2. determine whether GSE262846 supports a genuinely different external
   clinical question before any large raw-data download or outcome analysis.

Submission, GitHub Release, Zenodo, WP4, raw SRA download and external outcome
fitting remained outside scope.

## Inputs and independent intake

The external review input was
`C:/Users/Administrator/Downloads/SLE_RPv4_StageK_LimitedManuscript_ExternalNovelty_20261011.zip`.
It is 5,706,515 bytes with SHA-256
`f81798c2e1dfb3159986d8977a8a843ab40b0636490056f95fcb4a4f6ba15e8f`.
The package passed ZIP path/CRC review and all 18 controlled payloads matched
their recorded size and SHA-256.

The current manuscript and Supplementary Markdown matched the expected Git
blobs before patch application. The proposed Stage K source changes applied
cleanly. The external candidate was treated as evidence, not as a
self-authorizing PASS.

## Stage J-K evidence reconciliation

The Stage I estimate was independently checked against the canonical RP v3 WP1
output:

| Procedure | Point estimate | 95% interval | Additional quantity |
|---|---:|---|---|
| RP v3 WP1 paired percentile bootstrap | 0.03492500214665206 | 0.013789273887900366 to 0.057129573029123096 | 2,000 paired donor resamples |
| RP v4 Stage I HC3-t(64) | 0.034925002146652055 | 0.011834174910715159 to 0.05801582938258895 | SE 0.011558534552475956; nominal P 0.0036124588023115677 |

The point-estimate difference is approximately `6.94e-18`. Both procedures use
the same 68 donors, same `delta_profile` estimand, same outcome definition and
same four-column design. Stage I is therefore an uncertainty re-estimation for
one existing measurement-rule contrast, not an independent replication.

The integration preserves the chronology: G2C was developed after the positive
WP1 contrast was known. Its synthetic PASS qualifies the HC3-t(64) interval in
the tested generating regimes; it does not remove outcome exposure, license
other WP2 targets, establish mediation or prove a cell-intrinsic effect.

## Canonical manuscript changes

Source-level edits were made to:

- `01_manuscript/Manuscript.md`: one Methods paragraph and one Discussion
  paragraph;
- `01_manuscript/Supplementary_Information.md`: Supplementary Table S10,
  exact methods/results text and boundary note;
- `phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/01_STAGE_K_SOURCE_DATA.csv`:
  two full-precision rows marked `SAME_DONORS_SAME_ESTIMAND`.

The final wording uses "re-estimated uncertainty" rather than the awkward
"re-interval" construction. No Results claim, Figure 1-5 panel,
Supplementary Figure S1-S10 panel, biological result or historical statistic
was changed.

## Document rebuild and QA

The editable candidate documents were rebuilt from source-level replacements,
then rendered and inspected:

| Check | Manuscript | Supplementary Information |
|---|---:|---:|
| LibreOffice pages | 32 | 16 |
| WPS pages | 32 | 16 |
| DOCX accessibility high/medium/low | 0/0/0 | 0/0/0 |
| Text anchors | PASS | PASS |
| Visual review | all LibreOffice pages; WPS pp.15 and 18 | all LibreOffice pages; WPS p.6 |

No clipping, overlap, orphaned Table S10, unexpected page shift or figure
change was observed. The Stage K integrity manifest passed 10/10 files.

Stage K decision:
`PASS_STAGE_K_LIMITED_SOURCE_INTEGRATION__HOLD_SUBMISSION_AND_EXTERNAL_OUTCOMES`.

## Stage L official metadata reconstruction

Only official GEO MINiML and previously frozen run-planning metadata were read.
No expression matrix or phenotype outcome model was opened.

### GSE262846 RNA

- 88 libraries, 45 patient IDs;
- 17 healthy controls, 13 active SLE and 15 inactive SLE patients;
- 43 patients have both rN and T1T2 libraries;
- the prospective paired-SLE primary set contains 26 patients: 12 active and
  14 inactive;
- patient 3553 (SLEDAI 20) and patient 428 (SLEDAI 0) are rN-only and excluded
  from the paired primary estimand;
- title `SLE.0.3621.rN` maps to deposited patient ID `3651` and is retained as
  a provenance anomaly;
- the deposited processed object is RPKM, not integer counts.

### GSE263716 ATAC and cross-assay boundary

- 62 ATAC libraries, 43 patient IDs and 19 fully rN/T1T2-paired patients;
- 36 patient IDs overlap GSE262846;
- overlapping patient IDs 1655 and 3651 have discordant deposited SLEDAI;
- same-visit multi-omic pairing is not established;
- the ATAC series is neither an independent cohort nor an authorized
  confirmatory outcome source.

The earlier GSE118254 cohort remains a historical/technical comparator because
it is already linked to the published 2019 SLE B-cell epigenomic and
transcriptomic study; it is not prioritized as a second novelty cohort.

## Frozen external scientific question

The sole primary external question is whether the within-patient frozen
12-gene IFN/ISG score difference
`D_i = score(T1T2) - score(rN)` differs between active and inactive SLE.

- independent unit: patient;
- primary population: 26 paired SLE patients;
- primary design: intercept, active-SLE indicator and deposited RNA batch;
- uncertainty candidate: donor-level OLS with HC3 covariance and residual-df
  two-sided t reference, conditional on a prospective small-sample simulation;
- continuous SLEDAI: one secondary sensitivity;
- healthy controls: descriptive context only;
- sex/race: reported limitations, not model covariates because within-SLE
  support is effectively absent;
- no score, threshold, covariate or method selection by smaller P value.

The primary novelty is the paired B-cell-compartment/activity interaction, not
another generic positive IFN result.

## Raw-count and runtime gate

The official plan identifies 176 SRA runs across 88 RNA experiments, about
233.209 GB of SRA payload. At least 2.5 TB scratch is recommended for safe raw
reconstruction. The following remain incomplete and therefore fail closed:

- explicit author authorization for the large download;
- sample-to-run reconciliation;
- frozen GRCh38 and GENCODE versions;
- disease-blind alignment/count pipeline and checksum contract;
- integer-count reconstruction;
- outcome-inaccessible score measurability checks;
- prospective small-sample operating-characteristic qualification.

No raw download was started and no external activity coefficient was fitted.

## Engineering and regression results

- Stage L parser/unit tests: 4/4 PASS.
- Full RP v4 regression suite: 81/81 PASS.
- New Python modules: byte-compilation PASS.
- Stage K integrity manifest: 10/10 PASS.
- Stage L integrity manifest: 12/12 PASS.
- JSON structured-file parsing: 8/8 PASS.
- CSV structured-file parsing: 9/9 PASS.
- Stage L provenance paths were regenerated as project-relative paths; no
  local `H:` or `C:` path is stored in the canonical receipt.

The Stage L generator, Windows runner and tests are tracked. Local MINiML
downloads and candidate-package extracts remain ignored evidence caches.

## Decisions and next stage

Final decision:
`PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION`.

Next gate:
`RPV4_STAGE_M__RAW_RECONSTRUCTION_AUTHORIZATION_AND_DISEASE_BLIND_COUNT_PIPELINE_FREEZE`.

Stage M should freeze storage, SRA identity, reference/annotation versions,
alignment/count software, sample-to-run accounting, checksums, outcome firewall
and the small-sample simulation plan. It must still stop before downloading or
fitting outcomes unless those operations receive separate explicit approval.

## Canonical outputs

- `phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/`
- `phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/`
- `audit_tools/rp_v4_stageK_02_refine_documents.py`
- `audit_tools/rp_v4_stageL_01_external_gate.py`
- `audit_tools/run_rp_v4_stageL.ps1`
- `audit_tools/test_rp_v4_stageL.py`
- `01_manuscript/Manuscript.md`
- `01_manuscript/Supplementary_Information.md`

The final Git commit is reported after repository-wide QA and is deliberately
not self-embedded in this record.
