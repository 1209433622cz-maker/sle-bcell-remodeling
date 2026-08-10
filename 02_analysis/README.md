# Analysis Plan

## Goal

Build a reproducible analysis pipeline that supports the manuscript story, starting from public SLE and immune reference datasets and ending with interpretable figures, tables, and ranked candidate mechanisms.

## Current Local Data Status

Available locally:

- GEO metadata files for `GSE174188`.
- Supplementary files for `PRJNA1301449` / Younis et al.
- Canonical English literature PDFs in `PAPER/`.

Not yet available locally:

- Processed expression matrices or H5AD files for the main SLE re-analysis.
- OneK1K cell-by-gene / eQTL-ready resources.
- CIMA processed H5AD/MTX, scATAC, GRN, or xQTL resources.
- Standardized sample-level metadata table.

## Recommended Data Strategy

Phase A should use processed matrices/H5AD files wherever available. This is the fastest route to a figure-generating manuscript workflow.

Raw FASTQ/SRA reprocessing should be delayed until a specific figure or validation need justifies it.

## Pipeline Phases

0. Environment setup

- Create a reproducible Python/R environment.
- Pin versions for Scanpy/Seurat, plotting, enrichment, and statistics packages.
- Record all accession downloads.

1. Data acquisition

- Download processed matrices/H5AD files.
- Build a standardized metadata table.
- Preserve raw accession information and checksums.

2. QC and harmonization

- Apply dataset-aware QC.
- Normalize and integrate with conservative batch handling.
- Keep donor/sample metadata for pseudobulk or donor-aware testing.

3. B-cell extraction and annotation

- Extract B cells from each dataset.
- Re-cluster B cells at high resolution.
- Annotate states using canonical markers and literature anchors.

4. State characterization

- Marker genes.
- Pathway and module scores.
- Pseudobulk differential testing where donor information exists.
- Robustness across datasets.

5. State relationship analysis

- Pseudotime or similarity graph.
- Transition/state-continuum testing.
- Sensitivity to clustering and integration choices.

6. Regulatory prioritization

- Intersect SLE state signatures with OneK1K/CIMA eQTL, xQTL, GRN, and dynamic B-cell resources.
- Rank candidate regulators by evidence convergence.

7. Figure and table generation

- Generate publication-ready figures in `03_results/figures/`.
- Generate clean tables in `03_results/tables/`.

## Script Layout

Suggested future script names:

- `02_analysis/scripts/00_download_accessions.*`
- `02_analysis/scripts/01_build_metadata.*`
- `02_analysis/scripts/02_qc_integrate.*`
- `02_analysis/scripts/03_bcell_recluster.*`
- `02_analysis/scripts/04_state_programs.*`
- `02_analysis/scripts/05_regulatory_prioritization.*`
- `02_analysis/scripts/06_make_figures.*`

Use either R or Python consistently for the first pass unless a specific package requires mixing.
