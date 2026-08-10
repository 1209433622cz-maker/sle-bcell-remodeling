# Phase 4 Targets - 2026-06-29

## Current Status After Phase 3

The project now has three manuscript-oriented main figures in working form.

Figure 1:

- Dataset overview and B-lineage workflow.
- Source object: 1,263,676 cells and 261 donors.
- B-lineage subset: 152,981 cells and 259 donors.
- B-lineage donor groups: 99 normal and 160 SLE donors.

Figure 2:

- Refined B-cell state atlas.
- Raw-count marker support from `adata.raw.X`.
- Donor-level abundance testing.
- Sensitivity analysis excluding the flagged platelet/ambient-RNA-high state.

Figure 3:

- Donor-aware ABC/APC-like focus figure.
- Donor-state pseudobulk marker and program evidence.
- SLE abundance expansion confirmed before and after flagged-state exclusion.
- Disease-state descriptive summary for the focus state.

## Current Manuscript Model

The strongest story is now:

1. SLE expands an atypical ABC/APC-like B-cell state.
2. This state is supported by donor-aware ABC/DN2 and antigen-presentation programs.
3. SLE also expands an activated naive-like B-cell state.
4. A memory-like B-cell state is reduced or redistributed in SLE.
5. Plasmablasts are transcriptionally clear but are not the dominant donor-level disease signal in this cohort.
6. A platelet/ambient-RNA-high cluster is explicitly flagged and excluded from central biological claims.

## Phase 3 Completion Checklist

- Completed `02_analysis/scripts/19_pseudobulk_state_expression.py`.
- Completed `02_analysis/scripts/20_make_figure3_abc_apc_focus.py`.
- Generated `03_results/figure3_abc_apc_focus/figures/figure3_v1_abc_apc_focus.png`.
- Generated `03_results/figure3_abc_apc_focus/figures/figure3_v1_abc_apc_focus.pdf`.
- Generated donor-state pseudobulk tables and ABC/APC-like evidence tables.
- Added `01_manuscript/figure3_v1_legend_draft.md`.
- Added `01_manuscript/results_draft_phase3.md`.
- Added `02_analysis/RUNBOOK_phase3_abc_apc_focus.md`.

## Early Phase 4 Progress Completed

- Added `01_manuscript/results_draft_v1_figures1_to3.md`.
- Added `01_manuscript/methods_draft_v1_figures1_to3.md`.
- Added `00_project_management/manuscript_evidence_table_2026-06-29.csv`.
- Added `02_analysis/scripts/21_make_supplement_qc_flagged_cluster.py`.
- Generated `03_results/supplement_qc_flagged_cluster/figures/supplement_qc_flagged_cluster.png`.
- Generated `03_results/supplement_qc_flagged_cluster/figures/supplement_qc_flagged_cluster.pdf`.
- Added `01_manuscript/supplement_qc_flagged_cluster_legend_draft.md`.
- Added `02_analysis/RUNBOOK_phase4_supplement_qc_flagged_cluster.md`.
- Added `01_manuscript/title_abstract_options_v1.md`.

## Recommended Next Stage

Phase 4 should shift from broad discovery to manuscript assembly and robustness.

The priority should be:

1. Build a coherent Results draft around Figures 1 to 3.
2. Create a supplement/QC figure for the flagged platelet/ambient-RNA-high cluster and key sensitivity checks.
3. Add a compact Methods draft covering data source, B-lineage extraction, state refinement, donor-level abundance testing, and donor-state pseudobulk program analysis.
4. Decide whether a Figure 4 is needed. The best candidate Figure 4 would be either external/literature validation of the ABC/APC-like state or a concise disease-state/covariate sensitivity figure.
5. Start assembling a submission-readiness checklist for Q1/Q2 SCI journals, including data availability, code availability, reproducibility, figure resolution, and limitations.

## Why This Should Be The Next Stage

The core evidence chain is already strong enough to write:

- Figure 1 establishes the dataset and guardrails.
- Figure 2 establishes the refined state atlas and disease-associated remodeling.
- Figure 3 strengthens the central ABC/APC-like claim with donor-aware expression evidence.

Adding more analyses before writing could dilute the story. The manuscript now needs controlled claims, clean methods, and robustness documentation. After the first full draft, we can identify the exact missing analysis needed for the target journal.

## Immediate Phase 4 Tasks

1. Completed: merge `results_draft_phase2.md` and `results_draft_phase3.md` into a full Results section.
2. Completed: draft a Methods section from the runbooks and scripts.
3. Completed: generate a supplemental QC figure for the flagged platelet/ambient-RNA-high state.
4. Completed: build a manuscript evidence table linking each claim to a figure panel, table, script, and limitation.
5. Completed: prepare a journal-agnostic abstract and title set for SCI Q1/Q2 positioning.
6. Next: decide whether Figure 4 should be external/literature validation, covariate sensitivity, or a compact graphical model.
