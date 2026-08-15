# Gate C2B4 two-level state-model adjudication

**Decision:** `PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED`

## Binding model

- Hard identity compartments: `B_CONV` and `B_ASC`.
- Naive-memory structure: continuous within `B_CONV`; hard composition labels are prohibited.
- Platelet-associated structure: overlay/sensitivity program, not a B-cell identity.
- Source cluster 4: unresolved conventional-B boundary, not a publication subtype.
- Outcome unlock authorized: True.

## Checks

- [PASS] c2b3_integrity: 30/30 manifest rows verified
- [PASS] source_hold_preserved: original five/four/three-state HOLD remains unchanged
- [PASS] representation_contract: schema=2; PCs=50/50
- [PASS] transition_reconstruction_equivalence: maximum agreement delta=1.110e-16
- [PASS] two_compartment_replicates: 20/20 replicates
- [PASS] two_compartment_median_mapped_ari: 0.996 >= 0.950
- [PASS] two_compartment_minimum_mapped_ari: 0.990 >= 0.900
- [PASS] two_compartment_median_mapping_agreement: 0.9999 >= 0.9950
- [PASS] two_compartment_minimum_mapping_agreement: 0.9998 >= 0.9900
- [PASS] two_compartment_state_jaccard: 0.991 >= 0.950
- [PASS] asc_marker_panel: required markers present: DERL3, JCHAIN, MZB1, TNFRSF17, XBP1
- [PASS] asc_marker_sample_support: minimum required-marker support=1.000
- [PASS] asc_cluster_sample_support: cluster median support=1.000
- [PASS] disease_blind_contract: transition, marker and candidate evidence remain disease blind

## Interpretation

The original C2B3 HOLD remains valid for five-, four- and three-state hard clustering.
C2B4 does not relabel that failure. It replaces the unstable naive-memory partition with
a disease-blind two-level model supported by resampling transitions and an orthogonal ASC
marker panel. Only the scope recorded above may proceed to outcome-aware analysis.
