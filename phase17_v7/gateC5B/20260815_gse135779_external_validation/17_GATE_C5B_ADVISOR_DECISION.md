# Gate C5B advisor decision

## `PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION`

GSE135779 was analyzed from the Gate C5A frozen source and design objects after successful no-effect software and import qualification.

| Analysis | IFN/ISG effect | 95% CI | Four-program BH q |
|---|---:|---:|---:|
| childhood_min50 | 1.042 | 0.681 to 1.402 | 2.98e-06 |
| combined_min50 | 0.996 | 0.655 to 1.337 | 1.31e-06 |
| adult_min50 | 0.968 | -0.123 to 2.060 | 0.291 |
| combined_min20 | 0.965 | 0.643 to 1.286 | 6.75e-07 |
| combined_min100 | 0.939 | 0.602 to 1.276 | 4.06e-06 |

## Stability and specificity

- Donor LOO range: `0.987` to `1.094` across 43 deletions.
- Source-label omission range: `1.019` to `1.051` across B-caSC0 to B-caSC7.
- IFN ranked-gene coherence: childhood expected-direction fraction `1.000`, camera FDR `1.85e-07`.
- Cross-dataset IFN genes: `10` jointly tested, positive in both datasets fraction `1.000`.
- Childhood controls: platelet `0.049`, ASC/UPR `0.221`, pan-B `-0.232` versus IFN `1.042`.
- Shared tested transcriptome Spearman rho: `0.026`; the replication claim is program-specific, not genome-wide.

## Interpretation

The frozen IFN/ISG program satisfies the independent replication contract and may be integrated as the manuscript's central cross-dataset transcriptional result.

The adult result remains secondary, and the source annotation authorizes only a broad conventional-B interpretation.

## Next action

Gate C6 manuscript claim integration plus targeted external regulatory evidence.
