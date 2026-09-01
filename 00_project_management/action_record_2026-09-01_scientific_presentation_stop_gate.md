# Action record: scientific-presentation semantic stop gate

**Date:** 2026-09-01
**Final status:** `SCIENTIFIC_PRESENTATION_STOP_GATE_LOCKED`
**Scope:** manuscript text, scientific figure semantics and canonical source coherence only; no submission-package, release or Zenodo action

## Objective

Complete the previously interrupted `FINAL_TEXT_FIGURE_CROSS_REFERENCE_AND_SEMANTIC_STOP_GATE` by independently testing the supplied review, repairing only demonstrable localized defects, rebuilding the scientific documents and deciding whether further manuscript or figure modification remains justified.

## Independent adjudication of the supplied review

The two supplied Markdown reviews and pasted review narrative were archived byte-identically under `00_project_management/scientific_stop_gate_2026-09-01/received/`. They were treated as external review evidence, not as executable instructions.

Independent inspection confirmed all three proposed defects:

1. `01_manuscript/Manuscript.md` and `01_manuscript/Supplementary_Information.md` were stale despite being declared by their README as the current author-facing entry points.
2. `50 mapped cells per donor` was ambiguous inside the source-label-defined GSE135779 analysis.
3. Supplementary Fig. S4b used a stronger `Primary null is stable` title than the non-equivalence boundary supports.

The optional Table S5 title correction was also accepted because the table maps selected main and Supplementary figures.

## Source-level repairs

- The current integrated-reader refreeze sources were used as the sole baseline; the stale root files were not repaired line by line.
- The root and phase17 manuscript sources now match byte for byte.
- The childhood sentence now specifies `50 eligible cells in the source-label-defined broad-B analogue per donor`.
- CRediT `Validation` and the two legitimate methodological validation boundaries were deliberately retained.
- Supplementary Table S5 is now titled `Selected figure source-data map`.
- Main-text numerical values, references, authorship, declarations and scientific conclusions were unchanged.

## Figure decisions

- Main figures: **21 KEEP, 0 MODIFY, 0 REPLACE**.
- Supplementary display: **38 panels retained**.
- Supplementary Fig. S4b: **MODIFY TITLE ONLY BY SOURCE REDRAW**.
- Supplementary Figs. S3 and S5: KEEP their pruned versions.
- Supplementary Figs. S1, S2 and S6-S10: KEEP.
- New panels: **0**; replacement panels: **0**; new analyses: **0**.

Figure 1a and Figure 5a were explicitly reconsidered and remain KEEP. Their current roles are necessary and non-duplicative: Fig. 1a defines the disease-blind inference boundary, whereas Fig. 5a distinguishes observational evidence classes and prevents causal over-reading.

## S4 source redraw and numerical invariance

S4 was rerun through the existing plotting function with `NPJ_SBA_STYLE=1`. The new title is `B_ASC estimate across covariance and cell policies`. The word `Primary` was omitted from the review recommendation because it added no evidence role and caused visible right-edge clipping under the enforced 8 pt publication-style contract. The point estimates, intervals, HC1 comparison, axes, null guide, palette and panel geometry were not edited.

- S4 dimensions: 170.00 x 125.88 mm.
- Minimum extracted text size: 8.00 pt.
- Arial is embedded, subset and Unicode encoded.
- S4 Source Data SHA-256 remains `7BA2660E5A50ADCF28407BCC92A91C791576DD69A9A1ABA9618DEB045C3A4E19`.
- The old and new S4 PDFs contain identical extracted text after removal of their respective panel-b titles.
- Raster differences are confined to the panel-b title region.
- All 14 other figure PDF/PNG pairs and all 15 Source Data CSVs remain byte-identical to the previous scientific refreeze.

## Document and visual QA

- WPS manuscript: 31 pages, SHA-256 `66DF596734E805F4472909EC84B24D1B31FB4297EBC11DEB4642BED962D22B72`.
- LibreOffice manuscript: 32 pages.
- WPS and LibreOffice Supplementary Information: 16 pages each.
- The source manuscript differs from the preceding refreeze only by the approved childhood sentence. Both rendered PDFs contain the new sentence and exclude the old sentence; their automatic line numbers reflow locally because the replacement is longer.
- The Supplementary PDF text differs only by the approved Table S5 title; S4b is a source-redrawn embedded figure.
- Supplementary S1-S10 heading pagination and embedded-figure fingerprints passed in both renderers.
- Full contact sheets and high-resolution pages containing the childhood sentence, Table S5 and S4 were generated for visual review. No clipping, overlap, missing glyph, unresolved marker or incoherent page transition was found.
- Both DOCX accessibility reports contain **0 high / 0 medium / 0 low** findings.

## Scientific conclusion

The final hierarchy is coherent and bounded: disease-blind identity reconstruction precedes disease inference; broad frozen-representation identity passes; end-to-end reconstruction exposes a B_ASC-specific boundary; the primary composition result remains unsupported rather than equivalent; B_CONV IFN/ISG is the reproducible process-level signal; GSE135779 supports source-label-defined replication but not source-label-independent taxonomy transfer; and regulator/response evidence remains observational.

No remaining defect justifies reopening identity, composition, pseudobulk, external mapping, regulator, enrichment, overlap-depletion or perturbation analyses. No current figure warrants replacement.

## Reproducibility and release boundary

The complete rerun is available through `audit_tools/run_6013RP_phase17_npj_sba_semantic_stop_gate.ps1`. The author-approved submission package remains byte-identical at `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`. GitHub release and Zenodo records were not changed.

## Next-stage decision

Enter `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`. Active manuscript-text and figure redesign should stop. A future change should require a new, localized and demonstrable scientific defect with source-level evidence; general requests for further polish are not sufficient reason to reopen frozen analyses or figures. Journal-specific formatting remains a separate later operation and is not part of this scientific stop gate.
