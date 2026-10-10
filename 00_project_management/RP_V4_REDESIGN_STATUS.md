# RP v4 scientific redesign status

**Effective date:** 2026-10-10

**Overall state:** `ACTIVE_RP_V4_SCIENTIFIC_REDESIGN`

**Submission state:** `HOLD`

**Current gate:** `PASS_RPV4_STAGE_A_AND_V4B_HISTORICAL_DIAGNOSIS__HOLD_G2C_AND_NEW_COHORT_OUTCOMES`

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

## Current authorization

Allowed:

- freeze one primary G2C estimand/method and at most one prespecified fallback;
- define independent final-simulation random streams, DGP shifts, thresholds and
  compute budget;
- resolve raw-count compatibility and donor provenance for GSE262846/GSE118254;
- freeze result-blind S0/S1 technical handling.

Not allowed:

- run final G2C validation;
- fit or inspect real WP2 effects;
- fit new-cohort diagnosis/activity effects;
- introduce S2 by outcome tuning;
- rewrite the manuscript or figures around RP v4;
- rebuild a submission package, GitHub Release or Zenodo version.

## Next gate

`RPV4_STAGE_C__SINGLE_G2C_AND_EXTERNAL_INPUT_PROTOCOL_FREEZE`

The next gate must decide one estimand and one primary method before final
simulation, separate interval calibration from point-estimator bias, and issue
a fail-closed raw-count/provenance decision for each external candidate. If the
single frozen G2C strategy fails, the decomposition branch closes; RP v4 does not
permit a G2D rescue.

## Canonical evidence

- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json)
- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md)
- [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md`](../phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md)
- [`00_project_management/action_record_2026-10-10_rp_v4_stageA_authority_feasibility_freeze.md`](action_record_2026-10-10_rp_v4_stageA_authority_feasibility_freeze.md)
