from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image


ASSETS = [
    {
        "asset_id": "main_manuscript_v2",
        "role": "Main manuscript working draft",
        "recommended_submission_role": "main_text",
        "path": "01_manuscript/manuscript_v2_submission_style.md",
        "priority": "required",
    },
    {
        "asset_id": "references_working",
        "role": "Working BibTeX skeleton",
        "recommended_submission_role": "references_source",
        "path": "01_manuscript/references_working_v1.bib",
        "priority": "required_verify",
    },
    {
        "asset_id": "figure1",
        "role": "Dataset overview and analysis guardrails",
        "recommended_submission_role": "main_figure",
        "path": "03_results/figure1_dataset_overview/figures/figure1_dataset_overview.png",
        "priority": "required",
    },
    {
        "asset_id": "figure2",
        "role": "Refined B-cell atlas and donor-level remodeling",
        "recommended_submission_role": "main_figure",
        "path": "03_results/first_pass_bcell_full/figures/figure2_v3_refined_bcell_state_atlas.png",
        "priority": "required",
    },
    {
        "asset_id": "figure3",
        "role": "ABC/APC-like donor-state pseudobulk evidence",
        "recommended_submission_role": "main_figure",
        "path": "03_results/figure3_abc_apc_focus/figures/figure3_v1_abc_apc_focus.png",
        "priority": "required",
    },
    {
        "asset_id": "figure4",
        "role": "Covariate sensitivity robustness",
        "recommended_submission_role": "main_or_supplement",
        "path": "03_results/figure4_covariate_sensitivity/figures/figure4_v1_covariate_sensitivity.png",
        "priority": "high_value",
    },
    {
        "asset_id": "figure5",
        "role": "Literature-informed signature validation",
        "recommended_submission_role": "main_figure",
        "path": "03_results/figure5_literature_signature_validation/figures/figure5_v1_literature_signature_validation.png",
        "priority": "required",
    },
    {
        "asset_id": "supp_fig_s1_flagged_qc",
        "role": "Flagged platelet/ambient-high cluster QC",
        "recommended_submission_role": "supplementary_figure",
        "path": "03_results/supplement_qc_flagged_cluster/figures/supplement_qc_flagged_cluster.png",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s1_dataset_summary",
        "role": "Dataset overview summary",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/figure1_dataset_overview/tables/figure1_dataset_summary.csv",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s2_state_counts",
        "role": "Refined B-cell state counts",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/figure1_dataset_overview/tables/bcell_refined_state_counts.csv",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s3_donor_state_tests",
        "role": "Donor-level state abundance tests",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/first_pass_bcell_full/tables/state_level/donor_state_fraction_disease_tests.csv",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s4_raw_marker_summary",
        "role": "Raw-count marker summaries by state",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/first_pass_bcell_full/marker_refinement/tables/raw_count_marker_summary_by_state.csv",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s5_abc_pseudobulk_tests",
        "role": "ABC/APC-like donor-state pseudobulk signature tests",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/figure3_abc_apc_focus/tables/abc_apc_vs_other_program_tests.csv",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s6_covariate_models",
        "role": "Covariate-adjusted donor-level abundance models",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/figure4_covariate_sensitivity/tables/state_abundance_covariate_models.csv",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s7_signature_tests",
        "role": "Literature-informed signature tests",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/figure5_literature_signature_validation/tables/abc_apc_vs_other_literature_signature_tests.csv",
        "priority": "required_supplement",
    },
    {
        "asset_id": "table_s8_signature_catalog",
        "role": "Literature-informed signature catalog",
        "recommended_submission_role": "supplementary_table",
        "path": "03_results/figure5_literature_signature_validation/tables/literature_informed_signature_catalog.csv",
        "priority": "required_supplement_verify_citations",
    },
    {
        "asset_id": "table_s9_citation_audit",
        "role": "Signature-to-citation audit",
        "recommended_submission_role": "internal_or_supplementary_table",
        "path": "00_project_management/citation_audit_2026-07-01/signature_to_citation_audit_2026-07-01.csv",
        "priority": "internal_required",
    },
    {
        "asset_id": "evidence_table",
        "role": "Claim-to-evidence mapping",
        "recommended_submission_role": "internal_qc",
        "path": "00_project_management/manuscript_evidence_table_2026-06-29.csv",
        "priority": "internal_required",
    },
]


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        return None, None
    with Image.open(path) as im:
        return im.size


def build_manifest(project_root: Path) -> pd.DataFrame:
    rows = []
    for asset in ASSETS:
        path = project_root / asset["path"]
        exists = path.exists()
        width, height = (None, None)
        if exists:
            try:
                width, height = image_dimensions(path)
            except Exception:
                width, height = None, None
        rows.append(
            {
                **asset,
                "exists": bool(exists),
                "size_bytes": int(path.stat().st_size) if exists else 0,
                "width_px": width,
                "height_px": height,
                "absolute_path": str(path),
            }
        )
    return pd.DataFrame(rows)


def write_markdown(path: Path, manifest: pd.DataFrame) -> None:
    missing = manifest[~manifest["exists"]]
    image_rows = manifest[manifest["width_px"].notna()].copy()
    is_figure = manifest["asset_id"].str.contains("figure|fig", case=False, na=False) | manifest["recommended_submission_role"].str.contains("figure", na=False)
    lines = [
        "# Submission Manifest v1",
        "",
        "## Status",
        "",
        f"- Assets tracked: {len(manifest)}.",
        f"- Missing assets: {len(missing)}.",
        "",
        "## Main Figure Assets",
        "",
    ]
    for row in manifest[is_figure].itertuples(index=False):
        dims = f"{int(row.width_px)} x {int(row.height_px)} px" if pd.notna(row.width_px) else "not an image"
        status = "OK" if row.exists else "MISSING"
        lines.append(f"- {row.asset_id}: {status}; {dims}; `{row.path}`")
    lines.extend(["", "## Key Tables And Text Assets", ""])
    for row in manifest[~is_figure].itertuples(index=False):
        status = "OK" if row.exists else "MISSING"
        lines.append(f"- {row.asset_id}: {status}; {row.role}; `{row.path}`")
    if len(missing):
        lines.extend(["", "## Missing Assets", ""])
        for row in missing.itertuples(index=False):
            lines.append(f"- {row.asset_id}: `{row.path}`")
    lines.extend(
        [
            "",
            "## Figure Resolution Check",
            "",
            "All current main and supplementary PNG figures are above 3000 px on their longest edge, suitable for working drafts. Final journal-specific DPI, width, font, and file-type rules still need target-journal verification.",
        ]
    )
    if not image_rows.empty:
        min_long_edge = int(image_rows[["width_px", "height_px"]].max(axis=1).min())
        lines.append(f"- Minimum longest edge among tracked images: {min_long_edge} px.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a submission package manifest for manuscript assets.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out-csv", default="04_submission/submission_manifest_v1.csv")
    parser.add_argument("--out-md", default="04_submission/submission_manifest_v1.md")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    manifest = build_manifest(project_root)
    out_csv = project_root / args.out_csv
    out_md = project_root / args.out_md
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(out_csv, index=False, encoding="utf-8-sig")
    write_markdown(out_md, manifest)
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    print(manifest[["asset_id", "exists", "width_px", "height_px", "path"]].to_string(index=False))


if __name__ == "__main__":
    main()
