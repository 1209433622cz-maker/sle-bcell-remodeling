# Gate C8R pre-submission repair action record

**Date:** 20 August 2026

**Role:** bioinformatics advisor-level scientific, figure, manuscript and package audit

**Scope:** repair the Gate C8 submission candidate without changing frozen
biological results by hand; regenerate analyses, figures and documents wherever
the defect arose upstream.

## 1. Trigger and governing decision

The prior Gate C8 package was scientifically close to submission-ready but was
not accepted as a final handoff. The repair round addressed five material risks:

1. Figure 2a did not visibly carry the frozen control/managed-SLE raw-point
   mapping even though the source table contained the observations.
2. Cross-panel typography and status language were not yet consistent with a
   restrained Nature-family figure standard.
3. The STAT1/STAT2 ULM family did not explicitly account for within-regulon gene
   correlation.
4. The novelty argument needed clearer separation from prior SLE interferon
   and molecular-endotype literature.
5. The submission archive needed machine-verifiable panel, document, reference
   and integrity gates.

The governing principle was to repair upstream scripts and rerun outputs. No
reported estimate, P value, q value, sample size or biological label was edited
directly in a final figure or DOCX.

## 2. Figure regeneration and visual policy

`audit_tools/phase17_c7_01_build_main_figures.py` was revised and rerun in the
`sle-bcell-v7` environment. The repair:

- maps Figure 2a controls from `na` and managed SLE from `managed`;
- asserts exactly 43 control, 47 managed-SLE and 90 total raw observations;
- adds exact assertions for every plotted table/filter/point family;
- removes internal PASS/HOLD language from reader-facing Figure 1;
- treats identity policies as discrete alternatives rather than connecting
  them as a trajectory;
- standardizes panel lettering, typography, axes, legends and palette;
- requires visible figure text of at least 5 pt;
- emits five PDF composites and five 600-dpi PNG composites from frozen Gate
  C2B4-C6B tables.

The generated assertion record contains 43 checks and all 43 pass. Figure 2a
passes the exact 43/47/90 mapping. PNG dimensions range from 4254 x 3270 to
4254 x 3720 pixels; every PDF and PNG is below 10 MB. All five figures were
visually reviewed for clipping, overlap, legend interference and missing marks.

## 3. Correlation-aware regulator sensitivity

`audit_tools/phase17_c8r_01_correlation_aware_regulator_sensitivity.R` was added
and run with R 4.6.0, edgeR 4.10.1 and limma 3.68.4. It reused, without
reselection, the frozen STAT1/STAT2 regulators, signed CollecTRI targets, three
contrasts, `filterByExpr` backgrounds and design matrices.

The six exact target counts match the ULM family: `98/14/129/19/161/20`.

| Method | Positive direction | BH significant | Interpretation |
|---|---:|---:|---|
| CAMERA | 6/6 | 5/6 | Supports direction and five strict core tests |
| FRY | 6/6 | 6/6 | Supports all six directional rotation tests |

The explicit exception is GSE174188 primary STAT2: 14 targets, estimated
inter-gene correlation 0.1225, CAMERA q=0.1355 and FRY q=4.91 x 10^-5. The
manuscript therefore states convergence with a discovery STAT2 CAMERA
limitation; it does not state universal CAMERA significance.

## 4. Literature and manuscript repair

`audit_tools/phase17_c8r_02_verify_references.py` verified 26 DOI-bearing
references through Crossref; all 26 passed. Together with GEO/repository
records, manuscript v11 contains 30 references.

`audit_tools/phase17_c8r_03_build_submission_sources.py` generated:

- `01_manuscript/manuscript_v11_genome_medicine_gateC8R_2026-08-20.md`;
- `01_manuscript/supplementary_information_v2_gateC8R_2026-08-20.md`;
- the Gate C8R cover letter, author completion form, target decision and
  reporting checklist in the local submission tree.

The structured abstract is 314 words and has Background, Methods, Results and
Conclusions labels. The manuscript is 6,353 words and retains all five figure
legends. The novelty logic now states that the advance is not rediscovery of
interferon involvement; it is identification of the remodeling layer that
survives disease-blind identity reconstruction, biological-unit inference,
donor non-overlap, independent validation and external response evidence.

The following boundaries are explicit throughout:

- no hard fine naive-memory disease subtype;
- no primary B_ASC expansion claim;
- no globally shared disease transcriptome claim;
- no causal STAT1/STAT2, direct TF-binding or unique ligand claim;
- no inferential claim from the two-donor perturbation experiment.

## 5. Document generation and WPS verification

`audit_tools/phase17_c8r_04_build_documents.py` regenerated three editable DOCX
files using the existing formal submission visual system:

- main manuscript: 12 pt Times New Roman, double spacing, continuous line
  numbering, page numbering and odd/even running headers;
- supplement: 11 pt body and six tables with explicit OOXML widths, grids,
  indents and cell geometry;
- cover letter: 10.5 pt body, compact one-page layout and visible author-action
  placeholders.

WPS Office rendered all documents in the background. The final page counts are
26 manuscript pages, 4 supplementary pages and 1 cover-letter page. All 31
pages were visually reviewed; no text or table clipping, overlap, missing glyph,
stray blank page or isolated signature page remained.

The standard bundled `render_docx.py` path was also attempted during the round
but could not start because LibreOffice/`soffice` is not installed. This was a
renderer-availability failure, not a DOCX conversion failure. WPS was therefore
used as the authoritative renderer and completed successfully. The bundled DOCX
accessibility audit reported zero high-, medium- and low-severity findings for
all three documents.

## 6. Reproducibility and package controls

The repository `README.md` and `REPRODUCIBILITY.md` were updated from the stale
Gate C2B2 state to the Gate C8R freeze. The one-command rebuild entry point is:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8R_submission_package.ps1
```

The final audit script checks scientific anchors, 43 panel assertions, figure
files, the six CAMERA/FRY tests, 26 DOI records, manuscript structure, claim
boundaries, DOCX OOXML, six-table geometry, accessibility, source-data hashes,
WPS pages and visible author hard stops.

Both additional-data ZIP files now use fixed entry ordering, timestamps and
permissions. The final package archive is likewise generated twice from the
same frozen package tree; unequal SHA-256 hashes would stop the gate. Every
package file except the manifest itself is recorded in `MANIFEST_SHA256.csv`.

## 7. Final gate result

**Decision:**
`PASS_GATE_C8R_SCIENTIFIC_FIGURE_REPRODUCIBILITY_REPAIR_AUTHOR_ACTION_REQUIRED`

- Scientific/technical package: PASS.
- Figure/data assertions: PASS 43/43.
- DOI verification: PASS 26/26.
- WPS visual review: PASS 31/31 pages.
- Accessibility: PASS, zero findings in all three DOCX files.
- Deterministic archive rebuild: PASS.
- Portal submission authorized: NO.

The canonical local archive contains 75 manifested files, is 12,198,352 bytes
and has SHA-256
`89d3f4139dd5c94bb216142351f6b425e8326f518efbdc0f0114652583f3c872`.

Portal authorization remains blocked because seven classes of facts cannot be
inferred by analysis code: institutional ethics determination, competing
interests, funding, final CRediT/all-author approval, acknowledgements,
originality/submission confirmation, and repository licence plus immutable DOI.

## 8. Files created or materially changed

- `audit_tools/phase17_c7_01_build_main_figures.py`
- `audit_tools/phase17_c8r_01_correlation_aware_regulator_sensitivity.R`
- `audit_tools/phase17_c8r_02_verify_references.py`
- `audit_tools/phase17_c8r_03_build_submission_sources.py`
- `audit_tools/phase17_c8r_04_build_documents.py`
- `audit_tools/phase17_c8r_05_final_submission_audit.py`
- `audit_tools/run_6013RP_phase17_gateC8R_submission_package.ps1`
- `01_manuscript/manuscript_v11_genome_medicine_gateC8R_2026-08-20.md`
- `01_manuscript/supplementary_information_v2_gateC8R_2026-08-20.md`
- `phase17_v7/gateC8R/20260820_pre_submission_repair/`
- `README.md`
- `REPRODUCIBILITY.md`

Generated upload files are stored under
`04_submission/package_genome_medicine_gateC8R_2026-08-20/` and remain outside
Git by repository policy.
