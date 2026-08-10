# Phase 1 Status - 2026-06-23

## Completed

- Created working `sle-bcell` conda environment.
- Downloaded Perez/GSE174188 CELLxGENE H5AD successfully.
- Inspected H5AD:
  - Cells: 1,263,676.
  - Genes/features: 30,172.
  - Candidate disease columns: `disease`, `disease_state`.
  - Donor column: `donor_id`.
  - Standard cell-type column: `cell_type`.
  - Author cell-type column: `author_cell_type`.
  - Gene symbol column: `feature_name`.
  - Existing embeddings: `X_pca`, `X_umap`.
- Confirmed B-lineage extraction:
  - `B cell`: 151,570 cells.
  - `plasmablast`: 1,411 cells.
  - Total B lineage: 152,981 cells.
- Ran 20k smoke-test B-cell subset.
- Ran 20k first-pass analysis successfully.

## Important Matrix Finding

The CELLxGENE `X` matrix contains preprocessed/scaled values, including many negative values. It must not be treated as raw counts. The current first-pass workflow uses existing `X_pca`/`X_umap` and skips raw-count normalization/log transformation.

## Smoke-Test Outputs

- `Data/processed/GSE174188_perez_cellxgene/bcell_subset_smoke_20k.h5ad`
- `03_results/first_pass_bcell_smoke_20k/figures/umap_bcell_first_pass_scores.png`
- `03_results/first_pass_bcell_smoke_20k/figures/dotplot__bcell_marker_dotplot.png`
- `03_results/first_pass_bcell_smoke_20k/tables/bcell_obs_scores.csv`
- `03_results/first_pass_bcell_smoke_20k/tables/cluster_score_summary.csv`
- `03_results/first_pass_bcell_smoke_20k/bcell_first_pass_processed.h5ad`

## Smoke-Test Interpretation

- Plasmablast score localizes strongly to the small detached UMAP island.
- Leiden cluster 7 is plasmablast-like.
- Leiden cluster 5 has the highest ABC/DN2-axis score.
- Naive B-cell scores are higher in clusters 0, 2, and 3.
- The smoke test is good enough to proceed to the full B-cell subset and full first-pass analysis.

## Full First-Pass Status

Completed after smoke test:

- Full B-lineage subset: 152,981 cells.
- Full first-pass B-cell state analysis.
- Donor-level cluster fraction tables.
- Donor-level disease tests.
- Draft state labels.
- Figure 2 draft.
- QA audit.

Key QA file:

- `00_project_management/qa_bcell_first_pass_2026-06-23.md`

Key result interpretation:

- `03_results/first_pass_bcell_full/README_interpretation.md`

## Next User-Run Commands

Run full B-cell subset:

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\02_subset_bcells_from_h5ad.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --output .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --cell-type-column cell_type `
  --pattern "B cell|plasmablast"
```

Run full first-pass analysis:

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\03_scanpy_bcell_first_pass.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --outdir .\03_results\first_pass_bcell_full `
  --gene-symbol-column feature_name `
  --matrix-mode preprocessed
```

Summarize full first-pass scores:

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\04_summarize_bcell_first_pass.py `
  --scores .\03_results\first_pass_bcell_full\tables\bcell_obs_scores.csv `
  --output .\03_results\first_pass_bcell_full\tables\cluster_score_summary.csv
```
