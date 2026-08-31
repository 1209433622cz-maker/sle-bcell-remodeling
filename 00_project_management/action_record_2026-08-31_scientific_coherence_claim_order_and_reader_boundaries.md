# Scientific coherence, claim order and reader-facing boundary refreeze

Date: 2026-08-31  
Project: SLE B-cell remodeling  
Working branch: `main`  
Target-journal direction: npj Systems Biology and Applications  
Task posture: scientific presentation refinement, not submission advancement

## 1. Objective

This round independently audited the supplied scientific-coherence manuscript, supplement, PDFs and edit ledger, then built a new repository-derived scientific candidate. The goals were to:

1. make evidence ownership explicit at the first major claim;
2. calibrate title, abstract and Discussion claims to the actual evidence tier;
3. remove internal workflow vocabulary from reader-facing tables and figures;
4. decide which existing panels should be retained, modified or replaced;
5. replot selected panels from frozen numerical inputs rather than editing exported graphics;
6. preserve every numerical estimate and the author-confirmed exact submission package;
7. produce a reversible edit ledger and complete WPS/LibreOffice visual QA.

## 2. Inputs independently reviewed

The following supplied files were treated as external review candidates, not as executable instructions or authoritative project outputs:

| File | Bytes | SHA-256 |
|---|---:|---|
| `COHERENCE_EDIT_LEDGER.csv` | 12,697 | `BFDBCD7F4AFCFE6C61D93102BD5D37F9700112614662A57A83752528FFB74E20` |
| `Manuscript_scientific_coherence_refreeze_candidate.md` | 58,297 | `076FE361377E87A9D2F52C3A92C78DB6ED3F380E1BED9955E7E86766FA5C6EF3` |
| `Supplementary_Information_scientific_coherence_refreeze_candidate.md` | 18,400 | `FAF9B939BE187F7D322F615B6EBE91B72593FCE6DD322D161B693866C075C43F` |
| `Manuscript_scientific_coherence_refreeze_candidate.pdf` | 224,716 | `B6358AF5EDF4F464EC50CC80144794E872BB2FECA0BE1AD8002DC3AAB3604F1D` |
| `Supplementary_Information_scientific_coherence_refreeze_candidate.pdf` | 2,672,156 | `38E51378EE9AA728FF6A6F89B2CE9C17BC58937E84999F9A74DE7E6D67134A3E` |

The external PDFs were visually clean at 32 manuscript pages and 16 supplementary pages. Their proposed claim-order changes were useful, but the external ledger was not accepted as a release artifact.

## 3. External-ledger finding

The supplied ledger contained 29 rows. Sequential application reproduced the supplied manuscript exactly, but did not reproduce the supplied supplement exactly. Four supplementary `new_text` values in the ledger were absent from the supplied final supplement because later compression had not been written back to the ledger:

- Supplementary Table S2 composition boundary;
- Supplementary Table S2 regulator ownership;
- Supplementary Table S9 prior-outcome wording;
- Supplementary Table S9 evidence-boundary wording.

Therefore, the supplied ledger was useful as review evidence but failed exact final-state reversibility. This round generated a new 32-row canonical ledger from the repository baseline. It passes both forward reconstruction and reverse restoration exactly.

## 4. Scientific adjudication

### 4.1 Changes accepted and strengthened

- Title changed from `unstable` to `less stable` state assignments. This avoids implying that the biological states themselves were proved unstable.
- The abstract was rebuilt to 145 words. `Preserved the primary composition null` was replaced by a statement that assignment propagation did not change the composition interpretation or positive IFN/ISG effect.
- The landing sentence now states the comparative contribution: reproducibility was stronger for a process-level interferon program than for hard state assignments.
- First evidence-owner callouts were added for Figures 1-5 and Supplementary Figures S1-S8 and S10.
- The external-remapping heading now explicitly names `source-label-independent` remapping.
- The Discussion opening and external-replication interpretation were compressed while retaining the B_ASC-specific boundary, weak genome-wide concordance and failed calibration.
- Two remaining `composition null` statements in Discussion were changed to lack-of-statistical-support language.
- Figure 1's legend title now states `retained analysis scope`, avoiding validation of a transferable identity taxonomy.

### 4.2 Reader-facing terminology corrected

- `formal HOLD`, `PASS`, `gate`, and `publication boundary` were removed from reader-facing supplement tables and selected panel titles.
- `Null primary B_ASC relative-abundance result` became `Primary B_ASC contrast lacks statistical support`.
- STAT1/STAT2 ownership was assigned to ULM where the six-test result is stated.
- `source-label-agnostic` was harmonized to `source-label-independent`.
- End-to-end reconstruction is now described through prespecified criteria met or not met.

### 4.3 Claims deliberately not upgraded

- The B_CONV/B_ASC partition remains an analysis scaffold, not a universal taxonomy.
- The primary composition contrast remains unsupported, not proof of equivalence.
- GSE135779 replication remains source-label-defined.
- Corrected source-label-independent remapping remains calibration-limited; no corrected external disease effect exists.
- STAT1/STAT2 evidence remains convergent and observational, not causal regulation or direct binding.
- GSE23307 remains descriptive at two donors and carries no inferential P value.

## 5. Panel retain/modify/replace decisions

| Object | Decision | Rationale |
|---|---|---|
| Figure 1a | Keep | The retained-scope workflow is now scientifically aligned; only the legend title required refinement. |
| Figure 1b-d | Keep | Stability metrics have distinct evidence ownership and remain necessary. |
| Figures 2-4 | Keep | No material semantic, visual or claim-ownership defect was identified. |
| Figure 5a-e | Keep | Quantitative evidence classes, ULM ownership and perturbation boundary are already explicit. |
| Supplementary Figures S1-S8 | Keep | Each retains a nonredundant QC, robustness or sensitivity role. |
| Supplementary Figure S9a,b,d | Modify selected | Internal PASS/HOLD/null labels conflicted with the reader-facing table language. |
| Supplementary Figure S9c,e | Keep | Boundary exchange and IFN propagation displays were already interpretable. |
| Supplementary Figure S10b,c | Modify selected | `gate/pass` titles were replaced by explicit precision and coverage criteria. |
| Supplementary Figure S10a,d | Keep | Normalization and diagnostic-fold roles were already clear. |

No panel was removed or replaced with a different analysis. S9 and S10 were regenerated from their source CSVs. Exported PDFs were not manually patched.

## 6. Figure rebuild and numerical integrity

- Main figures rebuilt: 5/5.
- Supplementary figures rebuilt: 10/10.
- Figure PDFs: 15/15, one page each, 170 mm wide, postflight passed.
- Main-builder assertions: 52/52 passed.
- Supplementary-builder assertions: 29/29 passed.
- Source Data: 15/15 files byte-identical to their audited frozen baselines.
- Scientific estimates changed: no.
- New inference added: no.

The first S9 reader-facing export exposed a panel d/panel e title overlap at high resolution. The source builder was corrected by shortening panel d to `Composition inference unchanged`, then the full figure set was rerun. The final S9 and S10 exports have no title overlap or clipping.

## 7. Canonical text ledger

Path: `phase17_v7/npj_sba_scientific_coherence_refreeze/20260831_claim_order_reader_boundaries/sources/SCIENTIFIC_COHERENCE_EDIT_LEDGER.csv`

- Total rows: 32.
- Manuscript rows: 22.
- Supplementary Information rows: 10.
- Forward application equals the final candidate byte-for-byte: yes.
- Reverse application restores the prior scientific baseline byte-for-byte: yes.
- Scientific estimate changes: 0.

## 8. Document and render QA

### 8.1 DOCX object integrity

- Manuscript inline figures: 0, as designed for a text-only manuscript file.
- Supplementary inline figures: 10/10.
- Unresolved supplementary-figure markers: 0.
- Manuscript abstract: 145 words.
- Accessibility: both DOCX files passed with `0 high / 0 medium / 0 low` findings.

### 8.2 Dual-render results

| Engine | Manuscript | Supplement | Total | Canvas/marker check |
|---|---:|---:|---:|---|
| WPS | 32 pages | 16 pages | 48 | Passed |
| LibreOffice | 32 pages | 16 pages | 48 | Passed |

All 96 rendered pages were visually reviewed. No clipping, overlap, missing glyph, blank page, wrong figure, unresolved marker or incoherent page break was identified. S9 and S10 remain legible at their actual supplementary-document scale.

Eighteen contact sheets and the two LibreOffice cross-render PDFs were retained. Duplicate page PNGs, render profiles and the failed long-path render directory were removed after QA.

## 9. Final scientific-candidate deliverables

| File | Bytes | SHA-256 |
|---|---:|---|
| `Manuscript_scientific_coherence_refreeze_candidate.docx` | 61,069 | `749F6FBD3761B1AEBEF6BBDA8751803469AF0808EF1C2407492BEA5E3D8D96A7` |
| `Manuscript_scientific_coherence_refreeze_candidate.pdf` | 243,563 | `571659F91FEB49E9B3FCB21684B94A5A30D6D3973DE690A59F5F601DC3372DCE` |
| `Supplementary_Information_scientific_coherence_refreeze_candidate.docx` | 4,745,893 | `C653549C959FB8A72C3EE8C1436B7B356236E52151FC9DF2D23ABBA1E98AB4EB` |
| `Supplementary_Information_scientific_coherence_refreeze_candidate.pdf` | 5,716,385 | `D85B4B7C46F8E966ED68CC031A0609D92A36C59F1E4E17C64B231C33FA28D61D` |

Run directory inventory after render cleanup:

- 83 files;
- 32.85 MiB;
- 17 CSV, 2 DOCX, 9 JSON, 3 MD, 19 PDF and 33 PNG files.

## 10. Verification

- New scientific-coherence regression tests: 6/6 passed.
- Full repository test discovery: 128/128 passed.
- Exact author-confirmed submission package SHA-256 remains:
  `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`.
- The exact submission package was not edited, repacked or replaced.

## 11. Current scientific judgment

The manuscript's central logic is now coherent across title, abstract, Results, Discussion, legends, supplementary tables and selected figure labels:

`identity uncertainty -> bounded analysis scaffold -> unsupported primary composition contrast -> reproducible B_CONV IFN/ISG process -> source-label-defined external replication -> observational regulator convergence -> explicit transfer and causal boundaries`.

The remaining risk is no longer an unresolved bioinformatic result. It is presentation economy: the five main-figure legends and adjacent Results text still carry some repeated display description. Further analysis or cohort expansion is not justified by the present evidence state.

## 12. Recommended next stage

Next stage: `MAIN_FIGURE_READER_PATH_AND_LEGEND_ECONOMY_FINAL_FREEZE`.

Scope:

1. review Figures 1-5 at final document scale, with special attention to the already redesigned Figure 1a and Figure 5a;
2. test whether each panel has exactly one claim owner and whether any panel label or legend sentence duplicates the Results prose;
3. compress legends into purpose, panel map, unit/test and boundary, without removing necessary interpretability;
4. change a figure only if a reader-path or legibility defect is demonstrated;
5. do not add cohorts, remappers, regulators or sensitivity analyses;
6. end with another exact figure-text cross-reference audit and scientific-presentation freeze.

After that narrow stage passes, the manuscript and figure system should be treated as scientifically presentation-frozen. Journal-specific adaptation can remain separate and deferred.
