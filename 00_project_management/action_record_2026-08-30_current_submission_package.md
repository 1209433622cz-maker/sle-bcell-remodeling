# Current journal-neutral submission package action record

Date: 2026-08-30 (Asia/Hong_Kong)

Status: **PASS_CURRENT_SUBMISSION_PACKAGE_INTEGRITY_NOT_SUBMISSION_AUTHORIZATION**

## Request and decision

The user requested packaging of the current submission materials. Because no target journal has been selected and official JCR Q1/APC evidence remains pending, this round built a journal-neutral editorial preflight package rather than inventing a journal-specific final submission.

The historical `04_submission/journal_submission/` package was rejected as the build source. It contains an earlier 32-page manuscript, a Genome Medicine-specific cover letter, the withdrawn historical DOI and pre-correction C9 language. Reusing that directory would have reintroduced superseded content.

The scientific source of truth was instead the publicly verified Zenodo `Research_Archive.zip` associated with `10.5281/zenodo.22151739`, SHA-256 `AAE67863FC6B34B0AC091F8D38524FFC55A7CF364FF7FF4B4D43FEDFA4AE0095`. All scientific files in the new package were selected from this immutable archive and checked against its internal content manifest before extraction.

## Output

Primary deliverable:

`04_submission/current_submission_package/SLE_Bcell_Submission_Package.zip`

- Bytes: `19,168,244`
- SHA-256: `B7D30320ADFFF5D15E335A269AFC62E516C5001B2FF7BE4F8188E3B72AAFBFD5`
- ZIP entries: 31, including the package manifest itself
- Manifest-managed files: 30
- Consecutive deterministic rebuilds: 2/2 with identical bytes and SHA-256

The ZIP-level checksum is stored beside the package in `SLE_Bcell_Submission_Package_SHA256.txt`. The extracted package remains available in the same output directory for direct inspection.

## Package inventory

1. `01_Manuscript/`: current author-confirmed QiTeng R2 manuscript in DOCX and WPS-rendered PDF; PDF page count 18.
2. `02_Supplementary_Information/`: current supplementary information in DOCX and PDF; PDF page count 19.
3. `03_Main_Figures/`: Figures 1-5 as single-page vector PDFs.
4. `04_Supplementary_Figures/`: Supplementary Figures S1-S10 as single-page vector PDFs.
5. `05_Source_Data/`: `Figure_Source_Data.zip`, `Full_Statistical_Results.zip` and `Regulator_Sensitivity.zip`.
6. `06_Administrative/`: journal-neutral cover-letter draft in Markdown, DOCX and WPS PDF; author/declaration entry sheet; submission-readiness sheet.
7. `07_Integrity/`: package metadata, SHA-256 manifest and portable standard-library verifier.

Twenty-two scientific files were copied byte-for-byte from the verified public archive. No manuscript science, supplementary science, figure, source table, statistic, threshold, mapper, cohort or analysis result was regenerated or edited.

## Journal-neutral cover letter

The previous cover letter was not reused because it named Genome Medicine, used the earlier title, cited the withdrawn DOI as current, described a revised archive as pending and referred to an earlier approval scope.

A new administrative draft was built around the current title and evidence boundary. It now states:

- current title using `distinguishes`;
- current DOI `10.5281/zenodo.22151739` and repository;
- source-label-defined independent replication;
- permanent R1 HOLD;
- C9R calibration HOLD and no corrected external disease outcome;
- five main and ten supplementary figures;
- noncausal regulatory interpretation;
- confirmed originality, conflicts, funding, ethics and generative-AI declarations.

It deliberately omits a target-journal fit paragraph and does not claim approval of the new exact package. The footer states `Journal-neutral draft | Target selection and exact-file author approval pending`.

DOCX build and render QA:

- DOCX paragraphs: 16
- DOCX bytes: 39,368
- WPS PDF bytes: 75,234
- WPS PDF pages: 1
- all WPS-rendered pages visually inspected: 1/1 PASS
- clipping, overlap, missing glyphs and footer collision: none observed
- accessibility audit: 0 high, 0 medium, 0 low findings

LibreOffice was also used for an independent initial render. Its first invocation could not locate `soffice` because the executable directory was absent from the process PATH; the existing LibreOffice and bundled Poppler paths were supplied only to that process, without changing system settings. The resulting one-page render also passed visual inspection. The final package uses the WPS PDF.

## Integrity and structural verification

The package builder performed the following checks before writing the ZIP:

- public Research Archive SHA-256 matched the frozen value;
- Research Archive CRC passed;
- every selected scientific file matched its internal bytes and SHA-256 row;
- cover-letter DOCX included the current title, DOI, R1/C9R limits and pending-approval footer;
- stale Genome Medicine, old DOI and pending-archive language were absent;
- package paths could not escape the output root;
- manifest inventory, bytes and SHA-256 passed for all 30 listed files;
- outer ZIP CRC and exact inventory passed.

Independent post-build audit then confirmed:

- portable bundled self-verifier: 30/30 PASS;
- main/supplement/cover PDF pages: 18/19/1;
- five main and ten supplementary PDF files, each one page;
- all three DOCX files opened and contained readable paragraphs;
- nested ZIP CRC: 3/3 PASS;
- nested entries: Figure Source Data 16, Full Statistical Results 185, Regulator Sensitivity 11;
- two consecutive builds produced SHA-256 `B7D30320ADFFF5D15E335A269AFC62E516C5001B2FF7BE4F8188E3B72AAFBFD5`;
- scientific freeze reverification: `PASS_FREEZE_INTEGRITY_NOT_SCIENTIFIC_GATE_PASS`.

One exploratory nested-ZIP Python one-liner contained a closing-parenthesis typo and did not execute. It was replaced by a normal loop; all three CRC checks then passed. The first package attempt also correctly stopped because the DOCX semantic reader initially inspected only `document.xml` while the approval-warning text was in `footer1.xml`; the verifier was repaired to inspect both the body and all footer parts before the successful build.

## Regression tests

Five new package-specific tests cover:

- exact five-main/ten-supplementary figure inventory;
- rejection of invented target, JCR/APC, author-approval or submission states;
- rejection of stale journal/DOI cover-letter text;
- path traversal rejection;
- manifest tamper rejection.

Final test result:

- document, release, package, review and scientific-freeze suite: 73/73 PASS;
- C9 calibration and normalization contract suite: 9/9 PASS;
- combined: **82/82 PASS**.

## Governance state

- Scientific baseline: QiTeng R2, unchanged.
- R1: `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`, permanent.
- C9R: `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`, retained.
- Corrected external outcome unlock: false.
- Target journal: none.
- JCR Q1 eligibility verified: false.
- Institutional APC/OA coverage verified: false.
- Target-specific adaptation: not started.
- Exact approval of this new package: pending.
- Journal submission authorization: false.
- APC commitment authorization: false.

The package is complete and technically ready for author/editorial review. It must not be uploaded to a journal portal in its current form.

## Next-stage objective

The next stage remains `JCR_PROFILE_AND_APC_EVIDENCE_ACQUISITION`, not further biological analysis:

1. Archive the complete JCR profiles for npj Systems Biology and Applications and Communications Biology, including all categories, rank/denominator and quartile.
2. Obtain CUHK-Shenzhen's applicable multicategory Q1 rule and APC/OA eligibility response.
3. Freeze the first target using the recorded decision rule.
4. Perform one bounded target-specific adaptation of title, abstract, section structure, declarations, figure dimensions and cover letter.
5. Rebuild this package from the same frozen scientific sources, repeat WPS/manifest/portal QA and obtain approval of the exact final hashes.
6. Seek separate explicit authorization before any portal upload, submission or APC commitment.
