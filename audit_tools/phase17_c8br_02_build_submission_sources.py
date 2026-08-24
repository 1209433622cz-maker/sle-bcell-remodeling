#!/usr/bin/env python3
"""Build Gate C8BR release-portability and reader-facing preflight sources."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BR" / "20260825_release_portability_preflight"
SOURCE = ROOT / "01_manuscript" / "manuscript_v13_genome_medicine_gateC8B_editorial_preflight_2026-08-21.md"
MANUSCRIPT = ROOT / "01_manuscript" / "manuscript_v14_genome_medicine_release_preflight_2026-08-25.md"
SUPPLEMENT_SOURCE = ROOT / "01_manuscript" / "supplementary_information_v4_gateC8B_editorial_preflight_2026-08-21.md"
SUPPLEMENT = ROOT / "01_manuscript" / "supplementary_information_v5_release_preflight_2026-08-25.md"
SUBMISSION = ROOT / "04_submission"
TITLE = "Disease-blind single-cell reconstruction separates unstable B-cell states from reproducible interferon remodeling in systemic lupus erythematosus"


def words(text: str) -> int:
    clean = re.sub(r"[`*_#|\[\]]", " ", text)
    return len(re.findall(r"\b[\w'-]+\b", clean))


def section(text: str, start: str, end: str | None) -> str:
    begin = text.index(start) + len(start)
    finish = text.index(end, begin) if end else len(text)
    return text[begin:finish].strip()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


def build_manuscript() -> tuple[str, int, int]:
    manuscript = SOURCE.read_text(encoding="utf-8-sig")
    placeholders = manuscript.count("[[")
    manuscript = replace_once(
        manuscript,
        "**Version:** Gate C8B editorial and literature preflight v13, 21 August 2026",
        "**Version:** Pre-submission release-portability preflight v14, 25 August 2026",
        "version line",
    )
    manuscript = replace_once(manuscript, "**Date:** 21 August 2026", "**Date:** 25 August 2026", "date line")
    manuscript = replace_once(
        manuscript,
        "These findings make cohort structure and disease context central to interpretation: a null primary composition estimate in managed SLE need not contradict plasmablast expansion in clinically enriched subgroups.",
        "These findings make cohort structure and disease context central to interpretation: a null primary composition estimate in the source-defined `managed` SLE category need not contradict plasmablast expansion in clinically enriched subgroups.",
        "source-defined managed label",
    )
    manuscript = replace_once(
        manuscript,
        "The primary expression result was then carried into independent GSE135779 under a pre-effect mapping and analysis contract.",
        "The primary expression result was then carried into independent GSE135779 under a prespecified mapping and analysis plan finalized before disease-effect estimation.",
        "Background analysis-plan wording",
    )
    manuscript = replace_once(
        manuscript,
        "technical- library",
        "technical library",
        "technical-library typo",
    )
    manuscript = replace_once(
        manuscript,
        "The primary comparison was processing cohort 4 managed SLE versus normal, adjusted for age and ethnicity. Internal processing-cohort-2 and secondary processing-cohort-3 flare analyses were estimated separately.",
        "The primary comparison was processing cohort 4 source-metadata `managed` SLE versus `normal`, adjusted for age and ethnicity. Internal processing-cohort-2 and secondary processing-cohort-3 analyses of the source-metadata `flare` category were estimated separately.",
        "source clinical-label definitions",
    )
    manuscript = replace_once(
        manuscript,
        "Real matrices were imported for dimension and count-conservation qualification only; synthetic null and signal data qualified the statistical engine before the real disease coefficients were unlocked.",
        "Real matrices were imported for dimension and count-conservation qualification only; synthetic null and signal data qualified the statistical engine before disease effects were estimated.",
        "external qualification wording",
    )
    manuscript = replace_once(
        manuscript,
        "Every gate used timestamped run directories, immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 integrity manifests. Real effects were calculated only after input, design and statistical- engine qualification.",
        "Analyses used timestamped run directories, immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 integrity manifests. Disease effects were calculated only after input, design and statistical engine qualification.",
        "reproducibility wording",
    )
    manuscript = replace_once(
        manuscript,
        "The primary analysis included 89 pseudobulks, comprising 43 reference and 46 SLE strata, and retained 59,873,385 UMI counts.",
        "One source-defined managed-SLE composition stratum contained 44 `B_CONV` cells after compartment assignment and therefore did not meet the prespecified 50-cell `B_CONV` threshold for transcriptional analysis. The primary analysis consequently included 89 pseudobulks, comprising 43 reference and 46 SLE strata, and retained 59,873,385 UMI counts.",
        "90-to-89 pseudobulk explanation",
    )
    manuscript = replace_once(
        manuscript,
        "The mapping contract authorized only a broad conventional-B analog constructed from source B-cell labels; it did not authorize transfer of hard naive-memory identities. Matrix import and edgeR behavior were qualified with count-conservation checks and synthetic null and signal data before the real external contrasts were unlocked.",
        "The prespecified external mapping allowed only a broad conventional-B analog constructed from source B-cell labels; hard naive-memory identities were not transferred. Matrix import and edgeR behavior were qualified with count-conservation checks and synthetic null and signal data before external disease effects were estimated.",
        "external mapping prose",
    )
    manuscript = replace_once(
        manuscript,
        "The contract was frozen before real regulator effects were inspected and included four IFN-centred regulators (STAT1, STAT2, IRF7 and IRF9), four proliferation controls (E2F1, FOXM1, MYC and MYBL2), and the three confirmatory contrasts used above.",
        "The regulator analysis was specified before regulator effects were inspected and included four IFN-centred regulators (STAT1, STAT2, IRF7 and IRF9), four proliferation specificity comparators (E2F1, FOXM1, MYC and MYBL2), and the three confirmatory contrasts used above.",
        "regulator plan and comparator wording",
    )
    manuscript = replace_once(
        manuscript,
        "The proliferation controls did not reproduce a positive globally significant pattern across all three contrasts.",
        "The proliferation specificity comparators did not reproduce a positive globally significant pattern across all three contrasts.",
        "regulator comparator result wording",
    )
    manuscript = replace_once(
        manuscript,
        "Fine-grained hard B-cell states were not stable under the prespecified disease-blind resampling contract, and the repaired model deliberately stopped at two broad compartments.",
        "Fine-grained hard B-cell state assignments did not meet the prespecified disease-blind resampling criteria, and the resulting model deliberately stopped at two broad compartments.",
        "Discussion identity wording",
    )
    discussion_anchor = (
        "Persistent IFN activity in antimalarial-treated patients with low disease activity stratified by polygenic risk [31] is likewise consistent with context-dependent interferon remodeling; because neither cohort nor frozen program is shared, it remains external biological context rather than independent validation of our effect."
    )
    manuscript = replace_once(
        manuscript,
        discussion_anchor,
        discussion_anchor
        + " Recent functional evidence links type I interferon exposure to B-cell activation and DN2 differentiation in SLE [32]. This supports the biological plausibility of interferon-responsive fine states, while our resampling result addresses a different question: whether a disease-blind hard fine-grained partition is stable enough to serve as a disease-inference unit in a heterogeneous public dataset.",
        "Faheem context boundary",
    )
    manuscript = replace_once(
        manuscript,
        "The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [14-16]. Analysis scripts, machine-readable decisions and derived source-data tables are available in the public project repository [17]. Gate C8S remains the canonical frozen scientific state; Gate C8B adds editorial and literature preflight only. An open-source licence and immutable archive DOI remain required for the final citable release.",
        "The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [14-16]. Version-controlled analysis scripts, machine-readable decisions, derived source-data tables and SHA-256 provenance records are available in the public project repository [17]. An author-approved open-source licence and immutable archive DOI remain required for the final citable release.",
        "reader-facing data availability",
    )
    manuscript = replace_once(
        manuscript,
        "**a,** Prespecified three-contrast, eight-regulator design, global 24-test Benjamini-Hochberg family and core target-robustness analyses.",
        "**a,** Parallel evidence architecture linking replicated IFN/ISG remodeling to a prespecified three-contrast, eight-regulator branch and a separate orthogonal-response branch without implying causal ordering.",
        "Figure 5a legend",
    )
    manuscript = replace_once(
        manuscript,
        "31. Sayadi A, Eloranta M-L, Oparina N, Wallgren M, Skoglund E, Frodlund M, et al. Single-cell RNA-seq reveals a persistent interferon signature in immune cells from systemic lupus erythematosus patients with high versus low polygenic risk scores despite antimalarial treatment. Journal of Autoimmunity. 2026;161:103575. doi:10.1016/j.jaut.2026.103575.",
        "31. Sayadi A, Eloranta M-L, Oparina N, Wallgren M, Skoglund E, Frodlund M, et al. Single-cell RNA-seq reveals a persistent interferon signature in immune cells from systemic lupus erythematosus patients with high versus low polygenic risk scores despite antimalarial treatment. Journal of Autoimmunity. 2026;161:103575. doi:10.1016/j.jaut.2026.103575.\n32. Faheem Z, Boukhaled GM, Nassar C, Manion K, Kim M, Bonilla D, et al. Type I interferons enhance B cell activation and promote differentiation of double negative 2 cells in SLE. Lupus Science & Medicine. 2026;13(1):e002042. doi:10.1136/lupus-2026-002042.",
        "Faheem reference",
    )

    abstract_words = words(section(manuscript, "## Abstract", "## Keywords"))
    references = [int(value) for value in re.findall(r"^(\d+)\.\s", section(manuscript, "## References", None), flags=re.M)]
    required = [
        TITLE,
        "source-defined `managed` SLE category",
        "44 `B_CONV` cells",
        "proliferation specificity comparators",
        "whether a disease-blind hard fine-grained partition is stable enough",
        "doi:10.1136/lupus-2026-002042",
        "Parallel evidence architecture",
        "Version-controlled analysis scripts",
    ]
    forbidden = [
        "technical- library",
        "statistical- engine",
        "proliferation controls",
        "The proliferation controls",
        "mapping contract authorized",
        "real external contrasts were unlocked",
        "real disease coefficients were unlocked",
        "Every gate used",
        "Gate C8S remains",
        "Gate C8B adds",
    ]
    missing = [token for token in required if token not in manuscript]
    present_forbidden = [token for token in forbidden if token in manuscript]
    if abstract_words > 350 or references != list(range(1, 33)) or missing or present_forbidden:
        raise RuntimeError(
            f"C8BR manuscript contract failed: abstract={abstract_words}; refs={len(references)}; "
            f"missing={missing}; forbidden={present_forbidden}"
        )
    if manuscript.count("[[") != placeholders:
        raise RuntimeError("Author-controlled placeholder count changed")
    return manuscript, abstract_words, placeholders


def build_supplement() -> str:
    supplement = SUPPLEMENT_SOURCE.read_text(encoding="utf-8-sig")
    supplement = replace_once(
        supplement,
        "**Version:** Gate C8B editorial and literature preflight, 21 August 2026",
        "**Version:** Pre-submission release-portability preflight, 25 August 2026",
        "supplement version",
    )
    supplement = replace_once(
        supplement,
        "Gate C8B inherits the frozen Gate C8S reviewer-facing evidence and statistical traceability without changing upstream estimates.",
        "This release-portability preflight inherits the frozen reviewer-facing evidence and statistical traceability without changing upstream estimates.",
        "supplement overview",
    )
    supplement = supplement.replace(
        "`phase17_v7/gateC8B/20260821_editorial_literature_preflight/02_PANEL_DATA_ASSERTIONS.json`",
        "`phase17_v7/gateC8BR/20260825_release_portability_preflight/02_PANEL_DATA_ASSERTIONS.json`",
    )
    supplement = supplement.replace(
        "`01_manuscript/manuscript_v13_genome_medicine_gateC8B_editorial_preflight_2026-08-21.md`",
        "`01_manuscript/manuscript_v14_genome_medicine_release_preflight_2026-08-25.md`",
    )
    supplement = replace_once(
        supplement,
        "## Supplementary Methods 1 | Gate governance and outcome protection",
        "## Supplementary Methods 1 | Prespecification and outcome protection",
        "supplement governance heading",
    )
    supplement = replace_once(
        supplement,
        "## Supplementary Table S6 | Reproducibility contract",
        "## Supplementary Table S6 | Reproducibility record",
        "supplement reproducibility heading",
    )
    supplement = replace_once(
        supplement,
        "The workflow used sequential gates for source integrity, hard quality control, disease-blind identity reconstruction, sample-level composition, within-compartment pseudobulk analysis, independent validation and external regulatory evidence. Protected disease fields were separated during identity reconstruction. Real outcome effects were unlocked only after the relevant input, mapping, contrast and statistical-engine contracts had been recorded. Each gate retained a machine-readable decision and SHA-256 integrity manifest.",
        "The workflow used prespecified stages for source integrity, hard quality control, disease-blind identity reconstruction, sample-level composition, within-compartment pseudobulk analysis, independent validation and external regulatory evidence. Protected disease fields were separated during identity reconstruction. Disease effects were estimated only after the relevant inputs, mappings, contrasts and statistical methods had been recorded. Each stage retained a machine-readable decision and SHA-256 integrity manifest.",
        "supplement governance prose",
    )
    supplement = supplement.replace("43 controls and 47 managed SLE", "43 controls and 47 source-defined managed SLE")
    return supplement


def build_auxiliary_sources() -> dict[str, Path]:
    source_paths = {
        "cover": SUBMISSION / "cover_letter_genome_medicine_gateC8B_AUTHOR_COMPLETION_REQUIRED_2026-08-21.md",
        "author_completion_matrix": SUBMISSION / "author_completion_form_gateC8B_2026-08-21.md",
        "journal_target_decision": SUBMISSION / "journal_target_decision_gateC8B_2026-08-21.md",
        "reporting_checklist": SUBMISSION / "reporting_checklist_gateC8B_2026-08-21.md",
    }
    missing = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing tracked C8B source templates: {missing}")

    outputs = {
        "cover": SUBMISSION / "cover_letter_genome_medicine_gateC8BR_AUTHOR_COMPLETION_REQUIRED_2026-08-25.md",
        "author_completion_matrix": SUBMISSION / "author_completion_matrix_gateC8BR_2026-08-25.md",
        "journal_target_decision": SUBMISSION / "journal_target_decision_gateC8BR_2026-08-25.md",
        "reporting_checklist": SUBMISSION / "reporting_checklist_gateC8BR_2026-08-25.md",
    }

    cover_source = source_paths["cover"]
    cover = cover_source.read_text(encoding="utf-8-sig")
    cover = replace_once(cover, "21 August 2026", "25 August 2026", "cover date")
    cover = replace_once(
        cover,
        "Independent M5911 enrichment and paired IFN-beta perturbation profiles supplied orthogonal response evidence.",
        "Orthogonal enrichment of the independently curated M5911 response set and paired IFN-beta perturbation profiles supplied complementary response evidence.",
        "cover M5911 independence wording",
    )
    cover_path = outputs["cover"]
    cover_path.write_text(cover, encoding="utf-8", newline="\n")

    matrix = source_paths["author_completion_matrix"].read_text(encoding="utf-8-sig")
    matrix = matrix.replace("# Gate C8B author completion form", "# Gate C8BR release and author-completion matrix")
    matrix = matrix.replace(
        "Gate C8B scientific and technical repair is complete.",
        "The scientific analysis remains frozen; release portability and reader-facing repairs are complete.",
    )
    matrix = matrix.replace(
        "- [x] Corresponding author email and official institutional postal address.",
        "- [x] Corresponding author email supplied by the author.\n"
        "- [x] Official School postal address independently matched to the School of Medicine contact page on 25 August 2026: "
        "<https://med.cuhk.edu.cn/en/page/1489>.\n"
        "- Confirm that Teng Qi approves use of this institutional postal address for correspondence in the submission.",
    )
    matrix += """

## Code-owned preflight completed on 25 August 2026

- [x] Pinned release environment and PNG/PDF savefig smoke test added.
- [x] Runner resolves explicit parameters, environment variables, named conda environments and PATH without machine-local defaults.
- [x] Figure 5a rebuilt as parallel regulatory and response-evidence branches.
- [x] Figure 5 source data remain byte-identical to Gate C8B.
- [x] Main-text copyediting, comparator terminology, source-label definitions and 90-to-89 explanation completed.
- [x] Faheem et al. 2026 added as functional context with a non-replication boundary.
- [x] Full Statistical Results remain byte-identical to the scientific freeze.

## Author-controlled hard stop

Submission remains unauthorized until every unchecked author, institution, licence and archive item above is documented. Do not infer or auto-fill these facts.
"""
    outputs["author_completion_matrix"].write_text(matrix, encoding="utf-8", newline="\n")

    target = source_paths["journal_target_decision"].read_text(encoding="utf-8-sig")
    target = target.replace("Gate C8B", "Gate C8BR")
    target += """

## Release-portability preflight decision

Genome Medicine remains the primary target. The scientific analysis is closed. Gate C8BR repairs release portability, reader-facing prose and Figure 5a semantics without changing estimates. Faheem et al. (2026; doi:10.1136/lupus-2026-002042; PMID 42373139) is functional context rather than replication. The next stage is author completion, licence approval, immutable archive DOI, zero-placeholder rebuild and portal preflight.
"""
    outputs["journal_target_decision"].write_text(target, encoding="utf-8", newline="\n")

    checklist = source_paths["reporting_checklist"].read_text(encoding="utf-8-sig")
    checklist = checklist.replace("Gate C8B", "Gate C8BR")
    checklist += """

## Gate C8BR additions

- [x] Figure 5a depicts regulatory and orthogonal-response evidence as parallel branches.
- [x] Source-defined clinical labels are identified in the main text.
- [x] The 90 composition strata versus 89 transcriptional pseudobulks are reconciled.
- [x] Portable release environment and savefig qualification are version controlled.
- [ ] Author-controlled declarations, licence, immutable DOI and portal metadata remain pending.
"""
    outputs["reporting_checklist"].write_text(checklist, encoding="utf-8", newline="\n")
    return outputs


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manuscript, abstract_words, placeholders = build_manuscript()
    supplement = build_supplement()
    MANUSCRIPT.write_text(manuscript, encoding="utf-8", newline="\n")
    SUPPLEMENT.write_text(supplement, encoding="utf-8", newline="\n")
    auxiliary = build_auxiliary_sources()
    status = {
        "created_at": "2026-08-25",
        "status": "PASS_GATE_C8BR_RELEASE_PREFLIGHT_SOURCES_BUILT",
        "source_gate": "C8S frozen scientific state",
        "scientific_estimates_changed": False,
        "abstract_words": abstract_words,
        "references": 32,
        "author_controlled_placeholders": placeholders,
        "authors_information_section_present": False,
        "new_reference": {"doi": "10.1136/lupus-2026-002042", "pmid": "42373139", "role": "functional context only"},
        "figure5a_semantics": "parallel evidence branches",
        "figure5c_wording": "Prespecified proliferation specificity comparators",
        "pseudobulk_reconciliation": "90 composition strata; one managed stratum had 44 B_CONV cells; 89 transcription pseudobulks",
        "outputs": {
            "manuscript": MANUSCRIPT.relative_to(ROOT).as_posix(),
            "supplement": SUPPLEMENT.relative_to(ROOT).as_posix(),
            **{key: value.relative_to(ROOT).as_posix() for key, value in auxiliary.items()},
        },
    }
    (RUN_DIR / "03_GATE_C8BR_SOURCE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
