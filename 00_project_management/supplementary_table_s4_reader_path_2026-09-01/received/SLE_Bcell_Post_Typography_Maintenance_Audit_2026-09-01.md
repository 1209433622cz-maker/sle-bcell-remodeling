# SLE B-cell remodeling — post-typography scientific-presentation maintenance audit

**Date:** 2026-09-01  
**Independent status:** `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_VALID__ONE_READER_FACING_SUPPLEMENT_NUMBERING_DEFECT_FOUND`  
**Scope:** manuscript wording, figure/panel retention or replacement, Supplementary reader path and Nature/npj-style scientific presentation only. No submission-package, Release or Zenodo work.

## Executive decision

The Nature/npj artwork typography micropass is technically and scientifically successful. The 12 source-driven redraws should be retained, the three already role-aware Supplementary figures should remain byte-identical, and no main or Supplementary panel currently warrants replacement.

A single localized reader-facing defect remains in the Supplementary Information: the document declares `Tables S1-S9` but presents headings `S1, S2, S3, S4, S4B, S5, S6, S7, S8, S9`. The isolated `S4B` heading has no paired `S4A` and makes the visible table sequence look inconsistent even though the scientific content is valid.

## 1. Current scientific object

Retain without reopening:
- disease-blind identity reconstruction;
- frozen-representation and end-to-end identity sensitivities;
- B_ASC composition modelling;
- B_CONV raw-count pseudobulk and frozen programs;
- GSE135779 source-label-defined replication;
- corrected source-label-independent mapper calibration boundary;
- CollecTRI ULM, CAMERA/FRY and overlap-depletion analyses;
- M5911 and GSE23307 orthogonal response evidence.

The manuscript evidence hierarchy remains coherent: identity -> boundary propagation -> composition boundary -> B_CONV IFN/ISG discovery/internal replication -> source-label-defined external replication -> failed source-label-independent transfer -> observational regulator/response convergence.

## 2. Figure decisions after typography micropass

| Object | Decision | Rationale |
|---|---|---|
| Fig. 1a-d | KEEP | Fig. 1a uniquely owns the identity-to-disease inference boundary; b-d own frozen-representation stability. |
| Fig. 2a-d | KEEP | Primary composition result, sensitivities and leave-one-out diagnostics remain non-redundant. |
| Fig. 3a-d | KEEP | Unique owner of GSE174188 B_CONV program hierarchy and IFN branch effects. |
| Fig. 4a-d | KEEP | Essential source-label-defined external replication, gene-level concordance and influence evidence. |
| Fig. 5a-e | KEEP | Fig. 5a constrains interpretation; b-e supply the actual regulator/response evidence. |
| S1-S2 | KEEP | Unique QC and representation evidence. |
| S3 | KEEP exact | Two-panel prune is already optimal. |
| S4 | KEEP | New title and role-aware typography are correct; no further redraw is justified. |
| S5 | KEEP exact | Three-panel diagnostic-only version is optimal. |
| S6 | KEEP exact | External donor/support/source-label robustness is useful and non-duplicative. |
| S7 | KEEP | Table S4 owns exact values; S7 owns visual pattern recognition. |
| S8 | KEEP | Critical overlap-depletion evidence ceiling. |
| S9 | KEEP | Critical negative-boundary / uncertainty-propagation figure. |
| S10 | KEEP | Critical source-label-independent transfer calibration boundary. |
| New panels | 0 | No evidence gap. |
| Replacement panels | 0 | No existing panel is scientifically misleading. |

## 3. Typography micropass adjudication

The repaired style contract is preferable to the previous uniform-8-pt system:
- Arial retained;
- panel letters remain 8 pt;
- body text now spans the intended 5.5-8 pt hierarchy;
- ordinary rules below 1 pt are again allowed;
- 15 Source Data files remain invariant.

Do **not** run another global typography redraw merely to quantize small fractional font-size differences. The current figures have passed actual-size contact-sheet review; further global artwork churn would create more regression risk than reader benefit.

## 4. Localized Supplementary defect

Current overview:
`This single Supplementary Information file contains Tables S1-S9 and Figures S1-S10...`

Visible table headings:
`S1, S2, S3, S4, S4B, S5, S6, S7, S8, S9`.

### Why this should be repaired

`S4B` is presented as a separate table heading but has no `S4A`. Readers can reasonably interpret this as an irregular tenth Supplementary Table even though the overview says S1-S9.

### Preferred fix

Keep downstream S5-S9 numbers unchanged and treat the two regulator-sensitivity blocks as one Supplementary Table S4:

- `Supplementary Table S4 | Regulator-sensitivity summaries`
- `a, Correlation-aware core-regulator sensitivity`
- `b, IFN-overlap-depletion summary`

This is preferable to renumbering S5-S9, because it avoids changing any later table identifiers and preserves the current main-text `Supplementary Table S9` reference.

No numerical table cell changes are needed.

## 5. One optional reader-facing wording cleanup

Current Supplementary Table S5 evidence basis:
`Sample-level composition and asserted 43/47 primary groups`

Preferred:
`Sample-level composition and 43-control/47-managed-SLE primary groups`

Reason: `asserted` is an implementation/QC term rather than reader-facing scientific prose.

## 6. Manuscript text

The two `independent validation -> independent replication` edits are correct and should remain.

No additional QiTeng-style rewrite is justified now. In particular:
- keep the current title and abstract;
- keep the explicit non-equivalence wording for B_ASC composition;
- keep the program-level-vs-genome-wide distinction;
- keep the explicit source-label-defined external replication boundary;
- keep the Discussion's causal/clinical/taxonomic ceiling;
- keep the final sentence ending on a bounded process-level interferon association.

## 7. Next-stage decision

Proceed only to a narrow:

`SUPPLEMENTARY_TABLE_S4_READER_PATH_MICROPASS`

Scope:
1. merge S4/S4B into reader-facing S4a/S4b under one numbered Supplementary Table S4;
2. optionally replace `asserted 43/47 primary groups` with reader-facing wording;
3. rerender Supplementary Information only;
4. verify that Tables S1-S9 and Figures S1-S10 are sequential and all cross-references resolve;
5. confirm the Supplementary text differs only by these approved labels;
6. keep every figure, Source Data file, statistic and manuscript result unchanged.

If this passes, return immediately to:

`SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`

No further active figure redesign or manuscript polishing should occur unless a new localized, demonstrable defect is found.
