from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


CORE_PAPERS = [
    {
        "citation_key": "Perez2022",
        "pdf": "PAPER/science.abf1970.pdf",
        "year": "2022",
        "journal": "Science",
        "primary_doi": "10.1126/science.abf1970",
        "expected_title": "Single-cell RNA-seq reveals cell type-specific molecular and genetic associations to lupus",
        "role": "Primary SLE PBMC single-cell dataset and disease biology anchor.",
        "linked_figures": "Figure 1; Figure 2; Figure 4",
        "linked_claims": "Public SLE PBMC atlas; donor-level SLE metadata; interferon and cell-type-specific lupus biology.",
    },
    {
        "citation_key": "Dai2024",
        "pdf": "PAPER/science.adf8531.pdf",
        "year": "2024",
        "journal": "Science",
        "primary_doi": "10.1126/science.adf8531",
        "expected_title": "The transcription factor ZEB2 drives the formation of age-associated B cells",
        "role": "ZEB2 and age-associated/ABC mechanistic anchor.",
        "linked_figures": "Figure 3; Figure 5",
        "linked_claims": "ZEB2-linked ABC and age-associated B-cell interpretation.",
    },
    {
        "citation_key": "Zeng2025",
        "pdf": "PAPER/scitranslmed.adu6015.pdf",
        "year": "2025",
        "journal": "Science Translational Medicine",
        "primary_doi": "10.1126/scitranslmed.adu6015",
        "expected_title": "The m6A demethylase FTO links TLR7 to mitochondrial oxidation driving age-associated B cell formation in systemic lupus erythematosus",
        "role": "TLR7-FTO-m6A-mitochondrial oxidation and ABC biology context.",
        "linked_figures": "Figure 5; Discussion",
        "linked_claims": "TLR7/FTO is broader mechanistic context, not focus-state-specific in our dataset.",
    },
    {
        "citation_key": "Younis2025",
        "pdf": "PAPER/scitranslmed.ady0210.pdf",
        "year": "2025",
        "journal": "Science Translational Medicine",
        "primary_doi": "10.1126/scitranslmed.ady0210",
        "expected_title": "Epstein-Barr virus reprograms autoreactive B cells as antigen-presenting cells in systemic lupus erythematosus",
        "role": "EBV-positive APC-like autoreactive B-cell anchor.",
        "linked_figures": "Figure 3; Figure 5",
        "linked_claims": "APC-like/antigen-presenting autoreactive B-cell framing.",
    },
    {
        "citation_key": "Yazar2022",
        "pdf": "PAPER/science.abf3041.pdf",
        "year": "2022",
        "journal": "Science",
        "primary_doi": "10.1126/science.abf3041",
        "expected_title": "Single-cell eQTL mapping identifies cell type-specific genetic control of autoimmune disease",
        "role": "OneK1K immune single-cell eQTL reference for future genetic regulatory framing.",
        "linked_figures": "Discussion; future work",
        "linked_claims": "External immune genetic reference context.",
    },
    {
        "citation_key": "Yin2026",
        "pdf": "PAPER/science.adt3130.pdf",
        "year": "2026",
        "journal": "Science",
        "primary_doi": "10.1126/science.adt3130",
        "expected_title": "Chinese Immune Multi-Omics Atlas",
        "role": "CIMA multi-omic/xQTL/GRN reference for future regulatory prioritization.",
        "linked_figures": "Discussion; future work",
        "linked_claims": "External immune multi-omic regulatory context.",
    },
    {
        "citation_key": "Zheng2022",
        "pdf": "PAPER/s41467-022-35209-1.pdf",
        "year": "2022",
        "journal": "Nature Communications",
        "primary_doi": "10.1038/s41467-022-35209-1",
        "expected_title": "Single-cell sequencing shows cellular heterogeneity of cutaneous lesions in lupus erythematosus",
        "role": "Cutaneous lupus single-cell tissue-context reference.",
        "linked_figures": "Introduction; Discussion",
        "linked_claims": "Tissue and cutaneous lupus context.",
    },
    {
        "citation_key": "Lee2025",
        "pdf": "PAPER/2025.04.27.649460v1.full.pdf",
        "year": "2025",
        "journal": "bioRxiv",
        "primary_doi": "10.1101/2025.04.27.649460",
        "expected_title": "Transcriptomic analysis reveals immune signatures associated with specific cutaneous manifestations of lupus in systemic lupus erythematosus",
        "role": "Cutaneous manifestation transcriptomic context.",
        "linked_figures": "Discussion",
        "linked_claims": "Cutaneous lupus transcriptomic context if retained.",
    },
    {
        "citation_key": "Zhu_iScience_Autoimmune",
        "pdf": "PAPER/Single-cell landscape of immune cells in multiple autoimmune diseases.pdf",
        "year": "2025",
        "journal": "iScience",
        "primary_doi": "10.1016/j.isci.2025.114515",
        "expected_title": "Single-cell landscape of immune cells in multiple autoimmune diseases",
        "role": "Broad autoimmune single-cell context; optional.",
        "linked_figures": "Introduction; Discussion",
        "linked_claims": "Broad autoimmune atlas context if needed.",
    },
]


KEYWORD_GROUPS = {
    "SLE_single_cell": ["single-cell", "single cell", "lupus", "SLE", "PBMC", "B cell"],
    "ABC_DN2": ["age-associated B", "ABC", "DN2", "ITGAX", "TBX21", "FCRL5", "FCRL3"],
    "ZEB2_axis": ["ZEB2", "zinc finger E-box", "age-associated B cells", "ABC formation"],
    "APC_HLA": ["antigen-presenting", "antigen presenting", "HLA", "CD74", "CD86", "APC-like"],
    "EBV_APC": ["Epstein", "EBV", "autoreactive B", "antigen-presenting cells"],
    "IFN": ["interferon", "IFN", "ISG", "IFI44L", "ISG15"],
    "TLR7_FTO": ["TLR7", "FTO", "m6A", "mitochondrial oxidation", "age-associated B cell formation"],
    "immune_genetics": ["eQTL", "xQTL", "genetic", "GRN", "multi-omics", "regulatory"],
    "cutaneous_lupus": ["cutaneous", "skin", "lesion", "DLE", "discoid"],
}


SIGNATURE_TO_CITATIONS = {
    "ABC_DN2_core": {
        "primary_citations": "Dai2024; Zeng2025; Perez2022",
        "support_level": "primary_state_interpretation",
        "audit_note": "ABC/DN2 marker framing is supported by age-associated/ABC SLE biology; formal final draft may need additional classic DN2 references if available.",
    },
    "ABC_low_naive_context": {
        "primary_citations": "Dai2024; Zeng2025",
        "support_level": "primary_state_interpretation",
        "audit_note": "Signed score combines ABC markers with low naive-context markers; useful but should be described as an analysis construct.",
    },
    "ZEB2_ABC_axis": {
        "primary_citations": "Dai2024",
        "support_level": "strong_direct_anchor",
        "audit_note": "Direct ZEB2/ABC formation anchor.",
    },
    "APC_HLA_B_cell": {
        "primary_citations": "Younis2025; Perez2022",
        "support_level": "primary_state_interpretation",
        "audit_note": "Supports antigen-presentation/APC-like B-cell framing.",
    },
    "EBV_APC_like_B": {
        "primary_citations": "Younis2025",
        "support_level": "strong_direct_anchor",
        "audit_note": "Use for EBV/APC-like conceptual framing; avoid claiming EBV positivity in our dataset unless measured.",
    },
    "IFN_ISG": {
        "primary_citations": "Perez2022; Zheng2022",
        "support_level": "disease_context",
        "audit_note": "Supports IFN/ISG lupus inflammatory context, but our state is not uniquely maximal for IFN.",
    },
    "TLR7_FTO_innate_axis": {
        "primary_citations": "Zeng2025",
        "support_level": "boundary_context",
        "audit_note": "Not focus-state specific in our data; use as boundary/mechanistic context only.",
    },
    "Age_associated_B_like": {
        "primary_citations": "Dai2024; Zeng2025",
        "support_level": "primary_state_interpretation",
        "audit_note": "Strongly supports age-associated/atypical B-cell framing.",
    },
    "Naive_B_control": {
        "primary_citations": "current_dataset_marker_control",
        "support_level": "control_signature",
        "audit_note": "Canonical marker control; not a central literature claim.",
    },
    "Memory_B_control": {
        "primary_citations": "current_dataset_marker_control",
        "support_level": "control_signature",
        "audit_note": "Canonical marker control; not a central literature claim.",
    },
    "Plasmablast_ASC_control": {
        "primary_citations": "current_dataset_marker_control",
        "support_level": "control_signature",
        "audit_note": "Canonical marker control; not a central literature claim.",
    },
    "Platelet_ambient_QC": {
        "primary_citations": "current_dataset_QC",
        "support_level": "qc_signature",
        "audit_note": "QC signature derived from dataset-specific ranked markers.",
    },
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\x00", " ")).strip()


def extract_pdf_text(path: Path) -> tuple[str, int, str]:
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception as exc:
            parts.append(f" EXTRACT_ERROR {exc} ")
    text = normalize_text("\n".join(parts))
    metadata_title = ""
    try:
        metadata_title = str(reader.metadata.title or "")
    except Exception:
        metadata_title = ""
    return text, len(reader.pages), metadata_title


def find_dois(text: str) -> str:
    pattern = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
    matches = []
    for match in pattern.findall(text):
        cleaned = match.rstrip(".,;)")
        cleaned = re.sub(r"doi:?$", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.rstrip(".,;:-)")
        if cleaned.endswith("-"):
            continue
        if cleaned not in matches:
            matches.append(cleaned)
    return ";".join(matches[:5])


def count_keywords(text: str) -> dict[str, int]:
    text_lower = text.lower()
    out = {}
    for group, keywords in KEYWORD_GROUPS.items():
        total = 0
        for keyword in keywords:
            total += text_lower.count(keyword.lower())
        out[group] = total
    return out


def title_match_score(text: str, title: str) -> float:
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9]+", title) if len(w) > 2]
    if not words:
        return 0.0
    text_lower = text.lower()
    return sum(1 for w in words if w in text_lower) / len(words)


def make_paper_audit(project_root: Path) -> pd.DataFrame:
    rows = []
    for paper in CORE_PAPERS:
        pdf_path = project_root / paper["pdf"]
        if not pdf_path.exists():
            rows.append({**paper, "exists": False, "pages": 0, "doi_candidates": "", "title_match_score": 0.0, "keyword_hit_summary": ""})
            continue
        text, pages, metadata_title = extract_pdf_text(pdf_path)
        keyword_counts = count_keywords(text)
        keyword_summary = "; ".join(f"{k}={v}" for k, v in keyword_counts.items() if v > 0)
        rows.append(
            {
                **paper,
                "exists": True,
                "pages": pages,
                "metadata_title": metadata_title,
                "doi_candidates": find_dois(text),
                "title_match_score": round(title_match_score(text[:5000], paper["expected_title"]), 3),
                "keyword_hit_summary": keyword_summary,
            }
        )
    return pd.DataFrame(rows)


def make_signature_audit(signature_catalog_path: Path) -> pd.DataFrame:
    catalog = pd.read_csv(signature_catalog_path)
    rows = []
    for row in catalog.itertuples(index=False):
        mapping = SIGNATURE_TO_CITATIONS.get(row.signature, {})
        rows.append(
            {
                "signature": row.signature,
                "anchor": row.anchor,
                "expected_focus": row.expected_focus,
                "n_positive_present": row.n_positive_present,
                "n_negative_present": row.n_negative_present,
                "positive_present": row.positive_present,
                "negative_present": row.negative_present,
                "primary_citations": mapping.get("primary_citations", ""),
                "support_level": mapping.get("support_level", ""),
                "audit_note": mapping.get("audit_note", ""),
            }
        )
    return pd.DataFrame(rows)


def write_markdown(path: Path, paper_audit: pd.DataFrame, signature_audit: pd.DataFrame) -> None:
    lines = [
        "# Citation And Signature Audit v1",
        "",
        "## Purpose",
        "",
        "This audit maps local retained PDFs to the current manuscript claims and maps Figure 5 literature-informed signatures to citation keys. It is a working audit for manuscript polishing, not a final reference list.",
        "",
        "## Core Paper Audit",
        "",
    ]
    for row in paper_audit.itertuples(index=False):
        lines.extend(
            [
                f"### {row.citation_key}",
                "",
                f"- PDF: `{row.pdf}`",
                f"- Expected title: {row.expected_title}",
                f"- Journal/year: {row.journal} {row.year}",
                f"- Primary DOI: {row.primary_doi}",
                f"- DOI candidates: {row.doi_candidates if row.doi_candidates else 'not extracted'}",
                f"- Pages extracted: {row.pages}",
                f"- Role: {row.role}",
                f"- Linked figures: {row.linked_figures}",
                f"- Linked claims: {row.linked_claims}",
                f"- Keyword hits: {row.keyword_hit_summary if row.keyword_hit_summary else 'none'}",
                "",
            ]
        )
    lines.extend(["## Signature-To-Citation Audit", ""])
    for row in signature_audit.itertuples(index=False):
        lines.extend(
            [
                f"### {row.signature}",
                "",
                f"- Anchor: {row.anchor}",
                f"- Primary citations: {row.primary_citations}",
                f"- Support level: {row.support_level}",
                f"- Present positive genes ({row.n_positive_present}): {row.positive_present}",
                f"- Present negative/context genes ({row.n_negative_present}): {row.negative_present if isinstance(row.negative_present, str) else ''}",
                f"- Audit note: {row.audit_note}",
                "",
            ]
        )
    lines.extend(
        [
            "## Current Phase 6 Judgment",
            "",
            "- The retained PDF set is sufficient to support the current five-figure manuscript backbone.",
            "- The strongest citation-backed signatures are ZEB2/ABC, APC/HLA, EBV/APC-like, ABC/DN2/age-associated, and IFN/ISG context.",
            "- The TLR7/FTO signature should remain a boundary/context result because it is not focus-state specific in Figure 5.",
            "- Additional classic DN2/ABC references may still be useful before final submission if the target journal expects canonical DN2 citations beyond the retained PDF set.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bib(path: Path, paper_audit: pd.DataFrame) -> None:
    lines = [
        "% Working BibTeX skeleton generated from local PDF audit.",
        "% Verify author lists, page numbers, and DOI formatting before submission.",
        "",
    ]
    for row in paper_audit.itertuples(index=False):
        entry_type = "article"
        doi = str(row.primary_doi) if isinstance(row.primary_doi, str) else ""
        lines.extend(
            [
                f"@{entry_type}{{{row.citation_key},",
                f"  title = {{{row.expected_title}}},",
                f"  journal = {{{row.journal}}},",
                f"  year = {{{row.year}}},",
                f"  doi = {{{doi}}},",
                "  note = {Working citation skeleton; verify before submission}",
                "}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit retained PDFs and map Figure 5 signatures to citation support.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--signature-catalog", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--manuscript-dir", default="01_manuscript")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    outdir = project_root / args.outdir
    manuscript_dir = project_root / args.manuscript_dir
    outdir.mkdir(parents=True, exist_ok=True)
    manuscript_dir.mkdir(parents=True, exist_ok=True)

    paper_audit = make_paper_audit(project_root)
    signature_audit = make_signature_audit(project_root / args.signature_catalog)

    paper_audit.to_csv(outdir / "citation_pdf_audit_2026-07-01.csv", index=False, encoding="utf-8-sig")
    signature_audit.to_csv(outdir / "signature_to_citation_audit_2026-07-01.csv", index=False, encoding="utf-8-sig")
    write_markdown(manuscript_dir / "citation_signature_audit_v1.md", paper_audit, signature_audit)
    write_bib(manuscript_dir / "references_working_v1.bib", paper_audit)

    print(f"Wrote citation audit outputs to: {outdir}")
    print(f"Wrote manuscript audit to: {manuscript_dir / 'citation_signature_audit_v1.md'}")
    print(paper_audit[["citation_key", "pages", "doi_candidates", "title_match_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
