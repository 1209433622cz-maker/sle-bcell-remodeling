from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BundleAsset:
    source: str
    package_relpath: str
    role: str
    required: bool = True
    note: str = ""


ASSETS: list[BundleAsset] = [
    BundleAsset(
        "01_manuscript/manuscript_v5_genome_medicine_targeted.md",
        "main_text/manuscript_v5_genome_medicine_targeted.md",
        "main_text_targeted",
        note="Primary Genome Medicine-targeted draft generated reproducibly from manuscript v4.",
    ),
    BundleAsset(
        "01_manuscript/manuscript_v4_nature_style_refined.md",
        "main_text/manuscript_v4_nature_style_refined.md",
        "main_text",
        note="Preferred Nature-style refined manuscript draft.",
    ),
    BundleAsset(
        "01_manuscript/manuscript_v3_upper_q1_working.md",
        "main_text/manuscript_v3_upper_q1_working.md",
        "main_text_comparison",
        note="Full upper-Q1 working manuscript draft retained for comparison.",
    ),
    BundleAsset(
        "01_manuscript/manuscript_v2_submission_style.md",
        "main_text/manuscript_v2_submission_style.md",
        "main_text_fallback",
        note="Conservative fallback manuscript draft retained for comparison.",
    ),
    BundleAsset(
        "01_manuscript/title_abstract_options_v1.md",
        "main_text/title_abstract_options_v1.md",
        "main_text_support",
        note="Alternative title/abstract options.",
    ),
    BundleAsset(
        "01_manuscript/references_working_v1.bib",
        "references/references_working_v1.bib",
        "references_source",
        note="Working BibTeX file; metadata still require final verification.",
    ),
    BundleAsset(
        "01_manuscript/references_verified_crossref_2026-07-09.bib",
        "references/references_verified_crossref_2026-07-09.bib",
        "references_source_verified",
        note="Crossref-derived BibTeX; final target-journal style still requires verification.",
    ),
    BundleAsset(
        "01_manuscript/citation_signature_audit_v1.md",
        "internal_qc/citation_signature_audit_v1.md",
        "internal_qc",
        note="Citation-to-signature audit notes.",
    ),
    BundleAsset(
        "01_manuscript/figure1_legend_draft.md",
        "main_text/figure_legends/figure1_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/figure2_v3_legend_draft.md",
        "main_text/figure_legends/figure2_v3_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/figure3_v1_legend_draft.md",
        "main_text/figure_legends/figure3_v1_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/figure4_v1_legend_draft.md",
        "main_text/figure_legends/figure4_v1_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/figure5_v1_legend_draft.md",
        "main_text/figure_legends/figure5_v1_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/supplement_qc_flagged_cluster_legend_draft.md",
        "main_text/figure_legends/supplement_qc_flagged_cluster_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/figure6_gse163121_validation_legend_draft.md",
        "main_text/figure_legends/figure6_gse163121_validation_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/figure6_gse135779_validation_legend_draft.md",
        "main_text/figure_legends/figure6_gse135779_validation_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/figure7_onek1k_reference_context_legend_draft.md",
        "main_text/figure_legends/figure7_onek1k_reference_context_legend_draft.md",
        "figure_legend",
    ),
    BundleAsset(
        "01_manuscript/results_draft_phase10_external_validation.md",
        "main_text/results_drafts/results_draft_phase10_external_validation.md",
        "main_text_support",
    ),
    BundleAsset(
        "01_manuscript/results_draft_phase12_onek1k_reference_context.md",
        "main_text/results_drafts/results_draft_phase12_onek1k_reference_context.md",
        "main_text_support",
    ),
    BundleAsset(
        "01_manuscript/methods_external_validation_addendum.md",
        "main_text/methods_external_validation_addendum.md",
        "main_text_support",
    ),
    BundleAsset(
        "03_results/figure1_dataset_overview/figures/figure1_dataset_overview.png",
        "figures_main/Figure_1_dataset_overview.png",
        "main_figure",
    ),
    BundleAsset(
        "03_results/figure1_dataset_overview/figures/figure1_dataset_overview.pdf",
        "figures_main/Figure_1_dataset_overview.pdf",
        "main_figure_pdf",
    ),
    BundleAsset(
        "03_results/first_pass_bcell_full/figures/figure2_v3_refined_bcell_state_atlas.png",
        "figures_main/Figure_2_refined_bcell_state_atlas.png",
        "main_figure",
    ),
    BundleAsset(
        "03_results/first_pass_bcell_full/figures/figure2_v3_refined_bcell_state_atlas.pdf",
        "figures_main/Figure_2_refined_bcell_state_atlas.pdf",
        "main_figure_pdf",
    ),
    BundleAsset(
        "03_results/figure3_abc_apc_focus/figures/figure3_v1_abc_apc_focus.png",
        "figures_main/Figure_3_abc_apc_focus.png",
        "main_figure",
    ),
    BundleAsset(
        "03_results/figure3_abc_apc_focus/figures/figure3_v1_abc_apc_focus.pdf",
        "figures_main/Figure_3_abc_apc_focus.pdf",
        "main_figure_pdf",
    ),
    BundleAsset(
        "03_results/figure4_covariate_sensitivity/figures/figure4_v1_covariate_sensitivity.png",
        "figures_main/Figure_4_covariate_sensitivity.png",
        "main_or_supplementary_figure",
        note="Move to supplementary Figure S2 if the selected journal allows only four main figures.",
    ),
    BundleAsset(
        "03_results/figure4_covariate_sensitivity/figures/figure4_v1_covariate_sensitivity.pdf",
        "figures_main/Figure_4_covariate_sensitivity.pdf",
        "main_figure_pdf",
    ),
    BundleAsset(
        "03_results/figure5_literature_signature_validation/figures/figure5_v1_literature_signature_validation.png",
        "figures_main/Figure_5_literature_signature_validation.png",
        "main_figure",
    ),
    BundleAsset(
        "03_results/figure5_literature_signature_validation/figures/figure5_v1_literature_signature_validation.pdf",
        "figures_main/Figure_5_literature_signature_validation.pdf",
        "main_figure_pdf",
    ),
    BundleAsset(
        "03_results/supplement_qc_flagged_cluster/figures/supplement_qc_flagged_cluster.png",
        "figures_supplementary/Supplementary_Figure_S1_flagged_cluster_qc.png",
        "supplementary_figure",
    ),
    BundleAsset(
        "03_results/supplement_qc_flagged_cluster/figures/supplement_qc_flagged_cluster.pdf",
        "figures_supplementary/Supplementary_Figure_S1_flagged_cluster_qc.pdf",
        "supplementary_figure_pdf",
    ),
    BundleAsset(
        "03_results/gse163121_bcell_validation/figures/figure6_gse163121_independent_bcell_validation.png",
        "figures_validation/Figure_6_candidate_gse163121_independent_bcell_validation.png",
        "validation_figure",
        note="Small validation/boundary figure; keep supplementary now that GSE135779 succeeded.",
    ),
    BundleAsset(
        "03_results/gse135779_bcell_validation/figures/figure6_gse135779_large_cohort_validation.png",
        "figures_main/Figure_6_gse135779_large_cohort_validation.png",
        "main_figure",
        note="Preferred main Figure 6 for the Q1 package.",
    ),
    BundleAsset(
        "03_results/gse135779_bcell_validation/figures/figure6_gse135779_large_cohort_validation.pdf",
        "figures_main/Figure_6_gse135779_large_cohort_validation.pdf",
        "main_figure_pdf",
        note="Vector/PDF export for journal formatting.",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/figures/figure7_candidate_onek1k_bcell_reference_context.png",
        "figures_validation/Figure_7_candidate_OneK1K_Bcell_reference_context.png",
        "external_reference_figure",
        note="Use as main Figure 7 only for the upper-Q1 route; otherwise keep as supplementary regulatory-context figure.",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/figures/figure7_candidate_onek1k_bcell_reference_context.pdf",
        "figures_validation/Figure_7_candidate_OneK1K_Bcell_reference_context.pdf",
        "external_reference_figure_pdf",
        note="Vector/PDF export for journal formatting.",
    ),
    BundleAsset(
        "04_submission/outputs/supplementary_tables_2026-07-22/Supplementary_Tables_S1-S12.xlsx",
        "tables_supplementary/Supplementary_Tables_S1-S12.xlsx",
        "supplementary_tables_workbook",
        note="Preferred machine-readable supplementary table file; 23 worksheets cover Tables S1-S12 and subparts.",
    ),
    BundleAsset(
        "03_results/figure1_dataset_overview/tables/figure1_dataset_summary.csv",
        "tables_supplementary/Supplementary_Table_S1_dataset_summary.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/figure1_dataset_overview/tables/bcell_refined_state_counts.csv",
        "tables_supplementary/Supplementary_Table_S2_refined_bcell_state_counts.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/first_pass_bcell_full/tables/state_level/donor_state_fraction_disease_tests.csv",
        "tables_supplementary/Supplementary_Table_S3_donor_state_abundance_tests.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_marker_summary_by_state.csv",
        "tables_supplementary/Supplementary_Table_S4_raw_count_marker_summary_by_state.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/figure3_abc_apc_focus/tables/abc_apc_vs_other_program_tests.csv",
        "tables_supplementary/Supplementary_Table_S5_abc_apc_pseudobulk_program_tests.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/figure4_covariate_sensitivity/tables/state_abundance_covariate_models.csv",
        "tables_supplementary/Supplementary_Table_S6_covariate_adjusted_abundance_models.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/figure5_literature_signature_validation/tables/abc_apc_vs_other_literature_signature_tests.csv",
        "tables_supplementary/Supplementary_Table_S7_literature_signature_tests.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/figure5_literature_signature_validation/tables/literature_informed_signature_catalog.csv",
        "tables_supplementary/Supplementary_Table_S8_literature_signature_catalog.csv",
        "supplementary_table",
        note="Citation metadata require final verification before submission.",
    ),
    BundleAsset(
        "03_results/supplement_qc_flagged_cluster/tables/flagged_cluster_top_ranked_markers.csv",
        "tables_supplementary/Supplementary_Table_S9a_flagged_cluster_top_ranked_markers.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/supplement_qc_flagged_cluster/tables/flagged_cluster_selected_marker_expression.csv",
        "tables_supplementary/Supplementary_Table_S9b_flagged_cluster_selected_marker_expression.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/supplement_qc_flagged_cluster/tables/core_state_sensitivity_original_vs_exclude_flagged.csv",
        "tables_supplementary/Supplementary_Table_S9c_core_state_sensitivity_excluding_flagged_cluster.csv",
        "supplementary_table",
    ),
    BundleAsset(
        "03_results/gse163121_bcell_validation/tables/gse163121_sample_program_scores.csv",
        "tables_validation/GSE163121_sample_program_scores.csv",
        "validation_table",
    ),
    BundleAsset(
        "03_results/gse163121_bcell_validation/tables/gse163121_sample_program_score_tests.csv",
        "tables_validation/GSE163121_sample_program_score_tests.csv",
        "validation_table",
    ),
    BundleAsset(
        "03_results/gse163121_bcell_validation/tables/gse163121_marker_summary_by_disease.csv",
        "tables_validation/GSE163121_marker_summary_by_disease.csv",
        "validation_table",
    ),
    BundleAsset(
        "03_results/gse135779_validation_readiness/tables/gse135779_metadata_summary.csv",
        "tables_validation/GSE135779_metadata_summary.csv",
        "validation_readiness_table",
    ),
    BundleAsset(
        "03_results/gse135779_validation_readiness/tables/gse135779_program_gene_presence.csv",
        "tables_validation/GSE135779_program_gene_presence.csv",
        "validation_readiness_table",
    ),
    BundleAsset(
        "03_results/gse135779_bcell_validation/tables/gse135779_donor_program_scores.csv",
        "tables_validation/GSE135779_donor_program_scores.csv",
        "validation_table",
    ),
    BundleAsset(
        "03_results/gse135779_bcell_validation/tables/gse135779_donor_program_score_tests.csv",
        "tables_validation/GSE135779_donor_program_score_tests.csv",
        "validation_table",
    ),
    BundleAsset(
        "03_results/gse135779_bcell_validation/tables/gse135779_marker_summary_by_disease.csv",
        "tables_validation/GSE135779_marker_summary_by_disease.csv",
        "validation_table",
    ),
    BundleAsset(
        "04_submission/figure_triage_v1.md",
        "submission_docs/figure_triage_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/figure_triage_nature_style_2026-07-22.md",
        "submission_docs/figure_triage_nature_style_2026-07-22.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/journal_target_decision_matrix_v1.md",
        "submission_docs/journal_target_decision_matrix_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/journal_shortlist_upper_q1_2026-07-09.md",
        "submission_docs/journal_shortlist_upper_q1_2026-07-09.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/final_formatting_todo_by_journal_type_v1.md",
        "submission_docs/final_formatting_todo_by_journal_type_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/upper_q1_validation_strategy_v1.md",
        "submission_docs/upper_q1_validation_strategy_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/external_regulatory_evidence_strategy_v1.md",
        "submission_docs/external_regulatory_evidence_strategy_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/supplementary_tables_index_v1.md",
        "submission_docs/supplementary_tables_index_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/data_code_availability_v1.md",
        "submission_docs/data_code_availability_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/cover_letter_pitch_v1.md",
        "submission_docs/cover_letter_pitch_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/cover_letter_genome_medicine_draft_2026-07-22.md",
        "submission_docs/cover_letter_genome_medicine_draft_2026-07-22.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/manuscript_qc_v1.md",
        "submission_docs/manuscript_qc_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/genome_medicine_target_alignment_2026-07-22.md",
        "submission_docs/genome_medicine_target_alignment_2026-07-22.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/advisor_full_project_audit_2026-07-22.md",
        "submission_docs/advisor_full_project_audit_2026-07-22.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/advisor_full_project_audit_v2_2026-07-22.md",
        "submission_docs/advisor_full_project_audit_v2_2026-07-22.md",
        "submission_planning",
        note="Current advisor-level scientific and submission-readiness audit.",
    ),
    BundleAsset(
        "04_submission/manuscript_v3_numeric_claim_audit.md",
        "internal_qc/manuscript_v3_numeric_claim_audit.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/manuscript_v4_numeric_claim_audit_2026-07-22.md",
        "internal_qc/manuscript_v4_numeric_claim_audit_2026-07-22.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/manuscript_structure_qc/manuscript_v3_structure_qc_2026-07-09.csv",
        "internal_qc/manuscript_v3_structure_qc_2026-07-09.csv",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/manuscript_structure_qc/manuscript_v3_structure_qc_2026-07-09.md",
        "internal_qc/manuscript_v3_structure_qc_2026-07-09.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/manuscript_structure_qc/manuscript_v3_upper_q1_working_structure_qc_2026-07-22.md",
        "internal_qc/manuscript_v3_upper_q1_working_structure_qc_2026-07-22.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/manuscript_structure_qc/manuscript_v4_nature_style_refined_structure_qc_2026-07-22.md",
        "internal_qc/manuscript_v4_nature_style_refined_structure_qc_2026-07-22.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/manuscript_structure_qc/manuscript_v5_genome_medicine_targeted_structure_qc_2026-07-22.md",
        "internal_qc/manuscript_v5_genome_medicine_targeted_structure_qc_2026-07-22.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/figure_quality_qc/figure_quality_qc_2026-07-22.md",
        "internal_qc/figure_quality_qc_2026-07-22.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/figure_quality_qc/figure_quality_qc_2026-07-22.csv",
        "internal_qc/figure_quality_qc_2026-07-22.csv",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/figure_quality_qc/figure_contact_sheet_2026-07-22.png",
        "internal_qc/figure_contact_sheet_2026-07-22.png",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/reference_verification/reference_verification_crossref_2026-07-09.csv",
        "internal_qc/reference_verification_crossref_2026-07-09.csv",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/reference_verification/reference_verification_crossref_2026-07-09.md",
        "internal_qc/reference_verification_crossref_2026-07-09.md",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/reviewer_risk_register_v1.md",
        "submission_docs/reviewer_risk_register_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/submission_package_checklist_v1.md",
        "submission_docs/submission_package_checklist_v1.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/submission_package_checklist_v2_2026-07-22.md",
        "submission_docs/submission_package_checklist_v2_2026-07-22.md",
        "submission_planning",
    ),
    BundleAsset(
        "04_submission/submission_manifest_v1.csv",
        "internal_qc/submission_manifest_v1.csv",
        "internal_qc",
    ),
    BundleAsset(
        "04_submission/submission_manifest_v1.md",
        "internal_qc/submission_manifest_v1.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/manuscript_evidence_table_2026-06-29.csv",
        "internal_qc/manuscript_evidence_table_2026-06-29.csv",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/citation_audit_2026-07-01/signature_to_citation_audit_2026-07-01.csv",
        "internal_qc/signature_to_citation_audit_2026-07-01.csv",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase9_targets_2026-07-01.md",
        "internal_qc/phase9_targets_2026-07-01.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase10_targets_2026-07-07.md",
        "internal_qc/phase10_targets_2026-07-07.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase11_targets_2026-07-08.md",
        "internal_qc/phase11_targets_2026-07-08.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase12_targets_2026-07-08.md",
        "internal_qc/phase12_targets_2026-07-08.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase13_targets_2026-07-08.md",
        "internal_qc/phase13_targets_2026-07-08.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase14_targets_2026-07-09.md",
        "internal_qc/phase14_targets_2026-07-09.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase15_targets_2026-07-22.md",
        "internal_qc/phase15_targets_2026-07-22.md",
        "internal_qc",
    ),
    BundleAsset(
        "00_project_management/phase16_targets_2026-07-22.md",
        "internal_qc/phase16_targets_2026-07-22.md",
        "internal_qc",
    ),
    BundleAsset(
        "03_results/gse163121_bcell_validation/gse163121_bcell_validation_summary.md",
        "internal_qc/gse163121_bcell_validation_summary.md",
        "internal_qc",
    ),
    BundleAsset(
        "03_results/gse135779_validation_readiness/gse135779_validation_readiness_summary.md",
        "internal_qc/gse135779_validation_readiness_summary.md",
        "internal_qc",
    ),
    BundleAsset(
        "03_results/gse135779_bcell_validation/gse135779_bcell_validation_summary.md",
        "internal_qc/gse135779_bcell_validation_summary.md",
        "internal_qc",
    ),
    BundleAsset(
        "03_results/onek1k_cellxgene_inspection/onek1k_cellxgene_inspection_summary.md",
        "internal_qc/onek1k_cellxgene_inspection_summary.md",
        "internal_qc",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/onek1k_bcell_reference_context_summary.md",
        "internal_qc/onek1k_bcell_reference_context_summary.md",
        "internal_qc",
    ),
    BundleAsset(
        "Data/processed/GSE196830_onek1k_cellxgene/source/checksums_sha256_2026-07-08.txt",
        "internal_qc/OneK1K_checksums_sha256_2026-07-08.txt",
        "internal_qc",
        note="Checksum record only; large H5AD is intentionally not copied into the working submission package.",
    ),
    BundleAsset(
        "03_results/onek1k_cellxgene_inspection/tables/onek1k_cellxgene_collection_metadata.csv",
        "tables_validation/OneK1K_cellxgene_collection_metadata.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_cellxgene_inspection/tables/onek1k_b_lineage_like_summary.csv",
        "tables_validation/OneK1K_b_lineage_like_summary.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_cellxgene_inspection/tables/onek1k_manuscript_gene_presence.csv",
        "tables_validation/OneK1K_manuscript_gene_presence.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_cellxgene_inspection/tables/onek1k_top_cell_type_counts.csv",
        "tables_validation/OneK1K_top_cell_type_counts.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/tables/onek1k_bcell_cell_type_counts.csv",
        "tables_validation/OneK1K_bcell_cell_type_counts.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/tables/onek1k_bcell_program_gene_presence.csv",
        "tables_validation/OneK1K_bcell_program_gene_presence.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/tables/onek1k_bcell_target_gene_presence.csv",
        "tables_validation/OneK1K_bcell_target_gene_presence.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/tables/onek1k_bcell_program_summary_by_cell_type.csv",
        "tables_validation/OneK1K_bcell_program_summary_by_cell_type.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/tables/onek1k_bcell_program_summary_by_donor_cell_type.csv",
        "tables_validation/OneK1K_bcell_program_summary_by_donor_cell_type.csv",
        "external_reference_table",
    ),
    BundleAsset(
        "03_results/onek1k_bcell_reference_context/tables/onek1k_bcell_marker_expression_by_cell_type.csv",
        "tables_validation/OneK1K_bcell_marker_expression_by_cell_type.csv",
        "external_reference_table",
    ),
]


def copy_asset(project_root: Path, package_root: Path, asset: BundleAsset) -> dict[str, object]:
    source = project_root / asset.source
    destination = package_root / asset.package_relpath
    exists = source.exists()
    copied = False
    size_bytes = 0
    if exists:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied = True
        size_bytes = destination.stat().st_size
    return {
        "source": asset.source,
        "package_path": str(destination.relative_to(project_root)),
        "role": asset.role,
        "required": asset.required,
        "exists": exists,
        "copied": copied,
        "size_bytes": size_bytes,
        "note": asset.note,
    }


def write_manifest_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_manifest_md(path: Path, rows: list[dict[str, object]]) -> None:
    missing = [row for row in rows if not row["exists"]]
    copied = [row for row in rows if row["copied"]]
    total_bytes = sum(int(row["size_bytes"]) for row in copied)
    lines = [
        "# Submission Asset Bundle Manifest",
        "",
        "## Status",
        "",
        f"- Assets listed: {len(rows)}.",
        f"- Assets copied: {len(copied)}.",
        f"- Missing required assets: {sum(1 for row in missing if row['required'])}.",
        f"- Copied size: {total_bytes / (1024 * 1024):.2f} MB.",
        "",
        "## Package Contents",
        "",
    ]
    for row in rows:
        status = "OK" if row["copied"] else "MISSING"
        line = f"- {status}: `{row['package_path']}` from `{row['source']}`"
        if row["note"]:
            line += f" ({row['note']})"
        lines.append(line)
    if missing:
        lines.extend(["", "## Missing Assets", ""])
        for row in missing:
            lines.append(f"- `{row['source']}`")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This is a working bundle, not a final journal upload.",
            "- Original analysis outputs remain in their source directories.",
            "- Figures 1-6 form the default main set; Figure 7 is supplementary reference context and GSE163121 remains directional supplementary validation.",
            "- Manuscript v5 is aligned to Genome Medicine, while manuscript v4 remains the target-neutral source draft.",
            "- Reference expansion, declarations, persistent repository links, and final editable-manuscript formatting remain required.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(path: Path) -> None:
    lines = [
        "# Working Submission Package",
        "",
        "This directory is an assembled working copy of manuscript, figure, table, reference, and QC assets.",
        "",
        "## Directory Map",
        "",
        "- `main_text`: manuscript draft, title/abstract options, and figure legends.",
        "- `references`: working BibTeX source.",
        "- `figures_main`: discovery, robustness, and literature-signature figure candidates.",
        "- `figures_validation`: independent-validation and external-reference figure candidates for the upper-Q1 route.",
        "- `figures_supplementary`: supplementary figure candidates.",
        "- `tables_supplementary`: the preferred S1-S12 workbook plus traceable source CSV tables.",
        "- `tables_validation`: independent-validation, readiness, and external-reference tables.",
        "- `submission_docs`: cover-letter pitch, figure triage, availability statements, and submission planning notes.",
        "- `internal_qc`: evidence, citation, and manifest files for author-side checking.",
        "",
        "## Current Submission Logic",
        "",
        "Use manuscript v5 for the Genome Medicine route and manuscript v4 as the target-neutral source draft. The default main set is Figures 1-6; keep the flagged-cluster QC, OneK1K reference context, and small GSE163121 validation as Supplementary Figures S1-S3.",
        "",
        "## Regeneration",
        "",
        "From the project root, run:",
        "",
        "```powershell",
        "python .\\02_analysis\\scripts\\26_prepare_submission_asset_bundle.py",
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_checksums(package_root: Path) -> None:
    checksum_path = package_root / "checksums_sha256.txt"
    lines = []
    for path in sorted(package_root.rglob("*")):
        if not path.is_file() or path == checksum_path:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative = path.relative_to(package_root).as_posix()
        lines.append(f"{digest}  {relative}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy current manuscript assets into a working submission package.")
    parser.add_argument("--project-root", default=".", help="Project root directory.")
    parser.add_argument("--package-dir", default="04_submission/package_working", help="Output package directory.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    package_root = (project_root / args.package_dir).resolve()
    if not package_root.is_relative_to(project_root):
        raise ValueError(f"Package directory must be inside the project root: {package_root}")

    package_root.mkdir(parents=True, exist_ok=True)
    rows = [copy_asset(project_root, package_root, asset) for asset in ASSETS]
    write_manifest_csv(package_root / "bundle_manifest.csv", rows)
    write_manifest_md(package_root / "bundle_manifest.md", rows)
    write_readme(package_root / "README.md")
    write_checksums(package_root)

    missing_required = [row for row in rows if row["required"] and not row["exists"]]
    print(f"Prepared working package: {package_root}")
    print(f"Assets listed: {len(rows)}")
    print(f"Missing required assets: {len(missing_required)}")
    if missing_required:
        for row in missing_required:
            print(f"MISSING: {row['source']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
