# Gate C4B independent result-integrity audit

- Decision: `PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION`
- Checks passed: `7/7`
- Gene tables: `7/7` complete and exact
- Program rows: `63/63`; four-program BH independently reproduced
- Full gene tables contain all 30,172 frozen Ensembl features, including explicit non-tested rows.

| Analysis | Rows | Tested | Ensembl unique | BH exact |
|---|---:|---:|---:|---:|
| primary_base | 30,172 | 4,414 | yes | yes |
| primary_min20 | 30,172 | 4,098 | yes | yes |
| primary_min100 | 30,172 | 4,524 | yes | yes |
| primary_residual_risk_negative | 30,172 | 4,432 | yes | yes |
| validation_full | 30,172 | 6,099 | yes | yes |
| validation_nonoverlap | 30,172 | 6,077 | yes | yes |
| flare_full | 30,172 | 7,761 | yes | yes |
