# Action record: Gate C3A frozen abundance models

**Date:** 15 August 2026

**Project:** 6013RP-wyf / v7 Phase 17

**Scope:** frozen sample-level B-cell compartment abundance inference, mandatory
sensitivity analyses, replication-overlap audit, statistical diagnostics, figure
quality control and manuscript-claim adjudication

## 1. Authorization and unchanged scope

Gate C3 authorized effect estimation only after exact cell-ID metadata joining and
pre-effect freezing of the three abundance-model matrices. The authorized hard
identities remained `B_CONV` and `B_ASC`. Hard naive-memory composition, a
platelet-associated B-cell identity, a source-cluster-4 subtype and cell-level
inferential tests remained prohibited.

Before fitting any model, the Gate C3 integrity manifest was reverified: 21/21
files passed size and SHA-256 checks.

## 2. Statistical implementation

The implemented model is a sample-stratum beta-binomial likelihood:

- response: `asc_cells` out of `total_cells`;
- biological replicate: `sample_uuid`;
- technical stratum: `sample_uuid x Processing_Cohort`;
- zero-ASC strata: retained without a pseudocount in the count likelihood;
- mean model: logit link with the exact frozen covariates;
- dispersion: jointly estimated beta-binomial precision `kappa`;
- primary uncertainty: observed-information covariance from the frozen
  beta-binomial likelihood; and
- robustness audit: HC1 sandwich covariance calculated from independent
  sample-stratum score contributions.

All three frozen contrasts contain one row per donor, so donor-clustered covariance
is numerically equivalent to sample-stratum clustering within each contrast.

Absolute adjusted proportions were estimated by g-computation, setting the disease
indicator to each contrast level while retaining the observed covariate
distribution. Confidence intervals used 5,000 parameter draws with a fixed seed.

The two-part sensitivity uses Firth/Jeffreys bias-reduced logistic regression for
ASC presence and HC3 OLS on the positive-only logit abundance. Firth regression was
used uniformly because the flare presence outcome has separation.

## 3. Replication-overlap audit

The frozen validation matrices were retained unchanged. An additional
prespecified sensitivity removed any row whose sample or donor also occurred in
the primary cohort.

| Analysis | Frozen n | Shared samples | Shared donors | Nonoverlap n | Reference/exposed |
|---|---:|---:|---:|---:|---:|
| Cohort-2 validation | 64 | 11 | 11 | 53 | 21/32 |
| Cohort-3 flare | 34 | 3 | 4 | 30 | 15/15 |

The nonoverlap validation is a stronger internal sensitivity, but it is not an
independent external cohort.

## 4. Primary managed-state result

The frozen cohort-4 analysis included 90 sample strata, 38,846 B cells and 481 ASC
cells. Thirteen strata had zero ASC cells.

| Quantity | Result |
|---|---:|
| Managed conditional OR | 0.947 |
| Model-based 95% CI | 0.636-1.410 |
| Model-based P | 0.787 |
| HC1 95% CI | 0.651-1.376 |
| HC1 P | 0.774 |
| Adjusted ASC fraction, normal | 1.61% |
| Adjusted ASC fraction, managed | 1.52% |

This result provides no evidence for a managed-state ASC composition difference.
It must not be rewritten as depletion or equivalence: the confidence interval is
compatible with moderate effects in either direction.

## 5. Mandatory primary sensitivities

| Variant | n | OR | 95% CI | P |
|---|---:|---:|---:|---:|
| Minimum 20 B cells | 94 | 0.997 | 0.670-1.484 | 0.990 |
| Frozen minimum 50 | 90 | 0.947 | 0.636-1.410 | 0.787 |
| Minimum 100 B cells | 87 | 0.880 | 0.594-1.305 | 0.525 |
| Exclude explicit non-B `ct_cov` | 90 | 0.946 | 0.636-1.409 | 0.786 |
| Exclude residual doublet calls | 90 | 0.948 | 0.637-1.412 | 0.792 |

All four non-base variants matched the weak negative frozen direction. This is
directional stability of a null-sized estimate, not evidence of a biological
effect.

All 90 leave-one-out fits converged and retained the frozen direction. Their ORs
ranged from 0.896 to 0.989 and P values from 0.584 to 0.956. The result is therefore
not concealed by one influential sample.

The two-part primary results were also null:

- ASC presence OR 0.937 (95% CI 0.300-2.925; P=0.911); and
- positive-only abundance ratio 1.057 (95% CI 0.683-1.635; P=0.803).

## 6. Managed-state internal validation

The frozen cohort-2 European-American female estimate was directionally concordant
but unsupported: OR 0.772 (95% CI 0.372-1.602; P=0.488). After excluding all
primary-overlapping samples or donors, the estimate remained negative: OR 0.591
(95% CI 0.271-1.291; P=0.187; n=53).

The adjusted ASC fractions in the nonoverlap set were 0.77% in normal and 0.46% in
managed strata. The wide interval and age imbalance prevent a replication claim.

## 7. Secondary flare result

The frozen cohort-3 flare contrast was positive:

- OR 2.303 (model 95% CI 1.093-4.850; nominal P=0.0282);
- HC1 95% CI 1.356-3.910 (P=0.00201);
- nonoverlap OR 2.579 (95% CI 1.158-5.744; P=0.0204; n=30); and
- adjusted ASC fraction 0.80% normal versus 1.82% flare.

Threshold and exclusion sensitivities remained positive (OR 2.30-2.39). The
positive-only two-part component was also positive (ratio 2.605, 95% CI
1.242-5.464; P=0.0113), whereas ASC presence was imprecise after Firth correction
(OR 2.544, 95% CI 0.112-57.748; P=0.558).

This is a secondary hypothesis-generating signal. Its BH q value across the three
frozen base contrasts was 0.0845, it has only 34 strata, and it lacks independent
external validation. It cannot replace the failed managed-state primary result or
be described as a confirmed disease mechanism.

## 8. Numerical diagnostics

- Formal beta-binomial fits: 17/17 converged.
- Positive-definite numerical Hessians: 17/17.
- Base-model beta-binomial `kappa`: 53.8 primary, 52.5 validation and 88.8 flare.
- Corresponding intraclass overdispersion `rho`: 0.0182, 0.0187 and 0.0111.
- All reported contrast and two-part estimates were finite.
- OR values exactly matched `exp(beta)` within numerical tolerance.
- All adjusted estimates and confidence intervals were within [0,1] and correctly
  ordered.

The validation Pearson residual scale was larger than the other contrasts. HC1
sandwich inference was therefore retained beside model-based uncertainty rather
than selecting the more favorable result.

## 9. Implementation and outputs

Implemented files:

- `audit_tools/phase17_c3_02_fit_frozen_abundance.py`;
- `audit_tools/run_6013RP_phase17_gateC3A_abundance.ps1`;
- `phase17_v7/gateC3A/20260815_frozen_abundance`; and
- pointer `phase17_v7/gateC3A/_LATEST_GATE_C3A.txt`.

The result directory contains coefficient and contrast tables, adjusted
predictions, 12 mandatory sensitivity contrasts, six two-part results, 90
leave-one-out fits, overlap and diagnostics tables, JSON/Markdown decisions,
raster/vector figures and a SHA-256 manifest.

The manifest covers 14 generated files totaling 235,496 bytes. All 14 hashes and
sizes were independently reverified.

## 10. Figure quality control

The four-panel audit figure contains:

- frozen and nonoverlap contrast forest estimates;
- the complete primary threshold/exclusion sensitivity forest;
- model-adjusted absolute primary proportions; and
- all 90 primary leave-one-out coefficients.

The first rendered version exposed crowded logarithmic tick labels and was not
accepted. The figure was regenerated with fixed readable log ticks, manuscript
labels instead of internal variable names, stable panel geometry and no clipped or
overlapping text. PNG and PDF outputs were visually checked.

This figure is suitable as a supplementary robustness figure. Because the primary
effect is unsupported, it should not be promoted as a main-figure biological
claim.

## 11. Verification performed

- Python compilation: passed.
- PowerShell parsing: passed.
- End-to-end conda launcher: passed after full rerun.
- Frozen Gate C3 input integrity: 21/21 passed.
- Expected output-table dimensions: 8/8 passed.
- Finite-value and algebraic identity audit: passed.
- Formal model convergence and Hessian audit: 17/17 passed.
- Gate C3A output integrity: 14/14 passed.
- Raster figure visual review: passed after one layout correction.
- Git whitespace check: passed before commit.

## 12. Gate decision and manuscript consequence

Decision:

`NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM`

The manuscript must not claim a managed-state ASC expansion or depletion. The
composition result should be reported transparently as a negative/secondary
finding. The flare estimate may motivate a transcriptional analysis, but its
secondary status, q value, sample size and lack of external replication must remain
visible.

The central paper logic now shifts from hard composition to continuous
within-`B_CONV` programs and true sample-level raw-count pseudobulk transcription.

## 13. Immediate next objective

Begin Gate C4A by freezing disease-blind continuous program dictionaries and
extracting the selected cells from source `.raw.X` by exact cell ID. Freeze the
sample-by-cohort B_CONV pseudobulk design before inspecting disease coefficients.
Then fit cohort-4 primary, cohort-2 internal directional and cohort-3 secondary
flare transcription models, followed by independent external validation.
