# O01 Project Audit: QiTeng reader-language and hard-negative gate

Date: 2026-09-29
Target journal: npj Systems Biology and Applications
Decision: **PASS — QITENG_SCIENTIFIC_SUBMISSION_CANDIDATE_FREEZE**

## Scope and authority

This round used the QiTeng Academic Writing Skill v0.3.24.2 registry as the sole active authority. The Round 2 package was treated as the scientific-text parent. The authorized task was a guarded improvement of reader language and package coherence, not a new statistical analysis, result search or portal submission.

## Source-level changes

- Figure 2c: `Frozen >=50` became `Primary >=50`.
- Figure 3a: `Four frozen programs in discovery` became `Four prespecified programs in discovery`.
- Figure 3c: `Frozen IFN-arm genes` became `Prespecified IFN-arm genes`.
- Supplementary Table S4b/S7 and the S10 legend were synchronized to `prespecified` / `additional sensitivity` wording.
- Supplementary Figure S10 was source-redrawn so its panel title and target-retention axis use reader-facing `prespecified` terminology.

Figure 2 and Figure 3 source-data CSVs are byte-identical to Supplementary Data 1. The 36-row S10 depletion source table is byte-identical to the frozen archive. No estimate, confidence interval, P value, q value, sample count, target count, multiplicity family, panel ownership or scientific conclusion changed.

## Scientific hard-negative audit

The package still explicitly owns all required boundaries: B_ASC end-to-end overlap failure; lack of statistical support for the primary B_ASC composition contrast; weak genome-wide correlation despite IFN-program replication; corrected B_ASC mapping-calibration failure with no corrected external effect; the discovery-STAT2 CAMERA/depletion exception; observational rather than causal regulatory interpretation; and descriptive n=2 perturbation context.

## Document and figure QA

- Manuscript: 31 pages, 31/31 visually inspected.
- Supplementary Information: 15 pages in WPS and 15 pages in LibreOffice; S7 and S10 targeted pages independently inspected in both engines.
- DOCX accessibility: manuscript 0/0/0; Supplementary 0/0/0.
- QiTeng deterministic structure checks: no comments, tracked insertions or tracked deletions; no forbidden reader-language labels; all expected terminology present.
- QiTeng reference parser reported zero references because the DOCX uses Word automatic numbering. Independent style-aware extraction verified 33 continuous references, 33 unique cited numbers, first appearance 1–33, no missing references and no orphan references.
- PDFs: 20 files, 99 aggregate pages, all readable and unencrypted.
- Full regression: 215/215 PASS.

## Package integrity

The final package contains 38 manifested payload files. Portable verification passes both in place and after independent ZIP extraction. The archive contains 39 members including the root manifest, and ZIP CRC testing reports no damaged member.

ZIP SHA-256: `EBC9017D24FEACC5628DF978C09FF6D9CD33ABF41BBB7F2CE259A5EC80796709`
ZIP bytes: `18958008`

## Final judgment

The current object is a scientifically bounded, internally consistent submission candidate. No further proactive analysis or language compression is justified without a concrete numerical error, provenance issue, actual-size defect, new data or author/reviewer scientific question.
