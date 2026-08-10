# Phase 4 Runbook - Covariate Sensitivity Figure 4

This runbook regenerates the donor-level metadata audit, covariate-adjusted abundance models, and Figure 4 v1.

## Environment

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

## Generate Covariate Sensitivity Outputs

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\22_covariate_sensitivity_abundance.py `
  --bcell-h5ad .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --donor-fractions .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fractions.csv `
  --outdir .\03_results\figure4_covariate_sensitivity
```

## Key Outputs

- `03_results/figure4_covariate_sensitivity/figures/figure4_v1_covariate_sensitivity.png`
- `03_results/figure4_covariate_sensitivity/figures/figure4_v1_covariate_sensitivity.pdf`
- `03_results/figure4_covariate_sensitivity/covariate_sensitivity_summary.md`
- `03_results/figure4_covariate_sensitivity/tables/donor_metadata_covariates.csv`
- `03_results/figure4_covariate_sensitivity/tables/donor_metadata_completeness_audit.csv`
- `03_results/figure4_covariate_sensitivity/tables/donor_covariate_balance_categorical.csv`
- `03_results/figure4_covariate_sensitivity/tables/donor_age_balance_summary.csv`
- `03_results/figure4_covariate_sensitivity/tables/state_abundance_covariate_models.csv`
- `03_results/figure4_covariate_sensitivity/tables/state_abundance_by_disease_state_summary.csv`
- `01_manuscript/figure4_v1_legend_draft.md`

## Model Specification

The script fits donor-level OLS models with HC3 robust standard errors for each B-cell state fraction.

Age and log10 donor B-lineage cell count are centered and scaled before fitting to improve numerical conditioning without changing the disease coefficient.

Model tiers:

- Unadjusted: disease only.
- Demographic adjusted: disease, age, sex, self-reported ethnicity.
- Full adjusted: disease, age, sex, self-reported ethnicity, simplified processing cohort, and log10 donor B-lineage cell count.

Multiple processing cohort values within a donor are collapsed into `multiple`. Multiple SLE disease-state labels within a donor are collapsed into `SLE mixed` for descriptive disease-state summaries.

## Current Interpretation

The core disease-associated state abundance results remain directionally stable and statistically supported after full adjustment:

- ABC/APC-like: beta 0.0175; FDR 2.22e-02.
- Memory-like B I: beta -0.0999; FDR 9.66e-07.
- Activated SLE-naive-like: beta 0.1491; FDR 2.41e-10.

This supports using Figure 4 as the manuscript robustness figure, or moving it to the supplement if a stronger external-validation Figure 4 is later generated.
