# Phase 4 Runbook - Supplementary Flagged Cluster QC

This runbook regenerates the supplementary QC figure for the flagged platelet/ambient-RNA-high B-cell cluster.

## Environment

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

## Generate Supplementary QC Figure

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\21_make_supplement_qc_flagged_cluster.py `
  --h5ad .\03_results\first_pass_bcell_full\bcell_first_pass_labeled.h5ad `
  --marker-summary .\03_results\first_pass_bcell_full\marker_refinement\tables\raw_count_marker_summary_by_state.csv `
  --ranked-markers .\03_results\first_pass_bcell_full\marker_refinement\tables\raw_count_ranked_state_markers.csv `
  --donor-fractions .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fractions.csv `
  --state-tests .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fraction_disease_tests.csv `
  --sensitivity-tests .\03_results\first_pass_bcell_full\marker_refinement\sensitivity\donor_state_fraction_tests_exclude_Naive_B_III_-_small_naive-like_cluster.csv `
  --outdir .\03_results\supplement_qc_flagged_cluster
```

## Key Outputs

- `03_results/supplement_qc_flagged_cluster/figures/supplement_qc_flagged_cluster.png`
- `03_results/supplement_qc_flagged_cluster/figures/supplement_qc_flagged_cluster.pdf`
- `03_results/supplement_qc_flagged_cluster/supplement_qc_flagged_cluster_summary.md`
- `03_results/supplement_qc_flagged_cluster/tables/flagged_cluster_top_ranked_markers.csv`
- `03_results/supplement_qc_flagged_cluster/tables/flagged_cluster_selected_marker_expression.csv`
- `03_results/supplement_qc_flagged_cluster/tables/flagged_cluster_donor_fraction_test.csv`
- `03_results/supplement_qc_flagged_cluster/tables/core_state_sensitivity_original_vs_exclude_flagged.csv`
- `01_manuscript/supplement_qc_flagged_cluster_legend_draft.md`

## Current Interpretation

The flagged cluster retains B-cell identity marker expression but is dominated by platelet/ambient-associated ranked markers. It should be shown transparently in supplementary QC, while the main Results should emphasize that core disease-associated B-cell signals remain stable after excluding it.
