# Gate C2B3 neutral-state advisor review

**Decision:** `HOLD_GATE_C2B3_REVIEW_REQUIRED`

- Identity backbone: r=0.4
- Neutral IDs evaluated: B0, B1, B2, B3, B4
- Outcome unlock authorized: False
- Publication-ready biological labels authorized: False

## Checks

- [PASS] resampling_complete: 20 replicates; 150,402 cells
- [FAIL] identity_median_ari: 0.603 >= 0.750
- [FAIL] identity_minimum_ari: 0.305 >= 0.650
- [PASS] identity_mapping_agreement: median=0.954 >= 0.800
- [FAIL] identity_cluster_jaccard: minimum cluster median=0.000 >= 0.600
- [PASS] marker_dictionary_complete: 5/5 clusters; minimum markers=20
- [PASS] marker_sample_support: minimum cluster median=0.874
- [PASS] candidate_mapping_complete: 768 candidates; automatic append=False
- [PASS] disease_blind_contract: all three C2B3 components are disease blind

## Binding interpretation

Passing this gate freezes neutral IDs for inference. Biological display names remain pending a marker-led advisor annotation table and cannot be outcome-derived.
