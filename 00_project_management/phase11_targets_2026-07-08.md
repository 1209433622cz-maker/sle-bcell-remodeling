# Phase 11 Targets - 2026-07-08

## Status After GSE135779 Validation

The upper-Q1 strengthening route now has a successful independent validation layer.

Completed:

- Downloaded `GSE135779_RAW.tar` (1,299,783,680 bytes).
- Inspected RAW tar structure: 56 sample-level barcode/matrix pairs.
- Built and ran `30_run_gse135779_bcell_validation.py`.
- Matched 32,179 metadata-defined B-subcluster cells to raw processed matrices.
- Retained 56 donor/sample names: 16 healthy controls and 40 SLE donors.
- Generated donor-level program scores, statistical tests, marker summaries, and a new Figure 6 candidate.

## Key Validation Results

All-donor GSE135779 validation:

- IFN/ISG score: delta SLE-HC 0.2810; FDR 8.72e-04.
- ZEB2/TBX21/ITGAX-axis score: delta 0.0351; FDR 4.48e-02.
- ABC/APC-high fraction: delta 0.0567; FDR 7.88e-02.
- ABC/DN2 core score: delta 0.0370; FDR 1.09e-01.
- ABC/APC-focus score: delta 0.0425; FDR 1.75e-01.
- APC/HLA score: delta 0.0342; FDR 3.49e-01.

Interpretation:

GSE135779 strongly validates the IFN/ISG and ZEB2/TBX21/ITGAX axes and directionally supports an expanded ABC/APC-high B-cell tail. It does not independently prove a global APC/HLA increase.

## Recommended Next Stage

Phase 11 should integrate the new validation layer into the manuscript rather than launching another large dataset immediately.

Priority tasks:

1. Replace the current Figure 6 candidate with GSE135779 as the main validation figure.
2. Move GSE163121 to supplementary validation or boundary evidence.
3. Update the main manuscript Results and Discussion with GSE135779 validation.
4. Update the figure triage and submission package.
5. Decide whether to add an external regulatory convergence table using OneK1K/CIMA before target-journal formatting.

## Recommendation

For upper-Q1, the next most valuable step is manuscript integration plus a compact external regulatory evidence table centered on `ZEB2`, `TBX21`, `ITGAX`, `FCRL5/FCRL3`, HLA/CD74, and IFN/ISG genes.
