# Gate C9 label-agnostic GSE135779 advisor review

**Decision:** `PASS_C9_LABEL_AGNOSTIC_EXTERNAL_SUPPORT`

## Frozen execution

- C9A authorization: `PASS_C9A_PREFREEZE_OUTCOME_UNLOCK_AUTHORIZED`.
- Protected metadata were joined only after input and per-cell prediction hashes were reverified.
- No selection, mapper, confidence, minimum-cell or program threshold changed after unlock.
- Minimum confidently mapped B_CONV support: 50 cells per donor/sample.

## Primary childhood IFN/ISG result

- elastic_net: n=11 HC and 32 SLE; effect=0.3060; 95% bootstrap CI 0.2078 to 0.4143; P=0.000587; q=0.00235.
- nearest_centroid: n=11 HC and 32 SLE; effect=0.3042; 95% bootstrap CI 0.2075 to 0.4113; P=0.000529; q=0.00212.

## Selection and mapping audit

- elastic_net: source-B recovery 98.7%; non-B contamination 3.3%; confident assignment 97.8%.
- nearest_centroid: source-B recovery 98.7%; non-B contamination 3.3%; confident assignment 95.3%.

## Interpretation boundary

The source-label-defined external IFN/ISG replication is supported by a fully label-agnostic B-lineage selection and broad-state mapping sensitivity.

This sensitivity can strengthen the external-validation methods and supplementary evidence only. It does not repair the formal R1 state-overlap HOLD and does not authorize a discrete IFN-high B-cell subtype claim.
