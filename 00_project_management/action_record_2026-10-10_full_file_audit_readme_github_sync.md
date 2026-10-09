# Full project file audit, README refreeze and GitHub synchronization action record

**Date:** 2026-10-10
**Scope:** complete workspace inventory, file/content health, valuable-asset
classification, scientific-status synthesis, README/status refreeze and GitHub
synchronization
**Scientific decision:** `PROCEED_TO_WP2_PREFIT_IDENTIFIABILITY_AND_FULL_G2_SIMULATION_FREEZE`
**Submission decision:** `HOLD`

## 1. Work completed

1. Enumerated every regular file outside `.git` and the audit-output directory.
2. Computed file sizes and complete SHA-256 hashes for 7,850 files (5.687 GiB).
3. Performed format-aware checks for structured text, code, archives, Office
   files, PDFs, images, compressed files, NPZ and HDF5/H5AD containers.
4. Produced directory/extension summaries, a large-file register, duplicate
   groups and portability findings.
5. Separated canonical scientific objects from historical evidence, local-only
   data, render/runtime caches and superseded diagnostic runs.
6. Rewrote `README.md` around the active RP v3 redesign rather than the stale
   target-submission state.
7. Added `RP_V3_REDESIGN_STATUS.md` and updated
   `SCIENTIFIC_PRESENTATION_STATUS.md` and `REPRODUCIBILITY.md`.
8. Added a reusable full-inventory audit and a dedicated HDF5 audit tool.
9. Tightened `.gitignore` so deep third-party runtimes, QA pages, duplicate
   packages and noncanonical RP v3 exports remain local.
10. Preserved all existing user/scientific changes; no files were deleted and no
    historical HOLD was changed.

## 2. File-integrity outcome

- Direct format checks: 7,433 PASS.
- HDF5/H5AD checks: 5/5 PASS.
- Recognized-format failures: 0.
- One zero-byte warning is an expected third-party Python package marker.
- 411 binary/compiled-cache files were fully hashed/sized but had no dedicated parser.
- 64 files are at least 10 MiB.
- 34 duplicate groups above the 1 MiB threshold account for about 340.15 MiB
  beyond one retained copy.
- 119 long paths are localized to a copied QiTeng runtime tree.
- 146 files contain machine-specific absolute Windows paths, primarily historical
  records and runbooks; public audit output does not reproduce those values.

## 3. Scientific synthesis

The historical bounded conclusion remains process-level B_CONV IFN/ISG
remodeling, with permanent R1 identity, corrected C9R transfer and observational
mechanistic ceilings. RP v3 does not rescue those limits.

Stage 0 and Stage 0B established prospective inputs, units, estimands, A1/A2,
score and support contracts. WP1 then used 68 common-support donors and 2,000
paired bootstraps. A0/A1/A2 managed-SLE coefficients were 1.037152, 1.072077 and
1.037718, respectively. The final gate passed 11/11 checks and authorized only
WP2 prefit/G2 freeze.

## 4. Outputs

- `00_project_management/full_project_audit_2026-10-10/`
- `00_project_management/full_project_audit_2026-10-10/FINAL_FULL_PROJECT_AUDIT_2026-10-10.md`
- `00_project_management/VALUABLE_ASSET_REGISTER_2026-10-10.csv`
- `00_project_management/RP_V3_REDESIGN_STATUS.md`
- rewritten `README.md`
- updated `REPRODUCIBILITY.md`
- updated `00_project_management/SCIENTIFIC_PRESENTATION_STATUS.md`
- `audit_tools/project_full_inventory_audit.py`
- `audit_tools/project_hdf5_health_audit.py`

## 5. Next stage

Proceed to `WP2_PREFIT_IDENTIFIABILITY_AND_FULL_G2_SIMULATION_FREEZE`.
Freeze the target, composition geometry, support/missing-state policy, estimand
scales, simulation truth, stress scenarios, Monte Carlo intervals and acceptance
table before fitting any real WP2 disease effect. WP4, manuscript/figure
replacement, submission package, Release and Zenodo remain HOLD.

## 6. Validation before synchronization

- `git diff --check`: PASS.
- Python compile of `audit_tools/`: PASS.
- Stage 0 and Stage 0B tests: 10/10 PASS.
- WP1 unit tests: 6/6 PASS under an independent Python/NumPy runtime.
- Manuscript/figure/QiTeng maintenance tests: 45/45 PASS.
- README/status relative-link check: PASS, zero missing targets.
- Audit JSON parse and asset/inventory CSV reads: PASS.
- Full inventory workflow: PASS.
- HDF5/H5AD health workflow: 5/5 PASS.

The project `sle-bcell` Conda environment reproduced its previously documented
Windows NumPy/LAPACK native exit during the WP1 OLS unit test, without a Python
assertion failure or traceback. The same six tests passed in the independent
bundled NumPy runtime after stubbing plotting/statsmodels imports that those unit
tests do not execute. This remains an environment-maintenance issue; it does not
change the already completed WP1 results or gates.
