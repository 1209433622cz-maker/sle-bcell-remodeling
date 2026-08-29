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
approval apply to that historical snapshot. The linked replacement draft is
record `22151739`, with reserved DOI `10.5281/zenodo.22151739`; local release
materials are rebuilt from the QiTeng R2 scientific freeze and are not yet public.
Do not treat DOI reservation or a local archive check as publication.

## Generated package

`corrected_candidate/` and `corrected_candidate.zip` are the current locally generated,
journal-neutral correction candidate. Their `STATUS.json` explicitly prohibits
submission. `PORTAL_FILES.csv` lists draft roles, not permission to upload.
Figure 1c and its legend are corrected together; Figure 1a interpretation nodes
have non-overlapping text. The omission claim is qualified without changing any
numbers. `governance/` distinguishes the confirmed prior materials from this
pending candidate, retains original changed files and verifies the exact delta.
All three statistical/source-data ZIPs and the other fourteen figures are unchanged.
`author_confirmed_review/`, `author_review/`, `correction_review/` and their ZIPs
are preserved snapshots; they are not final upload materials.
The user requires JCR Q1. Current-year category, rank and quartile evidence,
journal-specific formatting and final-file approval remain separate tasks.

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
