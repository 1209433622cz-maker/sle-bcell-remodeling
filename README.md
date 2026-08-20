# SLE B-cell remodeling study

This repository contains the auditable analysis and manuscript sources for a
raw-count, hierarchy-aware single-cell study of B-cell remodeling in systemic
lupus erythematosus (SLE).

Repository: [`1209433622cz-maker/sle-bcell-remodeling`](https://github.com/1209433622cz-maker/sle-bcell-remodeling).
Large public matrices and cell-level intermediates are accession- and
checksum-managed outside Git.

## Current status

Gate C8S is the active freeze. The scientific analysis, main and supplementary
figures, statistical traceability, references and WPS-rendered documents are
complete. Portal submission remains blocked only by author-controlled
declarations, institutional confirmation, repository licensing and an immutable
archive DOI.

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

- Manuscript source: `01_manuscript/manuscript_v12_genome_medicine_gateC8S_2026-08-21.md`
- Supplement source: `01_manuscript/supplementary_information_v3_gateC8S_2026-08-21.md`
- Five main figures, seven supplementary figures and source data:
  `phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/`
- Full statistical-results archive: 12 complete gene-level branches and 12
  sanitized design matrices, with deterministic SHA-256 verification.
- Final audit: `phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/08_GATE_C8S_FINAL_AUDIT.md`
- Local submission handoff: `04_submission/package_genome_medicine_gateC8S_2026-08-21/`
- Deterministic local archive: `04_submission/package_genome_medicine_gateC8S_2026-08-21.zip`

The `04_submission/` handoff is intentionally excluded from Git because it
contains generated upload files and WPS page-review artifacts. Its SHA-256
manifest and package status are recorded in the tracked Gate C8S output.

## Rebuild

From the repository root on the tested Windows workstation:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8S_submission_package.ps1
```

The runner rebuilds five main figures, seven supplementary figures, the full
statistical archive, manuscript sources, editable DOCX files, WPS PDFs, every
page PNG, accessibility reports, integrity manifests and the deterministic
submission archive. The Gate C8R correlation-aware sensitivity and reference
verification are reused as frozen inputs.

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

Gate C8B is author-controlled completion: ethics determination, competing
interests, funding, CRediT contributions, acknowledgements, all-author approval
and originality confirmation, repository licence, and an immutable Zenodo or
equivalent DOI. After these are supplied, rebuild once and perform the final
portal preflight without changing frozen scientific results.
