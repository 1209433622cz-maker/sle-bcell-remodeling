# External advisor audit action crosswalk

**Source:** `external_advisor_full_audit_2026-08-10.md`  
**Source SHA256:** `83220891801D2ADD09214993B30A5E4BD800A176CC248AA22B07DC48D39432A3`  
**Decision:** accept the scientific recommendations; retain submission NO-GO.

## Implemented immediately

| Recommendation | Binding project action | Status |
|---|---|---|
| Treat the second Scrublet pass as residual risk | C2B1 report and code now state residual-risk diagnostic; no automatic re-deletion | implemented |
| Preserve thresholds on resume | paired per-library score CSV and summary JSON checkpoints | implemented and tested |
| Review more than one doublet score | added RNA-content and mixed-lineage marker review script | implemented and tested |
| Carry two cell branches | `all-hard-QC` primary; reviewed high-confidence-singlet sensitivity | frozen in methods |
| Use bridge samples as technical repeats | bridge concordance added to Gate C2B2/Figure 2 contract; excluded from primary disease coefficient | frozen in design |
| Prevent IFN-driven state circularity | library-aware recurrent HVGs plus ISG-excluded identity-stability reconstruction | frozen in design |
| Audit source B-lineage completeness | lightweight full-PBMC marker audit added before state freeze | frozen in design |
| Respect compositional dependence | global composition test precedes per-state effects; alternative compositional model retained | frozen in design |
| Stratify GSE135779 | childhood and adult effects estimated separately before any combined estimate | frozen in design |
| Use repeated donors carefully | paired within-person analysis is secondary after core freeze; no treatment-causal language | frozen in design |
| Keep five main Results/Figures | robustness attached to the result it protects; no sixth robustness Results chapter | implemented in blueprint |
| Tighten Figure 1 style | removed gridlines, replaced colored annotations with black text and plotted excluded fraction from zero | implemented by rerun |

## Pending computation

1. Complete all-library Gate C2B1 residual-risk scoring and multimetric review.
2. Run full disease-blind representation with recurrent-HVG and ISG-excluded branches.
3. Execute the full-PBMC B-lineage extraction completeness audit.
4. Quantify bridge-sample state, pseudobulk and mapping concordance after neutral states exist.
5. Freeze neutral states before unlocking protected outcomes.

## Deferred until the relevant freeze

- Composition, pseudobulk and repeated-donor paired models wait for Gate C2B3.
- Childhood/adult GSE135779 inference waits for frozen discovery mapping.
- Final journal selection waits for Figures 3-5.

## Current advisor decision

The external audit strengthens the v7 plan but does not authorize disease
analysis or submission. The immediate gate remains C2B1, followed by C2B2/C2B3.
