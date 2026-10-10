# RP v4 Stage C protocol requirements

## Allowed scope

1. Select exactly one primary G2C estimand and interval/identification strategy from the historical-development evidence.
2. Prespecify at most one fallback, including its activation rule and error allocation before final simulation.
3. Freeze new random streams, old-comparable and shifted DGP families, support rules, target registry, thresholds, compute budget and failure accounting.
4. Separate interval calibration from point-estimator bias; do not claim an interval-only change repairs the six G2B bias failures.
5. Keep `S0=T_frozen` primary and `S1=T_rank` sensitivity. S2 remains excluded unless one unique outcome-blind formula, denominator and missing-feature rule are justified.
6. For GSE262846 and GSE118254, decide raw-count reconstruction, donor identity/provenance and repeated-subset handling before any disease or activity model.

## Required pre-execution artifacts

- mathematical estimand and estimator specification;
- one primary method and optional single fallback contract;
- independent final-simulation seed manifest;
- DGP registry including prespecified distribution shifts;
- coverage, bias, type-I, support-stop and numerical-failure gates;
- compute and checkpoint budget;
- raw-count compatibility receipt for each external candidate;
- donor-overlap/provenance statement stronger than token comparison;
- result-blind chronology and author sign-off.

## Prohibited

- using old G2/G2B outcomes as final G2C confirmation;
- trying multiple final methods and selecting the first PASS;
- changing target, DGP, applicable domain or threshold after final results;
- fitting real WP2 effects or new-cohort disease/activity effects;
- promoting S2 by clinical significance;
- manuscript, figure, submission, release or Zenodo changes.

## Stop condition

Failure of the single frozen G2C strategy closes the decomposition branch. No G2D rescue is permitted under RP v4.
