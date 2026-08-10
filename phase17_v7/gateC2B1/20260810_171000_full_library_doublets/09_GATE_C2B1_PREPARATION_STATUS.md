# Gate C2B1 preparation status

**Status:** full raw preparation passed; complete-library doublet scoring pending.

## Validated full object

- File: `04_full_raw_counts.h5ad`
- Dimensions: 150,402 cells by 30,172 genes
- Size: 270,671,628 bytes
- SHA256: `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5`
- Working observation fields: `source_cell_index`, `donor_id`, `sample_uuid`,
  `library_uuid`, `Processing_Cohort`
- Protected outcome leakage: none
- Raw-count read-back: sampled non-zero values are non-negative integers

The HDF5 runtime was aligned after this object was written and the object was
successfully read again using h5py 3.16 with HDF5 2.1.

## QC retention

The frozen hard-QC rules excluded 2,579 of 152,981 source cells and retained
150,402. Retention is recorded by processing cohort and disease in
`02_full_qc_retention_summary.csv`; protected outcomes remain in the separate
`03_protected_outcome_metadata.csv.gz` file.

## Script validation

`phase17_c2b_02_full_library_doublets.py` passed syntax checks and an end-to-end
test on a complete 493-cell library. The test produced cell scores, checkpoint,
library summary, PNG/PDF diagnostics and a `REVIEW_REQUIRED_DO_NOT_EXCLUDE_YET`
decision with zero execution errors. The test library's automatic predicted
fraction was 6.49%; this is a software validation result, not a global dataset
estimate.

## Resume command

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1 `
  -ResumeRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B1\20260810_171000_full_library_doublets"
```

The runner reuses `04_full_raw_counts.h5ad`, checkpoints each completed library
and stops at review. No automatic doublet calls are applied to the full object.
