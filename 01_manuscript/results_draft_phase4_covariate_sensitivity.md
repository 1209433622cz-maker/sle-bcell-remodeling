# Results Draft - Phase 4 Covariate Sensitivity

## Covariate-Adjusted Donor-Level Models Support Robust B-Cell State Remodeling

Because donor metadata showed imbalance between normal and SLE groups, we next tested whether the major donor-level B-cell state abundance signals remained stable after covariate adjustment. Donor-level metadata were complete for disease status, sex, self-reported ethnicity, age parsed from `development_stage`, processing cohort, and donor B-lineage cell count across all 259 B-lineage donors. Some donors were represented across multiple processing cohorts, and these were collapsed into a `multiple` processing cohort category for donor-level modeling.

Normal and SLE donors differed in age distribution and covariate composition, supporting the need for sensitivity analysis. We therefore fit donor-level abundance models for each refined B-cell state using three specifications: an unadjusted disease-only model, a demographic model adjusted for age, sex, and self-reported ethnicity, and a full model additionally adjusted for simplified processing cohort and donor B-lineage cell count.

The three central disease-associated B-cell state signals remained directionally stable after adjustment. In the full model, the activated SLE-naive-like state remained expanded in SLE (beta 0.1491; 95% CI 0.1051 to 0.1931; FDR 2.41e-10). The memory-like B I state remained reduced in SLE (beta -0.0999; 95% CI -0.1378 to -0.0620; FDR 9.66e-07). The atypical ABC/APC-like state also remained expanded in SLE after full adjustment (beta 0.0175; 95% CI 0.0045 to 0.0305; FDR 2.22e-02).

Disease-state abundance summaries were treated as descriptive because disease-state labels are nested within disease status and some SLE donors carried multiple disease-state labels. Descriptively, ABC/APC-like abundance was higher in SLE flare and SLE mixed donor groups than in normal donors, while the activated SLE-naive-like state was higher across SLE strata.

## Working Manuscript Claim

These covariate sensitivity results strengthen the manuscript by showing that the core B-cell remodeling model is not explained solely by age, sex, self-reported ethnicity, processing cohort, or donor B-lineage cell count. The strongest robustness claim is that the activated SLE-naive-like expansion, memory-like B-cell reduction, and ABC/APC-like expansion remain directionally stable after full donor-level adjustment.

## Limitations To Preserve

- The models are observational sensitivity analyses and do not establish causality.
- Disease-state patterns remain descriptive because disease_state is structurally nested within disease group.
- Processing cohort was simplified at donor level because a subset of donors had cells represented across multiple cohorts.
