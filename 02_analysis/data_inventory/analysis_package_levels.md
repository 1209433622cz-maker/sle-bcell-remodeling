# Analysis Package Levels

This file translates the Q1/Q2 publication goal into concrete computational requirements.

## Level 1: Minimum Viable Manuscript

Purpose: produce a coherent public-data SLE B-cell analysis suitable for a conservative Q2 or lower Q1 attempt.

Required outputs:

- Dataset table with accession, sample size, disease/control status, tissue, assay, and local file status.
- QC report for the primary dataset.
- B-cell subset extraction.
- Re-clustering of B cells.
- Marker-supported annotation of major B-cell states.
- Program scoring for interferon, antigen presentation, TLR7/innate sensing, plasmablast, ABC/DN2, and memory programs.
- One candidate regulator table supported by literature and expression patterns.
- Five clean figures.

Main risk:

- If only one dataset is used, the paper may read as descriptive.

## Level 2: Strong Q1/Q2 Manuscript

Purpose: make the paper credible for realistic Q1/Q2 journals.

Additional required outputs:

- Independent validation dataset or cross-study validation.
- Donor-aware or pseudobulk testing when metadata allow.
- Robustness checks for integration, clustering resolution, and marker scoring.
- External reference integration using OneK1K and/or CIMA.
- Ranked candidate regulator table with explicit evidence layers.
- At least one figure showing convergence across lupus state specificity, trajectory/state relationship, and external regulatory support.

Main risk:

- Data access may be slower than writing, especially for processed matrices or controlled-access genotype resources.

## Level 3: Stretch Q1 Manuscript

Purpose: support submissions to upper Q1 journals.

Additional required outputs:

- Multiple SLE cohorts or tissue-context validation.
- Strong biological model centered on a small number of programs or regulators.
- Clinical or tissue relevance where metadata allow.
- Reusable computational prioritization framework.
- Public code repository and polished supplementary package.
- Clear limitations section that anticipates public-data-only concerns.

Main risk:

- Without experimental validation, claims must stay mechanism-prioritization rather than causal proof.

## Immediate Computational Next Step

Before running analysis, locate the processed expression data for the primary SLE dataset. The current local `GSE174188` folder contains only small GEO metadata files, not the full matrix needed for analysis.

Candidate first-pass data route:

1. Perez et al. SLE PBMC dataset as primary discovery.
2. Younis et al. EBV/APC-like B-cell study as mechanism anchor or validation if usable processed data are available.
3. OneK1K/CIMA as external regulatory references after primary B-cell states are defined.
