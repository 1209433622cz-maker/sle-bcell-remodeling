# Gate C4B frozen matrix export audit

- Status: `PASS_C4B_FROZEN_MATRIX_EXPORT`
- Disease-effect estimates inspected: **no**
- C4A integrity manifest: **verified**
- Frozen source-count SHA256: `28DF02DD8C46232000F5492B3A6B026AD2D94DC1C77319B2925C5AA770DE4B11`

| Analysis | Branch | Genes | Samples | Reference | Exposed | UMI | Rank |
|---|---|---:|---:|---:|---:|---:|---:|
| primary_base | all_hard_qc | 30,172 | 89 | 43 | 46 | 59,873,385 | 4/4 |
| primary_min20 | all_hard_qc | 30,172 | 94 | 44 | 50 | 60,143,685 | 4/4 |
| primary_min100 | all_hard_qc | 30,172 | 87 | 41 | 46 | 59,493,597 | 4/4 |
| primary_residual_risk_negative | residual_risk_negative | 30,172 | 89 | 43 | 46 | 58,989,619 | 4/4 |
| validation_full | all_hard_qc | 30,172 | 64 | 21 | 43 | 56,214,928 | 3/3 |
| validation_nonoverlap | all_hard_qc | 30,172 | 54 | 21 | 33 | 46,156,989 | 3/3 |
| flare_full | all_hard_qc | 30,172 | 34 | 18 | 16 | 35,877,776 | 4/4 |

All matrices are genes-by-samples sparse integer Matrix Market exports. Column sums were independently compared with frozen C4A pseudobulk libraries.
