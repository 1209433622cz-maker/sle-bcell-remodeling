# B-Cell Signature Seed

This is a first-pass marker and program seed for annotation and scoring. It should be refined after checking the core papers and dataset-specific marker behavior.

## Cell Identity Markers

| State or program | Positive markers | Negative or contextual markers | Notes |
|---|---|---|---|
| Pan B cell | MS4A1, CD79A, CD79B, CD74, HLA-DRA | NKG7, LST1, CD3D | Use for B-cell extraction sanity check |
| Naive B cell | TCL1A, IGHD, IGHM, IL4R, FCER2, CCR7 | PRDM1, XBP1, JCHAIN | Expected to decrease in activated/disease-skewed compartments |
| Memory B cell | CD27, TNFRSF13B, AIM2, BANK1 | TCL1A low | Split further if dataset supports it |
| ABC/DN2-like B cell | TBX21, ITGAX, FCRL5, FCRL3, ZEB2, CXCR3, IFITM1 | CR2 low, FCER2 low, IGHD low | Central pathogenic state family for SLE |
| Plasmablast / antibody-secreting cell | MZB1, XBP1, PRDM1, JCHAIN, SDC1, IRF4, TNFRSF17 | MS4A1 low | Strongly distinct transcriptional endpoint |
| Activated memory-like B cell | CD69, CD83, CD86, NFKBIA, JUNB, FOS | TCL1A low | May overlap with antigen-presentation and inflammatory activation |
| APC-like B cell | HLA-DRA, HLA-DRB1, HLA-DPA1, HLA-DPB1, CD74, CIITA, CD86 | Plasma genes low to moderate | Important for EBV/APC-like SLE B-cell framing |

## Disease-Relevant Programs

| Program | Seed genes | Manuscript role |
|---|---|---|
| Type I interferon response | ISG15, IFIT1, IFIT2, IFIT3, MX1, MX2, OAS1, OAS2, IFI44L, IFI6 | Core SLE inflammatory program |
| TLR7 / innate sensing | TLR7, MYD88, IRAK1, IRF7, NFKB1, RELA, DDX58, IFIH1 | Links nucleic-acid sensing to B-cell activation |
| Antigen presentation | HLA-DRA, HLA-DRB1, HLA-DPA1, HLA-DPB1, CD74, CIITA, CD86 | APC-like B-cell state support |
| ABC / T-bet axis | TBX21, ITGAX, FCRL5, ZEB2, CXCR3, TLR7 | ABC/DN2-like state support |
| Plasmablast program | PRDM1, XBP1, MZB1, JCHAIN, IRF4, SDC1, TNFRSF17 | Antibody-secreting differentiation |
| FTO / m6A / metabolic anchor | FTO, ATP6V1G1, TLR7, MYD88 | Mechanistic anchor from FTO/TLR7 SLE ABC literature |
| BCR and activation | CD79A, CD79B, BLK, SYK, CD40, TNFRSF13B, NFKBIA | Contextual activation scoring |

## Rules For Use

- Do not use a marker list as proof of cell identity by itself.
- Confirm each annotated state by multiple markers and dataset-specific differential expression.
- Use program scores as supporting evidence, not as replacement for careful annotation.
- Keep ABC/DN2-like, activated memory-like, and APC-like labels flexible until the data show whether they separate cleanly.
