# Phase 14 Targets - 2026-07-09

## Completed In This Phase

This phase moved the manuscript from integrated upper-Q1 working draft toward submission hardening.

Completed:

- Added `02_analysis/scripts/34_verify_references_crossref.py`.
- Generated Crossref reference audit:
  - `04_submission/reference_verification/reference_verification_crossref_2026-07-09.csv`
  - `04_submission/reference_verification/reference_verification_crossref_2026-07-09.md`
- Generated Crossref-derived BibTeX:
  - `01_manuscript/references_verified_crossref_2026-07-09.bib`
- Added upper-Q1 journal shortlist:
  - `04_submission/journal_shortlist_upper_q1_2026-07-09.md`
- Added manuscript structure QC:
  - `02_analysis/scripts/35_manuscript_structure_qc.py`
  - `04_submission/manuscript_structure_qc/manuscript_v3_structure_qc_2026-07-09.md`
  - `04_submission/manuscript_structure_qc/manuscript_v3_structure_qc_2026-07-09.csv`
- Updated manuscript v3 to point to the Crossref-verified BibTeX.

## Key Findings

Reference audit:

- All DOI records queried successfully through Crossref.
- All citation keys used in manuscript v3 are represented in the BibTeX source.
- The verified BibTeX is ASCII-clean and has no HTML `<sup>` residues.
- Lee2025 is a preprint and is not currently used in manuscript v3; its missing journal field is expected.

Structure audit:

- Manuscript v3 contains approximately 2,599 words excluding the References section.
- Abstract contains approximately 346 words.
- Results contains approximately 981 words.
- Methods contains approximately 569 words.
- The manuscript has seven figure entries.
- Placeholder hits are declaration placeholders rather than missing analysis sections.

Journal strategy:

- Current ambitious first-shot candidates: Annals of the Rheumatic Diseases or Genome Medicine.
- Best fit/feasibility backup: Journal of Autoimmunity.
- Risk-controlled alternatives: Communications Biology or npj Autoimmunity after current metrics/indexing verification.

## Recommended Next Stage

Choose the first-shot target journal, then create a target-specific manuscript version:

1. Verify current JCR/CAS category, APC, article type, figure policy, and word limits through institutional access or official author instructions.
2. If targeting Annals of the Rheumatic Diseases, compress toward a clinically framed rheumatology manuscript and move Figure 7 to supplementary material unless allowed.
3. If targeting Genome Medicine, preserve the seven-figure structure and strengthen reproducibility/data-code language.
4. Build final supplementary tables S1-S12 into a clean submission-ready package.
5. Replace author contribution, conflict-of-interest, and funding placeholders.

## Recommendation

Do not add more datasets now. The manuscript is analytically strong enough for target-specific shaping. The next bottleneck is journal selection and formatting.

