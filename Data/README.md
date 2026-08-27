# Public data cache

Large public matrices and archives are intentionally excluded from Git. The
2026-08-27 workspace cleanup removed the local public-data cache while retaining
the formal Phase 17 inputs required to reproduce the current R1 robustness
analysis:

- `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad`
- `phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad`

GSE135779 metadata have been restored locally. The 1.30 GB public RAW archive
and its derived B-cell H5AD are deliberately not resident after cleanup. Restore
the active external-validation source from the project root with:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\02_analysis\scripts\00_download_gse135779_validation_sources.ps1 `
  -DownloadRaw

C:\ProgramData\miniforge3\condabin\conda.bat run -n sle-bcell `
  python .\02_analysis\scripts\30_run_gse135779_bcell_validation.py
```

The downloader resumes partial files, verifies exact byte counts and uses the
Windows curl certificate workaround when needed.

The 12.2 GB GSE174188 CELLxGENE source is not required for the next external
mapping analysis because the formal raw-count and representation inputs above
are retained. It can be restored only if a pre-Gate-C2 rebuild is required:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\02_analysis\scripts\00_download_perez_gse174188_cellxgene.ps1
```

GSE163121, OneK1K/GSE196830 and unused regulatory/SRA caches are not part of the
current manuscript evidence chain and are not scheduled for restoration.
