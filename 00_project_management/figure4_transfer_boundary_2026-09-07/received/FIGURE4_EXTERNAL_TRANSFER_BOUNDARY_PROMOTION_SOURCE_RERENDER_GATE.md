# Next-stage gate: FIGURE4_EXTERNAL_TRANSFER_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE

## Canonical baseline
`SCIENTIFIC_FIGURE1_BOUNDARY_PROMOTION_REFREEZE` at GitHub commit d317c4619cfc84134934910cfea87b65ee41e059.

## Scientific reason to reopen Figure 4d
Corrected source-label-independent remapping failure is a major inferential boundary in Abstract/Results/Discussion but is Supplementary-only. Current Figure 4d duplicates robustness already owned by Supplementary Figure S7.

## Required frozen inputs
- Figure4_source_data.csv
- Supplementary_Figure_S7_source_data.csv
- Supplementary_Figure_S8_source_data.csv

All must match the hashes recorded in `SOURCE_HASH_PROVENANCE.txt`.

## Candidate architecture
- 4a KEEP
- 4b KEEP
- 4c KEEP
- 4d replace with a compact required elastic-net calibration gate derived from S8

## Hard no-change constraints
- no disease-effect model rerun;
- no mapping threshold change;
- no mapper substitution;
- no cohort or donor change;
- no change to source-label-defined external effect;
- no change to Supplementary S7/S8 scientific values;
- no hand editing of existing Figure 4 pixels.

## Main-panel decision values
Required elastic-net mapper:
- coverage 0.941958 versus criterion 0.80 — pass;
- B_CONV precision 0.996450 versus criterion 0.90 — pass;
- B_ASC precision 0.885210 versus criterion 0.90 — fail.

Therefore no corrected source-label-independent external disease effect is estimated.

## Source Data rule
New Figure4 Source Data should contain only data actually used in panels 4a-d.
The donor/source-label influence values removed from main 4d remain fully preserved in Supplementary Figure S7 Source Data and must not be deleted.

## PASS gate
1. candidate generated through project plotting chain from locked CSVs;
2. panel 4d readable at actual target width;
3. panel 4d communicates the failed required mapper without implying the centroid mapper is an eligible replacement;
4. exact manuscript cross-reference changes only;
5. S7/S8 remain complete detailed owners;
6. no scientific estimates change;
7. dual-render manuscript QA and full regression pass.

## Terminal decision
- PASS: refreeze Figure 4 and proceed to `FIGURE5_REGULATORY_CEILING_PROMOTION_SOURCE_RERENDER_GATE`.
- FAIL: restore current Figure 4 byte-identically and proceed to Figure 5 gate independently.
