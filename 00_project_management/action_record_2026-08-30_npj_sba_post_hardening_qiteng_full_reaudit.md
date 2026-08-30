# npj Systems Biology and Applications post-hardening QiTeng full reaudit

Date: 2026-08-30 (Asia/Hong_Kong)

Repository: `1209433622cz-maker/sle-bcell-remodeling`

Authoritative starting commit: `a960fa81c730cd3f6da5f81ace6a9212bc4ede1f`

Final decision: `PASS_NPJ_SBA_POST_HARDENING_REAUDIT_TEXT_FREEZE`

Next gate: `NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`

## 1. Purpose and scope

This round performed a full post-hardening review of the scientific purpose,
analysis architecture, manuscript logic, statistical language, figures,
submission package and release boundaries for a planned Article submission to
npj Systems Biology and Applications. The review applied the supplied QiTeng
Academic Writing Skill v0.3.21 as a style and reasoning framework, while treating
the repository's frozen machine-readable outputs as the authority for scientific
facts.

The review was deliberately read-only with respect to scientific results. No
cohort, mapper, threshold, seed, gene set, transcription-factor method, model or
figure source was changed. No manuscript DOCX/PDF or public release was rebuilt.

## 2. Authority and received evidence

The evidence hierarchy used in this round was:

1. Frozen repository outputs and tracked source files.
2. Verified target-specific package manifests and machine-readable gates.
3. Current official Nature Portfolio and npj Systems Biology and Applications pages.
4. External audits and user-supplied matrices as review evidence only.
5. QiTeng skill files as writing and quality-control rules, not as scientific data.

The received external files and extracted QiTeng rules were archived under
`00_project_management/npj_sba_post_hardening_reaudit_2026-08-30/received/`.
Their byte sizes and SHA-256 values are recorded in
`received_evidence_manifest.csv`.

The original QiTeng release ZIP was 10,953,826 bytes with SHA-256
`C18AC4F0254286725B7449EA7B7E8DA89E8235B4FABA75B42A6E362D2AD87D99`.

## 3. Executive scientific judgment

The manuscript's strongest and most defensible contribution is not a new hard
B-cell taxonomy. It is a systems-level demonstration that inferential layers
have different reproducibility ceilings: process-level IFN remodeling is more
reproducible than the tested hard B-cell state assignments when identity,
composition and transcription are evaluated separately.

The evidence supports this single organizing claim:

- Disease-blind reconstruction provides a reproducible broad B_CONV/B_ASC
  analysis scaffold, but not a universally stable hard-state taxonomy.
- Primary B_ASC abundance remains null at sample level.
- The B_CONV IFN/ISG program reproduces across discovery, donor-nonoverlap and
  independent childhood data.
- Regulatory analyses support STAT1/STAT2/IRF context as association-level
  evidence, not direct binding, unique upstream control or causality.
- R1 and C9R are informative negative boundaries and remain permanent HOLDs.

The current analysis design is saturated for first submission. Additional
pre-submission reruns would add researcher degrees of freedom without repairing
an identified defect. The correct decision is scientific and textual freeze.

## 4. Scientific evidence-chain audit

### 4.1 Identity and representation

- Discovery contains 150,402 quality-controlled B-lineage cells.
- Disease-blind resampling supports the broad B_CONV/B_ASC scaffold.
- End-to-end reconstruction retains high global mapping agreement.
- The frozen B_ASC state-overlap criterion is not met: median Jaccard 0.930 is
  below the prespecified 0.95 threshold.
- The R1 decision therefore remains
  `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`.
- No threshold relaxation, selective seed choice or mapper substitution is justified.

### 4.2 Composition

- Primary B_ASC relative abundance is null: odds ratio 0.947, 95% CI
  0.636-1.410, P=0.787.
- Count-aware and mandatory sensitivity models do not support a primary
  B_ASC-enrichment claim.
- Boundary-exchange propagation retains the null across all 20 replicates.
- The manuscript correctly avoids converting absence of evidence into evidence
  of equivalence.

### 4.3 Transcription and replication

- The frozen B_CONV IFN/ISG effect is positive in discovery and donor-nonoverlap
  contrasts.
- Independent GSE135779 support is source-label-defined and is described as such.
- Genome-wide cross-dataset concordance is low (Spearman rho=0.026), so the
  valid conclusion is program-specific replication, not a globally shared SLE
  transcriptome.
- Corrected source-label-agnostic transfer remains on C9R HOLD because B_ASC
  precision is 0.885, below the frozen 0.90 criterion.
- Corrected external disease outcomes remain locked.

### 4.4 Regulatory and perturbation context

- Frozen STAT1/STAT2 ULM results are supported by CAMERA and FRY sensitivity
  analyses, with the declared discovery STAT2 CAMERA exception retained.
- All 36 method-level directions remain positive after removal of the frozen
  12-gene IFN/ISG arm or M5911 genes.
- M5911 depletion attenuates discovery STAT2 and therefore does not support an
  overlap-independent regulatory claim.
- GSE23307 IFN-beta evidence is explicitly limited to `n=2; descriptive only`.
- Evidence tier remains E2 for process-level IFN association and E1 for
  STAT1/STAT2 regulatory context. Causal mechanism and clinical utility are not
  established.

## 5. Methods-design judgment

The current methods architecture is appropriate for the stated target and
scientific claim because it separates five inferential layers:

1. Disease-blind identity reconstruction and frozen threshold adjudication.
2. Sample-level count-aware composition modeling.
3. Donor-aware pseudobulk transcriptional inference.
4. Internal nonoverlap and independent source-label-defined replication.
5. Correlation-aware and depletion-based regulatory sensitivity analyses.

This ordering prevents cell-level pseudoreplication, protects outcome labels
during identity definition, separates discovery from replication and propagates
negative identity boundaries into downstream interpretation. The remaining
limitations are properties of available evidence, not missing technical work.

No new cohort, mapper, threshold, TF/regulon method, gene set or sensitivity
analysis should be added before first submission unless an editor or reviewer
identifies a specific defect.

## 6. QiTeng manuscript audit

Mode: `FULL_MANUSCRIPT + QITENG_Q1`

Purpose: `TARGET_JOURNAL_SUBMISSION`

Decision: `PASS_QITENG_Q1_TEXT_FREEZE`

The manuscript satisfies the intended reasoning sequence:

- Introduction: tension, evidence gap, disease-blind response.
- Results: identity ceiling, composition null, IFN replication, transfer HOLD,
  observational regulatory context.
- Discussion: interpretive delta, evidence ownership, alternatives, prospective
  next test and restrained conclusion.
- Methods: source and unit, model, multiplicity, validation class and
  reproducibility boundary.

Machine checks confirmed:

- Exact target title and 15-word title length.
- Abstract length of 140 words.
- Reference first-appearance order 1-32 with no orphan or reordered citation.
- Explicit source-label ownership of GSE135779 replication.
- Explicit R1 and C9R inheritance.
- Explicit causal and clinical ceiling.
- No manuscript source or binary file changed in this round.

QiTeng's late-stage salience rule therefore favors `TEXT FREEZE`; another broad
rewrite would create more consistency risk than scientific gain.

## 7. Repository consistency corrections

Two documentation-only factual corrections were made in `README.md`:

1. Replaced the logically inverted statement that resampling "formally holds"
   despite B_ASC median Jaccard 0.930 being below 0.95. The README now states
   that the frozen state-overlap criterion was not met.
2. Replaced the historical QiTeng R2 title in the target section with the exact
   current npj title:
   `Disease-blind reconstruction distinguishes reproducible interferon remodeling from unstable B-cell state assignments in systemic lupus erythematosus`.

These corrections change neither scientific values nor submission-package bytes.

## 8. Figure and layout audit

All five main and ten supplementary figures were rendered into three contact
sheets and reviewed. Figure 1, Figure 5, Supplementary Figure S8 and
Supplementary Figure S9 received additional full-resolution inspection.

Results:

- 15/15 figures are single-page vector PDFs at 170 mm width.
- No clipping, incoherent overlap, missing labels or broken glyphs were found.
- Main-figure color roles remain consistent across identity, composition,
  transcription, replication and regulatory evidence.
- Figure 5 preserves the distinction among regulator robustness, response-set
  concordance and descriptive perturbation context.
- Supplementary Figure S8 labels depletion scope and retained targets without
  implying causality.
- Supplementary Figure S9 communicates the B_ASC-specific HOLD and retained
  B_CONV effects without hiding the failed criterion.
- Panel lettering, threshold ticks, uncertainty intervals and PASS/HOLD language
  are internally consistent.

The current figures meet the intended restrained Nature-style standard: flat
white backgrounds, direct statistical encoding, limited color roles, no
decorative panels and no claim inflation. No rerender is indicated now. Figure 5
and Supplementary Figure S8 should still receive a final portal-generated PDF
scaling check because of their tall aspect ratios.

The visual audit is recorded in
`phase17_v7/npj_sba_post_hardening_reaudit/20260830_qiteng_text_freeze/02_FIGURE_VISUAL_REAUDIT.json`.

## 9. Documents and package integrity

Current exact target documents:

| File | Bytes | SHA-256 |
|---|---:|---|
| `Manuscript.docx` | 60,845 | `3B98020C7C77871BEEAD3F5DC774703C7376A305BC362E6DB3E9EF8198490EAF` |
| `Manuscript.pdf` | 240,950 | `272A3453D47A0545C340ACD6B8B2CABB60028AAF826BA9B54680CAEAE418C79E` |
| `Supplementary_Information.docx` | 4,747,342 | `A08760EBA472E47EEDA53D0655D3AFE917E0CDE5D3AE4F9116E8DD95B86D42AA` |
| `Supplementary_Information.pdf` | 5,754,495 | `A52E255284F68411DF10222A50A9E8AABE4A359BC150E46919108B91AEB37BA4` |
| `Cover_Letter.docx` | 39,535 | `5A161E178712BBA458E6AB72F13F5B3D128DD96853F32D3650550DE39DC055FE` |
| `Cover_Letter.pdf` | 68,230 | `E4F9094B0BFFCB2B7089F89007EF4BE9D2F1519C07B6EEE155A918BC3E771837` |

The package
`04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip`
remains 15,221,543 bytes with SHA-256
`F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`.

Integrity findings:

- ZIP CRC passes.
- 20/20 manifest-listed files pass SHA-256 verification.
- Deterministic double-build identity remains recorded.
- Fifteen figure source tables remain byte-identical.
- Manuscript and cover DOCX contain no embedded scientific drawings.
- Supplementary DOCX contains exactly ten inline figure drawings and ten labels.
- Existing dual-render and accessibility receipts remain applicable because no
  document binary changed.

The package is technically valid but is not yet authorized for submission.

## 10. Target-journal and policy check

Official npj Systems Biology and Applications pages were checked on 2026-08-30.
The journal scope includes computational and mathematical systems biology,
disease modeling, single-cell systems biology and systems immunology. The paper
fits this scope when framed around inferential-layer reproducibility rather than
as a descriptive cell-atlas paper.

The official initial-submission page allows flexible first-submission formatting
and accepts Word or PDF files suitable for review. No scientific rewrite is
needed merely to satisfy initial formatting.

The current public APC page lists an Article processing charge of GBP 2,690,
USD 3,490 or EUR 2,990, with possible taxes. This does not establish institutional
coverage. CUHK-Shenzhen eligibility must be confirmed in writing.

The journal metrics page reports current journal-level metrics but does not by
itself prove the required JCR Q1 status for the intended year and category. An
official Clarivate or institutional receipt remains mandatory. If that receipt
does not confirm Q1 in the intended category, target selection must be reopened
before portal submission.

Official pages:

- https://www.nature.com/npjsba/aims
- https://www.nature.com/npjsba/for-authors-and-referees/submisions
- https://www.nature.com/npjsba/for-authors-and-referees
- https://www.nature.com/npjsba/editorial-policies
- https://www.nature.com/npjsba/apc
- https://www.nature.com/npjsba/journal-impact

## 11. Verification performed

Targeted post-hardening audit:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_npj_sba_post_hardening_reaudit.ps1 `
  -RecordVisualPass
```

Result: `PASS_NPJ_SBA_POST_HARDENING_REAUDIT_TEXT_FREEZE`; 6/6 targeted tests passed.

Full repository regression suite:

- 96/96 tests passed.
- Package verifier: `PASS: 20 files verified; exact-file author approval and submission authorization remain pending`.

Machine-readable outputs:

- `00_POST_HARDENING_FULL_REAUDIT.json`
- `01_QITENG_Q1_TEXT_FREEZE_AUDIT.json`
- `02_FIGURE_VISUAL_REAUDIT.json`

These files are under
`phase17_v7/npj_sba_post_hardening_reaudit/20260830_qiteng_text_freeze/`.

## 12. What was not changed

- No scientific analysis was rerun.
- No manuscript, supplement, cover letter or figure was rewritten or rebuilt.
- No threshold, seed, mapper or statistical method was changed.
- No GitHub release or Zenodo version was created or modified.
- No submission authorization was inferred.

## 13. Next-stage decision

The next stage is not more bioinformatics. It is the narrow administrative gate
`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`:

1. Both authors approve the exact DOCX/PDF, 15 figures, supplement, cover letter
   and package SHA-256 values listed above.
2. Archive an official current JCR receipt containing metric year, category,
   rank/denominator and quartile.
3. Obtain written CUHK-Shenzhen APC/OA eligibility or funding confirmation.
4. Complete the current official Nature Portfolio Reporting Summary and
   Editorial Policy Checklist; repository Markdown drafts are not substitutes.
5. Upload only the approved exact files and inspect the portal-generated PDF,
   especially Figure 5 and Supplementary Figure S8.
6. Freeze the manuscript number, submission timestamp, generated PDF and actual
   uploaded-file hashes as the submission receipt.

Until items 1-4 are complete, the correct state remains: technically ready,
scientifically frozen, and submission unauthorized.
