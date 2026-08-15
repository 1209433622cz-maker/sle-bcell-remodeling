#!/usr/bin/env python3
"""Gate C2B4: disease-blind adjudication of a two-level B-cell state model."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


POLICIES = {
    "five_state": {},
    "four_state_platelet_overlay_merged": {"2": "0"},
    "three_state_identity_core": {"2": "0", "4": "0"},
    "two_compartment_asc_vs_conventional": {"1": "0", "2": "0", "4": "0"},
}
POLICY_ORDER = list(POLICIES)
REQUIRED_ASC_MARKERS = {"TNFRSF17", "MZB1", "JCHAIN", "XBP1", "DERL3"}
THRESHOLDS = {
    "median_mapped_ari": 0.95,
    "minimum_mapped_ari": 0.90,
    "median_mapping_agreement": 0.995,
    "minimum_mapping_agreement": 0.990,
    "minimum_state_median_jaccard": 0.95,
    "asc_marker_sample_support": 0.90,
}


def collapse_label(value: object, collapse: dict[str, str]) -> str:
    label = str(value)
    return collapse.get(label, label)


def choose2(values):
    import numpy as np

    values = np.asarray(values, dtype=np.float64)
    return values * (values - 1.0) / 2.0


def adjusted_rand_from_counts(table) -> float:
    """Compute ARI from a contingency table without expanding cell-level labels."""
    import numpy as np

    counts = table.to_numpy(dtype=np.float64)
    n = counts.sum()
    if n < 2:
        return 1.0
    sum_cells = choose2(counts).sum()
    sum_rows = choose2(counts.sum(axis=1)).sum()
    sum_columns = choose2(counts.sum(axis=0)).sum()
    total_pairs = float(choose2([n])[0])
    expected = sum_rows * sum_columns / total_pairs
    maximum = 0.5 * (sum_rows + sum_columns)
    denominator = maximum - expected
    if np.isclose(denominator, 0.0):
        return 1.0 if np.isclose(sum_cells, maximum) else 0.0
    return float((sum_cells - expected) / denominator)


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_input_manifest(run_dir: Path):
    import pandas as pd

    manifest_path = run_dir / "17_gate_c2b3_integrity_manifest.csv"
    manifest = pd.read_csv(manifest_path)
    failures = []
    for row in manifest.itertuples(index=False):
        path = run_dir / str(row.relative_path)
        if not path.is_file():
            failures.append({"relative_path": row.relative_path, "issue": "missing"})
            continue
        if path.stat().st_size != int(row.size_bytes):
            failures.append({"relative_path": row.relative_path, "issue": "size"})
            continue
        if hash_file(path) != str(row.sha256).upper():
            failures.append({"relative_path": row.relative_path, "issue": "sha256"})
    return manifest, failures


def evaluate_policies(transitions, exact_policy_metrics):
    import numpy as np
    import pandas as pd

    replicate_rows = []
    state_rows = []
    transitions = transitions[np.isclose(transitions["resolution"], 0.4)].copy()
    transitions["reference_cluster"] = transitions["reference_cluster"].astype(str)
    transitions["mapped_reference_cluster"] = transitions["mapped_reference_cluster"].astype(str)

    for replicate, replicate_table in transitions.groupby("replicate", observed=True):
        for policy in POLICY_ORDER:
            collapse = POLICIES[policy]
            work = replicate_table.copy()
            work["reference_state"] = work["reference_cluster"].map(
                lambda value: collapse_label(value, collapse)
            )
            work["mapped_state"] = work["mapped_reference_cluster"].map(
                lambda value: collapse_label(value, collapse)
            )
            contingency = work.pivot_table(
                index="reference_state",
                columns="mapped_state",
                values="n_cells",
                aggfunc="sum",
                fill_value=0,
            )
            levels = sorted(
                set(contingency.index.astype(str)) | set(contingency.columns.astype(str)),
                key=lambda value: (len(value), value),
            )
            contingency = contingency.reindex(index=levels, columns=levels, fill_value=0)
            total = float(contingency.to_numpy().sum())
            diagonal = float(sum(contingency.loc[state, state] for state in levels))
            agreement = diagonal / total
            exact = exact_policy_metrics[
                (exact_policy_metrics["replicate"] == replicate)
                & (exact_policy_metrics["policy"] == policy)
            ]
            exact_agreement = (
                float(exact.iloc[0]["majority_mapping_agreement"])
                if len(exact) == 1 else float("nan")
            )
            replicate_rows.append(
                {
                    "replicate": int(replicate),
                    "policy": policy,
                    "n_states": len(levels),
                    "n_cells": int(total),
                    "mapped_adjusted_rand_index": adjusted_rand_from_counts(contingency),
                    "mapping_agreement": agreement,
                    "exact_saved_policy_agreement": exact_agreement,
                    "agreement_reconstruction_delta": (
                        agreement - exact_agreement if np.isfinite(exact_agreement) else np.nan
                    ),
                }
            )
            for state in levels:
                true_cells = float(contingency.loc[state].sum())
                mapped_cells = float(contingency[state].sum())
                intersection = float(contingency.loc[state, state])
                union = true_cells + mapped_cells - intersection
                state_rows.append(
                    {
                        "replicate": int(replicate),
                        "policy": policy,
                        "reference_state": state,
                        "reference_cells": int(true_cells),
                        "mapped_cells": int(mapped_cells),
                        "jaccard": intersection / union if union else 0.0,
                        "recall": intersection / true_cells if true_cells else 0.0,
                    }
                )
    return pd.DataFrame(replicate_rows), pd.DataFrame(state_rows)


def check(name: str, passed: bool, detail: str):
    return name, {"pass": bool(passed), "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c2b3-run-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    c2b3 = Path(args.c2b3_run_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    figure_dir = output / "figures"
    figure_dir.mkdir(exist_ok=True)

    required = {
        "resampling_status": c2b3 / "06_RESAMPLING_STATUS.json",
        "review": c2b3 / "16_GATE_C2B3_ADVISOR_REVIEW.json",
        "transitions": c2b3 / "02b_resampling_reference_transitions.csv",
        "policy_metrics": c2b3 / "01b_resampling_r04_policy_metrics.csv",
        "marker_dictionary": c2b3 / "12_neutral_marker_dictionary.csv",
        "marker_summary": c2b3 / "13_neutral_marker_dictionary_summary.csv",
        "marker_status": c2b3 / "14_MARKER_RANKING_STATUS.json",
        "mapping_status": c2b3 / "10_CANDIDATE_MAPPING_DECISION.json",
        "manifest": c2b3 / "17_gate_c2b3_integrity_manifest.csv",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing Gate C2B4 inputs: {missing}")

    input_manifest, integrity_failures = verify_input_manifest(c2b3)
    resampling_status = json.loads(required["resampling_status"].read_text(encoding="utf-8"))
    c2b3_review = json.loads(required["review"].read_text(encoding="utf-8"))
    marker_status = json.loads(required["marker_status"].read_text(encoding="utf-8"))
    mapping_status = json.loads(required["mapping_status"].read_text(encoding="utf-8"))
    transitions = pd.read_csv(required["transitions"])
    exact_policy_metrics = pd.read_csv(required["policy_metrics"])
    marker_dictionary = pd.read_csv(required["marker_dictionary"])
    marker_summary = pd.read_csv(required["marker_summary"])

    policy_metrics, state_metrics = evaluate_policies(transitions, exact_policy_metrics)
    policy_metrics.to_csv(
        output / "01_reconstructed_policy_metrics.csv", index=False, encoding="utf-8-sig"
    )
    policy_summary = (
        policy_metrics.groupby("policy", observed=True)
        .agg(
            replicates=("replicate", "nunique"),
            n_states=("n_states", "first"),
            median_mapped_ari=("mapped_adjusted_rand_index", "median"),
            minimum_mapped_ari=("mapped_adjusted_rand_index", "min"),
            median_mapping_agreement=("mapping_agreement", "median"),
            minimum_mapping_agreement=("mapping_agreement", "min"),
            maximum_absolute_reconstruction_delta=(
                "agreement_reconstruction_delta",
                lambda values: float(np.nanmax(np.abs(values)))
                if np.isfinite(values).any() else np.nan,
            ),
        )
        .reset_index()
    )
    state_summary = (
        state_metrics.groupby(["policy", "reference_state"], observed=True)
        .agg(
            median_jaccard=("jaccard", "median"),
            minimum_jaccard=("jaccard", "min"),
            median_recall=("recall", "median"),
            minimum_recall=("recall", "min"),
        )
        .reset_index()
    )
    policy_summary = policy_summary.merge(
        state_summary.groupby("policy", observed=True)
        .agg(
            minimum_state_median_jaccard=("median_jaccard", "min"),
            minimum_state_minimum_jaccard=("minimum_jaccard", "min"),
        )
        .reset_index(),
        on="policy",
        how="left",
    )
    policy_summary.to_csv(
        output / "02_reconstructed_policy_summary.csv", index=False, encoding="utf-8-sig"
    )
    binary_state_metrics = state_metrics[
        state_metrics["policy"] == "two_compartment_asc_vs_conventional"
    ].copy()
    binary_state_summary = state_summary[
        state_summary["policy"] == "two_compartment_asc_vs_conventional"
    ].copy()
    binary_state_metrics.to_csv(
        output / "03_two_compartment_state_stability.csv", index=False, encoding="utf-8-sig"
    )
    binary_state_summary.to_csv(
        output / "04_two_compartment_state_summary.csv", index=False, encoding="utf-8-sig"
    )

    existing = policy_summary[policy_summary["policy"].isin(POLICY_ORDER[:3])]
    max_equivalence_delta = float(
        existing["maximum_absolute_reconstruction_delta"].max()
    )
    binary = policy_summary[
        policy_summary["policy"] == "two_compartment_asc_vs_conventional"
    ].iloc[0]
    r04_markers = marker_dictionary[np.isclose(marker_dictionary["resolution"], 0.4)].copy()
    asc_markers = r04_markers[r04_markers["cluster"].astype(str) == "3"].copy()
    observed_asc_markers = set(asc_markers["gene"].astype(str))
    missing_asc_markers = sorted(REQUIRED_ASC_MARKERS - observed_asc_markers)
    required_support = asc_markers[asc_markers["gene"].isin(REQUIRED_ASC_MARKERS)][
        "sample_support_fraction"
    ].astype(float)
    r04_summary = marker_summary[np.isclose(marker_summary["resolution"], 0.4)].copy()
    asc_summary = r04_summary[r04_summary["cluster"].astype(str) == "3"]

    checks = dict(
        [
            check(
                "c2b3_integrity",
                not integrity_failures,
                f"{len(input_manifest) - len(integrity_failures)}/{len(input_manifest)} manifest rows verified",
            ),
            check(
                "source_hold_preserved",
                c2b3_review.get("decision") == "HOLD_GATE_C2B3_REVIEW_REQUIRED"
                and c2b3_review.get("outcome_unlock_authorized") is False,
                "original five/four/three-state HOLD remains unchanged",
            ),
            check(
                "representation_contract",
                int(resampling_status.get("schema_version", 0)) >= 2
                and resampling_status.get("representation_dimension_match") is True
                and int(resampling_status.get("n_pcs", -1)) == 50,
                f"schema={resampling_status.get('schema_version')}; PCs={resampling_status.get('n_pcs')}/50",
            ),
            check(
                "transition_reconstruction_equivalence",
                max_equivalence_delta <= 1e-12,
                f"maximum agreement delta={max_equivalence_delta:.3e}",
            ),
            check(
                "two_compartment_replicates",
                int(binary["replicates"]) == 20,
                f"{int(binary['replicates'])}/20 replicates",
            ),
            check(
                "two_compartment_median_mapped_ari",
                float(binary["median_mapped_ari"]) >= THRESHOLDS["median_mapped_ari"],
                f"{float(binary['median_mapped_ari']):.3f} >= {THRESHOLDS['median_mapped_ari']:.3f}",
            ),
            check(
                "two_compartment_minimum_mapped_ari",
                float(binary["minimum_mapped_ari"]) >= THRESHOLDS["minimum_mapped_ari"],
                f"{float(binary['minimum_mapped_ari']):.3f} >= {THRESHOLDS['minimum_mapped_ari']:.3f}",
            ),
            check(
                "two_compartment_median_mapping_agreement",
                float(binary["median_mapping_agreement"])
                >= THRESHOLDS["median_mapping_agreement"],
                f"{float(binary['median_mapping_agreement']):.4f} >= {THRESHOLDS['median_mapping_agreement']:.4f}",
            ),
            check(
                "two_compartment_minimum_mapping_agreement",
                float(binary["minimum_mapping_agreement"])
                >= THRESHOLDS["minimum_mapping_agreement"],
                f"{float(binary['minimum_mapping_agreement']):.4f} >= {THRESHOLDS['minimum_mapping_agreement']:.4f}",
            ),
            check(
                "two_compartment_state_jaccard",
                float(binary["minimum_state_median_jaccard"])
                >= THRESHOLDS["minimum_state_median_jaccard"],
                f"{float(binary['minimum_state_median_jaccard']):.3f} >= {THRESHOLDS['minimum_state_median_jaccard']:.3f}",
            ),
            check(
                "asc_marker_panel",
                not missing_asc_markers,
                "required markers present: " + ", ".join(sorted(REQUIRED_ASC_MARKERS)),
            ),
            check(
                "asc_marker_sample_support",
                len(required_support) == len(REQUIRED_ASC_MARKERS)
                and float(required_support.min()) >= THRESHOLDS["asc_marker_sample_support"],
                f"minimum required-marker support={float(required_support.min()):.3f}",
            ),
            check(
                "asc_cluster_sample_support",
                len(asc_summary) == 1
                and float(asc_summary.iloc[0]["median_sample_support"]) >= 0.90,
                f"cluster median support={float(asc_summary.iloc[0]['median_sample_support']):.3f}",
            ),
            check(
                "disease_blind_contract",
                resampling_status.get("disease_blind") is True
                and marker_status.get("disease_blind") is True
                and mapping_status.get("disease_blind") is True,
                "transition, marker and candidate evidence remain disease blind",
            ),
        ]
    )
    all_pass = all(result["pass"] for result in checks.values())
    decision = (
        "PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED"
        if all_pass else "HOLD_C2B4_TWO_COMPARTMENT_REVIEW_REQUIRED"
    )
    outcome_unlock = bool(all_pass)

    freeze_table = pd.DataFrame(
        [
            {
                "source_r04_cluster": "0",
                "frozen_neutral_id": "B_CONV",
                "identity_compartment": "conventional_B",
                "within_compartment_role": "naive-enriched anchor; model as continuous program",
            },
            {
                "source_r04_cluster": "1",
                "frozen_neutral_id": "B_CONV",
                "identity_compartment": "conventional_B",
                "within_compartment_role": "memory-enriched anchor; model as continuous program",
            },
            {
                "source_r04_cluster": "2",
                "frozen_neutral_id": "B_CONV",
                "identity_compartment": "conventional_B",
                "within_compartment_role": "platelet-associated overlay; sensitivity/program only",
            },
            {
                "source_r04_cluster": "3",
                "frozen_neutral_id": "B_ASC",
                "identity_compartment": "antibody_secreting_B",
                "within_compartment_role": "ASC identity compartment",
            },
            {
                "source_r04_cluster": "4",
                "frozen_neutral_id": "B_CONV",
                "identity_compartment": "conventional_B",
                "within_compartment_role": "unresolved boundary; no hard subtype claim",
            },
        ]
    )
    freeze_table["freeze_authorized"] = outcome_unlock
    freeze_table["hard_naive_memory_labels_authorized"] = False
    freeze_table.to_csv(
        output / "05_two_compartment_freeze_table.csv", index=False, encoding="utf-8-sig"
    )

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.4))
    colors = ["#6B7280", "#D97706", "#2563A6", "#008F7A"]
    labels = ["5-state", "4-state", "3-state", "2-compartment"]
    for index, policy in enumerate(POLICY_ORDER):
        values = policy_metrics[policy_metrics["policy"] == policy].sort_values("replicate")
        axes[0, 0].plot(
            values["replicate"], values["mapped_adjusted_rand_index"],
            marker="o", markersize=2.5, linewidth=0.8, color=colors[index], label=labels[index],
        )
    axes[0, 0].plot([1, 20], [0.90, 0.90], color="#444444", linestyle="--", linewidth=0.7)
    axes[0, 0].set(xlabel="Resampling replicate", ylabel="Mapped ARI", ylim=(0.25, 1.01))
    axes[0, 0].legend(frameon=False, fontsize=6, ncol=2)

    binary_values = policy_metrics[
        policy_metrics["policy"] == "two_compartment_asc_vs_conventional"
    ].sort_values("replicate")
    axes[0, 1].plot(
        binary_values["replicate"], binary_values["mapped_adjusted_rand_index"],
        marker="o", markersize=3, color="#2563A6", linewidth=0.9, label="Mapped ARI",
    )
    axes[0, 1].plot(
        binary_values["replicate"], binary_values["mapping_agreement"],
        marker="s", markersize=2.5, color="#008F7A", linewidth=0.9, label="Agreement",
    )
    axes[0, 1].plot([1, 20], [0.90, 0.90], color="#444444", linestyle="--", linewidth=0.7)
    axes[0, 1].set(xlabel="Resampling replicate", ylabel="Two-compartment stability", ylim=(0.88, 1.002))
    axes[0, 1].legend(frameon=False, fontsize=6)

    state_order = ["0", "3"]
    state_labels = ["Conventional B", "ASC"]
    distributions = [
        binary_state_metrics[binary_state_metrics["reference_state"] == state]["jaccard"]
        for state in state_order
    ]
    box = axes[1, 0].boxplot(distributions, patch_artist=True, widths=0.55, showfliers=True)
    for patch, color in zip(box["boxes"], ["#6BAED6", "#E76F51"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    axes[1, 0].plot([0.7, 2.3], [0.95, 0.95], color="#444444", linestyle="--", linewidth=0.7)
    axes[1, 0].set_xticks([1, 2], state_labels)
    axes[1, 0].set(ylabel="State Jaccard", ylim=(0.88, 1.002))

    marker_plot = asc_markers[asc_markers["gene"].isin(REQUIRED_ASC_MARKERS)].copy()
    marker_plot = marker_plot.set_index("gene").reindex(sorted(REQUIRED_ASC_MARKERS)).reset_index()
    marker_x = np.arange(len(marker_plot))
    marker_y = marker_plot["sample_support_fraction"].astype(float).to_numpy()
    axes[1, 1].plot(
        marker_x, marker_y, linestyle="none", marker="o", markersize=5, color="#E76F51",
    )
    axes[1, 1].plot([-0.5, 4.5], [0.90, 0.90], color="#444444", linestyle="--", linewidth=0.7)
    axes[1, 1].set_xticks(marker_x, marker_plot["gene"])
    axes[1, 1].set(ylabel="ASC marker sample support", ylim=(0, 1.05))
    axes[1, 1].tick_params(axis="x", rotation=35)
    for label, axis in zip("ABCD", axes.flat):
        axis.text(-0.14, 1.06, label, transform=axis.transAxes, fontsize=10, fontweight="bold")
        axis.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.12, top=0.96, wspace=0.30, hspace=0.38)
    fig.savefig(figure_dir / "c2b4_two_level_state_adjudication.png", dpi=300)
    fig.savefig(figure_dir / "c2b4_two_level_state_adjudication.pdf")
    plt.close(fig)

    decision_record = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "disease_blind": True,
        "source_c2b3_decision_preserved": c2b3_review.get("decision"),
        "identity_model": "two_compartment_with_continuous_within_conventional_programs",
        "frozen_neutral_ids": ["B_CONV", "B_ASC"],
        "outcome_unlock_authorized": outcome_unlock,
        "outcome_unlock_scope": (
            "two-compartment composition and prespecified continuous within-conventional programs"
            if outcome_unlock else "none"
        ),
        "hard_naive_memory_composition_authorized": False,
        "platelet_overlay_identity_authorized": False,
        "thresholds": THRESHOLDS,
        "two_compartment_metrics": {
            key: float(binary[key])
            for key in [
                "median_mapped_ari", "minimum_mapped_ari",
                "median_mapping_agreement", "minimum_mapping_agreement",
                "minimum_state_median_jaccard", "minimum_state_minimum_jaccard",
            ]
        },
        "checks": checks,
        "next_if_pass": "begin Gate C3 sample-level two-compartment composition and continuous-program design",
        "next_if_hold": "run independent full-graph seed decomposition before any outcome unlock",
    }
    (output / "06_GATE_C2B4_ADVISOR_DECISION.json").write_text(
        json.dumps(decision_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Gate C2B4 two-level state-model adjudication",
        "",
        f"**Decision:** `{decision}`",
        "",
        "## Binding model",
        "",
        "- Hard identity compartments: `B_CONV` and `B_ASC`.",
        "- Naive-memory structure: continuous within `B_CONV`; hard composition labels are prohibited.",
        "- Platelet-associated structure: overlay/sensitivity program, not a B-cell identity.",
        "- Source cluster 4: unresolved conventional-B boundary, not a publication subtype.",
        f"- Outcome unlock authorized: {outcome_unlock}.",
        "",
        "## Checks",
        "",
    ]
    for name, result in checks.items():
        label = "PASS" if result["pass"] else "FAIL"
        lines.append(f"- [{label}] {name}: {result['detail']}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The original C2B3 HOLD remains valid for five-, four- and three-state hard clustering.",
            "C2B4 does not relabel that failure. It replaces the unstable naive-memory partition with",
            "a disease-blind two-level model supported by resampling transitions and an orthogonal ASC",
            "marker panel. Only the scope recorded above may proceed to outcome-aware analysis.",
            "",
        ]
    )
    (output / "06_GATE_C2B4_ADVISOR_DECISION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    status = {
        "status": decision,
        "disease_blind": True,
        "source_c2b3_hold_preserved": True,
        "two_compartment_freeze_authorized": outcome_unlock,
        "hard_naive_memory_labels_authorized": False,
        "outcome_unlock_authorized": outcome_unlock,
    }
    (output / "00_GATE_C2B4_RUN_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    status_lines = [
        "# Gate C2B4 run status",
        "",
        f"**Status:** `{decision}`",
        "",
        f"- Source C2B3 HOLD preserved: True",
        f"- Two-compartment freeze authorized: {outcome_unlock}",
        "- Hard naive-memory labels authorized: False",
        f"- Outcome unlock authorized: {outcome_unlock}",
        "",
        "See `06_GATE_C2B4_ADVISOR_DECISION.md` for the binding scope.",
        "",
    ]
    (output / "00_GATE_C2B4_RUN_STATUS.md").write_text(
        "\n".join(status_lines), encoding="utf-8"
    )

    manifest_rows = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "07_gate_c2b4_integrity_manifest.csv":
            manifest_rows.append(
                {
                    "relative_path": path.relative_to(output).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": hash_file(path),
                }
            )
    pd.DataFrame(manifest_rows).to_csv(
        output / "07_gate_c2b4_integrity_manifest.csv", index=False, encoding="utf-8-sig"
    )
    print(json.dumps(decision_record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
