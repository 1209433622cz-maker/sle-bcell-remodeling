# Round 6 R1 HOLD advisor review

Date: 2026-08-27
Decision: **ACCEPT THE FORMAL HOLD AND NARROW THE TAXONOMY CLAIM**

## Integrity decision

- All 20 full-data replicates completed and all 20 Harmony runs converged.
- Replicate contracts, input and executable hashes, aggregate tables and final status were independently reproduced from replicate-level files.
- Four of five frozen criteria passed. The minimum state-median Jaccard was 0.930323, below the unchanged 0.95 criterion; `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY` is retained.
- The failing state is `B_ASC`: median Jaccard 0.930323. `B_CONV` median Jaccard was 0.999363.
- The median broad-state exchange was 76 of 120,320 sampled cells per replicate.

## Downstream propagation

- Replacing only the observed boundary-exchange cells in the complete frozen partition yielded primary B_ASC odds ratios from 0.896 to 0.967; all 20 confidence intervals included one.
- The primary B_CONV IFN/ISG effect ranged from 0.836 to 0.845; the donor-nonoverlap effect ranged from 1.059 to 1.087. All 40 effects were positive and all confidence intervals remained above zero.
- These are robustness sensitivities on the same data, not new replication.

## Authorized interpretation

The full-pipeline result prevents a stronger claim that `B_CONV`/`B_ASC` is a universally reproducible taxonomy. It does not invalidate the frozen disease-blind analysis partition, the primary B_ASC null result or the independently replicated within-B_CONV IFN/ISG program. The permitted framing is:

> End-to-end reconstruction retained high global two-compartment concordance but missed the prespecified B_ASC state-overlap criterion. We therefore use B_CONV/B_ASC as a disease-blind analysis scaffold rather than a universally reproducible taxonomy; observed boundary exchanges did not alter the primary composition null or the B_CONV IFN/ISG effects.

Do not:

- relax the 0.95 Jaccard threshold;
- remove replicate 1 or any other weak replicate;
- rerun with alternative seeds to obtain PASS;
- call the broad partition end-to-end reproducible without the HOLD qualification;
- describe propagation sensitivities as independent validation.

## Publication placement

Place Supplementary Figure S9 and its Source Data in the supplementary information. Figure 1 should identify panels b-d as frozen-representation resampling. The manuscript title should refer to unstable state **assignments**, not unstable biological states.
