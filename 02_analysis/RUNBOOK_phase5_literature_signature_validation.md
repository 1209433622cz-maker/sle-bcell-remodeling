# Phase 5 Runbook - Literature-Informed Signature Validation

This runbook regenerates the literature-informed signature validation analysis and Figure 5 v1.

## Environment

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

## Generate Figure 5

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\23_literature_signature_validation.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --labels .\03_results\first_pass_bcell_full\tables\bcell_obs_scores_labeled.csv `
  --outdir .\03_results\figure5_literature_signature_validation `
  --gene-symbol-column feature_name `
  --chunk-size 8000 `
  --min-cells 10
```

## Key Outputs

- `03_results/figure5_literature_signature_validation/figures/figure5_v1_literature_signature_validation.png`
- `03_results/figure5_literature_signature_validation/figures/figure5_v1_literature_signature_validation.pdf`
- `03_results/figure5_literature_signature_validation/literature_signature_validation_summary.md`
- `03_results/figure5_literature_signature_validation/tables/literature_informed_signature_catalog.csv`
- `03_results/figure5_literature_signature_validation/tables/donor_state_literature_signature_scores_long.csv`
- `03_results/figure5_literature_signature_validation/tables/abc_apc_vs_other_literature_signature_tests.csv`
- `03_results/figure5_literature_signature_validation/tables/state_literature_signature_summary.csv`
- `03_results/figure5_literature_signature_validation/tables/abc_apc_signature_specificity_ranks.csv`
- `03_results/figure5_literature_signature_validation/tables/signature_genes_present.csv`
- `03_results/figure5_literature_signature_validation/tables/signature_genes_missing.csv`
- `01_manuscript/figure5_v1_legend_draft.md`

## Current Numbers

- Signature genes present: 77.
- Signature genes missing: 3 (`IGHD`, `IGHM`, `DDX58`).
- Signatures evaluated: 12.
- Donor-state comparison: paired within donor, contrasting the ABC/APC-like state with the donor-specific mean across other retained states and excluding the flagged platelet/ambient-RNA-high state.
- Minimum donor-state cells for comparison: 10.
- Paired donors: 153.

## Current Interpretation

The ABC/APC-like state is specifically enriched for literature-informed ABC/DN2, low-naive-context ABC, ZEB2-linked ABC, APC/HLA B-cell, EBV/APC-like B-cell, IFN/ISG, and age-associated/atypical B-cell signatures. The TLR7/FTO innate-axis signature is not focus-state specific and should be framed cautiously.

This figure is a strong candidate for a final validation figure after formal citation audit.
