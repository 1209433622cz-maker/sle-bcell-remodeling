# Gate C5A advisor decision

## `PASS_GATE_C5A_TO_FROZEN_EXTERNAL_EFFECT_MODELING`

GSE135779 source, identity mapping, pseudobulk counts, program dictionary and external designs are frozen without inspecting a new disease-effect coefficient.

| Check | Result | Detail |
|---|---:|---|
| pre_effect_contract | PASS | both run status and freeze contract report no external effect inspection |
| source_file_integrity | PASS | 6 source files independently rehashed; failures=[] |
| tar_member_integrity | PASS | 112/112 members independently rehashed; failures=0 |
| sample_matrix_and_barcode_audit | PASS | 56 unique samples; 32,738 genes; 321,106 matched metadata cells; 4 explicit exceptions |
| metadata_matrix_sample_gap_explained | PASS | 58 metadata donors versus 56 matrices: JB19002/aHD2 and JB19016/aSLE8 absent, one per group |
| metadata_version_policy | PASS | 44 childhood samples; aggregate Jaccard=0.9751; extended metadata frozen as authoritative |
| pseudobulk_count_integrity | PASS | matrix=(672, 32738); dtype=int64; row sums and Ensembl uniqueness exact |
| label_to_compartment_conservation | PASS | all sample-level B/PC source-label rows sum exactly to their compartment pseudobulk |
| disease_blind_identity_mapping | PASS | 8 B-caSC labels -> B_CONV_ANALOG; 2 PC-caSC labels -> identity control; disease unused |
| frozen_program_contract | PASS | exact C4A dictionary; all signed arms >=80%; IFN/ISG 12/12 genes available |
| external_design_identifiability | PASS | five frozen designs match expected group sizes and are full rank |

## Frozen analyses

- Primary: childhood B_CONV analog, >=50 matched B cells, 11 HC and 32 SLE donors.
- Combined: childhood plus adult, >=50 cells, 16 HC and 38 SLE donors, adjusted for adult stratum.
- Secondary: adult, >=50 cells, 5 HC and 6 SLE donors.
- Threshold sensitivities: >=20 and >=100 cells.
- Confirmatory multiplicity: BH across the exact four Gate C4A programs.
- IFN/ISG dictionary: 12 frozen genes, 12/12 available.

## Source limitations

- The 58-to-56 donor difference is fully explained by absent matrices for JB19002/aHD2 and JB19016/aSLE8.
- Four metadata barcodes are absent from matrix barcode lists and are listed explicitly.
- 42,977 matrix barcodes have no extended processed metadata annotation and cannot enter source-label-defined B analysis.
- Childhood metadata versions overlap strongly but are not identical; they must never be concatenated.

## Next action

Gate C5B is authorized. Export the frozen >=50/20/100 B_CONV pseudobulks to edgeR, qualify R import against C5A row and gene sums, then fit childhood, combined and adult models. Existing legacy GSE135779 effects remain prohibited as confirmatory inputs.
