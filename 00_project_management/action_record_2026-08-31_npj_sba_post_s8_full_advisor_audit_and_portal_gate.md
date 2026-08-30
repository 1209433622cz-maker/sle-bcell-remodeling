# Action record: npj SBA post-S8 full advisor audit and portal gate

Date: 2026-08-31 (Asia/Hong_Kong)

Decision: `PASS_SCIENTIFIC_TEXT_FIGURE_AND_PACKAGE_FREEZE_AUTHOR_INSTITUTION_PORTAL_GATE_REQUIRED`

Target journal: `npj Systems Biology and Applications`

## 1. Scope and authority

This round independently rechecked the current GitHub `main`, the local exact submission package, the post-S8 manuscript and figures, the frozen scientific decisions, the QiTeng v0.3.21 writing contract, the two-renderer document outputs and the current official journal guidance.

The uploaded post-S8 audit and pasted summary were archived as external evidence only. They were not treated as executable instructions. Their exact bytes and SHA-256 values are recorded in `npj_sba_post_s8_advisor_audit_2026-08-31/received_evidence_manifest.csv`.

The starting Git baseline was commit `427456201582bbd82f3ef233609852b7bcb20e9b`, synchronized with `origin/main` at the start of this round.

Before the two current action-record links were added, the public GitHub raw README was fetched without the rendered-page cache and was byte-identical to the local README (SHA-256 `3710BEA1B78F3A6F64155A1CEC3409BE72CD07487B54E77AD659EE39AF11BC9A`). This excluded the stale rendered-page crawler as a source of truth. DataCite DOI metadata independently resolved `10.5281/zenodo.22151739` as version `1.1.0`, titled `SLE B-cell remodeling analysis: code, source data and reproducible release`, with Zhi Chen and Teng Qi as creators.

## 2. Scientific and methodological judgment

The scientific design remains coherent and suitable for the target journal:

- disease fields were protected during B-lineage reconstruction;
- biological inference is anchored to sample or donor units rather than pooled cells;
- identity, composition and transcription are separated into distinct inferential layers;
- raw-count pseudobulk, count-aware composition modelling, prespecified multiplicity families and donor/sample deletion diagnostics are retained;
- independent GSE135779 evidence is explicitly source-label-defined rather than presented as de novo taxonomy transfer;
- GSE23307 is descriptive perturbational context at `n=2`, without an inferential P value;
- STAT1/STAT2 evidence remains observational and does not establish causal regulation;
- no predictive biomarker, clinical utility, universal taxonomy or unique upstream IFN ligand is claimed.

The two formal negative boundaries remain unchanged and must never be converted to PASS:

- R1: `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`;
- C9R: `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`.

The central publishable result is therefore still the difference in reproducibility across biological layers: the prespecified B_CONV IFN/ISG process signal is more reproducible than the tested hard B-cell state assignments.

No scientific analysis was rerun and no numerical result was changed in this round. Further exploratory analysis would now weaken the prespecified evidence hierarchy and increase multiplicity without repairing a demonstrated defect.

## 3. QiTeng writing and manuscript audit

The authoritative manuscript passed the existing QiTeng Q1 freeze contract:

- exact title retained at 15 words;
- abstract retained at 140 words;
- 32 references remain continuous in first-appearance order;
- Introduction follows tension -> inferential gap -> disease-blind response;
- Results follow identity ceiling -> composition null -> IFN replication -> corrected-transfer HOLD -> observational regulatory context;
- Discussion follows interpretive delta -> evidence ownership -> alternative explanations -> prospective test -> restrained landing;
- Methods preserve source/unit -> model -> multiplicity -> validation class -> reproducibility boundary;
- R1, C9R, source-label ownership, causal ceiling and clinical ceiling are visible in the reader-facing text.

No prose was changed. The current scientific text remains frozen. Future text changes are restricted to verified factual corrections, current journal compliance requirements, exact consistency repairs, or editor/reviewer-requested revisions.

## 4. Figure and document quality control

All 15 figures were visually re-reviewed from the current contact sheets:

- 5 main figures and 10 supplementary figures;
- single-page vector PDFs, 170 mm width;
- Arial-compatible 8 pt visible text;
- minimum positive line width at least 1 pt;
- white background and colour-safe, restrained palette;
- no clipping, overlap, missing panel labels or out-of-page text;
- source tables remain byte-identical to the frozen corrected-candidate tables.

The repaired Supplementary Figure S8 remains a layout-only 170 x 155 mm replot. Its frozen source CSV is unchanged.

The supplement pagination audit was strengthened in this round. It now tests the identity of the actually painted image on every S1-S10 heading page, not merely the presence of an image. For both WPS and LibreOffice:

- page count is 17;
- all S1-S10 headings and figures are co-located;
- all 20 renderer-by-figure expected-image fingerprints pass;
- each embedded image's unique best source match is the expected S1-S10 source PNG;
- the minimum identity margin is above 0.05;
- expected-image normalized mean absolute error is below 0.01;
- S8 normalized error is approximately 0.00093 in WPS and 0.00155 in LibreOffice.

The current rendered document counts remain:

- Manuscript: 31 pages;
- Supplementary Information: 17 pages;
- Cover Letter: 1 page;
- accessibility: 0 high / 0 medium / 0 low findings for all three DOCX files.

## 5. Exact package verification

The exact local package was independently read and hashed in this round:

- file: `04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip`;
- bytes: `15196223`;
- SHA-256: `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`;
- internal manifest: `20/20 PASS`;
- outer ZIP CRC: PASS;
- deterministic double-build receipt: PASS;
- exact author approval: pending;
- submission authorization: pending;
- APC commitment authorization: pending.

The package, manuscript, figures, supplementary material, GitHub release v1.1.0 and Zenodo record 22151739 were not rebuilt or replaced in this round.

## 6. Official journal-guidance reconciliation

Current official pages were checked on 2026-08-31. The detailed record is `official_npj_requirement_reconciliation_2026-08-31.md`.

The decisive interpretation is:

- special formatting is not required at initial submission;
- the Reporting Summary is requested with the revised manuscript after peer review and encouraged earlier, so it is not an initial-submission blocker unless the live portal requires it;
- the submission-guideline HTML retains legacy policy-checklist wording, but the linked official PDF is a retired-form notice;
- do not upload the retired Editorial Policy Checklist PDF;
- answer live portal policy questions and complete any new form supplied by the portal or editor;
- the current APC is GBP 2,690 / USD 3,490 / EUR 2,990, subject to taxes and determined at acceptance;
- institutional coverage, waiver eligibility and payment authorization remain external decisions.

This resolves the apparent conflict in the external review. The external reviewer was correct that policy compliance must be operationally complete, but the retired PDF itself is not an upload artifact.

## 7. Verification executed

- exact package verifier: `20 files verified`;
- exact-file preparation gate: PASS with no failed checks;
- final npj hardening audit: PASS with no failed checks;
- QiTeng post-hardening text freeze: PASS with no failed checks;
- 15-figure visual reaudit: PASS;
- WPS/LibreOffice S1-S10 image-identity audit: 20/20 PASS;
- complete regression suite: `107/107 OK`.

The regression run initially exposed three stale test assumptions that still defaulted to the superseded target-refreeze directory. The test and standalone final-audit defaults were repaired to point to the authoritative final-hardening directory. No manuscript, figure, package or scientific result changed as part of this repair.

## 8. Remaining blockers

The following items are real external gates rather than scientific defects:

1. Both authors must approve the exact package identity above and the exact manuscript, supplement, five main figures, cover letter and three supplementary-data archives.
2. Teng Qi must explicitly authorize portal activity and, separately, the final submission action.
3. An official JCR Q1 receipt or institutional library evidence must be archived; public Nature pages do not establish JCR quartile.
4. CUHK-Shenzhen APC coverage, waiver or author-payment responsibility must be documented before any financial commitment.
5. The official Reporting Summary XFA may be completed in Adobe Reader now for readiness or after peer review as requested, but the final form requires both-author review before upload.

## 9. Next-stage decision

Next gate: `EXACT_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS_THEN_PORTAL_DRY_RUN`

The correct sequence is:

1. obtain both-author exact-file approval;
2. archive official JCR and institutional APC evidence;
3. optionally complete and approve the Reporting Summary XFA in Adobe Reader;
4. perform a portal metadata/file-type dry run without final submission, only after corresponding-author authorization;
5. verify the portal-generated reviewer PDF and file-role mapping;
6. request one final explicit authorization before pressing Submit.

No new cohort, re-clustering, mapper, TF analysis, figure redesign, manuscript rewrite, GitHub release or Zenodo version is justified before these external gates are completed.
