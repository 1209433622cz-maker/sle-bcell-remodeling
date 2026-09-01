# Action record: Supplementary Table S4 reader-path micropass

- **Date:** 2026-09-01
- **Final status:** `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`
- **Scope:** Supplementary reader structure only; no figure, model, Source Data, manuscript-result, submission-package, Release or Zenodo change

## Objective

Independently adjudicate the post-typography audit, repair the isolated reader-facing `S4B` numbering defect and determine whether any manuscript or figure object should be reopened.

## Independent adjudication

The defect was reproduced. The Supplementary overview declared Tables S1-S9, while the visible sequence was S1, S2, S3, S4, S4B, S5, S6, S7, S8 and S9. The scientific values were valid, but an unpaired `S4B` made the reader-facing inventory appear inconsistent.

No figure replacement or redraw was justified. Figure 1a remains the unique owner of the identity-to-disease inference boundary, and Figure 5a remains the unique owner of the evidence-class and causal-ceiling contract. All 21 main panels and 38 Supplementary panels remain KEEP; S3, S5 and S6 retain their exact role-aware artwork.

## Localized source repair

- The parent heading is now `Supplementary Table S4 | Regulator-sensitivity summaries`.
- The correlation-aware grid is labelled `a, Correlation-aware core-regulator sensitivity`.
- The overlap-depletion grid is labelled `b, IFN-overlap-depletion summary`.
- Downstream Tables S5-S9 retain their identifiers.
- Table S5 now describes Figure 2 as `Sample-level composition in the 43-control/47-managed-SLE primary comparison` instead of using the implementation term `asserted`.
- No table cell, number, statistic, threshold, inference or figure legend changed.

## Invariance controls

- The root manuscript and frozen manuscript source are byte-identical to the typography freeze.
- Every figure PDF and PNG is byte-identical to the typography freeze; no figure generator ran.
- All 15 Source Data CSV files are byte-identical.
- The prior panel-decision matrix is byte-identical: 0 new panels and 0 replacement panels.
- The author-approved submission ZIP remains `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`; Release and Zenodo were not changed.

## Document and visual QA

- WPS Supplementary Information: 16 pages, SHA-256 `A1F7CB6FD39AFAB3155D72BFF543893C37E7146127993B643D1B5A3030C167A5`.
- LibreOffice Supplementary Information: 16 pages, SHA-256 `5318AEE26920B55DCF198CB751858C606914A9151E1F901A4ED1DF7496DC0C54`.
- Both renderers show numbered Tables S1-S9 exactly once, the S4 a/b labels, Figures S1-S10 on their heading pages and no `Supplementary Table S4B`.
- All pages remain within canvas; no clipping, overlap, unresolved marker or missing figure fingerprint was detected.
- Six renderer contact sheets covering all 32 rendered pages were manually inspected; the S4 a/b hierarchy remained clear at page scale and no blank page, clipping, overlap or missing glyph was observed.
- DOCX accessibility audit: 0 high / 0 medium / 0 low findings.

## Next-stage decision

Return to `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`. The last demonstrated reader-path inconsistency is repaired. No broad manuscript rewrite, figure redesign or additional analysis is currently justified. Reopen only for a new localized numerical, semantic, cross-reference or actual-size legibility defect.
