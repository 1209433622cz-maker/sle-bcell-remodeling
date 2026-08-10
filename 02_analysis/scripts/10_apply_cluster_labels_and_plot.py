from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import scanpy as sc


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply draft cluster labels and plot state-level UMAPs.")
    parser.add_argument("--input-h5ad", required=True)
    parser.add_argument("--scores", required=True)
    parser.add_argument("--annotation", required=True)
    parser.add_argument("--output-h5ad", required=True)
    parser.add_argument("--output-scores", required=True)
    parser.add_argument("--figdir", required=True)
    args = parser.parse_args()

    annotation = pd.read_csv(args.annotation)
    label_map = dict(zip(annotation["leiden"].astype(str), annotation["draft_label"]))

    adata = sc.read_h5ad(args.input_h5ad)
    adata.obs["leiden"] = adata.obs["leiden"].astype(str)
    adata.obs["draft_state"] = adata.obs["leiden"].map(label_map).astype("category")

    scores = pd.read_csv(args.scores, index_col=0)
    scores["leiden"] = scores["leiden"].astype(str)
    scores["draft_state"] = scores["leiden"].map(label_map)

    Path(args.output_h5ad).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_scores).parent.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(args.output_h5ad, compression="gzip")
    scores.to_csv(args.output_scores, encoding="utf-8-sig")

    figdir = Path(args.figdir)
    figdir.mkdir(parents=True, exist_ok=True)
    sc.settings.figdir = str(figdir)
    color = ["draft_state", "leiden"]
    for col in ["disease", "disease_state", "ct_cov"]:
        if col in adata.obs:
            color.append(col)
    sc.pl.umap(adata, color=color, wspace=0.35, show=False, save="_draft_state_metadata.png")
    plt.close("all")

    print(f"Wrote: {args.output_h5ad}")
    print(f"Wrote: {args.output_scores}")
    print(f"Wrote figures to: {figdir}")


if __name__ == "__main__":
    main()
