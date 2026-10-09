# Stage 0B implementation incidents and resolution

## Harmony coordinate orientation

`harmonypy 0.2.0` returned corrected coordinates as cells by PCs, whereas the
historical fitter assumed PCs by cells. The shared fitter now validates both
orientations by shape before assigning `X_pca_harmony`. This is a runtime
compatibility repair and does not change the model specification.

## A2 normalization denominator

The first minimal rebuild normalized after subsetting to the 3,000 A2 features.
That implementation produced six clusters and A0-A2 ARI 0.446, failing the
prespecified structural gate. A CPU rerun of the same incorrect object produced
ARI 0.405 and therefore did not repair the result.

Source review then identified the discrepancy: the historical workflow filtered
to 16,357 genes, computed full-background library-size factors, normalized and
log-transformed, and only then selected A2 features. The Stage 0B builder was
corrected to use exactly that denominator without reselecting HVGs. The corrected
full-cell rebuild produced five clusters, ARI 0.795 and NMI 0.680.

## Legacy Harmony diagnostic

An isolated `harmonypy 0.0.10` diagnostic was attempted before the denominator
error was identified. It stopped in legacy `sklearn.KMeans` with Windows native
OpenMP exit code `-1066598273`, including under a single-thread retry. No legacy
output was used. The isolated package and noncanonical large diagnostic objects
were removed after the corrected current-runtime rebuild passed.

## Governance conclusion

The failed objects were treated as diagnostics, not overwritten evidence. Their
findings are recorded here, but they are not scientific outputs and do not enter
the Stage 0B integrity manifest. The final gate is based only on the corrected,
source-consistent, disease-blind rebuild.
