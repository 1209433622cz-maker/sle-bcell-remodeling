# Current submission package: action record

Date: 2026-09-09
Target: npj Systems Biology and Applications, Article
Outcome: Local submission file set built and verified; no submission performed.

## Authorization and scope

The user explicitly requested a complete submission package and supplied first-author information, then requested completion of the interrupted task and an action record. This authorizes local packaging after the previous scientific-presentation maintenance phase. It does not authorize this round to submit, change the scientific conclusions, or replace public archives.

Author order is Zhi Chen followed by Teng Qi. Teng Qi remains corresponding author under the previously confirmed author instructions. First-author email is zhichen1@link.cuhk.edu.cn; ORCID is 0009-0001-0072-5576. Corresponding-author email is tengqi@link.cuhk.edu.cn; ORCID is 0009-0007-7648-4776. The supplied biography was edited for English grammar and placed in author resources, not inserted into the scientific manuscript.

## Sources retained

- Main DOCX/PDF and figures: phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document.
- Supplement DOCX/PDF: phase17_v7/npj_sba_s7_readability/20260909_source_rebuild/documents, including the accepted source-built S7 layout.
- Current figure source data: all 15 CSVs from the accepted figure-source directory.
- Regulator sensitivity and full statistical archives: inherited byte-for-byte from the prior complete data bundle.
- Author contributions and declarations: previously confirmed project records, retained without inventing signatures or new approvals.

No statistical model, value, multiplicity family, figure panel, scientific text or DOI record was edited. Identity, transfer and mechanistic limitations remain intact.

## Deliverables

Directory: 04_submission/20260909_current_submission/SLE_Bcell_Submission_Package

- Manuscript DOCX and PDF, 31 pages.
- Supplementary Information DOCX and PDF, 15 pages, including S1-S10.
- Five separate main figure vector PDFs.
- Three supplementary-data ZIPs; Data 1 was regenerated from current panel source tables rather than reusing the outdated source-data archive.
- Journal-specific cover letter in Markdown, DOCX and PDF.
- Author information, biography, contributions and declarations in Markdown, DOCX and PDF.
- Reporting-information preparation text and supplementary-data descriptions.
- Optional combined manuscript-plus-main-figures review PDF, 36 pages.
- Ten separately exported supplementary figure PDFs in author resources.
- Upload README, source-provenance map, SHA256SUMS.csv and portable Verify_Package.py.

Builder: audit_tools/phase17_npj_sba_64_build_submission_package.py. The prepare stage creates/copies files; DOCX documents are then rendered; --finish verifies and archives them. Rebuilding scientific results is not part of this builder.

## Checks performed this round

1. All entries in Source_Provenance.json were checked against both the source file and package copy by SHA-256.
2. All three data ZIPs passed CRC checks. Root manifests in Data 1 and Data 3 were checked. The inherited Data 2 archive has no root manifest, so its exact source SHA was checked instead; no manifest was silently assumed to exist.
3. All packaged files were compared byte-for-byte with the final ZIP members.
4. Portable verification from outside the project directory passed: 34 payload files, plus the root manifest, total 35 files.
5. Two consecutive finish runs produced the same archive SHA and size.
6. The newly authored cover letter and author-information document were each rendered with WPS and LibreOffice. Each is one page; both renderer outputs were visually inspected without observed clipping or overlap.
7. Main/supplement PDF page counts are 31/15; the optional combined PDF is 36 pages. Main and supplement were reused unchanged rather than needlessly rebuilt.
8. The older locked submission ZIP still hashes to 02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1.

The historical 208-test scientific regression and full dual-renderer page audit were not rerun this round. They remain prior evidence for unchanged files, not a newly claimed test run. No new full-document accessibility certification is claimed.

## Final package identity

ZIP: 04_submission/20260909_current_submission/SLE_Bcell_Submission_Package.zip

Bytes: 19,210,790

SHA-256: 324391ADCA681CC479EC610357D2898B0334E2472D269E3160F55855F555C991

Machine-readable summary: 04_submission/20260909_current_submission/build_status.json

## Limitations and next stage

Official author/editorial-process information was consulted during preparation. The detailed submission-guidelines endpoint redirected to an inaccessible identity service; no assertion is made that every current portal-specific requirement was independently verified. Reporting_Information.md is preparation material, not the journal's official signed reporting-summary or editorial-policy form.

Next stage is author review of the assembled cover letter and upload choices, followed by completion of current journal portal fields/forms when requested. No further scientific analysis or figure redesign is indicated by this packaging work. The package is ready as a local file set, not a completed online submission.

No GitHub push, release, Zenodo update or actual journal submission was performed in this round. The version-specific DOI remains 10.5281/zenodo.22151739 and is not represented as the exact checksum of this new presentation package. Existing unrelated 05_Record files were left untouched.
