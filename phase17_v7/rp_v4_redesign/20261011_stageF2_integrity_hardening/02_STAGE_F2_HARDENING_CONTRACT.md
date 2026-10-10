# RP v4 Stage F2 integrity-hardening contract

Stage F2 preserves the single `delta_profile` estimand, OLS/HC3/t(64), the
fixed 40 x 4,000 outer grid, stages 141/142, seed base 2026101004, the original
truth and acceptance thresholds, no replenishment and no G2D rescue.

The additive implementation binds the complete local dependency set including
`rp_v4_g2c_truth.py`; requires an exact clean Git checkout and the qualified
Windows interpreter; seals every outer chunk and truth checkpoint; reconciles
the final accounting and truth CSV against receipts; validates HC3-t(64)
interval algebra; and supports fail-closed per-scenario truth resumption.

This freeze is not an exact-code GO. Stage 141 and 142 remain locked until both
authors separately approve the new post-commit Git SHA, source-binding digest
and runtime receipt digest.
