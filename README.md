# Disease-blind analysis of B-cell remodeling in systemic lupus erythematosus

This repository contains the auditable analysis, scientific-governance records,
manuscript sources and compact derived results for a hierarchy-aware single-cell
study of B-cell remodeling in systemic lupus erythematosus (SLE).

Repository: [1209433622cz-maker/sle-bcell-remodeling](https://github.com/1209433622cz-maker/sle-bcell-remodeling)

## Organized project view

The 12 October 2026 audit adds a non-destructive project view while preserving
all frozen analysis paths and hashes. Start with the
[master index](0_admin/MASTER_INDEX.md), then use the dedicated folders for
[data](1_data/), [code](2_code/), [results](3_results/),
[figures](4_figures/), [manuscript](5_manuscript/),
[release package](6_release/), [reports](7_report/),
[archive decisions](8_archive/), [references](8_reference/) and
[version/integrity records](9_version/).

The current verified package is
[`SLE_Bcell_Submission_Package_2026-10-12`](6_release/SLE_Bcell_Submission_Package_2026-10-12/)
with a matching downloadable ZIP. Its state is
`PRE_SUBMISSION_MASTER_PACKAGE__NOT_SUBMITTED`: the scientific text is the RP
v4 Stage K limited-integration baseline, Figures 1-5 use the QiTeng
reader-language freeze, and no Stage L/M external outcome has been inserted.

## Current status

**Active state on 11 October 2026:**
`ACTIVE_RP_V4_SCIENTIFIC_REDESIGN / HOLD_SUBMISSION`.

The public v1.1.0 archive and the September scientific-presentation baseline are
retained as historical, reproducible snapshots. They are not being silently
rewritten. RP v3 is retained as a completed bounded record: G2B improved the
applicable-domain result from 90/150 to 133/150 PASS target-scenario rows but did
not pass its frozen conjunction, and WP3 ended with outcome-blind pooled
measurement diagnostics only.

The active project now follows Research Plan v4 as a separate prospective
branch. Stage A verified the proposal bundle, carried forward every RP v3 HOLD,
diagnosed the 17 G2B failures and audited official GEO metadata. Stage C froze
exactly one G2C estimand and one method, independent final random streams, 40
data-generating scenarios, S0/S1 measurement handling and a fail-closed raw
input protocol. Stage D canonically integrated the shifted-DGP generator and
technical pilot. Stage E2 recorded both authors' approval of the frozen
scientific contract. The independent Stage F review then identified an unbound
truth helper and incomplete runtime/payload integrity checks. Stage F2 repaired
those issues additively, re-bound the complete local dependency set and passed
the canonical Windows qualification. Both authors then approved the exact
post-patch baseline. Final stages 141/142 completed and the single G2C procedure
passed all 30 applicable synthetic scenarios; 10 mandatory boundary scenarios
were retained. Stage H then bound the exact 68-donor real-input geometry and
confirmed, without constructing a response, that the observed design, support,
library and mixture anchors are inside the frozen synthetic applicability
domain. Both authors then approved all six Stage I conditions. The single
write-once real `delta_profile` fit completed and found a positive
measurement-rule association difference. Stage K then integrated this result
only as an uncertainty-method sensitivity for the same 68-donor estimand;
Stage L independently froze a clinically distinct external-cohort question
without reading expression outcomes. Stage M then closed the 176-run/88-library
identity map, pinned a disease-blind GENCODE 50 / nf-core-rnaseq 3.27.0 count
workflow and passed a prospective synthetic HC3-t(23) small-sample gate. The
current host still lacks the canonical toolchain and 2.5 TB scratch, and no
download authorization has been signed. Submission, external outcome fitting,
GitHub Release and Zenodo updates remain on hold.

Current gate:

```text
PASS_STAGE_M_DISEASE_BLIND_PIPELINE_AND_SIMULATION_FREEZE__HOLD_RUNTIME_STORAGE_AND_DOWNLOAD_AUTHORIZATION
```

Next stage:

```text
RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION
```

## Scientific position

The stable historical conclusion remains **reproducible process-level B_CONV
IFN/ISG remodeling**, bounded by three permanent limitations:

Historical scientific-presentation title: **Disease-blind reconstruction
distinguishes reproducible interferon remodeling from unstable B-cell state
assignments in systemic lupus erythematosus**.

End-to-end resampling did not meet the frozen identity criterion: the B_ASC median Jaccard was 0.930, below 0.95.
This historical HOLD remains in force.

1. **Identity ceiling:** end-to-end B_ASC membership did not meet the frozen
   reproducibility criterion (median Jaccard 0.930323 < 0.95).
2. **Transfer ceiling:** corrected source-label-independent external calibration
   failed its frozen B_ASC precision criterion (0.885210 < 0.90); corrected
   external disease outcomes were never unlocked.
3. **Mechanistic ceiling:** STAT1/STAT2 evidence is observational and partly
   coupled to the broader IFN-response transcriptome; it does not establish a
   unique ligand, direct binding or causal regulation.

The redesign does not attempt to rescue these HOLD decisions. It asks narrower,
predeclared questions about annotation sensitivity, composition, within-state
effects and the identifiability of those quantities.

## RP v4 progress

### Stage M: disease-blind raw-count pipeline freeze

- The Stage C RunInfo SHA-256 closes exactly over 176 unique paired-end runs,
  88 experiments, 88 BioSamples and 88 GSM libraries; every GSM has exactly
  two runs. Totals remain 752,698,793,704 bases and 233,209 MB.
- The execution map and nf-core samplesheet contain no patient, disease,
  SLEDAI, activity, cell-type or effect field. Patient identity is joined only
  after a sealed count/QC object, so the known `GSM8180322` title typo cannot
  silently alter donor mapping.
- The only admitted workflow is full-quality SRA Toolkit 3.4.1 followed by
  nf-core/rnaseq 3.27.0 under Linux x86-64 Docker for STAR alignment/QC, then
  standalone Subread featureCounts 2.1.1 for integer fragment counts, with no
  trimming, automatic strandedness and GENCODE 50 GRCh38.p14 primary assembly.
- The fixed 26-patient OLS/HC3/t(23) estimator passed six null and two
  alternative synthetic scenarios. Null rejection rates were 0.0303-0.0436;
  interval coverage was 0.9564-0.9697. Alternative power is descriptive only.
- WSL2 is present, but SRA Toolkit, Nextflow, Docker and featureCounts are absent.
  The largest host-volume free space is approximately 0.354 TB. WSL reports a
  0.987 TB virtual root, but this is diagnostic only and cannot qualify physical
  scratch. Both are below the frozen 2.5 TB requirement, and the Stage N
  authorization template remains unsigned.
- No SRA/reference payload was downloaded, no expression matrix was read and
  no external activity coefficient was fitted.

Decision:
`PASS_STAGE_M_DISEASE_BLIND_PIPELINE_AND_SIMULATION_FREEZE__HOLD_RUNTIME_STORAGE_AND_DOWNLOAD_AUTHORIZATION`.

### Stage K-L: bounded integration and external-question freeze

- Stage K independently confirmed that RP v3 WP1 and RP v4 Stage I are the
  same 68-donor `delta_profile` estimand: both point estimates are 0.034925002,
  differing only at floating-point precision. They are not independent
  replications.
- The manuscript received one bounded Methods addition and one bounded
  Discussion addition; Supplementary Table S10 and two full-precision Source
  Data rows compare the paired percentile and HC3-t(64) intervals. Figures 1-5
  and Supplementary Figures S1-S10 were unchanged.
- WPS and LibreOffice both render the integrated manuscript at 32 pages and
  the Supplementary Information at 16 pages. DOCX accessibility is 0/0/0 for
  both files; the Stage K controlled manifest is 10/10 PASS.
- Stage L reconstructed official GSE262846 metadata as 88 RNA libraries from
  45 patient IDs. Forty-three patients are rN/T1T2 paired; the prospective
  SLE-only primary set is 26 paired patients (12 active, 14 inactive).
- The unique external question is the patient-level T1T2-minus-rN IFN/ISG
  score difference between active and inactive SLE. Healthy controls are
  descriptive context; continuous SLEDAI is secondary.
- GSE263716 cannot yet be treated as same-visit multi-omic confirmation: only
  36 patient IDs overlap the RNA series and two overlapping IDs have discordant
  deposited SLEDAI values.
- No expression matrix was read, no SRA download began and no external outcome
  was fitted. The 233.209 GB raw payload and at least 2.5 TB scratch require a
  separate Stage M authorization and disease-blind count-pipeline freeze.

Decision:
`PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION`.

### Stage I: single real `delta_profile`

- Zhi Chen and Teng Qi jointly approved all six frozen conditions and one
  write-once execution bound to commit `b413ce09fae520eef0a7a781ee71ddece7606be0`.
- Both authors explicitly reconfirmed the same six conditions after execution;
  the reconfirmation is archival and does not authorize a second run.
- The sole estimate was `0.034925` T0 score units (HC3 SE `0.011559`, t(64)
  95% CI `0.011834` to `0.058016`, two-sided `P=0.003612`).
- Under the frozen sign convention, the managed-SLE versus control association
  was greater under the fixed-profile measurement rule than under pooled counts.
- This is bounded measurement/mixing-rule sensitivity evidence, not causal
  mediation, a cell-intrinsic disease effect or validation of other targets.
- No donor-level response was exported, no fallback or rerun occurred, and no
  external outcome, manuscript or submission gate was automatically unlocked.

Decision:
`PASS_STAGE_I_WRITE_ONCE_EXECUTION__POSITIVE_DELTA_PROFILE_ASSOCIATION__HOLD_AUTOMATIC_UNLOCK`.

### Historical Stage I author-decision preflight

- Rechecks the clean synchronized `main` baseline, all 10 Stage H controlled
  files, the input-manifest and execution-script hashes, and the exact qualified
  Windows runtime before creating any decision object.
- Produces an unsigned draft bound to the final Git commit in the ignored local
  `_software_tests` area, avoiding a self-referential commit hash.
- Passes that unsigned draft to the real Stage I runner and requires fail-closed
  rejection before response construction or output creation.
- Does not count a general instruction to continue as approval by both authors.
  No real disease/activity response has been loaded or fitted.

Checkpoint decision, subsequently superseded by the authorized execution:
`READY_FOR_EXPLICIT_TWO_AUTHOR_DECISION__STAGE_I_NOT_AUTHORIZED`.

The next scientific action is a binary author decision on the exact six-condition
form. It is not an invitation to preview or tune the coefficient.

### Stage H: effect-blind real-data applicability preflight

- Bound the canonical common-support set, four-column design, donor-bin raw
  sufficient counts, frozen T0 reference, `pi_ref`, effect-blind WP2 geometry,
  synthetic calibration model and final Stage G decision by SHA-256.
- Reconfirmed 68 unique donors (31 controls, 37 managed-SLE), rank 4, 340/340
  donor-bin units, minimum support of 30 cells and maximum outcome-blind hat
  leverage of 0.104567.
- The real design and 68 x 5 cell template are exactly identical to the G2C
  calibration anchor. Regularized 12-gene-plus-background probabilities are
  identical; captured-UMI-per-cell rates differ by at most `4.55e-13` from
  floating-point reconstruction.
- All 9 support/design checks and all 9 applicability checks passed. No
  observed-geometry extrapolation was found, while the untestable latent-DGP
  boundary remains explicit.
- The Stage I runner is write-once and fail-closed. Its unsigned template was
  rejected before response construction. Stage H loaded no real response and
  fit no disease coefficient.

Decision:
`PASS_STAGE_H_EFFECT_BLIND_APPLICABILITY__HOLD_STAGE_I_AUTHOR_SIGNOFF`.

See the [Stage H advisor review](phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/09_STAGE_H_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/08_STAGE_H_GATE_STATUS.json)
and [Stage I contract](phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/10_STAGE_I_EXECUTION_CONTRACT.md).

### Stage G: final synthetic G2C validation

- Both authors approved commit
  `ca95aa656e73694e80c8030e42608f6712099404`, the F2 source binding and the
  qualified runtime, and separately authorized stages 141 and 142.
- Stage 141 completed 40 scenarios, 160,000 attempts and 1,600 sealed chunks.
  A resume audit reused all chunks without changing their hashes.
- Stage 142 completed 15 shifted-DGP scenarios and 240 sealed checkpoints. All
  truth precision and independent score checks passed; maximum
  `MCSE / typical SE` was 0.007842.
- Final result-blind adjudication returned 30/30 applicable scenarios PASS and
  10/10 mandatory boundaries reported, with zero numerical failures. An
  independent readjudication was byte-identical.
- The closest bias case was `C4_X3` at 0.098054 against the 0.10 limit. The
  largest coverage Wilson upper bound was 0.972152 in `C0_X3` against 0.975.
  These passing but near-boundary results remain part of the interpretation.
- This synthetic PASS applies only to `delta_profile` under the frozen DGPs. It
  does not erase G2/G2B HOLDs or authorize a real coefficient.

Decision: `G2C_SYNTHETIC_PASS__SEPARATE_REAL_OUTCOME_REVIEW_REQUIRED`.

See the [Stage G advisor review](phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/14_STAGE_G_ADVISOR_REVIEW.md),
[final gate](phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/11_FINAL_SYNTHETIC_GATE.json)
and [Stage H effect-blind contract](phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/15_STAGE_H_EFFECT_BLIND_PREFLIGHT_CONTRACT.md).

### Stage F2: integrity hardening and post-patch rebinding

- Confirmed the Stage F review against GitHub commit `18cbcf0d6269464e2964b6b788c4a35572ed822e`.
  The review correctly identified that `rp_v4_g2c_truth.py` was used by the
  Stage 142 engine but omitted from the Stage E2 binding, and that clean-tree,
  exact-runtime and complete result-payload validation were insufficient.
- Preserved Stage E2 unchanged and added a new Stage F2 pipeline. The source
  binding now contains the complete local dependency set, including the truth
  helper, frozen contracts, calibration model and historical truth table.
- Final authorization now requires the exact Git HEAD, a clean worktree, the
  source-binding digest, the qualified Python executable SHA-256 and exact
  Python/NumPy/SciPy/statsmodels versions.
- Every outer chunk and truth checkpoint is write-once and SHA-256 sealed.
  Final adjudication must reconcile the chunk manifest, attempt accounting,
  truth checkpoint inventory, truth CSV and their receipts before reading any
  result.
- Every supported attempt must satisfy the exact HC3-t(64) interval identity.
  The truth engine also performs an independent score-formula cross-check and
  supports deterministic per-scenario checkpoint resumption without
  replenishment or seed changes.
- The combined G2C, Stage A, Stage D, Stage E2 and Stage F2 regression and
  adversarial suite passed 61/61.
  Windows stage-132 qualification completed 24 outer attempts, three truth
  scenarios and 48 truth checkpoints. Fresh/resume trees were byte-stable and
  maximum `MCSE / typical SE` remained 0.005907.
- Source-binding SHA-256 is
  `e69ca282c046e43325ee2ae1f0b53f76bf2ee017771423ace1e866c646bf21a8`;
  qualified-runtime receipt SHA-256 is
  `bc743876f470bca0e2fb9c8df73bd4f07f2d61f5de8600b5b2150e7cb8b4386d`.
  At the F2 freeze, Stage 141/142 remained unstarted and unauthorized.

Decision:
`PASS_STAGE_F2_INTEGRITY_HARDENING_AND_REBIND__HOLD_POST_COMMIT_EXACT_CODE_GO`.

See the [Stage F2 advisor review](phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/09_STAGE_F2_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/07_STAGE_F2_GATE_STATUS.json)
and [Stage G exact-code contract](phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/10_STAGE_G_GO_NO_GO_CONTRACT.md).

### Stage E2: author contract and canonical final-pipeline binding

- Independently verified the received Stage E package: 154 ZIP entries, clean
  CRC and 153/153 manifest-controlled payloads. The 15 shifted-DGP stage-131
  truth-budget results reproduced on the qualified Windows runtime; the largest
  `MCSE / typical SE` remained 0.007755.
- Found and repaired a real portability defect in the external candidate: its
  preflight opened CSV files with the Windows default encoding and failed under
  GBK. Canonical text readers now require UTF-8 explicitly.
- Recorded Zhi Chen and Teng Qi's approval of the single estimand, single method,
  40 x 4,000 grid, fixed seed/stages, unchanged thresholds, no replenishment and
  no-G2D stop rule. This contract sign-off is separate from exact-code execution
  authorization.
- Added a resumable stage-141-capable outer runner, independent stage-142 truth
  runner, fail-closed authorization binding and write-once 40-scenario
  adjudication driver. The final namespaces cannot open without a new receipt
  that binds both authors, the committed Git HEAD and the source manifest SHA.
- Passed 15/15 project-side tests. A non-final stage-132 qualification executed
  24 outer attempts with fresh/resume equivalence; three truth cases passed the
  full 131,072-per-arm budget with maximum `MCSE / typical SE = 0.005907`.
- Confirmed that at Stage E2, stages 141 and 142 were not started and no real outcome,
  SRA download, manuscript or submission asset was touched.

Decision:
`PASS_RPV4_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING__HOLD_EXACT_CODE_GO`.

See the [Stage E2 advisor review](phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/09_STAGE_E2_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/07_STAGE_E2_GATE_STATUS.json),
[author contract sign-off](phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/02_AUTHOR_CONTRACT_SIGNOFF.json)
and [Stage F exact-code contract](phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/10_STAGE_F_GO_NO_GO_CONTRACT.md).

### Stage D: canonical technical implementation

- Independently verified the received Stage D ZIP: 87 entries, 86 controlled
  payloads, zero CRC/size/SHA-256 failures and 6/6 Stage C inputs byte-identical
  to the repository authority.
- Integrated the shifted 40-DGP generator and independent development-stage
  truth engine while retaining the existing Stage C HC3-t kernel as the single
  canonical estimator.
- Passed 22/22 project-side Stage C/Stage D tests under
  `D:\bioinfor\python.exe`.
- Reproduced the fixed 24-attempt technical pilot: 18 supported attempts, six
  prespecified support stops and zero numerical failures. A 4-attempt checkpoint
  resumed to eight attempts matched a fresh eight-attempt run in 28/28 files
  byte for byte.
- Confirmed technical precision in the three selected development oracle cases;
  these are not the complete stage-142 truths and are not a G2C performance
  result.
- Generated a plan-only ledger for 261 SRA runs/171 experiments and 297.574 GB
  reported payload. No download, alignment or outcome inspection occurred.
- Qualified `D:\bioinfor\python.exe` for this stage. The Miniforge `sle-bcell`
  runtime exits with native code `0xC06D007F` on the X2 Cholesky path and is not
  approved for G2C execution.

Decision:
`PASS_RPV4_STAGE_D_CANONICAL_TECHNICAL_IMPLEMENTATION__HOLD_STAGE_E_AUTHOR_SIGNOFF_AND_FINAL_G2C`.

See the [Stage D advisor review](phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/11_STAGE_D_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/09_STAGE_D_GATE_STATUS.json),
[runtime qualification](phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/03_WINDOWS_RUNTIME_QUALIFICATION.json)
and [Stage E preflight contract](phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/12_STAGE_E_PREFLIGHT_CONTRACT.md).

### Stage C: single G2C and external-input protocol freeze

- Selected only `delta_profile`, because its historical G2B point-bias gate
  passed in all 15 applicable scenarios and its residual failures were confined
  to interval coverage. `delta_cellref` was not selected because it mixed
  coverage and point-bias failures.
- Replayed the exposed historical development stream. Bootstrap-SE p01/median
  was at least 0.532, maximum point leverage was 0.105, no inner diagnostic fit
  failed, and the direct delta equalled the coefficient difference to within
  `4.57e-15`. This argues against a collapsed studentizer or non-smooth target.
- Froze one method: direct donor-level `delta_profile` OLS with HC3 influence
  variance and a two-sided `t(64)` interval. It passed 15/15 exposed applicable
  development cells, but this is explicitly not forward confirmation.
- Registered a new seed base, 25 old-comparable plus 15 shifted DGPs and 4,000
  outer attempts per scenario (160,000 total). The final run is not authorized.
- Reconciled official NCBI SRA RunInfo: GSE262846 has 176 runs/88 experiments
  (about 233.21 GB SRA) and GSE118254 has 85 runs/83 experiments (about 64.37 GB).
  Raw reconstruction is feasible but pending; both outcome tables remain locked.
- Conservatively treat the two candidates as potentially donor-overlapping.
  GSE118254 cannot be counted as a second independent confirmation of GSE262846.
- Retained S0 as the primary frozen score and S1 as a technical sensitivity;
  S2 was abandoned because no unique result-blind formula could be justified.

Decision:
`PASS_RPV4_STAGE_C_PROTOCOL_FREEZE__AUTHOR_SIGNOFF_REQUIRED_BEFORE_FINAL`.

See the [Stage C advisor review](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/12_RPV4_STAGE_C_ADVISOR_REVIEW.md),
[method contract](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json),
[external-input contract](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/08_EXTERNAL_RAW_RECONSTRUCTION_AND_PROVENANCE_CONTRACT.md)
and [machine-readable gate](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/11_RPV4_STAGE_C_GATE_STATUS.json).

### Stage A: authority, historical diagnosis and external feasibility

- Rechecked all ten files in the external RP v4 proposal manifest by byte size
  and SHA-256; the bundle is evidence input, not a self-authorizing gate.
- Verified that the local RP v3 WP3 commit is accessible and descends directly
  from the current `origin/main`, correcting the proposal candidate's stale
  authority statement.
- Reproduced the historical G2 90/150 and G2B 133/150 applicable-cell counts.
- Classified all 17 G2B failures from the 2,000-attempt raw outputs: 11 coverage
  failures, six bias failures and one exact-null type-I failure overlapping a
  coverage failure.
- Localized residual undercoverage to nine `delta_profile` and two
  `delta_cellref` cells. The misses are mild and broadly two-sided; the frozen
  outputs do not identify a unique corrective interval.
- Parsed official GEO MINiML metadata for five candidate accessions. The two
  leading bulk candidates have recoverable donor structures, but neither is
  authorized for outcome analysis until raw-count compatibility and provenance
  independence are resolved.
- Retained `S0=T_frozen` as the primary measurement anchor and `S1=T_rank` as a
  sensitivity. S2 was not admitted because no unique result-blind formula exists.

Decision:
`PASS_RPV4_STAGE_A_AND_V4B_HISTORICAL_DIAGNOSIS__HOLD_G2C_AND_NEW_COHORT_OUTCOMES`.

See the [Stage A advisor review](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json)
and [next protocol requirements](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md).

## RP v3 historical progress

### Stage 0: inputs, units and estimands

- Recovered and hashed 21/21 required inputs.
- Confirmed 150,402 GSE174188 B-lineage cells, 30,172 genes, 259 donors,
  271 samples, 88 technical libraries and four processing cohorts.
- Verified the 1.30 GB GSE135779 RAW archive and all 56 matrix/barcode pairs.
- Registered biological units, chronology, estimands, branches and open
  parameters before new effect estimation.
- Initial decision: input recovery PASS; protocol/identifiability fields remained
  open and therefore correctly held.

See [Stage 0 gate](phase17_v7/rp_v3_redesign/20261009_stage0/08_STAGE0_GATE_STATUS.json)
and the [Stage 0 action record](00_project_management/action_record_2026-10-09_rp_v3_stage0_intake_and_freeze.md).

### Stage 0B: result-blind protocol and minimal trial

- Froze the A1 continuous 14-gene identity axis, the A2 3,000-feature
  strong-ISG-list-excluded representation, T0/T_frozen/T_rank and `pi_ref`.
- Rebuilt A2 on all 150,402 cells with the correct full-background
  normalization denominator.
- Obtained A0-A2 ARI 0.795448 and NMI 0.680148 with five A2 clusters.
- Verified finite score transfer and 12/12 program coverage.
- Completed five technical simulation scenarios with maximum absolute bias
  0.002315, empirical coverage 0.925-0.970 and no fit failures.
- No disease coefficient was inspected during this gate.

Decision: `PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY`.

See [Stage 0B gate](phase17_v7/rp_v3_redesign/20261009_stage0b/14_STAGE0B_GATE_STATUS.json),
[execution contract](phase17_v7/rp_v3_redesign/20261009_stage0b/17_WP1_ANNOTATION_SENSITIVITY_EXECUTION_CONTRACT.md)
and [action record](00_project_management/action_record_2026-10-09_rp_v3_stage0b_protocol_and_minimal_trial.md).

### WP1: annotation sensitivity

WP1 used the same 68-donor common support set (31 controls and 37 managed-SLE
donors), the same frozen four-column design and the same T0 reference in all
branches. All 2,000 paired donor-clustered bootstrap attempts succeeded.

| Estimand | Estimate | Paired bootstrap 95% CI |
|---|---:|---:|
| `beta_A0` | 1.037152 | 0.598263 to 1.477349 |
| `beta_A1` | 1.072077 | 0.630517 to 1.518759 |
| `beta_A2` | 1.037718 | 0.598753 to 1.477793 |
| `A1 - A0` | 0.034925 | 0.013789 to 0.057130 |
| `A2 - A0` | 0.000567 | 0.000000 to 0.001424 |

The managed-SLE coefficient remained positive across all three frozen
representations. A1 is a joint identity-axis/common-composition sensitivity,
not a pure annotation or mediation effect. A2 retains `LY6E`, and no equivalence
margin was declared; therefore neither "fully IFN-independent" nor "equivalent"
is authorized.

See [WP1 adjudication](phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/12_WP1_FINAL_ADJUDICATION.md),
[machine-readable decision](phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/11_WP1_FINAL_ADJUDICATION.json)
and [action record](00_project_management/action_record_2026-10-10_rp_v3_wp1_annotation_sensitivity.md).

### WP2: effect-free composition and identifiability preflight

The canonical WP2 preflight used the frozen 68-donor set and raw sufficient
statistics without fitting a new disease coefficient or writing grouped
expression summaries. It passed all support, hash, partition and design checks:

- every donor retained all five A1 bins, with a minimum of 30 cells per bin;
- A1 bin counts, full captured-library totals and cell counts exactly recover
  the parent A0 object;
- captured-UMI-weighted bin CPM reconstructs pooled CPM to `1.137e-13` maximum
  absolute error;
- the median absolute difference between cell and captured-UMI fractions is
  `0.015954`, with a maximum of `0.093275`;
- the optional base-plus-four-ILR design is rank 8/8, while intercept plus all
  five raw fractions is closure-redundant at rank 8/9.

The target registry now distinguishes the already observed fixed-profile WP1
target from a new cell-reference bridge target that retains captured UMI/cell.
Neither is an absolute-RNA or causal cell-composition effect. The target,
25-scenario and acceptance registries were frozen before G2 results.

Decision:
`PASS_WP2_EFFECT_FREE_PREFLIGHT__HOLD_G2_EXECUTION_IMPLEMENTATION_REQUIRED`.

See the [WP2 preflight review](phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/11_WP2_PREFIT_ADVISOR_REVIEW.md)
and [machine-readable gate](phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/06_WP2_PREFIT_GATE_STATUS.json).

### G2 implementation, full execution and adjudication

The sufficient-count generator, actual paired-bootstrap estimator and an
independent nonlinear truth engine are now hash-bound. Independent Windows
requalification reproduced all 50 pilot statuses, 60,000/60,000 successful
inner fits and 250/250 truth-precision passes. Generated counts and bootstrap
indices were byte-identical across platforms; the largest floating-point
difference was `8.88e-16`.

R0, R2 and R4 are frozen as the applicable performance domain. R1 and R3 remain
mandatory boundary domains and cannot be deleted or rescued. The complete grid
then ran 50,000 outer attempts and 60,106,000 paired-bootstrap fits with no
numerical failures. Of 150 applicable target-scenario cells, 90 passed and 60
were held. Coverage passed in 91/150 cells; all 59 coverage failures were
undercoverage. Bias passed in 149/150, truth precision in 150/150 and registered
exact-null type-I control in 10/10. None of the ten targets passed all 15
required applicable scenarios, so no WP2 real effect is unlocked.

Decision:
`HOLD_G2_APPLICABLE_DOMAIN`.

See the [G2 implementation review](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/10_G2_IMPLEMENTATION_ADVISOR_REVIEW.md),
[execution contract](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/08_G2_EXECUTION_CONTRACT.json)
and [full-G2 post-adjudication review](phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/08_G2_POST_ADJUDICATION_REVIEW.md).

### G2B full execution and scope contraction

The G2 HOLD was diagnosed without reading real WP2 outcomes. Exactly one
replacement was selected on methodological grounds: an equal-tailed paired
donor bootstrap-t interval with an HC3 studentizer. The point estimator,
generator, ten targets, 25 scenarios, truth table, applicable/boundary split and
all acceptance thresholds remain unchanged.

The external candidate archive passed 901/901 payload checks and 42/42 tests.
On Windows, the 150-object development replay reproduced 90 supported intervals,
60 support stops and 180,000 inner attempts with no numerical failures. A further
4,500 explicit expanded-row statsmodels fits agreed with the vectorized HC3
kernel. The canonical Stage 0 through G2B test suite passed 58/58 tests.

The project-side `rp_v3_g2b_*` implementation used a hash-bound stage-121 random
namespace and rejected old G2 bindings. The full grid completed 25/25 scenarios,
2,000/2,000 chunks, 50,000 outer attempts and 60,112,000 successful inner
bootstrap draws with no numerical failures. Formal and independent adjudications
were byte-identical.

Among 150 applicable target-scenario rows, 133 passed and 17 held. Coverage
failures fell from 59 under G2 to 11 under G2B, but six bias failures and one
overlapping exact-null type-I failure remained. Four targets passed 15/15
applicable scenarios; partial target unlock was not part of the frozen contract.
The final decision therefore keeps `WP2_REAL_EFFECT_UNLOCK=false`.

Decision:
`HOLD_G2B_APPLICABLE_DOMAIN`.

See the [G2B post-adjudication review](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/09_G2B_POST_ADJUDICATION_REVIEW.md),
[machine-readable decision](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/03_G2B_FINAL_DECISION.json)
and [scope-contraction contract](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/10_G2B_SCOPE_CONTRACTION_CONTRACT.md).

### WP3 result-blind available-object prefit

The project-side prefit passed 22/22 checks without computing new external
scores, disease-group summaries, coefficients, intervals or P values. It bound
56 unique source donors, exact eight-label-to-B_CONV closure, 54 min50-eligible
objects and a 43-donor childhood primary design (11 controls and 32 SLE donors).
All 12 IFN genes and 18,873 frozen rank-background symbols are present. The
source `T_rank` convention is now explicitly verified as average rank divided by
the fixed background size.

Decision:
`PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION`.

See the [WP3 prefit advisor review](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/12_WP3_PREFIT_ADVISOR_REVIEW.md),
[gate status](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/10_WP3_PREFIT_GATE_STATUS.json)
and [measurement-scope protocol](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/11_WP3_EFFECT_FREE_MEASUREMENT_SCOPE_PROTOCOL.md).

### WP3 pooled measurement diagnostics

The project-side pooled stage passed 13/13 focused tests, 25/25 real-input checks
and 4,389/4,389 independent numerical comparisons. Across 54 eligible objects,
`T_frozen` versus `T_rank` pooled Spearman correlation was 0.985744 and the
maximum rank displacement was 6. All 12 leave-one-gene-out correlations were at
least 0.995883. These are pooled measurement diagnostics, not a disease effect,
clinical calibration or cross-platform validation.

Decision:
`PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION`.

See the [pooled-measurement advisor review](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/14_WP3_POOLED_MEASUREMENT_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/12_WP3_MEASUREMENT_GATE_STATUS.json)
and [scope-closure recommendation](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/15_RP_V3_SCOPE_CLOSURE_RECOMMENDATION.md).

## Next gate: effect-blind real-data applicability preflight

The next action is
`RPV4_STAGE_H__REAL_DATA_APPLICABILITY_AND_EFFECT_BLIND_PREFLIGHT`. It may bind
and inspect the real-input donor support, design rank, leverage, missingness,
measurement inputs and DGP applicability, but it may not inspect or fit the
disease coefficient. A separate author approval after that preflight is
required before one real `delta_profile` estimate can run. Large raw download,
external disease/activity effects, WP4, manuscript replacement and submission
remain unauthorized.

## Reproduce the active redesign

Create or check the scientific environment first:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_create_conda_env.ps1
```

Reproduce the active RP v4 Stage A gate after restoring the ignored proposal
evidence and official MINiML files recorded by the action report:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v4_stageA.ps1
```

Reproduce the exposed Stage C development diagnosis in a new directory, then
verify the tracked frozen contract with its focused regression tests:

```powershell
python .\audit_tools\rp_v4_stageC_01_development_diagnostic.py `
  --output-dir .\phase17_v7\rp_v4_redesign\stageC_development_reproduction

& 'C:\ProgramData\miniforge3\envs\sle-bcell\python.exe' `
  -m unittest discover -s audit_tools -p 'test_rp_v4_g2c.py' -v
```

Run the completed gates from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_stage0.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_stage0b.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_wp1.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_wp2_prefit.ps1 `
  -OutputDir .\phase17_v7\rp_v3_redesign\wp2_prefit_reproduction

& .\audit_tools\run_rp_v3_g2_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2_full_runs\20261010_full `
  -Regimes @('R0','R1','R2','R3','R4') `
  -ChunkSize 25 `
  -Adjudicate

D:\bioinfor\python.exe `
  .\audit_tools\rp_v3_g2_04_finalize_full_adjudication.py `
  --run-root .\phase17_v7\rp_v3_redesign\g2_full_runs\20261010_full `
  --output-dir .\phase17_v7\rp_v3_redesign\g2_full_adjudication_reproduction

& .\audit_tools\run_rp_v3_g2b_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2b_full_runs\20261010_stage121_full `
  -ValidateOnly

& .\audit_tools\run_rp_v3_g2b_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2b_full_runs\20261010_stage121_full `
  -Regimes @('R0','R1','R2','R3','R4') `
  -ChunkSize 25 `
  -Adjudicate

powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_rp_v4_stageD.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v4_redesign\stageD_technical_reproduction

powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_rp_v4_stageE2_preflight.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v4_redesign\_software_tests\stageE2_reproduction `
  -CanonicalOutput .\phase17_v7\rp_v4_redesign\stageE2_reproduction_freeze

powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_rp_v4_stageF2_preflight.ps1 `
  -Python D:\bioinfor\python.exe `
  -WorkRoot .\phase17_v7\rp_v4_redesign\_software_tests\stageF2_reproduction `
  -CanonicalOutput .\phase17_v7\rp_v4_redesign\stageF2_reproduction_freeze
```

Run the focused tests:

```powershell
D:\bioinfor\python.exe -m unittest -v `
  audit_tools.test_rp_v3_stage0_freeze `
  audit_tools.test_rp_v3_stage0b `
  audit_tools.test_rp_v3_wp1 `
  audit_tools.test_rp_v3_wp2_prefit `
  audit_tools.test_rp_v3_g2 `
  audit_tools.test_rp_v3_g2b `
  audit_tools.test_rp_v4_g2c `
  audit_tools.test_rp_v4_stageD `
  audit_tools.test_rp_v4_stageE2 `
  audit_tools.test_rp_v4_stageF2
```

Large public matrices and cell-level intermediates are intentionally outside
Git. A checkout alone is not sufficient for a complete rerun; restore inputs
using [Data/README.md](Data/README.md) and verify the recorded checksums.

## Canonical objects

| Purpose | Canonical location |
|---|---|
| Current project status | [`00_project_management/RP_V4_REDESIGN_STATUS.md`](00_project_management/RP_V4_REDESIGN_STATUS.md) |
| RP v4 Stage A authority/feasibility freeze | [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/`](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/) |
| RP v4 Stage C method/input protocol freeze | [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/`](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/) |
| RP v4 Stage D canonical technical freeze | [`phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/`](phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/) |
| RP v4 Stage E2 canonical preflight | [`phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/`](phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/) |
| RP v4 Stage F2 integrity hardening freeze | [`phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/`](phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/) |
| RP v4 Stage G final synthetic validation | [`phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/`](phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/) |
| RP v4 Stage H effect-blind applicability preflight | [`phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/`](phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/) |
| RP v4 Stage I single real delta-profile result | [`phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/`](phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/) |
| RP v4 Stage K limited manuscript integration | [`phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/`](phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/) |
| RP v4 Stage L external-cohort metadata gate | [`phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/`](phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/) |
| Historical RP v3 status | [`00_project_management/RP_V3_REDESIGN_STATUS.md`](00_project_management/RP_V3_REDESIGN_STATUS.md) |
| Full file audit | [`00_project_management/full_project_audit_2026-10-10/FINAL_FULL_PROJECT_AUDIT_2026-10-10.md`](00_project_management/full_project_audit_2026-10-10/FINAL_FULL_PROJECT_AUDIT_2026-10-10.md) |
| Valuable asset register | [`00_project_management/VALUABLE_ASSET_REGISTER_2026-10-10.csv`](00_project_management/VALUABLE_ASSET_REGISTER_2026-10-10.csv) |
| Manuscript source baseline | [`01_manuscript/Manuscript.md`](01_manuscript/Manuscript.md) |
| Supplementary source baseline | [`01_manuscript/Supplementary_Information.md`](01_manuscript/Supplementary_Information.md) |
| Stage 0 output | [`phase17_v7/rp_v3_redesign/20261009_stage0/`](phase17_v7/rp_v3_redesign/20261009_stage0/) |
| Stage 0B output | [`phase17_v7/rp_v3_redesign/20261009_stage0b/`](phase17_v7/rp_v3_redesign/20261009_stage0b/) |
| WP1 prefit contract | [`phase17_v7/rp_v3_redesign/20261010_wp1_prefit_contract/`](phase17_v7/rp_v3_redesign/20261010_wp1_prefit_contract/) |
| WP1 result | [`phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/`](phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/) |
| WP2 effect-free preflight and G2 registries | [`phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/`](phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/) |
| G2 implementation/domain freeze | [`phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/`](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/) |
| Full G2 adjudication and next-stage contract | [`phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/`](phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/) |
| G2B single-method protocol freeze | [`phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/`](phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/) |
| Full G2B adjudication and scope-contraction contract | [`phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/`](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/) |
| WP3 effect-free prefit and measurement-scope contract | [`phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/`](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/) |
| WP3 pooled measurement diagnostics and scope recommendation | [`phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/`](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/) |
| Reproducibility detail | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |

## Repository layout

- `00_project_management/`: decisions, action records, audits and status files.
- `01_manuscript/`: editable manuscript, supplement and proposal sources.
- `02_analysis/`: environment, data acquisition and analysis runbooks.
- `03_results/`: compact retained result assets.
- `04_submission/`: author-facing sources and preserved historical packages;
  generated packages are local unless explicitly tracked.
- `05_Record/`: historical conversation/work records; useful for provenance but
  not authoritative scientific evidence.
- `audit_tools/`: executable analysis, build, validation and audit code.
- `phase17_v7/`: machine-readable gate outputs and scientific run records.
- `Data/`: retrieval guide plus Git-ignored public-data caches.

## Workspace audit

The 10 October 2026 full audit hashed and structurally checked every regular
workspace file outside `.git` and the audit-output directory. At scan time it
covered 7,850 files (5.687 GiB): 7,433 directly validated files, five separately
validated HDF5/H5AD containers, one benign empty package marker and 411
binary/compiled-cache files without a format-specific parser. No corrupt JSON,
CSV, ZIP/OOXML, PDF,
image, gzip, tar, NPZ or HDF5 object was found.

Large duplicate groups account for approximately 340 MiB, mainly historical
submission copies and render/portability tests. They are retained locally for
provenance and excluded from new Git tracking. Deep third-party QiTeng runtime
copies generated 119 Windows paths longer than 240 characters and are also kept
outside Git. See the [full audit](00_project_management/full_project_audit_2026-10-10/FINAL_FULL_PROJECT_AUDIT_2026-10-10.md).

## Public reproducibility archive

The immutable public reference remains:

- [GitHub release v1.1.0](https://github.com/1209433622cz-maker/sle-bcell-remodeling/releases/tag/v1.1.0)
- [Zenodo version DOI 10.5281/zenodo.22151739](https://doi.org/10.5281/zenodo.22151739)
- [Zenodo concept DOI 10.5281/zenodo.22086891](https://doi.org/10.5281/zenodo.22086891)

This release predates RP v3 and must be cited as a historical reproducibility
snapshot, not as the final output of the active redesign.

## Licence

Original code is MIT licensed. Original manuscript text, composite figures,
project documentation and project-generated derived source-data tables are CC
BY 4.0. Public GEO/CELLxGENE data and third-party material are excluded from
those project licences; see [LICENSE_SCOPE.md](LICENSE_SCOPE.md).
