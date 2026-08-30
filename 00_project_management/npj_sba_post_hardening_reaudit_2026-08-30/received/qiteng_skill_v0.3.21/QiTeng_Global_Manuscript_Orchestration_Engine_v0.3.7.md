# QiTeng Global Manuscript Orchestration Engine v0.3.7

## 1. Core idea

A mature manuscript does **not** avoid repeating the central concept.
It avoids repeating the **same function**.

Use:

`CLAIM PROPAGATION != SENTENCE REPETITION`

The same central claim may appear in Title, Abstract, Results, Discussion and Conclusion, but each occurrence must do a different job.

---

## 2. The Claim Ledger

Before drafting, create one row per major claim.

Fields:
- `CLAIM_ID`
- `CLAIM_FAMILY`
- `PRIMARY_EVIDENCE_TIER`
- `DIRECT SUPPORT`
- `BOUNDARY-CHANGING EVIDENCE`
- `TITLE FORM`
- `ABSTRACT FORM`
- `RESULTS FORM`
- `DISCUSSION DELTA`
- `CONCLUSION FORM`
- `FUTURE TEST`

No section may silently upgrade the claim beyond the ledger.

---

## 3. Claim strength lattice

Scientific branch:

`L0 SCOPE`
-> `L1 DESCRIPTIVE`
-> `L2 ASSOCIATIONAL`
-> `L3 CAUSAL-INFERENCE`
-> `L4 DIRECT MECHANISM`
-> `L5 CLINICAL UTILITY`

A manuscript may move upward only when new evidence justifies it.

Post-Results sections may reinterpret or compress the evidence, but must not climb the ladder without new evidence.

Perspective/framework writing uses a separate normative branch:
`PROBLEM FRAMING -> AUTHOR FRAMEWORK -> IMPLEMENTATION RECOMMENDATION`.

Do not confuse normative confidence with empirical causality.

---

## 4. Cross-section claim ecology

In the curated positive sentence library:

- Introduction: 69.4% descriptive; 16.1% translational/normative; 14.5% moderate/strong hedge.
- Discussion: 47.1% descriptive; 27.1% translational/normative; 37.6% moderate/strong hedge.
- Conclusion: 51.4% descriptive; 37.8% translational/normative; 16.2% moderate/strong hedge.

Interpretation:

> **Introduction sets the task. Discussion processes uncertainty. Conclusion compresses the adjudicated claim.**

Conclusion does not need maximal hedge density if the evidence boundary is already encoded in the chosen nouns/verbs.

---

## 5. Boundary inheritance

A boundary introduced because of material evidence must persist **semantically** across higher-level sections.

It does not have to be repeated verbatim.

Example logic:

`RESULT: external validation null`
-> `DISCUSSION: discovery signal is context-dependent`
-> `CONCLUSION: potential, not established utility`
-> `TITLE: potential/preliminary if clinical utility is foregrounded`

This is `BOUNDARY INHERITANCE`.

A later section may compress the boundary but may not erase its consequence.

---

## 6. Interpretive Delta

When Discussion restates a Result, require at least one delta:

- `LITERATURE CONTEXT`
- `MECHANISTIC PLAUSIBILITY`
- `CONTRADICTION`
- `EVIDENCE HIERARCHY`
- `BOUNDARY`
- `IMPLICATION`
- `NEXT TEST`

If a Discussion sentence merely says the same thing with synonyms:

`DELETE / MERGE`.

Use:

`RESULT CLAIM + DELTA = DISCUSSION VALUE`

---

## 7. Concept repetition versus phrase repetition

In the selected sentence library, cross-section semantic similarity remains detectable, but exact content-phrase reuse is low.

Descriptive signal:
- Introduction↔Discussion median TF-IDF concept similarity: 0.165.
- 57.1% of Introduction↔Discussion paper pairs share no exact content 4-gram.
- 77.8% of Introduction↔Conclusion pairs share no exact content 4-gram.
- 83.3% of Discussion↔Conclusion pairs share no exact content 4-gram.

Interpretation:

> Preserve **topic anchors**, not full sentence architecture.

This is not a quota because the sentence library is curated rather than exhaustive.

---

## 8. Function-aware Deduplication

Tag every repeated claim with its current job.

Legitimate repetition:
- Title: labels the contribution.
- Abstract: compresses evidence.
- Introduction: turns the gap into a task.
- Results: reports the evidence.
- Discussion: interprets/adjudicates.
- Conclusion: compresses the final defensible claim.

Redundant repetition:
- same claim;
- same evidence;
- same inference;
- no new boundary/decision;
- only synonym replacement.

Decision:

`SAME CLAIM + NEW FUNCTION -> KEEP`
`SAME CLAIM + SAME FUNCTION -> MERGE/DELETE`

---

## 9. Introduction–Results Contract

Every major final-Introduction aim/hypothesis must map to:
- a Results subsection;
- an explicit negative answer;
- or a clearly labeled exploratory analysis.

Flag:
- `ORPHAN AIM`
- `ORPHAN RESULT`
- `POST HOC AIM RETROFIT`

Do not rewrite the Introduction after seeing the Results in a way that falsely makes every exploratory result appear prespecified.

---

## 10. Methods–Results Contract

Reuse the Phase 3C mirror:

`RESULT -> SOURCE -> UNIT -> MODEL -> MULTIPLICITY -> VALIDATION CLASS`

Every headline Result must be reconstructable.

---

## 11. Results–Discussion Contract

Discussion should not replay the Results table.

For each central Results module, choose:
- `DEEPEN`
- `COMPARE`
- `EXPLAIN`
- `CONTRADICT`
- `BOUND`
- `TRANSLATE`

Not every Result deserves its own Discussion paragraph.

Use evidence priority:
`CENTRAL / BOUNDARY-CHANGING > SUPPORTIVE > SECONDARY ROBUSTNESS`.

---

## 12. Discussion–Conclusion Contract

Conclusion has three jobs:
1. identify the strongest convergent contribution;
2. preserve the material evidence ceiling;
3. state the next level of value without reopening the whole debate.

Conclusion must not introduce:
- new data;
- new mechanism;
- new clinical utility;
- a new future-method list.

---

## 13. Abstract–Body Contract

Every Abstract result must map to a body result.

Every material boundary-changing result must influence:
- Abstract conclusion;
- or the wording of the central Abstract result.

Flag:
- abstract-only result;
- body-negative omitted from abstract;
- abstract conclusion stronger than Discussion;
- abstract calls robustness `replication`.

---

## 14. Title–Body Contract

The title may be simpler than the body, but not materially stronger.

Use:
`TITLE CLAIM <= STRONGEST DEFENSIBLE BODY CLAIM`

Qualifiers may be relocated from Title to Abstract/Discussion only when the simplified headline remains accurate.

Clinical/causal/mechanistic qualifiers are non-optional when their removal changes claim class.

---

## 15. Terminology Lock

Lock:
- entity names;
- disease subtype;
- cohort/source;
- analysis unit;
- direction;
- evidence class;
- threshold class;
- causal language.

Do not use lexical variety at the expense of scientific identity.

`controlled repetition > decorative synonym substitution`

---

## 16. Negative-evidence propagation

Boundary-changing negative evidence has a propagation path:

`RESULTS`
-> `DISCUSSION EVIDENCE CEILING`
-> `ABSTRACT/CONCLUSION CLAIM`
-> `[TITLE IF MATERIAL]`

Examples:
- external null;
- failed threshold transport;
- absent predictive increment;
- unresolved fine-mapping;
- mechanistic assay null;
- multiplicity-corrected null.

Do not quarantine inconvenient evidence in Supplement.

---

## 17. Future inheritance

Every high-priority Future item should trace to an unresolved boundary.

Compile:

`LIMITATION / UNKNOWN`
-> `WHAT TEST`
-> `WHICH MODEL/COHORT`
-> `WHAT READOUT`
-> `WHAT DECISION CHANGES`

Flag `ORPHAN FUTURE` when a fashionable method appears without a corresponding unresolved question.

---

## 18. Redundancy Graph

For each paragraph/sentence, assign:
- `CLAIM_ID`
- `SECTION_JOB`
- `EVIDENCE_ID`
- `DELTA_TYPE`

Two nodes are redundant when:
- same CLAIM_ID;
- same SECTION_JOB;
- same evidence;
- no new delta.

Delete the weaker node.

Two nodes are complementary when:
- same CLAIM_ID;
- different section jobs;
- later node changes evidence classification or reader state.

---

## 19. Central-claim budget

A paper may have several analyses but should have a small number of manuscript-level claim families.

Default:
- 1 primary contribution;
- 2–4 supporting claim families;
- explicit boundaries.

If every Figure becomes a separate “major conclusion,” the manuscript lacks hierarchy.

---

## 20. End-to-end orchestration pass

Run in this order:

1. `BUILD CLAIM LEDGER`
2. `LOCK TERMINOLOGY`
3. `CHECK INTRODUCTION–RESULTS CONTRACT`
4. `CHECK METHODS–RESULTS MIRROR`
5. `CLASSIFY VALIDATION/NULLS`
6. `PROPAGATE NEGATIVE EVIDENCE`
7. `RUN INTERPRETIVE DELTA ON DISCUSSION`
8. `RUN FUNCTION-AWARE DEDUP`
9. `CHECK ABSTRACT–BODY CONTRACT`
10. `CHECK TITLE–BODY CONTRACT`
11. `CHECK CONCLUSION BOUNDARY INHERITANCE`
12. `TRACE FUTURE ITEMS TO LIMITATIONS`

Only then perform final language polishing.

---

## 21. Q1 failure modes

Flag:
- `ORPHAN_AIM`
- `ORPHAN_RESULT`
- `ABSTRACT_ONLY_RESULT`
- `BOUNDARY_DROPPED`
- `CLAIM_REESCALATION`
- `RESULTS_REPLAY_IN_DISCUSSION`
- `CONCLUSION_NEW_EVIDENCE`
- `TITLE_OVER_BODY`
- `TERMINOLOGY_DRIFT`
- `VALIDATION_LABEL_DRIFT`
- `NEGATIVE_EVIDENCE_QUARANTINED`
- `ORPHAN_FUTURE`
- `SYNONYMIC_REDUNDANCY`
- `SECTION_ROLE_LEAK`

---

## 22. Anti-template rule

Global consistency does not mean every section uses the same wording.

The goal is:

> **one scientific spine, multiple section-specific functions.**
