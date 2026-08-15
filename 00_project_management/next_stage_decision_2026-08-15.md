# Next-stage decision: Gate C3 sample-level composition and program design

## Advisor decision

Gate C2B4 passes a disease-blind two-compartment state model. The authorized hard
identities are conventional B cells (`B_CONV`) and antibody-secreting B cells
(`B_ASC`). The original C2B3 HOLD remains binding for five-, four- and three-state
hard clustering.

## Immediate target

Implement Gate C3 metadata unlock and design audit before fitting disease models:

1. join source metadata by `source_cell_index` and verify cell-ID identity;
2. reconcile `sample_uuid`, `library_uuid`, `donor_id` and `Processing_Cohort`;
3. preserve and quantify `ct_cov`/`ind_cov` missingness rather than silently
   imputing them;
4. produce one row per sample and compartment with cell counts and proportions;
5. identify repeated donors, cohort-disease confounding and unsupported strata; and
6. freeze the primary, validation and sensitivity model matrices before inspecting
   effect estimates.

## Authorized analyses

- Sample-level `B_ASC` abundance relative to total frozen B cells.
- Donor-aware uncertainty when a donor contributes repeated samples.
- Cohort-stratified effects followed by prespecified cross-cohort concordance.
- Continuous naive-memory, ASC, interferon and activation programs.
- Platelet-program sensitivity analyses within `B_CONV`.
- Sample-level or donor-aware pseudobulk expression models.

## Prohibited analyses

- Cell-level tests treating cells as independent biological replicates.
- Hard naive-versus-memory abundance tests based on source clusters 0 and 1.
- Calling cluster 2 a platelet-positive B-cell subtype.
- Assigning a publication cell type to source cluster 4.
- Selecting cohorts, covariates or contrasts after viewing the most favorable
  disease effect.

## Statistical design target

The design audit must determine whether each contrast has adequate independent
samples and donors within processing cohorts. Primary abundance inference should
use sample-level counts with an appropriate binomial/beta-binomial or comparable
overdispersed model. Repeated samples require donor blocking or random effects.

Continuous expression programs should be summarized within `B_CONV` at the sample
level. Gene-level discovery should use pseudobulk counts, explicit library-size
normalization, multiple-testing correction and cohort-aware replication.

## Publication implication

The project can now begin outcome-aware analysis, but the upper-Q1 claim is still
conditional. A credible manuscript requires a cohort-reproducible `B_ASC` or
continuous-program effect, donor-aware statistics, an independent validation
dataset and external regulatory/mechanistic support. Gate C3, not further
manuscript polishing, is the immediate priority.
