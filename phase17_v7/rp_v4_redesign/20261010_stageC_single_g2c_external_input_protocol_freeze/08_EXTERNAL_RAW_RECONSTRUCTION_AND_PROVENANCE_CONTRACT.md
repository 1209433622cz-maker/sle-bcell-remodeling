# RP v4 external raw-input reconstruction contract

## Locked decision

Both candidates have public paired-end RNA-seq runs and are technically
reconstructable from SRA.  Neither processed RPKM nor previously deposited
normalized values may be used as if they were the frozen count/CPM scale.
Downloading and reconstruction do not unlock disease or activity outcomes.

## Provenance boundary

GSE262846 and GSE118254 use different de-identification namespaces but have
related investigator lineage.  Public token comparison cannot prove distinct
people.  Until depositor-level provenance is available they are treated as
potentially overlapping.  They must never be counted as two independent
confirmations, pooled as independent donors, or used in a two-study meta-analysis.

## Reconstruction pipeline to implement before download

1. Freeze the exact SRA run list from the two hashed NCBI RunInfo files.
2. Prefetch each SRR with SRA Toolkit; verify toolkit validation and run hashes.
3. Convert paired reads with `fasterq-dump --split-files`; compress with `pigz`.
4. Record FastQC/MultiQC metrics.  Adapter trimming is allowed only under one
   fixed `fastp` rule applied to both studies; samples are not excluded by
   disease-labelled quality patterns.
5. Align all libraries with one frozen STAR/GRCh38/GENCODE build and emit raw
   gene counts.  The genome FASTA, GTF, STAR index and software hashes must be
   frozen before the first outcome join.
6. Merge multiple runs only within the same SRA experiment/GEO library.  Never
   merge rN with T1T2 or different sorted subsets.  Donor is the inferential
   unit; libraries/subsets are repeated measurements nested in donor.
7. Require all 12 frozen IFN genes to map uniquely by approved gene symbol.
   A true zero count remains zero; an absent annotation is a technical failure,
   not a zero.  `S0` uses full assigned-library counts for CPM and the unchanged
   43-control discovery mean/SD.  `S1` uses only the frozen 18,873-symbol
   background and remains a sensitivity.
8. Seal a count-only technical object and QC receipt before joining any disease,
   activity or treatment field.

## Resource envelope

- GSE262846: 176 runs, 752.70 G bases, approximately 233.21 GB SRA payload.
- GSE118254: 85 runs, 174.96 G bases, approximately 64.37 GB SRA payload.
- Combined: approximately 297.57 GB SRA payload and 927.66 G sequenced bases.
- Reserve at least 2.5 TB temporary disk for uncompressed paired FASTQ,
  alignment scratch, counts and checksums.  Download may be delegated to the
  author workstation after the Stage D runbook is generated.

## Outcome lock

No case-control, active-inactive, SLEDAI or score-direction result may be fitted
or inspected during intake.  GSE262846 remains a candidate for a prespecified
clinical-activity analysis; GSE118254 remains a technical measurement bridge.
