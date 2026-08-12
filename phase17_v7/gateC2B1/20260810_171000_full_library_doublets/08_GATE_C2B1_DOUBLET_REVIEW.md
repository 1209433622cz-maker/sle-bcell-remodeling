# Gate C2B1 residual doublet-risk review

**Status:** REVIEW REQUIRED; no cells have been excluded from the authoritative full raw object.

The Perez source workflow already applied donor demultiplexing and doublet
handling. This second Scrublet pass is a residual-risk diagnostic, not an
independent mandate for another automatic deletion step.

- Input cells: 150,402
- Cells with Scrublet scores: 150,402
- Automatic predicted fraction: 1.31%
- Median library fraction: 1.22%
- Maximum library fraction: 6.49%
- Libraries above 20%: 0
- Libraries skipped below 100 eligible cells: 0
- Library errors: 0

Automatic calls are diagnostic until score distributions, library rates and
mixed-lineage marker enrichment are reviewed. The full raw object remains unchanged.
The primary branch retains all hard-QC cells; a high-confidence-singlet branch
is carried only as a sensitivity analysis until cluster-localization review is complete.
