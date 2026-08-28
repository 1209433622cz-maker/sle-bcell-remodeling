# External methods review dossier

**Status: feedback and disposition considered by both authors; reviewer identity and an independently authenticated methods decision remain unverified.**

The user supplied a detailed audit and action matrix dated 28 August 2026,
referring to repository commit `f28cf6a481232408710862eee5ee2db735dec70b` and the
earlier correction-review ZIP with SHA-256
`DA07D1D7F87E559A7778618FDFAE5BD55DA77291E1F0BAA44B915CDE209B5993`.
Their originals are archived under `00_project_management/external_review_2026-08-28/received/` with a copy-integrity manifest.
The agent has not authenticated the reviewer identity, professional capacity,
independence or computational environment. This feedback is useful evidence of
review, but it does not constitute author approval or a signed methods decision.

## Scope and materials

Start with code, compact frozen outputs, tests and the current manuscript. A
363,083-cell rerun is not a prerequisite for this first code/output review.
If a decision-changing implementation defect is found, document it before
opening a separately specified correction run. Do not retune a failed gate.

Repository source paths below refer to the same project root. The review ZIP
contains the scientific scripts under `reproducibility/`, current manuscript
sources under `sources/`, and compact calibration outputs under
`additional_files/Full_Statistical_Results.zip:external_mapping_calibration/`.
Three per-cell diagnostic exports remain local and are indexed by hashes;
their absence from the ZIP limits what can be independently recomputed from it.

## Twelve review questions

All external decisions below are **PENDING**. Evidence pointers describe what
the reviewer should inspect; they are not proxy signatures by this agent.

| ID | Question | Evidence pointer / expected boundary |
|---|---|---|
| M01 | Same normalization formula? | `audit_tools/phase17_c9_common.py::normalize_log_cp10k`; reference and external both log1p(CP10K) using full-library totals |
| M02 | Reference full-library totals correctly aligned? | `phase17_c9_01_prefreeze_label_agnostic_mapping.py::train_reference_mappers`; local `03_REFERENCE_LIBRARY_SIZE_AUDIT.csv`; feature-subsetting regression |
| M03 | Candidate arithmetic correct? | `07_MAPPER_CONFIDENCE_CALIBRATION.csv`; 72 rows, recount CSV/JSON; OOF records are local, not an independent new model fit |
| M04 | State-specific eligibility enforced? | `calibrate_confidence` and `confidence_calibration_passed`; coverage >=0.80 and precision >=0.90 for both states |
| M05 | Diagnostic fallback truly fail-closed? | `validate_unlock_decision` and failed-calibration/forged-PASS regression cases; diagnostic threshold is not authorization |
| M06 | Corrected outcomes remain protected? | `02_PROTECTED_METADATA_CONTRACT.json`, decision JSON and `verify_prefreeze` before `load_metadata`; no corrected disease outputs |
| M07 | Formal run complete? | `11_SAMPLE_PREFREEZE_SUMMARY.csv`, decision checks; 56 matrices and 363,083 cells; non-test truncation prohibited |
| M08 | Donors separated across CV folds? | `06_MAPPER_DONOR_GROUPED_CV.csv`, recount audit; 258 donors across five folds; local OOF rows for independent recount |
| M09 | Non-nested tuning caveat explicit? | Manuscript reference-calibration Methods; shared feature selection and tuning prevent an unbiased held-out performance claim |
| M10 | No selective centroid rescue? | Both mapper eligibility checks required; elastic B_ASC precision 0.885210 <0.90 cannot be replaced by a successful centroid |
| M11 | Old C9 outcome appropriately superseded? | Correction contract, current Results and old-run provenance; original outcomes were already known and are no longer supporting evidence |
| M12 | Manuscript and code support the same claims? | Methods/Results/Discussion, S10, Table S9 and RP; source-label-defined primary replication remains, independent label-agnostic robustness unresolved |

## Required reviewer return

For each question, record a decision, the specific code/output inspected, any
command actually executed, and a finding or reason for no concern. Distinguish
document inspection, arithmetic recomputation and model refitting. Identify the
reviewer and declare any participation in the original analysis. The overall
decision may be qualified; do not convert uninspected items into PASS.

The current 15-item disposition is recorded in this round's action report.
The manuscript has only two targeted wording changes in response to TEXT-01/02.
S10's optional frontier redraw is deferred because it is not required to express
the current calibration failure and no reviewer has requested it as a blocker.

## Separate author gate

The user explicitly confirmed the current materials for both authors and stated
that both had considered the external methodological feedback and its disposition
on 28 August 2026. The record is `author_confirmation.json`, linked to the
reviewed package SHA-256. This closes author consideration and current-content
confirmation; it does not authenticate an external reviewer or invent an
independent methods decision. The twelve-question dossier remains available for
additional qualified review, but is not represented as a journal-mandated
signed pre-submission certificate. Journal selection and formatting preparation
may proceed while this limitation is recorded.

The current form is `04_submission/Author_Confirmation.md` in the repository and
`governance/Author_Confirmation.md` in the ZIP. Journal choice, matching revised
archive, final journal-formatted files and actual upload authorization remain
separate decisions. No additional confirmation of the same unchanged reviewed
scientific content is requested by this record.
