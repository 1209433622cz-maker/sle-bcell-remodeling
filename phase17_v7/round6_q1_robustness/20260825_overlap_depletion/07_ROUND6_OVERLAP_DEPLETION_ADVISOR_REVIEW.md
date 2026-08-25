# Round 6 STAT1/STAT2 overlap-depletion advisor review

Date: 2026-08-25
Decision: **ACCEPT AS QUALIFIED SUPPORTIVE SENSITIVITY**

## Question

Does the STAT1/STAT2 regulatory signal persist after removing genes shared with the frozen IFN/ISG program or the broader MSigDB M5911 interferon-alpha response set?

## Integrity checks

- The same three confirmatory contrasts and tested-gene backgrounds were reused.
- Frozen CollecTRI signs were reused without target re-selection.
- Baseline ULM target counts and slopes reproduced the frozen results within the prespecified tolerance.
- Branch-specific Benjamini-Hochberg correction was applied separately to each method across six regulator-by-contrast tests.
- All 36 depleted method-level results retained the expected upward direction.
- Eleven depleted ULM models retained at least 10 targets and underwent leave-one-target analysis; every leave-one-target estimate preserved direction.
- The M5911-depleted discovery STAT2 model retained only 8 targets and was correctly excluded from leave-one-target analysis.

## Frozen 12-gene IFN/ISG depletion

| Method | Upward direction | Dedicated q < 0.05 | Interpretation |
|---|---:|---:|---|
| ULM | 6/6 | 6/6 | All 95% confidence intervals remained above zero; minimum slope retention was 53.5%. |
| CAMERA | 6/6 | 5/6 | Discovery STAT2 remained upward but was not significant after six-test correction (q=0.326). |
| FRY | 6/6 | 6/6 | Direction and corrected support were retained throughout. |

The minimum target retention was 78.6% (discovery STAT2, 11/14 targets). These results support the statement that the regulatory signal is not explained solely by the 12 frozen positive-arm genes.

## M5911 depletion

| Method | Upward direction | Dedicated q < 0.05 | Main limitation |
|---|---:|---:|---|
| ULM | 6/6 | 5/6 | Discovery STAT2 retained 8/14 targets; slope 0.391, 95% CI -0.745 to 1.526, q=0.500, 17.9% of baseline slope. |
| CAMERA | 6/6 | 2/6 | Discovery STAT1, discovery STAT2, internal-nonoverlap STAT1 and childhood STAT2 did not pass the six-test correction. |
| FRY | 6/6 | 5/6 | Discovery STAT2 remained upward but did not pass correction (q=0.099). |

M5911 depletion therefore produces substantial attenuation and method-dependent loss of corrected significance. It does not reverse the direction, and the internal-nonoverlap and childhood ULM results remain positive, but it prevents any claim that STAT1/STAT2 support is independent of the broader interferon-response gene space.

## Authorized manuscript interpretation

The preferred wording is:

> STAT1/STAT2 activity remained directionally concordant after removing either the frozen 12-gene IFN/ISG arm or the broader M5911 response set. Support was robust to the narrow 12-gene depletion but attenuated after M5911 depletion, particularly for discovery STAT2, indicating that regulatory convergence is not reducible to the core program genes yet remains partly coupled to the broader interferon-response transcriptome.

Do not claim:

- overlap-independent regulation;
- an IFN-independent STAT1/STAT2 mechanism;
- a unique upstream regulator or ligand;
- universal corrected significance after M5911 depletion.

## Figure placement

Place `Supplementary_Figure_S8_overlap_depletion` and its Source Data in the Supplementary Information. Main Figure 5 should retain the simpler three-branch evidence architecture.

## Next decision

This R2 result is complete and publication-usable. The next P0 method task is R1 full-pipeline disease-blind identity resampling. Manuscript integration should wait until the R1 scientific run is complete or explicitly deferred, so the robustness paragraph can be revised once rather than repeatedly.
