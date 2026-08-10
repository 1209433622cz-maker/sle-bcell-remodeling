# Figure 1 v7 technical quality control

**Review date:** 2026-08-10  
**Status:** PASS as a design/QC figure; not manuscript-frozen before Gate C2B1 review.

## Reproducibility

- Generator: `02_analysis/scripts/50_make_v7_figure1_study_design.py`
- Generator SHA256: `4495AED2EA0FD8ED3EB698BE9E7A134E07C9BD3A2516BD1B5E37685C39BCA486`
- Strict-support re-audit generator SHA256: `14733683E7A9BA597671CA869E25F4A127AD960CEC64A0B9B945272ABD986EB4`
- Gate C1 donor-manifest source SHA256: `9A10E0C85505B1B58B5E54B142DD5DB8B71C1C8AF14C104DF5384EBD3350B1E5`
- Programmatically reproduced strict-support table SHA256: `1B374DEA672EDA7C81F0C83DF904B7AB4FA1001A40A1032E77E7B33C3AA61DD4`
- Gate C1 common-support source SHA256: `F78FD7F77D5D29C4AC21814292D6836491FDA98D563669EF34D9873D44BEAAB0`
- Gate C1 sample-manifest source SHA256: `B724C2EC2D9767EE2FC94AA8D2CAEF3B484B11D2FFE02235E077899A78C940B0`
- Gate C2B1 retention source SHA256: `EC6F436AC354D716182253B61A045C1EEC91D06BBD4F9BDF197705768DA91379`
- Script syntax compilation: PASS.
- Source assertions for 259 donors, 271 samples, 1,373 sample-library records, 88 libraries, 11 repeated donors, 53 bridge samples and 195 strict biological units: PASS.

## Export checks

- PNG: 4,322 x 3,590 pixels at 600 x 600 dpi; SHA256 `E923559CC2127DB6D1D14E22172522CDD601EF974C4E6A98FF7F43D5390BFFD7`.
- PDF: 518.740 x 430.866 pt (183.00 x 152.00 mm), one page; SHA256 `3647C02B46D301DD3FCCE291AAB27A0C78E28AB96D7A68FD7D0BD237B8EAABBF`.
- PDF fonts: subset-embedded Arial and Arial Bold TrueType; Unicode mapping present.
- Background: white; panel labels: lowercase bold; line/text content remains vector in PDF.
- Visual inspection at original resolution: PASS for clipping, overlap, legibility, panel ordering and color discrimination.
- Nature-style revision: no background gridlines; explanatory text is black/gray; color is reserved for symbols and categorical bars; hard-QC exclusions are plotted from zero.

## Scientific checks

- Panel a states the outcome-lock sequence and does not imply that doublet exclusion is complete.
- Panel b separates biological units from technical units.
- Panel c distinguishes sample-cohort records from the programmatically reproduced subset of donors with exactly one sample and one cohort.
- Panel d reports descriptive cell exclusion fractions from a zero baseline and does not treat cells as inferential replicates.
- Panel e restricts cohort roles according to common support; bridge samples are technical diagnostics only.
- The associated legend explicitly marks the figure as pre-freeze and defines all denominators.

## Required update before manuscript freeze

After Gate C2B1 doublet review, update panel a with the accepted singlet/sensitivity-branch cell totals and rerun this script from frozen sources. Do not edit the rendered PDF or PNG manually.
