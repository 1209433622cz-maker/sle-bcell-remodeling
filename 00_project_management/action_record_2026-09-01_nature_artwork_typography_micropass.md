# Action record: Nature/npj artwork typography micropass

- **Date:** 2026-09-01
- **Final status:** `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`
- **Scope:** scientific manuscript text and source-driven artwork only; no submission-package, release or Zenodo action

## Objective

Independently test the external hostile audit against the current `cb762af` scientific stop-gate object, repair only reproducible artwork defects, retain all frozen numerical objects and decide whether any panel requires modification, replacement or further analysis.

## Independent audit result

The supplied audit and pasted review were archived byte-identically under `00_project_management/nature_artwork_micropass_2026-09-01/received/` and treated as review evidence rather than executable instructions.

The artwork criticism was reproducible. `audit_tools/publication_style_contract.py` had forced every visible text object to 8 pt and every non-zero line or patch width to at least 1 pt. Object-level inspection of all 15 final PDFs showed that Figure 1-5 and Supplementary Figures S1, S2, S4 and S7-S10 were flattened to a single 8 pt text size. Supplementary Figures S3, S5 and S6 already retained deliberate 6/7/8 pt role hierarchies and were not candidates for rerun.

## Style-contract repair

The shared final-size pass now preserves the role sizes declared by each figure builder. It enforces Arial, raises only annotations below 5.5 pt to the readability floor, keeps bold panel letters at 8 pt and raises only sub-printable non-zero rules to 0.5 pt. It no longer promotes ordinary 0.5-0.8 pt rules or all text to a uniform value. A regression test locks the title, axis-label, tick, legend, annotation, panel-letter and line-width hierarchy.

## Source-driven redraw and invariance

- **12 figures redrawn:** Figure 1-5; Supplementary Figures S1, S2, S4, S7, S8, S9 and S10.
- **3 figures retained byte-identically:** Supplementary Figures S3, S5 and S6.
- All redraws used the established generators with `NPJ_SBA_STYLE=1`; no PDF or PNG was hand-edited.
- All 15 Source Data CSV files are byte-identical to the prior scientific stop gate.
- Statistical models, thresholds, point estimates, intervals, q values, panel geometry, panel membership and colour semantics were unchanged.
- Every redrawn PDF now contains at least three visible font-size levels, a 5.5 pt or larger minimum, an 8 pt maximum, Arial-only text and ordinary sub-1 pt rules.

## Panel decisions

- Main panels: **21 KEEP**, **21 typography-only source redraw**, **0 replace**.
- Supplementary panels: **38 KEEP**; **29 typography-only source redraw**, **9 keep exact**, **0 replace**.
- Figure 1a and Figure 5a remain KEEP. Their scientific roles are still necessary: Fig. 1a defines the identity-to-disease inference boundary; Fig. 5a defines evidence classes and the causal ceiling.
- Supplementary Figure S7 remains KEEP because the figure owns correlation-pattern recognition while the table owns exact numeric retrieval.
- No new panel, cohort, mapper, regulator analysis or sensitivity analysis was added.

## Targeted manuscript terminology

Two local evidence-boundary sentences were changed from `independent validation` to `independent replication`: the accession-internal Results boundary and the same-data uncertainty-propagation Methods boundary. Legitimate methodological validation, prospective clinical validation and the CRediT `Validation` role were preserved. The Supplementary text is byte-identical to the previous stop gate.

## Document and visual QA

- WPS manuscript: 31 pages, SHA-256 `85D701807F00AEB294ECCFC9CA98C46C9A3762A9BD4B7C276FDC7B88E26FA14D`.
- LibreOffice manuscript: 32 pages.
- WPS and LibreOffice Supplementary Information: 16 pages each.
- All pages remained within canvas; all embedded-figure markers resolved; Supplementary S1-S10 pagination and fingerprints passed in both renderers.
- Full document contact sheets and eight artwork contact sheets were generated for visual inspection. No clipping, overlap, missing glyph or incoherent panel hierarchy was found.
- Both DOCX accessibility audits contain 0 high / 0 medium / 0 low findings.

## Release boundary

The author-approved submission ZIP remains byte-identical at `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`. GitHub release and Zenodo were not changed. This round changes the scientific working candidate and reproducible generator, not the frozen submission package.

## Next-stage decision

Return to `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`. The demonstrable artwork defect has been repaired without reopening scientific inference. No existing panel currently warrants replacement, and further work should require a localized evidence, legibility or semantic defect rather than a general request for more polish. Journal-specific packaging remains a later and separate activity.
