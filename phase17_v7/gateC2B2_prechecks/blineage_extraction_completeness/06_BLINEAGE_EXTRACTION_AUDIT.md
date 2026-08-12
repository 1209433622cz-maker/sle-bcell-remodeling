# B-lineage extraction completeness audit

**Status:** REVIEW REQUIRED; this audit does not relabel or append cells.

- Full PBMC cells: 1,263,676
- Source B cell/plasmablast labels: 152,981
- Cells outside source B labels: 1,110,695
- Strict B-like candidates outside source labels: 4,711 (0.424%)
- Candidate donors/samples/libraries: 260 / 273 / 88
- Disease fields used or exported: none

## Binding interpretation

The strict rule requires at least two B-specific genes, at least three genes
across the B/plasma panel and at least 75% B-panel purity relative to the
prespecified non-B marker panel. The full threshold grid is retained because no
single marker rule can establish cell identity on its own.

Review candidate source labels, marker combinations and later disease-blind
graph localization. Expand the B-lineage input only if a coherent, broadly
represented B-like population was materially omitted; otherwise retain the
source B/plasmablast definition and report this as completeness QC.
