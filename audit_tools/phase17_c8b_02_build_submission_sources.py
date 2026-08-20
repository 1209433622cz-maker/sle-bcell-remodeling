#!/usr/bin/env python3
"""Build Gate C8B editorial and literature preflight sources from frozen C8S."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8B" / "20260821_editorial_literature_preflight"
SOURCE = ROOT / "01_manuscript" / "manuscript_v12_genome_medicine_gateC8S_2026-08-21.md"
MANUSCRIPT = ROOT / "01_manuscript" / "manuscript_v13_genome_medicine_gateC8B_editorial_preflight_2026-08-21.md"
SUPPLEMENT_SOURCE = ROOT / "01_manuscript" / "supplementary_information_v3_gateC8S_2026-08-21.md"
SUPPLEMENT = ROOT / "01_manuscript" / "supplementary_information_v4_gateC8B_editorial_preflight_2026-08-21.md"
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
        "**Version:** Gate C8S supplementary evidence and traceability freeze v12, 21 August 2026",
        "**Version:** Gate C8B editorial and literature preflight v13, 21 August 2026",
        "version line",
    )

    background_anchor = (
        "Large transcriptomic analyses likewise identify multiple molecular endotypes that are not uniformly represented across datasets [18]. "
        "These findings make cohort structure and disease context central to interpretation: a null primary composition estimate in managed SLE need not contradict plasmablast expansion in clinically enriched subgroups."
    )
    background_replacement = background_anchor + (
        " Recent single-cell profiling of 16 women with SLE in low disease activity on antimalarial treatment further showed that interferon activity varied with polygenic-risk burden across several immune compartments [31]. "
        "That study reinforces the need to separate persistent interferon-responsive state from disease activity and treatment context, but it did not test our disease-blind B_CONV program and is therefore contextual rather than replication evidence."
    )
    manuscript = replace_once(manuscript, background_anchor, background_replacement, "Background literature anchor")

    discussion_anchor = (
        "In particular, the reported plasmablast expansion in patients with higher activity and Sm/RNP autoantibodies [19] is compatible with our secondary positive flare estimate and our null primary managed-SLE estimate. "
        "The contribution here is the identification of the layer that survives a disease-blind, biological-replicate-aware and cross-cohort validation sequence, not a claim that interferon involvement itself is newly discovered."
    )
    discussion_replacement = discussion_anchor + (
        " Persistent IFN activity in antimalarial-treated patients with low disease activity stratified by polygenic risk [31] is likewise consistent with context-dependent interferon remodeling; because neither cohort nor frozen program is shared, it remains external biological context rather than independent validation of our effect."
    )
    manuscript = replace_once(manuscript, discussion_anchor, discussion_replacement, "Discussion literature anchor")

    author_information = (
        "### Authors' information\n\n"
        "Zhi Chen is an MSc student in Bioinformatics at The Chinese University of Hong Kong, Shenzhen. His research focuses on multi-omics integration, clinical cancer research and analysis of the tumour microenvironment. He holds a BSc in Biomedical Sciences from Queen Mary University of London and an MB in Clinical Medicine from Nanchang University. Teng Qi is an MSc student in Bioinformatics at The Chinese University of Hong Kong, Shenzhen.\n\n"
    )
    manuscript = replace_once(manuscript, author_information, "", "optional Authors' information section")
    manuscript = replace_once(
        manuscript,
        "**c,** Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation controls.",
        "**c,** Prespecified E2F1, FOXM1, MYC and MYBL2 proliferation specificity comparators.",
        "Figure 5c legend wording",
    )
    manuscript = replace_once(
        manuscript,
        "30. Barnas JL, Albrecht J, Meednu N, Alzamareh DF, Baker C, McDavid A, et al. B Cell Activation and Plasma Cell Differentiation Are Promoted by IFN-lambda in Systemic Lupus Erythematosus. The Journal of Immunology. 2021;207(11):2660-2672. doi:10.4049/jimmunol.2100339.",
        "30. Barnas JL, Albrecht J, Meednu N, Alzamareh DF, Baker C, McDavid A, et al. B Cell Activation and Plasma Cell Differentiation Are Promoted by IFN-lambda in Systemic Lupus Erythematosus. The Journal of Immunology. 2021;207(11):2660-2672. doi:10.4049/jimmunol.2100339.\n31. Sayadi A, Eloranta M-L, Oparina N, Wallgren M, Skoglund E, Frodlund M, et al. Single-cell RNA-seq reveals a persistent interferon signature in immune cells from systemic lupus erythematosus patients with high versus low polygenic risk scores despite antimalarial treatment. Journal of Autoimmunity. 2026;161:103575. doi:10.1016/j.jaut.2026.103575.",
        "new Sayadi reference",
    )
    manuscript = replace_once(
        manuscript,
        "Gate C8S is the current canonical analysis state; an open-source licence and immutable archive DOI remain required for the final citable release.",
        "Gate C8S remains the canonical frozen scientific state; Gate C8B adds editorial and literature preflight only. An open-source licence and immutable archive DOI remain required for the final citable release.",
        "canonical state declaration",
    )

    abstract_words = words(section(manuscript, "## Abstract", "## Keywords"))
    references = [int(value) for value in re.findall(r"^(\d+)\.\s", section(manuscript, "## References", None), flags=re.M)]
    required = [
        TITLE,
        "polygenic-risk burden",
        "contextual rather than replication evidence",
        "external biological context rather than independent validation",
        "proliferation specificity comparators",
        "doi:10.1016/j.jaut.2026.103575",
        "Gate C8S remains the canonical frozen scientific state",
    ]
    missing = [token for token in required if token not in manuscript]
    if abstract_words > 350 or references != list(range(1, 32)) or missing:
        raise RuntimeError(
            f"C8B manuscript contract failed: abstract={abstract_words}; refs={len(references)}; missing={missing}"
        )
    if manuscript.count("[[") != placeholders or "### Authors' information" in manuscript:
        raise RuntimeError("Author-control placeholders changed or optional author biography remains")
    return manuscript, abstract_words, placeholders


def build_supplement() -> str:
    supplement = SUPPLEMENT_SOURCE.read_text(encoding="utf-8-sig")
    supplement = replace_once(
        supplement,
        "**Version:** Gate C8S, 21 August 2026",
        "**Version:** Gate C8B editorial and literature preflight, 21 August 2026",
        "supplement version",
    )
    supplement = replace_once(
        supplement,
        "Gate C8S freezes reviewer-facing supplementary evidence and statistical traceability without changing upstream estimates.",
        "Gate C8B inherits the frozen Gate C8S reviewer-facing evidence and statistical traceability without changing upstream estimates.",
        "supplement overview",
    )
    supplement = supplement.replace(
        "`phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/02_PANEL_DATA_ASSERTIONS.json`",
        "`phase17_v7/gateC8B/20260821_editorial_literature_preflight/02_PANEL_DATA_ASSERTIONS.json`",
    )
    supplement = supplement.replace(
        "`01_manuscript/manuscript_v12_genome_medicine_gateC8S_2026-08-21.md`",
        "`01_manuscript/manuscript_v13_genome_medicine_gateC8B_editorial_preflight_2026-08-21.md`",
    )
    supplement = supplement.replace(
        "Gate C8S additionally corrects the machine-readable Figure 5 source-data panel assignment",
        "Gate C8S corrected the machine-readable Figure 5 source-data panel assignment; Gate C8B refines the Figure 5c specificity-comparator wording and adds current literature context",
    )
    return supplement


def build_auxiliary_sources() -> dict[str, Path]:
    existing_outputs = {
        "cover": SUBMISSION / "cover_letter_genome_medicine_gateC8B_AUTHOR_COMPLETION_REQUIRED_2026-08-21.md",
        "author_completion_form": SUBMISSION / "author_completion_form_gateC8B_2026-08-21.md",
        "journal_target_decision": SUBMISSION / "journal_target_decision_gateC8B_2026-08-21.md",
        "reporting_checklist": SUBMISSION / "reporting_checklist_gateC8B_2026-08-21.md",
    }
    c8s_inputs = [
        SUBMISSION / "cover_letter_genome_medicine_gateC8S_AUTHOR_COMPLETION_REQUIRED_2026-08-21.md",
        SUBMISSION / "author_completion_form_gateC8S_2026-08-21.md",
        SUBMISSION / "journal_target_decision_gateC8S_2026-08-21.md",
        SUBMISSION / "reporting_checklist_gateC8S_2026-08-21.md",
    ]
    if not all(path.is_file() for path in c8s_inputs):
        if not all(path.is_file() for path in existing_outputs.values()):
            missing = [str(path) for path in c8s_inputs if not path.is_file()]
            raise FileNotFoundError(f"Missing C8S templates and tracked C8B source fallback: {missing}")
        cover = existing_outputs["cover"].read_text(encoding="utf-8-sig")
        if "an interferon-responsive transcriptional program" not in cover or "a type I IFN/ISG program" in cover:
            raise RuntimeError("Tracked C8B cover-letter fallback failed the IFN wording contract")
        return existing_outputs

    cover_source = SUBMISSION / "cover_letter_genome_medicine_gateC8S_AUTHOR_COMPLETION_REQUIRED_2026-08-21.md"
    cover = cover_source.read_text(encoding="utf-8-sig")
    cover = cover.replace("Gate C8S", "Gate C8B")
    cover = replace_once(
        cover,
        "a type I IFN/ISG program",
        "an interferon-responsive transcriptional program",
        "cover IFN wording",
    )
    cover_path = existing_outputs["cover"]
    cover_path.write_text(cover, encoding="utf-8", newline="\n")

    outputs: dict[str, Path] = {"cover": cover_path}
    for stem in ("author_completion_form", "journal_target_decision", "reporting_checklist"):
        source = SUBMISSION / f"{stem}_gateC8S_2026-08-21.md"
        text = source.read_text(encoding="utf-8-sig").replace("Gate C8S", "Gate C8B")
        if stem == "journal_target_decision":
            text += (
                "\n## Gate C8B editorial and literature preflight\n\n"
                "The Figure 5c label now distinguishes proliferation specificity comparators from null controls. "
                "Sayadi et al. (2026; doi:10.1016/j.jaut.2026.103575; PMID 42119160) is included as current external biological context, not replication evidence. "
                "The optional Authors' information section has been removed. No scientific estimate or submission-target decision changed.\n"
            )
        target = existing_outputs[stem]
        target.write_text(text, encoding="utf-8", newline="\n")
        outputs[stem] = target
    return outputs


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manuscript, abstract_words, placeholders = build_manuscript()
    supplement = build_supplement()
    MANUSCRIPT.write_text(manuscript, encoding="utf-8", newline="\n")
    SUPPLEMENT.write_text(supplement, encoding="utf-8", newline="\n")
    auxiliary = build_auxiliary_sources()
    status = {
        "created_at": "2026-08-21",
        "status": "PASS_GATE_C8B_EDITORIAL_LITERATURE_SOURCES_BUILT",
        "source_gate": "C8S frozen scientific state",
        "scientific_estimates_changed": False,
        "abstract_words": abstract_words,
        "references": 31,
        "author_controlled_placeholders": placeholders,
        "authors_information_section_present": False,
        "new_reference": {"doi": "10.1016/j.jaut.2026.103575", "pmid": "42119160", "role": "context only"},
        "figure5c_wording": "Prespecified proliferation specificity comparators",
        "outputs": {
            "manuscript": MANUSCRIPT.relative_to(ROOT).as_posix(),
            "supplement": SUPPLEMENT.relative_to(ROOT).as_posix(),
            **{key: value.relative_to(ROOT).as_posix() for key, value in auxiliary.items()},
        },
    }
    (RUN_DIR / "03_GATE_C8B_SOURCE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
