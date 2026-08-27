# Public data cache

Large public matrices and archives are intentionally excluded from Git. The
2026-08-27 workspace cleanup removed the local public-data cache while retaining
the formal Phase 17 inputs required to reproduce the current R1 robustness
analysis:

- `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad`
- `phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad`

The GSE135779 metadata and 1.30 GB public RAW archive are the inputs to the
formal label-agnostic external sensitivity. They remain outside Git and can be
restored from the project root with:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\02_analysis\scripts\00_download_gse135779_validation_sources.ps1 `
  -DownloadRaw

powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1
```

The downloader resumes partial files, verifies exact byte counts and uses the
Windows curl certificate workaround when needed. The expected RAW archive is
1,299,783,680 bytes with SHA-256
`B5764C303AC76873738D6E05B6992277FCD6A14BF5BFCB27331E54DCBCAC619B`.
The Gate C9 runner processes all matrix cells sample by sample and does not
require a persistent derived B-cell H5AD.

The 12.2 GB GSE174188 CELLxGENE source is not required for the next external
mapping analysis because the formal raw-count and representation inputs above
are retained. It can be restored only if a pre-Gate-C2 rebuild is required:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\02_analysis\scripts\00_download_perez_gse174188_cellxgene.ps1
```

GSE163121, OneK1K/GSE196830 and unused regulatory/SRA caches are not part of the
current manuscript evidence chain and are not scheduled for restoration.
