# Gate C5B frozen matrix export audit

- Status: `PASS_C5B_FROZEN_MATRIX_EXPORT`
- External disease effects inspected: **no**
- Gate C5A integrity manifest: **verified**
- Frozen source-count SHA256: `2CB31DCDB5194C42CB52CBF3FD2D9530F137E9786F09BFDACDA4BE1EA9DC86C7`

| Analysis | Role | Genes | Samples | HC | SLE | UMI | Rank |
|---|---|---:|---:|---:|---:|---:|---:|
| childhood_min50 | primary | 32,738 | 43 | 11 | 32 | 89,498,882 | 2/2 |
| combined_min50 | combined | 32,738 | 54 | 16 | 38 | 98,962,678 | 3/3 |
| adult_min50 | secondary | 32,738 | 11 | 5 | 6 | 9,463,796 | 2/2 |
| combined_min20 | threshold | 32,738 | 56 | 16 | 40 | 99,161,064 | 3/3 |
| combined_min100 | threshold | 32,738 | 51 | 16 | 35 | 98,136,354 | 3/3 |

Eight source-label omission matrices retain the same 43 childhood donors. Only the selected B-caSC count contribution is removed; samples are not reselected.
