# Gate C4A pre-effect raw-count and program contract

**Status:** `PRE_EFFECT_FROZEN`

- Raw counts: 150,402 cells x 30,172 Ensembl features
- Raw H5AD SHA256: `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5`
- Exact Gate C3 cell-ID set and row order: verified
- Primary branch: all hard-QC cells
- Sensitivity branch: residual-risk automatic calls excluded
- B_CONV minimum cells per sample-cohort pseudobulk: 50
- Primary B_CONV design: n=89
- Internal validation B_CONV design: n=64
- Secondary flare B_CONV design: n=34
- Frozen programs: 9; primary multiplicity family: 4
- Disease expression coefficients inspected: False

## Binding restrictions

- cell-level differential expression
- scaled source X for count modeling
- source_cell_index as a full-source row position
- hard naive-memory composition
- outcome-adaptive program membership
- B_ASC gene-level disease inference without support-gate authorization