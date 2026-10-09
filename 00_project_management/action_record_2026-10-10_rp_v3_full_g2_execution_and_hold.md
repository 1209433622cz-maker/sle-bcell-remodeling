# Action record: RP v3 full-G2 execution and HOLD adjudication

**Date:** 2026-10-10

**Scope:** Complete the RP v3 G2 operating-characteristic grid, independently
verify the adjudication, preserve a compact tracked record and determine the
next authorized stage.

**Final decision:** `HOLD_G2_APPLICABLE_DOMAIN`

**Submission:** `HOLD`

**WP2 real effects:** locked and never loaded or fitted in this round.

## Starting point

The user supplied the completed R0 PowerShell log. The frozen implementation
gate had already passed under binding
`5546f5931069f2d09b784b0d365fa58c433a38c6e8edb5e7f5a55329585bfbf3`,
but the complete 25-scenario G2 grid had not yet been adjudicated. The Research
Plan v3 requires G2 to evaluate bias, interval coverage, exact-null type-I error,
support failure and numerical failure before real WP2 disease effects can be
opened.

The controlling RP v3 rules were re-read before final adjudication. They state
that poor coverage or systematic null rejection cannot be overridden by a small
real-data P value, that failed simulations must be retained, and that a repaired
model must be versioned and completely rerun rather than silently replacing the
failed version.

## R0 checkpoint audit

The five R0 scenarios contained all 10,000 planned outer attempts and all
20,000,000 planned inner paired-bootstrap fits. There were no support stops and
no numerical failures. Independent application of the frozen adjudicator gave
22 PASS and 28 HOLD target-scenario cells:

| Scenario | PASS | HOLD |
|---|---:|---:|
| C0_R0 | 10 | 0 |
| C1_R0 | 4 | 6 |
| C2_R0 | 0 | 10 |
| C3_R0 | 8 | 2 |
| C4_R0 | 0 | 10 |

All 50 R0 bias checks, all 50 truth-precision checks and all ten registered
exact-null type-I checks passed. Only 22/50 coverage checks passed. R0 was
therefore a valid operational checkpoint but not a G2 PASS.

## Runtime handling

An attempted front test in the Miniforge `sle-bcell` environment terminated in
NumPy linear algebra with Windows exception `0xc06d007f` before any simulation
output was created or changed. The run was returned to the previously validated
local runtime `D:\bioinfor\python.exe`:

- Python 3.13.7;
- NumPy 2.3.3;
- all ten focused G2 implementation tests passed before execution.

The runtime incident is documented as an environment failure, not a scientific
failure and not a reason to modify the frozen implementation.

## Complete synthetic execution

The existing hash-verified R0 chunks were reused. R1, R2, R3 and R4 were then
completed under the same binding, with no replenishment of support failures.

| Quantity | Result |
|---|---:|
| Registered scenarios | 25/25 |
| Chunks | 2,000 |
| Outer attempts | 50,000 |
| Interval-computed outer attempts | 30,053 |
| Prespecified support stops | 19,947 |
| Numerical failures | 0 |
| Paired-bootstrap fits attempted | 60,106,000 |
| Paired-bootstrap fits successful | 60,106,000 |
| Raw run files | 6,004 |
| Raw run size | 17,599,944 bytes |

R1 rarity support produced 10,000/10,000 support stops. R3 adjacent
mislabeling produced 53 interval-computed attempts and 9,947 support stops.
Both remain mandatory visible boundary domains and are not part of the
applicable-domain conjunction.

## Applicable-domain adjudication

R0, R2 and R4 contribute 150 applicable target-scenario cells.

| Criterion | PASS | FAIL/HOLD |
|---|---:|---:|
| Truth precision | 150 | 0 |
| Numerical stability | 150 | 0 |
| Bias | 149 | 1 |
| Coverage | 91 | 59 |
| Registered exact-null type-I | 10 | 0 |
| Final target-scenario decision | 90 | 60 |

The single bias failure was `C0_R4 / beta_bin_3`. All 59 coverage failures had
a Wilson lower bound below 0.925; none failed because the upper bound exceeded
0.975. The failure mode is therefore broad interval undercoverage. It is not a
truth-engine precision problem, numerical instability, support replenishment or
registered exact-null false-positive inflation.

Per applicable regime, R0 passed 22/50 target-scenario cells, R2 passed 33/50
and R4 passed 35/50. Every target was blocked in at least five of its 15
required scenarios. No target met the frozen conjunction and no target received
an unlock recommendation.

## Independent verification and retained outputs

The new downstream finalizer:

1. verified all 2,000 chunk manifests and payload hashes;
2. independently reran the complete adjudicator;
3. required all three official adjudication files to be byte-identical to the
   independently regenerated files;
4. audited all 50,000 unique outer attempt records and exact inner-fit counts;
5. confirmed that every chunk records `real_effects_fitted=false`;
6. generated scenario, target and boundary summaries, a run receipt, a
   next-stage contract and a SHA-256 manifest.

The compact tracked result is
`phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/`. The 6,004-file raw
run remains under the established Git-ignore rule at
`phase17_v7/rp_v3_redesign/g2_full_runs/20261010_full/`.

## Scientific and governance decision

The frozen percentile-bootstrap implementation does not meet the RP v3 G2
coverage contract across the applicable domain. The correct decision is
`HOLD_G2_APPLICABLE_DOMAIN`; it is not a partial PASS. Real WP2 disease effects
remain locked. Manuscript replacement, figure replacement, WP4, submission,
GitHub Release and Zenodo work remain closed.

This result is scientifically useful: it identifies a limitation of the
planned interval procedure before the real WP2 effects are seen. It must not be
rescued by weaker thresholds, deleted scenarios, additional random seeds near a
threshold or favorable real-data significance.

## Next-stage judgment

The next authorized goal is
`RP_V3_G2_HOLD_DIAGNOSTIC_AND_AMENDMENT_GATE`.

Permitted work is limited to synthetic/mathematical diagnosis of the interval
undercoverage and prospective freezing of at most one scientifically justified
replacement implementation. If a replacement is defensible, it must receive a
new binding and be evaluated over the unchanged 25-scenario contract using
fresh random streams before a separate post-G2B review. If no defensible repair
can be frozen, the RP v3 WP2 claim must be contracted. In both exits, the
current full-G2 HOLD remains permanent provenance.

## Files added or updated

- `audit_tools/rp_v3_g2_04_finalize_full_adjudication.py`
- `phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/`
- `00_project_management/RP_V3_REDESIGN_STATUS.md`
- `00_project_management/VALUABLE_ASSET_REGISTER_2026-10-10.csv`
- `README.md`
- `REPRODUCIBILITY.md`
- this action record

## Verification completed before repository close

- complete RP v3 unit-test set: 38/38 PASS in the validated runtime;
- independent full adjudication: byte-identical to all three official outputs;
- compact integrity manifest: 9/9 payloads matched size and SHA-256;
- raw attempt accounting: 50,000 unique attempts and 60,106,000/60,106,000
  successful inner fits;
- frozen raw run remained Git-ignored and was not staged;
- `git diff --check` passed;
- ordinary Git HTTPS push failed three times because the GitHub connection was
  reset or timed out. The already authenticated GitHub CLI API remained
  available, so the exact local tree was uploaded through the official Git Data
  API and `main` was fast-forwarded. The synchronized scientific/result commit
  before this documentation-only follow-up was
  `85c725281a17bffa35b2ec7e202ee691c036beba`; scientific/result tree:
  `ac63e80212d756610e3a744f52e9341c85a13fa4`.
