"""Stage 3: several variables at once.

These describe structure (which variables move together, which groups of places or firms look alike, whether an
association survives holding others fixed). None of them shows cause and effect. The method is ADR 0046.
"""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

from .style import label


def corr_heatmap(
    df: pd.DataFrame,
    columns: list[str],
    *,
    lens: str | None = None,
    method: str = "spearman",
    title="",
    names: dict[str, str] | None = None,
):
    """The correlation of every pair of `columns`, as a lower-triangle heatmap with the values written in.

    The legend (the final review's request, ADR 0046) says what the colours and numbers mean, the measure, and how
    many rows each pair uses: pairs are taken on the rows where both are present, so the count is given as a range.
    """
    d = df[columns].apply(pd.to_numeric, errors="coerce")
    c = d.corr(method=method)
    present = d.notna().astype(int)
    pair_n = present.T @ present
    lo, hi = int(pair_n.to_numpy()[np.tril_indices(len(columns), -1)].min()), int(pair_n.to_numpy().max())
    names = names or {}
    shown = [names.get(x, label(lens, x, unit=False) if lens else x) for x in columns]
    c.index, c.columns = shown, shown
    mask = np.triu(np.ones_like(c, dtype=bool), k=1)
    size = 0.55 * len(columns) + 3
    fig, ax = plt.subplots(figsize=(size + 2, size))
    sns.heatmap(
        c,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        ax=ax,
        cbar_kws={"shrink": 0.6, "label": f"{method.capitalize()} correlation (-1 to 1)"},
        annot_kws={"size": 8},
    )
    ax.set_title(title or f"How the variables move together ({method})")
    rows = f"{lo:,}" if lo == hi else f"{lo:,} to {hi:,}"
    fig.text(
        0.01,
        -0.02,
        f"How to read: each square is the {method.capitalize()} correlation of two variables, written in. Red: they"
        f" rise together; blue: one rises as the other falls; white: no association. 1 or -1 is a perfect"
        f" {'rank ' if method == 'spearman' else ''}relationship. Each pair uses the rows where both are present"
        f" ({rows} rows).",
        fontsize=8,
        wrap=True,
        ha="left",
        va="top",
    )
    return fig


def _standardised(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    d = df[columns].apply(pd.to_numeric, errors="coerce").dropna()
    return pd.DataFrame(StandardScaler().fit_transform(d), index=d.index, columns=columns)


def pca(df: pd.DataFrame, columns: list[str], n: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Principal components of the standardised `columns` (rows with any missing value are left out).

    Returns the share of variation each component explains, and the loadings (how much each variable contributes to
    each component).
    """
    z = _standardised(df, columns)
    p = PCA(n_components=n).fit(z)
    names = [f"PC{i + 1}" for i in range(p.n_components_)]
    explained = pd.DataFrame(
        {"% explained": 100 * p.explained_variance_ratio_, "cumulative %": 100 * p.explained_variance_ratio_.cumsum()},
        index=names,
    )
    loadings = pd.DataFrame(p.components_.T, index=columns, columns=names)
    explained.attrs["rows used"] = len(z)
    return explained, loadings


def scree(explained: pd.DataFrame, title: str = "How much each component explains"):
    """Bars of each component's share of the variation, with the running total."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(explained.index, explained["% explained"])
    ax.plot(explained.index, explained["cumulative %"], marker="o", color="black", label="cumulative")
    ax.set_ylabel("% of variation")
    ax.set_ylim(0, 105)
    ax.legend(frameon=False)
    ax.set_title(title)
    return fig


def vif(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """Variance inflation factors: how far each variable is predictable from the others (above about 5 to 10, two or
    more variables are carrying much the same information)."""
    z = sm.add_constant(_standardised(df, columns))
    return pd.Series(
        [variance_inflation_factor(z.values, i) for i in range(1, z.shape[1])], index=columns, name="VIF"
    ).sort_values(ascending=False)


def partial_corr(df: pd.DataFrame, x: str, y: str, controls: list[str], method: str = "spearman") -> pd.Series:
    """The correlation of `x` and `y` before and after holding `controls` fixed (both are regressed on the controls
    and the leftovers correlated; with `method='spearman'` this is done on ranks)."""
    d = df[[x, y, *controls]].apply(pd.to_numeric, errors="coerce").dropna()
    if method == "spearman":
        d = d.rank()
    c = sm.add_constant(d[controls])
    rx = sm.OLS(d[x], c).fit().resid
    ry = sm.OLS(d[y], c).fit().resid
    return pd.Series({"n": len(d), "raw": d[x].corr(d[y]), "partial": rx.corr(ry), "controls": ", ".join(controls)})


def clusters(df: pd.DataFrame, columns: list[str], ks=range(2, 9), seed: int = 0) -> pd.DataFrame:
    """k-means on the standardised `columns` for each k, scored by silhouette (-1 to 1; higher means the groups are
    better separated). Choose k from this table, then call `assign`."""
    z = _standardised(df, columns)
    sample = z.sample(min(len(z), 20_000), random_state=seed)
    rows = []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(z)
        rows.append({"k": k, "silhouette": silhouette_score(sample, km.predict(sample)), "inertia": km.inertia_})
    return pd.DataFrame(rows).set_index("k")


def assign(df: pd.DataFrame, columns: list[str], k: int, seed: int = 0) -> tuple[pd.Series, pd.DataFrame]:
    """Cluster labels for each row used, and each cluster's size and average (standardised) profile."""
    z = _standardised(df, columns)
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(z)
    labels = pd.Series(km.labels_, index=z.index, name="cluster")
    profile = z.groupby(labels).mean()
    profile.insert(0, "n", labels.value_counts().sort_index())
    return labels, profile


# --- Signals with their third factors held together (ADR 0046) ---------------------------------------------------


def _logistic(p):
    return 1 / (1 + np.exp(-p))


def adjusted_effect(
    df: pd.DataFrame,
    outcome: str,
    signal: str,
    controls: list[str] | None = None,
    *,
    cluster: str | None = None,
    numeric: list[str] | None = None,
    weights: str | None = None,
    min_level: int = 30,
) -> pd.Series:
    """How far a yes-or-no `outcome` differs with a yes-or-no `signal`, before and after holding `controls` fixed.

    A logistic regression of the outcome on the signal and the controls (categories unless named in `numeric`),
    reported as the **average marginal effect** of the signal: the average, over the rows, of the difference in the
    predicted chance of the outcome with the signal on and off, the controls kept as each row has them. The raw
    figure is the same model with no controls (the plain difference in shares). Intervals are 95%, by the delta
    method, from standard errors clustered by `cluster` when given (rows of one filer are not independent).
    Rows missing any variable are left out (so code a missing category as "unknown" first); a control with one value
    only is dropped; with fewer than `min_level` rows on either side of the signal, nothing is estimated ("too few
    rows"); a level with fewer than `min_level` rows, or whose outcome never varies, is merged into the
    control's most common level (`rows merged` counts them). With `weights`, the outcome may be a share (for
    example, women among a cell's inventors) and each row counts by its weight (the cell's inventors), in a
    quasi-binomial model whose spread is estimated.
    """
    controls, numeric = list(controls or []), set(numeric or [])
    cols = [outcome, signal, *controls] + ([cluster] if cluster else []) + ([weights] if weights else [])
    d = df[cols].dropna().copy()
    if weights:
        d = d[d[weights] > 0]
    d[outcome] = d[outcome].astype(float)
    d[signal] = d[signal].astype(float)
    w = d[weights].to_numpy(float) if weights else np.ones(len(d))
    # a level with few rows, or whose outcome never varies, would make the model's estimates run off to infinity
    # (separation): such levels are merged into the control's most common level, and the rows merged are counted
    merged = 0
    for c in controls:
        if c in numeric:
            continue
        g = d.assign(_w=w).groupby(c, observed=True)
        size = g["_w"].sum()
        uniform = g[outcome].agg(lambda v: v.max() <= 0 or v.min() >= 1)
        bad = size.index[(size < min_level) | uniform]
        if len(bad):
            top = size.drop(bad).idxmax() if len(bad) < len(size) else size.idxmax()
            hit = d[c].isin(bad)
            merged += int(hit.sum())
            d[c] = d[c].astype(object).where(~hit, top)
    keep = [c for c in controls if d[c].nunique() > 1]
    on, off = (d[signal] == 1).to_numpy(), (d[signal] == 0).to_numpy()
    if min(w[on].sum(), w[off].sum()) < min_level:  # too few on one side to say anything
        cols = ["share with signal", "share without", "raw", "raw low", "raw high", "adjusted", "adjusted low"]
        cols += ["adjusted high", "share of raw remaining", "rows merged"]
        return pd.Series({"rows": len(d), **dict.fromkeys(cols, np.nan), "controls": "", "verdict": "too few rows"})
    out = {
        "rows": len(d),
        "share with signal": np.average(d[outcome][on], weights=w[on]),
        "share without": np.average(d[outcome][off], weights=w[off]),
    }
    for name, terms in (("raw", []), ("adjusted", keep)):
        rhs = " + ".join([signal] + [c if c in numeric else f"C({c})" for c in terms])
        fit_kw = {"cov_type": "cluster", "cov_kwds": {"groups": pd.factorize(d[cluster])[0]}} if cluster else {}
        glm_kw = {"var_weights": w} if weights else {}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = smf.glm(f"{outcome} ~ {rhs}", d, family=sm.families.Binomial(), **glm_kw)
            fit = model.fit(scale="X2" if weights else None, **fit_kw)
        x = fit.model.exog
        j = fit.model.exog_names.index(signal)
        x1, x0 = x.copy(), x.copy()
        x1[:, j], x0[:, j] = 1.0, 0.0
        b = fit.params.to_numpy()
        p1, p0 = _logistic(x1 @ b), _logistic(x0 @ b)
        ame = float(np.average(p1 - p0, weights=w))
        grad = np.average((p1 * (1 - p1))[:, None] * x1 - (p0 * (1 - p0))[:, None] * x0, axis=0, weights=w)
        se = float(np.sqrt(grad @ fit.cov_params().to_numpy() @ grad))
        out[name], out[f"{name} low"], out[f"{name} high"] = ame, ame - 1.96 * se, ame + 1.96 * se
    out["controls"] = ", ".join(keep)
    out["rows merged"] = merged
    out["share of raw remaining"] = out["adjusted"] / out["raw"] if out["raw"] else np.nan
    out["verdict"] = verdict(
        out["raw"], out["adjusted"], out["adjusted low"], out["adjusted high"], out["raw low"], out["raw high"]
    )
    return pd.Series(out)


def _merge_rare(d: pd.DataFrame, controls: list[str], min_level: int, event: str | None = None) -> int:
    """Merge each control's levels with fewer than `min_level` rows (or, given `event`, with no events: a level in
    which no right ends sends its coefficient to infinity) into its most common level; return the rows merged."""
    merged = 0
    for c in controls:
        size = d[c].value_counts()
        bad = size.index[size < min_level]
        if event is not None:
            ends = d.groupby(c, observed=True)[event].sum().reindex(size.index)
            bad = size.index[(size < min_level) | (ends == 0)]
        if len(bad) and len(bad) < len(size):
            hit = d[c].isin(bad)
            merged += int(hit.sum())
            d[c] = d[c].astype(object).where(~hit, size.drop(bad).idxmax())
    return merged


def cox_cluster_cov(time, event, entry, x, beta, naive_cov, groups) -> np.ndarray:
    """The clustered (Lin and Wei) covariance of a Cox model's coefficients, with delayed entry and Breslow's ties:
    the model's inverse information on either side of the sum, over clusters, of the outer product of each cluster's
    summed score residuals. (statsmodels' own version gives NaN when censored rows tie with the last event time.)"""
    t, d, e = (np.asarray(v, float) for v in (time, event, entry))
    x = np.asarray(x, float)
    w = np.exp(x @ beta)
    u = np.unique(t[d == 1])  # event times
    if len(u) == 0:
        return np.full_like(naive_cov, np.nan)

    def at_risk_sums(v):  # sum over rows with e < s <= t, for each event time s
        ot, oe = np.argsort(t), np.argsort(e)
        suffix_t = np.concatenate([np.cumsum(v[ot][::-1], axis=0)[::-1], np.zeros((1, *v.shape[1:]))])
        suffix_e = np.concatenate([np.cumsum(v[oe][::-1], axis=0)[::-1], np.zeros((1, *v.shape[1:]))])
        return suffix_t[np.searchsorted(t[ot], u, "left")] - suffix_e[np.searchsorted(e[oe], u, "left")]

    s0 = at_risk_sums(w)
    s1 = at_risk_sums(w[:, None] * x)
    dn = np.bincount(np.searchsorted(u, t[d == 1]), minlength=len(u)).astype(float)
    dlam = dn / s0
    xbar = s1 / s0[:, None]
    cum_lam = np.concatenate([[0.0], np.cumsum(dlam)])
    cum_c = np.concatenate([np.zeros((1, x.shape[1])), np.cumsum(xbar * dlam[:, None], axis=0)])
    kt, ke = np.searchsorted(u, t, "right"), np.searchsorted(u, e, "right")
    d_lam = cum_lam[kt] - cum_lam[ke]
    d_c = cum_c[kt] - cum_c[ke]
    resid = -w[:, None] * (x * d_lam[:, None] - d_c)
    ev = d == 1
    resid[ev] += x[ev] - xbar[np.searchsorted(u, t[ev], "left")]
    g = pd.factorize(np.asarray(groups))[0]
    summed = np.zeros((g.max() + 1, x.shape[1]))
    np.add.at(summed, g, resid)
    return naive_cov @ (summed.T @ summed) @ naive_cov


def adjusted_hazard(
    df: pd.DataFrame,
    time: str,
    event: str,
    entry: str,
    signal: str,
    controls: list[str] | None = None,
    *,
    cluster: str | None = None,
    horizon: float | None = None,
    min_level: int = 30,
) -> pd.Series:
    """How far the chance of a right ending differs with a yes-or-no `signal`, before and after holding `controls`
    fixed: a proportional hazards (Cox) model with delayed entry, so each right is counted from `entry` (its grant),
    as Stage 2's survival curves count it (ADR 0041). Reported as **hazard ratios**: 0.8 means a right with the signal
    is 20% less likely to end in any given year, the controls held. With `horizon`, follow-up stops there (a right
    still in force at 10 years counts as in force), so the comparison is over the same years as a share in force at
    `horizon`. Robust standard errors clustered by `cluster`; levels with fewer than `min_level` rows merged into the
    most common level. The verdict uses the log of the ratios."""
    controls = list(controls or [])
    cols = [time, event, entry, signal, *controls] + ([cluster] if cluster else [])
    d = df[cols].dropna().copy()
    d[time] = d[time].astype(float)
    d[event] = d[event].astype(float)
    d[entry] = d[entry].astype(float).clip(lower=0)
    if horizon is not None:  # rights that join after the horizon were never at risk before it
        d = d[d[entry] < horizon].copy()
        d.loc[d[time] > horizon, event] = 0.0
        d[time] = np.minimum(d[time], horizon)
    d[entry] = np.minimum(d[entry], d[time] - 1e-6)
    out = {"rows": len(d), "ended": int(d[event].sum()), "with signal": int(d[signal].sum())}
    names = ["raw", "raw low", "raw high", "adjusted", "adjusted low", "adjusted high", "share of raw remaining"]
    if min(out["with signal"], len(d) - out["with signal"]) < min_level:  # too few on one side to say anything
        return pd.Series({**out, **dict.fromkeys(names, np.nan), "controls": "", "rows merged": np.nan,
                          "verdict": "too few rows"})  # fmt: skip
    merged = _merge_rare(d, controls, min_level, event)
    keep = [c for c in controls if d[c].nunique() > 1]
    for name, terms in (("raw", []), ("adjusted", keep)):
        x = pd.get_dummies(
            d[[signal, *terms]].astype({c: str for c in terms}), columns=terms, drop_first=True, dtype=float
        )
        model = sm.PHReg(d[time].to_numpy(), x.to_numpy(float), status=d[event].to_numpy(), entry=d[entry].to_numpy())
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fit = model.fit()
        except np.linalg.LinAlgError:
            return pd.Series({**out, **dict.fromkeys(names, np.nan), "controls": ", ".join(keep), "rows merged": merged,
                              "verdict": "not estimated"})  # fmt: skip
        cov = fit.cov_params()
        if cluster:
            cov = cox_cluster_cov(d[time], d[event], d[entry], x.to_numpy(float), fit.params, cov, d[cluster])
        b, se = fit.params[0], float(np.sqrt(cov[0, 0]))
        out[name], out[f"{name} low"], out[f"{name} high"] = np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)
    out["controls"], out["rows merged"] = ", ".join(keep), merged
    lr = np.log(
        [out["raw"], out["adjusted"], out["adjusted low"], out["adjusted high"], out["raw low"], out["raw high"]]
    )
    out["share of raw remaining"] = lr[1] / lr[0] if lr[0] else np.nan
    out["verdict"] = verdict(*lr)
    return pd.Series(out)


def effects_chart(
    t: pd.DataFrame,
    *,
    title: str,
    xlabel: str,
    percent: bool = True,
    fmt: str = "{:.1f}",
    raw_name: str = "raw",
    null: float = 0,
):
    """Each row's raw effect beside its effect with the third factors held together (`adjusted_effect`'s columns),
    with 95% intervals and a line at no difference (`null`: 0 for differences, 1 for ratios): how much of each
    association the factors account for."""
    from .bivariate import dot_chart

    parts = [
        t[[col, f"{col} low", f"{col} high"]].set_axis(["value", "low", "high"], axis=1).assign(estimate=name)
        for col, name in (("raw", raw_name), ("adjusted", "third factors held together"))
    ]
    fig = dot_chart(
        pd.concat(parts),
        value="value",
        low="low",
        high="high",
        hue="estimate",
        title=title,
        xlabel=xlabel,
        percent=percent,
        fmt=fmt,
    )
    fig.axes[0].axvline(null, color="black", lw=0.8)
    return fig


def verdict(
    raw: float, adjusted: float, low: float, high: float, raw_low: float = np.nan, raw_high: float = np.nan
) -> str:
    """ADR 0046's words for what is left of a raw association once third factors are held together.

    holds: same direction, interval clear of zero, at least half the raw size left; weakened: same direction and
    interval clear of zero, less than half left; not detected once held: the interval includes zero; reversed: the
    other direction, interval clear of zero. Where the raw interval is given and includes zero, the raw association
    was not detected: appears once held (the adjusted interval is clear of zero) or not detected either way.
    """
    if not np.isfinite([raw, adjusted, low, high]).all():
        return "not estimated"
    if np.isfinite([raw_low, raw_high]).all() and raw_low <= 0 <= raw_high:
        return "not detected either way" if low <= 0 <= high else "appears once held"
    if low <= 0 <= high:
        return "not detected once held"
    if np.sign(adjusted) != np.sign(raw):
        return "reversed"
    return "holds" if abs(adjusted) >= 0.5 * abs(raw) else "weakened"


def nb_rate_ratios(
    d: pd.DataFrame,
    formula: str,
    exposure: str | None = None,
    *,
    drop: tuple[str, ...] = ("Intercept", "alpha"),
    cluster: str | None = None,
) -> pd.DataFrame:
    """Rate ratios, with 95% intervals, from a negative binomial model of a count with `exposure` (people, works,
    years: the rate's denominator). Started from a Poisson fit, which the negative binomial needs to converge on
    these data (as in B29). `alpha` is the extra spread beyond chance (0 would be Poisson). With no `exposure`, every
    row has the same (a count per patent); with `cluster`, standard errors are clustered by that column."""
    off = np.log(d[exposure].astype(float)) if exposure else np.zeros(len(d))
    final = {"cov_type": "cluster", "cov_kwds": {"groups": pd.factorize(d[cluster])[0]}} if cluster else {}
    pois = smf.glm(formula, d, family=sm.families.Poisson(), offset=off).fit()
    model = smf.negativebinomial(formula, d, offset=off)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = model.fit(start_params=np.r_[pois.params.to_numpy(), 1.0], method="bfgs", maxiter=2000, disp=0)
        fit = model.fit(start_params=fit.params.to_numpy(), method="newton", maxiter=200, disp=0, **final)
    ci = np.exp(fit.conf_int())
    return (
        pd.DataFrame({"rate ratio": np.exp(fit.params), "low": ci[0], "high": ci[1]})
        .drop(index=list(drop), errors="ignore")
        .assign(alpha=fit.params.get("alpha", np.nan), rows=int(fit.nobs), converged=bool(fit.mle_retvals["converged"]))
    )


def partial_corr_interval(
    df: pd.DataFrame, x: str, y: str, controls: list[str], *, reps: int = 1000, seed: int = 0, method="spearman"
) -> pd.Series:
    """`partial_corr` with 95% intervals for the raw and partial correlations from `reps` resamples of the rows (for
    the small lenses, whose rows are the units: countries, divisions, institutions). 1,000 resamples or more for any
    interval that is quoted (A29)."""
    d = df[[x, y, *controls]].apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)
    est = partial_corr(d, x, y, controls, method=method)
    rng = np.random.default_rng(seed)
    raw, part = [], []
    for _ in range(reps):
        r = partial_corr(d.iloc[rng.integers(0, len(d), len(d))], x, y, controls, method=method)
        raw.append(r["raw"])
        part.append(r["partial"])
    raw, part = np.array(raw, float), np.array(part, float)
    est["raw low"], est["raw high"] = np.nanquantile(raw, [0.025, 0.975])
    est["partial low"], est["partial high"] = np.nanquantile(part, [0.025, 0.975])
    est["resamples"] = reps
    return est


# --- Series over time: dependence between adjacent periods (the final review, A29) ---------------------------------


def autocorrelation(x, lag: int) -> float:
    x = np.asarray(x, float)
    x = x - x.mean()
    return float((x[:-lag] * x[lag:]).sum() / (x * x).sum()) if lag < len(x) else np.nan


def effective_n(x, y, *, max_lag: int | None = None) -> float:
    """The number of independent pairs two serially dependent series are worth for their correlation (Bartlett's
    approximation: n over 1 + 2 times the sum, over lags, of the product of the two series' autocorrelations).
    Lags run to n/4, or `max_lag`; the result is never more than n."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    max_lag = max_lag or max(1, n // 4)
    s = sum(autocorrelation(x, k) * autocorrelation(y, k) for k in range(1, max_lag + 1))
    return float(min(n, n / max(1e-9, 1 + 2 * s)))


def block_bootstrap_corr(
    x, y, *, block: int = 4, reps: int = 1000, seed: int = 0, method: str = "spearman"
) -> tuple[float, float, float]:
    """The correlation of two series with a 95% interval from a moving-block bootstrap: resamples are built from runs
    of `block` consecutive periods (4 quarters by default), so that dependence between neighbouring periods is kept,
    which resampling single periods ignores (the final review's point about §5's quarterly changes)."""
    d = pd.DataFrame({"x": np.asarray(x, float), "y": np.asarray(y, float)}).dropna().reset_index(drop=True)
    n = len(d)
    est = float(d.x.corr(d.y, method=method))
    rng = np.random.default_rng(seed)
    starts = np.arange(n - block + 1)
    k = int(np.ceil(n / block))
    vals = []
    for _ in range(reps):
        idx = (rng.choice(starts, k)[:, None] + np.arange(block)).ravel()[:n]
        s = d.iloc[idx]
        vals.append(s.x.corr(s.y, method=method))
    lo, hi = np.nanquantile(np.array(vals, float), [0.025, 0.975])
    return est, float(lo), float(hi)


def silhouette_word(score: float) -> str:
    """ADR 0046: clusters are read as segments only with a silhouette of 0.25 or more."""
    return "clear segments" if score >= 0.5 else "some structure" if score >= 0.25 else "no clear segments"
