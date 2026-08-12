# 6013RP-wyf Active Workspace

This is the active workspace for a raw-count, hierarchy-aware single-cell study
of B-cell remodeling in systemic lupus erythematosus (SLE).

Private working repository:
[`1209433622cz-maker/sle-bcell-remodeling-v7`](https://github.com/1209433622cz-maker/sle-bcell-remodeling-v7).
Raw matrices, archives and cell-level exports are accession/checksum managed
outside Git.

## Active Direction

Working title:

**Donor- and cohort-resolved single-cell analysis separates compositional and
transcriptional B-cell remodeling in systemic lupus erythematosus**

Current scientific center:

- Reconstruct neutral B-cell states from authoritative raw counts without
  disease labels.
- Separate sample-level state abundance changes from within-state SLE
  transcription using cohort-supported contrasts.
- Freeze discovery states and signatures before independent validation.
- Treat interferon, ZEB2/TBX21, TLR7/FTO and APC programs as candidate
  interpretation unless direct perturbational or causal evidence exists.

Active advisor decision:

- v6 is frozen for provenance and is not submission-ready.
- v7/Phase 17 is the active analysis generation.
- Gate C2B1 passed programmatically after complete-library residual-risk scoring:
  150,402/150,402 cells and 88/88 libraries reconciled exactly.
- The 1,972 automatic residual-risk calls (1.31%) are sensitivity-only; no
  second-round automatic deletion is authorized before disease-blind graph review.
- Full-PBMC audit supports source `B cell` plus `plasmablast` labels as the
  primary input; 768 core-BCR-supported external candidates are mapping-only.
- Gate C2B2 full disease-blind representation is the active compute gate.

## Research Proposal (RP)

The active proposal files are:

- `01_manuscript/research_proposal_v14_methodologically_revised_2026-08-10.docx`:
  active methodologically revised proposal.
- `01_manuscript/research_proposal_v14_methodologically_revised_2026-08-10.pdf`:
  rendered and visually checked 10-page proposal.
- `01_manuscript/research_proposal_v14_methodologically_revised_2026-08-10.md`:
  version-controlled proposal source.
- `04_submission/document_qc/research_proposal_v14_2026-08-10_external_audit_integrated_qc_r2/RESEARCH_PROPOSAL_V14_QC.md`:
  final render, content-consistency and accessibility audit.

Selected proposal sources retained for provenance:

- `01_manuscript/proposal_basis_final_v4.docx`
- `01_manuscript/proposal_basis_humanized_v13.docx`
- `01_manuscript/proposal_latex_source/main.tex`: editable LaTeX proposal source.

## Repository Layout

- `00_project_management/`: scientific audits, evidence tables and gate decisions.
- `01_manuscript/`: active RP, v7 blueprint and frozen manuscript provenance.
- `02_analysis/`: analysis scripts, environments, data inventory and runbooks.
- `03_results/`: the active v7 Figure 1 bundle and its source tables.
- `04_submission/`: current figure architecture and RP quality-control records.
- `audit_tools/`: active Phase 17 gate scripts and scientific decision reports.
- `phase17_v7/`: compact gate summaries and diagnostic figures required to audit
  the v7 rerun.

Raw and processed matrices, source literature, local administration files,
large per-cell exports and software-test artifacts remain outside Git. Their
accessions, checksums and reconstruction instructions are recorded in the
tracked manifests and `REPRODUCIBILITY.md`.

## Near-Term Priorities

1. Complete Gate C2B2 full recurrent-HVG, unintegrated and Harmony representations.
2. Compare all-hard-QC, residual-risk-negative and ISG-excluded branches; document
   the source-feature limitation that makes IG-dominance sensitivity non-evaluable.
3. Audit technical mixing, bridge-sample concordance and biological marker conservation.
4. Freeze neutral states using markers, biological coverage and resampling
   stability before disease outcomes are unlocked.
5. Run cohort 4 primary composition and sample-by-state pseudobulk analyses;
   keep cohort 3 exploratory.
6. Apply a discovery-frozen mapper/signature to GSE135779 and finalize journal
   targeting only after Figures 3-5 are known.

## Local Compute Handoff

The discovery and validation datasets are already local. The next long run is
the resumable Gate C2B2 representation workflow. From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B2_full_representation.ps1 `
  -ResumeRunDir ".\phase17_v7\gateC2B2\20260812_full_representation"
```

The runner first freezes disease-blind recurrent-HVG inputs and then checkpoints
each of three representation branches independently. Repeating the same command
reuses every valid checkpoint. Formal full-data review, not software-test output,
determines whether Gate C2B2 passes to neutral state freezing.
If the review reports Harmony non-convergence at 20 iterations, rerun the same
directory with `-HarmonyMaxIter 40`; lower-limit checkpoints are then recomputed.

## Active design documents

- `00_project_management/advisor_full_project_reassessment_2026-08-10.md`
- `00_project_management/external_audit_action_crosswalk_2026-08-10.md`
- `00_project_management/next_stage_decision_2026-08-12.md`
- `00_project_management/phase17_integrity_audit_2026-08-12.md`
- `01_manuscript/manuscript_v7_scientific_blueprint_2026-08-10.md`
- `01_manuscript/figure1_v7_legend_draft_2026-08-10.md`
- `04_submission/figure_architecture_v7_nature_style_2026-08-10.md`
- `03_results/phase17_v7_figure1_study_design_2026-08-10/figures/figure1_v7_study_design.pdf`
- `03_results/phase17_v7_figure1_study_design_2026-08-10/FIGURE1_TECHNICAL_QC.md`
- `phase17_v7/gateC2A/20260810_164012_smoke/16_GATE_C2A_DECISION.md`
- `phase17_v7/gateC1/20260806_134213_hotfix_v1_1/16_STRICT_COMMON_SUPPORT_ERRATUM.md`
- `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/16_GATE_C2B1_DECISION.md`
- `phase17_v7/gateC2B2_prechecks/blineage_extraction_completeness/10_BLINEAGE_INPUT_DECISION.md`

## Reproducibility locks

- `audit_tools/environment_phase17_v7_resolved_2026-08-10.yml`: resolved cross-platform-style environment export.
- `audit_tools/environment_phase17_v7_explicit_win64_2026-08-10.txt`: exact Windows conda package URLs.
- `audit_tools/environment_phase17_v7_pip_freeze_2026-08-10.txt`: four pip-channel overrides required after the explicit conda install.
