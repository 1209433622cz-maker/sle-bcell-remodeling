# Action record: Gate C9 label-agnostic GSE135779 validation

**Date:** 2026-08-28

**Formal decision:** `PASS_C9_LABEL_AGNOSTIC_EXTERNAL_SUPPORT`

**Next target:** `GATE_C9_MANUSCRIPT_SUPPLEMENT_INTEGRATION_AND_RELEASE_REFREEZE`

## 1. Round objective

This round completed the highest-value scientific task left by the 2026-08-27
workspace audit: test whether the independent GSE135779 IFN/ISG result depended
on the authors' source-provided `subclusters` labels. The implementation had to
parse all external matrix cells, protect source labels and disease outcomes
during selection and mapping, apply two reference-calibrated broad-state
mappers, retain the frozen 12-gene program and make an explicit post hoc quality
decision.

The task did not reopen the formal Round 6 identity decision. R1 remains HOLD
because the end-to-end B_ASC median Jaccard was 0.930 against the unchanged 0.95
criterion.

## 2. Input restoration and provenance

The GSE135779 RAW archive was present at the start of this round:

- size: 1,299,783,680 bytes;
- SHA-256:
  `B5764C303AC76873738D6E05B6992277FCD6A14BF5BFCB27331E54DCBCAC619B`;
- archive structure: 56 matched barcode/matrix pairs;
- matrix cells: 363,083;
- matrix cell range per sample: 2,965-13,834.

The frozen reference inputs were the 150,402-cell GSE174188 raw-count H5AD and
its 3,000-feature representation H5AD. Their cell indices and donor IDs matched
exactly. The reference labels were reconstructed only from the frozen r0.4
mapping: clusters 0, 1, 2 and 4 to B_CONV; cluster 3 to B_ASC.

The external metadata contained 332,641 rows and 58 metadata samples, whereas
56 samples had matrices. The stage-one code hashed the metadata files for input
identity but did not parse fields or join either metadata table.

## 3. Legacy-code audit

The previous exploratory script
`02_analysis/scripts/30_run_gse135779_bcell_validation.py` was not suitable for
this test. It derived disease and cohort from `Names`, constructed
`is_b_subcluster` from `subclusters`, and selected only source-labeled B rows
before matrix extraction. Its results remain historical/exploratory and were
not reused as confirmatory inputs.

Gate C9 therefore uses a new implementation rather than editing any existing
effect table.

## 4. New protected workflow

Four executable files were added:

- `audit_tools/phase17_c9_common.py`;
- `audit_tools/phase17_c9_01_prefreeze_label_agnostic_mapping.py`;
- `audit_tools/phase17_c9_02_unlock_outcomes_and_review.py`;
- `audit_tools/run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1`.

The PowerShell runner has two physical stages.

### 4.1 C9A prefreeze

C9A hashes all inputs, verifies the reference join, removes protected fields
from the working contract and processes each external sample independently. QC
thresholds are deterministic sample-distribution rules. Each QC-passing sample
is log1p(CP10K) normalized, reduced using disease-blind HVGs and clustered with
Leiden at resolution 0.6.

Cluster-level B selection is primary. A cluster must have a median frozen
B-lineage score greater than every exclusion-module score, mean B-marker
detection of at least 1/9 and at least ten cells. A per-cell B-minus-exclusion
margin is frozen as sensitivity only.

The reference mapper feature space uses common GSE174188/GSE135779 genes from
the frozen ISG-excluded reference feature set plus forced B_CONV/B_ASC identity
markers. Strong ISGs, immunoglobulin, mitochondrial, ribosomal, hemoglobin,
stress and cell-cycle features are excluded from model selection.

The reference training set contains 13,000 B_CONV and all 1,300 B_ASC cells
across 258 represented donors. Five-fold stratified donor-grouped cross-
validation selected an averaged stochastic elastic-net logistic classifier
(`alpha=0.0001`, `l1_ratio=0.5`) and independently calibrated a Pearson
nearest-centroid mapper.

Reference-only low-confidence thresholds were frozen at:

- elastic-net maximum probability >=0.95;
- nearest-centroid absolute correlation margin >=0.1077157.

The complete four-program family was scored before outcome access. IFN/ISG used
all 12 frozen genes: ISG15, IFIT1, IFIT2, IFIT3, MX1, MX2, OAS1, OAS2, IFI44L,
IFI6, LY6E and IRF7.

### 4.2 C9B protected unlock

C9B was permitted to run only after C9A returned
`PASS_C9A_PREFREEZE_OUTCOME_UNLOCK_AUTHORIZED`. It reverified every input hash
and the 31.4 MB compressed per-cell prediction hash before opening metadata.
Source labels were used only for recovery and contamination audits. Disease,
cohort and SLEDAI fields were joined only after cell selection, mapper outputs,
confidence thresholds, program scores, donor aggregation and the 50-cell
B_CONV minimum had been frozen.

No threshold changed after unlock.

## 5. Software qualification

Static Python compilation, PowerShell parser validation and `git diff --check`
all passed. A protected four-sample test processed 19,914 cells without opening
outcomes. It achieved donor-grouped balanced accuracies of 0.949 and 0.942 and
minimum external confident fractions of 98.8% and 90.7% after nontrivial
confidence thresholds were imposed.

The initial `saga` implementation was stopped during software testing because
it was slow and did not converge at 2,000 iterations under the installed
scikit-learn version. Before any outcome access, it was replaced by an averaged
SGD implementation of elastic-net logistic loss. The model definition,
reference-only cross-validation and interpretation did not change. The formal
run then completed twice with identical numerical output; the second run
verified clean rerun behavior and portable manifests.

One Windows environment warning reported simultaneous Intel and LLVM OpenMP
runtimes. It did not cause a crash, deadlock or numerical discrepancy across
the two formal runs. It is recorded as an environment warning, not silently
suppressed.

## 6. Formal C9A result

- Samples processed: 56/56.
- Matrix cells reconciled: 363,083.
- QC-passing cells: 353,527 (97.37%).
- Primary cluster-selected B cells: 36,630.
- Per-cell-margin selected cells: 41,599.
- Elastic-net mean donor-grouped balanced accuracy: 0.9601.
- Nearest-centroid mean donor-grouped balanced accuracy: 0.9502.
- Overall primary-selection confident assignment: 97.76% and 95.33%.

Four samples had per-sample confidence below 80% for at least one
mapper. The frozen decision criterion was the overall selected-cell confidence,
which passed. Samples with fewer than 50 confidently mapped B_CONV cells were
excluded by the predeclared donor support rule; 43 childhood and 11 adult
donors remained eligible in the primary branch.

## 7. Post hoc selection audit

Among 32,741 QC-passing cells carrying a source B or PC label, the primary
cluster method recovered 32,313 (98.69%). Among 33,421 selected cells with a
known source label, 1,108 were non-B (3.32%). Most contamination came from
pDC/cDC source labels, consistent with shared antigen-presentation markers; no
post-outcome exclusion was introduced.

The per-cell margin sensitivity recovered 98.49% of source B cells but carried
15.05% non-B contamination. It therefore failed the 10% quality target and is
retained only as a directional sensitivity. Its positive outcome cannot be used
to replace the cleaner cluster-primary method.

## 8. Primary outcome

The primary unit was the childhood donor/sample mean frozen IFN/ISG score among
at least 50 confidently mapped B_CONV cells.

| Mapper | HC | SLE | SLE-HC effect | Bootstrap 95% CI | P | BH q |
|---|---:|---:|---:|---:|---:|---:|
| Elastic net | 11 | 32 | 0.30597 | 0.20782 to 0.41433 | 0.0005868 | 0.002347 |
| Nearest centroid | 11 | 32 | 0.30418 | 0.20751 to 0.41130 | 0.0005293 | 0.002117 |

BH correction was applied independently within each mapper to the unchanged
four-program childhood family. The minimum leave-one-donor effects were 0.28066
and 0.27898; all 86 mapper-specific exclusions retained the positive direction.

The per-cell margin branch also retained positive IFN/ISG effects and q<0.002,
but its 15.05% contamination prevents methodological promotion. Adult effects
were positive (approximately 0.24) but not significant with five HC and six SLE
eligible donors, so the adult result remains secondary and underpowered.

## 9. Additional program context

Under the primary cluster branch, both mappers retained a significant positive
atypical/low-naive axis. Naive-to-memory and APC/HLA effects were positive but
did not pass the four-program BH family. These are complete family outputs, not
new central claims. The manuscript remains anchored to the predeclared IFN/ISG
program.

## 10. Figure and file QA

The compact three-panel supplementary figure reports selection/mapping quality,
donor-grouped reference CV and childhood donor IFN/ISG scores. Visual inspection
confirmed no clipping, overlap or missing legend. PDF inspection confirmed:

- one page;
- 518.16 x 177.6 points, or approximately 182.8 x 62.7 mm;
- embedded Arial and Arial Bold CID TrueType fonts;
- no encryption, JavaScript or forms;
- matched PDF, SVG and 600-dpi PNG outputs.

The final C9 directory contains 29 files. Its integrity manifest covers the
other 28 files and all SHA-256 values were recomputed successfully. The local
per-cell gzip contains 363,083 rows, 56 samples and zero duplicate
sample/barcode keys. It is excluded from Git. No tracked C9 file contains the
local `H:\\...` project path.

## 11. Scientific decision and claim boundary

Gate C9 passes its predeclared supportive rule. The external childhood IFN/ISG
signal is not dependent on source-provided B labels under either frozen broad-
state mapper. This materially strengthens the manuscript against a foreseeable
label-circularity criticism.

The result remains a sensitivity within GSE135779. It does not:

- create an additional independent cohort;
- repair or supersede the Round 6 R1 HOLD;
- establish stable fine B-cell states;
- establish a discrete IFN-high B-cell subtype;
- establish treatment-independent causality or direct upstream regulation;
- justify replacing the source-label-defined external pseudobulk analysis.

## 12. Reproduction command

From the project root:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1
```

The 1.30 GB RAW archive, two formal reference H5AD files and compressed per-cell
output remain outside Git. Stable source-data tables, decisions, figures,
manifests and executable scripts are retained.

## 13. Next-stage advisor judgment

The next stage is not another dataset or threshold search. The scientifically
justified target is
`GATE_C9_MANUSCRIPT_SUPPLEMENT_INTEGRATION_AND_RELEASE_REFREEZE`:

1. integrate one bounded Methods subsection and Results paragraph;
2. add the frozen C9 figure as supplementary evidence with complete source data;
3. disclose the per-cell margin contamination limitation;
4. update claim matrices, supplementary tables and reproducibility manifests;
5. rebuild DOCX/PDF/ZIP outputs and perform WPS, accessibility and adversarial
   claim review;
6. publish an updated Zenodo version tied to the synced Git commit;
7. proceed to the journal portal.

The exact integration rules are frozen in
`next_stage_after_gateC9_manuscript_integration_contract_2026-08-28.md`.
