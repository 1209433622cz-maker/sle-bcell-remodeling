# RP v3 G2 domain-adjudication policy

**Frozen before full G2:** 2026-10-10
**Scope:** ten mandatory targets, 25 registered scenarios, 2,000 outer attempts and 2,000 paired donor bootstraps per supported outer attempt.

## Scientific target

G2 evaluates the actual raw-sufficient-count to full-background CPM to nonlinear T0 to four-column OLS and paired-percentile-bootstrap procedure. It does not validate latent B-cell identities, absolute RNA abundance, causal composition effects or a source-label-independent external mapper.

The independent truth is the population coefficient on the **observed measurement scale conditional on the registered support rule**. A scenario named `null` means no injected composition or within-bin biological shift. It does not force an observed nonlinear score coefficient to zero when depth or capture differs by arm. In particular, C0_R2 and C0_R4 are not silently recoded as true-null tests.

## Domain classes

The original scenario registry is unchanged. All 25 scenarios remain mandatory and all 2,000 outer attempt IDs must be retained without replacement.

| Regime | Role in final adjudication | Rule |
|---|---|---|
| R0 baseline | Applicable domain | Bias, coverage, registered true-null type-I and numerical gates apply. |
| R1 rarity/support | Boundary domain | Report support probability, stops and numerical failures. Do not rescue by redrawing, merging bins or dropping donors. |
| R2 depth imbalance | Applicable domain | Use independent observed-measurement truth; do not substitute a latent zero. |
| R3 adjacent mislabeling | Boundary stress domain | Preserve the registered mislabel stress. Report support and any eligible conditional performance; do not treat low support as PASS. |
| R4 capture-content shift | Applicable domain | Use independent observed-measurement truth and the unchanged full denominator. |

R1 and R3 remain part of the full grid. Their removal would invalidate the run. They do not enter the applicable-domain PASS conjunction because the technical pilot and independently qualified truth engine show that they primarily test failure of the all-68-donor, five-bin support condition. Their outcome is a boundary statement, never evidence that the method performs well under those perturbations.

## Minimum support for performance adjudication

The frozen coverage rule requires the Wilson 95% interval to lie wholly within `[0.925, 0.975]`. No sample size below **274 supported outer attempts** can satisfy that rule for any integer number of covered intervals. Therefore bias/coverage/type-I performance is marked non-adjudicable below 274 supported attempts. This threshold is a mathematical consequence of the previously frozen acceptance interval, not a value selected from full-G2 results.

Support stops are not numerical failures. Numerical failures are counted against all 2,000 registered attempts and must not exceed 1%. Neither class is replenished.

## Target-level and overall decisions

For each target, the applicable-domain set is the 15 cells formed by C0-C4 crossed with R0, R2 and R4. A target is unlocked only if all 15 cells pass:

1. independent truth precision;
2. upper-95% normalized bias at most 0.10 empirical SD;
3. Wilson coverage interval wholly within `[0.925, 0.975]`;
4. Wilson type-I upper bound at most 0.075 when the truth is independently registered as exactly zero;
5. numerical-failure proportion at most 0.01.

The overall applicable-domain G2 decision is the conjunction across all ten mandatory targets. This conjunction is an operational gate; it is **not** described as a simultaneous 95% confidence statement across 150 target-scenario cells. R1/R3 boundary results are reported alongside the decision and remain interpretation limits.

Until the complete full grid is run and adjudicated, `G2=NOT_RUN`, `WP2_REAL_EFFECT_UNLOCK=false`, WP4 remains conditional HOLD, and manuscript/submission/release work remains HOLD.
