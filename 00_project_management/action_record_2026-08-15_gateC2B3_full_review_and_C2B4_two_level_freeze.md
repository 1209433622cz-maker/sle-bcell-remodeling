# Action record: Gate C2B3 full review and Gate C2B4 two-level freeze

**Date:** 15 August 2026

**Project:** 6013RP-wyf / v7 Phase 17

**Scope:** schema-v2 full resampling verification, HOLD localization, disease-blind
two-level state-model adjudication, figure QC and next-gate authorization

## 1. User computation received

The corrected Gate C2B3 workflow completed 20 library-stratified resampling
replicates using 120,320 of 150,402 cells per replicate. The binding run contract
was satisfied:

- schema version 2;
- 50 source and 50 resampling Harmony dimensions;
- `representation_dimension_match=true`;
- 15 graph neighbors;
- 80% sampling fraction;
- candidate mapping and full-gene marker checkpoints reused; and
- no disease, treatment, clinical or outcome field used by the state selection.

The Scanpy message about a future Leiden backend default was a `FutureWarning`, not
an execution failure. The workflow explicitly pins `flavor="leidenalg"`, matching
the source C2B2 labels.

## 2. File and integrity audit

The active C2B3 result directory contains the complete schema-v2 metric suite,
per-cell stability export, marker dictionary, candidate mapping, review, figures
and status records. The generated integrity manifest contains 30 entries totalling
6,135,508 bytes. Independent size and SHA-256 verification passed for 30/30 rows.

The large `05_resampling_cell_stability.csv.gz` remains local under the repository's
existing `*.csv.gz` Git exclusion. Its manifest hash is preserved in the formal
C2B3 result.

## 3. Binding C2B3 result

The corrected run returned `HOLD_GATE_C2B3_REVIEW_REQUIRED`. The original result is
preserved and was not edited or relabelled.

| Prespecified policy | Median raw ARI | Minimum raw ARI | Median agreement | Minimum cluster median Jaccard | Result |
|---|---:|---:|---:|---:|---|
| Five-state | 0.812 | 0.319 | 0.963 | 0.455 | fail |
| Four-state | 0.786 | 0.295 | 0.973 | 0.805 | fail |
| Three-state | 0.769 | 0.281 | 0.974 | 0.925 | fail |

All marker, candidate-mapping, dimension and disease-blind checks passed. Failure
was restricted to state-stability requirements; outcome unlock remained false.

## 4. Failure localization

Replicates 8 and 9 produced the strongest failures. In replicate 8, 59.4% of
reference cluster 1 mapped to cluster 0; in replicate 9, 27.1% of cluster 0 mapped
to cluster 1. This was a large-scale exchange along the conventional-B
naive-memory continuum, not loss of the antibody-secreting compartment.

The structures were interpreted as follows from full-gene markers and stability:

- cluster 0: naive-enriched conventional-B anchor (`TCL1A`, `FCER2`, `IL4R`);
- cluster 1: memory-enriched conventional-B anchor (`CD27`, `TNFRSF13B`, `GPR183`);
- cluster 2: platelet-associated overlay (`PF4`, `PPBP`, `TUBB1`);
- cluster 3: antibody-secreting B compartment (`TNFRSF17`, `MZB1`, `JCHAIN`,
  `XBP1`, `DERL3`); and
- cluster 4: unresolved conventional-B boundary without a sufficiently specific
  marker identity.

The data therefore reject hard naive-memory composition labels but do not reject a
coarser conventional-B versus antibody-secreting-cell identity model.

## 5. Metric-layer correction

The original collapsed-policy ARI compared consolidated reference states with the
unconsolidated raw Leiden partition. This appropriately describes full partition
recovery but penalizes subdivisions that are irrelevant to a coarser identity
compartment. Mapping agreement and state Jaccard were already evaluated after
majority alignment.

Gate C2B4 therefore reconstructed majority-aligned contingency matrices directly
from the 60,809 saved transition rows and calculated mapped ARI without expanding
millions of cell-level labels. Reconstruction was checked against all saved
five-, four- and three-state policy agreements for every replicate. The maximum
absolute discrepancy was `1.110e-16`, establishing numerical equivalence of the
transition reconstruction.

This correction does not convert the original five-, four- or three-state HOLD into
a pass. It supports a distinct, explicitly coarser repair model.

## 6. Gate C2B4 implementation

The following reproducible components were added:

- `audit_tools/phase17_c2b_15_adjudicate_two_level_model.py`;
- `audit_tools/run_6013RP_phase17_gateC2B4_two_level_state_model.ps1`; and
- `phase17_v7/gateC2B4/20260815_two_level_state_repair`.

The PowerShell launcher uses `conda run --no-capture-output` so the environment's
Windows DLL search path is initialized before Matplotlib loads. Directly invoking
the environment Python from the Codex process reproduced native exception
`0xc06d007f`; the Conda launcher resolved it without changing statistical results.

## 7. C2B4 binding thresholds and result

The two-compartment model passed every adjudication check:

| Metric | Observed | Required |
|---|---:|---:|
| Median mapped ARI | 0.9956 | >=0.950 |
| Minimum mapped ARI | 0.9902 | >=0.900 |
| Median mapping agreement | 0.99993 | >=0.995 |
| Minimum mapping agreement | 0.99983 | >=0.990 |
| Minimum state median Jaccard | 0.9914 | >=0.950 |
| Minimum state minimum Jaccard | 0.9811 | descriptive |
| Minimum required ASC-marker sample support | 1.000 | >=0.900 |

The C2B4 input audit also reverified all 30 C2B3 manifest entries, schema-v2
50/50-PC matching, 20/20 replicates, disease-blind provenance and the complete ASC
marker panel.

Decision:

`PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED`

## 8. Frozen scope

Only two hard neutral identity compartments are frozen:

- `B_CONV`: source clusters 0, 1, 2 and 4; and
- `B_ASC`: source cluster 3.

The following restrictions are binding:

- no hard naive-versus-memory composition claim;
- no platelet-associated B-cell identity claim;
- no publication subtype claim for source cluster 4;
- naive-memory remodeling must be analyzed as a continuous program within
  `B_CONV`; and
- platelet genes are a continuous overlay and sensitivity/QC program.

Outcome metadata is unlocked only for two-compartment sample-level composition and
prespecified continuous within-conventional programs. It is not a general license
to revive older subtype comparisons.

## 9. Figure review

The new four-panel audit figure records:

- mapped ARI across all four hierarchy levels;
- replicate-level two-compartment mapped ARI and agreement;
- conventional-B and ASC Jaccard distributions; and
- sample support for the five required ASC markers.

The PNG and vector PDF were generated from the adjudication script and are included
in the C2B4 integrity manifest. Layout, text fit, panel labels, axis ranges and
threshold lines were visually reviewed.

## 10. Verification performed

- C2B3 manifest: 30/30 files passed size and SHA-256 verification.
- C2B4 transition reconstruction: agreement delta <=1.110e-16.
- Python compilation: passed.
- PowerShell parsing: passed.
- PowerShell end-to-end launcher rerun: passed.
- C2B4 output manifest: generated and independently rechecked before commit.
- Figure visual inspection: passed.

## 11. Next authorized gate

Gate C3 begins with an exact `source_cell_index` metadata join and sample/donor
design audit. The first outcome-aware analysis must use samples, not cells, as the
replicate unit. It will evaluate `B_ASC` abundance relative to all frozen B cells
and then construct continuous naive-memory and activation programs within `B_CONV`.

No definitive disease claim, manuscript result sentence or final journal selection
is authorized until Gate C3 establishes cohort support, donor-aware uncertainty and
processing-cohort sensitivity.
