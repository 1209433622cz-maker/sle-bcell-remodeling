# Phase 12 Targets - 2026-07-08

## Status After Third Large Dataset Download

The third large dataset has been downloaded and inspected.

Dataset:

- Source: OneK1K / GSE196830, CELLxGENE collection `dde06e0f-ab3b-46be-96a2-a8082383c4a1`.
- Publication: Yazar et al., Science 2022, DOI `10.1126/science.abf3041`.
- Local H5AD: `Data/processed/GSE196830_onek1k_cellxgene/source/onek1k_gse196830_cellxgene.h5ad`.
- Local collection metadata: `Data/processed/GSE196830_onek1k_cellxgene/source/cellxgene_collection_onek1k_gse196830.json`.
- H5AD size: 4,434,273,970 bytes.
- SHA256 checksums recorded in `Data/processed/GSE196830_onek1k_cellxgene/source/checksums_sha256_2026-07-08.txt`.

Inspection results:

- Total cells: 1,248,980.
- Features: 35,528.
- Detected B-lineage-like cells: 129,579.
- Detected B-lineage-like donors: 981.
- Key metadata columns available: `cell_type`, `donor_id`, `assay`, `disease`, and `tissue`.
- All current manuscript genes are present: `ZEB2`, `TBX21`, `ITGAX`, `FCRL5`, `FCRL3`, `CD74`, `HLA-DRA`, `HLA-DRB1`, `HLA-DPA1`, `HLA-DPB1`, `MS4A1`, `ISG15`, `IFIT1`, `MX1`, `TLR7`, and `FTO`.

## Interpretation

OneK1K should not be treated as a third SLE validation cohort. Its strongest role is external immune-reference and regulatory-context evidence. It can strengthen the upper-Q1 route by showing that the manuscript axes are biologically coherent across a large independent PBMC reference, especially in B-lineage compartments.

## Recommended Next Stage

Completed after download:

1. Extracted B-lineage-like cells from the OneK1K CELLxGENE H5AD.
2. Scored the current manuscript programs across OneK1K B-cell compartments.
3. Summarized gene/program expression by `cell_type` and donor.
4. Produced a compact table set and Figure 7 candidate.
5. Drafted figure legend and Results text for OneK1K reference-context evidence.

## Next Stage

Integrate Figure 6 and the OneK1K Figure 7 candidate into manuscript v3. Keep claims conservative: OneK1K supports external immune/regulatory plausibility, while GSE135779 remains the main independent SLE validation cohort.
