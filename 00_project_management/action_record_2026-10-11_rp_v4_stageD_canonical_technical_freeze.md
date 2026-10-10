# RP v4 Stage D canonical technical freeze action record

**Date:** 2026-10-11
**Workspace:** `H:\cuhk-2025fALL\6013RP-wyf`
**Input Git HEAD:** `e66c0bd073a7cacf708c4a909e74babeb9894507`
**Input remote baseline:** `origin/main=6bdadc06004cab1d10f59909cfb1fb8e2eb500e0`
**Outcome access:** locked throughout

## 1. Request and boundary

The user asked the project to continue under Research Plan v4 using the received
Stage D candidate. This round treated the ZIP and its reports as untrusted
evidence input, independently verified them, integrated only the supported code
into the repository and froze a project-side Stage D decision.

The following were deliberately not run or changed:

- no stage-141 160,000-attempt final G2C simulation;
- no stage-142 complete truth calculation;
- no real WP2 response, disease coefficient or interval;
- no external diagnosis, activity, treatment or score-direction analysis;
- no SRA download, FASTQ conversion, alignment or count reconstruction;
- no manuscript, figure, submission package, GitHub Release or Zenodo change;
- no rescue of any RP v3 G2/G2B, identity, transfer or mechanistic HOLD.

## 2. External candidate intake

Received archive:

`C:\Users\Administrator\Downloads\SLE_RPv4_StageD_G2C_TechnicalPilot_20261010.zip`

| Check | Result |
|---|---:|
| ZIP size | 162,441 bytes |
| ZIP SHA-256 | `94b0c2a225111d89c3110cd424668dec0bf1bc50b3749c86e59c5b4e8816ff5b` |
| ZIP entries | 87 |
| Uncompressed bytes | 510,740 |
| CRC failure | none |
| Controlled payload rows | 86 |
| Manifest size/hash failures | 0 |
| Unlisted package payloads | 0 |

The separately supplied `12_STAGE_D_ADVISOR_REVIEW.md` and
`13_STAGE_E_GO_NO_GO_CONTRACT.md` were byte-identical to the package copies.
Their SHA-256 values were respectively:

- `339a77575bdf06e50597219925ce233f1689f0ac433a71423827573f54b21669`;
- `4d9bf821e3b1500e9f67525c408a893c7cf183a681e77d7fd75a63032c1c326f`.

Six packaged Stage C inputs were byte-identical to the current canonical Stage C
files: method contract, 40-DGP registry, seed/compute contract, external-input
manifest, S0/S1 measurement contract and Stage D pilot protocol. The candidate
was therefore internally coherent with the repository authority, but remained
non-authoritative until project-side replay.

## 3. Code review and integration decision

The received package contained a second HC3-t implementation. It was numerically
equivalent in the tested cases but was not promoted because Stage C already binds
`audit_tools/rp_v4_g2c_hc3t.py` as the sole canonical estimator. Maintaining two
primary kernels would create avoidable code-authority ambiguity.

The project instead integrated:

- `audit_tools/rp_v4_g2c_generator.py`: hash-bound 40-DGP generator with only
  development stage 131 exposed;
- `audit_tools/rp_v4_g2c_truth.py`: independent Philox development oracle that
  does not import the generator, estimator or regression kernel;
- `audit_tools/rp_v4_stageD_pilot.py`: atomic checkpoints, resume verification,
  technical accounting and selected-oracle receipts;
- `audit_tools/rp_v4_stageD_sra_plan.py`: plan-only SRA ledger with no execution
  switch;
- `audit_tools/test_rp_v4_stageD.py`: project-side fail-closed regression tests;
- `audit_tools/run_rp_v4_stageD.ps1`: one-command technical-only entry point;
- `audit_tools/rp_v4_stageD_freeze.py`: canonical freeze and integrity builder.

The generator preserved all 25 legacy scenario counters byte-for-byte at the
first registered development attempt. The three new stresses remained exactly:

1. X1 gamma-Poisson category-level overdispersion;
2. X2 correlated donor/bin capture heterogeneity; and
3. X3 nonadjacent label contamination.

Final stage 141 remains inaccessible from the Stage D generator. The oracle uses
a separate Philox address and leaves final stage 142 untouched.

## 4. Windows runtime qualification

The first independent replay under
`C:\ProgramData\miniforge3\envs\sle-bcell\python.exe` did not complete. The X2
correlated-capture test terminated the process with native exit code
`0xC06D007F` on the NumPy/LAPACK Cholesky path. This is a runtime qualification
failure, not a scientific simulation result.

The same test and the complete project-side suite passed under:

`D:\bioinfor\python.exe`

Runtime versions:

- Python 3.13.7;
- NumPy 2.3.3;
- SciPy 1.16.2;
- statsmodels 0.14.6.

This interpreter is the only Windows runtime qualified by Stage D. The
Miniforge `sle-bcell` environment must not be used for final G2C unless repaired
and separately requalified.

## 5. Independent tests and technical replay

The combined canonical Stage C/Stage D suite passed 22/22 tests. It covered:

- 40-scenario registry identity and 30/10 adjudication split;
- final-stream refusal and real-response refusal;
- 25/25 legacy generator counter parity;
- X1/X2/X3 shape, determinism and transition semantics;
- registry-hash tamper refusal;
- direct HC3 agreement with statsmodels;
- exact `delta_profile = beta_profile - beta_pooled` algebra;
- oracle import independence and C0 exact symmetry;
- plan-only SRA behavior and overwrite refusal; and
- unchanged Stage C method, seed and outcome locks.

The canonical 24-attempt development pilot returned:

| Scenario | Attempts | Supported | Support stop | Numerical failure |
|---|---:|---:|---:|---:|
| C0_X1 | 8 | 8 | 0 | 0 |
| C1_X2 | 8 | 8 | 0 | 0 |
| C2_X3 | 8 | 2 | 6 | 0 |
| Total | 24 | 18 | 6 | 0 |

The six X3 support stops are expected protocol stops under a stress case. They
are not software failures, but they also cannot be interpreted as evidence that
the X3 domain passes.

A separate run wrote attempts 1-4, resumed to attempts 1-8 and was compared to a
fresh eight-attempt run. All 28 stable files were byte-identical. The received
package's own fresh-versus-resume comparison was also independently rechecked at
28/28 byte-identical files.

When the received Linux-origin numerical outputs were compared with the
project-side Windows output, all 24 synthetic input digests and all 24 support
statuses matched. Maximum absolute differences were `1.39e-16` for the point
estimate, `6.94e-18` for the HC3 standard error and `1.67e-16` for confidence
limits. These are lower-order floating-point/runtime differences, not a change
in scientific or gate status.

## 6. Independent technical truth result

Three selected development-stage cases used 32,768 coupled attempts per arm:

| Scenario | Truth status | MCSE / typical SE | Interpretation |
|---|---|---:|---|
| C0_X1 | exact symmetry | 0 | technical precision PASS |
| C1_X2 | paired independent oracle | 0.008694 | technical precision PASS |
| C2_X3 | paired independent oracle | 0.007037 | technical precision PASS |

This qualifies only the implementation and selected truth precision. It is not
the full 40-scenario truth table, does not consume stage 142 and cannot support a
bias, coverage, type-I or G2C PASS claim.

## 7. External raw-input plan

The official hash-bound RunInfo inputs produced a plan-only ledger:

| BioProject | Runs | Experiments | Reported SRA size |
|---|---:|---:|---:|
| PRJNA1093470 / GSE262846 | 176 | 88 | 233.209 GB |
| PRJNA484963 / GSE118254 | 85 | 83 | 64.365 GB |
| Total | 261 | 171 | 297.574 GB |

The studies remain potentially donor-overlapping and cannot be counted as two
independent confirmations. At least 2.5 TB scratch remains the planning floor.
No download or biological outcome join occurred.

## 8. Canonical artifacts

Canonical Stage D directory:

`phase17_v7/rp_v4_redesign/20261011_stageD_canonical_technical_freeze/`

It contains:

- external-candidate intake receipt;
- complete source/code/contract SHA-256 binding;
- Windows runtime qualification and disqualification record;
- technical attempt accounting;
- selected independent-oracle receipt;
- SRA resource ledger and plan-only receipt;
- 14-item Stage D checklist;
- machine-readable Stage D gate;
- unsigned Stage E author-signoff template;
- Stage D advisor review;
- Stage E preflight contract; and
- 12-payload integrity manifest.

The external package, replay directories and official RunInfo inputs remain
local evidence caches under Git-ignored paths. Only canonical compact evidence
and executable source are tracked.

## 9. Final verification

- Stage D checklist: 14/14 PASS.
- Canonical source bindings: 16/16 current size/SHA-256 matches.
- Canonical integrity manifest: 12/12 payloads verified.
- Canonical Stage C + Stage D focused tests: 22/22 PASS.
- Full `audit_tools/test_*.py` discovery under `D:\bioinfor\python.exe`:
  314 tests discovered, 313 passed and one import error caused solely by the
  absence of `anndata` in that runtime.
- The omitted dependency-sensitive C9 contract suite was then run under the
  `sle-bcell` environment and passed 9/9. Stage D itself was not rerun there
  because that runtime is explicitly disqualified on the X2 numerical path.
- Python compile check: PASS.
- Canonical JSON/CSV parse audit: 6 JSON and 5 CSV files PASS.
- `git diff --check`: PASS.
- Final stage-141 attempts: 0.
- Final stage-142 truth runs: 0.
- Real disease/activity models fitted: 0.

## 10. Gate decision

`PASS_RPV4_STAGE_D_CANONICAL_TECHNICAL_IMPLEMENTATION__HOLD_STAGE_E_AUTHOR_SIGNOFF_AND_FINAL_G2C`

All 14 Stage D checks passed. This means the implementation is suitable for an
execution-preflight review. It does not authorize or imply final G2C success.

Machine-readable lock state:

- `G2C_PASS=false`;
- `final_G2C_authorized=false`;
- `final_truth_authorized=false`;
- `WP2_REAL_EFFECT_UNLOCK=false`;
- `EXTERNAL_OUTCOME_UNLOCK=false`;
- `LARGE_SRA_DOWNLOAD_AUTHORIZED=false`;
- `MANUSCRIPT_REPLACEMENT=HOLD`;
- `SUBMISSION=HOLD`.

## 11. Next-stage objective

Proceed to:

`RPV4_STAGE_E__AUTHOR_SIGNOFF_AND_FINAL_G2C_PREFLIGHT`

Stage E must:

1. obtain explicit author approval of every field in the exact signoff template;
2. implement and hash-bind the complete stage-142 truth runner;
3. implement and hash-bind the stage-141 runner plus an independent
   adjudicator;
4. test checkpoint/resume, overwrite refusal, support-stop/numerical-failure
   separation and real-response rejection on non-final streams;
5. benchmark runtime/storage without consuming stage 141/142; and
6. issue a separate `GO_FOR_FULL_SYNTHETIC_G2C` only if every preflight gate
   passes.

Even that later GO will authorize only synthetic validation. It will not
automatically unlock real WP2 effects, external disease/activity analyses,
large SRA download, manuscript replacement or submission.
