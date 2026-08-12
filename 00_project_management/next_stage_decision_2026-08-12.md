# Next-stage decision: complete Gate C2B2 before neutral state freezing

## Advisor decision

Gate C2B1 has passed, but the project remains **NO-GO for disease inference and
submission**. The immediate objective is the complete, disease-blind Gate C2B2
representation run on all 150,402 hard-QC cells, followed by a documented review.

## Evidence now frozen

- Complete-library residual-risk scoring succeeded for 88/88 libraries and
  reconciled 150,402/150,402 cells.
- Automatic residual-risk calls total 1,972 (1.31%); the maximum library rate is
  6.49%, with no library above 20%.
- Calls show weak correlations with key QC metrics, modest RNA-content shifts and
  no mixed-lineage enrichment. They are not automatic exclusions.
- The primary branch retains all hard-QC cells; the residual-risk-negative branch
  is sensitivity-only until disease-blind state localization.
- Full-PBMC audit identified 4,711 sensitive outside-label candidates, of which
  768 have at least two core B-receptor genes and only 57 also have low non-B
  signal. Source `B cell` plus `plasmablast` remains the primary input; candidates
  are mapping-only.

## Run now

From the project root in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B2_full_representation.ps1 `
  -ResumeRunDir ".\phase17_v7\gateC2B2\20260812_full_representation"
```

The runner freezes recurrent HVGs and then fits three separately checkpointed
branches. Rerunning the same command reuses valid checkpoints. For a two-stage
handoff, append `-PreparationOnly` first, then rerun without that switch.
If any branch reaches 20 Harmony iterations without convergence, rerun the same
directory with `-HarmonyMaxIter 40`; the convergence contract invalidates and
recomputes lower-limit branch checkpoints.

## Gate C2B2 review contract

Gate C2B2 may pass only if all of the following are documented:

1. The primary object contains all 150,402 hard-QC cells and no protected disease,
   clinical or outcome field.
2. Residual-risk scores and source indices align exactly; the sensitivity branch
   removes only the prespecified 1,972 automatic calls.
3. Library-aware recurrent HVGs are frozen before representation fitting. The
   primary excludes technical nuisance and immunoglobulin-dominance genes; matched
   ISG-excluded branch is retained. IG-dominance sensitivity is recorded as
   non-evaluable because the source feature space lacks canonical IG constant genes;
   no proxy program is substituted.
4. The unintegrated representation is preserved. Harmony by technical library must
   improve relevant mixing and bridge-sample consistency without erasing marker-
   coherent rare states or unsupported cohort structure.
5. Multi-resolution states have broad donor, sample and library support; no state
   is accepted solely because it separates on UMAP.
6. Primary versus singlet and ISG-excluded state assignments show
   interpretable stability. Material branch discordance requires biological review,
   not threshold shopping.
7. Residual-risk calls and the highest-rate small library are localized on the
   disease-blind graph before any final exclusion decision.
8. Refined outside-label B-lineage candidates are projected as a mapping sensitivity
   before any input expansion is considered.

## Ordered work after C2B2

1. **Gate C2B3 neutral-state freeze:** marker dictionary, ranked markers, coverage,
   adjacent-resolution and resampling stability, residual-risk localization and
   B-lineage candidate mapping.
2. **Outcome unlock:** join protected disease metadata only after cells, representation
   and neutral labels are frozen.
3. **Gate C3 composition:** cohort-supported sample-level abundance models with
   donor-aware sensitivity for repeated samples.
4. **Gate C4 transcription:** raw-count sample-by-state pseudobulk, within-cohort
   contrasts and explicit separation from abundance effects.
5. **Gate C5 validation:** frozen mapping/signatures in GSE135779, with childhood and
   adult strata analysed separately and transfer uncertainty reported.

## Publication threshold

The current work strengthens rigor but does not by itself establish an upper-Q1
biological advance. Journal selection remains provisional until frozen discovery
states, sample-level disease effects and independent validation are known. A
credible upper-Q1 attempt requires replicated biology plus convergent external
regulatory evidence; technically correct clustering alone is insufficient.

## Next decision point

The next advisor review is triggered by complete Gate C2B2 branch checkpoints and
their full-data diagnostic tables. Until then, disease outcomes remain locked and
no Results claim, state name or final journal target is authorized.
