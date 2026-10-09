# SLE B-cell project full-file and scientific-status audit

**Audit date:** 2026-10-10
**Workspace scope:** every regular file outside `.git` and this audit-output
directory
**Scientific baseline reviewed:** historical frozen manuscript/evidence chain
plus active RP v3 Stage 0, Stage 0B and WP1
**Decision:** `PASS_FILE_INTEGRITY_AND_ASSET_CLASSIFICATION / PROCEED_TO_WP2_PREFIT_G2_FREEZE`

## 1. Audit method and limits

The audit enumerated 7,850 regular files and computed a full SHA-256 for every
file. It recorded size, extension, modification time, Git state and path length.
Format-aware checks covered JSON parsing, CSV/TSV shape, Python syntax, text
decoding, ZIP/OOXML CRC and required parts, PDF structure/page count, image
decoding/dimensions, gzip CRC, TAR members, NPZ arrays and HDF5/H5AD structure.

This is a complete byte/structure inventory, not a claim that every sentence in
all historical records was reread manually. Content-level review concentrated on
the current README/status files, manuscript baseline, RP v3 contracts, gate
decisions, action records and machine-readable final results. Historical action
records were retained as provenance even when they contain superseded states.

Machine-readable outputs:

- `FILE_INVENTORY.csv`: full relative-path, size, SHA-256 and status ledger.
- `FORMAT_HEALTH_CHECKS.csv`: per-file parser/structure result.
- `HDF5_HEALTH_CHECKS.csv`: dedicated HDF5/H5AD inspection.
- `DIRECTORY_SIZE_SUMMARY.csv` and `EXTENSION_SUMMARY.csv`.
- `LARGE_FILE_REGISTER.csv`.
- `DUPLICATE_LARGE_FILE_GROUPS.csv`.
- `PORTABILITY_FINDINGS.csv`.
- `AUDIT_SUMMARY.json` and `HDF5_AUDIT_SUMMARY.json`.

## 2. Inventory summary

| Metric | Result |
|---|---:|
| Files audited | 7,850 |
| Total bytes | 6,106,137,873 |
| Total size | 5.687 GiB |
| Git-tracked or staged at scan time | 4,045 |
| Ignored/local-only | 3,805 |
| Files at least 10 MiB | 64 |
| Duplicate groups at least 1 MiB/file | 34 |
| Potential duplicate bytes beyond one copy | 356,673,470 bytes (340.15 MiB) |

Largest top-level areas:

| Area | Files | Size | Share |
|---|---:|---:|---:|
| `phase17_v7/` | 5,041 | 3.041 GiB | 53.509% |
| `Data/` | 7 | 1.251 GiB | 22.010% |
| `04_submission/` | 690 | 0.777 GiB | 13.675% |
| `00_project_management/` | 1,248 | 0.287 GiB | 5.048% |
| root `6013RP-wyf.zip` | 1 | 0.257 GiB | 4.519% |

The dominant extensions are ZIP (2.091 GiB), TAR (1.211 GiB), PNG
(1.063 GiB), H5AD (0.596 GiB), PDF (0.352 GiB) and DOCX (0.185 GiB). This
confirms that most disk use is raw/public data, scientific matrices, historical
packages and rendered QA rather than source code.

## 3. File-health findings

| Result | Count | Interpretation |
|---|---:|---|
| Direct format PASS | 7,433 | Parsed/decoded/CRC-checked successfully |
| HDF5 deferred then PASS | 5/5 | All H5AD containers opened and traversed with h5py |
| WARN | 1 | Empty third-party `dist-info/REQUESTED` marker; expected and harmless |
| Format-specific parser unavailable/not applicable | 411 | Still fully hashed and sized; increase reflects ignored compiled caches produced during validation |
| FAIL | 0 | No corrupt recognized object found |

The five H5AD files included the 150,402 x 30,172 raw-count object, the frozen
primary representation, the A2 prepared object and both A2 fitted diagnostics.
All opened successfully and exposed coherent root groups. The Stage 0B canonical
A2 fitted object remains the `a2_rebuild` file with SHA-256
`4943C575EB010572FA874864FD8258624310E077D5AF439EDA0C446C1A1B5F59`;
the CPU-repair diagnostic is not a substitute.

Two historical review-pack scripts emitted Python invalid-escape `SyntaxWarning`
messages because a Windows path appeared in an ordinary docstring. Their
docstrings were converted to raw strings; behavior and data were unchanged.

## 4. Size, duplication and portability

The largest local files are scientifically expected:

- GSE135779 RAW archive: 1.240 GiB.
- root workspace backup ZIP: 263.0 MiB.
- GSE174188 raw-count H5AD: 258.1 MiB.
- RP v3 local redesign ZIP: 256.5 MiB.
- frozen primary representation H5AD: 109.1 MiB.
- A2 prepared/fitted H5AD objects: 78.2-86.3 MiB.

The 34 large duplicate groups are dominated by historical submission packages,
Supplementary Information copies, portability-test extractions and render
proofs. They are useful for forensic provenance but should not be newly tracked
or treated as canonical. No deletion was performed. A future space-recovery task
may remove only a separately approved, hash-deduplicated list.

Portability review found 265 items:

- 119 paths longer than 240 characters, all concentrated in the copied QiTeng
  skill runtime/archives under the September QA tree. These cause Windows Git and
  `pathlib` traversal warnings.
- 146 text files containing absolute Windows paths. Most are historical action
  records or runbooks documenting real commands. They are provenance, not
  portable entry points. Public audit output redacts the path values.

The copied QiTeng runtime, rendered QA pages, duplicated package inputs, RP v3
render-review cache, third-party runtime and superseded prefit exports are now
explicitly Git-ignored. They remain on disk.

## 5. Valuable scientific and operational assets

### P0: active and canonical

- `README.md`, `RP_V3_REDESIGN_STATUS.md` and the machine-readable gate files.
- RP v3 Stage 0 input/unit/estimand/branch freeze.
- Stage 0B A1/A2, score, support, simulation and integrity contracts.
- WP1 disease-blind prefit freeze and pre-effect execution contract.
- WP1 donor scores, point estimates, paired bootstrap intervals, diagnostic
  figure, 11/11 audit and final adjudication.
- RP v3 runners, analysis scripts and regression tests.
- This complete inventory and its rerunnable audit tools.

### P1: frozen evidence and manuscript baseline

- Editable manuscript and Supplementary Information sources.
- Historical R1 identity and corrected C9R transfer boundaries.
- Scientific-presentation maintenance record and 21-panel evidence ownership.
- GitHub v1.1.0 / Zenodo 22151739 verification receipts.
- Dated action records, including negative results and implementation incidents.

### P2: necessary local-only inputs

- GSE174188 raw counts and frozen representation H5AD files.
- GSE135779 RAW archive and restored public-data cache.
- Stage 0B canonical A2 H5AD and other large recomputable intermediates.
- Historical package binaries needed only for exact-file forensic comparison.

### P3: retain locally but do not treat as evidence owners

- QiTeng third-party runtime copies and rendered QA pages.
- Duplicate candidate/input packages.
- Interrupted WP1 prefit exports; canonical prefit is
  `20261010_wp1_prefit_freeze` plus `20261010_wp1_prefit_contract`.
- Root/workflow ZIP backups and superseded render bundles.
- `05_Record/` conversation summaries, which are useful historical context but
  cannot override source files, manifests or machine-readable gates.

The exact classification is recorded in
`../VALUABLE_ASSET_REGISTER_2026-10-10.csv`.

## 6. Current scientific result

The historical paper remains strongest when framed as a hierarchy of
reproducibility rather than a new hard B-cell taxonomy. The retained positive
claim is process-level B_CONV IFN/ISG remodeling, with permanent identity,
transfer and mechanistic ceilings.

RP v3 has now added a prospective, result-bounded redesign layer:

1. Stage 0 recovered the real raw inputs and fixed biological units and
   estimands.
2. Stage 0B prospectively defined the A1 continuous axis, A2 IFN-excluded
   representation, common support, score scales and technical simulations.
3. WP1 restricted all branches to the same 68 donors and frozen design.
4. The managed-SLE coefficient remained positive in A0, A1 and A2.
5. A2 was nearly identical to A0; A1 produced a small positive shift. These
   results support tested-representation robustness, not equivalence, pure
   annotation independence, mediation or causal interpretation.

WP1 estimates are:

| Estimand | Estimate | 95% paired bootstrap CI |
|---|---:|---:|
| beta_A0 | 1.037152 | 0.598263-1.477349 |
| beta_A1 | 1.072077 | 0.630517-1.518759 |
| beta_A2 | 1.037718 | 0.598753-1.477793 |
| A1 - A0 | 0.034925 | 0.013789-0.057130 |
| A2 - A0 | 0.000567 | 0.000000-0.001424 |

All 2,000 paired bootstrap attempts succeeded and the final WP1 audit passed
11/11 checks.

## 7. Next-stage decision

Proceed only to:

**`WP2_PREFIT_IDENTIFIABILITY_AND_FULL_G2_SIMULATION_FREEZE`**

The next work is contract-first, not effect-first. Before any WP2 disease
coefficient, freeze the state/continuous target, composition coordinates,
support and missing-state policy, compatible estimand scales, nonlinear truth
calculation, core and stress simulations, 2,000 replicates per scenario, Monte
Carlo intervals and fail-closed acceptance criteria.

WP4, manuscript replacement, figure replacement, journal package rebuilding,
GitHub Release and Zenodo remain HOLD. The September manuscript/package remains
a frozen comparison baseline, not the active endpoint of RP v3.

## 8. GitHub disposition

The repository update should include source code, compact contracts, gate files,
WP1 results, action records, the asset register, the full audit and the rewritten
README/status documentation. Large matrices, public-data caches, copied skill
runtimes, rendered QA pages, duplicated package inputs and noncanonical interrupted
exports remain local and ignored. This preserves reproducibility without turning
GitHub into a raw-data or render-cache mirror.

## 9. Validation note

All 61 focused scientific/regression tests passed: 10 Stage 0/Stage 0B tests,
six WP1 unit tests and 45 manuscript/figure/QiTeng maintenance tests. The project
Conda environment still exhibits the already documented Windows NumPy/LAPACK
native exit in the WP1 OLS unit test; the identical six-test suite passed under
an independent NumPy runtime. This is retained as an environment issue rather
than hidden or misreported as a scientific failure.
