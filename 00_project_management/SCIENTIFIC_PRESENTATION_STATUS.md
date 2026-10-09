# Scientific presentation and active redesign status

Effective date: 2026-10-10.

Overall state: **ACTIVE_RP_V3_SCIENTIFIC_REDESIGN / HOLD_SUBMISSION**.

## Frozen presentation baseline

The September manuscript, figures and Supplementary Information remain a valid
scientific-presentation baseline. Their bounded conclusion is reproducible
process-level B_CONV IFN/ISG remodeling. Identity failure, primary-composition
non-support, weak genome-wide concordance, corrected transfer-calibration
failure, observational regulatory evidence and the n=2 perturbation boundary
remain part of the evidence hierarchy and must not be rescued by retuning.

Canonical editable sources remain:

- `01_manuscript/Manuscript.md`
- `01_manuscript/Supplementary_Information.md`

The final September local package is retained under
`04_submission/20260929_qiteng_submission_candidate/`, but it is not authorized
for upload while RP v3 is active.

## Active RP v3 state

- Stage 0 recovered 21/21 inputs and froze units, chronology, estimands and
  branches.
- Stage 0B closed the protocol fields and passed G0/G1 without inspecting a
  disease coefficient.
- WP1 used a 68-donor common support set and passed 11/11 final checks.
- WP2 effect-free preflight verified five-bin support, p/q measurement geometry
  and an 8/8 ILR design without fitting a disease effect.
- The G2 generator, independent truth engine, paired-bootstrap estimator,
  full-run scheduler and adjudicator passed technical and Windows
  requalification. Full G2 has not been run.
- Current decision:
  `PASS_G2_IMPLEMENTATION_AND_DOMAIN_FREEZE__READY_FOR_FULL_G2`.
- WP4: `HOLD_CONDITIONAL`.
- Submission, manuscript replacement, release and Zenodo: `HOLD`.

## Reopening rule

The presentation baseline may be reopened only for a verified numerical error,
claim-owner or cross-reference mismatch, provenance/hash failure, actual-size
readability defect, new data, explicit author scientific feedback, a concrete
portal requirement, or a gated RP v3 result that materially changes the paper.

Any revision must begin from the source, rerender and pass the relevant audit.
Manual editing of final PDFs is prohibited.

## Next stage

The only active scientific next step is:

`G2_FULL_EXECUTION_R0_CORE_FIRST`

The target, scenario, acceptance and domain-adjudication rules are frozen. Run
R0 first, then retain and adjudicate all 25 scenarios. No WP2 disease-effect
estimate may be fitted until the complete applicable-domain G2 gate passes and
is separately reviewed. See `RP_V3_REDESIGN_STATUS.md` and the project README
for the complete gate definition.
