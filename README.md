# Disease-blind single-cell analysis of B-cell remodeling in SLE

This repository contains the auditable analysis and manuscript sources for a
raw-count, hierarchy-aware single-cell study of B-cell remodeling in systemic
lupus erythematosus (SLE).

Repository: [`1209433622cz-maker/sle-bcell-remodeling`](https://github.com/1209433622cz-maker/sle-bcell-remodeling).
Large public matrices and cell-level intermediates are accession- and
checksum-managed outside Git.

## Study status

The primary scientific families remain frozen. The declared post-freeze Round 6
robustness cycle is complete. Twenty end-to-end disease-blind reconstruction
replicates retained high global concordance but missed the unchanged B_ASC
state-overlap criterion; the formal result is HOLD, and B_CONV/B_ASC is now
framed as an analysis scaffold rather than a universally reproducible taxonomy.
Propagating every observed broad-state boundary exchange retained the primary
composition null and both tested GSE174188 B_CONV IFN/ISG effects. The local
journal package is an earlier WPS-audited snapshot, not a submission-ready release.
A post-freeze code audit invalidated the subsequent C9 PASS: reference and external
normalization differed, and failed confidence calibration incorrectly authorized
outcome access. The corrected full run processed all 363,083 cells but stopped
at calibration HOLD (B_ASC precision 0.885 < 0.90). No corrected external disease
outcomes were opened. Source-label-defined primary GSE135779 replication is
retained; source-label-independent robustness is not established. See the
[correction contract](00_project_management/gateC9_technical_correction_contract_2026-08-28.md).
The existing citable
archive is available at [doi:10.5281/zenodo.22086892](https://doi.org/10.5281/zenodo.22086892);
a matching new archive version is required before journal submission; the initial
snapshot remains historical.

Working title:

**Disease-blind single-cell reconstruction separates unstable B-cell state assignments
from reproducible interferon remodeling in systemic lupus erythematosus**

The frozen evidence chain is:

- 150,402 quality-controlled GSE174188 B-lineage cells, 259 donors, 271 samples
  and 88 libraries.
- Frozen-representation resampling supports a broad conventional-B (`B_CONV`)
  and antibody-secreting-cell (`B_ASC`) analysis partition, not stable hard
  naive-memory outcome subtypes. End-to-end resampling formally holds because
  B_ASC median Jaccard is 0.930, below the unchanged 0.95 criterion.
- Boundary propagation retains the primary B_ASC null across all 20 replicates
  and retains positive primary and donor-nonoverlap B_CONV IFN/ISG effects.
- Primary B_ASC relative abundance is null: odds ratio 0.947, 95% CI
  0.636-1.410, P=0.787.
- The frozen IFN/ISG program replicates in GSE174188 discovery, a
  donor-nonoverlap internal contrast and independent GSE135779 childhood donors.
- Corrected reference-calibrated, source-label-agnostic mapping is on HOLD:
  elastic-net B_ASC precision missed the frozen 0.90 criterion. Original C9
  effects are superseded audit records, not supporting publication evidence.
- Genome-wide cross-dataset agreement is low (Spearman rho=0.026); the claim is
  program-specific replication, not a globally shared disease transcriptome.
- Frozen STAT1/STAT2 ULM results are supported by a correlation-aware
  sensitivity: CAMERA is positive in 6/6 tests and BH-significant in 5/6; FRY
  is positive and BH-significant in 6/6. Discovery STAT2 is the explicit CAMERA
  exception (q=0.1355).
- All 36 method-level directions remained positive after removal of either the
  frozen 12-gene IFN/ISG arm or M5911 genes. The narrow depletion retained
  broad support, whereas M5911 depletion materially attenuated discovery
  STAT2; the result does not support overlap-independent regulation.
- M5911 enrichment and paired GSE23307 IFN-beta response provide orthogonal
  response evidence; neither establishes causality, direct TF binding or a
  unique upstream ligand.

## Current manuscript and submission files

- [Manuscript source](01_manuscript/Manuscript.md)
- [Supplementary information source](01_manuscript/Supplementary_Information.md)
- [Research proposal](01_manuscript/Research_Proposal.md)
- [Cover letter source](04_submission/Cover_Letter.md)
- [Author confirmation](04_submission/Author_Confirmation.md)
- [Reporting checklist](04_submission/Reporting_Checklist.md)
- [Portal upload guide](04_submission/Portal_Upload_Guide.md)
- [Round 6 execution contract](00_project_management/round6_q1_robustness_execution_contract_2026-08-25.md)
- [Full-run handoff](00_project_management/round6_full_pipeline_resampling_handoff_2026-08-25.md)
- [R1 HOLD integration review](phase17_v7/round6_q1_robustness/20260827_r1_hold_integration/14_ROUND6_R1_HOLD_ADVISOR_REVIEW.md)
- [Corrected mapping calibration review](phase17_v7/gateC9R/20260828_normalization_correction/16_GATE_C9A_PREFREEZE_REVIEW.md)
- [Correction review and synchronization record](00_project_management/action_record_2026-08-28_correction_release_reconciliation.md)
- [Current external-review response and author gate](00_project_management/action_record_2026-08-28_external_review_author_gate.md)
- [Author confirmation and next-stage preparation](00_project_management/action_record_2026-08-28_author_confirmation_and_journal_preparation.md)
- [Current author confirmation](04_submission/Author_Confirmation.md)
- [External methods-review dossier](00_project_management/author_confirmation_2026-08-28/External_Methods_Review.md)
- [Journal fit and formatting assessment](00_project_management/external_review_2026-08-28/Journal_Fit_and_Format_Assessment.md)
- [JCR Q1 criterion and next-format draft](00_project_management/author_confirmation_2026-08-28/Journal_Format_Draft.md)
- [Integrated Figure 1 correction record](00_project_management/jcr_q1_refreeze_2026-08-28/Figure_1_Legend_Correction.md)
- [Current candidate figure and source-data manifest](phase17_v7/post_gateC9/20260828_corrected_candidate/02_REVIEW_FIGURE_MANIFEST.csv)
- [Corrected candidate and JCR Q1 action record](00_project_management/action_record_2026-08-28_jcr_q1_corrected_candidate.md)
- [JCR evidence and journal decision](00_project_management/jcr_q1_refreeze_2026-08-28/Journal_Decision.md)

Git history and the immutable public release preserve superseded submission
drafts. The stable filenames above are the only current author-facing entry
points. The historical `04_submission/journal_submission/` directory is preserved;
Git tracks its reader-facing README, manifests, portal maps and
11-file REQUIRED upload set, while internal renders and duplicate working assets
remain ignored. Markdown, scripts and machine-readable analysis outputs remain
the authoritative sources. That historical package predates the correction and
must not be submitted unchanged. Historical PASS labels do not override this status.

The preserved local `04_submission/author_confirmed_review.zip` contains the prior four
review documents, five main and ten supplementary figures, and reconciled
statistical attachments. It passed WPS, accessibility, manifest and deterministic
packaging checks and records both authors' confirmation as reported by the user.
The manuscript and cover letter were also explicitly approved. Approval is bound
to identified source hashes and the preserved `author_review.zip`, not arbitrary
later edits. Current and historical decisions are separated. External reviewer
identity remains unverified, and the package is not authorized for submission.
Both earlier review ZIPs are preserved.
A Figure 1c threshold-label error was subsequently identified: 0.990 is the
mapping-agreement criterion, not the ARI criterion. The current local
`04_submission/corrected_candidate.zip` integrates a source-driven Figure 1
redraw and corrected legend, fixes interpretation-box spacing in panel a, and
qualifies the single-source-label omission claim. Its four documents are rebuilt
from the current sources. All scientific source data and statistical attachments
remain unchanged. The prior approval is preserved; candidate approval is pending.
The manuscript and cover-letter source links above now identify this candidate,
not the older author-confirmed snapshot. No new release or submission is authorized.
Generated review packages are not tracked in Git; the linked action record gives
the exact package hash, verification scope and next-stage requirements.

## Licence and citation

Original repository code is MIT-licensed. Original manuscript text, composite figures, project documentation and project-generated derived source-data tables are CC BY 4.0. Public GEO/CELLxGENE data and other third-party material are excluded from these project licences; see `LICENSE_SCOPE.md`.

## Reproduce the end-to-end robustness cycle

Run the resumable end-to-end identity analysis from the project root:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_round6_full_pipeline_identity_resampling.ps1 `
  -OutputDir .\phase17_v7\round6_q1_robustness\20260825_full_pipeline_identity_resampling `
  -Replicates 20 `
  -ResampleFraction 0.8 `
  -MaxCells 0 `
  -HarmonyMaxIter 50
```

The exact inputs, hashes, checkpoints, monitoring command and decision rules are
documented in the full-run handoff. Rerunning the same command resumes completed
replicates. Audit the HOLD and rebuild its downstream propagation with:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_round6_r1_hold_integration.ps1
```

Run the protected two-stage GSE135779 label-agnostic sensitivity with:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1 `
  -PostUnblindingCorrection
```

The runner freezes selection, mapper calibration and program scores before it
permits source-label or outcome-field parsing and joins. The recomputable per-cell
prediction table remains outside Git. Use a new `-OutputDir` for a repeat run;
nonempty runs are protected. A calibration HOLD returns nonzero and deliberately
prevents outcome access; it is not an instruction to relax the threshold.

## Repository layout

- `00_project_management/`: advisor audits, action records and formal decisions.
- `01_manuscript/`: current canonical manuscript, supplement and proposal sources.
- `02_analysis/`: environments, acquisition scripts, inventories and runbooks.
- `03_results/`: the retained Phase 17 study-design figure bundle.
- `audit_tools/`: executable analysis, build and audit scripts.
- The analysis run tree contains machine-readable audit outputs and publication figures.
- `04_submission/`: current review guide, author records and a preserved historical package.
- `Data/`: a tracked retrieval guide plus ignored, disposable public-data caches.

## Research proposal

The active completed RP is [Research_Proposal.md](01_manuscript/Research_Proposal.md).
Earlier proposal files remain recoverable from Git history and the project
action records. The current manuscript is more specific where completed
analyses require it, but it does not overwrite the proposal history.

## Next stage

The corrected limitation is integrated into the manuscript, supplement and RP.
The separate correction-review bundle adds the full calibration family and S10,
with portable hash checks. It is not authorized for submission. Historical
one-click release writers are retired to protect the revised sources and old
package. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for current entry points.

Current-content confirmation, explicit manuscript/cover-letter approval and
author consideration of external feedback are recorded. The user requires JCR
Q1. Next, verify candidate-specific JCR year/category evidence, select a journal, prepare
its final format and reconcile the corresponding archive. Further independent
methods review can address the remaining authentication gap; no journal-mandated
signed pre-submission certificate is assumed. Do not
tune C9 thresholds or substitute the centroid mapper to obtain a PASS. R1 HOLD
and source-label dependence remain explicit. No new DOI or journal submission
is implied by a GitHub code correction.
