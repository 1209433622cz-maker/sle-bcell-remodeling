# Gate C2B3 resampling invalidation notice

**Status:** `INVALIDATED_REPRESENTATION_DIMENSION_MISMATCH`

The 20-replicate output generated on 14 August 2026 used the first 30 Harmony
dimensions, whereas the source Gate C2B2 neighbor graph and Leiden labels were built
from all 50 dimensions in `X_pca_harmony`. The run therefore changed both the cell
subset and representation dimensionality and is not a valid resampling-only test.

The observed HOLD metrics cannot authorize cluster merging, cluster deletion,
neutral-state freezing or outcome unlock. They have been retained only as invalidated
audit evidence under:

`phase17_v7/gateC2B3/_invalidated_30pc_resampling_20260814`

The schema-v2 runner now requires 50/50 dimension matching, pins the current
`leidenalg` backend, records reference-cluster absorption and evaluates a locked
hierarchical policy order before any disease field is joined:

1. five-state r=0.4 solution;
2. four-state solution with platelet-overlay cluster 2 merged into cluster 0; and
3. three-state identity core with clusters 2 and 4 merged into cluster 0.

No scientific Gate C2B3 decision exists until the corrected full run completes.
