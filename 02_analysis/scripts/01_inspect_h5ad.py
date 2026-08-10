from __future__ import annotations

import argparse
import json
from pathlib import Path

import anndata as ad
import pandas as pd


CELL_TYPE_HINTS = ("cell_type", "celltype", "annotation", "cluster", "ident", "subclass", "label")
STATUS_HINTS = ("disease", "condition", "status", "case", "control", "diagnosis", "phenotype")
DONOR_HINTS = ("donor", "sample", "subject", "individual", "patient", "pool")


def summarize_frame(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        series = df[col]
        non_null = int(series.notna().sum())
        n_unique = int(series.nunique(dropna=True))
        examples = series.dropna().astype(str).unique()[:12]
        rows.append(
            {
                "column": col,
                "dtype": str(series.dtype),
                "non_null": non_null,
                "n_unique": n_unique,
                "examples": " | ".join(examples),
            }
        )
    return pd.DataFrame(rows)


def find_candidate_columns(columns: list[str], hints: tuple[str, ...]) -> list[str]:
    out = []
    for col in columns:
        low = col.lower()
        if any(h in low for h in hints):
            out.append(col)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect an H5AD file without loading the full matrix into memory.")
    parser.add_argument("--input", required=True, help="Path to .h5ad file")
    parser.add_argument("--outdir", default="02_analysis/data_inventory/h5ad_inspection", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    adata = ad.read_h5ad(input_path, backed="r")
    info = {
        "input": str(input_path),
        "n_obs": int(adata.n_obs),
        "n_vars": int(adata.n_vars),
        "obs_columns": list(map(str, adata.obs.columns)),
        "var_columns": list(map(str, adata.var.columns)),
        "obsm_keys": list(map(str, adata.obsm.keys())),
        "layers": list(map(str, adata.layers.keys())),
        "uns_keys": list(map(str, adata.uns.keys())),
        "candidate_cell_type_columns": find_candidate_columns(list(map(str, adata.obs.columns)), CELL_TYPE_HINTS),
        "candidate_status_columns": find_candidate_columns(list(map(str, adata.obs.columns)), STATUS_HINTS),
        "candidate_donor_columns": find_candidate_columns(list(map(str, adata.obs.columns)), DONOR_HINTS),
    }

    (outdir / "basic_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    summarize_frame(adata.obs).to_csv(outdir / "obs_columns_summary.csv", index=False, encoding="utf-8-sig")
    summarize_frame(adata.var).to_csv(outdir / "var_columns_summary.csv", index=False, encoding="utf-8-sig")

    print(json.dumps(info, indent=2))
    print(f"\nWrote inspection outputs to: {outdir}")
    print("\nNext: inspect obs_columns_summary.csv and choose the cell-type annotation column.")


if __name__ == "__main__":
    main()
