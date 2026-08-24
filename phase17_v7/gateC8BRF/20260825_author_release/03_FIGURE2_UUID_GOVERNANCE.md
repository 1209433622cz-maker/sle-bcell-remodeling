# Figure 2 UUID governance audit

**Decision:** `PASS_FIGURE2_PUBLIC_NON_IDENTIFYING_SOURCE_UUIDS`

The 90 unique values in `sample_uuid` and `omitted_sample_uuid` are retained. They are UUIDv4 identifiers carried from the public CELLxGENE H5AD `obs.sample_uuid` field through the frozen Gate C3 model matrix and Gate C3A leave-one-out analysis. All 90 publication values map to those frozen inputs; none is locally generated for a patient, and no direct identifying field is present in Figure 2 Source Data.

Public provenance: https://cellxgene.cziscience.com/collections/436154da-bcf1-4130-9c8b-120ff9a888f2

- Public source H5AD: Data/processed/GSE174188_perez_cellxgene/perez_gse174188_cellxgene.h5ad
- Public asset size: 12,218,105,530 bytes, matching the CELLxGENE metadata
- Public H5AD `sample_uuid` levels: 274
- Figure 2 UUID union: 90
- UUID version set: [4]
- Unmapped publication IDs: 0
- Direct identifier columns: 0

No substitution with a local analysis index is required.
