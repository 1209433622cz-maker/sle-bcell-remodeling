# Action record: Gate C5A GSE135779 source, mapping and design freeze

Date: 2026-08-15
Project: 6013RP-wyf / Phase 17 v7
Gate: C5A
Final decision: `PASS_GATE_C5A_TO_FROZEN_EXTERNAL_EFFECT_MODELING`

## 1. Objective and governance

This round prepared GSE135779 for genuinely independent SLE validation of the
Gate C4B conventional-B-cell transcriptional result. It was deliberately completed
without estimating or inspecting any new external disease coefficient.

The workflow froze source integrity, matrix-to-metadata joins, disease-blind B-cell
mapping, pseudobulk counts, program membership, sample-support thresholds and model
matrices before authorizing Gate C5B. Existing GSE135779 effect tables remain legacy
feasibility outputs and were not used as confirmatory evidence or design input.

## 2. Source inventory and integrity

Six local source files were hashed. The principal assets were:

| Asset | Size (bytes) | SHA256 |
|---|---:|---|
| `GSE135779_RAW.tar` | 1,299,783,680 | `B5764C303AC76873738D6E05B6992277FCD6A14BF5BFCB27331E54DCBCAC619B` |
| `GSE135779_genes.tsv.gz` | 257,271 | `53D571FC7422E854D4884D6497106EA7C138AD776012598713E7C72B0AF1D23C` |
| childhood-only metadata | 20,902,801 | `5704FC8626A7AEBF113D933D49A6275BE02CE1AC9FDFE7724E92D81DCD897A15` |
| childhood-plus-adult metadata | 22,285,464 | `B3530E5E222BFC0EF81A1F1B63A8FABC345B03A53CD0CF922D39C2950C85E25F` |

The raw archive contains exactly 56 barcode files and 56 Matrix Market files. All
112 compressed members were hashed during source processing and independently
rehashed during review. No source-file or tar-member integrity failure was found.

The gene table contains 32,738 rows and unique Ensembl identifiers. Ninety-five
gene-symbol duplicates exist and must be summed by symbol only where a program score
requires symbols; Ensembl remains the unique gene-level key. No frozen program gene
is affected by a duplicated source symbol.

## 3. The 58-to-56 donor discrepancy

The authoritative extended metadata contains 58 donors, but raw matrices exist for
56. The two metadata-only adult donors are:

| Matrix sample | Donor | Group | B-labelled metadata cells |
|---|---|---|---:|
| `JB19002` | `aHD2` | HC | 402 |
| `JB19016` | `aSLE8` | SLE | 211 |

The omission is balanced at one HC and one SLE donor. These donors cannot enter any
expression analysis because no count matrix is present. They are documented rather
than imputed, reconstructed or represented as zero-count samples.

## 4. Metadata-version audit

The childhood-only file and the childhood subset of the extended file contain the
same 44 sample identifiers but are not cell-identical:

- childhood-only rows: 252,279;
- extended-version childhood rows: 252,348;
- exact sample-plus-barcode matches: 249,136;
- aggregate barcode Jaccard: 0.9751;
- mean per-sample Jaccard: 0.9706; and
- minimum per-sample Jaccard: 0.7553 for `JB17019`.

The extended `Meta_caSLE_processed_08092021_small.csv` file is frozen as the sole
authoritative annotation because it defines both age strata in one version. The
childhood-only file is retained for provenance and version sensitivity only. The two
files must never be concatenated or treated as independent cohorts.

## 5. Barcode and raw-count accounting

Across the 56 matrices:

| Quantity | Count |
|---|---:|
| Matrix barcodes | 363,083 |
| Extended-metadata rows for matrix samples | 321,110 |
| Exact matched metadata barcodes | 321,106 |
| Metadata barcodes absent from matrices | 4 |
| Matrix barcodes without extended metadata rows | 42,977 |
| Full-matrix UMI | 1,375,427,998 |

The four metadata-without-matrix barcodes occur in `JB17015`, `JB17016`, `JB17019`
and `JB18064`, one per sample. All four carry monocyte labels, so they do not alter
the frozen B or PC compartments. They remain explicit in
`03A_METADATA_BARCODE_EXCEPTIONS.csv`.

Every matrix had 32,738 gene rows and non-negative integer counts. The 42,977 raw
matrix barcodes lacking processed metadata were excluded because no defensible
source label is available; they were not assigned using disease status or de novo
clustering after outcome inspection.

## 6. Disease-blind identity mapping

The source annotation was mapped before external effects as follows:

- all eight `B-caSC0` to `B-caSC7` labels -> `B_CONV_ANALOG`;
- both `PC-caSC0` and `PC-caSC1` labels -> `B_ASC_CONTROL`; and
- disease label, SLEDAI and effect enrichment were not used in the mapping.

This supports a broad conventional-B analog, not hard naive, memory or atypical
subtype identities. Plasma/ASC cells are an identity and contamination control only
and are prohibited as the conventional-B confirmatory endpoint.

The mapping yielded 32,179 B_CONV-analog cells with 99,161,064 UMI and 850 PC/ASC
control cells with 6,854,436 UMI. For every sample, source-label pseudobulks summed
exactly to their corresponding compartment pseudobulk.

## 7. Frozen pseudobulk and designs

The integer pseudobulk object contains 672 rows by 32,738 Ensembl features: for each
of 56 samples, two compartment rows and ten source-label rows. Independent review
confirmed dtype, row sums, feature uniqueness and label-to-compartment conservation.

| Frozen analysis | Minimum B cells | Samples | HC | SLE | Design | Rank |
|---|---:|---:|---:|---:|---|---:|
| Combined primary context | 50 | 54 | 16 | 38 | intercept + SLE + adult | 3/3 |
| Childhood primary | 50 | 43 | 11 | 32 | intercept + SLE | 2/2 |
| Adult secondary | 50 | 11 | 5 | 6 | intercept + SLE | 2/2 |
| Combined threshold sensitivity | 20 | 56 | 16 | 40 | intercept + SLE + adult | 3/3 |
| Combined threshold sensitivity | 100 | 51 | 16 | 35 | intercept + SLE + adult | 3/3 |

Childhood >=50 is the primary independent endpoint. Combined >=50 with age-stratum
adjustment is the prespecified complementary estimate. Adult >=50 is secondary due
to only 5 HC and 6 SLE donors. Sex, treatment and other complete confounder fields
are absent from the local processed metadata and cannot be added post hoc.

## 8. Frozen programs

The exact Gate C4A dictionary was carried forward without membership changes. All
signed arms meet the predeclared 80% availability threshold. The central IFN/ISG
program contains 12 frozen genes and all 12 are present. ASC/UPR and platelet control
arms each retain 9/10 genes; all four confirmatory program arms have 100% coverage.

A prior management document incorrectly described IFN/ISG as a 13-gene program.
That wording was corrected to 12 genes in this round. The statistical dictionary and
all completed C4 analyses already used the correct 12 genes, so no result changed.

## 9. Independent decision and visual QC

The independent reviewer rehashed all sources and archive members, reconstructed
sample/gene/count checks, audited the two metadata versions, verified the four
barcode exceptions, reloaded the pseudobulk object, tested all conservation laws,
recreated program coverage and checked all five model-matrix ranks.

Every gate check passed. The decision is
`PASS_GATE_C5A_TO_FROZEN_EXTERNAL_EFFECT_MODELING`. The disease-blind four-panel QC
figure was inspected at full resolution; labels, axes, thresholds and panel spacing
are readable without overlap. It contains source/support information only and does
not reveal disease effects.

## 10. Reproducibility assets

Added:

- `audit_tools/phase17_c5a_01_source_mapping_freeze.py`;
- `audit_tools/phase17_c5a_02_review_freeze.py`; and
- `audit_tools/run_6013RP_phase17_gateC5A_gse135779_freeze.ps1`.

The launcher completed source reconstruction and independent review end to end. The
integrity manifest covers 27 pre-manifest artifacts. The 11.39 MB NPZ count matrix
and compressed gene universe are local recomputable objects governed by hashes;
compact metadata, decisions, audit tables and PNG/PDF QC outputs are repository
artifacts.

A pre-commit portability audit detected that the initial Windows run wrote text
tables with CRLF while repository attributes require LF. Git normalization would
therefore have invalidated byte-level manifest hashes after a fresh checkout. Both
generators were changed to write LF explicitly, and the entire source and review
workflow was rerun. The final 27/27 manifest matches normalized repository files;
scientific counts, mappings, designs and the PASS decision were unchanged.

## 11. Scientific consequence and next target

Gate C5A establishes that GSE135779 can provide a predeclared independent test. It
does not yet demonstrate replication because no external effect has been estimated.
The next target is Gate C5B: qualify edgeR import against the frozen row/gene sums,
then run the childhood, combined, adult and support-threshold models with the exact
four-program multiplicity rule, donor influence checks and source-label sensitivity.

Only a positive, multiplicity-supported and influence-stable external IFN/ISG result
will authorize integration into the central manuscript claim and further escalation
toward an upper-Q1 submission.
