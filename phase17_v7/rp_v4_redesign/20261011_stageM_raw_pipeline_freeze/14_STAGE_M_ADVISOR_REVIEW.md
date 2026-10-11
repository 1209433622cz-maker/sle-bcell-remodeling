# RP v4 Stage M advisor review

## Decision

`PASS_STAGE_M_DISEASE_BLIND_PIPELINE_AND_SIMULATION_FREEZE__HOLD_RUNTIME_STORAGE_AND_DOWNLOAD_AUTHORIZATION`

## What passed

The frozen RunInfo closes exactly: 176 unique paired-end runs map to 88 unique
experiments, BioSamples and GSM libraries, with two runs per library and totals
of 752,698,793,704 bases and 233,209 MB. The
disease-blind execution map contains no patient, disease, activity, SLEDAI,
cell-type or effect field. This prevents the known GSM8180322 title typo from
being converted into a patient-identity error.

GENCODE release 50 on GRCh38.p14 primary assembly, nf-core/rnaseq 3.27.0 and
Subread featureCounts 2.1.1 are now frozen, including official resource
checksums, full-quality SRA, no trimming, automatic strandedness and within-GSM
technical-run merging. Salmon output is explicitly secondary and cannot
substitute for the required integer fragment-count matrix.

The prospective 26-patient OLS/HC3/t(23) implementation
passed all six null and two alternative synthetic scenarios. The largest null
rejection rate was 0.0436; the minimum interval coverage was
0.9564. Alternative-scenario power is descriptive and was not used
to choose an estimator.

## Why execution remains on hold

This host does not have the canonical SRA Toolkit/Nextflow/Docker/featureCounts
toolchain and no observed storage root provides the required 2.5 TB scratch. The unsigned
Stage N authorization template remains false in every approval field. No SRA
payload, reference FASTA/GTF or expression matrix was downloaded, and no
external activity coefficient was fitted.

## Scientific judgment

The paired compartment-by-activity question remains worth pursuing for an SCI
Q2 paper because it is distinct from another generic SLE IFN-positive result.
The correct next investment is infrastructure qualification and one
write-once, disease-blind count reconstruction. Reopening the score, mapper,
annotation or cohort after seeing expression would create more bias than
scientific value.
