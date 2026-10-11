# RP v4 Stage L advisor review

## Decision

`PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION`

Stage K is accepted as a bounded uncertainty-method integration: Stage I and
WP1 are the same 68-donor contrast and do not constitute independent positive
findings. The current main figures and prior biological claims remain frozen.

## External-cohort result

Official GEO MINiML independently reconstructs 88 RNA libraries from 45 patient
IDs. Forty-three patients are paired for rN and T1T2; the primary SLE-only
paired design contains 12 active and 14 inactive patients. Patient 3553
(SLEDAI 20) and patient 428 (SLEDAI 0) have rN only and are not eligible for the
paired primary estimand. The title `SLE.0.3621.rN` maps to patient ID 3651 and
is retained as an explicit source anomaly.

GSE263716 contributes 62 ATAC libraries from 43 patient IDs, but only 36 IDs
overlap the RNA series. Patients 3651 and 1655 have different deposited SLEDAI
values across modalities. ATAC therefore cannot yet be described as same-visit
multi-omic confirmation or independent replication.

## Scientific placement

The only sufficiently differentiated external question is whether the paired
T1T2-minus-rN IFN/ISG score differs by SLE activity. A generic additional IFN
positive result would add little novelty. The paired question is promising for
an SCI Q2 manuscript but remains small and metadata-limited: age and treatment
are absent, and sex/race have almost no within-SLE variation.

## Boundaries and next gate

No expression matrix was read, no SRA payload was downloaded, and no activity
effect was fitted. The deposited processed file is RPKM and cannot satisfy the
frozen count-scale gate. Stage M may begin only after a separate authorization
for approximately 233.21 GB of SRA payload and at least 2.5 TB scratch, together
with a disease-blind GRCh38/GENCODE count pipeline, sample-to-run reconciliation,
and prospective small-sample operating-characteristic qualification.
