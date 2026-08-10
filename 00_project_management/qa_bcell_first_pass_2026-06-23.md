# B-cell First-Pass Output QA

## Shapes

- Source H5AD: 1,263,676 cells x 30,172 features.
- B-cell subset H5AD: 152,981 cells x 30,172 features.
- Processed B-cell H5AD: 152,981 cells x 30,172 features.
- Score table rows: 152,981.

## Core Consistency Checks

- Score rows match subset cells: True.
- Processed rows match subset cells: True.
- Cluster counts match cluster summary: True.
- Number of Leiden clusters: 8.

## Cell-Type Counts

- B cell: 151,570
- plasmablast: 1,411

## Donor Counts By Disease

- systemic lupus erythematosus: 160
- normal: 99

## Missing Values

- cell_type: 0
- author_cell_type: 0
- disease: 0
- disease_state: 0
- donor_id: 0
- ct_cov: 11,021

`ct_cov` missingness is inherited from the source CELLxGENE object, not caused by an incomplete local run. In the full source object, 469,803 of 1,263,676 cells have missing `ct_cov`, while `cell_type` has no missing values.

## Best Disease Test

- Cluster 1: mean SLE 0.2748, mean normal 0.1292, FDR 7.421e-14.

## Interpretation Notes

- The output is internally consistent for Phase 1.
- Because the CELLxGENE matrix is preprocessed/scaled, these results are suitable for state mapping and figure planning, not final raw-count differential expression.
- Donor-level cluster fraction tests reduce, but do not eliminate, pseudoreplication concerns.
