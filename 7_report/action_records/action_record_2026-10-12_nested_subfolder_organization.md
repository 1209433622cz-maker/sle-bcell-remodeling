# Action record: nested subfolder organization

Date: 2026-10-12

## Objective

Extend the non-destructive organized project view beyond `4_figures` so the remaining organized folders also have precise topic subfolders. Preserve all frozen paths, hashes, scientific objects and reproducibility contracts.

## Inputs and policy

- Workspace: `H:\cuhk-2025fALL\6013RP-wyf`
- Baseline inventory: `9_version/inventory/WORKSPACE_FILE_INVENTORY_2026-10-12.csv`
- Baseline inventory rows: 39,521
- Git baseline before this round: `bdc5556e86164c15cdf3085610f3f6b8ef2b616d`
- Existing figure organization: 3,765 inventory records under the established Fig1-Fig8, Supplementary, QA Renders and Other Visuals structure

This round used a catalog-view design rather than moving original files. Each baseline file outside `4_figures` was assigned to exactly one second-level topic. Every topic folder contains a scope README and a dated CSV with original path, size, SHA-256, lifecycle, value tier, audit status and assigned category.

## Accounting result

- Baseline files: 39,521
- Existing figure-tree records excluded from reclassification: 3,765
- Files assigned to new second-level catalogs: 35,756
- Unclassified targeted files: 0
- Missing source paths: 0
- Non-PASS content-check rows: 0
- Source paths moved: 0
- Source paths renamed: 0
- P3 cleanup-review rows, non-exclusive: 4,869
- Current submission directory files: 41
- Submission payload files covered by package verifier: 40/40 PASS
- Generated organization files covered by the organization SHA-256 manifest: 141/141 PASS

## Bucket totals and taxonomy

- `0_admin`: 8 records classified into citation/licensing, governance/reproducibility, status/navigation and other administration.
- `1_data`: 8,901 records classified into raw inputs, processed matrices, external cohorts, metadata/design, manifests/checksums and derived tables.
- `2_code`: 1,323 records classified into current Stage M, tests, Windows runners, environments, audit/QC, analysis workflows and legacy support.
- `3_results`: 23,562 records classified into RP v3, RP v4, simulations, identity, composition, transcription, external validation, regulation, diagnostics and other historical results.
- `5_manuscript`: 273 records classified into current text, source Markdown, supplementary material, cover letters, author declarations, render QA and manuscript history.
- `6_release`: 783 records classified into current submission, candidate packages, GitHub/Zenodo, journal portal, integrity manifests and historical releases.
- `7_report`: 694 records classified into action records, advisor reviews, method audits, figure audits, release audits, project management and other reports.
- `8_archive`: 201 records classified into cache, recomputable QA, duplicate candidates, superseded versions, large archives and other archive candidates.
- `8_reference`: 10 records classified into primary literature, bibliography, dataset documentation, methods guidance and other references.
- `9_version`: 1 baseline record classified into version-state views; the new organized-layer inventories are separately indexed.

Categories with zero baseline rows were retained as explicitly labelled reserved locations. They are not evidence of missing data; they prevent future additions from returning to an unstructured root.

## Important navigation outputs

- `0_admin/SUBFOLDER_TAXONOMY_2026-10-12.md`: full cross-folder taxonomy.
- `9_version/inventory/SUBFOLDER_CLASSIFICATION_2026-10-12.csv`: one-row-per-file master classification for all 35,756 targeted records.
- `9_version/release_state/SUBFOLDER_ORGANIZATION_STATUS_2026-10-12.json`: machine-readable PASS decision and counts.
- `9_version/hashes_integrity/SUBFOLDER_ORGANIZATION_SHA256_2026-10-12.csv`: SHA-256 manifest for 141 generated taxonomy, index and catalog files.
- `6_release/current_submission/PACKAGE_CONTENTS_2026-10-12.csv`: SHA-256 inventory of the assembled package directory.
- `8_archive/duplicate_candidates/P3_CLEANUP_REVIEW_VIEW_2026-10-12.csv`: non-exclusive P3 review view; it is not deletion authorization.
- `audit_tools/project_subfolder_organization_20261012.py`: idempotent rebuild script.

## Scientific and release safeguards

- `4_figures` was not modified. Existing Fig1-Fig8 assignments and scientific artwork remain unchanged.
- The submission package passed its embedded verifier: 40/40 payload files matched.
- The package directory contains 41 files because its root README is intentionally outside the 40-file checksum payload set.
- No statistical model, count matrix, figure, manuscript claim, Source Data value, author statement, GitHub Release or Zenodo record was changed.
- No file in the P3 review view was deleted. Duplicate cleanup remains a separate, explicitly authorized operation.
- A Python absolute-path existence check can misreport paths longer than the legacy Windows path limit. PowerShell literal-path access and the baseline content audit confirm those long-path records remain present; no missing-file conclusion was drawn from the Python limitation.

## Valuable assets retained

1. The Stage K manuscript integration remains the current text baseline.
2. Figures 1-5 and Supplementary Figures S1-S10 retain their frozen claim ownership and boundary panels.
3. RP v3 and RP v4 outputs remain separately navigable, preventing the same 68-donor estimand from being mistaken for independent replication.
4. Stage G synthetic evidence, Stage I write-once result, Stage K limited integration and Stage M disease-blind raw-count protocol remain fully traceable.
5. The current submission package remains complete and internally verifiable, but not submitted.
6. Historical action records, advisor reviews and negative/HOLD decisions remain first-class project evidence rather than cleanup targets.

## Current scientific position

The stable manuscript conclusion remains reproducible process-level B_CONV IFN/ISG remodeling, bounded by permanent identity, transfer and mechanistic ceilings. RP v4 Stage I adds a qualified interval interpretation for the same 68-donor measurement-rule contrast; it is not an independent disease-effect replication. Stage L/M define a genuinely different external activity-by-compartment question, but external expression outcomes remain unopened.

## Decision

`PASS_NESTED_NON_DESTRUCTIVE_PROJECT_ORGANIZATION`

The project is now browsable at both the top-folder and topic-subfolder levels without compromising reproducibility. The organized folders are navigation views; frozen source paths remain authoritative.

## GitHub synchronization

The organization change was committed as `91b3843ca3d000252e78b0b2204cd3b28391e19f` with message `Organize project catalog subfolders` and pushed successfully from local `main` to `origin/main`. The push advanced the remote from `bdc5556e86164c15cdf3085610f3f6b8ef2b616d` to the organization commit.

## Next stage

The scientific next target remains `RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION`.

That stage should begin only after a qualified Linux x86-64 runtime, at least 2.5 TB scratch storage and explicit raw-download authorization are available. Until then, preserve the Stage K manuscript/package as the current bounded submission candidate and do not infer external disease or activity effects.

For project maintenance, the immediate rule is catalog-first: place new artifacts in the matching organized subfolder view, regenerate the master classification, and reopen scientific objects only for a real numerical, provenance, cross-reference, readability or new-data trigger.
