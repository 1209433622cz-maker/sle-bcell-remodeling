# Current correction review checklist

**REVIEW ONLY. NOT AUTHORIZED FOR SUBMISSION.**

This file contains current status only. Previous checked approvals and old
acceptance counts are preserved at
`00_project_management/external_review_2026-08-28/history/Reporting_Checklist.md`.
They do not authorize this correction or its submission.

## Scientific scope

- [x] The original C9 PASS is excluded from supporting evidence after the normalization and calibration-gate audit.
- [x] The corrected 56-matrix, 363,083-cell run remains on reference-calibration HOLD; corrected disease outcomes were not estimated.
- [x] R1 end-to-end identity HOLD and source-label dependence remain explicit.
- [x] No threshold, seed, mapper, gene set or original disease effect was changed in this editorial round.
- [x] Methods describes evaluated confidence candidates, not an eligible elastic-net threshold.
- [x] Discussion explicitly states the corrected B_ASC calibration failure and absence of corrected disease estimates.
- [x] Main-figure checks are 42 scientific/data assertions plus 5 typography checks, totaling 47; this is not 47 independent scientific tests.
- [x] Existing S1-S7 checks total 29; S8 and S9 have separate 36-row and 128-row source contracts. S10 describes reference calibration, not a disease effect.

## Review governance

- [x] The user-supplied review memo and 15-row action matrix have been archived with hashes and itemized responses.
- [x] Historical author approvals and the earlier pending form are preserved separately from the current confirmation.
- [x] The external methods-review dossier defines 12 checkable questions and distinguishes feedback received from signed methodological closure.
- [ ] External reviewer identity, independence, evidence scope and a specific final decision are recorded.
- [x] The user confirmed the exact reviewed materials for both authors, bound to the SHA-256 in author_confirmation.json.
- [x] Both authors considered the external methodological feedback and the documented disposition, as explicitly reported by the user.
- [x] The user specified JCR Q1, rather than a CAS or SJR quartile, as the selection criterion.
- [x] The confirmed prior snapshot is preserved; the figure-label-corrected candidate has its own pending final-file approval state.
- [ ] The target journal, ranking basis and APC arrangements have been confirmed.

## Technical and release checks

Each new build must validate its own Markdown/DOCX/PDF hashes, all-page WPS
rendering, accessibility, complete nested manifests and deterministic ZIP bytes.
The machine-readable build receipt records the actual result for that payload;
this checklist does not transfer a prior render PASS to changed files.

- [ ] Target-journal figure dimensions and submission instructions have been applied from source code and rechecked.
- [x] Figure 1c was regenerated and its agreement-threshold legend integrated into the journal-neutral corrected candidate; all scientific source tables are unchanged.
- [ ] The corrected candidate has completed target-journal formatting and final exact-file author approval.
- [ ] Any required independent-environment numerical reproduction has been completed and scoped accurately.
- [ ] The approved final commit is associated with a new immutable archive and matching version-specific DOI.
- [ ] DOI insertion and any subsequent edits have been rebuilt, reverified and approved for the final payload.
- [ ] Actual portal upload files have been authorized; submission receipt and manuscript number may be recorded only after submission.

The initial DOI remains historical. Current-content confirmation is recorded;
it is not approval of future changes, a new release or actual journal submission.
Unverified external-reviewer identity remains disclosed, without inventing a
journal requirement for a signed pre-submission methods certificate.
