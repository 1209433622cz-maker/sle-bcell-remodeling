# Gate C2B3 neutral-state advisor review

**Decision:** `HOLD_GATE_C2B3_REVIEW_REQUIRED`

- Identity backbone: r=0.4
- Selected identity policy: none
- Neutral IDs evaluated: B0, B1, B2, B3, B4
- Outcome unlock authorized: False
- Publication-ready biological labels authorized: False

## Checks

- [PASS] resampling_complete: 20 replicates; 150,402 cells
- [PASS] representation_dimension_match: resampling=50 PCs; source=50 PCs
- [FAIL] identity_policy_selected: no prespecified r=0.4 policy passed
- [PASS] identity_median_ari: five_state: 0.812 >= 0.750
- [FAIL] identity_minimum_ari: five_state: 0.319 >= 0.650
- [PASS] identity_mapping_agreement: five_state: median=0.963 >= 0.800
- [FAIL] identity_cluster_jaccard: five_state: minimum cluster median=0.455 >= 0.600
- [PASS] marker_dictionary_complete: 5/5 clusters; minimum markers=20
- [PASS] marker_sample_support: minimum cluster median=0.874
- [PASS] candidate_mapping_complete: 768 candidates; automatic append=False
- [PASS] disease_blind_contract: all three C2B3 components are disease blind

## Binding interpretation

No prespecified identity policy passed all stability thresholds. Neutral IDs and outcome metadata remain locked pending disease-blind repair.
