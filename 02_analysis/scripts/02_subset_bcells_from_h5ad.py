from __future__ import annotations

import argparse
import re
from pathlib import Path

import anndata as ad
import numpy as np


DEFAULT_PATTERN = r"\bB\b|B cell|B-cell|plasmablast|plasma cell|ASC|antibody"


def main() -> None:
    parser = argparse.ArgumentParser(description="Subset B cells from a large H5AD using an obs annotation column.")
    parser.add_argument("--input", required=True, help="Path to source .h5ad")
    parser.add_argument("--output", required=True, help="Path to output B-cell .h5ad")
    parser.add_argument("--cell-type-column", required=True, help="obs column containing cell-type labels")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help="Regex for labels to keep")
    parser.add_argument("--max-cells", type=int, default=0, help="Optional smoke-test limit; 0 means keep all matched cells")
    parser.add_argument("--dry-run", action="store_true", help="Only print matching labels and counts")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    adata = ad.read_h5ad(input_path, backed="r")
    if args.cell_type_column not in adata.obs.columns:
        raise SystemExit(
            f"Column not found: {args.cell_type_column}\n"
            f"Available columns:\n" + "\n".join(map(str, adata.obs.columns))
        )

    labels = adata.obs[args.cell_type_column].astype(str)
    regex = re.compile(args.pattern, flags=re.IGNORECASE)
    mask = labels.map(lambda value: bool(regex.search(value))).to_numpy()

    counts = labels[mask].value_counts()
    print("Matched labels:")
    print(counts.to_string())
    print(f"\nMatched cells: {int(mask.sum())} / {adata.n_obs}")

    if args.dry_run:
        print("\nDry run only. No file written.")
        return

    if mask.sum() == 0:
        raise SystemExit("No cells matched. Adjust --pattern or --cell-type-column.")

    selected_idx = np.flatnonzero(mask)
    if args.max_cells and selected_idx.size > args.max_cells:
        selected_idx = selected_idx[: args.max_cells]
        print(f"Smoke-test mode: writing first {args.max_cells} matched cells.")

    print("Loading selected cells into memory and writing output...")
    selected_mem = adata[selected_idx, :].to_memory()
    selected_mem.write_h5ad(output_path, compression="gzip")
    print(f"Wrote: {output_path}")
    print(f"Shape: {selected_mem.n_obs} cells x {selected_mem.n_vars} genes")


if __name__ == "__main__":
    main()
