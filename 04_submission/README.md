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
approval apply to that historical snapshot. The linked replacement is public as
record `22151739`, DOI `10.5281/zenodo.22151739`; its release materials were rebuilt
from the QiTeng R2 scientific freeze and independently checked against the public
API. The separately authorized old-record deletion was subsequently completed: DOI
`10.5281/zenodo.22086892` now resolves to a visible tombstone, while the concept
DOI resolves to record `22151739`. GitHub release `v1.1.0` mirrors the three
verified Zenodo upload files and its annotated tag targets the frozen content
commit `f1859ff8498d5569a1d5027b36ed18c8b7c7536f`.

## Generated package

`current_submission_package/SLE_Bcell_Submission_Package.zip` is the current local
journal-neutral editorial preflight package. It is generated from the verified
Zenodo Research Archive by
`audit_tools/phase17_postc9_23_build_current_submission_package.py`. Its manifest
contains the current 18-page manuscript, 19-page supplementary information, five
main figures, ten supplementary figures, three source-data/statistical archives,
a WPS-rendered journal-neutral cover-letter draft and integrity/governance files.
The ZIP is intentionally ignored by Git; its exact size, SHA-256 and verification
state are recorded under
`00_project_management/current_submission_package_2026-08-30/`.

This package is complete for review but is **not authorized for portal upload**.
The target journal, official JCR Q1 evidence, APC/OA route, target-specific format
adaptation and approval of the exact final hashes remain pending. The bundled
`00_READ_ME_FIRST.md`, `Submission_Readiness.md` and self-verifier preserve this
boundary.

`corrected_candidate/` and `corrected_candidate.zip` are earlier local correction
candidates. Figure 1c and its legend were corrected together; Figure 1a
interpretation nodes have non-overlapping text and the omission claim is qualified
without changing any numbers. Their governance records remain historical evidence.
`author_confirmed_review/`, `author_review/`, `correction_review/` and their ZIPs
are preserved snapshots; they are not final upload materials.
The user requires JCR Q1. Current-year category, rank and quartile evidence,
journal-specific formatting and final-file approval remain separate tasks.

`journal_submission/` and `journal_submission.zip` remain historical snapshots.
Do not mix their portal files with the revised documents or overwrite them.
The old one-click release entry points are retired because they would regenerate
outdated prose and remove the old package.

Build the current package by first generating and rendering the cover-letter draft,
then running the package builder. Verify the extracted package with
`07_Integrity/Verify_Package.py`; the bundled verifier needs only Python's standard
library. Verification is not a fresh numerical rerun or submission approval. Use
each historical ZIP's own bundled verifier for its original schema.

Superseded submission drafts remain recoverable from Git history and the
immutable public release; they are not retained as competing files on `main`.
