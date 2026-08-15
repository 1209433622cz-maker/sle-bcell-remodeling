# Gate C3 protected-metadata and model-design audit

**Decision:** `PASS_GATE_C3_METADATA_JOIN_AND_MODEL_DESIGN_FREEZE`

- Cells joined by exact cell ID: 150,402
- Biological samples: 271
- Sample-cohort technical strata: 332
- Libraries: 88
- Donors: 259
- `ct_cov` missing: 10,890 (7.24%)
- Explicit non-B `ct_cov` labels: 30
- Effect estimates inspected: False

## Checks

- [PASS] gate_c2b4_integrity: 11/11 rows verified
- [PASS] gate_c2b4_scope: two-compartment composition and prespecified continuous within-conventional programs
- [PASS] cell_id_join_complete: 150402/150402 cell IDs joined; all-null rows=0
- [PASS] cell_ids_unique: primary=True; source=True
- [PASS] key_concordance: library_uuid mismatches=0; sample_uuid mismatches=0; donor_id mismatches=0; Processing_Cohort mismatches=0
- [PASS] join_method_guard: cell-ID join required; positional source_cell_index library match=0.011
- [PASS] two_compartment_assignment_complete: assigned=150,402/150,402
- [PASS] sample_metadata_invariants: conflicting sample-field groups=0
- [PASS] library_cohort_invariant: libraries with multiple cohorts=0
- [PASS] donor_metadata_invariants: conflicting donor-field groups=0
- [PASS] donor_ind_cov_bijection: donor->multiple ind_cov=0; ind_cov->multiple donor=0
- [PASS] age_complete: age range=20-83
- [PASS] explicit_non_b_localized: explicit non-B ct_cov labels=30/150402; sensitivity only
- [PASS] primary_design_support: cohort 4 normal=43; managed=47
- [PASS] primary_design_full_rank: rank=4/4; n=90
- [PASS] validation_design_support: cohort 2 European-female normal=21; managed=43
- [PASS] validation_design_full_rank: rank=3/3; n=64
- [PASS] flare_design_support: cohort 3 normal=18; flare=16
- [PASS] flare_design_full_rank: rank=4/4; n=34

## Binding interpretation

The metadata join and three prespecified model matrices are frozen. Gate C3A may fit sample-level abundance models without changing cohorts, cutoffs or covariates after effect inspection.