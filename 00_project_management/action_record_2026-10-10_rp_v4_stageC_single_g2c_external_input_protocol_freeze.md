# RP v4 Stage C single-G2C and external-input protocol freeze action record

**Date:** 2026-10-10  
**Workspace:** `H:\cuhk-2025fALL\6013RP-wyf`  
**Input Git HEAD:** `16f15399f090f0631f5c9dd33d2adf015bd0b0b4`  
**Input remote baseline:** `origin/main=f2eca1abec44afb73688823f57e42ab78b971203`  
**Outcome access:** locked throughout

## 1. Request and scientific boundary

The user instructed the project to continue under Research Plan v4. This round
implemented `RPV4_STAGE_C__SINGLE_G2C_AND_EXTERNAL_INPUT_PROTOCOL_FREEZE`.
The work was restricted to historical synthetic-development evidence, protocol
selection, official raw-input metadata and outcome-blind measurement rules.

The following were not run or changed:

- no final G2C validation;
- no real WP2 effect or interval;
- no external diagnosis, activity, treatment or score-direction model;
- no S2 score fitting or outcome-driven score selection;
- no manuscript, figure, submission package, Release or Zenodo change;
- no revision of any RP v3 G2/G2B HOLD.

## 2. Estimand decision

Exactly one primary estimand was selected: `delta_profile`.

It is the disease-coefficient difference between:

1. the frozen fixed-profile mixture score; and
2. the pooled-count score.

It is an association difference between two observed measurement/mixing rules.
It is not a mediated proportion, a pure cell-composition effect, an absolute-RNA
effect or a cell-intrinsic causal effect.

The selection was made because `delta_profile` passed all 15 historical G2B
point-bias gates while nine applicable cells failed interval coverage. This
separates an interval-calibration question from point-estimator bias.
`delta_cellref` was not selected because its three historical failures include
both undercoverage and a point-bias failure.

## 3. Historical-development mechanism diagnosis

The project replayed all 2,000 outer attempts for each of the 25 exposed G2B
scenarios using the unchanged stage-121 generator. For each scenario, eight
fixed attempt IDs also recomputed the 2,000-draw bootstrap-t internals. This is
development evidence and cannot count as forward confirmation.

Key findings:

| Diagnostic | Result |
|---|---:|
| Applicable historical scenarios | 15 |
| Single-candidate development PASS | 15/15 |
| Minimum bootstrap-SE p01/median | 0.531997 |
| Maximum absolute t-star skew | 0.637169 |
| Maximum absolute t-star excess kurtosis | 0.772025 |
| Maximum point leverage | 0.104567 |
| Maximum bootstrap leverage | 0.210382 |
| Maximum inner failures | 0 |
| Minimum beta_B/profile bootstrap correlation | 0.992466 |
| Maximum delta algebra error | `4.57e-15` |

The direct candidate's development coverage ranged from 0.9515 to 0.9660 in the
15 applicable cells. Every Wilson interval remained inside the frozen
`[0.925, 0.975]` gate, and every bias gate passed.

The observed evidence does not support `NEAR_ZERO_STUDENTIZER`, a non-smooth
delta or gross donor leverage as the dominant failure mode. The old G2B misses
are more consistent with mild finite-sample calibration interacting with DGP
sensitivity. This interpretation still requires independent shifted-DGP
validation.

## 4. Frozen G2C method

The only primary method entering later final validation is:

> Direct donor-level OLS of the `delta_profile` response, HC3 influence-function
> variance and a two-sided Student-t interval with `df=68-4=64`.

No fallback method is registered. Failure closes the decomposition branch and
produces `G2C_HOLD__WP2_DECOMPOSITION_NOT_CLAIMABLE`; RP v4 permits no G2D.

The method choice is consistent with the small-sample motivation for HC3 in
MacKinnon and White (1985; DOI 10.1016/0304-4076(85)90158-7) and Long and Ervin
(2000; DOI 10.1080/00031305.2000.10474549). Historical 15/15 performance is a
selection/development result, not a success claim.

## 5. Independent final-simulation contract

The final contract is frozen but not authorized for execution:

- seed base: `2026101004`;
- outer stage: 141;
- truth stage: 142;
- 25 old-comparable scenarios;
- 15 prespecified shifted scenarios;
- 4,000 outer attempts per scenario;
- 160,000 registered outer attempts total;
- no attempt replenishment;
- no inner bootstrap or alternative-method search;
- 30 scenarios in the applicable conjunction;
- 10 mandatory boundary scenarios.

The three shifted DGP families are:

1. gamma-Poisson category-level overdispersion;
2. correlated donor/bin capture heterogeneity; and
3. nonadjacent label contamination.

Truth precision, normalized bias, Wilson coverage, exact-null type-I,
support-stop and numerical-failure gates are frozen before the first final
result. The final random stream has not been opened.

## 6. Official external raw-input audit

Official NCBI SRA RunInfo was downloaded from the BioProject accessions and
stored locally under the Git-ignored `source_metadata/` directory.

| Accession | BioProject | Runs | Experiments | Bases | SRA size | RunInfo SHA-256 |
|---|---|---:|---:|---:|---:|---|
| GSE262846 | PRJNA1093470 | 176 | 88 | 752.70 G | 233.21 GB | `25f5a677e283d3f3dedf957699c8c56abfdb6e41aafc09b2fb36f054fe441ad0` |
| GSE118254 | PRJNA484963 | 85 | 83 | 174.96 G | 64.37 GB | `5a6b62806ffe2a56a3d6d352f623d091afda320314d49faef19d8bc6a77dc47f` |

Both studies are paired-end RNA-seq and are technically reconstructable from
raw SRA. The combined compressed SRA payload is approximately 297.57 GB and the
combined sequence volume is 927.66 G bases. A minimum 2.5 TB scratch allocation
is recommended for uncompressed FASTQ, alignment scratch, counts and hashes.

The public metadata cannot exclude shared people across the two studies because
their de-identification namespaces differ and investigator lineage overlaps.
The protocol therefore treats them as potentially donor-overlapping. They may
not be pooled as independent donors or counted as two independent confirmations.
GSE262846 remains the primary clinical-activity candidate; GSE118254 is limited
to a technical measurement bridge until stronger provenance exists.

No large SRA download was started in this round.

## 7. Measurement contract

- `S0=T_frozen` remains the primary score with its unchanged 12 genes,
  full-library CPM denominator, `log2(CPM+0.5)` transform and 43-control
  discovery reference.
- `S1=T_rank` remains a technical sensitivity using the frozen 18,873-symbol
  rank background.
- An annotated gene absent from the count reference is a technical failure, not
  a zero. A genuine zero count remains zero and uses the frozen pseudocount.
- S2 is abandoned/not admitted because no unique outcome-blind formula,
  denominator and missing-feature rule was justified.

## 8. Generated artifacts

Canonical Stage C directory:

`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/`

It contains:

- exposed-stream studentizer diagnostics;
- single-candidate development performance;
- diagnostic summary;
- estimand/method contract;
- final 40-scenario DGP registry;
- seed/compute contract;
- official external raw-input manifest;
- raw reconstruction/provenance contract;
- S0/S1 measurement contract;
- 16-item gate checklist;
- machine-readable Stage C decision;
- advisor review;
- Stage D technical-pilot protocol; and
- SHA-256 integrity manifest.

New executable sources:

- `audit_tools/rp_v4_g2c_hc3t.py`
- `audit_tools/rp_v4_stageC_01_development_diagnostic.py`
- `audit_tools/rp_v4_stageC_02_freeze.py`
- `audit_tools/test_rp_v4_g2c.py`

The root README and `RP_V4_REDESIGN_STATUS.md` were updated to make Stage C the
active authority without deleting historical manuscript/release baselines.

## 9. Verification

- Stage C checklist: 16/16 PASS.
- Stage C focused tests: 6/6 PASS.
- C9 dependency-sensitive tests under `sle-bcell`: 9/9 PASS.
- Full `audit_tools/test_*.py` suite under the `sle-bcell` environment: PASS
  (298 tests discovered in the full suite).
- `git diff --check`: PASS.
- Stage C integrity manifest: 13/13 canonical payloads recorded.
- Outcome models fitted: 0.

The system Python lacks `anndata`; therefore the complete regression suite was
correctly rerun with `C:\ProgramData\miniforge3\envs\sle-bcell\python.exe`.
This is an environment distinction, not a project test failure.

## 10. Gate decision

`PASS_RPV4_STAGE_C_PROTOCOL_FREEZE__AUTHOR_SIGNOFF_REQUIRED_BEFORE_FINAL`

This decision means the protocol is coherent enough to implement. It does not
mean G2C works in independent simulations, and it grants no access to real
outcomes.

## 11. Next-stage objective

Proceed to:

`RPV4_STAGE_D__G2C_IMPLEMENTATION_AND_EXTERNAL_RAW_INTAKE_TECHNICAL_PILOT`

Stage D should:

1. implement and unit-test the three shifted generators and independent truth
   engine without changing the frozen method;
2. run only a small non-adjudicative technical grid for deterministic replay,
   support accounting, checkpointing and runtime benchmarking;
3. generate resumable SRA download/count scripts and a hash-controlled runbook;
4. verify S0/S1 feature mapping on count-only objects with outcomes absent; and
5. require exact author sign-off before final G2C or any large raw download.

Final G2C, real WP2 effects and external outcome analysis remain locked.

## 12. Git record and remote synchronization

- Stage C implementation/results commit: `fe9e114` (`Freeze RP v4 Stage C protocol`).
- Local ancestry remains linear: `f2eca1a -> 8cba831 -> 16f1539 -> fe9e114`.
- The first normal `git push origin main` could not reach GitHub on port 443
  after 21,080 ms and stopped before authentication or object transfer.
- A second normal retry succeeded and fast-forwarded remote `main` from
  `f2eca1a` through the Stage C implementation and synchronization record.
- No force push, history rewrite, API reconstruction or alternate remote was
  used. Any later status-only commit remains ordinary linear history and does
  not alter the scientific artifacts or gate decision.
