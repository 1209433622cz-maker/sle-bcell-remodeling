# Next-stage decision: Gate C6B regulatory evidence

## Advisor decision

Proceed to Gate C6B under the frozen pre-effect contract. Gate C6A has converted the
validated analysis into a coherent manuscript claim hierarchy. The remaining
upper-Q1 opportunity is a narrowly prespecified regulatory layer, not another broad
search for cell states, pathways or datasets.

Real regulator effects remain locked until C6B-1 qualification passes.

## Gate C6B-1: resource and software qualification

### Required work

1. Retrieve and freeze the exact human MSigDB release containing
   `HALLMARK_INTERFERON_ALPHA_RESPONSE` (`M5911`), including member checksum and
   license record.
2. Freeze GSE23307 sample pairing, platform annotation and processed-expression
   checksum without computing IFN-control differences.
3. Parse the frozen CollecTRI snapshot using exact individual TF symbols and
   consensus `+1/-1` target directions.
4. Implement signed `sqrt(F)` ranking, duplicate-symbol averaging and weighted
   univariate linear-model activity.
5. Reproduce the estimator independently by direct matrix algebra.
6. Qualify positive, negative and null synthetic data, including sign recovery,
   interval coverage, null P-value calibration and 24-test BH recovery.
7. Import the three real gene tables only for dimensions, tested-gene symbols and
   regulator coverage.

### Unlock criterion

Emit `PASS_GATE_C6B1_NO_EFFECT_QUALIFICATION` with
`regulatory_effects_inspected=false`. Any failure holds the real activity stage.

## Gate C6B-2: frozen regulator analysis

After C6B-1 passes, run exactly:

- GSE174188 primary;
- GSE174188 donor-nonoverlap internal validation; and
- GSE135779 childhood independent validation.

The confirmatory multiplicity family is 24 tests: STAT1, STAT2, IRF7, IRF9, E2F1,
FOXM1, MYC and MYBL2 across the three contrasts. STAT1/STAT2 are core; IRF7/IRF9 are
extended support because of lower tested-target coverage.

Run target leave-one-out and 100 x 80% target resampling for the core regulators.
Sensitivity contrasts must remain separate from the confirmatory family.

## Orthogonal evidence

If qualification succeeds:

- test M5911 as a frozen response signature on the same ranked contrasts; and
- score the exact 12-gene IFN positive arm in paired GSE23307 B-cell IFN-beta/control
  samples.

GSE23307 contains only two donors, so report the two paired directions without a
powered P value. GSE142637 and GSE175913 remain literature or supplementary context.

## Decision outcomes

### If Gate C6B passes

Authorize a carefully qualified regulatory framing such as:

> Independently replicated IFN remodeling is accompanied by concordant
> STAT1/STAT2-centred target activity across discovery, internal and external SLE
> contrasts.

Use `accompanied by` or `consistent with`; do not use causal verbs. Build conditional
Figure 5 and revise the abstract and Discussion only after the result-integrity audit.

### If Gate C6B fails

Retain the current four-figure manuscript. Remove central regulator claims and state
that the data independently replicate IFN/ISG remodeling without resolving its
upstream regulatory cause. This remains a valid multi-cohort paper.

## Work after C6B

Gate C7 will regenerate Figures 1-3 from frozen Source Data, perform full numerical
and citation consistency checks, render the RP/manuscript package, and prepare the
submission files. Journal selection should occur only after the C6B result determines
whether the final paper is descriptive or regulator-supported.
