#!/usr/bin/env python3
"""Gate C2B3-04: bind neutral-state stability, marker, and candidate-mapping evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def check(name: str, passed: bool, detail: str):
    return name, {"pass": bool(passed), "detail": detail}


def sha256(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--identity-resolution", type=float, default=0.4)
    args = parser.parse_args()

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    run_dir = Path(args.run_dir).resolve()
    required = {
        "resampling_status": run_dir / "06_RESAMPLING_STATUS.json",
        "resampling": run_dir / "03_resampling_resolution_summary.csv",
        "clusters": run_dir / "04_resampling_cluster_summary.csv",
        "mapping": run_dir / "10_CANDIDATE_MAPPING_DECISION.json",
        "marker_status": run_dir / "14_MARKER_RANKING_STATUS.json",
        "marker_summary": run_dir / "13_neutral_marker_dictionary_summary.csv",
        "marker_dictionary": run_dir / "12_neutral_marker_dictionary.csv",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing Gate C2B3 inputs: {missing}")
    resampling_status = json.loads(required["resampling_status"].read_text(encoding="utf-8"))
    mapping = json.loads(required["mapping"].read_text(encoding="utf-8"))
    marker_status = json.loads(required["marker_status"].read_text(encoding="utf-8"))
    resampling = pd.read_csv(required["resampling"])
    clusters = pd.read_csv(required["clusters"])
    marker_summary = pd.read_csv(required["marker_summary"])
    marker_dictionary = pd.read_csv(required["marker_dictionary"])
    test_mode = bool(
        resampling_status.get("test_mode")
        or mapping.get("test_mode")
        or marker_status.get("test_mode")
    )
    identity = resampling[np.isclose(resampling["resolution"], args.identity_resolution)]
    identity_clusters = clusters[np.isclose(clusters["resolution"], args.identity_resolution)]
    identity_markers = marker_summary[np.isclose(marker_summary["resolution"], args.identity_resolution)]
    if len(identity) != 1:
        raise RuntimeError("Identity-resolution resampling summary is missing or duplicated")
    identity = identity.iloc[0]
    expected_clusters = int(identity_clusters["reference_cluster"].nunique())

    checks = dict(
        [
            check(
                "resampling_complete",
                resampling_status.get("status") in {"FULL_RESAMPLING_COMPLETE_REVIEW_REQUIRED", "SOFTWARE_TEST_COMPLETE"},
                f"{resampling_status.get('replicates')} replicates; {resampling_status.get('analysis_cells'):,} cells",
            ),
            check("identity_median_ari", float(identity["median_ari"]) >= 0.75, f"{float(identity['median_ari']):.3f} >= 0.750"),
            check("identity_minimum_ari", float(identity["minimum_ari"]) >= 0.65, f"{float(identity['minimum_ari']):.3f} >= 0.650"),
            check(
                "identity_mapping_agreement",
                float(identity["median_mapping_agreement"]) >= 0.80,
                f"median={float(identity['median_mapping_agreement']):.3f} >= 0.800",
            ),
            check(
                "identity_cluster_jaccard",
                float(identity["minimum_cluster_median_jaccard"]) >= 0.60,
                f"minimum cluster median={float(identity['minimum_cluster_median_jaccard']):.3f} >= 0.600",
            ),
            check(
                "marker_dictionary_complete",
                identity_markers["cluster"].nunique() == expected_clusters
                and bool((identity_markers["markers"] >= 10).all()),
                f"{identity_markers['cluster'].nunique()}/{expected_clusters} clusters; minimum markers={int(identity_markers['markers'].min())}",
            ),
            check(
                "marker_sample_support",
                bool((identity_markers["median_sample_support"] >= 0.50).all()),
                f"minimum cluster median={identity_markers['median_sample_support'].min():.3f}",
            ),
            check(
                "candidate_mapping_complete",
                mapping.get("decision") == "MAPPING_COMPLETE_NO_AUTOMATIC_APPEND"
                and mapping.get("automatic_append_authorized") is False,
                f"{mapping.get('candidates'):,} candidates; automatic append=False",
            ),
            check(
                "disease_blind_contract",
                resampling_status.get("disease_blind") is True
                and marker_status.get("disease_blind") is True
                and mapping.get("disease_blind") is True,
                "all three C2B3 components are disease blind",
            ),
        ]
    )
    structural_names = {"resampling_complete", "marker_dictionary_complete", "candidate_mapping_complete", "disease_blind_contract"}
    if test_mode:
        decision = (
            "SOFTWARE_TEST_PASS_NOT_BIOLOGICAL_GATE"
            if all(checks[name]["pass"] for name in structural_names)
            else "SOFTWARE_TEST_FAIL"
        )
        outcome_unlock = False
    else:
        all_pass = all(result["pass"] for result in checks.values())
        decision = "PASS_NEUTRAL_STATE_FREEZE_OUTCOME_UNLOCK_AUTHORIZED" if all_pass else "HOLD_GATE_C2B3_REVIEW_REQUIRED"
        outcome_unlock = all_pass

    clusters_sorted = sorted(identity_clusters["reference_cluster"].astype(str).unique(), key=lambda value: (len(value), value))
    freeze_table = pd.DataFrame(
        {
            "identity_resolution": args.identity_resolution,
            "source_cluster": clusters_sorted,
            "frozen_neutral_id": [f"B{i}" for i in range(len(clusters_sorted))],
            "biological_annotation": "pending marker-led advisor annotation",
            "publication_label_authorized": False,
        }
    )
    freeze_table.to_csv(run_dir / "15_neutral_state_freeze_table.csv", index=False, encoding="utf-8-sig")
    review = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "disease_blind": True,
        "test_mode": test_mode,
        "identity_resolution": args.identity_resolution,
        "neutral_ids": freeze_table["frozen_neutral_id"].tolist(),
        "outcome_unlock_authorized": outcome_unlock,
        "publication_labels_authorized": False,
        "checks": checks,
        "candidate_policy": "mapping sensitivity only; source-label primary unchanged",
        "next_if_pass": "join protected metadata and begin Gate C3 sample-level composition",
        "next_if_hold": "repair unstable identity clusters before any outcome unlock",
    }
    (run_dir / "16_GATE_C2B3_ADVISOR_REVIEW.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    fig, axis = plt.subplots(figsize=(6.2, 3.8))
    ordered = resampling.sort_values("resolution")
    axis.plot(ordered["resolution"], ordered["median_ari"], marker="o", label="Median ARI", color="#277DA1")
    axis.plot(ordered["resolution"], ordered["minimum_ari"], marker="s", label="Minimum ARI", color="#D1495B")
    axis.axhline(0.75, color="#777777", linewidth=0.8, linestyle="--")
    axis.set(xlabel="Leiden resolution", ylabel="Resampling agreement", ylim=(0, 1.02))
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False)
    fig.tight_layout()
    figure_dir = run_dir / "figures"
    figure_dir.mkdir(exist_ok=True)
    fig.savefig(figure_dir / "c2b3_resampling_stability.png", dpi=280, bbox_inches="tight")
    fig.savefig(figure_dir / "c2b3_resampling_stability.pdf", bbox_inches="tight")
    plt.close(fig)

    lines = [
        "# Gate C2B3 neutral-state advisor review",
        "",
        f"**Decision:** `{decision}`",
        "",
        f"- Identity backbone: r={args.identity_resolution:g}",
        f"- Neutral IDs evaluated: {', '.join(freeze_table['frozen_neutral_id'])}",
        f"- Outcome unlock authorized: {outcome_unlock}",
        "- Publication-ready biological labels authorized: False",
        "",
        "## Checks",
        "",
    ]
    for name, result in checks.items():
        lines.append(f"- [{'PASS' if result['pass'] else 'FAIL'}] {name}: {result['detail']}")
    lines.extend(
        [
            "",
            "## Binding interpretation",
            "",
            (
                "This is a software-only test. Full-data state freezing and outcome unlock are not authorized."
                if test_mode else
                "Passing this gate freezes neutral IDs for inference. Biological display names remain pending a marker-led advisor annotation table and cannot be outcome-derived."
            ),
            "",
        ]
    )
    (run_dir / "16_GATE_C2B3_ADVISOR_REVIEW.md").write_text("\n".join(lines), encoding="utf-8")
    run_status = {
        "status": decision,
        "disease_blind": True,
        "full_candidate_mapping_complete": not mapping.get("test_mode", False),
        "full_marker_ranking_complete": not marker_status.get("test_mode", False),
        "full_resampling_complete": not resampling_status.get("test_mode", False),
        "neutral_state_freeze_authorized": outcome_unlock,
        "outcome_unlock_authorized": outcome_unlock,
    }
    (run_dir / "00_GATE_C2B3_RUN_STATUS.json").write_text(
        json.dumps(run_status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    status_lines = [
        "# Gate C2B3 run status",
        "",
        f"**Status:** `{decision}`",
        "",
        f"- Full candidate mapping complete: {run_status['full_candidate_mapping_complete']}",
        f"- Full marker ranking complete: {run_status['full_marker_ranking_complete']}",
        f"- Full resampling complete: {run_status['full_resampling_complete']}",
        f"- Neutral-state freeze authorized: {outcome_unlock}",
        f"- Outcome unlock authorized: {outcome_unlock}",
        "",
        "See `16_GATE_C2B3_ADVISOR_REVIEW.md` for binding checks and interpretation.",
        "",
    ]
    (run_dir / "00_GATE_C2B3_RUN_STATUS.md").write_text(
        "\n".join(status_lines), encoding="utf-8"
    )
    manifest_rows = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file() or path.name == "17_gate_c2b3_integrity_manifest.csv":
            continue
        manifest_rows.append(
            {
                "relative_path": path.relative_to(run_dir).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    pd.DataFrame(manifest_rows).to_csv(
        run_dir / "17_gate_c2b3_integrity_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )
    print(json.dumps(review, ensure_ascii=False, indent=2))
    return 0 if not decision.endswith("FAIL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
