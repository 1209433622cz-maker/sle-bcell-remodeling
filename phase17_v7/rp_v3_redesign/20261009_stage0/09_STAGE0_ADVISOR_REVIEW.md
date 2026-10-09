# RP v3 Stage 0 intake and freeze review

## Decision

- Submission remains **HOLD**. Historical manuscript, figures, submission packages, GitHub Release and Zenodo were not modified.
- **G0A input recovery: PASS**. All 21 registered inputs are present and hashed; the raw discovery matrix, frozen representation, unit registries and external raw archive are available.
- **G0B protocol freeze: HOLD**. The remaining open definitions are: state_support_threshold, T0, T_frozen, T_rank, pi_ref, conditional_bootstrap, simulation_core, new_multiplicity.
- **G1 precheck: HOLD** until A1/A2, common support, state support, T0, T_frozen/T_rank and pi_ref pass a result-blind technical trial.

## Verified input facts

- GSE174188 raw-count object: **150,402 cells x 30,172 genes**; non-negative integer count scan = **True**.
- Complete cell mapping: **259 donors, 271 samples, 88 libraries, 4 processing cohorts**.
- Primary historical B_CONV design: **89 rows and 89 unique donors**; the 90-versus-89 difference is preserved.
- GSE135779 raw archive: **56 paired matrix/barcode samples**, SHA-256 and byte count match the frozen public-data contract.
- R4 package manifest: **38/38 verified**. Diagnostic archive manifest: **34/34 verified**.
- A1 candidate dictionary contains **14 genes** and has **0 overlap** with the frozen IFN program.

## Important boundaries

- Existing positive and negative effects were not re-estimated in this intake run.
- The historical A0 broad compartment remains a scaffold, not a biological gold standard.
- A2 has a recoverable historical specification, but its materialized branch H5AD is absent and must be rebuilt from source before use.
- No equivalence or non-inferiority margin is claimed. Differences remain continuous estimates unless an externally justified margin is frozen.
- WP4 remains closed; the post-result 42/3,003 depletion diagnostic is not promoted to a confirmatory P value.

## RP document review

The supplied RP v3 rendered to **36 pages** without clipping or overlap. Its TOC field still labels the last appendix as page 37. Exact OOXML tag inspection found **0 tracked insertions, 0 tracked deletions and no comments**; the 25 `instrText` nodes are Word field instructions rather than revisions. The stale TOC page number is a maintenance note, not a scientific gate failure.

## Next stage

Proceed to **SCIENTIFIC_REDESIGN_STAGE0B_PROTOCOL_AND_MINIMAL_TRIAL**:

1. Freeze the A1 continuous-axis score contract and rebuild the historical A2 IFN-excluded representation.
2. Freeze common donor support, state-support rules, T0, T_frozen, T_rank and pi_ref without inspecting new branch effects.
3. Run the five RP v3 technical prototypes only: one historical contrast, one identity rebuild, one donor-by-state count construction, one frozen-score transfer, and four minimal simulation truth classes.
4. Re-adjudicate G0/G1 before any full WP1-WP3 disease-effect run or figure replacement.
