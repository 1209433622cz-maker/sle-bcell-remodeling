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
journal package has been rebuilt and fully WPS-audited. A subsequent
label-agnostic analysis of all 363,083 GSE135779 matrix cells independently
recovered the external B-lineage compartment and retained the childhood
IFN/ISG direction under two frozen broad-state mappers. This result is a
supplementary robustness sensitivity and does not change the formal identity
HOLD. The existing citable
archive is available at [doi:10.5281/zenodo.22086892](https://doi.org/10.5281/zenodo.22086892);
its payload must be updated before journal submission.

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
- Label-agnostic GSE135779 selection recovered 98.7% of post hoc source-labeled
  B cells with 3.3% non-B contamination. Elastic-net and nearest-centroid
  mappings retained positive childhood IFN/ISG effects (0.306 and 0.304;
  q=0.00235 and q=0.00212), with no leave-one-donor reversal.
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
- [Label-agnostic GSE135779 review](phase17_v7/gateC9/20260828_gse135779_label_agnostic_validation/28_GATE_C9_ADVISOR_REVIEW.md)

Git history and the immutable public release preserve superseded submission
drafts. The stable filenames above are the only current author-facing entry
points. The generated `04_submission/journal_submission/` directory is
reproducible; Git tracks its reader-facing README, manifests, portal maps and
11-file REQUIRED upload set, while internal renders and duplicate working assets
remain ignored. Markdown, scripts and machine-readable analysis outputs remain
the authoritative sources. The current local package passed WPS, accessibility,
portal-map and deterministic-ZIP audits but has not been submitted.

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
  -File .\audit_tools\run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1
```

The runner freezes selection, mapper calibration and program scores before it
permits source-label or outcome-field parsing and joins. The recomputable per-cell
prediction table remains outside Git.

## Repository layout

- `00_project_management/`: advisor audits, action records and formal decisions.
- `01_manuscript/`: current canonical manuscript, supplement and proposal sources.
- `02_analysis/`: environments, acquisition scripts, inventories and runbooks.
- `03_results/`: the retained Phase 17 study-design figure bundle.
- `audit_tools/`: executable analysis, build and audit scripts.
- The analysis run tree contains machine-readable audit outputs and publication figures.
- `04_submission/`: current portal guide, author records and journal-facing package.
- `Data/`: a tracked retrieval guide plus ignored, disposable public-data caches.

## Research proposal

The active completed RP is [Research_Proposal.md](01_manuscript/Research_Proposal.md).
Earlier proposal files remain recoverable from Git history and the project
action records. The current manuscript is more specific where completed
analyses require it, but it does not overwrite the proposal history.

## Next stage

Integrate the completed Gate C9 result as a supplementary robustness analysis,
not as a replacement primary analysis. Add one concise Methods subsection, one
bounded Results paragraph, a supplementary figure with source data and the
explicit 15.1% contamination limitation of the per-cell margin sensitivity.
Then rebuild the manuscript and submission package, repeat WPS/PDF/adversarial
audits, publish an updated Zenodo version and proceed to the journal portal. No
new exploratory dataset or identity-threshold repair is justified before
submission, and the formal R1 HOLD must remain unchanged.
