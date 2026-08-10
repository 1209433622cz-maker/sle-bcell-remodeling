# Phase 2 Runbook - Refined B-Cell Figure 2

This runbook regenerates the raw-count marker refinement, sensitivity analysis, and Figure 2 v3.

## Environment

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

Use the Miniforge conda wrapper directly:

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\01_check_scanpy_env.py
```

## 1. Curated Raw-Count Marker Summary

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\14_raw_count_marker_refinement.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --labels .\03_results\first_pass_bcell_full\tables\bcell_obs_scores_labeled.csv `
  --outdir .\03_results\first_pass_bcell_full\marker_refinement `
  --gene-symbol-column feature_name `
  --chunk-size 8000
```

Key outputs:

- `03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_marker_summary_by_state.csv`
- `03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_program_summary_by_state.csv`
- `03_results/first_pass_bcell_full/marker_refinement/figures/raw_count_state_marker_dotplot.png`

## 2. Balanced Raw-Count Ranked State Markers

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\15_raw_count_rank_state_markers.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --labels .\03_results\first_pass_bcell_full\tables\bcell_obs_scores_labeled.csv `
  --outdir .\03_results\first_pass_bcell_full\marker_refinement `
  --state-column draft_state `
  --gene-symbol-column feature_name `
  --max-cells-per-state 3000 `
  --method t-test_overestim_var `
  --n-genes 100 `
  --min-cells 20
```

Key outputs:

- `03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_ranked_state_markers.csv`
- `03_results/first_pass_bcell_full/marker_refinement/raw_count_ranked_state_markers_summary.md`

## 3. Sensitivity Analysis Excluding Flagged Cluster

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\16_state_fraction_sensitivity.py `
  --scores .\03_results\first_pass_bcell_full\tables\bcell_obs_scores_labeled.csv `
  --outdir .\03_results\first_pass_bcell_full\marker_refinement\sensitivity `
  --exclude-state "Naive B III / small naive-like cluster"
```

Key output:

- `03_results/first_pass_bcell_full/marker_refinement/sensitivity/donor_state_fraction_tests_exclude_Naive_B_III_-_small_naive-like_cluster.csv`

## 4. Figure 2 v3

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\17_make_figure2_v3_refined.py `
  --h5ad .\03_results\first_pass_bcell_full\bcell_first_pass_labeled.h5ad `
  --marker-summary .\03_results\first_pass_bcell_full\marker_refinement\tables\raw_count_marker_summary_by_state.csv `
  --program-summary .\03_results\first_pass_bcell_full\marker_refinement\tables\raw_count_program_summary_by_state.csv `
  --donor-fractions .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fractions.csv `
  --state-tests .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fraction_disease_tests.csv `
  --sensitivity-tests .\03_results\first_pass_bcell_full\marker_refinement\sensitivity\donor_state_fraction_tests_exclude_Naive_B_III_-_small_naive-like_cluster.csv `
  --output .\03_results\first_pass_bcell_full\figures\figure2_v3_refined_bcell_state_atlas.png `
  --state-table-output .\03_results\first_pass_bcell_full\marker_refinement\figure2_v3_refined_state_labels.csv
```

Key outputs:

- `03_results/first_pass_bcell_full/figures/figure2_v3_refined_bcell_state_atlas.png`
- `03_results/first_pass_bcell_full/figures/figure2_v3_refined_bcell_state_atlas.pdf`
- `03_results/first_pass_bcell_full/marker_refinement/figure2_v3_refined_state_labels.csv`

## Current Interpretation

Figure 2 v3 supports the following working model:

- SLE expands an atypical ABC/APC-like B-cell state.
- SLE expands an activated naive-like B-cell state.
- A memory-like B-cell state is reduced in SLE.
- A small platelet/ambient-RNA-high cluster should be flagged and excluded from central claims.
- Plasmablasts are transcriptionally clear but not significantly expanded at donor level in this cohort.
