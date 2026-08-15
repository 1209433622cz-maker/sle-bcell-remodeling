# Action record: Gate C3 metadata join and model-design freeze

**Date:** 15 August 2026

**Project:** 6013RP-wyf / v7 Phase 17

**Scope:** protected metadata unlock, join-key adjudication, sample/donor design
audit, cohort support review and pre-effect model-matrix freeze

## 1. Authorization entering this action

Gate C2B4 authorized outcome-aware analysis only for the frozen `B_CONV` and
`B_ASC` compartments and prespecified continuous programs within `B_CONV`. Hard
naive-memory composition, a platelet-positive B-cell identity and a publication
subtype for source cluster 4 remained prohibited.

The Gate C2B4 integrity manifest was independently reverified before metadata were
joined: 11/11 files passed size and SHA-256 checks.

## 2. Critical join-key finding

The first read-only audit tested whether `source_cell_index` in the 150,402-cell
primary representation was a row position in the 1,263,676-cell CELLxGENE object.
It was not:

- positional cell-ID agreement: 0/150,402;
- positional library-key agreement: 1.1%; and
- positional joining produced biologically impossible T/NK labels in the selected
  B-lineage population.

`source_cell_index` is an intermediate B-lineage workflow index. It must never be
used as a full CELLxGENE row position.

The correct key is the exact cell ID stored in `.obs_names`. Both source and primary
IDs were unique. Exact cell-ID reindexing produced:

- source rows recovered: 150,402/150,402;
- all-null joined rows: 0;
- `library_uuid` mismatches: 0;
- `sample_uuid` mismatches: 0;
- `donor_id` mismatches: 0; and
- `Processing_Cohort` mismatches: 0.

The permanent Gate C3 script now contains an explicit guard that rejects positional
interpretation of `source_cell_index`.

## 3. Metadata recovered

The protected join recovered disease, disease state, sex, age/development stage,
ethnicity, source cell-type covariate, individual covariate and technical cohort
metadata for all primary cells.

| Item | Result |
|---|---:|
| Cells | 150,402 |
| Biological samples (`sample_uuid`) | 271 |
| Sample-cohort technical strata | 332 |
| Libraries | 88 |
| Donors | 259 |
| Age range | 20-83 years |
| Repeated donors | 11 |
| `ind_cov` missing | 0 |
| `ct_cov` missing | 10,890 (7.24%) |
| Explicit non-B `ct_cov` labels | 30 (0.020%) |

`ind_cov` and `donor_id` form an exact 259-to-259 bijection. `donor_id` is frozen as
the canonical individual key; `ind_cov` is retained as an audited alias.

The `ct_cov` missingness is present in the source CELLxGENE metadata. It was not
caused by an unfinished local run or a failed previous command. Missing values are
retained and quantified. The 30 explicit non-B source labels are not removed from
the primary model; their exclusion is a prespecified sensitivity analysis because
C2B4 identity assignment is independent of `ct_cov`.

## 4. Hierarchy and replication unit

Every library belongs to exactly one `Processing_Cohort`, but 53 biological samples
occur in more than one cohort. The observed sample overlap matrix was:

| | C1 | C2 | C3 | C4 |
|---|---:|---:|---:|---:|
| C1 | 47 | 19 | 8 | 0 |
| C2 | 19 | 140 | 14 | 25 |
| C3 | 8 | 14 | 50 | 3 |
| C4 | 0 | 25 | 3 | 95 |

Consequently:

- biological replicate: `sample_uuid`;
- technical analysis stratum: `sample_uuid x Processing_Cohort`;
- individual clustering/blocking key: `donor_id`; and
- processing cohort cannot be collapsed to one arbitrary sample-level value.

No cell is treated as an independent biological replicate.

## 5. Frozen cell-count threshold

The primary threshold is at least 50 frozen B cells per sample-cohort stratum.
Prespecified sensitivity thresholds are 20 and 100 cells. At 50 cells, 315 of 332
technical strata remain eligible.

Eligible stratum counts were:

| Cohort | Normal | Managed | Flare | Treated |
|---|---:|---:|---:|---:|
| 1 | 47 | 0 | 0 | 0 |
| 2 | 22 | 113 | 0 | 0 |
| 3 | 18 | 4 | 16 | 5 |
| 4 | 43 | 47 | 0 | 0 |

Cohort 1 contains no disease contrast and is restricted to technical/reference QC.
Cohort-3 treated and managed strata are too sparse for confirmatory inference.

## 6. Frozen model matrices

No abundance effect estimate was calculated or inspected before freezing the
following matrices.

### Primary managed-state analysis

- ID: `C3A_PRIMARY_C4_MANAGED_VS_NORMAL`
- cohort: 4;
- strata: 90;
- normal/managed: 43/47;
- sex: all female, therefore not included as a non-varying covariate;
- fixed effects: managed status, centered age and Asian ethnicity indicator; and
- matrix rank: 4/4.

Cohort 4 is the primary comparison because its disease groups have similar age and
balanced Asian/European-American representation.

### Internal managed-state replication

- ID: `C3A_VALIDATION_C2_EUROPEAN_FEMALE`
- cohort: 2;
- restriction: European-American females;
- strata: 64;
- normal/managed: 21/43;
- fixed effects: managed status and centered age; and
- matrix rank: 3/3.

This is directional internal replication, not an independent external cohort. Age
remains imbalanced and must be reported as a limitation even after adjustment.

### Secondary flare-state analysis

- ID: `C3A_SECONDARY_C3_FLARE_VS_NORMAL`
- cohort: 3;
- strata: 34;
- normal/flare: 18/16;
- fixed effects: flare status, centered age and European-American indicator; and
- matrix rank: 4/4.

This analysis is secondary and cannot replace managed-state replication.

## 7. Statistical contract

The response is `B_ASC` cells out of all frozen B cells in each eligible stratum.
Zero-ASC samples remain in the count likelihood. The planned primary model is a
sample-stratum beta-binomial or equivalent overdispersed count model, with
donor-clustered or donor-random-effect uncertainty if repeated donors enter a
contrast.

Prespecified sensitivities are:

- minimum B-cell thresholds of 20 and 100;
- exclusion of only explicit non-B `ct_cov` cells;
- exclusion of `residual_doublet_auto_call` cells; and
- two-part ASC presence/positive-abundance analysis.

Covariates, cohorts and thresholds cannot be changed after viewing disease effects.

## 8. Files implemented

- `audit_tools/phase17_c3_01_unlock_metadata_and_freeze_design.py`;
- `audit_tools/run_6013RP_phase17_gateC3_metadata_design.ps1`;
- `phase17_v7/gateC3/20260815_metadata_design`; and
- pointer `phase17_v7/gateC3/_LATEST_GATE_C3.txt`.

The result directory includes the local cell-level gzip, sample and sample-cohort
count tables, donor audit, missingness audit, cohort-overlap table, three frozen
model matrices, JSON/Markdown contracts, vector/raster figures and an integrity
manifest.

## 9. Figure quality review

The four-panel design audit shows eligible cohort-state counts, B-cell depth by
cohort, sample overlap between cohorts and protected-field missingness. It contains
no disease effect estimate. Panel labels, text fit, threshold visibility, matrix
annotations and vector/PDF output were visually checked.

## 10. Gate decision

Decision:

`PASS_GATE_C3_METADATA_JOIN_AND_MODEL_DESIGN_FREEZE`

All join, invariant, support and model-rank checks passed. Gate C3A is authorized to
fit the frozen abundance models. Hard naive-memory labels remain prohibited, and no
manuscript disease claim is yet authorized.

## 11. Verification performed

- Python compilation: passed.
- PowerShell parsing: passed.
- End-to-end launcher run under `conda run`: passed.
- C2B4 input integrity: 11/11 passed.
- C3 output integrity: 21/21 files and 8,246,411 bytes independently rechecked.
- Figure visual inspection: passed.
- Git diff whitespace check: passed before commit.

## 12. Immediate next objective

Fit Gate C3A exactly from the frozen matrices, report effect sizes and uncertainty
before significance labels, and execute every prespecified sensitivity. A managed
effect is eligible for manuscript prioritization only if cohort 4 is supported and
cohort 2 has concordant direction. Cohort-3 flare findings remain secondary.
