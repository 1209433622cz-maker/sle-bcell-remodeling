# Phase 5 Targets - 2026-07-01

## Current Status After Phase 4

The project now has a coherent four-figure manuscript backbone plus one supplementary QC figure.

Main figures:

- Figure 1: dataset overview, B-lineage extraction, donor retention, and analysis guardrails.
- Figure 2: refined B-cell state atlas, raw-count marker support, donor-level abundance, and flagged-state sensitivity.
- Figure 3: donor-state pseudobulk evidence for the atypical ABC/APC-like B-cell state.
- Figure 4: donor-level metadata audit and covariate-adjusted abundance sensitivity.

Supplementary figure:

- Flagged platelet/ambient-RNA-high B-cell cluster QC and sensitivity support.

## Phase 4 Conclusion

The covariate sensitivity analysis supports the robustness of the core disease-associated B-cell remodeling model.

Full-adjusted donor-level results:

- ABC/APC-like: beta 0.0175; 95% CI 0.0045 to 0.0305; FDR 2.22e-02.
- Memory-like B I: beta -0.0999; 95% CI -0.1378 to -0.0620; FDR 9.66e-07.
- Activated SLE-naive-like: beta 0.1491; 95% CI 0.1051 to 0.1931; FDR 2.41e-10.

This means the central manuscript claim is no longer just an unadjusted donor-fraction result. It is supported after adjustment for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count.

## Recommended Next Stage

Phase 5 should focus on manuscript consolidation plus external/literature validation planning.

Priority order:

1. Consolidate Results, Methods, and figure legends into a full manuscript v1.
2. Decide whether Figure 4 remains the covariate-sensitivity figure or is moved to supplement.
3. Evaluate whether an external/literature signature validation figure can be added as Figure 5 or replace Figure 4.
4. Build a reference/signature table for ABC/DN2, APC-like B cells, IFN response, and SLE B-cell state literature.
5. Prepare a submission-readiness checklist for SCI Q1/Q2 journals.

## Figure 5 Candidate Options

Option A: Literature signature validation.

- Score published ABC/DN2, age-associated B-cell, APC-like B-cell, and IFN signatures in the current states.
- Low compute and directly strengthens biological interpretation.

Option B: External dataset validation.

- Requires another suitable SLE B-cell scRNA-seq dataset.
- Higher impact if feasible, but may require download and heavier harmonization.

Option C: Graphical model plus evidence matrix.

- Lower compute and useful for manuscript clarity.
- Less convincing as validation than Options A or B.

## Current Recommendation

Start with Option A: literature signature validation. It is the best balance of impact, feasibility, and speed. If it works, it can become Figure 5 or a strong supplementary validation figure. If it does not add enough, we keep Figure 4 as the robustness main figure and move validation into Discussion.
