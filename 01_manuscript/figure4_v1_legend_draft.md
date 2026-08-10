# Figure 4. Covariate sensitivity supports donor-level B-cell state remodeling in SLE

**a,** Donor age distribution in the B-lineage subset. Age was parsed from the CELLxGENE `development_stage` metadata. Normal donors and SLE donors showed age imbalance, motivating covariate-adjusted sensitivity analysis.

**b,** Categorical covariate balance. Bars show the SLE-minus-normal difference in donor proportions for processing-cohort and self-reported-ethnicity categories. Donors represented in multiple processing cohorts were collapsed into a `multiple` category.

**c,** Disease-effect sensitivity for three core states. Points and lines show SLE coefficients and 95% confidence intervals from unadjusted, demographic-adjusted, and full models. The full model included age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count. Continuous covariates were centered and scaled. All three effects remained directionally stable.

**d,** Signed adjusted significance across all states and models. Positive values indicate higher fractions in SLE and negative values lower fractions; values are signed -log10(FDR), Benjamini-Hochberg corrected within each model.

In the full model, SLE coefficients were 0.1491 for activated SLE-naive-like (FDR 2.41e-10), -0.0999 for memory-like B I (FDR 9.66e-07), and 0.0175 for ABC/APC-like cells (95% CI 0.0045-0.0305; FDR 2.22e-02).
