# Gate C6B-2 frozen regulator decision

## `PASS_GATE_C6B2_REGULATOR_LAYER_PENDING_ORTHOGONAL_REVIEW`

The 24-test family and all target diagnostics follow the pre-effect contract.

## Checks

- [PASS] core_positive_all_three
- [PASS] core_global_q_each_contrast
- [PASS] ifn_family_direction_and_no_reversal
- [PASS] proliferation_control_specificity
- [PASS] core_leave_one_out_and_resampling
- [PASS] confirmatory_family_exactly_24
- [PASS] qualification_unlock_verified

## Confirmatory estimates

- gse174188_primary / STAT1: slope=1.2853, 95% CI 0.9604 to 1.6103, global q=6.55e-14, targets=98
- gse174188_primary / STAT2: slope=2.1823, 95% CI 1.3256 to 3.0390, global q=1.84e-06, targets=14
- gse174188_primary / IRF7: slope=1.2109, 95% CI -0.2248 to 2.6466, global q=0.147, targets=5
- gse174188_primary / IRF9: slope=3.4464, 95% CI 2.2366 to 4.6562, global q=8.49e-08, targets=7
- gse174188_primary / E2F1: slope=0.0844, 95% CI -0.2695 to 0.4382, global q=0.698, targets=83
- gse174188_primary / FOXM1: slope=-0.1327, 95% CI -0.9359 to 0.6705, global q=0.778, targets=16
- gse174188_primary / MYC: slope=-0.3555, 95% CI -0.5392 to -0.1719, global q=0.000325, targets=317
- gse174188_primary / MYBL2: slope=-0.1254, 95% CI -1.2612 to 1.0103, global q=0.829, targets=8
- gse174188_internal_nonoverlap / STAT1: slope=1.0905, 95% CI 0.8426 to 1.3384, global q=6.46e-17, targets=129
- gse174188_internal_nonoverlap / STAT2: slope=2.9619, 95% CI 2.3211 to 3.6026, global q=2.04e-18, targets=19
- gse174188_internal_nonoverlap / IRF7: slope=2.1966, 95% CI 0.9414 to 3.4518, global q=0.00121, targets=5
- gse174188_internal_nonoverlap / IRF9: slope=2.6864, 95% CI 1.8006 to 3.5721, global q=1.16e-08, targets=10
- gse174188_internal_nonoverlap / E2F1: slope=0.1480, 95% CI -0.1222 to 0.4182, global q=0.377, targets=109
- gse174188_internal_nonoverlap / FOXM1: slope=-0.3835, 95% CI -0.9697 to 0.2028, global q=0.282, targets=23
- gse174188_internal_nonoverlap / MYC: slope=-0.2254, 95% CI -0.3695 to -0.0812, global q=0.00374, targets=393
- gse174188_internal_nonoverlap / MYBL2: slope=-0.7761, 95% CI -1.5873 to 0.0352, global q=0.0973, targets=12
- gse135779_childhood / STAT1: slope=1.1380, 95% CI 0.9127 to 1.3633, global q=1.31e-21, targets=161
- gse135779_childhood / STAT2: slope=2.4002, 95% CI 1.7631 to 3.0372, global q=7.97e-13, targets=20
- gse135779_childhood / IRF7: slope=1.8490, 95% CI 0.7703 to 2.9277, global q=0.00145, targets=7
- gse135779_childhood / IRF9: slope=2.1618, 95% CI 1.2599 to 3.0637, global q=7.1e-06, targets=10
- gse135779_childhood / E2F1: slope=-0.0754, 95% CI -0.3095 to 0.1588, global q=0.622, targets=150
- gse135779_childhood / FOXM1: slope=0.1734, 95% CI -0.3871 to 0.7338, global q=0.622, targets=26
- gse135779_childhood / MYC: slope=-0.2585, 95% CI -0.3920 to -0.1250, global q=0.000325, targets=470
- gse135779_childhood / MYBL2: slope=-0.2796, 95% CI -1.0431 to 0.4840, global q=0.597, targets=14

## Consequence

run frozen MSigDB and GSE23307 orthogonal response analyses
