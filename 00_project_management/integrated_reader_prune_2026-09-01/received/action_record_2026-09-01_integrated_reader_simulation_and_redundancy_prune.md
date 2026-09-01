# Action record: final integrated reader simulation and redundancy adjudication

**Date:** 2026-09-01  
**Status:** `INTEGRATED_READER_SIMULATION_COMPLETE__S3_S5_SOURCE_REDRAW_REQUIRED`  
**Scope:** manuscript text, figure/legend reader path and claim ownership only; no submission engineering

## Inputs independently reviewed

- Current 31-page manuscript and canonical Markdown source.
- Current 16-page Supplementary Information and canonical Markdown source.
- Current standalone Supplementary Figure S6.
- Frozen main- and supplementary-figure Source Data objects.
- GitHub scientific refreeze commit `078e403c0e2cd5aca9a284e016b57a226e8abc0e`.

## Integrated reader result

The scientific hierarchy remains coherent and no result warrants a new cohort, mapper, TF model, sensitivity analysis or replacement panel. However, final-order reading reveals three display-level duplicate evidence owners that were not visible when each figure was audited in isolation.

### Exact duplicate 1: S3a -> Figure 1b

Machine comparison result: **True**.

Current S3a and Figure 1b encode the same four policy-level median/minimum mapped ARI and mapping-agreement values. Keeping both makes the Supplement repeat the main identity-policy adjudication rather than add a new diagnostic layer.

Decision: remove S3a from display; retain Figure 1b as sole owner.

### Exact duplicate 2: S3d -> Figure 1d

Machine comparison result: **True**.

Current S3d and Figure 1d encode the same B_CONV/B_ASC median and minimum Jaccard values.

Decision: remove S3d from display; retain Figure 1d as sole owner.

### Exact duplicate 3: S5d -> Figure 3b

Machine comparison result: **True**.

All seven frozen branches are exactly equal between current S5d and Figure 3b for analysis name, effect, lower/upper confidence interval and four-program q value.

Decision: remove S5d from display; retain Figure 3b as sole owner.

## Revised figure adjudication

- Main figures: **21/21 KEEP**.
- S1: KEEP.
- S2: KEEP.
- S3: **MODIFY_SOURCE_REDRAW_AND_PRUNE**, 4 panels -> 2 panels; retain old b/c as new a/b.
- S4: KEEP. Panel b has conceptual overlap with Figure 2c but uniquely displays model-based versus HC1 covariance, so it is not redundant. Optional title polish only.
- S5: **MODIFY_SOURCE_REDRAW_AND_PRUNE**, 4 panels -> 3 panels; retain old a/b/c.
- S6: KEEP current refreeze.
- S7: KEEP.
- S8: KEEP.
- S9: KEEP.
- S10: KEEP.
- Entire-figure replacements: **0**.
- New panels: **0**.
- New analyses: **0**.
- Numerical Source Data changes: **0**.

## Manuscript redundancy prune

Only two text changes are recommended at this stage.

1. Introduction: replace generic `reconstruction and validation` with `reconstruction and replication tests` so the evidence hierarchy cannot be misread as claiming independent validation at every stage.
2. Final Discussion: compress the repeated exclusion list into one final positive boundary sentence:
   `the data support a bounded process-level interferon association within explicit identity and transfer limits.`

The Results closing sentences, opening Discussion synthesis, negative-narrative paragraph, and repeated `source-label-defined` qualifiers are retained because they serve distinct reader-path functions rather than redundant ownership.

## Source-data policy

Frozen numerical Source Data remain untouched. S3/S5 are to be re-rendered by selecting only retained source panels. Because panel letters change, write a derived display-panel mapping manifest instead of mutating the frozen CSVs.

SHA-256:
- Figure1 Source Data: `F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805`
- Supplementary S3 Source Data: `133E973C2753F4946A24739C049308152299A915A3FC6754B30AD0521F979C96`
- Figure3 Source Data: `DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8`
- Supplementary S5 Source Data: `F6682D636C1FF3A1784E0B9E8AEFF5C5D1BB075176312E87FCB938F65C4DA897`

## Typography / rendering boundary

The final source redraw must use the established project contract: 170-mm working width, embedded Arial, minimum visible text 6 pt, no redundant figure-wide title. The attached runner therefore **hard-fails when Arial is not installed** rather than silently substituting Arimo or DejaVu Sans.

## Next stage

`S3_S5_SOURCE_REDRAW_AND_FINAL_READER_PATH_REFREEZE`

Do only:
1. execute the supplied S3/S5 source-redraw runner in the canonical Arial environment;
2. integrate the two manuscript sentence edits and two Supplementary legend edits;
3. rebuild manuscript/Supplementary documents;
4. repeat actual-size reader-path QA and confirm no new page-flow defect.

Do not reopen disease-effect models, identity reconstruction, external mapping, TF analysis, multiplicity, Source Data, Release, Zenodo or the submission package.
