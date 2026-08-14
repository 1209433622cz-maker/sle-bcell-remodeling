# Next-stage decision: rerun Gate C2B3 with source-matched 50-PC graphs

## Advisor decision

The completed 30-PC resampling run is invalidated because the Gate C2B2 reference
graph used all 50 Harmony dimensions. Gate C2B3 remains pending rather than failed.
Disease/outcome metadata remains locked.

## Immediate target

Run the corrected schema-v2 20-replicate workflow using 50/50 matching dimensions.
The valid candidate mapping and marker ranking are already checkpointed.

```powershell
powershell -ExecutionPolicy Bypass `
  -File "H:\cuhk-2025fALL\6013RP-wyf\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1" `
  -GateC2B2RunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B2\20260812_full_representation" `
  -ResumeRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B3\20260813_full_neutral_state_freeze" `
  -Replicates 20 `
  -ResampleFraction 0.8
```

Expected status fields include `schema_version=2`, `n_pcs=50`,
`source_representation_dimensions=50` and `representation_dimension_match=true`.

## Locked decision order

The reviewer will test the following disease-blind policies in order and accept the
first policy satisfying every stability threshold:

1. five-state r=0.4 backbone;
2. four-state backbone after merging platelet-overlay cluster 2 into cluster 0;
3. three-state identity core after also merging unresolved cluster 4 into cluster 0.

The hierarchy is fixed before corrected full results and cannot be changed after
viewing disease effects.

## Decision after the corrected run

If one policy passes, freeze its neutral IDs, complete marker-led display annotations
without outcome information and unlock Gate C3 sample-level composition analysis.

If no policy passes, retain the HOLD and redesign the disease-blind state model. The
next repair would be recursive modeling of stable naive, memory and plasmablast cores
with platelet, IFN and atypical signals represented as continuous programs, rather
than selecting another Leiden resolution after observing outcomes.

## Publication objective

This correction protects the central manuscript claim from a false stability failure.
Upper-Q1 positioning still depends on cohort-supported composition, within-state
transcription and independent validation after the neutral identity gate is validly
frozen.
