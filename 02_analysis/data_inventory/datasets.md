# Dataset Inventory

This file tracks the working status of datasets and references for the SLE B-cell manuscript.

| Source | Accession or file | Local status | Role | Next action |
|---|---|---|---|---|
| Perez et al., Science 2022 | GSE174188, HCA project `9fc0064b-84ce-40a5-a768-e6eb3d364ee0`, CELLxGENE `436154da-bcf1-4130-9c8b-120ff9a888f2`, dbGaP `phs002812.v1.p1` | Full CELLxGENE H5AD local; B-lineage subset local; manuscript figures 1-5 generated | Primary SLE PBMC single-cell discovery dataset | Keep as discovery cohort; do not redownload unless provenance changes |
| Bhamidipati et al. / GSE163121 | GSE163121, PRJNA684938 | Processed GEO supplementary matrices downloaded and parsed; Figure 6 candidate generated | Small independent B-cell validation and boundary evidence | Use cautiously because donor count is HC n=2 and SLE n=3 |
| Nehar-Belaid et al., Nat Immunol 2020 | GSE135779, PRJNA560047, dbGaP `phs002048` | Metadata, gene list, series matrix, and processed RAW tar downloaded; B-subcluster validation completed | Preferred large independent validation cohort | Integrate as main Figure 6 validation layer |
| Younis et al., Sci Transl Med 2025 | PRJNA1301449 plus supplementary files | Supplementary tables and figures present | EBV/APC-like B-cell mechanistic anchor | Use as mechanism support; not currently treated as general independent B-cell cohort validation |
| Dai et al., Science 2024 | GSE242615, GSE242607, GSE242611 | Literature PDF only | ZEB2/ABC mechanistic anchor | Decide whether data are needed for computation or literature-only support |
| Zeng et al., Sci Transl Med 2025 | GSE135779, HRA001909, SRR35211570/71 | Literature PDF only | FTO/TLR7/m6A/ABC mechanistic anchor | Decide whether data are needed for computation or literature-only support |
| Yazar et al., Science 2022 | GSE196830, OneK1K/cellxgene | CELLxGENE H5AD downloaded, inspected, and B-lineage reference analysis completed; 1,248,980 cells, 35,528 features, 129,579 B-lineage-like cells across 981 donors; all current manuscript genes present | External immune eQTL and B-cell reference context | Integrate as Figure 7 candidate or supplementary regulatory-context evidence |
| Yin et al., Science 2026 | CIMA resources, OMIX/CNP/GVM/GWAS resources | Literature PDF only | Immune multi-omic, GRN, xQTL, and Chinese cohort reference | Identify accessible processed H5AD/MTX and regulatory summary files |
| Zheng et al., Nat Commun 2022 | s41467-022-35209-1 | Literature PDF only | Cutaneous lupus tissue context | Determine whether processed data are needed |
| Lee et al., bioRxiv 2025 | 2025.04.27.649460v1.full.pdf | Literature PDF only | Cutaneous manifestation context | Determine whether processed data are needed |

## Minimum Data Needed for First Results

1. One primary SLE PBMC single-cell dataset with cell-level expression and metadata.
2. One external immune reference with B-cell state or eQTL/regulatory information.
3. A curated marker/signature table for ABC/DN2-like, plasmablast, memory, and APC-like B-cell states.

## Current Analysis Route

Perez/GSE174188 is now the completed discovery cohort, with the full CELLxGENE H5AD and B-lineage subset available locally. For the upper-Q1 strengthening route, GSE163121 provides small B-cell-specific directional validation, while GSE135779 is the preferred larger independent validation cohort. OneK1K/GSE196830 has now been downloaded and inspected as a third large external dataset for immune reference and regulatory-context evidence rather than as another SLE case-control validation cohort.

## Data Rules

- Keep accession files and downloaded data separate from derived analysis outputs.
- Do not manually edit raw or processed downloaded matrices.
- Store derived objects with date, source dataset, and analysis step in the filename.
- Record checksums for any large downloaded files.
