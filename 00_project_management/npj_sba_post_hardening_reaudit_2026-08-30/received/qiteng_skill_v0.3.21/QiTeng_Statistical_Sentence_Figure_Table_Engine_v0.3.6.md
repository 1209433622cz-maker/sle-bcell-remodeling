# QiTeng Statistical Sentence Micro-architecture + Figure/Table Narrative Engine v0.3.6

## 1. Mission

Phase 3C-1 defined what Methods and Results must report.
Phase 3C-2 defines **how much statistical information belongs in one sentence and where each evidence component should live**.

Core split:

`MAIN CLAUSE = SCIENTIFIC PROPOSITION`
`STATISTICAL PACKET = EVIDENCE COORDINATES`
`HEADING = SUBSECTION ANSWER`
`FIGURE/TABLE = DISPLAY + EXHAUSTIVE DETAIL`
`LANDING = EVIDENCE CLASSIFICATION`

---

## 2. Statistical Evidence Packet

For a central estimate, prefer:

`EFFECT -> 95% CI -> P/q/FDR`

Add `n/events` when denominator is inferentially important.

In the CBX8 paired Final calibration:
- 103 Results sentences were detected;
- median sentence length was 19 words;
- 25 sentences contained at least two statistical metric types;
- **100.0%** of those multi-metric sentences packaged the statistics in parentheses;
- **92.0%** used semicolons inside/around parallel statistical packets.

Interpretation:

> Parentheses and semicolons are useful for compact **evidence coordinates**, not for hiding the scientific claim.

---

## 3. Main-clause / packet separation

Preferred:

`[Scientific proposition] ([effect]; 95% CI [a–b]; q=[x]).`

Avoid making the parenthesis carry:
- a new biological mechanism;
- a new subgroup conclusion;
- a literature comparison;
- a long caveat unrelated to the estimate.

If the reader needs the parenthesis to understand what happened scientifically, the main clause is too weak.

---

## 4. Statistical order by evidence type

### Group comparison
`group denominators/central values -> difference/effect -> CI -> P/q`

### Survival
`n + events -> HR -> CI -> P`

### Correlation/regression
`rho/beta -> CI if available -> q/P`

### High-dimensional screen
`K of M -> strongest 1–3 effects -> corrected significance -> remainder to table`

### Colocalization
`variant set -> posterior -> prior/model -> evidence boundary`

### Fine-mapping
`variant set -> PIP -> credible set -> purity/model dependence`

The exact statistic may differ; the information logic should not.

---

## 5. Semicolon gate

Use semicolons for:
- two or more **parallel** effect packets;
- paired discovery/validation estimates;
- multiple components of one compact statistical packet.

Do not use semicolons to connect:
- unrelated endpoints;
- a result and a mechanism;
- a current result and a literature paragraph;
- more than ~3 heterogeneous evidence claims.

If the clauses differ in evidence type or interpretation, split the sentence.

---

## 6. Sentence Load Gate

A sentence is overloaded when it contains:
- >3 heterogeneous comparisons;
- effect + sensitivity + mechanism + clinical implication;
- multiple denominators that refer to different analysis populations;
- a screen list that should be a table.

Decision:

`KEEP ONE PACKET / PARALLEL STACK / SPLIT / MOVE TO TABLE`

One sentence may contain several numbers, but should usually have **one dominant scientific claim**.

---

## 7. Results Heading Engine

Heading ladder:

`METHOD LABEL`
< `TOPIC LABEL`
< `ANSWER-ORIENTED`
< `BOUNDED ANSWER`

Use the strongest rung that the subsection directly supports.

Preferred Q1 heading:
- states the biological/statistical answer;
- includes a qualifier if validation is partial;
- does not claim mechanism/clinical utility beyond evidence.

Examples of bounded heading logic:
- `reproducible increase`;
- `context-dependent prognostic potential`;
- `feature-specific immune state`;
- `prioritizes X at a locus`.

Do not force every subsection into a declarative heading. Diagnostics such as heterogeneity may remain method-labeled.

---

## 8. Results subsection opening

Choose one of four openings:

### A. Denominator-first
Use when sample/unit is crucial:
`Among [n/unit], ...`

### B. Question-to-answer
Use when the subsection follows a conceptual sequence:
`To determine whether [question], we evaluated... [answer].`

Keep method recap to one short clause.

### C. Screen-first
For high-dimensional analyses:
`Of [M] tested features, [K] passed [correction].`

### D. Validation-first
For a replication subsection:
`In the independent [cohort], ...`

Do not restart a full Methods explanation.

---

## 9. Results subsection landing

A subsection should end on one of:

`ROBUST OBSERVATION`
`VALIDATION STATUS`
`EVIDENCE BOUNDARY`
`BRIDGE TO NEXT EVIDENCE LAYER`

Avoid ending on:
- a raw P value;
- a figure reference;
- a minor sensitivity result;
- a new mechanistic hypothesis.

CBX8 Final repeatedly lands on evidence classification:
- patient-supported vs imprecise concordance;
- discovery vs non-generalization;
- reproducible feature-specific vs globally inconsistent;
- target prioritization vs causal nucleotide/mediation.

---

## 10. Figure/Table Narrative Hierarchy

### Results prose owns:
- central scientific answer;
- effect magnitude;
- uncertainty;
- multiplicity status;
- validation/non-replication;
- evidence-changing null.

### Figure legend owns:
- panel mapping;
- axes/encoding;
- visual group/sample sizes;
- displayed test;
- symbol meaning;
- panel-specific visual caution.

### Main table owns:
- exact central estimates across comparable evidence units.

### Supplement owns:
- exhaustive high-dimensional results;
- pairwise comparisons;
- sensitivity/diagnostic details;
- provenance.

Hard rule:

> **Exhaustiveness belongs to tables/supplement; hierarchy belongs to prose.**

---

## 11. Figure legend de-duplication

A legend should be independently interpretable, so some controlled redundancy is necessary.

Use **orthogonal redundancy**:
- prose tells *what the result means*;
- legend tells *what is displayed and how*.

Do not duplicate an entire Results paragraph in the legend.

Do not hide a boundary-changing negative result only in a legend or supplement.

---

## 12. Figure reference placement

Prefer:

`[Scientific proposition] (Figure X).`

Use `Figure X shows...` sparingly, mainly when describing a visual pattern that has no compact numerical equivalent.

If more than two consecutive Results sentences begin with `Figure/Table`, rewrite.

---

## 13. Table-vs-prose allocator

Move to a table when:
- >3 parallel estimates need exact values;
- every feature needs reporting;
- multiple diagnostics share the same columns;
- pairwise tests are exhaustive;
- provenance fields matter.

Keep in prose:
- strongest estimate;
- strongest external validation;
- boundary-changing negative result;
- one exemplar that changes interpretation.

---

## 14. Null and partial-validation micro-grammar

### Null
`[Estimate] (95% CI [...]; P/q=...) did not provide evidence for [claim].`

### Directional concordance
`The external estimate had the same direction but limited precision...`

### Failed replication
`The association did not replicate/generalize in [independent cohort].`

### Model robustness
`The estimate was stable across [models/methods], supporting model robustness rather than independent replication.`

The label belongs in the main clause; statistics belong in the packet.

---

## 15. Multiplicity grammar

Do not hide multiplicity status behind `significant`.

Prefer:
- `passed FDR correction`;
- `remained significant after correction`;
- `nominally associated but did not survive correction`;
- `predefined validation family`;
- `exploratory family`.

P and q/FDR answer different questions. Preserve both only when both are decision-relevant.

---

## 16. Results boundary sentence

A short boundary sentence is valuable when it prevents immediate overclassification.

Good jobs:
- explain why a same-data method agreement is robustness;
- separate a selected-cutoff discovery from validated prediction;
- separate shared-signal evidence from mediation;
- label an underpowered concordant external cohort.

Do not turn the Results section into a Discussion by explaining biological mechanisms.

---

## 17. Statistical punctuation

Default compact packet:
`(effect; 95% CI ...; P/q ...)`

Use commas inside a metric:
`95% CI 0.81–1.14`

Use semicolons between distinct metric classes.

Do not create long parenthetical chains with >4 heterogeneous components if a second sentence or table is clearer.

---

## 18. Cross-corpus interpretation boundary

The 13-paper corpus spans different designs and journals.

Early bioinformatics papers more often use topic/method headings and figure-navigation-heavy Results.
MR papers more naturally use OR/CI/P packets.
CBX8 Final provides the strongest real paired calibration for a modern multi-omics Original Research style.

Therefore v0.3.6 learns **transferable evidence operations**, not a universal punctuation quota.

---

## 19. Q1 anti-patterns

Flag:
- `significant` without magnitude when magnitude exists;
- P value before the scientific effect in the main clause;
- >3 heterogeneous estimates in prose;
- heading stronger than the subsection evidence;
- `validated biomarker` from discovery-only data;
- figure legend repeating Results interpretation;
- boundary-changing null hidden only in Supplement;
- same-data robustness called replication;
- subsection ending on a figure number/P value;
- statistics in parentheses carrying a second scientific claim.

---

## 20. Final Phase 3C-2 pass

Run:

`HEADING STRENGTH`
-> `OPENING TYPE`
-> `EFFECT/CI/P PACKET`
-> `SENTENCE LOAD`
-> `TABLE/PROSE ALLOCATION`
-> `FIGURE LEGEND DE-DUP`
-> `SUBSECTION LANDING`
-> `ABSTRACT/DISCUSSION CLAIM PROPAGATION`

If a negative or non-generalizing result changes evidence classification, propagate that change upward.
