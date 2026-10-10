# RP v4 Stage C advisor review

## Decision

`PASS_RPV4_STAGE_C_PROTOCOL_FREEZE__AUTHOR_SIGNOFF_REQUIRED_BEFORE_FINAL`

Stage C freezes one estimand and one method.  It does not run or imply a final
G2C PASS.  Real WP2 effects, new-cohort outcomes, manuscript changes and
submission work remain locked.

## Why `delta_profile`

`delta_profile` is the clean interval-calibration problem: all 15 historical
G2B point-bias gates passed, while nine cells failed coverage.  `delta_cellref`
was not selected because its historical failures mix interval undercoverage
with a point-bias failure.  The registered interpretation is an association
difference between two observed measurement/mixing rules, never a mediation
percentage or cell-intrinsic causal effect.

## Historical-development diagnosis

The exposed development replay found:

- 15/15 applicable cells passed the single HC3-t candidate;
- bootstrap-SE p01/median was never below 0.532;
- maximum point leverage was 0.105;
- no inner bootstrap failed in the diagnostic subset;
- beta_B and beta_S_profile bootstrap correlation was at least
  0.992; and
- direct delta equalled the coefficient difference to within
  4.57e-15.

These results argue against a near-zero studentizer, non-smooth delta or gross
leverage failure.  They support a small-sample influence-function correction,
but they are exposed development evidence only.  Confirmation requires the
new seed base, 40 frozen DGPs and 160,000 registered outer attempts.

## External-input decision

Official NCBI RunInfo confirms 176 runs/88 experiments for GSE262846 and 85
runs/83 experiments for GSE118254.  The combined SRA payload is about 297.57 GB
and contains 927.66 G bases.  Raw reconstruction is feasible but pending.  At
least 2.5 TB scratch space should be reserved.

The two studies are conservatively treated as potentially overlapping because
different de-identification tokens cannot resolve shared-donor provenance.
GSE262846 may become the primary clinical-activity candidate only after sealed
count reconstruction.  GSE118254 is a technical measurement bridge and cannot
be counted as a second independent confirmation.

## Measurement decision

S0 remains the primary frozen score; S1 remains a technical sensitivity.  S2 is
abandoned because no unique result-blind formula was justified.  Neither score
may be selected or promoted using disease direction, P value or AUC.

## Next stage

Proceed only to `RPV4_STAGE_D__G2C_IMPLEMENTATION_AND_EXTERNAL_RAW_INTAKE_TECHNICAL_PILOT`:

1. implement and unit-test the three shifted generators and independent truth engine;
2. benchmark a small non-adjudicative technical grid without final performance claims;
3. generate a resumable SRA download/count runbook and checksum plan;
4. obtain exact author sign-off on the frozen protocol before any final G2C run;
5. keep all real outcomes sealed.

Failure of the single final strategy will produce
`G2C_HOLD__WP2_DECOMPOSITION_NOT_CLAIMABLE`; RP v4 permits no G2D rescue.
