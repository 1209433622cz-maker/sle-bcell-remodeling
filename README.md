# Disease-blind analysis of B-cell remodeling in systemic lupus erythematosus

This repository contains the auditable analysis, scientific-governance records,
manuscript sources and compact derived results for a hierarchy-aware single-cell
study of B-cell remodeling in systemic lupus erythematosus (SLE).

Repository: [1209433622cz-maker/sle-bcell-remodeling](https://github.com/1209433622cz-maker/sle-bcell-remodeling)

## Current status

**Active state on 10 October 2026:**
`ACTIVE_RP_V4_SCIENTIFIC_REDESIGN / HOLD_SUBMISSION`.

The public v1.1.0 archive and the September scientific-presentation baseline are
retained as historical, reproducible snapshots. They are not being silently
rewritten. RP v3 is retained as a completed bounded record: G2B improved the
applicable-domain result from 90/150 to 133/150 PASS target-scenario rows but did
not pass its frozen conjunction, and WP3 ended with outcome-blind pooled
measurement diagnostics only.

The active project now follows Research Plan v4 as a separate prospective
branch. Stage A verified the proposal bundle, carried forward every RP v3 HOLD,
diagnosed the 17 G2B failures and audited official GEO metadata. Stage C has now
frozen exactly one G2C estimand and one method, independent final random streams,
40 data-generating scenarios, S0/S1 measurement handling and a fail-closed raw
input protocol. No final G2C run or real disease/activity model has been run.
Manuscript replacement, submission, GitHub Release and Zenodo updates remain on
hold.

Current gate:

```text
PASS_RPV4_STAGE_C_PROTOCOL_FREEZE__AUTHOR_SIGNOFF_REQUIRED_BEFORE_FINAL
```

Next stage:

```text
RPV4_STAGE_D__G2C_IMPLEMENTATION_AND_EXTERNAL_RAW_INTAKE_TECHNICAL_PILOT
```

## Scientific position

The stable historical conclusion remains **reproducible process-level B_CONV
IFN/ISG remodeling**, bounded by three permanent limitations:

Historical scientific-presentation title: **Disease-blind reconstruction
distinguishes reproducible interferon remodeling from unstable B-cell state
assignments in systemic lupus erythematosus**.

End-to-end resampling did not meet the frozen identity criterion: the B_ASC median Jaccard was 0.930, below 0.95.
This historical HOLD remains in force.

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

## RP v4 progress

### Stage C: single G2C and external-input protocol freeze

- Selected only `delta_profile`, because its historical G2B point-bias gate
  passed in all 15 applicable scenarios and its residual failures were confined
  to interval coverage. `delta_cellref` was not selected because it mixed
  coverage and point-bias failures.
- Replayed the exposed historical development stream. Bootstrap-SE p01/median
  was at least 0.532, maximum point leverage was 0.105, no inner diagnostic fit
  failed, and the direct delta equalled the coefficient difference to within
  `4.57e-15`. This argues against a collapsed studentizer or non-smooth target.
- Froze one method: direct donor-level `delta_profile` OLS with HC3 influence
  variance and a two-sided `t(64)` interval. It passed 15/15 exposed applicable
  development cells, but this is explicitly not forward confirmation.
- Registered a new seed base, 25 old-comparable plus 15 shifted DGPs and 4,000
  outer attempts per scenario (160,000 total). The final run is not authorized.
- Reconciled official NCBI SRA RunInfo: GSE262846 has 176 runs/88 experiments
  (about 233.21 GB SRA) and GSE118254 has 85 runs/83 experiments (about 64.37 GB).
  Raw reconstruction is feasible but pending; both outcome tables remain locked.
- Conservatively treat the two candidates as potentially donor-overlapping.
  GSE118254 cannot be counted as a second independent confirmation of GSE262846.
- Retained S0 as the primary frozen score and S1 as a technical sensitivity;
  S2 was abandoned because no unique result-blind formula could be justified.

Decision:
`PASS_RPV4_STAGE_C_PROTOCOL_FREEZE__AUTHOR_SIGNOFF_REQUIRED_BEFORE_FINAL`.

See the [Stage C advisor review](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/12_RPV4_STAGE_C_ADVISOR_REVIEW.md),
[method contract](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json),
[external-input contract](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/08_EXTERNAL_RAW_RECONSTRUCTION_AND_PROVENANCE_CONTRACT.md)
and [machine-readable gate](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/11_RPV4_STAGE_C_GATE_STATUS.json).

### Stage A: authority, historical diagnosis and external feasibility

- Rechecked all ten files in the external RP v4 proposal manifest by byte size
  and SHA-256; the bundle is evidence input, not a self-authorizing gate.
- Verified that the local RP v3 WP3 commit is accessible and descends directly
  from the current `origin/main`, correcting the proposal candidate's stale
  authority statement.
- Reproduced the historical G2 90/150 and G2B 133/150 applicable-cell counts.
- Classified all 17 G2B failures from the 2,000-attempt raw outputs: 11 coverage
  failures, six bias failures and one exact-null type-I failure overlapping a
  coverage failure.
- Localized residual undercoverage to nine `delta_profile` and two
  `delta_cellref` cells. The misses are mild and broadly two-sided; the frozen
  outputs do not identify a unique corrective interval.
- Parsed official GEO MINiML metadata for five candidate accessions. The two
  leading bulk candidates have recoverable donor structures, but neither is
  authorized for outcome analysis until raw-count compatibility and provenance
  independence are resolved.
- Retained `S0=T_frozen` as the primary measurement anchor and `S1=T_rank` as a
  sensitivity. S2 was not admitted because no unique result-blind formula exists.

Decision:
`PASS_RPV4_STAGE_A_AND_V4B_HISTORICAL_DIAGNOSIS__HOLD_G2C_AND_NEW_COHORT_OUTCOMES`.

See the [Stage A advisor review](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/11_RPV4_STAGE_A_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/10_RPV4_STAGE_A_GATE_STATUS.json)
and [next protocol requirements](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md).

## RP v3 historical progress

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

### G2 implementation, full execution and adjudication

The sufficient-count generator, actual paired-bootstrap estimator and an
independent nonlinear truth engine are now hash-bound. Independent Windows
requalification reproduced all 50 pilot statuses, 60,000/60,000 successful
inner fits and 250/250 truth-precision passes. Generated counts and bootstrap
indices were byte-identical across platforms; the largest floating-point
difference was `8.88e-16`.

R0, R2 and R4 are frozen as the applicable performance domain. R1 and R3 remain
mandatory boundary domains and cannot be deleted or rescued. The complete grid
then ran 50,000 outer attempts and 60,106,000 paired-bootstrap fits with no
numerical failures. Of 150 applicable target-scenario cells, 90 passed and 60
were held. Coverage passed in 91/150 cells; all 59 coverage failures were
undercoverage. Bias passed in 149/150, truth precision in 150/150 and registered
exact-null type-I control in 10/10. None of the ten targets passed all 15
required applicable scenarios, so no WP2 real effect is unlocked.

Decision:
`HOLD_G2_APPLICABLE_DOMAIN`.

See the [G2 implementation review](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/10_G2_IMPLEMENTATION_ADVISOR_REVIEW.md),
[execution contract](phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/08_G2_EXECUTION_CONTRACT.json)
and [full-G2 post-adjudication review](phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/08_G2_POST_ADJUDICATION_REVIEW.md).

### G2B full execution and scope contraction

The G2 HOLD was diagnosed without reading real WP2 outcomes. Exactly one
replacement was selected on methodological grounds: an equal-tailed paired
donor bootstrap-t interval with an HC3 studentizer. The point estimator,
generator, ten targets, 25 scenarios, truth table, applicable/boundary split and
all acceptance thresholds remain unchanged.

The external candidate archive passed 901/901 payload checks and 42/42 tests.
On Windows, the 150-object development replay reproduced 90 supported intervals,
60 support stops and 180,000 inner attempts with no numerical failures. A further
4,500 explicit expanded-row statsmodels fits agreed with the vectorized HC3
kernel. The canonical Stage 0 through G2B test suite passed 58/58 tests.

The project-side `rp_v3_g2b_*` implementation used a hash-bound stage-121 random
namespace and rejected old G2 bindings. The full grid completed 25/25 scenarios,
2,000/2,000 chunks, 50,000 outer attempts and 60,112,000 successful inner
bootstrap draws with no numerical failures. Formal and independent adjudications
were byte-identical.

Among 150 applicable target-scenario rows, 133 passed and 17 held. Coverage
failures fell from 59 under G2 to 11 under G2B, but six bias failures and one
overlapping exact-null type-I failure remained. Four targets passed 15/15
applicable scenarios; partial target unlock was not part of the frozen contract.
The final decision therefore keeps `WP2_REAL_EFFECT_UNLOCK=false`.

Decision:
`HOLD_G2B_APPLICABLE_DOMAIN`.

See the [G2B post-adjudication review](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/09_G2B_POST_ADJUDICATION_REVIEW.md),
[machine-readable decision](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/03_G2B_FINAL_DECISION.json)
and [scope-contraction contract](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/10_G2B_SCOPE_CONTRACTION_CONTRACT.md).

### WP3 result-blind available-object prefit

The project-side prefit passed 22/22 checks without computing new external
scores, disease-group summaries, coefficients, intervals or P values. It bound
56 unique source donors, exact eight-label-to-B_CONV closure, 54 min50-eligible
objects and a 43-donor childhood primary design (11 controls and 32 SLE donors).
All 12 IFN genes and 18,873 frozen rank-background symbols are present. The
source `T_rank` convention is now explicitly verified as average rank divided by
the fixed background size.

Decision:
`PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION`.

See the [WP3 prefit advisor review](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/12_WP3_PREFIT_ADVISOR_REVIEW.md),
[gate status](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/10_WP3_PREFIT_GATE_STATUS.json)
and [measurement-scope protocol](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/11_WP3_EFFECT_FREE_MEASUREMENT_SCOPE_PROTOCOL.md).

### WP3 pooled measurement diagnostics

The project-side pooled stage passed 13/13 focused tests, 25/25 real-input checks
and 4,389/4,389 independent numerical comparisons. Across 54 eligible objects,
`T_frozen` versus `T_rank` pooled Spearman correlation was 0.985744 and the
maximum rank displacement was 6. All 12 leave-one-gene-out correlations were at
least 0.995883. These are pooled measurement diagnostics, not a disease effect,
clinical calibration or cross-platform validation.

Decision:
`PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION`.

See the [pooled-measurement advisor review](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/14_WP3_POOLED_MEASUREMENT_ADVISOR_REVIEW.md),
[machine-readable gate](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/12_WP3_MEASUREMENT_GATE_STATUS.json)
and [scope-closure recommendation](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/15_RP_V3_SCOPE_CLOSURE_RECOMMENDATION.md).

## Next gate: G2C implementation and external raw-intake technical pilot

The next action is implementation qualification only: implement the frozen
shifted DGPs and truth engine, run a small non-adjudicative technical pilot and
generate resumable SRA download/count scripts. Final G2C execution, large raw
download, real WP2 effects, new-cohort disease/activity effects, WP4, manuscript
replacement and submission remain unauthorized until a later explicit gate.

## Reproduce the active redesign

Create or check the scientific environment first:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_create_conda_env.ps1
```

Reproduce the active RP v4 Stage A gate after restoring the ignored proposal
evidence and official MINiML files recorded by the action report:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v4_stageA.ps1
```

Reproduce the exposed Stage C development diagnosis in a new directory, then
verify the tracked frozen contract with its focused regression tests:

```powershell
python .\audit_tools\rp_v4_stageC_01_development_diagnostic.py `
  --output-dir .\phase17_v7\rp_v4_redesign\stageC_development_reproduction

& 'C:\ProgramData\miniforge3\envs\sle-bcell\python.exe' `
  -m unittest discover -s audit_tools -p 'test_rp_v4_g2c.py' -v
```

Run the completed gates from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_stage0.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_stage0b.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_wp1.ps1
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_wp2_prefit.ps1 `
  -OutputDir .\phase17_v7\rp_v3_redesign\wp2_prefit_reproduction

& .\audit_tools\run_rp_v3_g2_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2_full_runs\20261010_full `
  -Regimes @('R0','R1','R2','R3','R4') `
  -ChunkSize 25 `
  -Adjudicate

D:\bioinfor\python.exe `
  .\audit_tools\rp_v3_g2_04_finalize_full_adjudication.py `
  --run-root .\phase17_v7\rp_v3_redesign\g2_full_runs\20261010_full `
  --output-dir .\phase17_v7\rp_v3_redesign\g2_full_adjudication_reproduction

& .\audit_tools\run_rp_v3_g2b_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2b_full_runs\20261010_stage121_full `
  -ValidateOnly

& .\audit_tools\run_rp_v3_g2b_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2b_full_runs\20261010_stage121_full `
  -Regimes @('R0','R1','R2','R3','R4') `
  -ChunkSize 25 `
  -Adjudicate
```

Run the focused tests:

```powershell
D:\bioinfor\python.exe -m unittest -v `
  audit_tools.test_rp_v3_stage0_freeze `
  audit_tools.test_rp_v3_stage0b `
  audit_tools.test_rp_v3_wp1 `
  audit_tools.test_rp_v3_wp2_prefit `
  audit_tools.test_rp_v3_g2 `
  audit_tools.test_rp_v3_g2b `
  audit_tools.test_rp_v4_g2c
```

Large public matrices and cell-level intermediates are intentionally outside
Git. A checkout alone is not sufficient for a complete rerun; restore inputs
using [Data/README.md](Data/README.md) and verify the recorded checksums.

## Canonical objects

| Purpose | Canonical location |
|---|---|
| Current project status | [`00_project_management/RP_V4_REDESIGN_STATUS.md`](00_project_management/RP_V4_REDESIGN_STATUS.md) |
| RP v4 Stage A authority/feasibility freeze | [`phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/`](phase17_v7/rp_v4_redesign/20261010_stageA_authority_feasibility_freeze/) |
| RP v4 Stage C method/input protocol freeze | [`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/`](phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/) |
| Historical RP v3 status | [`00_project_management/RP_V3_REDESIGN_STATUS.md`](00_project_management/RP_V3_REDESIGN_STATUS.md) |
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
| Full G2 adjudication and next-stage contract | [`phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/`](phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/) |
| G2B single-method protocol freeze | [`phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/`](phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/) |
| Full G2B adjudication and scope-contraction contract | [`phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/`](phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/) |
| WP3 effect-free prefit and measurement-scope contract | [`phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/`](phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/) |
| WP3 pooled measurement diagnostics and scope recommendation | [`phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/`](phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/) |
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
