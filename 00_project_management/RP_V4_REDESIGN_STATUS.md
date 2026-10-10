# RP v4 scientific redesign status

**Effective date:** 2026-10-11

**Overall state:** `ACTIVE_RP_V4_SCIENTIFIC_REDESIGN`

**Submission state:** `HOLD`

**Current gate:** `PASS_RPV4_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING__HOLD_EXACT_CODE_GO`

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

## Current authorization

Allowed:

- review the committed Stage E2 code and source-binding manifest;
- prepare a new exact-code GO receipt only after the commit hash exists;
- exercise checkpoint, resume, overwrite refusal and fail-closed adjudication
  on non-final technical streams;
- estimate final compute/storage requirements without executing the final grid.

Not allowed:

- run the 160,000-attempt final G2C validation before a new exact-code
  `GO_FOR_FULL_SYNTHETIC_G2C` receipt binds both authors, the committed Git HEAD
  and the Stage E2 source manifest;
- consume stage-141 or stage-142 random streams during preflight;
- change the estimand, t(64) method, DGP registry, thresholds or seed base;
- fit or inspect real WP2 effects;
- fit new-cohort diagnosis/activity effects;
- introduce S2 by outcome tuning;
- rewrite the manuscript or figures around RP v4;
- rebuild a submission package, GitHub Release or Zenodo version.

## Next gate

`RPV4_STAGE_F__POST_COMMIT_EXACT_CODE_GO_REVIEW`

Stage F must bind both authors to the exact synchronized Git commit and the
existing source-binding manifest. Only a newly issued receipt may authorize
stage 141 and stage 142. The current template remains false. Large data download
and all real outcomes still require separate later approval.

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
