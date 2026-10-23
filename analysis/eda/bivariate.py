"""Stage 2: two variables at a time.

With hundreds of thousands of rows almost any association is "statistically significant", so these helpers report
strength (r, rho, differences, rates with intervals) first and p-values second.
"""

from __future__ import annotations

import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.nonparametric.smoothers_lowess import lowess

from .style import ACCENT, MAIN, thousands


def pair_stats(x: pd.Series, y: pd.Series) -> pd.Series:
    """Pearson r (straight-line association) and Spearman rho (rises or falls together, in any shape), on the rows
    where both are present."""
    d = pd.concat([pd.to_numeric(x, errors="coerce"), pd.to_numeric(y, errors="coerce")], axis=1).dropna()
    if len(d) < 3:
        return pd.Series({"n": len(d)})
    r, pr = stats.pearsonr(d.iloc[:, 0], d.iloc[:, 1])
    rho, prho = stats.spearmanr(d.iloc[:, 0], d.iloc[:, 1])
    return pd.Series({"n": len(d), "pearson r": r, "p (r)": pr, "spearman rho": rho, "p (rho)": prho})


def screen_pairs(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Every pair of `columns`, strongest association first (by the larger of |r| and |rho|)."""
    rows = []
    for a, b in itertools.combinations(columns, 2):
        s = pair_stats(df[a], df[b])
        rows.append({"variable 1": a, "variable 2": b, **s.to_dict()})
    out = pd.DataFrame(rows)
    if "pearson r" in out:
        out["strength"] = out[["pearson r", "spearman rho"]].abs().max(axis=1)
        out["rho - r"] = out["spearman rho"].abs() - out["pearson r"].abs()
        out = out.sort_values("strength", ascending=False)
    return out.reset_index(drop=True)


def scatter_trend(ax: plt.Axes, x: pd.Series, y: pd.Series, *, sample: int = 20_000, logx=False, logy=False, seed=0):
    """Points (a random sample of `sample` if there are more) with a LOWESS curve, which follows the data without
    assuming a straight line. Large samples are drawn as a density of hexagons instead of points."""
    d = pd.concat([pd.to_numeric(x, errors="coerce"), pd.to_numeric(y, errors="coerce")], axis=1).dropna()
    d.columns = ["x", "y"]
    if logx:
        d = d[d.x > 0]
    if logy:
        d = d[d.y > 0]
    n = len(d)
    if n > sample:
        d = d.sample(sample, random_state=seed)
    xs, ys = (np.log10(d.x) if logx else d.x), (np.log10(d.y) if logy else d.y)
    if n > 5_000:
        ax.hexbin(xs, ys, gridsize=45, cmap="Blues", mincnt=1, bins="log")
    else:
        ax.scatter(xs, ys, s=8, alpha=0.4, color=MAIN, edgecolor="none")
    if len(d) > 10:
        fit = lowess(ys, xs, frac=0.3, return_sorted=True)
        ax.plot(fit[:, 0], fit[:, 1], color=ACCENT, lw=2.5, label="LOWESS trend")
        ax.legend(frameon=False)
    ax.set_xlabel(f"{x.name}{' (log10)' if logx else ''}")
    ax.set_ylabel(f"{y.name}{' (log10)' if logy else ''}")
    note = f"n = {n:,}" + (f" (a random {sample:,} drawn)" if n > sample else "")
    ax.text(0.99, 0.01, note, transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color="grey")
    return ax


def binned_summary(groups: pd.Series, y: pd.Series) -> pd.DataFrame:
    """For each group: how many, and the centre and spread of `y`."""
    d = pd.DataFrame({"group": groups, "y": pd.to_numeric(y, errors="coerce")}).dropna()
    g = d.groupby("group", observed=True)["y"]
    return pd.DataFrame(
        {
            "n": g.size(),
            "mean": g.mean(),
            "median": g.median(),
            "25%": g.quantile(0.25),
            "75%": g.quantile(0.75),
        }
    )


def equal_bins(x: pd.Series, q: int = 5) -> pd.Series:
    """Cut `x` into `q` groups of about equal size (fifths by default), labelled by their range."""
    return pd.qcut(x, q=q, duplicates="drop")


def compare_groups(y: pd.Series, groups: pd.Series) -> pd.Series:
    """Do the groups differ in `y`? Kruskal-Wallis (Mann-Whitney for two groups), which uses ranks so a few extreme
    values cannot drive it, with an effect size: rank-biserial correlation for two groups (-1 to 1; positive when the
    first group, in sorted order, tends to have the higher values), epsilon squared
    for more (0 to 1, the share of rank variation explained by the groups)."""
    d = pd.DataFrame({"y": pd.to_numeric(y, errors="coerce"), "g": groups}).dropna()
    samples = [v.to_numpy() for _, v in d.groupby("g", observed=True)["y"]]
    if len(samples) == 2:
        u, p = stats.mannwhitneyu(*samples, alternative="two-sided")
        effect = 2 * u / (len(samples[0]) * len(samples[1])) - 1
        return pd.Series({"test": "Mann-Whitney", "n": len(d), "p": p, "rank-biserial": effect})
    h, p = stats.kruskal(*samples)
    return pd.Series({"test": "Kruskal-Wallis", "n": len(d), "p": p, "epsilon squared": h / (len(d) - 1)})


def wilson(successes: np.ndarray, n: np.ndarray, z: float = 1.96) -> tuple[np.ndarray, np.ndarray]:
    """The Wilson 95% interval for a proportion (well behaved for rates near 0 or 1 and for small groups)."""
    successes, n = np.asarray(successes, float), np.asarray(n, float)
    p = np.divide(successes, n, out=np.zeros_like(n), where=n > 0)
    centre = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return centre - half, centre + half


def rate_by(flag: pd.Series, groups: pd.Series) -> pd.DataFrame:
    """The share of each group for which `flag` is true, with a 95% interval (for example, the share of firms in each
    remoteness area that hold a patent)."""
    d = pd.DataFrame({"flag": flag.astype(float), "g": groups}).dropna()
    t = d.groupby("g", observed=True)["flag"].agg(n="size", yes="sum")
    t["rate"] = t["yes"] / t["n"]
    t["low"], t["high"] = wilson(t["yes"], t["n"])
    return t


def rate_chart(t: pd.DataFrame, *, title: str, xlabel: str = "share", percent: bool = True):
    """Bars of `rate_by`'s rates with their 95% intervals."""
    k = 100 if percent else 1
    fig, ax = plt.subplots(figsize=(11, 0.4 * len(t) + 1.2))
    names = [str(i) for i in t.index][::-1]
    rate, low, high = (t[c].to_numpy()[::-1] * k for c in ("rate", "low", "high"))
    ax.barh(names, rate, color=MAIN, xerr=[rate - low, high - rate], ecolor="black", capsize=3)
    for i, (r, n) in enumerate(zip(rate, t["n"].to_numpy()[::-1], strict=True)):
        ax.text(r, i, f"  {r:.1f}{'%' if percent else ''} (n = {n:,.0f})", va="center", fontsize=8.5)
    ax.margins(x=0.2)
    ax.set_xlabel(f"{xlabel} (%)" if percent else xlabel)
    ax.set_title(title)
    thousands(ax, "x")
    return fig
