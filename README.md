# Disease-blind single-cell analysis of B-cell remodeling in SLE

This repository contains the auditable analysis and manuscript sources for a
raw-count, hierarchy-aware single-cell study of B-cell remodeling in systemic
lupus erythematosus (SLE).

Repository: [`1209433622cz-maker/sle-bcell-remodeling`](https://github.com/1209433622cz-maker/sle-bcell-remodeling).
Large public matrices and cell-level intermediates are accession- and
checksum-managed outside Git.

## Study status

The primary scientific families remain frozen. A declared post-freeze Round 6
robustness cycle is in progress before journal submission: STAT1/STAT2
IFN-overlap depletion is complete, while the 150,402-cell end-to-end
disease-blind identity resampling run is ready for local execution. The formal
journal package is therefore on hold and must not be uploaded until that run is
reviewed and the documents are rebuilt. The existing citable archive is available at
[doi:10.5281/zenodo.22086892](https://doi.org/10.5281/zenodo.22086892).

Working title:

**Disease-blind single-cell reconstruction separates unstable B-cell states
from reproducible interferon remodeling in systemic lupus erythematosus**

The frozen evidence chain is:

- 150,402 quality-controlled GSE174188 B-lineage cells, 259 donors, 271 samples
  and 88 libraries.
- Disease-blind identity supports broad conventional-B (`B_CONV`) and
  antibody-secreting-cell (`B_ASC`) compartments, not stable hard
  naive-memory outcome subtypes.
- Primary B_ASC relative abundance is null: odds ratio 0.947, 95% CI
  0.636-1.410, P=0.787.
- The frozen IFN/ISG program replicates in GSE174188 discovery, a
  donor-nonoverlap internal contrast and independent GSE135779 childhood donors.
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

Git history and the immutable public release preserve superseded submission
drafts. The stable filenames above are the only current author-facing entry
points. The generated `04_submission/journal_submission/` directory is not an
authoritative source and remains withheld while Round 6 R1 is pending.

## Licence and citation

Original repository code is MIT-licensed. Original manuscript text, composite figures, project documentation and project-generated derived source-data tables are CC BY 4.0. Public GEO/CELLxGENE data and other third-party material are excluded from these project licences; see `LICENSE_SCOPE.md`.

## Pending full run

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
replicates.

## Repository layout

- `00_project_management/`: advisor audits, action records and formal decisions.
- `01_manuscript/`: current manuscript sources and historical drafting provenance.
- `02_analysis/`: environments, acquisition scripts, inventories and runbooks.
- `03_results/`: retained result bundles and earlier figure provenance.
- `audit_tools/`: executable analysis, build and audit scripts.
- The analysis run tree contains machine-readable audit outputs and publication figures.
- `04_submission/`: current portal guide, author records and journal-facing package.

## Research proposal

The active completed RP is [Research_Proposal.md](01_manuscript/Research_Proposal.md).
Earlier proposal files remain as pre-outcome methodological provenance. The
current manuscript is more specific where completed analyses require it, but it
does not overwrite the proposal history.

## Next stage

Complete and independently audit the full R1 run. If it passes, add the
end-to-end identity result as a supplementary robustness figure; if it holds,
retain the frozen-embedding result and narrow the identity claim explicitly.
Then rebuild the DOCX and portal package, render every page with WPS, rerun
accessibility and deterministic-manifest audits, update the archival release,
and only then begin journal-portal submission.
