#!/usr/bin/env python3
"""Build Gate C8BR figures while preserving the Gate C8S scientific freeze."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BR" / "20260825_release_portability_preflight"
C8S_RUN = ROOT / "phase17_v7" / "gateC8S" / "20260821_supplementary_traceability_freeze"
C8B_RUN = ROOT / "phase17_v7" / "gateC8B" / "20260821_editorial_literature_preflight"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    figure_dir = RUN_DIR / "figures"
    source_dir = RUN_DIR / "source_data"
    for directory in (figure_dir, source_dir):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    carried_hashes: dict[str, str] = {}
    for number in range(1, 5):
        for source in sorted((C8S_RUN / "figures").glob(f"Figure{number}_*.*")):
            target = figure_dir / source.name
            shutil.copy2(source, target)
            if sha256(source) != sha256(target):
                raise RuntimeError(f"Carried figure hash mismatch: {source.name}")
            carried_hashes[source.name] = sha256(target)
        source_csv = C8S_RUN / "source_data" / f"Figure{number}_source_data.csv"
        target_csv = source_dir / source_csv.name
        shutil.copy2(source_csv, target_csv)
        if sha256(source_csv) != sha256(target_csv):
            raise RuntimeError(f"Carried source-data hash mismatch: {source_csv.name}")

    frozen_assertions = json.loads(
        (C8S_RUN / "02_PANEL_DATA_ASSERTIONS.json").read_text(encoding="utf-8")
    )["checks"]
    carried = [
        row
        for row in frozen_assertions
        if not str(row.get("check", "")).startswith(("Figure5.", "Figure5_"))
    ]

    base.ASSERTIONS.clear()
    base.configure_style()
    base.build_figure5(
        ROOT,
        figure_dir,
        source_dir,
        proliferation_specificity_comparators=True,
        parallel_evidence_branches=True,
    )
    assertions = carried + list(base.ASSERTIONS)
    if len(assertions) != 46 or not all(row.get("pass") is True for row in assertions):
        raise RuntimeError(f"Expected 46 passing assertions; found {len(assertions)}")

    c8b_source = C8B_RUN / "source_data" / "Figure5_source_data.csv"
    c8br_source = source_dir / "Figure5_source_data.csv"
    if sha256(c8b_source) != sha256(c8br_source):
        raise RuntimeError("Figure 5 source data changed during schematic-only rebuild")

    status = {
        "created_at": "2026-08-25",
        "status": "PASS_GATE_C8BR_MAIN_FIGURES_BUILT",
        "figures": 5,
        "formats": ["PDF", "PNG_600_DPI"],
        "source_data_files": 5,
        "scientific_estimates_changed": False,
        "source_policy": "Figures 1-4 byte-identical from Gate C8S; Figure 5 rebuilt from frozen Gate C6B values",
        "figure5a_semantics": "parallel regulatory and orthogonal-response evidence branches",
        "figure5c_wording": "Prespecified proliferation specificity comparators",
        "figure5_source_data_sha256": sha256(c8br_source),
        "figure5_source_data_matches_gateC8B": True,
        "carried_figure_hashes": carried_hashes,
        "panel_data_assertions": len(assertions),
        "panel_data_assertions_passed": True,
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
