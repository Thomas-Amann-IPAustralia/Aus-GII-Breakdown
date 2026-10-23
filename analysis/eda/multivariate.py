"""Stage 3: several variables at once.

These describe structure (which variables move together, which groups of places or firms look alike, whether an
association survives holding others fixed). None of them shows cause and effect.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

from .style import label


def corr_heatmap(df: pd.DataFrame, columns: list[str], *, lens: str | None = None, method: str = "spearman", title=""):
    """The correlation of every pair of `columns`, as a lower-triangle heatmap with the values written in."""
    c = df[columns].apply(pd.to_numeric, errors="coerce").corr(method=method)
    names = [label(lens, x, unit=False) if lens else x for x in columns]
    c.index, c.columns = names, names
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
        cbar_kws={"shrink": 0.6, "label": f"{method} correlation"},
        annot_kws={"size": 8},
    )
    ax.set_title(title or f"How the variables move together ({method})")
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
