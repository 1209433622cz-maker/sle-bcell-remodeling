# RP v4 Stage G final synthetic validation review

**Decision:** `G2C_SYNTHETIC_PASS__SEPARATE_REAL_OUTCOME_REVIEW_REQUIRED`.

Both authors approved the exact synchronized F2 baseline and separately
authorized stages 141 and 142. The GO receipt bound commit
`ca95aa656e73694e80c8030e42608f6712099404`, source-binding SHA-256
`e69ca282c046e43325ee2ae1f0b53f76bf2ee017771423ace1e866c646bf21a8`
and runtime-receipt SHA-256
`bc743876f470bca0e2fb9c8df73bd4f07f2d61f5de8600b5b2150e7cb8b4386d`.

Stage 141 completed all 40 frozen scenarios and 160,000 attempts in 1,600
sealed chunks. Stage 142 completed the 15 shifted-DGP truth scenarios in 240
sealed checkpoints. All truth precision and independent score-formula checks
passed; maximum MCSE divided by typical coefficient SE was 0.007842.

The applicable conjunction passed in 30/30 scenarios, with 10/10 mandatory
boundary scenarios reported and no numerical failures. A second complete
adjudication was byte-identical to the first. The closest bias result was
`C4_X3` at 0.098054 against the 0.10 limit; the largest coverage Wilson upper
bound was 0.972152 in `C0_X3` against the 0.975 limit. These near-boundary
results must remain visible in later interpretation.

This PASS validates the single `delta_profile` OLS/HC3/t(64) procedure only in
the frozen synthetic operating domain. It does not validate all historical
targets, erase G2/G2B HOLD decisions, establish a causal decomposition or
automatically authorize any real WP2 or external-cohort disease effect.

The next stage is an effect-blind real-data applicability preflight. It must
freeze the single real estimand, common-support donor set, design matrix,
measurement inputs and DGP-to-real applicability diagnostics before any disease
coefficient is read or fitted.
