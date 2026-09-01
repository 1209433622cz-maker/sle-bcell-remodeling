# SLE B-cell remodeling — scientific-presentation maintenance audit

**Date:** 2026-09-01  
**Independent status:** `SCIENTIFIC_STOP_GATE_VALID__ONE_ARTWORK_STYLE_CONTRACT_DEFECT_FOUND`  
**Scope:** manuscript prose, figure semantics, panel retention/replacement, and Nature-Portfolio-style artwork consistency only. No submission-package, release, Zenodo, or new biological analysis work.

## 1. Current lock verification

The current manuscript and Supplementary Information remain scientifically coherent. The localized repairs recorded in commit `cb762af3c1346e9fe2e7d63fe3323cf1fc32f7ca` are appropriate:

- canonical manuscript/Supplementary sources were synchronized;
- the GSE135779 `mapped cells` ambiguity was removed;
- Supplementary Table S5 was renamed to `Selected figure source-data map`;
- Supplementary Fig. S4b was redrawn from frozen Source Data with a neutral title;
- numerical Source Data and scientific estimates were not changed.

No evidence was found that warrants reopening identity reconstruction, composition models, pseudobulk, GSE135779 disease modelling, external remapping, regulator analysis, CAMERA/FRY, overlap depletion, M5911, or GSE23307.

## 2. New maintenance-level defect: typography contract is not Nature-style

The repository's `audit_tools/publication_style_contract.py` currently implements `apply_npj_sba_style()` by setting **every visible text object to 8 pt**. It also raises all non-zero line widths to at least 1 pt.

This explains why the current S4 audit reports a minimum character size of 8 pt. The rendered S4 is readable, but its typography is visibly larger than neighboring Supplementary figures.

For a Nature-Portfolio-style target, this contract should not be treated as final. The Nature research figure guide recommends:

- panel letters: 8 pt bold;
- other figure text: 5–7 pt;
- Arial or Helvetica;
- editable/vector text;
- compact panel arrangement with minimal unnecessary white space;
- line widths within roughly 0.25–1 pt at final size.

### Recommended replacement style contract

Do **not** simply shrink every figure. Replace the global 8-pt override with role-aware typography:

- panel letters: 8 pt bold;
- panel titles: 7 pt;
- axis labels: 6.5–7 pt;
- tick labels: 5.5–6.5 pt;
- legends: 5.5–6.5 pt;
- annotations: 5.5–6.5 pt;
- colorbar labels: 6–6.5 pt;
- keep Arial embedded and editable;
- preserve original line hierarchy rather than forcing every line to 1 pt; use ~0.5–0.8 pt for ordinary axes/error bars and reserve ~1 pt only where visually necessary.

This is a **display-style rerun only**. Source Data, estimates, confidence intervals, q values, thresholds and panel geometry must remain unchanged.

## 3. Panel-by-panel decision

| Object | Decision | Rationale |
|---|---|---|
| Fig. 1a–d | KEEP | Fig. 1a owns the disease-blind inference boundary; b–d own frozen-representation stability. No duplicate owner. |
| Fig. 2a–d | KEEP | Clean primary-composition hierarchy; the non-equivalence boundary is explicit in the text. |
| Fig. 3a–d | KEEP | Fig. 3b remains the unique owner of frozen branch-wise IFN/ISG effects. |
| Fig. 4a–d | KEEP | Essential source-label-defined external replication and genome-wide-vs-program distinction. |
| Fig. 5a–e | KEEP | Fig. 5a is interpretive but necessary because it prevents causal over-reading of b–e. |
| S1 | KEEP | Unique source/QC evidence. |
| S2 | KEEP | Unique representation/bridge diagnostics. |
| S3 | KEEP current 2-panel prune | Further pruning would remove the fine-state failure mechanism or transition structure. |
| S4 | KEEP 4 panels; typography-only rerun candidate | The new panel-b title is scientifically correct. Data and panel structure should not change. |
| S5 | KEEP current 3-panel prune | Correctly restricted to model/ranked-list diagnostics. |
| S6 | KEEP | Provides donor/support/source-label robustness not efficiently replaceable in text. |
| S7 | KEEP | Panels b–d overlap numerically with Table S4, but the figure supplies visual method-concordance and target-imbalance structure; pruning gives little reader benefit. |
| S8 | KEEP | Critical attenuation/overlap-depletion boundary. |
| S9 | KEEP | One of the most important negative-boundary figures; directly supports the analysis-scaffold interpretation. |
| S10 | KEEP | Essential for the corrected source-label-independent transfer HOLD. |
| New panels | 0 | No scientific gap justifies expansion. |
| Replacement panels | 0 | No current panel is scientifically misleading. |

## 4. Manuscript micro-edits worth considering

These are optional maintenance edits, not required scientific repairs.

### T1 — Results terminology consistency

Current:
`Because both analyses originate from the same accession, they are internal replication rather than independent validation.`

Preferred:
`Because both analyses originate from the same accession, they provide internal replication rather than independent replication.`

Reason: the manuscript's evidence taxonomy is now consistently framed around discovery / internal replication / independent replication. `Validation` should remain reserved for methodological validation, calibration or CRediT terminology.

### T2 — Methods same-data boundary

Current:
`These analyses quantify same-data sensitivity to identity uncertainty; they are not independent validation.`

Preferred:
`These analyses quantify same-data sensitivity to identity uncertainty; they are not independent replication.`

Reason: matches the Supplementary Fig. S9 wording and avoids mixing evidence-class terminology.

No other prose rewrite is currently justified. The title, abstract, Introduction-to-Results transition, Discussion ceiling and final sentence should remain frozen.

## 5. S7 redundancy adjudication

Supplementary Table S4 already contains the exact six CAMERA/FRY q values, inter-gene correlations and matched-target counts. S7b–d therefore repeat those numerical quantities visually.

I nevertheless recommend **KEEP**, not prune, because:

- S7a gives the cross-method concordance pattern at a glance;
- S7b shows why STAT2 is the higher-correlation edge case;
- S7c makes the single CAMERA exception visually obvious;
- S7d exposes the severe target-count imbalance for STAT2.

The table owns exact values; the figure owns pattern recognition. This is complementary rather than harmful duplication.

## 6. Supplementary whitespace

The visible blank space below S3/S5/S6/S7 is not, by itself, a reason to redraw or enlarge the scientific panels. These figures are already full-width Supplementary display objects. Enlarging them only to fill an A4 page would create inconsistent apparent type size and would not improve evidence density.

## 7. Recommended next stage

Proceed once, and only once, to:

`NATURE_PORTFOLIO_ARTWORK_TYPOGRAPHY_MICROPASS`

Required sequence:

1. extract minimum **and maximum** font sizes from all 15 final figure PDFs;
2. classify text objects by panel-label / title / axis / tick / legend / annotation;
3. identify only figures outside the 5–7 pt body-text and 8 pt panel-label target;
4. update the shared style contract to role-aware sizing;
5. rerun affected figures **from frozen Source Data**;
6. assert byte-identical Source Data and numerically identical plotted objects;
7. perform actual-size visual review and dual-render document QA;
8. optionally apply T1/T2 terminology edits;
9. re-lock scientific presentation.

If the typography audit shows that only S4 is an outlier, rerun only S4. If multiple figures were generated under the global 8-pt contract, rerun only those affected figures. Do not use this pass as permission to reopen scientific analyses.

After that pass, return to `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`.
