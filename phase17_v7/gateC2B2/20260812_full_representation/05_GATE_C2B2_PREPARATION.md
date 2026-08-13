# Gate C2B2 representation preparation

**Status:** `PASS_TO_REPRESENTATION_FIT`

- Working cells: 150,402 across 88 libraries
- Residual auto calls retained in primary: 1,972
- Genes after minimum-cell filter: 16,357
- Union of frozen HVG branches: 3,023
- Protected outcome columns: none
- Software-test mode: False

The primary branch retains all hard-QC cells and excludes technical nuisance and
immunoglobulin-dominance genes from representation HVGs. Residual-risk-negative,
and strong-ISG-excluded analyses are fitted as sensitivity branches. An IG-
dominance reconstruction is documented as non-evaluable because canonical IG
constant genes are absent from the source raw feature space.
No disease or clinical outcome was used for feature selection.
