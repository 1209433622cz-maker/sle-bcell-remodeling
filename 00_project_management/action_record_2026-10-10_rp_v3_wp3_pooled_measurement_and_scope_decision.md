# RP v3 WP3 pooled measurement execution and scope decision

**Date:** 2026-10-10

**Workspace:** `H:\cuhk-2025fALL\6013RP-wyf`

**Parent commit:** `f2eca1abec44afb73688823f57e42ab78b971203`

## Objective

Continue Research Plan v3 from the effect-free WP3 prefit, independently audit
the received pooled-measurement review, rerun the permitted diagnostics from
canonical inputs, preserve the no-outcome boundary, and determine the next
scientific stage.

## External evidence intake

Reviewed archive:
`SLE_RPv3_WP3_PooledMeasurement_IndependentReview_20261010.zip`

- archive bytes: `11,467,377`;
- SHA-256:
  `d50a6babb834c567d96c01e9205a7c354264e44f2b3f7f567844eb19ae2ab3e1`;
- entries: 95; uncompressed bytes: 13,027,987;
- path traversal: none;
- duplicate archive paths: none;
- internal manifest: 94/94 payloads PASS;
- bundled tests: 31/31 PASS.

The archive was extracted only under the Git-ignored local evidence directory
`phase17_v7/rp_v3_redesign/20261010_wp3_pooled_external_candidate/`.

## Independent review of the external candidate

All 16 packaged source objects matched the current workspace by size and
SHA-256. The candidate was replayed with `D:\bioinfor\python.exe`; its 22 real
checks and 4,389 independent comparisons passed. Nine of eleven output files
were cross-platform byte-identical. The other two had a maximum scientific
numeric difference of `8.88e-16`, consistent with the candidate's explicit
statement that only same-runtime byte identity was claimed.

The candidate's disclosed first-run incident was retained rather than erased:
the initial real execution computed scores transiently, stopped before writing
results on an exact source-parity mismatch of at most `3.33e-16`, then restored
the frozen row-wise reduction. No threshold was relaxed and donor ranks were
unchanged. This is a source-parity repair, not a prospective pre-result freeze.

## Project-side implementation

Added:

- `audit_tools/rp_v3_wp3_02_pooled_measurement.py`;
- `audit_tools/rp_v3_wp3_03_independent_recompute.py`;
- `audit_tools/test_rp_v3_wp3_pooled_measurement.py`;
- `audit_tools/run_rp_v3_wp3_pooled_measurement.ps1`.

The project-side pipeline reads current canonical files directly and imports
the complete frozen Stage 0B scoring module. It does not depend on the external
candidate package. The complete operator SHA-256 is
`13a5ea7bf395968cd95317e9ce49344290e22c41bec8d2d4068fc5b221676853`.

Analytical outputs use neutral keys `D001`-`D054`. No sample ID, donor name,
cohort, disease group, age, treatment or activity field is emitted. The pipeline
contains no disease model, P value, confidence interval, ROC or transform-
selection rule.

## Verification performed

- 13/13 project boundary tests PASS;
- 25/25 real canonical checks PASS;
- 4,389/4,389 independent scalar checks PASS;
- maximum independent absolute error: `1.776e-15` (`1e-11` tolerance);
- second-directory project replay: 13/13 files byte-identical;
- prohibited-field scan across analytical outputs: 0 hits;
- canonical versus external candidate: all table shapes, text and reported
  values matched, with only a maximum `8.88e-16` difference in one detailed
  floating-point table.

## Scientific findings

- `T_frozen` versus `T_rank` pooled Spearman: `0.9857442348`;
- maximum/mean between-transform rank displacement: `6` / `2.111111`;
- leave-one-gene-out Spearman range: `0.9958833619-0.9991614256`;
- maximum leave-one-gene-out rank displacement: `6` (`OAS2` omission);
- lowest leave-one-gene-out correlation: `0.9958833619` (`LY6E` omission);
- pseudobulk detection: IFIT1 47/54, IFIT3 52/54, OAS2 53/54, all other frozen
  genes 54/54;
- fixed rank-background share of full measured library: 95.09%-96.69%.

The permitted pooled diagnostic therefore adds a real but narrow measurement
finding: donor ordering is stable across the two frozen transforms and all 12
single-gene omission branches. It does not test a disease effect.

## Decision and boundaries

Accepted gate:
`PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION`.

Still false or held:

- `WP2_REAL_EFFECT_UNLOCK=false`;
- `WP3_OUTCOME_EXECUTION_AUTHORIZED=false`;
- `WP4=HOLD_CONDITIONAL`;
- manuscript replacement, submission, Release and Zenodo remain HOLD;
- no cross-platform, clinical, external-disease or causal validation claim.

## Next-stage judgment

The limited WP3 measurement question is complete. Another prefit, interval,
transform or disease-analysis loop would add post-hoc risk without a registered
scientific question. The recommended next stage is the author-level gate:

`RP_V3_AUTHOR_SCOPE_CLOSURE_DECISION`

At that gate, the authors should decide whether to close RP v3 as a completed
methodological audit and whether the pooled measurement fact remains provenance
only or merits a narrowly bounded manuscript/supplement integration review.
No manuscript object is changed in this round.

## Repository delivery status

All canonical code, results, governance documents and this action record were
committed locally on `main`. Four HTTPS push attempts were made, including an
HTTP/1.1 retry and a delayed retry. The host could not reach `github.com:443`;
the failures occurred before authentication and were reported as connection
reset or connection timeout. The local branch is therefore one commit ahead of
`origin/main`. No alternate GitHub API commit was created because that would
produce a second commit identity and split the local and remote histories.

When network access returns, the exact remaining delivery command is:

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"
git push origin main
```
