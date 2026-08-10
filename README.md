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
- Gate C2A supports full representation learning but its smoke-stage doublet
  calls are not freezable.
- Gate C2B-01 passed: 150,402 hard-QC cells by 30,172 genes were extracted from
  `raw/X` with protected outcomes removed from the working object.

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

Superseded proposal sources retained for provenance:

- `01_manuscript/proposal_basis_final_v4.docx`
- `01_manuscript/proposal_basis_humanized_v13.docx`
- `01_manuscript/proposal_latex_source/main.tex`: editable LaTeX proposal source.
- `00_project_management/legacy_rp_archive_2026-08-10/`: recovered Chinese, bilingual, working-draft, v7, and v10 versions; archive only.

The former `RP/` directory was deliberately removed during cleanup after these active files were moved. The original path mapping is recorded in `00_project_management/keepers_moved_2026-06-22.csv`.

## What Was Kept

- `Data/`: retained accession notes and currently available supplementary data.
- `PAPER/`: retained canonical English PDF literature set.
- `01_manuscript/`: retained the two most useful proposal basis documents and LaTeX proposal source.
- `99_admin_course_docs/`: moved course/admin documents out of the manuscript root.
- `00_project_management/`: cleanup manifests and movement logs.

## Cleanup Log

The large legacy folders and generated artifacts were removed from the active workspace on 2026-06-22. The main action log is:

- `00_project_management/cleanup_manifest_2026-06-22.csv`
- `00_project_management/cleanup_actions_2026-06-22.csv`
- `00_project_management/cleanup_manifest_extra_2026-06-22.csv`
- `00_project_management/cleanup_actions_extra_2026-06-22.csv`
- `00_project_management/keepers_moved_2026-06-22.csv`

Removed items were sent to the Windows Recycle Bin.

Exception: `RP/` and `RP-TT/` reappeared after the Recycle Bin operation on the H: drive, so they were permanently deleted after path verification. See `00_project_management/cleanup_actions_permanent_2026-06-22.csv`.

## Current Working Folders

- `01_manuscript/`: active RP, v7 blueprint and frozen v1-v6 manuscript sources.
- `02_analysis/`: established analysis scripts, environments and runbooks.
- `03_results/`: frozen analysis tables and figure outputs from completed phases.
- `04_submission/`: v6 provenance package, quality audits and v7 figure design.
- `audit_tools/`: active Phase 17 gate scripts and scientific decision reports.
- `phase17_v7/`: timestamped v7 raw-count rerun outputs.

## Near-Term Priorities

1. Complete Gate C2B1 Scrublet scoring on all complete technical libraries.
2. Review library-level rates, score distributions and mixed-lineage enrichment;
   freeze the doublet policy only after that review.
3. Rebuild full unintegrated and Harmony B-cell representations.
4. Freeze neutral states using markers, biological coverage and resampling
   stability before disease outcomes are unlocked.
5. Run cohort 4 primary composition and sample-by-state pseudobulk analyses;
   keep cohort 3 exploratory.
6. Apply a discovery-frozen mapper/signature to GSE135779 and finalize journal
   targeting only after Figures 3-5 are known.

## Local Compute Handoff

The discovery and validation datasets are already local. The next long run is
resumable complete-library doublet scoring. From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1 `
  -ResumeRunDir ".\phase17_v7\gateC2B1\20260810_171000_full_library_doublets"
```

The runner reuses the validated 258.1 MB full raw object and checkpoints every
completed library. Completion does not authorize automatic doublet exclusion;
the generated review report is the next decision gate.

## Active design documents

- `00_project_management/advisor_full_project_reassessment_2026-08-10.md`
- `00_project_management/external_audit_action_crosswalk_2026-08-10.md`
- `00_project_management/next_stage_decision_2026-08-10.md`
- `01_manuscript/manuscript_v7_scientific_blueprint_2026-08-10.md`
- `01_manuscript/figure1_v7_legend_draft_2026-08-10.md`
- `04_submission/figure_architecture_v7_nature_style_2026-08-10.md`
- `03_results/phase17_v7_figure1_study_design_2026-08-10/figures/figure1_v7_study_design.pdf`
- `03_results/phase17_v7_figure1_study_design_2026-08-10/FIGURE1_TECHNICAL_QC.md`
- `phase17_v7/gateC2A/20260810_164012_smoke/16_GATE_C2A_DECISION.md`
- `phase17_v7/gateC1/20260806_134213_hotfix_v1_1/16_STRICT_COMMON_SUPPORT_ERRATUM.md`
- `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/09_GATE_C2B1_PREPARATION_STATUS.md`

## Reproducibility locks

- `audit_tools/environment_phase17_v7_resolved_2026-08-10.yml`: resolved cross-platform-style environment export.
- `audit_tools/environment_phase17_v7_explicit_win64_2026-08-10.txt`: exact Windows conda package URLs.
- `audit_tools/environment_phase17_v7_pip_freeze_2026-08-10.txt`: four pip-channel overrides required after the explicit conda install.
