# Phase 6 Runbook - Compositional Abundance Sensitivity

This workflow tests whether the donor-level B-cell remodeling pattern remains supported after accounting for the constant-sum structure of state fractions.

## Environment

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

## Run

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\38_compositional_abundance_sensitivity.py `
  --donor-fractions .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fractions.csv `
  --donor-metadata .\03_results\figure4_covariate_sensitivity\tables\donor_metadata_covariates.csv `
  --original-models .\03_results\figure4_covariate_sensitivity\tables\state_abundance_covariate_models.csv `
  --outdir .\03_results\compositional_abundance_sensitivity `
  --pseudocount 0.5 `
  --pseudocount-grid 0.1,0.5,1.0
```

## Method

- Exclude the platelet/ambient-RNA-high QC state.
- Add a count-scale pseudocount to each of seven retained state counts.
- Convert counts to retained-state proportions and apply donor-wise centered log-ratio transformation.
- Fit unadjusted, demographic-adjusted, and fully adjusted OLS models with HC3 robust standard errors.
- Correct P values across seven states within each analysis and model tier.
- Repeat core full-adjusted CLR models across pseudocounts of 0.1, 0.5, and 1.0.

CLR coefficients are relative to the geometric mean abundance of retained states and do not estimate absolute cell-number changes.

## Key Outputs

- `03_results/compositional_abundance_sensitivity/tables/donor_state_compositional_abundance.csv`
- `03_results/compositional_abundance_sensitivity/tables/compositional_abundance_models.csv`
- `03_results/compositional_abundance_sensitivity/tables/core_state_compositional_comparison.csv`
- `03_results/compositional_abundance_sensitivity/tables/core_state_pseudocount_sensitivity.csv`
- `03_results/compositional_abundance_sensitivity/figures/supplementary_figure_s4_compositional_sensitivity.png`
- `03_results/compositional_abundance_sensitivity/figures/supplementary_figure_s4_compositional_sensitivity.pdf`
- `03_results/compositional_abundance_sensitivity/compositional_abundance_sensitivity_summary.md`
