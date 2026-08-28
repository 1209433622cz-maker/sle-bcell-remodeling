# Gate C9 technical correction and supersession contract

Date: 2026-08-28. Status at registration: correction specified before corrected
outcomes, but after original C9 outcomes were known. This is not a new prospective
preregistration. The original pre-outcome contract and run remain preserved.

## Independently verified implementation defects

1. Reference mapper training normalized only the selected-feature counts, whereas
   external mapping normalized the whole transcriptome before feature subsetting.
   The two feature spaces therefore used incompatible library-size denominators.
2. The original selected elastic-net threshold of 0.95 had reference B_ASC precision
   0.894074, below the declared 0.90 threshold. A diagnostic fallback was allowed
   to authorize outcome access. The original C9 PASS is invalid as gate authorization.
3. Outcome metadata supplied on the command line were not bound to the frozen
   protected input, and partial formal runs could satisfy a reduced sample gate.
   These are latent governance defects; no substitution or partial formal run has
   been demonstrated in the original 56-sample run.

The external independent review did not identify defects 1 and 2. Its recommendation
to integrate the original PASS is not adopted. Old outcomes are historical, not
current manuscript evidence. The previous integration contract is superseded here.

## Frozen correction scope

- Normalize reference counts to each cell's full 30,172-gene library total before
  subsetting the identical mapper features. External normalization is unchanged.
- Keep reference cell sampling, gene choice, alpha grid, confidence candidate grid,
  eligibility thresholds, QC, lineage modules, clustering, donor minimum, four-program
  family, outcome tests and seed unchanged. Refit calibration under corrected inputs.
- Diagnostic fallback parameters may be exported, but ineligible calibration must
  produce HOLD and prohibit protected-outcome access. No selective mapper rescue.
- Bind requested metadata to the hashed protected input; verify all prefreeze
  artifacts and executable code. Full formal runs require 56 samples/363,083 cells.
- Refuse nonempty run directories; never overwrite the original C9 outputs.
- Record package versions, script hashes, full-library versus feature-only totals,
  and known prior outcome exposure.
- Use two algorithmically distinct mappers sharing a reference and features. Do not
  call them two independent validations or call the analysis fully label-free.
- Plotting-only changes: fixed 170-mm canvas, 8-pt panel labels, 5-7-pt remaining
  text, editable vectors and an explicit known-label contamination metric.

## Execution and decision

Corrected run: `phase17_v7/gateC9R/20260828_normalization_correction`.

```powershell
powershell -ExecutionPolicy Bypass `
  -File "H:\cuhk-2025fALL\6013RP-wyf\audit_tools\run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1" `
  -PostUnblindingCorrection
```

If corrected C9A passes, run the unchanged outcome family and accept PASS/HOLD/NO_GO.
If calibration fails, stop outcome integration, retain the source-label-defined
primary GSE135779 replication, and report the mapping limitation without changing
the threshold or choosing the better-looking mapper. Neither outcome repairs R1
identity HOLD or changes the original pseudobulk estimand. No release/DOI update
is authorized merely by completion of this correction.
