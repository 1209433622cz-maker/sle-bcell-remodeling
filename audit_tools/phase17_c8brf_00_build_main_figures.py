#!/usr/bin/env python3
"""Build the final 170-mm publication figures from frozen scientific inputs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

from pypdf import PdfReader

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BRF" / "20260825_author_release"
PREFREEZE_RUN = ROOT / "phase17_v7" / "gateC8BRP" / "20260825_journal_facing_prefreeze"
TARGET_WIDTH_MM = 170.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def pdf_dimensions_mm(path: Path) -> tuple[float, float]:
    page = PdfReader(path).pages[0]
    return (
        float(page.mediabox.width) * 25.4 / 72.0,
        float(page.mediabox.height) * 25.4 / 72.0,
    )


def normalized_pdf_text(path: Path) -> str:
    text = " ".join((page.extract_text() or "") for page in PdfReader(path).pages)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    figure_dir = RUN_DIR / "figures"
    source_dir = RUN_DIR / "source_data"
    for directory in (figure_dir, source_dir):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    base.ASSERTIONS.clear()
    base.configure_style()
    base.set_output_width_mm(TARGET_WIDTH_MM)
    base.build_figure1(
        ROOT,
        figure_dir,
        source_dir,
        graphical_validation_workflow=True,
        publication_source_data=True,
        explicit_threshold_semantics=True,
        nature_evidence_hierarchy=True,
    )
    base.build_figure2(ROOT, figure_dir, source_dir)
    base.build_figure3(ROOT, figure_dir, source_dir)
    base.build_figure4(
        ROOT,
        figure_dir,
        source_dir,
        reader_facing_source_labels=True,
    )
    base.build_figure5(
        ROOT,
        figure_dir,
        source_dir,
        proliferation_specificity_comparators=True,
        parallel_evidence_branches=True,
        three_evidence_branches=True,
    )
    assertions = list(base.ASSERTIONS)
    if len(assertions) != 46 or not all(row.get("pass") is True for row in assertions):
        raise RuntimeError(f"Expected 46 passing assertions; found {len(assertions)}")

    frozen_figure1 = PREFREEZE_RUN / "source_data" / "Figure1_source_data.csv"
    publication_figure1 = source_dir / "Figure1_source_data.csv"
    frozen_rows = csv_rows(frozen_figure1)
    expected_rows = [row for row in frozen_rows if row["series"] != "gate_decision"]
    publication_rows = csv_rows(publication_figure1)
    if publication_rows != expected_rows:
        raise RuntimeError("Publication Figure 1 rows differ beyond gate_decision removal")
    removed_rows = [row for row in frozen_rows if row["series"] == "gate_decision"]
    if len(removed_rows) != 2:
        raise RuntimeError(f"Expected two removed gate_decision rows; found {len(removed_rows)}")
    publication_text = publication_figure1.read_text(encoding="utf-8-sig")
    internal_tokens = ("HOLD_GATE", "PASS_GATE", "OUTCOME_UNLOCK")
    if any(token in publication_text for token in internal_tokens):
        raise RuntimeError("Internal gate token remains in publication Figure 1 Source Data")

    figure1_text = normalized_pdf_text(figure_dir / "Figure1_disease_blind_identity_scope.pdf")
    figure5_text = normalized_pdf_text(figure_dir / "Figure5_regulatory_evidence.pdf")
    semantic_checks = {
        "figure1_hierarchy_title": "Study design and evidence hierarchy" in figure1_text,
        "figure1_internal_validation": "GSE174188 internal validation" in figure1_text,
        "figure1_independent_replication": "GSE135779 independent replication" in figure1_text,
        "figure1_parallel_interpretation_labels": all(
            token in figure1_text
            for token in (
                "same-data regulator robustness",
                "M5911 response-set concordance",
                "GSE23307 perturbational context",
            )
        ),
        "figure1_legacy_terms_absent": all(
            token not in figure1_text
            for token in (
                "Independent validation",
                "frozen validation",
                "Regulatory + response evidence",
                "identity stability",
            )
        ),
        "figure5_architecture_title": "Evidence architecture for the replicated IFN/ISG program" in figure5_text,
        "figure5_three_parallel_branches": all(
            token in figure5_text
            for token in (
                "Same-data regulator robustness",
                "Curated response-set concordance",
                "Separate perturbational context",
            )
        ),
        "figure5_limitation_visible": all(
            token in figure5_text
            for token in (
                "n=2 healthy donors",
                "descriptive; no inferential P",
                "Interpretive support only",
            )
        ),
        "figure5_legacy_branch_absent": "Response branch" not in figure5_text,
    }
    if not all(semantic_checks.values()):
        failed = [name for name, passed in semantic_checks.items() if not passed]
        raise RuntimeError(f"Figure semantic assertions failed: {failed}")

    source_hashes: dict[str, str] = {}
    for number in range(2, 6):
        current = source_dir / f"Figure{number}_source_data.csv"
        prior = PREFREEZE_RUN / "source_data" / current.name
        if sha256(current) != sha256(prior):
            raise RuntimeError(f"Frozen source data changed: {current.name}")
        source_hashes[current.name] = sha256(current)
    source_hashes[publication_figure1.name] = sha256(publication_figure1)

    dimensions: dict[str, dict[str, float]] = {}
    for pdf in sorted(figure_dir.glob("Figure*.pdf")):
        width_mm, height_mm = pdf_dimensions_mm(pdf)
        if abs(width_mm - TARGET_WIDTH_MM) > 0.15:
            raise RuntimeError(f"Unexpected width for {pdf.name}: {width_mm:.3f} mm")
        if height_mm > 225.0:
            raise RuntimeError(f"Figure exceeds 225-mm height: {pdf.name}")
        dimensions[pdf.name] = {
            "width_mm": round(width_mm, 3),
            "height_mm": round(height_mm, 3),
        }

    provenance = {
        "created_at": "2026-08-25",
        "status": "PASS",
        "frozen_source": frozen_figure1.relative_to(ROOT).as_posix(),
        "frozen_source_sha256": sha256(frozen_figure1),
        "publication_source": publication_figure1.relative_to(ROOT).as_posix(),
        "publication_source_sha256": sha256(publication_figure1),
        "removed_non_plotted_rows": removed_rows,
        "publication_rows_equal_frozen_rows_after_declared_filter": True,
        "plotted_numeric_rows_changed": False,
    }
    (RUN_DIR / "00_FIGURE1_PUBLICATION_SOURCE_PROVENANCE.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    status = {
        "created_at": "2026-08-25",
        "status": "PASS_GATE_C8BRF_170MM_PUBLICATION_FIGURES_BUILT",
        "figures": 5,
        "formats": ["PDF_VECTOR", "PNG_600_DPI"],
        "target_width_mm": TARGET_WIDTH_MM,
        "dimensions": dimensions,
        "scientific_estimates_changed": False,
        "figure1_publication_filter": "removed only two non-plotted gate_decision rows",
        "figure1_threshold_semantics": "explicit labels for all three dashed criteria",
        "figure2_to_figure5_source_data_byte_identical_to_prefreeze": True,
        "source_data_sha256": source_hashes,
        "panel_data_assertions": len(assertions),
        "panel_data_assertions_passed": True,
        "semantic_diagram_assertions": semantic_checks,
    }
    (RUN_DIR / "01_FIGURE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (RUN_DIR / "02_PANEL_DATA_ASSERTIONS.json").write_text(
        json.dumps(
            {"created_at": "2026-08-25", "status": "PASS", "checks": assertions},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
