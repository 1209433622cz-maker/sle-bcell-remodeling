# Next-stage decision: complete Gate C2B1 before biological inference

## Decision

The project has a defensible v7 study design, a revised research proposal and a traceable design figure, but it is not ready for disease-effect estimation or submission. The immediate objective is to complete full per-library doublet scoring on all 150,402 hard-QC-eligible cells and conduct a documented review without automatically deleting predicted doublets.

## Why this gate is first

The Gate C2A representation smoke test supported moving to the full dataset, but its doublet rates cannot be frozen because balanced cell sampling occurred before Scrublet. State reconstruction, composition and pseudobulk results would all inherit that selection error if biological analyses proceeded now.

## Run now

From the project root in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1 `
  -ResumeRunDir ".\phase17_v7\gateC2B1\20260810_171000_full_library_doublets"
```

The runner reuses the validated 270,671,628-byte H5AD and checkpoints every completed library, so an interrupted run should be resumed in the same directory.

## Gate C2B1 review contract

Required outputs are `05_full_library_doublet_summary.csv`, `06_full_cell_doublet_scores.csv.gz`, paired per-library threshold checkpoints, diagnostic PNG/PDF files, `08_GATE_C2B1_DOUBLET_REVIEW.md` and `15_GATE_C2B1_RESIDUAL_DOUBLET_ASSESSMENT.md`. Review must reconcile the source demultiplexing/doublet workflow, execution success for all eligible libraries, score distributions and automatic thresholds, observed-versus-expected rates, extreme-library diagnostics, RNA content and mixed-lineage marker fractions.

No global rate cap or silent threshold override is permitted. The accepted analysis plan must carry both an all-hard-QC branch and a documented high-confidence-singlet sensitivity branch until conclusions are shown to be robust.

## Ordered work after approval

1. **Gate C2B2: full disease-blind representation.** Recompute library-aware recurrent HVGs/PCA, preserve an unintegrated reference, construct Harmony as a technical sensitivity representation, quantify bridge-sample concordance, audit B-lineage extraction completeness and rerun an ISG-excluded identity-stability sensitivity without using disease labels.
2. **Gate C2B3: neutral state freeze.** Select resolution using resampling stability, marker coherence and donor/sample/library coverage; review residual doublet localization; freeze neutral labels and marker rules before outcome unlock.
3. **Gate C3: composition.** Test sample-level state abundance within supported cohorts, with donor-aware uncertainty for repeated samples and explicit sensitivity to compositional modeling choices.
4. **Gate C4: within-state transcription.** Aggregate raw counts by sample and frozen state, test within-cohort disease effects, and separate abundance from state-internal transcription.
5. **Gate C5: frozen external validation.** Map GSE135779 without relabeling, estimate childhood and adult strata separately, report transfer uncertainty and validate only prespecified signatures supported by compatible metadata. A repeated-donor paired analysis follows as secondary evidence after the core results freeze.

## Publication threshold

- Current submission status: **NO-GO**.
- A rigorous replicated state/composition/transcription result supports a realistic Q1 translational-genomics target.
- Genome Medicine is the present best-fit target if v7 succeeds; Communications Biology is a defensible fallback.
- Nature Communications remains a stretch target and requires a clearly replicated, broadly important biological advance beyond a technically correct reanalysis.

## Next decision point

Do not choose a final journal or write definitive Results claims until Gate C2B3 freezes the cell-state model. The next advisor review is triggered by completion of the Gate C2B1 library summary and doublet diagnostics.
