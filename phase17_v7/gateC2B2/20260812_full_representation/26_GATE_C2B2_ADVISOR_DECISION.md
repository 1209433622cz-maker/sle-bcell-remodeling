# Gate C2B2 full-data advisor decision

**Decision:** `PASS_TO_C2B3_WITH_R04_IDENTITY_BACKBONE`

## Binding judgement

The full disease-blind representation run passes Gate C2B2. Resolution 0.4 is
frozen as the coarse identity backbone because it is the only biologically
covered candidate with strong agreement in both prespecified sensitivity branches.
It is not authorization to publish five final cell types. Resolutions 0.6 and 0.8
remain candidate substate layers and must survive Gate C2B3 resampling and marker review.

## Resolution evidence

| r | Clusters | Min cells | Min samples | Singlet ARI | ISG-excluded ARI | Status |
|---:|---:|---:|---:|---:|---:|---|
| 0.2 | 2 | 1,302 | 225 | 0.082 | 0.195 | not eligible |
| 0.4 | 5 | 1,251 | 225 | 0.793 | 0.772 | selected backbone |
| 0.6 | 6 | 1,307 | 226 | 0.561 | 0.428 | eligible |
| 0.8 | 7 | 1,319 | 227 | 0.702 | 0.432 | eligible |
| 1 | 9 | 4 | 4 | 0.706 | 0.381 | not eligible |
| 1.2 | 11 | 3 | 3 | 0.639 | 0.388 | not eligible |

## Biological interpretation

The targeted marker audit retains B-lineage identity across the backbone. At r=0.6,
one structure is plasmablast-program enriched and another is platelet-program enriched;
both labels remain provisional. The plasmablast structure is not rejected as generic
contamination because JCHAIN, MZB1, XBP1, TNFRSF17 and DERL3 are jointly elevated.

## Integrity

- Hashed files: 32
- Hashed bytes: 433,617,710
- Disease/outcome fields in working representation: none
- Outcome unlock: not authorized

## Next gate

Run Gate C2B3 with repeated disease-blind graph resampling, full-gene descriptive
marker ranking, and outside-label candidate projection. Only a passing C2B3 advisor
review may freeze neutral state labels and unlock sample-level disease analyses.
