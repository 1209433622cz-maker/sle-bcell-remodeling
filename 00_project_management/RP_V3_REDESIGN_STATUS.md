# RP v3 scientific redesign status

**Effective date:** 2026-10-10
**Overall state:** `ACTIVE_RP_V3_SCIENTIFIC_REDESIGN`
**Submission state:** `HOLD`
**Current gate:** `PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2`

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

## G2 implementation/domain-freeze result

The previously missing generator, independent truth and truth-receipt hashes are
now filled by audited objects. The Windows rerun reproduced all 50 pilot
statuses, all generated count arrays and all bootstrap index arrays; 60,000
inner fits succeeded. All 250 independent truth rows met the MCSE rule, with
cross-platform truth differences no larger than `1.11e-16`.

R0/R2/R4 are the applicable performance domain. R1/R3 remain mandatory
support/stress boundaries and cannot be removed or replenished. The full runner
stores compact, hash-bound chunks for all registered outer IDs, and the
adjudicator applies the frozen bias, coverage, type-I and numerical gates.

Decision: `PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2`.
This approves synthetic execution only. Full G2 remains `NOT_RUN`, and WP2 real
disease effects remain locked. The next authorized stage is
`G2_FULL_EXECUTION_R0_CORE_FIRST`, followed by the complete 25-scenario grid.

## Closed workstreams

Until G2 passes, do not:

- rewrite the manuscript around RP v3 results;
- replace main or supplementary figures;
- reopen WP4;
- update the public release or Zenodo DOI;
- rebuild or upload a journal submission package;
- tune thresholds after inspecting disease effects.
