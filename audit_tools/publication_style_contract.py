"""Shared final-size typography for source-driven scientific figure redraws."""

import os
import re
from matplotlib.collections import Collection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Annotation, Text
import numpy as np


def apply_publication_style(figure, width_mm=170.0):
    if os.environ.get("NPJ_SBA_STYLE") == "1":
        return apply_npj_sba_style(figure, width_mm)
    width, height = figure.get_size_inches()
    figure.set_size_inches(width_mm / 25.4, height * width_mm / (25.4 * width), forward=True)
    figure.canvas.draw()


def apply_npj_sba_style(figure, width_mm=170.0):
    """Apply the frozen npj SBA visual contract without changing plotted data."""

    width, height = figure.get_size_inches()
    figure.set_size_inches(width_mm / 25.4, height * width_mm / (25.4 * width), forward=True)
    figure.set_facecolor("white")
    figure.patch.set_facecolor("white")
    figure.canvas.draw()
    for item in figure.findobj(Text):
        if isinstance(item, Annotation) and item.arrow_patch is not None:
            item.arrow_patch.set_linewidth(max(1.0, item.arrow_patch.get_linewidth()))
        if not item.get_visible() or not item.get_text().strip():
            continue
        panel = re.fullmatch(r"[a-z]", item.get_text().strip()) and item.get_fontweight() in ("bold", 700)
        item.set_fontsize(8.0)
        item.set_fontfamily("Arial")
        if panel:
            item.set_fontweight("bold")
        bbox_patch = item.get_bbox_patch()
        if bbox_patch is not None and bbox_patch.get_linewidth() > 0:
            bbox_patch.set_linewidth(max(1.0, bbox_patch.get_linewidth()))
    for item in figure.findobj():
        if isinstance(item, (Line2D, Patch)) and item.get_linewidth() > 0:
            item.set_linewidth(max(1.0, item.get_linewidth()))
        if isinstance(item, Line2D) and item.get_markeredgewidth() > 0:
            item.set_markeredgewidth(max(1.0, item.get_markeredgewidth()))
        if isinstance(item, Collection) and hasattr(item, "get_linewidths"):
            widths = np.asarray(item.get_linewidths())
            if widths.size:
                item.set_linewidths(np.where(widths > 0, np.maximum(widths, 1.0), widths))
    figure.canvas.draw()
