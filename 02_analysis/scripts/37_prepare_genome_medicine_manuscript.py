from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT_ROOT / "01_manuscript" / "manuscript_v4_nature_style_refined.md"
OUTPUT = PROJECT_ROOT / "01_manuscript" / "manuscript_v5_genome_medicine_targeted.md"


MAIN_LEGENDS = [
    "figure1_legend_draft.md",
    "figure2_v3_legend_draft.md",
    "figure3_v1_legend_draft.md",
    "figure4_v1_legend_draft.md",
    "figure5_v1_legend_draft.md",
    "figure6_gse135779_validation_legend_draft.md",
]

SUPPLEMENTARY_LEGENDS = [
    ("supplement_qc_flagged_cluster_legend_draft.md", None),
    (
        "figure7_onek1k_reference_context_legend_draft.md",
        "Supplementary Figure S2. OneK1K reference context for prioritized SLE B-cell programs",
    ),
    (
        "figure6_gse163121_validation_legend_draft.md",
        "Supplementary Figure S3. Directional B-cell validation in GSE163121",
    ),
    (
        "supplementary_figure_s4_compositional_sensitivity_legend_draft.md",
        "Supplementary Figure S4. Compositional sensitivity of donor-level B-cell state abundance",
    ),
]


def split_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+)$", text, flags=re.M))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip()] = text[start:end].strip()
    return sections


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def remove_abstract_citations(text: str) -> str:
    text = re.sub(r"\s*\[@[^\]]+\]", "", text)
    return re.sub(r" +([.,;:])", r"\1", text)


def format_legend(filename: str, replacement_title: str | None = None) -> str:
    path = SOURCE.parent / filename
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if replacement_title:
        lines[0] = f"# {replacement_title}"
    lines[0] = re.sub(r"^#+\s*", "### ", lines[0])
    text = "\n".join(lines)
    return re.sub(r"\*\*([A-E])\.\*\*", lambda match: f"**{match.group(1).lower()},**", text)


def main() -> None:
    source_text = SOURCE.read_text(encoding="utf-8")
    title = source_text.splitlines()[0]
    sections = split_sections(source_text)

    abstract = remove_abstract_citations(sections["Abstract"])
    if "@" in abstract or count_words(abstract) > 350:
        raise ValueError("Genome Medicine abstract must contain no citations and no more than 350 words.")

    discussion = sections["Discussion"]
    conclusion_marker = "\n\nOverall, "
    if conclusion_marker not in discussion:
        raise ValueError("Could not locate the conclusion paragraph in the source Discussion.")
    discussion, conclusion_tail = discussion.rsplit(conclusion_marker, maxsplit=1)
    conclusion = "Overall, " + conclusion_tail

    methods = "\n\n".join(
        [
            "### Study design\n\nThis was a secondary observational analysis of public single-cell transcriptomic datasets organized into a discovery cohort, independent disease-validation cohorts, and an external B-lineage reference cohort.",
            sections["Methods"],
            "### Generative AI-assisted tools\n\n[Author confirmation required before submission: generative AI-assisted tools supported code drafting, documentation, manuscript organization, and language editing. All analysis scripts, outputs, and scientific interpretations must be reviewed and approved by the authors, who retain full responsibility for the work.]",
        ]
    )

    results = sections["Results"].replace(
        "Fig. 7/Extended Data Fig. 1", "Supplementary Fig. S2"
    )

    main_legends = "\n\n".join(format_legend(name) for name in MAIN_LEGENDS)
    supplementary_legends = "\n\n".join(
        format_legend(name, title_override)
        for name, title_override in SUPPLEMENTARY_LEGENDS
    )

    declarations = """### Ethics approval and consent to participate

This study was a secondary analysis of publicly available de-identified data and involved no new participant recruitment or intervention. Ethics approval and informed consent for the primary studies were reported by the original investigators. [Author/institutional confirmation of whether additional approval or waiver documentation is required for this secondary analysis must be added before submission.]

### Consent for publication

Not applicable.

### Availability of data and materials

The public datasets analyzed in this study are available through GEO under accession numbers GSE174188, GSE135779, GSE163121, and GSE196830 and through the corresponding CELLxGENE resources where stated. The analysis-ready supplementary tables are provided with the article. Large source H5AD and RAW archives are not redistributed.

### Competing interests

[Author declaration required before submission.]

### Funding

[Funding sources and the role of each funder are required before submission.]

### Authors' contributions

[Author initials and CRediT-aligned contributions are required before submission. All authors must read and approve the final manuscript.]

### Acknowledgements

[Acknowledgements or "Not applicable" are required before submission.]

### Authors' information

Not applicable."""

    output_parts = [
        title,
        "## Abstract\n\n" + abstract,
        "## Keywords\n\nsystemic lupus erythematosus; B cells; single-cell RNA sequencing; donor-aware analysis; atypical B cells; independent validation",
        "## Background\n\n" + sections["Introduction"],
        "## Methods\n\n" + methods,
        "## Results\n\n" + results,
        "## Discussion\n\n" + discussion.strip(),
        "## Conclusions\n\n" + conclusion,
        "## List of abbreviations\n\nABC, age-associated B cell; APC, antigen-presenting cell; ASC, antibody-secreting cell; CLR, centered log-ratio; CP10K, counts per 10,000; FDR, false discovery rate; GEO, Gene Expression Omnibus; HC, healthy control; IFN, interferon; ISG, interferon-stimulated gene; OLS, ordinary least squares; PBMC, peripheral blood mononuclear cell; SLE, systemic lupus erythematosus.",
        "## Declarations\n\n" + declarations,
        "## Figure legends\n\n" + main_legends,
        "## Supplementary figure legends\n\n" + supplementary_legends,
        "## References\n\nReference metadata are maintained in `references_verified_crossref_2026-07-09.bib` and must be rendered in Vancouver style for submission.",
    ]

    output_text = "\n\n".join(output_parts).rstrip() + "\n"
    OUTPUT.write_text(output_text, encoding="utf-8")

    legend_sections = [format_legend(name) for name in MAIN_LEGENDS]
    over_limit = [count_words(legend) for legend in legend_sections if count_words(legend) > 300]
    if over_limit:
        raise ValueError(f"Main figure legend exceeds 300 words: {over_limit}")

    print(f"Wrote {OUTPUT}")
    print(f"Abstract words: {count_words(abstract)}")
    print(f"Main legend words: {[count_words(legend) for legend in legend_sections]}")


if __name__ == "__main__":
    main()
