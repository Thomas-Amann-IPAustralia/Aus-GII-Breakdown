"""The EDA helpers (analysis/eda), on small synthetic data: no network, no corpus downloads."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
import pytest  # noqa: E402
from eda import bivariate as bi  # noqa: E402
from eda import data, style  # noqa: E402
from eda import multivariate as multi  # noqa: E402
from eda import univariate as uni  # noqa: E402

KINDS = {"id", "category", "binary", "count", "money", "numeric", "rate", "date", "year"}


def test_sql_refuses_results_that_were_not_aggregated():
    assert len(data.sql("SELECT * FROM range(5)", max_rows=5)) == 5
    with pytest.raises(data.TooManyRows):
        data.sql("SELECT * FROM range(6)", max_rows=5)
    assert len(data.sql("SELECT * FROM range(6)", max_rows=None)) == 6


def test_resolve_leaves_ordinary_braces_alone(monkeypatch):
    monkeypatch.setattr(data, "table", lambda s, n: f"T[{s}.{n}]")
    monkeypatch.setattr(data, "lens_table", lambda n: f"L[{n}]")
    q = data.resolve("SELECT {'a': 1} FROM {iprapid/patent_rights} JOIN {lens/firms}")
    assert q == "SELECT {'a': 1} FROM T[iprapid.patent_rights] JOIN L[firms]"


def test_register_is_well_formed():
    reg = style.register()
    assert set(reg) == {"rights", "firms", "regions", "national", "timeline"}
    for lens, cols in reg.items():
        for col, v in cols.items():
            assert v.get("label"), f"{lens}.{col} has no label"
            assert v.get("kind") in KINDS, f"{lens}.{col} has kind {v.get('kind')!r}"
    assert style.label("firms", "rd_latest") == "R&D spend claimed (latest year) (AUD)"
    assert style.label("firms", "not_a_column") == "not_a_column"


@pytest.mark.parametrize("lens", ["rights", "firms", "regions", "national", "timeline"])
def test_register_matches_built_lens(lens):
    p = data.LENS_DIR / f"{lens}.parquet"
    if not p.exists():
        pytest.skip("lens not built here (run: uv run python -m eda.build)")
    cols = pq.read_schema(p).names
    assert cols == list(style.register()[lens]), "variables.yaml must list the lens's columns, in order"


def test_describe_counts_outliers_and_zeros():
    s = pd.Series([0, 1, 2, 3, 4, 5, 6, 7, 8, 100, None])
    d = uni.describe(s)
    assert d["count"] == 10 and d["missing"] == 1
    assert d["% zero"] == pytest.approx(10.0)
    assert d["outliers (1.5 IQR)"] == 1
    assert d["median"] == pytest.approx(4.5)


def test_overview_reports_completeness():
    df = pd.DataFrame({"a": [1, 2, None, 4], "b": ["x", "x", "y", None]})
    o = uni.overview(df)
    assert o.loc["a", "% filled"] == 75 and o.loc["b", "most common"] == "x (66.7%)"
    assert pd.isna(o.loc["b", "min"])


def test_pair_stats_and_screening():
    rng = np.random.default_rng(0)
    x = pd.Series(rng.normal(size=500), name="x")
    df = pd.DataFrame({"x": x, "y": np.exp(x), "z": rng.normal(size=500)})
    s = bi.pair_stats(df.x, df.y)
    assert s["spearman rho"] == pytest.approx(1.0) and s["pearson r"] < 1
    screen = bi.screen_pairs(df, ["x", "y", "z"])
    assert (screen.iloc[0]["variable 1"], screen.iloc[0]["variable 2"]) == ("x", "y")


def test_wilson_interval_matches_known_value():
    low, high = bi.wilson(np.array([5]), np.array([10]))
    assert low[0] == pytest.approx(0.2366, abs=1e-4) and high[0] == pytest.approx(0.7634, abs=1e-4)


def test_rate_by_and_compare_groups():
    g = pd.Series(["a"] * 100 + ["b"] * 100)
    flag = pd.Series([True] * 30 + [False] * 70 + [True] * 60 + [False] * 40)
    t = bi.rate_by(flag, g)
    assert t.loc["a", "rate"] == pytest.approx(0.3) and t.loc["b", "rate"] == pytest.approx(0.6)
    c = bi.compare_groups(pd.Series(range(200)), g)
    assert c["test"] == "Mann-Whitney" and c["rank-biserial"] == pytest.approx(-1.0)


def test_partial_correlation_removes_a_shared_driver():
    rng = np.random.default_rng(1)
    z = rng.normal(size=2000)
    df = pd.DataFrame({"z": z, "x": z + 0.3 * rng.normal(size=2000), "y": z + 0.3 * rng.normal(size=2000)})
    p = multi.partial_corr(df, "x", "y", ["z"], method="pearson")
    assert p["raw"] > 0.8 and abs(p["partial"]) < 0.1


def test_pca_and_clusters_run():
    rng = np.random.default_rng(2)
    df = pd.DataFrame(rng.normal(size=(300, 4)), columns=list("abcd"))
    df["e"] = df.a * 2
    explained, loadings = multi.pca(df, list("abcde"))
    assert explained["cumulative %"].iloc[-1] == pytest.approx(100)
    assert loadings.shape == (5, 5)
    assert multi.vif(df, list("abcd")).max() < 2
    scores = multi.clusters(df, list("abcd"), ks=range(2, 4))
    assert list(scores.index) == [2, 3]


def test_charts_draw():
    style.setup()
    s = pd.Series(np.random.default_rng(3).lognormal(size=1000), name="v")
    for fig in (
        uni.distribution(s),
        uni.distribution(s, log=True),
        uni.bin_check(s),
        uni.counts(pd.Series(list("aabbbcd") * 10 + [None])),
        uni.missing(pd.DataFrame({"a": [1, None], "b": [1, 2]})),
        bi.rate_chart(bi.rate_by(pd.Series([True, False] * 50), pd.Series(["x"] * 60 + ["y"] * 40)), title="t"),
        multi.corr_heatmap(pd.DataFrame({"a": s, "b": s**2, "c": -s}), ["a", "b", "c"]),
    ):
        assert isinstance(fig, plt.Figure)
    months = pd.date_range("2000-01-01", periods=48, freq="MS")
    timeline = pd.DataFrame({"month": months, "patents_granted": pd.array(range(48), dtype="Int64")})
    timeline["policy_events"] = None
    timeline.loc[20, "policy_events"] = "raising-the-bar"
    assert isinstance(uni.monthly(timeline, ["patents_granted"], events=["raising-the-bar"]), plt.Figure)
    fig, ax = plt.subplots()
    bi.scatter_trend(ax, s, s * 2, sample=500)
    plt.close("all")
