# Supplementary Table S7 readability repair

Status: PASS_S7_READABILITY_MICRO_GATE (2026-09-09).

The current supplementary document is `documents/Supplementary_Information_S7_readability.docx` with its WPS PDF. The `lo_final` PDF is the independent LibreOffice rendering. Main manuscript and scientific figures remain those in `phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document`.

The builder `audit_tools/phase17_npj_sba_62_s7_readability.py` reconstructs the supplementary document from frozen Markdown and changes only S7 column widths, horizontal cell padding and S2 pagination formatting. The audit script `audit_tools/phase17_npj_sba_63_audit_s7_readability.py` checks both PDFs against the parent.

Both renderers retain 15 pages, with changes confined to pages 4-6. Text, font sizes and all 45 scientific assets are unchanged. See `audit.json`, `pagination.json`, `a11y.json`, `page_comparison.csv`, and the full action record `00_project_management/action_record_2026-09-09_s7_source_readability_micro_gate.md`.

Regression: 208 tests passed, no skips, failures or errors. This is a local presentation repair; the submission archive, GitHub Release and Zenodo were not updated.
