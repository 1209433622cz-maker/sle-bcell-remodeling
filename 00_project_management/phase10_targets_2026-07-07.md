# Phase 10 Targets - 2026-07-07

## Status

The project shifted from a realistic Q1/Q2 package to an upper-Q1 strengthening route. The key requirement was independent validation or stronger external regulatory evidence.

## Completed

- Identified GSE163121 as a small, direct B-cell validation dataset.
- Downloaded and parsed GSE163121 processed matrices.
- Generated `figure6_gse163121_independent_bcell_validation.png`.
- Generated GSE163121 sample-level program-score tables and marker summaries.
- Identified GSE135779 as the preferred large independent validation cohort.
- Downloaded GSE135779 metadata, gene list, series matrix, and processed RAW tar.
- Inspected GSE135779 RAW tar structure.
- Built and ran `30_run_gse135779_bcell_validation.py`.
- Matched 32,179 metadata-defined B-subcluster cells from 56 donor/sample names.
- Generated `figure6_gse135779_large_cohort_validation.png`.

## Current Scientific Assessment

GSE163121 provides useful but limited external evidence. It directionally supports SLE B-cell ZEB2/TBX21/ITGAX and IFN axes, but does not show a global APC/HLA increase. Because it has only five donors, it should be framed as supplementary validation or boundary evidence.

GSE135779 is now the main upper-Q1 validation layer. It strongly validates IFN/ISG activity and the ZEB2/TBX21/ITGAX axis, and directionally supports an expanded ABC/APC-high B-cell tail. APC/HLA is directionally positive but not statistically decisive in this validation cohort.

## Next Stage Goal

Phase 11 should integrate GSE135779 validation into the manuscript and submission package.

Priority tasks:

1. Use GSE135779 as the main Figure 6 validation layer.
2. Move GSE163121 to supplementary validation or boundary evidence.
3. Update manuscript v2 into manuscript v3 with the validation Results section.
4. Update figure triage and supplementary table index.
5. Decide whether to add a compact OneK1K/CIMA external regulatory convergence table.

## Recommendation

Proceed to manuscript integration before adding another large analysis. A compact OneK1K/CIMA regulatory convergence table is now optional but attractive for upper-Q1 positioning.
