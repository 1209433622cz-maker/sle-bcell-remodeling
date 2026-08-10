# Gate C1 strict common-support re-audit

**Status:** corrected, programmatically reproducible table.  
**Source:** `H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1\20260806_134213_hotfix_v1_1\02_donor_manifest.csv`

## Binding definition

The strict subset contains donors represented by exactly one biological sample,
assigned to exactly one processing cohort, with one unambiguous disease label.
No sample is selected from a repeated-sample donor in this ambiguity-free
summary. The subset contains 195 donors.

| Processing cohort | Disease | Strict biological units |
|---:|---|---:|
| 1 | Normal | 28 |
| 1 | SLE | 0 |
| 2 | Normal | 1 |
| 2 | SLE | 87 |
| 3 | Normal | 5 |
| 3 | SLE | 8 |
| 4 | Normal | 41 |
| 4 | SLE | 25 |

## Erratum

The earlier manually transcribed values 28/0, 1/78, 5/15 and 38/23 do not
reproduce from either Gate C1 manifest. They must not be used. The corrected
normal/SLE counts are 28/0, 1/87, 5/8 and 41/25 for cohorts 1-4, respectively.

This correction does not change the inferential ranking: cohort 4 remains the
primary direct comparison, cohort 3 remains small and exploratory, and cohorts
1-2 remain discovery/technical strata without credible direct disease support.
