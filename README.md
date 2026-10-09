# Disease-blind analysis of B-cell remodeling in systemic lupus erythematosus

This repository contains the auditable analysis, scientific-governance records,
manuscript sources and compact derived results for a hierarchy-aware single-cell
study of B-cell remodeling in systemic lupus erythematosus (SLE).

Repository: [1209433622cz-maker/sle-bcell-remodeling](https://github.com/1209433622cz-maker/sle-bcell-remodeling)

## Current status

**Active state on 10 October 2026:**
`ACTIVE_RP_V3_SCIENTIFIC_REDESIGN / HOLD_SUBMISSION`.

The public v1.1.0 archive and the September scientific-presentation baseline are
retained as historical, reproducible snapshots. They are not being silently
rewritten. The active project is now following the focused redesign specified by
Research Plan v3. Stage 0 input recovery, Stage 0B protocol/identifiability work,
WP1 annotation sensitivity, the WP2 effect-free structural preflight and the G2
implementation/domain freeze are complete. The full 25-scenario G2 operating-
characteristic run has not yet been executed. Therefore,
manuscript replacement, submission, GitHub Release and Zenodo updates remain on
hold until the redesign produces a fully gated and materially informative result.

Current gate:

```text
PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2
```

Next stage:

```text
G2_FULL_EXECUTION_R0_CORE_FIRST
```

## Scientific position

The stable historical conclusion remains **reproducible process-level B_CONV
IFN/ISG remodeling**, bounded by three permanent limitations:

1. **Identity ceiling:** end-to-end B_ASC membership did not meet the frozen
   reproducibility criterion (median Jaccard 0.930323 < 0.95).
2. **Transfer ceiling:** corrected source-label-independent external calibration
   failed its frozen B_ASC precision criterion (0.885210 < 0.90); corrected
   external disease outcomes were never unlocked.
3. **Mechanistic ceiling:** STAT1/STAT2 evidence is observational and partly
   coupled to the broader IFN-response transcriptome; it does not establish a
   unique ligand, direct binding or causal regulation.

The redesign does not attempt to rescue these HOLD decisions. It asks narrower,
predeclared questions about annotation sensitivity, composition, within-state
effects and the identifiability of those quantities.

## RP v3 progress

### Stage 0: inputs, units and estimands

- Recovered and hashed 21/21 required inputs.
- Confirmed 150,402 GSE174188 B-lineage cells, 30,172 genes, 259 donors,
  271 samples, 88 technical libraries and four processing cohorts.
- Verified the 1.30 GB GSE135779 RAW archive and all 56 matrix/barcode pairs.
- Registered biological units, chronology, estimands, branches and open
  parameters before new effect estimation.
- Initial decision: input recovery PASS; protocol/identifiability fields remained
  open and therefore correctly held.

See [Stage 0 gate](phase17_v7/rp_v3_redesign/20261009_stage0/08_STAGE0_GATE_STATUS.json)
and the [Stage 0 action record](00_project_management/action_record_2026-10-09_rp_v3_stage0_intake_and_freeze.md).

### Stage 0B: result-blind protocol and minimal trial

- Froze the A1 continuous 14-gene identity axis, the A2 3,000-feature
  strong-ISG-list-excluded representation, T0/T_frozen/T_rank and `pi_ref`.
- Rebuilt A2 on all 150,402 cells with the correct full-background
  normalization denominator.
- Obtained A0-A2 ARI 0.795448 and NMI 0.680148 with five A2 clusters.
- Verified finite score transfer and 12/12 program coverage.
- Completed five technical simulation scenarios with maximum absolute bias
  0.002315, empirical coverage 0.925-0.970 and no fit failures.
- No disease coefficient was inspected during this gate.

Decision: `PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY`.

See [Stage 0B gate](phase17_v7/rp_v3_redesign/20261009_stage0b/14_STAGE0B_GATE_STATUS.json),
[execution contract](phase17_v7/rp_v3_redesign/20261009_stage0b/17_WP1_ANNOTATION_SENSITIVITY_EXECUTION_CONTRACT.md)
and [action record](00_project_management/action_record_2026-10-09_rp_v3_stage0b_protocol_and_minimal_trial.md).

### WP1: annotation sensitivity

WP1 used the same 68-donor common support set (31 controls and 37 managed-SLE
donors), the same frozen four-column design and the same T0 reference in all
branches. All 2,000 paired donor-clustered bootstrap attempts succeeded.

| Estimand | Estimate | Paired bootstrap 95% CI |
|---|---:|---:|
| `beta_A0` | 1.037152 | 0.598263 to 1.477349 |
| `beta_A1` | 1.072077 | 0.630517 to 1.518759 |
| `beta_A2` | 1.037718 | 0.598753 to 1.477793 |
| `A1 - A0` | 0.034925 | 0.013789 to 0.057130 |
| `A2 - A0` | 0.000567 | 0.000000 to 0.001424 |

The managed-SLE coefficient remained positive across all three frozen
representations. A1 is a joint identity-axis/common-composition sensitivity,
not a pure annotation or mediation effect. A2 retains `LY6E`, and no equivalence
margin was declared; therefore neither "fully IFN-independent" nor "equivalent"
is authorized.

See [WP1 adjudication](phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/12_WP1_FINAL_ADJUDICATION.md),
[machine-readable decision](phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/11_WP1_FINAL_ADJUDICATION.json)
and [action record](00_project_management/action_record_2026-10-10_rp_v3_wp1_annotation_sensitivity.md).

### WP2: effect-free composition and identifiability preflight

The canonical WP2 preflight used the frozen 68-donor set and raw sufficient
statistics without fitting a new disease coefficient or writing grouped
expression summaries. It passed all support, hash, partition and design checks:

- every donor retained all five A1 bins, with a minimum of 30 cells per bin;
- A1 bin counts, full captured-library totals and cell counts exactly recover
  the parent A0 object;
- captured-UMI-weighted bin CPM reconstructs pooled CPM to `1.137e-13` maximum
  absolute error;
- the median absolute difference between cell and captured-UMI fractions is
  `0.015954`, with a maximum of `0.093275`;
- the optional base-plus-four-ILR design is rank 8/8, while intercept plus all
  five raw fractions is closure-redundant at rank 8/9.

The target registry now distinguishes the already observed fixed-profile WP1
target from a new cell-reference bridge target that retains captured UMI/cell.
Neither is an absolute-RNA or causal cell-composition effect. The target,
25-scenario and acceptance registries were frozen before G2 results.

Decision:
`PASS_WP2_EFFECT_FREE_PREFLIGHT__HOLD_G2_EXECUTION_IMPLEMENTATION_REQUIRED`.

See the [WP2 preflight review](phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/11_WP2_PREFIT_ADVISOR_REVIEW.md)
and [machine-readable gate](phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/06_WP2_PREFIT_GATE_STATUS.json).

### G2 implementation and domain freeze

The sufficient-count generator, actual paired-bootstrap estimator and an
independent nonlinear truth engine are now hash-bound. Independent Windows
requalification reproduced all 50 pilot statuses, 60,000/60,000 successful
inner fits and 250/250 truth-precision passes. Generated counts and bootstrap
indices were byte-identical across platforms; the largest floating-point
difference was `8.88e-16`.

R0, R2 and R4 are frozen as the applicable performance domain. R1 and R3 remain
mandatory boundary domains and cannot be deleted or rescued. The complete
chunked scheduler and adjudicator are implemented, but full G2 remains
`NOT_RUN` and no WP2 real effect is unlocked.

Decision:
`PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2`.

See the [G2 implementation review](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/10_G2_IMPLEMENTATION_ADVISOR_REVIEW.md),
[execution contract](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/08_G2_EXECUTION_CONTRACT.json)
and [local runbook](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/11_G2_FULL_RUN_RUNBOOK.md).

## Next gate: full G2 execution

Run the five R0 core scenarios first as an operational checkpoint, then complete
all 25 frozen scenarios and apply the unchanged target-scenario adjudicator.
WP2 results may be fitted only after a complete applicable-domain G2 PASS and a
separate post-G2 review. WP4 remains conditional and submission remains on hold.

## Reproduce the active redesign

Create or check the scientific environment first:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_create_conda_env.ps1
```

Run the completed gates from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_stage0.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_stage0b.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_wp1.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_wp2_prefit.ps1 `
  -OutputDir .\phase17_v7\rp_v3_redesign\wp2_prefit_reproduction

powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_g2_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2_full_runs\20261010_full `
  -Regimes R0 `
  -ChunkSize 25
```

Run the focused tests:

```powershell
C:\ProgramData\miniforge3\envs\sle-bcell\python.exe -m unittest -v `
  audit_tools.test_rp_v3_stage0_freeze `
  audit_tools.test_rp_v3_stage0b `
  audit_tools.test_rp_v3_wp1 `
  audit_tools.test_rp_v3_wp2_prefit `
  audit_tools.test_rp_v3_g2
```

Large public matrices and cell-level intermediates are intentionally outside
Git. A checkout alone is not sufficient for a complete rerun; restore inputs
using [Data/README.md](Data/README.md) and verify the recorded checksums.

## Canonical objects

| Purpose | Canonical location |
|---|---|
| Current project status | [`00_project_management/RP_V3_REDESIGN_STATUS.md`](00_project_management/RP_V3_REDESIGN_STATUS.md) |
| Full file audit | [`00_project_management/full_project_audit_2026-10-10/FINAL_FULL_PROJECT_AUDIT_2026-10-10.md`](00_project_management/full_project_audit_2026-10-10/FINAL_FULL_PROJECT_AUDIT_2026-10-10.md) |
| Valuable asset register | [`00_project_management/VALUABLE_ASSET_REGISTER_2026-10-10.csv`](00_project_management/VALUABLE_ASSET_REGISTER_2026-10-10.csv) |
| Manuscript source baseline | [`01_manuscript/Manuscript.md`](01_manuscript/Manuscript.md) |
| Supplementary source baseline | [`01_manuscript/Supplementary_Information.md`](01_manuscript/Supplementary_Information.md) |
| Stage 0 output | [`phase17_v7/rp_v3_redesign/20261009_stage0/`](phase17_v7/rp_v3_redesign/20261009_stage0/) |
| Stage 0B output | [`phase17_v7/rp_v3_redesign/20261009_stage0b/`](phase17_v7/rp_v3_redesign/20261009_stage0b/) |
| WP1 prefit contract | [`phase17_v7/rp_v3_redesign/20261010_wp1_prefit_contract/`](phase17_v7/rp_v3_redesign/20261010_wp1_prefit_contract/) |
| WP1 result | [`phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/`](phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity/) |
| WP2 effect-free preflight and G2 registries | [`phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/`](phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/) |
| G2 implementation/domain freeze | [`phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/`](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/) |
| Reproducibility detail | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |

## Repository layout

- `00_project_management/`: decisions, action records, audits and status files.
- `01_manuscript/`: editable manuscript, supplement and proposal sources.
- `02_analysis/`: environment, data acquisition and analysis runbooks.
- `03_results/`: compact retained result assets.
- `04_submission/`: author-facing sources and preserved historical packages;
  generated packages are local unless explicitly tracked.
- `05_Record/`: historical conversation/work records; useful for provenance but
  not authoritative scientific evidence.
- `audit_tools/`: executable analysis, build, validation and audit code.
- `phase17_v7/`: machine-readable gate outputs and scientific run records.
- `Data/`: retrieval guide plus Git-ignored public-data caches.

## Workspace audit

The 10 October 2026 full audit hashed and structurally checked every regular
workspace file outside `.git` and the audit-output directory. At scan time it
covered 7,850 files (5.687 GiB): 7,433 directly validated files, five separately
validated HDF5/H5AD containers, one benign empty package marker and 411
binary/compiled-cache files without a format-specific parser. No corrupt JSON,
CSV, ZIP/OOXML, PDF,
image, gzip, tar, NPZ or HDF5 object was found.

Large duplicate groups account for approximately 340 MiB, mainly historical
submission copies and render/portability tests. They are retained locally for
provenance and excluded from new Git tracking. Deep third-party QiTeng runtime
copies generated 119 Windows paths longer than 240 characters and are also kept
outside Git. See the [full audit](00_project_management/full_project_audit_2026-10-10/FINAL_FULL_PROJECT_AUDIT_2026-10-10.md).

## Public reproducibility archive

The immutable public reference remains:

- [GitHub release v1.1.0](https://github.com/1209433622cz-maker/sle-bcell-remodeling/releases/tag/v1.1.0)
- [Zenodo version DOI 10.5281/zenodo.22151739](https://doi.org/10.5281/zenodo.22151739)
- [Zenodo concept DOI 10.5281/zenodo.22086891](https://doi.org/10.5281/zenodo.22086891)

This release predates RP v3 and must be cited as a historical reproducibility
snapshot, not as the final output of the active redesign.

## Licence

Original code is MIT licensed. Original manuscript text, composite figures,
project documentation and project-generated derived source-data tables are CC
BY 4.0. Public GEO/CELLxGENE data and third-party material are excluded from
those project licences; see [LICENSE_SCOPE.md](LICENSE_SCOPE.md).
