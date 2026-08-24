# SLE B-cell remodeling study

This repository contains the auditable analysis and manuscript sources for a
raw-count, hierarchy-aware single-cell study of B-cell remodeling in systemic
lupus erythematosus (SLE).

Repository: [`1209433622cz-maker/sle-bcell-remodeling`](https://github.com/1209433622cz-maker/sle-bcell-remodeling).
Large public matrices and cell-level intermediates are accession- and
checksum-managed outside Git.

## Current status

Gate C8S remains the canonical scientific freeze. Gate C8BRF is the author-approved release state: all declarations are complete, the five main figures are rendered at 170 mm, Figure 1 publication Source Data is sanitized through its builder, Figure 2 public UUID governance has passed, and the release is citable under doi:10.5281/zenodo.22086892. Scientific estimates remain unchanged.

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

## Active deliverables

- Manuscript source: `01_manuscript/manuscript_v16_genome_medicine_final_2026-08-25.md`
- Supplement source: `01_manuscript/supplementary_information_v7_final_2026-08-25.md`
- Final main figures and Source Data: `phase17_v7/gateC8BRF/20260825_author_release/`
- Canonical scientific freeze and supplementary figures: `phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/`
- Final local submission package: `04_submission/package_genome_medicine_gateC8BRF_author_release_2026-08-25/`
- Deterministic local archive: `04_submission/package_genome_medicine_gateC8BRF_author_release_2026-08-25.zip`
- Release tag: `v1.0.0`
- DOI: `https://doi.org/10.5281/zenodo.22086892`

Generated package binaries and WPS page-review artifacts remain excluded from Git; tracked status, provenance and audit records are sufficient to reconstruct and verify them.

## Licence and citation

Original repository code is MIT-licensed. Original manuscript text, composite figures, project documentation and project-generated derived source-data tables are CC BY 4.0. Public GEO/CELLxGENE data and other third-party material are excluded from these project licences; see `LICENSE_SCOPE.md`.

## Rebuild

Create or refresh the pinned release environment, then run the final workflow:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\00_create_gateC8BR_release_env.ps1

powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8BRF_author_release.ps1 `
  -Doi "10.5281/zenodo.22086892"
```

The workflow rebuilds the author-approved sources, 170-mm figures, editable DOCX files, REQUIRED/OPTIONAL portal maps, WPS review PDFs, all page PNGs, accessibility reports, manifests and the canonical deterministic ZIP.

## Repository layout

- `00_project_management/`: advisor audits, action records and gate decisions.
- `01_manuscript/`: research proposal, manuscript and supplement sources.
- `02_analysis/`: environments, acquisition scripts, inventories and runbooks.
- `03_results/`: retained result bundles and earlier figure provenance.
- `audit_tools/`: executable analysis, build and audit scripts.
- `phase17_v7/`: compact machine-readable gate outputs and publication figures.
- `04_submission/`: generated local submission package, excluded from Git.

## Research proposal

The active completed RP is
`01_manuscript/research_proposal_v16_gateC7_completed_2026-08-20.md`. The earlier
`research_proposal_v14_methodologically_revised_2026-08-10.md` and its DOCX/PDF
renderings remain the pre-outcome methodological provenance. Later manuscripts
supersede both RP versions only where frozen analyses and reporting details are
more specific; they do not overwrite the RP history.

## Next gate

Scientific analysis is closed. The next stage is journal operations: confirm APC eligibility with the submission account or institutional library, enter the final metadata and declarations into the Genome Medicine portal, upload only the REQUIRED file map by default, compare every portal field against the final manuscript, and submit. New analyses should be opened only in response to a decision-changing reviewer request.
