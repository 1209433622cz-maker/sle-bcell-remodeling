# SLE B-cell remodeling — Figure 1 boundary-promotion hostile audit

**Date:** 2026-09-02  
**Independent status:** `SCIENTIFIC_VALID__ONE_MAIN_FIGURE_INFORMATION_HIERARCHY_OPPORTUNITY_FOUND`  
**Scope:** manuscript scientific logic, main/supplementary figure ownership, and source-driven artwork architecture. No submission engineering.

## Executive decision

The claim-owner semantic micropass is correct and should be retained. No numerical, statistical, or cross-reference defect was found in the current manuscript.

A deeper main-figure hierarchy audit identified one remaining presentation-level scientific opportunity:

> The manuscript title, abstract, and first Results subsection make the end-to-end B_ASC overlap failure central to the paper's inference boundary, but current main Figure 1b-d all visualize the frozen-representation pass. The actual end-to-end failure is only visualized in Supplementary Figure S4.

This is not a correctness defect. It is an evidence-prioritization issue. For a Nature/npj-style main-figure narrative, the main figure should visually show both the **pass** and the **boundary**.

## 1. Current manuscript logic verified

The current manuscript already has the correct textual sequence:

1. disease-blind reconstruction;
2. frozen-representation broad partition passes;
3. end-to-end reconstruction fails the B_ASC overlap criterion;
4. propagation of observed boundary exchanges does not alter the composition interpretation or positive B_CONV IFN/ISG effects;
5. broad B_CONV/B_ASC is therefore an analysis scaffold rather than a universal taxonomy.

The current claim-owner corrections are also internally consistent:
- Supplementary Table S4a owns correlation-aware regulator sensitivity;
- Supplementary Table S4b owns overlap depletion;
- Supplementary Table S3 owns the quantitative synthesis;
- Supplementary Tables S5-S8 own reproducibility/provenance structure.

## 2. Why Figure 1 is the only figure worth reopening

### Current Figure 1

- **1a**: inference workflow and identity scope — unique and essential.
- **1b**: frozen-representation policy selection — unique and essential.
- **1c**: per-resample mapped ARI and mapping agreement for the frozen two-compartment partition.
- **1d**: frozen-representation state-Jaccard scope gate.

Panels 1c and 1d both reinforce the same scientific fact: the broad partition is stable **when the representation is held fixed**.

The manuscript's stronger and more interesting boundary — full representation reconstruction produces a B_ASC-specific overlap failure — is relegated to Supplementary Figure S4.

### Proposed main-figure architecture

- **1a KEEP** — inference workflow / disease fields protected.
- **1b KEEP** — fine-state policies fail; broad policy is selected.
- **new 1c** — current state-Jaccard panel, showing the frozen-representation broad-state pass.
- **new 1d** — source-rerun summary of end-to-end state Jaccard, showing the B_ASC-specific failure.

This turns Figure 1 into a direct sequence:

`workflow → policy selection → frozen pass → end-to-end boundary`

That sequence better matches both the title and the abstract.

## 3. Source-level evidence for the candidate

The candidate was generated only from frozen current-source objects whose SHA-256 hashes match the GitHub manifest:

- `Figure1_source_data.csv`: `F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805`
- current `Supplementary_Figure_S4_source_data.csv`: `46EE840F86CA33AA4F5FCE0A37EEFCB4DB23831533BBFA20400BAE50744F5D42`

The latter exists in the mounted audit workspace under its pre-reader-path display name; byte identity was confirmed by SHA-256.

Exact state-overlap values used:

| Reconstruction depth | State | Minimum Jaccard | Median Jaccard | Criterion |
|---|---:|---:|---:|---:|
| Frozen representation | B_CONV | 0.999832 | 0.999925 | median >= 0.95 |
| Frozen representation | B_ASC | 0.981096 | 0.991371 | median >= 0.95 |
| End-to-end | B_CONV | 0.998760 | 0.999363 | median >= 0.95 |
| End-to-end | B_ASC | 0.871750 | 0.930323 | median >= 0.95 |

Thus the proposed visual change is not cosmetic: it exposes the exact scientific transition from a fixed-representation PASS to the prespecified end-to-end HOLD.

## 4. What should happen to current Figure 1c

Current Figure 1c is scientifically valid, but it is the least indispensable main panel because:

- Figure 1b already summarizes the frozen policy's ARI performance.
- Figure 1d already shows the state-level frozen scope gate.
- the Results text reports the frozen minimum ARI, minimum agreement and state-median Jaccard explicitly.
- Supplementary Figure S4 contains the more consequential end-to-end robustness layer.

Recommended action: **remove current 1c from the main figure rather than hand-edit it**. Its source data remain preserved and can remain machine-readable. Do not delete or rewrite the underlying result.

## 5. Supplementary Figure S4

**KEEP all five panels.**

The proposed new main 1d should be a compact summary of S4b rather than a duplicate of the full replicate-level panel.

S4 should remain the detailed owner for:
- all five end-to-end criteria;
- replicate-wise B_CONV/B_ASC state Jaccard;
- boundary exchanges;
- composition propagation;
- IFN/ISG propagation.

This preserves the main/supplement distinction:
- main Figure 1 = inferential boundary;
- Supplementary S4 = complete sensitivity audit.

## 6. Other main figures

### Figure 2 — KEEP 4/4
No panel is redundant. It provides observed abundance, contrast-level estimates, mandatory sensitivity policies and leave-one-sample-out stability.

### Figure 3 — KEEP 4/4
The program hierarchy, robustness sequence, gene-level positive-arm coherence and technical/pan-B specificity controls are all distinct.

### Figure 4 — KEEP 4/4
External effect replication, discovery-vs-external comparison, genome-wide discordance with IFN-gene concordance, and donor/source-label influence are complementary and directly support the bounded replication claim.

### Figure 5 — KEEP 5/5
Figure 5a should not be replaced by a causal network. It is the manuscript's explicit evidence-class/causal-ceiling panel. Panels 5b-e provide the actual regulatory and orthogonal response evidence.

## 7. Supplementary figures

S1-S10 remain scientifically justified. No supplementary panel should be deleted or replaced in this pass.

Particularly:
- S2 retains representation/ISG-exclusion diagnostics;
- S4 retains the complete end-to-end boundary audit;
- S8 retains the corrected external-mapping calibration failure;
- S9/S10 retain the correlation-aware and overlap-depletion regulator sensitivities.

## 8. Text changes if the Figure 1 candidate is adopted

Only source-linked cross-reference/legend changes are justified:

1. frozen-representation Results sentence: change `Fig. 1a-d` to `Fig. 1a-c`;
2. end-to-end Results paragraph: add main-figure ownership, e.g. `Fig. 1d; Supplementary Fig. S4`;
3. rewrite Figure 1 legend c/d so:
   - c = frozen state-Jaccard pass;
   - d = end-to-end state-Jaccard boundary;
4. do not change any number, threshold, claim strength or statistical model.

## 9. Adoption gate

Do not make the candidate canonical automatically.

Adopt only if a final rerender from the project plotting code satisfies all of the following:

- same frozen source-data hashes;
- no statistical rerun;
- no manually edited PDF/PNG;
- main Figure 1 makes the fixed-pass → end-to-end-boundary contrast clearer at actual publication width;
- no text below the existing figure-size readability standard;
- WPS/LibreOffice manuscript pagination remains stable;
- Supplementary S4 remains the complete sensitivity owner;
- full regression suite passes.

If the final source rerender is not clearly better at actual size, retain the current Figure 1.

## 10. Next-stage decision

The next justified stage is not broad maintenance-freeze work and not a new cohort search.

It is the very narrow:

`FIGURE1_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE`

After this single figure-architecture experiment, either:
- **ACCEPT** the source-rerun Figure 1 and refreeze; or
- **REJECT** the candidate and restore the current Figure 1 byte-identically.

No other main or supplementary figure should be reopened unless this gate uncovers a concrete downstream defect.
