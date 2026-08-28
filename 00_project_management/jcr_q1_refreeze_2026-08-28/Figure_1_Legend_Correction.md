# Figure 1c correction integrated into the candidate

Status: INTEGRATED_CORRECTED_CANDIDATE_PENDING_APPROVAL.

The horizontal guide in Figure 1c denotes minimum mapping agreement, 0.990.
The frozen minimum mapped-ARI criterion is 0.900 and appears in Figure 1b.
The figure generator reads the agreement threshold from the frozen C2B4 JSON;
the new figure is regenerated rather than edited as a PDF. The corresponding
manuscript legend now says "minimum mapping-agreement criterion of 0.990".
Visual inspection also identified overlap between the interpretation boxes in
panel a. Their existing text is now wrapped over three lines; the builder checks
at least two points of clear space between adjacent boxes at the final width.

Figure1_source_data.csv remains byte-identical. No threshold, numerical result,
state identity, disease contrast or inference is changed. The exact before/after
phrases are enforced in verify_review_bundle.py. The omission claim is separately
qualified to "arguing against dependence on any single contributing source label".

The prior approved manuscript, cover letter and Figure 1 files are retained under
governance/prior_snapshot/ in the candidate package. The original author-confirmed
ZIP is preserved in full. Previous approval does not apply automatically to the
new candidate. Final journal choice, formatting, archive and submission remain
separate decisions. This record is not an author signature.
