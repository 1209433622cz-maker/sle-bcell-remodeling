# WP1 annotation-sensitivity execution contract

**Authorization:** `READY_AFTER_G1_PASS`

## Question

Estimate how much the primary managed-versus-normal IFN/ISG coefficient changes
when identity is represented by A1 or A2 instead of the historical A0 scaffold.
This is an annotation-sensitivity analysis, not a search for a favorable branch.

## Frozen branches

- **A0:** historical r=0.4 broad scaffold; clusters 0, 1, 2 and 4 are B_CONV,
  cluster 3 is B_ASC.
- **A1:** continuous 14-gene identity axis. Five quantile bins are used only to
  build supported donor-bin pseudobulks. The donor-level score is standardized
  to the frozen `pi_ref`; no biological subtype label or adaptive cutpoint is
  permitted.
- **A2:** corrected full-cell IFN-excluded representation. A2 clusters must be
  mapped to the A0 broad B_CONV/B_ASC scaffold by cell-overlap only, before
  disease fields are joined. The mapping and its purity/recall are frozen before
  any disease coefficient is fitted.

## Frozen transform and analysis set

- Use the Stage 0B T0 transform and the 43-control gene means/SDs without branch
  restandardization.
- Use the 89-donor primary C4 model matrix and its frozen covariates.
- Enforce at least 30 cells per A1 donor-bin. Use only common-support units for
  paired branch comparisons; report every exclusion and its reason.
- Do not change IFN program membership, covariates, minimum-cell rules or
  normalization after viewing coefficients.

## Estimands

- `beta_A0`: primary disease coefficient under A0.
- `beta_A1`: coefficient for the A1-bin score standardized to frozen `pi_ref`.
- `beta_A2`: coefficient under the disease-blind A2 broad mapping.
- `delta_beta_ann_A1 = beta_A1 - beta_A0`.
- `delta_beta_ann_A2 = beta_A2 - beta_A0`.

Report estimates and 95% confidence intervals continuously. No equivalence or
non-inferiority claim is authorized because RP v3 did not justify a margin.

## Resampling and multiplicity

- Run 2,000 paired donor-clustered bootstrap replicates with one shared donor
  draw applied to all three branches.
- Record fit failures and effective donor counts in every replicate.
- The two annotation deltas form one family only if formal p values are reported;
  otherwise retain estimation-first confidence intervals without a new testing
  claim.

## Stop rules

HOLD WP1 if the A2 broad mapping is not disease-blind, if any branch silently
changes the T0 reference, if common support is insufficient under the frozen
rule, or if paired bootstrap failure exceeds 1%. Do not merge states or alter
thresholds in response to the observed disease coefficient.

WP1 does not unlock WP4, manuscript rewriting, figure replacement, a submission
package, GitHub release or Zenodo update. Those remain conditional on later RP v3
gates.
