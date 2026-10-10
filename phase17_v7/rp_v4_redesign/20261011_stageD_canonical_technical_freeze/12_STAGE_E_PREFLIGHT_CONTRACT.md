# RP v4 Stage E author sign-off and final-G2C preflight contract

Status: `HOLD_FINAL_G2C_AND_NEW_COHORT_OUTCOMES`.

Before final execution, the authors must explicitly approve every field in
`10_STAGE_E_AUTHOR_SIGNOFF_TEMPLATE.json`: one `delta_profile` estimand; one
four-column OLS/HC3/t(64) method; 40 scenarios x 4,000 attempts; seed base
2026101004 with outer stage 141 and truth stage 142; unchanged acceptance and
truth-precision rules; no replenishment, deleted scenarios or G2D rescue; and no
automatic real-outcome unlock even if synthetic G2C passes.

The machine preflight must then bind the actual runner, independent truth engine,
adjudicator, contracts, environment and calibration model by SHA-256; prove
checkpoint/resume and overwrite refusal on non-final streams; reject any real
response input; and emit an execution estimate without touching stage 141/142.

The final G2C may begin only after a separate gate states
`GO_FOR_FULL_SYNTHETIC_G2C`. Large SRA download requires its own authorization.
