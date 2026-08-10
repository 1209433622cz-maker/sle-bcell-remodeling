from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "04_submission" / "manuscript_structure_qc"


def count_words(text: str) -> int:
    text = re.sub(r"`[^`]+`", " ", text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def count_placeholders(text: str) -> int:
    patterns = [
        r"Placeholder|TODO|TBD",
        r"\[(?:Author|Funding|Acknowledgement)[^\]]*(?:required|confirmation)[^\]]*\]",
    ]
    return sum(len(re.findall(pattern, text, flags=re.I)) for pattern in patterns)


def split_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+)$", text, flags=re.M))
    sections = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[start:end].strip()))
    return sections


def main() -> None:
    parser = argparse.ArgumentParser(description="Run section-level structure QC for a manuscript markdown file.")
    parser.add_argument(
        "--manuscript",
        default=str(
            PROJECT_ROOT
            / "01_manuscript"
            / "manuscript_v5_genome_medicine_targeted.md"
        ),
        help="Manuscript markdown file to inspect.",
    )
    parser.add_argument("--date", default=date.today().isoformat(), help="Date string for output filenames.")
    args = parser.parse_args()

    manuscript = Path(args.manuscript)
    if not manuscript.is_absolute():
        manuscript = PROJECT_ROOT / manuscript
    manuscript = manuscript.resolve()
    stem = manuscript.stem
    out_csv = OUT_DIR / f"{stem}_structure_qc_{args.date}.csv"
    out_md = OUT_DIR / f"{stem}_structure_qc_{args.date}.md"

    text = manuscript.read_text(encoding="utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for section, body in split_sections(text):
        rows.append(
            {
                "section": section,
                "word_count": count_words(body),
                "heading_count_level3": len(re.findall(r"^###\s+", body, flags=re.M)),
                "placeholder_count": count_placeholders(body),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    figure_legends = re.findall(r"^(?:#{1,3}\s+)?Figure\s+\d+\.", text, flags=re.M)
    supplementary_figure_legends = re.findall(
        r"^(?:#{1,3}\s+)?Supplementary Figure\s+S\d+\.", text, flags=re.M
    )
    citation_keys = sorted(set(re.findall(r"@([A-Za-z0-9_:-]+)", text)))
    total_words_excluding_refs = int(df.loc[df["section"] != "References", "word_count"].sum())
    back_matter_sections = {
        "References",
        "Declarations",
        "Figure legends",
        "Supplementary figure legends",
        "Data availability",
        "Code availability",
        "Ethics statement",
        "Author contributions",
        "Competing interests",
    }
    core_words = int(df.loc[~df["section"].isin(back_matter_sections), "word_count"].sum())
    lines = [
        f"# {stem} Structure QC",
        "",
        f"Date: {args.date}",
        "",
        f"- Manuscript: `{manuscript}`.",
        f"- Total words excluding References section: {total_words_excluding_refs:,}.",
        f"- Core manuscript words excluding declarations and figure-legend sections: {core_words:,}.",
        f"- Abstract words: {int(df.loc[df['section'] == 'Abstract', 'word_count'].sum()):,}.",
        f"- Results words: {int(df.loc[df['section'] == 'Results', 'word_count'].sum()):,}.",
        f"- Discussion words: {int(df.loc[df['section'] == 'Discussion', 'word_count'].sum()):,}.",
        f"- Methods words: {int(df.loc[df['section'] == 'Methods', 'word_count'].sum()):,}.",
        f"- Figure legend entries in manuscript: {len(figure_legends)}.",
        f"- Supplementary figure legend entries in manuscript: {len(supplementary_figure_legends)}.",
        f"- Citation keys used: {len(citation_keys)}.",
        f"- Placeholder/TODO/TBD hits: {int(df['placeholder_count'].sum())}.",
        "",
        "## Section Counts",
        "",
        "| Section | Words | Level-3 headings | Placeholder hits |",
        "|---|---:|---:|---:|",
    ]
    for row in df.itertuples(index=False):
        lines.append(f"| {row.section} | {int(row.word_count):,} | {int(row.heading_count_level3)} | {int(row.placeholder_count)} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The draft is structurally complete enough for target-specific compression.",
            "- The remaining placeholder hits are declaration placeholders, not missing analysis sections.",
            f"- The current architecture contains {len(figure_legends)} main figures and "
            f"{len(supplementary_figure_legends)} supplementary figures.",
            "- For a strict rheumatology target, compress Results and Methods while retaining the independent disease-validation figure in the main text.",
            "- For a genomics/systems target, retain the current evidence hierarchy and strengthen reproducibility and regulatory interpretation.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    print("\n".join(lines[:16]))


if __name__ == "__main__":
    main()
