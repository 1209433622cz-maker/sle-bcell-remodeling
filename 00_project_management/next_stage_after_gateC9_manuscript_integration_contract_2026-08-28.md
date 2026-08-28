# Post-Gate-C9 manuscript integration contract

**Superseded on 2026-08-28:** independent implementation review invalidated the
original C9 PASS. The corrected full run is on calibration HOLD. The positive
integration instructions below are retained only as history and must not be
executed. See `gateC9_technical_correction_contract_2026-08-28.md` and the current
action report. Do not use the numerical anchors below as publication evidence.

**Status:** PRE-INTEGRATION FREEZE

**Date:** 2026-08-28

## 1. Purpose

Integrate the completed GSE135779 label-agnostic sensitivity into the current
manuscript and submission package without changing the formal Round 6 identity
HOLD or displacing the source-label-defined external validation.

## 2. Frozen scientific interpretation

The authorized new statement is:

> The childhood GSE135779 IFN/ISG direction remained positive and significant
> when B-lineage selection and B_CONV mapping were reconstructed without source
> cell labels or disease outcomes, using two independently calibrated broad-state
> mappers.

This is supplementary robustness evidence within the existing independent
dataset. It is not a third cohort, a new discovery analysis, a repair of the R1
state-overlap HOLD or evidence for a discrete IFN-high B-cell subtype.

## 3. Numerical anchors that may not change

- All external matrix cells parsed: 363,083 across 56 samples.
- QC-passing cells: 353,527.
- Primary cluster-selected B-lineage cells: 36,630.
- Post hoc source-B recovery: 32,313/32,741, or 98.69%.
- Non-B source-label contamination: 1,108/33,421, or 3.32%.
- Confident mapping: 97.76% by elastic net and 95.33% by centroid correlation.
- Childhood eligible donors: 11 HC and 32 SLE under the frozen 50-cell rule.
- Elastic-net IFN/ISG effect: 0.30597; bootstrap 95% CI 0.20782-0.41433;
  P=0.0005868; four-program BH q=0.002347.
- Nearest-centroid IFN/ISG effect: 0.30418; bootstrap 95% CI
  0.20751-0.41130; P=0.0005293; four-program BH q=0.002117.
- Minimum leave-one-donor effects: 0.28066 and 0.27898; no reversal.
- Per-cell margin sensitivity contamination: 15.05%. This limitation must be
  disclosed; the margin sensitivity cannot replace the primary cluster method.
- Adult IFN/ISG direction remained positive but was not significant; it stays
  secondary and underpowered.

## 4. Required manuscript changes

1. Add one Methods subsection describing protected metadata, sample-wise QC,
   sample-wise Leiden clustering, frozen lineage modules, reference-only
   donor-grouped calibration, the 50-cell rule and the four-program BH family.
2. Add one Results paragraph reporting the primary cluster-selection quality,
   two childhood mapper effects and leave-one-donor result.
3. Add a short Discussion sentence stating that the external signal is not an
   artifact of source-provided cell labels while preserving the R1 boundary.
4. Add one supplementary figure based on the frozen PDF/SVG and its source-data
   table. Do not promote it to a main figure.
5. Add a supplementary methods/results table containing the complete C9
   program family, selection audit and confidence-calibration summary.
6. Update the claim matrix, reporting checklist, reproducibility manifest and
   data/code availability text.

## 5. Prohibited changes

- Do not refit, retune or relabel C9 after outcome access.
- Do not replace the source-label-defined GSE135779 analysis with C9.
- Do not report the per-cell margin branch as equally clean; its contamination
  exceeded the 10% quality threshold.
- Do not convert the Round 6 R1 HOLD to PASS.
- Do not use `independent validation` to imply a third dataset or a causal
  experiment.
- Do not add another public dataset before first submission unless a new formal
  advisor contract identifies a specific unresolved claim.

## 6. Package and release gate

The next package may be released only after all of the following pass:

- manuscript, supplement, legend and source-data numerical cross-check;
- deterministic document and ZIP rebuild;
- WPS visual review of every affected page;
- PDF font, clipping, accessibility and page-order review;
- independent adversarial claim-boundary audit;
- GitHub clean/synced verification;
- updated Zenodo version with matching repository commit and payload hashes;
- portal filename map and author-facing upload checklist refresh.

The next operational target is therefore
`GATE_C9_MANUSCRIPT_SUPPLEMENT_INTEGRATION_AND_RELEASE_REFREEZE`, followed by
journal submission. It is not another exploratory analysis round.
