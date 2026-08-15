# Action record: Gate C4A raw pseudobulk and program freeze

**Date:** 15 August 2026

**Project:** 6013RP-wyf / v7 Phase 17

**Scope:** authoritative raw-count selection, resumable dual-branch pseudobulk
aggregation, per-gene count-conservation audit, B_CONV/B_ASC support adjudication,
disease-blind continuous-program freeze and pre-effect Gate C4B design freeze

## 1. Authorization entering this action

Gate C3A rejected managed-state ASC composition as a central manuscript claim but
authorized continuous-program and gene-level transcription analysis within the
frozen two-compartment identity model. The only hard identities remain `B_CONV`
and `B_ASC`; hard naive-memory, ABC, platelet-associated or source-cluster-4
publication subtypes remain prohibited.

Before extraction, the Gate C3 and Gate C3A manifests were reverified: 21/21 and
14/14 files passed size and SHA-256 checks. No disease expression coefficient was
calculated or inspected during Gate C4A.

## 2. Authoritative raw-count input adjudication

The Gate C2B2 representation H5AD intentionally contains no expression matrix and
cannot support pseudobulk. Initial planning therefore anticipated returning to the
12.2-GB full CELLxGENE source `.raw.X`.

A more efficient already-audited input was then identified:

`phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad`

This file is the hard-QC output created before representation learning. It contains
the exact 150,402 retained cells and all 30,172 Ensembl features as sparse raw
integer counts.

| Input check | Result |
|---|---:|
| File size | 270,671,628 bytes |
| SHA-256 | `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5` |
| Cells | 150,402 |
| Features | 30,172 |
| Exact Gate C3 cell-ID set | PASS |
| Exact Gate C3 row order | PASS |
| Sample/donor/cohort key mismatches | 0/0/0 |
| Negative or fractional nonzero counts | 0 |

Using this file avoids rescanning unrelated PBMCs while preserving the same
authoritative raw counts. `source_cell_index` was not used as a full-source row
position.

## 3. Resumable dual-branch aggregation

The extractor processes 5,000 cells per chunk and writes contract-bound sparse
checkpoints. Thirty-one chunks cover all 150,402 cells. A checkpoint is reused only
when its raw-input hash, cell-metadata hash, matrix shape, branch definitions and
row-mapping contract match exactly.

Two branches were aggregated simultaneously:

- primary: all 150,402 hard-QC cells; and
- sensitivity: 148,430 cells after excluding 1,972 automatic residual-risk calls.

Each branch contains both frozen compartments across all 332 sample-cohort strata.
The final row structure is therefore:

`2 branches x 2 compartments x 332 strata = 1,328 pseudobulk rows`.

## 4. Raw-count and pseudobulk results

| Quantity | Result |
|---|---:|
| Raw nonzero values | 103,783,938 |
| Raw nonzero range | 1-7,836 |
| Raw UMI total | 323,179,379 |
| Sensitivity-branch UMI total | 318,588,065 |
| Pseudobulk dimensions | 1,328 x 30,172 |
| Pseudobulk nonzero entries | 9,384,987 |
| Local sparse count file size | 24,099,636 bytes |

All-hard-QC pseudobulk UMI sums equal the source raw-count UMI total exactly.
Pseudobulk row sums also equal their row-metadata library sizes exactly.

## 5. Independent per-gene conservation

The review stage independently rereads the raw H5AD in 10,000-cell blocks and
sums every one of the 30,172 gene columns. These direct column sums are compared
with the final pseudobulk column sums for both branches.

| Branch | Genes compared | Mismatched genes | Maximum absolute difference |
|---|---:|---:|---:|
| All hard-QC | 30,172 | 0 | 0 |
| Residual-risk negative | 30,172 | 0 | 0 |

This verifies count conservation at gene resolution rather than only at total-UMI
resolution.

## 6. Frozen B_CONV model support

Gate C4B uses at least 50 `B_CONV` cells per sample-cohort pseudobulk. The resulting
effect-free designs are:

| Analysis | Normal | Exposed | Total | Rank |
|---|---:|---:|---:|---:|
| Cohort-4 managed primary | 43 | 46 managed | 89 | 4/4 |
| Cohort-2 European-female validation | 21 | 43 managed | 64 | 3/3 |
| Cohort-3 flare secondary | 18 | 16 flare | 34 | 4/4 |

The primary C4B matrix has one fewer sample than C3A. The excluded managed sample
`c21e0e54-2ea8-4fc7-9438-5d2d8d63899c` contains 44 `B_CONV` and 11 `B_ASC` cells:
it passed the earlier total-B-cell threshold but does not pass the frozen
within-B_CONV pseudobulk threshold.

Primary cohort-4 threshold support remains adequate:

| Minimum B_CONV cells | Normal | Managed | Total |
|---|---:|---:|---:|
| 20 | 44 | 50 | 94 |
| 50 | 43 | 46 | 89 |
| 100 | 41 | 46 | 87 |

These counts are unchanged in the residual-risk-negative branch. The 50-cell
matrix is primary; 20 and 100 cells are frozen sensitivities.

## 7. Replication independence

Relative to the 89-sample primary B_CONV design:

| Analysis | Frozen n | Shared samples | Shared donors | Nonoverlap n | Reference/exposed |
|---|---:|---:|---:|---:|---:|
| Cohort-2 validation | 64 | 10 | 10 | 54 | 21/33 |
| Cohort-3 flare | 34 | 3 | 4 | 30 | 15/15 |

The cohort-2 nonoverlap subset is a strengthened internal sensitivity, not an
independent external cohort.

## 8. B_ASC pseudobulk no-go

B_ASC composition remains a valid hard compartment, but gene-level disease
pseudobulk requires adequate numbers of ASC cells in enough independent samples.
That requirement fails.

At a minimum of 10 ASC cells:

- primary: 7 normal and 9 managed strata;
- validation: 1 normal and 1 managed stratum; and
- flare: 1 normal and 4 flare strata.

At a minimum of 20 ASC cells:

- primary: 1 normal and 4 managed strata;
- validation: 0 normal and 1 managed stratum; and
- flare: 0 normal and 1 flare stratum.

Decision: B_ASC gene-level disease differential expression is not authorized. The
Gate C3A flare composition signal cannot be converted into a mechanistic claim by
fitting sparse or zero-dominated ASC pseudobulks.

## 9. Disease-blind continuous-program freeze

Nine exact program/QC dictionaries were frozen before disease expression effects:

- primary family: naive-to-memory, atypical/low-naive, APC/HLA and IFN/ISG;
- secondary context: activation/stress and TLR7/innate;
- QC only: platelet/ambient overlay;
- identity QC only: ASC/UPR and pan-B programs.

All requested genes are present. Coverage is 100% for all 9 programs, with no
duplicate-symbol matches among requested genes.

The frozen score is computed from TMM logCPM B_CONV pseudobulks: genes are z-scored
within each frozen contrast, then the mean negative-gene z score is subtracted from
the mean positive-gene z score. Primary multiplicity is BH correction across the
four primary program coefficients. Program membership cannot change after effects
are inspected.

## 10. Gene-level contract

The preferred model is edgeR TMM with robust quasi-likelihood and `filterByExpr`
applied before coefficient inspection within each frozen contrast. The inferential
unit is the sample-cohort B_CONV pseudobulk. Genome-wide BH FDR is applied within
contrast.

Scaled expression, cell-level tests, outcome-adaptive gene sets and B_ASC disease
pseudobulk are prohibited. The residual-risk-negative branch and 20/100-cell
thresholds are required sensitivities.

## 11. Figure quality control

The effect-free four-panel figure shows:

- B_CONV support by cohort and disease state;
- collapse of per-group B_ASC support as its cell threshold increases;
- exact program-gene availability; and
- B_CONV pseudobulk library-size distributions by processing cohort.

The first rendering clipped long program IDs in Panel C and was rejected. It was
regenerated with concise publication labels, fixed biological ordering, readable
axis text and no clipping or overlap. PNG and PDF outputs passed visual review.

## 12. Files and integrity

Implemented files:

- `audit_tools/phase17_c4a_01_extract_raw_pseudobulk.py`;
- `audit_tools/phase17_c4a_02_review_freeze.py`;
- `audit_tools/run_6013RP_phase17_gateC4A_raw_pseudobulk_freeze.ps1`;
- `phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze`; and
- pointer `phase17_v7/gateC4A/_LATEST_GATE_C4A.txt`.

The count NPZ, gene-universe gzip and checkpoint directory are local recomputable
artifacts and are excluded from Git. Their sizes and hashes remain in the Gate C4A
integrity manifest. The complete PowerShell entry point was rerun using all 31
existing checkpoints and reproduced the same pass decision.

## 13. Verification performed

- Python compilation: passed.
- PowerShell parsing: passed.
- Gate C3 input integrity: 21/21 passed.
- Gate C3A input integrity: 14/14 passed.
- Raw H5AD SHA-256: passed.
- Exact cell-ID set/order and metadata keys: passed.
- Full-matrix non-negative integer audit: passed.
- Total UMI conservation: passed.
- Per-gene conservation in both branches: 30,172/30,172 passed.
- Pseudobulk row metadata and matrix dimensions: passed.
- Three design support and rank checks: passed.
- Nine program-availability checks: passed.
- Complete checkpoint-resume workflow: passed.
- Figure visual inspection: passed after one correction.
- Manifest size/hash recheck: passed.

## 14. Gate decision

Decision:

`PASS_GATE_C4A_BCONV_RAW_PSEUDOBULK_AND_PROGRAM_FREEZE`

- B_CONV gene-level pseudobulk: authorized.
- B_CONV continuous programs: authorized.
- B_ASC gene-level disease pseudobulk: not authorized.
- Disease expression effects inspected: no.

## 15. Immediate next objective

Begin Gate C4B with a software-qualification gate. Install and lock a validated
negative-binomial pseudobulk engine, verify count import and model recovery on
synthetic and frozen no-effect test matrices, and only then fit the exact frozen
B_CONV primary, validation, nonoverlap and flare contrasts.
