# Exact source-level patch specification — supplementary reader path

## Status

`PROPOSED_SOURCE_LEVEL_RENUMBER_ONLY__NO_SCIENTIFIC_OBJECT_CHANGE`

## Why this is worth reopening

The current main-text first-citation order of Supplementary Figures is:

`S1 -> S2 -> S3 -> S9 -> S4 -> S5 -> S6 -> S10 -> S7 -> S8`

The current repository cross-reference audit verifies that S1-S10 exist, but it does not verify first-citation order.

For a Nature-Portfolio-oriented reader path, the display identifiers should follow the narrative order. This is a presentation/cross-reference repair, not a biological-analysis revision.

## Required display renumber map

| Old | New | Role |
|---|---|---|
| S1 | S1 | Source integrity and hard-QC |
| S2 | S2 | Representation and bridge diagnostics |
| S3 | S3 | Fine-state failure / transition structure |
| S9 | S4 | End-to-end reconstruction boundary and propagation |
| S4 | S5 | Composition-model diagnostics |
| S5 | S6 | Pseudobulk / ranked-list diagnostics |
| S6 | S7 | GSE135779 replication robustness |
| S10 | S8 | Corrected reference-calibration / transfer boundary |
| S7 | S9 | Correlation-aware regulator sensitivity |
| S8 | S10 | IFN-overlap-depletion sensitivity |

## Implementation rules

1. Do not rerun any statistical model.
2. Do not change any plotted number, confidence interval, q value, threshold, colour semantic, panel geometry or legend meaning.
3. Do not hand-edit PDF/PNG artwork.
4. The ten Supplementary figure image objects may be reused byte-identically because the figure number is outside the scientific image.
5. In the new refreeze directory, create renamed display copies according to the map.
6. Create byte-identical renamed copies of the ten Supplementary Source Data CSVs so machine-readable filenames match the new display IDs.
7. Update canonical manuscript references, main Figure 1 legend, Supplementary legends/cross-references, Supplementary Table S5 source-data map, figure alt titles and build manifests.
8. Preserve a machine-readable old->new provenance map.
9. Add a regression test that parses the manuscript body before `## Figure legends`, records unique Supplementary Figure references in first-occurrence order and requires exactly `S1...S10`.

## Recommended table anchoring micro-edits

The current main manuscript explicitly cites Supplementary Table S9, while Supplementary Tables S1-S8 are not explicitly anchored in the main article.

Do not add nine repetitive sentences. Use a small number of functional anchors:

- Introduction or early Results:
  `Dataset roles, inferential units and the claim boundaries used throughout the analysis are summarized in Supplementary Tables S1 and S2.`

- End of Results:
  `The principal quantitative anchors across identity, composition, replication and response layers are summarized in Supplementary Table S3.`

- Regulatory Results:
  add `Supplementary Table S4` beside the correlation-aware and overlap-depletion figure citations.

- Reproducibility and provenance:
  `Figure-source mapping, reproducibility records, statistical and multiplicity families, and the statistical-results archive structure are summarized in Supplementary Tables S5-S8.`

Keep the existing Supplementary Table S9 citation in the corrected external-mapping subsection.

## Supplementary page-density experiment

Current page 6 contains only the explanatory paragraph following Supplementary Table S9, while Supplementary Figure S1 is forced to a new page.

Generate, but do not automatically adopt, one compact candidate in which the manual page break before Supplementary Figure S1 is removed.

Accept the compact candidate only if both WPS and LibreOffice show:
- the S9 explanatory paragraph complete;
- the complete S1 title, legend and image on the same page;
- no font-size reduction;
- no table compression;
- no clipping or overlap.

If either renderer fails, retain the current 16-page pagination. This is lower priority than citation-order repair.

## Explicit KEEP decisions

No figure panel is to be replaced. Figure 1a and Figure 5a remain scientific evidence-boundary panels, not decorative schematics.

No new cohort, mapper, regulator, sensitivity analysis or panel is justified.
