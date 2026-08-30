# SLE B-cell remodeling → npj Systems Biology and Applications
## Exact-package hostile re-audit + QiTeng v0.3.21 + Nature/npj figure QC + next-stage decision

**Date:** 2026-08-30  
**Repository:** `1209433622cz-maker/sle-bcell-remodeling`  
**Observed GitHub main:** `a6050a779d32324d8085f543221da5ffcb545ace`  
**Frozen scientific release commit:** `f1859ff8498d5569a1d5027b36ed18c8b7c7536f`  
**Zenodo record:** `10.5281/zenodo.22151739`  
**Target journal:** *npj Systems Biology and Applications*  
**Article type:** Article  

### Authoritative uploaded artifacts

- Exact npj package ZIP SHA-256:  
  `F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`
- QiTeng Academic Writing Skill v0.3.21 ZIP SHA-256:  
  `C18AC4F0254286725B7449EA7B7E8DA89E8235B4FABA75B42A6E362D2AD87D99`
- Bundled package verifier:  
  `PASS: 20 files verified; exact-file author approval and submission authorization remain pending`

---

# 1. Executive decision

The scientific manuscript is mature and should remain frozen.

However, inspection of the **actual uploaded exact package**, rather than only machine gate receipts, exposed one real reader-facing defect:

> **Supplementary Figure S8 has its title/legend on Supplementary Information page 15, while the figure itself is moved alone to page 16.**

This was not a clipping or overlap failure, so previous technical gates legitimately did not detect it. It is nevertheless important because the current npj guidance asks that each figure legend be on the same page as the corresponding figure, states that the multi-panel guidance also applies to supplementary figures, and states that Supplementary Information is not edited, typeset or proofed by the journal.

Therefore the updated project state is:

`SCIENCE_FROZEN`  
`MAIN_TEXT_FROZEN`  
`MAIN_FIGURES_FROZEN`  
`S1-S7/S9-S10_FROZEN`  
`S8_LAYOUT_NARROWLY_UNFROZEN`  
`CURRENT_EXACT_PACKAGE_HOLD_BEFORE_AUTHOR_APPROVAL`

This is a **layout-only source-level repair**, not a scientific revision.

---

# 2. What remains scientifically correct

## 2.1 Central question

The paper should not be presented as a discovery that SLE contains an interferon signature.

Its defensible systems-biology question is:

> When identity, composition and within-state transcription are separated into distinct inferential layers, which layer of SLE B-cell remodeling remains reproducible under disease-blind reconstruction, biological-unit-aware inference, end-to-end state sensitivity and independent cohort replication?

The supported answer remains:

> **Process-level IFN remodeling is more reproducible than the tested hard B-cell state assignments.**

This is the manuscript's principal conceptual contribution and the reason it fits *npj Systems Biology and Applications*.

## 2.2 Evidence class

- IFN process-level signal: **E2 robust association**
- STAT1/STAT2 regulatory context: **E1 observational association**
- causal regulator: **not established**
- unique upstream IFN ligand: **not established**
- clinical utility: **not established**
- transferable universal B-cell taxonomy: **not established**

No evidence level should be promoted.

---

# 3. Full scientific audit

## 3.1 GSE174188 design and unit structure

The discovery source contains:

- 152,981 B-lineage source cells
- 150,402 cells after hard QC
- 259 donors
- 271 biological samples
- 88 technical libraries
- four processing cohorts

The analysis explicitly separates donor, biological-sample, technical-library and processing-cohort levels and protects disease variables during identity reconstruction.

This is a major strength because it prevents cell-level pseudoreplication from carrying the disease claim.

**Verdict: PASS.**

## 3.2 Disease-blind identity reconstruction

The five-state fine solution failed the frozen stability requirements and was correctly retained as a negative result.

The broad B_CONV/B_ASC partition is highly stable under the frozen representation, but the stricter end-to-end reconstruction gives a minimum state-median Jaccard of about **0.930**, below the frozen **0.95** criterion. Failure is localized mainly to B_ASC, while B_CONV remains highly concordant.

Correct interpretation:

`B_CONV/B_ASC = analysis scaffold`

not:

`B_CONV/B_ASC = universally transferable taxonomy`

**Verdict: R1 HOLD is scientifically correct and must not be rescued.**

Forbidden post-hoc actions include lowering the 0.95 threshold, adding favorable seeds, reselecting states or selecting an alternative result after outcome inspection.

## 3.3 Propagation of state-boundary uncertainty

Across 20 complete reconstruction perturbations:

- primary B_ASC composition OR approximately 0.896-0.967
- every corresponding confidence interval includes 1
- primary B_CONV IFN effect approximately 0.836-0.845
- donor-nonoverlap IFN effect approximately 1.059-1.087
- all propagated IFN intervals remain above zero

Thus, identity uncertainty does not reverse the disease-level conclusions.

**Verdict: PASS.**

## 3.4 B_ASC composition

Primary:

- OR = **0.9467**
- 95% CI = **0.6357-1.4097**
- P = **0.7873**
- n = **90 sample-cohort strata** (43 controls; 47 managed SLE)

Secondary flare:

- OR = **2.3029**
- nominal P = **0.0282**
- q = **0.0845**

The manuscript correctly treats the primary result as unsupported enrichment, not as proof of exact equivalence, and does not allow the secondary flare signal to overwrite the frozen primary result.

**Verdict: PASS.**

## 3.5 B_CONV IFN/ISG program

Primary:

- effect = **0.8366**
- 95% CI = **0.5254-1.1477**
- q = **2.98 × 10^-6**

Internal full:

- effect = **0.8561**
- q = **0.00462**

Donor-nonoverlap:

- effect = **1.0862**
- q = **3.61 × 10^-4**

The signal is also stable to support thresholds, residual-doublet restriction and leave-one-sample-out analyses.

**Verdict: PASS and remains the central disease signal.**

## 3.6 Independent GSE135779 replication

Childhood:

- 43 donors
- 11 controls / 32 SLE
- effect = **1.0418**
- 95% CI = **0.6812-1.4023**
- q = **2.98 × 10^-6**

Combined:

- effect = **0.9960**
- q = **1.31 × 10^-6**

Adult only:

- effect = **0.9684**
- CI crosses zero
- q = **0.291**
- correctly classified as directional, not confirmatory

Across 4,410 shared tested genes, genome-wide Spearman rho is only **0.026**, while all ten jointly tested frozen IFN genes are positive in both primary datasets.

Correct interpretation:

`prespecified IFN program replication`

not:

`global transcriptome replication`

**Verdict: PASS.**

## 3.7 Corrected source-label-independent external mapping

The corrected mapping branch contains:

- 56 external matrices
- 363,083 cells before QC
- 353,527 QC-passing cells
- 36,630 B-lineage candidates

At elastic-net diagnostic threshold 0.95:

- reference coverage = **0.941958**
- B_CONV precision = **0.996450**
- B_ASC precision = **0.885210**, below the frozen 0.90 criterion

The centroid mapper cannot be substituted post hoc simply because it performs better on this gate.

No corrected external disease outcome was estimated.

**Verdict: C9R HOLD is correct and must remain visible.**

## 3.8 Regulator / response evidence

STAT1 and STAT2 ULM activity is positive and globally significant across the three confirmatory contrasts.

Correlation-aware sensitivity:

- CAMERA: 6/6 positive; 5/6 BH-supported
- discovery STAT2 is the explicit CAMERA exception
- FRY: 6/6 positive and BH-supported

After depletion of the 12 frozen IFN genes, broad support remains.

After depletion of the broader M5911 response set, support materially attenuates, particularly for discovery STAT2.

GSE23307 contains only two healthy donors and is correctly treated as descriptive perturbational context.

Correct conclusion:

> convergent observational IFN-centred regulatory context

not:

> causal STAT1/STAT2 mechanism

**Verdict: PASS.**

---

# 4. QiTeng Academic Writing Skill v0.3.21 audit

The uploaded v0.3.21 Skill explicitly prioritizes argument reconstruction over cosmetic language editing.

Its core state machine is:

`KNOWN -> INSUFFICIENT -> GAP/TENSION -> RESPONSE -> EVIDENCE -> INTERPRETATION -> IMPLICATION -> BOUNDARY -> NEXT TEST`

For a manuscript already in **STABILIZATION**, the Skill states that **KEEP should dominate**.

The current npj manuscript already satisfies this logic.

## Introduction

Current route:

`single-cell inferential problem -> context-dependent SLE biology -> unresolved reproducibility question -> disease-blind systems response`

This is stronger than an IFN-discovery framing.

## Results

Current route:

`identity ceiling -> composition null -> reproducible IFN program -> independent replication -> external-transfer HOLD -> observational regulator context`

This is the strongest part of the manuscript.

## Discussion

Current route:

`central interpretive delta -> literature ownership -> apparent contradiction resolution -> replication boundary -> regulator boundary -> prospective translation -> limitations -> restrained landing`

The manuscript correctly allows negative evidence to change claim scope.

## Writing decision

**Do not reopen broad prose editing.**

Only the following should justify text changes before submission:

1. verified factual error;
2. journal-compliance correction;
3. exact wording inconsistency introduced by the S8 rebuild;
4. editor/reviewer-requested revision.

No new broad rewrite is recommended.

---

# 5. Nature/npj figure audit

The current target figure contract is appropriate for the actual journal:

- single-page vector PDF
- 170 mm width
- white background
- RGB
- same sans-serif typeface
- 8 pt text at expected publication size
- lower-case bold panel labels
- minimum 1 pt line width
- accessible colors
- no unnecessary decoration

The journal-specific 8 pt recommendation should override a generic attempt to force all figures toward a smaller flagship-Nature font convention.

Existing main figures and Supplementary Figures S1-S7/S9-S10 should remain frozen.

---

# 6. Newly identified S8 defect

## 6.1 Exact current behavior

In the **actual uploaded Supplementary Information PDF**:

- page 15: S8 heading + complete legend, then a large blank region;
- page 16: S8 four-panel figure only.

All other Supplementary Figures S1-S7 and S9-S10 have their headings/legends and figure content together on the same page.

Therefore S8 is the only supplementary figure with this pagination defect.

## 6.2 Why this matters

The current npj guidance says:

- each figure legend should be on the same page as its figure;
- multi-panel figure guidance applies to supplementary figures;
- Supplementary Information is uploaded essentially as provided and is not edited, typeset or proofed by the journal.

This makes S8 worth repairing before exact-file author approval.

## 6.3 Root cause

The current repository source builder inserts every supplementary figure at a fixed width of **6.35 inches**.

The current S8 source script under the npj branch creates S8 at **170 × 215 mm**.

At 6.35-inch insertion width, that aspect ratio produces an image too tall to remain on the page below the S8 legend, so the word processor moves the figure to the next page.

This is a layout-engine consequence, not a scientific-data problem.

---

# 7. Source-level S8 repair performed in this audit

A compact S8 candidate was rebuilt from the **unchanged frozen source-data CSV**.

Frozen source-data SHA-256:

`26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2`

Candidate S8 PDF SHA-256:

`47C72B16423605A1B57C5C5131CBD1BC8ED73F231CF69F0D7F73A5A95F687385`

Candidate properties:

- 170.0 mm width
- 155.0 mm height
- single-page vector PDF
- Helvetica / Helvetica-Bold
- all visible text = 8.0 pt
- minimum positive vector line width = 1.0 pt
- no clipped text
- no change to source data
- same four scientific panels:
  - a: ULM after 12-gene depletion
  - b: ULM after M5911 depletion
  - c: exact six-test BH q values
  - d: frozen target retention
- no changed estimate, CI, q value, target count or interpretation

The redesign improves density by:

- preserving the two top forest panels;
- wrapping long contrast labels rather than shrinking font;
- retaining exact q values in the heatmap;
- using a short in-panel fill note instead of a separate vertical colorbar;
- placing the depletion legend in unused x-space in panel d;
- preserving the 8 pt / 1 pt npj artifact contract.

---

# 8. Same-page proof

A layout proof was built with:

- the actual S8 heading;
- the actual full S8 legend;
- the same 8.5 × 11-inch page;
- 1-inch margins;
- the same 10.5 pt supplementary body size;
- 1.15 line spacing;
- the same 6.35-inch figure insertion width;
- the compact 170 × 155 mm S8.

Result:

> **heading + full legend + complete four-panel S8 fit cleanly on a single page.**

This validates the source-level repair strategy before touching the final package.

The proof is **not a submission file**; it is a pagination validation artifact.

---

# 9. Updated freeze matrix

| Component | Decision |
|---|---|
| Scientific hypotheses | FROZEN |
| Samples / donors / matrices | FROZEN |
| QC rules | FROZEN |
| R1 thresholds | FROZEN |
| C9R thresholds / mapper policy | FROZEN |
| Statistical models | FROZEN |
| Multiplicity families | FROZEN |
| Main manuscript scientific prose | FROZEN |
| Abstract/title | FROZEN |
| Main Figures 1-5 | FROZEN |
| Supplementary Figures S1-S7 | FROZEN |
| Supplementary Figure S8 numbers | FROZEN |
| Supplementary Figure S8 **layout** | **NARROWLY UNFROZEN** |
| Supplementary Figures S9-S10 | FROZEN |
| Supplementary Information pagination | **NARROWLY UNFROZEN** |
| Current exact package SHA | **DO NOT AUTHOR-APPROVE YET** |

---

# 10. Correct next-stage execution order

The next stage should no longer start with author approval of the current package SHA.

The correct sequence is:

### Gate N1 - S8 source-level layout repair

Modify only the S8 plotting layout in:

`audit_tools/phase17_round6_02_build_overlap_depletion_figure.py`

Keep all frozen inputs and values unchanged.

Recommended target height: approximately **155 mm** at 170 mm width.

### Gate N2 - source-driven figure rerender

Run the existing npj figure build chain.

Required assertions:

- 15 figure source CSVs remain byte-identical;
- no scientific reanalysis;
- all figure artifact contracts pass;
- only S8 layout bytes are expected to differ materially.

### Gate N3 - rebuild Supplementary Information from source

Use the existing target Markdown + document builder.

Required visual outcome:

- S8 heading, full legend and S8 figure on the same page;
- no new orphan heading;
- no new blank page;
- S9/S10 pagination remains clean;
- all ten supplementary figures remain embedded.

### Gate N4 - dual-render QA

Re-render the complete manuscript package through the established WPS/LibreOffice QA route.

Explicitly inspect:

- every Supplementary Information page;
- S7 → S8 transition;
- S8 → S9 transition;
- S8 figure at 100%;
- all four S8 panel labels;
- all q-value annotations;
- all target-count labels.

### Gate N5 - rebuild exact package

Rebuild the deterministic npj package.

Then:

- run package verifier;
- verify manifest 20/20;
- verify ZIP CRC;
- record the **new** package SHA-256;
- invalidate the old exact-file approval contract tied to `F4F8...` for submission purposes.

### Gate N6 - external/author gate

Only after the repaired exact package is frozen:

1. Zhi Chen exact-file approval;
2. Teng Qi exact-file approval;
3. official Reporting Summary;
4. official JCR Q1 evidence;
5. written CUHK-Shenzhen APC/OA determination;
6. portal submission authorization;
7. APC commitment authorization if applicable.

### Gate N7 - portal dry-run

Upload the repaired exact files and inspect the portal-generated review PDF before final submission authorization.

---

# 11. What should NOT be done next

Do not:

- rerun clustering to make R1 pass;
- reduce the B_ASC Jaccard threshold;
- add favorable resampling seeds;
- substitute centroid mapping for the frozen elastic-net gate;
- estimate corrected GSE135779 disease effects after the failed mapping gate;
- redefine IFN programs or regulator families;
- add exploratory DEG / trajectory / CellChat panels;
- expand causal language around STAT1/STAT2;
- rewrite the Discussion merely to create visible editorial activity;
- author-approve the old exact package SHA before S8 is repaired.

---

# 12. Reviewer-reserve scientific upgrades

No new science is required for initial submission.

If a reviewer requests stronger evidence, the most valuable additions would be:

1. a genuinely independent third donor-level SLE B-cell cohort tested with the fully frozen IFN program;
2. a longitudinal or treatment-annotated cohort testing whether the B_CONV IFN score associates with activity/response independently of B-cell composition and available clinical covariates;
3. a new prospective external-mapping protocol frozen before disease outcome access.

These should be treated as reviewer-reserve extensions rather than pre-submission fishing.

---

# 13. Updated assessment

| Dimension | Current assessment |
|---|---:|
| Research question / conceptual framing | 9.5 / 10 |
| Identity-composition-transcription separation | 9.8 / 10 |
| Statistical design | 9.6 / 10 |
| Independent biological replication | 8.5 / 10 |
| Mechanistic depth | 6.8 / 10 |
| Evidence calibration | 9.8 / 10 |
| Reproducibility / provenance | 9.9 / 10 |
| QiTeng argument architecture | 9.6 / 10 |
| Main-figure quality | 9.5 / 10 |
| Supplementary-figure scientific content | 9.5 / 10 |
| Current SI pagination / display readiness | 8.4 / 10 because of S8 split |
| Journal scope fit | 9.2 / 10 |
| Scientific readiness | ~95% |
| Administrative readiness | still gated |
| Current exact-package readiness | **HOLD pending S8 layout rebuild** |

After S8 source-level integration and full package rerender, the manuscript should return to exact-file author approval without reopening science.

---

# 14. Final advisor decision

The manuscript's credibility is strengthened by retaining the analyses that **failed** their prespecified gates. Those failures define the evidence ceiling and are part of the contribution.

The only justified pre-submission reopening found in this exact-package hostile audit is:

> **Supplementary Figure S8 layout + Supplementary Information pagination.**

Therefore:

`KEEP SCIENCE FROZEN`  
`KEEP QITENG TEXT FREEZE`  
`DO NOT RESCUE R1/C9R`  
`SOURCE-LEVEL REPLOT S8`  
`REBUILD SI`  
`RE-RUN FULL RENDER/PACKAGE QA`  
`FREEZE NEW EXACT SHA`  
`THEN AUTHOR APPROVAL / REPORTING SUMMARY / JCR-APC / PORTAL DRY-RUN`

This is now the highest-value next stage.
