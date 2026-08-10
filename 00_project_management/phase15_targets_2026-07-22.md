# Phase 15 Targets - 2026-07-22

## Completed In This Phase

This phase focused on manuscript refinement and Nature-style quality control rather than adding new datasets.

Completed:

- Created the preferred refined manuscript:
  - `01_manuscript/manuscript_v4_nature_style_refined.md`
- Reworked manuscript logic from a full seven-figure upper-Q1 draft into a tighter Nature-style structure.
- Generated manuscript structure QC for v3 and v4:
  - `04_submission/manuscript_structure_qc/manuscript_v3_upper_q1_working_structure_qc_2026-07-22.md`
  - `04_submission/manuscript_structure_qc/manuscript_v4_nature_style_refined_structure_qc_2026-07-22.md`
- Added objective figure quality QC:
  - `02_analysis/scripts/36_figure_nature_style_qc.py`
  - `04_submission/figure_quality_qc/figure_quality_qc_2026-07-22.md`
  - `04_submission/figure_quality_qc/figure_contact_sheet_2026-07-22.png`
- Regenerated Figure 6 from the GSE135779 validation script.
- Regenerated Figure 7 from the OneK1K reference-context script.
- Added PDF/vector-style exports for Figure 6 and Figure 7.
- Added advisor-level full project audit:
  - `04_submission/advisor_full_project_audit_2026-07-22.md`
- Added Nature-style figure triage:
  - `04_submission/figure_triage_nature_style_2026-07-22.md`

## Key QC Findings

Manuscript:

- v4 is now the preferred writing base.
- v4 total words excluding References: 2,327.
- v4 abstract words: 287.
- v4 Results words: 807.
- v4 Discussion words: 360.
- v4 Methods words: 430.
- Placeholder hits are limited to author contribution and competing-interest declarations.

Figures:

- Figures 1-7 and Supplementary Figure S1 now pass basic technical QC.
- Figure 6 and Figure 7 now have PNG and PDF outputs.
- Figure 6 should remain a main figure because it closes the independent validation loop.
- Figure 7 is scientifically useful but can move to Extended Data/Supplementary material for strict rheumatology targets.

## Current Advisor Recommendation

Do not add a new dataset now. The analysis is strong enough for SCI Q1 target-specific shaping.

Use:

- `manuscript_v4_nature_style_refined.md` as the primary writing base.
- `manuscript_v3_upper_q1_working.md` as the fuller comparison draft.
- Figures 1-6 as the default main figure set.
- Figure 7 as optional main, Extended Data, or supplementary material depending on journal policy.

## Recommended Next Stage

Build a target-specific submission version:

1. Select one primary target journal.
2. Verify current JCR/CAS quartile, APC, word limit, figure limit, file formats, and supplementary policy.
3. Create the target-specific manuscript from v4.
4. Assemble Supplementary Tables S1-S12 as one clean workbook.
5. Replace author contribution, funding, competing interest, acknowledgements, and ORCID placeholders.
6. Final-audit every numeric claim after target-specific edits.

