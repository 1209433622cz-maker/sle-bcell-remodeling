# GitHub synchronization and submission-facing naming action record

## 1. Objective

This round synchronized the working repository with the remote `main` branch,
reduced ambiguity in the public repository surface, replaced current manuscript
and submission artifacts with stable filenames, rebuilt the journal package,
and verified that presentation-level changes did not alter scientific estimates.

The governing rule was to remove internal gate labels, draft numbers and build
dates from current author-facing filenames while retaining necessary provenance
inside Git history, immutable release metadata and the internal audit layer.

## 2. Starting state and synchronization boundary

- Local branch: `main`.
- Remote: `origin/main`.
- Starting local and remote commit: `e6f4cac6625879633cddb30d0399069275e87c71`.
- A fresh `git fetch origin` confirmed that the remote had not advanced during
  this round.
- The existing public DOI remained `10.5281/zenodo.22086892`.
- The immutable public release tag was inspected but not modified.

## 3. Stable current filenames

The following current files now provide the only author-facing entry points:

| Role | Stable path |
|---|---|
| Main manuscript source | `01_manuscript/Manuscript.md` |
| Supplementary source | `01_manuscript/Supplementary_Information.md` |
| Completed research proposal | `01_manuscript/Research_Proposal.md` |
| Cover letter source | `04_submission/Cover_Letter.md` |
| Author confirmation | `04_submission/Author_Confirmation.md` |
| Reporting checklist | `04_submission/Reporting_Checklist.md` |
| Portal instructions | `04_submission/Portal_Upload_Guide.md` |
| Submission package directory | `04_submission/journal_submission/` |
| Local deterministic archive | `04_submission/journal_submission.zip` |
| Release notes | `RELEASE_NOTES.md` |

The main manuscript, supplementary information, research proposal and release
notes were renamed through Git so their provenance remains visible as a rename,
not an unrelated deletion and recreation.

## 4. Current-branch submission cleanup

Fifteen superseded files were removed from the current `04_submission` tree,
including prior author forms, cover letters, reporting checklists, target
decisions, figure-architecture notes and a proposal QC note carrying internal
gate or date labels. These files remain recoverable from Git history and the
immutable release; they no longer compete with the stable files on `main`.

The `.gitignore` policy was tightened so regenerated historical submission
builds remain local while the stable author files, package manifest, required
portal set and portal maps can be tracked.

## 5. README and reproducibility refinement

- The root `README.md` now opens with the study, frozen evidence chain, DOI,
  current files, licence boundary, stable rebuild commands and portal-stage
  next action.
- `01_manuscript/README.md` distinguishes current sources from drafting
  provenance.
- `04_submission/README.md` identifies the exact current source files and the
  required versus optional upload directories.
- `REPRODUCIBILITY.md` separates scientific inference from document rendering
  and uses stable environment-lock aliases.
- Stable public wrappers were added for submission-environment creation and
  package rebuilding.

Stable reproducibility filenames added in this round were:

- `audit_tools/environment_analysis.yml`
- `audit_tools/environment_analysis_win64.txt`
- `audit_tools/environment_analysis_python.txt`
- `audit_tools/environment_submission.yml`
- `audit_tools/environment_submission_win64.txt`
- `audit_tools/check_submission_environment.py`
- `audit_tools/create_submission_environment.ps1`
- `audit_tools/build_submission_package.ps1`

The original dated environment locks and internal gate scripts were retained as
historical implementation provenance. The stable wrappers and aliases are the
documented public entry points.

## 6. Portal-directory hardening

The package builder previously placed an instruction text file inside each
upload directory. This could cause a user to select 12 files instead of the
intended 11-file required set. The policy text was moved to
`submission_docs/PORTAL_UPLOAD_POLICY.txt`.

The final audit now compares manifest aliases against the actual files on disk.
It passes only when:

- the required manifest contains exactly 11 files;
- `portal_upload_required` contains exactly those same 11 files;
- the optional manifest contains exactly 7 files;
- `portal_upload_optional` contains exactly those same 7 files; and
- no standalone supplementary figure is included in the default required set.

Final result: required 11/11 and optional 7/7, with all 11 required-file
SHA-256 values independently recomputed and matched to the portal map.

## 7. Full rebuild and scientific integrity

The stable build command was executed with the public DOI, reusing the already
validated main figures and release-runtime qualification:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\build_submission_package.ps1 `
  -Doi "10.5281/zenodo.22086892" `
  -SkipMainFigureBuild `
  -SkipRuntimeSmokeTest
```

Final scientific and package checks:

- scientific estimates changed: `false`;
- manuscript placeholders: 0;
- cover-letter placeholders: 0;
- supplementary embedding markers: 7/7;
- main-figure panel assertions: 46/46;
- supplementary panel assertions: 29/29;
- main figure width: 170 mm for 5/5 figures;
- supplementary DOCX structure: 7 inline figures and 8 tables;
- accessibility findings: 0 high, 0 medium and 0 low for all three DOCX files;
- restricted large source-data files in the package: 0;
- final internal audit decision:
  `PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`.

The internal gate wording above is retained only as a machine-audit status, not
as a journal-facing filename or manuscript label.

## 8. Rendering and visual quality control

WPS Office rendered and rasterized every final page:

- manuscript: 29 pages;
- supplementary information: 13 pages;
- cover letter: 1 page.

LibreOffice was independently located at
`C:\Program Files\LibreOffice\program\soffice.exe`, temporarily added to the
process `PATH`, and used through the document rendering tool. It independently
produced the same 29, 13 and 1 page counts. Contact sheets covering all 43 pages
were visually inspected. No clipped text, overlapping elements, blank pages,
missing supplementary figures, malformed tables or pagination failures were
observed. The final S7 figure begins on its intended page.

## 9. Final archive identity

- Local archive: `04_submission/journal_submission.zip`.
- Bytes: `45,995,822`.
- SHA-256: `C6FA38AEEFDCD8BD077283EFF3E3586DF2A7F2AC534F8E69656A421C2EB1044F`.
- Manifest payload files: 150.
- DOI: `10.5281/zenodo.22086892`.

The full archive remains local because repository policy excludes generated ZIP
archives. The stable required portal files and their machine-readable maps are
tracked on GitHub.

## 10. Content and repository checks

- Python compilation passed for the updated build, audit and environment-check
  scripts.
- PowerShell parser checks passed for the stable environment and build wrappers
  and the internal runner.
- Markdown local-link validation passed for 12 current entry documents.
- `git diff --check` reported no whitespace errors.
- Current-facing Gate/date/draft-token scanning returned no substantive hit.
  The only broad-regex hit was `gkv007` inside a valid literature DOI.
- `CITATION.cff` and Zenodo metadata retain the release date and semantic version
  because these are required citation/archive fields and describe the immutable
  public record.

## 11. Decision

**PASS_GITHUB_SUBMISSION_PRESENTATION_AND_STABLE_NAMING_SYNC**

The repository is scientifically frozen, the current GitHub-facing submission
surface is substantially less ambiguous, and the package is authorized for
portal use. This round made presentation, reproducibility-entry and packaging
changes only; it did not reopen outcome analysis or alter numerical claims.

## 12. Next stage

The next stage is journal operation rather than new analysis:

1. Enter the manuscript metadata and declarations field by field in the Genome
   Medicine submission portal.
2. Upload the exact 11-file required set using `Portal_Upload_Guide.md` and
   `PORTAL_UPLOAD_REQUIRED.csv`.
3. Compare the portal-generated combined PDF against the final DOCX files,
   figures, author order, DOI, declarations and supplementary-file labels.
4. Submit only after the corresponding author confirms that generated PDF.
5. Freeze the submission receipt, manuscript number, submitted combined PDF and
   portal metadata export as the next immutable administrative record.

New scientific analyses should be opened only for a decision-changing editorial
or reviewer request. The current evidence package should otherwise remain
frozen.
