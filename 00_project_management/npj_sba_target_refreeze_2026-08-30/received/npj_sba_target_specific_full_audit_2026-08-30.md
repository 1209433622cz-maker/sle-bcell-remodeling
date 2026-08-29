# SLE B-cell remodeling — npj Systems Biology and Applications target-specific full audit

Date: 2026-08-30  
Repository: `1209433622cz-maker/sle-bcell-remodeling`  
Latest GitHub main reviewed: `82912054f8ac79e8941bf5dd8546aa30b290ad66`  
Current reproducibility DOI: `10.5281/zenodo.22151739`  
Current package SHA-256: `B7D30320ADFFF5D15E335A269AFC62E516C5001B2FF7BE4F8188E3B72AAFBFD5`  
Selected target: **npj Systems Biology and Applications**  
Recommended content type: **Article**

## Executive decision

Scientific content is sufficiently mature for first submission. No new cohort, mapper, gene-set family, regulator screen, clustering strategy or outcome-informed rescue should be added before first submission.

The current journal-neutral package is integrity-valid but is **not target-compliant** for npj Systems Biology and Applications. The correct next gate is:

`NPJ_SBA_TARGET_SPECIFIC_REFREEZE`

This gate is publication engineering plus source-driven figure rerendering, not a new biological analysis gate.

## Independent package integrity

The uploaded `SLE_Bcell_Submission_Package.zip` was independently rechecked.

- SHA-256: `B7D30320ADFFF5D15E335A269AFC62E516C5001B2FF7BE4F8188E3B72AAFBFD5`
- portable verifier: 30/30 PASS
- five main figures
- ten supplementary figures
- three nested source/statistical archives
- R1 HOLD preserved
- C9R HOLD preserved
- corrected external outcome unlock remains false

The package action record correctly identifies the package as journal-neutral and not authorized for upload.

## Journal fit

The target is scientifically well chosen.

The journal explicitly covers:
- computational and mathematical analysis of complex biological systems;
- disease modeling;
- single-cell systems biology;
- systems immunology.

The paper should therefore be positioned as a systems-biology study of **inferential robustness across biological layers**, not as a claim that interferon involvement in SLE is novel.

The central editorial hook should be:

> Disease-blind reconstruction reveals that hard B-cell state assignments have explicit reproducibility limits, whereas a process-level IFN/ISG program remains reproducible under biological-unit-aware inference, uncertainty propagation and independent source-label-defined validation.

The main editorial risk is novelty framing, not statistical weakness.

## Target-specific P0 gaps

### 1. Title exceeds the Article limit

Current title = 16 words.

npj Article guidance: title up to 15 words.

Recommended 15-word title:

**Disease-blind reconstruction distinguishes reproducible interferon remodeling from unstable B-cell state assignments in systemic lupus erythematosus**

This preserves the method, the contrast between inferential layers and the disease context without implying that biological B-cell states do not exist.

### 2. Abstract is structurally incompatible

Current abstract:
- approximately 356 words;
- structured with Background / Methods / Results / Conclusions.

npj Article guidance:
- no subheadings;
- up to 150 words.

Recommended 140-word target draft:

> Single-cell disease studies can conflate cell identity, abundance and transcription when unstable annotations are treated as fixed biological states. We reanalysed public systemic lupus erythematosus datasets using disease-blind B-lineage reconstruction and donor-aware inference. Among 150,402 discovery B-lineage cells, end-to-end resampling failed a prespecified antibody-secreting-cell overlap criterion, restricting broad B-cell compartments to an analysis scaffold, yet propagation of observed assignment exchanges preserved the primary composition null and conventional-B IFN/ISG effect. The IFN/ISG program replicated in independent GSE135779 childhood donors using a source-label-defined broad B-cell analogue despite weak genome-wide concordance. Corrected source-label-independent remapping failed prespecified calibration, so no corrected external disease effect was estimated. STAT1/STAT2 analyses provided convergent but observational support and weakened after broader interferon-gene depletion. These results separate reproducible process-level interferon remodeling from less stable hard state assignments without establishing a universal B-cell taxonomy, causal regulator or clinical utility.

### 3. Main-text section structure must be converted from BMC/Genome-Medicine style

Current:
`Background -> Methods -> Results -> Discussion -> Conclusions -> Abbreviations -> Declarations`

Recommended npj Article structure:
`Introduction -> Results -> Discussion -> Methods -> Data availability -> Code availability -> Acknowledgements -> Author contributions -> Competing interests -> References -> Figure legends`

Actions:
- rename `Background` to `Introduction`;
- move Methods after Discussion;
- fold the separate Conclusions into the final Discussion paragraph;
- remove the standalone List of abbreviations;
- remove the BMC-style `Declarations` wrapper;
- retain ethics details in a Methods subsection or journal-appropriate ethics declaration;
- retain generative-AI disclosure in Methods.

### 4. Data Availability is in the wrong location

Current Data Availability is in Declarations after the Conclusion.

npj requires a separate `Data availability` section after Methods and before References.

Recommended reader-facing text should cite:
- GSE174188;
- GSE135779;
- GSE23307;
- GitHub repository;
- current Zenodo DOI `10.5281/zenodo.22151739`.

Do not foreground the withdrawn historical DOI in the journal article.

### 5. Code Availability is missing as a dedicated section

Custom code is central to the paper.

Add a dedicated `Code availability` section immediately after Data availability and before References.

It should identify:
- GitHub repository;
- release tag / frozen commit;
- Zenodo DOI;
- restoration/provenance instructions.

### 6. Separate Funding section is not npj style

Current:
- Funding: `This research received no specific funding.`
- Acknowledgements: `Not applicable.`

npj guidance states funding belongs in Acknowledgements and a separate Funding statement is not permitted.

Recommended:
`Acknowledgements: This study received no funding.`

### 7. Supplementary Information has two target-specific P0 problems

#### 7a. Supplement title is inconsistent

The current Supplementary Information still uses:

`Disease-blind single-cell reconstruction separates ...`

while the manuscript uses:

`... distinguishes ...`

This is an internal package inconsistency and must be corrected in the target rebuild.

#### 7b. Supplementary Methods are not permitted

The current Supplement contains seven method-labelled sections:
- Supplementary Methods 1;
- Supplementary Methods 2;
- Supplementary Methods 2B;
- Supplementary Methods 3;
- Supplementary Methods 4;
- Supplementary Methods 5;
- Supplementary Methods 6.

npj explicitly states that Supplementary Methods are not permitted; all Methods must be in the main manuscript.

Most of these details already exist in the main Methods. Unique reproducibility details should either:
- be merged into the main Methods, or
- remain in the public reproducibility archive/code documentation if not necessary to interpret the article.

The submission Supplement should retain:
- Supplementary Tables;
- Supplementary Figures;
- short non-methodological explanatory notes only if necessary.

### 8. Supplementary upload organization should be simplified

npj requests Supplementary Information as a single merged PDF.

The present package already contains a 19-page merged Supplement PDF in which S1-S10 appear, so the ten separate supplementary-figure PDFs should remain internal/reproducibility assets rather than being uploaded as ten separate Supplement files.

Recommended portal-facing structure:
- `Supplementary_Information.pdf` — one merged PDF;
- `Supplementary_Data_1` — figure source data;
- `Supplementary_Data_2` — regulator sensitivity;
- `Supplementary_Data_3` — full statistical results.

Replace BMC-style `Additional file 1–4` terminology.

### 9. References should be converted to Nature style

Current reference count = 32, comfortably below the journal's 60-reference guide.

Target conversion:
- numbered sequentially;
- Nature-style abbreviated journal titles;
- >5 authors -> first author + `et al.`;
- dataset DOI/accessions retained;
- remove unnecessary raw website-style references where an accession/dataset citation can carry the provenance.

This is formatting only; no literature expansion is required.

### 10. Current generic Nature figure contract should be replaced by an npj-specific render contract

The current builder uses:
- non-panel text clamped to 5–7 pt;
- panel labels 8 pt;
- line widths clamped to 0.25–1.0 pt;
- output width 170 mm.

npj publication guidance instead states:
- Arial or Helvetica;
- RGB;
- vector files preferred;
- optimum final-size font around 8 pt;
- thinnest lines should be at least 1 pt;
- avoid red/green contrast;
- prepare at expected publication/A4-page width.

Therefore the correct action is **not manual editing**. Create an `npj_sba` style contract and rerender all five main and ten supplementary figures from the same frozen source tables.

Recommended assertions:
- main/supplement source-data SHA unchanged;
- all numeric text unchanged;
- panel inventory unchanged;
- font family Arial/Helvetica;
- target text ~8 pt at final size;
- no positive line width <1 pt;
- RGB output;
- no direct red-vs-green comparison;
- figure remains single-page vector PDF;
- no clipping after final-size render.

No biological analysis needs to be rerun.

## Statistical reporting audit

Strengths already present:
- explicit biological units;
- explicit multiplicity families;
- beta-binomial composition model;
- robust edgeR pseudobulk;
- HC3 program inference;
- CAMERA/FRY correlation-aware sensitivity;
- exact R1/C9R negative boundaries;
- no inferential P at n=2 GSE23307.

npj asks for exact test, n, sidedness, alpha and actual P value for every inferential test.

Recommended target QA:
- generate a machine-readable `npj_statistics_reporting_map` from frozen outputs;
- map every main-text and main-figure inferential claim to test, n, nominal P, adjusted q, sidedness and multiplicity family;
- fill any reporting gaps from existing frozen statistical tables only;
- do not recompute or select new tests.

## Cover letter

The current cover letter is correctly journal-neutral but is not suitable for the chosen target.

Problems:
- it does not name npj Systems Biology and Applications;
- it repeats much of the abstract;
- it does not explain journal fit;
- it calls the manuscript a `Research Article` rather than the journal's `Article` content type.

Target-specific cover letter should emphasize:
1. the systems-biology question;
2. single-cell systems biology / systems immunology fit;
3. why the inferential hierarchy is the novelty;
4. independent program-level replication and explicit negative gates;
5. public data/code and reproducibility DOI;
6. originality, related-work and conflict statements.

Do not sell the paper as a new discovery of SLE interferon biology.

## Systems Immunology Collection

An open `Systems immunology` Collection currently has a deadline of 12 September 2026.

The paper fits the broad computational systems-immunology theme, but it is not a multi-omics, dynamical-modeling or agentic-AI study.

Recommendation:
- target the journal as a regular **Article** first;
- use the Collection only if the authors explicitly want thematic placement and the final cover letter can explain the fit without changing the scientific story;
- do not rush or add analyses simply to match the Collection title.

## APC / OA

Current Original Research APC displayed by the journal:
- GBP 2,690;
- USD 3,490;
- EUR 2,990;
subject to applicable taxes.

Springer Nature publicly lists `The Chinese University of Hong Kong` as having Nature Portfolio OA coverage, but the submitting affiliation is `The Chinese University of Hong Kong, Shenzhen`. Eligibility must be confirmed by the institutional OA/library team and should not be inferred from the Hong Kong agreement.

If a discretionary waiver is needed, the journal states it should be requested at submission.

## Editorial-readiness assessment

| Module | Status |
|---|---:|
| Scientific design | 98% |
| Statistical rigor | 98% |
| Reproducibility / provenance | 99% |
| R1/C9R boundary transparency | 99% |
| Main narrative | 98% |
| Journal scope fit | 96% |
| Current title compliance | 80% |
| Current abstract compliance | 35% |
| Main section-format compliance | 65% |
| Data/Code availability compliance | 65% |
| Supplementary Information compliance | 55% |
| Generic Nature figure quality | 99% |
| npj-specific figure compliance | 80% |
| Cover letter target fit | 55% |
| Package integrity | 100% |
| npj submission readiness | ~75% |

The remaining ~25% is target formatting and publication engineering, not missing biology.

## Next stage

Formal next gate:

`NPJ_SBA_TARGET_SPECIFIC_REFREEZE`

No new exploratory science.

Deliverables:
1. npj-specific Manuscript DOCX/PDF;
2. 15 source-rerendered npj-style figures;
3. single merged Supplementary Information PDF without Supplementary Methods;
4. Supplementary Data 1–3;
5. target-specific cover letter;
6. Nature Portfolio Reporting Summary draft;
7. Editorial Policy Checklist draft;
8. JCR Q1 evidence receipt;
9. APC/OA eligibility receipt;
10. deterministic target-package manifest;
11. exact-file author approval.

Only after those items pass should portal upload be authorized.
