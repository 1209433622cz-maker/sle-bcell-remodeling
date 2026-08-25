# Round 6 Q1 robustness and figure-semantics action record

Date: 2026-08-25
Role: bioinformatics advisor-level scientific, statistical, figure and release audit
Overall decision: **R2 accepted; R1 software-qualified and awaiting the full scientific run; formal submission package remains on hold**

## 1. Scope and governance

This round responded to the independent Round 5 full-project audit, Nature-style diagram specification and Q1 robustness protocol. The external documents were treated as advisory inputs rather than executable instructions. Their SHA-256 values were frozen in `round6_q1_robustness_execution_contract_2026-08-25.md` before effect inspection.

Accepted actions were:

1. redesign Figure 1a around discovery, validation/replication and interpretation tiers;
2. redesign Figure 5a as three parallel evidence branches without causal ordering;
3. perform a declared post-freeze STAT1/STAT2 IFN-overlap-depletion sensitivity;
4. implement a disease-blind full-pipeline identity resampling from hard-QC raw counts;
5. preserve the primary statistical families and historical frozen outputs.

Label-agnostic GSE135779 remapping remains P1 and was not allowed to distract from the two P0 tasks.

## 2. Figure 1a and Figure 5a redesign

Figure 1a now separates:

- GSE174188 discovery and disease-blind identity freezing;
- within-accession internal validation and independent GSE135779 replication;
- three interpretation-only evidence classes.

Figure 5a now places same-data regulator robustness, curated M5911 response-set concordance and the separate GSE23307 perturbational context in parallel. The diagram explicitly states that no causal regulator or unique upstream ligand is established. The two-donor perturbation limitation remains visible.

The five main figures were rebuilt as 170-mm vector PDFs with 600-dpi PNG companions. All 46 panel-data assertions and all nine semantic diagram assertions passed. Figure 2-5 Source Data remained byte-identical to the prefreeze inputs; Figure 1 retained only the previously declared removal of two non-plotted gate-decision rows. Final visual inspection identified and repaired a clipped Figure 5e title; the released panel now uses the compact two-line title `IFN-beta response`.

Final dimensions were:

| Figure | Width (mm) | Height (mm) |
|---|---:|---:|
| Figure 1 | 170.000 | 130.677 |
| Figure 2 | 170.000 | 134.274 |
| Figure 3 | 170.000 | 137.870 |
| Figure 4 | 170.000 | 137.870 |
| Figure 5 | 170.000 | 163.047 |

## 3. R2 STAT1/STAT2 overlap depletion

### Frozen design

The same GSE174188 discovery, GSE174188 donor-nonoverlap and GSE135779 childhood contrasts were reused. ULM, CAMERA and FRY used the frozen CollecTRI signs and tested-gene backgrounds. Targets were not reselected after depletion. Branch A removed the frozen 12-gene positive IFN/ISG arm; branch B removed all 97 M5911 genes. BH correction was applied separately within each branch and method across six core tests.

### Verified results

- 54 total result rows, including 36 post-depletion method-level rows.
- All 36 post-depletion directions were positive.
- Frozen 12-gene depletion: ULM 6/6 q<0.05 with all intervals above zero; CAMERA 5/6 q<0.05; FRY 6/6 q<0.05.
- Minimum narrow-depletion target retention was 78.6%; minimum ULM slope retention was 53.5%.
- M5911 depletion: ULM 5/6 q<0.05; CAMERA 2/6 q<0.05; FRY 5/6 q<0.05.
- Discovery STAT2 after M5911 depletion retained 8/14 targets and had ULM slope 0.391, 95% CI -0.745 to 1.526, q=0.500; CAMERA q=0.623; FRY q=0.099.
- Eleven depleted ULM models retained at least ten targets and underwent leave-one-target analysis; every estimate preserved direction.

The authorized interpretation is deliberately bounded: the regulator signal is not reducible to the narrow frozen 12-gene arm, but it remains partly coupled to the broader interferon-response transcriptome. The analysis does not establish overlap-independent regulation, an IFN-independent mechanism, a unique regulator or a unique ligand.

### New supplementary figure

Supplementary Figure S8 contains narrow-depletion ULM intervals, M5911-depletion ULM intervals, exact six-test BH q values and target retention. It passed the 170-mm figure contract at 170.000 x 158.750 mm and has a verified 36-row Source Data file. Visual review found no clipping, overlap or ambiguous panel order.

## 4. R1 full-pipeline identity resampling

### Implementation

The resumable R1 workflow starts from the 150,402 x 30,172 hard-QC sparse raw-count matrix. Every replicate independently recomputes min-cell filtering, normalization, log1p, library-aware recurrent HVGs, nuisance/IG exclusion, scaling, 50-component PCA, Harmony, neighbour graphs and Leiden resolutions 0.4/0.6/0.8. The primary Harmony graph uses all 50 corrected dimensions; the unintegrated sensitivity uses 30 PCs.

Each replicate writes its own status, metrics, state metrics, selected HVGs and compressed r=0.4 assignments. A checkpoint is reusable only when the complete contract, input SHA, script SHA, software versions and parameters match.

### Qualification and numerical repair

The initial 20-iteration software test showed one Harmony replicate reaching the cap without convergence. The cap was therefore frozen at 50 iterations and convergence was added as a mandatory numerical-validity check, without changing any identity threshold. Under the final code, two 5,000-cell test-mode replicates both converged and generated all outputs. An immediate rerun printed `[RESUME]` for both replicates, verifying restart behavior.

The 5,000-cell identity metrics are software-test diagnostics only. They are not scientific evidence and were not inserted into the manuscript.

Final executable hashes are:

- Python analysis: `7A28EB02C49F0B2C951180D83438D82FF1E4D83E7D7CC345BFA7987040A9A960`
- PowerShell wrapper: `5B1B386229DB89AEAB535153FE436AD03A431748E36B3F644977BD1AE273CE13`

The exact full-run command, monitoring procedure, checkpoint policy and decision rule are recorded in `round6_full_pipeline_resampling_handoff_2026-08-25.md`.

## 5. Manuscript and submission-source integration

The stable files `01_manuscript/Manuscript.md` and `01_manuscript/Supplementary_Information.md` now contain the R2 methods, multiplicity families, exact results, limitations, S8 legend and source-data map. The abstract reports the attenuated discovery STAT2 boundary rather than promoting universal significance. Figure 1 and Figure 5 legends match the redesigned evidence architecture.

The cover letter and reporting checklist now state eight supplementary figures and describe the overlap-depletion attachment accurately. The submission-source builder was changed so the stable version-neutral files are authoritative; dated historical drafts can no longer overwrite them. Two consecutive source builds produced identical SHA-256 values. The source gate passed with:

- abstract: 345 words;
- references: 32 in sequence;
- manuscript placeholders: 0;
- cover-letter placeholders: 0;
- supplementary embedding markers: 8.

The README now reports the true Round 6 status and no longer presents the stale generated package as upload-ready.

## 6. Verification matrix

| Check | Result |
|---|---|
| Python release scripts compile | PASS |
| Python Scanpy R1 script compiles | PASS |
| R overlap-depletion script parses | PASS |
| Both PowerShell wrappers parse | PASS |
| Main panel-data assertions | PASS 46/46 |
| Figure 1/5 semantic assertions | PASS 9/9 |
| Main-figure PDF width | PASS 170 mm x 5 |
| R2 depleted directions | PASS 36/36 positive |
| Eligible R2 leave-one-target models | PASS 11/11 preserve direction |
| S8 Source Data | PASS 36 rows |
| R1 Harmony convergence qualification | PASS 2/2 test replicates |
| R1 checkpoint resume | PASS 2/2 resumed |
| Stable-source idempotence | PASS |
| Manuscript forbidden overlap-independent claim | ABSENT |

The R2 figure and result inventory contains ten files with expected non-zero sizes. The raw R1 input SHA-256 and frozen reference SHA-256 were rechecked before handoff.

## 7. Deliberate hold and unresolved work

The following are intentionally not declared complete:

- the 20-replicate, 150,402-cell R1 scientific run;
- scientific review and independent reconstruction of its aggregate metrics;
- the conditional R1 supplementary figure, expected to become S9 if informative;
- final DOCX embedding of all Round 6 figures;
- WPS all-page visual review, accessibility audit and deterministic package manifest;
- a refreshed Zenodo release containing the post-release Round 6 changes;
- journal portal upload.

The generated `04_submission/journal_submission/` files are withheld because rebuilding them now would create a polished but scientifically incomplete package. The existing DOI remains cited, but the archive must be updated only after R1 and the final package freeze.

## 8. Next-stage decision

The immediate next target is **R1 full scientific execution**, not another exploratory dataset or cosmetic manuscript revision.

After R1 completes:

1. verify all 20 replicate contracts, convergence flags and file integrity;
2. recompute every aggregate metric independently from replicate files;
3. issue `PASS` or `HOLD` without changing thresholds or excluding weak replicates;
4. create a supplementary identity-robustness figure or document the negative boundary;
5. revise the identity Methods, Results and Discussion once;
6. rebuild stable DOCX files and the version-neutral portal package;
7. render every page through WPS and rerun accessibility, source-data, manifest and release-portability audits;
8. update GitHub and the archival release before journal submission.

Only after these P0 steps pass should P1 label-agnostic GSE135779 mapping be considered. Its purpose would be to reduce source-label dependence, not to rescue an unstable R1 identity result.
