# WP1 pre-effect execution addendum — review draft v0.1

Date: 2026-10-10
Status: **REVIEW_DRAFT_NOT_A_REPLACEMENT_FOR_FROZEN_STAGE0B**
No new disease coefficients have been inspected in preparing this addendum.

## Existing authority preserved

RP v3, the original Stage0B artifacts and `17_WP1_ANNOTATION_SENSITIVITY_EXECUTION_CONTRACT.md` remain unchanged. All new decisions require an additive, dated record before the first coefficient is fitted. Historical G0/G1 receipts are not erased. WP4 and submission remain HOLD.

## Decisions that must be explicitly resolved

### D01 — A1 estimand and operator [UNRESOLVED]

A1 uses an A0 B_CONV continuous-axis bin scaffold and a fixed pi_ref. This changes aggregation/standardization as well as representation. It is not a one-factor manipulation of annotation alone.

Select and freeze one operator with its interpretation; do not select using beta or p values:

- **Score-space estimand:** `s_i = sum_k pi_ref_k * mean_g[(log2(CPM_ikg + 0.5)-mu0_g)/sd0_g]`. This is a fixed-composition weighted bin-score association. Its difference from A0 is a joint representation/aggregation contrast. It is not automatically RP-v3 beta_S.
- **Expression-reconstruction estimand:** predict or otherwise explicitly define common-depth linear state expression, combine using pi_ref, then apply the identical T0. Define measurement units and the state-model fit. Bootstrap must include any model fitted to the resampled donors. This option is not implemented by merely averaging logged scores.

Do not call either association causal, cell intrinsic, an exact mediated fraction, or an equivalence result. If the scientific aim remains pure annotation sensitivity, revise the target definition before inference rather than hiding this joint intervention under a variable name.

### D02 — A2 semantics [VERIFIED FACT, LABEL CLARIFICATION NEEDED]

The frozen historical feature list excludes all `is_strong_isg`-flagged genes, but retains LY6E from the 12-gene IFN score. Keep this A2 hash unchanged. Describe it as historical strong-ISG-list-excluded representation, not full IFN12-excluded or statistically IFN-independent.

A fully IFN12-excluded variant, if scientifically required, is a separately approved, pre-effect branch with its own feature hash and background denominator; it must not overwrite this A2 or be chosen by disease effect.

### D03 — common-support population [PARTIALLY VERIFIED]

Archived A1 support is 89 donors × 5 bins. All-five-bin >=30 support gives 68 donors before A2 eligibility. Five positive pi_ref weights are fixed.

For an observed-bin complete-case analysis, use the common intersection for all three branches. No donor-specific renormalization of pi_ref, filling a missing bin with zero, or outcome-adaptive merging. Report all exclusions and both biological arms by ID-linked design. Explicitly state whether the historical >=50 B_CONV support applies unchanged to A2; the exporter reports this as a candidate diagnostic, not as a newly passed gate.

Freeze a shared complete-case analysis and its covariate design before fitting. A0 on the original 89 units is not the comparator in a delta against a reduced A1 population. Keep the original 43-control T0 reference and original pi_ref even when the paired set shrinks; the analysis conditions on them.

### D04 — mapping and provenance [EXECUTION REQUIRED]

Match exact source_cell_index universes and technical IDs. Map A2 clusters using A0 broad B_CONV/B_ASC cell overlap only. Do not assign A2 cluster 3 by matching its numeric label. Record confusion, purity, recall and coverage as agreement to A0, not biological accuracy.

Freeze the mapping before loading the disease design. Ties, class collapse or source disagreement require review, not an effect-based fallback. Do not add a new numerical purity threshold after observing beta.

### D05 — bootstrap mechanics [DETAILS TO FREEZE]

Retain 2,000 paired donor-clustered replicates, one shared draw for all branches, original fixed covariates, and the >1% fit-failure stopping rule.

Before inference record: seed; ordinary or case/control-stratified cluster sampling; percentile/basic/other CI construction; rank/finite/arm-presence failure criteria; duplicate-cluster handling; minimum effective-donor reporting. Every attempted replicate counts in the denominator; do not silently replenish failed draws.

State explicitly whether the result conditions on A2 mapping, A1 cutpoints, pi_ref, T0 and the support set (recommended reading of the current frozen-object design). This is not full end-to-end representation uncertainty or unconditional reference-parameter uncertainty. No equivalence margin is authorized. Marginal 95% intervals do not create a simultaneous two-delta testing claim.

### D06 — simulation and data identity [BOUNDARY RETAINED]

The five-scenario, 400-replicate technical summary does not unlock G2. Full simulation must use the finally chosen estimand/operator and support/missingness procedure; nonlinear score truth cannot simply be taken from an additive count/mean coefficient.

Use 15_STAGE0B_INTEGRITY_MANIFEST for current canonical bytes. Preserve 01_STAGE0B_INPUT_AND_CONTRACT_MANIFEST as a stale/historical inventory unless its time-specific role is demonstrated. New portable-export manifests exclude themselves; no recursive hash promises.

## Completion record to fill before effects

```
A1_operator_and_target: UNRESOLVED
A1_delta_semantic_label: UNRESOLVED
A2_feature_scope: historical strong-list exclusion; LY6E retained
A2_overlap_mapping_hash: PENDING
A2_support_rule: TO_BE_EXPLICITLY_RECORDED
shared_donor_ID_hash: PENDING
shared_covariate_matrix_hash_and_rank: PENDING
T0_reference_hash: 0244242AB31441F7D46305A5E69AD77714FBF2A2833EE09D16CF893F3D9E610F
pi_ref_hash: D8492404E9EA19F5D6735A2995A4E52B0ED7A867B7B1A0577D0237BBDE131BB4
bootstrap_seed_sampling_CI_failure_rules: PENDING
raw_or_sufficient_count_export_hash: PENDING
first_effect_fit_time: NOT_STARTED
WP4: HOLD_CONDITIONAL
SUBMISSION: HOLD
```

This document deliberately leaves unresolved choices visible. It does not invent agreement, preregistration, equivalence margins or a completed WP1 result.
