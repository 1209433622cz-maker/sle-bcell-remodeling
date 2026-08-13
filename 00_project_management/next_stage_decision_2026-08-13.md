# Next-stage decision: complete Gate C2B3 full graph resampling

## Advisor decision

Gate C2B2 passes with r=0.4 as the disease-blind coarse identity backbone. The
project remains **NO-GO for disease inference and submission** until Gate C2B3
passes full graph-resampling stability and freezes neutral IDs.

## Evidence now complete

- Full primary, residual-risk-negative and ISG-excluded representation branches.
- Complete C2B2 integrity and advisor review.
- r=0.4 selected by the lower of two prespecified sensitivity ARIs (0.793 and 0.772).
- Full-gene marker ranking across 150,402 cells and 30,172 genes.
- Full mapping of 768 outside-label candidates against 150,402 reference B cells.
- Candidate-input decision closed as `MAPPING_COMPLETE_NO_AUTOMATIC_APPEND`.

## Immediate objective

Complete 20 library-stratified 80% graph resamples at r=0.4, r=0.6 and r=0.8.
The r=0.4 solution must meet all binding thresholds:

1. median ARI at least 0.75;
2. minimum replicate ARI at least 0.65;
3. median majority-mapping agreement at least 0.80;
4. minimum cluster-level median Jaccard at least 0.60;
5. full marker dictionary and sample-support checks remain satisfied; and
6. all inputs remain disease blind.

Run:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1 `
  -GateC2B2RunDir ".\phase17_v7\gateC2B2\20260812_full_representation" `
  -ResumeRunDir ".\phase17_v7\gateC2B3\20260813_full_neutral_state_freeze" `
  -Replicates 20 `
  -ResampleFraction 0.8
```

The full marker and candidate components are checkpointed and will be reused.

## Decision after the run

If Gate C2B3 passes, freeze source r=0.4 clusters as neutral IDs `B0` to `B4`,
complete marker-led biological display labels without consulting disease outcomes,
join protected metadata, and begin Gate C3 sample-level composition analysis.

If Gate C2B3 holds, inspect the failing cluster rather than selecting another
resolution after seeing disease effects. The unresolved `ANKRD40/C1orf56`-associated
cluster and the platelet-associated cluster are the leading candidates for targeted
repair or merger, but no action is authorized before resampling evidence is known.

## Ordered work after a C2B3 pass

1. Gate C3 sample-level composition within processing cohort 4, with cohort 3 as
   exploratory replication and donor-aware sensitivity.
2. Gate C4 sample-by-frozen-state raw-count pseudobulk disease contrasts.
3. Gate C5 frozen external mapping in GSE135779, stratified by childhood/adult design.
4. Regulatory evidence and manuscript Figures 3-5 only after replicated effects exist.

## Publication judgement

The project is methodologically stronger, but upper-Q1 positioning still depends on
cohort-reproducible disease effects and independent validation. C2B2/C2B3 rigor is a
necessary foundation, not the biological advance itself. Journal selection remains
provisional until composition, transcription and external-validation gates are frozen.
