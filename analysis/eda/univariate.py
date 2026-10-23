"""Stage 1: one variable at a time.

Each function returns a small table or a figure, never the raw rows, so a notebook stays readable and small.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .style import ACCENT, MAIN, MUTED, label, thousands


def overview(df: pd.DataFrame, lens: str | None = None) -> pd.DataFrame:
    """One row per column: its kind, how complete it is, how many distinct values, and its range or top value."""
    from .style import kind

    rows = []
    for c in df.columns:
        s, k = df[c], kind(lens, c) if lens else None
        filled, distinct = int(s.notna().sum()), s.nunique(dropna=True)
        vc = s.value_counts(dropna=True) if distinct < filled else None  # every value unique: no "most common"
        rows.append(
            {
                "column": c,
                "label": label(lens, c) if lens else c,
                "kind": k,
                "dtype": str(s.dtype),
                "% filled": 100 * filled / len(s) if len(s) else None,
                "distinct": distinct,
                "min": _show(s.min(), k) if _orderable(s) else None,
                "max": _show(s.max(), k) if _orderable(s) else None,
                "most common": None
                if vc is None or vc.empty
                else f"{_top(vc.index[0])} ({100 * vc.iloc[0] / filled:.1f}%)",
            }
        )
    return pd.DataFrame(rows).set_index("column")


def _top(v) -> str:
    return v.date().isoformat() if isinstance(v, pd.Timestamp) else str(v)


def _show(v, kind: str | None) -> str | None:
    """A min or max as text, so dates, years and amounts each read naturally in one column."""
    if v is None or pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.date().isoformat()
    if kind == "year":
        return str(int(v))
    return f"{v:,.6g}"


def _orderable(s: pd.Series) -> bool:
    numeric = pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)
    return numeric or pd.api.types.is_datetime64_any_dtype(s)


def describe(s: pd.Series) -> pd.Series:
    """The numbers behind a distribution: size, missing, zeros, centre, spread, tails, shape and outliers.

    Outliers use the box-plot rule: below Q1 - 1.5 IQR or above Q3 + 1.5 IQR (IQR = Q3 - Q1, the middle half).
    """
    x = pd.to_numeric(s, errors="coerce").dropna().astype(float)
    q1, q3 = x.quantile([0.25, 0.75])
    iqr = q3 - q1
    return pd.Series(
        {
            "count": len(x),
            "missing": int(s.isna().sum()),
            "% missing": 100 * s.isna().mean(),
            "% zero": 100 * (x == 0).mean() if len(x) else np.nan,
            "mean": x.mean(),
            "median": x.median(),
            "std": x.std(),
            "min": x.min(),
            "1%": x.quantile(0.01),
            "25%": q1,
            "75%": q3,
            "99%": x.quantile(0.99),
            "max": x.max(),
            "skew": x.skew(),
            "kurtosis": x.kurt(),
            "outliers (1.5 IQR)": int(((x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)).sum()),
        },
        name=s.name,
    )


def distribution(s: pd.Series, *, title: str | None = None, xlabel: str | None = None, log: bool = False, bins=40):
    """A histogram with its smoothed outline (KDE) beside a box plot, with the mean and median marked.

    `log=True` draws both on a log scale (zeros and negatives are dropped, and the title says how many).
    """
    x = pd.to_numeric(s, errors="coerce").dropna()
    dropped = 0
    if log:
        dropped = int((x <= 0).sum())
        x = x[x > 0]
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.5), gridspec_kw={"width_ratios": [3, 2]})
    sns.histplot(x, bins=bins, kde=len(x) > 1 and x.nunique() > 1, log_scale=log, color=MAIN, ax=a)
    for v, name, colour, style in ((x.mean(), "mean", ACCENT, "--"), (x.median(), "median", "black", "-")):
        a.axvline(v, color=colour, ls=style, lw=1.5, label=f"{name} {v:,.4g}")
    a.legend(frameon=False)
    sns.boxplot(x=x, log_scale=log, color=MAIN, ax=b, flierprops={"markersize": 2, "alpha": 0.4})
    thousands(a)
    for ax in (a, b):
        ax.set_xlabel(xlabel or s.name)
    a.set_ylabel("count")
    suffix = f" (log scale; {dropped:,} zero or negative values left out)" if log else ""
    fig.suptitle((title or f"Distribution of {xlabel or s.name}") + suffix, x=0, ha="left", fontweight="bold")
    return fig


def bin_check(s: pd.Series, bins=(10, 30, 100), *, xlabel: str | None = None, log: bool = False):
    """The same data drawn with three bin counts. A peak or gap that survives all three is in the data; one that
    appears in only one is an artefact of the binning."""
    x = pd.to_numeric(s, errors="coerce").dropna()
    if log:
        x = x[x > 0]
    fig, axes = plt.subplots(1, len(bins), figsize=(14, 3.8), sharey=False)
    for ax, n in zip(axes, bins, strict=True):
        sns.histplot(x, bins=n, log_scale=log, color=MAIN, ax=ax)
        ax.set_title(f"{n} bins", fontweight="normal")
        ax.set_xlabel(xlabel or s.name)
        thousands(ax)
    return fig


def counts(s: pd.Series, *, top: int = 15, title: str | None = None, xlabel: str | None = None):
    """Horizontal bars of the most common values, each labelled with its count and share; the rest are grouped as
    'all other values', and missing values get their own bar."""
    vc = s.astype("object").where(s.notna(), "(missing)").value_counts()
    if len(vc) > top:
        vc = pd.concat([vc.iloc[:top], pd.Series({f"all other values ({len(vc) - top:,})": vc.iloc[top:].sum()})])
    share = 100 * vc / vc.sum()
    fig, ax = plt.subplots(figsize=(11, 0.35 * len(vc) + 1.2))
    colours = [MUTED if str(k).startswith(("(missing)", "all other")) else MAIN for k in vc.index]
    ax.barh([str(k) for k in vc.index][::-1], vc.values[::-1], color=colours[::-1])
    for i, (n, p) in enumerate(zip(vc.values[::-1], share.values[::-1], strict=True)):
        ax.text(n, i, f"  {n:,} ({p:.1f}%)", va="center", fontsize=9)
    ax.set_xlabel("count")
    thousands(ax, "x")
    ax.margins(x=0.18)
    ax.set_title(title or f"Most common values of {xlabel or s.name}")
    return fig


def missing(df: pd.DataFrame, lens: str | None = None, *, title: str = "How complete is each column?"):
    """The share of rows filled in each column, lowest first."""
    filled = (100 * df.notna().mean()).sort_values()
    names = [label(lens, c, unit=False) if lens else c for c in filled.index]
    fig, ax = plt.subplots(figsize=(11, 0.28 * len(filled) + 1.2))
    ax.barh(names, filled.values, color=[ACCENT if v < 100 else MAIN for v in filled.values])
    for i, v in enumerate(filled.values):
        ax.text(v, i, f" {v:.1f}%", va="center", fontsize=8.5)
    ax.set_xlim(0, 112)
    ax.set_xlabel("% of rows filled")
    ax.set_title(title)
    return fig


def over_time(counts_by_year: pd.DataFrame, *, x: str, y: str, hue: str | None = None, title: str = "", ylabel=None):
    """Counts per year (already aggregated, usually in SQL), one line per group."""
    fig, ax = plt.subplots()
    sns.lineplot(data=counts_by_year, x=x, y=y, hue=hue, marker="o", markersize=3, ax=ax)
    thousands(ax)
    ax.set_title(title)
    ax.set_ylabel(ylabel or y)
    return fig
