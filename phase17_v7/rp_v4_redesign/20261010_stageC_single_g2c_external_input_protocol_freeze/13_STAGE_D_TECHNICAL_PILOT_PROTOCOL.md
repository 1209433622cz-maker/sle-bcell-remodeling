# RP v4 Stage D technical-pilot protocol

## Allowed

- Implement the frozen HC3-t kernel wrapper, shifted DGP generator and truth engine.
- Run unit tests and a tiny counter-addressed technical pilot for shape, support,
  reproducibility, checkpoint and manifest validation.
- Generate (but do not automatically start) resumable NCBI SRA download and
  count-reconstruction scripts.
- Verify S0/S1 feature mapping using count-only objects with outcome fields absent.

## Not allowed

- Do not run the 160,000-attempt final G2C grid.
- Do not alter the estimand, t(64) method, 40 scenarios, thresholds or seed base.
- Do not inspect or fit real WP2, case-control, activity or treatment effects.
- Do not describe GSE262846 and GSE118254 as independent confirmations.
- Do not modify manuscript, figures, submission package, Release or Zenodo.

## Stage D exit

PASS requires deterministic replay, independent truth precision qualification,
all implementation tests, a complete checkpoint/run manifest, resource benchmark
and exact author approval of the final contract.  Only a later explicit gate may
authorize final simulation or large external download.
