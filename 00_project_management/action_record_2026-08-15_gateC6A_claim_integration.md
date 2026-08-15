# Action record: Gate C6A claim integration and regulatory pre-effect design

Date: 2026-08-15
Project: 6013RP-wyf / Phase 17 v7-v8 writing transition
Gate: C6A
Final decision: `PASS_GATE_C6A_CLAIM_AND_MANUSCRIPT_FREEZE`

## 1. Objective and governance

This round converted the completed C2B4-C5B analyses into a manuscript-level claim
hierarchy. It did not rerun or reinterpret an older manuscript result. All numerical
claims were taken from machine-readable frozen decisions and compact result tables.
The v6 manuscript and earlier ABC/APC-like figure sequence remain historical only.

The work had five objectives:

1. reconcile the C2B3 failure, C2B4 repair, C3A composition no-go, C4B transcription
   pass and C5B independent-validation pass;
2. create a claim-to-evidence matrix with explicit permitted and prohibited wording;
3. write a new manuscript and research proposal rather than overwrite prior versions;
4. replace the old figure sequence with a Nature-style evidence hierarchy; and
5. inventory regulatory resources and freeze a C6B contract without calculating any
   real regulator effect.

## 2. Source decision audit

The following binding decisions were re-read from JSON and Markdown sources:

| Gate | Decision | Manuscript consequence |
|---|---|---|
| C2B3 | `HOLD_GATE_C2B3_REVIEW_REQUIRED` | five-/four-/three-state hard identities remain failed |
| C2B4 | `PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED` | only `B_CONV`, `B_ASC` and continuous within-`B_CONV` programs authorized |
| C3A | `NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM` | `B_ASC` abundance is secondary/negative context |
| C4B | `PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION` | IFN/ISG is the discovery and internal-replication anchor |
| C5B | `PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION` | independent program-level replication authorized |

The C2B3 failure was not rewritten as success. C2B4 replaces only the unstable
fine-state scope with a broad two-compartment model. This distinction is now visible
in the manuscript, proposal and Figure 1 architecture.

## 3. Frozen claim hierarchy

The central sentence is:

> A disease-blind broad conventional-B-cell compartment exhibits reproducible
> SLE-associated type I interferon transcriptional remodeling across GSE174188 and
> the independent GSE135779 cohort.

The claim hierarchy is:

- central: GSE174188 discovery/internal IFN plus independent GSE135779 IFN;
- foundation: disease-blind `B_CONV`/`B_ASC` identity scope;
- supporting internal: GSE174188 naive-to-memory and APC/HLA axes;
- external-only: GSE135779 atypical/low-naive observation;
- secondary: `B_ASC` abundance and flare context;
- boundary: adult GSE135779 is directional and underpowered;
- required limitation: genome-wide cross-dataset rho is 0.026; and
- locked future claim: regulator activity pending C6B.

Eleven structured claims were assigned evidence sources, analysis units, allowed
wording, prohibited wording and manuscript locations. This prevents the external
atypical result, internal nonoverlap result or adult estimate from being promoted
beyond their design tier.

## 4. Quantitative narrative integrated

The new text reports the following critical values from frozen outputs:

- two-compartment minimum mapped ARI 0.990 and minimum state median Jaccard 0.991;
- primary `B_ASC` composition odds ratio 0.947 (95% CI 0.636-1.410; P=0.787);
- primary GSE174188 IFN effect 0.837 (95% CI 0.525-1.148; q=2.98 x 10^-6);
- GSE174188 donor-nonoverlap IFN effect 1.086 (q=3.61 x 10^-4);
- GSE135779 childhood IFN effect 1.042 (95% CI 0.681-1.402;
  q=2.98 x 10^-6);
- GSE135779 combined IFN effect 0.996 (q=1.31 x 10^-6);
- adult effect 0.968 with a confidence interval crossing zero; and
- shared tested-gene Spearman rho 0.026 with 10/10 shared IFN genes positive in both
  datasets.

Every critical display value is also exported to a machine-readable numeric-source
table with its JSON field and evidence role.

## 5. Manuscript v8

`01_manuscript/manuscript_v8_gateC6A_claim_integrated_2026-08-15.md` was created as a
new scientific draft. It contains:

- a claim-bounded title and quantitative abstract;
- an introduction centered on identity, composition and transcription;
- four Results sections following the gate logic;
- a Discussion that explains program-specific replication despite low genome-wide
  agreement;
- reproducible Methods for disease-blind reconstruction, sample-level composition,
  robust edgeR pseudobulk, HC3 program inference and pre-effect external validation;
- four main-figure legends; and
- explicit limitations for covariates, adult sample size, internal overlap, source
  mapping and causal interpretation.

The manuscript does not inherit v6 effect sizes, hard ABC identities or the old claim
that multiple non-IFN axes replicated.

## 6. Research proposal v15

`01_manuscript/research_proposal_v15_gateC6A_integrated_2026-08-15.md` updates the RP
from a pre-analysis plan to an outcome-integrated proposal. Aims 1-3 are recorded as
completed with their binding results. Aim 4 is narrowed to a prespecified IFN-centred
regulatory test. The revised proposal adds:

- completed evidence and negative-result sections;
- explicit Gate C6B resource, contrast and multiplicity requirements;
- alternatives for low regulon coverage and weak perturbation replication;
- milestones through manuscript/source-data freeze; and
- a final writing-boundary checklist.

The prior v14 PDF, DOCX and Markdown remain unchanged for provenance. Document-format
rendering of v15 is deferred until scientific content and C6B disposition are stable,
avoiding repeated layout work on moving text.

## 7. Figure architecture and Figure 4 legend

The new five-position architecture assigns one scientific job to each figure:

1. valid design and disease-blind identity scope;
2. secondary/null sample-level composition;
3. GSE174188 within-`B_CONV` transcription;
4. independent GSE135779 IFN replication; and
5. conditional regulatory evidence only after C6B passes.

The Gate C5B four-panel PDF is retained as the Figure 4 candidate. A complete legend
now defines donor counts, HC3 intervals, the four-program BH family, internal versus
independent validation, rho=0.026, donor deletion and source-label omission. The
adult estimate is explicitly labelled directional and underpowered.

## 8. C6B resource inventory

A no-effect resource inventory downloaded and deterministically compressed the
human CollecTRI network from OmniPath:

- 64,516 interaction rows;
- raw size 4,061,567 bytes;
- raw SHA-256 `98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1`;
- deterministic gzip size 648,943 bytes; and
- gzip SHA-256 `C99EC03032009F935610C1808D75BD6FE7DCA25C8B7EA80786242BB6EE457F40`.

The resource file is local and recomputable; compact metadata and coverage tables are
versioned. OmniPath booleans were verified as `True/False`, and the parser was
corrected before direction counts were frozen. Ambiguous or unsigned duplicate
TF-target pairs are excluded.

Exact signed-target counts were 291 STAT1, 50 STAT2, 32 IRF7, 25 IRF9, 299 E2F1,
93 FOXM1, 787 MYC and 43 MYBL2. This was inspected without any disease effect.

## 9. Pre-effect contrast coverage and design consequence

Target overlap with frozen tested-gene universes showed:

- STAT1: 98, 129 and 161 targets across the three confirmatory contrasts;
- STAT2: 14, 19 and 20;
- IRF7: 5, 5 and 7;
- IRF9: 7, 10 and 10; and
- a minimum of 8, 12 and 14 for MYBL2, while the other negative controls were larger.

Because IRF7 and primary IRF9 did not meet a ten-target floor, the contract was
revised before any effects: STAT1/STAT2 are the core confirmatory family, IRF7/IRF9
are extended support, and five targets is the formal availability floor. Extended
regulators cannot pass the gate without the core family.

## 10. Frozen C6B statistical contract

The C6B contract fixes:

- three confirmatory contrasts: GSE174188 primary, GSE174188 donor-nonoverlap and
  GSE135779 childhood;
- STAT1/STAT2 core plus IRF7/IRF9 extended IFN family;
- E2F1/FOXM1/MYC/MYBL2 proliferation controls;
- signed `sqrt(F)` ranked statistics and deterministic symbol collapse;
- weighted univariate linear-model activity estimates;
- one global BH family across 8 regulators x 3 contrasts = 24 tests;
- leave-one-target and 100 x 80% target-resampling stability; and
- orthogonal MSigDB M5911 and paired two-donor GSE23307 evidence as supportive
  layers.

No real regulator effect was calculated. The contract requires resource/software
qualification and a machine-readable no-effect unlock before analysis.

## 11. External resource assessment

Official resource records were reviewed for design rather than effects:

- CollecTRI is a curated TF-target network available through OmniPath/decoupleR;
- MSigDB M5911 is the human Hallmark interferon-alpha response set;
- GSE23307 contains paired IFN-beta/control primary B cells from two healthy donors;
- GSE142637 provides IFN-alpha/lambda-stimulated human PBMC single-cell context but
  lacks donor-level replication for inference; and
- GSE175913 provides sorted SLE/healthy B-cell RNA-seq and pSTAT1 response context but
  is not a randomized expression perturbation experiment.

The small perturbation datasets cannot rescue a failed regulator gate or justify
causal language.

## 12. Files created

- `audit_tools/phase17_c6a_01_integrate_claims.py`
- `audit_tools/phase17_c6b_00_inventory_resources.py`
- `.gitignore` policy update for the tracked v8 architecture and local `*.tsv.gz` resources
- `01_manuscript/manuscript_v8_gateC6A_claim_integrated_2026-08-15.md`
- `01_manuscript/research_proposal_v15_gateC6A_integrated_2026-08-15.md`
- `01_manuscript/figure4_gateC5B_legend_draft_2026-08-15.md`
- `04_submission/figure_architecture_v8_gateC6A_2026-08-15.md`
- `00_project_management/gateC6B_regulatory_evidence_freeze_contract_2026-08-15.md`
- `phase17_v7/gateC6A/20260815_claim_integration/*`
- `phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/*`
- this action record; and
- the Gate C6B next-stage decision.

## 13. Quality-control plan

The final automated C6A run must verify:

- all four source JSON decisions match expected decision strings;
- 11 claim rows and 10 manuscript-critical metrics are emitted;
- all C6A document files exist;
- required boundary language is present and prohibited overclaims are absent;
- regulator effects remain uninspected;
- every tracked C6A artifact matches its manifest size and SHA-256; and
- Git staged content matches the final disk bytes.

## 14. Limitations and unresolved work

- C6B regulator effects are intentionally not available in this round.
- The exact MSigDB release/member file still requires retrieval and hashing.
- GSE23307 platform annotation and sample pairing require a no-effect freeze.
- Figure 1-3 artwork must be regenerated from frozen Source Data; only Figure 4 is a
  current main-figure candidate.
- v15 DOCX/PDF rendering is deferred until post-C6B scientific freeze.
- References in manuscript v8 remain a bibliographic integration task.

## 15. Advisor interpretation and next target

The manuscript now has a coherent upper-Q1-compatible descriptive spine: strict
disease-blind identity scope, an honestly negative composition result, robust
within-compartment IFN discovery and independent external replication with influence
and specificity checks. This is already stronger than the prior ABC-centred draft.

The next bottleneck is no longer manuscript logic. It is whether prespecified
STAT1/STAT2-centred evidence survives the strict C6B contract. The immediate next
target is Gate C6B-1 resource/software qualification, followed only on pass by the
24-test frozen regulator analysis and small orthogonal perturbation check.
