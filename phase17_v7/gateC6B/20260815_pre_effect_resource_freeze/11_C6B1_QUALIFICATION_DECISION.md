# Gate C6B-1 no-effect qualification decision

## `PASS_GATE_C6B1_NO_EFFECT_QUALIFICATION`

Real regulator activities and GSE23307 expression differences were not inspected.

## Checks

- [PASS] resource_hashes: 3/3 frozen external resources
- [PASS] collectri_hash_and_parser: STAT1=291, STAT2=50, IRF7=32, IRF9=25, E2F1=299, FOXM1=93, MYC=787, MYBL2=43
- [PASS] real_input_coverage: 24/24 >=5; core minimum=14
- [PASS] independent_ulm_reproduction: max delta=2.220e-15
- [PASS] null_calibration: P<0.05 fraction=0.0505 across 2000 tests
- [PASS] signal_recovery: median slope=0.719; direction=1.000
- [PASS] global_bh_recovery: sensitivity=1.000; empirical FDR=0.000
- [PASS] bh_independent_reproduction: max delta=5.551e-17
- [PASS] no_real_effect_inspection: real imports used only tested flags, symbols and target coverage

## Consequence

unlock the frozen 24-test Gate C6B2 regulator analysis
