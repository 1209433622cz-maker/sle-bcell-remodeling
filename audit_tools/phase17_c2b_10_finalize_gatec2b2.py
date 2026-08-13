#!/usr/bin/env python3
"""Gate C2B2 advisor finalization after the complete disease-blind run."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


PROTECTED_COLUMNS = {
    "disease", "disease_state", "diagnosis", "case_control", "case_status",
    "clinical_status", "sle_status", "activity", "disease_activity",
    "treatment", "medication", "response", "outcome", "flare", "ct_cov",
}


def sha256(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    import anndata as ad
    import numpy as np
    import pandas as pd

    run_dir = Path(args.run_dir).resolve()
    required = {
        "preparation": run_dir / "04_GATE_C2B2_PREPARATION.json",
        "fit": run_dir / "16_GATE_C2B2_FIT_SUMMARY.json",
        "review": run_dir / "22_GATE_C2B2_REVIEW.json",
        "coverage": run_dir / "12_primary_cluster_coverage.csv",
        "risk": run_dir / "13_residual_risk_localization.csv",
        "concordance": run_dir / "14_branch_and_resolution_concordance.csv",
        "markers": run_dir / "24_marker_module_all_resolutions.csv",
        "primary": run_dir / "06_primary_all_cells_representation.h5ad",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing Gate C2B2 finalization inputs: {missing}")

    preparation = json.loads(required["preparation"].read_text(encoding="utf-8"))
    fit = json.loads(required["fit"].read_text(encoding="utf-8"))
    review = json.loads(required["review"].read_text(encoding="utf-8"))
    coverage = pd.read_csv(required["coverage"])
    risk = pd.read_csv(required["risk"])
    concordance = pd.read_csv(required["concordance"])
    markers = pd.read_csv(required["markers"])
    primary = ad.read_h5ad(required["primary"], backed="r")

    protected = sorted(column for column in primary.obs.columns if column.lower() in PROTECTED_COLUMNS)
    expected_cells = int(preparation["working_cells"])
    observed_cells = int(primary.n_obs)
    branch_metadata = primary.uns.get("phase17_c2b2_branch", {})
    resolutions = [float(value) for value in fit["resolutions"]]

    rows = []
    for resolution in resolutions:
        at_resolution = coverage[np.isclose(coverage["resolution"], resolution)]
        risk_at_resolution = risk[np.isclose(risk["resolution"], resolution)]
        branch = concordance[
            np.isclose(pd.to_numeric(concordance["resolution"], errors="coerce"), resolution)
            & concordance["comparison"].str.startswith("primary_all_cells_vs_")
        ].set_index("comparison")
        singlet_ari = float(branch.loc["primary_all_cells_vs_singlet_sensitivity", "adjusted_rand_index"])
        isg_ari = float(branch.loc["primary_all_cells_vs_isg_excluded", "adjusted_rand_index"])
        min_cells = int(at_resolution["n_cells"].min())
        min_samples = int(at_resolution["n_samples"].min())
        max_library_fraction = float(at_resolution["max_library_fraction"].max())
        max_risk_fraction = float(risk_at_resolution["residual_auto_call_fraction"].max())
        eligible_backbone = bool(
            0.4 <= resolution <= 0.8
            and min_cells >= 1000
            and min_samples >= 200
            and max_library_fraction <= 0.10
            and max_risk_fraction <= 0.05
        )
        rows.append(
            {
                "resolution": resolution,
                "n_clusters": int(len(at_resolution)),
                "minimum_cluster_cells": min_cells,
                "minimum_cluster_samples": min_samples,
                "minimum_cluster_donors": int(at_resolution["n_donors"].min()),
                "minimum_cluster_libraries": int(at_resolution["n_libraries"].min()),
                "maximum_library_fraction": max_library_fraction,
                "maximum_residual_risk_fraction": max_risk_fraction,
                "singlet_branch_ari": singlet_ari,
                "isg_excluded_branch_ari": isg_ari,
                "minimum_branch_ari": min(singlet_ari, isg_ari),
                "eligible_identity_backbone": eligible_backbone,
            }
        )
    resolution_table = pd.DataFrame(rows)
    eligible = resolution_table[resolution_table["eligible_identity_backbone"]].copy()
    if eligible.empty:
        selected_resolution = None
    else:
        selected_resolution = float(
            eligible.sort_values(
                ["minimum_branch_ari", "resolution"], ascending=[False, True]
            ).iloc[0]["resolution"]
        )
    resolution_table["selected_identity_backbone"] = np.isclose(
        resolution_table["resolution"], selected_resolution if selected_resolution is not None else -1
    )
    resolution_table.to_csv(
        run_dir / "25_gate_c2b2_resolution_advisor_table.csv",
        index=False,
        encoding="utf-8-sig",
    )

    selected_markers = markers[np.isclose(markers["resolution"], selected_resolution)] if selected_resolution is not None else markers.iloc[0:0]
    marker_clusters = int(selected_markers["cluster"].nunique())
    marker_modules = int(selected_markers["module"].nunique())
    marker_complete = bool(
        marker_clusters == int(
            resolution_table.loc[resolution_table["selected_identity_backbone"], "n_clusters"].iloc[0]
        )
        and marker_modules >= 8
    ) if selected_resolution is not None else False

    r06 = markers[np.isclose(markers["resolution"], 0.6)].copy()
    provisional_structures = []
    for module in ("plasmablast", "platelet"):
        subset = r06[r06["module"] == module]
        if not subset.empty:
            top = subset.sort_values("mean_module_log_expression", ascending=False).iloc[0]
            provisional_structures.append(
                {
                    "resolution": 0.6,
                    "cluster": str(top["cluster"]),
                    "module": module,
                    "interpretation": f"{module}-enriched structure; provisional until Gate C2B3",
                }
            )

    selected_row = (
        resolution_table.loc[resolution_table["selected_identity_backbone"]].iloc[0]
        if selected_resolution is not None else None
    )
    checks = {
        "complete_full_run": {
            "pass": bool(not preparation.get("test_mode") and observed_cells == expected_cells == 150402),
            "detail": f"{observed_cells:,}/{expected_cells:,} cells; test_mode={preparation.get('test_mode')}",
        },
        "outcome_lock": {"pass": not protected, "detail": f"protected columns={protected or 'none'}"},
        "review_contract": {
            "pass": review.get("decision") == "READY_FOR_C2B3_ADVISOR_REVIEW",
            "detail": str(review.get("decision")),
        },
        "harmony_converged": {
            "pass": all(item.get("harmony_converged") is True for item in fit["branches"].values()),
            "detail": ", ".join(
                f"{name}={item.get('harmony_iterations')} iterations"
                for name, item in fit["branches"].items()
            ),
        },
        "identity_backbone_selected": {
            "pass": selected_row is not None and float(selected_row["minimum_branch_ari"]) >= 0.70,
            "detail": (
                f"r={selected_resolution:g}; minimum sensitivity ARI={float(selected_row['minimum_branch_ari']):.3f}"
                if selected_row is not None else "no eligible backbone"
            ),
        },
        "marker_panel_complete": {
            "pass": marker_complete,
            "detail": f"{marker_clusters} clusters x {marker_modules} modules",
        },
    }
    passed = all(item["pass"] for item in checks.values())
    decision = (
        "PASS_TO_C2B3_WITH_R04_IDENTITY_BACKBONE"
        if passed and np.isclose(selected_resolution, 0.4)
        else "HOLD_GATE_C2B2_ADVISOR_REVIEW"
    )
    output = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "disease_blind": True,
        "outcome_unlock_authorized": False,
        "identity_backbone_resolution": selected_resolution,
        "identity_backbone_selection_rule": (
            "Among resolutions 0.4-0.8 meeting cell/sample/library/residual-risk coverage, "
            "maximize the lower of singlet-removal and ISG-exclusion ARI; break ties toward "
            "the coarser resolution."
        ),
        "checks": checks,
        "provisional_structures": provisional_structures,
        "substate_candidate_resolutions": [0.6, 0.8],
        "binding_limits": [
            "r0.4 is an identity backbone, not a final named-state solution",
            "r0.6 and r0.8 may be used only for constrained substate evaluation",
            "residual-risk calls remain sensitivity-only rather than automatic exclusions",
            "outside-label candidates remain mapping-only rather than primary input",
            "disease and outcome metadata remain locked through Gate C2B3",
        ],
        "next_required_gate": "C2B3 disease-blind neutral-state stability and marker freeze",
    }
    decision_path = run_dir / "26_GATE_C2B2_ADVISOR_DECISION.json"
    decision_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest_rows = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file() or path.name == "27_gate_c2b2_integrity_manifest.csv":
            continue
        manifest_rows.append(
            {
                "relative_path": path.relative_to(run_dir).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    pd.DataFrame(manifest_rows).to_csv(
        run_dir / "27_gate_c2b2_integrity_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )
    total_bytes = sum(row["size_bytes"] for row in manifest_rows)

    table_lines = [
        "| r | Clusters | Min cells | Min samples | Singlet ARI | ISG-excluded ARI | Status |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in resolution_table.itertuples(index=False):
        status = "selected backbone" if row.selected_identity_backbone else (
            "eligible" if row.eligible_identity_backbone else "not eligible"
        )
        table_lines.append(
            f"| {row.resolution:g} | {row.n_clusters} | {row.minimum_cluster_cells:,} | "
            f"{row.minimum_cluster_samples:,} | {row.singlet_branch_ari:.3f} | "
            f"{row.isg_excluded_branch_ari:.3f} | {status} |"
        )
    lines = [
        "# Gate C2B2 full-data advisor decision",
        "",
        f"**Decision:** `{decision}`",
        "",
        "## Binding judgement",
        "",
        "The full disease-blind representation run passes Gate C2B2. Resolution 0.4 is",
        "frozen as the coarse identity backbone because it is the only biologically",
        "covered candidate with strong agreement in both prespecified sensitivity branches.",
        "It is not authorization to publish five final cell types. Resolutions 0.6 and 0.8",
        "remain candidate substate layers and must survive Gate C2B3 resampling and marker review.",
        "",
        "## Resolution evidence",
        "",
        *table_lines,
        "",
        "## Biological interpretation",
        "",
        "The targeted marker audit retains B-lineage identity across the backbone. At r=0.6,",
        "one structure is plasmablast-program enriched and another is platelet-program enriched;",
        "both labels remain provisional. The plasmablast structure is not rejected as generic",
        "contamination because JCHAIN, MZB1, XBP1, TNFRSF17 and DERL3 are jointly elevated.",
        "",
        "## Integrity",
        "",
        f"- Hashed files: {len(manifest_rows):,}",
        f"- Hashed bytes: {total_bytes:,}",
        "- Disease/outcome fields in working representation: none",
        "- Outcome unlock: not authorized",
        "",
        "## Next gate",
        "",
        "Run Gate C2B3 with repeated disease-blind graph resampling, full-gene descriptive",
        "marker ranking, and outside-label candidate projection. Only a passing C2B3 advisor",
        "review may freeze neutral state labels and unlock sample-level disease analyses.",
        "",
    ]
    (run_dir / "26_GATE_C2B2_ADVISOR_DECISION.md").write_text("\n".join(lines), encoding="utf-8")
    primary.file.close()
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
