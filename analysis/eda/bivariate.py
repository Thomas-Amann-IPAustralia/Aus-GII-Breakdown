"""Stage 2: two variables at a time.

With hundreds of thousands of rows almost any association is "statistically significant", so these helpers report
strength (r, rho, differences, rates with intervals) first and p-values second.
"""

from __future__ import annotations

import itertools
from functools import cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
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


# The screen: every pair of a lens's variables on one scale ---------------------------------------------------------
#
# Each pair gets one "strength" from 0 (no association) to 1 (each fully determines the other), whatever the kinds:
# - two numbers: |Spearman rho|, the correlation of their ranks;
# - a number and a category: the rank correlation ratio, the square root of Kruskal-Wallis's epsilon squared (the
#   share of the number's rank variation that the categories explain);
# - two categories: Cramér's V, with Bergsma's correction for the bias of many categories.
# For two yes/no variables, or a yes/no and a number, all three equal |Spearman rho|, so the scale is shared. 0.1 is
# conventionally a small association, 0.3 a moderate one and 0.5 a strong one.

SMALL, MODERATE, STRONG = 0.1, 0.3, 0.5


def size_word(strength: float) -> str:
    """'negligible', 'small', 'moderate' or 'strong', by the conventional thresholds 0.1, 0.3 and 0.5."""
    if not np.isfinite(strength):
        return ""
    return (
        "strong"
        if strength >= STRONG
        else "moderate"
        if strength >= MODERATE
        else "small"
        if strength >= SMALL
        else "negligible"
    )


def prepare(df: pd.DataFrame, kinds: dict[str, str], *, max_levels: int = 20, min_level: int = 30) -> pd.DataFrame:
    """The columns of `kinds` ({column: 'number' or 'category'}) ready to screen: numbers as floats, categories as
    integer codes (-1 for missing) of their `max_levels` most common values, with rarer values (or any held by fewer
    than `min_level` rows) pooled as 'other'. The categories' names are kept in `out.attrs['levels']`."""
    out, levels = {}, {}
    for c, k in kinds.items():
        s = df[c]
        if k == "number":
            if pd.api.types.is_bool_dtype(s):
                s = s.astype("Float64")
            out[c] = pd.to_numeric(s, errors="coerce").astype(float)
            continue
        s = s.astype("string")
        top = s.value_counts()
        keep = top[top >= min_level].index[:max_levels]
        s = s.where(s.isin(keep) | s.isna(), "other")
        cat = pd.Categorical(s)
        out[c] = pd.Series(cat.codes, index=df.index).astype(np.int32)
        levels[c] = list(cat.categories)
    res = pd.DataFrame(out, index=df.index)
    res.attrs["levels"] = levels
    res.attrs["kinds"] = dict(kinds)
    return res


def _ranks(v: np.ndarray) -> tuple[np.ndarray, float]:
    """Average ranks of `v`, and the tie correction factor (1 - sum(t^3 - t) / (n^3 - n))."""
    r = stats.rankdata(v)
    _, t = np.unique(v, return_counts=True)
    n = len(v)
    tie = 1 - (t.astype(float) ** 3 - t).sum() / (float(n) ** 3 - n) if n > 1 else 1.0
    return r, tie


def _codes(c: np.ndarray) -> tuple[np.ndarray, int]:
    u, inv = np.unique(c, return_inverse=True)
    return inv, len(u)


def association(x: np.ndarray, y: np.ndarray, kx: str, ky: str, *, min_n: int = 100) -> dict:
    """The strength of association between `x` and `y` (see the note above), on the rows where both are present
    (a category's code -1 is missing). Returns the measure's name, n, the strength, Spearman's rho where both are
    numbers (with its sign), and a p-value: from Spearman's t, Kruskal-Wallis's H or the chi-squared test."""
    x, y = np.asarray(x), np.asarray(y)
    ok = (x >= 0) if kx == "category" else ~np.isnan(x)
    ok &= (y >= 0) if ky == "category" else ~np.isnan(y)
    x, y = x[ok], y[ok]
    n = int(ok.sum())
    blank = {"measure": "", "n": n, "strength": np.nan, "rho": np.nan, "p": np.nan}
    if n < min_n:
        return blank
    if kx == "number" and ky == "number":
        rx, _ = _ranks(x)
        ry, _ = _ranks(y)
        if rx.std() == 0 or ry.std() == 0:
            return blank
        rho = float(np.corrcoef(rx, ry)[0, 1])
        t = rho * np.sqrt((n - 2) / max(1e-300, 1 - rho**2))
        return {
            "measure": "spearman",
            "n": n,
            "strength": abs(rho),
            "rho": rho,
            "p": float(2 * stats.t.sf(abs(t), n - 2)),
        }
    if kx == "category" and ky == "category":
        a, ka = _codes(x)
        b, kb = _codes(y)
        if ka < 2 or kb < 2:
            return blank
        obs = np.bincount(a * kb + b, minlength=ka * kb).reshape(ka, kb).astype(float)
        exp = obs.sum(1, keepdims=True) * obs.sum(0, keepdims=True) / n
        chi2 = float(((obs - exp) ** 2 / exp).sum())
        phi2 = max(0.0, chi2 / n - (ka - 1) * (kb - 1) / (n - 1))
        kr, kc = ka - (ka - 1) ** 2 / (n - 1), kb - (kb - 1) ** 2 / (n - 1)
        v = np.sqrt(phi2 / max(1e-12, min(kr - 1, kc - 1)))
        p = float(stats.chi2.sf(chi2, (ka - 1) * (kb - 1)))
        return {"measure": "cramer_v", "n": n, "strength": float(min(v, 1.0)), "rho": np.nan, "p": p}
    g, v = (x, y) if kx == "category" else (y, x)
    codes, k = _codes(g)
    if k < 2:
        return blank
    r, tie = _ranks(v)
    if tie == 0:
        return blank
    sizes = np.bincount(codes)
    means = np.bincount(codes, weights=r) / sizes
    h = 12 / (n * (n + 1)) * (sizes * (means - (n + 1) / 2) ** 2).sum() / tie
    eps2 = min(1.0, h / (n - 1))
    return {
        "measure": "rank_eta",
        "n": n,
        "strength": float(np.sqrt(eps2)),
        "rho": np.nan,
        "p": float(stats.chi2.sf(h, k - 1)),
    }


def fdr(p: pd.Series) -> pd.Series:
    """Benjamini-Hochberg q-values: the false discovery rate at which each test would be called a finding, given how
    many were run. A pair with q below 0.05 survives the correction for the number of pairs tested."""
    p = pd.Series(p, dtype=float)
    ok = p.notna()
    q = pd.Series(np.nan, index=p.index)
    if ok.any():
        v = p[ok].to_numpy()
        order = np.argsort(v)
        m = len(v)
        ranked = v[order] * m / np.arange(1, m + 1)
        ranked = np.minimum.accumulate(ranked[::-1])[::-1].clip(max=1)
        out = np.empty(m)
        out[order] = ranked
        q[ok] = out
    return q


def construction_pairs(groups: dict[str, list[str]]) -> set[frozenset]:
    """Every pair inside one of `groups` (variables that are the same measure, or made from each other)."""
    return {frozenset(p) for g in groups.values() for p in itertools.combinations(g, 2)}


def screen(prepared: pd.DataFrame, *, groups: dict[str, list[str]] | None = None, min_n: int = 100) -> pd.DataFrame:
    """Every pair of the prepared columns (`prepare`), strongest first: the measure, n, strength, rho, p, the q-value
    across the pairs not related by construction (`groups`), and whether the pair is related by construction."""
    kinds = prepared.attrs["kinds"]
    built = construction_pairs(groups or {})
    cols = [c for c in kinds if c in prepared]
    arrays = {c: prepared[c].to_numpy() for c in cols}
    rows = []
    for a, b in itertools.combinations(cols, 2):
        r = association(arrays[a], arrays[b], kinds[a], kinds[b], min_n=min_n)
        rows.append({"variable 1": a, "variable 2": b, **r, "by construction": frozenset((a, b)) in built})
    out = pd.DataFrame(rows)
    out["q"] = np.nan
    free = ~out["by construction"]
    out.loc[free, "q"] = fdr(out.loc[free, "p"])
    return out.sort_values("strength", ascending=False, na_position="last").reset_index(drop=True)


def replicate(
    discovery: pd.DataFrame, replication: pd.DataFrame, *, threshold: float = SMALL, q: float = 0.05
) -> pd.DataFrame:
    """The screen of the discovery sample beside the replication sample's, with each pair's verdict:
    - 'lead': at least `threshold` and q below `q` in discovery, and again in replication (its q recomputed over the
      pairs taken forward), with the same sign where both are numbers;
    - 'not replicated': passed in discovery but not in replication;
    - 'negligible': below `threshold` in discovery (however small its q);
    - 'not significant': q of `q` or more in discovery;
    - 'by construction': the same measure, or made from each other; 'too few rows': not measured."""
    key = ["variable 1", "variable 2"]
    keep = ["measure", "n", "strength", "rho", "p", "q"]
    a = discovery[key + keep + ["by construction"]]
    b = replication[key + keep].rename(columns={c: f"{c} (replication)" for c in keep})
    m = a.merge(b, on=key, how="left")
    forward = (~m["by construction"]) & (m.strength >= threshold) & (m.q < q)
    m["q (replication)"] = np.nan
    m.loc[forward, "q (replication)"] = fdr(m.loc[forward, "p (replication)"])
    same_sign = m.rho.isna() | (np.sign(m.rho) == np.sign(m["rho (replication)"]))
    held = (m["strength (replication)"] >= threshold) & (m["q (replication)"] < q) & same_sign
    m["verdict"] = np.select(
        [m.strength.isna(), m["by construction"], forward & held, forward, m.strength < threshold],
        ["too few rows", "by construction", "lead", "not replicated", "negligible"],
        "not significant",
    )
    m["size"] = m.strength.map(size_word)
    return m


def strength_interval(
    x: pd.Series, y: pd.Series, kx: str, ky: str, *, reps: int = 100, n_max: int | None = None, seed: int = 0
) -> tuple[float, float]:
    """A 95% bootstrap interval for a pair's strength (percentiles of `reps` resamples of the rows where both are
    present; of a random `n_max` of them, if given, which widens the interval and, for Cramér's V with rare
    categories, shifts it, since its bias correction depends on the number of rows)."""
    x, y = np.asarray(x), np.asarray(y)
    ok = (x >= 0) if kx == "category" else ~np.isnan(x)
    ok &= (y >= 0) if ky == "category" else ~np.isnan(y)
    x, y = x[ok], y[ok]
    rng = np.random.default_rng(seed)
    if n_max and len(x) > n_max:
        i = rng.choice(len(x), n_max, replace=False)
        x, y = x[i], y[i]
    vals = []
    for _ in range(reps):
        i = rng.integers(0, len(x), len(x))
        vals.append(association(x[i], y[i], kx, ky, min_n=10)["strength"])
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def describe_pair(prepared: pd.DataFrame, a: str, b: str, label=None) -> str:
    """In words, which way a pair goes: for two numbers, the sign of rho; for a number and a category, the categories
    with the highest and lowest median; for two categories, the combination most over-represented against chance."""
    label = label or (lambda c: c)
    kinds, levels = prepared.attrs["kinds"], prepared.attrs["levels"]
    d = prepared[[a, b]]
    d = d[(d[a] >= 0) if kinds[a] == "category" else d[a].notna()]
    d = d[(d[b] >= 0) if kinds[b] == "category" else d[b].notna()]
    if kinds[a] == "number" and kinds[b] == "number":
        rho = association(d[a].to_numpy(), d[b].to_numpy(), "number", "number")["rho"]
        return f"{'rise' if rho > 0 else 'fall'}s with" if np.isfinite(rho) else ""
    if kinds[a] == "category" and kinds[b] == "category":
        t = pd.crosstab(d[a], d[b])
        exp = np.outer(t.sum(1), t.sum(0)) / t.to_numpy().sum()
        ratio = (t / exp).where(t >= 30)
        i, j = np.unravel_index(np.nanargmax(ratio.to_numpy()), ratio.shape)
        return f"{levels[a][t.index[i]]} with {levels[b][t.columns[j]]} ({ratio.iat[i, j]:.1f}× chance)"
    g, v = (a, b) if kinds[a] == "category" else (b, a)
    stat = d.groupby(g)[v].agg(["median", "mean", "size"])
    stat = stat[stat["size"] >= 30]
    # the median, unless the groups' highest and lowest medians tie (common for counts that are mostly 0): then the mean
    which = "median" if stat["median"].max() > stat["median"].min() else "mean"
    s = stat[which].sort_values()
    name = levels[g]
    hi, lo = f"{name[s.index[-1]]} ({s.iloc[-1]:,.4g})", f"{name[s.index[0]]} ({s.iloc[0]:,.4g})"
    return f"{label(v)}: highest {which} for {hi}, lowest for {lo}"


def third_factors(result: pd.DataFrame, a: str, b: str, *, threshold: float = SMALL, top: int = 3) -> list[str]:
    """Candidate third factors for the pair (a, b): the other variables associated with both by at least
    `threshold` in the screen, strongest (by the weaker of the two links) first."""
    s = {}
    for _, r in result.dropna(subset=["strength"]).iterrows():
        s[(r["variable 1"], r["variable 2"])] = s[(r["variable 2"], r["variable 1"])] = r["strength"]
    others = {v for pair in s for v in pair} - {a, b}
    scored = {z: min(s.get((a, z), 0), s.get((b, z), 0)) for z in others}
    return [z for z, v in sorted(scored.items(), key=lambda kv: (-kv[1], kv[0])) if v >= threshold][:top]


def family_of(groups: dict[str, list[str]]) -> dict[str, str]:
    """Each grouped variable's family: the first group (in the order given) that holds it."""
    out = {}
    for g, members in groups.items():
        for c in members:
            out.setdefault(c, g)
    return out


def distinct_leads(m: pd.DataFrame, groups: dict[str, list[str]]) -> pd.DataFrame:
    """The leads with one row per pair of families: where several versions of the same measure (the members of a
    group, such as the origin of the filer and of the holder) make the same lead, only the strongest is kept, with the
    number of versions in `versions`."""
    fam = family_of(groups)
    d = m[m.verdict == "lead"].copy()
    d["families"] = [
        tuple(sorted((fam.get(a, a), fam.get(b, b)))) for a, b in zip(d["variable 1"], d["variable 2"], strict=True)
    ]
    d["versions"] = d.groupby("families")["families"].transform("size")
    return d.sort_values("strength", ascending=False).drop_duplicates("families").reset_index(drop=True)


def leads_table(m: pd.DataFrame, prepared: pd.DataFrame, discovery_result: pd.DataFrame, *, label=None, reps=100):
    """The leads of `replicate` (or `distinct_leads`), each with its strength in both samples, a 95% bootstrap
    interval, its direction in words and its candidate third factors. `label` maps a column to its plain-English
    name."""
    label = label or (lambda c: c)
    kinds = prepared.attrs["kinds"]
    rows = []
    for _, r in m[m.verdict == "lead"].iterrows():
        a, b = r["variable 1"], r["variable 2"]
        lo, hi = strength_interval(prepared[a], prepared[b], kinds[a], kinds[b], reps=reps)
        rows.append(
            {
                "pair": f"{label(a)} × {label(b)}",
                "measure": r.measure,
                "strength": r.strength,
                "95% interval": f"{lo:.3f} to {hi:.3f}",
                "replication": r["strength (replication)"],
                "size": r["size"],
                **({"versions": r["versions"]} if "versions" in r else {}),
                "direction": describe_pair(prepared, a, b, label),
                "candidate third factors": ", ".join(label(z) for z in third_factors(discovery_result, a, b)),
            }
        )
    return pd.DataFrame(rows)


def verdict_counts(m: pd.DataFrame) -> pd.Series:
    """How many pairs got each verdict."""
    order = ["lead", "not replicated", "negligible", "not significant", "by construction", "too few rows"]
    return m.verdict.value_counts().reindex(order, fill_value=0)


def strength_map(m: pd.DataFrame, columns: list[str], *, label=None, title: str = ""):
    """Every screened pair's strength as a lower-triangle heatmap: leads outlined in black, pairs related by
    construction hatched grey, pairs that did not replicate marked with a cross."""
    label = label or (lambda c: c)
    k = len(columns)
    pos = {c: i for i, c in enumerate(columns)}
    grid = np.full((k, k), np.nan)
    fig, ax = plt.subplots(figsize=(0.32 * k + 4, 0.32 * k + 3))
    marks = []
    for _, r in m.iterrows():
        a, b = r["variable 1"], r["variable 2"]
        if a not in pos or b not in pos:
            continue
        i, j = sorted((pos[a], pos[b]), reverse=True)
        grid[i, j] = r.strength
        marks.append((i, j, r.verdict))
    im = ax.imshow(grid, cmap="Blues", vmin=0, vmax=0.6)
    for i, j, v in marks:
        if v == "lead":
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="black", lw=1.4))
        elif v == "by construction":
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=True, fc="#DDDDDD", ec="none", hatch="///"))
        elif v == "not replicated":
            ax.plot(j, i, marker="x", color=ACCENT, ms=4)
    ax.set_xticks(range(k), [label(c) for c in columns], rotation=90, fontsize=7.5)
    ax.set_yticks(range(k), [label(c) for c in columns], fontsize=7.5)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.6)
    cb.set_label("strength (0 none, 0.1 small, 0.3 moderate, 0.5+ strong)")
    ax.set_title(title or "Every pair's strength: leads outlined, by construction hatched, not replicated ×")
    return fig


def replication_chart(m: pd.DataFrame, *, title: str = ""):
    """Each pair's strength in the discovery sample against the replication sample: pairs on the diagonal held."""
    colours = {"lead": MAIN, "not replicated": ACCENT, "negligible": "#BBBBBB", "not significant": "#BBBBBB"}
    fig, ax = plt.subplots(figsize=(6.5, 6))
    d = m[m.verdict.isin(colours)]
    for v, c in colours.items():
        s = d[d.verdict == v]
        if len(s):
            ax.scatter(s.strength, s["strength (replication)"], s=12, color=c, alpha=0.7, label=f"{v} ({len(s):,})")
    hi = float(np.nanmax([d.strength.max(), d["strength (replication)"].max(), 0.2])) * 1.05
    ax.plot([0, hi], [0, hi], color="black", lw=0.8)
    ax.axvline(SMALL, color=MAIN, ls=":", lw=1)
    ax.axhline(SMALL, color=MAIN, ls=":", lw=1)
    ax.set_xlim(0, hi)
    ax.set_ylim(0, hi)
    ax.set_xlabel("strength in the discovery sample")
    ax.set_ylabel("strength in the replication sample")
    ax.legend(frameon=False, fontsize=8.5)
    ax.set_title(title or "Does each pair hold in a second sample?")
    return fig


# Effect sizes for the planned pairs -------------------------------------------------------------------------------


def rate_difference(yes1, n1, yes2, n2, z: float = 1.96) -> tuple[float, float, float]:
    """The difference between two proportions (first minus second), with Newcombe's hybrid score 95% interval (from
    each proportion's Wilson interval; well behaved near 0 and 1)."""
    p1, p2 = yes1 / n1, yes2 / n2
    l1, u1 = wilson(np.array([yes1]), np.array([n1]), z)
    l2, u2 = wilson(np.array([yes2]), np.array([n2]), z)
    d = p1 - p2
    lo = d - np.sqrt((p1 - l1[0]) ** 2 + (u2[0] - p2) ** 2)
    hi = d + np.sqrt((u1[0] - p1) ** 2 + (p2 - l2[0]) ** 2)
    return float(d), float(lo), float(hi)


def median_difference(y1: pd.Series, y2: pd.Series, *, reps: int = 400, seed: int = 0) -> tuple[float, float, float]:
    """The difference between two groups' medians (first minus second), with a 95% bootstrap interval."""
    # sorted, so the same seed gives the same interval whatever order the rows arrived in
    a = np.sort(pd.to_numeric(y1, errors="coerce").dropna().to_numpy())
    b = np.sort(pd.to_numeric(y2, errors="coerce").dropna().to_numpy())
    rng = np.random.default_rng(seed)
    boots = [np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b))) for _ in range(reps)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(np.median(a) - np.median(b)), float(lo), float(hi)


def rate_ratio(k1, e1, k2, e2, z: float = 1.96) -> tuple[float, float, float]:
    """The ratio of two Poisson rates (k1/e1 over k2/e2), with a 95% interval on the log scale."""
    rr = (k1 / e1) / (k2 / e2)
    se = np.sqrt(1 / k1 + 1 / k2)
    return float(rr), float(rr * np.exp(-z * se)), float(rr * np.exp(z * se))


def split_half(keys: pd.Series, *, salt: str = "stage2") -> pd.Series:
    """A stable random half for each key (True for the discovery half, False for replication), from a hash of the key,
    so the same row always lands in the same half whichever columns are loaded."""
    h = pd.util.hash_pandas_object(keys.astype(str) + salt, index=False).to_numpy()
    return pd.Series((h % 2) == 0, index=keys.index)


# The screen's design, from screens.yaml ----------------------------------------------------------------------------

SCREENS = Path(__file__).with_name("screens.yaml")


@cache
def screens() -> dict:
    """The screen's design for each lens (`screens.yaml`)."""
    return yaml.safe_load(SCREENS.read_text())


def screen_kinds(lens: str) -> dict[str, str]:
    """{column: 'number' or 'category'} for every screened column of `lens`, derived ones last."""
    spec = screens()[lens]
    kinds = {c: k for c, k in spec["columns"].items() if isinstance(k, str)}
    kinds.update({c: d["kind"] for c, d in spec.get("derived", {}).items()})
    return kinds


def screen_label(lens: str, column: str) -> str:
    """A screened column's plain-English label: the register's, or the derived column's own."""
    derived = screens()[lens].get("derived", {})
    if column in derived:
        return derived[column]["label"]
    from .style import label

    return label(lens, column, unit=False)


def screen_sample(lens: str, part: str, stratum: str | None = None, *, keyed: bool = False) -> pd.DataFrame:
    """The rows of one sample ('discovery' or 'replication') of `lens` (one `stratum` of it, if it has strata), at
    most `sample` of them, chosen by a hash of the key so the same rows come back every time, prepared for `screen`
    (indexed by the key if `keyed`)."""
    from .data import sql

    spec = screens()[lens]
    kinds = screen_kinds(lens)
    derived = spec.get("derived", {})
    select = [f'"{c}"' for c in kinds if c not in derived] + [f'({d["sql"]}) AS "{c}"' for c, d in derived.items()]
    h = f"hash(CAST({spec['key']} AS VARCHAR) || 'stage2')"
    cond = spec[part]
    where = [f"{h} % 2 = {0 if part == 'discovery' else 1}" if cond == "half" else f"({cond})"]
    if stratum is not None:
        where.append(f"({spec['strata']['sql']}) = '{stratum}'")
    limit = f"LIMIT {spec['sample']}" if spec.get("sample") else ""
    select.append(f"{spec['key']} AS __key")
    q = f"SELECT {', '.join(select)} FROM {{lens/{lens}}} WHERE {' AND '.join(where)} ORDER BY {h} {limit}"
    df = sql(q, max_rows=None)
    df = df.set_index("__key").rename_axis(spec["key"]) if keyed else df.drop(columns="__key")
    return prepare(df, kinds)


def run_screen(lens: str, stratum: str | None = None) -> dict:
    """The whole screen of one lens (or stratum): both samples prepared and screened, and the verdicts."""
    groups = screens()[lens].get("groups", {})
    a = screen_sample(lens, "discovery", stratum)
    b = screen_sample(lens, "replication", stratum)
    ra, rb = screen(a, groups=groups), screen(b, groups=groups)
    return {"prepared": a, "discovery": ra, "replication": rb, "verdicts": replicate(ra, rb), "n": (len(a), len(b))}


def dot_chart(
    t: pd.DataFrame,
    *,
    value: str,
    low: str,
    high: str,
    hue: str | None = None,
    title: str = "",
    xlabel: str = "",
    percent: bool = True,
    fmt: str = "{:.1f}",
):
    """Dots with 95% intervals, one row per index value of `t` (and one colour per `hue` value, side by side), with
    each dot's value written beside it."""
    from .style import PALETTE

    k = 100 if percent else 1
    rows = list(dict.fromkeys(t.index))
    hues = list(dict.fromkeys(t[hue])) if hue else [None]
    fig, ax = plt.subplots(figsize=(11, 0.42 * len(rows) * max(1, len(hues) * 0.7) + 1.3))
    step = 0.7 / max(1, len(hues))
    for h_i, h in enumerate(hues):
        d = t[t[hue] == h] if hue else t
        y = np.array([len(rows) - 1 - rows.index(i) for i in d.index]) + (h_i - (len(hues) - 1) / 2) * step
        v, lo, hi = (d[c].to_numpy(float) * k for c in (value, low, high))
        colour = PALETTE[h_i % len(PALETTE)]
        ax.errorbar(v, y, xerr=[v - lo, hi - v], fmt="o", color=colour, ms=5, capsize=2, label=str(h) if hue else None)
        for vi, yi in zip(v, y, strict=True):
            ax.text(vi, yi + step * 0.25, "  " + fmt.format(vi), fontsize=7.5, va="bottom", color=colour)
    ax.set_yticks(range(len(rows)), [str(r) for r in rows][::-1])
    ax.set_xlabel(xlabel + (" (%)" if percent and xlabel else ""))
    ax.set_title(title)
    if hue:
        ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1, 1))
    return fig


def survival_with_interval(curves: pd.DataFrame, year: float, *, by: str, time: str = "t", min_at_risk: int = 30):
    """Each group's share still in force at `year` with its 95% interval (from `univariate.kaplan_meier`'s curves:
    the last time not after `year`), and the number still at risk then. Groups whose curve stops short of `year`, or
    with fewer than `min_at_risk` left, are left out."""
    rows = {}
    for g, d in curves.groupby(by, sort=False):
        d = d.sort_values(time)
        if d[time].max() < year:
            continue
        seen = d[d[time] <= year]
        if not len(seen) or seen.at_risk.iloc[-1] < min_at_risk:
            continue
        r = seen.iloc[-1]
        rows[g] = {"in force": r.survival, "low": r.lower, "high": r.upper, "at risk": r.at_risk}
    return pd.DataFrame(rows).T.rename_axis(by)


def ratio_by(df: pd.DataFrame, by: str | list[str], num: str, den: str, *, reps: int = 200, seed: int = 0):
    """For each group of `df`, the ratio of sums `num` / `den` (for example, expected women over inventors with an
    estimate), with a 95% bootstrap interval that resamples rows (patents) whole, so inventors of one patent stay
    together. Returns the ratio, its interval, the rows and the denominator's total."""
    rng = np.random.default_rng(seed)
    out = {}
    for g, d in df.groupby(by, observed=True, sort=True):
        d = d.sort_values([num, den], kind="mergesort")  # the same interval whatever order the rows arrived in
        x, y = np.nan_to_num(d[num].to_numpy(float)), np.nan_to_num(d[den].to_numpy(float))
        if y.sum() <= 0:
            continue
        i = rng.integers(0, len(d), (reps, len(d)))
        boots = x[i].sum(1) / np.where(y[i].sum(1) > 0, y[i].sum(1), np.nan)
        lo, hi = np.nanpercentile(boots, [2.5, 97.5])
        out[g] = {"ratio": x.sum() / y.sum(), "low": lo, "high": hi, "rows": len(d), "total": y.sum()}
    res = pd.DataFrame(out).T
    if isinstance(by, list) and len(by) > 1:
        res.index = pd.MultiIndex.from_tuples(res.index, names=by)
    else:
        res.index.name = by if isinstance(by, str) else by[0]
    return res
