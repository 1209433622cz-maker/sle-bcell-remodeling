# Phase 1 Local Compute Runbook

This runbook is written for the user to run large downloads and heavier compute locally.

Goal: get from public Perez/GSE174188 processed data to a first B-cell subset and first-pass Scanpy figures.

## Before Running Commands

The scripts are inside:

```text
H:\cuhk-2025fALL\6013RP-wyf
```

Either enter the project directory first:

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

Or call scripts with absolute paths, for example:

```powershell
powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\00_create_conda_env.ps1"
```

## Route Choice

### Preferred Formal Route: CELLxGENE/HCA H5AD

Pros:

- Clean public processed-data provenance.
- Direct H5AD format for Scanpy/Anndata.
- Easier to describe in Methods.

Cons:

- Large download: about 12.2 GB.
- First read/subset may require substantial RAM and disk space.

Script:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_perez_gse174188_cellxgene.ps1
```

Expected output:

```text
Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad
```

If the download is interrupted, do not delete the partial file. Rerun the same script; it resumes from the existing file and retries until the expected 12,218,105,530 bytes are present.

### Backup Fast Route: Zenodo BPCells Conversion

Pros:

- Smaller download: about 1.5 GB total.
- Includes extracted metadata and BPCells matrix archive.

Cons:

- It is a third-party 2026 redistribution/conversion.
- BPCells is R-oriented; extra conversion work may be needed before Scanpy.

Script:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_perez_gse174188_zenodo.ps1
```

Expected output:

```text
Data\processed\GSE174188_perez_zenodo_20406617\
```

## Environment Setup

Recommended: install Miniforge first, then create the analysis environment.

If `conda` is not recognized, install Miniforge with:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_install_miniforge_with_winget.ps1
```

After installation, close and reopen PowerShell, return to the project directory, and check:

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
conda --version
```

If `conda --version` still fails, continue anyway. The project scripts can call the installed Miniforge directly from `C:\ProgramData\miniforge3\condabin\conda.bat`.

Create and verify the environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_create_conda_env.ps1
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\01_check_scanpy_env_conda.ps1
```

Expected success message:

```text
Environment check passed for Phase 1.
```

If `gseapy` is reported as optional missing or broken, continue. It is only needed later for enrichment analysis, not for Phase 1 inspection, B-cell extraction, clustering, UMAP, or signature scoring.

## Step 1: Inspect H5AD

Run after the CELLxGENE H5AD is downloaded. If `conda activate sle-bcell` works, use:

```powershell
conda activate sle-bcell
python .\02_analysis\scripts\01_inspect_h5ad.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --outdir .\02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene
```

If `conda activate` does not work, use the PATH-independent command:

```powershell
& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell python .\02_analysis\scripts\01_inspect_h5ad.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --outdir .\02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene
```

Expected outputs:

```text
02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene\basic_info.json
02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene\obs_columns_summary.csv
02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene\var_columns_summary.csv
```

After this step, send me or inspect:

- `basic_info.json`
- `obs_columns_summary.csv`
- `var_columns_summary.csv`

The important decision is which `obs` column contains usable cell-type labels.

Observed for Perez/GSE174188 CELLxGENE H5AD:

- `cell_type` is the best public-standard B-lineage extraction column.
- B-lineage labels are `B cell` and `plasmablast`.
- `author_cell_type` also works conceptually with `B` and `PB`, but Windows command quoting is easier with `cell_type`.
- Gene symbols are stored in `var["feature_name"]`.
- `X` contains preprocessed/scaled values with many negative entries, so do not run raw-count normalization/log1p on this H5AD.

## Step 2: Dry-Run B-Cell Matching

Replace `CELL_TYPE_COLUMN_HERE` with the real column identified in Step 1.

```powershell
python .\02_analysis\scripts\02_subset_bcells_from_h5ad.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --output .\Data\processed\GSE174188_perez_cellxgene\bcell_subset.h5ad `
  --cell-type-column cell_type `
  --pattern "B cell|plasmablast" `
  --dry-run
```

Expected output:

- A list of matched labels.
- Number of matched cells.
- No file written.

## Step 3: Smoke-Test B-Cell Subset

This writes only the first 20,000 matched B cells. Use it to confirm that the pipeline works before making the full subset.

```powershell
python .\02_analysis\scripts\02_subset_bcells_from_h5ad.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --output .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_smoke_20k.h5ad `
  --cell-type-column cell_type `
  --pattern "B cell|plasmablast" `
  --max-cells 20000
```

## Step 4: Smoke-Test First-Pass Scanpy

```powershell
python .\02_analysis\scripts\03_scanpy_bcell_first_pass.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_smoke_20k.h5ad `
  --outdir .\03_results\first_pass_bcell_smoke_20k `
  --max-cells 20000 `
  --gene-symbol-column feature_name `
  --matrix-mode preprocessed
```

Expected outputs:

```text
03_results\first_pass_bcell_smoke_20k\figures\
03_results\first_pass_bcell_smoke_20k\tables\bcell_obs_scores.csv
03_results\first_pass_bcell_smoke_20k\bcell_first_pass_processed.h5ad
```

## Step 5: Full B-Cell Subset

Run only after smoke test succeeds.

```powershell
python .\02_analysis\scripts\02_subset_bcells_from_h5ad.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --output .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --cell-type-column cell_type `
  --pattern "B cell|plasmablast"
```

## Step 6: Full First-Pass Scanpy

Run only after full B-cell subset succeeds.

```powershell
python .\02_analysis\scripts\03_scanpy_bcell_first_pass.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad `
  --outdir .\03_results\first_pass_bcell_full `
  --gene-symbol-column feature_name `
  --matrix-mode preprocessed
```

## What To Send Back To Me

After Step 1:

- `basic_info.json`
- `obs_columns_summary.csv`
- `var_columns_summary.csv`

After smoke test:

- The terminal output.
- The generated UMAP and dotplot PNGs from `03_results\first_pass_bcell_smoke_20k\figures`.

After full run:

- `03_results\first_pass_bcell_full\figures`
- `03_results\first_pass_bcell_full\tables\bcell_obs_scores.csv`

## Stop Conditions

Stop and send me the error/output if:

- The H5AD inspection fails.
- No B-cell labels are matched in dry run.
- Memory usage becomes unstable during full subset.
- The UMAP has no structure or marker scores look blank.
