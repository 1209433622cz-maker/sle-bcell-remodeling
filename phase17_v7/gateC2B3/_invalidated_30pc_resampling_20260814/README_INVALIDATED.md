# Invalidated Gate C2B3 30-PC resampling archive

**Status:** `INVALIDATED_REPRESENTATION_DIMENSION_MISMATCH`

This directory preserves the original 20-replicate Gate C2B3 resampling output from
14 August 2026. The source C2B2 labels were generated from all 50 Harmony dimensions,
but this archived run used only the first 30 dimensions. Its HOLD decision and all
stability metrics are retained for audit history only and have no biological or
inferential authority.

The original run reported r=0.4 median/minimum ARI 0.603/0.305, median mapping
agreement 0.954, and zero median Jaccard for cluster 2. These values must not be used
to merge or delete clusters because representation dimensionality was not held fixed.

The copied files were verified against the original
`17_gate_c2b3_integrity_manifest.csv` before the active run was invalidated. The
corrected schema-v2 workflow uses all 50 dimensions and writes additional hierarchical
policy and cluster-transition diagnostics.

The post-separation audit resolved all 24 manifest rows across this archive and the
active run directory, with every recorded size and SHA-256 digest matching. Valid
candidate-mapping and marker files remain active; invalid stability and freeze files
are held here. The per-cell gzip is retained locally under the repository's existing
`*.csv.gz` Git exclusion.
