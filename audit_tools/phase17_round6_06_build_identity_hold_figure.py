#!/usr/bin/env python3
"""Build Supplementary Figure S9 for the R1 identity reproducibility boundary."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
WIDTH_MM = 170.0
HEIGHT_MM = 160.0
COLORS = {
    "blue": "#377EB8",
    "teal": "#009E73",
    "orange": "#D55E00",
    "purple": "#756BB1",
    "gray": "#777777",
    "light": "#C8C8C8",
    "dark": "#222222",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--integration-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def style_axis(axis) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(labelsize=5.8, width=0.7, length=3)
    axis.xaxis.label.set_size(6.5)
    axis.yaxis.label.set_size(6.5)
    axis.title.set_fontsize(7.2)


def panel_label(axis, label: str, x: float = -0.14, y: float = 1.08) -> None:
    axis.text(
        x,
        y,
        label,
        transform=axis.transAxes,
        fontsize=8,
        fontweight="bold",
        ha="left",
        va="top",
    )


def main() -> None:
    args = parse_args()
    run = args.integration_dir.resolve()
    output = args.output_dir.resolve() if args.output_dir else run
    figure_dir = output / "figures"
    source_dir = output / "source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)

    branch = pd.read_csv(run / "01_RECOMPUTED_BRANCH_SUMMARY.csv")
    state = pd.read_csv(run / "02_RECOMPUTED_STATE_SUMMARY.csv")
    boundary = pd.read_csv(run / "03_BOUNDARY_EXCHANGE.csv")
    composition = pd.read_csv(run / "07_COMPOSITION_UNCERTAINTY_RESULTS.csv")
    ifn = pd.read_csv(run / "10_IFN_UNCERTAINTY_RESULTS.csv")
    prep_status = json.loads(
        (run / "06_AUDIT_AND_PROPAGATION_PREP_STATUS.json").read_text(encoding="utf-8")
    )
    composition_status = json.loads(
        (run / "09_COMPOSITION_UNCERTAINTY_STATUS.json").read_text(encoding="utf-8")
    )
    ifn_status = json.loads(
        (run / "12_IFN_UNCERTAINTY_STATUS.json").read_text(encoding="utf-8")
    )
    if prep_status["r1_decision"] != "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY":
        raise RuntimeError("S9 requires the formal R1 HOLD")
    if composition_status["status"] != "PASS_R1_IDENTITY_UNCERTAINTY_COMPOSITION_PROPAGATION":
        raise RuntimeError("Composition propagation is not qualified")
    if ifn_status["status"] != "PASS_R1_IDENTITY_UNCERTAINTY_IFN_PROPAGATION":
        raise RuntimeError("IFN propagation is not qualified")

    primary = branch.loc[
        branch["branch"].eq("harmony") & np.isclose(branch["resolution"], 0.4)
    ].iloc[0]
    metric_rows = pd.DataFrame(
        [
            ("Median mapped ARI", primary["median_mapped_ari"], 0.95),
            ("Minimum mapped ARI", primary["minimum_mapped_ari"], 0.90),
            ("Median agreement", primary["median_mapping_agreement"], 0.995),
            ("Minimum agreement", primary["minimum_mapping_agreement"], 0.990),
            ("Minimum state\nmedian Jaccard", primary["minimum_state_median_jaccard"], 0.95),
        ],
        columns=["metric", "observed", "threshold"],
    )
    metric_rows["pass"] = metric_rows["observed"] >= metric_rows["threshold"]
    primary_boundary = boundary.copy()
    primary_composition = composition.loc[composition["analysis"].eq("primary")].copy()
    ifn_plot = ifn.loc[ifn["analysis"].isin(["primary_base", "validation_nonoverlap"])].copy()
    if len(primary_boundary) != 40 or len(primary_composition) != 21 or len(ifn_plot) != 42:
        raise RuntimeError("Unexpected S9 source row counts")
    if metric_rows["pass"].sum() != 4 or bool(metric_rows.iloc[-1]["pass"]):
        raise RuntimeError("S9 threshold pattern is not the formal four-pass/one-fail result")
    basc = primary_boundary.loc[primary_boundary["reference_state"].eq("B_ASC")]
    bconv = primary_boundary.loc[primary_boundary["reference_state"].eq("B_CONV")]
    if not (basc["jaccard"] < 0.95).all() or not (bconv["jaccard"] > 0.95).all():
        raise RuntimeError("S9 state-specific boundary pattern differs")

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 6.2,
            "axes.linewidth": 0.75,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )
    figure = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4))
    grid = figure.add_gridspec(
        2,
        6,
        left=0.170 if os.environ.get("NPJ_SBA_STYLE") == "1" else 0.145,
        right=0.985,
        bottom=0.09,
        top=0.965,
        wspace=1.70,
        hspace=0.34,
    )

    axis = figure.add_subplot(grid[0, 0:3])
    y = np.arange(len(metric_rows))[::-1]
    for index, row in metric_rows.reset_index(drop=True).iterrows():
        y_value = y[index]
        axis.plot(
            [row["threshold"], row["observed"]],
            [y_value, y_value],
            color=COLORS["light"],
            lw=1.1,
            zorder=1,
        )
        axis.plot(row["threshold"], y_value, "|", color=COLORS["dark"], ms=9, mew=1.2)
        color = COLORS["teal"] if row["pass"] else COLORS["orange"]
        axis.plot(row["observed"], y_value, "o", color=color, ms=4.5, zorder=3)
        npj_style = os.environ.get("NPJ_SBA_STYLE") == "1"
        axis.text(
            0.972 if npj_style else 1.006,
            y_value,
            "PASS" if row["pass"] else "HOLD",
            fontsize=5.5,
            color=color,
            va="center",
            ha="left",
            clip_on=False,
        )
    axis.set_yticks(y, metric_rows["metric"])
    axis.set_xlim(0.885, 1.006)
    axis.set_xlabel("Observed value (dot); frozen criterion (tick)")
    axis.set_title("Four global criteria pass; state overlap holds", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "a", x=-0.22)

    axis = figure.add_subplot(grid[0, 3:6])
    for label, table, color, marker in (
        ("B_ASC", basc, COLORS["orange"], "o"),
        ("B_CONV", bconv, COLORS["blue"], "s"),
    ):
        axis.plot(
            table["replicate"],
            table["jaccard"],
            marker=marker,
            ms=3.2,
            lw=0.8,
            color=color,
            label=label,
        )
    axis.axhline(0.95, color=COLORS["gray"], ls="--", lw=0.8)
    axis.text(20.4, 0.9515, "frozen criterion", ha="right", va="bottom", fontsize=5.3)
    axis.set_xlim(0.5, 20.5)
    axis.set_ylim(0.855, 1.006)
    axis.set_xticks([1, 5, 10, 15, 20])
    axis.set_xlabel("End-to-end resampling replicate")
    axis.set_ylabel("State Jaccard")
    axis.legend(frameon=False, fontsize=5.8, loc="lower right")
    axis.set_title("The formal HOLD is B_ASC-specific", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "b", x=-0.20)

    axis = figure.add_subplot(grid[1, 0:2])
    axis.plot(
        basc["replicate"],
        basc["false_positive"],
        "o-",
        color=COLORS["orange"],
        ms=3,
        lw=0.8,
        label="B_CONV to B_ASC",
    )
    axis.plot(
        basc["replicate"],
        basc["false_negative"],
        "s-",
        color=COLORS["purple"],
        ms=3,
        lw=0.8,
        label="B_ASC to B_CONV",
    )
    axis.set_xlim(0.5, 20.5)
    axis.set_xticks([1, 5, 10, 15, 20])
    axis.set_xlabel("Replicate")
    axis.set_ylabel("Exchanged cells")
    axis.legend(frameon=False, fontsize=5.1, loc="upper right")
    axis.set_title("Broad-state boundary exchange", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "c", x=-0.28)

    axis = figure.add_subplot(grid[1, 2:4])
    baseline = primary_composition.loc[primary_composition["replicate"].eq(0)].iloc[0]
    sensitivity = primary_composition.loc[primary_composition["replicate"].gt(0)]
    axis.vlines(
        sensitivity["replicate"],
        sensitivity["ci_low"],
        sensitivity["ci_high"],
        color="#B5B5B5",
        lw=0.55,
        zorder=1,
    )
    axis.scatter(
        sensitivity["replicate"], sensitivity["odds_ratio"], s=10, color=COLORS["blue"], zorder=2
    )
    axis.axhline(1, color=COLORS["gray"], ls="--", lw=0.8)
    axis.axhline(baseline["odds_ratio"], color=COLORS["orange"], lw=0.9)
    axis.text(
        20.4,
        baseline["odds_ratio"] - 0.025,
        "frozen OR",
        ha="right",
        va="top",
        fontsize=5.2,
        color=COLORS["orange"],
    )
    axis.set_xlim(0.5, 20.5)
    axis.set_xticks([1, 5, 10, 15, 20])
    axis.set_ylim(0.42, 1.48)
    axis.set_xlabel("Boundary-exchange replicate")
    axis.set_ylabel("Primary B_ASC odds ratio (95% CI)")
    axis.set_title("Primary composition remains null", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "d", x=-0.28)

    axis = figure.add_subplot(grid[1, 4:6])
    plot_definitions = (
        ("primary_base", "Discovery", COLORS["blue"], "o"),
        ("validation_nonoverlap", "Internal nonoverlap", COLORS["teal"], "s"),
    )
    for analysis, label, color, marker in plot_definitions:
        table = ifn_plot.loc[ifn_plot["analysis"].eq(analysis)]
        baseline = table.loc[table["replicate"].eq(0), "effect"].iloc[0]
        table = table.loc[table["replicate"].gt(0)]
        axis.plot(
            table["replicate"],
            table["effect"],
            marker=marker,
            ms=3,
            lw=0.8,
            color=color,
            label=label,
        )
        axis.axhline(baseline, color=color, ls=":", lw=0.75)
    axis.axhline(0, color=COLORS["gray"], ls="--", lw=0.8)
    axis.set_xlim(0.5, 20.5)
    axis.set_xticks([1, 5, 10, 15, 20])
    axis.set_ylim(0, 1.18)
    axis.set_xlabel("Boundary-exchange replicate")
    axis.set_ylabel("IFN/ISG effect")
    axis.legend(frameon=False, fontsize=5.1, loc="lower right")
    axis.set_title("B_CONV IFN effects are retained", loc="left", pad=4)
    style_axis(axis)
    panel_label(axis, "e", x=-0.28)

    pdf_path = figure_dir / "Supplementary_Figure_S9_identity_boundary_and_propagation.pdf"
    png_path = figure_dir / "Supplementary_Figure_S9_identity_boundary_and_propagation.png"
    from publication_style_contract import apply_publication_style
    apply_publication_style(figure)
    figure.savefig(
        pdf_path,
        format="pdf",
        dpi=600,
        metadata={"Creator": "Round 6 reproducible figure builder", "CreationDate": None},
    )
    figure.savefig(png_path, format="png", dpi=600)
    plt.close(figure)

    source_frames: list[pd.DataFrame] = []
    source_frames.append(metric_rows.assign(panel="a", record_type="threshold_audit"))
    source_frames.append(primary_boundary.assign(panel="b", record_type="state_jaccard"))
    source_frames.append(
        basc[["replicate", "false_positive", "false_negative"]].assign(
            panel="c", record_type="boundary_exchange"
        )
    )
    source_frames.append(
        primary_composition.assign(panel="d", record_type="composition_propagation")
    )
    source_frames.append(ifn_plot.assign(panel="e", record_type="ifn_propagation"))
    source_data = pd.concat(source_frames, ignore_index=True, sort=False)
    source_path = source_dir / "Supplementary_Figure_S9_source_data.csv"
    source_data.to_csv(source_path, index=False)

    page = PdfReader(str(pdf_path)).pages[0]
    width_mm = float(page.mediabox.width) * 25.4 / 72
    height_mm = float(page.mediabox.height) * 25.4 / 72
    checks = {
        "width_170mm": abs(width_mm - WIDTH_MM) < 0.01,
        "five_panels": set(source_data["panel"]) == {"a", "b", "c", "d", "e"},
        "formal_four_pass_one_hold": int(metric_rows["pass"].sum()) == 4,
        "basc_below_state_threshold_all_replicates": bool((basc["jaccard"] < 0.95).all()),
        "bconv_above_state_threshold_all_replicates": bool((bconv["jaccard"] > 0.95).all()),
        "primary_composition_intervals_include_one": bool(
            (
                (sensitivity["ci_low"] <= 1)
                & (sensitivity["ci_high"] >= 1)
            ).all()
        ),
        "ifn_effects_positive": bool((ifn_plot.loc[ifn_plot["replicate"].gt(0), "effect"] > 0).all()),
        "ifn_intervals_above_zero": bool(
            (ifn_plot.loc[ifn_plot["replicate"].gt(0), "ci_low"] > 0).all()
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"S9 assertions failed: {checks}")
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_ROUND6_SUPPLEMENTARY_FIGURE_S9_BUILT",
        "decision": "ACCEPT_R1_HOLD_WITH_DOWNSTREAM_ROBUSTNESS_BOUNDARY",
        "figure_pdf": pdf_path.relative_to(ROOT).as_posix(),
        "figure_png": png_path.relative_to(ROOT).as_posix(),
        "source_data": source_path.relative_to(ROOT).as_posix(),
        "width_mm": round(width_mm, 3),
        "height_mm": round(height_mm, 3),
        "source_rows": len(source_data),
        "checks": checks,
    }
    (output / "13_SUPPLEMENTARY_FIGURE_S9_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    review = f"""# Round 6 R1 HOLD advisor review

Date: 2026-08-27
Decision: **ACCEPT THE FORMAL HOLD AND NARROW THE TAXONOMY CLAIM**

## Integrity decision

- All 20 full-data replicates completed and all 20 Harmony runs converged.
- Replicate contracts, input and executable hashes, aggregate tables and final status were independently reproduced from replicate-level files.
- Four of five frozen criteria passed. The minimum state-median Jaccard was {primary['minimum_state_median_jaccard']:.6f}, below the unchanged 0.95 criterion; `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY` is retained.
- The failing state is `B_ASC`: median Jaccard {prep_status['state_medians']['B_ASC']['median_jaccard']:.6f}. `B_CONV` median Jaccard was {prep_status['state_medians']['B_CONV']['median_jaccard']:.6f}.
- The median broad-state exchange was {prep_status['boundary_exchange']['median_changed_cells']:.0f} of 120,320 sampled cells per replicate.

## Downstream propagation

- Replacing only the observed boundary-exchange cells in the complete frozen partition yielded primary B_ASC odds ratios from {composition_status['primary']['minimum_odds_ratio']:.3f} to {composition_status['primary']['maximum_odds_ratio']:.3f}; all 20 confidence intervals included one.
- The primary B_CONV IFN/ISG effect ranged from 0.836 to 0.845; the donor-nonoverlap effect ranged from 1.059 to 1.087. All 40 effects were positive and all confidence intervals remained above zero.
- These are robustness sensitivities on the same data, not new replication.

## Authorized interpretation

The full-pipeline result prevents a stronger claim that `B_CONV`/`B_ASC` is a universally reproducible taxonomy. It does not invalidate the frozen disease-blind analysis partition, the primary B_ASC null result or the independently replicated within-B_CONV IFN/ISG program. The permitted framing is:

> End-to-end reconstruction retained high global two-compartment concordance but missed the prespecified B_ASC state-overlap criterion. We therefore use B_CONV/B_ASC as a disease-blind analysis scaffold rather than a universally reproducible taxonomy; observed boundary exchanges did not alter the primary composition null or the B_CONV IFN/ISG effects.

Do not:

- relax the 0.95 Jaccard threshold;
- remove replicate 1 or any other weak replicate;
- rerun with alternative seeds to obtain PASS;
- call the broad partition end-to-end reproducible without the HOLD qualification;
- describe propagation sensitivities as independent validation.

## Publication placement

Place Supplementary Figure S9 and its Source Data in the supplementary information. Figure 1 should identify panels b-d as frozen-representation resampling. The manuscript title should refer to unstable state **assignments**, not unstable biological states.
"""
    (output / "14_ROUND6_R1_HOLD_ADVISOR_REVIEW.md").write_text(
        review, encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
