# Manuscript sources

## Current documents

- `Manuscript.md`: current main manuscript source.
- `Supplementary_Information.md`: current supplementary information source.
- `Research_Proposal.md`: current completed research proposal.

These stable filenames are the only author-facing entry points. Draft numbers,
internal review labels and dates are intentionally omitted from current files.

## Provenance

Superseded manuscript, supplement and proposal drafts were removed from the
working tree during the 2026-08-27 workspace cleanup. Their complete evolution
remains recoverable from Git history and the dated action records under
`00_project_management/`; they must not be uploaded to a journal portal.

The only retained internal reference assets in this folder are the verified
BibTeX library and citation/signature audit. They are not journal uploads.

The generated DOCX files are built from the current Markdown sources by
`audit_tools/build_submission_package.ps1`.
