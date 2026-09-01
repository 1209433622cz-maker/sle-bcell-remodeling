# SLE B-cell remodeling — maintenance-freeze reader-path hostile audit

**Date:** 2026-09-01  
**Independent status:** `MAINTENANCE_FREEZE_SCIENCE_VALID__SUPPLEMENTARY_FIRST_CITATION_ORDER_GAP_FOUND`

## Executive decision

The S4/S4B reader-path repair is correct and should be retained. The scientific object remains frozen: all 21 main panels and all 38 Supplementary panels remain KEEP, with no new or replacement panel.

A new, localized reader-path gap remains: Supplementary Figures are not numbered in their order of first citation in the main manuscript. The manuscript currently encounters them as:

`S1 -> S2 -> S3 -> S9 -> S4 -> S5 -> S6 -> S10 -> S7 -> S8`

This causes the reader to jump forward and backward through the Supplementary PDF even though the underlying scientific narrative is now linear.

## Scientific hierarchy

The current hierarchy is strong and should not be reopened:

1. disease-blind source/QC and representation checks;
2. fine-state failure and broad analysis scaffold;
3. end-to-end B_ASC-specific reconstruction boundary;
4. propagation showing stable disease-level conclusions;
5. unsupported primary B_ASC composition contrast;
6. reproducible B_CONV IFN/ISG program;
7. source-label-defined GSE135779 replication;
8. failed source-label-independent calibration;
9. observational regulator convergence;
10. overlap-depletion ceiling.

This hierarchy matches the target journal's single-cell systems biology and systems immunology scope without requiring extra modelling merely for scope signalling.

## Panel adjudication

- Main Figure 1a-d: KEEP.
- Main Figure 2a-d: KEEP.
- Main Figure 3a-d: KEEP.
- Main Figure 4a-d: KEEP.
- Main Figure 5a-e: KEEP.
- Supplementary Figures S1-S10: all scientific panels KEEP.
- New panels: 0.
- Replacement panels: 0.
- New biological analyses: 0.

Figure 1a remains necessary because it owns the identity-to-disease inference boundary. Figure 5a remains necessary because it owns the evidence-class/causal-ceiling contract.

## Reader-path repair recommended

Renumber Supplementary display objects only so first-citation order becomes exactly S1-S10. Use the mapping in the accompanying CSV.

This is not a request to redraw the figures. The ten images can remain byte-identical; only the display identifiers, canonical references, derived filenames, alt titles, Source Data filenames/copies and manifests need to be regenerated from source.

## Cross-reference audit gap

The current machine audit verifies:
- source figure numbers are S1-S10;
- renderer contains S1-S10;
- Supplementary Table S9 is referenced.

It does not test the first-occurrence order of Supplementary Figure citations, and it does not test citation coverage for Supplementary Tables S1-S8.

Add both checks in the next refreeze.

## Supplementary tables

The repaired S4a/S4b structure is good. No further table renumbering is justified.

A small manuscript anchoring pass is worthwhile so Supplementary Tables S1-S8 are not reader-orphaned. Prefer four functional anchor locations rather than repetitive table-by-table callouts.

## Pagination

The uploaded 16-page Supplementary PDF is clean, but page 6 is a low-density bridge page containing only the explanatory paragraph after Supplementary Table S9. This is not a scientific defect.

A source-level pagination experiment may remove the forced break before Supplementary Figure S1. Adopt it only if the full S1 title, legend and image remain together and both renderers pass. Do not shrink tables or fonts just to save one page.

## Next stage

`SUPPLEMENTARY_FIRST_CITATION_ORDER_AND_TABLE_ANCHOR_REFREEZE`

Scope:
1. implement display-only Supplementary Figure renumbering;
2. update all canonical cross-references and source-data display filenames through a provenance map;
3. add concise main-text anchors for Supplementary Tables S1-S8;
4. optionally test the 15-page Supplementary pagination candidate;
5. dual-render and visually inspect;
6. require all figures and all Source Data numerical content to remain invariant.

If this passes, return immediately to `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`.
