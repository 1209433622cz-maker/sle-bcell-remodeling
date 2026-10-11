# RP v4 Stage L prospective external-cohort contract

## Scientific question

The sole primary question is whether the within-patient difference in the frozen
12-gene IFN/ISG score between transitional and resting-naive B cells differs
between active and inactive SLE. Generic SLE-versus-control IFN positivity is
not a new primary claim.

## Analysis population and unit

- Independent unit: patient.
- Primary population: the 26 SLE patients with both rN and T1T2 RNA libraries
  (12 active, 14 inactive under the deposited SLEDAI >4 rule).
- The two unpaired SLE patients are excluded from the paired primary estimand
  and retained only for intake/QC summaries; no imputation is permitted.
- The 17 paired healthy controls provide descriptive scale/context only and do
  not enter the primary active-versus-inactive test.
- Technical runs and sorted subsets are never counted as independent patients.

## Frozen score and primary estimand

After a separately approved raw-read reconstruction, counts must be generated
with one frozen GRCh38/GENCODE pipeline. Library-size normalization, detection
rules, and the mapping of the unchanged 12-gene positive IFN/ISG arm must be
fixed while activity labels remain inaccessible. For each paired patient,
define D_i = score(T1T2) - score(rN). The primary coefficient is the adjusted
mean difference in D_i for active versus inactive SLE.

## Primary model and sensitivities

- Primary design: intercept, active-SLE indicator, and deposited RNA batch.
- Primary uncertainty: donor-level OLS with HC3 covariance and a two-sided
  t reference using residual degrees of freedom; the exact implementation must
  pass a prospective small-sample simulation gate before outcomes are opened.
- Continuous SLEDAI is a single secondary sensitivity, not a co-primary target.
- Sex and race are not model covariates because the paired SLE support contains
  one male and one Caucasian patient; this limitation must be reported.
- No gene-set, subset, threshold, covariate, or method may be selected by the
  smaller P value. Failure or null results remain reportable.

## Multiplicity and multi-omics boundary

There is one primary transcriptomic contrast. Any gene-level follow-up is
exploratory and requires a separately frozen multiplicity family. GSE263716
ATAC-seq is not an independent cohort and cannot be called same-visit paired
multi-omics until visit provenance resolves the two discordant SLEDAI records.

## Stop rules

Stop without fitting an activity outcome if integer gene counts cannot be
reconstructed, sample-to-run identity is incomplete, the fixed score is not
measurable without outcome-guided repair, or the prospective small-sample
simulation fails. No result from processed RPKM may substitute for this gate.
