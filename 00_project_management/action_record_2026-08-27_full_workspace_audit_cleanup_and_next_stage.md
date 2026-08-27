# Full workspace audit, cleanup and next-stage decision

**Date:** 2026-08-27

**Workspace:** `H:\cuhk-2025fALL\6013RP-wyf`

**Scope:** complete file inventory, size/content integrity audit, duplicate review,
working-tree minimization, submission-package revalidation and scientific
next-stage decision.

## 1. Executive decision

The workspace is now a compact, auditable project rather than an accumulation
of exploratory analyses and submission builds. The canonical manuscript,
supplement, research proposal, project records, executable methods, compact
frozen results, two formal Phase 17 H5AD inputs, literature set and complete
journal package were retained. Superseded drafts remain recoverable from Git
history.

The scientific freeze remains unchanged. The end-to-end identity result is a
formal HOLD because B_ASC median Jaccard is 0.930, below the unchanged 0.95
criterion. Boundary propagation retains the primary composition null and the
tested B_CONV IFN/ISG effects. No threshold, seed, label or estimate was altered
during cleanup.

The highest-value next scientific action is a label-agnostic GSE135779 mapping
sensitivity. It must be completed before a new Zenodo version or journal upload.

## 2. Audit scope and machine-readable records

The audit covered every file outside `.git`. The following records are retained
under `00_project_management/workspace_audit_2026-08-27/`:

- `full_file_inventory_before_cleanup.csv`: all 4,790 pre-clean files.
- `full_file_inventory_after_cleanup.csv`: the post-clean inventory.
- `cleanup_action_manifest.csv`: file-level action, category, reason and final
  existence state.
- `duplicate_content_groups_le_300mb.csv`: pre-clean SHA-256 duplicate groups.
- `duplicate_content_groups_after_cleanup.csv`: retained duplicate groups.
- `h5ad_integrity_after_cleanup.json`: H5AD dimensions and structural checks.
- `zip_integrity_after_cleanup.json`: entry counts and CRC checks for every ZIP.
- `retained_content_integrity_summary.json`: extension-aware content audit.
- `retained_content_issues.csv`: empty because no retained integrity issue was
  found.
- `canonical_markdown_link_audit.json`: 11/11 local links resolved.

## 3. Before-and-after size accounting

All values below exclude `.git` so the comparison is like-for-like.

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Files | 4,790 | 1,379 | -3,411 |
| Directories | 735 at initial scan | 166 | substantially reduced |
| Bytes | 23.714 GiB | 0.642 GiB | -23.072 GiB |

The final 689,319,876-byte working content is concentrated in assets with a
defined role:

| Area | Files | Size |
|---|---:|---:|
| `phase17_v7` | 768 | 437.07 MB |
| `04_submission` | 193 | 117.66 MB |
| `PAPER` | 9 | 53.10 MB |
| `Data` | 6 | 41.44 MB |
| `00_project_management` | 121 | 4.84 MB |
| `audit_tools` | 172 | 1.97 MB |
| `02_analysis` | 84 | 0.58 MB |
| `03_results` | 8 | 0.57 MB |
| `01_manuscript` | 6 | 0.11 MB |

## 4. Deleted or relocated content

### 4.1 Deleted as superseded or reproducible

- 2.43 GB of pre-Phase-17 exploratory results, including duplicate first-pass
  H5AD objects and obsolete figures/tables.
- Approximately 1.00 GB of historical submission packages, duplicate ZIPs,
  render workspaces and superseded quality-control copies.
- Approximately 0.93 GB of Phase 17 test H5ADs, software-test runs, pseudobulk
  checkpoints, matrix exports, per-cell assignments and visual-QA caches.
- The 192.40 MB extracted review pack and its duplicated payload.
- Python bytecode caches and the root duplicate of `science.abf1970.pdf`.
- 65 superseded manuscript/proposal/draft files. Their complete history remains
  in Git and their substantive decisions remain in project action records.

### 4.2 Public data cache policy

The ignored `Data/` parent was cleaned as a unit. This removed all resident
public source caches, including the 12.2 GB GSE174188 CELLxGENE H5AD, the 4.4 GB
OneK1K H5AD, GSE135779 RAW/derived files, GSE163121, unused regulatory files and
small SRA supplements. These were public, redownloadable resources; no private
or irreplaceable patient data were present.

This broader parent-level removal is explicitly recorded rather than hidden.
The five required GSE135779 metadata/source-index files were immediately
restored from their authoritative locations and exact byte counts verified.
`Data/README.md` now documents restoration commands. The 1.30 GB GSE135779 RAW
archive remains intentionally absent pending the next local-compute run.

### 4.3 Relocated rather than deleted

- Six tracked historical H5AD audit records were moved from
  `_phase17_h5ad_audit/` to
  `00_project_management/historical_audits/phase17_h5ad_audit_2026-08-06/`.
- Four non-project course/administrative files were moved intact to
  `H:\cuhk-2025fALL\6013RP_nonproject_archive_2026-08-27\99_admin_course_docs`.
- Existing cleanup manifests, action reports and formal gate decisions were
  retained as project provenance.

## 5. Critical retained assets

### 5.1 Formal analysis inputs

| Asset | Shape | Bytes | SHA-256 | Result |
|---|---:|---:|---|---|
| Gate C2B1 raw counts | 150,402 x 30,172 | 270,671,628 | `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5` | exact match |
| Gate C2B2 primary representation | 150,402 x 3,000 | 114,432,893 | `594A040FC483973B38B744D5D0E526633D7F1C91F2544D34C28D35F2084E3AFB` | exact match |

The representation retains `X_pca`, `X_pca_harmony`, `X_umap_harmony` and
`X_umap_unintegrated`. Both H5AD files open successfully in backed mode.

### 5.2 Statistical and submission archives

| Asset | Bytes | SHA-256 | Result |
|---|---:|---|---|
| Frozen Gate C8S statistical ZIP | 8,314,122 | `AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5` | 63 entries, CRC PASS |
| Current journal package ZIP | 58,515,354 | `63446D18B55A856B016C377A8EF4E7BBDAC1B713C0E56B27E6F0ACE505EE22BB` | 186 entries, CRC PASS |

The current author-facing manuscript directory now contains only:

- `Manuscript.md`
- `Supplementary_Information.md`
- `Research_Proposal.md`
- `references_verified_crossref_2026-07-09.bib`
- `citation_signature_audit_v1.md`
- `README.md`

## 6. Full retained-content integrity results

The final extension-aware audit examined all 1,379 retained files:

| Type | Files checked | Result |
|---|---:|---|
| UTF-8 text/code/Markdown | 466 | PASS |
| JSON | 170 | PASS |
| CSV | 455 | PASS |
| PDF | 105 | PASS |
| PNG | 141 | PASS |
| DOCX | 12 | PASS |
| ZIP | 13 | PASS |
| H5AD | 2 | PASS |

No retained content issue was detected. Both edited PowerShell download scripts
also pass the PowerShell parser with zero syntax errors.

The formal Gate C8BRF package audit was rerun after cleanup and passed:

- decision: `PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`;
- WPS pages: 32 main, 17 supplement and 1 cover-letter page;
- accessibility findings: 0 high, 0 medium and 0 low;
- portal files: 11 required and 9 optional;
- main figures: 5/5 vector PDFs at 170 mm width;
- supplementary assertions: legacy 29/29 plus verified S8 and S9 contracts;
- full statistical archive: 163 manifest rows and 101 identity-robustness files;
- final deterministic ZIP hash unchanged.

## 7. Duplicate-content decision

The pre-clean audit found 822 duplicate groups and 646.04 MB of duplicated
physical content among files no larger than 300 MB. After cleanup, 149 groups
and 63.57 MB remain.

The largest retained duplicate is the 10.31 MB statistical archive copied into
both `additional_files` and `portal_upload_required`. Other retained duplicates
are portal aliases, source-data copies, WPS/package assets and the same
publication figure retained at a gate freeze and in the current package. These
duplicates are intentional interface or provenance copies; deleting them would
break package maps, manifests or gate traceability.

## 8. Scientific status after audit

### 8.1 Strongest supported conclusions

1. The study contains 150,402 quality-controlled GSE174188 B-lineage cells from
   259 donors, 271 samples and 88 libraries.
2. Fine B-cell labels do not meet the predeclared joint stability criteria. A
   broad B_CONV/B_ASC scaffold is permissible for analysis, but it is not a
   universally reproducible taxonomy.
3. End-to-end 20-replicate reconstruction is a formal HOLD because B_ASC median
   Jaccard is 0.930 rather than at least 0.95.
4. Primary B_ASC relative abundance is null: OR 0.947, 95% CI 0.636-1.410,
   P=0.787.
5. Boundary propagation retains the primary composition null and positive
   primary/donor-nonoverlap B_CONV IFN/ISG effects in every replicate.
6. The frozen IFN/ISG program replicates in discovery, donor-nonoverlap internal
   validation and independent GSE135779 childhood donors.
7. Genome-wide cross-dataset concordance is low (Spearman rho=0.026), so the
   defensible claim is program-specific replication rather than a shared global
   disease transcriptome.
8. STAT1/STAT2 evidence is correlation-aware and directionally strong but not
   causal. The M5911 depletion result prevents an overlap-independent upstream
   regulation claim.

### 8.2 Remaining scientific vulnerability

The independent GSE135779 result currently depends on source-provided
`subclusters` to identify B cells. That does not invalidate the reported
program-level replication, but it leaves an upper-Q1 reviewer an obvious
question: does the result survive when external B-cell selection and broad-state
mapping are learned without those labels?

## 9. Next-stage decision

Proceed to the separately frozen
`next_stage_gse135779_label_agnostic_mapping_contract_2026-08-27.md`.

Immediate local-compute prerequisite:

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"

powershell -ExecutionPolicy Bypass `
  -File .\02_analysis\scripts\00_download_gse135779_validation_sources.ps1 `
  -DownloadRaw
```

The downloader is resumable and expects exactly 1,299,783,680 bytes for
`GSE135779_RAW.tar`. Do not update the manuscript, figures, Zenodo record or
journal package until the label-agnostic contract has been executed and
reviewed. If the external sensitivity passes, add it as a supplementary
robustness result; if it fails, preserve the failure and narrow the external
claim. Either outcome is scientifically preferable to post hoc threshold
adjustment.

## 10. Final audit conclusion

The cleanup is complete and did not change any frozen estimate or journal-facing
package byte. The workspace is materially easier to understand and reproduce.
Its only intentional near-term data gap is the public GSE135779 RAW archive
required for the next label-agnostic external validation.
