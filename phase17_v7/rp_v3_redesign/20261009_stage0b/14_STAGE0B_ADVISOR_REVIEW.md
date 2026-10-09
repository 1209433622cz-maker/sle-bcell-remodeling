# RP v3 Stage 0B advisor gate review

**Decision:** `PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY`

## Result-blind trial findings

- The 14-gene A1 axis is fully computable in 150,402 cells and remains continuous.
- Its five quantile bins are an audit scaffold only; they do not authorize biological subtype labels.
- A2 was rebuilt in all 150,402 cells from the frozen 3,000-feature IFN-excluded list.
- A0 versus A2 structural concordance at resolution 0.4 is ARI=0.795, NMI=0.680.
- T0 is computable in 89 discovery strata from a 43-control frozen reference.
- T_frozen and T_rank are computable in 54 eligible external source-label B_CONV rows.
- The five-scenario simulation completed without model failures; it is a technical test, not a G2 claim.
- No disease coefficient, annotation effect or external case-control score difference was estimated.

## Checks

- [x] `a1_dictionary_complete`: 7 positive + 7 negative genes
- [x] `a1_scores_finite`: 150,402/150,402
- [x] `a1_structural_support`: minimum supported donors=72
- [x] `a1_future_arm_support`: minimum normal=33; managed=39
- [x] `pi_ref_valid`: sum=1.000000000000
- [x] `a2_full_cell_rebuild`: 150,402 x 3,000
- [x] `a2_ifn_exclusion`: zero strong-ISG features
- [x] `a2_structural_alignment`: ARI=0.795; NMI=0.680; clusters=5
- [x] `t0_computable`: 89 discovery strata; 43 reference controls
- [x] `external_frozen_score_computable`: 54 external rows; 12/12 genes
- [x] `rank_score_computable`: fixed background=18,873
- [x] `simulation_technical_truth_recovery`: max |bias|=0.002; coverage=0.925-0.970
- [x] `result_blind_contract`: no disease coefficient or between-group score summary estimated

## Interpretation boundary

A G1 pass authorizes WP1 annotation-sensitivity estimation under the frozen contracts. It does not
rescue the historical fine-state freeze, authorize subtype naming, unlock WP4, or modify the current
manuscript and figures. The historical identity failure remains part of the project record.

## Next stage

`SCIENTIFIC_REDESIGN_WP1_ANNOTATION_SENSITIVITY`
