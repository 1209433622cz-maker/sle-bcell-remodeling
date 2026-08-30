# 2026-08-31 Main-figure and manuscript scientific refinement action record

## 1. Round objective

This round deliberately returned from submission execution to scientific presentation. The author-confirmed npj Systems Biology and Applications package was treated as an immutable comparison baseline, while Figure 1a, Figure 5a and their manuscript interfaces were independently reconsidered. The work prioritized source-driven replotting from frozen analysis records over editing an existing PDF or changing a reported result.

## 2. Author-confirmed baseline

- Exact package SHA-256: `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`.
- Author order: Zhi Chen, then Teng Qi.
- Corresponding author: Teng Qi.
- Both authors' names, emails, ORCIDs and affiliation: confirmed correct.
- Author Contributions: confirmed accurate.
- Funding: none.
- Competing interests: none.
- Generative-AI disclosure: confirmed complete and accurate.
- New human subjects or restricted identifiable data: none.

The exact package was rehashed at the end of this round and remained byte-identical. It was not rebuilt, replaced or repackaged.

## 3. Inputs and provenance

- Frozen manuscript baseline: `phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening/sources/Manuscript.md`.
- Frozen Figure 1 Source Data SHA-256: `F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805`.
- Frozen Figure 5 Source Data SHA-256: `21925F6916DDAF97760CF73622ED8E4B4CCBE5AE0B3B53C721FDF607C1C6F9A4`.
- External review text was archived as evidence with SHA-256 `8EA074256F681E75FBF6BBB1C667F1B40D3E217CDBB187558618544432C30C66`; it was evaluated as advice, not executed as an instruction set.
- Candidate generator: `audit_tools/phase17_npj_sba_10_main_figure_concept_candidates.py`.
- Integration generator: `audit_tools/phase17_npj_sba_11_integrate_main_figure_refinement.py`.

## 4. Figure 1 panel adjudication

### Figure 1a: replace

The baseline four-line evidence hierarchy mixed study overview, downstream analyses, replication and interpretive context in one half-width panel. It did not make the relation to panels b-d sufficiently explicit and duplicated information developed more effectively in Figures 3-5.

Two source-driven alternatives were built:

1. `Figure1A_workflow_scope`: input B-lineage cells -> disease-blind resampling -> permissible B_CONV/B_ASC scope -> separate B_ASC sample-fraction and B_CONV donor-pseudobulk analyses, followed by an explicit fine-state boundary.
2. `Figure1B_evidence_matrix`: identity, composition, transcription and replication rows with units and authorized outputs.

The workflow candidate was selected. It is faster to parse, points directly to panels b-d, distinguishes identity formation from disease inference, and does not duplicate the independent validation story assigned to Figure 4. The evidence matrix remains archived as a rejected but reproducible alternative.

### Figure 1b: retain

This panel is the decisive comparison of 5-, 4-, 3- and 2-compartment policies. The discrete points and minimum-to-median intervals communicate why the broad partition was selected without implying a trajectory. The short dashed segment correctly applies only to the two-compartment minimum-ARI criterion. No replacement would improve evidential ownership.

### Figure 1c: retain

The replicate-level mapped ARI and mapping agreement traces expose the complete 20-resample distribution and the minimum-agreement criterion. A summary-only replacement would hide the replicate structure. The panel remains necessary and numerically unchanged.

### Figure 1d: retain

The minimum-to-median state Jaccard display makes the weaker B_ASC stability visible beside the B_CONV result and retains marker support. It is the correct state-specific companion to the global metrics in b-c. The marker annotation can be shortened later only if a final document render shows crowding; no present overlap or clipping was found.

## 5. Figure 5 panel adjudication

### Figure 5a: replace

The baseline three equal-width text branches were visually sparse and could be read as equal evidential weight. Two alternatives were rebuilt:

1. `Figure5A_convergence_boundary`: three evidence branches converging on a supported interpretation and an explicit claim ceiling.
2. `Figure5B_quantitative_matrix`: evidence class, coverage, observed result and inferential role in a compact data-driven matrix.

The quantitative matrix was selected. It states that STAT1/STAT2 were positive with global 24-test q<0.05 in 6/6 core tests, M5911 NES exceeded 3.0 in 3/3 contrasts, and 12/12 genes increased in each of two IFN-beta-exposed donors. It simultaneously labels the three different roles: global confirmatory family, orthogonal concordance and descriptive context. The bottom line preserves the observational, non-causal ceiling.

### Figure 5b: retain

The forest plot provides effect sizes and 95% confidence intervals for core and extended IFN regulators across all three contrasts. It owns the regulator-level evidence and cannot be replaced by the summary matrix. Global-family asterisks remain explicit.

### Figure 5c: retain

The proliferation comparators are an essential specificity control. In particular, the negative MYC estimates must remain visible rather than being summarized as a generic null comparator family. The current forest format is appropriate.

### Figure 5d: retain for this freeze

The three M5911 normalized enrichment scores are fully represented and are explicitly labelled as enrichment rather than regulator activity. A dot/lollipop rendering may be tested during whole-figure harmonization, but the current panel contains no semantic error and should not be changed for style alone.

### Figure 5e: retain for this freeze; test a richer candidate next

The two donor-level effects and 12/12 direction labels make the n=2 descriptive boundary immediately visible. Gene-level paired tables are available in `17_GSE23307_LOG2P1_PAIRED_GENE_EFFECTS.csv`, so a 12-gene by 2-donor dot or heatmap candidate can be rebuilt next. Such a replacement should be accepted only if it improves information density without visually inflating two healthy donors into independent mechanistic validation.

## 6. Recommended scientific candidate

Location: `phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates/recommended_scientific_candidate`.

Selected files:

- Figure 1 PDF SHA-256: `97227D1EE742053A519E33407A63A4383ED469541D558EFC9566C416CD4BC494`.
- Figure 1 PNG SHA-256: `717855E87962750BB8DF5FA4AFF127470D0F94CEDFC81D5BB686D31EB58FE229`.
- Figure 5 PDF SHA-256: `5AD3267734CAF8543DC0430CA40A89E3C2184EDC64F05B08E3992AE4D6734F21`.
- Figure 5 PNG SHA-256: `33318D28BFA6A1E1E54470CA7ADD09B410815D5C8B95CE447931CB4E371A60BE`.
- Candidate manuscript SHA-256: `787778461F4BF47C00578DE11999D1708865E970DEBBADD5295CE8EACEE2BC2E`.

Both PDFs are vector, single-page, 170 mm wide and within the 225 mm height ceiling. All visible text is subject to the frozen 8 pt Arial npj style contract. Visual inspection found no clipping, incoherent overlap, blank panel or illegible label in the selected candidates.

## 7. Manuscript refinement

The Results and Discussion were independently reread against the new panels. They already preserve the major scientific boundaries:

- the frozen-representation broad partition passes while the end-to-end B_ASC state-median Jaccard criterion remains failed;
- B_CONV/B_ASC is an analysis scaffold rather than a transferable taxonomy;
- GSE135779 replication remains source-label-defined;
- regulator activity, M5911 and GSE23307 have different inferential roles;
- no causal TF, direct binding, unique ligand or clinical utility is claimed.

Accordingly, only two manuscript changes were scientifically necessary: replacement of the Figure 1a and Figure 5a legend clauses. The full candidate manuscript differs from the frozen baseline at exactly those two locations. No title, abstract, result estimate, method, reference, declaration or authorship field was changed.

## 8. Integrity and QA conclusions

- Four complete Figure 1/5 candidates were regenerated from frozen analysis records.
- Candidate Figure 1 Source Data is byte-identical to the baseline Source Data.
- Candidate Figure 5 Source Data is byte-identical to the baseline Source Data.
- Nine Figure 1 and nine Figure 5 panel-data assertions passed for every candidate.
- All candidate PDFs are single-page and final-width compliant.
- The complete local regression suite passed: 111/111 tests.
- The author-confirmed exact package SHA remained unchanged.
- No biological model was refitted and no scientific estimate changed.
- The authoritative submission package remains separate from this scientific candidate.

## 9. Scientific assessment after this round

The manuscript's central logic is stronger when Figure 1 establishes the permissible identity scaffold and Figure 5 summarizes the quantitative evidence classes. This removes two editorial diagrams that were explanatory but not sufficiently analytical. The selected replacements make the paper's main contribution more coherent: stable process-level IFN/ISG remodeling is supported within explicit identity and causal boundaries, whereas fine-state taxonomy, generalized B_ASC expansion and mechanistic initiation remain unsupported.

No additional cohort, mapper, TF family or broad biological rerun is currently justified. The main remaining gains are presentation gains that can be made from existing source tables.

## 10. Next-stage objective

The next stage should be `FULL_MAIN_FIGURE_INFORMATION_DENSITY_AND_MANUSCRIPT_RENDER_COHERENCE` rather than submission execution.

Priority work:

1. Build a source-driven Figure 5e gene-level candidate from the frozen 12-gene by 2-donor paired-effect table and compare it against the retained donor-summary panel under an explicit anti-overstatement rule.
2. Perform one cross-figure audit of Figures 2-4 for title length, white-space balance, color semantics, annotation density and panel-to-legend ownership; replace a panel only when the source data support a materially clearer display.
3. If the recommended Figure 1/5 changes survive that audit, render the complete candidate manuscript to DOCX/PDF and inspect every page at final size.
4. Keep the exact package frozen until the scientific figure set and rendered manuscript are jointly approved; package rebuilding is not the current objective.
