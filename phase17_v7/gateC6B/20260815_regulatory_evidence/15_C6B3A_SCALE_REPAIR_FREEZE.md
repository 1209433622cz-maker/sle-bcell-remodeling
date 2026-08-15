# Gate C6B-3A objective GSE23307 scale repair

## `PASS_C6B3A_OBJECTIVE_SCALE_REPAIR_RERUN_REQUIRED`

The first orthogonal run exposed a units error before final audit. The GEO matrix is
Illumina BeadStudio quantile-normalized linear intensity: frozen-probe values span
37.65039 to 24,966.73, and the GEO processing statement does not report a log
transformation. Therefore the initial `median_log2_expression` label and its paired
effects are invalid.

## Frozen repair

- Transform every selected probe-sample value as `log2(x + 1)`.
- Then aggregate multiple probes per gene by the median.
- Retain the same four samples, 12 genes, 21 probes and paired-donor calculation.
- Do not calculate a powered P value for two donors.
- The repair is determined by the submitted scale and metadata, not response direction.

## Superseded outputs

Files `10` through `14` are retained only as an audit trail and must not be used in
figures, prose or scientific interpretation. Corrected outputs must be newly written
as files `16` through `20`; the original files are not overwritten.
