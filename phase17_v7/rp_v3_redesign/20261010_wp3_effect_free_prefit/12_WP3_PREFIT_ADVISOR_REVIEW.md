# RP v3 WP3 effect-free prefit advisor review

**Date:** 2026-10-10
**Decision:** `PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION`

## Independent review of the received candidate

The received ZIP contained 12,189 entries and 52,724,494 uncompressed bytes.
No path traversal or duplicate path was present. Its manifest verified
12,188/12,188 payloads, and the packaged test suite passed 20/20 when invoked
through the documented discovery command.

All 22 candidate input receipts matched current local canonical files exactly
in size and SHA-256. This includes the Stage 0B external sufficient-count
objects, score contracts and reference parameters, five historical design
matrices and the ID-linked childhood design.

An independent Windows replay reproduced eight of ten preflight outputs
byte-for-byte. The other two were semantically identical after normalizing
Windows path separators and CRLF line endings. Therefore the candidate's
scientific result is reproducible, but its unqualified `10/10 byte-identical`
claim is platform-local rather than cross-platform. The project-side tool now
fixes path ordering, POSIX relative paths and LF output bytes.

## Project-side result

The canonical implementation passed 9/9 focused tests and 22/22 real-input
checks. It verified:

- a 672 by 32,738 integer count object with 4,537,683 stored nonzero entries;
- 56 source samples and 56 unique donors;
- exact eight-label-to-B_CONV count and cell closure in 56/56 samples;
- 54 donors meeting the frozen 50-cell support rule;
- a 43-donor childhood primary design with 11 controls and 32 SLE donors;
- 12/12 IFN genes, all 18,873 frozen rank-background symbols and the exact
  43-control reference parameters;
- the source `T_rank` convention as average rank divided by background size;
- absence of verified age, sex, ancestry, treatment, activity and processing-
  batch columns in the current ID-linked design.

A second project-side run in a new output directory regenerated all ten machine-
produced files byte-for-byte, confirming that the deterministic path and newline
repairs work on Windows.

Two adult donors have metadata but no source matrix and were not reconstructed.
Two matrix donors fail the frozen 50-cell rule. The preflight starts from the
archived sufficient-count object; it does not rebuild the raw TAR/barcodes.

## Boundary of the PASS

This PASS establishes object identity, eligibility, closure, feature coverage
and source-operator identity. It does not establish cross-platform measurement
equivalence, clinical calibration or uncertainty calibration. It generated no
new score, disease-group expression summary, coefficient, interval or P value.

Stage 0B had already shown that `T_frozen` and `T_rank` are finite on the 54
eligible external rows. The new contribution here is stronger source/donor
linkage, complete denominator/partition checks, explicit covariate accounting
and a fail-closed project-side execution boundary. It must not be described as
a new external validation result.

## Decision and next stage

WP2 remains closed, WP4 remains held, and WP3 disease-outcome execution remains
unauthorized. One narrowly bounded, outcome-free measurement-sensitivity stage
is permitted under `11_WP3_EFFECT_FREE_MEASUREMENT_SCOPE_PROTOCOL.md`.

```text
current: PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION
next: WP3_EFFECT_FREE_MEASUREMENT_SENSITIVITY_PROTOCOL_AND_DRY_RUN
WP3_OUTCOME_EXECUTION_AUTHORIZED: false
submission: HOLD
```

If the next stage cannot add interpretable measurement information beyond
computability and the historical IFN replication, RP v3 should close or be
retopiced rather than expanded.
