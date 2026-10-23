"""One look for every chart, and plain-English labels from the variable register.

Colours are the Okabe-Ito palette, which stays distinguishable for readers with colour-blindness.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import yaml
from matplotlib.ticker import FuncFormatter

PALETTE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
MAIN, ACCENT, GOOD, MUTED = PALETTE[0], PALETTE[1], PALETTE[2], "#8C8C8C"
RIGHTS = {"patent": PALETTE[0], "trade_mark": PALETTE[1], "design": PALETTE[2], "pbr": PALETTE[3]}

REGISTER = Path(__file__).with_name("variables.yaml")


def setup() -> None:
    """Apply the house style to matplotlib, seaborn and pandas. Call once at the top of a notebook."""
    sns.set_theme(style="whitegrid", context="notebook", palette=PALETTE)
    mpl.rcParams.update(
        {
            "figure.figsize": (11, 4.5),
            "figure.dpi": 100,
            "savefig.dpi": 110,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.constrained_layout.use": True,
        }
    )
    pd.set_option("display.max_rows", 40)
    pd.set_option("display.max_columns", 40)
    pd.set_option("display.width", 160)
    pd.set_option("display.float_format", lambda v: f"{v:,.4g}")


@cache
def register() -> dict:
    """The variable register (`variables.yaml`) as {lens: {column: {label, kind, unit, note}}}."""
    return yaml.safe_load(REGISTER.read_text())


def label(lens: str, column: str, unit: bool = True) -> str:
    """The plain-English label of a lens column, with its unit in brackets."""
    v = register().get(lens, {}).get(column)
    if v is None:
        return column
    return f"{v['label']} ({v['unit']})" if unit and v.get("unit") else v["label"]


def kind(lens: str, column: str) -> str | None:
    """The column's kind in the register: id, category, binary, count, money, numeric, rate, date or year."""
    return register().get(lens, {}).get(column, {}).get("kind")


def thousands(ax: plt.Axes, axis: str = "y") -> None:
    """Show an axis's numbers with thousands separators (and k, m, bn for large ones)."""

    def fmt(v, _):
        a = abs(v)
        if a >= 1e9:
            return f"{v / 1e9:,.1f}bn"
        if a >= 1e6:
            return f"{v / 1e6:,.1f}m"
        if a >= 1e4:
            return f"{v / 1e3:,.0f}k"
        return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"

    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(FuncFormatter(fmt))


def source(fig: plt.Figure, text: str) -> None:
    """A small grey caption under the figure naming its data (every chart should say where its numbers come from)."""
    fig.text(0.0, -0.02, f"Source: {text}", ha="left", va="top", fontsize=8.5, color=MUTED)
