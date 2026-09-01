# SLE B-cell remodeling — Final text–figure cross-reference and semantic stop-gate audit

**Date:** 2026-09-01  
**Audit status:** `STOP_GATE_NOT_YET_LOCKED__THREE_LOCALIZED_DEFECTS_FOUND`  
**Scope:** scientific manuscript text, figure semantics, figure ownership and author-facing source coherence only. No submission-package, release or Zenodo changes.

## Executive decision

The current rendered manuscript and Supplementary Information are scientifically coherent and substantially cleaner after the S3/S5 display prune. No new cohort, mapper, TF model, sensitivity analysis, replacement main panel or new Supplementary panel is justified.

However, the scientific-presentation layer should **not** be finally frozen yet because three localized defects remain:

1. **Author-facing canonical Markdown sources are stale relative to the current refreeze** — high priority.
2. **One GSE135779 sentence still uses the ambiguous phrase “mapped cells” inside a source-label-defined analysis** — medium priority.
3. **Supplementary Fig. S4b uses a rhetorically overstrong panel title (“Primary null is stable…”)** — medium priority.

A fourth item is minor and optional: Supplementary Table S5 is titled “Main-figure source-data map” despite including Supplementary Figs. S8-S10.

## Gate 1 — Panel-letter and cross-reference audit

### Main manuscript

All current references resolve to existing panels after the S3/S5 prune.

- Supplementary Fig. S1: source integrity / hard QC — valid.
- Supplementary Fig. S2: representation and bridge diagnostics — valid.
- Supplementary Fig. S3: fine-state failure / transition structure — valid after renumbering.
- Fig. 1a-d: broad frozen-representation identity scaffold — valid.
- Supplementary Fig. S9: end-to-end reconstruction and boundary propagation — valid.
- Fig. 2a-d + Supplementary Fig. S4: composition and sensitivity hierarchy — valid.
- Fig. 3a-c + Supplementary Fig. S5: primary program/gene evidence plus pseudobulk diagnostics — valid.
- Fig. 3d: program specificity family — valid.
- Fig. 4a,b + Supplementary Fig. S6: source-label-defined external replication and robustness — valid.
- Fig. 4c,d: gene concordance and donor/source-label influence — valid.
- Supplementary Fig. S10: corrected source-label-independent mapping boundary — valid.
- Fig. 5a-c + Supplementary Figs. S7/S8: regulatory convergence and attenuation boundary — valid.
- Fig. 5d,e: response-set and two-donor perturbational context — valid.

No surviving main-text sentence points to removed old S3a/S3d/S5d.

### Supplementary Information

- Current S3 has only panels a-b and its legend matches that two-panel structure.
- Current S5 has only panels a-c and explicitly assigns frozen branch-wise IFN/ISG estimates to Fig. 3b.
- S8-S10 legends and panel letters match their visible four/five-panel figures.
- No orphaned old S3d or S5d panel references were found.

**Gate result:** PASS.

## Gate 2 — Claim-owner uniqueness

The current evidence hierarchy has clean ownership:

- **Fig. 1**: frozen-representation broad identity stability.
- **Supplementary Fig. S3**: why fine-state identity failed and how the transition structure motivated broad adjudication.
- **Supplementary Fig. S9**: end-to-end reconstruction failure and disease-effect propagation.
- **Fig. 2**: primary composition result and main sensitivities.
- **Supplementary Fig. S4**: composition-model diagnostic decomposition.
- **Fig. 3b**: frozen GSE174188 branch-wise IFN/ISG effects.
- **Supplementary Fig. S5**: pseudobulk / dispersion / ranked-list diagnostics only.
- **Fig. 4**: source-label-defined GSE135779 replication and cross-dataset support.
- **Supplementary Fig. S6**: donor count, four-program, source-label omission and donor-deletion detail.
- **Fig. 5**: observational regulator / response evidence.
- **Supplementary Figs. S7/S8**: correlation-aware and overlap-depletion robustness.
- **Supplementary Fig. S10**: corrected source-label-independent transfer boundary.

The prior three duplicate display owners remain correctly removed.

**Gate result:** PASS.

## Gate 3 — Main-text semantic precision

### Localized defect T1 — “mapped cells” in source-label-defined GSE135779 analysis

Current sentence:

> The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 mapped cells per donor.

Problem:

The paragraph explicitly defines the analysis as a broad conventional-B analogue assembled from **source B-cell labels**, while the manuscript later reserves mapping/remapping language for the distinct corrected source-label-independent sensitivity. “Mapped cells” can therefore be misread as implying the childhood replication used the later mapper.

Recommended replacement:

> **The childhood analysis included 43 donors (11 controls and 32 SLE) with at least 50 eligible cells in the source-label-defined broad-B analogue per donor.**

No number, model or interpretation changes.

### Correct uses of “validation” that should NOT be mechanically replaced

Do not globally replace the word `validation`.

Retain:
- CRediT author-contribution role `Validation`.
- statements such as “not independent validation of the full feature-selection and tuning pipeline”.
- “not prospective validation” in the corrected mapping boundary.

These are methodological/evidential qualifications, not dataset-role labels.

## Gate 4 — Figure semantic precision

### Localized defect F1 — Supplementary Fig. S4b title

Visible current panel title:

> **Primary null is stable to covariances and cell policy**

Problem:

The main text correctly states that the confidence interval does **not** establish equivalent abundance. Describing a “null” as “stable” is rhetorically stronger than necessary and can sound like equivalence support. The panel itself only needs to show that the primary estimate remains qualitatively similar across covariance and cell-policy sensitivities.

Recommended source-redraw title:

> **Primary B_ASC estimate across covariance and cell policies**

Required implementation:
- rerun the existing S4 plotting code from frozen Source Data;
- change the panel-b title only;
- preserve all points, intervals, axes, null guide, colours and panel geometry;
- keep embedded Arial and >=6 pt visible type;
- do not crop or edit the PDF/PNG by hand.

All other S4 panels should be retained unchanged.

### No further figure replacements warranted

- Fig. 1a: KEEP.
- Fig. 5a: KEEP.
- S3: KEEP the new two-panel version.
- S5: KEEP the new three-panel version.
- S6-S10: KEEP.
- No new panel should be added to fill the deliberate whitespace created by S3/S5 pruning.

## Gate 5 — Author-facing source coherence

### High-priority defect S1 — root manuscript sources are stale

`01_manuscript/README.md` explicitly declares:
- `Manuscript.md` = current main manuscript source.
- `Supplementary_Information.md` = current supplementary information source.
- these stable filenames are the only author-facing entry points.

But the current `01_manuscript/Manuscript.md` still contains an older manuscript state, including:
- the older title beginning “Disease-blind single-cell reconstruction separates…”;
- a structured Background/Methods/Results/Conclusions abstract;
- a Keywords section containing `independent validation`;
- `Background` rather than the current `Introduction`;
- dataset-role wording such as `internal validation` / `independent SLE validation`.

The current `01_manuscript/Supplementary_Information.md` is also stale, including:
- Supplementary Methods sections that are absent from the current 16-page refreeze;
- `Discovery and internal validation`;
- `Independent SLE validation`;
- an older Zenodo state and text saying an updated archive is required.

This is not a cosmetic repository issue. Because the README identifies these as the author-facing current sources and the document build script uses them, a future rebuild could silently reintroduce superseded scientific wording.

### Required fix

At source level only:

1. replace `01_manuscript/Manuscript.md` with the current integrated-reader-refreeze manuscript source;
2. replace `01_manuscript/Supplementary_Information.md` with the current integrated-reader-refreeze Supplementary source;
3. apply T1 and the optional Table-S5 title polish during that sync;
4. assert exact semantic parity between root sources and the phase17 frozen sources after the localized edits;
5. rerun the document build and text-diff the resulting PDFs against the present refreeze, expecting only the approved localized changes.

Do **not** change numerical Source Data, release objects, Zenodo or the existing author-approved submission package in this scientific-presentation round.

## Minor optional text cleanup

Supplementary Table S5 is titled:

> `Main-figure source-data map`

but it also contains Supplementary Figs. S8-S10.

Recommended title-only cleanup:

> **Supplementary Table S5 | Selected figure source-data map**

No rows need to be added.

This is optional and should be bundled with the root-source sync if applied.

## Final figure decision matrix

| Object | Decision |
|---|---|
| Main Fig. 1a-d | KEEP |
| Main Fig. 2a-d | KEEP |
| Main Fig. 3a-d | KEEP |
| Main Fig. 4a-d | KEEP |
| Main Fig. 5a-e | KEEP |
| S1 | KEEP |
| S2 | KEEP |
| S3 | KEEP current 2-panel refreeze |
| S4a/c/d | KEEP |
| S4b | MODIFY TITLE BY SOURCE REDRAW ONLY |
| S5 | KEEP current 3-panel refreeze |
| S6 | KEEP |
| S7 | KEEP |
| S8 | KEEP |
| S9 | KEEP |
| S10 | KEEP |
| New panels | 0 |
| Replacement panels | 0 |
| New analyses | 0 |

## Final scientific assessment

The manuscript’s substantive logic is now strong:

1. identity is reconstructed before disease inference;
2. frozen-representation broad identity passes;
3. end-to-end reconstruction exposes a B_ASC-specific boundary;
4. uncertainty propagation preserves the disease-effect interpretation;
5. primary B_ASC composition remains unsupported rather than “equivalent”;
6. B_CONV IFN/ISG is the reproducible process-level signal;
7. GSE135779 supports source-label-defined independent replication but not source-label-independent taxonomy transfer;
8. STAT1/STAT2 and response analyses add observational convergence with explicit attenuation/causal limits.

No scientific gap currently justifies additional cohorts or methods.

## Next-stage decision

Proceed to:

`CANONICAL_SOURCE_SYNC__S4B_NEUTRAL_TITLE__FINAL_SEMANTIC_REFREEZE`

This should be the **last scientific-presentation modification round** and should contain only:

1. canonical root-source synchronization;
2. the one GSE135779 “mapped cells” sentence correction;
3. S4b source redraw with a neutral title;
4. optional Supplementary Table S5 title correction;
5. full text/figure cross-reference regression and dual-render QA.

If those checks pass, set:

`SCIENTIFIC_PRESENTATION_STOP_GATE_LOCKED`

and stop changing manuscript text or figures unless a new, demonstrable scientific defect is discovered.
