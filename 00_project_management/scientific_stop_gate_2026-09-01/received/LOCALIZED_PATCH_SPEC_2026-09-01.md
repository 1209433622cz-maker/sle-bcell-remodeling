# Localized patch specification — SLE B-cell remodeling

## Main manuscript

### T1 — source-label-defined external replication terminology

Replace:

`The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 mapped cells per donor.`

With:

`The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 eligible cells in the source-label-defined broad-B analogue per donor.`

Reason: removes ambiguity between source-label-defined replication and the separate source-label-independent remapping sensitivity.

## Supplementary Figure S4b

Replace panel title:

`Primary null is stable to covariances and cell policy`

With:

`Primary B_ASC estimate across covariance and cell policies`

Implementation: rerun S4 from frozen Source Data; title change only. Preserve all numerical and graphical encodings.

## Supplementary Table S5 — optional

Replace title:

`Supplementary Table S5 | Main-figure source-data map`

With:

`Supplementary Table S5 | Selected figure source-data map`

Reason: the table also lists Supplementary Figs. S8-S10.

## Canonical source synchronization

The author-facing files declared by `01_manuscript/README.md` must be synchronized to the integrated-reader-refreeze sources:

- `01_manuscript/Manuscript.md`
- `01_manuscript/Supplementary_Information.md`

Do not reconstruct the final manuscript by editing the stale root files line-by-line. Copy/synchronize from the integrated-reader-refreeze source objects, then apply only the localized changes above.

## Explicit no-change list

Do not reopen:
- identity reconstruction;
- composition models;
- edgeR pseudobulk;
- GSE135779 disease models;
- external mapper thresholds;
- regulator models;
- CAMERA/FRY;
- overlap depletion;
- M5911;
- GSE23307;
- Source Data;
- release/Zenodo/submission package.
