# Gate C7 action record: manuscript and five-figure scientific integration

**Date:** 20 August 2026
**Project:** 6013RP-wyf SLE B-cell manuscript
**Final decision:** `PASS_GATE_C7_MANUSCRIPT_AND_FIVE_FIGURE_SCIENTIFIC_FREEZE`
**Role of this record:** detailed, reproducible account of the work completed in this round

## 1. Round objective

Gate C7 converted the audited Gates C2B4-C6B results into one internally consistent
paper package. The required products were:

1. five main figures rebuilt from frozen numerical outputs;
2. one source-data table per main figure;
3. a Gate C6B-integrated manuscript;
4. a completed and updated research proposal;
5. claim-to-number and figure-to-source crosswalks; and
6. an automated final scientific audit.

No new biological contrast, cluster, threshold, regulator, gene set or perturbation
dataset was selected during this round. The work was integration and verification,
not post hoc discovery.

## 2. Authoritative inputs

The package inherits the following frozen decisions without modification:

| Gate | Authoritative decision | Consequence for Gate C7 |
|---|---|---|
| C2B4 | `PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED` | publish `B_CONV` and `B_ASC`; retain fine-state failure |
| C3A | `NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM` | `B_ASC` abundance is secondary negative context |
| C4B | `PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION` | GSE174188 IFN/ISG is the transcriptional discovery |
| C5B | `PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION` | reserve independent replication for GSE135779 IFN/ISG |
| C6B | `PASS_GATE_C6B_UPPER_Q1_REGULATORY_FRAMING_AUTHORIZED_NONCAUSAL` | permit convergent observational regulatory wording |

Only the corrected active GSE23307 outputs 16-20 were eligible. Outputs 10-14
remain superseded audit artifacts and were excluded from the active manuscript,
figures and source data.

## 3. Actions completed

### 3.1 Unified main-figure reconstruction

Created `audit_tools/phase17_c7_01_build_main_figures.py`. The script reads only
frozen Gate C2B4-C6B tables and deterministically writes five 7.09-inch-wide main
figures as vector PDF and 600-dpi PNG, together with five source-data tables.

The final inferential order is:

1. Figure 1: disease-blind identity scope and the preserved fine-state failure;
2. Figure 2: sample-level `B_ASC` composition and negative primary boundary;
3. Figure 3: GSE174188 `B_CONV` transcription and IFN/ISG prioritization;
4. Figure 4: independent GSE135779 replication and program-specific coherence; and
5. Figure 5: prespecified regulatory and orthogonal IFN-response convergence.

The figures use a shared restrained palette, Arial-compatible typography, lower-case
panel labels, consistent effect/interval grammar and explicit null references. The
figures were visually inspected at full resolution after each rebuild.

### 3.2 Figure interface repairs found during execution

The first Figure 4 run failed because the donor influence file stores a summarized
range as `loo_min_effect` and `loo_max_effect`, not one row-level `effect` field. The
builder was corrected to use the actual frozen summary interface.

The first complete Figure 4 omitted eight source-label sensitivity estimates because
the filter expected `childhood_min50`, whereas the frozen rows are named
`childhood_min50_without_*`. The filter was repaired, and the final panel contains
the full childhood estimate, the 43-donor-deletion range and all eight source-label
omissions.

The first visual review also identified crowded top-row axis titles in Figure 4 and
an unclear orthogonal-panel label/footnote position in Figure 5. Axis wording was
shortened, panel `e` was made explicit, and the significance definition was moved
inside the control panel. All five figures were then regenerated from source.

### 3.3 Manuscript and RP integration

Created `audit_tools/phase17_c7_02_integrate_manuscript.py`. The generator uses v8
and the frozen evidence to produce:

- `manuscript_v9_gateC7_submission_scientific_draft_2026-08-20.md`;
- `research_proposal_v16_gateC7_completed_2026-08-20.md`; and
- `main_figure_legends_v9_gateC7_2026-08-20.md`.

The manuscript now has five Results sections matching Figures 1-5. The new fifth
section reports the prespecified 24-test CollecTRI analysis, target influence and
resampling, M5911 enrichment and corrected GSE23307 paired response. The Discussion
was rewritten so that regulatory convergence strengthens the IFN interpretation
without claiming direct binding, a unique ligand or causation.

Methods now document the exact CollecTRI hash and parser policy,
`sign(logFC) * sqrt(F)`, duplicate-symbol averaging, intercept-containing activity
models, global 24-test correction, target deletion, 100 x 80% target resampling,
MSigDB 2026.1.Hs M5911, 10,000 gene-label permutations and the corrected GSE23307
log2(x+1) workflow. The GSE23307 publication details were verified against PubMed
PMID 20956346.

The RP v16 records Aims 1-4 as completed and replaces future Gate C6B language with
the observed result and its limitations. It preserves the original research logic
while making the completed evidence chain auditable.

### 3.4 Crosswalks and traceability

Generated:

- `02_CLAIM_NUMBER_CROSSWALK.csv`: 14 unique claims, including required negative and
  noncausal boundaries;
- `03_FIGURE_SOURCE_CROSSWALK.csv`: Figures 1-5 mapped to frozen gates, source data
  and claim IDs; and
- `04_MANUSCRIPT_NUMERIC_SOURCE.csv`: 16 unique manuscript metrics with display
  values and authoritative fields.

Every main figure has a separate source-data CSV. Figure 4 contains 4,410 jointly
tested genes, all eight source-label omissions and one donor-deletion summary. Gate
C7 Figure 5 source values match the corrected active Gate C6B source within floating
serialization tolerance.

## 4. Final automated audit

Created `audit_tools/phase17_c7_03_audit_package.py`. The first test execution
correctly returned a temporary HOLD because three audit rules were too strict: line
wrapped boundary sentences were compared literally, the expected numeric-source
count was one too high, and Figure 5 used strict pandas equality despite harmless
floating serialization differences. The audit was repaired to normalize whitespace,
expect the actual 10 inherited plus 6 new metrics, and compare numeric values with a
tight tolerance. No scientific output was changed to make these checks pass.

The final audit passed all 20 checks, including:

- complete C2B4-C6B decision chain;
- five Results sections and five figure legends;
- no stale pending-C6B language;
- all three required noncausal boundary passages;
- exact gene-label-permutation wording;
- no superseded GSE23307 file citation;
- six of six STAT1/STAT2 confirmatory rows positive and global-q significant;
- core target-influence and resampling pass;
- exact M5911 NES and 10,000-permutation values;
- exact corrected GSE23307 donor values;
- 14 unique claims and 16 unique numeric sources;
- five complete PDF/PNG figures and five source-data tables;
- correct Figure 4 and Figure 5 data interfaces; and
- completed RP aims and verified GSE23307 citation.

The final machine-readable decision is in
`phase17_v7/gateC7/20260820_manuscript_figure_integration/06_GATE_C7_FINAL_AUDIT.json`.
An SHA-256 manifest records the active package.

The Codex execution sandbox permitted project-file writes but denied creation of
`.git/index.lock`, so this round could not safely update the local Git index. A
scoped handoff script was added as
`audit_tools/run_6013RP_phase17_gateC7_commit.ps1`. It verifies the final Gate C7
PASS decision, requires branch `main`, stages only the explicit Gate C7 paths, runs
`git diff --cached --check`, commits and pushes. It does not stage unrelated working
tree changes.

## 5. Output inventory

### Manuscript documents

| File | Size | Scope |
|---|---:|---|
| manuscript v9 | 32,363 bytes; 4,378 words | full scientific draft, five Results sections |
| RP v16 | 12,726 bytes; 1,630 words | completed proposal and binding boundaries |
| standalone legends | 3,595 bytes; 467 words | Figures 1-5 |

### Main figures

| Figure | PDF bytes | PNG bytes | Final panels |
|---|---:|---:|---|
| Figure 1 | 57,720 | 610,052 | a-d |
| Figure 2 | 48,942 | 485,523 | a-d |
| Figure 3 | 53,403 | 442,445 | a-d |
| Figure 4 | 55,421 | 637,595 | a-d |
| Figure 5 | 53,558 | 501,635 | a-e |

All PNGs are at least 4,000 x 3,000 pixels; all PDFs exceed 20 KB and retain vector
text/geometry. No panel was assembled by manually editing a rendered image.

## 6. Frozen scientific interpretation

The strongest defensible paper-level conclusion is:

> SLE is associated with an independently replicated IFN/ISG transcriptional shift
> within a disease-blind broad conventional-B compartment, accompanied by
> prespecified and convergent observational IFN-centred regulatory evidence.

The package does not authorize:

- a hard naive, memory, atypical or IFN-high subtype;
- primary `B_ASC` expansion or depletion;
- transcriptome-wide cross-dataset concordance;
- independent replication of GSE174188 internal contrasts;
- a powered inference from the two GSE23307 donors;
- direct STAT1/STAT2 binding;
- a unique IFN-alpha or IFN-beta initiating stimulus; or
- causal or mechanistic validation language.

## 7. Advisor assessment

The paper is now scientifically coherent enough to leave exploratory analysis and
enter submission engineering. The five-figure sequence is logically cumulative and
each later panel respects the scope established by Figure 1. The strongest asset is
not the magnitude of one differential-expression result, but the combination of
disease-blind identity control, biological-unit-aware inference, independent
program-level replication, low-genome-wide-correlation transparency and prespecified
regulatory convergence.

The principal upper-Q1 risk remains that all central patient evidence is secondary
analysis and the only direct perturbation layer has two healthy donors. This is a
reason to maintain noncausal language and choose journals strategically, not a
reason to add another uncontrolled public dataset before packaging the current
paper.

## 8. Next-stage decision

Proceed to Gate C8: journal-specific submission package, complete reference
verification, authorship/declaration capture, supplement architecture, reporting
checklists, rendered DOCX/PDF QA, cover letter and final submission manifest. Do not
unlock additional biological analyses unless Gate C8 identifies a specific,
decision-changing deficiency.
