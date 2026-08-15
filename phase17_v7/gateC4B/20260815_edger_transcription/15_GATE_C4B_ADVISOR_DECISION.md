# Gate C4B advisor decision

## `PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION`

The frozen B_CONV transcription analysis passes to independent validation. The central anchor is the pre-registered IFN/ISG program, not the number of significant genes.

| Frozen program | Primary effect | Primary BH q | Validation effect | Nonoverlap effect | Central criteria |
|---|---:|---:|---:|---:|---:|
| Naive-to-memory axis | -0.541 | 0.0213 | -0.581 | -0.443 | PASS |
| Atypical/ABC with low-naive context | -0.057 | 0.748 | -0.120 | 0.184 | NO |
| Antigen-presentation program | 0.268 | 0.0213 | 0.361 | 0.340 | PASS |
| Type I interferon response | 0.837 | 2.98e-06 | 0.856 | 1.086 | PASS |

## Principal finding

- IFN/ISG: primary effect `0.837` (95% CI `0.525` to `1.148`, BH q `2.98e-06`).
- Internal validation: full C2 effect `0.856` (q `0.00462`); donor-nonoverlap effect `1.086` (q `0.000361`).
- Direction is stable at B_CONV thresholds 20 and 100 and in the residual-risk-negative branch; all 89 leave-one-sample-out effects retain the sign.
- Leading primary genes are coherent interferon-response genes rather than technical or ambient families.

## Secondary interpretation

Naive-to-memory and APC/HLA pass frozen directional and influence checks but lack multiplicity-supported internal validation; they are supporting axes, not co-equal central claims. The atypical/low-naive program is negative.

The significant pan-B identity control is retained as an explicit caution. It is smaller than the IFN effect and does not coincide with platelet/ASC contamination or ranked technical-family dominance, but it requires direct review in external datasets.

## Scope control

Cohort 2 is internal replication within GSE174188. This gate does not yet support an upper-Q1 mechanistic claim, does not authorize B_ASC gene-level inference, and does not establish treatment-independent causality.

## Next gate

Proceed to Gate C5. Use GSE135779 as the principal independent SLE validation layer, GSE163121 only as smaller directional support, and OneK1K as healthy immune-reference context. Freeze external mapping and the IFN/ISG score before inspecting external disease effects.
