# npj SBA exact-file approval and official-forms preparation

Date: 2026-08-30 (Asia/Hong_Kong)

Repository starting commit:
`d2e36a4a852711b7fd6895ce4586dd6fea474806`

Final technical status:
`PASS_TECHNICAL_PREPARATION_AUTHOR_AND_INSTITUTION_RECEIPTS_REQUIRED`

Next gate:
`EXPLICIT_EXACT_FILE_AUTHOR_APPROVAL_AND_EXTERNAL_RECEIPT_INGESTION`

## 1. Objective

This round continued the post-hardening npj Systems Biology and Applications
submission workflow. Its purpose was to complete every remaining task that could
be performed from verified local evidence without impersonating an author,
institution, Clarivate or Springer Nature approval process.

The work covered:

- Exact-file author-approval preparation.
- Current official Nature Portfolio form retrieval and verification.
- Reporting Summary field-level response preparation.
- Current Editorial Policy Checklist status determination.
- Institutional JCR and APC/OA evidence-request preparation.
- Exact portal upload inventory and runbook preparation.
- A read-only machine gate and regression tests.

No scientific analysis, manuscript, figure, target-formatted document, public
release or Zenodo record was changed.

## 2. Authoritative inputs

The following files remained the scientific and target-format authority:

- Final-hardened manuscript, supplement, figures and cover letter under
  `phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening/`.
- Target package under
  `04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications/`.
- Frozen package ZIP with SHA-256
  `F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`.
- Post-hardening text-freeze gate
  `PASS_NPJ_SBA_POST_HARDENING_REAUDIT_TEXT_FREEZE`.
- GitHub release v1.1.0 and Zenodo DOI 10.5281/zenodo.22151739.

## 3. Current official journal-rule findings

Official sources were checked on 2026-08-30.

### 3.1 Initial-submission format

npj Systems Biology and Applications does not require special formatting at
initial submission and accepts Word or PDF material suitable for editorial and
peer review. Separate high-resolution figure files are acceptable when a
combined manuscript is not used.

The current target package therefore does not require scientific or document
rebuilding merely to meet the initial-submission format rule.

### 3.2 Nature Portfolio Reporting Summary

The journal's submission guidelines state that the Reporting Summary is required
with a revised manuscript after peer review and encourage authors to include it
at initial submission. The current official form is an XFA dynamic PDF that must
be completed in Adobe Reader. A flat seven-page reference copy is also provided
for guidance but is not the submitted form.

The project now contains both unmodified official copies and a field-by-field
technical response map. The form itself remains incomplete because final entry
and review are author actions.

### 3.3 Editorial Policy Checklist

The current official URL for the Nature Portfolio Editorial Policy Checklist
returns a one-page PDF stating:

`This form is no longer required for Nature Portfolio submissions and has been removed.`

This supersedes the prior project assumption that a completed standalone
checklist PDF was a mandatory upload. The result is handled conservatively:

- The official retirement notice is archived unchanged.
- The historical project Markdown checklist is retained as an internal policy
  audit only.
- The retired PDF is excluded from the portal upload manifest.
- Current portal policy questions remain binding if presented during submission.

### 3.4 Statistics, code and data

The current journal guidelines require transparent sample sizes, biological
units, tests, sidedness, covariates, uncertainty, exact P values where suitable,
multiplicity handling and code/data availability. The final-hardened manuscript
and `npj_statistics_reporting_map.csv` already cover these requirements.

Nature Portfolio requires central custom code to be available to editors and
reviewers and encourages DOI-minting archival release. The existing GitHub and
Zenodo release satisfies the repository and DOI architecture without requiring a
new release.

### 3.5 Generative AI

The journal guidelines state that an LLM does not qualify for authorship and
that LLM use should be documented in Methods or another appropriate section.
The exact manuscript contains a dedicated `Generative AI assistance` subsection,
identifies OpenAI Codex uses, assigns all responsibility to the authors and lists
no AI system as an author. No wording change was required.

## 4. Official forms frozen

Unmodified official files were downloaded from Nature Portfolio and stored under
`00_project_management/npj_sba_exact_file_approval_2026-08-30/official_forms/`.

| Official file | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `Nature_Portfolio_Reporting_Summary_dynamic.pdf` | 1,633,663 | `6B529F32B850373216528FFEB55283A28711186C06FB1F65F4CC8447AC236E03` | Current XFA form; Adobe completion required |
| `Nature_Portfolio_Reporting_Summary_flat_reference.pdf` | 437,072 | `5AB917D5DD2AD4C2F6ED5067D43119E3235095CDE9A46488B2972E5C89A19FD6` | Seven-page reference copy |
| `Nature_Portfolio_Editorial_Policy_Checklist_dynamic.pdf` | 57,111 | `77852E16C76936DC9BB946B1D7819B0DB30F53E396AA6ED5DBBE559EE3691FE1` | Official retirement notice; do not upload |

The dynamic Reporting Summary was programmatically confirmed to contain an XFA
form. The flat copy was confirmed as seven pages. The checklist retirement
notice was text-extracted and visually reviewed.

## 5. Exact-file author approval contract

`Exact_File_Author_Approval.md` now binds approval to the exact package SHA-256
and identifies:

- Manuscript DOCX and review PDF.
- Five main figure PDFs.
- One merged Supplementary Information PDF.
- Three Supplementary Data archives.
- Author/declaration record.
- Cover-letter DOCX and review PDF.
- R1 and C9R permanent HOLD boundaries.
- Source-label ownership of external replication.
- Observational ceiling of regulator analyses.
- Ethics, competing interests, funding and generative-AI declarations.
- Originality and one-journal-at-a-time policy.
- GitHub and Zenodo release identity.

Four independent markers remain pending:

- `ZHI_CHEN_APPROVAL: PENDING`
- `TENG_QI_APPROVAL: PENDING`
- `PORTAL_SUBMISSION_AUTHORIZATION: PENDING`
- `APC_COMMITMENT_AUTHORIZATION: PENDING`

Manuscript approval must not be interpreted as portal or APC authorization.

## 6. Reporting Summary response map

The prepared response map covers:

- Exact sample sizes and biological units.
- Repeated-measure and pseudoreplication handling.
- Statistical tests, sidedness, covariates, uncertainty and multiplicity.
- Absence of Bayesian analysis.
- Hierarchical donor/sample-level inference.
- Software, code and DOI-backed availability.
- GEO accessions and project-generated Supplementary Data.
- Human-data status, sex/gender and race/ethnicity limitations.
- Source-study recruitment, consent and ethics.
- Sample-size rationale and prespecified exclusions.
- Internal, end-to-end and independent replication classes.
- Disease-label protection during identity reconstruction.
- Non-applicable materials and specialized-method sections.

The map explicitly prevents the following errors:

- Calling GSE23307 an inferential replication.
- Claiming sex, gender, race or ethnicity balance or subgroup analysis.
- Calling R1 or C9R a PASS.
- Calling GSE135779 source-label-independent.
- Entering `n/a` where the official form expects an explanatory sentence.

## 7. JCR and APC/OA evidence

No public source accessible in this round supplied a date-stamped Clarivate JCR
record with category, rank, denominator and quartile. The official JCR Q1 receipt
therefore remains pending.

Springer Nature's public Hong Kong agreement pages list "The Chinese University
of Hong Kong" and describe corresponding-author eligibility. They do not prove
that The Chinese University of Hong Kong, Shenzhen is recognized as the same
eligible institution or that this exact fully OA journal and Article are covered.

The prepared institutional request asks for:

- Current JCR year, category, rank/denominator and quartile.
- CUHK-Shenzhen recognition status.
- Journal and Article eligibility.
- Coverage amount or percentage.
- Tax, quota, cap and expiry conditions.
- Required email domain and affiliation wording.
- Approval timing and responsible office.

Public agreement text remains supporting context rather than authorization.

## 8. Portal upload manifest

The machine-generated portal manifest contains 12 rows:

- One manuscript DOCX.
- Five main figure PDFs.
- One merged Supplementary Information PDF.
- Three Supplementary Data ZIPs.
- One cover-letter DOCX.
- One Reporting Summary row marked pending Adobe completion and both-author approval.

All rows are marked `NOT_AUTHORIZED`. The retired checklist is excluded. Review
PDFs, package README files, audit JSON files and historical submission files are
not default portal uploads.

## 9. Machine gate

New gate:

`phase17_v7/npj_sba_submission_gate/20260830_exact_file_approval_preparation/00_EXACT_FILE_APPROVAL_PREPARATION.json`

Final status:

`PASS_TECHNICAL_PREPARATION_AUTHOR_AND_INSTITUTION_RECEIPTS_REQUIRED`

The gate verified:

- Starting Git baseline remains an ancestor.
- Package size and SHA-256 are exact.
- All 20 package manifest entries pass.
- ZIP CRC passes.
- Three official form files match frozen sizes and SHA-256 values.
- Reporting Summary dynamic/flat structure is correct.
- Official checklist retirement is detected.
- Retired checklist is absent from the portal manifest.
- Approval, JCR, APC, Reporting Summary and authorization gates remain pending.
- Scientific files and public releases remain unchanged.

## 10. Verification

Focused gate command:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_npj_sba_exact_file_approval_preparation.ps1
```

Results:

- Focused tests: 6/6 passed.
- Full repository regression: 102/102 passed.
- Target package verifier: 20/20 files passed.
- Package SHA-256 remained
  `F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`.

## 11. Files created

Management materials:

- `00_project_management/npj_sba_exact_file_approval_2026-08-30/README.md`
- `Exact_File_Author_Approval.md`
- `Institutional_JCR_APC_Evidence_Request.md`
- `Nature_Portfolio_Reporting_Summary_Response_Map.md`
- `Retired_Editorial_Policy_Checklist_Status.md`
- `Portal_Submission_Runbook.md`
- `official_form_manifest.csv`
- Three unmodified official PDFs under `official_forms/`

Audit tooling:

- `audit_tools/phase17_npj_sba_07_exact_file_approval_preparation.py`
- `audit_tools/run_6013RP_phase17_npj_sba_exact_file_approval_preparation.ps1`
- `audit_tools/test_npj_sba_exact_file_approval_preparation.py`

Machine outputs:

- `00_EXACT_FILE_APPROVAL_PREPARATION.json`
- `01_PORTAL_UPLOAD_MANIFEST.csv`
- `02_OFFICIAL_FORM_STATUS.json`

## 12. Files not changed

- Manuscript source, DOCX and PDF.
- Supplementary Information source, DOCX and PDF.
- Cover letter source, DOCX and PDF.
- Five main and ten supplementary figures.
- Supplementary Data 1-3.
- Target package ZIP.
- GitHub v1.1.0 release.
- Zenodo 22151739.
- Any scientific result or decision.

## 13. Next-stage decision

All locally executable preparation is complete. The next stage is an external
evidence and explicit-consent gate, not another scientific or document-production
round.

Required next inputs are:

1. Explicit Zhi Chen approval tied to package SHA-256
   `F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`.
2. Explicit Teng Qi approval tied to the same package SHA-256.
3. Completed official Reporting Summary from Adobe Reader, reviewed by both authors.
4. Official current Clarivate JCR Q1 receipt.
5. Written CUHK-Shenzhen APC/OA determination.
6. Separate portal submission authorization and, if applicable, APC commitment
   authorization from the corresponding author.

After those items are ingested and hashed, the project may run a portal dry-run.
No actual submission should occur until a final generated-PDF review passes and
the corresponding author explicitly authorizes the final action.

Current honest state: scientifically frozen, technically prepared, externally
awaiting approval and receipts, and not authorized for submission.

## 14. Official sources

- https://www.nature.com/npjsba/for-authors-and-referees/submission-guidelines
- https://www.nature.com/npjsba/for-authors-and-referees/submisions
- https://www.nature.com/npjsba/for-authors-and-referees/about/editorial-policies/reporting-standards
- https://www.nature.com/documents/nr-reporting-summary.pdf
- https://www.nature.com/documents/nr-reporting-summary-flat.pdf
- https://www.nature.com/documents/nr-editorial-policy-checklist.pdf
- https://www.springernature.com/cn/open-science/oa-agreements/hong-kong
- https://www.springernature.com/de/open-science/oa-agreements/hong-kong/joint-university-librarians-advisory-committee
