---
name: qiteng-academic-writing
version: 0.3.21
status: experimental-phase3g0e1-figure-object-integrity-calibrated
language: English scientific writing; Chinese or English instructions accepted
purpose: Reconstruct biomedical manuscripts using Teng Qi's recurrent argument architecture, move-state transitions, evidence calibration, contradiction handling, and translation-oriented logic, with a Q1-rigor enhancement layer.
---

# QiTeng Academic Writing Skill v0.3.21

## 1. Mission

Do not merely polish language. Reconstruct the scientific argument so a reader can continuously answer:

1. Why does this problem matter?
2. What is already known?
3. What remains insufficient or uncertain?
4. Why is the chosen target/method/framework appropriate?
5. What does the manuscript actually add?
6. What evidence directly supports each claim?
7. What alternative explanation or contradiction matters?
8. Why does the finding matter mechanistically, clinically, or methodologically?
9. What remains unproven?
10. What specific next test would resolve that uncertainty?

Target style: **explicitly navigated, evidence-dense, tension-aware, mechanism-oriented, translationally relevant, and claim-calibrated**.

Capture reasoning architecture, not reusable phrases. Never copy or closely reproduce sentences from the reference corpus.

---

## 2. Core invariant: logic survives compression

The corpus shows a stable rule across long articles, reviews, letters, and perspectives:

> **The number of paragraphs may change; the logical states should not disappear.**

A long Introduction may expand a state across several paragraphs. A Letter may compress several states into one paragraph. Do not force a fixed paragraph count.

Use a state machine rather than a rigid template.

Core cross-genre kernel:

`KNOWN -> INSUFFICIENT -> GAP/TENSION -> RESPONSE -> EVIDENCE -> INTERPRETATION -> IMPLICATION -> BOUNDARY -> NEXT TEST`

Allowed operations:
- `EXPAND`: one state -> multiple paragraphs;
- `COMPRESS`: several adjacent states -> one paragraph;
- `LOOP`: repeat FINDING -> INTERPRETATION for multiple findings;
- `SKIP_OPTIONAL`: omit nonessential context;
- `NEVER_SKIP_REQUIRED`: do not omit a gap, evidence boundary, or study task when the genre requires it.

---

## 3. Before writing: build an argument map

Construct internally:

`CENTRAL CLAIM -> UNRESOLVED PROBLEM -> NOVELTY -> EVIDENCE MAP -> SECTION JOBS -> MOVE STATES -> CLAIM STRENGTH -> NEXT TESTS`

If the argument map is weak, repair it before sentence-level editing.

Required audit questions:
- What is the single most defensible contribution?
- Which result/figure/table supports it?
- What evidence would a hostile reviewer say is missing?
- Is the manuscript claiming association, causal inference, mechanism, or clinical utility?
- Does the language reveal that distinction?

---

## 4. Evidence ladder and claim governor

Classify every major claim:

- `E0_BACKGROUND`: established background knowledge.
- `E1_ASSOCIATION`: observational, bioinformatic, correlational, exploratory evidence.
- `E2_ROBUST_ASSOCIATION`: replicated, externally validated, or sensitivity-supported association.
- `E3_CAUSAL_INFERENCE`: valid causal-inference evidence such as well-supported MR; not direct biochemical mechanism.
- `E4_MECHANISTIC`: perturbational/experimental evidence directly supporting mechanism.
- `E5_TRANSLATIONAL`: prospective clinical, interventional, implementation, or validated clinical-utility evidence.

Hard rule:

> **Claim strength must not exceed the strongest evidence that directly supports that claim.**

Examples:
- E1: `is associated with`, `correlates with`, `is linked to`.
- E2: `is consistently associated with`, `was reproduced across independent analyses`.
- E3: `genetic evidence supports a potential causal effect`, `is compatible with a causal relationship`.
- E4: `regulates`, `mediates`, `drives` only when direct perturbation supports the mechanism.
- E5: `improves clinical outcome`, `has clinical utility` only with appropriate prospective/interventional evidence.

Never collapse:

`ASSOCIATION != CAUSAL INFERENCE != BIOLOGICAL MECHANISM != CLINICAL EFFICACY`

---

## 5. Move vocabulary

Use one dominant move per argument unit; a unit may have one secondary move.

### Problem-establishing moves
`CONTEXT`, `BURDEN`, `PROBLEM`, `UNMET_NEED`, `CURRENT_STANDARD`, `RESIDUAL_PROBLEM`

### Rationale moves
`TARGET_RATIONALE`, `BIOLOGICAL_RATIONALE`, `MODEL_LIMITATION`, `SOLUTION_RATIONALE`, `BIOLOGICAL_PLAUSIBILITY`

### Tension/gap moves
`GAP`, `TENSION`, `CAUSAL_AMBIGUITY`, `CONTRADICTION`, `EVIDENCE_GAP`, `TRANSLATIONAL_GAP`

### Response moves
`AIM`, `SCOPE`, `CORE_QUESTIONS`, `METHOD_RATIONALE`, `APPROACH_MAP`, `ACTIONABLE_FRAMEWORK`

### Evidence moves
`FINDING`, `FINDING_SUMMARY`, `ROBUSTNESS`, `EVIDENCE`, `EMPIRICAL_SUPPORT`, `LITERATURE_CONTEXT`

### Interpretation moves
`MECHANISM`, `MECHANISM_HYPOTHESIS`, `SYNTHESIS`, `CONTRADICTION_RESOLUTION`, `CONTEXT_DEPENDENCE`

### Application moves
`IMPLICATION`, `TRANSLATION`, `TARGETS`, `POLICY_SCALE_UP`, `IMPLEMENTATION`

### Boundary moves
`LIMITATION`, `EVIDENCE_BOUNDARY`, `CAUSAL_BOUNDARY`, `SAFETY`, `REPRODUCIBILITY`

### Forward moves
`FUTURE`, `NEXT_TEST`, `RESEARCH_PRIORITY`, `TRIAL_DESIGN`

---

## 6. Core paragraph algorithm

Default analytical paragraph:

`CLAIM -> EVIDENCE -> INTERPRETATION -> QUALIFICATION -> BRIDGE`

### 6.1 Claim
Open with the proposition the paragraph will establish.

### 6.2 Evidence
Provide only evidence necessary for that proposition. Prefer effect size, direction, confidence interval, consistency, evidence type, and external validation over adjectives.

### 6.3 Interpretation
Explain the meaning. A result left uninterpreted is unfinished.

### 6.4 Qualification
State contradiction, indirectness, heterogeneity, competing explanation, or design limitation when material.

### 6.5 Bridge
End by resolving the current question or generating the next question.

Hard rule:

> A paragraph should change the reader's state of knowledge. If deleting it does not change the argument, compress or remove it.

---

## 7. Transition engine

First classify the relation between adjacent units:

`CONTINUATION / ADDITION / CONTRAST / CONCESSION / CAUSE / CONSEQUENCE / EXAMPLE / QUALIFICATION / SYNTHESIS / GAP / PIVOT`

Only then choose transition wording.

Do not use connectors merely to sound academic. Prefer lexical continuity and repeated conceptual anchors where possible.

---

# 8. Router: ORIGINAL_RESEARCH

## 8.1 Introduction state machine

Required states:

`CONTEXT/PROBLEM -> UNMET_NEED -> TARGET_RATIONALE -> PRECISE_GAP -> AIM/APPROACH`

Optional branches:
- immune or therapeutic context;
- current-standard ceiling;
- contradiction in prior evidence;
- independent-validation need.

Hard rules:
1. Do not introduce the focal molecule before the reader understands why the disease problem needs another determinant, unless the target itself defines the problem.
2. Target history is expendable; target-to-disease plausibility is not.
3. The final Introduction unit must state a research task, not background.
4. Do not promise biomarker/therapeutic-target status before validation.

### Q1 upgrade
Replace generic burden-first openings with tension-first openings when the topic allows it:

`Despite [current advance], [specific unresolved failure] persists because [mechanistic/clinical gap].`

## 8.2 Results state machine

For each evidence module:

`ANSWER-ORIENTED HEADING -> DENOMINATOR/UNIT -> DIRECTION + MAGNITUDE -> UNCERTAINTY -> MULTIPLICITY -> VALIDATION/ROBUSTNESS -> [SHORT BOUNDARY IF NEEDED]`

Hard rules:
- report effect/magnitude when available; do not let P value carry the whole result;
- distinguish independent replication, orthogonal triangulation, same-data model robustness, and assumption diagnostics;
- summarize high-dimensional screens before developing a small number of central exemplars;
- null/non-generalizing evidence is boundary-changing evidence and must not be hidden;
- figure/table references navigate evidence; they should not replace the scientific proposition;
- keep literature comparison and mechanism-heavy explanation primarily for Discussion.

## 8.3 Discussion state machine

Opening:

`PROBLEM RESET -> STUDY CONTRIBUTION`

Then loop for each major result:

`FINDING -> LITERATURE CONTEXT -> AGREEMENT/CONTRADICTION -> EXPLANATION/MECHANISM -> IMPLICATION -> CONFIDENCE BOUNDARY`

Close with:

`INTEGRATIVE MODEL -> TRANSLATIONAL RELEVANCE -> LIMITATIONS -> NEXT TESTS -> RESTRAINED CONCLUSION`

Hard rules:
- A Discussion paragraph that only repeats Results is incomplete.
- Restate only enough result detail to support interpretation.
- If a result conflicts with prior literature, do not hide it; route it through the contradiction resolver.
- Correlation-derived immune or pathway claims must be labeled as hypotheses unless directly validated.

---

# 9. Router: MR_GENETIC_EPIDEMIOLOGY

## 9.1 Introduction state machine

`OBSERVATIONAL SIGNAL -> CAUSAL AMBIGUITY -> WHY OBSERVATIONAL DATA CANNOT RESOLVE IT -> WHY MR HELPS -> PRECISE EXPOSURE/OUTCOME QUESTION -> AIM`

Preferred mature pattern:

> Ask the causal question before teaching the method.

Avoid generic MR tutorials at the start.

## 9.2 Methods visibility requirements

Preferred order:

`MR ASSUMPTIONS -> EXPOSURE/OUTCOME SOURCES -> ANCESTRY/SAMPLE OVERLAP -> IV SELECTION -> LD CLUMPING -> HARMONIZATION -> INSTRUMENT STRENGTH -> PRIMARY ESTIMATOR -> HETEROGENEITY -> PLEIOTROPY -> INFLUENCE/OUTLIERS -> REVERSE MR -> MULTIPLE TESTING -> REPLICATION STATUS`

Expose:
- relevance, independence and exclusion restriction, but keep textbook explanation proportional to the journal/audience;
- exposure/outcome release, ancestry and sample overlap;
- instrument selection and LD clumping;
- harmonization and F statistics / weak instrument assessment;
- primary estimator;
- heterogeneity;
- horizontal pleiotropy;
- influence/leave-one-out/outlier analysis;
- directionality/reverse MR when relevant;
- multiple-testing strategy;
- replication or absence of replication.

Hard rule:
> Do not spend more words teaching MR than specifying the actual MR analysis.

## 9.3 Results order

`INSTRUMENT SET/SCREEN -> PRIMARY IVW ESTIMATE -> ALTERNATIVE-ESTIMATOR CONCORDANCE -> HETEROGENEITY -> PLEIOTROPY -> OUTLIER/INFLUENCE -> REVERSE MR -> MULTIPLE TESTING -> REPLICATION STATUS`

Report:
`EFFECT -> 95% CI -> P/q` when available.

For many exposures:
`SCREEN SUMMARY -> CENTRAL EXEMPLARS -> REMAINDER IN TABLE/SUPPLEMENT`.

Do not call an estimate a protective/pathogenic biological factor when the evidence only supports a genetically predicted effect or association.

## 9.4 Discussion state machine

`PRINCIPAL CAUSAL-INFERENCE SIGNAL -> LITERATURE CONTEXT -> PLAUSIBLE BIOLOGICAL PATHWAY -> NOVEL/CONFLICTING EVIDENCE -> ROBUSTNESS -> LIMITATIONS -> SPECIFIC FUNCTIONAL TEST`

### MR claim governor
- nominal IVW only: `suggestive evidence`;
- robust across estimators/sensitivity: `genetic evidence supports a potential causal effect`;
- inconsistent or underpowered: `compatible with, but does not establish, a causal relationship`;
- mechanism language remains hypothetical without E4 evidence;
- therapeutic-target language remains prioritization, not efficacy.

---

# 10. Router: REVIEW_CRITICAL_REVIEW

## 10.1 Mature review architecture

Prefer:

`FOUNDATION -> DISEASE/STATE ALTERATION -> MECHANISTIC AXES -> EVIDENCE HIERARCHY -> CONTRADICTIONS -> TRANSLATIONAL OPPORTUNITY -> IMPLEMENTATION/SAFETY BARRIERS -> TESTABLE FUTURE AGENDA`

Avoid encyclopedia-style literature stacking.

## 10.2 Review synthesis cycle

After a cluster of studies, perform:

`WHAT THEY COLLECTIVELY SHOW -> EVIDENCE TIER -> WHERE THEY DISAGREE -> WHY THEY MAY DISAGREE -> WHAT REMAINS UNKNOWN -> WHAT TEST RESOLVES IT`

Hard rule:

> Never write three consecutive study summaries without synthesis.

## 10.3 Evidence hierarchy

Separate:
- randomized/interventional human evidence;
- prospective human evidence;
- observational human evidence;
- patient-derived ex vivo evidence;
- animal evidence;
- cell-line evidence;
- computational/in silico evidence.

Do not present them as interchangeable.

## 10.4 Critical-view requirement

A mature critical review should explicitly state:
1. what this review adds beyond existing reviews;
2. the strongest evidence;
3. the weakest/most indirect evidence;
4. the central contradiction;
5. the most consequential missing experiment or dataset;
6. the translational bottleneck;
7. a testable research agenda.

## 10.5 Review closing rule

The conclusion should reduce uncertainty, not merely summarize topics.

Preferred close:

`WHAT IS SUPPORTED -> WHAT IS NOT ESTABLISHED -> PRACTICAL INTERPRETATION -> NEXT DECISIVE TEST`

---

# 11. Router: LETTER_SHORT_REPORT

Use maximal compression while preserving state order.

Preferred sequence:

`TRIGGERING FINDING -> GAP/QUESTION -> METHOD AS SOLUTION -> METHODS IN 2-4 SENTENCES -> PRIMARY EFFECT ESTIMATE -> ROBUSTNESS -> INTERPRETATION -> BOUNDARY -> NEXT TEST`

Do not waste limited space on broad disease background.

The corpus demonstrates that several states may occupy one paragraph; preserve logical order even under extreme compression.

---

# 12. Router: PERSPECTIVE_COMMENTARY

Use tension-driven architecture:

`ACCEPTED TRUTH -> HIDDEN CONTEXTUAL TENSION -> EMPIRICAL SUPPORT -> MECHANISM OF THE PROBLEM -> ACTIONABLE FRAMEWORK -> IMPLEMENTATION SAFEGUARDS -> POLICY/CLINICAL SCALE-UP -> PRINCIPLE-LEVEL CLOSE`

Hard rule:

> Critique without an implementable response is incomplete.

For frameworks, specify:
- components/phases;
- responsible actor;
- decision point;
- intended benefit;
- risk prevented;
- implementation constraint.

---

# 13. Contradiction resolver

When new findings disagree with prior literature, do not write only `This may be due to sample differences.`

Run this sequence:

1. `STATE_CONFLICT`: exactly what differs? direction, magnitude, significance, phenotype, timing, subgroup, endpoint?
2. `COMPARE_EVIDENCE`: which study has stronger design/evidence tier?
3. `CLASSIFY_SOURCE`:
   - population/ancestry;
   - sample size;
   - disease stage/subtype;
   - treatment context;
   - tissue/cell type;
   - assay/platform;
   - endpoint definition;
   - statistical model/covariates;
   - temporal context;
   - biological context dependence;
   - random error or winner's curse.
4. `EXPLAIN_WITHOUT_OVERREACH`: give the most plausible explanation(s), clearly labeled as hypotheses if untested.
5. `DECISIVE_TEST`: state what analysis/experiment would discriminate between explanations.

Preferred output unit:

`CONFLICT -> PLAUSIBLE SOURCE -> BIOLOGICAL/METHOD EXPLANATION -> DECISIVE TEST`

---

# 14. Future-direction compiler

Ban empty endings such as `more studies are needed` unless immediately followed by a concrete design.

Compile every major uncertainty into:

`UNCERTAINTY -> MODEL/POPULATION -> INTERVENTION/EXPOSURE -> COMPARATOR -> READOUT -> ENDPOINT -> DECISION RULE`

Examples of decision-level questions:
- Does direct perturbation of X alter Y in a relevant model?
- Does the association replicate in an independent ancestry/cohort?
- Does the biomarker improve discrimination/calibration beyond current clinical variables?
- Does intervention change a hard clinical endpoint, not only a surrogate?
- Does the effect depend on stage, subtype, dose, timing, or cell state?

Future work should be prioritized, not merely enumerated:
- `P1`: required to validate the central claim;
- `P2`: mechanism refinement;
- `P3`: translation/implementation.

---

# 15. Claim calibration dictionary

Automatically challenge:

- `X is a biomarker` -> `X is a candidate biomarker` unless intended-use validation exists.
- `X is a prognostic biomarker` -> prefer `X is associated with prognosis` unless independent prognostic validation is adequate.
- `X is a therapeutic target` -> `X may represent a candidate therapeutic vulnerability/target` unless intervention evidence exists.
- `X causes Y` -> reserve for designs/evidence that justify causal language.
- `This study proves` -> generally `shows`, `supports`, `provides evidence`, `is consistent with`.
- `clinical application` -> distinguish `clinical relevance`, `translational potential`, `clinical validity`, `clinical utility`.
- `mechanism` -> use `possible mechanism`, `mechanistic hypothesis`, or `pathway consistent with` unless experimentally demonstrated.

---

# 16. Sentence Move Engine — Phase 3A

The sentence is not the starting unit. The **move** is.

Composer pipeline:

`MOVE -> INFORMATION SLOTS -> EVIDENCE TIER -> CLAIM STRENGTH -> HEDGE -> SEMANTIC BRIDGE -> LENGTH/RHYTHM CHECK`

## 16.1 Semantic-relation-first rule

First determine what the sentence does to the reader's knowledge state. Only then choose wording or a connector.

Hard rule:

> `However`, `Therefore`, `Conversely`, `In contrast`, `framework`, `support`, or similar lexical cues do not define a move by themselves.

Examples:
- `In contrast` may compare subtypes without creating a literature contradiction.
- `framework` may refer to an MR analytic framework rather than an implementation framework.
- `support` may describe infrastructure, not an evidence boundary.

## 16.2 One dominant move

Prefer one dominant rhetorical job per sentence. A secondary move is allowed when it is tightly coupled.

Split or reconstruct a sentence when it performs unrelated jobs such as:
`BACKGROUND + RESULT + MECHANISM + CLINICAL CLAIM`.

## 16.3 Move-specific realization

Use the abstract patterns in `patterns/QiTeng_sentence_move_pattern_catalog_v0.3.0.md`.

Examples of logic, not copyable phrases:
- `PRECISE_GAP`: known -> missing specific relation.
- `TENSION`: accepted benefit -> residual competing problem.
- `METHOD_RATIONALE`: named uncertainty -> why this design resolves it.
- `FINDING`: observation -> quantitative/comparative anchor.
- `CONTRADICTION`: exact conflict -> prior evidence.
- `CONTRADICTION_RESOLUTION`: plausible source -> discriminating test.
- `EVIDENCE_BOUNDARY`: supported claim -> explicitly unsupported stronger claim.
- `NEXT_TEST`: uncertainty -> model/design/readout -> decision endpoint.

## 16.4 Evidence and hedge coupling

Hedging is not decoration. Couple it to evidence tier.

- E1 association: use association verbs; mechanism is hypothetical.
- E3 causal inference: causal wording remains design-bounded and does not imply biochemical mechanism.
- E4 mechanism: direct regulatory verbs require perturbational support.
- E5 translation: clinical-utility wording requires appropriate prospective/interventional validation.

Do not weaken every sentence. Hedge only the uncertain component.

## 16.5 Gold, Silver and negative exemplars

The embedded Phase 3A library contains:
- `GOLD`: high-confidence or manually corrected/reconstructed examples;
- `SILVER`: context-dependent valid variants;
- `NEGATIVE_EXEMPLAR`: corpus-derived patterns retained specifically to teach what Q1 mode should upgrade.

Use Gold first for structural abstraction. Use Silver to diversify realization. Never imitate a Negative Exemplar.

## 16.6 Anti-copy rule

The library is a **functional pattern corpus**, not a phrase bank.

Never output or closely paraphrase a reference sentence merely because it matches the desired move. Generate a new sentence from:
`new manuscript facts + abstract move pattern + evidence tier + intended transition`.

## 16.7 Default sentence style

- one main proposition per sentence;
- usually 15-28 words, but logical density is more important than count;
- active voice when the actor is meaningful;
- concrete nouns and verbs;
- quantitative evidence before evaluative adjectives;
- repeated conceptual anchors rather than stacked transition adverbs;
- sentence endings should either resolve the current move or create a legitimate bridge.

Avoid:
- generic burden openers when a sharper tension is available;
- long historical catalogs that do not advance the gap;
- repeated connector adverbs;
- ornamental novelty words;
- result repetition in Discussion;
- speculative mechanism stated as fact;
- premature biomarker/therapeutic-target claims;
- meta-prose that describes the manuscript or figure instead of advancing the science.

---


# 16A. Phase 3B human-edit calibration

A real paired manuscript case showed that Teng Qi's editing preference is not simply `add more boundaries`. It often follows a two-pass pattern:

`LOGICAL COMPLETENESS -> NARRATIVE COMPRESSION`

The manuscript should first become scientifically complete. Then remove or relocate repeated explanation, repeated qualification, duplicate roadmaps, and secondary evidence that no longer changes the reader's conclusion.

## 16A.1 Two fidelity modes

### `QITENG_NATIVE`
Use when the user explicitly asks to imitate Teng Qi's observed editing behavior as faithfully as possible.

Priorities:
- compression;
- direct narrative flow;
- fewer repeated boundary sentences;
- merge adjacent compatible moves;
- dedicated future-facing close;
- concise top-level title/claim.

### `QITENG_Q1_GUARDED` — default
Use Teng Qi's compression behavior but retain Q1 evidence safeguards.

Priorities:
- apply all native compression rules;
- never remove the last material evidence boundary;
- preserve a local boundary when omission would make the immediately preceding claim misleading;
- preserve mechanism/causality/clinical-utility distinctions even if they make prose slightly longer.

## 16A.2 Boundary Budget

Do not ask only `Is a boundary present?` Ask:

1. Where is the strongest claim made?
2. Where could a reader first misinterpret it?
3. Has the same boundary already been stated nearby?
4. Can the qualification be moved to a higher-value location without creating local overclaim?
5. Is this the last remaining statement of a material limitation?

Allowed operation:

`BOUNDARY_PRESENT -> DUPLICATE? -> RELOCATE / COMPRESS / KEEP`

A boundary may be removed only when:
- the local sentence remains accurate without it; and
- the material limitation is explicit elsewhere at the point of decision.

## 16A.3 Title-to-body qualification ladder

Titles should carry only qualifiers required to prevent headline-level misrepresentation.

A qualifier may be omitted from the title when:
- the core title remains scientifically defensible;
- the Abstract conclusion restores the nuance;
- the Discussion/Conclusion states the evidence boundary clearly.

Do not copy this behavior if omission would convert an association into a causal, mechanistic, or validated-clinical claim.

## 16A.4 Compression pass

After the argument is complete, run a second pass:

- merge adjacent `APPROACH_MAP + AIM` when both are short and sequential;
- merge adjacent Discussion units when the second only repeats a boundary already preserved elsewhere;
- remove duplicate study-design roadmaps when subsection headings already provide navigation;
- remove secondary robustness paragraphs from the main Discussion when they do not alter the central claim;
- separate a clean Conclusion when journal structure permits.

Compression must reduce redundancy, not evidence.

## 16A.5 Dedicated future-agenda close

For Original Research, after limitations consider one dedicated forward paragraph:

`P1 prospective/clinical validation -> P2 cross-platform/mechanistic validation -> P3 translation/implementation`

Do not present all future work at equal priority. In Q1-guarded mode, rank the agenda by which uncertainty most threatens the central claim.

## 16A.6 Human-edit evidence is not automatically a scientific gold standard

A paired human edit is evidence about **editorial preference**. It is not automatically evidence that every deletion is scientifically superior.

When a human-style edit conflicts with the evidence ladder:
- `QITENG_NATIVE` may reproduce the editorial tendency if the user explicitly requests fidelity;
- `QITENG_Q1_GUARDED` preserves the stronger scientific safeguard.



# 16B. Paragraph Assembly & Cadence Engine — Phase 3B-2

The move is the unit of reasoning, but the **paragraph is the unit of reading**.

Build paragraphs with:

`ANCHOR -> DEVELOPMENT -> INTERPRETATION -> [BOUNDARY IF LOCALLY NEEDED] -> LANDING`

Then run a compression pass.

## 16B.1 Position-aware assembly

Corpus fingerprint:
- Introduction Q1: 93.1% Problem/Context family.
- Introduction Q4: 72.9% Response/Aim family.
- 9/10 manually coded Introductions begin with Problem/Context.
- 8/10 end with Response/Aim.

Operational rule:

> **Introduction narrows.**

Do not let the final Introduction unit drift back into generic background.

Late Discussion fingerprint:
- Application: 30.8%;
- Boundary: 19.2%;
- Forward: 11.5%.

Operational rule:

> **Discussion lands.**

Do not introduce a new major evidence stream late unless it changes the central claim.

## 16B.2 Transition economy

Natural continuation dominates selected sentence transitions:
- Introduction: 74.2%;
- Discussion: 64.7%.

Default:

`LEXICAL CONTINUITY > EXPLICIT CONNECTOR`

Use an explicit cue only when it helps the reader identify a real relation:
`CONTRADICTION / CONCESSION / BOUNDARY / CAUSAL PIVOT / MAJOR SYNTHESIS`.

## 16B.3 Localized hedge

Do not hedge uniformly.

Phase 3A functional cadence shows:
- Boundary, Application and Interpretation carry the most uncertainty language;
- Problem Setup and Response/Aim carry substantially less.

Operational rule:
- state established context directly;
- state the study task directly;
- hedge the uncertain inference, not the entire sentence;
- keep boundary sentences short and exact.

## 16B.4 Functional sentence rhythm

Use different rhythms by move:
- `RATIONALE_CONTEXT`: may be longer because it links biology/evidence.
- `PROBLEM_SETUP`: direct.
- `RESPONSE`: direct and task-oriented.
- `EVIDENCE`: quantitative where possible.
- `INTERPRETATION`: one explanatory step at a time.
- `BOUNDARY`: short and decisive.
- `FORWARD`: may be longer when it specifies model, design, readout and endpoint.

Do not force every sentence into the same length band.

## 16B.5 Original Research paragraph span

Default functional span:
1. anchor proposition;
2. 2–4 development sentences;
3. interpretation;
4. optional local boundary;
5. landing/bridge.

This is not a fixed sentence-count template.

Paired human-edit evidence showed:
- adjacent Introduction moves were merged into a stronger 5-sentence final paragraph;
- low-priority 2-sentence Discussion content was removed;
- a dedicated 4-sentence future paragraph was added.

Hard rule:

> `ONE MOVE != ONE PARAGRAPH`.

## 16B.6 Microparagraph gate

In full Original Research, flag standalone 1–2 sentence paragraphs unless they have a deliberate special function.

Decision:
`KEEP SPECIAL / MERGE / EXPAND / DELETE`.

## 16B.7 Landing engine

A paragraph should end at the reader-state destination.

- early Introduction -> unmet need;
- target-rationale paragraph -> precise gap;
- final Introduction -> aim/hypothesis/analytic task;
- Results -> robust observation;
- Discussion -> interpretation / bounded implication;
- Limitation -> evidence ceiling or resolving test;
- Future -> decision-relevant endpoint;
- Conclusion -> strongest defensible contribution.

## 16B.8 Evidence-space allocator

Before assigning paragraph length, classify evidence:
- `CENTRAL`;
- `BOUNDARY_CHANGING`;
- `SUPPORTIVE`;
- `SECONDARY_ROBUSTNESS`.

Give main-text space primarily to the first two.

## 16B.9 Compression after completeness

Run:

`LOGICAL COMPLETENESS -> PARAGRAPH ASSEMBLY -> BOUNDARY AUDIT -> NARRATIVE COMPRESSION`

Compression may:
- merge same-destination paragraphs;
- delete duplicate roadmaps;
- relocate repeated boundaries;
- demote secondary robustness;
- preserve or expand decisive future tests.

Compression must reduce redundancy, not scientific evidence.



# 16C. Genre-Conditional Claim & Novelty Engine — Phase 3B-3

Before drafting a title, abstract, contribution sentence, Discussion close, or translational claim, route by **genre**.

Cross-corpus observation:
only **8/343 positive sentence units (2.3%)** contain strict explicit novelty cues such as `novel`, `first study`, `new insight/evidence`, `unique value`, or `emerging role`.

Operational rule:

> **Show novelty structurally before naming it lexically.**

Use:
`PRIOR LIMIT -> NEW OPERATION -> NEW EVIDENCE/LOGIC -> WHAT CHANGES -> BOUNDARY`

## 16C.1 Novelty Budget

Assign one primary novelty type:
- `EMPIRICAL_NOVELTY`
- `INFERENTIAL_NOVELTY`
- `MECHANISTIC_NOVELTY`
- `INTEGRATIVE_NOVELTY`
- `FRAMEWORK_NOVELTY`
- `TRANSLATIONAL_NOVELTY`

Allow zero to two secondary types.

Do not choose the novelty type by prestige. Choose it by the evidence level and what the manuscript actually changes.

## 16C.2 Genre contribution routing

### ORIGINAL_RESEARCH
Primary contribution: empirical/validation/integration.
Novelty should emerge from the evidence chain.
Do not use review-level synthesis to compensate for weak direct results.

### MR_GENETIC_EPIDEMIOLOGY
Primary contribution: inferential.
The novelty is causal direction/prioritization under MR assumptions.
Mechanism remains a next test unless E4 evidence exists.

### LETTER_MR
Primary contribution: compressed refinement of a specific published question.
The title + opening paragraph act as a mini-abstract.

### REVIEW
Primary contribution: integrative synthesis.
A review is not novel merely because it covers a recent topic.

### CRITICAL_REVIEW
Primary contribution: evidence adjudication.
State what is supported, what is not, and what evidence would change the conclusion.

### REVIEW_PERSPECTIVE
Primary contribution: thesis + synthesis.

### PERSPECTIVE_COMMENTARY
Primary contribution: reframing/actionable framework.
The empirical evidence establishes the problem; the framework is the intellectual contribution.

## 16C.3 Title aggressiveness

Use a 0–3 ladder:
- 0 neutral;
- 1 descriptive/scope/method;
- 2 cautious interpretive/causal thesis;
- 3 definitive empirical/clinical claim.

Default Q1 target:
- E1/E2 Original Research: 1–2;
- MR: 1–2 with method/evidence labeling;
- Review: usually 1;
- Perspective: 1–2;
- E4/E5 may justify stronger titles.

## 16C.4 Abstract landing

Route by genre.

Original Research:
`GAP -> METHODS -> CORE RESULTS -> VALIDATION/BOUNDARY -> BOUNDED CONTRIBUTION`

MR:
`CAUSAL GAP -> DESIGN -> EFFECT -> ROBUSTNESS/REVERSE -> BOUNDED CAUSAL INFERENCE`

Review:
`PROBLEM/THESIS -> SYNTHESIS -> MODEL -> OPPORTUNITY -> BARRIER -> FUTURE`

Critical Review:
`TENSION -> EVIDENCE HIERARCHY -> CAUSAL/INTERVENTION BOUNDARY -> PRACTICAL INTERPRETATION -> AGENDA`

Perspective/Letter:
if no abstract, title + opening paragraph must perform the abstract's argumentative work.

## 16C.5 Abstract Result Budget

Prioritize:
`CENTRAL RESULT + ORTHOGONAL/EXTERNAL VALIDATION + BOUNDARY-CHANGING RESULT`.

Do not list every sensitivity analysis in the abstract.

## 16C.6 Review thesis test

Remove `this review summarizes...`.

If no substantive thesis remains, reconstruct the abstract/introduction around:
- what current models miss;
- the organizing lens;
- the central contradiction;
- the translational bottleneck.

## 16C.7 Misrouting guard

Before finalizing, ask:
`Would this sentence/paragraph still be appropriate if the manuscript were a different genre?`

If yes because it is generic, strengthen genre specificity.
If no because it violates the current genre's evidence rules, reroute.



# 16D. Evidence-Citation Choreography & Cohesion Engine — Phase 3B-4

Citation behavior is routed by **evidence ownership**, not citation density.

## 16D.1 Evidence ownership

Label each sentence:
- `KNOWN_FIELD`
- `PRIOR_STUDY`
- `PRESENT_STUDY`
- `AUTHOR_INTERPRETATION`
- `AUTHOR_FRAMEWORK`
- `UNRESOLVED_QUESTION`

Never allow ownership to remain ambiguous in a key Discussion/Review sentence.

## 16D.2 Data-paper choreography

Preferred Discussion sequence:

`PRESENT RESULT -> PRIOR LITERATURE -> AGREEMENT/CONFLICT -> AUTHOR INTERPRETATION -> [BOUNDARY]`

Do not attach a citation to the present result merely to make it look more scholarly.

## 16D.3 MR choreography

`MR SIGNAL -> PRIOR BIOLOGY -> PLAUSIBLE MECHANISM -> BOUNDED CAUSAL INTERPRETATION -> NEXT TEST`

Prior mechanistic citations contextualize E3 evidence; they do not upgrade it to E4.

## 16D.4 Review choreography

`SYNTHESIS CLAIM -> EVIDENCE CLUSTER -> HIERARCHY/CONTRADICTION -> AUTHOR SYNTHESIS`

Avoid paper-by-paper narration unless differences between studies are analytically important.

## 16D.5 Perspective choreography

`ACCEPTED GUIDANCE -> EMPIRICAL PROBLEM EVIDENCE -> AUTHOR DIAGNOSIS -> FRAMEWORK -> IMPLEMENTATION EXAMPLES -> PRINCIPLE`

The framework must remain visibly author-owned.

## 16D.6 Citation placement

In the curated positive sentence library, approximately **90.3% of detected cited sentences** use sentence-final/end-attached citations.

Default:
`PROPOSITION -> CITATION`

Use integrated author attribution when the identity/design of the prior study matters.

## 16D.7 Concept-chain cohesion

Approximately **63.0%** of positive sentence units begin through lexical/topic anchoring rather than an explicit discourse cue.

Default:
`CONCEPT ECHO > CONNECTOR`

Use `This/These/Such` only when the antecedent is unambiguous.

## 16D.8 Citation stacking

Use compact clusters for convergent evidence.
Use named paper-by-paper attribution for contradiction, methodological difference, population difference, or evidence hierarchy.

## 16D.9 Citation omission test

Interpretation/framework/future sentences do not automatically require citation if they are clearly presented as author reasoning derived from the current evidence.

Do cite external facts, precedents, mechanisms, guidelines, instruments, and prior empirical claims.

## 16D.10 Q1 evidence firewall

A citation cannot upgrade the evidence tier of the current study.

Split:
`PRIOR MECHANISTIC FACT`
from
`PRESENT ASSOCIATION/CAUSAL-INFERENCE RESULT`
from
`PROPOSED RELATIONSHIP`.



# 16E. Methods & Results Evidence Reporting Engine — Phase 3C

Methods and Results are mirror sections:

`METHODS = RECONSTRUCT THE ANALYSIS`
`RESULTS = RECONSTRUCT THE EVIDENCE`

## 16E.1 General Methods order

`DESIGN -> SOURCE -> ELIGIBILITY/UNIT -> PREPROCESSING -> PRIMARY ANALYSIS -> UNCERTAINTY/MULTIPLICITY -> ROBUSTNESS/VALIDATION -> REPRODUCIBILITY PARAMETERS -> ETHICS/ACCESS`

Do not force these into separate subsections if compression improves readability.

## 16E.2 Reproducibility-preserving compression

Delete duplicate navigation before reproducibility-critical detail.

Preserve:
- denominator;
- analysis unit;
- threshold/cutoff;
- effect scale;
- model/covariates;
- multiplicity;
- validation definition;
- material software/version/seed/iteration settings.

## 16E.3 Effect-first Results

Default:
`DIRECTION/MAGNITUDE -> UNCERTAINTY -> P/q/FDR -> FIGURE/TABLE`

`significant` is not a substitute for effect size.

## 16E.4 Screen/exemplar allocator

For high-dimensional data:
`SCREEN -> N SIGNALS -> 1–3 EXEMPLARS -> REMAINDER COMPRESSED -> VALIDATION/BOUNDARY`.

## 16E.5 Validation taxonomy

Never collapse:
- independent replication;
- orthogonal triangulation;
- release/model/prior robustness;
- assumption diagnostics;
- directional concordance;
- null non-replication.

## 16E.6 Null compiler

Use:
`QUESTION -> ESTIMATE/CI -> INFERENTIAL STATUS -> EVIDENCE CEILING`.

A non-significant P value does not establish no effect.

## 16E.7 Results interpretation budget

Allow one short boundary in Results when it prevents immediate misclassification:
- directionally concordant but imprecise;
- robustness but not independent replication;
- discovery signal but not validated clinical utility.

Mechanistic explanations and literature comparison belong mainly in Discussion.

## 16E.8 Methods-Results mirror audit

Every central Result must map to:
`SOURCE -> UNIT -> MODEL/TEST -> MULTIPLICITY -> VALIDATION CLASS`.

Repair Methods if the chain is missing.

## 16E.9 Review Methods provenance boundary

Do not invent systematic-review machinery **or narrative-review methodology**.

Hard:

> **EDITORIAL PROCESS != AUTHOR REVIEW METHOD**

If a narrative review has no Methods/search-strategy section in the source, default to:
`KEEP NO METHODS SECTION`.

Do not convert the Skill's own:
- source verification;
- web searching;
- citation audit;
- evidence-tier labeling;
- claim adjudication;
- targeted updating during editing;

into author methodology.

A Review Methods/Search Strategy section may be added only when:
1. the authors provide the factual process; or
2. the target journal requires it and the missing factual process is obtained and confirmed.

If the manuscript claims a systematic/scoping review, require the corresponding real methodology.



# 16F. Statistical Sentence Micro-architecture + Figure/Table Narrative Engine — Phase 3C-2

The main Results clause states the scientific proposition.
The statistical packet supplies evidence coordinates.

Default:
`PROPOSITION -> (EFFECT; 95% CI; P/q) -> FIGURE/TABLE`

## 16F.1 Statistical packet

In the CBX8 paired Final calibration, 25 multi-metric Results sentences were detected.
All (100.0%) packaged their multi-metric evidence in parentheses, and 92.0% used semicolons for compact metric separation.

Use this as a descriptive signal, not a punctuation quota.

## 16F.2 Sentence Load Gate

One sentence may carry several numbers but should usually carry one dominant scientific claim.

Decision:
`KEEP ONE PACKET / PARALLEL STACK / SPLIT / MOVE TO TABLE`.

Split when:
- >3 heterogeneous comparisons;
- different analysis populations are mixed;
- a mechanism/clinical implication is added to a statistical result;
- the sentence becomes a substitute for a table.

## 16F.3 Results heading ladder

`METHOD LABEL < TOPIC LABEL < ANSWER-ORIENTED < BOUNDED ANSWER`

Use the strongest level directly supported by the subsection.

Diagnostics may retain method labels.
Primary evidence modules should prefer answer-oriented headings when evidence is stable.

## 16F.4 Subsection opening

Choose:
- denominator-first;
- question-to-answer;
- screen-first;
- validation-first.

Do not re-run a Methods tutorial at the start of Results.

## 16F.5 Subsection landing

End on:
`ROBUST OBSERVATION / VALIDATION STATUS / EVIDENCE BOUNDARY / BRIDGE`.

Do not end on a raw P value, figure number, or minor sensitivity.

## 16F.6 Figure/Table hierarchy

`PROSE = EVIDENCE HIERARCHY`
`LEGEND = DISPLAY MAP`
`TABLE = EXACT COMPARABLE VALUES`
`SUPPLEMENT = EXHAUSTIVENESS`

A boundary-changing negative result must remain visible in main text.

## 16F.7 Orthogonal redundancy

Legends should be independently interpretable, so limited redundancy is acceptable.

Prose tells **what the result means**.
Legend tells **what is displayed and how**.

Do not duplicate a full Results paragraph in the legend.

## 16F.8 Statistical grammar by design

Use design-specific packets:
- group comparison: `difference/effect -> CI -> P/q`;
- survival: `n/events -> HR -> CI -> P`;
- correlation/regression: `rho/beta -> CI -> q/P`;
- screen: `K of M -> exemplars -> correction`;
- colocalization: `variant set -> posterior -> prior/model -> boundary`;
- fine-mapping: `PIP -> credible set -> model/LD boundary`.

## 16F.9 Validation/null grammar

The evidence classification belongs in the main clause:
- `directionally concordant but imprecise`;
- `did not replicate/generalize`;
- `model robustness rather than independent replication`;
- `did not provide evidence for`.

Statistics support the label; they do not replace it.



# 16G. Global Manuscript Orchestration Engine — Phase 3D-0

A manuscript must have one scientific spine across sections.

Use a `Claim Ledger` before final prose polishing.

For each major claim track:
`EVIDENCE TIER -> DIRECT SUPPORT -> BOUNDARY -> TITLE -> ABSTRACT -> RESULTS -> DISCUSSION DELTA -> CONCLUSION -> FUTURE TEST`.

## 16G.1 Claim propagation

The same central claim may appear in several sections only if its function changes.

`SAME CLAIM + NEW FUNCTION = LEGITIMATE PROPAGATION`
`SAME CLAIM + SAME FUNCTION = REDUNDANCY`

## 16G.2 Interpretive Delta

A Discussion restatement of a Result must add at least one:
`LITERATURE / MECHANISM PLAUSIBILITY / CONTRADICTION / HIERARCHY / BOUNDARY / IMPLICATION / NEXT TEST`.

No delta -> merge/delete.

## 16G.3 Boundary inheritance

A material negative/null/failed-validation result must retain its consequence across Abstract, Discussion, Conclusion and, when material, Title.

The wording may compress; the evidence ceiling may not disappear.

## 16G.4 Section contracts

- Introduction creates the research contract.
- Methods makes the analysis reconstructable.
- Results answers the contract with evidence.
- Discussion adds interpretation.
- Conclusion compresses the adjudicated claim.
- Figure/Table/Supplement carry display/exactness/exhaustiveness.
- Future resolves identified uncertainty.

## 16G.5 Terminology lock

Lock:
`ENTITY / UNIT / DIRECTION / EVIDENCE CLASS / THRESHOLD CLASS / CAUSAL LANGUAGE`.

Do not use synonyms that change scientific identity or validation status.

## 16G.6 Claim strength lattice

Scientific:
`SCOPE -> DESCRIPTIVE -> ASSOCIATIONAL -> CAUSAL-INFERENCE -> DIRECT MECHANISM -> CLINICAL UTILITY`.

No section may silently climb without evidence.

Perspective/normative writing follows a separate framework branch.

## 16G.7 Global negative-evidence propagation

`RESULTS -> DISCUSSION BOUNDARY -> ABSTRACT/CONCLUSION -> [TITLE IF MATERIAL]`.

Do not quarantine claim-changing evidence in Supplement.

## 16G.8 Future inheritance

Every major Future item should trace to a real unresolved boundary:
`UNKNOWN -> TEST -> MODEL/COHORT -> READOUT -> DECISION`.



# 16H. Reviewer-Resistance & Objection Anticipation Engine — Phase 3D-0B

Do not write a defensive manuscript.
Write a manuscript that recognizes its material evidence risks before the reviewer does.

## 16H.1 Three boundary levels

- `LOCAL_FIREWALL`: prevent immediate evidence misclassification.
- `SECTION_CEILING`: state the strongest defensible inference for a module.
- `GLOBAL_LIMITATION`: constrain manuscript-wide validity/generalizability.

## 16H.2 Reviewer risk classes

Classify:
`POWER_PRECISION / GENERALIZABILITY / CAUSALITY_BIAS / TRANSLATION_UTILITY / MEASUREMENT_DESIGN_HETEROGENEITY / EVIDENCE_ADEQUACY / MODEL_REPRODUCIBILITY / SAFETY_IMPLEMENTATION / CURRENT_STANDARD_LIMIT`.

Do not use generic limitation prose when a precise class is identifiable.

## 16H.3 Risk routing

Place the objection where it first changes reader interpretation:
- Results for immediate evidence class;
- Discussion for inference/generalizability;
- Methods for reproducibility/design specification;
- Critical View for evidence hierarchy;
- Future for the resolving design.

## 16H.4 Objection response compiler

Use:
`RISK SOURCE -> INFERENTIAL CONSEQUENCE -> CLAIM DOWNGRADE/BOUNDARY -> [RESOLVING TEST]`.

## 16H.5 Defensive-writing governor

If caveats repeat:
`CALIBRATE VERBS -> KEEP FIRST MATERIAL FIREWALL -> CONSOLIDATE GLOBAL LIMITATIONS -> BUILD ACTIONABLE FUTURE`.

## 16H.6 Contradiction resolution

`EXACT CONFLICT -> LIKELY SOURCE -> DISCRIMINATING TEST`.

A contradiction without adjudication is an unfinished reviewer response.

## 16H.7 Reviewer Stress Test

Before final polish identify the top five objections that could:
- change claim class;
- undermine replication/generalizability;
- expose design/reproducibility ambiguity;
- reveal mechanism/clinical overclaim.

Each must be:
`RESOLVED / BOUNDED / LINKED TO DECISIVE FUTURE TEST`.


# 16I. Figure, Layout & Submission Production Engine — Phase 3D-0C

Figures are part of the argument, not post-hoc decoration.

## 16I.1 Two figure modes

- `QITENG_FIGURE_NATIVE`: close to observed Teng Qi visual organization.
- `QITENG_FIGURE_Q1_GUARDED` — default: preserve logic while upgrading legibility, accessibility, vector/source traceability and journal compliance.

## 16I.2 Figure role router

Classify each main figure as:
`STATISTICAL_EVIDENCE / STUDY_DESIGN / COMPACT_LETTER_SUMMARY / MECHANISTIC_SYNTHESIS / COMPARATIVE_TECHNOLOGY_SYNTHESIS / TRANSLATIONAL_PATHWAY / ROBUSTNESS_DIAGNOSTIC / MULTILAYER_EVIDENCE`.

One main figure should have one dominant scientific job.

## 16I.3 Panel argument order

Prefer:
`ORIENTATION -> PRIMARY EVIDENCE -> VALIDATION/ROBUSTNESS -> BOUNDARY`.

Panel order should be readable as an evidence sequence.

## 16I.4 Figure Claim Gate

`VISUAL CLAIM <= TEXTUAL EVIDENCE CLAIM`.

Check:
- figure title;
- arrow direction;
- internal labels;
- `replicated/validated/causal/therapeutic` words;
- color/line semantics.

## 16I.5 Caption engine

`FIGURE PURPOSE -> PANEL MAP -> n/UNIT -> TEST/ERROR/MULTIPLICITY -> ABBREVIATIONS -> DISPLAY-SPECIFIC BOUNDARY`.

Prose tells meaning; legend tells display/how.

## 16I.6 Editable master

Keep:
- vector/editable master for plots/schematics;
- native raster originals;
- panel sources;
- source data;
- plotting code;
- assembled figure master.

Submission export is a derivative, never the only source.

## 16I.7 Journal Compliance Router

Before final export, retrieve the current official target-journal instructions and record:
`WIDTH / DPI / FILE TYPE / COLOR MODE / FONT / PANEL LABEL / LEGEND PLACEMENT / SUPPLEMENT RULES / INITIAL-vs-FINAL SUBMISSION`.

Publisher-level profiles are only defaults; journal instructions override.

## 16I.8 Submission Production Gate

Run S01-S22 before upload.
Critical failures block submission.

Observed CBX8 package structure may inform file separation, but observed 144-dpi TIFF metadata must not be learned as a technical target.



# 16J. Dry-Run Reliability & Operational State Engine — Phase 3D-1

This module is based on an out-of-corpus operational dry run.

## 16J.1 Test Mode Gate

Classify:
- `TRUE_BLIND`
- `CLEAN_INPUT_DRY_RUN`
- `OPERATIONAL_DRY_RUN`

Historical QC, Claim-Evidence matrices, prior Final/reference packages or reviewer records make the run non-blind unless isolated.

Never claim blind accuracy after contamination.

## 16J.2 No-Change Gate

Before rewriting:
`MATERIAL SCIENTIFIC/LOGICAL IMPROVEMENT?`

If no:
`KEEP`.

Do not manufacture edits in an already mature section.

## 16J.3 Reproducibility Contribution Gate

If reproducibility is part of the paper's contribution:
- preserve inferential reproducibility;
- compress implementation engineering details first.

## 16J.4 Project Archive vs Submission Package

Project archive retains source data/code/masters.
Submission package contains target-journal-required files only.

Traceability is mandatory; portal over-upload is not.

## 16J.5 Post-Submission State Gate

If already submitted/in screening/under review:
generated edits are `REVISION CANDIDATE ONLY`.

Do not imply that upload files should be replaced unless a permitted correction/revision is needed.

## 16J.6 Historical QC comparison

Freeze primary conclusions before historical-QC comparison when possible.
If contamination occurs earlier, disclose it.

## 16J.7 Cost/Page Budget

Journal page/figure charges belong to production planning, not scientific claim grading.

## 16J.8 Patch discipline

Only observed dry-run or blind-test failures may create new core rules.
A passed module should not be made more complicated merely because another example is available.



# 16K. Cross-Dataset Identity & Publication Interface Engine — Phase 3D-1B

## 16K.1 Replication Object Gate

Always name the object that replicates:
`IDENTITY / PROGRAM / EFFECT / DIRECTION / ROBUSTNESS`.

`PROGRAM_REPLICATION != IDENTITY_REPLICATION`.

If an external cohort uses a source-label or proxy analog, state the analog explicitly in Abstract, Results and Conclusion.

## 16K.2 Biological Unit Salience

In single-cell/spatial/repeated-measure manuscripts, technical N cannot substitute for biological N.

If cells/spots/reads are foregrounded in a headline result, pair them with donor/patient/sample/pseudobulk denominators at the same decision point.

## 16K.3 Publication Interface Sanitization

Keep scientific governance:
`prespecified / frozen before outcome / checksum / deterministic / independent reimplementation`.

Remove or relocate internal release vocabulary:
`Gate C8B / preflight / canonical state / outcome unlock / superseded manuscript chronology`.

The manuscript explains trustworthiness; the repository records internal release history.


# 16L. Serial Human-Edit Trajectory Engine — Phase 3F-0

This module is calibrated from five chronological Teng Qi-edited versions of the same Review manuscript.

The user states that the writing revisions were independently completed by Teng Qi.
Do not author-weight Track Changes or comments.

## 16L.1 Non-monotonic revision

`GOOD EDITING != MONOTONIC SHORTENING`.

A mature revision may expand to:
- establish a unifying thesis;
- create missing mechanistic sections;
- make evidence boundaries visible;
- convert generic headings into relation/micro-thesis headings.

Compression remains local and purpose-driven.

## 16L.2 Hierarchy-reopenable workflow

Editing is not a one-way funnel.

Use:
`DIAGNOSE HIGHEST-ORDER DEFECT -> REOPEN REQUIRED LAYER -> REBUILD -> STABILIZE -> COMPRESS -> PRECISION -> SYNCHRONIZE`.

If a late comment reveals a structural problem, reopen architecture even after prose polish.

## 16L.3 Review Thesis Ratchet

Prefer:
`UNIFYING THESIS -> SCOPE MAP`

over:
`This review summarizes A/B/C`

when the evidence supports a substantive synthesis.

## 16L.4 Heading Maturation

Headings may evolve:
`TOPIC -> FUNCTION -> RELATION/MICRO-THESIS -> EVIDENCE BOUNDARY`.

Examples of jobs:
- reciprocal relationship;
- upstream/downstream mechanism;
- causal/associational boundary;
- emerging evidence / knowledge gap.

Hard:
`HEADING CLAIM <= SECTION EVIDENCE CLAIM`.

Do not optimize heading word count.

## 16L.5 Section Function Refactor

Generic `Discussion` is not mandatory in Reviews, but visible subdivision is **not** a default improvement.

For a narrative review whose source Discussion is continuous:
`KEEP CONTINUOUS DISCUSSION`
unless the author or target journal supports visible subheadings, or readability clearly fails and the author approves the change.

Internal jobs may still be mapped as:
`synthesis + contradiction + translation + limitation + future agenda`.

Hard:

> **HIDDEN FUNCTION MAP != VISIBLE HEADING MAP**

Section labels follow author/journal surface conventions as well as section job.

## 16L.6 Narrative Budget

Allocate words by:
- thesis importance;
- evidence complexity;
- contradiction/boundary burden;
- translational decision value.

Do not impose a whole-manuscript compression percentage.

## 16L.7 Late Title Semantic Compression

Compress scaffold-heavy titles after architecture stabilizes.
Preserve evidence class.

## 16L.8 Biomedical Nomenclature Lock

Check:
`SPECIES -> GENE SYMBOL -> GENE/PROTEIN TYPE -> ITALIC/ROMAN -> CAPITALIZATION -> ABBREVIATION`.

Use authoritative nomenclature resources when verification is needed.

## 16L.9 Comment Closure Gate

Final clean manuscripts should contain no unintended unresolved comments or Track Changes.

A reply such as `fixed` does not count as closure until the underlying manuscript/figure/reference is verified.

## 16L.10 Late-Revision Synchronization Gate — Q1 Guard

If late revision changes:
- title;
- primary thesis;
- level-1 section architecture;
- translational position;
- evidence ceiling;

then re-audit:

`TITLE <-> ABSTRACT <-> KEYWORDS <-> INTRO THESIS <-> HEADINGS <-> CONCLUSION`.

This gate is mandatory in `QITENG_Q1_GUARDED`.

## 16L.11 Serial edit operation vocabulary

Classify:
`KEEP / MICRO_POLISH / REWRITE_SAME_JOB / REFRAME / EXPAND / COMPRESS / INSERT / DELETE / MOVE / SPLIT_SECTION / MERGE_SECTION / RENAME_HEADING / RESYNC_HIGH_LEVEL`.

Learn an operation only when its reader-state/evidence job is identifiable.



# 16M. Genesis-to-Final Revision Compiler — Phase 3F-1

This module is calibrated from a six-stage chronological Review sequence beginning with a clean original draft.

## 16M.1 Evidence Floor Gate

Before compression, ask whether the manuscript has enough representative evidence to support synthesis.

If evidence is thin:
`BUILD EVIDENCE -> MAP MECHANISM -> VERIFY CLAIM SUPPORT`.

Hard:
`EVIDENCE-POOR + CONCISE != MATURE`.

## 16M.2 Scaffold-Preserving Densification

If the raw scaffold is viable:
`KEEP -> EXPAND UNDER-SUPPORTED UNITS -> INSERT EVIDENCE BRIDGES`.

Do not rebuild every section merely because the draft is early.

## 16M.3 Evidence Reservoir / Narrative Evidence Set

Separate:
- `EVIDENCE_RESERVOIR`: broad project literature/evidence inventory;
- `NARRATIVE_EVIDENCE_SET`: representative studies emphasized in manuscript prose.

Hard:
`CITATION DENSITY != EVIDENCE QUALITY`.

But also:

> **REFERENCE MINIMALISM IS NOT A QUALITY TARGET.**

Narrative-review references serve direct support **and** field coverage, landmark attribution, historical continuity, contradiction mapping and positioning.

Default:
`PRESERVE REFERENCES`.

A large reduction (>20% or >10 references) is a `REFERENCE_COVERAGE_REVIEW` trigger.
Every material deletion batch requires a reason/coverage ledger.
Do not prune a broad narrative review merely to create a minimal evidence set.

## 16M.4 Claim Reset Gate

After evidence acquisition, recompute claims from zero:

`EVIDENCE TYPE -> DIRECTNESS -> CONSISTENCY -> MODEL/POPULATION -> CLAIM TIER -> BOUNDARY`.

Hard:
`EVIDENCE ACQUISITION != CLAIM ESCALATION`.

New evidence can strengthen, narrow, redirect, contradict or downgrade the prior claim.

## 16M.5 Body-First Interface Compilation

Treat Title, Abstract, Keywords, high-level headings and Conclusion as interfaces compiled from the final body argument.

Preferred workflow:
`BODY EVIDENCE -> BODY ARCHITECTURE -> CLAIM RESET -> INTERFACE COMPILE`.

This is sequencing, not permission to neglect the Abstract.

After any late structural change, run the Late-Revision Synchronization Gate.

## 16M.6 Figure Revision Sequence

Use:
`SCIENCE MAP -> MECHANISM RESOLUTION -> NOMENCLATURE -> FUNCTIONAL ENDPOINTS -> LEGEND CLOSURE -> LAYOUT/LEGIBILITY -> FREEZE`.

### Scientific Error Override
Scientific mapping errors override figure freeze.
Wrong arrow direction/pathway/entity/sign must be corrected immediately.

## 16M.7 Figure-Text Mechanism Parity

If a distinction is central to the text and the schematic claims to summarize that mechanism, encode it when necessary to understand the figure.

Examples:
`DIRECT/INDIRECT`
`ACTIVATING/INHIBITORY`
`RAPID/SLOW`
`NEURAL/HUMORAL`
`DISCOVERY/VALIDATION`
`ASSOCIATION/CAUSAL`.

Do not overload the figure with nonessential prose details.

## 16M.8 Functional Endpoint Specificity

When physiological output is the point:
`ORGAN -> FUNCTION`
is preferable to an unlabeled organ icon alone.

## 16M.9 Figure Panel-Job Maturation

Panel labels may evolve:
`TOPIC -> PROCESS/FUNCTION -> RELATION -> EVIDENCE BOUNDARY`.

Hard:
`PANEL CLAIM <= PANEL EVIDENCE`.

## 16M.10 Figure Nomenclature Lock

The Biomedical Nomenclature Lock applies to text, legends, figure labels and graphical abstracts equally.

A scientifically correct body with an incorrect figure label still fails release.

## 16M.11 Genesis workflow router

`GENESIS TRIAGE`
-> `SCAFFOLD-PRESERVING DENSIFICATION`
-> `LOCAL SEMANTIC PRECISION`
-> `CLAIM RESET`
-> `ARCHITECTURE REBUILD`
-> `EVIDENCE CURATION`
-> `STABILIZE`
-> `SEMANTIC COMPRESSION`
-> `ARGUMENT-LABEL MATURATION`
-> `FINAL INTERFACE RECOMPILE`.

This is not a fixed number of human revision rounds.
Route by manuscript state.



# 16N. Edit Decision Router & Cross-Corpus Generalization — Phase 3F-2

## 16N.1 Revision Magnitude Triangulation

Hard:
`EDIT MAGNITUDE != WORD-COUNT DELTA`.

Estimate revision magnitude using:
`WORD DELTA + SEMANTIC PRESERVATION + OPERATION MIX + SECTION/HEADING CHANGE`.

A near-zero word delta can still be a reconstruction.

## 16N.2 State-Conditioned Operation Selection

Choose operation only after manuscript state is known.

- EVIDENCE_BUILD: KEEP viable scaffold + EXPAND/INSERT.
- LOCAL_PRECISION: KEEP + MICRO_POLISH.
- MACRO_REWRITE: DELETE/INSERT/REPLACE/REFRAME may dominate.
- STABILIZATION: KEEP dominates.
- LATE_MATURATION: KEEP + heading/function edits.

Do not learn a global “delete more” or “expand more” preference.

## 16N.3 Review Architecture Spectrum

Review subtype determines architecture.

### NARRATIVE / EDUCATIONAL
May be `SCOPE_LED` or `SYNTHESIS_LED`.

### MECHANISTIC / TRANSLATIONAL
Prefer `THESIS_LED`.

### REVIEW / PERSPECTIVE
Prefer `THESIS_LED + CENTRAL ARGUMENT`.

### CRITICAL REVIEW
Prefer:
`QUESTION_LED_CRITICAL`
or
`THESIS_FRAMEWORK_LED`.

The Review Thesis Test is therefore conditional.

## 16N.4 Discussion Boundary

Hard:
`GENERIC DISCUSSION IS OPTIONAL, NOT PROHIBITED`.

Published Teng Qi reviews include both Discussion and non-Discussion terminal architectures.

For narrative reviews, visible Discussion subheadings are **not** automatically preferred.
Preserve the source/author surface when it is already coherent.

Choose from:
`AUTHOR STYLE + TARGET JOURNAL + REVIEW SUBTYPE + SECTION JOB`.

Internal planning structure does not have to be exposed as headings.

## 16N.5 Feedback Assimilation Gate

Separate:
`TRIGGER PROVENANCE`
from
`EDIT EXECUTION`.

Learn:
`UNDERLYING DEFECT -> ACCEPTED EDIT -> WHY IT WORKED`.

Do not automatically learn the commenter’s prescription as QiTeng style.

Feedback classes:
- SCIENTIFIC_SAFETY
- EDITORIAL_QA
- JOURNAL_OVERLAY
- PROJECT_SPECIFIC.

Journal-specific requests remain overlays unless cross-corpus evidence supports generalization.

## 16N.6 Source-Interpretation Feedback

If feedback identifies source misreading:
`VERIFY SOURCE -> COMPARE CLAIM -> REWRITE/DELETE/RELOCATE -> RECHECK DOWNSTREAM CLAIMS`.

Hedging alone does not repair a wrong source interpretation.

## 16N.7 Reporting Verb Economy

Explicit `studies have shown/found/revealed...` framing is uncommon in the curated positive sentence corpus.

Prefer direct propositions when ownership is clear.

Do not ban reporting frames when attribution itself is informative.

## 16N.8 Evidence Provenance for Skill Learning

Tag candidate rules:
- SERIAL_DIRECT
- TRACKED_DIRECT
- CROSS_CORPUS_FINAL_STATE
- CROSS_CORPUS_CONTRADICTION
- INFERENCE_ONLY.

A published final can support mature-state patterns but cannot prove the edit sequence that produced them.

## 16N.9 Decision Learning Confidence

GOLD:
- direct tracked operation;
- high-confidence aligned pair;
- explicit INSERT/DELETE/heading change;
- verified feedback closure.

SILVER:
- plausible serial alignment with weaker directness.

DO NOT LEARN:
- administrative metadata;
- orphan reference tokens;
- Track Changes parsing noise;
- ambiguous low-similarity pairings.

Core formula:

`STATE FIRST -> DEFECT -> OPERATION -> CLOSURE`

and:

`LEARN THE DEFECT-SOLUTION RELATION, NOT THE SURFACE EDIT`.


# 16O. Content Lineage & Trajectory Survival — Phase 3F-3

## 16O.1 Paragraph Fate != Content Fate

Hard:
`DELETE PARAGRAPH != DELETE CLAIM`
and
`INSERT PARAGRAPH != NEW SCIENTIFIC IDEA`.

Macro rewrites may decompose, recompose, relocate or reframe prior scientific content.

## 16O.2 Event / Pair / Lineage Separation

Store separately:

### EDIT EVENT
INSERT / DELETE / MOVE / HEADING / SECTION operations.

### TRANSFORMATION PAIR
High-confidence old -> new same-job or clearly related mappings.

### CONTENT LINEAGE
Scientific-content fate across many-to-many reconstruction.

Do not force a transformation pair when only the event is certain.

## 16O.3 Dual Confidence

Record:
`EVENT_CONFIDENCE`
and
`LINEAGE/PAIR_CONFIDENCE`
separately.

A DELETE event can be certain while its scientific destination remains uncertain.

## 16O.4 Object-Type Gate

Before edit learning classify:
`TITLE / ABSTRACT / HEADING / BODY / LEGEND / TABLE / CITATION TOKEN / ADMIN`.

Do not:
- train heading changes as prose sentence edits;
- learn orphan reference tokens;
- learn funding metadata as writing style.

## 16O.5 Trajectory Survival Gate

Intermediate human edits have two possible learning roles:

### PROCESS_STRATEGY
Useful for stage routing even if later superseded.

### FINAL_STYLE
Stronger when wording/architecture survives into late/final versions.

Hard:
`LOW FINAL SURVIVAL != BAD EDIT`.

But:
`LOW FINAL SURVIVAL != STRONG FINAL-STYLE TEMPLATE`.

## 16O.6 Downstream-Survival Weighting

Use:
- EXACT/NEAR FINAL -> strong final-style evidence
- HIGH SURVIVAL -> strong final-style evidence
- PARTIAL -> transitional/recomposed
- LOW -> primarily process-strategy unless independently validated

Thresholds are calibration aids, not universal language targets.

## 16O.7 Many-to-Many Rewrite Gate

If:
`OLD A + OLD B -> NEW 1 + NEW 2 + FIGURE`,
record content lineage rather than fabricated one-to-one pairs.

## 16O.8 Hard-Negative Calibration

The Skill must learn tempting but wrong actions.

Examples:
- compressing evidence-poor drafts;
- rewriting stable mature prose;
- treating word delta as revision magnitude;
- treating paragraph deletion as claim deletion;
- universalizing journal feedback;
- fixing source misinterpretation with hedging;
- learning transient intermediate wording as final style.

Hard:
`MORE ELEGANT != BETTER EDIT`
unless the edit improves the correct reader/evidence state.

## 16O.9 Adjudication Compiler

`OBJECT TYPE`
-> `REVISION STATE`
-> `DEFECT`
-> `EVENT`
-> `CONTENT LINEAGE`
-> `PAIR CONFIDENCE`
-> `FINAL SURVIVAL`
-> `LEARNING SCOPE`
-> `CLOSURE`.

Core formula:

`TRACK SCIENTIFIC CONTENT, NOT JUST DOCUMENT BLOCKS`.



# 16P. Quantitative Identity Integrity & MR Calibration — Phase 3G-0A

## 16P.1 Effect-Scale Integrity Gate

For every quantitative effect packet:

`ESTIMATE SCALE == CI SCALE == TABLE/AXIS LABEL SCALE`.

### Ratio scales
For:
- OR
- HR
- RR

the estimate and confidence interval must be strictly positive.

If an OR/HR/RR packet contains a negative interval endpoint:

`BLOCK`
-> inspect raw output
-> determine beta/log-ratio vs exponentiated-ratio scale
-> transform estimate and CI together
-> regenerate text/table/figure.

Hard:

> **EFFECT-SCALE MISMATCH IS A DATA-REPORTING ERROR, NOT A LANGUAGE ERROR.**

## 16P.2 Signal Identity Lock

For multi-exposure/multi-outcome analyses define:

`SIGNAL_ID = EXPOSURE_ID + OUTCOME_ID + DIRECTION + ESTIMATOR + EFFECT_SCALE + DATASET`.

Carry the same identity through:
- Results
- Figure/Table
- Discussion
- Abstract
- Conclusion.

Before freeze, run a checksum.

Hard:

> **ENDPOINT DRIFT ACROSS SECTIONS = BLOCK.**

## 16P.3 Estimator Concordance != Replication

Alternative estimators and diagnostics:
- weighted median
- MR-Egger
- simple/weighted mode
- Cochran Q
- Egger intercept
- MR-PRESSO
- leave-one-out

are robustness/diagnostic evidence unless they use genuinely independent data.

Do not call them:
- independent validation
- replication
- external confirmation.

## 16P.4 Multiplicity in High-Dimensional Causal Screens

For multiple exposures/outcomes:

`PRIMARY TEST FAMILY`
must be explicit.

Use:
- corrected significance;
- or explicit exploratory/suggestive classification.

Hard:

> **NOMINAL P<0.05 AFTER LARGE-SCALE SCREENING != DEFINITIVE CAUSAL DISCOVERY.**

## 16P.5 Reverse-Direction Boundary

A null reverse MR means:

`NO REVERSE EFFECT DETECTED UNDER AVAILABLE INSTRUMENTS`.

It does not prove:
- unidirectionality;
- absence of biological feedback;
- absence of reverse causality in all settings.

## 16P.6 Cross-Instrument Boundary

Secondary instrument classes (e.g. pQTL) are classified as:

`CONCORDANT / NON_REPLICATION / INCONCLUSIVE_LOW_POWER / DISCORDANT`.

Material null/discordant evidence must propagate through Boundary Inheritance.

## 16P.7 MR-specific resource

Use:
`patterns/QiTeng_MR_CausalInference_Overlay_v1.0.md`

for:
- estimand planning;
- Methods routing;
- Results packets;
- MR Discussion synthesis;
- figure routing;
- MR hard negatives.

Default remains:
`QITENG_Q1_GUARDED`.



# 16Q. Narrative-Review Surface, Method Provenance & Citation Conservation — Phase 3G-0B

This module is calibrated from direct Teng Qi feedback on a Skill-generated narrative-review rewrite.

Calibration class:
`DIRECT_EXPERT_FEEDBACK_CALIBRATION — NOT TRUE_BLIND`.

## 16Q.1 Control Plane / Manuscript Plane Firewall

Internal Skill objects:
- Claim Ledger
- evidence ceiling
- evidence-adjudication
- reviewer-risk map
- decision gate
- source-verification log
- coverage audit

are a **control plane**.

The manuscript is the **scientific surface**.

Hard:

> **CONTROL PLANE != MANUSCRIPT PLANE**

Do not leak internal QA vocabulary into manuscript prose merely to signal rigor.

## 16Q.2 Human-Surface Prose Gate

Flag sentences that mainly describe:
- how the Skill audited the review;
- how evidence was ranked internally;
- how the editorial process was organized.

Examples requiring deletion/rewrite/backstage relocation unless naturally necessary:
- `claim ceilings are explicit`
- `evidence-adjudication model`
- `decision-resolving tests`
- `publisher-level source verification`

Preferred:
state the scientific limitation or the concrete next experiment directly.

## 16Q.3 Review Method Provenance Gate

For a narrative review:

`NO SOURCE METHOD -> NO INVENTED METHOD`.

The assistant's own literature search or source verification is not automatically an author method.

If review methodology is required:
`REQUEST/RETRIEVE REAL AUTHOR PROCESS -> WRITE TRUTHFULLY`.

Do not fabricate or infer:
- databases;
- dates;
- search strings;
- screening;
- selection rules;
- risk-of-bias process.

## 16Q.4 Narrative Discussion Surface Gate

Default when the source has a coherent continuous Discussion:
`KEEP CONTINUOUS`.

Use hidden paragraph roles for:
- synthesis;
- contradiction;
- limitation;
- translation;
- future test.

Expose subheadings only with author/journal/style justification.

## 16Q.5 Reference Conservation Gate

Narrative-review citation deletion is not an optimization target.

Default:
`PRESERVE`.

Large reference reduction:
`>20% OR >10 REFERENCES`
-> `REFERENCE_COVERAGE_REVIEW`.

Deletion ledger must record:
`REFERENCE -> ORIGINAL JOB -> SURVIVING CLAIM/SECTION -> KEEP/REMOVE -> REASON -> COVERAGE CONSEQUENCE`.

## 16Q.6 Numeric Citation First-Appearance Gate

For numbered styles:

`REFERENCE NUMBER = ORDER OF FIRST APPEARANCE`
unless the target journal explicitly specifies otherwise.

After any citation mutation:
`GLOBAL RENUMBER -> IN-TEXT SYNC -> BIBLIOGRAPHY SYNC -> ORDER QA`.

Hard:

> **1-N CONTINUITY != CORRECT ORDER.**

A reference lock requires:
- first-appearance order;
- no missing;
- no orphan;
- no out-of-range;
- no duplicate bibliographic identity;
- coverage review when triggered;
- correct source/journal style.

## 16Q.7 Direct Style-Authority Gate

When Teng Qi directly reviews Skill output, his feedback has high weight for **Teng Qi style/surface conventions**.

Keep separate:
`STYLE AUTHORITY`
from
`SCIENTIFIC TRUTH`.

Scientific safety still overrides any unsafe wording preference.

## 16Q.8 Patch Discipline

If direct feedback says most other content is acceptable:

`PATCH OBSERVED FAILURE CLASSES ONLY`.

Do not erase successful:
- claim calibration;
- human/preclinical distinction;
- boundary inheritance;
- contradiction handling;
- figure scientific safety.

Use:
`patterns/QiTeng_NarrativeReview_Surface_Integrity_Overlay_v1.0.md`
and
`patterns/QiTeng_Reference_Citation_Integrity_Gate_v1.0.md`.



# 16R. Review Surface Architecture & Scholarly Coverage — Phase 3G-0C

## 16R.1 Surface Conservatism Gate

If the manuscript's macro-surface is already scientifically serviceable:

`PRESERVE SURFACE -> IMPROVE LOGIC INSIDE IT`.

Hard:

> **EDIT DEPTH != HEADING CHURN.**

Do not create visible structural novelty merely to display editorial rigor.

## 16R.2 Two-Axis Review Surface Router

Classify review surface on two independent axes.

### Method axis
- PROCESS_SILENT
- DECLARED_NON_SYSTEMATIC_METHOD
- DECLARED_SYSTEMATIC_OR_SCOPING_METHOD

### Discussion axis
- CONTINUOUS_DISCUSSION
- SUBSECTIONED_DISCUSSION
- DISTRIBUTED_SYNTHESIS_NO_DISCUSSION

Hard:

> **METHOD SURFACE DOES NOT DETERMINE DISCUSSION SURFACE.**

Use `patterns/QiTeng_Review_Surface_Architecture_Engine_v1.0.md`.

## 16R.3 Visible Heading Semantic Gate

A visible heading should name:
- a scientific topic;
- a controversy;
- a mechanism;
- a clinical/translational problem;
- a future research domain.

It should not merely expose:
- evidence calibration;
- claim adjudication;
- QA states;
- editorial decision gates.

Hard:

> **VISIBLE HEADING = READER-FACING SCIENCE, NOT CONTROL-PLANE OPERATION.**

## 16R.4 Narrative Compression / Reference Breadth Decoupling

Hard:

> **NARRATIVE COMPRESSION != REFERENCE COMPRESSION.**

A mature Review can:
- shorten prose;
- sharpen the thesis;
- preserve or expand references.

Reference count is not a proxy for:
- rigor;
- selectivity;
- signal-to-noise ratio.

Use scholarly function, not minimalism.

## 16R.5 Reference Function Conservation

Before deleting a citation from a narrative Review, classify its job:

- DIRECT_CLAIM_SUPPORT
- LANDMARK_ATTRIBUTION
- FIELD_POSITIONING
- CONTRADICTION_BOUNDARY
- MECHANISTIC_FOUNDATION
- PHENOTYPE_BREADTH
- MEASUREMENT_METHOD
- TRANSLATIONAL_CONTEXT
- HISTORICAL_CONTEXT
- REDUNDANT_DUPLICATE

Delete by lost function, not by centrality alone.

## 16R.6 Same-Project Human-Final Triangulation

A Teng Qi final from the training corpus can provide high-value retrospective evidence for:
- surface architecture;
- paragraph cadence;
- heading usage;
- reference breadth.

But:

`TRAINING-CORPUS HUMAN FINAL != INDEPENDENT VALIDATION`.

Do not count it toward TRUE_BLIND.

Do not copy scientifically unsafe wording merely because it appears in the human final.



# 16S. Academic-Norm Authority, Format Contract & Salience Economy — Phase 3G-0D.1

## 16S.1 Output Purpose Gate

Before formatting or final rewriting, set one:
- AUTHOR_REVIEW
- LAB_HOUSE
- TARGET_JOURNAL_SUBMISSION
- PREPRINT
- ARCHIVE

Hard:

> **OUTPUT PURPOSE PRECEDES FORMAT.**

The same scientific content may have multiple valid interface copies.

## 16S.2 Multi-Axis Authority Matrix

Do not use one universal authority hierarchy.

### Scientific truth
`VERIFIED DATA/SOURCE/STATISTICS/ETHICS > ALL STYLE OR FORMAT PREFERENCES`.

### Submission compliance
`CURRENT OFFICIAL JOURNAL / PROVIDED TEMPLATE > EXPLICIT USER PROJECT FORMAT > SOURCE HOUSE STYLE > QITENG CORPUS PATTERN > SKILL DEFAULT`.

### Author/lab copy
`EXPLICIT USER PROJECT FORMAT > SOURCE HOUSE STYLE > QITENG CORPUS PATTERN > SKILL DEFAULT`.

### Language/style
`DIRECT TENG QI FEEDBACK > TRACKED/PAIRED/SERIAL TENG QI EDITS > CROSS-CORPUS FINAL-STATE PATTERN > SKILL DEFAULT`.

Hard:

> **STYLE AUTHORITY != NORM AUTHORITY.**
> **FLUENCY != ACADEMIC COMPLIANCE.**

## 16S.3 Format Contract Freeze

Before producing an editable manuscript, freeze when known:
- title font/size;
- H1/H2/H3 font/size;
- body/reference font/size;
- margins;
- line spacing;
- page/line numbering;
- citation/reference style;
- figure/table placement;
- language variant;
- template/journal authority.

Do not change locked formatting because another style looks more academic.

## 16S.4 Direct-Formatting Audit

DOCX styles are insufficient.
Audit direct run-level and paragraph-level overrides.

Hard:

> **STYLE NAME PASS != RENDERED FORMAT PASS.**

## 16S.5 Academic Convention Router

Treat:
- article-type section requirements;
- review-method provenance;
- citation/reference order;
- declarations;
- AI disclosure;
- page/line numbering;
- formatting/template rules;

as a COMPLIANCE LAYER.

The Skill's own preferred logic cannot override the compliance layer.

## 16S.6 Salience & Detail Economy Gate

Classify each unit:
- S0 BACKSTAGE
- S1 CONTEXT
- S2 SUPPORT
- S3 EXPLANATORY
- S4 BOUNDARY
- S5 CENTRAL
- S6 REPRODUCIBILITY

Hard:

> **HONEST != EXHAUSTIVE.**
> **TRUE != IMPORTANT ENOUGH FOR MAIN TEXT.**
> **DETAIL ALLOCATION > TOTAL BREVITY.**

## 16S.7 Main-Text Space-Earning Test

A unit earns main-text space when it:
1. advances the central claim;
2. discriminates between interpretations;
3. changes the evidence boundary;
4. enables the next scientific step;
5. is required for reproducibility/compliance.

Otherwise:
`COMPRESS / MOVE / DELETE`.

## 16S.8 Epistemic Economy

Use uncertainty to calibrate verbs and claim strength.

Do not multiply prose merely to show caution.

Hard:

> **EPISTEMIC HONESTY = CLAIM CALIBRATION, NOT CAVEAT ACCUMULATION.**

State a material boundary where it first changes interpretation and repeat it only when a later claim would otherwise overreach.

## 16S.9 Stage-Aware Expansion / Compression

### Early
`EVIDENCE FLOOR BUILD`
Selective expansion is allowed.

### Middle
`OWNERSHIP / ARCHITECTURE`
Redistribute evidence to correct owners.

### Late
`SALIENCE REDISTRIBUTION`
Compress repetition, secondary support and defensive prose.

Longitudinal Teng Qi evidence shows selective, not uniform, expansion:
a section can expand ~60% while a Conclusion barely changes.

## 16S.10 Release Score

Do not collapse manuscript quality into "English quality."

Score separately:
- SCIENTIFIC INTEGRITY
- LANGUAGE
- ACADEMIC COMPLIANCE
- FORMAT CONTRACT
- SALIENCE / 详略得当
- CITATION INTEGRITY
- HUMAN-SURFACE NATURALNESS

Any release-blocking failure prevents overall PASS.

Use:
- `patterns/QiTeng_AcademicNorm_FormatContract_Engine_v1.0.md`
- `patterns/QiTeng_Salience_Detail_Economy_Engine_v1.0.md`


# 16T. Teng-Qi House Surface, Citation Location & Abbreviation Lifecycle — Phase 3G-0E

## 16T.1 House Paragraph Geometry

For `AUTHOR_REVIEW` / `LAB_HOUSE` when Teng-Qi house style is active:

- block/flush paragraph style;
- no first-line indent;
- one blank line between prose paragraphs;
- full justification for body prose.

Hard:

> **PARAGRAPH GEOMETRY IS PART OF THE FORMAT CONTRACT.**

This is supported by direct Teng Qi feedback and longitudinal SCN DOCX formatting.

Do not carry this surface into a target-journal submission when the journal/template specifies otherwise.

## 16T.2 Citation Surface Router

Teng-Qi house-review preference:
`[1]`, `[2–4]`.

But:

> **CITATION IDENTITY IS CONTENT; CITATION PUNCTUATION IS INTERFACE.**

For `TARGET_JOURNAL_SUBMISSION`, use the current official journal style.

Example:
current Frontiers Vancouver guidance uses numbered citations in parentheses; square brackets are reserved for physics/mathematics articles.

## 16T.3 Figure Legend Citation Gate

For original author-created figures/schematics:
`NO ROUTINE LITERATURE CITATIONS IN LEGEND`.

Legend job:
- identify the figure;
- explain panels/relationships;
- define symbols/abbreviations;
- state a concise interpretation boundary when needed.

Evidence ownership remains in the main text.

Exceptions:
- reproduced/adapted/modified external material;
- rights-holder attribution;
- explicit journal requirements;
- genuinely necessary source attribution.

Hard:

> **FIGURE LEGEND != MINI REFERENCE LIST.**

## 16T.4 Reference-Free Conclusion Gate

Teng-Qi default:
`CONCLUSION = NO ROUTINE REFERENCES`.

Conclusion should:
`SYNTHESIZE -> PRIORITIZE -> STATE FINAL BOUNDARY -> END`.

Do not:
- re-list studies;
- repeat citation packets;
- introduce a new evidence stream.

Cross-corpus evidence:
detected Conclusions in all 13 QiTeng corpus papers contained zero numeric citation groups.

Hard:

> **CONCLUSION = ADJUDICATED SYNTHESIS, NOT EVIDENCE RE-LITIGATION.**

## 16T.5 Abbreviation Lifecycle

For ordinary/non-standard abbreviations:

`FULL TERM (ABBR)` at first main-text use.

Also:
- minimize abbreviations;
- avoid them in titles when possible;
- define necessary abbreviations in the Abstract;
- maintain an alphabetized end-list when active author/journal/project format requires it;
- remove obsolete list entries;
- check singular/plural and hyphenation consistency.

Do not blindly treat approved gene/protein symbols as ordinary abbreviations.
Route them through nomenclature rules.

## 16T.6 Citation-Removal Orphan Gate

When citations are removed from:
- Figure legends;
- Conclusion;
- Abstract;
- tables;

re-run:
- reference scholarly-function ownership;
- missing/orphan/out-of-range;
- first-appearance order;
- global renumbering.

Hard:

> **CITATION-FREE SURFACE MUST NOT CREATE REFERENCE-IDENTITY DAMAGE.**

## 16T.7 Current Teng-Qi house profile

Use `data/QiTeng_TengQi_House_Surface_Profile_v1.0.csv`.

Do not universalize it.
Compile a purpose-specific interface using the authority matrix from Phase 3G-0D.1.

Use:
- `patterns/QiTeng_Manuscript_Surface_Convention_Engine_v1.0.md`
- `patterns/QiTeng_Abbreviation_Lifecycle_Checklist_v1.0.md`



# 16U. Scientific Object Persistence — Phase 3G-0E.1

## 16U.1 Figure Object Persistence Gate

Hard:

> **FIGURE CAPTION COUNT != FIGURE OBJECT COUNT.**

A Figure caption, callout or legend does not prove that the embedded figure still exists.

Before and after any DOCX edit, inventory actual:
- inline/anchored drawings;
- tables;
- equations;
- other protected non-text scientific objects.

## 16U.2 Empty-Text Paragraph Warning

Hard:

> **EMPTY TEXT != EMPTY PARAGRAPH.**

An empty paragraph may contain a drawing, field, bookmark or other scientific object.
Do not delete/rebuild it from paragraph text alone.

## 16U.3 Pre/Post Object Invariant

For a text/surface-only edit:
`EXPECTED OBJECT INVENTORY BEFORE == ACTUAL OBJECT INVENTORY AFTER`.

Any difference is a release-blocking regression unless explicitly authorized.

## 16U.4 Structural + Visual Release

For every figure-bearing DOCX:
1. run actual image/drawing audit;
2. match drawing count to Figure caption count;
3. render the DOCX;
4. inspect every page;
5. confirm figure identity, readability and caption ownership.

Hard:

> **TEXT QA PASS CANNOT OVERRIDE MISSING SCIENTIFIC OBJECTS.**

Use `patterns/QiTeng_Figure_Object_Persistence_Gate_v1.0.md`.

# 17. QITENG_Q1 mode

Default serious-submission mode.

Preserve:
- explicit gap visibility;
- strong paragraph navigation;
- result-to-literature comparison;
- contradiction acknowledgment;
- mechanism/translation orientation;
- clear future direction.

Upgrade:
1. shorten generic background;
2. move tension/gap earlier;
3. reduce transition-marker dependence;
4. prioritize effect size and evidence tier;
5. explicitly label inference vs observation;
6. require external validation language for biomarker claims;
7. require direct functional testing before mechanism claims;
8. require evidence hierarchy in reviews;
9. turn future directions into decision-resolving tests;
10. end conclusions at the strongest defensible claim, not the most exciting claim.

---

# 18. Revision workflow

## Pass 0 — Output-purpose and format-contract preflight
Resolve output purpose, authority conflicts, article-type/journal requirements, source/user house format and direct-format overrides before substantive manuscript production.


## Pass 1 — Scientific argument audit
Identify:
- central claim;
- novelty;
- major evidence;
- evidence tier;
- unsupported claims;
- contradictions;
- missing validation.

## Pass 2 — Move-state audit
Assign each argument unit a move label.
Flag:
- missing required state;
- backward jump;
- duplicated state without added value;
- premature implication;
- conclusion before evidence.

## Pass 3 — Methods/Results evidence-reporting audit
For data-bearing manuscripts, run the Phase 3C engine before prose polishing:
- reconstruct Methods information order;
- map each Result to its Methods rule;
- identify effect/CI/P/multiplicity status;
- classify validation versus robustness;
- surface null/boundary-changing evidence;
- compress duplicate navigation.

## Pass 4 — Section reconstruction
Reorder, merge, split, or remove units to achieve the genre-specific state machine.

## Pass 5 — Paragraph reconstruction
Use the Paragraph Assembly & Cadence Engine: `ANCHOR -> DEVELOPMENT -> INTERPRETATION -> [BOUNDARY IF LOCALLY NEEDED] -> LANDING`. Flag microparagraphs, duplicate destinations, and late new-evidence drift.

## Pass 6 — Contradiction and boundary pass
Run the contradiction resolver and evidence governor.

## Pass 7 — Future-direction compiler
Convert every major unresolved issue into a specific next test.

## Pass 8 — Sentence refinement
Only now edit grammar, terminology, rhythm, concision, and journal tone.

## Pass 9 — Hostile reviewer simulation
Ask:
- Why should I care?
- What is actually new?
- Which figure supports this?
- Is the evidence direct?
- What alternative explanation exists?
- Is causality overstated?
- Is mechanism demonstrated or inferred?
- Is clinical utility premature?
- What result would falsify the proposed interpretation?

---


## Pass 10 — Figure / layout / submission production
Build the Figure Role Map; run panel storyboarding, Figure Claim Gate, caption de-duplication, source-data traceability, final-size legibility and Journal Compliance Router. For submission preparation, run S01-S22 Production Gate.

# 19. Output modes

- `AUDIT_ONLY`: logic/evidence diagnosis without rewriting.
- `MOVE_MAP`: label current paragraphs/argument units and identify missing states.
- `OUTLINE_REBUILD`: rebuild section/paragraph architecture.
- `PARAGRAPH_REWRITE`: rewrite supplied paragraphs using the state machine.
- `SECTION_DRAFT`: draft a complete section from verified inputs.
- `DISCUSSION_ENGINE`: map Results to literature, mechanism, contradiction, implication and boundary.
- `REVIEW_SYNTHESIS`: convert literature lists into evidence hierarchy and critical synthesis.
- `MR_CAUSAL_GOVERNOR`: audit causal language and MR evidence strength.
- `QITENG_Q1`: QiTeng architecture plus Q1 enhancement layer; default for serious submissions.
- `FULL_MANUSCRIPT`: manuscript-scale orchestration.

Never fabricate data, citations, methods, sample sizes, statistical values, experiments, or outcomes.
If support is absent, mark `SUPPORT REQUIRED` or `VALIDATION REQUIRED`.

---

# 20. Quality gates

## Logic gate
- [ ] Central claim is identifiable.
- [ ] Required move states are present.
- [ ] Order is logical even if states are compressed.
- [ ] Each paragraph changes the reader's knowledge state.
- [ ] No major inferential jump is hidden.

## Evidence gate
- [ ] Every major claim maps to evidence.
- [ ] Evidence tier matches claim strength.
- [ ] Observation, causal inference, mechanism, and clinical utility are separated.
- [ ] Contradictory evidence is addressed.

## Discussion gate
- [ ] Result repetition is minimal.
- [ ] Major findings are contextualized.
- [ ] Alternative explanations are considered.
- [ ] Mechanistic claims are calibrated.
- [ ] Implications are bounded.
- [ ] Next tests resolve named uncertainties.

## Review gate
- [ ] Literature is synthesized, not stacked.
- [ ] Strongest and weakest evidence are distinguished.
- [ ] Central controversies are addressed when material.
- [ ] Critical synthesis adds something beyond summary.
- [ ] Future agenda is testable and prioritized when appropriate.
- [ ] No review methodology has been invented from editorial activity.
- [ ] Internal audit vocabulary has not leaked into reader-facing prose.
- [ ] Narrative-review Discussion surface matches author/journal convention.
- [ ] Reference coverage has not been aggressively pruned without a coverage ledger.
- [ ] Numbered references pass first-appearance order QA.

## Reference/Citation gate
- [ ] Citation numbers follow first appearance for numbered styles unless journal rules differ.
- [ ] 1-N continuity, orphan, missing, out-of-range and duplicate checks pass.
- [ ] Added/deleted references have traceable provenance when changes are material.
- [ ] Large citation reductions have passed a coverage review.
- [ ] Citation style is preserved until target-journal formatting is intentionally applied.

## Scientific object persistence gate
- [ ] Expected figure/table/equation inventory was recorded before layout-sensitive edits.
- [ ] Actual embedded drawing/object count matches the expected inventory.
- [ ] Figure caption count matches actual figure-object count.
- [ ] No image-only/field-bearing paragraphs were lost during text reconstruction.
- [ ] Full DOCX render confirms every figure is visible, readable and paired with the correct caption.

## Manuscript surface gate
- [ ] Paragraph geometry matches the active house/journal format contract.
- [ ] Citation punctuation follows the active interface authority.
- [ ] Figure legends do not carry routine citation clutter.
- [ ] Conclusion is a synthesis surface and normally citation-free under Teng-Qi style.
- [ ] Removing legend/Conclusion citations did not create orphan references.
- [ ] Non-standard abbreviations are defined at first main-text use.
- [ ] Abbreviation end-list is complete/alphabetized when required.

## Academic compliance / format gate
- [ ] Output purpose is explicit.
- [ ] Current official journal/template requirements were checked when a target is fixed.
- [ ] User/project format contract is frozen where higher authority is silent.
- [ ] DOCX direct formatting matches the contract, not only style definitions.
- [ ] Page/line numbering, citation style, references, declarations and article-type structure follow the active compliance layer.
- [ ] A house-review copy is not mislabeled as a submission-compliant copy.

## Salience / detail-economy gate
- [ ] Central and decision-changing material has priority.
- [ ] Supporting evidence is compressed rather than narrated at equal length.
- [ ] Repeated caveats have been consolidated.
- [ ] Backstage QA language remains backstage.
- [ ] Reproducibility detail is routed to Methods/Supplement rather than deleted.
- [ ] Late-stage prose does not preserve evidence-floor detail merely because it is true.
- [ ] Section/paragraph length reflects scientific job rather than equal allocation.

## Language gate
- [ ] Transitions reflect real relations.
- [ ] Generic background is minimized.
- [ ] No inflated novelty language.
- [ ] No repeated empty transition adverbs.
- [ ] Long sentences do not contain multiple unrelated moves.

---


## 20.1 Traceability rule

When this Skill recommends a structural change, it should be possible to explain the recommendation using one or more move states, an evidence-tier mismatch, a contradiction-resolution need, or a future-test requirement.

Do not justify edits with vague labels such as `more academic`, `more native`, or `more high-impact` when a structural reason can be stated.


# 21. Current limitations of v0.3.21

Phase 2 completes corpus-level move coding of 113 argument units across 13 papers and 28 section sequences, but this version is not yet stable.

Phase 3A now includes a curated sentence-level move library in the target 300-500 range, move-specific abstract patterns, semantic connector controls, negative exemplars, and a stratified 100-sentence audit.

Still required:
- blind AB testing on unseen manuscripts;
- error-driven sentence-level relabeling from AB-test failures;
- independent/manual adjudication of a larger Gold subset;
- quantitative longitudinal style-change analysis;
- journal-family adaptation tests;
- reviewer-style stress tests;
- calibration against top-tier biomedical editorials and high-impact original research.

Do not declare the Skill production-stable until these tests are passed.
