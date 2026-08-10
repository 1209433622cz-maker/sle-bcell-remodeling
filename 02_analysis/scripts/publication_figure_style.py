from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


NATURE_WORKING_WIDTH_IN = 6.8
NATURE_MAX_HEIGHT_IN = 170 / 25.4
NATURE_OUTPUT_DPI = 600
PANEL_LABEL_SIZE = 8


def apply_nature_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 6,
            "axes.titlesize": 7,
            "axes.labelsize": 6,
            "axes.linewidth": 0.5,
            "axes.titlepad": 3,
            "xtick.labelsize": 5.5,
            "ytick.labelsize": 5.5,
            "xtick.major.width": 0.5,
            "ytick.major.width": 0.5,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "legend.fontsize": 5.5,
            "legend.title_fontsize": 6,
            "lines.linewidth": 0.7,
            "patch.linewidth": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def nature_figsize(original_width: float, original_height: float) -> tuple[float, float]:
    height = NATURE_WORKING_WIDTH_IN * original_height / original_width
    return NATURE_WORKING_WIDTH_IN, min(height, NATURE_MAX_HEIGHT_IN)


def save_nature_figure(fig: plt.Figure, png_path: str | Path) -> None:
    path = Path(png_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"bbox_inches": "tight", "pad_inches": 0.02}
    fig.savefig(path, dpi=NATURE_OUTPUT_DPI, **kwargs)
    fig.savefig(path.with_suffix(".pdf"), **kwargs)
