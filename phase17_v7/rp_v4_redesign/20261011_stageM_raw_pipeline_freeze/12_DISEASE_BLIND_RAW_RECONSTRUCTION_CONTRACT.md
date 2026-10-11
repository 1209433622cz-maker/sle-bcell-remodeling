# RP v4 Stage M disease-blind raw reconstruction contract

## Frozen input identity

- Authority: PRJNA1093470 RunInfo SHA-256 `25f5a677e283d3f3dedf957699c8c56abfdb6e41aafc09b2fb36f054fe441ad0`.
- Scope: 176 paired-end SRA runs, 88 GSM libraries,
  88 experiments and 88 BioSamples.
- Every GSM has exactly two runs. Runs may be combined only inside the same
  experiment/GSM. Different GSM libraries, cell subsets and patients are never
  merged.
- `GSM8180322` retains the deposited title anomaly. Patient identity must be
  joined later by the frozen Stage L GSM map; title parsing is prohibited.

## Reference and workflow

The only admitted workflow is SRA Toolkit 3.4.1 full-quality SRA followed by
nf-core/rnaseq 3.27.0 under Linux x86-64 Docker for STAR alignment,
strandedness inference and QC. Integer fragment counts are then produced from
the saved STAR BAM for each GSM with Subread featureCounts 2.1.1 using paired
fragment counting, both-ends and non-chimeric requirements, exon features and
`gene_id` aggregation. Salmon estimates are not the integer-count owner. The
GENCODE 50 GRCh38.p14 primary-assembly FASTA and comprehensive GTF are recorded
in `05_REFERENCE_ANNOTATION_MANIFEST.csv`; MD5 values must match before index
construction. Trimming is skipped for all libraries; raw FastQC, alignment and
MultiQC records are retained. Strandedness is inferred with the pipeline's
fixed `auto` rule and thresholds 0.8/0.1, then translated to featureCounts
0/1/2 per library. An undetermined call stops the pipeline. No sample may be
excluded because of a disease-labelled QC pattern.

## Disease firewall and count seal

The run map and nf-core samplesheet contain no patient, disease, SLEDAI,
activity, treatment, cell-type or effect field. A sealed 88-library integer
count matrix, library-level QC receipt, FASTQ/count hashes and exact tool
versions must exist before the Stage L metadata map is joined. All 12 frozen
IFN/ISG symbols must map uniquely; an absent annotation is a technical failure,
whereas an observed zero count remains zero.

## Prospective inference gate

The fixed 26-patient design (12 active, 14 inactive; intercept, activity and RNA
batch) was tested only with synthetic responses. The estimator remains OLS with
HC3 covariance and a two-sided t(23) reference. The
simulation may qualify that implementation; it cannot authorize expression
access or select a more favourable method.

## Stop rules

Stop before download when either author approval, a qualified Linux/Docker
runtime, or at least 2.5 TB scratch is absent. Stop before outcome access if any
run/library identity, checksum, count, annotation, strandedness or simulation
gate fails. Processed RPKM cannot substitute for integer counts. No automatic
repair, alternative mapper, alternative annotation, sample removal, score
change or outcome-guided rerun is permitted.
