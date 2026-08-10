# Manuscript Planning Outline

## Working Title

Deciphering Single-Cell Multi-Omic and Genetic Regulatory Programs of Pathogenic B-Cell States in Systemic Lupus Erythematosus

## Core Claim

Pathogenic B-cell states in SLE are best understood as a connected state landscape rather than as isolated marker-defined subsets. Candidate drivers should be prioritized by convergence across disease-state specificity, trajectory or state-transition relevance, external immune regulatory support, and mechanistic plausibility from SLE-focused studies.

## Likely Article Type

Computational immunology manuscript with a mechanism-prioritization emphasis.

Possible positioning:

- Integrative re-analysis of public lupus single-cell datasets.
- State-focused B-cell atlas and regulatory prioritization.
- Hypothesis-generating resource for pathogenic B-cell mechanisms in SLE.

## Target-Neutral Formatting Assumption

Until a final journal is chosen, write for a flexible Q1/Q2 package:

- 4,500 to 6,500 word main text.
- 5 to 6 main figures.
- One 250-word structured abstract and one 350-word broader abstract.
- Up to 50 core references in the main manuscript, with additional references moved to supplement if needed.
- Supplementary figures for QC, replication, and robustness.
- Complete data and code availability statements from the start.

## Draft Structure

1. Abstract
2. Introduction
3. Results
4. Discussion
5. Methods
6. Data and code availability
7. Supplementary information

## Results Storyboard

Result 1: Public lupus and immune reference datasets define the analysis scope.

Result 2: B-cell re-clustering resolves pathogenic SLE-associated states.

Result 3: Pathway and program scoring places ABC/DN2-like, activated memory-like, plasmablast-associated, and APC-like states into a shared inflammatory landscape.

Result 4: Trajectory or neighborhood analysis tests whether these states form a connected continuum or separable endpoints.

Result 5: Integration with OneK1K/CIMA and mechanistic literature prioritizes candidate regulators and genetically supported programs.

Result 6: Tissue-context resources test whether blood-derived B-cell programs generalize to cutaneous lupus contexts.

## Figure Plan

Figure 1: Study design and dataset map.

Figure 2: Integrated SLE B-cell atlas and major pathogenic B-cell states.

Figure 3: Program scores and pathway modules across B-cell states.

Figure 4: State-transition, pseudotime, or similarity structure among pathogenic B-cell states.

Figure 5: Regulatory prioritization using lupus signatures, eQTL/xQTL support, GRN evidence, and mechanistic literature anchors.

Figure 6: External contextualization in tissue or broader autoimmune resources.

Supplementary figures:

- QC metrics and integration diagnostics.
- Marker tables for each B-cell state.
- Dataset-specific replication of key signatures.
- Sensitivity analysis for scoring and clustering choices.

## Tables

Table 1: Datasets and accessions.

Table 2: Marker genes and annotation evidence for prioritized B-cell states.

Table 3: Ranked candidate regulators and evidence layers.

Supplementary tables:

- Full differential expression results.
- Gene set scores.
- eQTL/xQTL overlap table.
- Ligand-receptor or interaction results if used.

## Open Decisions

- Use processed matrices/H5AD first, or reprocess raw FASTQ for a subset.
- Whether to make Perez et al. the primary lupus discovery dataset and use others for validation.
- How strongly to include CIMA/OneK1K if downloadable processed files are not yet local.
- Target journal level and formatting constraints.
