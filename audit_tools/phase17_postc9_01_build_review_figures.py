"""Rebuild review figures from frozen results and expose the corrected C9 HOLD."""

import argparse
import json
from pathlib import Path
import os
import subprocess
import sys

os.environ["MPLBACKEND"] = "Agg"
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

import phase17_c7_01_build_main_figures as main_figures
import phase17_c8s_01_build_supplementary_figures as supplements
from phase17_c9_common import integrity_manifest, write_csv, write_json
from publication_style_contract import apply_publication_style


def build_s10(
    c9: Path,
    figure_dir: Path,
    source_dir: Path,
    *,
    semantic_harmonization: bool = False,
    reader_facing_criterion_labels: bool = False,
) -> None:
    decision = json.loads((c9 / "15_GATE_C9A_PREFREEZE_DECISION.json").read_text())
    if decision["outcome_unlock_authorized"]:
        raise RuntimeError("S10 is the pre-outcome C9 calibration-HOLD diagnostic")
    calibration = pd.read_csv(c9 / "07_MAPPER_CONFIDENCE_CALIBRATION.csv")
    chosen = calibration.loc[calibration["selected"]].set_index("mapper")
    library = pd.read_csv(c9 / "03_REFERENCE_LIBRARY_SIZE_AUDIT.csv")
    cv = pd.read_csv(c9 / "06_MAPPER_DONOR_GROUPED_CV.csv")
    alpha = decision["reference_model"]["chosen_alpha"]
    cv = cv.loc[cv["mapper"].eq("nearest_centroid") | cv["parameter"].eq(f"alpha={alpha:g};l1_ratio=0.5")]
    figure, axes = plt.subplots(2, 2, figsize=(170 / 25.4, 110 / 25.4), constrained_layout=True)
    mappers = ["elastic_net", "nearest_centroid"]
    names = ["Elastic net", "Centroid"]
    colors = ["#2C6EAD", "#D55E00"] if semantic_harmonization else ["#2878B5", "#C44536"]
    summaries = []
    for x, state in enumerate(["B_CONV", "B_ASC"]):
        values = library.loc[library["state"].eq(state), "legacy_prelog_inflation_factor"]
        q1, median, q3 = values.quantile([0.25, 0.5, 0.75])
        panel_a_color = "#555555" if semantic_harmonization else colors[x]
        panel_a_marker = ["o", "s"][x] if semantic_harmonization else "o"
        axes[0, 0].errorbar(
            x,
            median,
            yerr=[[median-q1], [q3-median]],
            fmt=panel_a_marker,
            color=panel_a_color,
            capsize=3,
        )
        summaries.append({"panel":"a", "state":state, "n":len(values), "q25":q1, "median":median, "q75":q3})
    axes[0, 0].set_xticks([0, 1], ["B_CONV", "B_ASC"])
    axes[0, 0].set_xlim(-0.6, 1.6)
    axes[0, 0].set_ylabel("Full / feature-only library counts")
    axes[0, 0].set_title(
        "Legacy denominator mismatch" if semantic_harmonization else "Normalization mismatch corrected",
        loc="left",
    )
    if semantic_harmonization:
        state_definitions = (
            (-0.09, "B_CONV_precision", "B_CONV", "o"),
            (0.09, "B_ASC_precision", "B_ASC", "s"),
        )
        for offset, metric, _label, marker in state_definitions:
            for x, mapper in enumerate(mappers):
                axes[0, 1].scatter(
                    x + offset,
                    chosen.loc[mapper, metric],
                    color=colors[x],
                    marker=marker,
                    s=25,
                )
    else:
        for offset, metric, label, color, marker in (
            (-0.10,"B_CONV_precision","B_CONV",colors[0],"o"),
            (0.10,"B_ASC_precision","B_ASC",colors[1],"s"),
        ):
            axes[0, 1].scatter(np.arange(2)+offset, chosen.loc[mappers,metric], label=label, color=color, marker=marker, s=25)
    axes[0, 1].axhline(0.90, color="#666666", lw=.7, ls="--")
    axes[0, 1].set_xticks([0, 1], names)
    axes[0, 1].set_xlim(-.6, 1.6)
    axes[0, 1].set_ylim(.80, 1.02)
    axes[0, 1].set_ylabel("Reference precision")
    axes[0, 1].set_title(
        (
            "Elastic-net B_ASC precision below criterion"
            if reader_facing_criterion_labels
            else "Primary mapper misses B_ASC gate"
        )
        if semantic_harmonization
        else "Frozen precision gate",
        loc="left",
    )
    if semantic_harmonization:
        axes[0, 1].text(
            0.98,
            0.905,
            "state-precision criterion",
            transform=axes[0, 1].get_yaxis_transform(),
            ha="right",
            va="bottom",
            color="#555555",
            fontsize=5.5,
        )
        state_handles = [
            Line2D([0], [0], marker="o", linestyle="none", color="#555555", markersize=4, label="B_CONV"),
            Line2D([0], [0], marker="s", linestyle="none", color="#555555", markersize=4, label="B_ASC"),
        ]
        axes[0, 1].legend(handles=state_handles, frameon=False, fontsize=6, loc="lower right")
    else:
        axes[0, 1].legend(frameon=False, fontsize=6, loc="lower right")
    if semantic_harmonization:
        for x, mapper in enumerate(mappers):
            coverage = float(chosen.loc[mapper, "coverage"])
            axes[1, 0].vlines(x, 0.80, coverage, color=colors[x], lw=1.5)
            axes[1, 0].scatter(x, coverage, color=colors[x], s=28, zorder=3)
            axes[1, 0].text(x, coverage + 0.007, f"{coverage:.3f}", ha="center", va="bottom", fontsize=5.7)
    else:
        axes[1, 0].bar(names, chosen.loc[mappers,"coverage"], width=.45, color=colors)
    axes[1, 0].axhline(.80,color="#666666",lw=.7,ls="--")
    axes[1, 0].set_xticks([0, 1], names)
    axes[1, 0].set_xlim(-.6, 1.6)
    axes[1, 0].set_ylim(0.77 if semantic_harmonization else 0,1.02)
    axes[1, 0].set_ylabel("Reference cells retained")
    axes[1, 0].set_title(
        (
            "Coverage criterion met by both mappers"
            if reader_facing_criterion_labels
            else "Coverage passes for both mappers"
        )
        if semantic_harmonization
        else "Frozen coverage gate",
        loc="left",
    )
    if semantic_harmonization:
        axes[1, 0].text(
            0.98,
            0.805,
            "coverage criterion",
            transform=axes[1, 0].get_yaxis_transform(),
            ha="right",
            va="bottom",
            color="#555555",
            fontsize=5.5,
        )
    for x, mapper in enumerate(mappers):
        values=cv.loc[cv["mapper"].eq(mapper),"balanced_accuracy"].to_numpy()
        axes[1, 1].scatter(x+np.linspace(-.08,.08,len(values)),values,color=colors[x],s=15)
        if semantic_harmonization:
            mean_value = float(np.mean(values))
            axes[1, 1].plot([x - 0.16, x + 0.16], [mean_value, mean_value], color="#222222", lw=1.0)
            axes[1, 1].text(x, 0.922, f"mean {mean_value:.3f}", ha="center", va="bottom", fontsize=5.5, color="#555555")
    if not semantic_harmonization:
        axes[1, 1].axhline(.90,color="#666666",lw=.7,ls="--")
    axes[1, 1].set_xticks([0,1],names)
    axes[1, 1].set_xlim(-.6,1.6)
    axes[1, 1].set_ylim(.92 if semantic_harmonization else .85,.98 if semantic_harmonization else 1.01)
    axes[1, 1].set_ylabel("Balanced accuracy")
    axes[1, 1].set_title(
        "Donor-grouped folds (diagnostic only)"
        if semantic_harmonization
        else "Donor-grouped calibration folds",
        loc="left",
    )
    for axis,label in zip(axes.flat,"abcd"):
        supplements.style_axis(axis)
        supplements.panel_label(axis,label)
    apply_publication_style(figure)
    stem="Supplementary_Figure_S10_reference_calibration_boundary"
    figure.savefig(figure_dir / f"{stem}.pdf")
    figure.savefig(figure_dir / f"{stem}.png",dpi=600)
    plt.close(figure)
    source=pd.concat([pd.DataFrame(summaries),chosen.reset_index().assign(panel="b-c"),cv.assign(panel="d")],ignore_index=True)
    write_csv(source,source_dir / "Supplementary_Figure_S10_source_data.csv")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--c9-dir",type=Path,required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    output=args.output_dir.resolve()
    figure_dir=output / "figures"
    source_dir=output / "source_data"
    figure_dir.mkdir(parents=True,exist_ok=True)
    source_dir.mkdir(parents=True,exist_ok=True)
    main_figures.ASSERTIONS.clear()
    main_figures.configure_style()
    main_figures.set_output_width_mm(170)
    main_figures.build_figure1(root,figure_dir,source_dir,graphical_validation_workflow=True,
        publication_source_data=True,explicit_threshold_semantics=True,nature_evidence_hierarchy=True)
    main_figures.build_figure2(root,figure_dir,source_dir)
    main_figures.build_figure3(root,figure_dir,source_dir)
    main_figures.build_figure4(root,figure_dir,source_dir,reader_facing_source_labels=True)
    main_figures.build_figure5(root,figure_dir,source_dir,proliferation_specificity_comparators=True,
        parallel_evidence_branches=True,three_evidence_branches=True)
    supplements.ASSERTIONS.clear()
    supplements.configure_style()
    for builder in (supplements.build_s1,supplements.build_s2,supplements.build_s3,
                    supplements.build_s4,supplements.build_s5,supplements.build_s6,supplements.build_s7):
        builder(root,figure_dir,source_dir)
    subprocess.run([sys.executable,str(root / "audit_tools/phase17_round6_02_build_overlap_depletion_figure.py"),
                    "--output-dir",str(output)],check=True)
    subprocess.run([sys.executable,str(root / "audit_tools/phase17_round6_06_build_identity_hold_figure.py"),
                    "--integration-dir",str(root / "phase17_v7/round6_q1_robustness/20260827_r1_hold_integration"),
                    "--output-dir",str(output)],check=True)
    build_s10(args.c9_dir.resolve(),figure_dir,source_dir)
    checks=main_figures.ASSERTIONS+supplements.ASSERTIONS
    write_json({"status":"BUILT_PENDING_VISUAL_REVIEW","assertions":len(checks),
                "all_pass":all(row["pass"] for row in checks),"checks":checks,
                "scope":"Source-driven redraw of Figures 1-5 and S1-S9; new S10 shows calibration HOLD only"},
               output / "01_FIGURE_BUILD_ASSERTIONS.json")
    write_csv(integrity_manifest(output),output / "02_REVIEW_FIGURE_MANIFEST.csv")


if __name__=="__main__":
    main()
