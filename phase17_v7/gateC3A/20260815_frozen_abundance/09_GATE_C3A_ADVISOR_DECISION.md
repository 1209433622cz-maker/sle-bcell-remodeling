# Gate C3A frozen abundance-model advisor decision

**Decision:** `NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM`

- Primary conditional OR: 0.947 (95% CI 0.636-1.410; P=0.787)
- Primary HC1 audit: 95% CI 0.651-1.376; P=0.774
- Primary adjusted B_ASC fraction: 1.61% normal vs 1.52% managed
- Validation OR: 0.772; nonoverlap validation OR: 0.591 (n=53)
- Secondary flare OR: 2.303; nominal P=0.0282; frozen three-contrast BH q=0.0845
- Primary mandatory variants with same direction: 4/4
- Primary leave-one-out fits with same direction: 90/90

## Checks

- [PASS] gate_c3_integrity: 21/21 Gate C3 rows verified
- [PASS] frozen_base_models_complete: primary, internal validation and flare models fitted
- [PASS] base_model_diagnostics: all frozen models converged with positive-definite numerical Hessians
- [FAIL] primary_prespecified_support: OR=0.947; model 95% CI 0.636-1.410, P=0.787; HC1 95% CI 0.651-1.376, P=0.774
- [PASS] primary_mandatory_sensitivity_direction: 4/4 variants match frozen direction
- [PASS] primary_leave_one_out_direction: 90/90 leave-one-out fits match frozen direction
- [PASS] validation_nonoverlap_support: nonoverlap n=53; reference=21; exposed=32
- [PASS] validation_directional_replication: frozen OR=0.772; nonoverlap OR=0.591; primary direction matched=True
- [PASS] prohibited_inference_guard: sample-level two-compartment inference only; no hard naive-memory or cell-level test

## Binding interpretation

Two-compartment B_ASC composition must not be a central manuscript claim; retain as exploratory or secondary and prioritize continuous programs and pseudobulk replication.

The validation set is internal and partially overlaps the primary cohort. The explicit nonoverlap sensitivity reduces this concern but does not convert it into an external validation cohort.

## Next stage

Gate C4 prespecified continuous B_CONV programs plus sample-level pseudobulk differential expression; then independent external validation