# Content anomaly disposition

The strict format scan flags one source file:
`Data/processed/GSE135779_nehar_validation/source/libaries.csv`.

- Size: 540 bytes.
- SHA-256: `3A854C6D571616FE04299AE3C5052988C076E7F390608D0F5D2C18ABD17D7125`.
- The file is a molecule-info example template: Sample1 through Sample12,
  placeholder paths, a literal ellipsis row, and SampleX. It is not a 56-library
  data table. The ellipsis has one column rather than two.
- Disposition: preserve the original, do not invent missing rows, and do not use
  it as sample-level metadata. C9 only hashes this ancillary file. Actual sample
  parsing uses paired matrix/barcode members in the RAW archive.
- Scientific impact found: none on executed C9 selection or inference. This is
  an explicitly classified source-template anomaly, not an unreported PASS.

All original raw scan entries are retained in `content_issues.csv`.
