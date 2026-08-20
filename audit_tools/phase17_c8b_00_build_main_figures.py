#!/usr/bin/env python3
"""Rebuild Figure 5 for C8B and carry forward unchanged frozen Figures 1-4."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8B" / "20260821_editorial_literature_preflight"
C8S_RUN = ROOT / "phase17_v7" / "gateC8S" / "20260821_supplementary_traceability_freeze"


def main() -> None:
    figure_dir = RUN_DIR / "figures"
    source_dir = RUN_DIR / "source_data"
    for directory in (figure_dir, source_dir):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    for number in range(1, 5):
        for source in sorted((C8S_RUN / "figures").glob(f"Figure{number}_*.*")):
            shutil.copy2(source, figure_dir / source.name)
        source_csv = C8S_RUN / "source_data" / f"Figure{number}_source_data.csv"
        shutil.copy2(source_csv, source_dir / source_csv.name)

    frozen_assertions = json.loads((C8S_RUN / "02_PANEL_DATA_ASSERTIONS.json").read_text(encoding="utf-8"))["checks"]
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
    )
    rebuilt = list(base.ASSERTIONS)
    assertions = carried + rebuilt
    if len(assertions) != 46 or not all(row.get("pass") is True for row in assertions):
        raise RuntimeError(
            f"Expected 46 passing assertions after C8B Figure 5 rebuild; found {len(assertions)}"
        )

    status = {
        "created_at": "2026-08-21",
        "status": "C8B_MAIN_FIGURES_BUILT_WITH_ASSERTIONS",
        "figures": 5,
        "formats": ["PDF", "PNG_600_DPI"],
        "source_data_files": 5,
        "source_policy": "Figures 1-4 byte-identical from Gate C8S; Figure 5 rerendered from frozen Gate C6B data",
        "figure5c_wording": "Prespecified proliferation specificity comparators",
        "panel_data_assertions": len(assertions),
        "panel_data_assertions_passed": True,
    }
    (RUN_DIR / "01_FIGURE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (RUN_DIR / "02_PANEL_DATA_ASSERTIONS.json").write_text(
        json.dumps(
            {"created_at": "2026-08-21", "status": "PASS", "checks": assertions},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
