from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot donor-level cluster fractions by disease.")
    parser.add_argument("--donor-fractions", required=True, help="donor_cluster_fractions.csv")
    parser.add_argument("--tests", required=True, help="donor_cluster_fraction_disease_tests.csv")
    parser.add_argument("--output", required=True, help="Output PNG")
    args = parser.parse_args()

    frac = pd.read_csv(args.donor_fractions)
    tests = pd.read_csv(args.tests)
    frac["leiden"] = frac["leiden"].astype(str)
    tests["leiden"] = tests["leiden"].astype(str)
    order = sorted(frac["leiden"].unique(), key=lambda x: int(x) if x.isdigit() else x)

    label_map = {
        row["leiden"]: f"C{row['leiden']}\nFDR={row['fdr_bh']:.1e}" for _, row in tests.iterrows()
    }
    frac["cluster_label"] = frac["leiden"].map(label_map).fillna("C" + frac["leiden"])
    label_order = [label_map.get(cluster, "C" + cluster) for cluster in order]

    sns.set_theme(style="whitegrid", context="talk")
    plt.figure(figsize=(16, 6))
    ax = sns.boxplot(
        data=frac,
        x="cluster_label",
        y="fraction_within_donor",
        hue="disease",
        order=label_order,
        showfliers=False,
        linewidth=1,
    )
    sns.stripplot(
        data=frac,
        x="cluster_label",
        y="fraction_within_donor",
        hue="disease",
        order=label_order,
        dodge=True,
        alpha=0.35,
        size=2,
        linewidth=0,
        ax=ax,
    )
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], title="Disease", loc="upper right", frameon=True)
    ax.set_xlabel("Leiden cluster")
    ax.set_ylabel("Fraction of donor B-lineage cells")
    ax.set_title("Donor-level B-cell cluster fractions")
    plt.xticks(rotation=0)
    plt.tight_layout()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
