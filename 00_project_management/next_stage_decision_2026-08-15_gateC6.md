# Next-stage decision: Gate C6 manuscript integration and regulatory evidence

## Advisor decision

Gate C5B passed independent IFN/ISG replication in GSE135779. The central scientific
bottleneck has shifted from external validation to disciplined manuscript integration
and orthogonal regulatory support.

Proceed to Gate C6 with two sequential components:

1. `Gate C6A`: freeze the manuscript claim hierarchy and rebuild the text and figures
   from the audited C4B/C5B outputs; and
2. `Gate C6B`: freeze and test a targeted external regulatory-evidence contract.

Regulatory analysis must follow the replicated IFN result. It must not search across
many regulators and then present the strongest one as if it had been prespecified.

## Gate C6A: central claim freeze

### Authorized central claim

The exact claim is:

> A disease-blind broad conventional-B-cell compartment exhibits reproducible
> SLE-associated type I interferon transcriptional remodeling across GSE174188 and
> the independent GSE135779 cohort.

The wording must retain all of these boundaries:

- broad conventional-B analog rather than a hard naive/memory subtype;
- association rather than causation;
- IFN-program replication rather than genome-wide replication; and
- adult directional compatibility rather than powered adult confirmation.

### Claim hierarchy

- Central: independently replicated IFN/ISG remodeling.
- Supporting internal context: GSE174188 naive-to-memory and APC/HLA axes.
- External-only observation: GSE135779 atypical/low-naive signal.
- Secondary abundance context: previously frozen B_CONV/B_ASC composition results.
- QC only: platelet/ambient, ASC/UPR and pan-B controls.

The external atypical result cannot be promoted as replication because it was not
positive in GSE174188. Naive-to-memory cannot be described as external replication
because its GSE135779 estimate is null and reverses direction.

## Manuscript restructuring

The preferred Results sequence is:

1. multi-cohort design, disease-blind B-lineage identity and support gates;
2. sample-level B_CONV/B_ASC abundance findings and their limits;
3. GSE174188 conventional-B transcriptional discovery and internal validation;
4. independent GSE135779 IFN/ISG validation, influence and specificity; and
5. targeted regulatory evidence, only if Gate C6B passes.

Methods must describe sample/donor pseudobulk as the inferential unit, the exact
support thresholds, edgeR robust QL, HC3 program inference, four-program BH,
pre-effect C5A freezing and all source limitations.

Discussion must explicitly report the low cross-dataset genome-wide effect
correlation and explain why a frozen program can replicate despite cohort-wide
heterogeneity. It must not use phrases such as "global transcriptomic concordance",
"mechanism" or "B-cell subtype-specific" without additional evidence.

## Figure architecture

The proposed main-figure spine is:

1. Figure 1: cohort architecture, metadata gates and disease-blind B-lineage map;
2. Figure 2: sample-level B-lineage abundance results and support sensitivities;
3. Figure 3: GSE174188 B_CONV IFN discovery/internal replication;
4. Figure 4: GSE135779 independent IFN replication and influence; and
5. Figure 5: regulatory evidence, only after its own frozen gate passes.

The current Gate C5B four-panel figure is the Figure 4 candidate. Avoid a generic
volcano panel. Complete ranked gene tables remain supplementary data.

## Gate C6B: regulatory-evidence freeze

Before inspecting regulator effects, freeze:

- exact reference resources and versions for TF-target inference;
- a narrow IFN-centered regulator family, such as STAT1, STAT2, IRF7 and IRF9;
- direction expectations based on established IFN signaling;
- the same discovery, internal-validation and external-validation contrasts;
- a negative-control regulator family unrelated to interferon biology;
- multiplicity across all nominated regulator activities; and
- acceptance thresholds for cross-dataset direction, uncertainty and influence.

Preferred evidence layers are:

- regulon activity estimated from complete donor-level ranked statistics using a
  curated resource such as CollecTRI or DoRothEA;
- enrichment against independently curated type I IFN perturbation signatures; and
- direct public TF-binding evidence only where a relevant immune/B-cell context and
  traceable source exist.

Do not call TF-target enrichment a causal mechanism. Causal language requires a
relevant perturbational experiment or a truly orthogonal intervention dataset.

## Supporting datasets

GSE163121 may be rerun with the exact 12-gene score as a five-donor directional
boundary analysis. It cannot rescue a failed result or become a powered validation.

OneK1K may establish healthy immune-cell and B-lineage context for the exact frozen
program. It is not an SLE replication cohort and must not be counted as one.

## Gate C6 acceptance

An upper-Q1 regulatory framing is authorized only if the frozen IFN-centered
regulator activity is directionally concordant in discovery, internal validation and
GSE135779, survives its nominated multiplicity rule, and is not reproduced by the
negative controls or technical families.

If this gate fails, retain the strong multi-cohort descriptive IFN-remodeling paper
and remove mechanistic language. The independent IFN replication remains valid.

## Immediate next action

Create a manuscript claim-to-evidence matrix from the audited C2B3 through C5B
decisions, then revise the research proposal, Results, Methods, Discussion and figure
captions around the frozen central claim. In parallel, inventory available curated
regulon and perturbation resources without calculating regulator effects until the
Gate C6B contract is finalized.
