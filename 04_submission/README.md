# Journal submission workspace

This folder contains current review sources and a historical submission package.
**Submission is on hold.** The corrected external-mapping sensitivity failed
reference calibration; the original C9 PASS is not supporting evidence.

## Current sources

- `Cover_Letter.md`
- `Author_Confirmation.md`
- `Reporting_Checklist.md`
- `Portal_Upload_Guide.md`

`Zenodo_Metadata.json` records the initial published archive. Its DOI and author
approval apply to that historical snapshot, not the current correction review.
Do not reuse it as metadata for a new release without reconciliation.

## Generated package

`author_review/` and `author_review.zip` are the current locally generated,
journal-neutral author-review bundle. Their `STATUS.json` explicitly prohibits
submission. `PORTAL_FILES.csv` lists draft roles, not permission to upload.
The `governance/` directory contains the current unchecked author form, the
current-only checklist and the external methods-review dossier. The previous
`correction_review/` and ZIP are preserved review snapshots, not current sources.

`journal_submission/` and `journal_submission.zip` remain historical snapshots.
Do not mix their portal files with the revised documents or overwrite them.
The old one-click release entry points are retired because they would regenerate
outdated prose and remove the old package.

Build a new review bundle with `audit_tools/build_correction_review.ps1` using an
empty output directory. Verify an existing bundle with its bundled
`verify_review_bundle.py`; the verifier needs only Python's standard library.
Verification is not a fresh numerical rerun, publication approval or a new DOI.
Use each historical ZIP's own bundled verifier for its original schema.

Superseded submission drafts remain recoverable from Git history and the
immutable public release; they are not retained as competing files on `main`.
