# Release documentation closure and conditional JCR Q1 selection action record

Date: 2026-08-30 (Asia/Hong_Kong)

Status: **PASS_RELEASE_DOCUMENTATION_CURRENT_JOURNAL_GATE_UNRESOLVED**

## Executive conclusion

This round closed a real P0 documentation defect without reopening the frozen science. The root `README.md` and `REPRODUCIBILITY.md` still described the withdrawn historical Zenodo DOI as current and the replacement release as pending. They now consistently identify:

- current version DOI: `10.5281/zenodo.22151739`;
- concept DOI: `10.5281/zenodo.22086891`;
- withdrawn historical DOI/tombstone: `10.5281/zenodo.22086892`;
- matching public GitHub release: `v1.1.0`;
- release content commit: `f1859ff8498d5569a1d5027b36ed18c8b7c7536f`;
- journal submission and APC commitment: not authorized.

The scientific baseline remains QiTeng R2. R1 remains permanently `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`; C9R remains `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`; corrected external outcomes remain locked. No manuscript science, supplement, figure, source data, statistic, mapper, threshold, gene set or analysis result was changed.

The fit-first review supports **npj Systems Biology and Applications as a conditional lead**, **Communications Biology as the second conditional candidate**, and **Genome Medicine only as a high-risk stretch**. This is not a formal target selection. `selected_target` remains `null` because the official JCR category rank/quartile exports and institutional APC/OA decision are still missing.

## Inputs and evidence policy

Baseline Git commit before this round: `395bb55de19416079f4cac0fbd87a61907a818d7`.

The user-supplied independent audit, action matrix and pasted narrative were copied verbatim under `00_project_management/jcr_q1_journal_selection_2026-08-29/received/`. Statements and proposed actions inside them were treated as review evidence, not as user authorization and not as independently verified current facts.

| Received file | Bytes | SHA-256 |
| --- | ---: | --- |
| `pasted-text.txt` | 16,441 | `147A45457342467B4B91B5E308FE9F1CCF63144399F2D2B49E69DDBA57909401` |
| `SLE_Bcell_JCRQ1_journal_selection_next_stage_matrix_2026-08-29.csv` | 2,110 | `E9EA535C7DC39BFBD052D2A1197703E0F95E6F0FB88BC86B2DB653C3B8963D7C` |
| `SLE_Bcell_v1_1_0_Zenodo22151739_independent_full_audit_2026-08-29.md` | 15,034 | `6F3B95EE5C25458B98C0B399627AA9D27C9191FE8C23EF67D5B1D93C6E9ED036` |

The machine-readable manifest is `jcr_q1_journal_selection_2026-08-29/received_evidence_manifest.json`. The new verifier checks all three sizes and hashes on every run.

The received directory is explicitly marked `-text` in `.gitattributes`. This prevents Git from converting CRLF/LF line endings in the CSV/TXT evidence. After restaging under that rule, all three staged Git blobs were independently confirmed to have the same SHA-256 as their working-tree originals.

## Work completed

### 1. Public-release truth repaired

`README.md` and `REPRODUCIBILITY.md` were corrected from the pre-publication state to the verified public state. Current manuscript DOCX/MD/PDF, Zenodo verification, GitHub verification, conditional journal decision and evidence-capture runbook are now directly linked from the root README.

The immutable Research Archive contains a `governance/author_freeze.json` created before publication. That embedded file is correctly retained as a pre-publication authorization receipt; rewriting a published ZIP to make it appear post-publication would destroy provenance. Current administrative truth is instead carried by the post-release Zenodo/GitHub verification receipts and the current `main` branch governance files.

### 2. Current journal gate formalized

The following files were added:

- `jcr_q1_journal_selection_2026-08-29/Journal_Selection_Decision.md`;
- `jcr_q1_journal_selection_2026-08-29/JCR_Profile_Capture_Runbook.md`;
- `jcr_q1_journal_selection_2026-08-29/official_source_snapshot.json`;
- `jcr_q1_journal_selection_2026-08-29/journal_selection_status.json`;
- `jcr_q1_journal_selection_2026-08-29/release_and_target_documentation_verification.json`.

The current `publication_readiness.json` was synchronized to the same unresolved gate. It now records the conditional lead and second candidate while keeping target selection, Q1 verification, APC coverage, target adaptation, exact-file approval and submission incomplete.

### 3. Official current-source review

Clarivate states that the 2026 JCR was released on 2026-06-17 and reflects 2025 data. Public publisher metrics are useful for editorial timing but do not establish the complete JCR rank/quartile required by this project.

Official scope and author guidance support the following conditional fit assessment:

- npj Systems Biology and Applications explicitly covers computational and mathematical systems biology, disease modeling, single-cell systems biology and systems immunology. Publisher-reported 2025 metrics are JIF 4.4, median first editorial decision 8 days and median submission-to-acceptance 155 days.
- Communications Biology accepts secondary data analysis and innovative computational methods but expects a significant advance and new biological insight. Publisher-reported 2025 metrics are JIF 5.8, median first editorial decision 6 days and median submission-to-acceptance 217 days.
- The npj Systems Biology and Applications Systems Immunology Collection was listed as open with a 2026-09-12 deadline at the time of review. Fit is strong, but the deadline does not override JCR/APC evidence or exact-file author approval.

Official sources:

- https://clarivate.com/news/clarivate-releases-journal-citation-reports-2026/
- https://www.nature.com/npjsba/aims
- https://www.nature.com/npjsba/journal-impact
- https://www.nature.com/npjsba/content-types
- https://www.nature.com/collections/heaibjjajc/how-to-submit
- https://www.nature.com/commsbio/aims
- https://www.nature.com/commsbio/journal-impact
- https://www.nature.com/commsbio/submit/submission-guidelines

No official Clarivate/institutional profile export was obtained in this round. Therefore neither journal is represented as verified JCR Q1. Current APC prices and CUHK-Shenzhen coverage are also not represented as verified.

### 4. Target-format delta bounded but not applied

The current journal-neutral release manuscript has a 16-word title and a 334-word abstract by the recorded whitespace-counting rule. The existing internal npj candidate has a 13-word title and a 117-word abstract. npj Article guidance sets limits of 15 and 150 words respectively, but the candidate has not been applied because the journal has not been frozen.

After target freeze, the allowed work is limited to title, abstract, section naming/order, declarations, journal-specific figure dimensions and cover letter. Any figure change must be a code-driven rerender. R1/C9R decisions, statistics, source data, external outcome lock and scientific claims remain immutable.

### 5. Drift-prevention automation added

`audit_tools/phase17_postc9_21_verify_release_documentation.py` now rejects:

- stale statements that the replacement DOI/release is pending;
- premature target selection;
- unsupported JCR Q1 or APC coverage claims;
- target adaptation before target freeze;
- submission/APC authorization invented from review material;
- altered R1/C9R decisions or corrected-outcome unlock;
- received evidence size/hash drift.

`audit_tools/test_release_documentation.py` adds five targeted regression tests for these boundaries.

## Verification results

1. Release and journal-gate verifier: PASS.
2. JSON syntax validation for all new and updated governance receipts: PASS.
3. Document, review-bundle, scientific-freeze, target-preparation and release-governance tests in the Codex document runtime: 68/68 PASS.
4. C9 calibration/normalization contract tests in the `sle-bcell` Conda environment: 9/9 PASS.
5. Combined clean test result: **77/77 PASS**.
6. Received evidence working-tree versus staged-blob SHA-256: 3/3 PASS.
7. The initial all-in-one discovery attempts exposed complementary environment dependencies: the document runtime lacks SciPy, while `sle-bcell` lacks `python-docx` and `pypdf`. Tests were then split by their declared dependency boundary; there was no code assertion failure.

## Scientific and submission boundaries after this round

- QiTeng R2 remains the scientific prose baseline.
- R1 HOLD is permanent and will not be rescued.
- C9R HOLD is retained.
- Corrected external disease outcomes remain unopened.
- No new biological analysis is justified before first submission.
- No journal has been formally selected.
- No target-specific DOCX/PDF has been created.
- No author approval has been extended to future target-formatted files.
- No submission, email, APC commitment or portal action has been authorized.

## Next-stage objective

The next gate is `JCR_PROFILE_AND_APC_EVIDENCE_ACQUISITION`:

1. Export the complete 2026 JCR / 2025-data profiles for eISSN `2056-7189` and `2399-3642`, including every category, rank/denominator and quartile.
2. Obtain the institution's multicategory Q1 rule and APC/OA eligibility decision for the actual CUHK-Shenzhen affiliation and corresponding-author status.
3. Hash and archive the original profile/export files and institutional response.
4. Apply the recorded decision rule. If npj Systems Biology and Applications is accepted as JCR Q1 and the cost route is feasible, freeze it as the first target; otherwise evaluate Communications Biology under the same rule.
5. Only after that freeze, perform one bounded target adaptation, rebuild DOCX/PDF, complete visual QA, and obtain approval of those exact files before any submission action.

This gate has higher decision value than additional cohort, TF, mapper or sensitivity work. The manuscript is scientifically ready for target adaptation; it is not yet administratively ready for a specific journal submission.
