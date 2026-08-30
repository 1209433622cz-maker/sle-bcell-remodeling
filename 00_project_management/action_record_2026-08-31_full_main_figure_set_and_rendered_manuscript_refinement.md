# 2026-08-31 Full main-figure set and rendered-manuscript refinement action record

## 1. Round objective

This round continued scientific presentation work without advancing submission execution. The author-confirmed npj Systems Biology and Applications package remained an immutable comparison baseline. The work completed the panel-by-panel adjudication of Figures 2-4, tested the previously deferred Figure 5e replacement from frozen gene-level records, assembled a complete five-figure scientific candidate, and rendered the corresponding manuscript candidate for page-level quality control.

The governing rule was unchanged: prefer a reproducible replot from frozen source records when a panel can be materially improved; otherwise retain the existing panel. No panel was altered merely to create visual novelty, and no existing PDF was manually edited.

## 2. Immutable author-confirmed baseline

- Exact package: `04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip`.
- Reconfirmed package SHA-256: `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`.
- Author order: Zhi Chen, then Teng Qi.
- Corresponding author: Teng Qi.
- Author identities, emails, ORCIDs and affiliation: author-confirmed.
- Author Contributions: author-confirmed.
- Funding: none.
- Competing interests: none.
- Generative-AI disclosure: author-confirmed as complete and accurate.
- Human-subject boundary: no new human subjects or restricted identifiable data.

The exact package was neither unpacked for editing nor rebuilt during this round. All new outputs live in an explicitly separate scientific-candidate directory.

## 3. Inputs, code and output boundary

Primary frozen inputs:

- Final-hardened manuscript: `phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening/sources/Manuscript.md`.
- Prior Figure 1a/Figure 5a candidate manuscript: `phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates/recommended_scientific_candidate/sources/Manuscript_figure_refinement_candidate.md`.
- Figure 2 Source Data SHA-256: `DAA6DDBAB469E0D510AB578BEE0A21AA73FA2D71184739E3F361C3EA6EC8DFE2`.
- Figure 3 Source Data SHA-256: `DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8`.
- Figure 4 Source Data SHA-256: `F3604F40DAEDB0DD01617BB223A8762323C8AAC7F16185292367B9A13FEC4755`.
- Baseline Figure 5 Source Data SHA-256: `21925F6916DDAF97760CF73622ED8E4B4CCBE5AE0B3B53C721FDF607C1C6F9A4`.
- Frozen GSE23307 paired-gene table: `phase17_v7/gateC6B/20260815_regulatory_evidence/17_GSE23307_LOG2P1_PAIRED_GENE_EFFECTS.csv`.
- Frozen paired-gene table SHA-256: `BD3FBCADB7F1321F5627D764EC2A1C8CF0A1BEFE330FF8B3B441CF5C987D08A5`.

Reproducible code added or extended:

- `audit_tools/phase17_c7_01_build_main_figures.py`: added an optional, assertion-protected Figure 5e paired-gene rendering path; the default path remains unchanged.
- `audit_tools/phase17_npj_sba_12_figure5e_gene_level_candidate.py`: builds and audits the Figure 5e candidate.
- `audit_tools/phase17_npj_sba_13_integrate_full_main_figure_candidate.py`: rebuilds Figures 2-4 from frozen inputs and integrates the five-figure candidate.
- `audit_tools/phase17_npj_sba_14_build_candidate_manuscript_document.py`: reproducibly builds the DOCX candidate from the candidate Markdown.
- `audit_tools/phase17_npj_sba_15_finalize_candidate_render_qa.py`: promotes the rendered PDF and records page/text/visual QA.
- `audit_tools/test_npj_sba_full_main_figure_refinement.py`: regression tests for package immutability, Source Data identity, Figure 5e provenance, narrow text change and render QA.

Candidate output root:

`phase17_v7/npj_sba_full_main_figure_refinement/20260831_figure5e_and_figures2to4_adjudication`

After removal of disposable per-page render PNGs and duplicate contact-sheet inputs, the retained candidate root contains 40 files and 10,115,418 bytes. The retained files are source data, vector and review-resolution figures, build/QA records, four manuscript contact sheets, and the candidate DOCX/PDF. Disposable render intermediates were not retained.

## 4. Complete panel-by-panel adjudication

### Figure 1

- **Figure 1a: replacement selected.** The workflow-and-identity-scope diagram replaces the text-only hierarchy. It defines the disease-blind input, permissible B_CONV/B_ASC scaffold, separate composition and pseudobulk branches, and the prohibition on hard fine-state assignments.
- **Figure 1b-d: retained.** Policy selection, replicate-level mapped ARI/mapping agreement, and state-specific Jaccard/marker support own distinct identity evidence and are not redundant with the workflow panel.

### Figure 2

- **Figure 2a: retained.** It owns the observed sample-level B_ASC distribution and adjusted group summaries. Replacing it with an effect-only forest would hide the data distribution.
- **Figure 2b: retained.** It synthesizes the five composition contrasts and makes the primary null distinguishable from secondary or sensitivity contrasts.
- **Figure 2c: retained.** It owns the mandatory minimum-cell, explicit-non-B and residual-doublet sensitivity checks. These cannot be merged into panel b without obscuring their prespecified status.
- **Figure 2d: retained.** It exposes all 90 leave-one-sample deletion estimates. A range-only summary would conceal influence structure.

Figure 2 therefore remains a coherent sequence: observed data -> estimand family -> mandatory sensitivity -> sample influence. No panel replacement was scientifically justified.

### Figure 3

- **Figure 3a: retained.** It ranks the four frozen transcriptional programs with uncertainty.
- **Figure 3b: retained.** It shows IFN/ISG robustness across support thresholds, residual-risk restriction, internal replication, donor-nonoverlap replication and the secondary flare contrast.
- **Figure 3c: retained.** It owns gene-level direction for the frozen IFN positive arm and preserves missingness rather than imputing filtered tests.
- **Figure 3d: retained.** It provides technical/biological specificity controls for platelet/ambient, ASC/UPR and pan-B families.

Figure 3 therefore moves from program prioritization to robustness, gene direction and specificity. All four roles are nonredundant.

### Figure 4

- **Figure 4a: retained.** It owns the childhood, combined, adult and support-threshold external estimates.
- **Figure 4b: retained.** It places discovery, internal and source-label-defined external standardized effects on one scale.
- **Figure 4c: retained.** It exposes the essential boundary: positive frozen IFN genes coexist with weak genome-wide concordance (`rho=0.026`).
- **Figure 4d: retained.** It owns donor-deletion and source-label-omission influence checks and prevents the external result from being read as source-label independent.

The four panels jointly distinguish replicated program direction from genome-wide agreement and mapping independence. No panel was replaced.

### Figure 5

- **Figure 5a: replacement selected in the preceding round and retained here.** The quantitative evidence matrix states coverage, result and inferential role rather than presenting three equal-weight text branches.
- **Figure 5b: retained.** It owns core and extended regulator activity effects with 95% confidence intervals.
- **Figure 5c: retained.** It owns the prespecified proliferation comparator family.
- **Figure 5d: retained.** It owns the three M5911 permutation-enrichment estimates. A lollipop restyling would not add evidence.
- **Figure 5e: paired-gene replacement selected in this round.** The two donor means were replaced by all 24 frozen donor-gene effects, with same-gene points connected solely to aid donor comparison.

## 5. Figure 5e alternative assessment

Four display strategies were considered under an explicit anti-overstatement rule:

1. **Retain two donor-mean bars.** This is concise and makes `n=2` obvious, but it hides the 12-gene distribution and can make the result look like two homogeneous aggregate observations.
2. **Use a 12-gene by two-donor heat map.** This is compact, but color encodes effect magnitude less directly, two columns are visually thin, and a heat map can encourage pattern interpretation that is not supportable with two donors.
3. **Use a donor-level raincloud or violin display.** Rejected because the 12 genes are a prespecified correlated program, not independent biological replicates; a distributional glyph would invite pseudoreplication.
4. **Use a paired gene-level dot display.** Selected because it reveals every declared effect, donor heterogeneity and the all-positive direction while preserving the donor-level descriptive boundary.

The selected panel contains 12 genes for each of HI1 and HI2. All 24 effects are positive. The original donor means are reproduced exactly from the gene table:

- HI1 mean: `3.293570512080079`; observed range approximately `1.22-5.81`.
- HI2 mean: `3.665668905432541`; observed range approximately `1.62-5.52`.

No P value was calculated or added. The panel is explicitly labelled `n=2; descriptive`, and the manuscript legend states that it carries no inferential P value.

## 6. Source Data integrity

The Figure 5 candidate Source Data preserves the original 29 rows byte-for-value at the table-content level and appends 24 declared gene-level rows. The resulting Figure 5 Source Data SHA-256 is:

`A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B`

The appended rows are transparently labelled as `GSE23307_paired_gene_log2p1_effect`; they do not replace the two original donor-mean rows. Fourteen panel-specific data assertions passed, including row count, donor count, 12 genes per donor, positivity and exact reproduction of the donor means.

Figures 2-4 were regenerated by the main-figure builder from their frozen Source Data. Twenty-nine builder assertions passed. Their candidate Source Data files are SHA-identical to the final-hardened baseline files.

## 7. Complete five-figure candidate

Recommended root:

`phase17_v7/npj_sba_full_main_figure_refinement/20260831_figure5e_and_figures2to4_adjudication/recommended_full_main_figure_set`

Selected replacements:

- Figure 1a.
- Figure 5a.
- Figure 5e.

Retained panels:

- Figure 1b-d.
- Figure 2a-d.
- Figure 3a-d.
- Figure 4a-d.
- Figure 5b-d.

Final figure audit:

| Figure | PDF SHA-256 | PNG SHA-256 | Size (mm) |
|---|---|---|---|
| Figure 1 | `97227D1EE742053A519E33407A63A4383ED469541D558EFC9566C416CD4BC494` | `717855E87962750BB8DF5FA4AFF127470D0F94CEDFC81D5BB686D31EB58FE229` | 170.0 x 130.677 |
| Figure 2 | `F9B652B2CC84D213ED9A80459A8AC5CA960DB0260D7E9FB4A2C83271EABC9194` | `2415FCE81FDF9BF7C56E77494485CA79E3D063DCF390E6450E2E60E965200CE5` | 170.0 x 134.274 |
| Figure 3 | `F8EDBF94AB3B545CD6DC4ECB29E7E4AFA890A38834296643BB516A3F3C0A4035` | `913B19C5D0E9513A95EA71CAD73CA88788CEA147B50B0DEF274B35F841CA1BCA` | 170.0 x 137.870 |
| Figure 4 | `328944493A1C8BAC2D8BE90EF561D08B6C07E008996897E785A853267AA7B0F9` | `3424D846876C549487F9DD76D64A433A074541FF4712FCE680FB375DC6094258` | 170.0 x 137.870 |
| Figure 5 | `B40EEC04B7F5439F980D93B423360E506D5532E8838364B702C61B01F845BA84` | `A3A458563BA2C661E376DFDFCD77D143CC39B634A985C50308838441A59E814F` | 170.0 x 211.001 |

All PDFs are single-page vector outputs. Figure 5 remains within a full-page scientific-figure height. Visual inspection found no clipping, incoherent overlap, blank panel or misleading legend placement. The first Figure 5e candidate placed the donor legend too close to the `n=2` annotation; the figure was regenerated with the legend at upper left before selection.

## 8. Manuscript interface and change boundary

Candidate Markdown:

`recommended_full_main_figure_set/sources/Manuscript_full_main_figure_candidate.md`

SHA-256:

`3890EA6D4F0188081954DCD1054CA5E535920DD47DF27A8BA52C28F9D2F836F3`

Relative to the preceding Figure 1a/Figure 5a manuscript candidate, this round changes exactly one clause: the Figure 5e legend. The donor-mean description is replaced by a gene-level paired-effect description with an explicit all-24-positive statement and unchanged `n=2`/no-inferential-P boundary.

Relative to the author-confirmed scientific baseline, the complete candidate contains only the three figure-interface changes already justified by selected replots: Figure 1a legend, Figure 5a legend and Figure 5e legend. No title, abstract, Results estimate, Methods statement, Discussion claim, reference identity, authorship field or declaration was changed in this round.

## 9. Candidate DOCX/PDF and render QA

Candidate DOCX:

`recommended_full_main_figure_set/documents/Manuscript_scientific_candidate.docx`

- SHA-256: `77DA55B5509FEF66CEE0D756D9FC1C8D7BEC243C0207F2FC08D7CB3D9B3B42B0`.
- Size: 60,984 bytes.
- Format: 12 pt manuscript text, double spacing, line numbering and running header.
- Embedded main figures: none; figures remain separate scientific files.

Candidate PDF:

`recommended_full_main_figure_set/documents/Manuscript_scientific_candidate.pdf`

- SHA-256: `D1435EC34ACDD8FB70FFA6B59AE363CD9028EAB4391F0254E0DAD333A837490C`.
- Size: 244,728 bytes.
- Page count: 32.

The DOCX was rendered through LibreOffice using the canonical document QA workflow. All 32 pages were reviewed through four eight-page contact sheets. Pages 1, 24, 25 and 29-32 were additionally inspected at page resolution because they contain the title/abstract, availability/declaration transition, reference/legend transition and revised legends.

Render conclusions:

- No blank page, clipping, overlap, missing text or isolated `X` artifact.
- Data Availability appears on page 24 and contains the current Zenodo DOI.
- References begin on page 25.
- Figure legends begin on page 29.
- The revised Figure 5e boundary appears intact on page 32.
- Page 32 has substantial white space because the double-spaced final legend ends there; this is an acceptable manuscript-format close and was not compressed cosmetically.
- Accessibility audit: `0 high / 0 medium / 0 low` findings.

## 10. Verification completed

- Exact package hash recheck: pass.
- Figure 5e frozen-source hash and row assertions: pass.
- Figure 2-4 Source Data identity and 29 rebuild assertions: pass.
- Candidate panel decision matrix: pass.
- Narrow manuscript-diff reconstruction: pass.
- Candidate DOCX structural checks: pass.
- Candidate PDF page/text checks: pass.
- Visual contact-sheet and high-risk-page checks: pass.
- Full local regression suite: `116/116` tests passed.
- Scientific estimates changed: no.
- New inference added: no.
- Exact submission package modified: no.

## 11. Scientific assessment after this round

The five main figures now form a coherent evidence sequence:

1. Figure 1 defines the permissible identity scaffold and its uncertainty boundary.
2. Figure 2 tests sample-level composition and supports the primary null.
3. Figure 3 identifies robust discovery-cohort IFN/ISG remodeling with specificity controls.
4. Figure 4 tests external reproducibility while exposing genome-wide and source-label boundaries.
5. Figure 5 decomposes convergent regulator, response-set and perturbational evidence without crossing into causal attribution.

The Figure 5e replacement is a genuine information-density gain because it exposes the existing 24 effects rather than adding a new analysis. It also improves honesty: readers can see heterogeneity across genes and donors while the figure and legend explicitly prevent gene-level pseudoreplication or mechanistic overclaiming.

No additional cohort, regulator family, mapper or broad biological rerun is justified by the main-figure audit. Further main-figure changes should now require discovery of a concrete semantic defect, not a preference for a different visual style.

## 12. Next-stage objective

The next stage should be `SUPPLEMENTARY_FIGURE_INFORMATION_DENSITY_AND_MAIN_TEXT_CLAIM_OWNERSHIP_AUDIT`, not submission execution.

Priority work:

1. Audit Supplementary Figures S1-S10 panel by panel against their frozen Source Data, with first priority on S8-S10 because they carry overlap-depletion, end-to-end identity and reference-calibration failure boundaries.
2. For every supplementary panel, decide retain, modify or replace using the same rule applied here: replot only when the new display materially improves evidential ownership or exposes hidden data.
3. Build a Result-claim-to-figure/source-data map. Confirm that every numerical or boundary claim has one clear evidence owner and remove only true textual duplication.
4. Apply a narrow QiTeng sentence-level coherence pass to Title, Abstract, Results and Discussion after the supplementary audit. The purpose is to align claim order and interpretation with the final figure architecture, not to reopen the scientific model.
5. Render the combined manuscript and supplementary candidate after those changes and repeat page-level visual QA.

The main five-figure candidate should remain frozen during that audit. The author-confirmed exact package should continue to remain untouched until the authors explicitly approve a later scientific-candidate refreeze.
