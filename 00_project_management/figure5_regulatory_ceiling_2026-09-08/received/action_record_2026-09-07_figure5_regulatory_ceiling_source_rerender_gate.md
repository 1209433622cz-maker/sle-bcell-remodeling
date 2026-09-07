# Figure 5 regulatory-ceiling source-rerender gate

**Date:** 2026-09-07  
**Gate decision:** `PASS_ARCHITECTURE_AND_READABILITY__PROCEED_TO_CANONICAL_SOURCE_INTEGRATION`  
**Scope:** manuscript text and scientific figure presentation only; no submission engineering.

## 1. Independent baseline check

The current manuscript already states the evidential ceiling in the Abstract, Results and Discussion: STAT1/STAT2 support is convergent but observational and weakens after broader interferon-gene depletion. The current Figure 5, however, still uses panel d for three M5911 NES bars. Because panel a already records the M5911 evidence class and its three-contrast concordance, and the exact NES values are reported in the Results/Supplementary Table S3, current panel d has the lowest unique information density in Figure 5.

Frozen source hashes verified before candidate generation:
- Figure5_source_data.csv: `A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B`
- Supplementary_Figure_S9_source_data.csv: `D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3`
- Supplementary_Figure_S10_source_data.csv: `26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2`

No existing Figure 5 pixels were edited.

## 2. Panel-level adjudication

- 5a KEEP: evidence classes and causal/interpretive boundary.
- 5b KEEP: core and extended IFN-centred regulator activity.
- 5c KEEP: proliferation specificity comparators.
- current 5d REPLACE_IN_MAIN: scientifically correct but quantitatively low-density.
- candidate 5d SOURCE_REPLACEMENT: ULM slopes after 12-gene IFN/ISG-arm depletion versus all-M5911 depletion.
- 5e KEEP: two-donor IFN-beta perturbational context.
- S9/S10 KEEP as complete detailed owners.

## 3. Candidate d source-level result

The candidate uses the frozen S10 ULM rows only, because ULM provides the directly comparable slope/95% CI scale required for a compact main panel. CAMERA and FRY are deliberately not forced into the same main-panel axis and remain in S9/S10 and Supplementary Table S4.

The compact panel shows six core STAT1/STAT2 models across discovery, donor-nonoverlap and childhood replication:
- after removing the 12-gene IFN/ISG positive arm, all six ULM 95% CIs remain above zero;
- removing the broader M5911 response set produces stronger attenuation;
- discovery STAT2 is the explicit limiting case after M5911 depletion, with its 95% CI crossing zero.

This is a mechanistic-ceiling visualization, not a pass/fail gate. The candidate therefore uses neutral marker-shape encoding rather than red/green gate semantics.

## 4. Actual-size readability verdict

A dedicated approximately half-width 86 mm × 68 mm rendering was generated with publication-scale typography. The six rows, both depletion branches, the zero line and the discovery-STAT2 CI-cross-zero annotation remain readable without requiring a larger panel. Therefore the candidate clears the information-density/readability gate in the current Figure 5 lower-left slot.

## 5. Source-data ownership requirement

When integrated canonically:
- retain the three M5911 NES source rows because panel 5a still displays the quantitative summary `3/3 NES >3.0`;
- reassign those rows to panel-a/evidence-summary provenance rather than deleting them;
- add the 12 ULM depletion rows used by new panel 5d;
- leave panels b/c/e source rows unchanged.

Supplementary S10 remains the complete owner for all ULM/CAMERA/FRY branch details and target-retention diagnostics.

## 6. Narrow manuscript synchronization

Only three reader-facing synchronization operations are justified:
1. add `Fig. 5d` to the overlap-depletion Results paragraph while retaining Supplementary Fig. S10/Table S4b;
2. remove old panel-5d ownership from the M5911 NES sentence; panel 5a/Table S3 retain M5911 evidence ownership, and panel 5e retains GSE23307 display ownership;
3. rewrite only Figure 5d legend.

No change is justified to the title, Abstract, Discussion, Methods, regulator family, multiplicity family, effect estimates, q values or causal wording.

Recommended panel-d legend:
`d, Post-freeze ULM STAT1/STAT2 sensitivity after removing the 12-gene IFN/ISG positive arm or all 97 M5911 genes; intervals are 95% CIs. The broader M5911 depletion produced stronger attenuation, with discovery STAT2 crossing zero. Complete ULM/CAMERA/FRY depletion results are in Supplementary Fig. S10 and Supplementary Table S4b.`

## 7. Next stage

Proceed to `FIGURE5_REGULATORY_CEILING_CANONICAL_INTEGRATION_AND_REFREEZE`.

The project builder, not the proof PNG, should regenerate the complete 170-mm Figure 5 from locked sources. If the canonical render cannot preserve normal publication-size text and current a/b/c/e geometry, revert current 5d byte-identically. If it passes, refreeze Figure 5 and proceed to `SCIENTIFIC_PRESENTATION_FINAL_CROSS_DOCUMENT_FREEZE`, with no additional active analysis or figure redesign unless a localized semantic/numerical defect is found.
