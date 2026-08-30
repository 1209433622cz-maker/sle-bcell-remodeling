# npj Systems Biology and Applications portal submission runbook

Status: `PREPARED_SUBMISSION_NOT_AUTHORIZED`

## Stop conditions

Do not submit until all of the following exist:

- Explicit Zhi Chen approval for the exact package hash.
- Explicit Teng Qi approval for the exact package hash.
- Separate corresponding-author authorization to submit.
- Official current JCR Q1 receipt satisfying the project target rule.
- Written CUHK-Shenzhen APC/OA determination and, if needed, explicit APC
  commitment authorization.
- Completed official Nature Portfolio Reporting Summary reviewed by both authors.

## Do not upload

- The historical `04_submission/journal_submission/` package.
- Superseded manuscript or cover-letter files.
- Internal audit JSON files, test files, README files or machine gates.
- The retired Nature Portfolio Editorial Policy Checklist PDF.
- The full project ZIP as a single manuscript file.

## Default initial upload set

Use the machine-generated `01_PORTAL_UPLOAD_MANIFEST.csv` in
`phase17_v7/npj_sba_submission_gate/20260830_exact_file_approval_preparation/`.

Default content files are:

1. `Manuscript.docx` as the manuscript file.
2. `Figure_1.pdf` through `Figure_5.pdf` as separate main figures.
3. `Supplementary_Information.pdf` as the single merged supplementary file.
4. Supplementary Data 1-3 as separate supplementary data archives.
5. `Cover_Letter.docx` as the cover letter.
6. The completed official Reporting Summary if accepted by the portal at initial
   submission; otherwise retain it for the requested peer-review or revision stage.

The review PDFs are author-approval references. Upload them only if the portal
requests a PDF alternative or the generated review PDF requires replacement.

## Portal metadata

- Journal: npj Systems Biology and Applications.
- Article type: Article.
- Title: use the exact 15-word title from the approval contract.
- Abstract: use the exact 140-word abstract in `Manuscript.docx`.
- First author: Zhi Chen.
- Corresponding author: Teng Qi.
- Affiliations: use the exact manuscript affiliation and postal address.
- ORCID: link Teng Qi's ORCID in the Springer Nature account before acceptance;
  link both ORCIDs when the portal permits.
- Funding: this study received no funding.
- Competing interests: the authors declare no competing interests.
- Ethics: secondary analysis of public de-identified data; no additional ethics
  approval required; source-study ethics govern original collection.
- Data: GEO GSE174188, GSE135779 and GSE23307; Zenodo 22151739.
- Code: GitHub release v1.1.0 and the cited Zenodo archive.
- Generative AI: reproduce the approved manuscript disclosure exactly where the
  portal requests AI use.
- Related manuscripts: none under consideration, according to the author record.

## Generated-PDF review

Before final submission, inspect every generated page and confirm:

- Correct title, author order, affiliation and corresponding author.
- No dropped Methods, references, legends or declarations.
- Figure order 1-5 and readable panel labels.
- Figure 5 remains legible at portal scaling.
- Supplementary Figure S8 remains legible in the merged supplement.
- R1 and C9R HOLD language is unchanged.
- No legacy title or superseded DOI appears.
- Supplementary Data 1-3 are attached and correctly labeled.
- Reporting Summary answers match the exact manuscript.

## Final receipt freeze

After the corresponding author explicitly authorizes submission and the portal
accepts it, archive:

- Manuscript number.
- Submission timestamp and timezone.
- Portal-generated review PDF.
- Actual uploaded filenames, bytes and SHA-256 hashes.
- Portal metadata export or screenshots.
- JCR receipt and APC/OA determination.
- Author approvals and submission authorization.

No successful upload or portal draft should be described as submission unless a
manuscript number and final submission receipt exist.
