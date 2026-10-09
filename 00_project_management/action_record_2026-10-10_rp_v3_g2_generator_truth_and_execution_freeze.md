# RP v3 G2 generator, truth engine and execution-freeze action record

**Date:** 2026-10-10
**Requested scope:** continue Research Plan v3 after the WP2 effect-free preflight, independently audit the received G2 technical candidate, complete the next authorized work and determine the next stage.
**Final decision:** `PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2`
**Real-data boundary:** no new WP2 disease coefficient, disease-stratified program mean or manuscript claim was computed.

## 1. Inputs and chain of custody

Received archive:

`C:\Users\Administrator\Downloads\SLE_RPv3_G2_Generator_Truth_TechnicalPilot_20261010.zip`

- size: 20,897,297 bytes;
- SHA-256: `D9FB9E1DBBB889FBAB72AD499869844B29E3D7B0EC36BFBD7D48837CDEF1AFBA`;
- archive entries: 935, comprising `MANIFEST.csv` plus 934 registered payloads;
- extracted payload size: 33,832,898 bytes.

The archive was extracted only into the Git-ignored review directory
`phase17_v7/rp_v3_redesign/20261010_g2_external_candidate/`. Instructions embedded in the archive were treated as candidate documentation, not as authorization.

## 2. Independent bundle and code audit

The package verifier confirmed 934/934 payloads with no missing, altered or unmanifested scientific payload. The candidate's 48 unit tests were rerun under local Windows Python 3.13.7 and all passed. Tests cover generator dimensions and closure, full-background normalization, disjoint random streams, support stops, conservative adjacent-bin flow, rejection of real inputs, independent score agreement, actual 2,000-resample paired bootstrap behavior, rank/nonfinite failures, truth import boundaries, deterministic gzip, tamper/orphan/partial checkpoint rejection and resume binding.

The source review confirmed:

1. whole five-bin templates are sampled independently of synthetic disease assignment;
2. all 12 IFN genes plus the remaining-library category enter every denominator;
3. generated libraries and cell flows are nonnegative and closed;
4. the estimator accepts only `SIMULATED_ONLY` objects;
5. the truth engine imports neither the generator nor the estimator and uses a different NumPy bit generator and seed namespace;
6. pilot and full-G2 streams use distinct stage keys;
7. support failures are persisted without replacement;
8. the existing runner cannot silently switch to real-data or full-G2 mode.

## 3. Windows technical-pilot requalification

The 50-attempt pilot was rerun from a new output directory with `D:\bioinfor\python.exe`, NumPy 2.3.3 and single-thread environment locks.

| Item | Result |
|---|---:|
| Registered pilot outer attempts | 50/50 |
| Interval-computed attempts | 30 |
| Support stops | 20 |
| Inner paired bootstraps | 60,000 |
| Inner numerical failures | 0 |
| Resume checkpoints reused | 50/50 |
| New attempts on resume | 0 |

Cross-platform comparison was performed at object level rather than by comparing only final labels:

- 50/50 cell-count arrays byte-identical;
- 50/50 thirteen-category count arrays byte-identical;
- 50/50 design arrays byte-identical;
- 50/50 template-index arrays byte-identical;
- 30/30 bootstrap-index arrays byte-identical;
- maximum response difference `8.8818e-16`;
- maximum point-estimate difference `8.8818e-16`;
- maximum interval-endpoint difference `2.2204e-16`.

The non-identical text/NPY hashes are therefore explained by platform-level floating-point reduction order, not changed random draws, data generation, fit status or scientific decisions.

## 4. Independent truth requalification

The complete fixed truth-precision ladder was rerun locally for all 25 scenarios. Results:

- 25/25 scenario statuses matched the received independent run;
- 25/25 final effort levels matched;
- 250/250 target-scenario truth rows passed `MCSE <= 0.01 x typical coefficient SE`;
- 30 exact symmetry truths and 220 independent Monte Carlo truths were retained;
- worst MCSE/SE ratio remained `0.0095413`;
- maximum cross-platform truth difference was `1.1102e-16`;
- arm-specific and whole-68 support probabilities were identical.

These are truth-precision results only, not bias/coverage results and not a full-G2 PASS.

## 5. Scientific review of new DGP assumptions

The generator is accepted for the declared observed-measurement question, not as a biological generative model of all B-cell heterogeneity. The 68 joint templates preserve empirical five-bin and gene/background heterogeneity, while the conditional Poisson law does not model cell-level overdispersion, expression-dependent misclassification, complete annotation retraining or external clinical confounding.

The truth target is the coefficient after the complete observation and nonlinear scoring process. Consequently, no injected biological shift does not always imply zero observed-score truth. C0_R2 yields, for example, `beta_B=-0.097796`, `beta_S_profile=-0.105463` and `beta_S_cellref=-0.105974`; these values reflect depth-sensitive finite-count nonlinear measurement and must not be called SLE effects or false positives.

R1 and R3 frequently violate the all-68-donor, five-bin support rule. They are retained as mandatory boundary domains. No donor deletion, redraw, zero fill, bin merge or adaptive renormalization is permitted.

## 6. Frozen adjudication policy

The original 25-scenario registry and numeric acceptance table were not changed. A pre-full-run domain policy now makes their interpretation explicit:

- R0, R2 and R4: applicable performance domains;
- R1: rarity/support boundary;
- R3: mandatory adjacent-mislabel stress boundary;
- all 25 scenarios and all 2,000 attempt IDs remain mandatory;
- a performance cell needs at least 274 supported attempts, the mathematical minimum at which the frozen Wilson coverage interval could possibly lie wholly within `[0.925, 0.975]`;
- support stops and numerical failures remain separate;
- a mandatory target unlocks only if all 15 C0-C4 x R0/R2/R4 cells pass truth precision, bias, coverage, applicable true-null type-I and numerical rules;
- the overall decision is a deterministic operational conjunction, not a simultaneous 95% family-confidence claim.

## 7. Canonical implementation added

Promoted unchanged audited components:

- `audit_tools/rp_v3_g2_generator.py`;
- `audit_tools/rp_v3_g2_estimation.py`;
- `audit_tools/rp_v3_g2_truth.py`.

New project-side components:

- `audit_tools/rp_v3_g2_full_runner.py`: full-stage, counter-addressed, hash-bound chunk runner;
- `audit_tools/rp_v3_g2_adjudicate.py`: complete-grid accounting and frozen per-target/scenario adjudication;
- `audit_tools/run_rp_v3_g2_full.ps1`: local R0-first and full-grid orchestrator;
- `audit_tools/rp_v3_g2_03_freeze.py`: bundle/runtime/truth comparison and contract freezer;
- `audit_tools/test_rp_v3_g2.py`: ten focused integration and boundary tests.

The full runner records every outer attempt and target, point and interval, support/numerical state, generated-data hash and bootstrap-index hash. It does not retain billions of redundant inner coefficients and cannot access real WP2 responses. Existing complete chunks are verified and reused; altered, partial or orphan chunks fail closed.

## 8. Verification

- received candidate tests: 48/48 PASS;
- canonical G2 integration tests: 10/10 PASS;
- candidate manifest: 934/934 PASS;
- Windows technical pilot: 50/50 attempts accounted;
- truth qualification: 250/250 PASS;
- canonical implementation manifest: 11/11 payloads recorded before the manifest itself;
- repository RP v3 tests: 38/38 PASS (Stage 0, Stage 0B, WP1, WP2 preflight and G2 integration).

## 9. Current gate and prohibited actions

The three previously empty hashes are now populated by qualified objects, and the synthetic execution contract is approved. This means **ready to run full G2**, not G2 passed.

Current state:

- `G2=NOT_RUN`;
- `G2_PASS=false`;
- `WP2_REAL_EFFECT_UNLOCK=false`;
- `WP4=HOLD_CONDITIONAL`;
- manuscript/figure replacement, submission, GitHub Release and Zenodo remain HOLD.

## 10. Next-stage decision

Next stage:

`G2_FULL_EXECUTION_R0_CORE_FIRST`

Run the five R0 cells first using the exact 2,000 outer x 2,000 paired-bootstrap procedure as an operational checkpoint. Then reuse the same bound output root to complete R1-R4 and adjudicate all 25 cells. R0 completion alone does not unlock real effects.

The reproducible commands, resume behavior and final decision path are documented in:

`phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/11_G2_FULL_RUN_RUNBOOK.md`.
