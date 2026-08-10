# Next Local Compute Tasks

Use this as the short checklist version of `02_analysis/RUNBOOK_phase1_local_compute.md`.

## User-Run Tasks

0. Open PowerShell and enter the project directory:

```powershell
cd /d H:\cuhk-2025fALL\6013RP-wyf
```

If `cd /d` fails in PowerShell, use:

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
```

1. Install Miniforge/conda if not already available:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_install_miniforge_with_winget.ps1
```

After installation, close and reopen PowerShell, then return to the project directory. If `conda --version` still fails, that is okay; the project scripts can call `C:\ProgramData\miniforge3\condabin\conda.bat` directly.

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
conda --version
```

2. Create the analysis environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_create_conda_env.ps1
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\01_check_scanpy_env_conda.ps1
```

3. Download the preferred CELLxGENE H5AD:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_perez_gse174188_cellxgene.ps1
```

4. Inspect the H5AD:

```powershell
python .\02_analysis\scripts\01_inspect_h5ad.py `
  --input .\Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad `
  --outdir .\02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene
```

5. Send these files back to Codex:

```text
02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene\basic_info.json
02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene\obs_columns_summary.csv
02_analysis\data_inventory\h5ad_inspection\GSE174188_cellxgene\var_columns_summary.csv
```

## Codex-Next Tasks After Inspection

1. Choose the correct cell-type annotation column.
2. Confirm gene symbol handling.
3. Tune the B-cell regex if needed.
4. Ask the user to run B-cell subset dry-run.
5. Ask the user to run 20k smoke-test analysis.
6. Review smoke-test figures before full B-cell computation.

## Absolute-Path Alternative

If you are not in the project directory, run scripts by absolute path:

```powershell
powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\00_install_miniforge_with_winget.ps1"
powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\00_create_conda_env.ps1"
powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\01_check_scanpy_env_conda.ps1"
powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\00_download_perez_gse174188_cellxgene.ps1"
```
