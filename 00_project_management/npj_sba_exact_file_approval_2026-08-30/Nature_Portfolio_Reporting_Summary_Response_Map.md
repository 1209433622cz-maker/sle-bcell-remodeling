# Nature Portfolio Reporting Summary response map

Status: `TECHNICAL_RESPONSE_MAP_AUTHOR_REVIEW_AND_ADOBE_TRANSCRIPTION_REQUIRED`

Official dynamic form:
`official_forms/Nature_Portfolio_Reporting_Summary_dynamic.pdf`

Flat reference:
`official_forms/Nature_Portfolio_Reporting_Summary_flat_reference.pdf`

The dynamic PDF is an XFA form and must be opened and completed in Adobe Reader.
This response map is not the submitted form. Both authors must review the final
official PDF generated from these answers.

## Header

- Corresponding author(s): Teng Qi.
- Last updated by author(s): enter the actual Adobe completion date.
- Field-specific reporting: Life sciences.

## Statistics

| Official item | Proposed response | Evidence location |
|---|---|---|
| Exact sample sizes | Confirmed. Exact cells, donors, samples and libraries are reported for each analysis. | Methods; Results; figure legends; `npj_statistics_reporting_map.csv` |
| Distinct or repeated measurements | Confirmed. Donors or sample-by-processing-cohort strata are the biological units; repeated cells are not treated as independent replicates. | Methods: cohort assembly, pseudobulk and statistical analysis |
| Test and sidedness | Confirmed. Unless explicitly directional, tests are two-sided; positive-direction families are identified. | Statistical analysis and multiplicity |
| Covariates | Confirmed. Covariates and sensitivity specifications are described for each composition and transcription model. | Methods; Supplementary Data 3 |
| Assumptions and corrections | Confirmed. Count-aware models, robust quasi-likelihood inference, HC3 covariance and Benjamini-Hochberg families are declared. | Methods; Supplementary Data 3 |
| Estimates and uncertainty | Confirmed. Odds ratios, regression effects, confidence intervals and descriptive summaries are labeled. | Results; figure legends; reporting map |
| Null-hypothesis details | Confirmed where inferential tests were performed. Exact P or q values and test families are available; GSE23307 n=2 is explicitly descriptive without an inferential P value. | Results; legends; Supplementary Data 3 |
| Bayesian analysis | No Bayesian analysis was performed. | Methods |
| Hierarchical or complex designs | Confirmed. Testing level is the donor or sample stratum, with cells aggregated before disease-effect inference. | Methods |
| Effect sizes | Confirmed. Model effects, odds ratios, standardized program differences and correlations are reported with their definitions. | Results; Methods; reporting map |

## Software and code

### Data collection

No primary participant recruitment or specimen collection was performed. Public
GEO and CELLxGENE records were downloaded for GSE174188, GSE135779 and GSE23307.
Accession, checksum and restoration information is recorded in the repository
and frozen archive.

### Data analysis

Custom analysis and audit code, environment specifications, deterministic seeds
and decision records are available at:

- https://github.com/1209433622cz-maker/sle-bcell-remodeling
- https://doi.org/10.5281/zenodo.22151739

The cited scientific release is GitHub v1.1.0 and Zenodo record 22151739.

## Data

Public source data are available through NCBI GEO under GSE174188, GSE135779
and GSE23307. Project-generated figure source data and complete statistical
outputs are included in Supplementary Data 1-3 and the version-specific Zenodo
archive. Large recomputable matrices are not duplicated from their source
repositories. Third-party data remain subject to source terms.

## Research involving human participants or human data

### Reporting on sex and gender

This is a retrospective secondary analysis of public de-identified datasets.
Sex and gender metadata were not uniformly available or harmonized across all
cohorts and contrasts and were not used as inferential covariates. No post hoc
sex- or gender-stratified claim is made. This limitation is stated in the
Discussion.

### Race, ethnicity or other socially relevant groupings

The present study did not recruit participants or assign race or ethnicity.
Source-study population descriptors were not uniformly harmonized across the
public datasets and were not used to support subgroup claims. Recruitment and
reporting remain governed by the source publications.

### Population characteristics

The study analyzes public SLE and control B-lineage transcriptomic datasets.
GSE174188 contributes 150,402 quality-controlled B-lineage cells from 259 donors,
271 samples and 88 libraries. GSE135779 provides source-label-defined independent
donor-level replication. GSE23307 provides paired descriptive IFN-beta context
from two healthy donors. Exact eligibility and support counts are reported with
each analysis.

### Recruitment

No participants were recruited by the present study. Recruitment, consent and
source-study eligibility were conducted by the original investigators and are
described in the cited publications.

### Ethics oversight

The present study used only publicly available de-identified data and involved
no recruitment, intervention or new specimen collection. No additional ethics
approval was required for this secondary analysis. Source-study ethics and
consent procedures are reported in the original publications. Consent for
publication is not applicable because no identifiable participant information
is reported.

## Life sciences study design

### Sample size

All eligible public biological units passing prespecified quality-control,
support and mapping rules were included. No prospective sample-size or power
calculation was performed for this retrospective secondary analysis. Exact
analysis sizes are reported in Results, Methods, legends and source tables.

### Data exclusions

Exclusions followed prespecified quality-control, support and mapping criteria.
No cells, samples or donors were excluded after inspection of disease outcomes.
Disease fields were protected during B-lineage identity reconstruction.

### Replication

Robustness includes twenty within-library representation resamples, twenty
end-to-end disease-blind reconstruction resamples, donor-nonoverlap internal
analysis, source-label-defined GSE135779 replication, and assignment-exchange
propagation. R1 and C9R failures are retained as explicit HOLD boundaries.
GSE23307 is descriptive perturbation context, not an inferential replication.

### Randomization

No experimental allocation was performed in this retrospective secondary
analysis. Randomization was therefore not applicable to the present analysis.
Deterministic seeds were fixed for computational resampling and are recorded.

### Blinding

Disease fields were protected during B-lineage identity reconstruction and
identity adjudication. Disease outcomes were accessed only after representation
qualification. Corrected source-label-independent external outcomes remained
locked after calibration failed.

## Materials, systems and specialized methods

- Antibodies: not involved.
- Eukaryotic cell lines: not involved.
- Animals and other organisms: not involved.
- Plants: not involved.
- Palaeontology and archaeology: not involved.
- Clinical trial data: not involved; this is not a clinical trial.
- Dual-use research of concern: not involved.
- ChIP-seq: not involved.
- Flow cytometry: not involved.
- MRI-based neuroimaging: not involved.
- Functional connectivity, graph analysis and predictive modeling form sections:
  not involved. Graph-based clustering is an analytical preprocessing method,
  not a clinical predictive model.

## Author review cautions

- Do not enter `n/a` where the form asks for an explanatory sentence.
- Do not label GSE23307 as replication or attach an inferential P value.
- Do not state that sex, gender, race or ethnicity were balanced or analyzed.
- Do not claim that R1 or C9R passed.
- Do not call the source-label-defined GSE135779 result source-label-independent.
- Preserve the exact GitHub release and Zenodo DOI.
