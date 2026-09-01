# S3/S5 Source-Redraw Specification

Status: `SOURCE_REDRAW_REQUIRED_FROM_FROZEN_DATA`

## Scientific adjudication

This is a display-pruning round only. No biological estimate, model, threshold, multiplicity family or Source Data object is changed.

### Supplementary Figure S3

Current 4-panel figure -> proposed 2-panel figure.

- REMOVE current S3a from display.
  - Evidence owner becomes Figure 1b.
  - Exact duplicate check: `True`.
  - The four policy rows have byte-for-value identical median/minimum mapped ARI and mapping-agreement values in the two Source Data objects.
- KEEP current S3b -> new S3a.
  - Unique role: localizes frozen-representation failure to fine-state membership.
- KEEP current S3c -> new S3b.
  - Unique role: mean transition structure from original resolution-0.4 clusters to mapped reference clusters.
- REMOVE current S3d from display.
  - Evidence owner becomes Figure 1d.
  - Exact duplicate check: `True`.
  - B_CONV and B_ASC median/minimum Jaccard values are identical in the two Source Data objects.

Recommended title:
`Supplementary Figure S3 | Fine-state failure and transition structure`

Recommended geometry:
- 170 mm width.
- Start at ~82 mm height; two side-by-side panels.
- No figure-wide title inside the graphic.
- Embedded Arial; minimum visible type 6 pt.
- Preserve current semantic encodings; do not add a replacement/filler panel.

### Supplementary Figure S5

Current 4-panel figure -> proposed 3-panel figure.

- KEEP current S5a -> new S5a.
- KEEP current S5b -> new S5b.
- KEEP current S5c -> new S5c.
- REMOVE current S5d from display.
  - Evidence owner becomes Figure 3b.
  - Exact duplicate check: `True`.
  - All seven rows are exactly equal for `analysis_name`, `effect`, `ci_low`, `ci_high`, and `q_value_primary4`.

Recommended title:
`Supplementary Figure S5 | Pseudobulk and ranked-list diagnostics`

Recommended geometry:
- 170 mm width.
- Prefer 2+1 layout: S5a/S5b on the top row and S5c spanning the lower row.
- Start at ~104 mm height and reduce only if 6-pt minimum text remains comfortable.
- No replacement/filler panel.

## Source Data policy

Do not edit or overwrite:
- `Supplementary_Figure_S3_source_data.csv`
- `Supplementary_Figure_S5_source_data.csv`
- `Figure1_source_data.csv`
- `Figure3_source_data.csv`

They remain frozen numerical provenance objects.

For the final display build, create a derived panel-mapping manifest only:

| frozen source panel | final display panel | action |
|---|---|---|
| S3a | - | display-pruned; owner Figure 1b |
| S3b | S3a | retained |
| S3c | S3b | retained |
| S3d | - | display-pruned; owner Figure 1d |
| S5a | S5a | retained |
| S5b | S5b | retained |
| S5c | S5c | retained |
| S5d | - | display-pruned; owner Figure 3b |

This prevents a presentation-only change from mutating the frozen scientific objects.
