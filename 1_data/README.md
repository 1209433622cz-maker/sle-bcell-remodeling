# Data

This folder contains input manifests and indexes, not a redistributed copy of
all source data. Read [Data/README.md](../Data/README.md) for acquisition and
checksum instructions. Restore raw objects at their frozen backend paths.

| Data | Role | Current limit |
|---|---|---|
| GSE174188 / CELLxGENE | Discovery B lineage, pseudobulk and identity reconstruction | Cells are not disease-model replicates |
| GSE135779 | Source-label-defined external broad-B support | Childhood/combined overlap; required corrected mapping failed |
| GSE23307 | Two-donor IFN-beta context | Descriptive only; no inferential P |
| GSE262846 | Prospective activity-by-compartment question | Stage N gates remain HOLD; no external expression effect |

## Compact Frozen Inputs

- [Disease-blind run map](manifests/StageM_Disease_Blind_Run_Map.csv).
- [88-library accounting](manifests/StageM_Library_Run_Accounting.csv).
- [Reference manifest](manifests/StageM_Reference_Annotation_Manifest.csv).
- [Metadata/design catalog](metadata_design/README.md) and [data index](DATA_INDEX_2026-10-12.csv).

Raw H5AD and embedding-only H5AD are different objects. The latter has no
expression X by design and cannot substitute for counts. Large matrices and
reads remain ignored in Git. Source data retain their original access,
privacy, attribution and licensing conditions.
