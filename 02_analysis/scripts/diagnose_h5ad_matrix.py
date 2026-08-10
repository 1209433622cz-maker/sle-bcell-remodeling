from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import scanpy as sc
from scipy import sparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    adata = sc.read_h5ad(Path(args.input))
    print("shape", adata.shape)
    print("X type", type(adata.X))
    x = adata.X
    if sparse.issparse(x):
        data = x.data
        print("sparse nnz", x.nnz)
        print("data min", float(np.nanmin(data)))
        print("data max", float(np.nanmax(data)))
        print("data mean", float(np.nanmean(data)))
        print("negative nnz", int((data < 0).sum()))
        sums = np.asarray(x.sum(axis=1)).ravel()
    else:
        print("dense min", float(np.nanmin(x)))
        print("dense max", float(np.nanmax(x)))
        print("dense mean", float(np.nanmean(x)))
        print("negative count", int((x < 0).sum()))
        sums = np.asarray(x.sum(axis=1)).ravel()

    print("cell sum min", float(np.nanmin(sums)))
    print("cell sum max", float(np.nanmax(sums)))
    print("cell sum mean", float(np.nanmean(sums)))
    print("zero_or_negative_sums", int((sums <= 0).sum()))
    if "feature_is_filtered" in adata.var:
        print("feature_is_filtered counts")
        print(adata.var["feature_is_filtered"].value_counts(dropna=False).to_string())
    print("first var_names", list(map(str, adata.var_names[:10])))
    if "feature_name" in adata.var:
        print("first feature_name", list(map(str, adata.var["feature_name"].head(10))))


if __name__ == "__main__":
    main()
