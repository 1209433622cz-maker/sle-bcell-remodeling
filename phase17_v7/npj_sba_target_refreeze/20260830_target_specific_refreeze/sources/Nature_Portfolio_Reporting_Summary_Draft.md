# Nature Portfolio Reporting Summary draft

Status: `DRAFT_FOR_PORTAL_FORM_TRANSCRIPTION_AND_AUTHOR_REVIEW`

## Study design

- Secondary analysis of publicly available, de-identified human transcriptomic data.
- Discovery: GSE174188; independent source-label-defined replication: GSE135779; descriptive perturbational context: GSE23307.
- Disease fields were protected during B-lineage identity reconstruction.
- Biological units were sample-by-processing-cohort strata for GSE174188 and donors for GSE135779.

## Replication and robustness

- Twenty within-library frozen-representation resamples and twenty end-to-end reconstruction resamples.
- R1 decision retained as `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`; no threshold or seed rescue.
- C9R decision retained as `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`; no corrected external disease effect estimated.
- Assignment exchanges were propagated through frozen composition and IFN/ISG models as same-data sensitivity analyses.

## Statistical reporting

- Exact tests, biological units, sidedness, multiplicity families, sample sizes, P values, q values and confidence intervals are indexed in `npj_statistics_reporting_map.csv`.
- No inferential P value was calculated for GSE23307 at n=2 donors.
- No cells or donors were excluded after outcome inspection; all eligibility rules are described in Methods and executable decision records.

## Data and code

- GEO accessions: GSE174188, GSE135779 and GSE23307.
- Code: https://github.com/1209433622cz-maker/sle-bcell-remodeling
- Frozen reproducibility archive: https://doi.org/10.5281/zenodo.22151739

## Software

Pinned environments and package versions are recorded in `REPRODUCIBILITY.md` and the archived environment files. This draft must be transcribed into the journal's current portal form and checked by both authors before submission.
