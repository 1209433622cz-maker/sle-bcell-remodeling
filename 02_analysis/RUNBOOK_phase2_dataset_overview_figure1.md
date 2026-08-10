# Phase 2 Runbook - Figure 1 Dataset Overview

This runbook regenerates the dataset overview figure and summary tables.

## Environment

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

## Generate Figure 1

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\18_make_figure1_dataset_overview.py `
  --source-h5ad .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --bcell-scores .\03_results\first_pass_bcell_full\tables\bcell_obs_scores_labeled.csv `
  --outdir .\03_results\figure1_dataset_overview
```

## Key Outputs

- `03_results/figure1_dataset_overview/figures/figure1_dataset_overview.png`
- `03_results/figure1_dataset_overview/figures/figure1_dataset_overview.pdf`
- `03_results/figure1_dataset_overview/tables/figure1_dataset_summary.csv`
- `03_results/figure1_dataset_overview/tables/source_cell_type_counts.csv`
- `03_results/figure1_dataset_overview/tables/source_donor_counts_by_disease.csv`
- `03_results/figure1_dataset_overview/tables/bcell_donor_counts_by_disease.csv`
- `03_results/figure1_dataset_overview/tables/bcell_refined_state_counts.csv`

## Current Numbers

- Source object: 1,263,676 cells and 261 donors.
- Source disease groups: 99 normal donors and 162 SLE donors.
- B-lineage subset: 152,981 cells and 259 donors.
- B-lineage disease groups: 99 normal donors and 160 SLE donors.
- B cells: 151,570.
- Plasmablasts: 1,411.
- Flagged platelet/ambient-high B cluster: 4,037 cells.

## Interpretation

Figure 1 should be used as the manuscript entry point. It documents the dataset scale, B-lineage extraction, donor retention, refined state sizes, and core QC/analysis guardrails. It pairs with Figure 2 v3, which carries the disease-associated B-cell state results.
