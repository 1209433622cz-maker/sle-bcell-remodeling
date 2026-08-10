# Methods Draft v1 - Figures 1 To 3

## Data Source

We analyzed the public Perez/GSE174188 CELLxGENE H5AD object containing 1,263,676 immune cells from 261 donors. The object was used as the processed single-cell reference for this phase of the study. Gene symbols were read from `var["feature_name"]` when mapping curated marker genes.

## B-Lineage Extraction

B-lineage cells were selected using the standardized CELLxGENE `cell_type` annotation. Cells annotated as `B cell` or `plasmablast` were retained, yielding 152,981 B-lineage cells from 259 donors. Donor-level disease metadata retained 99 normal donors and 160 SLE donors in the B-lineage subset.

## Matrix Handling

Initial inspection showed that the H5AD `X` matrix contained preprocessed/scaled values, including negative values. The analysis therefore did not apply raw-count normalization or log transformation to `X`. Provided PCA/UMAP representations were used for first-pass state mapping where available. Count-like analyses, including marker refinement and donor-state pseudobulk expression summaries, used `adata.raw.X`.

## First-Pass B-Cell State Mapping

B-lineage cells were processed using Scanpy. When the source object contained a precomputed PCA representation, neighbor graph construction used `X_pca` with 15 neighbors. UMAP coordinates from the source object were used when available. Leiden clustering was run at resolution 0.6 to define first-pass B-lineage clusters. Curated B-cell marker scores were added for exploratory annotation.

## State Annotation And Marker Refinement

First-pass Leiden clusters were refined into manuscript-oriented B-cell state labels using public metadata, curated marker expression, raw-count marker summaries from `adata.raw.X`, ranked state markers, and donor-level disease tests. Refined labels included resting naive B cells, activated SLE-naive-like B cells, memory-like states, an atypical ABC/APC-like B-cell state, a plasmablast/antibody-secreting cell state, and a flagged platelet/ambient-RNA-high cluster.

Raw-count marker summaries were calculated from `adata.raw.X`. Counts were normalized to counts per 10,000 and transformed as log1p(CP10K). Marker dotplots and state-level program summaries used curated marker sets for naive, memory, ABC/DN2, antigen-presentation, activation, interferon-response, plasmablast, and platelet/ambient programs.

## Donor-Level Abundance Testing

For donor-level state abundance analysis, cells were counted by donor and refined B-cell state. State fractions were calculated as the fraction of each donor's B-lineage cells assigned to a given state. Normal and SLE donor fractions were compared using Mann-Whitney U tests, with Benjamini-Hochberg correction across tested states. Sensitivity analysis repeated the donor-level fraction tests after excluding the flagged platelet/ambient-RNA-high cluster from the denominator.

## Donor-State Pseudobulk Program Analysis

For the ABC/APC-like focus analysis, cells were aggregated by donor, disease group, disease state, and refined B-cell state. Marker-gene counts were summed within each donor-state group from `adata.raw.X`, and CP10K values were calculated using total raw counts across all genes for the corresponding donor-state group. Expression values were transformed as log1p(CP10K).

Curated program scores were calculated as the mean marker-level log1p(CP10K) value for each donor-state group. Donor-state groups with fewer than 10 cells were excluded from program comparisons. The atypical ABC/APC-like state was compared with other retained B-cell states using Mann-Whitney U tests with Benjamini-Hochberg correction across marker genes or programs. The flagged platelet/ambient-RNA-high state was excluded from the main comparator.

## Figure Generation

Figures were generated in Python using Scanpy, pandas, NumPy, matplotlib, and seaborn. Figure 1 summarizes dataset scale, B-lineage extraction, donor retention, state sizes, and analysis guardrails. Figure 2 shows the refined B-cell state atlas, raw-count marker support, donor-level abundance testing, sensitivity analysis, and state-level marker programs. Figure 3 focuses on donor-aware expression evidence for the atypical ABC/APC-like B-cell state.

## Statistical Framing

Donor-level tests were treated as the primary evidence for disease-associated abundance differences. Single-cell visualizations and marker summaries were used for annotation and interpretation, not as final disease-level statistical evidence. Disease-state summaries within SLE were treated as descriptive because several strata had limited donor-state sample sizes.
