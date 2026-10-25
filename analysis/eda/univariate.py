"""Stage 1: one variable at a time.

Each function returns a small table or a figure, never the raw rows, so a notebook stays readable and small.
"""

from __future__ import annotations

import matplotlib.dates as mdates
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


def monthly(
    timeline: pd.DataFrame,
    columns: list[str],
    *,
    start=None,
    title: str = "",
    average: int = 12,
    events: bool | list[str] = True,
):
    """Monthly counts from the timeline lens: a thin line per month and a thick line for the `average`-month moving
    average (which smooths out seasons and month length), with policy changes marked."""
    from .style import PALETTE, label, mark_events

    t = timeline if start is None else timeline[timeline["month"] >= pd.Timestamp(start)]
    fig, ax = plt.subplots(figsize=(13, 5))
    for colour, c in zip(PALETTE, columns, strict=False):
        y = t[c].astype(float)
        ax.plot(t["month"], y, color=colour, lw=0.6, alpha=0.45)
        ax.plot(
            t["month"],
            y.rolling(average, min_periods=average).mean(),
            color=colour,
            lw=2.2,
            label=label("timeline", c, unit=False),
        )
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0, -0.08), ncol=2)
    ax.set_ylabel(f"per month (thick line: {average}-month average)")
    thousands(ax)
    ax.set_title(title)
    if events:
        mark_events(ax, timeline, ids=None if events is True else events)
    return fig


def seasonal_profile(timeline: pd.DataFrame, columns: list[str], *, start=None, end=None) -> pd.DataFrame:
    """Each series' typical month of the year: every month's count as a % of the centred 12-month average around it
    (the average of two 12-month windows, so it centres on the month), then the median of each calendar month over
    `start` to `end`. 100 is an ordinary month; 75 is a quarter below. One row per series, one column per month."""
    t = timeline.set_index("month")
    out = {}
    for c in columns:
        y = t[c].astype(float)
        centred = y.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
        ratio = (100 * y / centred).loc[start:end].dropna()
        out[c] = ratio.groupby(ratio.index.month).median()
    return pd.DataFrame(out).T.rename_axis(columns="month of the year")


def _event_months(timeline: pd.DataFrame) -> dict[str, pd.Timestamp]:
    marked = timeline.loc[timeline["policy_events"].notna(), ["month", "policy_events"]]
    return {e: m for m, names in marked.itertuples(index=False) for e in names.split(", ")}


def event_windows(timeline: pd.DataFrame, targets: dict[str, list[str]], *, months: int = 12) -> pd.DataFrame:
    """For each policy change and each series it targets: the average month in the `months` before the change's
    month, the month before, the change's month, the average in the `months` after, and the changes between them.
    Descriptive only: trends and seasons move these too, which Stage 2 allows for."""
    when = _event_months(timeline)
    t = timeline.set_index("month")
    rows = []
    for event, columns in targets.items():
        i = t.index.get_loc(when[event])
        for c in columns:
            y = t[c].astype(float)
            before, after = y.iloc[max(i - months, 0) : i].mean(), y.iloc[i + 1 : i + 1 + months].mean()
            rows.append(
                {
                    "change": event,
                    "month": f"{when[event]:%Y-%m}",
                    "series": c,
                    f"average, {months} months before": before,
                    "month before": y.iloc[i - 1],
                    "month of the change": y.iloc[i],
                    f"average, {months} months after": after,
                    "month of the change, × average before": y.iloc[i] / before if before else np.nan,
                    "% change in the average": 100 * (after / before - 1) if before else np.nan,
                }
            )
    return pd.DataFrame(rows).set_index(["change", "series"])


def around_events(timeline: pd.DataFrame, targets: dict[str, list[str]], *, months: int = 24, ncols: int = 3):
    """Small multiples: for each policy change, the series it targets in the `months` either side, with the change's
    month marked. Each panel has its own scale."""
    from .style import PALETTE, label

    when = _event_months(timeline)
    t = timeline.set_index("month")
    nrows = -(-len(targets) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 2.6 * nrows), squeeze=False)
    for ax, (event, columns) in zip(axes.flat, targets.items(), strict=False):
        m = when[event]
        w = t.loc[m - pd.DateOffset(months=months) : m + pd.DateOffset(months=months)]
        for colour, c in zip(PALETTE, columns, strict=False):
            ax.plot(w.index, w[c].astype(float), color=colour, lw=1.4, label=label("timeline", c, unit=False))
        ax.axvline(m, color=MUTED, ls="--", lw=1)
        ax.set_title(f"{event} ({m:%b %Y})", fontsize=9.5)
        ax.legend(frameon=False, fontsize=6.5, loc="upper left")
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(labelsize=7.5)
        thousands(ax)
    for ax in axes.flat[len(targets) :]:
        ax.set_visible(False)
    return fig


def kaplan_meier(
    counts: pd.DataFrame,
    *,
    time: str = "t",
    ended: str = "ended",
    unfinished: str = "unfinished",
    by: str | None = None,
) -> pd.DataFrame:
    """Survival curves from grouped counts: one row per (group and) time, with the number that `ended` then and the
    number still going (`unfinished`, censored) last seen then. Returns, for each time, the share still going after
    it (Kaplan-Meier: the product over times of 1 minus the share at risk that ended), the number at risk, and a 95%
    interval (Greenwood's variance, on the log-log scale, so it stays between 0 and 1). Aggregate in SQL first: a
    curve needs only counts, never the rows."""
    groups = counts.groupby(by) if by else [(None, counts)]
    out = []
    for g, d in groups:
        d = d.groupby(time)[[ended, unfinished]].sum().sort_index()
        at_risk = d[ended].add(d[unfinished]).iloc[::-1].cumsum().iloc[::-1]
        q = (d[ended] / at_risk).clip(upper=1)
        s = (1 - q).cumprod()
        var = (d[ended] / (at_risk * (at_risk - d[ended])).where(at_risk > d[ended])).cumsum()
        with np.errstate(divide="ignore", invalid="ignore"):
            se = np.sqrt(var) / np.log(s).abs()
            lo, hi = s ** np.exp(1.96 * se), s ** np.exp(-1.96 * se)
        r = pd.DataFrame({"at_risk": at_risk, "survival": s, "lower": lo, "upper": hi}).reset_index()
        if by:
            r.insert(0, by, g)
        out.append(r)
    return pd.concat(out, ignore_index=True)


def survival_at(curves: pd.DataFrame, years, *, by: str, time: str = "t", min_at_risk: int = 30) -> pd.DataFrame:
    """The share still going at each of `years` (the curve's value at the last time not after it), by group. Empty
    where the curve has not reached that time, or fewer than `min_at_risk` are left at risk by then."""
    rows = {}
    for g, d in curves.groupby(by, sort=False):
        d = d.set_index(time).sort_index()
        rows[g] = {}
        for y in years:
            seen = d[d.index <= y]
            if y > d.index.max() or (len(seen) and seen.at_risk.iloc[-1] < min_at_risk):
                rows[g][y] = np.nan
            else:
                rows[g][y] = seen.survival.iloc[-1] if len(seen) else 1.0
    return pd.DataFrame(rows).T.rename_axis(index=by, columns="years")
