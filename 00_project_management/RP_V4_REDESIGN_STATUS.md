# RP v4 scientific redesign status

**Effective date:** 2026-10-10

**Overall state:** `ACTIVE_RP_V4_SCIENTIFIC_REDESIGN`

**Submission state:** `HOLD`

**Current gate:** `PASS_RPV4_STAGE_C_PROTOCOL_FREEZE__AUTHOR_SIGNOFF_REQUIRED_BEFORE_FINAL`

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

## Current authorization

Allowed:

- implement and unit-test the frozen HC3-t wrapper, shifted DGP generator and
  independent truth engine;
- run a small non-adjudicative technical pilot for deterministic replay,
  checkpointing and resource benchmarking;
- generate resumable SRA download/count scripts without starting the large
  download;
- verify S0/S1 feature mapping in count-only, outcome-free technical objects.

Not allowed:

- run the 160,000-attempt final G2C validation before exact protocol sign-off;
- change the estimand, t(64) method, DGP registry, thresholds or seed base;
- fit or inspect real WP2 effects;
- fit new-cohort diagnosis/activity effects;
- introduce S2 by outcome tuning;
- rewrite the manuscript or figures around RP v4;
- rebuild a submission package, GitHub Release or Zenodo version.

## Next gate

`RPV4_STAGE_D__G2C_IMPLEMENTATION_AND_EXTERNAL_RAW_INTAKE_TECHNICAL_PILOT`

Stage D must implement only the frozen contracts, qualify independent shifted
truths, demonstrate deterministic checkpoint/replay and produce a resumable raw
intake runbook. It must not inspect final performance or real outcomes. Exact
author approval remains required before any final G2C execution or large data
download.

## Canonical evidence

- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md)
- [`00_project_management/action_record_2026-10-10_rp_v4_stageA_authority_feasibility_freeze.md`](action_record_2026-10-10_rp_v4_stageA_authority_feasibility_freeze.md)
- [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/11_RPV4_STAGE_C_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/11_RPV4_STAGE_C_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/12_RPV4_STAGE_C_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/12_RPV4_STAGE_C_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/13_STAGE_D_TECHNICAL_PILOT_PROTOCOL.md`](../phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/13_STAGE_D_TECHNICAL_PILOT_PROTOCOL.md)
