# Journal portal preparation guide

**Submission hold (28 August 2026):** the existing package predates the corrected
external-mapping calibration audit. Do not upload it unchanged. Canonical sources
now retain C9A HOLD; the original C9 PASS is superseded. The target journal is not
currently fixed. Rebuild the package, rerender the documents and reconcile the
version-specific archive before using the historical checklist below.

Use `correction_review/PORTAL_FILES.csv` to review proposed file roles only.
No files are currently authorized for upload. The historical `journal_submission`
directory must not be used as the current package.

## Required files

| Portal role | Filename |
|---|---|
| Main manuscript | `Manuscript.docx` |
| Supplementary information | `Supplementary_Information.docx` |
| Cover letter | `Cover_Letter.docx` |
| Figure source data | `Figure_Source_Data.zip` |
| Regulator sensitivity results | `Regulator_Sensitivity.zip` |
| Complete statistical results | `Full_Statistical_Results.zip` |
| Main figure 1 | `Figure_1.pdf` |
| Main figure 2 | `Figure_2.pdf` |
| Main figure 3 | `Figure_3.pdf` |
| Main figure 4 | `Figure_4.pdf` |
| Main figure 5 | `Figure_5.pdf` |

## Optional files

The ten `Supplementary_Figure_S*.pdf` files duplicate figures embedded in
`Supplementary_Information.docx`. Upload them only if the portal explicitly
requires standalone supplementary figures.

## Portal checks

1. Preserve author order: Zhi Chen first author; Teng Qi corresponding author.
2. Confirm both ORCID records and the corresponding email.
3. Copy ethics, consent, competing interests, funding, acknowledgements,
   contributions and generative-AI statements from `Manuscript.docx`.
4. Create and verify a matching archive after renewed approval. The initial DOI
   `10.5281/zenodo.22086892` does not identify the revised materials.
5. Compare the portal-generated PDF against the manuscript, supplement, cover
   letter and all five figures before final submission.
6. After submission, save the receipt, manuscript number, submission time and
   uploaded-file hashes in a new action record.
