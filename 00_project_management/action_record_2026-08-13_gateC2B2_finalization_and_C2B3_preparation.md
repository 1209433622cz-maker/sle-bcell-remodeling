# Action record: Gate C2B2 finalization and Gate C2B3 preparation

**Date:** 13 August 2026

**Project:** 6013RP-wyf / v7 Phase 17

**Decision scope:** disease-blind B-cell representation and neutral-state freeze preparation

**Submission target:** SCI Q1, journal not yet locked

## 1. Starting state and evidence received

The complete Gate C2B2 run had finished locally after the earlier software and
download repairs. The supplied PowerShell transcript documented all three full
representation branches and the marker-review pass. This round did not accept the
terminal transcript alone: every result file was reopened from the run directory,
tables were reconciled, figures were visually reviewed, H5AD schemas were checked,
and the formal review was regenerated from the underlying files.

Authoritative run directory:

`phase17_v7/gateC2B2/20260812_full_representation`

## 2. Full Gate C2B2 reconciliation

- Primary branch: 150,402 cells, 3,000 recurrent HVGs.
- Residual-risk-negative sensitivity: 148,430 cells after removing exactly the
  prespecified 1,972 automatic residual-risk calls.
- ISG-excluded sensitivity: 150,402 cells, 3,000 HVGs and zero strong ISGs.
- All three Harmony branches converged after two iterations.
- The working H5ADs contain no disease, disease-state, `ct_cov`, treatment or
  outcome field.
- Harmony reduced mean same-library neighbor fraction from 0.08285 to 0.01408
  and mean same-processing-cohort fraction from 0.69313 to 0.36458.
- Median bridge-sample cosine centroid distance decreased from 0.59462 to 0.24019.
- At r=0.4, all five clusters include 88 libraries, at least 218 donors and at
  least 225 biological samples. Maximum single-library contribution is 3.08%.
- At r=0.4, maximum residual-risk-call fraction is 1.68%; residual-risk calls do
  not define a cluster and remain sensitivity-only.

The run directory contains 34 files totalling 433,623,010 bytes. The generated
integrity manifest records SHA256 values for 32 pre-existing result files and the
machine-readable advisor decision, totalling 433,617,710 bytes; the manifest itself
and its human-readable companion are intentionally outside their own hash set.

## 3. Review defect found and repaired

The original `21_GATE_C2B2_REVIEW.md` contained a template defect: it described the
complete run as “Software-test output” even though `test_mode=false`. The defect was
limited to reporting text, but it was not repaired by editing the result manually.

The review generator was changed to:

1. emit distinct full-data and software-test interpretations;
2. write marker-gene and marker-module summaries for every fitted resolution;
3. make sensitivity-branch ARI part of the selected-resolution checks; and
4. use r=0.4 as the runner's advisor-review default.

The full 150,402-cell marker extraction was rerun. The corrected review passed all
18 checks at r=0.4, including singlet-removal ARI 0.793 and ISG-exclusion ARI 0.772.

## 4. Binding Gate C2B2 decision

Decision: `PASS_TO_C2B3_WITH_R04_IDENTITY_BACKBONE`

The selection rule was frozen without disease information: among r=0.4 to r=0.8
solutions meeting cell, sample, library and residual-risk coverage, maximize the
lower of the singlet-removal and ISG-exclusion ARIs, with ties resolved toward the
coarser solution.

| Resolution | Clusters | Minimum cells | Singlet ARI | ISG-excluded ARI | Use |
|---:|---:|---:|---:|---:|---|
| 0.2 | 2 | 1,302 | 0.082 | 0.195 | rejected as under-resolved/unstable |
| 0.4 | 5 | 1,251 | 0.793 | 0.772 | identity backbone |
| 0.6 | 6 | 1,307 | 0.561 | 0.428 | substate candidate only |
| 0.8 | 7 | 1,319 | 0.702 | 0.432 | substate candidate only |
| 1.0 | 9 | 4 | 0.706 | 0.381 | rejected for tiny clusters |
| 1.2 | 11 | 3 | 0.639 | 0.388 | rejected for tiny clusters |

This decision freezes a coarse graph backbone, not five publication cell-type names.
Disease metadata remains locked.

## 5. Full-gene marker audit

A new sparse raw-count marker-ranking workflow was run on all 150,402 cells and all
30,172 genes at r=0.4 and r=0.6. It is explicitly descriptive and is not used as an
inferential disease test. Marker support is calculated across sample-cluster strata.

Provisional r=0.4 interpretation:

- Cluster 0: naive-enriched B-cell backbone (`TCL1A`, `IL4R`, `FCER2`).
- Cluster 1: memory-enriched B-cell backbone (`GPR183`, `TNFRSF13B`, `AIM2`).
- Cluster 2: platelet-associated B-cell structure (`CLU`, `NRGN`, `TUBB1`, `PF4`,
  `PPBP`, `RGS18`); no automatic exclusion is authorized.
- Cluster 3: coherent plasmablast program (`TNFRSF17`, `MZB1`, `JCHAIN`, `XBP1`,
  `DERL3`, `SEC11C`), not generic contamination.
- Cluster 4: unresolved `ANKRD40/C1orf56`-associated B-cell program. It remains a
  neutral state candidate and receives no publication label before resampling review.

Each r=0.4 cluster yielded 20 non-nuisance dictionary markers. Median sample-support
fractions range from 0.874 to 1.000, with at least 91 eligible sample-cluster strata
for every cluster.

### Cluster 4 artifact check

The two most specific features were examined directly rather than silently removed.

- `ANKRD40` and `ENSG00000262967` are adjacent features but not duplicate count
  vectors: Pearson correlation 0.346; 873 cells co-detect both.
- They recur as HVGs in 59 and 60 libraries, respectively.
- They are not the dominant PC9 loadings; the separating program also contains
  `C1orf56`, `HNRNPH1`, `MDM4`, `B4GALT1`, `CDC42SE1`, `FGD2` and related genes.
- Cluster 4 includes 1,251 cells, 221 donors, 227 samples and all 88 libraries.

The evidence does not justify deleting the cluster or launching a two-gene-only
Harmony rerun at this point. Full graph-resampling stability remains mandatory.

## 6. Outside-label candidate mapping

All 768 core-B-identity candidates outside the source B-cell/plasmablast labels were
projected from full-PBMC raw counts into the unintegrated primary PCA using the frozen
means, standard deviations and loadings. Nearest neighbors were selected within the
same technical library; a recorded same-processing-cohort fallback exists only for
libraries lacking sufficient reference cells.

Full-reference result:

- Reference cells: 150,402.
- Median r=0.4 nearest-state vote confidence: 0.760.
- Candidates within the same-library reference q95 distance: 20.31%.
- Candidates satisfying the earlier core-B plus low-non-B rule: 57/768 (7.42%).
- Source labels: 516 conventional dendritic, 105 plasmacytoid dendritic, 98 CD4 T,
  22 CD8 T and only small residual categories.
- Binding decision: `MAPPING_COMPLETE_NO_AUTOMATIC_APPEND`.

The candidates can often be assigned a nearest B state, but most are out-of-
distribution relative to genuine within-library B cells and retain non-B evidence.
The primary source-label input is therefore unchanged. This sensitivity question is
closed unless a future independent dataset supplies stronger lineage evidence.

## 7. Gate C2B3 workflow implemented

New executable components:

- `phase17_c2b_11_resampling_stability.py`: repeated library-stratified graph
  resampling on the frozen Harmony embedding; ARI, AMI, majority-mapping agreement,
  cluster Jaccard/recall and cell-level stability.
- `phase17_c2b_12_map_blineage_candidates.py`: raw-count PCA projection with
  technical-scope and out-of-distribution diagnostics.
- `phase17_c2b_13_rank_neutral_markers.py`: full-gene descriptive ranking with
  sample-stratum support.
- `phase17_c2b_14_review_gatec2b3.py`: binding thresholds, neutral-ID freeze table
  and outcome-unlock decision.
- `run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1`: resumable orchestration.

The runner validates and reuses completed components. The full candidate mapping and
full marker ranking already exist in:

`phase17_v7/gateC2B3/20260813_full_neutral_state_freeze`

Only the full graph-resampling component and final review remain.

## 8. Verification performed

- Python syntax compilation passed for all six modified/new Python scripts.
- PowerShell parsing passed for both C2B2 and C2B3 runners.
- Corrected full C2B2 review completed successfully on 150,402 cells.
- C2B2 advisor finalizer completed and generated SHA256 integrity evidence.
- A 5,000-cell, three-replicate C2B3 software test completed end to end.
- The first software test correctly failed on a sparse-library mapping edge case;
  the explicit technical-cohort fallback was added and the complete test then passed.
- Software-test decision: `SOFTWARE_TEST_PASS_NOT_BIOLOGICAL_GATE`.
- Full candidate mapping and full-gene marker ranking completed successfully.

## 9. Current authorization state

- Gate C2B2 representation: PASS.
- Coarse identity backbone: r=0.4.
- Full candidate mapping: complete; no primary-input expansion.
- Full marker ranking: complete; biological labels remain provisional.
- Gate C2B3 neutral-state freeze: pending full resampling.
- Disease/outcome unlock: not authorized.
- Manuscript disease claims and final journal choice: not authorized.

## 10. Required next command

Run from the project root in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1 `
  -GateC2B2RunDir ".\phase17_v7\gateC2B2\20260812_full_representation" `
  -ResumeRunDir ".\phase17_v7\gateC2B3\20260813_full_neutral_state_freeze" `
  -Replicates 20 `
  -ResampleFraction 0.8
```

The runner will reuse the full candidate-mapping and marker-ranking checkpoints.
The long-running work is 20 repeated neighbor-graph/Leiden fits on 80% of the full
cells. Do not add `-MaxCells`; that switch creates software-test evidence only.
