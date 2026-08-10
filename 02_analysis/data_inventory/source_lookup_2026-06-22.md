# Data Source Lookup - 2026-06-22

This note records live source checks for the first-pass SLE B-cell analysis.

## Perez et al. / GSE174188

Primary study:

- Perez et al., Science 2022.
- Local PDF: `PAPER/science.abf1970.pdf`.
- Main accession: `GSE174188`.
- Related earlier accession: `GSE137029`.
- HCA project: `9fc0064b-84ce-40a5-a768-e6eb3d364ee0`.
- CELLxGENE collection: `436154da-bcf1-4130-9c8b-120ff9a888f2`.
- dbGaP study: `phs002812.v1.p1`.

Live source findings:

- GEO describes 1.2 million PBMCs from 162 SLE cases and 99 controls.
- GEO states that raw and processed data are made available through dbGaP controlled access because of patient privacy concerns.
- HCA Data Explorer lists the project as access granted and links to CELLxGENE plus a Zenodo resource associated with the original publication.
- CELLxGENE collection API lists one dataset:
  - Collection ID: `436154da-bcf1-4130-9c8b-120ff9a888f2`.
  - Dataset ID: `218acb0f-9f2f-4f76-b90b-15a4b7c7f629`.
  - Dataset title: multiplexed scRNA-seq of 1.2 million PBMCs from adult lupus samples.
  - Cell count: 1,263,676.
  - H5AD asset size: 12,218,105,530 bytes.
  - H5AD URL: `https://datasets.cellxgene.cziscience.com/c55dc602-d168-4d15-acc1-5de4f2f5d551.h5ad`.
- A newer Zenodo record, `10.5281/zenodo.20406617`, published on 2026-05-27, provides processed files derived from `COMBAT-CITESeq-DATA.h5ad`:
  - `perez_sle_sobj_meta.csv.gz`, 55.8 MB.
  - `SLE_scRNA_GSE174188_perez_bpcells.tar.zst`, 1.4 GB.

Interpretation:

- Best formal provenance: original paper, GEO, HCA/CELLxGENE, and dbGaP policy.
- Fastest practical route: use HCA/CELLxGENE or the 2026 Zenodo BPCells conversion if direct H5AD access is inconvenient.
- Manuscript wording should avoid implying that controlled-access genotype data were used unless dbGaP access is actually granted.

Risk notes:

- The 2026 Zenodo record appears to be a convenience redistribution/conversion, not the original author-hosted primary repository.
- Before using it in the final manuscript, record DOI, license, MD5, download date, and transformation details.
- If reviewer sensitivity is expected, prefer HCA/CELLxGENE-derived files or dbGaP-authorized files.

## Immediate Recommendation

Use Perez/GSE174188 as the first discovery dataset only after one of these is available locally:

1. HCA/CELLxGENE H5AD or equivalent processed matrix.
2. The Zenodo BPCells matrix plus metadata.
3. dbGaP-authorized processed files.

The fastest first pass is option 2, but the cleanest provenance is option 1 or 3.

Prepared scripts:

- CELLxGENE route: `02_analysis/scripts/00_download_perez_gse174188_cellxgene.ps1`.
- Zenodo BPCells route: `02_analysis/scripts/00_download_perez_gse174188_zenodo.ps1`.
