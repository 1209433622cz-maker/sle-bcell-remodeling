# npj Systems Biology and Applications target-adaptation contract

Status: `TARGET_SELECTED_NPJ_SBA_SCIENCE_FROZEN_FORMAT_REFREEZE_REQUIRED`

## Scientific freeze

The following must not change during adaptation:
- R1 = `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`;
- C9R = `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`;
- corrected external outcome unlock = false;
- cohorts, samples, genes, programs, regulators, thresholds, seeds and inferential families;
- all numerical results and source-data values.

## Allowed target-specific changes

- title;
- abstract;
- section names and order;
- location of ethics/data/code/AI declarations;
- reference formatting;
- supplement organization;
- figure typography, line width, dimensions and color accessibility;
- cover letter;
- reporting/checklist forms;
- file naming and portal organization.

## Required npj manuscript changes

1. `Article` content type.
2. Title <=15 words.
3. Unstructured abstract <=150 words.
4. `Introduction` instead of `Background`.
5. Results with subheadings.
6. Discussion without a separate Conclusions section.
7. Methods with subheadings.
8. Data availability after Methods.
9. Code availability after Data availability.
10. Funding moved into Acknowledgements.
11. Generative-AI disclosure retained in Methods.
12. Nature-style references.
13. Remove BMC-style Additional file terminology.

## Required supplement changes

- correct title to match manuscript;
- remove all `Supplementary Methods`;
- preserve Supplementary Tables and Figures;
- merge Supplementary Information into one PDF;
- expose large machine-readable outputs as `Supplementary Data` files.

## Required figure rerender

Build from frozen source tables only.

Target contract:
- Arial/Helvetica;
- target final-size text approximately 8 pt;
- panel labels bold lower-case;
- line widths >=1 pt;
- RGB;
- no red-green direct contrast;
- white background;
- vector PDF;
- multi-panel figure in one file;
- exact source-data hashes unchanged.

## STOP rules

Do not:
- add a cohort;
- change a threshold;
- rescue R1/C9R;
- substitute a mapper;
- add a TF/regulon database;
- add a new gene-set family;
- change seeds;
- recompute corrected external disease outcomes;
- manually edit final PDF figures.

## Final gate

`PASS_NPJ_SBA_TARGET_SPECIFIC_REFREEZE_AUTHOR_APPROVAL_REQUIRED`

This gate requires technical compliance only and must not be described as a new scientific PASS.
