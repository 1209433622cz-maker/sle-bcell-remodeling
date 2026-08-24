# Journal submission workspace

This folder contains the current author-facing submission sources and the
reproducibly generated portal package.

## Current sources

- `Cover_Letter.md`
- `Author_Confirmation.md`
- `Reporting_Checklist.md`
- `Portal_Upload_Guide.md`
- `Zenodo_Metadata.json`

## Generated package

`journal_submission/portal_upload_required/` is the default 11-file portal
set. Its filenames are stable and do not contain draft numbers, internal gate
labels or build dates. `journal_submission/portal_upload_optional/` contains
standalone supplementary figures for use only when the journal requests them.

The deterministic local archive is `journal_submission.zip`. WPS renders,
page images and most internal quality-control artifacts remain local; the
manifest and portal maps provide the tracked integrity record.

Superseded submission drafts remain recoverable from Git history and the
immutable public release; they are not retained as competing files on `main`.
