# RP v3 scientific redesign status

**Effective date:** 2026-10-10
**Overall state:** `ACTIVE_RP_V3_SCIENTIFIC_REDESIGN`
**Submission state:** `HOLD`
**Current gate:** `PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION`

## Completed gates

| Stage | Decision | Principal evidence |
|---|---|---|
| Stage 0 input recovery | PASS | 21/21 inputs, raw-count and unit checks, GSE135779 archive verification |
| Stage 0 initial protocol gate | HOLD then resolved in Stage 0B | Open score, support, composition and simulation definitions were closed prospectively |
| Stage 0B G0/G1 | `PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY` | Disease-blind A1/A2 construction, score transfer and technical simulation |
| WP1 prefit | PASS | 68 donors, 31 controls, 37 managed SLE, frozen four-column design, rank 4/4 |
| WP1 analysis | `PASS_WP1_TO_WP2_PREFIT_AND_G2_FREEZE` | Three frozen representations, 2,000/2,000 paired bootstraps, 11/11 audit checks |
| WP2 effect-free preflight | `PASS_WP2_EFFECT_FREE_PREFLIGHT` | Five-bin support, count/library/cell closure, p/q geometry and 8/8 ILR design verified without fitting a disease effect |
| G2 implementation/domain freeze | `PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2` | 934/934 bundle payloads, 48/48 candidate tests, 50-attempt Windows pilot, 250/250 truth precision and 10/10 canonical integration tests |
| Full G2 operating-characteristic execution | `HOLD_G2_APPLICABLE_DOMAIN` | 25/25 scenarios, 50,000 outer attempts, 60,106,000 paired-bootstrap fits, independent byte-identical readjudication; 90/150 applicable target-scenario cells passed and 60/150 held |
| G2B single-method integration and binding | `PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED` | One HC3 bootstrap-t amendment; 901/901 external payloads, 42/42 external tests, 150-object Windows replay, 4,500 expanded-row checks and 58/58 canonical tests |
| Full G2B execution and independent adjudication | `HOLD_G2B_APPLICABLE_DOMAIN` | 25/25 scenarios, 2,000/2,000 chunks, 50,000 outer attempts and 60,112,000 successful inner draws; formal and independent outputs byte-identical; 133/150 applicable rows passed and 17/150 held |
| WP3 result-blind available-object prefit | `PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION` | 22/22 canonical checks, 56 unique donors, 54 min50-eligible source-label B_CONV objects, 43 childhood primary donors, 12/12 IFN genes and 18,873/18,873 rank-background symbols; no new score or disease outcome generated |
| WP3 pooled measurement diagnostics | `PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION` | 13/13 tests, 25/25 canonical checks and 4,389/4,389 independent numeric comparisons; pooled transform rho 0.985744 and 12/12 leave-one-gene-out correlations at least 0.995883; no phenotype field or inferential outcome loaded |

## WP1 numerical record

| Estimand | Estimate | 95% bootstrap CI |
|---|---:|---:|
| beta_A0 | 1.037152 | 0.598263-1.477349 |
| beta_A1 | 1.072077 | 0.630517-1.518759 |
| beta_A2 | 1.037718 | 0.598753-1.477793 |
| A1 - A0 | 0.034925 | 0.013789-0.057130 |
| A2 - A0 | 0.000567 | 0.000000-0.001424 |

Interpretation is deliberately bounded. A1 is a joint identity-axis and
common-composition sensitivity. A2 excludes the historical strong-ISG list but
retains LY6E. No equivalence margin was defined. The analysis therefore supports
representation robustness on the tested common support, not annotation
independence, mediation, equivalence or a causal mechanism.

## Permanent historical boundaries

- R1 identity HOLD: B_ASC median Jaccard 0.930323 < 0.95.
- Corrected C9R transfer HOLD: B_ASC precision 0.885210 < 0.90.
- No corrected external disease outcome was unlocked.
- Regulatory evidence remains observational and does not establish a unique
  ligand, direct binding or causal regulation.

These decisions are not candidates for rescue in RP v3.

## WP2 effect-free preflight result

The canonical local preflight used the frozen 68 donors and sufficient raw
statistics without calculating a new disease coefficient, disease-stratified
expression mean or IFN score. It established:

- minimum support of 30 cells in every donor-bin;
- exact partition of A0 gene counts, full captured-library totals and cells;
- pooled CPM reconstruction error no larger than `1.137e-13`;
- median absolute `p_cell - q_UMI` difference of `0.015954` and maximum of
  `0.093275`;
- rank 8/8 for the optional four-ILR conditional design;
- rank 8/9 for intercept plus all five raw fractions, confirming the expected
  closure redundancy.

Cell fractions and captured-UMI fractions are therefore distinct measurement
objects. The new `beta_S_cellref` bridge target fixes the cell reference while
retaining observed captured UMI/cell; it remains neither absolute RNA/cell nor a
causal composition effect.

## Full G2 result

The full registered grid was executed under binding
`5546f5931069f2d09b784b0d365fa58c433a38c6e8edb5e7f5a55329585bfbf3`.
It contains 25 scenarios, 2,000 outer attempts per scenario and 2,000 paired
bootstrap attempts for each supported outer attempt. The completed run contains
2,000 hash-verified chunks, 50,000 outer attempts and 60,106,000 successful
inner fits. There were 30,053 interval-computed outer attempts, 19,947
prespecified support stops and no numerical failures. Real WP2 effects were not
loaded or fitted.

R0/R2/R4 are the applicable performance domain. R1/R3 remain mandatory
support/stress boundaries and cannot be removed, replenished or converted to
PASS. Within the 150 applicable target-scenario cells:

- 90 passed and 60 were held;
- truth precision passed in 150/150;
- numerical stability passed in 150/150;
- bias passed in 149/150, with the sole failure at `C0_R4 / beta_bin_3`;
- coverage passed in 91/150 and failed in 59/150, all through lower-bound
  undercoverage rather than upper-bound overcoverage;
- exact-null type-I control passed in 10/10 registered cells.

No target passed all 15 applicable scenarios. The official adjudication and a
fresh independent adjudication were byte-identical. The dominant defect is the
coverage of the frozen percentile-bootstrap interval, not implementation
instability or a missing simulation truth.

Decision: `HOLD_G2_APPLICABLE_DOMAIN`.
WP2 real disease effects remain locked. This HOLD cannot be overridden by a
small real-data P value or by weakening the frozen acceptance contract. The
diagnostic gate selected one theory-driven replacement only: paired donor
bootstrap-t with an HC3 studentizer. Its point estimator, targets, scenarios,
truth and acceptance rules are unchanged.

The canonical G2B implementation was executed at stage 121 under binding
`ce40a673df8c051e4eb7036292fe5827eb6ce8b552ee56964affc61d1fa25d0c`.
All 25 scenarios completed with 2,000 outer attempts per scenario. The run
contains 30,056 interval-computed objects, 19,944 support stops, no numerical
failure and 60,112,000 successful inner bootstrap draws. Within the 150
applicable target-scenario rows, 133 passed and 17 held. There were six bias
failures, 11 coverage failures and one overlapping exact-null type-I failure.

G2B materially reduced the original coverage problem but did not satisfy the
ten-target conjunction. The official and independent adjudications are
byte-identical. `WP2_REAL_EFFECT_UNLOCK=false`; no real WP2 response was loaded
or fitted. The frozen stop rule therefore closes interval development and moves
the project to `HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION`. The original
G2 and final G2B failures remain permanent provenance and will not be
overwritten.

Canonical compact evidence is in
`phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/`.
The G2B protocol freeze and runbook are in
`phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/`.
The full G2B adjudication, recovery receipt, independent summaries and
scope-contraction contract are in
`phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/`.

## Closed workstreams

Under the final G2B HOLD and scope-contraction contract, do not:

- rewrite the manuscript around RP v3 results;
- replace main or supplementary figures;
- reopen WP4;
- update the public release or Zenodo DOI;
- rebuild or upload a journal submission package;
- tune thresholds after inspecting simulation or disease effects;
- load or fit real WP2 responses under the held implementation;
- delete failed scenarios or rewrite the full-G2 HOLD as a partial PASS.
- try a second interval method, change stage 121 or rerun seeds after seeing G2B results.
- unlock only the four targets that passed 15/15 applicable scenarios;
- run WP3 disease outcomes without a separate author-reviewed uncertainty and
  multiplicity contract.

## WP3 prefit and pooled measurement result

The available external sufficient-count object contains 672 rows by 32,738
features, representing multiple stored views of 56 samples rather than 672
donors. Exact source linkage confirms 56 unique donors. Eight source labels sum
exactly to the B_CONV_ANALOG count and cell totals in every sample. Fifty-four
donors meet the frozen 50-cell rule; the childhood primary set contains 43
donors (11 controls and 32 SLE).

All 12 frozen IFN genes, the complete 18,873-symbol rank background and the
43-control discovery reference are available. The source `T_rank` implementation
was tested as `rankdata(method="average") / M`. The current ID-linked design does
not verify age, sex, ancestry, treatment, activity or processing-batch columns.
The prefit did not regenerate the raw TAR/barcodes, reopen source-label-
independent mapping, compute new real scores, summarize disease groups or fit an
outcome.

The permitted pooled measurement stage was executed over all 54 eligible
objects without loading phenotype fields. `T_frozen` versus `T_rank` pooled
Spearman correlation was 0.985744; the maximum donor-rank displacement was 6.
All 12 leave-one-gene-out correlations were between 0.995883 and 0.999161.
IFIT1, IFIT3 and OAS2 were detected in 47/54, 52/54 and 53/54 pseudobulks;
the other nine genes were detected in 54/54. The fixed rank background captured
95.09%-96.69% of the full measured library, so it remains unsuitable as a
replacement normalization denominator.

The stage passed 13/13 focused tests, 25/25 real-input checks and 4,389/4,389
independent scalar comparisons. A second project-side execution reproduced all
13 machine outputs byte-for-byte. No disease/cohort summary, coefficient,
interval, P value or clinical calibration was generated.

The limited WP3 measurement question is complete. WP2 remains closed; WP3
outcomes, WP4 and all manuscript/submission/release changes remain unauthorized.
The next gate is `RP_V3_AUTHOR_SCOPE_CLOSURE_DECISION`.
