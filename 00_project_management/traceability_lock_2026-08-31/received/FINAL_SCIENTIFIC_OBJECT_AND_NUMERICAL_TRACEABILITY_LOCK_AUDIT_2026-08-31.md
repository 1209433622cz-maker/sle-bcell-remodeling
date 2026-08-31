# FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCK — independent audit

Date: 2026-08-31  
Repository: `1209433622cz-maker/sle-bcell-remodeling`  
Audited commit: `154e342e03af870cff44ccdbffc61b5a42e41740`  
Scientific-presentation run: `phase17_v7/npj_sba_scientific_presentation_freeze/20260831_reader_path_and_legend_economy`  
Posture: scientific content/object traceability only; no submission-package, Release or Zenodo mutation.

## Executive judgment

Current status:

`TRACEABILITY_LOCK_PENDING_2_SOURCE_TEXT_FIXES__NO_NUMERICAL_RERUN_REQUIRED`

The core numerical evidence chain is internally coherent. The audit traced the main identity, composition, B_CONV IFN/ISG, external-replication, calibration-boundary, regulator, depletion, M5911 and GSE23307 claims to repository Source Data objects. No contradictory effect estimate, confidence interval, P/q value, threshold, cohort count, donor count or direction was found in the audited core claims.

Two reader-facing object-level inconsistencies remain:

1. Supplementary Table S7 uses the umbrella biological-unit label `Donor/sample pseudobulk` for both gene-level expression and four-program inference. This is not sufficiently traceable because the main Methods explicitly define GSE174188 pseudobulks at the sample-cohort stratum, whereas GSE135779 inference is donor-level. The fix is wording-only and should be applied at source level, followed by Supplementary rebuild.
2. Supplementary Table S6 states that the Zenodo version-specific archive `matches the frozen manuscript, figures and statistical outputs`. The current scientific-presentation round changed Figure 1a, Figure 5a and manuscript presentation while explicitly leaving Release/Zenodo unchanged. Because all 15 Source Data files and statistical estimates remained unchanged, the correct claim is that Zenodo archives the released analysis code, Source Data and statistical outputs—not that it is byte/object-identical to the current manuscript and figure presentation.

Neither issue requires re-running a biological or statistical analysis.

## Main-figure adjudication after traceability audit

All 21 main panels remain scientifically frozen. There is no new evidence-based reason to remove, replace or redraw Figure 1b-d, Figures 2-4, or Figure 5b-e. The source-level redraws already made to Figure 1a and Figure 5a correctly align the inferential-unit and evidence-role semantics. The present traceability audit found no numerical defect that would justify reopening them.

Supplementary Figures S1-S10 likewise remain retained. S7/S8/S9/S10 are especially important because they own correlation-aware sensitivity, overlap-depletion, end-to-end identity propagation and corrected mapping-calibration boundaries, respectively. Their numerical contents agree with the corresponding Results and Supplementary tables.

## Core numerical traceability findings

The attached CSV contains 24 traceability objects. Of these:

- 20 are direct or rounded matches to explicit Source Data rows/fields;
- 2 are derived but reproducible directly from Source Data fields (median boundary exchanges; cross-dataset correlation/subset logic);
- 2 require source-text correction only (Supplementary Tables S6 and S7);
- 0 require statistical re-analysis;
- 0 require a new cohort, mapper, regulator, gene set or sensitivity branch;
- 0 require a main-figure replacement.

Key examples include:

- Figure 2 primary composition: source OR `0.9466531607`, CI `0.6357046975-1.4096988903`, P `0.7872791209`, 43/47 strata, faithfully reported as 0.947, 0.636-1.410, P=0.787.
- Figure 3 primary IFN/ISG: source effect `0.8365564764`, CI `0.5254302647-1.1476826882`, q `2.97700418e-6`, faithfully reported as 0.837, 0.525-1.148, q=2.98e-6.
- Figure 4 childhood replication: source effect `1.0417569525`, CI `0.6811655903-1.4023483146`, q `2.97551135e-6`, 11 HC/32 SLE donors, faithfully reported.
- S10 elastic-net calibration: coverage `0.94195804196`, B_CONV precision `0.99644950871`, B_ASC precision `0.88520971302`; the manuscript's 94.20%, 99.64% and 88.52% are correct rounding.
- S7 discovery STAT2: CAMERA correlation `0.1225027275`, CAMERA q `0.1354722163`, FRY q `4.90918365e-5`, exactly supporting the stated CAMERA exception.
- S8 M5911-depleted discovery STAT2: 8/14 targets, ULM `0.3906577146`, CI `-0.7450461772 to 1.5263616063`, q `0.5001111487`, CAMERA q `0.6228677150`, FRY q `0.0994655688`, faithfully reported.
- Figure 5 GSE23307: donor means `3.2935705121` and `3.6656689054`; all 24 gene-level effects are positive; no inferential P value is stored.

## Claim ownership lock

The evidence hierarchy remains clean:

`identity scaffold -> Figure 1`
`primary composition -> Figure 2`
`GSE174188 B_CONV IFN/ISG -> Figure 3`
`independent source-label-defined replication -> Figure 4`
`ULM / M5911 / GSE23307 convergence -> Figure 5`
`correlation-aware regulator sensitivity -> Supplementary Figure S7`
`IFN-overlap depletion -> Supplementary Figure S8`
`identity reconstruction/propagation boundary -> Supplementary Figure S9`
`source-label-independent calibration boundary -> Supplementary Figure S10`

No central positive biological claim is owned only by a sensitivity-only panel. The two negative/boundary claims in S9 and S10 are appropriately owned by the analyses that define those boundaries.

## Exact source-level patch

`TRACEABILITY_LOCK_SOURCE_PATCH_2026-08-31.diff` contains only three line replacements in the Supplementary source:

- one provenance wording correction in Table S6;
- two dataset-specific biological-unit corrections in Table S7.

No numerical cell, figure Source Data file, threshold, estimate, CI, P/q value, cohort definition or figure panel is changed.

## Recommended integration rule

Apply the patch to the canonical Supplementary Markdown source, regenerate the Supplementary DOCX/PDF through the existing builder, and rerun the existing scientific-presentation regression suite plus dual-render QA. Do not hand-edit the existing DOCX or PDF.

If the regenerated Supplementary document passes and all Source Data hashes remain unchanged, the project can be classified:

`FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCKED`

At that point scientific editing should stop unless a new objective factual or numerical defect is demonstrated.

## Next-stage target

The next stage should therefore be extremely narrow:

`TRACEABILITY_TEXT_FIX_REBUILD_AND_FINAL_LOCK`

Scope:
1. integrate only the S6/S7 source-text patch;
2. rebuild Supplementary Information from source;
3. verify all 15 Source Data hashes remain byte-identical;
4. rerun the regression suite and WPS/LibreOffice visual QA;
5. emit the final zero-defect traceability matrix and freeze scientific objects.

No new biological analysis, cohort expansion, mapper, TF analysis, sensitivity analysis, Release update, Zenodo update or submission-package work is justified by this audit.
