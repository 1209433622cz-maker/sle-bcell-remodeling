# Phase 17 active-artifact integrity audit

## Scope and result

This audit covers every file currently present in the active Gate C2B1 run and
the full-PBMC B-lineage precheck directory. The machine-readable manifest is
`phase17_integrity_manifest_2026-08-12.csv`.

- Files hashed: 213
- Gate C2B1 files: 198, including 176 paired checkpoint files
- B-lineage precheck files: 15
- Total audited size: 294,957,724 bytes
- Hash algorithm: SHA-256
- Content-contract result: **PASS**

The 12,218,105,530-byte CELLxGENE source H5AD is governed by the existing Gate C1
manifest and was not duplicated into this compact artifact manifest. Its frozen
SHA-256 is `FBD4692E033A57412FCC9DFE761180A9E4BDAE37C4FDA8F5ECC2E28FDE46371B`.

## Key artifact locks

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Gate C2B1 raw-count working H5AD | 270,671,628 | `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5` |
| Complete residual-risk score table | 2,052,079 | `271EA9FE22122588C207A1C61E76FC3C3590E5A81C0DC296085D5895FBA877D6` |
| Gate C2B1 binding decision JSON | 2,244 | `3A92D319FBBFCA0CCFC1661AE8E2871FCCBE8FF08CD0A274609E6BC655EBB48A` |
| B-lineage input decision JSON | 612 | `950366090EE06B0A03EF67DC59D882FCC258BBA7AFD411EBC20D7B39C6C5ADAC` |

## Content reconciliation

- Working H5AD: 150,402 cells by 30,172 genes; cell and gene identifiers unique.
- Working metadata: `source_cell_index`, `donor_id`, `sample_uuid`,
  `library_uuid` and `Processing_Cohort` only.
- Protected metadata: `disease`, `disease_state`, `ct_cov`, sex, ethnicity and
  development stage are physically separated in the protected table and absent
  from the representation object.
- Residual-risk table: 150,402 unique cell IDs with an exact set match to the H5AD.
- Automatic residual-risk calls: 1,972; reconciled between cell and library tables.
- Complete-library status: 88/88 `ok`; 88 score checkpoints and 88 summary checkpoints.
- Gate C2B1 decision: `PASS_TO_C2B2_WITH_DUAL_BRANCH`; all 12 checks pass.
- B-lineage input policy:
  `SOURCE_B_LABELS_PRIMARY_WITH_CANDIDATE_MAPPING_SENSITIVITY`.
- Refined outside-label candidates: 768 with core BCR identity; 57 also have low
  non-B signal. Automatic input expansion remains unauthorized.

## Interpretation

No size, hash, row-count, identifier or policy inconsistency was found. `ct_cov`
is not missing because a run stopped early; it is intentionally retained in the
protected outcome table and excluded from all disease-blind representation inputs.
The next numerical dependency is Gate C2B2 full representation fitting, not repair
of Gate C2B1 or re-extraction of the B-lineage primary input.
