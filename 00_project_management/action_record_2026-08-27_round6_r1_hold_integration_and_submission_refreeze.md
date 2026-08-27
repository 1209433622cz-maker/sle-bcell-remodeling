# Round 6 R1 HOLD integration and submission refreeze action record

Date: 2026-08-27

Role: bioinformatics advisor-level scientific, statistical, figure, manuscript and release audit

Overall decision: **ACCEPT THE FORMAL R1 HOLD, RETAIN THE FROZEN DISEASE RESULTS, NARROW THE TAXONOMY CLAIM, AND ACCEPT THE REBUILT PACKAGE FOR FINAL PRE-SUBMISSION REVIEW**

## 1. Scope and starting state

This round resumed after completion of the full 150,402-cell, 20-replicate R1 end-to-end identity reconstruction. The work had five linked objectives:

1. independently verify every R1 checkpoint, aggregate and formal criterion;
2. determine which broad state caused the formal HOLD;
3. propagate observed B_CONV/B_ASC boundary uncertainty into the frozen composition and IFN/ISG analyses;
4. integrate the result into Figure 1, a new Supplementary Figure S9, the manuscript, supplementary information and submission attachments;
5. rebuild and visually audit the complete WPS submission package.

The primary statistical families, samples, genes, contrasts, thresholds and identity criteria were not changed. No weak replicate was excluded, no seed was rerun to obtain a more favourable result, and no exploratory result was promoted.

## 2. Full R1 inventory and integrity audit

The full run is located at:

`phase17_v7/round6_q1_robustness/20260825_full_pipeline_identity_resampling/`

Inventory:

- 106 files;
- 71,649,288 bytes;
- 20 complete replicate directories;
- 20 compressed per-cell assignment files;
- 20/20 replicate status files;
- 20/20 metric tables;
- 20/20 state-metric tables;
- 20/20 selected-HVG tables;
- aggregate run contract, branch metrics, state metrics, summaries and final status.

All 20 replicates completed and all 20 Harmony runs converged. Aggregate branch metrics, state metrics and the final decision were independently reconstructed from replicate-level outputs. The following integrity hashes were retained:

- raw input SHA-256: `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5`;
- frozen reference SHA-256: `594A040FC483973B38B744D5D0E526633D7F1C91F2544D34C28D35F2084E3AFB`;
- R1 analysis script SHA-256: `7A28EB02C49F0B2C951180D83438D82FF1E4D83E7D7CC345BFA7987040A9A960`.

The independently verified primary Harmony resolution-0.4 metrics were:

| Criterion | Observed | Threshold | Decision |
|---|---:|---:|---|
| Median mapped ARI | 0.962972 | 0.950 | PASS |
| Minimum mapped ARI | 0.929697 | 0.900 | PASS |
| Median mapping agreement | 0.999368 | 0.995 | PASS |
| Minimum mapping agreement | 0.998770 | 0.990 | PASS |
| Minimum state-median Jaccard | 0.930323 | 0.950 | HOLD |

Additional global metrics were median AMI 0.916518 and minimum AMI 0.863081. The unchanged formal decision is:

`HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`

## 3. Localization of the formal HOLD

The state-specific audit showed that the HOLD is not a general collapse of the broad partition. It is localized to B_ASC membership:

| State | Median Jaccard | Minimum Jaccard | Median recall |
|---|---:|---:|---:|
| B_ASC | 0.930323 | 0.871750 | 0.972220 |
| B_CONV | 0.999363 | 0.998760 | 0.999598 |

Across replicates, the median number of broad-state changes was 76 among 120,320 sampled cells, with a range of 59-148. The typical B_ASC reference count was approximately 1,043 cells; the median replicate contained 29 B_ASC-to-B_CONV and 48 B_CONV-to-B_ASC exchanges.

The correct interpretation is therefore:

> End-to-end reconstruction retained high global two-compartment concordance but missed the prespecified B_ASC state-overlap criterion. B_CONV/B_ASC is used as a disease-blind analysis scaffold rather than a universally reproducible taxonomy.

## 4. Boundary-uncertainty propagation

The integration run is located at:

`phase17_v7/round6_q1_robustness/20260827_r1_hold_integration/`

It contains 57 files and 96,162,799 bytes. Forty local sparse matrix exports account for 95,453,354 bytes and remain Git-ignored. Reviewer-facing aggregate, integrity, model and source-data outputs are retained in the repository and submission attachments.

For each replicate, only sampled cells observed to cross the B_CONV/B_ASC boundary were changed in the complete frozen partition. Unsampled cells retained their frozen assignment. Sample eligibility, covariates, model matrices, genes, programs and thresholds were not reselected.

### Composition propagation

The frozen beta-binomial implementation and sample eligibility were reused. Baseline odds ratios were reproduced within the prespecified numerical tolerance of 0.0005; the largest absolute discrepancy was 0.000136.

Primary results across 20 boundary-exchange replicates:

- odds-ratio range: 0.896040-0.966758;
- median odds ratio: 0.925555;
- all 20 models converged;
- all Hessians were positive;
- all 20 95% confidence intervals included one.

The primary B_ASC null boundary is retained. Validation and donor-nonoverlap intervals also included one. The secondary flare estimates remained positive with intervals excluding one, but the pre-existing frozen multiplicity boundary was not changed and the flare result was not promoted.

### IFN/ISG propagation

Boundary-cell raw counts were added to or subtracted from frozen B_CONV pseudobulks. The workflow then reran edgeR TMM logCPM, the frozen 12-gene IFN/ISG score and OLS with HC3 uncertainty.

| Analysis | Frozen effect | Sensitivity range | Minimum attenuation | Interval result |
|---|---:|---:|---:|---|
| GSE174188 primary | 0.8366 | 0.8361-0.8446 | 0.9995 | 20/20 above zero |
| GSE174188 donor-nonoverlap | 1.0862 | 1.0593-1.0867 | 0.9752 | 20/20 above zero |

All 40 propagated effects were positive and all 40 confidence intervals remained above zero. This is a same-data assignment-sensitivity analysis, not new replication.

## 5. Executable additions and runtime handling

New executable files:

- `audit_tools/phase17_round6_04_audit_r1_hold_and_prepare_propagation.py`;
- `audit_tools/phase17_round6_05_fit_identity_uncertainty_composition.py`;
- `audit_tools/phase17_round6_05_fit_identity_uncertainty_ifn.R`;
- `audit_tools/phase17_round6_06_build_identity_hold_figure.py`;
- `audit_tools/run_6013RP_round6_r1_hold_integration.ps1`.

The full integration entry point is:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_round6_r1_hold_integration.ps1
```

Two runtime problems were detected and repaired transparently:

1. `source_cell_index` is a stable non-contiguous source index, not a raw matrix row position. The audit now constructs an explicit index-to-row map before extracting boundary-cell counts.
2. SciPy L-BFGS-B in the Scanpy analysis environment terminated with Windows native exit `0xC06D007F`. The beta-binomial step was isolated to the qualified legacy numerical Python, while the Scanpy audit and R/edgeR IFN analysis retained their appropriate environments. Baseline reproduction checks guard this separation.

## 6. Supplementary Figure S9

Supplementary Figure S9 was built from 128 machine-readable source rows at exactly 170 x 160 mm. Its five panels report:

- formal four-PASS/one-HOLD criteria;
- state-specific B_ASC and B_CONV Jaccard values;
- broad-state boundary exchanges;
- propagated primary B_ASC composition odds ratios and intervals;
- propagated primary and donor-nonoverlap B_CONV IFN/ISG effects.

All eight S9 data assertions passed. Visual review detected and repaired left-label clipping, excessive inter-row whitespace and PASS-label overlap. The final figure contains no clipped text, incoherent overlap or ambiguous threshold semantics.

Final S9 PDF:

- bytes: 52,943;
- SHA-256: `4D04E51A9282E2BBB39DCBE7745D6978A46B1BCBD47FBC7C54DDD33964EAE075`.

## 7. Figure 1 and manuscript refreeze

Figure 1 panels b-d are now explicitly labelled as frozen-representation analyses. Figure 1a describes B_CONV/B_ASC as a frozen-representation analysis scaffold. The Figure 1 legend states that HVGs, PCA and Harmony were not recomputed in those panels and directs readers to S9 for the end-to-end sensitivity.

The five main figures were rebuilt. All 46 panel-data assertions passed. Figure 2-5 Source Data remained byte-identical to the previous frozen sources. The final Figure 1 PDF is 58,256 bytes with SHA-256 `2A983EF01120B69DD57CF25DD601489F50991F9F1BED31F9B317D08BB9865C24`.

The manuscript title was narrowed from unstable biological states to unstable state assignments:

**Disease-blind single-cell reconstruction separates unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus**

The abstract, Methods, Results, Discussion, limitations, Conclusions, figure legend and Additional files were revised. The Supplementary Methods, claim-boundary table, numerical anchors, source-data map, reproducibility map, statistical-family map, archive map and S9 legend were updated. The cover letter and reporting checklist now report nine supplementary figures and the formal identity HOLD.

Source contracts:

- abstract: 349 words;
- numbered references: 32 in sequence;
- manuscript placeholders: 0;
- cover-letter placeholders: 0;
- supplementary embedding markers: 9;
- main manuscript SHA-256: `511A4138F054AAAAC9556EB1B55D49299780D2249528245E2FB8438404066FC4`;
- supplementary information SHA-256: `C417326C47614120D3ECEF471AB8B54E7AD5FEE5F3D79FD16BD1E087CB35EDF8`;
- cover letter SHA-256: `CA1A0F0B1B298D41E89CD619F3D5074040A391734E3AA566F0CBAEF35D259F61`.

## 8. Submission attachment integration

The generated package contains:

- five main figures in vector PDF plus 600-dpi PNG;
- nine supplementary figures in vector PDF plus 600-dpi PNG;
- 14 figure source-data CSV files;
- 11 REQUIRED portal files;
- nine OPTIONAL standalone supplementary-figure PDFs;
- a regulator-sensitivity attachment;
- an augmented Full Statistical Results attachment;
- release and reproducibility records.

The Full Statistical Results ZIP preserves the frozen statistical payload and adds 101 reviewer-facing identity-robustness files:

- six aggregate R1 run files;
- 80 replicate status, metric, state and HVG files;
- 14 boundary-propagation and audit files;
- one S9 source-data file.

Per-cell assignment exports and 40 sparse matrix exports are intentionally excluded. The augmented archive contains 164 entries, a 163-row internal manifest and 101 `identity_robustness/` files. Every manifest size and SHA-256 check passed.

## 9. WPS, accessibility and deterministic-package audit

The final documents were rendered through WPS Office, rasterized page by page and reviewed through seven contact sheets. Visual review found no truncated figures, clipped tables, incoherent overlaps or orphaned headings. The cover letter initially rendered with only the signature on page 2; its journal-facing body was adjusted to 10 pt and rerendered as one readable page.

Final WPS results:

| Document | Pages | Page PNGs | Accessibility findings |
|---|---:|---:|---:|
| Manuscript | 32 | 32 | 0 high, 0 medium, 0 low |
| Supplementary information | 17 | 17 | 0 high, 0 medium, 0 low |
| Cover letter | 1 | 1 | 0 high, 0 medium, 0 low |

Other release checks:

- Supplementary Table S7 begins on page 7 with its first data row;
- supplementary DOCX contains nine tables and nine embedded figures;
- legacy supplementary assertions pass 29/29;
- S8 contract passes with 36 source rows;
- S9 contract passes with 128 source rows and 8/8 checks;
- no restricted H5AD, H5, RDS, MTX, BAM or FASTQ payload entered the package;
- deterministic package archive built twice with identical bytes.

Final local submission ZIP:

- path: `04_submission/journal_submission.zip`;
- bytes: 58,515,354;
- SHA-256: `63446D18B55A856B016C377A8EF4E7BBDAC1B713C0E56B27E6F0ACE505EE22BB`.

The complete generated package ZIP and internal WPS assets are Git-ignored. The
11-file REQUIRED portal set, package README, manifest and upload maps are tracked
for reviewer-facing reproducibility. The package has not been uploaded to a journal.

## 10. Claim authorization

Authorized claims:

- fine-grained naive/memory hard assignments are unstable;
- the B_CONV/B_ASC partition is a disease-blind analysis scaffold with high global but incomplete B_ASC end-to-end overlap;
- primary B_ASC relative abundance is null under the frozen analysis and remains null under observed boundary exchanges;
- the B_CONV IFN/ISG program is supported in GSE174188 discovery, donor-nonoverlap internal analysis and independent GSE135779 childhood donors;
- the IFN result remains positive under observed R1 boundary exchanges;
- regulator, overlap-depletion, response-set and perturbational results are convergent but non-causal support.

Prohibited claims:

- universally reproducible B_CONV/B_ASC taxonomy;
- stable hard naive, memory, atypical or IFN-high subtype;
- independent replication by the GSE174188 donor-nonoverlap contrast;
- general B_ASC expansion in SLE;
- overlap-independent STAT1/STAT2 regulation;
- causal TF activity, direct binding or a unique upstream IFN ligand;
- independent replication supplied by the boundary-propagation sensitivity.

## 11. File-governance decision

Historical dated manuscripts and supplementary files retain earlier wording as provenance and were not rewritten. The stable current sources are:

- `01_manuscript/Manuscript.md`;
- `01_manuscript/Supplementary_Information.md`;
- `04_submission/Cover_Letter.md`;
- `README.md`;
- `REPRODUCIBILITY.md`.

Large local outputs remain excluded by `.gitignore`:

- 20 `*.csv.gz` per-cell assignment files;
- 40 `*.mtx.gz` propagation matrix exports;
- generated internal WPS renders, duplicate working assets and
  `04_submission/journal_submission.zip`.

Compact replicate metrics, source data, decision records, figures, scripts and
the 11-file REQUIRED portal set are retained for GitHub synchronization. The
largest tracked attachment is the 10.8 MB Full Statistical Results ZIP and does
not contain raw or per-cell matrices.

## 12. Next-stage decision

The interrupted P0 R1 task is complete. Additional cosmetic revision or repeated identity reruns are not the next priority.

For the stated high-risk upper-Q1 objective, the next scientific target is a **label-agnostic GSE135779 mapping/transfer sensitivity**. Its purpose is to reduce dependence on eight source B-cell labels after the R1 taxonomy boundary, not to rescue the formal HOLD. The analysis must be disease-blind, predeclare transfer features and acceptance criteria, preserve donor-level inference, and retain a transparent HOLD if the broad conventional-B analog does not transfer.

After that single P1 decision, the release sequence is:

1. perform one independent adversarial review of the integrated manuscript and WPS pages;
2. choose the final Q1 target and apply only target-specific formatting;
3. update the public Zenodo payload associated with DOI `10.5281/zenodo.22086892`;
4. verify the archived hashes and GitHub release linkage;
5. complete portal metadata and inspect the journal-generated submission PDF;
6. submit only after both authors reconfirm the final target-specific package.

No additional exploratory dataset, threshold optimization or result-driven cluster relabelling is authorized before this P1 decision.
