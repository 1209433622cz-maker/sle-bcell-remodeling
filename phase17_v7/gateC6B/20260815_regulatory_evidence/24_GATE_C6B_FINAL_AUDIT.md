# Gate C6B final independent audit

## `PASS_GATE_C6B_UPPER_Q1_REGULATORY_FRAMING_AUTHORIZED_NONCAUSAL`

## Independent checks

- [PASS] c6b1_qualification_pass
- [PASS] confirmatory_exact_24_unique
- [PASS] independent_ulm_reproduction
- [PASS] independent_global_bh_reproduction
- [PASS] c6b2_all_frozen_checks_pass
- [PASS] influence_row_counts_reconcile
- [PASS] resampling_row_counts_reconcile
- [PASS] core_influence_pass
- [PASS] sensitivity_exact_72
- [PASS] gse23307_gene_effect_exact_24
- [PASS] gse23307_donor_summary_reproduced
- [PASS] scale_repaired_orthogonal_pass
- [PASS] msigdb_exact_three_positive
- [PASS] external_resource_hashes
- [PASS] all_gene_input_hashes
- [PASS] superseded_scale_outputs_preserved

## Numerical reproduction

- Maximum independently recomputed ULM field delta: `1.776e-15`.
- Maximum independent statsmodels BH delta: `1.110e-16`.
- Maximum recomputed GSE23307 donor-mean delta: `4.441e-16`.

## Scientific interpretation

The data authorize an upper-Q1 observational framing in which the independently replicated IFN/ISG program is accompanied by concordant STAT1/STAT2-centred regulatory activity and orthogonal interferon-response evidence. They do not establish causality, a unique upstream ligand or a new B-cell subtype.

## Next stage

Gate C7: regenerate the complete figure set around the frozen result hierarchy, reconcile every manuscript claim against the gate decisions, and prepare source-data/caption/method packages before journal selection.
