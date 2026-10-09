# RP v3 Stage 0B protocol freeze and minimal-trial action record

**Date:** 2026-10-09
**Workspace:** `H:\cuhk-2025fALL\6013RP-wyf`
**Research-plan baseline:** `SLE_Bcell_RP_v3_定向科学重设计研究计划书_20261009.docx`
**Stage:** `SCIENTIFIC_REDESIGN_STAGE0B_PROTOCOL_AND_MINIMAL_TRIAL`
**Final decision:** `PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY`

## 1. Objective and governance boundary

This round implemented the next stage authorized by the RP v3 Stage 0 audit. The
goal was to close the protocol-level open fields and test whether the proposed
identity and score definitions are technically identifiable before estimating any
new disease effect.

The following boundaries were enforced:

1. A1 and A2 construction used no disease or outcome columns.
2. The trial inspected structural concordance, coverage, score computability and
   simulation truth recovery only.
3. No disease coefficient, annotation effect, external case-control score
   difference or new biological claim was estimated.
4. The current manuscript, figures, supplementary material, submission package,
   GitHub release and Zenodo record were not modified.
5. Historical fine-state failure remains valid and was not converted to PASS.

## 2. Protocol objects frozen

### 2.1 A1 continuous identity axis

A1 was frozen as a continuous signed 14-gene score from the existing
disease-blind dictionary:

- Positive pole: `CD27`, `TNFRSF13B`, `AIM2`, `BANK1`, `CD40`, `LTB`, `GPR183`.
- Negative pole: `TCL1A`, `IL4R`, `FCER2`, `CCR7`, `SELL`, `CXCR4`, `VPREB3`.
- Cell transform: full-library counts per 10,000, then `log1p`.
- Standardization: gene-wise mean and population SD across all 150,402
  disease-blind cells.
- Score: mean positive-gene z score minus mean negative-gene z score.
- Five global quantile bins are permitted only as a support and standardization
  scaffold. They are not biological subtypes and have no publication labels.

### 2.2 A2 IFN-excluded representation

A2 was frozen from the historical `hvg_isg_excluded` list:

- 3,000 HVGs.
- Zero strong-ISG features.
- Zero immunoglobulin features and zero prespecified technical-nuisance features.
- Full 150,402-cell reconstruction.
- PCA followed by Harmony on `library_uuid`, 15-neighbor graph and Leiden
  resolution 0.4.
- No HVG reselection and no outcome-adaptive tuning.

The correct normalization order is now explicit and machine-checked:

1. use the historical 16,357-gene post-filter background;
2. compute each cell's library-size factor on that complete background;
3. normalize to 10,000 and apply `log1p`;
4. select the frozen 3,000 A2 features afterward.

### 2.3 T0, T_frozen and T_rank

- `T0`: `log2(full-background CPM + 0.5)` for the 12 frozen IFN/ISG genes,
  standardized once using 43 A0 normal-control strata. A1 and A2 are prohibited
  from branch-specific restandardization.
- `T_frozen`: the same discovery control means and SDs applied to external
  source-label B_CONV pseudobulk. No external outcome-dependent scaling.
- `T_rank`: mean percentile rank of the same 12 genes over a fixed intersection
  of 18,873 discovery/external gene symbols, with duplicate symbols summed.

### 2.4 Common support and reference composition

- Minimum A1 donor-bin support: 30 cells.
- Structural minimum: 20 independent donors per bin overall.
- Future inferential minimum: 10 independent donors per comparison arm per bin.
- Unsupported rows must be removed with reasons; bins cannot be merged after
  viewing an effect.
- `pi_ref` is the pooled supported A1-bin composition among A0 normal controls.

The frozen `pi_ref` values are:

| A1 bin | pi_ref |
|---:|---:|
| 1 | 0.141064 |
| 2 | 0.160787 |
| 3 | 0.198034 |
| 4 | 0.251417 |
| 5 | 0.248699 |

## 3. Technical trial results

### 3.1 A1 support

- Scores were finite for 150,402/150,402 cells.
- All 14 genes were present, with 7 genes per sign.
- The five bins retained 72, 78, 84, 85 and 83 supported donors.
- Minimum future arm support was 33 normal and 39 managed donors.
- Every prespecified A1 structural and future-arm support check passed.

### 3.2 A2 reconstruction

- Corrected A2 shape: 150,402 cells by 3,000 frozen features.
- Resolution 0.4 clusters: 5.
- A0-A2 ARI: 0.795448.
- A0-A2 NMI: 0.680148.
- Minimum cluster support: 691 cells and 189 donors.
- Strong-ISG features: 0.

This exceeds the Stage 0B structural gate of ARI at least 0.70 while preserving
the original outcome-blind representation contract.

### 3.3 Score transfer

- T0 was finite in all 89 discovery strata using 43 frozen reference controls.
- T_frozen was finite in all 54 eligible external source-label B_CONV rows.
- T_rank was finite in all discovery and external rows.
- Program coverage was 12/12 in both datasets.
- No score was summarized by disease group and no disease coefficient was fitted.

### 3.4 Simulation

Five technical scenarios were run with 400 replicates each:

1. null effect;
2. composition only;
3. within-state effect only;
4. composition and within-state effects in the same direction;
5. composition and within-state effects in opposite directions.

Across the broad, common-composition and three state-specific estimands:

- maximum absolute bias: 0.002315;
- empirical 95% coverage range: 0.925 to 0.970;
- fit failure rate: 0;
- all required outputs were finite.

This is a technical truth-recovery pass only. It is not a full G2 operating-
characteristics authorization.

## 4. Implementation incidents and corrective actions

### 4.1 Harmony orientation compatibility

`harmonypy 0.2.0` returned corrected coordinates as cells by PCs, whereas the
historical fitter assumed PCs by cells. The shared fitter was repaired to validate
both orientations by dimension. It now also records Harmony version/device and
supports an explicit device argument.

### 4.2 Initial A2 denominator error

The first minimal A2 object was normalized after restricting to 3,000 genes. It
produced 6 clusters and A0-A2 ARI 0.446, so G1 correctly returned HOLD. A CPU
repeat of that same incorrect object produced ARI 0.405 and did not repair the
failure.

Source review showed that the historical normalization denominator was the
16,357-gene post-filter background. After correcting that order and rebuilding
from raw counts, A2 returned 5 clusters and ARI 0.795. The failed objects were
treated as diagnostics and never used as scientific outputs.

### 4.3 Legacy runtime diagnostic

An isolated `harmonypy 0.0.10` diagnostic was attempted before the denominator
error was identified. It stopped in legacy `sklearn.KMeans` with Windows native
OpenMP exit code `-1066598273`; no legacy output entered the analysis. The root
cause was subsequently resolved at the source-normalization layer using the
current frozen runtime.

## 5. QA and integrity

- Workflow rerun after completion reused the valid A2 checkpoint and reproduced
  the same gate decision.
- Independent test suite: 6/6 PASS.
- Integrity manifest: all listed files present and SHA-256 verified.
- Canonical A2 prepared H5AD SHA-256:
  `FA23FAB973B96A9B128F251B3F0FF946D03BD34F12B90EC39AECC2A967C12256`.
- Canonical A2 fitted H5AD SHA-256:
  `4943C575EB010572FA874864FD8258624310E077D5AF439EDA0C446C1A1B5F59`.
- Gate status SHA-256:
  `D7459854930ECD31CA4FB1D70A58FC8C880A9F69E3A59EDB1234C68BACEC84D8`.
- Final output tree at audit time: 60 files, 270,504,028 bytes. This count includes
  explicitly noncanonical diagnostic objects that are excluded from the integrity
  manifest and scientific decision.

## 6. Files created or changed

Core scripts:

- `audit_tools/rp_v3_stage0b_01_freeze_protocol.py`
- `audit_tools/rp_v3_stage0b_02_minimal_trial.py`
- `audit_tools/rp_v3_stage0b_03_legacy_harmony_repair.py`
- `audit_tools/run_rp_v3_stage0b.ps1`
- `audit_tools/test_rp_v3_stage0b.py`
- `audit_tools/phase17_c2b_08_fit_representation.py` compatibility repair

Canonical output root:

- `phase17_v7/rp_v3_redesign/20261009_stage0b`

Key review files:

- `01_STAGE0B_PROTOCOL_FREEZE.md`
- `14_STAGE0B_GATE_STATUS.json`
- `14_STAGE0B_ADVISOR_REVIEW.md`
- `15_STAGE0B_INTEGRITY_MANIFEST.csv`
- `16_STAGE0B_IMPLEMENTATION_INCIDENTS.md`
- `17_WP1_ANNOTATION_SENSITIVITY_EXECUTION_CONTRACT.md`

## 7. Gate decision

- `G0A_INPUT_RECOVERY = PASS`
- `G0B_PROTOCOL_FREEZE = PASS`
- `G0_OVERALL = PASS_G0`
- `G1 = PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY`
- `WP4 = HOLD_CONDITIONAL`
- `SUBMISSION = HOLD`

G1 PASS means only that A1/A2 are sufficiently defined and technically
identifiable to estimate the prespecified annotation-sensitivity estimands. It
does not validate fine states, authorize hard subtype names, rescue any historical
HOLD, or justify manuscript revision.

## 8. Next-stage decision

The next stage is:

`SCIENTIFIC_REDESIGN_WP1_ANNOTATION_SENSITIVITY`

The exact execution contract has already been frozen. WP1 should:

1. map A2 clusters to the A0 broad scaffold by disease-blind cell overlap;
2. build A0/A1/A2 common-support pseudobulks;
3. apply the identical frozen T0 reference in every branch;
4. estimate `beta_A0`, `beta_A1`, `beta_A2`, `delta_beta_ann_A1` and
   `delta_beta_ann_A2` in the same 89-donor primary design;
5. run 2,000 paired donor-clustered bootstrap replicates;
6. report continuous estimates and intervals without inventing an equivalence
   margin;
7. stop on mapping, common-support, transform or bootstrap-contract failure.

Manuscript and figure work should remain closed until WP1 and later RP v3 gates
show that a redesigned scientific claim is both valid and materially informative.
