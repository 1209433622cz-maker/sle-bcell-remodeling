# RP v4 scientific redesign status

**Effective date:** 2026-10-11

**Overall state:** `ACTIVE_RP_V4_SCIENTIFIC_REDESIGN`

**Submission state:** `HOLD`

**Current gate:** `PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION`

## Scope

RP v4 is a separate prospective branch created after the complete RP v3 G2/G2B
results were known. It does not rewrite RP v3 as prospectively anticipating a
third interval method, and it does not reopen any historical disease effect.

The active questions are limited to:

1. whether one explicitly registered G2C estimand/method can address the
   historical difference-estimand calibration problem in independent simulation;
2. whether frozen IFN measurements can be transported on a compatible technical
   scale without outcome-based score selection; and
3. whether a genuinely independent public cohort has recoverable donor units,
   suitable raw counts and a prespecifiable clinical question.

## Stage A completed

### Authority

- The external RP v4 proposal ZIP is 224,853 bytes with SHA-256
  `ad4f422f185a75ead5cec4d7fe91b2bd3b36cbe1b5f3dce227016cd8c2fd3b05`.
- Its ten manifest-controlled files passed byte-size and SHA-256 rechecking.
- The proposal is accepted as an evidence input, not as a self-authorizing gate.
- The RP v4 input baseline was local commit
  `8cba83172a52b71528cc2ab44dd3a936cb4dd8c7`; current `origin/main`
  `f2eca1abec44afb73688823f57e42ab78b971203` is its direct parent.

### Historical simulation diagnosis

The project-side recount reproduced:

- G2: 90/150 applicable target-scenario cells PASS;
- G2B: 133/150 PASS and 17 HOLD;
- G2B residual failures: 11 coverage, six bias and one overlapping exact-null
  type-I failure.

Nine coverage failures belong to `delta_profile` and two to `delta_cellref`.
Their misses are mild and broadly two-sided. The frozen outputs do not contain
the per-replicate studentizer or inner-pivot distribution required to identify
one unique corrective interval. Six separate bias failures show that changing
interval endpoints alone cannot be a universal repair.

The following historical boundaries remain unchanged:

- `G2=HOLD_G2_APPLICABLE_DOMAIN`;
- `G2B=HOLD_G2B_APPLICABLE_DOMAIN`;
- `WP2_REAL_EFFECT=LOCKED`;
- `WP3_NEW_OUTCOME=LOCKED`;
- `WP4=HOLD_CONDITIONAL`;
- `SUBMISSION=HOLD`.

### External metadata feasibility

| Accession | Official GEO samples | Recoverable units | Stage A decision |
|---|---:|---:|---|
| GSE262846 | 88 | 45 patient IDs | Conditional metadata pass; count/provenance HOLD |
| GSE118254 | 83 | 17 donor tokens | Conditional donor-structure pass; count/provenance HOLD |
| GSE163121 | 5 | 5 donors | Exploratory only; not primary validation |
| GSE254176 | 57 | 6 longitudinal SLE patients | Repeat-measures exploratory only |
| GSE239459 | 3 | not recoverable | No-go for donor-level inference |

`GSE262846` contains 17 HC, 13 active-SLE and 15 inactive-SLE patient IDs;
43/45 patients have both rN and T1T2 libraries. One sample title conflicts with
its `patient id` field and is retained as a provenance anomaly. Its deposited
processed matrix is RPKM, not the frozen count/CPM scale.

`GSE118254` contains eight HC and nine SLE donor tokens represented by 3-6
sorted-subset libraries each. No exact numeric donor-token overlap with
GSE262846 was observed, but this does not establish independence because the
studies may use different de-identification namespaces and share investigator
lineage.

### Measurement scores

- `S0=T_frozen`: retained as primary frozen measurement anchor.
- `S1=T_rank`: retained as technical sensitivity only.
- `S2`: not admitted because a unique outcome-blind formula, denominator and
  missing-feature rule do not yet exist.

## Stage C completed

### Single estimand and method

- Primary estimand: `delta_profile`, the disease-coefficient difference between
  the frozen fixed-profile mixture score and pooled-count score.
- Interpretation: association difference between two observed measurement and
  mixing rules; not a causal mediation proportion or cell-intrinsic effect.
- Primary method: direct donor-level OLS of the delta response, HC3 influence
  variance and a two-sided `t(64)` interval.
- Fallback: none. A failed final G2C closes the decomposition branch; no G2D is
  permitted.

The exposed development replay passed 15/15 applicable cells. Studentizer and
leverage diagnostics did not indicate collapse: minimum bootstrap-SE
p01/median 0.532, maximum point leverage 0.105, zero inner failures and
algebraic delta error at most `4.57e-15`. This is method-development evidence,
not independent validation.

### Final simulation contract

- independent seed base `2026101004`;
- final outer stage 141 and truth stage 142;
- 25 old-comparable scenarios plus 15 prespecified shifted DGPs;
- 4,000 outer attempts per scenario, 160,000 total, no replenishment;
- 30 scenarios in the applicable conjunction and 10 mandatory boundaries;
- unchanged bias, Wilson coverage, exact-null type-I, truth-precision and
  numerical-failure gates.

The final simulation has not been run and requires exact author sign-off.

### External raw-input contract

Official NCBI RunInfo was downloaded and hashed:

| Accession | Runs | Experiments | Bases | SRA payload |
|---|---:|---:|---:|---:|
| GSE262846 / PRJNA1093470 | 176 | 88 | 752.70 G | 233.21 GB |
| GSE118254 / PRJNA484963 | 85 | 83 | 174.96 G | 64.37 GB |

Raw count reconstruction is technically feasible but pending. At least 2.5 TB
scratch is recommended. Because shared-donor provenance cannot be excluded from
public de-identification tokens, the studies are treated as potentially
overlapping and cannot count as two independent confirmations.

S0 remains primary, S1 remains a technical sensitivity and S2 is abandoned.
All disease/activity outcomes remain sealed.

## Stage D completed

### Independent intake and canonical integration

- The received ZIP had 87 entries and 510,740 uncompressed bytes. Its 86-row
  payload manifest matched every listed file by size and SHA-256; ZIP CRC was
  clean.
- Six Stage C contract inputs in the received package were byte-identical to
  the repository authority.
- The project promoted the shifted-DGP generator and independent truth engine,
  but retained `audit_tools/rp_v4_g2c_hc3t.py` as the only canonical estimator.
  The candidate's duplicate kernel was not promoted.
- Project-side Stage C + Stage D tests passed 22/22 under
  `D:\bioinfor\python.exe`.

### Technical pilot and truth qualification

- The fixed pilot executed 24 development-stream attempts: 18 were supported,
  six reached the prespecified support stop and none failed numerically.
- All six support stops occurred in the selected X3 stress case. They are a
  domain-risk signal, not software failure and not evidence that X3 passes.
- A four-attempt checkpoint resumed to eight attempts matched a fresh
  eight-attempt execution in 28/28 files byte for byte.
- Three selected development-stage oracle cases met the technical precision
  rule. They do not replace the complete stage-142 truth calculation and do not
  support a bias, coverage or type-I claim.

### Windows runtime and SRA boundary

- `D:\bioinfor\python.exe` (Python 3.13.7, NumPy 2.3.3, SciPy 1.16.2,
  statsmodels 0.14.6) is the only Windows runtime qualified by Stage D.
- `C:\ProgramData\miniforge3\envs\sle-bcell\python.exe` terminates on the X2
  Cholesky path with native exit `0xC06D007F`; it is explicitly disqualified for
  final G2C unless repaired and independently requalified.
- The plan-only SRA ledger covers 261 runs, 171 experiments and 297.574 GB of
  reported payload. No download, alignment, count reconstruction or outcome
  inspection was performed.

Stage D decision:
`PASS_RPV4_STAGE_D_CANONICAL_TECHNICAL_IMPLEMENTATION__HOLD_STAGE_E_AUTHOR_SIGNOFF_AND_FINAL_G2C`.

## Stage E2 completed

### External intake and independent replay

- The received Stage E ZIP contained 154 entries and passed CRC testing. Its
  153-row payload manifest matched all controlled files by byte size and
  SHA-256.
- The external adjudicator passed 14/14 focused tests. Its 15 shifted-DGP
  stage-131 truth-budget rows reproduced on `D:\bioinfor\python.exe`: all
  statuses matched, the largest truth difference was zero, and the largest
  MCSE difference was `4.34e-19`.
- The external preflight was not portable as written: a CSV opened without an
  explicit encoding failed under the Windows GBK default. The canonical Stage
  E2 implementation uses UTF-8 explicitly and records this candidate defect.

### Author contract and code binding

- Zhi Chen and Teng Qi approved the single `delta_profile` estimand, the sole
  OLS/HC3/t(64) method, 40 x 4,000 grid, seed base `2026101004`, final stages
  141/142, unchanged truth/performance thresholds, no replenishment and the
  no-G2D stop rule.
- This approval is stored as a scientific-contract sign-off. It does not claim
  that the authors approved code bytes that had not yet been committed.
- The canonical project implementation now contains a resumable outer runner,
  independent shifted-DGP truth runner, fail-closed authorization validator,
  pure adjudicator and write-once full adjudication driver. The source manifest
  binds all code, Stage C contracts, calibration model and historical truth.

### Windows qualification

- Project-side Stage E2 tests passed 15/15 under `D:\bioinfor\python.exe`
  (Python 3.13.7, NumPy 2.3.3, SciPy 1.16.2, statsmodels 0.14.6).
- The non-final stage-132 outer qualification executed 24 attempts across
  C0_X1, C1_X2 and C2_X3. Resume and independent fresh outputs were identical
  for all stable files.
- Three stage-132 truth cases used the full 131,072-per-arm budget and all met
  the precision criterion; maximum `MCSE / typical SE` was 0.005907.
- The unissued exact-code GO template was rejected for both outer and truth
  execution. Stage 141 and stage 142 were not started.

Stage E2 decision:
`PASS_RPV4_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING__HOLD_EXACT_CODE_GO`.

## Stage F exact-code review completed

The independent Stage F package was treated as review evidence rather than as
a self-authorizing result. Its 18,208-byte ZIP was CRC-clean and all 7/7
manifest-controlled files matched their declared size and SHA-256. The review
correctly identified three material integrity gaps in the Stage E2 candidate:

- `audit_tools/rp_v4_g2c_truth.py` was a runtime dependency but was absent from
  the source-binding manifest;
- Git HEAD identity did not prove a clean worktree or the exact qualified
  Windows executable and package versions; and
- final outputs did not yet have complete chunk/checkpoint, truth payload,
  accounting and receipt reconciliation.

The external package's focused test command produced 4/5 rather than its
reported 5/5 on this Windows host because its own newline test hashes a file
written with platform CRLF while expecting LF bytes. This portability defect
does not alter the substantive Stage F findings and the external package was
not modified.

Stage F decision:
`HOLD_STAGE_F_EXACT_CODE_GO__INTEGRITY_HARDENING_REQUIRED`.

## Stage F2 completed

### Additive integrity hardening

- A new F2 implementation was added without rewriting the Stage E2 historical
  freeze. Its required source set explicitly includes the previously omitted
  truth helper, all F2 modules and tests, the Stage C contracts, calibration
  model and historical truth table.
- Final authorization now binds exact Git HEAD, a fully clean tracked and
  untracked worktree, the source-manifest digest, a qualified-runtime receipt,
  the resolved Python executable and its SHA-256, and the Python/NumPy/SciPy/
  statsmodels versions.
- The outer runner uses write-once chunk payloads and sidecar seals, verifies
  bytes and SHA-256, reconciles complete attempt accounting, rejects extra or
  unregistered files and produces a hash-bound receipt.
- The truth runner uses deterministic per-scenario checkpoints and seals,
  verifies the complete checkpoint inventory, refuses partial files and
  independently cross-checks the score formula on every batch.
- The adjudicator verifies both payload systems before reading results and
  independently enforces `point +/- t(0.975,64) * SE`, df=64, method/data flags,
  leverage and outcome-lock conditions.

### Windows qualification and freeze

- The combined Stage A, Stage D, Stage E2 and Stage F2 test suite passed 61/61.
- Non-final outer qualification completed 24 attempts in three sealed chunks;
  resume and fresh outputs were byte-stable.
- Non-final truth qualification completed three scenarios and 48 sealed
  checkpoints; maximum `MCSE / typical SE` was `0.005907133725217648`, and
  resume and fresh outputs were byte-stable.
- The qualified executable is `D:\bioinfor\python.exe`, SHA-256
  `d932e5e2f324d57f392e8fd063dcf6d0185be8a664c57c6d24e7762ed02c28ca`
  (Python 3.13.7, NumPy 2.3.3, SciPy 1.16.2, statsmodels 0.14.6).
- The frozen source-binding SHA-256 is
  `e69ca282c046e43325ee2ae1f0b53f76bf2ee017771423ace1e866c646bf21a8`;
  the qualified-runtime receipt SHA-256 is
  `bc743876f470bca0e2fb9c8df73bd4f07f2d61f5de8600b5b2150e7cb8b4386d`.
- The canonical integrity manifest passed 10/10. Both final invocations failed
  closed, and neither stage 141 nor stage 142 created an output directory.

Stage F2 decision:
`PASS_STAGE_F2_INTEGRITY_HARDENING_AND_REBIND__HOLD_POST_COMMIT_EXACT_CODE_GO`.

## Stage G completed

Both authors approved the exact synchronized F2 baseline and separately
authorized outer stage 141 and truth stage 142. The issued GO bound Git commit
`ca95aa656e73694e80c8030e42608f6712099404`, source-binding SHA-256
`e69ca282c046e43325ee2ae1f0b53f76bf2ee017771423ace1e866c646bf21a8`
and runtime-receipt SHA-256
`bc743876f470bca0e2fb9c8df73bd4f07f2d61f5de8600b5b2150e7cb8b4386d`.

- Stage 141 completed 40/40 scenarios, 160,000/160,000 attempts and 1,600
  sealed chunks with zero numerical failures. Resume verification reused all
  chunks without changing any summary hash.
- Stage 142 completed 15/15 shifted-DGP truth scenarios and 240 sealed
  checkpoints. All precision and independent score checks passed; maximum
  `MCSE / typical SE` was 0.007842.
- The result-blind adjudicator returned 30/30 applicable PASS and reported all
  10 mandatory boundaries. A second full adjudication was byte-identical.
- The nearest bias boundary was `C4_X3` at 0.098054 versus 0.10. The largest
  coverage Wilson upper bound was 0.972152 in `C0_X3` versus 0.975. These are
  passing but must remain explicit near-boundary results.
- The result validates only the single `delta_profile` OLS/HC3/t(64) procedure
  in the frozen synthetic domain. It does not validate the other historical
  targets, establish causal mediation or automatically unlock real outcomes.

Stage G decision:
`G2C_SYNTHETIC_PASS__SEPARATE_REAL_OUTCOME_REVIEW_REQUIRED`.

## Stage H completed

Stage H remained fully effect blind and bound the exact canonical real-input
objects by SHA-256. The common support remains 68 unique donors with 31 controls
and 37 managed-SLE donors. The four-column design has rank 4, maximum
outcome-blind hat leverage 0.104567 and no missing design values. All 340
donor-bin units are present, minimum support is 30 cells and every full captured
library is positive.

The real 68 x 4 design and 68 x 5 cell template are exactly identical to the
synthetic calibration anchor. The regularized 12-gene-plus-background
probabilities are identical, and captured-UMI-per-cell rates agree to a maximum
absolute difference of `4.55e-13`. Thus no observed support, leverage, library
or mixture-geometry extrapolation was detected. Aggregate inputs still cannot
prove that the unknown real latent overdispersion, capture correlation or label
contamination mechanism equals a simulated DGP.

The project froze one real estimand and one write-once result schema only. The
unsigned Stage I template is fail-closed, and its rejection was tested before
response construction. Stage H loaded no real response and fit no disease
coefficient.

Stage H decision:
`PASS_STAGE_H_EFFECT_BLIND_APPLICABILITY__HOLD_STAGE_I_AUTHOR_SIGNOFF`.

## Stage I author-decision preflight prepared

The project now has a separate effect-firewalled preflight for the post-Stage-H
author decision. It requires a clean synchronized `main`, rechecks the complete
Stage H integrity manifest, exact input and execution-code hashes, and the Stage
F2 qualified Windows runtime. It writes only an unsigned, commit-bound local
decision packet under the ignored `_software_tests` tree.

The unsigned draft is actively passed to the real Stage I runner and must fail
before response construction and before a result directory is created. A
general instruction to continue is not substituted for explicit approval by
both Zhi Chen and Teng Qi. No real response or coefficient has been accessed.

Current decision:
`READY_FOR_EXPLICIT_TWO_AUTHOR_DECISION__STAGE_I_NOT_AUTHORIZED`.

## Stage I completed once

Zhi Chen and Teng Qi jointly approved all six frozen conditions and authorized
one write-once execution bound to commit
`b413ce09fae520eef0a7a781ee71ddece7606be0`. The exact Stage I runner produced
one result and receipt; it exported no donor-level response and fitted no other
target or external outcome.

The `delta_profile` estimate was 0.034925002 T0 score units with HC3 standard
error 0.011558535, t(64) 95% CI 0.011834175 to 0.058015829 and two-sided
P=0.003612459. Under the frozen sign convention, the managed-SLE versus control
association is greater under the fixed-profile rule than under pooled counts.

This is measurement/mixing-rule sensitivity evidence. It is not a mediation
proportion, causal cell-intrinsic effect, proof of a latent mechanism or
validation of other historical targets. Automatic manuscript, external-outcome,
WP4 and submission unlocks remain false.

Stage I decision:
`PASS_STAGE_I_WRITE_ONCE_EXECUTION__POSITIVE_DELTA_PROFILE_ASSOCIATION__HOLD_AUTOMATIC_UNLOCK`.

On 11 October 2026, Zhi Chen and Teng Qi explicitly jointly reconfirmed all six
conditions in the Stage I template. This is an archival post-execution
reconfirmation bound to the original template, executed GO, result and
integrity-manifest hashes. It does not authorize a second Stage I execution and
does not change the current Stage L gate.

## Stage J-K evidence reconciliation and limited integration

Independent rechecking established that RP v3 WP1 and RP v4 Stage I use the
same 68 donors, outcome definition, four-column design and `delta_profile`
estimand. Their point estimates agree to approximately `6.94e-18`. Stage I is
therefore an uncertainty re-estimation for the existing measurement-rule
contrast, not an independent positive finding.

The author-approved limited integration adds exact Methods and Discussion
boundaries, Supplementary Table S10 and two full-precision Source Data rows.
Figures 1-5 and Supplementary Figures S1-S10 are unchanged. WPS and
LibreOffice both produced 32 manuscript pages and 16 Supplementary pages;
DOCX accessibility is 0 high / 0 medium / 0 low for both documents.

Stage K decision:
`PASS_STAGE_K_LIMITED_SOURCE_INTEGRATION__HOLD_SUBMISSION_AND_EXTERNAL_OUTCOMES`.

## Stage L external-cohort unique-question gate

Official GEO MINiML was independently reconstructed without reading expression
outcomes. GSE262846 contains 88 RNA libraries from 45 patient IDs, including
43 rN/T1T2-paired patients. The prospective primary set is 26 paired SLE
patients: 12 active and 14 inactive. The only differentiated primary question
is whether the patient-level T1T2-minus-rN IFN/ISG score differs by activity.

GSE263716 contains 62 ATAC libraries from 43 patient IDs, but only 36 IDs
overlap the RNA series and patients 1655 and 3651 have discordant deposited
SLEDAI values. Same-visit multi-omic confirmation is therefore not established.

The deposited RNA matrix is RPKM rather than integer counts. No expression
matrix was read, no SRA payload was downloaded and no activity effect was
fitted. Raw reconstruction remains blocked pending a separate authorization,
sample-to-run reconciliation, frozen GRCh38/GENCODE configuration and
small-sample operating-characteristic qualification.

Stage L decision:
`PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION`.

## Current authorization

Allowed:

- preserve and independently review the completed Stage G through Stage L
  evidence;
- use the Stage K integrated documents as a scientific candidate while
  submission remains on hold;
- prepare a disease-blind Stage M raw-count reconstruction contract without
  downloading data or fitting outcomes.

Not allowed:

- rerun, preview or alter the completed Stage I coefficient;
- reopen or selectively rerun the completed stage-141/142 streams;
- change the estimand, t(64) method, DGP registry, thresholds or seed base;
- fit or inspect any additional real WP2 effect;
- fit new-cohort diagnosis/activity effects;
- introduce S2 by outcome tuning;
- promote Stage I as independent replication or rewrite the figures around it;
- download the 233.209 GB GSE262846 SRA payload without separate authorization;
- read the external expression matrix or fit diagnosis/activity outcomes;
- rebuild a submission package, GitHub Release or Zenodo version.

## Next gate

`RPV4_STAGE_M__RAW_RECONSTRUCTION_AUTHORIZATION_AND_DISEASE_BLIND_COUNT_PIPELINE_FREEZE`

Stage I is complete and must not be rerun. Stage K integrated it only as a
bounded uncertainty-method sensitivity, and Stage L froze the external
patient-paired question without outcomes. Stage M must bind raw-run identity,
reference/annotation versions, count reconstruction, storage, checksums and a
prospective small-sample simulation before any raw download or activity model.
External outcomes, WP4 and submission remain unauthorized.

## Canonical evidence

- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md)
- [`00_project_management/action_record_2026-10-10_rp_v4_stageA_authority_feasibility_freeze.md`](action_record_2026-10-10_rp_v4_stageA_authority_feasibility_freeze.md)
- [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/11_RPV4_STAGE_C_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/11_RPV4_STAGE_C_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/12_RPV4_STAGE_C_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/12_RPV4_STAGE_C_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/13_STAGE_D_TECHNICAL_PILOT_PROTOCOL.md`](../phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/13_STAGE_D_TECHNICAL_PILOT_PROTOCOL.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/09_STAGE_D_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/09_STAGE_D_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/11_STAGE_D_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/11_STAGE_D_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/12_STAGE_E_PREFLIGHT_CONTRACT.md`](../phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/12_STAGE_E_PREFLIGHT_CONTRACT.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/07_STAGE_E2_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/07_STAGE_E2_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/09_STAGE_E2_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/09_STAGE_E2_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/10_STAGE_F_GO_NO_GO_CONTRACT.md`](../phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/10_STAGE_F_GO_NO_GO_CONTRACT.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/07_STAGE_F2_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/07_STAGE_F2_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/09_STAGE_F2_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/09_STAGE_F2_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/10_STAGE_G_GO_NO_GO_CONTRACT.md`](../phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/10_STAGE_G_GO_NO_GO_CONTRACT.md)
- [`00_project_management/action_record_2026-10-11_rp_v4_stageF2_integrity_hardening.md`](action_record_2026-10-11_rp_v4_stageF2_integrity_hardening.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/11_FINAL_SYNTHETIC_GATE.json`](../phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/11_FINAL_SYNTHETIC_GATE.json)
- [`phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/14_STAGE_G_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/14_STAGE_G_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/15_STAGE_H_EFFECT_BLIND_PREFLIGHT_CONTRACT.md`](../phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation/15_STAGE_H_EFFECT_BLIND_PREFLIGHT_CONTRACT.md)
- [`00_project_management/action_record_2026-10-11_rp_v4_stageG_final_synthetic_validation.md`](action_record_2026-10-11_rp_v4_stageG_final_synthetic_validation.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/08_STAGE_H_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/08_STAGE_H_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/09_STAGE_H_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/09_STAGE_H_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/10_STAGE_I_EXECUTION_CONTRACT.md`](../phase17_v7/rp_v4_redesign/20261011_stageH_effect_blind_prefit/10_STAGE_I_EXECUTION_CONTRACT.md)
- [`00_project_management/action_record_2026-10-11_rp_v4_stageH_effect_blind_prefit.md`](action_record_2026-10-11_rp_v4_stageH_effect_blind_prefit.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/04_STAGE_I_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/04_STAGE_I_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/05_STAGE_I_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageI_single_real_delta_profile/05_STAGE_I_ADVISOR_REVIEW.md)
- [`00_project_management/action_record_2026-10-11_rp_v4_stageI_single_real_delta_profile.md`](action_record_2026-10-11_rp_v4_stageI_single_real_delta_profile.md)
- [`00_project_management/rp_v4_stageI_author_reconfirmation_2026-10-11.json`](rp_v4_stageI_author_reconfirmation_2026-10-11.json)
- [`00_project_management/action_record_2026-10-11_rp_v4_stageI_author_reconfirmation.md`](action_record_2026-10-11_rp_v4_stageI_author_reconfirmation.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/03_STAGE_K_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/03_STAGE_K_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/06_DOCUMENT_QA.json`](../phase17_v7/rp_v4_redesign/20261011_stageK_limited_integration/06_DOCUMENT_QA.json)
- [`phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/09_PROSPECTIVE_ANALYSIS_CONTRACT.md`](../phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/09_PROSPECTIVE_ANALYSIS_CONTRACT.md)
- [`phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/11_STAGE_L_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261011_stageL_external_cohort_gate/11_STAGE_L_ADVISOR_REVIEW.md)
- [`00_project_management/action_record_2026-10-11_rp_v4_stageK_limited_integration_stageL_external_gate.md`](action_record_2026-10-11_rp_v4_stageK_limited_integration_stageL_external_gate.md)
