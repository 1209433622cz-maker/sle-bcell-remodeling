# SLE B-cell remodeling -> npj Systems Biology and Applications
## Post-S8 refreeze full advisor audit, QiTeng v0.3.21 review, Nature/npj figure QC, and next-stage decision

**Audit date:** 2026-08-31  
**Repository:** `1209433622cz-maker/sle-bcell-remodeling`  
**Observed GitHub main:** `427456201582bbd82f3ef233609852b7bcb20e9b`  
**Target journal:** *npj Systems Biology and Applications*  
**Scientific archive DOI:** `10.5281/zenodo.22151739`  
**Scientific release policy:** v1.1.0 remains frozen; S8 repair is submission-layout only.

---

# 1. Executive decision

## Final advisor state

`PASS_SCIENCE_FROZEN`  
`PASS_QITENG_TEXT_FROZEN`  
`PASS_NATURE_NPJ_FIGURE_CONTRACT`  
`PASS_S8_SAME_PAGE_REPAIR`  
`PASS_17_PAGE_SUPPLEMENT`  
`PASS_REPO_REFREEZE_EVIDENCE`  
`HOLD_ONLY_AUTHOR_INSTITUTION_PORTAL_AUTHORIZATION`

No new biological analysis, clustering, mapping, differential expression, TF analysis, pathway analysis, or figure redesign is justified before initial submission.

The project has crossed the point at which further scientific modification is more likely to create scope drift, multiplicity ambiguity, or post-hoc selection risk than to materially improve the central claim.

---

# 2. Independent verification performed in this audit

## 2.1 GitHub refreeze

GitHub `main` was independently checked and is currently:

`427456201582bbd82f3ef233609852b7bcb20e9b`

Commit message:

`Repair npj supplement S8 pagination`

The tracked action record binds the repaired exact package to:

- bytes: `15,196,223`
- SHA-256: `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`
- manifest-controlled files: `20/20 PASS`
- ZIP CRC: PASS
- deterministic double-build: PASS

The old `F4F8...BFD` package is correctly superseded.

## 2.2 Uploaded repaired S8

The uploaded `Supplementary_Figure_S8_overlap_depletion.pdf` was independently hashed:

`1AD5B47752A44B27107E12A4EE94343404B7AB12F59C8D697988AC854A52E665`

This exactly matches the GitHub refreeze record.

Independent PDF inspection found:

- 1 page
- 170.0 x 155.0 mm
- vector PDF
- embedded Arial / Arial Bold
- every visible text span = 8.0 pt
- minimum positive vector line width = 1.0 pt
- no out-of-page text
- no encryption / scan / form artefact

The frozen S8 source-data table in the baseline archive has 36 rows and SHA-256:

`26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2`

The post-repair repository record reports the same hash.

## 2.3 Uploaded repaired Supplementary Information

The uploaded `Supplementary_Information.pdf` was independently hashed:

`0882D26BA305C301FBAF08E24EBD4BDDC950045034CE97BE00EABE4485E69CF7`

This exactly matches the GitHub refreeze record.

Independent inspection found:

- 17 pages
- Letter size 612 x 792 pt throughout
- searchable text; not scanned
- embedded Times New Roman / Courier New fonts
- no out-of-page text
- no empty page

Page-by-page comparison with the pre-repair 18-page SI showed:

- pages 1-14: text unchanged
- new page 15: original S8 title/legend retained and repaired S8 added on the same page
- old page 17 -> new page 16: S9 text unchanged apart from page numbering
- old page 18 -> new page 17: S10 text unchanged apart from page numbering

Therefore the repair is exactly the intended pagination/layout delta.

## 2.4 Manuscript and Cover Letter freeze

The uploaded current manuscript and cover letter have different PDF binary hashes from the earlier package because they were re-rendered, but independent comparisons found:

- extracted manuscript text: exactly identical
- extracted cover-letter text: exactly identical
- manuscript: 31/31 rendered pages pixel-identical at 100 dpi
- cover letter: 1/1 rendered page pixel-identical at 120 dpi

Thus the statement "re-rendered for validation, text not changed" is independently supported.

## 2.5 Important provenance note about the uploaded hardening ZIP

The uploaded:

`20260830_final_render_semantic_hardening(1).zip`

is a **pre-S8-repair baseline archive**, not the repaired exact-package run.

Its internal Supplementary Information is still 18 pages and its S8 is the former tall layout.

This is not a scientific contradiction: it is useful provenance. However it must never be confused with the current submission package or used as evidence of the final 17-page SI.

The new exact package binary itself was **not uploaded in this audit turn**. Therefore its `02A385...` byte hash and internal `20/20` status are verified here from the tracked GitHub build/audit record, not by independently hashing the ZIP binary in this environment.

For the cleanest final sign-off, directly hash the actual local ZIP once immediately before the two author approvals.

---

# 3. Project purpose and systems-biology contribution

The manuscript's defensible question is not:

> Is interferon involved in SLE?

That is established background.

The manuscript asks:

> When cell identity, composition and within-state transcription are separated into different inferential layers, which layer of SLE B-cell remodeling remains reproducible after disease-blind reconstruction, biological-unit-aware inference, assignment-uncertainty propagation and independent cohort testing?

The supported answer remains:

> Process-level IFN/ISG remodeling is substantially more reproducible than the tested hard B-cell state assignments.

The current evidence hierarchy is internally coherent:

`identity ceiling -> composition null -> reproducible IFN program -> source-label-defined independent replication -> external-transfer HOLD -> observational regulator context`

This is the manuscript's real systems-biology novelty.

---

# 4. Scientific-method audit

## 4.1 Discovery hierarchy

The discovery scaffold retains:

- 150,402 hard-QC B-lineage cells
- 259 donors
- 271 biological samples
- 88 technical libraries
- four processing cohorts

The manuscript correctly distinguishes donor, sample, library and cohort levels and avoids treating cells as independent disease replicates.

**Decision: KEEP.**

## 4.2 Disease-blind identity reconstruction

The fine-grained identity solution failed the prespecified stability criteria and remains a negative result.

The frozen broad B_CONV/B_ASC scaffold passes frozen-representation resampling but fails the stricter end-to-end state-specific criterion because B_ASC median Jaccard falls to about 0.930 below the unchanged 0.95 criterion.

This is correctly retained as:

`analysis scaffold`

not:

`universally reproducible taxonomy`

**Decision: KEEP R1 HOLD. Never rescue it post hoc.**

## 4.3 Boundary propagation

Observed end-to-end assignment exchanges were propagated into the disease models without reselecting genes, samples, thresholds or models.

Across 20 perturbed partitions:

- primary B_ASC OR remains approximately 0.896-0.967 and all intervals include 1
- primary B_CONV IFN/ISG remains approximately 0.836-0.845 with intervals above 0
- donor-nonoverlap IFN remains approximately 1.059-1.087 with intervals above 0

Thus identity uncertainty changes the taxonomy claim, not the disease-level direction.

**Decision: PASS.**

## 4.4 Composition inference

Primary B_ASC composition:

- OR = 0.9467
- 95% CI = 0.6357-1.4097
- P = 0.7873
- BH q across the three frozen base contrasts = 0.7873

Secondary flare:

- OR = 2.3029
- P = 0.0282
- q = 0.0845

The manuscript correctly states that the primary comparison lacks statistical support and does not reinterpret it as equivalence.

**Decision: PASS.**

## 4.5 B_CONV transcription

Primary IFN/ISG:

- effect = 0.8366
- 95% CI = 0.5254-1.1477
- q = 2.98 x 10^-6

Donor-nonoverlap:

- effect = 1.0862
- q = 3.61 x 10^-4

No other frozen B_CONV program has comparable consistency through discovery plus internal robustness.

**Decision: PASS; this remains the principal disease signal.**

## 4.6 Independent GSE135779 replication

Childhood:

- n = 43 donors
- 11 controls / 32 SLE
- IFN/ISG effect = 1.0418
- 95% CI = 0.6812-1.4023
- q = 2.98 x 10^-6

Combined:

- effect = 0.9960
- q = 1.31 x 10^-6

Adult only is directionally positive but imprecise and is correctly not promoted to confirmation.

Across 4,410 shared tested genes:

- genome-wide Spearman rho = 0.026

Therefore the external claim is correctly:

`prespecified IFN-program replication`

not:

`global transcriptome replication`

**Decision: PASS.**

## 4.7 Corrected source-label-independent mapping

Corrected elastic-net calibration at threshold 0.95 retains high coverage but B_ASC precision remains approximately 0.885, below the frozen 0.90 state-specific criterion.

Centroid success must not replace the prespecified primary mapper after outcome exposure.

No corrected external disease outcome was estimated.

**Decision: KEEP C9R HOLD.**

## 4.8 STAT1/STAT2 and interferon response evidence

The regulator branch remains correctly classified as observational.

Correlation-aware CAMERA/FRY testing exposes discovery STAT2 as the explicit CAMERA exception.

12-gene depletion retains broad support; broader M5911 depletion materially attenuates support, particularly discovery STAT2.

This argues for:

`IFN-centred regulatory context`

not:

`causal STAT1/STAT2 mechanism`

**Decision: PASS.**

---

# 5. QiTeng Academic Writing Skill v0.3.21 audit

The actual uploaded Skill defines the core logical state machine:

`KNOWN -> INSUFFICIENT -> GAP/TENSION -> RESPONSE -> EVIDENCE -> INTERPRETATION -> IMPLICATION -> BOUNDARY -> NEXT TEST`

It also states that in manuscript **STABILIZATION**, KEEP should dominate and that claim strength must not exceed direct evidence.

## 5.1 Introduction

Current sequence:

`single-cell inferential problem -> context-dependent SLE biology -> precise reproducibility gap -> staged disease-blind systems response`

The Introduction ends with a research task rather than generic background.

**KEEP.**

## 5.2 Results

Current sequence:

`identity ceiling -> composition null -> IFN program -> independent replication -> source-independent transfer HOLD -> bounded regulator evidence`

Negative and non-generalizing evidence changes claim scope rather than being hidden.

**KEEP.**

## 5.3 Discussion

Current sequence:

`central interpretive delta -> reconciliation with prior SLE literature -> replication boundary -> regulatory boundary -> unsupported narratives removed -> prospective translation -> limitations -> restrained conclusion`

The Discussion does not promote E1/E2 evidence into mechanism or clinical utility.

**KEEP.**

## 5.4 Text decision

No broad QiTeng rewrite is warranted.

The only future text changes that should reopen the manuscript are:

1. a verified factual error;
2. a journal/editor request;
3. a reviewer-requested clarification;
4. an administrative declaration that must be updated;
5. a direct inconsistency introduced during portal conversion.

---

# 6. Nature / npj figure quality control

A current 15-figure set was reconstructed for audit using the unchanged final-hardening figures plus the repaired S8.

All 15 PDFs independently satisfy:

- one-page vector PDF
- width = 170.0 mm
- Arial / Arial Bold
- visible text = 8.0 pt
- minimum positive line width = 1.0 pt
- no text outside page bounds

Current heights:

- Figure 1: 130.7 mm
- Figure 2: 134.3 mm
- Figure 3: 137.9 mm
- Figure 4: 137.9 mm
- Figure 5: 163.0 mm
- S1-S7: ~123.5-128.3 mm
- S8: 155.0 mm
- S9: 160.0 mm
- S10: 110.0 mm

Visual contact-sheet review found no new clipping, legend obstruction, label loss or obvious panel imbalance.

## S8 specifically

The new layout is superior to the old 215-mm version because it:

- preserves all four evidence panels;
- preserves all exact q values;
- keeps 8 pt text instead of solving pagination by font shrinkage;
- uses two-line labels where needed;
- eliminates the redundant colorbar;
- moves the target-retention legend into unused data space;
- fits below the complete legend on SI page 15 without crowding.

**Decision: S8 repair is accepted as the final publication layout.**

---

# 7. Current manuscript / journal fit

The manuscript is well aligned with the journal's current stated scope:

- computational and mathematical analysis of complex biological systems
- disease modeling
- single-cell systems biology
- systems immunology

The current cover letter correctly frames the manuscript around a systems-level reproducibility problem rather than claiming novelty from rediscovering SLE interferon biology.

The largest editorial risk is still **perceived novelty**, not technical quality:

> an editor could initially see "public SLE scRNA-seq reanalysis + IFN" unless the evidence-hierarchy contribution is immediately understood.

The title, abstract, Introduction and cover letter now address this risk sufficiently. Further prose expansion would likely make the manuscript less efficient rather than more persuasive.

---

# 8. Current npj compliance observations

Current official guidance supports the present package architecture:

- initial submission does not need acceptance-stage formatting;
- figures may be separate high-resolution files if a combined manuscript is not used;
- figure legends should accompany their figures;
- supplementary information should be supplied as a separate single merged PDF;
- Supplementary Methods are not permitted;
- SI is not edited/typeset/proofed by the journal.

The repaired 17-page SI is therefore substantially safer than the superseded 18-page version.

## Reporting Summary nuance

The current npj instructions state that the Nature Portfolio Reporting Summary is requested with the **revised manuscript after peer review**, while authors are encouraged to submit the reporting forms earlier.

Therefore:

> Reporting Summary completion is excellent pre-submission hygiene, but it is not technically necessary to block an initial portal dry-run.

The Editorial Policy Checklist becomes operationally important if the manuscript is sent for peer review.

---

# 9. Remaining risk register

## P0 blockers before final upload authorization

1. Two authors have not yet approved the exact `02A385...` package.
2. The actual local new ZIP should be re-hashed immediately before those approvals.
3. Corresponding-author portal submission authorization is still pending.
4. APC commitment is still pending.

## P1 administrative evidence

1. Complete/approve Nature Portfolio Reporting Summary.
2. Prepare Editorial Policy Checklist.
3. Archive current-year official JCR evidence if required by the project/institution.
4. Obtain CUHK-Shenzhen APC/OA determination.

Current official APC for Original Research is **US$3,490 / £2,690 / €2,990**, subject to applicable tax, and the amount is determined by the date of acceptance. Institutional coverage must therefore be verified separately.

## P2 portal integrity

After upload:

- save portal-generated review PDF;
- save upload file list and submission receipt;
- compare portal manuscript text against the approved exact files;
- verify figure order and legends;
- verify S8 and SI remain intact;
- verify metadata, authorship, ORCID, corresponding-author details and declarations.

## P3 non-blocking engineering backlog

The new pagination gate is adequate for the current artifact, but its automated rule identifies the presence of **an image** on the heading page rather than cryptographically identifying the expected figure image.

Because the current SI was independently visually verified, this is not a submission blocker.

If the document pipeline is modified in a later revision, strengthen the gate by checking expected figure-image fingerprints, object identity, or heading-to-image ordering.

Do not reopen the current exact package solely for this engineering refinement.

---

# 10. Readiness assessment

| Dimension | Assessment |
|---|---:|
| Central scientific question | 9.6 / 10 |
| Systems-biology framing | 9.5 / 10 |
| Identity/composition/transcription separation | 9.8 / 10 |
| Statistical design and multiplicity | 9.6 / 10 |
| Independent biological replication | 8.6 / 10 |
| Mechanistic depth | 6.8 / 10 |
| Evidence/claim calibration | 9.9 / 10 |
| Reproducibility/provenance | 9.9 / 10 |
| QiTeng argument architecture | 9.7 / 10 |
| Main figures | 9.5 / 10 |
| Supplementary figures after S8 repair | 9.6 / 10 |
| SI publication readiness | 9.8 / 10 |
| npj scope fit | 9.3 / 10 |
| Scientific readiness | ~98% |
| Manuscript/figure readiness | ~99% |
| Administrative/portal readiness | ~85-90% |
| Need for additional pre-submission science | **NO** |

---

# 11. Next-stage decision

The project should now transition from:

`SCIENTIFIC DEVELOPMENT`

to:

`EXACT-FILE / AUTHOR / INSTITUTION / PORTAL CONTROL`

Recommended execution order:

1. Independently hash the actual local final ZIP and confirm exactly  
   `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`.
2. Zhi Chen and Teng Qi separately approve that exact SHA.
3. Prepare Reporting Summary and Editorial Policy Checklist; do not change the manuscript to answer form questions unless a real inconsistency is found.
4. Archive JCR/institutional APC-OA evidence.
5. Perform portal metadata dry-run.
6. Corresponding author separately authorizes submission and APC commitment.
7. Upload exact files.
8. Save the portal-generated review PDF and receipts.
9. Run one final post-upload semantic/visual comparison.
10. Submit.

---

# 12. Final advisor conclusion

The S8 repair closes the only material publication-layout defect identified in the previous hostile audit.

There is no remaining scientific reason to reopen:

- clustering;
- identity thresholds;
- B_ASC composition;
- IFN program definitions;
- pseudobulk models;
- external mapper selection;
- TF families;
- overlap-depletion analyses;
- main manuscript prose;
- main figures.

The failed R1 and C9R gates should remain visible. They are not weaknesses to be hidden; they are the evidence boundaries that make the final systems-biology claim credible.

**Final decision: freeze science, freeze QiTeng text, freeze the repaired figure set, and move to exact-file author/institutional/portal authorization.**
