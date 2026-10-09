# O07 Action Record — QiTeng Round 2

**Date:** 2026-09-29
**State transition:** `BASELINE_0_QITENG_TAKEOVER_COMPLETE -> QITENG_R2_GUARDED_REFINEMENT_PASS`

## 1. Inputs

- `SLE_Bcell_Submission_Package.zip`
- `QiTeng_Academic_Writing_Skill_v0.3.24.2_CompressionGovernance_Release_2026-09-20.zip`

The original submission ZIP was preserved. All edits were made in a working copy.

## 2. QiTeng execution mode

Applied the active authority model and Standard Output Contract under:
- `QITENG_Q1_GUARDED`
- `QITENG_FIGURE_Q1_GUARDED`
- `SUBMISSION_GATE_MODE`
- hard-negative late-stage audit

The main decision rule was evidence-first: no claim strengthening without an evidence-tier change, and no compression without a named redundancy plus retained evidence owner.

## 3. Manuscript changes

No section reordering, result deletion, statistical rerun or claim-owner change was performed.

Reader-facing refinements included:
- first-use definitions for unique molecular identifier (UMI), trimmed mean of M values (TMM), univariate linear model (ULM) and the M5911 Hallmark interferon-alpha response set;
- replacement of project-stage wording such as `post-freeze` with transparent timing language;
- `Frozen program inference` -> `Prespecified program inference` and selected program-level `frozen` wording -> `prespecified`, while retaining `frozen` where it describes an intentionally fixed reference/partition;
- calibration closing sentence revised to state that source-label-defined replication remains supported while source-label-independent **transfer** is not established;
- overlap-depletion Methods and multiplicity wording synchronized so the later sensitivity families do not appear to replace the original 24-test family;
- Generative AI paragraph clarified that computations were locally executed against fixed inputs, numerical results were read from analysis outputs, and scientific interpretation/final decisions remained author-led;
- reproducibility/provenance wording changed from project-internal file-history language to current-output provenance;
- Figure 1 legend defines ARI;
- Figure 4/5 legends compressed only where explanation duplicated the Results/Methods, preserving all panel evidence owners and ceilings.

The first expanded render became 32 pages with a two-line orphan on page 32. Under QiTeng compression governance, this was treated as a genuine presentation redundancy problem rather than a target page count. Figure 4/5 legends were tightened without deleting evidence, and the manuscript returned to **31 pages** with unchanged font/layout specifications.

## 4. Cover letter

Rewritten around the manuscript's actual editorial contribution:
- central advance = reproducibility hierarchy, not a new SLE cell taxonomy;
- process-level IFN/ISG replication is paired with end-to-end identity and transfer failures;
- regulatory evidence is explicitly observational and depletion-sensitive;
- journal fit is framed as a general systems-biology question about portability under changing representation, annotation and cohort structure;
- package inventory language was de-emphasized in favor of scientific significance.

## 5. Declarations/reporting/package synchronization

- AI disclosure synchronized across manuscript, cover letter, Authors and Declarations and Reporting Information.
- README policy-check date updated to 29 September 2026.
- human-facing extracted-text companions regenerated from revised DOCX files; 33 reference numbers were reconstructed in the extraction layer without altering Word's native numbering.
- reviewer convenience `Manuscript_With_Figures.pdf` rebuilt from the current manuscript plus unchanged Figures 1-5.
- Source Provenance updated with parent hashes/revision notes for revised human-facing documents.
- `SHA256SUMS.csv` rebuilt.

## 6. Figure decision

No figure data or scientific artwork changed. Figures 1-5 and Supplementary Information are byte-identical to baseline. The 21 main panels remain KEEP.

One low-priority reader-language issue remains for a later source-level micro-gate:
- Figure 2c: internal `Frozen >=50` wording;
- Figure 3a: `Four frozen programs in discovery`;
- Figure 3c: `Frozen IFN-arm genes`.

These should be normalized to reader-facing `Primary` / `Prespecified` only from the generating source, with no manual PDF editing and no data change.

## 7. QA

- Final Manuscript: 31 pages; all pages visually inspected in contact sheets; no clipping, overlap, orphan final page, broken reference layout or legend overflow.
- Cover Letter: 1 page, visually clean.
- Authors and Declarations: 1 page, visually clean.
- DOCX accessibility: manuscript 0/0/0; cover 0/0/0; declarations 0/0/0.
- PDF preflight: all package PDFs open successfully, are not encrypted, are not image-only scans and have no preflight warnings/errors.
- Combined manuscript+figures PDF: 36 pages.
- Package verifier: `PASS: 38 payload files verified`.
- QiTeng DOCX QA: expected strings present and forbidden overclaim strings absent. The tool still reports `reference_count=0` because Word auto-numbered `Reference` paragraphs are not counted by that parser; independent extraction confirms 33 references and first-appearance order remains 1..33.

## 8. Scientific invariants preserved

No change to:
- title or abstract;
- central result values;
- prespecified thresholds;
- multiplicity ownership;
- 21-panel claim ownership;
- figure PDFs/source-data assets;
- supplementary scientific content;
- identity, transfer or mechanistic ceilings.

## 9. Round-2 judgment

`QITENG_R2_GUARDED_REFINEMENT_PASS`

The package is materially stronger at the human-facing definition, evidence-boundary, editorial-framing and cross-file consistency layers. No new analysis is justified. The next high-value step is a narrowly scoped source-level figure terminology micro-gate followed by one final hard-negative cross-document audit.

## 10. Final revised package artifact

- ZIP: `SLE_Bcell_Submission_Package_QiTeng_R2_2026-09-29.zip`
- Bytes: 18983004
- SHA-256: `E5F995ECF98CB45F6597DE937B06A2261BDC0685788702E16B9A17781F5E2760`
- Independent re-extraction verifier: `PASS: 38 payload files verified`
