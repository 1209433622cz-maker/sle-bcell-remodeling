# Gate C4A raw pseudobulk and program-freeze advisor decision

**Decision:** `PASS_GATE_C4A_BCONV_RAW_PSEUDOBULK_AND_PROGRAM_FREEZE`

- B_CONV gene-level pseudobulk authorized: True
- B_CONV continuous-program models authorized: True
- B_ASC gene-level disease pseudobulk authorized: False
- Primary B_CONV design: n=89 (43 normal / 46 managed)
- Validation B_CONV design: n=64 (21 normal / 43 managed)
- Flare B_CONV design: n=34 (18 normal / 16 flare)
- Programs available: 9/9; minimum gene coverage=100.0%
- Disease expression coefficients inspected: False

## Checks

- [PASS] extraction_status: EXTRACTION_COMPLETE_REVIEW_REQUIRED
- [PASS] effect_blind_contract: no disease expression coefficient inspected
- [PASS] raw_checksum: DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5
- [PASS] exact_cell_ids: set=True; order=True
- [PASS] raw_keys_concordant: {"Processing_Cohort": 0, "donor_id": 0, "sample_uuid": 0}
- [PASS] raw_integer_nonnegative: source range=1-7836; final integer=True
- [PASS] pseudobulk_shape: matrix=(1328, 30172); rows=1328; genes=30172
- [PASS] pseudobulk_library_sizes: matrix row sums equal row metadata
- [PASS] raw_count_conservation: raw=323179379; all-hard-QC=323179379
- [PASS] per_gene_count_conservation: all-hard-QC mismatches=0; sensitivity mismatches=0
- [PASS] dual_branch_cell_counts: all=150402; sensitivity=148430
- [PASS] gene_ids_unique: unique=30172; total=30172
- [PASS] primary_bconv_support: n=89; normal=43; managed=46
- [PASS] validation_bconv_support: n=64; normal=21; managed=43
- [PASS] flare_bconv_support: n=34; normal=18; flare=16
- [PASS] design_ranks: primary=4/4; validation=3/3; flare=4/4
- [PASS] replication_nonoverlap_support: [{"analysis":"validation","frozen_n":64,"shared_samples_with_primary":10,"shared_donors_with_primary":10,"nonoverlap_n":54,"nonoverlap_reference_n":21,"nonoverlap_exposed_n":33},{"analysis":"flare","frozen_n":34,"shared_samples_with_primary":3,"shared_donors_with_primary":4,"nonoverlap_n":30,"nonoverlap_reference_n":15,"nonoverlap_exposed_n":15}]
- [PASS] program_dictionary_frozen: programs=9; primary=4
- [PASS] program_gene_availability: minimum=1.000
- [PASS] hard_label_guard: continuous within-B_CONV programs only

## Binding interpretation

B_CONV raw-count pseudobulk and continuous-program analysis may proceed. B_ASC gene-level disease pseudobulk is not authorized because per-group sample support is inadequate.

## Next stage

install and validate a negative-binomial pseudobulk engine, then fit Gate C4B exactly from the frozen B_CONV matrices and programs