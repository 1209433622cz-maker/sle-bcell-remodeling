# Journal submission package

This directory is the current author-approved, journal-facing submission set.
Internal build identifiers and draft numbers are intentionally excluded from
submission filenames.

## Scientific and release status

- DOI: https://doi.org/10.5281/zenodo.22086892
- Scientific estimates changed during final publication engineering: no
- Main panel-data assertions: PASS 46/46
- Supplementary-figure panel-data assertions: PASS 29/29
- Main figures: vector PDF at 170 mm plus 600-dpi PNG
- Author declarations and generative-AI disclosure: complete
- Code licence: MIT
- Original text, figures, documentation and derived source-data licence: CC BY 4.0
- Third-party GEO/CELLxGENE data: excluded from project relicensing

## Portal policy

Use `portal_upload_required/` as the default 11-file upload set. The seven PDFs
in `portal_upload_optional/` duplicate figures embedded in Supplementary
Information and should be used only if the journal portal explicitly requires
standalone supplementary figures.

## Verification

`MANIFEST_SHA256.csv` records every package payload file. The canonical ZIP is built twice and accepted only when both byte streams have the same SHA-256.
