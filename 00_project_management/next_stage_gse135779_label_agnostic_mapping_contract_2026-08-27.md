# GSE135779 label-agnostic external mapping contract

**Status:** PRE-OUTCOME METHOD FREEZE  
**Date:** 2026-08-27  
**Purpose:** test whether the independent IFN/ISG replication depends on the
source-provided GSE135779 `subclusters` labels.

## 1. Scientific question

Does the childhood GSE135779 SLE-versus-control IFN/ISG effect remain positive
and inferentially supported when external B-lineage selection and B_CONV/B_ASC
mapping are performed without using source-provided cell labels or disease
outcomes?

This is a sensitivity analysis. It cannot convert the formal GSE174188 R1
identity HOLD into PASS and cannot turn GSE135779 into a discovery cohort.

## 2. Frozen inputs

- GSE174188 raw-count reference:
  `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad`.
- GSE174188 frozen representation and broad-state reference:
  `phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad`.
- GSE135779 processed sample matrices from `GSE135779_RAW.tar`.
- GSE135779 barcode/sample metadata. The `subclusters`, `Groups`, `SLEDAI`,
  `SLEDAI_cat` and other outcome fields remain protected during selection,
  mapping and threshold choice.

Input hashes and exact cell/sample reconciliation must be frozen before any
outcome comparison.

## 3. Blinding contract

1. Disease, activity and source `subclusters` columns are removed from the
   analysis object used for QC, feature selection, B-lineage selection and
   state mapping.
2. Any method threshold is selected using the GSE174188 reference, unsupervised
   GSE135779 structure or fixed marker dictionaries only.
3. Source labels may be joined only after predictions are frozen, and only for
   post hoc recovery/contamination auditing.
4. Disease outcomes may be joined only after the cell inclusion set, mapping
   probabilities, low-confidence rule, donor aggregation and IFN/ISG score are
   frozen.
5. No threshold may be changed after unblinding.

## 4. Analysis design

### 4.1 External preprocessing

- Parse all available GSE135779 cells rather than selecting rows whose
  `subclusters` begin with `B-`.
- Apply sample-aware count QC with thresholds declared from count distributions
  without disease labels.
- Normalize to log1p(CP10K) for mapping and scoring while retaining raw counts.
- Use the intersection of measured genes and the frozen reference features.

### 4.2 Label-agnostic B-lineage selection

Use two disease-blind views:

1. unsupervised external Leiden clusters annotated only from a frozen positive
   B-lineage module (`CD19`, `MS4A1`, `CD79A`, `CD79B`, `CD37`, `CD74`,
   `HLA-DRA`, `CD22`, `CD83`) and frozen exclusion modules for T/NK, myeloid,
   platelet and erythroid lineages;
2. a per-cell module-margin sensitivity using the same frozen dictionaries.

The cluster-level selection is primary. The per-cell margin is a sensitivity,
not a replacement chosen after outcomes are seen.

### 4.3 Broad-state transfer

Apply two independent, disease-blind transfer methods on the frozen common-gene
space:

1. donor-grouped elastic-net logistic regression trained on GSE174188 B_CONV
   versus B_ASC labels;
2. nearest-centroid correlation to frozen GSE174188 B_CONV and B_ASC reference
   profiles.

Hyperparameters and low-confidence probability/margin rules are selected using
GSE174188 donor-grouped cross-validation only. GSE135779 disease labels are not
available to either method.

### 4.4 Frozen outcome

The primary outcome is the donor/sample-level mean frozen IFN/ISG score within
label-agnostically selected, confidently mapped B_CONV cells in the childhood
stratum. The same donor/sample definition, two-sided Mann-Whitney test and
Benjamini-Hochberg family used by the current external validation are retained.

Secondary outputs are B-lineage recovery, post hoc source-label concordance,
low-confidence fraction, B_ASC abundance and adult-stratum direction. They do
not replace the primary outcome.

## 5. Predeclared interpretation rules

### 5.1 Supportive result

The label-agnostic sensitivity is supportive only if all conditions hold:

- both transfer methods retain a positive childhood SLE-minus-control B_CONV
  IFN/ISG effect;
- the primary elastic-net result remains BH-significant at q < 0.05 under the
  unchanged external test family;
- no single donor/sample reversal explains the direction;
- at least 80% of source-labeled B cells are recovered post hoc and at most 10%
  of selected cells carry a non-B source label;
- at least 80% of selected cells receive a confident broad-state assignment;
- all sample and outcome joins pass one-to-one integrity checks.

### 5.2 Mixed result

If direction is positive but significance, recovery, contamination or mapping
confidence misses a threshold, report a directional robustness result only.
Do not use it to strengthen the abstract or title.

### 5.3 Non-supportive result

If either transfer method reverses the childhood effect, if the primary effect
is dominated by one sample, or if selection/mapping quality is inadequate,
retain the failure and narrow the manuscript to source-label-defined external
replication. No replacement threshold, alternative stratum or selectively
reported mapper is permitted.

## 6. Required outputs

- input and hash manifest;
- protected-metadata contract and unlock log;
- sample/cell reconciliation tables;
- B-lineage selection audit before and after source-label join;
- mapper cross-validation and probability calibration tables;
- per-cell predictions retained locally but excluded from Git;
- donor/sample-level frozen IFN/ISG table;
- complete primary and sensitivity statistics;
- one compact supplementary figure with source data;
- advisor decision JSON/Markdown and file-level integrity manifest;
- a detailed action record for the round.

## 7. Execution prerequisite

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"

powershell -ExecutionPolicy Bypass `
  -File .\02_analysis\scripts\00_download_gse135779_validation_sources.ps1 `
  -DownloadRaw
```

Expected RAW archive size: `1,299,783,680` bytes. The analysis runner will be
implemented against this frozen contract after the archive is present.
