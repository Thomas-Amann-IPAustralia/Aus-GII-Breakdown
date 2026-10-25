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

# Short headings of the Nice classes (trade marks, WIPO's 12th edition) and the Locarno classes (designs, 14th
# edition), so a chart can name a class in words. The full headings are WIPO's.
NICE = {
    "1": "Chemicals",
    "2": "Paints",
    "3": "Cosmetics and cleaning products",
    "4": "Industrial oils and fuels",
    "5": "Pharmaceuticals",
    "6": "Common metals",
    "7": "Machines",
    "8": "Hand tools",
    "9": "Scientific and electronic apparatus, software",
    "10": "Medical apparatus",
    "11": "Lighting, heating, cooling and sanitary",
    "12": "Vehicles",
    "13": "Firearms and fireworks",
    "14": "Jewellery and clocks",
    "15": "Musical instruments",
    "16": "Paper and printed matter",
    "17": "Rubber, plastics and insulation",
    "18": "Leather goods and luggage",
    "19": "Building materials (not metal)",
    "20": "Furniture",
    "21": "Household utensils",
    "22": "Ropes, tents and sacks",
    "23": "Yarns and threads",
    "24": "Textiles",
    "25": "Clothing, footwear and headwear",
    "26": "Lace, buttons and haberdashery",
    "27": "Carpets and floor coverings",
    "28": "Games, toys and sporting goods",
    "29": "Meat, dairy and preserved foods",
    "30": "Staple foods (coffee, bread, sweets)",
    "31": "Fresh produce, plants and animals",
    "32": "Beer and soft drinks",
    "33": "Wine and spirits",
    "34": "Tobacco",
    "35": "Advertising and business services",
    "36": "Insurance, finance and real estate",
    "37": "Construction and repair",
    "38": "Telecommunications",
    "39": "Transport and storage",
    "40": "Treatment of materials",
    "41": "Education, entertainment and sport",
    "42": "Science and technology services, software",
    "43": "Food and drink services, accommodation",
    "44": "Medical, beauty and farming services",
    "45": "Legal, security and personal services",
}
LOCARNO = {
    "01": "Foodstuffs",
    "02": "Clothing",
    "03": "Travel goods and cases",
    "04": "Brushware",
    "05": "Textile piece goods",
    "06": "Furnishing",
    "07": "Household goods",
    "08": "Tools and hardware",
    "09": "Packages and containers",
    "10": "Clocks, watches and measuring instruments",
    "11": "Articles of adornment",
    "12": "Means of transport",
    "13": "Electricity generation and distribution",
    "14": "Recording, communication and computing equipment",
    "15": "Machines",
    "16": "Photographic and optical apparatus",
    "17": "Musical instruments",
    "18": "Printing and office machinery",
    "19": "Stationery and teaching materials",
    "20": "Sales and advertising equipment, signs",
    "21": "Games, toys and sporting goods",
    "22": "Arms, hunting and pest control",
    "23": "Fluid distribution, sanitary, heating and ventilation",
    "24": "Medical and laboratory equipment",
    "25": "Building units and construction elements",
    "26": "Lighting apparatus",
    "27": "Tobacco and smokers' supplies",
    "28": "Pharmaceutical, cosmetic and toilet products",
    "29": "Fire and rescue equipment",
    "30": "Animal care articles",
    "31": "Food and drink preparation machines",
    "32": "Graphic symbols, logos and patterns",
    "99": "Miscellaneous",
}


def class_name(ip_right_type: str, code: str) -> str:
    """A Nice or Locarno class code with its short heading ('35: Advertising and business services'); other codes
    (IPC subclasses, WIPO fields, plant genera) are returned unchanged."""
    names = {"trade_mark": NICE, "design": LOCARNO}.get(ip_right_type, {})
    return f"{code}: {names[code]}" if code in names else code


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


def mark_events(ax: plt.Axes, timeline: pd.DataFrame, *, ids: list[str] | None = None, labels: bool = True) -> None:
    """Dashed vertical lines at the months when IP policy changes took effect (from the timeline lens's
    `policy_events`), labelled with their ids. `ids` limits them to the changes that matter for the chart."""
    marked = timeline.loc[timeline["policy_events"].notna(), ["month", "policy_events"]]
    lo, hi = ax.get_xlim()
    for month, names in marked.itertuples(index=False):
        names = [n for n in names.split(", ") if ids is None or n in ids]
        x = mpl.dates.date2num(month)
        if not names or not lo <= x <= hi:
            continue
        ax.axvline(month, color=MUTED, ls="--", lw=1)
        if labels:
            ax.text(
                month,
                0.98,
                " " + ", ".join(names),
                transform=ax.get_xaxis_transform(),
                rotation=90,
                va="top",
                ha="right",
                fontsize=7.5,
                color=MUTED,
            )
