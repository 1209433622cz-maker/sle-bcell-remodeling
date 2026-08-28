"""Regenerate the Figure 1 agreement-label correction without replacing approved files."""

import argparse
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np

import phase17_c7_01_build_main_figures as figures


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=root/"phase17_v7/post_gateC9/20260828_figure1_label_review")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not output.is_relative_to(root/"phase17_v7/post_gateC9") or output.exists():
        raise ValueError("Choose a new preview directory within phase17_v7/post_gateC9")
    figure_dir, source_dir = output/"figures", output/"source_data"
    figure_dir.mkdir(parents=True)
    source_dir.mkdir()
    decision_path = root/"phase17_v7/gateC2B4/20260815_two_level_state_repair/06_GATE_C2B4_ADVISOR_DECISION.json"
    thresholds = json.loads(decision_path.read_text())["thresholds"]
    checked = {}
    save = figures.save_figure

    def inspect_and_save(figure, directory, stem):
        axes = [axis for axis in figure.axes if axis.get_xlabel() == "Disease-blind resampling replicate"]
        if len(axes) != 1:
            raise AssertionError("Cannot identify Figure 1c")
        axis = axes[0]
        labels = [text.get_text() for text in axis.texts]
        if "minimum agreement criterion" not in labels or "minimum mapped-ARI criterion" in labels:
            raise AssertionError("Figure 1c still mislabels the agreement criterion")
        dashed = [line for line in axis.lines if line.get_linestyle() == "--"]
        expected = float(thresholds["minimum_mapping_agreement"])
        if len(dashed) != 1 or not np.allclose(dashed[0].get_ydata(), expected, rtol=0, atol=1e-12):
            raise AssertionError("Agreement guide differs from the frozen decision")
        checked.update({"actual_label":"minimum agreement criterion", "guide_y":expected,
                        "minimum_mapped_ari":thresholds["minimum_mapped_ari"],
                        "line_matches_frozen_agreement_threshold":True})
        save(figure, directory, stem)

    figures.ASSERTIONS.clear()
    figures.configure_style()
    figures.set_output_width_mm(170)
    with patch.object(figures, "save_figure", inspect_and_save):
        figures.build_figure1(root, figure_dir, source_dir, graphical_validation_workflow=True,
                              publication_source_data=True, explicit_threshold_semantics=True,
                              nature_evidence_hierarchy=True)
    original = root/"phase17_v7/post_gateC9/20260828_advisor_correction_review/source_data/Figure1_source_data.csv"
    if original.read_bytes() != (source_dir/"Figure1_source_data.csv").read_bytes():
        raise AssertionError("Figure 1 scientific source data changed")
    result = {"status":"PASS_FIGURE1_LABEL_CORRECTION_PREVIEW", **checked,
              "source_data_byte_identical":True,"source_data_sha256":digest(original),
              "frozen_threshold_source_sha256":digest(decision_path),
              "generator_sha256":digest(root/"audit_tools/phase17_c7_01_build_main_figures.py"),
              "assertions":figures.ASSERTIONS,
              "files":[{"path":path.relative_to(output).as_posix(),"bytes":path.stat().st_size,
                        "sha256":digest(path)} for path in sorted(output.rglob("*")) if path.is_file()],
              "integrated_into_approved_snapshot":False,"submission_authorized":False}
    (output/"01_LABEL_CORRECTION_AUDIT.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
