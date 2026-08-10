# Phase 2 Targets - 2026-06-24

## Current Position

The project has moved from Phase 1 exploratory B-cell mapping into Phase 2 marker refinement and manuscript-oriented result hardening.

The key upgrade today is that `adata.raw.X` in the B-cell subset was confirmed to behave like a non-negative integer count matrix. The scaled/preprocessed `X` remains unsuitable for raw-count differential expression, but `.raw.X` can support more rigorous marker refinement after normalization/log transformation.

## New Outputs Generated

- `02_analysis/scripts/14_raw_count_marker_refinement.py`
- `02_analysis/scripts/15_raw_count_rank_state_markers.py`
- `02_analysis/scripts/16_state_fraction_sensitivity.py`
- `02_analysis/scripts/17_make_figure2_v3_refined.py`
- `03_results/first_pass_bcell_full/marker_refinement/raw_count_marker_refinement_summary.md`
- `03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_marker_summary_by_state.csv`
- `03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_program_summary_by_state.csv`
- `03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_ranked_state_markers.csv`
- `03_results/first_pass_bcell_full/marker_refinement/figures/raw_count_state_marker_dotplot.png`
- `03_results/first_pass_bcell_full/marker_refinement/cluster_annotation_marker_review.csv`
- `03_results/first_pass_bcell_full/marker_refinement/sensitivity/donor_state_fraction_tests_exclude_Naive_B_III_-_small_naive-like_cluster.csv`
- `03_results/first_pass_bcell_full/figures/figure2_v3_refined_bcell_state_atlas.png`
- `03_results/first_pass_bcell_full/figures/figure2_v3_refined_bcell_state_atlas.pdf`
- `01_manuscript/figure2_v3_legend_draft.md`
- `02_analysis/RUNBOOK_phase2_refined_figure2.md`

## Updated Biological Interpretation

### Main Finding 1: Atypical ABC/APC-like B-cell state is robust

Cluster/state 5 remains the central pathogenic candidate.

Evidence:

- `ct_cov` support: enriched for `B_atypical` among non-missing cells.
- Curated marker panel: highest ABC/DN2 program among clusters.
- Raw-count ranked markers: `FCRL5`, `FCRL3`, `ZEB2`, `CD74`, `HLA-DRA`, `HLA-DRB1`, `HLA-DPB1`, `MS4A1`.
- Donor-level disease signal: higher in SLE.
- Sensitivity after excluding flagged cluster 6: still higher in SLE, FDR `1.68e-5`.

Working label:

`Atypical ABC/APC-like B`

Manuscript role:

This should be the central disease-associated B-cell state, framed around ABC/DN2-like and antigen-presenting features.

### Main Finding 2: SLE-enriched naive-like B state is strong but needs careful naming

Cluster/state 1 is the strongest donor-level disease signal.

Evidence:

- Donor-level FDR `7.42e-14` in original test.
- FDR `4.10e-14` after excluding flagged cluster 6.
- Raw-count markers: `TCL1A`, `VPREB3`, `CXCR4`, `CD79B`, plus activation/immediate-early genes `CD69`, `DUSP1`, `JUNB`, `FOS`.

Working label:

`Activated SLE-enriched naive-like B`

Manuscript role:

This can be a major result, but should not be overnamed as a fully distinct lineage until marker and trajectory/context analyses support it.

### Main Finding 3: Memory B-cell remodeling is reproducible

Cluster/state 2 is lower in SLE and remains significant after sensitivity testing.

Evidence:

- Original donor-level FDR `6.45e-13`.
- After excluding flagged cluster 6: FDR `8.94e-13`.
- Raw-count markers include `GPR183`, `LTB`, `CD1C`, `ARHGAP24`.

Working label:

`Memory-like B I`

Manuscript role:

This supports the broader claim that SLE changes B-cell compartment structure, not only one pathogenic cluster.

### Important Revision: Cluster 6 should be flagged

The previous label `Naive B III / small naive-like cluster` is now risky.

Raw-count ranked markers are dominated by platelet/ambient RNA genes:

- `PPBP`
- `PF4`
- `NRGN`
- `TUBB1`
- `RGS18`
- `CAVIN2`
- `GNG11`
- `SPARC`

Although the cluster still has B-cell metadata and B-cell markers, it should not be interpreted as a biological SLE-expanded naive B state without additional QC. The safest manuscript approach is to flag or remove it from central claims and show that main conclusions are stable when it is excluded.

### Plasmablast State

Cluster/state 7 is identity-secure:

- `MZB1`
- `JCHAIN`
- `XBP1`
- `TNFRSF17`
- `HSP90B1`
- `FKBP11`

However, donor-level SLE difference remains non-significant. It can be shown as a known endpoint state, but not as a primary SLE-expanded finding in this dataset.

## Phase 2 Core Objectives

1. Finalize the refined B-cell state model.
2. Build Figure 2 v3 using marker-refined labels.
3. Add QC/sensitivity panels or tables for the flagged platelet/ambient cluster.
4. Produce donor-aware analyses for the central ABC/APC-like state.
5. Start writing Results text around three durable axes:
   - Atypical ABC/APC-like B expansion.
   - Activated SLE-enriched naive-like B expansion.
   - Memory-like B-cell redistribution.

## Recommended Figure 2 v3 Structure

Panel A:

B-cell UMAP colored by refined state labels, with cluster 6 labeled as `Flagged platelet/ambient-high B`.

Panel B:

Raw-count marker dotplot using curated markers, including ABC/DN2, APC, naive, memory, plasmablast, and platelet/ambient markers.

Panel C:

Donor-level state fraction comparison for main retained states.

Panel D:

Sensitivity analysis excluding cluster 6, showing ABC/APC-like and activated naive-like findings remain significant.

Panel E:

Focused marker evidence for cluster 5: `FCRL5`, `FCRL3`, `ZEB2`, `CD74`, HLA genes.

## Near-Term Compute Tasks

Fast tasks already completed:

- Curated marker summary from raw counts.
- Balanced raw-count ranked marker analysis.
- Sensitivity analysis excluding flagged cluster 6.

Next compute tasks:

1. Make Figure 2 v3 panels from the refined marker/state outputs.
2. Run donor-level pseudobulk or aggregate expression analysis for cluster 5 vs other B cells.
3. Generate QC table for each state:
   - total raw counts,
   - genes detected,
   - platelet marker score,
   - mitochondrial/ribosomal marker proportions if available.
4. If computationally affordable, run full-cell or larger balanced Wilcoxon markers for state labels.

## Manuscript Direction

Provisional title direction:

`Single-cell dissection of disease-associated B-cell state remodeling in systemic lupus erythematosus`

Result section skeleton:

1. Construction of a B-lineage atlas from Perez/GSE174188.
2. Marker-refined B-cell states reveal ABC/APC-like and activated naive-like disease-associated compartments.
3. Donor-level abundance testing identifies robust SLE enrichment of ABC/APC-like and activated naive-like states.
4. Raw-count marker refinement flags a platelet/ambient RNA-high cluster, and sensitivity analysis preserves the main disease signals.
5. Plasmablasts form a clear transcriptional endpoint but are not significantly expanded at donor level in this cohort.
