#!/usr/bin/env python
"""Create a Genome Medicine submission source from the frozen v5 manuscript.

The script intentionally does not invent author, ethics, funding, or repository
metadata. Those fields remain explicit author actions in the generated source.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "01_manuscript" / "manuscript_v5_genome_medicine_targeted.md"
DEFAULT_BIB = ROOT / "01_manuscript" / "references_verified_crossref_2026-07-09.bib"
DEFAULT_OUTPUT = (
    ROOT / "01_manuscript" / "manuscript_v6_genome_medicine_submission_source.md"
)

TITLE_PAGE = """\
**Article type:** Research

**Authors:** [AUTHOR ACTION REQUIRED: enter each author's full name in publication order]

**Affiliations:** [AUTHOR ACTION REQUIRED: enter numbered institutional addresses for all authors]

**Corresponding author:** [AUTHOR ACTION REQUIRED: enter name, full postal address, and email]

**Running title:** Donor-aware SLE B-cell remodeling
"""

AI_OLD = """\
[Author confirmation required before submission: generative AI-assisted tools supported code drafting, documentation, manuscript organization, and language editing. All analysis scripts, outputs, and scientific interpretations must be reviewed and approved by the authors, who retain full responsibility for the work.]"""

AI_NEW = """\
Generative AI-assisted tools supported code drafting, documentation, manuscript organization, and language editing. No generative AI system is listed as an author. All analysis scripts, outputs, scientific interpretations, and final text were reviewed by the authors, who retain full accountability for the work. [AUTHOR ACTION REQUIRED: confirm this disclosure accurately describes the final workflow before submission.]"""

ETHICS_OLD = """\
This study was a secondary analysis of publicly available de-identified data and involved no new participant recruitment or intervention. Ethics approval and informed consent for the primary studies were reported by the original investigators. [Author/institutional confirmation of whether additional approval or waiver documentation is required for this secondary analysis must be added before submission.]"""

ETHICS_NEW = """\
This study was a secondary analysis of publicly available de-identified human data and involved no new participant recruitment, intervention, or access to direct identifiers. Ethics approval and informed consent for the primary studies were reported by the original investigators. [AUTHOR ACTION REQUIRED: confirm with the corresponding institution whether this secondary analysis is exempt from additional review or requires a waiver statement; add the committee name and reference number if applicable.]"""

DATA_OLD = """\
The public datasets analyzed in this study are available through GEO under accession numbers GSE174188, GSE135779, GSE163121, and GSE196830 and through the corresponding CELLxGENE resources where stated. The analysis-ready supplementary tables are provided with the article. Large source H5AD and RAW archives are not redistributed."""

DATA_NEW = """\
The public datasets analyzed in this study are available from the NCBI Gene Expression Omnibus under accession numbers GSE174188 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188), GSE135779 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779), GSE163121 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE163121), and GSE196830 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE196830), with corresponding CELLxGENE resources used where stated. Analysis-ready results are included in Supplementary Tables S1-S13. Large source H5AD and RAW archives are not redistributed because they remain available from the source repositories. Reproducible analysis scripts are included in the submission archive. [AUTHOR ACTION REQUIRED: before submission, archive the final code and compact derived data in a persistent public repository and insert its DOI or stable URL here.]"""

DECLARATION_REPLACEMENTS = {
    "[Author declaration required before submission.]": (
        "[AUTHOR ACTION REQUIRED: enter the authors' financial and non-financial "
        'competing-interest declaration, or state "The authors declare that they '
        'have no competing interests".]'
    ),
    "[Funding sources and the role of each funder are required before submission.]": (
        "[AUTHOR ACTION REQUIRED: list every grant and funder, award numbers, "
        "recipient initials, and the funders' roles; state explicitly if the "
        "funders had no role.]"
    ),
    (
        "[Author initials and CRediT-aligned contributions are required before "
        "submission. All authors must read and approve the final manuscript.]"
    ): (
        "[AUTHOR ACTION REQUIRED: provide contribution statements using author "
        "initials and CRediT roles. End with confirmation that all authors read "
        "and approved the final manuscript.]"
    ),
    '[Acknowledgements or "Not applicable" are required before submission.]': (
        '[AUTHOR ACTION REQUIRED: acknowledge eligible non-author contributors '
        'with permission, or state "Not applicable".]'
    ),
}

METHOD_SECTIONS = {
    "### Study design": """\
This was a secondary observational analysis of public single-cell transcriptomic datasets organized into a discovery cohort, independent disease-validation cohorts, and an external B-lineage reference cohort. All donors and cells meeting the dataset-specific inclusion criteria were retained; no prospective sample-size calculation, randomization, or blinding was applicable. Biological donors, or donor/sample names where that was the highest-resolution identifier available, defined the inferential units. All tests were two-sided. The normal or healthy-control group was the reference, and Benjamini-Hochberg false-discovery-rate (FDR) correction was applied over the explicitly stated family of tests.""",
    "### Matrix handling and state mapping": """\
The H5AD `X` matrix contained preprocessed/scaled values, including negative values, and was not treated as raw counts. For the B-lineage subset, a 15-nearest-neighbor graph was constructed from the source `X_pca` representation. Leiden clustering was performed at resolution 0.6, and the source `X_umap` representation was retained for visualization. No additional batch correction was applied. Count-like analyses, including marker refinement, donor-state pseudobulk expression, and literature-informed signatures, used `adata.raw.X`. Preliminary clusters were converted to manuscript state labels using source annotations, curated marker programs, raw-count marker summaries, ranked state markers, donor-level disease tests, and QC sensitivity; these labels were therefore treated as descriptive state definitions rather than externally trained cell-type predictions.""",
    "### Marker refinement, abundance testing, and QC sensitivity": """\
Raw-count marker summaries were calculated from `adata.raw.X`, normalized to counts per 10,000, and transformed as log1p(CP10K). For ranked-marker annotation, up to 3,000 cells per state were selected using random seed 13, genes detected in fewer than 20 selected cells were removed, and the top 100 genes per state were ranked with Scanpy's variance-overestimating t-test after CP10K normalization and log1p transformation; Benjamini-Hochberg-adjusted values were retained. These cell-level marker results were used for annotation, not for disease-level inference. Donor-level state abundance was calculated as the fraction of each donor's B-lineage cells assigned to each refined state. Normal and SLE donor fractions were compared using two-sided Mann-Whitney U tests with Benjamini-Hochberg correction across states. Sensitivity analysis repeated donor-level tests after excluding the flagged platelet/ambient-RNA-high cluster from state counts and denominators.""",
    "### Covariate sensitivity": """\
Donor-level covariate sensitivity used ordinary least-squares (OLS) models with HC3 robust standard errors. Model tiers included an unadjusted disease-only model, a demographic model adjusted for age, sex, and self-reported ethnicity, and a full model additionally adjusted for simplified processing cohort and log10 donor B-lineage cell count. Continuous covariates were centered and scaled; categorical covariates were dummy encoded with one reference level. Models used complete cases for the variables in each specification. Benjamini-Hochberg correction was applied across the eight B-cell states within each model tier.""",
    "### Independent SLE validation": """\
GSE163121 processed supplementary matrices were downloaded from GEO and parsed into a B-cell AnnData object [@Bhamidipati2021]. Counts were normalized to log1p(CP10K), program scores were averaged within sample, and healthy-control and SLE samples were compared using two-sided Mann-Whitney U tests with Benjamini-Hochberg correction across program and high-fraction metrics. The ABC/APC-high threshold was the pooled healthy-control cell-level 95th percentile of the ABC/APC-focus score. Because this dataset contains only five donors, it was treated as directional validation.

For GSE135779, processed Matrix Market files were downloaded from GEO and aligned to extended cell-level metadata from the associated analysis resources [@NeharBelaid2020]. Metadata-defined B-subcluster cells were matched to processed matrices within sample using the core barcode sequence preceding the dash. Counts were normalized to log1p(CP10K), and scores were averaged within donor/sample name. The ABC/APC-high threshold was the pooled healthy-control B-subcluster cell-level 95th percentile of the ABC/APC-focus score; the fraction above this fixed threshold was then calculated for each donor/sample name. Healthy-control and SLE donor/sample summaries were compared using two-sided Mann-Whitney U tests in all-donor/sample, childhood, and adult strata. Benjamini-Hochberg correction was applied across all program, high-fraction, and stratum tests. The all-donor/sample analysis was prespecified as the primary validation comparison; age-stratified results were supportive.""",
    "### OneK1K reference analysis": """\
The OneK1K/GSE196830 CELLxGENE H5AD was downloaded and inspected [@Yazar2022]. B-lineage-like cells were selected from standardized `cell_type` annotations, retaining naive B cells, memory B cells, transitional-stage B cells, and plasmablasts. Target-gene raw counts from `X` were normalized as log1p(CP10K) using the full-library `nCount_RNA` metadata column. Program scores were calculated as the mean expression of available marker genes and summarized by cell type and donor. OneK1K was used only as external immune-reference context and not for SLE-versus-control inference.""",
}

SOFTWARE_SECTION = """\
### Software and reproducibility

Analyses were run in Python 3.11 using Scanpy 1.11.5, AnnData 0.12.17, pandas 2.3.3, NumPy 2.4.6, SciPy 1.17.1, statsmodels 0.14.6, Matplotlib 3.11.0, seaborn 0.13.2, scikit-learn 1.9.0, igraph 1.0.0, and leidenalg 0.12.0. Deterministic seeds are specified in the analysis scripts where subsampling was used. Scripts, runbooks, intermediate QC summaries, numerical consistency checks, and figure checks are retained with the submission archive.
"""


def parse_bibtex(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    starts = list(re.finditer(r"(?m)^@\w+\{([^,]+),\s*$", text))
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[match.end() : end]
        fields: dict[str, str] = {}
        for line in block.splitlines():
            field_match = re.match(r"\s*(\w+)\s*=\s*\{(.*)\},?\s*$", line)
            if field_match:
                fields[field_match.group(1).lower()] = field_match.group(2)
        entries[match.group(1)] = fields
    return entries


def latex_to_unicode(value: str) -> str:
    replacements = {
        r'{\"u}': "ü",
        r'{\"o}': "ö",
        r'{\"a}': "ä",
        r"{\'e}": "é",
        r"{\'a}": "á",
        r"{\'i}": "í",
        r"{\'o}": "ó",
        r"{\'u}": "ú",
        r"{\~n}": "ñ",
        r"{\~N}": "Ñ",
        "{": "",
        "}": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def initials(given_names: str) -> str:
    tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", latex_to_unicode(given_names))
    return "".join(token[0].upper() for token in tokens if token)


def format_author(name: str) -> str:
    clean = latex_to_unicode(name.strip())
    if "," in clean:
        family, given = [part.strip() for part in clean.split(",", 1)]
        return f"{family} {initials(given)}".strip()
    parts = clean.split()
    if len(parts) == 1:
        return parts[0]
    return f"{parts[-1]} {initials(' '.join(parts[:-1]))}"


def format_reference(number: int, key: str, entry: dict[str, str]) -> str:
    authors = [format_author(author) for author in entry.get("author", "").split(" and ")]
    if len(authors) > 6:
        author_text = ", ".join(authors[:6]) + ", et al"
    else:
        author_text = ", ".join(authors)

    title = latex_to_unicode(entry.get("title", "")).rstrip(".")
    journal = latex_to_unicode(entry.get("journal", ""))
    year = entry.get("year", "")
    volume = entry.get("volume", "")
    pages = entry.get("pages", "").replace("--", "-")
    doi = entry.get("doi", "")

    source = journal
    if year:
        source += f". {year}"
    if volume:
        source += f";{volume}"
    if pages:
        source += f":{pages}"
    source = source.rstrip(".") + "."
    doi_text = f" https://doi.org/{doi}." if doi else ""
    return f"{number}. {author_text}. {title}. {source}{doi_text}"


def replace_citations(
    text: str, bib: dict[str, dict[str, str]]
) -> tuple[str, list[str]]:
    order: list[str] = []

    def replace(match: re.Match[str]) -> str:
        keys = [token.strip().lstrip("@") for token in match.group(1).split(";")]
        missing = [key for key in keys if key not in bib]
        if missing:
            raise KeyError(f"Unresolved citation keys: {', '.join(missing)}")
        for key in keys:
            if key not in order:
                order.append(key)
        numbers = [order.index(key) + 1 for key in keys]
        return "[" + ", ".join(str(number) for number in numbers) + "]"

    rendered = re.sub(r"\[@([^\]]+)\]", replace, text)
    return rendered, order


def word_count(text: str) -> int:
    text = re.sub(r"[#*_`\[\]]", " ", text)
    return len(re.findall(r"\b[\w/+-]+(?:[.-][\w/+-]+)*\b", text, flags=re.UNICODE))


def section_text(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading) + len(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def replace_markdown_section(text: str, heading: str, content: str) -> str:
    pattern = rf"(?ms)^{re.escape(heading)}\s+.*?(?=^### |^## )"
    replacement = f"{heading}\n\n{content.strip()}\n\n"
    rendered, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace manuscript section: {heading}")
    return rendered


def legend_word_counts(text: str, supplementary: bool) -> list[int]:
    if supplementary:
        pattern = r"(?ms)^### Supplementary Figure S\d+\..*?(?=^### |^## References)"
    else:
        main_block = section_text(text, "## Figure legends", "## Supplementary figure legends")
        pattern = r"(?ms)^### Figure \d+\..*?(?=^### |\Z)"
        text = main_block
    return [word_count(match.group(0)) for match in re.finditer(pattern, text)]


def validate(text: str, citation_order: list[str]) -> dict[str, int]:
    abstract = section_text(text, "## Abstract", "## Keywords")
    abstract_words = word_count(abstract)
    if abstract_words > 350:
        raise ValueError(f"Abstract exceeds 350 words: {abstract_words}")
    for required in ("**Background:**", "**Methods:**", "**Results:**", "**Conclusions:**"):
        if required not in abstract:
            raise ValueError(f"Missing structured abstract heading: {required}")

    keyword_text = section_text(text, "## Keywords", "## Background").strip()
    keyword_count = len([item for item in keyword_text.split(";") if item.strip()])
    if not 3 <= keyword_count <= 10:
        raise ValueError(f"Keyword count must be 3-10, found {keyword_count}")

    if re.search(r"\[@[^\]]+\]", text):
        raise ValueError("Unrendered citation tokens remain")
    if len(citation_order) != len(set(citation_order)):
        raise ValueError("Citation order contains duplicate keys")

    figure_titles = re.findall(r"^### (Figure \d+\..+)$", text, flags=re.MULTILINE)
    for title in figure_titles:
        title_words = word_count(title.split(".", 1)[1])
        if title_words > 15:
            raise ValueError(f"Figure title exceeds 15 words: {title}")

    main_legend_words = legend_word_counts(text, supplementary=False)
    supplementary_legend_words = legend_word_counts(text, supplementary=True)
    for count in main_legend_words + supplementary_legend_words:
        if count > 300:
            raise ValueError(f"Figure legend exceeds 300 words: {count}")

    return {
        "abstract_words": abstract_words,
        "main_text_words": word_count(
            section_text(text, "## Background", "## List of abbreviations")
        ),
        "keywords": keyword_count,
        "references": len(citation_order),
        "main_figures": len(figure_titles),
        "supplementary_figures": len(
            re.findall(r"^### Supplementary Figure S\d+\.", text, flags=re.MULTILINE)
        ),
        "max_main_legend_words": max(main_legend_words, default=0),
        "max_supplementary_legend_words": max(supplementary_legend_words, default=0),
        "author_actions": text.count("AUTHOR ACTION REQUIRED"),
    }


def build(input_path: Path, bib_path: Path, output_path: Path) -> dict[str, int]:
    source = input_path.read_text(encoding="utf-8")
    bib = parse_bibtex(bib_path)

    title, remainder = source.split("\n", 1)
    text = f"{title}\n\n{TITLE_PAGE}\n{remainder.lstrip()}"
    text = text.replace(AI_OLD, AI_NEW)
    text = text.replace(ETHICS_OLD, ETHICS_NEW)
    text = text.replace(DATA_OLD, DATA_NEW)
    for old, new in DECLARATION_REPLACEMENTS.items():
        text = text.replace(old, new)
    for heading, content in METHOD_SECTIONS.items():
        text = replace_markdown_section(text, heading, content)
    text = text.replace(
        "### Generative AI-assisted tools\n",
        f"{SOFTWARE_SECTION}\n### Generative AI-assisted tools\n",
        1,
    )

    text, citation_order = replace_citations(text, bib)
    references = "\n\n".join(
        format_reference(number, key, bib[key])
        for number, key in enumerate(citation_order, start=1)
    )
    text = re.sub(
        r"## References\s+.*\Z",
        f"## References\n\n{references}\n",
        text,
        flags=re.DOTALL,
    )

    metrics = validate(text, citation_order)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8", newline="\n")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    metrics = build(args.input, args.bib, args.output)
    print(f"Wrote: {args.output}")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
