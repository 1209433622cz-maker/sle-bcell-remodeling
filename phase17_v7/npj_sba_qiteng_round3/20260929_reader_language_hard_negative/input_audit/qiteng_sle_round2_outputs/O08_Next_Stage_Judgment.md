# O08 Next-stage Judgment

## Decision

**Next stage:** `QITENG_FIGURE_READER_LANGUAGE_MICRO_GATE_AND_FINAL_HARD_NEGATIVE_AUDIT`

## Why this is the next stage

The manuscript's scientific architecture is closed and the Round-2 package passes document, package and policy consistency checks. Remaining work should not reopen statistical modeling or add new biological narratives.

The only currently identifiable reader-facing inconsistency with enough benefit to justify a controlled reopen is terminology embedded inside existing figure artwork:

- Figure 2c: `Frozen >=50` -> preferably `Primary >=50` or equivalent source-faithful reader wording.
- Figure 3a: `Four frozen programs in discovery` -> `Four prespecified programs in discovery`.
- Figure 3c: `Frozen IFN-arm genes` -> `Prespecified IFN-arm genes`.

## Execution constraints

1. Locate and use the canonical figure-generating source; do not annotate or edit the final PDF by hand.
2. Change labels only; preserve underlying data, coordinates, confidence intervals, thresholds, panel letters and source-data files unless regeneration deterministically rewrites metadata only.
3. Re-render at final size and compare against the parent figure pixel/geometry outside intended text regions.
4. Recheck legends and manuscript terminology after regeneration.
5. Re-run package hashes and local verifier.
6. Perform a final hard-negative audit ensuring that identity, composition, transfer, CAMERA/depletion and n=2 boundaries remain visible wherever their positive parent claim appears.

## Stop rule

If the canonical figure source cannot reproduce the current figures without broader visual or numerical drift, **do not force the terminology change**. Retain the current figure and document the minor language issue as accepted technical debt.

## Not authorized by this stage

- new pathway/network panels;
- threshold retuning;
- mapper reselection;
- post-hoc rescue analyses;
- causal arrows or mechanism diagrams that exceed the evidence tier;
- submission-portal upload or Release/Zenodo replacement.

## Expected terminal state

If the figure-language micro-gate passes and the final hard-negative audit identifies no new discrepancy, the project can enter:

`QITENG_SCIENTIFIC_SUBMISSION_CANDIDATE_FREEZE`

This is a scientific/package freeze, not a claim that the journal portal has been submitted or that publication quality is guaranteed.
