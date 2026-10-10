# RP v4 Stage F2 integrity hardening action record

**Date:** 2026-10-11

**Scope:** synthetic-only integrity engineering and non-final qualification

**Decision:** `PASS_STAGE_F2_INTEGRITY_HARDENING_AND_REBIND__HOLD_POST_COMMIT_EXACT_CODE_GO`

## 1. Objective and authority boundary

This round independently assessed the uploaded Stage F exact-code review,
reproduced its material findings, repaired the identified integrity gaps in a
new additive F2 implementation and qualified that implementation on the
registered Windows runtime. It did not run final stage 141 or stage 142, fit a
real WP2 outcome, download SRA data, reopen WP4, alter the manuscript or rebuild
the submission package.

The scientific contract remains unchanged: the only estimand is
`delta_profile`; the only interval is donor-level OLS with HC3 variance and a
two-sided t interval with 64 degrees of freedom; the final grid is 40 scenarios
by 4,000 attempts; the seed base, thresholds, no-replenishment rule and no-G2D
stop rule remain frozen.

## 2. External Stage F intake

Input:
`C:/Users/Administrator/Downloads/SLE_RPv4_StageF_ExactCode_IntegrityReview_20261011.zip`

- ZIP size: 18,208 bytes.
- ZIP SHA-256:
  `ec099143d64d6058b3c19e6cfc3be6b2ca6f0015f083a8d4c7ddfd6a8a15d7e8`.
- CRC and path-safety checks: PASS.
- Manifest-controlled payloads: 7/7 size and SHA-256 matches.
- External decision retained as evidence:
  `HOLD_STAGE_F_EXACT_CODE_GO__INTEGRITY_HARDENING_REQUIRED`.

The package's focused test command returned 4/5 rather than the stated 5/5 on
this Windows host. The failing case was internal to the audit package: its test
used `Path.write_text()` and then compared the resulting platform-CRLF bytes
with an LF-only expected digest. The package was preserved unchanged. This
portability discrepancy does not invalidate its substantive integrity
findings, which were independently reproduced.

## 3. Confirmed Stage E2 integrity gaps

1. `audit_tools/rp_v4_g2c_truth.py` was called by the truth path but was absent
   from the Stage E2 source-binding manifest.
2. A matching Git HEAD did not prove a clean worktree or an exact match to the
   qualified executable and package environment.
3. Outer resume and final adjudication did not fully seal and reconcile each
   chunk, accounting table and receipt.
4. Truth output lacked a complete write-once checkpoint inventory and binding
   of the final truth CSV to its receipt.
5. The adjudicator needed an independent HC3-t(64) interval identity check,
   including df, method/data flags, leverage and outcome-lock conditions.

These findings are engineering and provenance blockers. They do not establish
failure or success of the G2C statistical method.

## 4. F2 implementation

F2 was added as a new namespace and did not overwrite the historical Stage E2
freeze. The implementation comprises:

- `audit_tools/rp_v4_stageF2_common.py`
- `audit_tools/rp_v4_stageF2_generator.py`
- `audit_tools/rp_v4_stageF2_runner.py`
- `audit_tools/rp_v4_stageF2_truth.py`
- `audit_tools/rp_v4_stageF2_adjudicator.py`
- `audit_tools/rp_v4_stageF2_adjudicate_run.py`
- `audit_tools/rp_v4_stageF2_preflight.py`
- `audit_tools/rp_v4_stageF2_freeze.py`
- `audit_tools/test_rp_v4_stageF2.py`
- `audit_tools/run_rp_v4_stageF2_preflight.ps1`

### 4.1 Exact source and runtime binding

The mandatory source set now includes the previously omitted truth helper,
every F2 module and test, the PowerShell entry point, Stage C contracts,
calibration model and historical truth table. Final authorization must bind:

- the exact synchronized Git HEAD;
- a clean `git status --porcelain --untracked-files=all`;
- the complete source-manifest digest;
- the qualified-runtime receipt digest;
- the resolved Python executable and executable SHA-256; and
- Python, NumPy, SciPy and statsmodels versions.

### 4.2 Outer-result integrity

Each outer chunk is write-once and paired with a seal sidecar. The manifest
records byte count and SHA-256 for payload and seal, complete attempt accounting
is reconciled, and the receipt binds contract, manifest and accounting digests.
Extra, missing, swapped, edited or unregistered chunk artifacts fail closed.

### 4.3 Truth-result integrity

Stage-142-compatible truth computation uses deterministic per-scenario batches
with one sealed checkpoint per batch. Resume verifies every existing payload,
rejects partial files and binds the scenario inventory, truth CSV and receipt.
Each batch independently cross-checks the score formula against the frozen
helper, reducing shared-implementation risk.

### 4.4 Independent adjudication identity

The adjudicator verifies outer and truth payload systems before reading results
and independently recomputes `point +/- t(0.975,64) * SE`. It rejects wrong df,
interval method, data identity, leverage status or outcome unlock, and retains
the original historical/shifted truth and stopping architecture: 30 applicable
scenarios, 10 mandatory boundaries and no rescue method.

## 5. Verification history

An initial F2 test run returned 18/19 because a new negative-test fixture did
not match its intended corruption case; the fixture was corrected without
changing analysis logic. A combined test command then produced two import
errors because only the repository root was on `PYTHONPATH`; the canonical
PowerShell runner now includes both the root and `audit_tools`.

PowerShell preflight also exposed two wrapper-only issues: interpolation of
`$LASTEXITCODE:` and unittest stderr being promoted to a PowerShell native
command error. The wrapper was corrected to use `${LASTEXITCODE}` and a hidden
`Start-Process` with explicit stdout/stderr capture. The first successful pass
was archived under the ignored software-test namespace before the final clean
run.

Final combined test result: **61/61 PASS** across Stage A, Stage D, Stage E2 and
Stage F2 suites.

## 6. Final non-final qualification results

Canonical output:
`phase17_v7/rp_v4_redesign/20261011_stageF2_integrity_hardening/`

### Outer qualification

- 24 attempts in three sealed chunks.
- Fresh and resumed stable trees: byte-identical.
- Contract SHA-256:
  `b36a0daad70ed2fd9f4c58fee5bee87b8ff4c8f8af1d4ab2feca024ea8afb9c6`.
- Chunk-manifest SHA-256:
  `fa134deb07d9c3f5e8c640be50c233d51bb2aa5273e79b5b45356f5ecb7aa0c4`.
- Accounting SHA-256:
  `4f25675e77d65958f03aed087ffbf4090bdc5d832d7fc3aaa9a86a57a47263aa`.
- Receipt SHA-256:
  `d40e7ae5102a50c5a818fa493d95bd1c53c8b7160abd2d3f76eb66cc51344f65`.

### Truth qualification

- Three scenarios and 48 sealed checkpoints.
- Fresh and resumed stable trees: byte-identical.
- Maximum `MCSE / typical SE`: `0.005907133725217648`.
- Contract SHA-256:
  `67d50ddfc127a50122b355b46f8d3db222498e0238b5c92d9ed8ca90012ce15f`.
- Scenario-manifest SHA-256:
  `aeda87cd833b45afbf7b3ba28a279502880167baf7e1d82fab5dc649d3949f1b`.
- Truth CSV SHA-256:
  `a0daa4bb29b737160d697acd50b7d042caf40c5766d7008ed826da4c46c64072`.
- Receipt SHA-256:
  `2aaa5652453e3201fea5dee3b7f33061f0200595d8ee5798e850a26a22fdd64a`.

### Qualified runtime and rebinding

- Executable: `D:/bioinfor/python.exe`.
- Executable SHA-256:
  `d932e5e2f324d57f392e8fd063dcf6d0185be8a664c57c6d24e7762ed02c28ca`.
- Runtime: Python 3.13.7, NumPy 2.3.3, SciPy 1.16.2, statsmodels 0.14.6.
- Complete source-binding SHA-256:
  `e69ca282c046e43325ee2ae1f0b53f76bf2ee017771423ace1e866c646bf21a8`.
- Qualified-runtime receipt SHA-256:
  `bc743876f470bca0e2fb9c8df73bd4f07f2d61f5de8600b5b2150e7cb8b4386d`.
- Canonical integrity manifest: 10/10 PASS.

Both deliberately attempted final invocations failed closed. No stage-141 or
stage-142 output directory was created.

## 7. Scientific and governance decision

F2 closes the specific Stage F integrity findings and establishes a credible
candidate for final synthetic validation. It does not constitute G2C method
validation, does not reverse the historical G2/G2B HOLD decisions and does not
unlock any real disease effect.

The next stage is:

`RPV4_STAGE_G__POST_PATCH_EXACT_CODE_AND_RUNTIME_GO_REVIEW`

Stage G must independently verify the synchronized post-patch Git commit, the
source-binding digest and qualified-runtime receipt, then obtain explicit
approval from both authors for stage 141 and stage 142 separately. Until that
new receipt is issued, the final 160,000-attempt simulation and full truth run
remain unauthorized.

## 8. Continuing locks

- G2 and G2B remain HOLD.
- Stage 141 and stage 142 are not authorized and have not started.
- Real WP2 outcomes and all external diagnosis/activity effects remain locked.
- Large SRA download, WP4, manuscript replacement and submission work remain
  unauthorized under RP v4.
- A later synthetic PASS, if obtained, will still require a separate scientific
  review before any real-outcome work.
