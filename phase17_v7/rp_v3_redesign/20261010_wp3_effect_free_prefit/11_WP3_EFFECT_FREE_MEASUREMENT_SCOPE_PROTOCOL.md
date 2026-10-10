# WP3 effect-free measurement-sensitivity protocol

**Date:** 2026-10-10
**Parent gate:** `PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION`
**Next stage:** `WP3_EFFECT_FREE_MEASUREMENT_SENSITIVITY_PROTOCOL_AND_DRY_RUN`

## Scientific question

The only permitted question is whether the already frozen 12-gene measurement
definition has stable computational behavior across two prespecified transforms
when applied to the same eligible source-label B_CONV donor pseudobulks.

This is not another external disease-association analysis. It cannot validate a
clinical score, establish cross-platform equivalence, rescue WP2, or replace the
existing source-label-defined IFN replication.

## Frozen analysis objects

- Eligible set: all 54 source-label B_CONV donor pseudobulks with at least 50
  B_CONV cells. Disease labels and childhood/adult strata must not be used to
  select, stratify or summarize measurement diagnostics.
- `T_frozen`: mean of the 12 program genes after duplicate-symbol summation,
  full measured-library CPM, `log2(CPM + 0.5)`, and standardization by the
  discovery A0 43-control means and population SDs.
- `T_rank`: mean percentile rank of the same 12 genes over the fixed 18,873
  symbol background after duplicate-symbol summation. The exact source operator
  is `scipy.stats.rankdata(method="average") / M`.
- `T_local`: historical context only. It is not recomputed and is not a third
  candidate from which to select a favorable result.

## Permitted diagnostics

The next stage may compute real expression-derived scores, but only without
disease-group summaries or inferential modeling:

1. finite-value, feature-coverage, duplicate-symbol and full-library-denominator
   checks;
2. pooled score ranges and empirical quantiles across all 54 eligible donors;
3. Spearman rank concordance between `T_frozen` and `T_rank`, reported without a
   P value or a claim of scale equivalence;
4. twelve leave-one-gene-out `T_frozen` scores, their pooled rank concordance
   with the full score and the maximum absolute donor-rank displacement;
5. per-gene detection frequency and standardized-contribution summaries pooled
   across all eligible donors;
6. a source-operator dry run on synthetic count vectors that locks duplicate
   symbols, ties, zeros and denominator behavior.

These diagnostics are descriptive. No correlation, overlap or leave-one-gene-
out threshold is a gate for choosing between transforms.

## Prohibited outputs

- HC/SLE, childhood/adult or treatment/activity subgroup score summaries;
- disease coefficients, confidence intervals, P values, ROC curves or clinical
  thresholds;
- selection of `T_rank` because it appears more favorable;
- refitting the discovery reference or changing the 18,873-symbol background;
- a new cohort, mapping method, gene set, pathway or mechanism analysis;
- statements of cross-platform, clinical or causal calibration;
- manuscript, figure, submission, Release or Zenodo changes.

## Stop rule

If score generation violates any frozen denominator, feature, symbol or source-
operator rule, WP3 closes. If the effect-free diagnostics are technically valid
but add no interpretable measurement information beyond the Stage 0B
computability check and the historical IFN replication, WP3 also closes without
outcome execution.

Passing the next stage does not unlock a disease association. Any later proposal
to fit `beta_E(T_frozen)` would require a separate author-reviewed uncertainty,
multiplicity and interpretation contract. No such contract is authorized here.
