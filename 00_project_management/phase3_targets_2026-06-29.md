# Phase 3 Targets - 2026-06-29

## Current Status

The project now has two manuscript-oriented figures in working form.

Figure 1:

- Dataset overview and B-lineage analysis workflow.
- Source object: 1,263,676 cells and 261 donors.
- B-lineage subset: 152,981 cells and 259 donors.
- B-lineage donor groups: 99 normal and 160 SLE donors.
- Analysis guardrails documented: scaled `X`, count-like `raw.X`, flagged platelet/ambient-high cluster.

Figure 2:

- Refined B-cell state atlas.
- Raw-count marker support.
- Donor-level abundance testing.
- Sensitivity analysis excluding the flagged platelet/ambient-high cluster.
- Program-level marker summary.

## Current Biological Model

The manuscript story is now coherent enough to support focused downstream analysis.

Core model:

1. SLE expands an atypical ABC/APC-like B-cell state.
2. SLE expands an activated naive-like B-cell state.
3. SLE is associated with redistribution/depletion of a memory-like B-cell state.
4. Plasmablasts are transcriptionally clear but are not the dominant significant donor-level abundance signal in this cohort.
5. A small platelet/ambient-high cluster should be flagged and excluded from central biological claims.

## Completed In This Step

- `02_analysis/scripts/18_make_figure1_dataset_overview.py`
- `03_results/figure1_dataset_overview/figures/figure1_dataset_overview.png`
- `03_results/figure1_dataset_overview/figures/figure1_dataset_overview.pdf`
- `03_results/figure1_dataset_overview/tables/figure1_dataset_summary.csv`
- `01_manuscript/figure1_legend_draft.md`
- `02_analysis/RUNBOOK_phase2_dataset_overview_figure1.md`

## Next Stage Recommendation

The next stage should be Phase 3:

**Donor-aware expression evidence and mechanism-focused Figure 3 for the atypical ABC/APC-like B-cell state.**

Reason:

Figures 1 and 2 already establish the atlas, labels, marker support, and donor-level abundance. The remaining gap for a Q1/Q2-style manuscript is stronger donor-aware evidence that the central ABC/APC-like B-cell state carries disease-relevant expression programs rather than being only an abundance cluster.

## Phase 3 Main Questions

1. Does the atypical ABC/APC-like B-cell state show donor-level enrichment of ABC/APC markers?
2. Are antigen-presentation genes and ABC/DN2-axis genes elevated in this state after donor aggregation?
3. Does this state show disease-state gradients within SLE, such as flare/managed/treated differences?
4. Can we build a compact Figure 3 around:
   - focused UMAP/location of ABC/APC-like state,
   - donor-level abundance,
   - donor-aggregated marker expression,
   - top raw-count markers,
   - disease-state stratification?

## Proposed Phase 3 Outputs

Scripts:

- `19_pseudobulk_state_expression.py`
- `20_make_figure3_abc_apc_focus.py`

Tables:

- donor-by-state pseudobulk expression matrix for curated marker genes.
- ABC/APC-like versus other B states donor-level marker comparison.
- SLE disease-state stratified abundance table.
- top donor-aware candidate markers for the ABC/APC-like state.

Figures:

- Figure 3 v1: focused ABC/APC-like B-cell pathogenic candidate panel.
- Supplemental QC figure: flagged platelet/ambient-high cluster details.

Manuscript:

- Results section focused on the atypical ABC/APC-like state.
- Methods paragraph for donor-level aggregation/pseudobulk marker analysis.

## Caution For Phase 3

The current data can support marker refinement and donor-level aggregation using `adata.raw.X`, but final disease differential expression should be framed carefully unless a full pseudobulk model with adequate donor-level replication and covariate checks is completed.

Avoid overclaiming:

- Do not claim plasmablast expansion as a primary SLE result.
- Do not treat the flagged platelet/ambient-high cluster as a real disease-expanded B-cell state.
- Do not use single-cell-level tests as final disease-level evidence.

## Phase 3 Success Criteria

Phase 3 is successful if it produces:

1. A donor-aware marker/program table supporting ABC/APC-like B-cell identity.
2. A focused Figure 3 draft that can stand next to Figures 1 and 2.
3. A Results subsection that explains why the ABC/APC-like state is the central pathogenic candidate.
4. A clear statement of limitations and sensitivity analyses.
