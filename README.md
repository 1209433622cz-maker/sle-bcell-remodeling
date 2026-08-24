# Disease-blind single-cell analysis of B-cell remodeling in SLE

This repository contains the auditable analysis and manuscript sources for a
raw-count, hierarchy-aware single-cell study of B-cell remodeling in systemic
lupus erythematosus (SLE).

Repository: [`1209433622cz-maker/sle-bcell-remodeling`](https://github.com/1209433622cz-maker/sle-bcell-remodeling).
Large public matrices and cell-level intermediates are accession- and
checksum-managed outside Git.

## Study status

The scientific analysis is frozen and the manuscript, supplementary information,
figures, source data and declarations have completed final author and technical
review. The citable archive is available at
[doi:10.5281/zenodo.22086892](https://doi.org/10.5281/zenodo.22086892).
The next operational step is journal-portal entry and submission receipt freeze.

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
- [Journal submission package](04_submission/journal_submission/)

Git history and the immutable public release preserve superseded submission
drafts. The stable filenames above are the only current author-facing entry
points. Submission filenames do not contain internal gate labels, build dates
or draft numbers.

## Licence and citation

Original repository code is MIT-licensed. Original manuscript text, composite figures, project documentation and project-generated derived source-data tables are CC BY 4.0. Public GEO/CELLxGENE data and other third-party material are excluded from these project licences; see `LICENSE_SCOPE.md`.

## Rebuild

Create or refresh the pinned document environment, then run the submission build:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\create_submission_environment.ps1

powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\build_submission_package.ps1 `
  -Doi "10.5281/zenodo.22086892"
```

The workflow rebuilds the author-approved sources, 170-mm figures, editable
DOCX files, required and optional portal maps, WPS review PDFs, page images,
accessibility reports, manifests and a deterministic local archive. Internal
audit identifiers remain inside the provenance layer and are not used in
journal-facing filenames.

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

Scientific analysis is closed. The next stage is journal operations: confirm
APC eligibility with the submission account or institutional library, enter the
final metadata and declarations into the Genome Medicine portal, upload the
required file set, compare every portal field and generated PDF against the
manuscript, and submit. New analyses should be opened only in response to a
decision-changing reviewer request.
