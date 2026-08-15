# Action record: Gate C6B regulatory evidence and Figure 5

Date: 2026-08-15
Project: 6013RP-wyf / Phase 17 v7-v8 writing transition
Gate: C6B
Final decision: `PASS_GATE_C6B_UPPER_Q1_REGULATORY_FRAMING_AUTHORIZED_NONCAUSAL`

## 1. Round objective

This round executed the complete prespecified Gate C6B contract after Gate C6A had
frozen the manuscript claim hierarchy. The objective was to determine whether the
independently replicated SLE IFN/ISG program is accompanied by concordant
STAT1/STAT2-centred regulatory evidence, without reselecting contrasts, regulators,
targets, thresholds or program genes after effect inspection.

The work was deliberately split into ordered locks:

1. freeze official external resources and mappings without effects;
2. qualify the regulator engine using resources, coverage, null data and synthetic
   signals only;
3. calculate the frozen 24-test confirmatory family only after qualification passed;
4. freeze the orthogonal mapping and scoring methods before reading perturbation
   effects;
5. run MSigDB and GSE23307 supportive evidence;
6. repair an objectively detected GSE23307 scale error without overwriting its audit
   trail; and
7. independently reproduce the critical calculations before authorizing Figure 5.

## 2. External resources frozen

Three official resources were downloaded and retained locally as recomputable,
Git-ignored inputs:

| Resource | Size | SHA-256 |
|---|---:|---|
| MSigDB human Hallmark GMT v2026.1.Hs | 48,686 B | `EECAF6DAD908334AE885406EC72BDC0646D8917588ED7C219FAC92FC5363F596` |
| GSE23307 series matrix | 645,027 B | `771D9F5C0D77447BC09330C18ECE17D9628E260A36E184C4EE76B1AB947EDF97` |
| GPL6104 annotation | 4,584,978 B | `82AE57D6D9EC26CE2BCFF01CCD1DB498BB8055EE01471829DEC0A5AB5666D518` |

The already frozen CollecTRI raw content retained SHA-256
`98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1`;
its deterministic gzip retained SHA-256
`C99EC03032009F935610C1808D75BD6FE7DCA25C8B7EA80786242BB6EE457F40`.

The MSigDB parser recovered systematic ID M5911,
`HALLMARK_INTERFERON_ALPHA_RESPONSE`, with exactly 97 unique genes in release
2026.1.Hs. Eight overlap the frozen 12-gene IFN positive arm.

The GSE23307 metadata parser identified six samples and froze only four paired
primary B-cell samples: IFN-beta and control for HI1 and HI2. GPL6104 contains
22,185 annotation rows and the expected `Gene symbol` field.

## 3. Resource-parser correction before effects

The first GPL6104 parser incorrectly treated the file-level `^Annotation` line as
the table header. This yielded zero symbol-column candidates and a metadata-inflated
row count. No expression or regulator effect had been unlocked.

The parser was repaired to read only between `!platform_table_begin` and
`!platform_table_end`. The corrected freeze recovered 22,185 platform rows and both
`Gene symbol` and `UniGene symbol`. The erroneous compact freeze output was
regenerated before C6B-1 qualification and did not enter downstream analysis.

## 4. C6B-1 no-effect qualification

The qualification read real gene tables only for tested flags, symbols and target
coverage. It did not read log fold changes, F statistics or expression differences.

All checks passed:

- 3/3 external-resource hashes matched;
- all eight CollecTRI regulons parsed with the frozen duplicate/direction rules;
- all 24 contrast-regulator pairs retained at least five targets;
- the minimum core-regulator coverage was 14 targets;
- two independent ULM implementations agreed to `2.220e-15`;
- 2,000 null tests produced a P<0.05 fraction of 0.0505;
- all 12 synthetic IFN signals were positive;
- synthetic global-24 BH sensitivity was 1.000 with empirical FDR 0.000; and
- manual BH and statsmodels BH differed by at most `5.551e-17`.

The resulting unlock was `PASS_GATE_C6B1_NO_EFFECT_QUALIFICATION` with both real
regulator and GSE23307 expression effects explicitly marked uninspected.

## 5. Windows numerical-runtime issue and repair

The Miniforge environment contains NumPy 2.4.6 and repeatedly raised native Windows
exception `0xc06d007f` in `numpy.linalg.lstsq`, `numpy.cov`, large BLAS dot products
and later Matplotlib coordinate transforms. These failures produced no Python
traceback unless `-X faulthandler` was enabled.

The analysis did not ignore the failures:

- qualification replaced the failing independent matrix path with a pure-Python
  `math.fsum` normal-equation implementation;
- the primary ULM used the qualified `fsum` path after the large-vector BLAS failure;
- the independent final audit used a distinct centred-`fsum` formulation; and
- final plotting and audit were rerun under `D:\bioinfor\python.exe`, which has an
  independent NumPy/SciPy/Matplotlib/statsmodels stack.

Cross-runtime reproduction therefore became an additional audit rather than an
unrecorded workaround. The Scanpy environment remains suitable for prior single-cell
steps, but its NumPy binary stack should be repaired before future plotting or
linear-algebra work.

## 6. Frozen 24-test regulator results

The confirmatory family contained exactly eight frozen regulators across exactly
three frozen contrasts. A single global Benjamini-Hochberg adjustment covered all 24
P values.

Core estimates were:

| Contrast | STAT1 slope | STAT1 global q | STAT2 slope | STAT2 global q |
|---|---:|---:|---:|---:|
| GSE174188 discovery | 1.285 | `6.55e-14` | 2.182 | `1.84e-6` |
| GSE174188 donor-nonoverlap | 1.091 | `6.46e-17` | 2.962 | `2.04e-18` |
| GSE135779 childhood | 1.138 | `1.31e-21` | 2.400 | `7.97e-13` |

IRF9 was positive and global-q significant in all three contrasts. IRF7 was positive
in all three, global-q significant in donor-nonoverlap and childhood, and positive
but not significant in discovery. Therefore every contrast had four of four IFN
regulators positive, with no globally significant opposite-direction IFN result.

No proliferation control produced a positive global-q<0.05 pattern across all three
contrasts. MYC was significantly negative in all three; this is a specificity result,
not evidence that MYC is an inert biological null.

## 7. Influence and sensitivity analyses

For STAT1 and STAT2 in all three confirmatory contrasts:

- every leave-one-target estimate retained the full positive direction; and
- all 100 deterministic 80%-target resamples were positive.

Thus all six core contrast-regulator pairs had leave-one-out direction fraction 1.0
and resampling positive fraction 1.0. Extended IFN regulators were subjected to the
same diagnostics and retained at least the frozen five-target minimum.

The supportive sensitivity table contains exactly 72 results: eight regulators
across nine prespecified branches. STAT1 and STAT2 were positive in all 9/9 branches;
their minimum sensitivity slopes were 0.652 and 1.439, respectively. These analyses
remain supportive and do not alter the global confirmatory family.

## 8. Orthogonal method freeze

Before reading GSE23307 expression effects, the platform mapping and scoring rules
were frozen:

- all 12 IFN positive-arm genes mapped;
- 21 exact-symbol GPL6104 probes were retained;
- multiple probes were aggregated by the median within gene and sample;
- paired IFN-beta minus control effects were calculated within each donor;
- the program effect was the arithmetic mean of the 12 gene effects; and
- n=2 prohibited a powered P value.

M5911 enrichment was frozen as weighted preranked GSEA with exponent 1, the frozen
symbol-collapsed `sign(logFC) * sqrt(F)` rank, 10,000 deterministic gene-label
permutations per contrast and descriptive BH across the three enrichment results.
This family is outside the global 24 regulator tests and cannot rescue them.

## 9. GSE23307 scale error, preservation and repair

The first orthogonal run revealed values on a linear-intensity scale, despite the
method label having assumed submitted log2 values. The initial mean paired values
were therefore invalid as log2 effects. The source processing statement reports
Illumina BeadStudio quantile normalization but no log transformation; selected raw
probe values ranged from 37.65039 to 24,966.73.

The repair was objective and unit-driven:

- apply `log2(x + 1)` to each probe-sample value;
- then aggregate probes by the frozen median rule; and
- keep all samples, genes, mappings and acceptance conditions unchanged.

Files 10-14 in the regulatory-evidence directory are retained and manifest-labelled
`superseded_audit_only`. They are prohibited from figures, prose and scientific
interpretation. Corrected files 16-20 are the active results. No old file was silently
overwritten or deleted.

## 10. Corrected orthogonal results

After `log2(x + 1)` repair:

- HI1 mean paired program effect was 3.294, with 12/12 genes positive;
- HI2 mean paired program effect was 3.666, with 12/12 genes positive; and
- no inferential P value was calculated for the two donors.

M5911 results were:

| Contrast | Matched genes | NES | Permutation P | Descriptive q |
|---|---:|---:|---:|---:|
| GSE174188 discovery | 54 | 3.187 | `1.68e-4` | `1.72e-4` |
| GSE174188 donor-nonoverlap | 68 | 3.050 | `1.50e-4` | `1.72e-4` |
| GSE135779 childhood | 81 | 3.527 | `1.72e-4` | `1.72e-4` |

Both orthogonal layers are directionally compatible with the regulator result and
show no material contradiction. They support an interferon-response interpretation
but do not establish a unique ligand or causal upstream mechanism.

## 11. Independent final audit

The final audit independently recomputed every confirmatory ULM using a centred
`fsum` formula and recomputed the 24-test BH values with statsmodels. It also
reconciled every influence/resampling group, all 72 sensitivity rows, all 24 paired
GSE23307 gene effects, all external hashes and all source-gene-table hashes.

All 16 final checks passed. Maximum discrepancies were:

- ULM field delta: `1.776e-15`;
- global BH delta: `1.110e-16`; and
- GSE23307 donor-mean delta: `4.441e-16`.

The integrity manifest contains 25 active files and six superseded audit-only files.

## 12. Figure 5

Figure 5 was generated only after the final PASS conditions were available. It has:

- panel A: frozen evidence architecture and multiplicity/influence design;
- panel B: IFN-family regulator slopes and 95% confidence intervals;
- panel C: prespecified proliferation-control slopes and intervals; and
- panel D: M5911 NES values and corrected two-donor IFN-beta program effects.

The visual output is 4,254 x 4,140 pixels at 600 dpi plus a vector PDF. A second
visual QA pass corrected clipped B-panel labels, shortened contrast labels and added
between-contrast separators. Figure source data and a complete claim-bounded caption
are versioned beside the image.

## 13. Final scientific decision

Gate C6B authorizes the following upper-Q1-compatible statement:

> The independently replicated SLE-associated IFN/ISG program in conventional B
> cells is accompanied by concordant STAT1/STAT2-centred regulatory activity and
> orthogonal interferon-response evidence.

The authorized boundary is observational. The data do not establish causality, a
unique upstream interferon species, direct TF binding in the assayed cells or a new
B-cell subtype. The C3A composition no-go and the C2B3 fine-state failure remain
binding and are not modified by Gate C6B.

## 14. Principal files created

Scripts:

- `audit_tools/phase17_c6b_01_freeze_external_resources.py`
- `audit_tools/phase17_c6b_02_qualify_regulatory_engine.py`
- `audit_tools/phase17_c6b_03_fit_frozen_regulators.py`
- `audit_tools/phase17_c6b_04_qualify_orthogonal_methods.py`
- `audit_tools/phase17_c6b_05_run_orthogonal_response.py`
- `audit_tools/phase17_c6b_06_review_and_figure.py`

Key active outputs:

- `phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/11_C6B1_QUALIFICATION_DECISION.json`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/01_CONFIRMATORY_REGULATOR_RESULTS.csv`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/02_IFN_TARGET_INFLUENCE_SUMMARY.csv`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/05_SUPPORTIVE_SENSITIVITY_REGULATOR_RESULTS.csv`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/19_MSIGDB_M5911_PRERANKED_GSEA.csv`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/22_FIGURE5_REGULATORY_EVIDENCE.pdf`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/24_GATE_C6B_FINAL_AUDIT.json`
- `phase17_v7/gateC6B/20260815_regulatory_evidence/25_INTEGRITY_MANIFEST.csv`

## 15. Limitations and residual risks

- CollecTRI activity is inferred from observational differential-expression ranks;
  it is not direct TF occupancy or causal perturbation in SLE B cells.
- GSE23307 has only two paired healthy donors and supports direction only.
- The source GSE23307 matrix required a transparent log2-scale repair.
- M5911 permutation P values are limited by 10,000 permutations and are supportive.
- IRF7 has only five matched targets in the two GSE174188 confirmatory contrasts.
- The Miniforge NumPy binary stack has a native Windows linear-algebra/Matplotlib
  fault and should be rebuilt before future use outside Scanpy-specific steps.
- Figure 1-3 still require regeneration under the same final visual system.
- Manuscript v8 and RP v15 do not yet contain the completed C6B values and wording.

## 16. Advisor judgment and next target

The project has crossed the main evidence threshold for a credible upper-Q1
observational paper. Its strongest chain is now: disease-blind broad identity scope,
an honest composition no-go, robust within-conventional-B IFN discovery, independent
childhood SLE replication, STAT1/STAT2-centred regulon concordance, and orthogonal
interferon-response evidence.

The next bottleneck is presentation consistency, not another exploratory dataset.
Gate C7 should integrate C6B into manuscript v9 and RP v16, regenerate Figures 1-3,
harmonize all five figures/captions/source-data tables, and audit every title,
abstract, Results, Discussion and Methods claim against the frozen gate hierarchy.
No additional large dataset should be added before that writing and figure audit is
complete.
