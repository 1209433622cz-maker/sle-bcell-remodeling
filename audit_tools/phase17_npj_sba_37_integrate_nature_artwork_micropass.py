#!/usr/bin/env python3
"""Apply a role-aware Nature/npj typography micropass from frozen figure sources."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import ContentStream

import phase17_c8s_01_build_supplementary_figures as supplementary_figures
import phase17_npj_sba_22_integrate_scientific_presentation_freeze as presentation


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase17_v7/npj_sba_scientific_stop_gate/20260901_canonical_source_s4b_refreeze"
RUN = ROOT / "phase17_v7/npj_sba_nature_artwork_micropass/20260901_role_aware_typography_refreeze"
FIGURE_ROOT = RUN / "figures"
FIGURE_DIR = FIGURE_ROOT / "figures"
SOURCE_DIR = FIGURE_ROOT / "source_data"
SOURCE_OUTPUT = RUN / "sources"
RECEIVED = ROOT / "00_project_management/nature_artwork_micropass_2026-09-01/received"
ROOT_MANUSCRIPT = ROOT / "01_manuscript/Manuscript.md"
ROOT_SUPPLEMENT = ROOT / "01_manuscript/Supplementary_Information.md"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
S4_TITLE = "B_ASC estimate across covariance and cell policies"

INPUTS = {
    "SLE_Bcell_Nature_Artwork_Maintenance_Audit_2026-09-01.md": Path(
        r"C:\Users\Administrator\Downloads\SLE_Bcell_Nature_Artwork_Maintenance_Audit_2026-09-01.md"
    ),
    "pasted_nature_artwork_review_2026-09-01.txt": Path(
        r"C:\Users\Administrator\.codex\attachments\9d129382-ae10-4941-aadc-59625c6d8dde\pasted-text.txt"
    ),
}

PRESERVE_EXACT = {
    "Supplementary_Figure_S3_fine_state_failure_transition_structure",
    "Supplementary_Figure_S5_pseudobulk_ranked_list_diagnostics",
    "Supplementary_Figure_S6_replication_robustness_diagnostics",
}

REDRAW = {
    "Figure1_disease_blind_identity_scope",
    "Figure2_sample_level_composition",
    "Figure3_gse174188_bconv_transcription",
    "Figure4_independent_ifn_replication",
    "Figure5_regulatory_evidence",
    "Supplementary_Figure_S1_source_integrity_qc",
    "Supplementary_Figure_S2_representation_diagnostics",
    "Supplementary_Figure_S4_composition_diagnostics",
    "Supplementary_Figure_S7_regulator_correlation_sensitivity",
    "Supplementary_Figure_S8_overlap_depletion",
    "Supplementary_Figure_S9_identity_boundary_and_propagation",
    "Supplementary_Figure_S10_reference_calibration_boundary",
}

OLD_INTERNAL = (
    "Because both analyses originate from the same accession, they are internal replication "
    "rather than independent validation."
)
NEW_INTERNAL = (
    "Because both analyses originate from the same accession, they provide internal replication "
    "rather than independent replication."
)
OLD_PROPAGATION = (
    "These analyses quantify same-data sensitivity to identity uncertainty; they are not "
    "independent validation."
)
NEW_PROPAGATION = (
    "These analyses quantify same-data sensitivity to identity uncertainty; they are not "
    "independent replication."
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_reset(path: Path) -> None:
    resolved = path.resolve()
    phase17 = (ROOT / "phase17_v7").resolve()
    if not resolved.is_relative_to(phase17):
        raise RuntimeError(f"Refusing to reset outside phase17_v7: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}; observed {count}")
    return text.replace(old, new, 1)


def archive_inputs() -> dict[str, dict[str, object]]:
    RECEIVED.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict[str, object]] = {}
    for name, source in INPUTS.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        target = RECEIVED / name
        shutil.copy2(source, target)
        records[name] = {
            "source": str(source),
            "archived": target.relative_to(ROOT).as_posix(),
            "bytes": target.stat().st_size,
            "sha256": sha256(target),
            "byte_identical": source.read_bytes() == target.read_bytes(),
        }
    return records


def pdf_artwork(path: Path) -> dict[str, object]:
    reader = PdfReader(path)
    sizes: list[float] = []
    fonts: list[str] = []
    widths: list[float] = []

    def visitor(text, _cm, _tm, font_dict, font_size):
        if text and text.strip():
            sizes.append(round(float(font_size), 2))
            if font_dict:
                fonts.append(str(font_dict.get("/BaseFont", "UNKNOWN")))

    for page in reader.pages:
        page.extract_text(visitor_text=visitor)
        stream = ContentStream(page.get_contents(), reader)
        for operands, operator in stream.operations:
            if operator == b"w" and operands:
                widths.append(round(float(operands[0]), 3))
    page = reader.pages[0]
    size_counts = dict(sorted(Counter(sizes).items()))
    nonzero_widths = [value for value in widths if value > 0]
    return {
        "sha256": sha256(path),
        "pages": len(reader.pages),
        "width_mm": round(float(page.mediabox.width) * 25.4 / 72.0, 3),
        "height_mm": round(float(page.mediabox.height) * 25.4 / 72.0, 3),
        "font_sizes": size_counts,
        "minimum_font_pt": min(sizes),
        "maximum_font_pt": max(sizes),
        "font_size_levels": len(size_counts),
        "fonts": sorted(set(fonts)),
        "arial_only": bool(fonts) and all("Arial" in value for value in fonts),
        "line_widths": dict(sorted(Counter(nonzero_widths).items())),
        "has_sub_1pt_rule": any(0 < value < 1.0 for value in nonzero_widths),
    }


def audit_set(directory: Path) -> dict[str, dict[str, object]]:
    return {path.stem: pdf_artwork(path) for path in sorted(directory.glob("*.pdf"))}


def build_role_aware_figures() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    FIGURE_DIR.mkdir(parents=True)
    SOURCE_DIR.mkdir(parents=True)
    SOURCE_OUTPUT.mkdir(parents=True)
    os.environ["NPJ_SBA_STYLE"] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")

    presentation.RUN = RUN
    presentation.FIGURE_ROOT = FIGURE_ROOT
    presentation.FIGURE_DIR = FIGURE_DIR
    presentation.SOURCE_DIR = SOURCE_DIR
    presentation.SOURCE_OUTPUT = SOURCE_OUTPUT
    assertions = presentation.build_all_figures()

    supplementary_figures.ASSERTIONS.clear()
    supplementary_figures.configure_style()
    supplementary_figures.build_s4(
        ROOT,
        FIGURE_DIR,
        SOURCE_DIR,
        log_ratio_two_part=True,
        panel_b_title=S4_TITLE,
    )

    generated_sources = {path.name: sha256(path) for path in SOURCE_DIR.glob("*.csv")}
    base_sources = {
        path.name: sha256(path) for path in (BASE / "figures/source_data").glob("*.csv")
    }
    if generated_sources != base_sources or len(generated_sources) != 15:
        raise RuntimeError("A source-driven redraw changed frozen Source Data")

    for legacy_pattern in (
        "Supplementary_Figure_S3_*",
        "Supplementary_Figure_S5_*",
        "Supplementary_Figure_S6_*",
    ):
        for path in FIGURE_DIR.glob(legacy_pattern):
            path.unlink()
    for stem in PRESERVE_EXACT:
        for suffix in (".pdf", ".png"):
            shutil.copy2(BASE / "figures/figures" / f"{stem}{suffix}", FIGURE_DIR / f"{stem}{suffix}")
    return assertions


def integrate_sources() -> tuple[Path, Path, list[dict[str, object]], dict[str, object]]:
    source = BASE / "sources/Manuscript_scientific_stop_gate.md"
    base_text = source.read_text(encoding="utf-8")
    text = replace_once(base_text, OLD_INTERNAL, NEW_INTERNAL, "internal-replication boundary")
    text = replace_once(text, OLD_PROPAGATION, NEW_PROPAGATION, "uncertainty-propagation boundary")

    manuscript = SOURCE_OUTPUT / "Manuscript_nature_artwork_micropass.md"
    supplement = SOURCE_OUTPUT / "Supplementary_Information_nature_artwork_micropass.md"
    manuscript.write_text(text, encoding="utf-8", newline="\n")
    shutil.copy2(BASE / "sources/Supplementary_Information_scientific_stop_gate.md", supplement)
    ROOT_MANUSCRIPT.write_text(text, encoding="utf-8", newline="\n")
    shutil.copy2(supplement, ROOT_SUPPLEMENT)

    ledger = [
        {
            "scope": "Results",
            "edit": "Accession-internal evidence boundary",
            "old_text": OLD_INTERNAL,
            "new_text": NEW_INTERNAL,
            "scientific_estimate_changed": False,
        },
        {
            "scope": "Methods",
            "edit": "Same-data uncertainty evidence boundary",
            "old_text": OLD_PROPAGATION,
            "new_text": NEW_PROPAGATION,
            "scientific_estimate_changed": False,
        },
    ]
    checks = {
        "exactly_two_changed_lines": sum(
            left != right
            for left, right in zip(base_text.splitlines(), text.splitlines())
        ) == 2,
        "independent_replication_boundaries_present": (
            NEW_INTERNAL in text and NEW_PROPAGATION in text
        ),
        "targeted_old_phrases_absent": OLD_INTERNAL not in text and OLD_PROPAGATION not in text,
        "methodological_validation_retained": (
            "not independent validation of the full feature-selection and tuning pipeline" in text
            and "prospective clinical validation" in text
            and "Project administration, Validation, Writing" in text
        ),
        "root_manuscript_exact_parity": ROOT_MANUSCRIPT.read_bytes() == manuscript.read_bytes(),
        "root_supplement_exact_parity": ROOT_SUPPLEMENT.read_bytes() == supplement.read_bytes(),
        "supplement_text_byte_identical": supplement.read_bytes()
        == (BASE / "sources/Supplementary_Information_scientific_stop_gate.md").read_bytes(),
    }
    return manuscript, supplement, ledger, checks


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_decisions() -> None:
    rows: list[dict[str, object]] = []
    for figure, panels in {
        "Figure 1": "abcd",
        "Figure 2": "abcd",
        "Figure 3": "abcd",
        "Figure 4": "abcd",
        "Figure 5": "abcde",
    }.items():
        for panel in panels:
            rows.append(
                {
                    "tier": "Main",
                    "object": f"{figure}{panel}",
                    "scientific_decision": "KEEP",
                    "artwork_action": "SOURCE_REDRAW_TYPOGRAPHY_ONLY",
                    "rationale": "Scientific evidence ownership retained; role-specific typography restored.",
                }
            )
    for figure, panels in {
        "S1": "abcd",
        "S2": "abcd",
        "S3": "ab",
        "S4": "abcd",
        "S5": "abc",
        "S6": "abcd",
        "S7": "abcd",
        "S8": "abcd",
        "S9": "abcde",
        "S10": "abcd",
    }.items():
        action = "KEEP_EXACT" if figure in {"S3", "S5", "S6"} else "SOURCE_REDRAW_TYPOGRAPHY_ONLY"
        for panel in panels:
            rows.append(
                {
                    "tier": "Supplementary",
                    "object": f"Supplementary Figure {figure}{panel}",
                    "scientific_decision": "KEEP",
                    "artwork_action": action,
                    "rationale": (
                        "Already role-aware and retained byte-identically."
                        if action == "KEEP_EXACT"
                        else "Scientific evidence ownership retained; role-specific typography restored."
                    ),
                }
            )
    write_csv(RUN / "02_PANEL_DECISION_MATRIX.csv", rows)


def main() -> None:
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-approved submission package changed before the artwork micropass")
    safe_reset(RUN)
    archived = archive_inputs()
    before = audit_set(BASE / "figures/figures")
    assertions = build_role_aware_figures()
    manuscript, supplement, text_ledger, source_checks = integrate_sources()
    after = audit_set(FIGURE_DIR)

    expected_inventory = REDRAW | PRESERVE_EXACT
    if set(before) != expected_inventory or set(after) != expected_inventory:
        raise RuntimeError("The 15-figure artwork inventory changed")

    rows: list[dict[str, object]] = []
    for stem in sorted(expected_inventory):
        action = "KEEP_EXACT" if stem in PRESERVE_EXACT else "SOURCE_REDRAW_TYPOGRAPHY_ONLY"
        for stage, record in (("before", before[stem]), ("after", after[stem])):
            rows.append(
                {
                    "figure": stem,
                    "stage": stage,
                    "action": action,
                    "minimum_font_pt": record["minimum_font_pt"],
                    "maximum_font_pt": record["maximum_font_pt"],
                    "font_size_levels": record["font_size_levels"],
                    "font_sizes_json": json.dumps(record["font_sizes"], sort_keys=True),
                    "line_widths_json": json.dumps(record["line_widths"], sort_keys=True),
                    "arial_only": record["arial_only"],
                    "has_sub_1pt_rule": record["has_sub_1pt_rule"],
                    "sha256": record["sha256"],
                }
            )
    write_csv(RUN / "01_ARTWORK_TYPOGRAPHY_AUDIT.csv", rows)
    write_csv(RUN / "03_TEXT_EDIT_LEDGER.csv", text_ledger)
    write_decisions()

    source_hashes = {path.name: sha256(path) for path in sorted(SOURCE_DIR.glob("*.csv"))}
    base_source_hashes = {
        path.name: sha256(path) for path in sorted((BASE / "figures/source_data").glob("*.csv"))
    }
    checks = {
        "base_stop_gate_locked": json.loads(
            (BASE / "04_FINAL_SCIENTIFIC_PRESENTATION_STOP_GATE_STATUS.json").read_text(encoding="utf-8")
        )["status"] == "SCIENTIFIC_PRESENTATION_STOP_GATE_LOCKED",
        "received_inputs_archived_byte_identically": all(
            record["byte_identical"] for record in archived.values()
        ),
        "baseline_12_flattened_figures_confirmed": all(
            before[stem]["font_sizes"] == {8.0: sum(before[stem]["font_sizes"].values())}
            for stem in REDRAW
        ),
        "three_role_aware_figures_identified": all(
            before[stem]["font_size_levels"] >= 3 for stem in PRESERVE_EXACT
        ),
        "twelve_redraws_have_role_hierarchy": all(
            after[stem]["font_size_levels"] >= 3
            and after[stem]["minimum_font_pt"] >= 5.5
            and after[stem]["maximum_font_pt"] <= 8.0
            for stem in REDRAW
        ),
        "all_figures_arial_and_vector_page": all(
            record["arial_only"] and record["pages"] == 1 for record in after.values()
        ),
        "all_redraws_restore_sub_1pt_rules": all(after[stem]["has_sub_1pt_rule"] for stem in REDRAW),
        "three_preserved_figures_byte_identical": all(
            before[stem]["sha256"] == after[stem]["sha256"] for stem in PRESERVE_EXACT
        ),
        "twelve_confirmed_outliers_redrawn": all(
            before[stem]["sha256"] != after[stem]["sha256"] for stem in REDRAW
        ),
        "all_15_source_data_byte_identical": source_hashes == base_source_hashes
        and len(source_hashes) == 15,
        "builder_assertions_pass": all(
            row.get("pass", False) for group in assertions for row in group
        ),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
        **source_checks,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Nature artwork micropass integration failed: {failed}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_NATURE_ARTWORK_TYPOGRAPHY_MICROPASS_DOCUMENT_REBUILD_REQUIRED",
        "checks": checks,
        "failed_checks": [],
        "archived_inputs": archived,
        "figure_inventory": {
            "total": 15,
            "source_redrawn_typography_only": sorted(REDRAW),
            "preserved_byte_identically": sorted(PRESERVE_EXACT),
            "new_panels": 0,
            "replacement_panels": 0,
        },
        "panel_inventory": {
            "main_keep": 21,
            "main_typography_only": 21,
            "supplementary_keep": 38,
            "supplementary_typography_only": 29,
            "supplementary_keep_exact": 9,
        },
        "sources": {
            "manuscript": manuscript.relative_to(ROOT).as_posix(),
            "supplement": supplement.relative_to(ROOT).as_posix(),
            "source_data_hashes": source_hashes,
        },
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_changed": False,
        "exact_submission_package_modified": False,
        "exact_submission_package_sha256": PACKAGE_SHA256,
    }
    (RUN / "00_NATURE_ARTWORK_MICROPASS_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
