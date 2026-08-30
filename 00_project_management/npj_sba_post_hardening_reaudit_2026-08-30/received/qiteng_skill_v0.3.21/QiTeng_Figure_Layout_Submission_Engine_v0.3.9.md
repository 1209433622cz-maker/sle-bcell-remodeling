# QiTeng Figure, Layout & Submission Production Engine v0.3.9

## 1. Scope

This module fixes into the Skill:
1. source-observed Teng Qi figure logic;
2. Q1/Nature-style production upgrades;
3. target-journal technical compliance;
4. submission-package integrity.

Critical distinction:

> **LEARN FIGURE LOGIC FROM THE CORPUS; DO NOT BLINDLY LEARN ONE JOURNAL'S EXPORT PARAMETERS.**

The 13-paper corpus contains 41 detected main figures.
The paired CBX8 Final package contains separate manuscript, cover letter, Supplementary file and six separate TIFF figures.

---

## 2. Two figure modes

### `QITENG_FIGURE_NATIVE`
Use when the user explicitly wants close fidelity to the observed Teng Qi visual organization.

Preserve:
- figure-level argument role;
- broad-to-focal/evidence sequence;
- prominent panel labels;
- consistent group colors;
- conceptual schematics for Reviews;
- study-design roadmap for MR.

### `QITENG_FIGURE_Q1_GUARDED` — default
Preserve the above logic while upgrading:
- final-size legibility;
- color accessibility;
- vector editability;
- evidence-safe arrows/labels;
- source-data traceability;
- panel density;
- alignment/white space;
- journal-compliant export.

---

## 3. Figure budget is genre-conditional

Descriptive corpus pattern:

- Original Research: typically many evidence figures; the two core bioinformatics papers use 7 figures each.
- MR Letters: often compress design + principal results into 1 composite figure.
- Full MR/genetic epidemiology: 4–5 figures, usually study design + forest/effect summary + scatter/diagnostic evidence.
- Reviews/Critical Reviews: usually 2–4 synthesis figures.
- Perspective/Commentary may use no figure.

These are descriptive, not quotas.

Use:
`ARGUMENT NEED -> FIGURE ROLE -> FIGURE COUNT`

not:
`GENRE -> FIXED NUMBER`.

---

## 4. One figure = one evidential job

Each main figure should have one dominant question.

Allowed internal sequence:
`ORIENTATION -> PRIMARY EVIDENCE -> VALIDATION/ROBUSTNESS -> BOUNDARY`.

Do not combine unrelated analyses merely to reduce the figure count.

Move panels to Supplement when they are:
- secondary robustness;
- exhaustive pairwise comparisons;
- diagnostic detail;
- redundant visualizations.

---

## 5. Figure architecture router

### STATISTICAL EVIDENCE
For Original Research/quantitative work.

Use:
`broad context -> focal cohort/effect -> validation/robustness`.

Panel order should mirror evidence hierarchy.

### STUDY DESIGN
Especially useful for MR/complex workflows.

Use:
`source -> selection/assumptions -> analysis -> diagnostics/validation`.

Keep text concise.

### COMPACT LETTER SUMMARY
Combine only logically connected design/result components when the format is space constrained.

### MECHANISTIC SYNTHESIS
For Review/Critical Review.

Use:
`central process/hub -> pathways/components -> disease consequence`.

### COMPARATIVE TECHNOLOGY SYNTHESIS
Use:
`existing limitations -> new capability -> residual challenges`.

### TRANSLATIONAL PATHWAY
Use:
`trigger/source -> mechanism -> intermediate phenotype -> clinical endpoint`.

### ROBUSTNESS DIAGNOSTIC
Treat as support for the main estimate, not a new biological claim.

### MULTILAYER EVIDENCE
Use:
`descriptive anchor -> primary effect -> external replication -> orthogonal evidence -> boundary`.

---

## 6. Panel sequence is argument sequence

Observed Teng Qi data figures commonly organize multiple panels under one scientific question.

Q1 rule:

> **Panel order should allow the reader to reconstruct the logic without reading the Results paragraph first.**

Typical orders:
- A = orientation/context;
- B/C = primary/focal evidence;
- later panels = validation, robustness or orthogonal evidence.

Do not make panel A a decorative schematic if the rest of the figure answers an unrelated question.

---

## 7. Panel lettering

Use a single convention throughout a manuscript.

Target journal decides:
- Nature commonly uses lower-case `a, b, c`;
- Frontiers uses bold capital panel references such as `(A), (B)`.

Do not mix A/B/C and a/b/c in the same manuscript unless journal production changes it.

Panel labels must:
- be visually prominent;
- occupy consistent positions;
- not collide with axes/data.

---

## 8. Typography

Maintain one figure font system.

Q1 default:
- one sans-serif family such as Arial/Helvetica unless the target journal requires another;
- consistent hierarchy for panel labels, axis labels, legends and annotations;
- test legibility at final publication width.

Never rescue an overcrowded figure by shrinking text below journal-safe size.

---

## 9. Color semantics

Use a **semantic color dictionary** across the manuscript.

Example:
`Tumour = one color`
`Normal = another`
`Discovery = one color`
`External validation = another`.

Never use the same color to mean different evidence classes in different figures.

Use:
`COLOR + SHAPE / LINE TYPE`
when color alone could fail accessibility.

Avoid red-green-only contrast.

---

## 10. Statistical figures

Main plot must prioritize:
- effect;
- uncertainty;
- group/sample identity;
- corrected significance where relevant.

Stars may be used as visual shorthand, but the Results text should still report interpretable effect/CI where available.

High-dimensional plots:
- show the central pattern;
- reduce illegible category labels;
- move exhaustive feature lists to Supplement.

---

## 11. Conceptual schematics

A review schematic is an **argument map**, not decoration.

Every:
- arrow;
- hub;
- box;
- gradient;
- pathway label

must encode a real relationship.

### Figure Claim Gate

`VISUAL CLAIM <= TEXTUAL EVIDENCE CLAIM`.

If evidence is associative or indirect:
- do not use an unqualified causal arrow;
- consider dashed/qualified links;
- state uncertainty in the caption when material.

---

## 12. Caption architecture

Default:

`FIGURE PURPOSE / TITLE`
-> `PANEL-BY-PANEL MAP`
-> `DENOMINATOR / UNIT`
-> `TEST / ERROR / MULTIPLICITY`
-> `ABBREVIATIONS`
-> `[DISPLAY-SPECIFIC BOUNDARY]`.

Caption and Results should use **orthogonal redundancy**:

- Results = what the evidence means;
- legend = what is displayed and how.

Do not paste the Results paragraph into the figure legend.

---

## 13. Figure-text contract

For every main figure create:

`FIGURE_ID`
-> `RESULTS QUESTION`
-> `CLAIM_ID`
-> `PANEL FUNCTIONS`
-> `VALIDATION CLASS`
-> `MAIN-TEXT SENTENCE`
-> `LEGEND`
-> `SOURCE DATA`.

No panel may become an orphan analysis.

No Results claim should cite a panel that does not actually display the supporting evidence.

---

## 14. Figure/Table/Supplement hierarchy

### Main figure
Carries:
- central evidence;
- strongest validation;
- boundary-changing visual evidence.

### Main table
Carries:
- exact comparable estimates.

### Supplement figure/table
Carries:
- exhaustiveness;
- diagnostics;
- secondary robustness;
- full feature lists.

Hard rule:

> **A result that changes the headline claim cannot exist only in Supplement.**

---

## 15. Image integrity

For microscopy/photography:
- preserve raw originals;
- retain correct scale bars;
- apply only legitimate/global processing;
- do not selectively enhance, remove or introduce image content;
- document transformations when material.

Q1/Nature-style polish never overrides scientific image integrity.

---

## 16. Editable-master rule

Maintain two layers:

### MASTER
- editable vector for graphs/schematics where possible;
- native-resolution raster originals;
- individual panel sources;
- source data;
- plotting code;
- final assembled layout master.

### EXPORT
- journal-specific derivative.

Never make the submission TIFF/JPEG the only surviving source file.

---

## 17. CBX8 paired package: what is learned and what is not

Observed real package:
- Cover Letter;
- manuscript DOCX;
- Supplementary DOCX;
- Figure 1–6 as separate TIFF files.

This supports a **submission package separation rule**.

However, the six TIFF files have embedded metadata of about 144 dpi.

Therefore:

> **144 dpi is explicitly NOT learned as a Teng Qi quality target.**

Technical export must be governed by the current target-journal specification.

---

## 18. Journal Compliance Router

At the start of submission production:
1. identify exact target journal;
2. retrieve current official Instructions/Guide for Authors;
3. record required:
   - figure width;
   - DPI/resolution;
   - file format;
   - color mode;
   - font;
   - panel label convention;
   - maximum file size/figure count if any;
   - legend placement;
   - supplementary rules;
   - initial vs final submission requirements.

Do not rely on memory when current official requirements can be checked.

---

## 19. Representative publisher profiles

### Nature / Nature Portfolio
Representative official guidance includes:
- Nature final artwork widths around 89 mm / 183 mm;
- raster/photographic images at least 300 dpi at maximum use size;
- editable/vector line art preferred;
- RGB;
- Arial/Helvetica;
- accessible color;
- initial submission may use review-quality embedded figures.

### Frontiers
Representative current guideline:
- 85 mm / 180 mm widths;
- 300 dpi at final size;
- smallest visible text at least 8 pt;
- lines at least 2 pt;
- bold capital panel labels.

### Elsevier
Representative current policy:
- approx. 90 mm single / 190 mm double;
- 300 dpi halftone;
- 500 dpi combination art;
- 1000 dpi line art;
- tightly cropped artwork and standard fonts.

### Wiley
Representative guide:
- approx. 80 / 180 mm artwork scales;
- 300 dpi images;
- 600 dpi line art.

Hard boundary:

> **These are publisher-level representative profiles, not permanent journal-level rules. Exact journal instructions override them.**

---

## 20. Submission Production Gate

Before upload, verify:

1. target journal locked;
2. current official requirements checked;
3. manuscript clean version;
4. continuous Figure 1..N inventory;
5. separate figure files if required;
6. legends complete;
7. Supplementary inventory complete;
8. figure-text claim consistency;
9. final-size legibility;
10. resolution/format compliance;
11. vector/raster appropriateness;
12. accessibility;
13. image integrity;
14. source-data traceability;
15. panel alignment;
16. editable tables;
17. cover letter if requested;
18. declarations consistent;
19. reporting checklist when applicable;
20. permissions/licensing;
21. initial-vs-final figure size strategy;
22. post-upload file integrity check.

BLOCK submission when a critical gate fails.

---

## 21. Layout QA

Check each figure at:
- 100% final print size;
- grayscale/color-blind simulation when relevant;
- single-column and double-column target widths if undecided.

Flag:
- text collision;
- clipped labels;
- inconsistent margins;
- over-wide legend;
- excessive blank space;
- visually unequal panel weight;
- redundant title inside the figure;
- axes/lines disappearing after reduction.

---

## 22. Figure overclaim firewall

Search all visual text for:
- `causes`
- `drives`
- `mediates`
- `validated biomarker`
- `therapeutic target`
- `clinical predictor`
- `replicated`
- `causal variant`

Compare each with the Claim Ledger.

Visual language must never bypass the manuscript's evidence governor.

---

## 23. Nature-style Q1 upgrade

When the user asks for Nature/Q1 visual quality:

- white/clean background;
- restrained palette;
- consistent font;
- aligned panel geometry;
- minimal decorative borders/gradients;
- vector plots/text;
- high information density without microtext;
- color-safe design;
- one visual hierarchy per figure;
- source-data traceability;
- explicit evidence boundary where needed.

Do not imitate a Nature aesthetic by sacrificing readability or evidence accuracy.

---

## 24. Final figure workflow

`CLAIM LEDGER`
-> `FIGURE ROLE MAP`
-> `PANEL STORYBOARD`
-> `SOURCE DATA`
-> `PANEL GENERATION`
-> `ASSEMBLY`
-> `FIGURE CLAIM GATE`
-> `LEGEND`
-> `FINAL-SIZE QA`
-> `JOURNAL EXPORT PROFILE`
-> `SUBMISSION PACKAGE QA`.

This module is now part of the default QiTeng full-manuscript workflow.
