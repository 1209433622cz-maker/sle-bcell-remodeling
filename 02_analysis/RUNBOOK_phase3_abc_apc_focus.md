# Phase 3 Runbook - ABC/APC-Like Donor-Aware Focus

This runbook regenerates the donor-state pseudobulk expression analysis and Figure 3 v1 for the atypical ABC/APC-like B-cell state.

## Environment

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\01_check_scanpy_env.py
```

## 1. Donor-State Pseudobulk Expression

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\19_pseudobulk_state_expression.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --labels .\03_results\first_pass_bcell_full\tables\bcell_obs_scores_labeled.csv `
  --outdir .\03_results\figure3_abc_apc_focus `
  --gene-symbol-column feature_name `
  --chunk-size 8000 `
  --min-cells 10
```

Key outputs:

- `03_results/figure3_abc_apc_focus/tables/donor_state_gene_pseudobulk_long.csv`
- `03_results/figure3_abc_apc_focus/tables/donor_state_program_pseudobulk_long.csv`
- `03_results/figure3_abc_apc_focus/tables/donor_state_pseudobulk_groups.csv`
- `03_results/figure3_abc_apc_focus/tables/abc_apc_vs_other_gene_tests.csv`
- `03_results/figure3_abc_apc_focus/tables/abc_apc_vs_other_program_tests.csv`
- `03_results/figure3_abc_apc_focus/tables/abc_apc_program_by_disease_state.csv`
- `03_results/figure3_abc_apc_focus/pseudobulk_state_expression_summary.md`

Current pseudobulk settings:

- Focus state: `Atypical ABC/APC-like B`.
- Count source: count-like `adata.raw.X`.
- Expression unit: log1p(CP10K).
- Curated marker genes requested: 83.
- Curated marker genes present: 83.
- Curated marker genes missing: 0.
- Minimum donor-state cells for tests: 10.
- Flagged platelet/ambient-RNA-high state excluded from the comparator.

## 2. Figure 3 v1

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\20_make_figure3_abc_apc_focus.py `
  --h5ad .\03_results\first_pass_bcell_full\bcell_first_pass_labeled.h5ad `
  --donor-fractions .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fractions.csv `
  --state-tests .\03_results\first_pass_bcell_full\tables\state_level\donor_state_fraction_disease_tests.csv `
  --sensitivity-tests .\03_results\first_pass_bcell_full\marker_refinement\sensitivity\donor_state_fraction_tests_exclude_Naive_B_III_-_small_naive-like_cluster.csv `
  --program-long .\03_results\figure3_abc_apc_focus\tables\donor_state_program_pseudobulk_long.csv `
  --gene-tests .\03_results\figure3_abc_apc_focus\tables\abc_apc_vs_other_gene_tests.csv `
  --program-tests .\03_results\figure3_abc_apc_focus\tables\abc_apc_vs_other_program_tests.csv `
  --disease-summary .\03_results\figure3_abc_apc_focus\tables\abc_apc_program_by_disease_state.csv `
  --output .\03_results\figure3_abc_apc_focus\figures\figure3_v1_abc_apc_focus.png `
  --focus-table-output .\03_results\figure3_abc_apc_focus\tables\figure3_v1_focus_evidence.csv
```

Key outputs:

- `03_results/figure3_abc_apc_focus/figures/figure3_v1_abc_apc_focus.png`
- `03_results/figure3_abc_apc_focus/figures/figure3_v1_abc_apc_focus.pdf`
- `03_results/figure3_abc_apc_focus/tables/figure3_v1_focus_evidence.csv`
- `01_manuscript/figure3_v1_legend_draft.md`

## Current Numbers

- Figure 3 PNG size: 4440 x 3533 pixels.
- ABC/APC-like state size: 5,502 cells.
- Original donor-level abundance test: normal mean fraction 0.0259, SLE mean fraction 0.0549, FDR 2.67e-05.
- Sensitivity test excluding the flagged state: normal mean fraction 0.0263, SLE mean fraction 0.0562, FDR 1.68e-05.
- Paired donors in focus-state tests: 153.
- ABC ranked paired donor-state program: delta 0.861, FDR 1.47e-26.
- ABC/DN2 paired donor-state program: delta 0.441, FDR 1.47e-26.
- APC/HLA paired donor-state program: delta 0.401, FDR 1.47e-26.
- IFN-response paired donor-state program: delta 0.051, FDR 2.29e-11.

## Interpretation

Figure 3 provides donor-aware expression support for the central ABC/APC-like B-cell candidate state. The state is expanded in SLE and carries ABC/DN2, antigen-presentation, B-cell identity, and modest IFN-response signals after donor-state aggregation. This is stronger than relying on single-cell marker display alone.

## Cautions

- Treated SLE donor-state observations are few in the focus-state disease summary, so treated-specific interpretation should remain descriptive.
- Program tests use two-sided paired Wilcoxon signed-rank tests comparing each donor's focus state with that donor's mean across other retained states; they are marker-set summaries, not genome-wide disease differential expression models.
- The current result supports a mechanistic candidate state; final causal language should be avoided.
