# SLE B-cell remodeling — npj Systems Biology and Applications + QiTeng v0.3.21 全量导师审计

Date: 2026-08-30

## 1. Audit baseline

- Repository: `1209433622cz-maker/sle-bcell-remodeling`
- Latest reviewed `main`: `0c7361022510b47e8cc7ae82baafd4b6dcff7c8e`
- Target-specific refreeze commit: `1257119efe6b3f88e581e3456af7e36506a02e70`
- Frozen scientific release commit: `f1859ff8498d5569a1d5027b36ed18c8b7c7536f`
- Reproducibility DOI: `10.5281/zenodo.22151739`
- Target journal: `npj Systems Biology and Applications`
- Writing framework: `QiTeng Academic Writing Skill v0.3.21`

## 2. Executive decision

The scientific analysis is mature and should remain frozen before first submission. The highest-value remaining work is not a new cohort or another positive sensitivity. It is a final source-driven render and semantic hardening pass.

Independent status:

`HOLD_NPJ_SBA_PREAPPROVAL_TECHNICAL_HARDENING_REQUIRED`

This is a technical pre-approval HOLD, not a scientific HOLD.

The project should not yet bind both authors to the current exact package hashes because two reproducible technical defects remain in the current refreeze implementation:

1. `apply_npj_sba_style()` partially reverses its own npj font/line-width settings by executing the generic style clamp afterwards.
2. `npj_statistics_reporting_map.csv` contains several human-readable claims that contradict their own machine decisions.

## 3. Scientific contribution and novelty class

QiTeng novelty router classifies the strongest contribution as **inferential novelty with replicated empirical support**.

The paper is not strongest as:

- a discovery of interferon biology in SLE;
- a new B-cell taxonomy;
- a generalized plasmablast/B_ASC expansion paper;
- a causal STAT1/STAT2 mechanism paper;
- a clinical biomarker paper.

The strongest defensible contribution is:

> Disease-blind reconstruction and biological-unit-aware inference expose different reproducibility ceilings across cell-identity, composition and within-compartment transcriptional layers. Hard state assignments retain explicit stability/transfer limits, whereas a prespecified IFN/ISG process-level signal remains supported after uncertainty propagation and in an independent, source-label-defined external cohort.

This framing matches the journal's systems-biology logic better than a conventional autoimmune descriptive paper.

## 4. Evidence ladder

### Identity

- 150,402 hard-QC GSE174188 B-lineage cells.
- Fine state solution fails frozen stability requirements.
- Broad B_CONV/B_ASC is an analysis scaffold, not a universal taxonomy.
- End-to-end R1 remains `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY` because B_ASC state overlap is below the unchanged criterion.

### Composition

- Primary B_ASC effect: OR 0.947, 95% CI 0.636-1.410, P=0.787.
- The correct statement is “not supported”, not “no enrichment exists”.
- Secondary flare cannot replace the primary null.

### Transcription

- Primary B_CONV IFN/ISG effect remains the central positive result.
- Internal donor-nonoverlap remains accession-internal.
- Independent GSE135779 supports the frozen IFN/ISG program in the childhood donor analysis.

### Transfer boundary

- Corrected source-label-independent external mapping does not pass the frozen calibration gate.
- No corrected external disease effect is estimated.
- Therefore external replication remains source-label-defined.

### Genome-wide boundary

- Cross-dataset genome-wide rho=0.026.
- The manuscript can claim program-level replication, not a globally shared disease transcriptome.

### Regulatory/orthogonal context

- STAT1/STAT2 support is convergent and observational.
- CAMERA has an explicit discovery-STAT2 exception.
- Broader M5911 depletion attenuates support and blocks an overlap-independent regulator claim.
- GSE23307 at n=2 is descriptive perturbational context only.

## 5. QiTeng v0.3.21 manuscript audit

### 5.1 Title

Current 15-word title is appropriate for an E2 manuscript. Aggressiveness is approximately level 2: interpretive but bounded. It does not claim causal mechanism or clinical utility.

### 5.2 Abstract

The 140-word abstract follows the QiTeng original-research landing logic:

`GAP -> DESIGN -> CENTRAL RESULT -> EXTERNAL SUPPORT -> BOUNDARY -> BOUNDED CONCLUSION`

No need to add more sensitivities. The abstract is already at the correct late-stage salience budget.

### 5.3 Introduction

The original target version contained one editorially self-weakening phrase: `neither interferon activity nor plasmablast biology is novel`.

The hardened version changes this to:

`interferon activity and plasmablast biology are well established yet strongly context dependent.`

This preserves scientific honesty but moves novelty to the correct inferential owner.

The Introduction landing has also been tightened from an “intended contribution” statement to an explicit research task: which features survive increasingly stringent reconstruction and validation, and which remain cohort-specific, representation-dependent or mechanistically unproven.

### 5.4 Results

Results remain effect-first and evidence-class aware. The key textual hardening is the explicit use of `source-label-defined` in the GSE135779 heading and external evidence ownership.

No numerical result is changed.

### 5.5 Discussion

The main target manuscript contained two consecutive end-of-Discussion conclusion paragraphs because the old Conclusions section had been folded into Discussion without fully removing the duplicate landing.

The hardened manuscript removes this redundancy and compresses Discussion from 1,081 to 996 words while retaining all material boundaries.

This implements QiTeng late-stage Salience Redistribution rather than generic shortening.

### 5.6 Methods

Methods remain intentionally detailed because reproducibility-critical information belongs here. No method information required to reconstruct the study was deleted.

The external validation subsection is renamed to `Source-label-defined GSE135779 validation` to maintain Methods-Results terminology lock.

### 5.7 Citations

The hardened manuscript retains 32 references. First-appearance order is monotonically 1 through 32, with no missing reference and no renumbering drift.

## 6. Hardened manuscript artifacts

New pre-approval candidate:

- `SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.docx`
- `SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.pdf`
- `SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.md`

QA:

- 31 pages.
- 140-word abstract.
- Accessibility: 0 high / 0 medium / 0 low.
- No drawing object in the manuscript body, matching the source document's object inventory.
- 31/31 LibreOffice-rendered 1547×2002 page PNGs opened and visually reviewed individually at full-page resolution; contact sheets were used only as a secondary overview.
- No clipping, overlap, broken glyph, abnormal page break or corrupted reference surface.

## 7. Figure audit

The target package correctly preserves 15 source-driven figures and byte-identical source CSVs. Visual architecture is strong and should not be redesigned conceptually.

The remaining problem is implementation, not figure logic.

### Current exported main-figure measurements

- Figure 1: fonts 7-8 pt; minimum vector width 0.60 pt.
- Figure 2: fonts 7-8 pt; minimum vector width 1.00 pt.
- Figure 3: fonts 7-8 pt; minimum vector width 1.00 pt.
- Figure 4: fonts 7-8 pt; minimum vector width 1.00 pt.
- Figure 5: fonts 7-8 pt; minimum vector width 0.90 pt.

The target code declares an npj contract of 8-pt target text and >=1 pt positive line width, but the style function applies the generic clamp afterwards. This must be fixed at source and rerun.

### Figure semantic hardening

During the source-driven rerender:

- Figure 2 `No primary B_ASC enrichment` -> `Primary B_ASC enrichment not supported`.
- Figure 1 external evidence node -> `GSE135779 source-label-defined replication`.
- Figure 4 title/panel ownership -> explicit source-label-defined replication.

All source-data hashes and numeric values must remain unchanged.

## 8. Machine-readable statistics-map audit

Correct the following claims at the builder level:

- R1: criterion did not meet the frozen state-specific requirement.
- C3_PRIMARY: primary B_ASC difference was not supported.
- C5_GENOMEWIDE: genome-wide concordance was weak.
- C9R: corrected mapper did not qualify for outcome estimation.
- TF_DEPLETION: broader M5911 depletion does not support overlap-independent regulation.

Add exact regression assertions so a machine `decision=HOLD/NOT_SUPPORTED` can never coexist with a positive human-readable claim.

## 9. Public repository status

README and REPRODUCIBILITY are currently one stage behind the repository. They should be updated after hardening to reflect:

- target journal selected;
- target-specific package built;
- final technical hardening before exact-file author approval;
- scientific release remains v1.1.0 / Zenodo 22151739;
- no scientific reanalysis;
- official JCR-Q1 and CUHK-Shenzhen APC/OA receipts still pending.

Do not modify the scientific release tag or Zenodo DOI for this formatting-only hardening.

## 10. Journal fit

npj Systems Biology and Applications remains a strong fit because its current scope explicitly includes computational analysis of complex biological systems, disease modeling, single-cell systems biology and systems immunology.

The editorial hook should be the evidence hierarchy and inferential robustness, not IFN novelty alone.

The current systems-immunology Collection remains open, but a regular Article is still the cleaner default because the paper is not a multi-omics or dynamical-modeling study.

## 11. What not to do before first submission

Do not add:

- a new cohort;
- a new clustering solution;
- a substitute external mapper;
- a relaxed threshold;
- a new TF database;
- a new gene-set family;
- post-hoc subgroup searching;
- an attempt to convert R1/C9R to PASS.

These actions would reopen the multiplicity/selection space and weaken the manuscript's strongest methodological feature: explicit preservation of negative gates.

## 12. Current readiness

- Scientific design: 98%.
- Statistical rigor: 98%.
- Evidence-boundary discipline: 99%.
- Manuscript argument architecture: 99% after QiTeng hardening.
- Source-data integrity: 100%.
- Figure visual architecture: 97%.
- Figure target-style artifact compliance: 88% pending rerender.
- Machine-readable claim semantics: 82% pending builder repair.
- Public repository current-state documentation: 80% pending sync.
- Overall first-submission readiness: approximately 93%.

## 13. Next stage

Formal next stage:

`NPJ_SBA_FINAL_RENDER_AND_SEMANTIC_HARDENING`

Required completion criteria:

1. fix the npj style branch;
2. add exported-artifact font/line-width tests;
3. rerender all 15 figures from frozen source tables;
4. retain 15/15 source-data byte identity;
5. synchronize the hardened manuscript text and figure ownership labels;
6. fix the statistics map and tests;
7. update README/REPRODUCIBILITY;
8. rebuild DOCX/PDF/supplement/cover/package;
9. perform dual-render and deterministic-hash QA;
10. only then obtain exact-file author approval;
11. archive official JCR-Q1 and APC/OA receipts and authorize portal submission.

No additional biological analysis should precede this gate.
