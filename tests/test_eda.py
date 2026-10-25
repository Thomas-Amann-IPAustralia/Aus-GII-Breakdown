"""The EDA helpers (analysis/eda), on small synthetic data: no network, no corpus downloads."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
import pytest  # noqa: E402
from eda import bivariate as bi  # noqa: E402
from eda import build, data, style  # noqa: E402
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
    assert set(reg) == {"rights", "firms", "regions", "region_indicators", "national", "timeline"}
    for lens, cols in reg.items():
        for col, v in cols.items():
            assert v.get("label"), f"{lens}.{col} has no label"
            assert v.get("kind") in KINDS, f"{lens}.{col} has kind {v.get('kind')!r}"
    assert style.label("firms", "rd_latest") == "R&D spend claimed (latest year) (AUD)"
    assert style.label("firms", "not_a_column") == "not_a_column"


@pytest.mark.parametrize("lens", ["rights", "firms", "regions", "region_indicators", "national", "timeline"])
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


def test_seasonal_profile_finds_a_quiet_month():
    months = pd.date_range("2000-01-01", periods=72, freq="MS")
    y = pd.Series(100, index=months).where(months.month != 1, 50)  # every January half an ordinary month
    p = uni.seasonal_profile(pd.DataFrame({"month": months, "s": y.values}), ["s"])
    assert p.loc["s", 1] == pytest.approx(100 * 50 / (100 - 50 / 12), rel=1e-6)
    assert p.loc["s", 7] == pytest.approx(100 / (1 - 50 / 1200), rel=1e-6)


def test_event_windows_compare_the_months_either_side():
    months = pd.date_range("2000-01-01", periods=36, freq="MS")
    timeline = pd.DataFrame({"month": months, "s": [10] * 18 + [40] + [20] * 17, "policy_events": None})
    timeline.loc[18, "policy_events"] = "a-change"
    w = uni.event_windows(timeline, {"a-change": ["s"]}).loc[("a-change", "s")]
    assert w["average, 12 months before"] == 10 and w["average, 12 months after"] == 20
    assert w["month of the change, × average before"] == 4 and w["% change in the average"] == 100


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
    assert isinstance(uni.around_events(timeline, {"raising-the-bar": ["patents_granted"]}), plt.Figure)
    fig, ax = plt.subplots()
    bi.scatter_trend(ax, s, s * 2, sample=500)
    plt.close("all")


def _built(lens):
    p = data.LENS_DIR / f"{lens}.parquet"
    if not p.exists():
        pytest.skip("lens not built here (run: uv run python -m eda.build)")
    return p


@pytest.mark.parametrize(
    ("lens", "key"),
    [
        ("rights", "ip_right_type, application_number"),
        ("firms", "abn"),
        ("regions", "poa_code"),
        ("region_indicators", "poa_code, source, indicator, period"),
        ("national", "iso3, year, indicator"),
        ("timeline", "month"),
    ],
)
def test_every_lens_has_one_row_per_key(lens, key):
    p = _built(lens)
    r = data.sql(f"SELECT count(*) AS n, count(DISTINCT ({key})) AS distinct_keys FROM read_parquet('{p}')").iloc[0]
    assert r["n"] == r["distinct_keys"]


def test_timeline_series_are_empty_where_not_recorded():
    """No false zeros (ADR 0010): within each series' coverage, no run of zeros longer than 12 months (except the
    'origin unknown' series, whose zeros are real); the months still being recorded are empty; and no series ends on
    a cliff (its last month at least half its previous year's median). The cliff check applies where that median is
    100 or more: a smaller series, such as design lapses at about 45 a month, halves by chance."""
    from eda import build

    _built("timeline")
    t = data.load_lens("timeline").set_index("month")
    for c, _ in build.TIMELINE_APPLICATIONS + build.TIMELINE_EVENTS:
        s = t[c].dropna()
        assert len(s), c
        assert s.index.max() == t.index.max() - pd.DateOffset(months=build.TIMELINE_LAG.get(c, 0)), c
        assert t[c].loc[s.index.min() : s.index.max()].notna().all(), f"{c} has gaps inside its coverage"
        if c not in build.TIMELINE_STRUCTURAL_ZEROS:
            run = longest = 0
            for v in s:
                run = run + 1 if v == 0 else 0
                longest = max(longest, run)
            assert longest <= 12, f"{c}: {longest} months of zeros inside its coverage"
        median = s.iloc[-13:-1].median()
        assert median < 100 or s.iloc[-1] >= median / 2, f"{c} ends on a cliff ({s.iloc[-1]} against {median})"


def test_timeline_series_start_where_set_and_have_no_batch_gaps():
    """Each hand-set start is where the series begins (ADR 0014); and within a series' coverage no month falls below
    a twentieth of the two years around it (where those run at 100 or more a month), except two known pauses: trade
    mark registrations in January 1996, when the Trade Marks Act 1995 commenced, and patent cessations in February
    2020 (7, against 2,468 in March)."""
    from eda import build

    _built("timeline")
    t = data.load_lens("timeline").set_index("month")
    for c, start in build.TIMELINE_START_OVERRIDE.items():
        assert t[c].first_valid_index() == pd.Timestamp(start), c
    known = {("trade_marks_registered", "1996-01"), ("patents_ceased", "2020-02")}
    for c, _ in build.TIMELINE_APPLICATIONS + build.TIMELINE_EVENTS:
        y = t[c].dropna().astype(float)
        around = y.rolling(25, center=True, min_periods=13).median()
        low = y[(around >= 100) & (y < around / 20)]
        assert {(c, f"{m:%Y-%m}") for m in low.index} <= known, f"{c}: {list(low.index.strftime('%Y-%m'))}"


def test_timeline_cpi_is_quarterly():
    _built("timeline")
    t = data.load_lens("timeline")
    filled = t[t.cpi.notna()]
    assert set(filled.month_of_year) == {3, 6, 9, 12} and len(filled) > 300


def test_firms_age_basis_names_the_date_that_set_first_seen():
    p = _built("firms")
    bad = data.sql(f"""
        SELECT count(*) FILTER (first_seen IS NOT NULL AND age_basis IS NULL) AS no_basis,
               count(*) FILTER (age_truncated AND age_basis = 'asic') AS truncated_asic
        FROM read_parquet('{p}')""").iloc[0]
    assert bad.to_dict() == {"no_basis": 0, "truncated_asic": 0}


def test_regions_have_no_zero_census_medians():
    p = _built("regions")
    cols = ["median_age", "median_personal_income_weekly", "median_household_income_weekly", "median_rent_weekly"]
    zero = " + ".join(f"count(*) FILTER ({c} = 0)" for c in cols)
    assert data.sql(f"SELECT {zero} AS n FROM read_parquet('{p}')").n[0] == 0


def test_national_has_one_name_per_country_and_both_rd_series():
    p = _built("national")
    r = data.sql(f"""
        SELECT (SELECT max(k) FROM (SELECT count(DISTINCT country) AS k FROM read_parquet('{p}') GROUP BY iso3))
                 AS names,
               count(*) FILTER (australia AND indicator = 'OECD.MSTI.G') AS au_oecd_rd,
               count(*) FILTER (australia AND indicator = 'GB.XPD.RSDV.GD.ZS') AS au_wdi_rd,
               count(*) FILTER (indicator LIKE 'IP.TMK%') AS trade_marks
        FROM read_parquet('{p}')""").iloc[0]
    assert r.names == 1 and r.au_oecd_rd > 0 and r.au_wdi_rd > 0 and r.trade_marks > 0


def test_rights_origin_is_three_valued_and_patents_are_typed():
    p = data.LENS_DIR / "rights.parquet"
    if not p.exists():
        pytest.skip("lens not built here (run: uv run python -m eda.build)")
    bad = data.sql(f"""
        SELECT
            count(*) FILTER (australian_applicant IS DISTINCT FROM
                CASE WHEN applicants_au > 0 THEN true WHEN applicants_overseas > 0 THEN false END) AS origin,
            count(*) FILTER (applicants_au + applicants_overseas + applicants_country_unknown <> applicant_count)
                AS applicants,
            count(*) FILTER ((ip_right_type = 'patent') <> (patent_type IS NOT NULL)) AS patent_type,
            count(*) FILTER (patent_type = 'provisional' AND has_agent IS NOT NULL) AS provisional_agents,
            count(*) FILTER (main_area IS NOT NULL AND ip_right_type <> 'patent') AS main_area,
            count(*) FILTER (retired_date = DATE '1970-01-01' OR year(registered_date) < 1904) AS placeholders,
            count(*) FILTER (ip_right_type = 'trade_mark' AND registered_date < DATE '1986-01-01'
                             AND days_to_registration IS NOT NULL) AS registered_at_filing,
            count(*) FILTER (applicant_country = 'au' AND applicant_state NOT IN
                             ('nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act')) AS australian_states,
            count(*) FILTER (founder_state NOT IN ('nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act'))
                AS founder_states,
            count(*) FILTER ((patent_type = 'provisional') <> (representation IS NULL)) AS representation,
            count(*) FILTER ((representation = 'self') <> (has_agent IS NOT DISTINCT FROM false)) AS self_filed,
            count(*) FILTER (representation = 'attorney' AND agent_clients < 5) AS attorneys,
            count(*) FILTER (founder_count = 0 AND (holder_changed IS NOT NULL OR founding_australian IS NOT NULL))
                AS no_founder,
            count(*) FILTER (founder_postcode IS NOT NULL AND NOT founding_australian) AS founder_postcode,
            count(*) FILTER (ip_right_type = 'patent' AND filing_fy < 2003 AND holder_changed IS NOT NULL)
                AS old_patent_holders
        FROM read_parquet('{p}')""").iloc[0]
    assert bad.to_dict() == {
        "origin": 0,
        "applicants": 0,
        "patent_type": 0,
        "provisional_agents": 0,
        "main_area": 0,
        "placeholders": 0,
        "registered_at_filing": 0,
        "australian_states": 0,
        "founder_states": 0,
        "representation": 0,
        "self_filed": 0,
        "attorneys": 0,
        "no_founder": 0,
        "founder_postcode": 0,
        "old_patent_holders": 0,
    }


def test_rights_events_attachment_is_consistent():
    p = _built("rights")
    dates = ["date_of_patent", "exam_requested_date", "accepted_date", "certified_date", "opposed_date"]
    dates += ["first_assigned_date", "term_extended_date"]
    out_of_range = " OR ".join(
        f"{d} < DATE '1904-01-01' OR {d} > DATE '{build.TODAY}' OR {d} = DATE '1970-01-01'" for d in dates
    )
    before_filing = " OR ".join(f"{d} < earliest_filed_date" for d in dates[1:])
    bad = data.sql(f"""
        SELECT
            count(*) FILTER ({out_of_range}) AS placeholder_dates,
            count(*) FILTER ({before_filing}) AS before_filing,
            count(*) FILTER (date_of_patent IS NOT NULL AND ip_right_type <> 'patent') AS date_of_patent,
            count(*) FILTER (exam_requested_date IS NOT NULL AND ip_right_type NOT IN ('patent', 'design')) AS exam,
            count(*) FILTER ((ip_right_type = 'trade_mark') AND exam_expedited IS NULL) AS trade_mark_expedited,
            count(*) FILTER (certified_date IS NOT NULL AND ip_right_type NOT IN ('patent', 'design')) AS certified,
            count(*) FILTER (term_extended_date IS NOT NULL AND patent_type IS DISTINCT FROM 'standard') AS extended,
            count(*) FILTER ((ip_right_type = 'pbr') <> (assignment_count IS NULL)) AS assignments,
            count(*) FILTER ((assignment_count > 0) <> (first_assigned_date IS NOT NULL)) AS first_assigned,
            count(*) FILTER ((in_force IS NULL) <> (years_in_force IS NULL)) AS lifetime_pairs,
            count(*) FILTER (in_force IS NOT NULL AND registered_date IS NULL) AS lifetime_unregistered,
            count(*) FILTER (years_in_force < 0) AS negative_lifetime,
            count(*) FILTER (NOT in_force AND retired_date IS NULL) AS ended_without_date
        FROM read_parquet('{p}')""").iloc[0]
    assert bad.to_dict() == dict.fromkeys(bad.index, 0)


def test_kaplan_meier_matches_a_hand_count():
    # 10 at risk: 2 end at t=1, 1 is unfinished at t=1, then 3 end at t=2 of the 7 left, and 4 are unfinished then
    counts = pd.DataFrame({"t": [1, 2], "ended": [2, 3], "unfinished": [1, 4]})
    km = uni.kaplan_meier(counts)
    assert km.at_risk.tolist() == [10, 7]
    assert np.allclose(km.survival, [0.8, 0.8 * 4 / 7])
    assert (km.lower <= km.survival).all() and (km.survival <= km.upper).all()
    at = uni.survival_at(km.assign(g="a"), [0, 1.5, 2, 5], by="g", min_at_risk=1)
    assert np.allclose(at.loc["a"].tolist()[:3], [1.0, 0.8, 0.8 * 4 / 7])
    assert np.isnan(at.loc["a", 5])  # beyond the curve


def test_firms_count_by_the_filer_and_name_their_state():
    p = _built("firms")
    rights = _built("rights")
    bad = data.sql(f"""
        SELECT
            count(*) FILTER (state NOT IN ('NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT')) AS states,
            count(*) FILTER (n_held_in_force > n_held) AS held,
            count(*) FILTER (remoteness LIKE 'No usual address%') AS remoteness,
            (SELECT count(*) FROM read_parquet('{rights}') WHERE founder_abn IS NOT NULL AND ip_right_type <> 'pbr')
              - sum(n_patents_standard + n_patents_provisional + n_patents_second_tier + n_trade_marks + n_designs)
              AS filed
        FROM read_parquet('{p}')""").iloc[0]
    assert bad.to_dict() == dict.fromkeys(bad.index, 0)


def test_poisson_interval_matches_known_values():
    lo, hi = uni.poisson_interval([0, 10])
    assert lo[0] == 0 and hi[0] == pytest.approx(3.689, abs=1e-3)
    assert (lo[1], hi[1]) == (pytest.approx(4.795, abs=1e-3), pytest.approx(18.390, abs=1e-3))
    fig, outside = uni.funnel(pd.Series([5, 50, 0, 400]), pd.Series([100, 1000, 10, 10_000]), per=1000)
    assert set(outside.index) >= {"% above the 95% limit", "% below the 95% limit"}
    plt.close("all")


def test_postcode_ranges():
    got = data.sql(f"""
        SELECT {build.postcode_range("pc")} AS r FROM (VALUES ('2000'), ('1475'), ('9726'), ('0031'), (NULL)) t(pc)
    """).r.tolist()
    assert got[:4] == ["delivery", "non_geographic", "non_geographic", "none"] and pd.isna(got[4])


def test_regions_count_by_the_filer_and_hide_unstable_rates():
    """Applications are the rights filed from each postal area (by `founder_postcode`, in the window), and no rate is
    shown where fewer than MIN_EXPECTED would be expected at the national rate (B3, ADR 0017)."""
    p = _built("regions")
    rights = _built("rights")
    lo, hi = build.WINDOW
    r = data.sql(f"""
        WITH filed AS (
            SELECT count(*) FILTER (ip_right_type = 'trade_mark') AS tm,
                   count(*) FILTER (patent_type = 'standard') AS sp
            FROM read_parquet('{rights}') WHERE filing_fy BETWEEN {lo} AND {hi}
              AND founder_postcode IN (SELECT poa_code FROM read_parquet('{p}')))
        , nat AS (SELECT sum(patents_standard) / sum(persons) AS rate FROM read_parquet('{p}'))
        SELECT (SELECT tm FROM filed) - sum(trade_marks) AS tm, (SELECT sp FROM filed) - sum(patents_standard) AS sp,
               count(*) FILTER (trade_marks_by_organisations > trade_marks) AS org,
               count(*) FILTER (persons * nat.rate < {build.MIN_EXPECTED}
                                AND patents_standard_per_10k_people IS NOT NULL) AS shown_small,
               count(*) FILTER (persons * nat.rate >= {build.MIN_EXPECTED}
                                AND patents_standard_per_10k_people IS NULL) AS hidden_large
        FROM read_parquet('{p}'), nat GROUP BY nat.rate""").iloc[0]
    assert r.to_dict() == dict.fromkeys(r.index, 0)


def test_region_indicators_split_counts_without_losing_them():
    """A count published for SA2s sums, over the postal areas, to the SA2s' own total (those with any residents or
    mesh blocks in the lens's postal areas); levels are never marked as counts; the Census's total people match the
    lens's population, to within the Census's perturbation (ADR 0018)."""
    p = _built("region_indicators")
    regions = _built("regions")
    r = data.sql(f"""
        WITH sa2 AS (SELECT DISTINCT sa2_code FROM {data.table("abs_regions", "mesh_blocks")}
                     WHERE poa_code IN (SELECT poa_code FROM read_parquet('{regions}'))),
        published AS (
            SELECT sum(value) AS v FROM {data.table("abs_cabee", "cubes")}
            WHERE cube = '8165DC08' AND table_title LIKE '%June 2025%' AND size = 'Total'
              AND sa2_code IN (SELECT sa2_code FROM sa2)),
        split AS (SELECT sum(value) AS v FROM read_parquet('{p}')
                  WHERE source = 'cabee' AND indicator LIKE 'employment|%|Total' AND period = 'June 2025')
        SELECT abs((SELECT v FROM split) / (SELECT v FROM published) - 1) < 1e-9 AS conserved,
               (SELECT count(*) FROM read_parquet('{p}') WHERE additive AND (
                    regexp_matches(lower(unit), 'median|mean|average|%|rate')
                    OR (source <> 'phidu' AND regexp_matches(lower(label), 'median|mean|average'))))
                 AS levels_as_counts,
               -- the Census's counts are perturbed (randomly adjusted to protect privacy), the ASGS's are not
               abs((SELECT sum(value) FROM read_parquet('{p}') WHERE indicator = 'G01.Tot_P_P')
                   / (SELECT sum(persons) FROM read_parquet('{regions}')) - 1) < 0.001 AS census_people
    """).iloc[0]
    assert bool(r.conserved) and r.levels_as_counts == 0 and bool(r.census_people)
