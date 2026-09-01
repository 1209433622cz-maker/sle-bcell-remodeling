# Figure 1 boundary-promotion source-rerender gate

## Canonical status before test
Current manuscript remains scientifically valid.

## Experimental branch
`FIGURE1_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE`

## Source inputs
- Figure1_source_data.csv — SHA-256 F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805
- Supplementary Figure S4 source data — SHA-256 46EE840F86CA33AA4F5FCE0A37EEFCB4DB23831533BBFA20400BAE50744F5D42

## Candidate architecture
- 1a workflow: KEEP
- 1b policy selection: KEEP
- 1c frozen state-Jaccard PASS: current 1d moved here
- 1d end-to-end state-Jaccard HOLD: new compact summary from frozen S4 source data
- current 1c per-replicate ARI/agreement: no longer a main panel; source data retained

## Hard no-change constraints
Do not change:
- any biological identity rule;
- any resampling replicate;
- any criterion;
- any disease outcome;
- any effect estimate, CI, P or q value;
- any other figure;
- Supplementary S4's detailed evidence ownership.

## PASS criteria
1. source hashes match;
2. main Figure 1 tells `policy selection → frozen pass → end-to-end B_ASC boundary` without relying on the legend for the central failure;
3. actual-size typography passes;
4. no new claim;
5. manuscript/SI cross-references pass;
6. regression suite passes.

## Terminal decision
- PASS → adopt new Figure 1, update only legend/cross-references, then return to SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE.
- FAIL → discard candidate and restore current Figure 1 byte-identically.
