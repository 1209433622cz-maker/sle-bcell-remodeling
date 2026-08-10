# Environment Notes

Checked on 2026-06-22.

## Available

System Python:

- Path: `D:\bioinfor\python.exe`
- Version: Python 3.13.7
- Available packages:
  - pandas 2.3.3
  - numpy 2.3.3
  - matplotlib 3.10.7
  - seaborn 0.13.2
  - scipy 1.16.2
  - scikit-learn 1.7.2
  - statsmodels 0.14.6

Bundled Codex Python:

- Path: `C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
- Version: Python 3.12.13
- Useful for document/PDF utilities, but currently missing Scanpy/Anndata/Scipy/Matplotlib in this thread environment.

## Missing

- `Rscript` is not available on PATH.
- `conda`, `mamba`, and `micromamba` are not available on PATH.
- `scanpy` and `anndata` are not installed in the available Python environments.

## Recommendation

For the first single-cell analysis pass, create a dedicated Python 3.11 or 3.12 environment rather than modifying the existing `D:\bioinfor` Python 3.13 environment.

Reason:

- Scanpy/Anndata ecosystems are more predictable on Python 3.11/3.12.
- Single-cell dependencies can be large and fragile on Windows.
- Keeping the analysis environment separate makes the future manuscript Methods section cleaner.

## Proposed Stack

- Python 3.11 or 3.12
- scanpy
- anndata
- pandas
- numpy
- scipy
- matplotlib
- seaborn
- scikit-learn
- statsmodels
- python-igraph
- leidenalg
- harmonypy

Optional later enrichment package:

- gseapy

`gseapy` is not required for Phase 1 inspection, B-cell subsetting, UMAP, clustering, or signature scoring. If it is broken on Windows, repair it later before enrichment analysis.

## Fallback

If a local Scanpy environment is difficult on Windows, use R/Seurat after installing R, or run the heavy single-cell workflow in WSL/Linux/remote HPC and keep this Windows workspace for manuscript, tables, and figure assembly.
