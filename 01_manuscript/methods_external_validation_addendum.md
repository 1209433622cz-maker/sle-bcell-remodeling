# Methods Addendum - External Validation

## GSE163121 Independent B-Cell Validation

Processed supplementary matrices for GSE163121 were downloaded from GEO. The dataset contains B cells isolated from PBMCs of two healthy controls and three SLE patients. The GEO `GSE163121_RAW.tar` archive contained one CellRanger filtered matrix archive per sample. Each sample matrix was parsed using the Matrix Market count matrix, barcode table, and gene table, then concatenated into a single AnnData object.

Counts were normalized to counts per 10,000 per cell and transformed as log1p(CP10K). Curated B-cell programs were scored as the mean log1p(CP10K) expression of present genes. Programs included ABC/APC-focus, ZEB2/TBX21/ITGAX axis, FCRL axis, HLA/CD74 axis, ABC/DN2 core, APC/HLA, IFN/ISG, naive B-cell, and plasmablast/ASC signatures. Sample-level mean scores were compared between healthy control and SLE samples using Mann-Whitney U tests with Benjamini-Hochberg correction across scored metrics.

To test for a high-scoring tail, the ABC/APC-focus score threshold was defined as the 95th percentile of healthy-control cells. The fraction of cells exceeding this threshold was calculated per sample and compared between disease groups. Because the dataset contains only five donors, this analysis was interpreted as directional external validation and boundary evidence rather than a fully powered replication cohort.

## GSE135779 Validation Readiness

GSE135779 metadata files from the associated analysis repository and GEO gene-list/series files were downloaded for readiness assessment. Cell-level metadata were summarized by cohort file, disease group, donor/sample name, and B-subcluster annotation. Program-gene coverage was assessed against the downloaded gene list.

## GSE135779 B-Subcluster Validation

The processed `GSE135779_RAW.tar` file was downloaded from GEO and inspected. The archive contained sample-level barcode and Matrix Market count files for 56 samples. The extended childhood-plus-adult metadata file was used for cell-level annotation. Because raw barcode files used sample-local `-1` suffixes whereas metadata used library-level suffixes, barcodes were matched within each sample using the core barcode sequence before the dash.

Cells annotated as B subclusters in the metadata were retained and matched to the processed matrices. This yielded 32,179 B-subcluster cells from 56 donor/sample names. Counts were normalized to counts per 10,000 per cell and transformed as log1p(CP10K). Program scores were calculated as the mean log1p(CP10K) expression of present genes. Donor-level mean scores and ABC/APC-high fractions were compared between healthy control and SLE donors using Mann-Whitney U tests with Benjamini-Hochberg correction across metrics and strata. Analyses were performed across all donors and separately in childhood and adult strata.

## OneK1K External B-Lineage Reference Context

The OneK1K/GSE196830 CELLxGENE H5AD was downloaded and inspected. B-lineage-like cells were selected from the standardized `cell_type` annotation, retaining naive B cells, memory B cells, transitional stage B cells, and plasmablasts. This yielded 129,579 B-lineage-like cells across 981 donors.

Target-gene raw counts from `X` were normalized as log1p(CP10K) using the full-library `nCount_RNA` metadata column. Only B-lineage-like cells and program/marker genes were loaded into memory. Program scores were calculated as the mean expression of present genes, then summarized by cell type and donor. OneK1K was used as external immune-reference context and not as SLE-vs-control disease validation.
