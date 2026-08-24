# SLE B-cell remodeling study

This repository contains the auditable analysis and manuscript sources for a
raw-count, hierarchy-aware single-cell study of B-cell remodeling in systemic
lupus erythematosus (SLE).

Repository: [`1209433622cz-maker/sle-bcell-remodeling`](https://github.com/1209433622cz-maker/sle-bcell-remodeling).
Large public matrices and cell-level intermediates are accession- and
checksum-managed outside Git.

## Current status

Gate C8S remains the canonical scientific freeze. Gate C8BRP is the active
journal-facing prefreeze: release portability, reader-facing manuscript and
Supplementary Information, exact identity-resampling reporting, visual-only
Figure 1/4 refinements, Figure 5 evidence semantics, current literature,
reference verification, clean portal filename aliases and WPS-rendered
documents are complete without changing scientific estimates. Portal
submission remains blocked by author-controlled declarations, institutional
confirmation, repository licensing and an immutable archive DOI.

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

- Manuscript source: `01_manuscript/manuscript_v15_genome_medicine_journal_facing_prefreeze_2026-08-25.md`
- Supplement source: `01_manuscript/supplementary_information_v6_journal_facing_2026-08-25.md`
- Five main figures, seven supplementary figures and source data:
  `phase17_v7/gateC8BRP/20260825_journal_facing_prefreeze/` and the frozen
  Gate C8S supplementary-figure source.
- Full statistical-results archive: 12 complete gene-level branches and 12
  sanitized design matrices, with deterministic SHA-256 verification.
- Final audit: `phase17_v7/gateC8BRP/20260825_journal_facing_prefreeze/05_GATE_C8BRP_FINAL_AUDIT.md`
- Local submission handoff: `04_submission/package_genome_medicine_gateC8BRP_journal_facing_prefreeze_2026-08-25/`
- Deterministic local archive: `04_submission/package_genome_medicine_gateC8BRP_journal_facing_prefreeze_2026-08-25.zip`

Generated `04_submission/` binaries, upload packages and WPS page-review
artifacts are intentionally excluded from Git. Four small Gate C8BRP Markdown
sources (cover letter, author matrix, target decision and reporting checklist)
are tracked explicitly so a fresh clone can rebuild the active package. Its
SHA-256 manifest and package status are recorded in the tracked Gate C8BRP
output.

## Rebuild

Create or refresh the pinned release environment from the repository root:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\00_create_gateC8BR_release_env.ps1
```

Then run the full Windows/WPS preflight:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8BRP_journal_facing_prefreeze.ps1
```

The runner discovers Python through an explicit argument, environment variable,
named conda environment, repository-local environment or `PATH`. It qualifies
imports and PNG/PDF/DOCX output, rerenders Figures 1, 4 and 5 from frozen data,
carries forward byte-identical Figures 2 and 3 and frozen Gate C8S
supplementary/statistical assets, verifies 28 DOI records and 32 references,
rebuilds manuscript sources and editable DOCX files, generates 18 hash-mapped
portal aliases, renders WPS PDFs and all page PNGs, runs accessibility checks,
and creates integrity manifests plus a deterministic submission archive.
`-Mode PortableCore` builds the portable source/DOCX layer when WPS or
`pdftoppm` is unavailable; a later `-Mode Full` run remains required before
submission.

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

Gate C8BRP now moves to author-controlled completion: ethics determination,
competing interests, funding, CRediT contributions, acknowledgements,
all-author approval and originality confirmation, correspondence-address
approval, repository licence, and an immutable Zenodo or equivalent DOI. After
these are supplied, replace every placeholder, rebuild once, and perform the
zero-placeholder WPS and portal preflight without reopening frozen scientific
analysis.
