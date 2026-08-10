from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import scanpy as sc


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot metadata UMAPs from first-pass B-cell H5AD.")
    parser.add_argument("--input", required=True, help="bcell_first_pass_processed.h5ad")
    parser.add_argument("--outdir", required=True, help="Output figure directory")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    sc.settings.figdir = str(outdir)
    adata = sc.read_h5ad(args.input)

    colors = [col for col in ["leiden", "ct_cov", "disease", "disease_state", "author_cell_type", "cell_type"] if col in adata.obs]
    if colors:
        sc.pl.umap(adata, color=colors, wspace=0.35, show=False, save="_metadata_overview.png")
        plt.close("all")
    print(f"Wrote metadata UMAPs to: {outdir}")


if __name__ == "__main__":
    main()
