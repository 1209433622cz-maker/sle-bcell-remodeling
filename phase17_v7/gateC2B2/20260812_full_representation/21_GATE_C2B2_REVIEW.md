# Gate C2B2 disease-blind representation review

**Decision:** `READY_FOR_C2B3_ADVISOR_REVIEW`

- Primary cells: 150,402
- Residual-risk-negative sensitivity cells: 148,430
- Primary diagnostic resolution: 0.4
- Disease/outcome fields used: none
- Software-test mode: False

## Programmatic checks

- [PASS] fit_complete: REPRESENTATION_FIT_COMPLETE_REVIEW_REQUIRED
- [PASS] outcome_lock: protected columns=none
- [PASS] primary_cells: 150,402/150,402
- [PASS] singlet_branch_exact: 148,430 = 150,402 - 1,972
- [PASS] hvg_counts: all branches=3,000
- [PASS] technical_nuisance_excluded: maximum=0
- [PASS] primary_ig_excluded: primary immunoglobulin HVGs=0
- [PASS] isg_branch_excluded: ISG-excluded strong ISG HVGs=0
- [PASS] ig_dominance_sensitivity_documented: status=NOT_EVALUABLE_SOURCE_FEATURE_SPACE; canonical IG loci=3; constant genes=0
- [PASS] mixing_improved: library 0.083->0.014; cohort 0.693->0.365
- [PASS] bridge_consistency: Harmony median bridge-pair cosine distance did not increase
- [PASS] cluster_technical_coverage: maximum library fraction=0.031
- [PASS] cluster_biological_coverage: minimum samples=225
- [PASS] residual_risk_not_dominant: maximum=0.017
- [PASS] singlet_branch_stability: ARI=0.793; threshold=0.700
- [PASS] isg_excluded_branch_stability: ARI=0.772; threshold=0.700
- [PASS] marker_coverage: at least two genes present per marker module
- [PASS] harmony_diagnostics_captured: convergence fields stored for all branches
- [PASS] harmony_all_converged: all representation branches converged within the configured limit

## Binding interpretation

This full-data output verifies the representation and diagnostic contracts at
the selected backbone resolution. State names, cell exclusions and biological
claims remain unauthorized until resampling stability, ranked markers and
outside-label candidate mapping pass advisor review at Gate C2B3.
