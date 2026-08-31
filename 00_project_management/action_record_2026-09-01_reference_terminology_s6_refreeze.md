# Action record: reference, terminology and Supplementary Figure S6 scientific refreeze

**Date:** 2026-09-01
**Final status:** `REFERENCE_TERMINOLOGY_AND_S6_SCIENTIFIC_REFREEZE_LOCKED`
**Scope:** scientific text and figure presentation only; no submission-package, release or Zenodo action

## Objective

Resolve the last demonstrated evidence-language inconsistencies without reopening the frozen biological or statistical analyses. The round independently verified method citations, normalized evidence-class terminology across the manuscript and Supplementary Information, redrew Supplementary Figure S6 from its locked Source Data, rebuilt both documents, and completed WPS/LibreOffice render QA.

## Independent decisions

- Added Chen, Lun and Smyth (2016) beside the original edgeR package citation because it directly supports filtering, TMM normalization and the robust quasi-likelihood workflow.
- Reworded FRY as a fast self-contained approximation to the directional `mroast/ROAST` gene-set test; the analysis and all q values were unchanged.
- Corrected the exact title of the MSigDB hallmark collection paper.
- Reserved `validation` for generic calibration, prospective validation, CRediT Validation and explicit statements that a same-data analysis is not independent validation.
- Standardized GSE174188 as discovery plus internal replication and GSE135779 as source-label-defined independent replication.
- Rejected direct use of the uploaded S6 candidate because tight bounding-box export reduced its width to about 167 mm, substituted Arimo for the established Arial contract and added an unnecessary figure-wide title.
- Retained the established four-panel S6 geometry, semantic palette and panel order; only panel a/c terminology, figure filename and legend title were changed.

## Scientific-object changes

- Numerical estimates changed: **0**
- Statistical models rerun: **0**
- Source Data changed: **0**
- Main panels: **21 KEEP, 0 MODIFY, 0 REPLACE**
- Supplementary figures: **S1-S5 and S7-S10 KEEP; S6 MODIFY by source redraw; 0 REPLACE**
- New biological claims: **0**

## Reference and terminology integration

The reference list now contains 33 contiguous references with continuous first-appearance order and no orphan citation. The manuscript now uses `biological-unit-aware inference`, `internal replication`, `source-defined managed SLE`, `source-defined flare`, `source-label-defined GSE135779 replication`, and the bounded phrase `support an IFN-centred regulatory context`. The Supplementary Information uses the same evidence classes in Tables S1, S5 and S8 and in the S6 legend.

## S6 source-redraw QA

- Source Data SHA-256: `A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6`; byte-identical to the previous frozen object and the received candidate input.
- Final physical size: 170.00 x 128.28 mm.
- Minimum extracted text size: 6.00 pt.
- Fonts: embedded/subset Unicode Arial.
- Panel titles: `GSE135779 donor support by analysis`, `Childhood primary program family`, `Source-label omission sensitivity`, `Childhood donor influence`.
- No figure-wide title was added; the scientific title remains in the Supplementary legend.

## Document and render QA

- Manuscript: 31 pages, WPS PDF SHA-256 `37988A6B23CA82D4FB69756F61A222565BBD3963059B4E0BABF2A21975C58C92`.
- Supplementary Information: 16 pages, WPS PDF SHA-256 `80712159D62F1E6943B8B23E015E26A5B1D83947049057957E6A363E745E0A4A`.
- WPS and LibreOffice retained complete content; their manuscript pagination differed by one page because LibreOffice moved the final legend fragment to page 32, while Supplementary pagination remained 16 pages in both renderers. All page text stayed inside the canvas, all ten Supplementary figures resolved, and all pages were nonblank.
- DOCX accessibility audits contained no high- or medium-severity findings.
- The author-confirmed submission package remains byte-identical at `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1` and was not rebuilt.

## Primary verification sources

- Chen, Lun and Smyth edgeR quasi-likelihood workflow: https://pubmed.ncbi.nlm.nih.gov/27508061/
- limma manual for `fry`/`mroast`: https://bioconductor.org/packages/release/bioc/manuals/limma/man/limma.pdf
- ROAST primary paper: https://pubmed.ncbi.nlm.nih.gov/20610611/
- MSigDB hallmark primary paper: https://pubmed.ncbi.nlm.nih.gov/26771021/

## Boundary and next stage

The scientific evidence chain is now textually closed: disease-blind identity scaffold; GSE174188 sample-cohort inference and internal replication; GSE135779 source-label-defined donor replication; observational regulator context; response-set concordance; descriptive perturbational context. No current defect justifies reopening disease-effect models, identity mapping, TF analysis, Source Data or another panel.

The next stage should be `FINAL_INTEGRATED_READER_SIMULATION_AND_REDUNDANCY_PRUNE`: read the manuscript and all legends in final order at actual size, test whether each paragraph and panel has a unique claim owner, remove only genuine repetition, and stop when no reader-path defect can be localized. It should not add cohorts, sensitivity analyses, replacement panels or submission engineering.
