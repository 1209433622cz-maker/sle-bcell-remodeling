# Action record: integrated reader-path and S3/S5 scientific refreeze

**Date:** 2026-09-01  
**Final status:** `INTEGRATED_READER_PATH_AND_DISPLAY_PRUNE_SCIENTIFIC_REFREEZE_LOCKED`  
**Scope:** manuscript text and scientific figure presentation only; no submission-package, GitHub release or Zenodo action

## Objective

Continue the scientific-presentation phase by testing every main and Supplementary panel for unique claim ownership, removing only frozen numerical duplicates, redrawing the affected Supplementary figures from immutable Source Data, and verifying that the revised manuscript remains coherent in WPS and LibreOffice. The biological analyses, statistical models and release objects were deliberately kept closed.

## Inputs and independent review

The six supplied reader-prune files were imported verbatim under `00_project_management/integrated_reader_prune_2026-09-01/received/` and treated as review candidates rather than executable truth. The 62-row panel matrix was independently checked against the frozen figure objects and Source Data.

Three proposed removals were confirmed as exact duplicates:

- old Supplementary Fig. S3a equals Fig. 1b across 16 compared policy-level values;
- old Supplementary Fig. S3d equals Fig. 1d across 8 compared broad-state values;
- old Supplementary Fig. S5d equals Fig. 3b across 7 rows and 5 numerical/identifier fields.

The supplied redraw code was not used unchanged. Its S3 guide was set to 0.95 although the frozen fine-state diagnostic threshold is 0.60, and its smallest labels were 5.5 pt. The production rerun corrected the guide to 0.60, enforced Arial and a minimum visible size of 6 pt, restored the project palette, moved the S3 legend outside the data region, and repaired S3 colorbar and S5 panel-label margins.

## Final panel decisions

- Main figures: **21 KEEP, 0 MODIFY, 0 REPLACE**.
- Supplementary panels: **38 retained or renumbered, 3 exact duplicates pruned, 0 REPLACE**.
- S3: old a and d removed; old b becomes new a; old c becomes new b.
- S5: a-c retained; d removed because Fig. 3b is the numerical owner.
- New panels, new estimates and new claims: **0**.

This is a display prune, not deletion of scientific provenance. The original Source Data remain in the reproducibility archive and the mapping is recorded in `S3_S5_DISPLAY_PANEL_MAPPING.csv`.

## Text integration

Only two main-text sentences changed. The Introduction now names `reconstruction and replication tests`, avoiding a generic validation label. The final Discussion boundary now closes on a single positive claim: `a bounded process-level interferon association within explicit identity and transfer limits`.

Only the S3 and S5 legends changed in the Supplementary Information. S3 now owns fine-state failure localization and transition structure, while pointing broad-state pass evidence to Fig. 1 and end-to-end propagation to Supplementary Fig. S9. S5 now owns pseudobulk and ranked-list diagnostics and explicitly points frozen IFN/ISG estimates to Fig. 3b.

## Figure source-redraw QA

- S3: 170.00 x 86.00 mm; minimum extracted text 6.00 pt; embedded/subset Unicode Arial; SHA-256 `ECB80FF10A95FFEE71F86A5D940EADA465D523143AA5EE9216BB41CA1C885934`.
- S5: 170.00 x 104.00 mm; minimum extracted text 6.00 pt; embedded/subset Unicode Arial; SHA-256 `AA2A6F9D0BCD49B4B26D311C479AA74E39BCCC5D7830447DB3026ACF79C5F0CF`.
- All four governing Source Data objects remained byte-identical to their frozen SHA-256 values.
- S3 and S5 were regenerated from Source Data; no PDF or PNG was edited by hand.

## Document and visual QA

- WPS manuscript: 31 pages, SHA-256 `49F9571664412B5B3B2FA19BDAC05E471DC9287E79DCCC45AC14711B499DBBC9`.
- LibreOffice manuscript: 32 pages; the expected one-page difference is only the final two legend lines on page 32.
- WPS and LibreOffice Supplementary Information: 16 pages each.
- All ten Supplementary headings and their figures occupy the same pages in both renderers; all ten embedded figure fingerprints match the intended sources.
- All 18 contact sheets and 10 high-resolution affected-page renders were visually reviewed. No clipping, overlap, missing glyph, unresolved marker or incoherent cross-reference was found.
- Both DOCX accessibility reports contain **0 high / 0 medium / 0 low** findings.

## Scientific conclusion

The pruning improves the evidence hierarchy without weakening it. Fig. 1 remains the owner of broad identity stability, Supplementary Fig. S3 explains why fine-state identity failed, Fig. 3b owns the frozen branch-wise IFN/ISG effects, and Supplementary Fig. S5 now remains a pure model-diagnostic figure. The negative reconstruction and transfer boundaries continue to constrain the positive process-level interferon result.

No current defect justifies replacing Fig. 1a, Fig. 5a, any other main panel, or reopening the identity, composition, pseudobulk, replication or regulator models.

## Reproducibility and unchanged release boundary

The complete rerun is available through `audit_tools/run_6013RP_phase17_npj_sba_integrated_reader_refreeze.ps1`. The author-approved submission package remains byte-identical at `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1` and was not rebuilt. GitHub release and Zenodo records were not changed.

## Next-stage decision

Proceed to `FINAL_TEXT_FIGURE_CROSS_REFERENCE_AND_SEMANTIC_STOP_GATE`. This should be a narrow, final scientific reader pass that checks every panel-letter reference, every numerical claim owner and every Results-to-legend transition against the final 21 main and 38 Supplementary panels at actual size. Only a localized, demonstrable defect should trigger another source redraw or sentence edit. If that gate finds no defect, scientific presentation should stop; it must not add cohorts, mappers, sensitivity analyses, replacement panels or submission engineering.
