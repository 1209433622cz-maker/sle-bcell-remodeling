# RP v3 scientific redesign status

**Effective date:** 2026-10-10
**Overall state:** `ACTIVE_RP_V3_SCIENTIFIC_REDESIGN`
**Submission state:** `HOLD`
**Current gate:** `PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED`

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
| G2B single-method integration and binding | `PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED` | One HC3 bootstrap-t amendment; 901/901 external payloads, 42/42 external tests, 150-object Windows replay, 4,500 expanded-row checks and 58/58 canonical tests; full G2B not run |

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

The canonical G2B implementation is now frozen at stage 121 under binding
`ce40a673df8c051e4eb7036292fe5827eb6ce8b552ee56964affc61d1fa25d0c`.
This is an implementation/protocol decision; `G2B=NOT_RUN` and
`WP2_REAL_EFFECT_UNLOCK=false`. The next authorized stage is
`G2B_FULL_SYNTHETIC_EXECUTION_AND_INDEPENDENT_ADJUDICATION`. A G2B PASS requires
a separate post-G2B review, while a G2B HOLD ends interval-method development
and triggers RP v3 scope contraction. The original G2 failure remains permanent
provenance and will not be overwritten.

Canonical compact evidence is in
`phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/`.
The G2B protocol freeze and runbook are in
`phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/`.

## Closed workstreams

While G2B has not passed a separate post-run review, do not:

- rewrite the manuscript around RP v3 results;
- replace main or supplementary figures;
- reopen WP4;
- update the public release or Zenodo DOI;
- rebuild or upload a journal submission package;
- tune thresholds after inspecting simulation or disease effects;
- load or fit real WP2 responses under the held implementation;
- delete failed scenarios or rewrite the full-G2 HOLD as a partial PASS.
- try a second interval method, change stage 121 or rerun seeds after seeing G2B results.
