# Gate C6B pre-effect regulatory-evidence contract

**Date:** 15 August 2026
**Status:** `PRE_EFFECT_CONTRACT_FROZEN_RESOURCE_AND_SOFTWARE_QUALIFICATION_REQUIRED`
**Real regulator effects inspected:** no

## 1. Scientific question

Test whether the independently replicated SLE-associated IFN/ISG program is
accompanied by concordant activity of a prespecified interferon-centred TF-target
family across GSE174188 discovery, GSE174188 internal donor-nonoverlap validation and
independent GSE135779 childhood validation.

This gate tests convergent observational regulatory evidence. It does not test
causality, identify a unique upstream stimulus or establish a new B-cell subtype.

## 2. Frozen input decisions

The contract inherits without modification:

- `PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED`;
- `NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM`;
- `PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION`; and
- `PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION`.

Only the broad `B_CONV`/conventional-B analog and frozen disease contrasts may be
used. No state, sample, threshold or program gene may be reselected using regulator
results.

## 3. Frozen confirmatory contrasts

| Contrast | Frozen gene table | Role |
|---|---|---|
| GSE174188 primary | `phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/primary_base_gene_results.csv.gz` | discovery |
| GSE174188 validation nonoverlap | `phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/validation_nonoverlap_gene_results.csv.gz` | internal donor-nonoverlap validation |
| GSE135779 childhood | `phase17_v7/gateC5B/20260815_gse135779_external_validation/05_gene_results/childhood_min50_gene_results.csv.gz` | independent validation |

GSE174188 full internal validation, GSE135779 combined, external minimum-cell
thresholds and residual-risk branches are sensitivity analyses. The adult external
contrast remains directional only and cannot satisfy a confirmatory criterion.

## 4. Frozen CollecTRI resource

The primary TF-target network is the human CollecTRI interaction set retrieved
directly from OmniPath:

- endpoint: `https://omnipathdb.org/interactions?datasets=collectri&format=tsv&genesymbols=1`;
- retrieval date: 15 August 2026;
- raw size: 4,061,567 bytes;
- raw SHA-256: `98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1`;
- rows: 64,516; and
- local deterministic gzip SHA-256: `C99EC03032009F935610C1808D75BD6FE7DCA25C8B7EA80786242BB6EE457F40`.

Only exact individual-TF source symbols are used. No complex splitting or orthology
translation is permitted. For duplicate TF-target rows, consensus stimulation is
encoded `+1` and consensus inhibition `-1`; targets with both or neither consensus
direction are excluded. Duplicate rows with the same sign collapse to one edge.

## 5. Frozen regulator families

### IFN confirmatory family

- core: `STAT1`, `STAT2`;
- extended: `IRF7`, `IRF9`; and
- expected direction: positive in every confirmatory contrast.

### Proliferation negative-control family

- `E2F1`, `FOXM1`, `MYC`, `MYBL2`;
- no regulator in this family is expected to reproduce a positive three-contrast
  pattern; and
- the family tests broad proliferation or nonspecific activation rather than a
  perfectly inert biological null.

The resource was inspected only for target availability. Exact signed-target counts
were STAT1 291, STAT2 50, IRF7 32, IRF9 25, E2F1 299, FOXM1 93, MYC 787 and MYBL2 43.

## 6. Pre-effect contrast coverage

Coverage was calculated using only gene identifiers and frozen `filterByExpr` flags,
without reading effect directions or values.

| Regulator | GSE174188 primary | GSE174188 nonoverlap | GSE135779 childhood |
|---|---:|---:|---:|
| STAT1 | 98 | 129 | 161 |
| STAT2 | 14 | 19 | 20 |
| IRF7 | 5 | 5 | 7 |
| IRF9 | 7 | 10 | 10 |
| E2F1 | 83 | 109 | 150 |
| FOXM1 | 16 | 23 | 26 |
| MYC | 317 | 393 | 470 |
| MYBL2 | 8 | 12 | 14 |

The formal minimum is five matched signed targets, matching the standard small-
regulon floor and chosen before any regulator effect is inspected. `STAT1` and
`STAT2` must each retain at least ten targets and form the core acceptance family.
IRF7 and IRF9 are extended support because their primary target coverage is smaller;
they cannot pass the gate without the core family.

## 7. Frozen ranked statistic and activity estimator

For every tested Ensembl feature, compute
`sign(logFC) * sqrt(F)` from the frozen robust edgeR quasi-likelihood result. Untested
features remain unavailable. Map to uppercase gene symbols and average the signed
statistics when multiple tested Ensembl features share a symbol.

For each regulator and contrast, fit a weighted univariate linear model of the
gene-level signed statistic on the frozen `+1/-1` TF-target weights, including an
intercept. Report the slope, standard error, t statistic, two-sided P value, matched
target count and 95% confidence interval. The primary activity direction is the sign
of the slope. The implementation must be independently reproduced by a direct matrix
formula before real effects are unlocked.

No regulator may be dropped, replaced, merged or reweighted after effect inspection.

## 8. Multiplicity

The confirmatory family contains 24 tests: eight nominated regulators across three
confirmatory contrasts. Benjamini-Hochberg correction is applied once across all 24
P values. Per-contrast adjusted values may be shown descriptively but cannot replace
the global family.

Sensitivity contrasts, target-resampling estimates, the MSigDB response signature
and perturbation datasets are outside this 24-test family and must be labelled as
supportive. They cannot rescue a failed confirmatory gate.

## 9. Influence and specificity

For each core regulator and confirmatory contrast:

- repeat the activity estimate after deleting each matched target;
- require all leave-one-target estimates to retain the full-model direction; and
- perform 100 deterministic 80%-target resamples, requiring at least 95% positive
  estimates.

Extended IFN regulators are reported with the same diagnostics where at least five
targets are available. Technical specificity reuses the frozen platelet/ambient,
ASC/UPR and pan-B audits; no new technical family may be added after viewing TF
activities.

## 10. Orthogonal response evidence

Two layers are frozen for qualification before use:

1. MSigDB `HALLMARK_INTERFERON_ALPHA_RESPONSE`, systematic ID `M5911`. The exact
   human release, member file and SHA-256 must be recorded before enrichment.
2. GSE23307 paired IFN-beta versus untreated primary human B cells from two healthy
   individuals. The exact frozen 12-gene IFN/ISG positive arm will be scored within
   each donor after platform annotation is frozen. Direction in both donors is the
   only permitted descriptive summary; n=2 does not support a powered P value.

GSE142637 may be used as supplementary single-cell perturbation context only. Its
lack of donor-level replication prohibits cell-level inferential testing. GSE175913
may provide B-cell/pSTAT1 biological context but is not treated as a randomized
transcriptomic perturbation dataset.

## 11. Gate C6B acceptance

An upper-Q1 regulatory framing is authorized only if all conditions hold:

1. STAT1 and STAT2 activity estimates are positive in all three confirmatory
   contrasts.
2. At least one of STAT1 or STAT2 has global 24-test BH q<0.05 in each of the three
   confirmatory contrasts.
3. At least three of the four IFN-family regulators are positive in each contrast,
   with no globally significant opposite-direction IFN regulator.
4. No proliferation-control regulator shows a positive global-q<0.05 pattern in all
   three confirmatory contrasts.
5. Core target-deletion and target-resampling criteria pass.
6. MSigDB and GSE23307 findings, if available, are directionally compatible and do
   not reveal a material contradiction.
7. All source hashes, identifier mappings, model formulas and multiplicity values are
   independently audited.

If any condition fails, the paper retains the independently replicated IFN/ISG
result and removes a central regulator claim. A partial result may be discussed as a
candidate regulatory hypothesis only.

## 12. Required qualification before effects

- freeze the exact MSigDB release and member checksum;
- qualify the CollecTRI parser, duplicate-edge collapse and direction encoding;
- reproduce weighted-ULM estimates on synthetic positive, negative and null data;
- verify null calibration and global BH implementation;
- verify all three real input tables only for dimensions, tested-gene symbols and
  target coverage; and
- emit a machine-readable unlock decision with `regulatory_effects_inspected=false`.

Until those checks pass, all real regulator activity calculations remain locked.
