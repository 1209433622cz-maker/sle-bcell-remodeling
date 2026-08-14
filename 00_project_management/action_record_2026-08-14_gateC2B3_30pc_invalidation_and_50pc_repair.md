# Action record: Gate C2B3 30-PC invalidation and 50-PC repair

**Date:** 14 August 2026

**Project:** 6013RP-wyf / v7 Phase 17

**Scope:** full Gate C2B3 resampling audit, implementation correction and rerun contract

## 1. Full computation received

The user completed 20 library-stratified resampling replicates. Each replicate used
120,320 of 150,402 cells (80%), and the candidate-mapping and full-gene marker
checkpoints were reused as intended. The generated reviewer returned
`HOLD_GATE_C2B3_REVIEW_REQUIRED` and did not unlock disease metadata.

The initially reported r=0.4 metrics were:

- median ARI: 0.603;
- minimum ARI: 0.305;
- median majority-mapping agreement: 0.954;
- minimum cluster median Jaccard: 0.000;
- marker dictionary: complete for 5/5 clusters;
- minimum cluster median sample support: 0.874; and
- outside-label candidate policy: unchanged, with no automatic append.

These values are preserved for audit history but were subsequently invalidated for
scientific interpretation because of the representation mismatch described below.

## 2. Initial cluster-level localization

Before the dimensional mismatch was identified, the HOLD signal was localized to
specific structures rather than treated as a global failure:

- r=0.4 cluster 0: median Jaccard 0.935, recovered 20/20 times;
- cluster 1: median Jaccard 0.909, recovered 20/20 times;
- cluster 2: median Jaccard 0.000, recovered only 6/20 times;
- cluster 3: median Jaccard 0.982, recovered 20/20 times; and
- cluster 4: median Jaccard 0.719, recovered 16/20 times.

Cell-level self-mapping stability medians were 1.000, 1.000, 0.294, 1.000 and
0.778 for clusters 0 through 4, respectively. Disease-blind nearest-neighbor review
placed 79.1% of cluster 2 and 73.4% of cluster 4 non-self neighbors in cluster 0.
Their QC distributions were comparable with cluster 0; neither was defined by high
doublet score or non-B fraction. These observations are non-binding because the
resampling representation was mismatched, but they motivated a transparent fallback
policy to be evaluated prospectively in the corrected run.

## 3. Root cause

The primary Gate C2B2 object stores `X_pca_harmony` with 50 dimensions. Its source
neighbor graph was built with:

```python
sc.pp.neighbors(work, use_rep="X_pca_harmony", ...)
```

No `n_pcs` truncation was supplied, so all 50 dimensions were used to produce the
reference Leiden labels. The Gate C2B3 resampling script instead sliced the embedding
to the first 30 dimensions before rebuilding each graph.

Consequently, the run varied two factors simultaneously:

1. the intended 80% cell resampling; and
2. an unintended 50-to-30 representation truncation.

It was therefore not a valid resampling-only test. The observed HOLD cannot be used
to merge or delete clusters, freeze neutral identities or unlock outcomes.

## 4. Invalidation and file handling

The original 30-PC result was copied to:

`phase17_v7/gateC2B3/_invalidated_30pc_resampling_20260814`

The copied files were checked against the original Gate C2B3 integrity manifest
before the active copies were removed. The archive contains 15 files totalling
5,516,402 bytes, including the per-cell stability export and diagnostic figures.
The final split-location audit resolved all 24 original manifest entries across the
archive and active directory, with 24/24 file sizes and SHA-256 hashes matching.
The 5,393,593-byte per-cell gzip remains preserved locally and is excluded from Git
by the repository's existing `*.csv.gz` rule.

The active run directory now contains only:

- validated full candidate mapping;
- validated full-gene marker ranking;
- candidate-mapping figures;
- an explicit 30-PC invalidation notice; and
- status `FULL_50PC_RESAMPLING_REQUIRED`.

No raw count, representation, candidate-mapping or marker result was deleted.

## 5. Schema-v2 correction

The resampling workflow now:

1. uses all source Harmony dimensions by default (`--n-pcs 0`);
2. records requested, used and source dimensions separately;
3. requires `representation_dimension_match=true`;
4. writes schema version 2 so old checkpoints cannot be reused;
5. validates 50 dimensions, 15 neighbors, replicate count and fraction in the
   PowerShell checkpoint contract;
6. explicitly pins the current `leidenalg` backend used by the source labels;
7. records reference-cluster absorption destinations for every replicate; and
8. writes policy-level ARI, agreement, Jaccard and recall diagnostics.

The Gate C2B3 reviewer now refuses outcome unlock unless source and resampling
dimensions match exactly.

## 6. Disease-blind hierarchical identity policy

To avoid a third expensive run if an overlay-like rare cluster remains unstable, the
following order was locked before corrected full results are available:

1. `five_state`: retain all r=0.4 clusters;
2. `four_state_platelet_overlay_merged`: merge platelet-associated cluster 2 into
   its cluster 0 mother population; and
3. `three_state_identity_core`: additionally merge unresolved cluster 4 into
   cluster 0, retaining naive-core, memory-core and plasmablast identity states.

The first policy meeting all four stability thresholds is selected. No disease,
clinical, treatment or outcome field participates in this choice. Platelet, IFN,
atypical and other activation signals remain available as continuous within-state
programs even when they are not accepted as cell identities.

Binding thresholds remain:

- median ARI at least 0.75;
- minimum replicate ARI at least 0.65;
- median majority-mapping agreement at least 0.80; and
- minimum cluster-level median Jaccard at least 0.60.

## 7. Software verification

A new 5,000-cell, three-replicate test was executed after the repair.

- schema version: 2;
- used/source dimensions: 50/50;
- representation dimension match: true;
- cells per replicate: 3,996;
- candidate and marker checkpoints: reused;
- policy, transition and integrity outputs: generated; and
- decision: `SOFTWARE_TEST_PASS_NOT_BIOLOGICAL_GATE`.

The small test selected the three-state policy, but this has no biological authority;
its purpose is to verify execution and file contracts only.

Python compilation, PowerShell parsing and checkpoint invalidation/reuse behavior
were verified after the code changes.

## 8. Current authorization state

- Gate C2B2: passed with r=0.4 identity backbone.
- Gate C2B3 valid full resampling: pending.
- Candidate-input expansion: rejected; primary input unchanged.
- Full marker ranking: complete.
- Neutral-state freeze: not authorized.
- Disease/outcome unlock: not authorized.
- Gate C3 composition analysis: not authorized.
- Manuscript disease claims and final journal choice: not authorized.

## 9. Corrected full command

Run from any PowerShell directory:

```powershell
powershell -ExecutionPolicy Bypass `
  -File "H:\cuhk-2025fALL\6013RP-wyf\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1" `
  -GateC2B2RunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B2\20260812_full_representation" `
  -ResumeRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B3\20260813_full_neutral_state_freeze" `
  -Replicates 20 `
  -ResampleFraction 0.8
```

The runner will reject the old schema-1 30-PC checkpoint, use all 50 Harmony
dimensions and continue to reuse the valid full candidate and marker checkpoints.
