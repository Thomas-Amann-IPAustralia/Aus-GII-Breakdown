"""Draw the evidence pages' interactive charts from the lens tables: `evidence/data/charts/<id>.json`.

    uv run python -m eda.build              # the lens tables, first (about two minutes once the corpus is cached)
    uv run python -m atlas.charts           # every chart
    uv run python -m atlas.charts U44 U45   # some

Each chart runs the same query, on the same lens, as the notebook cell above its observation, and then checks
(`same`) that it reproduces the numbers the observation quotes. If the lens has changed so that a quoted number no
longer comes out, the chart is not written: the notebook and its observation must be brought up to date first.

A chart is a small JSON spec that `evidence/js/charts.js` turns into an ECharts chart with a table beside it:

    {type: line | bar | scatter | range, horizontal, stack, title, subtitle, source, note,
     x: {name, type: category | value | log, values, min, max, format},
     y: {name, type, min, max, format, digits},
     series: [{name, data, line: dashed | dotted, area, step, colour}],
     marks: {x: [{at, label}], y: [{at, label}], bands: [{from, to, label}]},
     views: [{label, ...the same keys, overriding}]}

Charts of a handful of quoted values are written by hand in the observation's YAML instead (`chart:` as a mapping),
where the build checks every number against the notebook.
"""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
from eda import sql

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "data" / "charts"
CHARTS: dict[str, Callable[[], dict]] = {}

TYPES = {
    "standard": "Standard patents",
    "provisional": "Provisional applications",
    "second_tier": "Second-tier patents",
    "trade_mark": "Trade marks",
    "design": "Designs",
    "pbr": "Plant breeder's rights",
}


class Mismatch(AssertionError):
    """A chart no longer reproduces a number its observation quotes."""


def chart(fn: Callable[[], dict]) -> Callable[[], dict]:
    CHARTS[fn.__name__] = fn
    return fn


def same(got: float, quoted: float, what: str, tol: float | None = None) -> None:
    """Check that `got`, rounded as the observation rounds it, is the number it quotes."""
    if tol is None:
        decimals = len(str(quoted).split(".")[1]) if "." in str(quoted) else 0
        tol = 0.5 * 10**-decimals + 1e-9
    if got is None or (isinstance(got, float) and math.isnan(got)) or abs(got - quoted) > tol:
        raise Mismatch(f"{what}: the lens gives {got}, the observation quotes {quoted}")


def r(v, digits: int = 2):
    """A value for the JSON: rounded, and None for a missing one."""
    if v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NA:
        return None
    return round(float(v), digits) if isinstance(v, float) else int(v) if hasattr(v, "__int__") else v


def col(df: pd.DataFrame, name: str, digits: int = 2) -> list:
    return [r(v, digits) for v in df[name]]


def lorenz(values: pd.Series, grid: list[float]) -> list[list[float]]:
    """The share of the total held by the top p% of holders, for each p in `grid`, ranking the largest first. The top
    p% is round(p% of n) holders, as the notebook takes the top 1%."""
    v = values.sort_values(ascending=False).to_numpy(dtype=float)
    cum, total, n = v.cumsum(), v.sum(), len(v)
    out = [[0.0, 0.0]]
    for p in grid:
        k = max(1, round(p / 100 * n))
        out.append([p, round(100 * cum[k - 1] / total, 2)])
    return out


LORENZ_GRID = [0.1, 0.25, 0.5, 1, 2, 3, 4, 5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]


# ------------------------------------------------------------------------------------------------------------ firms


@chart
def U44() -> dict:
    cols = {"n_patents_standard": "Standard patents", "n_trade_marks": "Trade marks", "n_designs": "Designs"}
    f = sql(f"SELECT {', '.join(cols)} FROM {{lens/firms}}", max_rows=None)
    series = []
    for c, name in cols.items():
        v = f.loc[f[c] > 0, c]
        curve = lorenz(v, LORENZ_GRID)
        series.append({"name": name, "data": curve})
        quoted = {"n_patents_standard": 55.3, "n_trade_marks": 25.7, "n_designs": 35.6}[c]
        same(dict(map(tuple, curve))[1], quoted, f"top 1% share of {name}")
    same(int((f.n_patents_standard > 0).sum()), 23971, "firms filing standard patents")
    series.append(
        {"name": "If every firm filed the same", "data": [[0, 0], [100, 100]], "line": "dashed", "colour": "muted"}
    )
    return {
        "type": "line",
        "title": "How concentrated firms' filing is",
        "subtitle": "Firms lined up from the most applications to the fewest: the share of all applications "
        "filed by the "
        "top x% of filing firms",
        "x": {"name": "Top % of filing firms", "type": "value", "min": 0, "max": 100, "format": "pct"},
        "y": {"name": "% of the applications they filed", "min": 0, "max": 100, "format": "pct"},
        "series": series,
        "marks": {"x": [{"at": 1, "label": "Top 1%"}]},
        "source": "IP Australia, IP RAPID; ABN spine (lens: firms). Each application credited to the firm that "
        "filed it.",
        "note": "The observation quotes the top 1%. The rest of the curve is drawn from the same table for context.",
        "table_points": [1, 5, 10, 25, 50],
    }


@chart
def U45() -> dict:
    first = sql("""
        SELECT fy, count(*) FILTER (k = 'patent') AS patent, count(*) FILTER (k = 'trade_mark') AS trade_mark,
               count(*) FILTER (k = 'design') AS design
        FROM (SELECT patent_first_fy AS fy, 'patent' AS k FROM {lens/firms} UNION ALL
              SELECT trade_mark_first_fy, 'trade_mark' FROM {lens/firms} UNION ALL
              SELECT design_first_fy, 'design' FROM {lens/firms})
        WHERE fy BETWEEN 1990 AND 2026 GROUP BY 1 ORDER BY 1
    """)
    lag = sql("""
        SELECT filing_fy AS fy,
               100 * avg((founder_abn IS NOT NULL)::int) FILTER (ip_right_type = 'trade_mark'
                   AND founder_type = 'organisation') AS tm,
               100 * avg((founder_abn IS NOT NULL)::int) FILTER (patent_type = 'standard'
                   AND founder_type = 'organisation') AS std,
               100 * avg((founder_abn IS NOT NULL)::int) FILTER (ip_right_type = 'design'
                   AND founder_type = 'organisation') AS design
        FROM {lens/rights} WHERE founding_australian AND filing_fy BETWEEN 2015 AND 2026 GROUP BY 1 ORDER BY 1
    """)
    t = first.set_index("fy")
    same(t.trade_mark[2024], 11318, "first trade mark filers FY2024")
    same(t.trade_mark[2026], 7384, "first trade mark filers FY2026")
    lg = lag.set_index("fy")
    same(lg.tm[2024], 84.1, "trade marks with ABN FY2024")
    same(lg.tm[2026], 59.9, "trade marks with ABN FY2026")
    fy = lambda s: [f"FY{y}" for y in s]  # noqa: E731
    return {
        "type": "line",
        "title": "Fewer new filers, and fewer applications linked to a business",
        "source": "IP Australia, IP RAPID (lenses: firms, rights)",
        "views": [
            {
                "label": "Share linked to the filer's ABN",
                "subtitle": "Australian organisations' applications that carry the filer's ABN, by financial year",
                "x": {"type": "category", "values": fy(lag.fy)},
                "y": {"name": "% with the filer's ABN", "min": 40, "max": 100, "format": "pct", "digits": 1},
                "series": [
                    {"name": "Trade marks", "data": col(lag, "tm", 1)},
                    {"name": "Designs", "data": col(lag, "design", 1)},
                    {"name": "Standard patents", "data": col(lag, "std", 1)},
                ],
                "marks": {"bands": [{"from": "FY2024", "to": "FY2026", "label": "The fall"}]},
            },
            {
                "label": "Firms filing for the first time",
                "subtitle": "Firms filing their first application of each kind, by financial year",
                "x": {"type": "category", "values": fy(first.fy)},
                "y": {"name": "Firms", "min": 0, "format": "int"},
                "series": [
                    {"name": "Trade marks", "data": col(first, "trade_mark")},
                    {"name": "Designs", "data": col(first, "design")},
                    {"name": "Patents", "data": col(first, "patent")},
                ],
                "marks": {"bands": [{"from": "FY2024", "to": "FY2026", "label": "Linking falls"}]},
                "note": "ABNs began in 1999-2000; first filings before then are of firms that have had an ABN since.",
            },
        ],
    }


@chart
def U46() -> dict:
    f = sql(
        "SELECT rd_latest, in_rdti, austender_value, austender_contracts, in_austender, total_income_latest, "
        "in_ato_ctt "
        "FROM {lens/firms}",
        max_rows=None,
    )
    groups = [
        ("R&D claimed, latest year", f.loc[f.in_rdti, "rd_latest"].dropna(), 28.1),
        ("Government contract value", f.loc[f.in_austender, "austender_value"].dropna(), 83.1),
        ("Income (tax transparency reports)", f.loc[f.in_ato_ctt, "total_income_latest"].dropna(), 30.8),
    ]
    series = []
    for name, v, quoted in groups:
        curve = lorenz(v.astype(float), LORENZ_GRID)
        same(dict(map(tuple, curve))[1], quoted, f"top 1% of {name}")
        series.append({"name": name, "data": curve})
    series.append(
        {"name": "If every firm had the same", "data": [[0, 0], [100, 100]], "line": "dashed", "colour": "muted"}
    )
    return {
        "type": "line",
        "title": "Contract value is far more concentrated than R&D claims",
        "subtitle": "Firms lined up from the largest amount to the smallest: the share of the total held by the top x%",
        "x": {"name": "Top % of firms", "type": "value", "min": 0, "max": 100, "format": "pct"},
        "y": {"name": "% of the total", "min": 0, "max": 100, "format": "pct"},
        "series": series,
        "marks": {"x": [{"at": 1, "label": "Top 1%"}]},
        "source": "ATO, R&D Tax Incentive and tax transparency reports; AusTender (lens: firms). Nominal dollars.",
        "note": "The observation quotes the top 1%. The rest of each curve is drawn from the same table for context.",
        "table_points": [1, 5, 10, 25, 50],
    }


@chart
def U47() -> dict:
    groups = {
        "All firms": "true",
        "IP filers": "ip_filed_total > 0",
        "R&D claimants": "in_rdti",
        "Government suppliers": "in_austender",
    }
    order = [
        "Major Cities of Australia",
        "Inner Regional Australia",
        "Outer Regional Australia",
        "Remote Australia",
        "Very Remote Australia",
    ]

    def share(column: str) -> pd.DataFrame:
        parts = []
        for name, cond in groups.items():
            d = sql(
                f"SELECT {column} AS v, count(*) AS n FROM {{lens/firms}} WHERE {cond} AND {column} IS NOT NULL "
                "GROUP BY 1"
            )
            parts.append(d.set_index("v").n.rename(name) / d.n.sum() * 100)
        return pd.concat(parts, axis=1)

    remote = share("remoteness").loc[order]
    decile = share("irsad_decile").sort_index()
    same(remote.loc["Major Cities of Australia", "R&D claimants"], 89.9, "R&D claimants in major cities")
    same(decile.loc[10, "R&D claimants"], 39.3, "R&D claimants in decile 10")
    names = list(groups)
    return {
        "type": "bar",
        "title": "Where firms are registered, by group",
        "source": "ABR; ABS remoteness areas and SEIFA 2021 (lens: firms). The firm's main business address.",
        "views": [
            {
                "label": "Remoteness",
                "subtitle": "% of each group's firms, by the remoteness of their registered postcode",
                "x": {
                    "type": "category",
                    "values": [o.replace(" of Australia", "").replace(" Australia", "") for o in order],
                },
                "y": {"name": "% of the group", "min": 0, "max": 100, "format": "pct", "digits": 1},
                "series": [{"name": n, "data": col(remote, n, 1)} for n in names],
            },
            {
                "label": "Advantage",
                "subtitle": "% of each group's firms, by the advantage of their postcode (IRSAD tenth: 1 least, "
                "10 most "
                "advantaged)",
                "x": {"type": "category", "values": [str(int(i)) for i in decile.index], "name": "IRSAD tenth"},
                "y": {"name": "% of the group", "min": 0, "format": "pct", "digits": 1},
                "series": [{"name": n, "data": col(decile, n, 1)} for n in names],
            },
        ],
    }


# ------------------------------------------------------------------------------------------------------------ corpus


def fy(years) -> list[str]:
    return [f"FY{int(y)}" for y in years]


def pivot(df: pd.DataFrame, index: str, columns: str, values: str, order=None, full=None) -> pd.DataFrame:
    p = df.pivot_table(index=index, columns=columns, values=values, aggfunc="sum")
    if full is not None:
        p = p.reindex(full)
    return p[order] if order else p


@chart
def U0() -> dict:
    t = pd.read_csv(ROOT / "analysis" / "output" / "tables.csv")
    by = t.groupby("source").rows.sum().sort_values(ascending=False)
    same(len(t), 162, "tables")
    same(len(by), 41, "sources")
    same(int(by.sum()), 317792796, "rows")
    same(100 * by.iloc[:3].sum() / by.sum(), 69.73, "top three sources' share")
    names = {
        "iprapid": "IP RAPID (IP Australia)",
        "tmlink": "TM-Link (trade marks worldwide)",
        "oecd": "OECD panels",
        "abr": "ABN register (ABR)",
        "iplord": "IPLORD (IP Australia)",
        "abs_census": "ABS Census",
        "austender": "AusTender contracts",
        "phidu": "PHIDU social health atlas",
        "abs_regions": "ABS Data by Region",
        "google_patents": "Google Patents",
        "openalex_works": "OpenAlex works",
        "asic": "ASIC companies",
        "abs_cabee": "ABS business counts (CABEE)",
        "linkage": "ABN spine (built here)",
        "google_patents_inventors": "Google Patents inventors",
        "wipo_ipstats": "WIPO IP statistics",
        "wgnd": "WIPO gender-name dictionary",
        "rdti": "R&D Tax Incentive",
        "ror": "Research Organization Registry",
    }
    top = by.iloc[:12]
    rest = by.iloc[12:]
    cats = [names.get(s, s) for s in top.index] + [f"The other {len(rest)} sources"]
    vals = [r(100 * v / by.sum(), 2) for v in [*top.to_numpy(), rest.sum()]]
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Rows in the corpus, by source",
        "subtitle": "Share of all 317,792,796 rows (162 tables from 41 sources)",
        "x": {"type": "category", "values": cats},
        "y": {"name": "% of all rows", "min": 0, "format": "pct", "digits": 2},
        "series": [{"name": "Share of rows", "data": vals}],
        "source": "The corpus profile, analysis/output/tables.csv (25 October 2026)",
    }


# ------------------------------------------------------------------------------------------------------------ rights


@chart
def U1() -> dict:
    cols = {
        "ip_right_type": "Type of right",
        "status": "Current status",
        "applicant_count": "Number of applicants",
        "application_date": "Application date",
        "applicant_type": "Applicant type",
        "australian_applicant": "Origin (Australian or overseas)",
        "registered_date": "Date registered or granted",
        "retired_date": "Date the right ended",
        "applicant_state": "Applicant's state",
        "applicant_postcode": "Applicant's postcode",
        "patent_type": "Type of patent",
        "main_area": "Technology area",
        "applicant_abn": "Applicant's ABN",
    }
    q = ", ".join(f"100.0 * count({c}) / count(*) AS {c}" for c in cols)
    d = sql(f"SELECT {q} FROM {{lens/rights}}").iloc[0]
    same(d.application_date, 98.83, "application date filled")
    same(d.australian_applicant, 86.59, "origin known")
    order = sorted(cols, key=lambda c: -d[c])
    return {
        "type": "bar",
        "horizontal": True,
        "title": "How complete the rights table's core columns are",
        "subtitle": "% of the 4,356,908 rights with a value",
        "x": {"type": "category", "values": [cols[c] for c in order]},
        "y": {"name": "% filled", "min": 0, "max": 100, "format": "pct", "digits": 2},
        "series": [{"name": "% filled", "data": [r(d[c], 2) for c in order]}],
        "source": "IP Australia, IP RAPID (lens: rights)",
        "note": "Some columns are empty by design: a registration date for rights never registered, a type of patent "
        "for rights that are not patents, a state for overseas applicants.",
    }


@chart
def U3() -> dict:
    d = sql("""
        SELECT application_date AS d, count(*) AS n FROM {lens/rights}
        WHERE application_date BETWEEN DATE '2013-03-01' AND DATE '2013-05-31' GROUP BY 1 ORDER BY 1
    """)
    days = pd.DataFrame({"d": pd.date_range("2013-03-01", "2013-05-31")})
    d = days.merge(d.assign(d=pd.to_datetime(d.d)), on="d", how="left").fillna({"n": 0})
    same(int(d.loc[d.d == "2013-04-12", "n"].iloc[0]), 1856, "rights filed on 12 April 2013")
    labels = [x.strftime("%-d %b %Y") for x in d.d]
    return {
        "type": "bar",
        "title": "Applications per day around Raising the Bar",
        "subtitle": "Every type of right, 1 March to 31 May 2013. The reforms took effect on Monday 15 April 2013.",
        "x": {"type": "category", "values": labels},
        "y": {"name": "Applications", "min": 0, "format": "int"},
        "series": [{"name": "Applications", "data": col(d, "n")}],
        "labels": False,
        "marks": {"x": [{"at": "12 Apr 2013", "label": "12 April: 1,856"}]},
        "source": "IP Australia, IP RAPID (lens: rights); policy_events",
        "note": "Weekends have few or no applications.",
    }


ORIGIN = """CASE WHEN australian_applicant THEN 'Australian' WHEN NOT australian_applicant THEN 'Overseas'
                ELSE 'Origin unknown' END"""


@chart
def U5() -> dict:
    d = sql(f"""
        SELECT filing_fy AS y, coalesce(patent_type, ip_right_type) AS t, {ORIGIN} AS o, count(*) AS n
        FROM {{lens/rights}} WHERE filing_fy BETWEEN 1904 AND 2026 GROUP BY ALL
    """)
    tot = d.groupby(["t", "y"]).n.sum()
    same(tot["standard", 2026], 31136, "standard patents FY2026")
    same(tot["trade_mark", 2026], 98189, "trade marks FY2026")
    same(tot["provisional", 2026], 10069, "provisionals FY2026")
    same(tot["second_tier", 2021], 7150, "second-tier FY2021")
    survivors = {"trade_mark": 1983, "design": 1986, "provisional": 1986}
    views = []
    for t, name in TYPES.items():
        p = pivot(d[d.t == t], "y", "o", "n")
        p = p.reindex(range(int(p.index.min()), 2027)).fillna(0)
        series = [
            {"name": o, "data": col(p, o, 0), **({"colour": "muted"} if o == "Origin unknown" else {})}
            for o in ["Australian", "Overseas", "Origin unknown"]
            if o in p
        ]
        v = {
            "label": name,
            "subtitle": f"{name}: applications per financial year, by the applicants' origin",
            "x": {"type": "category", "values": fy(p.index)},
            "series": series,
        }
        if t in survivors:
            v["marks"] = {
                "bands": [{"from": f"FY{int(p.index.min())}", "to": f"FY{survivors[t]}", "label": "Survivors only"}]
            }
            v["note"] = "In the shaded years the register holds only rights that survived until it was computerised."
        views.append(v)
    return {
        "type": "line",
        "title": "Applications per financial year",
        "y": {"name": "Applications", "min": 0, "format": "int"},
        "views": views,
        "source": "IP Australia, IP RAPID (lens: rights). FY2027 (a part year) left out.",
    }


@chart
def U6() -> dict:
    d = sql("""
        SELECT filing_fy AS y, coalesce(patent_type, ip_right_type) AS t, count(*) AS n FROM {lens/rights}
        WHERE filing_fy BETWEEN 2017 AND 2027 GROUP BY ALL ORDER BY 1
    """)
    p = pivot(d, "y", "t", "n")
    same(p.loc[2025, "standard"], 29950, "standard patents FY2025")
    same(p.loc[2027, "standard"], 8357, "standard patents FY2027")
    views = []
    for t, name in TYPES.items():
        v = p[t]
        views.append(
            {
                "label": name,
                "subtitle": f"{name}: applications per financial year; FY2027 runs only to mid-October 2026",
                "series": [
                    {"name": "Complete year", "data": [r(x) if y < 2027 else None for y, x in v.items()]},
                    {
                        "name": "Part year (FY2027)",
                        "data": [r(x) if y == 2027 else None for y, x in v.items()],
                        "colour": "muted",
                    },
                ],
            }
        )
    return {
        "type": "bar",
        "stack": True,
        "title": "Are the latest years complete?",
        "x": {"type": "category", "values": fy(p.index)},
        "y": {"name": "Applications", "min": 0, "format": "int"},
        "views": views,
        "source": "IP Australia, IP RAPID (lens: rights)",
    }


@chart
def U7() -> dict:
    d = sql(f"""
        SELECT filing_fy AS y, coalesce(patent_type, ip_right_type) AS t, {ORIGIN} AS o, count(*) AS n
        FROM {{lens/rights}} WHERE filing_fy BETWEEN 1990 AND 2026 GROUP BY ALL
    """)
    p = d.pivot_table(index=["t", "y"], columns="o", values="n", aggfunc="sum", fill_value=0)
    unknown = 100 * p["Origin unknown"] / p.sum(axis=1)
    share = (100 * p.Australian / (p.Australian + p.Overseas)).where(unknown < 5)
    same(share["standard", 2026], 9.3, "Australian share of standard patents FY2026")
    same(share["trade_mark", 2026], 59.4, "Australian share of trade marks FY2026")
    years = list(range(1990, 2027))
    return {
        "type": "line",
        "title": "Australian applicants' share, where origin is recorded",
        "subtitle": "% of each type's applications of known origin; a gap where 5% or more are of unknown origin",
        "x": {"type": "category", "values": fy(years)},
        "y": {"name": "% Australian", "min": 0, "max": 100, "format": "pct", "digits": 1},
        "series": [{"name": name, "data": [r(share.get((t, y)), 1) for y in years]} for t, name in TYPES.items()],
        "source": "IP Australia, IP RAPID (lens: rights). Australian if any applicant is in Australia.",
    }


@chart
def U8() -> dict:
    d = sql("""
        SELECT strftime(date_trunc('month', application_date), '%Y-%m') AS m,
               coalesce(applicant_type, 'not recorded') AS a, count(*) AS n
        FROM {lens/rights}
        WHERE patent_type = 'provisional' AND application_date BETWEEN DATE '2021-07-01' AND DATE '2026-09-30'
        GROUP BY ALL ORDER BY 1
    """)
    p = pivot(d, "m", "a", "n").fillna(0)
    same(p.loc["2026-03"].sum(), 1274, "provisionals in March 2026")
    same(p.loc["2026-03", "individual"], 740, "individuals' provisionals in March 2026")
    labels = [pd.Timestamp(f"{m}-01").strftime("%b %Y") for m in p.index]
    return {
        "type": "line",
        "title": "Provisional applications per month",
        "subtitle": "July 2021 to September 2026, by the type of the first applicant",
        "x": {"type": "category", "values": labels},
        "y": {"name": "Provisional applications", "min": 0, "format": "int"},
        "series": [
            {"name": "First applicant an individual", "data": col(p, "individual", 0)},
            {"name": "First applicant an organisation", "data": col(p, "organisation", 0)},
        ],
        "marks": {"x": [{"at": "Mar 2026", "label": "Peak"}]},
        "source": "IP Australia, IP RAPID (lens: rights)",
    }


STAGES = {
    "Pending": ["filed", "published", "accepted", "new", "received"],
    "In force": ["granted", "registered", "protected", "certified"],
    "Ended before grant": [
        "lapsed",
        "withdrawn",
        "refused",
        "rejected",
        "inter_partes_refused",
        "ex_parte_refused",
        "voided",
    ],
    "Ended after grant": ["ceased", "expired", "revoked", "terminated", "surrendered", "cancelled", "removed"],
    "Other": ["converted", "linked", "not_filed"],
    "Unknown": ["unknown"],
}


@chart
def U9() -> dict:
    case = " ".join(f"WHEN status IN ({', '.join(repr(s) for s in v)}) THEN '{k}'" for k, v in STAGES.items())
    d = sql(f"""
        SELECT coalesce(patent_type, ip_right_type) AS t, CASE {case} END AS s, count(*) AS n
        FROM {{lens/rights}} GROUP BY ALL
    """)
    p = pivot(d, "t", "s", "n").fillna(0)
    same(p.loc["standard", "Unknown"], 393027, "standard patents of unknown status")
    pct = 100 * p.div(p.sum(axis=1), axis=0)
    same(pct.loc["trade_mark", "In force"], 41, "trade marks in force")
    order = list(TYPES)
    return {
        "type": "bar",
        "horizontal": True,
        "stack": True,
        "title": "Where each type of right stands today",
        "subtitle": "% of each type's rights, all years, grouped from the register's status",
        "x": {"type": "category", "values": [TYPES[t] for t in order]},
        "y": {"name": "% of the type's rights", "min": 0, "max": 100, "format": "pct", "digits": 1},
        "series": [
            {"name": s, "data": [r(pct.loc[t, s], 1) for t in order], **({"colour": "muted"} if s == "Unknown" else {})}
            for s in STAGES
        ],
        "source": "IP Australia, IP RAPID (lens: rights)",
    }


@chart
def U10() -> dict:
    d = sql("""
        SELECT filing_fy AS y, coalesce(patent_type, ip_right_type) AS t,
               100 * avg((registered_date IS NOT NULL)::int) AS reg
        FROM {lens/rights} WHERE filing_fy BETWEEN 1980 AND 2026 AND patent_type IS DISTINCT FROM 'provisional'
        GROUP BY ALL
    """)
    p = pivot(d, "y", "t", "reg").reindex(range(1980, 2027))
    same(p.loc[2008, "standard"], 54.4, "standard grant rate FY2008")
    same(p.loc[2019, "trade_mark"], 80.7, "trade mark registration rate FY2019")
    return {
        "type": "line",
        "title": "Share of each year's applications granted or registered",
        "subtitle": "By financial year of application, FY1980 to FY2026",
        "x": {"type": "category", "values": fy(p.index)},
        "y": {"name": "% granted or registered", "min": 0, "max": 100, "format": "pct", "digits": 1},
        "series": [{"name": TYPES[t], "data": col(p, t, 1)} for t in TYPES if t != "provisional"],
        "marks": {"bands": [{"from": "FY2022", "to": "FY2026", "label": "Many still being examined"}]},
        "source": "IP Australia, IP RAPID (lens: rights). Provisional applications are never granted.",
        "note": "Before FY1983 (trade marks) and FY1986 (designs) the register holds survivors, so their rates "
        "look high.",
    }


@chart
def U11() -> dict:
    views = []
    for t, name, width, top, quoted in [
        ("standard", "Standard patents", 50, 2500, 980),
        ("trade_mark", "Trade marks", 10, 800, 223),
    ]:
        cond = "patent_type = 'standard'" if t == "standard" else "ip_right_type = 'trade_mark'"
        d = sql(f"""
            SELECT least(floor(days_to_registration / {width}) * {width}, {top}) AS b, count(*) AS n
            FROM {{lens/rights}} WHERE {cond} AND filing_fy BETWEEN 2010 AND 2019 AND days_to_registration >= 0
            GROUP BY 1 ORDER BY 1
        """)
        med = sql(f"""SELECT median(days_to_registration) AS m FROM {{lens/rights}}
                      WHERE {cond} AND filing_fy BETWEEN 2010 AND 2019 AND days_to_registration IS NOT NULL""").m[0]
        same(med, quoted, f"median days, {name}")
        d["pct"] = 100 * d.n / d.n.sum()
        labels = [f"{int(b):,}+" if b == top else f"{int(b):,}" for b in d.b]
        mlabel = f"{int(med // width * width):,}"
        views.append(
            {
                "label": name,
                "subtitle": f"{name} filed FY2010 to FY2019 and since registered: % in each {width}-day band of "
                "days to "
                "registration",
                "x": {
                    "type": "category",
                    "values": labels,
                    "name": "Days from application to registration (start of band)",
                },
                "series": [{"name": "% of applications", "data": col(d, "pct", 2)}],
                "marks": {"x": [{"at": mlabel, "label": f"Median {int(med)} days"}]},
            }
        )
    return {
        "type": "bar",
        "title": "How long registration takes",
        "y": {"name": "% of applications", "min": 0, "format": "pct", "digits": 2},
        "labels": False,
        "views": views,
        "source": "IP Australia, IP RAPID (lens: rights). The last band holds everything longer.",
    }


@chart
def U12() -> dict:
    d = sql("""
        SELECT filing_fy AS y, coalesce(patent_type, ip_right_type) AS t, median(days_to_registration) / 365.25 AS v
        FROM {lens/rights} WHERE filing_fy BETWEEN 1990 AND 2021 AND days_to_registration IS NOT NULL GROUP BY ALL
    """)
    p = pivot(d, "y", "t", "v").reindex(range(1990, 2022))
    same(p.loc[2005, "standard"], 3.96, "median years FY2005")
    return {
        "type": "line",
        "title": "The typical wait, by year of application",
        "subtitle": "Median years from application to registration or grant, among those registered, FY1990 to FY2021",
        "x": {"type": "category", "values": fy(p.index)},
        "y": {"name": "Median years", "min": 0, "format": "num", "digits": 2},
        "series": [{"name": TYPES[t], "data": col(p, t, 2)} for t in TYPES if t != "provisional"],
        "source": "IP Australia, IP RAPID (lens: rights). Later years are still being examined, so they are left out.",
    }


def country(code: str) -> str:
    import pycountry

    special = {"us": "United States", "gb": "United Kingdom", "kr": "Korea", "tw": "Taiwan", "ru": "Russia"}
    if code in special:
        return special[code]
    c = pycountry.countries.get(alpha_2=code.upper())
    return getattr(c, "common_name", None) or (c.name if c else code.upper())


@chart
def U13() -> dict:
    d = sql("""
        SELECT applicant_country AS c, count(*) AS n FROM {lens/rights}
        WHERE patent_type = 'standard' AND filing_fy BETWEEN 2017 AND 2026 GROUP BY 1 ORDER BY 2 DESC, 1
    """)
    total = d.n.sum()
    same(100 * d.n.iloc[0] / total, 43.5, "United States share")
    top = d[d.c.notna()].head(10)
    rest = total - top.n.sum()
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Standard patents by the first applicant's country",
        "subtitle": "% of standard patents filed FY2017 to FY2026",
        "x": {"type": "category", "values": [country(c) for c in top.c] + ["All other countries, or none recorded"]},
        "y": {"name": "% of standard patents", "min": 0, "format": "pct", "digits": 1},
        "series": [{"name": "Share", "data": [r(100 * n / total, 1) for n in top.n] + [r(100 * rest / total, 1)]}],
        "source": "IP Australia, IP RAPID (lens: rights)",
    }


@chart
def U14() -> dict:
    from eda import style

    views = []
    d = sql("""SELECT main_area AS c, count(*) AS n FROM {lens/rights}
               WHERE patent_type = 'standard' AND filing_fy BETWEEN 2017 AND 2026 AND main_area IS NOT NULL
               GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 12""")
    same(d.n.iloc[0], 35626, "medical technology patents")
    views.append(
        {
            "label": "Standard patents",
            "subtitle": "Standard patents filed FY2017 to FY2026, by WIPO technology field",
            "x": {"type": "category", "values": [c.split("_", 1)[1].replace("_", " ").capitalize() for c in d.c]},
            "series": [{"name": "Standard patents", "data": col(d, "n")}],
        }
    )
    for t, name, label in [
        ("trade_mark", "Trade marks", "main Nice class"),
        ("design", "Designs", "main Locarno class"),
    ]:
        d = sql(f"""SELECT main_class AS c, count(*) AS n FROM {{lens/rights}}
                    WHERE ip_right_type = '{t}' AND filing_fy BETWEEN 2017 AND 2026 AND main_class IS NOT NULL
                    GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 12""")
        if t == "trade_mark":
            same(d.n.iloc[0], 97146, "class 35 trade marks")
        views.append(
            {
                "label": name,
                "subtitle": f"{name} filed FY2017 to FY2026, by {label}",
                "x": {"type": "category", "values": [f"{style.class_name(t, c)} ({int(c)})" for c in d.c]},
                "series": [{"name": name, "data": col(d, "n")}],
            }
        )
    d = sql("""SELECT main_class AS c, count(*) AS n FROM {lens/rights} WHERE ip_right_type = 'pbr' AND main_class
        IS NOT NULL
               GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 12""")
    views.append(
        {
            "label": "Plant breeder's rights",
            "subtitle": "Plant breeder's rights, all years, by plant genus",
            "x": {"type": "category", "values": [c.capitalize() for c in d.c]},
            "series": [{"name": "Plant breeder's rights", "data": col(d, "n")}],
        }
    )
    return {
        "type": "bar",
        "horizontal": True,
        "title": "What is protected: the largest fields and classes",
        "y": {"name": "Rights", "min": 0, "format": "int"},
        "views": views,
        "source": "IP Australia, IP RAPID (lens: rights). Class headings shortened from WIPO's.",
    }


@chart
def U17() -> dict:
    d = sql("""
        SELECT filing_fy AS y, coalesce(patent_type, ip_right_type) AS t, 100 * avg(holder_changed::int) AS v
        FROM {lens/rights} WHERE filing_fy BETWEEN 1980 AND 2026 GROUP BY ALL
    """)
    p = pivot(d, "y", "t", "v").reindex(range(1980, 2027))
    dec = sql("""SELECT 100 * avg(holder_changed::int) AS v FROM {lens/rights}
                 WHERE patent_type = 'standard' AND filing_fy BETWEEN 2000 AND 2009""").v[0]
    same(dec, 22.0, "standard patents of the 2000s with a changed holder")
    return {
        "type": "line",
        "title": "Rights now held by someone other than the filer",
        "subtitle": "% of each financial year's applications, FY1980 to FY2026",
        "x": {"type": "category", "values": fy(p.index)},
        "y": {"name": "% held by someone else", "min": 0, "format": "pct", "digits": 1},
        "series": [{"name": TYPES[t], "data": col(p, t, 1)} for t in TYPES],
        "marks": {"x": [{"at": "FY2003", "label": "Patent history starts"}]},
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/party). Compared by party id.",
        "note": "Patents filed before FY2003 have no holder history, so their lines start there. Newer rights have had "
        "less time to change hands.",
    }


@chart
def U21() -> dict:
    d = sql("""
        SELECT agent_name AS a, count(*) AS n FROM {lens/rights}
        WHERE patent_type = 'standard' AND filing_fy BETWEEN 2017 AND 2026 AND representation = 'attorney'
        GROUP BY 1 ORDER BY 2 DESC, 1
    """)
    total = d.n.sum()
    named = d[d.a.notna()].head(12)
    same(named.n.iloc[0], 64343, "Spruson & Ferguson's standard patents")
    same(100 * named.n.iloc[0] / total, 21.6, "Spruson & Ferguson's share")
    fix = {"fb rice": "FB Rice", "aj park": "AJ Park", "ipa pty ltd": "IPA Pty Ltd"}

    def nice(s: str) -> str:
        return fix.get(s, " ".join(w if w in {"&", "of", "and"} else w.capitalize() for w in s.split()))

    return {
        "type": "bar",
        "horizontal": True,
        "title": "Standard patents filed through an attorney, by firm",
        "subtitle": "% of standard patents filed FY2017 to FY2026 through an attorney: the 12 largest firms",
        "x": {"type": "category", "values": [nice(a) for a in named.a]},
        "y": {"name": "% of attorney-filed standard patents", "min": 0, "format": "pct", "digits": 1},
        "series": [{"name": "Share", "data": [r(100 * n / total, 1) for n in named.n]}],
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/party). Firm names as recorded.",
        "note": "Some firms belong to the same corporate group, which the register does not record.",
    }


# ------------------------------------------------------------------------------------------------------------ events


@chart
def U31() -> dict:
    d = sql("""
        SELECT strftime(date_trunc('month', retired_date), '%Y-%m') AS m, ip_right_type AS t, count(*) AS n
        FROM {lens/rights}
        WHERE status IN ('ceased', 'expired', 'terminated') AND retired_date BETWEEN DATE '2025-07-01' AND DATE
            '2026-09-30'
          AND ip_right_type IN ('trade_mark', 'design', 'patent')
        GROUP BY ALL ORDER BY 1
    """)
    p = pivot(d, "m", "t", "n").fillna(0)
    months = pd.period_range("2025-07", "2026-09", freq="M").strftime("%Y-%m")
    p = p.reindex(months).fillna(0)
    same(p.loc["2026-03", "trade_mark"], 3213, "trade marks ended in March 2026")
    same(p.loc["2026-05", "trade_mark"], 0, "trade marks ended in May 2026")
    return {
        "type": "line",
        "title": "Recorded ends per month, mid-2025 to September 2026",
        "subtitle": "Trade marks' and designs' ends stop being recorded after March 2026: the six-month grace period",
        "x": {"type": "category", "values": [pd.Timestamp(f"{m}-01").strftime("%b %Y") for m in p.index]},
        "y": {"name": "Rights that ceased, expired or terminated", "min": 0, "format": "int"},
        "series": [
            {"name": "Trade marks", "data": col(p, "trade_mark", 0)},
            {"name": "Patents", "data": col(p, "patent", 0)},
            {"name": "Designs", "data": col(p, "design", 0)},
        ],
        "marks": {"x": [{"at": "Mar 2026", "label": "Observed to 31 March"}]},
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/events)",
    }


MILESTONES = {
    "exam_requested_date": "Examination requested",
    "accepted_date": "Accepted",
    "certified_date": "Certified",
    "opposed_date": "Opposed",
    "first_assigned_date": "Assigned",
}


@chart
def U32() -> dict:
    d = sql(f"""
        SELECT coalesce(patent_type, ip_right_type) AS t, filing_fy AS y,
               {", ".join(f"100 * avg(({c} IS NOT NULL)::int) AS {c}" for c in MILESTONES)}
        FROM {{lens/rights}} WHERE filing_fy BETWEEN 1975 AND 2026 AND coalesce(patent_type, '') <> 'provisional'
        GROUP BY ALL
    """)
    dec = d.assign(dec=d.y // 10 * 10).groupby(["t", "dec"])[list(MILESTONES)].mean()
    same(dec.loc[("standard", 1980), "exam_requested_date"], 54.21, "standard patents with a request, 1980s")
    same(dec.loc[("trade_mark", 1980), "accepted_date"], 30.88, "trade marks accepted, 1980s")
    years = list(range(1975, 2027))
    views = []
    for t in ["standard", "trade_mark", "design", "second_tier"]:
        g = d[d.t == t].set_index("y").reindex(years)
        series = [{"name": name, "data": col(g, c, 1)} for c, name in MILESTONES.items() if g[c].max() >= 0.5]
        views.append(
            {
                "label": TYPES[t],
                "subtitle": f"{TYPES[t]}: % of each financial year's applications with each milestone recorded",
                "series": series,
            }
        )
    return {
        "type": "line",
        "title": "When each milestone starts being recorded",
        "x": {"type": "category", "values": fy(years)},
        "y": {"name": "% of the year's applications", "min": 0, "max": 100, "format": "pct", "digits": 1},
        "views": views,
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/events). Standing events only.",
    }


@chart
def U33() -> dict:
    d = sql("""
        SELECT filing_fy AS y,
            median(date_diff('day', application_date, exam_requested_date)) FILTER (patent_type = 'standard') AS a,
            median(date_diff('day', exam_requested_date, accepted_date)) FILTER (patent_type = 'standard') AS b,
            median(date_diff('day', application_date, accepted_date)) FILTER (ip_right_type = 'trade_mark') AS c
        FROM {lens/rights} WHERE filing_fy BETWEEN 1990 AND 2021 GROUP BY 1 ORDER BY 1
    """).set_index("y")
    same(d.b[2006], 755, "request to acceptance FY2006")
    same(d.a[2013], 44, "filing to request FY2013")
    return {
        "type": "line",
        "title": "The time between milestones",
        "subtitle": "Median days, by financial year of filing, among rights that reached each step",
        "x": {"type": "category", "values": fy(d.index)},
        "y": {"name": "Median days", "min": 0, "format": "int"},
        "series": [
            {"name": "Standard patents: filing to examination request", "data": col(d, "a", 0)},
            {"name": "Standard patents: request to acceptance", "data": col(d, "b", 0)},
            {"name": "Trade marks: filing to acceptance", "data": col(d, "c", 0)},
        ],
        "marks": {"x": [{"at": "FY2013", "label": "Raising the Bar"}]},
        "source": "IP Australia, IP RAPID (lens: rights). Later years still in progress are left out.",
    }


@chart
def U34() -> dict:
    eo = sql("""
        SELECT filing_fy AS y, coalesce(patent_type, ip_right_type) AS t, 100 * avg(exam_expedited::int) AS e
        FROM {lens/rights} WHERE filing_fy BETWEEN 1990 AND 2026
          AND coalesce(patent_type, ip_right_type) IN ('standard', 'trade_mark', 'design') GROUP BY ALL
    """)
    p = pivot(eo, "y", "t", "e").reindex(range(1990, 2027))
    same(p.loc[2026, "standard"], 10.31, "expedited standard patents FY2026")
    m = sql("""
        SELECT strftime(event_effective_date, '%Y-%m') AS m, count(*) AS n FROM {iprapid/events}
        WHERE ip_right_type = 'trade_mark' AND event_category = 'exam_request_expedite'
          AND event_effective_date BETWEEN DATE '2017-01-01' AND DATE '2020-12-31' GROUP BY 1 ORDER BY 1
    """).set_index("m")
    same(m.n["2018-11"], 604, "trade mark expedite requests November 2018")
    return {
        "type": "line",
        "title": "Asking for faster examination",
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/events)",
        "views": [
            {
                "label": "By year of filing",
                "subtitle": "% of applications whose examination was expedited, by financial year",
                "x": {"type": "category", "values": fy(p.index)},
                "y": {"name": "% expedited", "min": 0, "format": "pct", "digits": 2},
                "series": [{"name": TYPES[t], "data": col(p, t, 2)} for t in ["standard", "trade_mark", "design"]],
            },
            {
                "label": "Trade mark requests per month",
                "subtitle": "Trade mark expedite requests per month, 2017 to 2020",
                "x": {"type": "category", "values": [pd.Timestamp(f"{x}-01").strftime("%b %Y") for x in m.index]},
                "y": {"name": "Requests", "min": 0, "format": "int"},
                "series": [{"name": "Requests", "data": col(m, "n")}],
                "marks": {"x": [{"at": "Nov 2018", "label": "Records moved"}]},
            },
        ],
    }


@chart
def U35() -> dict:
    g = sql("""
        SELECT filing_fy AS y, 100 * avg((assignment_count > 0)::int) AS assigned, 100 * avg(holder_changed::int)
            AS changed
        FROM {lens/rights} WHERE patent_type = 'standard' AND filing_fy BETWEEN 1985 AND 2020 GROUP BY 1 ORDER BY 1
    """).set_index("y")
    same(g.assigned[2002], 15.4, "assigned FY2002")
    same(g.assigned[2003], 16.41, "assigned FY2003")
    return {
        "type": "line",
        "title": "Standard patents that changed hands",
        "subtitle": "By financial year of filing: with a recorded assignment, and held by someone other than the filer",
        "x": {"type": "category", "values": fy(g.index)},
        "y": {"name": "% of standard patents", "min": 0, "format": "pct", "digits": 2},
        "series": [
            {"name": "With an assignment", "data": col(g, "assigned", 2)},
            {"name": "Holder differs from the filer (from FY2003)", "data": col(g, "changed", 2)},
        ],
        "marks": {"x": [{"at": "FY2003", "label": "Holder history starts"}]},
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/events, iprapid/party)",
    }


@chart
def U36() -> dict:
    from eda import univariate as uni

    life = sql("""
        WITH c AS (
            SELECT coalesce(patent_type, ip_right_type) AS t,
                   year(CASE WHEN ip_right_type = 'patent' THEN date_of_patent WHEN ip_right_type = 'pbr'
                             THEN registered_date ELSE earliest_filed_date END) AS y,
                   floor(years_in_force * 12) / 12 AS years, in_force
            FROM {lens/rights} WHERE in_force IS NOT NULL
        )
        SELECT t, CASE WHEN t = 'second_tier' THEN (CASE WHEN y <= 2000 THEN 'Petty (to 2001)' ELSE 'Innovation' END)
                       WHEN t = 'trade_mark' AND y < 1990 THEN '1983 to 1989'
                       WHEN t = 'design' AND y < 1990 THEN '1986 to 1989'
                       ELSE ((y // 10) * 10)::VARCHAR || 's' END AS cohort,
               years, count(*) FILTER (NOT in_force) AS ended, count(*) FILTER (in_force) AS unfinished
        FROM c
        WHERE (t IN ('standard', 'second_tier') AND y >= 1980) OR (t = 'trade_mark' AND y >= 1983)
           OR (t = 'design' AND y >= 1986) OR t = 'pbr'
        GROUP BY ALL
    """)
    life["group"] = life.t + ": " + life.cohort
    curves = uni.kaplan_meier(life, time="years", by="group")
    at = uni.survival_at(curves, [10], by="group", time="years").mul(100)
    same(at.loc["standard: 1980s", 10], 54.3, "standard patents of the 1980s in force after 10 years")
    same(at.loc["trade_mark: 2000s", 10], 46.9, "trade marks of the 2000s in force after 10 years")
    views = []
    for t in ["standard", "trade_mark", "design", "second_tier", "pbr"]:
        series = []
        for g, d in curves[curves.group.str.startswith(t + ":")].groupby("group"):
            d = d[d.at_risk >= 30].sort_values("years")
            d = d[(d.years * 4) % 1 == 0]  # quarter-year steps keep the file small
            if (d.survival == 0).any():  # stop at the first point where none is left
                d = d.loc[: d.index[d.survival.to_numpy() == 0][0]]
            series.append(
                {
                    "name": g.split(": ", 1)[1],
                    "step": True,
                    "data": [[r(x, 2), r(100 * s, 1)] for x, s in zip(d.years, d.survival, strict=True)],
                }
            )
        views.append(
            {
                "label": TYPES[t],
                "subtitle": f"{TYPES[t]}: % still in force, by years since the term began, for "
                "each cohort (rights still in force count as unfinished)",
                "series": series,
            }
        )
    return {
        "type": "line",
        "title": "How long rights stay in force",
        "x": {"name": "Years since the term began", "type": "value", "min": 0, "format": "num", "digits": 1},
        "y": {"name": "% still in force", "min": 0, "max": 100, "format": "pct", "digits": 1},
        "tipHead": "After {x} years",
        "views": views,
        "source": "IP Australia, IP RAPID (lens: rights). Kaplan–Meier survival curves; each stops where fewer than 30 "
        "rights remain.",
    }


@chart
def U37() -> dict:
    e = sql("""SELECT year(term_extended_date) AS y, count(*) AS n FROM {lens/rights}
               WHERE term_extended_date IS NOT NULL GROUP BY 1 ORDER BY 1""").set_index("y")
    same(e.n[1999], 108, "extensions in 1999")
    same(e.n[2000], 114, "extensions in 2000")
    e = e.reindex(range(int(e.index.min()), int(e.index.max()) + 1)).fillna(0)
    return {
        "type": "bar",
        "title": "Extensions of term granted to standard patents",
        "subtitle": "By calendar year (pharmaceutical substances)",
        "x": {"type": "category", "values": [str(y) for y in e.index]},
        "y": {"name": "Extensions granted", "min": 0, "format": "int"},
        "series": [{"name": "Extensions", "data": col(e, "n")}],
        "labels": False,
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/events)",
    }


@chart
def U38() -> dict:
    tm = sql("""
        WITH e AS (
            SELECT DISTINCT application_number, event_category AS c, event_effective_date AS d FROM {iprapid/events}
            WHERE ip_right_type = 'trade_mark' AND event_category IN ('ceased', 'lapsed')
              AND year(event_effective_date) BETWEEN 1998 AND 2006
        )
        SELECT c, year(d) AS year,
               CASE WHEN c = 'lapsed' THEN (CASE WHEN year(r.application_date) IN (1999, 2000, 2001)
                                                 THEN 'Filed ' || year(r.application_date)::VARCHAR
                                                 ELSE 'Filed in other years' END)
                    ELSE CASE round(date_diff('day', r.earliest_filed_date, d) / 365.25)
                        WHEN 7 THEN 'At 7 years (first term, 1955 Act)'
                        WHEN 10 THEN 'At 10 years (first term, 1995 Act)'
                        ELSE 'Other ages (later renewals)' END END AS age,
               count(*) AS n
        FROM e JOIN {lens/rights} r ON r.ip_right_type = 'trade_mark' AND r.application_number = e.application_number
        GROUP BY ALL
    """)
    ce = tm[tm.c == "ceased"].pivot_table(index="year", columns="age", values="n", fill_value=0)
    la = tm[tm.c == "lapsed"].pivot_table(index="year", columns="age", values="n", fill_value=0)
    same(ce.loc[2000, "At 7 years (first term, 1955 Act)"], 4045, "7-year cessations in 2000")
    same(la.loc[2002, "Filed 2000"], 10247, "2002's lapses filed in 2000")
    years = [str(y) for y in ce.index]
    return {
        "type": "bar",
        "stack": True,
        "title": "Trade marks: why cessations fell and lapses rose in 2002",
        "x": {"type": "category", "values": years, "name": "Calendar year of the event"},
        "y": {"name": "Trade marks", "min": 0, "format": "int"},
        "source": "IP Australia, IP RAPID (iprapid/events; lens: rights). Each event once per mark and day.",
        "views": [
            {
                "label": "Cessations, by age",
                "subtitle": "Trade mark cessations, by the mark's age when it ceased",
                "series": [
                    {"name": c, "data": col(ce, c)}
                    for c in [
                        "At 7 years (first term, 1955 Act)",
                        "At 10 years (first term, 1995 Act)",
                        "Other ages (later renewals)",
                    ]
                ],
            },
            {
                "label": "Lapses, by year filed",
                "subtitle": "Trade mark lapses, by the year the mark was filed",
                "series": [
                    {"name": c, "data": col(la.reindex(ce.index).fillna(0), c)}
                    for c in ["Filed 1999", "Filed 2000", "Filed 2001", "Filed in other years"]
                ],
            },
        ],
    }


@chart
def U39() -> dict:
    a = sql("""
        WITH e AS (
            SELECT DISTINCT application_number, event_effective_date AS d FROM {iprapid/events}
            WHERE ip_right_type = 'design' AND event_category = 'lapsed' AND year(event_effective_date) BETWEEN
                1996 AND 2002
        )
        SELECT month(d) AS m, count(*) AS lapses, count(DISTINCT d) AS days FROM e GROUP BY 1 ORDER BY 1
    """).set_index("m")
    same(a.lapses[4], 101, "April lapses")
    same(a.days[4], 32, "April days with a lapse")
    months = [pd.Timestamp(2000, m, 1).strftime("%B") for m in a.index]
    return {
        "type": "bar",
        "title": "Design lapses by month of the year, 1996 to 2002 together",
        "x": {"type": "category", "values": months},
        "source": "IP Australia, IP RAPID (iprapid/events; lens: rights)",
        "views": [
            {
                "label": "Lapses",
                "subtitle": "Design lapses dated in each month, seven years pooled",
                "y": {"name": "Lapses", "min": 0, "format": "int"},
                "series": [{"name": "Lapses", "data": col(a, "lapses")}],
            },
            {
                "label": "Days with a lapse",
                "subtitle": "The number of different days each month's lapses are dated on",
                "y": {"name": "Days", "min": 0, "format": "int"},
                "series": [{"name": "Days with a lapse", "data": col(a, "days")}],
            },
        ],
    }


# ------------------------------------------------------------------------------------------------------------ links


@chart
def U89() -> dict:
    w = sql("""
        WITH r AS (
            SELECT year(application_date) AS year,
                   count(*) FILTER (filing_route = 'pct') AS pct,
                   count(*) FILTER (filing_route <> 'pct' AND patent_type = 'standard') AS other
            FROM {lens/rights} WHERE patent_type IN ('standard', 'second_tier') GROUP BY 1),
        w AS (
            SELECT year, sum(value) FILTER (indicator_id = 12) AS wpct, sum(value) FILTER (indicator_id = 11) AS wdirect
            FROM {wipo_ipstats/office_origin} WHERE office_code = 'AU' AND indicator_id IN (11, 12) GROUP BY 1)
        SELECT * FROM r JOIN w USING (year) WHERE year BETWEEN 1995 AND 2024 ORDER BY year
    """).set_index("year")
    ratio = w.pct / w.wpct
    same(ratio.median(), 1.001, "median PCT ratio")
    same(ratio.min(), 0.981, "lowest PCT ratio")
    return {
        "type": "line",
        "title": "Patent applications by route: the register against WIPO",
        "subtitle": "By calendar year, 1995 to 2024",
        "x": {"type": "category", "values": [str(y) for y in w.index]},
        "y": {"name": "Applications", "min": 0, "format": "int"},
        "series": [
            {"name": "IP RAPID: through the PCT", "data": col(w, "pct")},
            {"name": "WIPO: PCT entries at IP Australia", "data": col(w, "wpct"), "line": "dashed"},
            {"name": "IP RAPID: other standard patents", "data": col(w, "other")},
            {"name": "WIPO: direct applications", "data": col(w, "wdirect"), "line": "dashed"},
        ],
        "source": "IP Australia, IP RAPID (lens: rights); WIPO IP Statistics, indicators 1a and 1b",
        "note": "Each solid line and the dashed line beside it count the same thing from two sources; they "
        "nearly overlap.",
    }


ROUTES = {
    "pct": "PCT",
    "divisional": "Divisional",
    "convention": "Priority abroad",
    "australian_priority": "Australian priority",
    "madrid": "Madrid",
    "direct": "Direct",
}


@chart
def U90() -> dict:
    d = sql("""
        SELECT coalesce(patent_type, ip_right_type) AS t,
               CASE WHEN australian_applicant THEN 'Australian' ELSE 'overseas' END AS o,
               filing_fy AS y, filing_route AS route, count(*) AS n
        FROM {lens/rights}
        WHERE filing_fy BETWEEN 1985 AND 2026 AND filing_route IS NOT NULL AND australian_applicant IS NOT NULL
        GROUP BY ALL
    """)
    d["share"] = 100 * d.n / d.groupby(["t", "o", "y"]).n.transform("sum")
    sh = d.set_index(["t", "o", "y", "route"]).share
    same(sh["standard", "overseas", 2010, "pct"], 81.0, "overseas PCT share FY2010")
    same(sh["standard", "Australian", 2026, "direct"], 28.3, "Australian direct filing FY2026")
    years = list(range(1985, 2027))
    views = []
    for t, o, label in [
        ("standard", "overseas", "Standard patents, overseas"),
        ("standard", "Australian", "Standard patents, Australian"),
        ("trade_mark", "overseas", "Trade marks, overseas"),
        ("design", "overseas", "Designs, overseas"),
    ]:
        g = d[(d.t == t) & (d.o == o)].pivot_table(index="y", columns="route", values="share").reindex(years)
        views.append(
            {
                "label": label,
                "subtitle": f"{label}: % of each financial year's applications, by route",
                "series": [{"name": n, "data": col(g, k, 1)} for k, n in ROUTES.items() if k in g],
            }
        )
    return {
        "type": "bar",
        "stack": True,
        "title": "How rights came to Australia",
        "x": {"type": "category", "values": fy(years)},
        "y": {"name": "% of the year's applications", "min": 0, "max": 100, "format": "pct", "digits": 1},
        "views": views,
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/links). Origin known only.",
    }


@chart
def U91() -> dict:
    d = sql("""
        SELECT priority_office AS o, count(*) AS n FROM {lens/rights}
        WHERE patent_type = 'standard' AND filing_fy BETWEEN 2017 AND 2026 AND priority_claims > 0 AND NOT
            australian_applicant
        GROUP BY 1 ORDER BY 2 DESC, 1
    """)
    tot = d.n.sum()
    same(100 * d.n.iloc[0] / tot, 53.42, "US share of overseas priorities")
    top = d[d.o.notna()].head(8)
    names = {"ep": "European Patent Office", "wo": "WIPO (international)"}
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Where overseas inventions patented in Australia were first filed",
        "subtitle": "Office of the earliest priority, standard patents filed FY2017 to FY2026 from overseas",
        "x": {
            "type": "category",
            "values": [names.get(o, country(o)) for o in top.o] + ["All other offices, or unknown"],
        },
        "y": {"name": "% of those with a priority", "min": 0, "format": "pct", "digits": 2},
        "series": [
            {"name": "Share", "data": [r(100 * n / tot, 2) for n in top.n] + [r(100 * (tot - top.n.sum()) / tot, 2)]}
        ],
        "source": "IP Australia, IP RAPID (lens: rights; iprapid/links). Office read from the priority number.",
    }


# ------------------------------------------------------------------------------------------------------------ Google Pa


REACH = """FROM {lens/rights} WHERE patent_type = 'standard' AND filing_fy BETWEEN 2010 AND 2019 AND family_id IS
    NOT NULL
           AND australian_applicant IS NOT NULL"""
ORIGIN2 = "CASE WHEN australian_applicant THEN 'Australian applicants' ELSE 'Overseas applicants' END"


@chart
def U93() -> dict:
    d = sql(f"SELECT {ORIGIN2} AS o, least(family_offices, 15) AS k, count(*) AS n {REACH} GROUP BY ALL")
    med = sql(f"SELECT {ORIGIN2} AS o, median(family_offices) AS m {REACH} GROUP BY 1").set_index("o").m
    same(med["Overseas applicants"], 6, "overseas median offices")
    same(med["Australian applicants"], 2, "Australian median offices")
    p = pivot(d, "k", "o", "n").fillna(0)
    p = 100 * p / p.sum()
    return {
        "type": "bar",
        "title": "How many offices each patent's family reaches",
        "subtitle": "Standard patents filed FY2010 to FY2019: % of each group's patents by the number of offices "
        "(15 = 15 or more)",
        "x": {"type": "category", "values": [f"{int(k)}{'+' if k == 15 else ''}" for k in p.index], "name": "Offices"},
        "y": {"name": "% of patents", "min": 0, "format": "pct", "digits": 1},
        "series": [{"name": c, "data": col(p, c, 1)} for c in ["Australian applicants", "Overseas applicants"]],
        "source": "Google Patents Public Data, joined to IP RAPID (lens: rights)",
    }


@chart
def U94() -> dict:
    d = sql(f"""SELECT {ORIGIN2} AS o, least(family_citations_5y, 30) AS k, count(*) AS n {REACH}
                AND family_citations_5y IS NOT NULL GROUP BY ALL""")
    p = pivot(d, "k", "o", "n").fillna(0)
    p = 100 * p / p.sum()
    same(p.loc[0, "Australian applicants"], 43.99, "Australians never cited")
    same(p.loc[0, "Overseas applicants"], 13.29, "overseas never cited")
    return {
        "type": "bar",
        "title": "How often later inventions cite each patent",
        "subtitle": "Standard patents filed FY2010 to FY2019: % of each group's patents by the number of "
        "families citing "
        "them within five years (30 = 30 or more)",
        "x": {
            "type": "category",
            "values": [f"{int(k)}{'+' if k == 30 else ''}" for k in p.index],
            "name": "Citing families",
        },
        "y": {"name": "% of patents", "min": 0, "format": "pct", "digits": 2},
        "series": [{"name": c, "data": col(p, c, 2)} for c in ["Australian applicants", "Overseas applicants"]],
        "source": "Google Patents Public Data, joined to IP RAPID (lens: rights)",
        "note": "The long tail beyond 30 is grouped into the last bar.",
    }


# ------------------------------------------------------------------------------------------------------------ inventors


@chart
def U95() -> dict:
    d = sql("""
        SELECT CASE WHEN founding_australian THEN 'Australian filers' ELSE 'Overseas filers' END AS f,
               (filing_fy // 10) * 10 AS dec, 100 * avg((invented_in_australia IS NOT NULL)::int) AS known
        FROM {lens/rights}
        WHERE patent_type = 'standard' AND filing_fy BETWEEN 1990 AND 2026 AND founding_australian IS NOT NULL
        GROUP BY ALL
    """)
    p = pivot(d, "dec", "f", "known")
    same(p.loc[2010, "Australian filers"], 56.98, "Australian filers' country known, 2010s")
    return {
        "type": "bar",
        "title": "Standard patents with an inventor's country known",
        "subtitle": "% of standard patents, by decade of filing and who filed them",
        "x": {"type": "category", "values": [f"{int(x)}s" for x in p.index]},
        "y": {"name": "% with an inventor's country", "min": 0, "max": 100, "format": "pct", "digits": 2},
        "series": [{"name": c, "data": col(p, c, 2)} for c in ["Australian filers", "Overseas filers"]],
        "source": "Google Patents Public Data, joined to IP RAPID (lens: rights)",
    }


@chart
def U96() -> dict:
    o = sql("""
        SELECT filing_fy AS y,
               count(*) FILTER (invented_in_australia AND NOT founding_australian) AS overseas,
               count(*) FILTER (invented_in_australia AND founding_australian) AS au
        FROM {lens/rights} WHERE patent_type = 'standard' AND filing_fy BETWEEN 1990 AND 2026
          AND invented_in_australia IS NOT NULL GROUP BY 1 ORDER BY 1
    """).set_index("y")
    same(o.overseas[2010], 222, "overseas-filed with an Australian inventor FY2010")
    return {
        "type": "line",
        "title": "Standard patents with an inventor in Australia",
        "subtitle": "By who filed them and financial year of filing (patents whose inventors' countries are known)",
        "x": {"type": "category", "values": fy(o.index)},
        "y": {"name": "Standard patents", "min": 0, "format": "int"},
        "series": [
            {"name": "Filed from Australia", "data": col(o, "au")},
            {"name": "Filed from overseas", "data": col(o, "overseas")},
        ],
        "source": "Google Patents Public Data (inventors), joined to IP RAPID (lens: rights)",
    }


@chart
def U97() -> dict:
    g = sql("""
        WITH est AS (
            SELECT i.country_code AS c, count(*) AS n, 100 * avg(i.p_female) AS est
            FROM {google_patents_inventors/inventors} i JOIN {google_patents/families} f USING (family_id)
            WHERE f.pct AND year(f.first_priority_date) BETWEEN 2015 AND 2022 GROUP BY 1),
        w AS (SELECT origin_code AS c, avg(value) AS wipo FROM {wipo_ipstats/pmh}
              WHERE indicator_id = 1042 AND year BETWEEN 2016 AND 2023 GROUP BY 1)
        SELECT * FROM est JOIN w USING (c) WHERE n >= 2000 ORDER BY n DESC
    """).set_index("c")
    same(g.est["AU"], 14.6, "Australia's estimate")
    same(g.wipo["AU"], 13.8, "WIPO's share for Australia")
    same((g.est - g.wipo).median(), 4.5, "median difference")
    au = sql("""
        WITH est AS (
            SELECT year(f.first_priority_date) + 1 AS y, 100 * avg(i.p_female) AS est
            FROM {google_patents_inventors/inventors} i JOIN {google_patents/families} f USING (family_id)
            WHERE f.pct AND i.country_code = 'AU' GROUP BY 1),
        w AS (SELECT year AS y, value AS wipo FROM {wipo_ipstats/pmh} WHERE indicator_id = 1042 AND origin_code = 'AU')
        SELECT * FROM est JOIN w USING (y) WHERE y BETWEEN 2001 AND 2024 ORDER BY y
    """).set_index("y")
    named = {"AU": "Australia", "CN": "China", "KR": "Korea"}

    def pts(keep):
        return [
            [r(w, 1), r(e, 1), country(c.lower())] for c, w, e in zip(g.index, g.wipo, g.est, strict=True) if keep(c)
        ]

    return {
        "title": "Gender estimated from names, against WIPO's published shares",
        "source": "Google Patents Public Data (inventors); WIPO World Gender-Name Dictionary; WIPO IP Statistics "
        "(PCT indicator 15)",
        "views": [
            {
                "label": "By country",
                "type": "scatter",
                "subtitle": "% of inventors who are women, 2016 to 2023: WIPO's figure (across) against the "
                "estimate from names "
                "(up). On the dashed line they agree.",
                "x": {
                    "name": "WIPO: women among PCT inventors (%)",
                    "type": "value",
                    "min": 5,
                    "max": 40,
                    "format": "pct",
                    "digits": 1,
                },
                "y": {"name": "Estimated from names (%)", "min": 5, "max": 40, "format": "pct", "digits": 1},
                "series": [
                    {"name": "Other countries", "data": pts(lambda c: c not in named), "colour": 0},
                    {
                        "name": "Australia, China and Korea",
                        "data": pts(lambda c: c in named),
                        "colour": 1,
                        "size": 11,
                        "labels": True,
                    },
                    {
                        "name": "Where they agree",
                        "kind": "line",
                        "data": [[5, 5], [40, 40]],
                        "line": "dashed",
                        "colour": "muted",
                    },
                ],
            },
            {
                "label": "Australia, by year",
                "type": "line",
                "subtitle": "Women among inventors in Australia: the estimate from names against WIPO's figure",
                "x": {"type": "category", "values": [str(y) for y in au.index]},
                "y": {"name": "% women", "min": 0, "format": "pct", "digits": 1},
                "series": [
                    {"name": "Estimated from names", "data": col(au, "est", 1)},
                    {"name": "WIPO", "data": col(au, "wipo", 1), "line": "dashed"},
                ],
            },
        ],
    }


# ------------------------------------------------------------------------------------------------------------ timeline


def timeline() -> pd.DataFrame:
    from eda import load_lens

    t = load_lens("timeline")
    return t.set_index("month")


def tl_label(c: str) -> str:
    from eda import style

    return style.label("timeline", c, unit=False).replace(" (events)", "")


def tl_series() -> list[str]:
    from eda import style

    t = timeline()
    return [c for c in t.columns if style.kind("timeline", c) == "count" and c != "days_in_month"]


@chart
def U22() -> dict:
    t = timeline()
    cols = tl_series()
    same(t.patents_standard_au.max(), 1018, "busiest month of Australian standard patents")
    same(t.patents_standard_au.idxmax().year, 2013, "busiest year")
    spans = []
    for c in cols:
        s = t[c].dropna()
        a, b = s.index.min(), s.index.max()
        spans.append((tl_label(c), round(a.year + (a.month - 1) / 12, 2), round(b.year + b.month / 12, 2)))
    spans.sort(key=lambda x: x[1])
    return {
        "type": "range",
        "title": "Where each monthly series can be read",
        "subtitle": "The span of each of the timeline's 28 series, after the repairs: earlier months are empty, "
        "not zero",
        "x": {"type": "category", "values": [s[0] for s in spans]},
        "y": {"name": "Year", "min": 1900, "max": 2030, "format": "year"},
        "series": [{"name": "Months with a value", "data": [[s[1], s[2]] for s in spans]}],
        "height": "tall",
        "source": "IP Australia, IP RAPID (lens: timeline)",
    }


@chart
def U23() -> dict:
    e = sql("""
        SELECT strftime(date_trunc('quarter', application_date), '%Y-%m') AS q, ip_right_type AS t,
               100 * avg((registered_date IS NULL)::int) AS never
        FROM {lens/rights}
        WHERE application_date BETWEEN DATE '1978-01-01' AND DATE '1990-12-31' AND ip_right_type IN ('trade_mark',
            'design')
        GROUP BY ALL
    """)
    p = pivot(e, "q", "t", "never")
    same(p.loc["1983-01", "trade_mark"], 52.0, "trade marks never registered, first quarter 1983")
    same(p.loc["1986-01", "design"], 26.3, "designs never registered, first quarter 1986")
    labels = [f"{q[:4]} Q{(int(q[5:]) - 1) // 3 + 1}" for q in p.index]
    return {
        "type": "line",
        "title": "Applications never registered, by quarter of filing",
        "subtitle": "A share near zero means the register holds only the survivors: applications that failed are "
        "missing",
        "x": {"type": "category", "values": labels},
        "y": {"name": "% never registered", "min": 0, "max": 70, "format": "pct", "digits": 1},
        "series": [
            {"name": "Trade marks", "data": col(p, "trade_mark", 1)},
            {"name": "Designs", "data": col(p, "design", 1)},
        ],
        "marks": {"x": [{"at": "1983 Q1", "label": "Trade marks start"}, {"at": "1986 Q1", "label": "Designs start"}]},
        "source": "IP Australia, IP RAPID (lens: rights). The timeline's series now start at the marked quarters.",
    }


@chart
def U24() -> dict:
    t = timeline().loc["2016-07-01":"2026-06-01"]
    rows = []
    for c in tl_series():
        s = t[c].dropna().astype(float)
        if len(s) and s.median() >= 10:
            rows.append((tl_label(c), s.std() / s.mean()))
    rows.sort(key=lambda x: x[1])
    v = dict(rows)
    same(v[tl_label("patents_standard_overseas")], 0.08, "overseas standard patents' variation")
    same(v[tl_label("patents_second_tier")], 1.82, "second-tier variation")
    return {
        "type": "bar",
        "horizontal": True,
        "title": "How much each monthly series moves",
        "subtitle": "Variation from month to month as a share of the average (standard deviation ÷ mean), FY2017 "
        "to FY2026; "
        "series with a median of 10 or more a month",
        "x": {"type": "category", "values": [x[0] for x in rows]},
        "y": {"name": "Relative variation", "min": 0, "format": "num", "digits": 2},
        "series": [{"name": "Relative variation", "data": [r(x[1], 2) for x in rows]}],
        "height": "tall",
        "source": "IP Australia, IP RAPID (lens: timeline)",
    }


APPS = {
    "standard": ["patents_standard_au", "patents_standard_overseas", "patents_standard_origin_unknown"],
    "provisional": ["patents_provisional"],
    "second_tier": ["patents_second_tier"],
    "trade_mark": ["trade_marks_au", "trade_marks_overseas", "trade_marks_origin_unknown"],
    "design": ["designs_au", "designs_overseas", "designs_origin_unknown"],
    "pbr": ["pbr_applications"],
}


@chart
def U25() -> dict:
    t = timeline()
    years = t.groupby(t.index.year)[sum(APPS.values(), [])].sum(min_count=12)
    std = years[APPS["standard"]].sum(axis=1, min_count=1)
    same(std[2021], 32399, "standard patents in 2021")
    same(std[2025], 30448, "standard patents in 2025")
    names = {"_au": "Australian", "_overseas": "Overseas", "_origin_unknown": "Origin unknown"}
    views = []
    for k, cols in APPS.items():
        y = years[cols].dropna(how="all")
        y = y.loc[:2025]
        series = []
        for c in cols:
            name = next((n for s, n in names.items() if c.endswith(s)), "Applications")
            series.append(
                {"name": name, "data": col(y, c, 0), **({"colour": "muted"} if name == "Origin unknown" else {})}
            )
        views.append(
            {
                "label": TYPES[k],
                "subtitle": f"{TYPES[k]}: applications per calendar year, from the series' start",
                "x": {"type": "category", "values": [str(i) for i in y.index]},
                "series": series,
            }
        )
    return {
        "type": "line",
        "title": "Applications per calendar year",
        "y": {"name": "Applications", "min": 0, "format": "int"},
        "views": views,
        "source": "IP Australia, IP RAPID (lens: timeline). Complete years only.",
    }


@chart
def U26() -> dict:
    from eda import univariate as uni

    t = timeline().reset_index()
    cols = [
        "patents_standard_au",
        "patents_standard_overseas",
        "trade_marks_au",
        "trade_marks_overseas",
        "designs_au",
        "designs_overseas",
        "patents_provisional",
    ]
    s = uni.seasonal_profile(t, cols, start="2010-01-01", end="2019-12-01")
    same(s.loc["patents_standard_au", 1], 75, "Australian standard patents in January")
    same(s.loc["patents_standard_overseas", 1], 95, "overseas standard patents in January")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    views = []
    for label, a, o in [
        ("Standard patents", "patents_standard_au", "patents_standard_overseas"),
        ("Trade marks", "trade_marks_au", "trade_marks_overseas"),
        ("Designs", "designs_au", "designs_overseas"),
    ]:
        views.append(
            {
                "label": label,
                "subtitle": f"{label}: each month as a % of an ordinary month (100), median of 2010 to 2019",
                "series": [
                    {"name": "Australian applicants", "data": [r(v, 0) for v in s.loc[a]]},
                    {"name": "Overseas applicants", "data": [r(v, 0) for v in s.loc[o]]},
                ],
            }
        )
    return {
        "type": "line",
        "title": "The typical month of the year",
        "x": {"type": "category", "values": months},
        "y": {"name": "% of an ordinary month", "min": 50, "max": 130, "format": "num", "digits": 0},
        "marks": {"y": [{"at": 100, "label": "An ordinary month"}]},
        "views": views,
        "source": "IP Australia, IP RAPID (lens: timeline)",
    }


@chart
def U27() -> dict:
    t = timeline()
    groups = {
        "Granted or registered": ["patents_granted", "trade_marks_registered", "designs_registered"],
        "Lapsed": ["patents_lapsed", "trade_marks_lapsed", "designs_lapsed"],
        "Ceased or expired": ["patents_ceased", "trade_marks_ceased", "designs_ceased", "patents_expired"],
        "Sold or opposed": [
            "patent_assignments",
            "trade_mark_assignments",
            "trade_mark_oppositions",
            "patent_oppositions",
        ],
    }
    years = t.groupby(t.index.year)[sum(groups.values(), [])].sum(min_count=12).loc[1984:2025]
    same(years.patents_granted[2016], 25687, "patent grants in 2016")
    same(years.trade_marks_ceased[2025], 35484, "trade mark cessations in 2025")
    return {
        "type": "line",
        "title": "What happened to rights each year",
        "x": {"type": "category", "values": [str(y) for y in years.index]},
        "y": {"name": "Events", "min": 0, "format": "int"},
        "views": [
            {
                "label": g,
                "subtitle": f"{g}: events per calendar year, from each series' start",
                "series": [{"name": tl_label(c), "data": col(years, c, 0)} for c in cs],
            }
            for g, cs in groups.items()
        ],
        "source": "IP Australia, IP RAPID (iprapid/events, each event once; lens: timeline)",
    }


POLICY_TARGETS = {
    "pct-accession": ["patents_standard_origin_unknown", "patents_standard_overseas"],
    "patents-act-1990": ["patents_granted", "patents_second_tier"],
    "pbr-act-1994": ["pbr_applications"],
    "patent-term-20-years": ["patents_expired"],
    "trade-marks-act-1995": ["trade_marks_registered", "trade_marks_au", "trade_mark_assignments"],
    "pharma-extension-of-term": ["patent_extensions_of_term"],
    "innovation-patent-introduced": ["patents_second_tier"],
    "madrid-protocol": ["trade_marks_overseas"],
    "designs-act-2003": ["designs_registered", "designs_overseas", "designs_au"],
    "raising-the-bar-enacted": ["patents_standard_overseas", "patents_standard_au"],
    "tobacco-plain-packaging": ["trade_marks_au", "trade_marks_overseas"],
    "raising-the-bar": ["patents_standard_overseas", "patents_standard_au", "patents_granted"],
    "pc-response-parallel-importation": ["patent_extensions_of_term"],
    "pc-response-part-1": ["trade_mark_oppositions"],
    "innovation-patent-phase-out-enacted": ["patents_second_tier"],
    "innovation-patent-closed": ["patents_second_tier"],
    "designs-grace-period": ["designs_au", "designs_overseas"],
}


@chart
def U28() -> dict:
    from eda import univariate as uni

    t = timeline()
    w = uni.event_windows(t.reset_index(), POLICY_TARGETS)
    same(
        w.loc[("raising-the-bar", "patents_standard_au"), "month of the change, × average before"],
        4.39,
        "Raising the Bar rush",
    )
    same(
        w.loc[("innovation-patent-closed", "patents_second_tier"), "% change in the average"],
        -95.9,
        "after the closure",
    )
    names = sql("SELECT id, event FROM {policy_events/events}").set_index("id").event
    marked = t.loc[t.policy_events.notna(), "policy_events"]
    when = {e: m for m, es in marked.items() for e in es.split(", ")}
    views = []
    for ev, cols in sorted(POLICY_TARGETS.items(), key=lambda kv: when[kv[0]]):
        m = when[ev]
        win = t.loc[m - pd.DateOffset(months=24) : m + pd.DateOffset(months=24), cols].astype(float)
        labels = [x.strftime("%b %Y") for x in win.index]
        views.append(
            {
                "label": f"{m:%b %Y}: {names[ev]}",
                "subtitle": f"{names[ev]} ({m:%B %Y}): the series it targets, 24 months either side",
                "x": {"type": "category", "values": labels},
                "series": [{"name": tl_label(c), "data": col(win, c, 0)} for c in cols],
                "marks": {"x": [{"at": f"{m:%b %Y}", "label": "The change"}]},
            }
        )
    return {
        "type": "line",
        "title": "The 17 policy changes, one at a time",
        "y": {"name": "Per month", "min": 0, "format": "int"},
        "views": views,
        "select": True,
        "source": "IP Australia, IP RAPID (lens: timeline); dates from policy_events, checked against the "
        "Federal Register",
        "note": "Months either side are shown as recorded; trends and seasons are not allowed for until Stage 2.",
    }


@chart
def U29() -> dict:
    t = timeline()
    same(t.loc["2015-07-01", "patent_assignments"], 1603, "patent assignments in July 2015")
    same(t.loc["1991-06-01", "patents_granted"], 113, "patent grants in June 1991")
    cases = [
        (
            "Patent grants, 1990 to 1992",
            "patents_granted",
            "1990-01-01",
            "1992-12-01",
            "1991-06-01",
            "Patents Act 1990 began",
        ),
        (
            "Trade mark registrations, 1995 to 1997",
            "trade_marks_registered",
            "1995-01-01",
            "1997-12-01",
            "1996-01-01",
            "Trade Marks Act 1995 began",
        ),
        (
            "Patent assignments, 2014 to 2016",
            "patent_assignments",
            "2014-01-01",
            "2016-12-01",
            "2015-07-01",
            "One large transfer",
        ),
    ]
    views = []
    for label, c, a, b, m, why in cases:
        s = t.loc[a:b, c].astype(float)
        views.append(
            {
                "label": label,
                "subtitle": f"{label}, per month",
                "x": {"type": "category", "values": [x.strftime("%b %Y") for x in s.index]},
                "series": [{"name": tl_label(c), "data": [r(v, 0) for v in s]}],
                "marks": {"x": [{"at": pd.Timestamp(m).strftime("%b %Y"), "label": why}]},
            }
        )
    return {
        "type": "bar",
        "title": "Three of the 42 unusual months, and what they are",
        "y": {"name": "Per month", "min": 0, "format": "int"},
        "labels": False,
        "views": views,
        "source": "IP Australia, IP RAPID (lens: timeline)",
    }


@chart
def U30() -> dict:
    t = timeline()
    cpi = t.cpi.dropna()
    same(len(cpi), 312, "quarters")
    same(cpi.iloc[-1], 102.31, "the June quarter 2026")
    ch = (100 * (cpi / cpi.shift(4) - 1)).dropna()
    return {
        "type": "line",
        "title": "Price rises over the year, by quarter",
        "subtitle": "% change in the consumer price index over four quarters, 1949 to June quarter 2026",
        "x": {"type": "category", "values": [f"{m:%b %Y}" for m in ch.index]},
        "y": {"name": "% change over four quarters", "format": "pct", "digits": 1},
        "series": [{"name": "Change over four quarters", "data": [r(v, 1) for v in ch], "area": True}],
        "marks": {"y": [{"at": 0, "label": ""}]},
        "source": "ABS, Consumer Price Index, all groups, eight capital cities (abs_prices; lens: timeline)",
    }


# ------------------------------------------------------------------------------------------------------------ regions


REMOTE = [
    "Major Cities of Australia",
    "Inner Regional Australia",
    "Outer Regional Australia",
    "Remote Australia",
    "Very Remote Australia",
]


def regions() -> pd.DataFrame:
    from eda import load_lens

    return load_lens("regions")


@chart
def U49() -> dict:
    from eda import build

    d = sql(f"""
        WITH a AS (SELECT postcode, count(*) AS abns FROM {{abr/abns}} GROUP BY 1),
        r AS (
            SELECT coalesce(patent_type, ip_right_type) AS t, founder_postcode AS pc,
                   {build.postcode_range("founder_postcode")} AS rng,
                   founder_postcode IN (SELECT poa_code FROM {{lens/regions}}) AS in_poa
            FROM {{lens/rights}}
            WHERE founder_postcode IS NOT NULL AND filing_fy BETWEEN 2017 AND 2026 AND ip_right_type <> 'pbr')
        SELECT t, CASE WHEN in_poa THEN 'A postal area'
                       WHEN rng = 'non_geographic' THEN 'Post office box or large-volume range'
                       WHEN rng = 'delivery' AND coalesce(a.abns, 0) > 0 THEN 'A real postcode with no residents'
                       ELSE 'Other or unknown' END AS c, count(*) AS n
        FROM r LEFT JOIN a ON a.postcode = r.pc GROUP BY ALL
    """)
    p = pivot(d, "t", "c", "n").fillna(0)
    pct = 100 * p.div(p.sum(axis=1), axis=0)
    same(pct.loc["standard", "A postal area"], 94.45, "standard patents in a postal area")
    same(
        pct.loc["standard", "A real postcode with no residents"],
        4.14,
        "standard patents at real codes with no residents",
    )
    order = ["standard", "provisional", "second_tier", "trade_mark", "design"]
    cls = [
        "A postal area",
        "A real postcode with no residents",
        "Post office box or large-volume range",
        "Other or unknown",
    ]
    return {
        "type": "bar",
        "horizontal": True,
        "stack": True,
        "title": "Can the filer's postcode be placed?",
        "subtitle": "Applications from Australia, FY2017 to FY2026, by what the filer's postcode is",
        "x": {"type": "category", "values": [TYPES[t] for t in order]},
        "y": {"name": "% of applications", "min": 0, "max": 100, "format": "pct", "digits": 2},
        "series": [
            {
                "name": c,
                "data": [r(pct.loc[t, c], 2) for t in order],
                **({"colour": "muted"} if c == "Other or unknown" else {}),
            }
            for c in cls
        ],
        "source": "IP RAPID; ABS postal areas; ABR; Australia Post's postcode ranges (lens: regions)",
    }


@chart
def U50() -> dict:
    g = regions()
    p = g.persons.astype(float)
    same(int((p < 1000).sum()), 818, "areas under 1,000 people")
    same(p.median(), 3508, "median people")
    edges = [0, 1, 100, 500, 1000, 2500, 5000, 10000, 20000, 50000, 1e9]
    labels = [
        "None",
        "1 to 99",
        "100 to 499",
        "500 to 999",
        "1,000 to 2,499",
        "2,500 to 4,999",
        "5,000 to 9,999",
        "10,000 to 19,999",
        "20,000 to 49,999",
        "50,000 or more",
    ]
    cnt = pd.cut(p, edges, right=False, labels=labels).value_counts().reindex(labels)
    return {
        "type": "bar",
        "title": "How many people each postal area has",
        "subtitle": "Postal areas by their number of residents (2021 Census geography)",
        "x": {"type": "category", "values": labels, "name": "People in the area"},
        "y": {"name": "Postal areas", "min": 0, "format": "int"},
        "series": [{"name": "Postal areas", "data": [int(v) for v in cnt]}],
        "source": "ABS, ASGS 2021 and Census 2021 (lens: regions)",
    }


@chart
def U51() -> dict:
    g = regions()
    geo = (
        g.groupby("remoteness")
        .agg(a=("poa_code", "size"), p=("persons", "sum"), b=("active_gst_abns", "sum"))
        .loc[REMOTE]
    )
    pct = 100 * geo / geo.sum()
    same(pct.loc["Major Cities of Australia", "a"], 37.7, "areas in major cities")
    same(pct.loc["Major Cities of Australia", "p"], 72.8, "people in major cities")
    return {
        "type": "bar",
        "title": "Areas, people and businesses by remoteness",
        "x": {"type": "category", "values": [x.replace(" of Australia", "").replace(" Australia", "") for x in REMOTE]},
        "y": {"name": "% of the national total", "min": 0, "format": "pct", "digits": 1},
        "series": [
            {"name": "Postal areas", "data": col(pct, "a", 1)},
            {"name": "People", "data": col(pct, "p", 1)},
            {"name": "Businesses", "data": col(pct, "b", 1)},
        ],
        "source": "ABS remoteness areas and Census 2021; ABR (lens: regions)",
    }


@chart
def U52() -> dict:
    g = regions().sort_values("poa_code")
    series = []
    for c, name, quoted in [
        ("patents_standard", "Standard patents", 72.5),
        ("trade_marks", "Trade marks", 60.8),
        ("designs", "Designs", 75.4),
    ]:
        v = g[c].astype(float)
        ranked = v.sort_values(ascending=False, kind="stable")
        curve = [[0, 0]]
        for pt in LORENZ_GRID:
            k = max(1, round(pt / 100 * len(v)))
            curve.append([pt, r(100 * ranked.iloc[:k].sum() / v.sum(), 2)])
        same(100 * ranked.iloc[:264].sum() / v.sum(), quoted, f"top tenth's share, {name}")
        series.append({"name": name, "data": curve})
        if c == "patents_standard":
            people = [[0, 0]] + [
                [
                    pt,
                    r(
                        100
                        * g.loc[ranked.index[: max(1, round(pt / 100 * len(v)))], "persons"].sum()
                        / g.persons.sum(),
                        2,
                    ),
                ]
                for pt in LORENZ_GRID
            ]
            same(100 * g.loc[ranked.index[:264], "persons"].sum() / g.persons.sum(), 29.2, "people in the top tenth")
    series.append(
        {
            "name": "People in the same areas (ranked by standard patents)",
            "data": people,
            "line": "dashed",
            "colour": "ink",
        }
    )
    return {
        "type": "line",
        "title": "How concentrated filing is across places",
        "subtitle": "Postal areas lined up from the most applications to the fewest (FY2017 to FY2026): the "
        "share filed by "
        "the top x% of areas, and the share of people who live in the top areas for standard patents",
        "x": {"name": "Top % of postal areas", "type": "value", "min": 0, "max": 100, "format": "pct"},
        "y": {"name": "% of the national total", "min": 0, "max": 100, "format": "pct"},
        "series": series,
        "marks": {"x": [{"at": 10, "label": "Top tenth"}]},
        "table_points": [1, 5, 10, 25, 50],
        "source": "IP RAPID; ABS Census 2021 (lens: regions). At the filer's postcode.",
        "note": "The observation quotes the top tenth. The rest of each curve is drawn from the same table for "
        "context.",
    }


def log_range(values) -> tuple[float, float]:
    v = [x for x in values if x and x > 0]
    return 10 ** math.floor(math.log10(min(v))), 10 ** math.ceil(math.log10(max(v)))


def funnel_view(
    count: pd.Series, people: pd.Series, labels: pd.Series, name: str, quoted: tuple[float, float] | None
) -> dict:
    from eda import univariate as uni

    d = pd.DataFrame({"k": count.astype(float), "e": people.astype(float), "l": labels}).dropna()
    d = d[d.e > 0]
    nat = d.k.sum() / d.e.sum()
    lo_k, hi_k = uni.poisson_interval(nat * d.e)
    above, below = 100 * (d.k > hi_k).mean(), 100 * (d.k < lo_k).mean()
    if quoted:
        same(above, quoted[0], f"{name}: % above")
        same(below, quoted[1], f"{name}: % below")
    grid = np.logspace(np.log10(d.e.min()), np.log10(d.e.max()), 60)
    lo, hi = uni.poisson_interval(nat * grid)
    rate = 1000 * d.k / d.e
    pts = [[r(e, 0), r(v, 3), lab] for e, v, lab in zip(d.e, rate, d.l, strict=True) if v > 0]
    lim = lambda arr: [[r(x, 0), r(1000 * y / x, 4)] for x, y in zip(grid, arr, strict=True) if y > 0]  # noqa: E731
    ylo, yhi = log_range([p[1] for p in pts])
    xlo, xhi = log_range(d.e)
    return {
        "label": name,
        "x": {"min": xlo, "max": xhi},
        "y": {"min": ylo, "max": yhi},
        "subtitle": f"{name}: each area's applications a year per 10,000 people, against its population. Chance "
        "alone would "
        f"keep 95% of areas between the dashed lines; {above:.1f}% are above and {below:.1f}% below.",
        "series": [
            {"name": "Areas", "data": pts, "colour": 0, "size": 5, "opacity": 0.55},
            {"name": "Upper 95% limit (chance alone)", "kind": "line", "data": lim(hi), "line": "dashed", "colour": 1},
            {"name": "Lower 95% limit", "kind": "line", "data": lim(lo), "line": "dashed", "colour": 1},
            {
                "name": f"National rate ({1000 * nat:.2f})",
                "kind": "line",
                "data": [[r(grid[0], 0), r(1000 * nat, 3)], [r(grid[-1], 0), r(1000 * nat, 3)]],
                "colour": "ink",
            },
        ],
        "note": f"{int((rate == 0).sum()):,} areas with no applications cannot be drawn on the log scale.",
    }


@chart
def U53() -> dict:
    g = regions()
    sa3 = (
        g.groupby(["sa3_code", "sa3_name"])
        .agg(persons=("persons", "sum"), patents_standard=("patents_standard", "sum"))
        .reset_index()
    )
    return {
        "type": "scatter",
        "title": "Do places differ more than chance would make them?",
        "x": {"name": "People in the area (log scale)", "type": "log", "format": "int"},
        "y": {"name": "Applications a year per 10,000 people (log scale)", "type": "log", "format": "num", "digits": 2},
        "views": [
            funnel_view(g.patents_standard, g.persons, "Postal area " + g.poa_code, "Standard patents", (6.7, 68.2)),
            funnel_view(g.trade_marks, g.persons, "Postal area " + g.poa_code, "Trade marks", (15.0, 71.4)),
            funnel_view(
                sa3.patents_standard, sa3.persons, sa3.sa3_name, "Standard patents, pooled into SA3s", (15.5, 72.5)
            ),
        ],
        "height": "tall",
        "source": "IP RAPID, FY2017 to FY2026; ABS Census 2021 (lens: regions). A funnel plot.",
    }


@chart
def U55() -> dict:
    d = sql("SELECT source, count(*) AS n FROM {lens/region_indicators} GROUP BY 1 ORDER BY 2 DESC, 1")
    same(int(d.n.sum()), 22511923, "attached values")
    names = {
        "census": "Census 2021",
        "data_by_region": "Data by Region",
        "phidu": "PHIDU social health atlas",
        "cabee": "CABEE business counts",
        "cer": "Clean Energy Regulator",
    }
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Values attached to the places table, by source",
        "x": {"type": "category", "values": [names.get(s, s) for s in d.source]},
        "y": {"name": "Values", "min": 0, "format": "int"},
        "series": [{"name": "Values", "data": col(d, "n")}],
        "source": "ABS Census 2021, Data by Region, CABEE; PHIDU; Clean Energy Regulator (lens: region_indicators)",
    }


@chart
def U56() -> dict:
    d = sql("""
        WITH v AS (SELECT poa_code, sum(value) AS cabee FROM {lens/region_indicators}
                   WHERE source = 'cabee' AND indicator LIKE 'employment|%|Total' AND period = 'June 2025' GROUP BY 1)
        SELECT r.poa_code, r.active_gst_abns AS abr, v.cabee FROM {lens/regions} r JOIN v USING (poa_code) ORDER BY 1
    """).dropna()
    same(d.cabee.sum() / d.abr.sum(), 0.742, "CABEE against the ABR")
    d = d[(d.abr > 0) & (d.cabee > 0)]
    lo, hi = log_range([max(v, 1) for v in list(d.abr) + list(d.cabee)])
    return {
        "type": "scatter",
        "title": "Two counts of businesses, area by area",
        "subtitle": "Postal areas: active GST-registered ABNs in the business register (across) against CABEE's "
        "count of "
        "businesses actively trading, June 2025 (up). Points on the dashed line agree.",
        "x": {
            "name": "ABR: active GST-registered ABNs (log scale)",
            "type": "log",
            "format": "int",
            "min": lo,
            "max": hi,
        },
        "y": {"name": "CABEE: businesses (log scale)", "type": "log", "format": "int", "min": lo, "max": hi},
        "series": [
            {
                "name": "Postal areas",
                "data": [
                    [r(a, 0), r(c, 0), f"Postal area {p}"] for p, a, c in zip(d.poa_code, d.abr, d.cabee, strict=True)
                ],
                "size": 5,
                "opacity": 0.55,
            },
            {
                "name": "Where they agree",
                "kind": "line",
                "data": [[1, 1], [100000, 100000]],
                "line": "dashed",
                "colour": "muted",
            },
        ],
        "height": "tall",
        "source": "ABR; ABS CABEE split to postal areas by residents (lenses: regions, region_indicators)",
    }


@chart
def U58() -> dict:
    d = sql("""SELECT period, count(DISTINCT indicator) AS n FROM {lens/region_indicators}
               WHERE source = 'data_by_region' GROUP BY 1 ORDER BY 1""").set_index("period")
    same(d.n["2021"], 629, "Data by Region items in 2021")
    return {
        "type": "bar",
        "title": "Data by Region: items published for each year",
        "x": {"type": "category", "values": list(d.index)},
        "y": {"name": "Items", "min": 0, "format": "int"},
        "series": [{"name": "Items", "data": col(d, "n")}],
        "source": "ABS Data by Region (lens: region_indicators)",
        "note": "Census years (2011, 2016, 2021) carry the most.",
    }


@chart
def U59() -> dict:
    d = sql("""
        SELECT split_part(indicator, '|', 3) AS size, period, sum(value) AS n FROM {lens/region_indicators}
        WHERE source = 'cabee' AND split_part(indicator, '|', 1) = 'employment' GROUP BY ALL
    """)
    p = pivot(d, "period", "size", "n")
    sizes = ["Non employing", "1-4 Employees", "5-19 Employees", "20-199 Employees", "200+ Employees"]
    pct = 100 * p[sizes].div(p["Total"], axis=0)
    same(pct.loc["June 2023", "Non employing"], 61.3, "non-employing 2023")
    same(pct.loc["June 2025", "Non employing"], 63.6, "non-employing 2025")
    periods = [x for x in ["June 2023", "June 2024", "June 2025"] if x in pct.index]
    return {
        "type": "bar",
        "horizontal": True,
        "stack": True,
        "title": "Businesses by number of employees",
        "x": {"type": "category", "values": periods},
        "y": {"name": "% of businesses", "min": 0, "max": 100, "format": "pct", "digits": 1},
        "series": [
            {
                "name": s.replace("Non employing", "No employees")
                .replace(" Employees", " employees")
                .replace("-", " to "),
                "data": [r(pct.loc[x, s], 1) for x in periods],
            }
            for s in sizes
        ],
        "source": "ABS CABEE, split to postal areas by residents (lens: region_indicators)",
    }


@chart
def U60() -> dict:
    d = sql("""SELECT period, count(DISTINCT indicator) AS n FROM {lens/region_indicators}
               WHERE source = 'phidu' GROUP BY 1 ORDER BY n DESC, period LIMIT 10""")
    same(int(d.n.iloc[0]), 702, "indicators for 2022/23")
    return {
        "type": "bar",
        "horizontal": True,
        "title": "PHIDU indicators by the period they describe",
        "subtitle": "The ten most common periods",
        "x": {"type": "category", "values": list(d.period)},
        "y": {"name": "Indicators", "min": 0, "format": "int"},
        "series": [{"name": "Indicators", "data": col(d, "n")}],
        "source": "PHIDU, Social Health Atlas (lens: region_indicators)",
    }


@chart
def U61() -> dict:
    d = sql("""
        SELECT period::INT AS y, topic AS t, sum(value) AS n FROM {lens/region_indicators}
        WHERE source = 'cer' AND indicator LIKE '%|installations' GROUP BY 1, 2
    """)
    p = pivot(d, "y", "t", "n").sort_index()
    same(p.loc[2009, "solar_water_heater"], 122312, "solar water heaters 2009")
    same(p.loc[2020, "solar_pv"], 370287, "solar panels 2020")
    tech = {
        "solar_pv": "Solar panels",
        "solar_water_heater": "Solar water heaters",
        "heat_pump_water_heater": "Heat pump water heaters",
        "battery": "Batteries",
        "wind": "Small wind",
        "hydro": "Small hydro",
    }
    p = p.loc[2001:2025]
    return {
        "type": "line",
        "title": "Small-scale energy installations a year, by technology",
        "subtitle": "2001 to 2025 (2026 is part of a year and left out)",
        "x": {"type": "category", "values": [str(y) for y in p.index]},
        "y": {"name": "Installations a year", "min": 0, "format": "int"},
        "series": [{"name": tech[c], "data": col(p, c, 0)} for c in tech if c in p],
        "source": "Clean Energy Regulator, small-scale installations by postcode (lens: region_indicators)",
        "note": "Batteries are recorded from July 2025.",
    }


@chart
def U62() -> dict:
    g = regions()
    s = g.groupby("state")[["austender_contracts", "austender_value", "active_gst_abns"]].sum()
    s = 100 * s / s.sum()
    s = s.sort_values("austender_value", ascending=False)
    act = "Australian Capital Territory"
    same(s.loc[act, "austender_contracts"], 27.0, "ACT share of contracts")
    same(s.loc[act, "active_gst_abns"], 1.3, "ACT share of businesses")
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Government contracts and businesses, by state",
        "subtitle": "Contracts first published FY2017 to FY2026, by the supplier's postcode, against the share "
        "of businesses",
        "x": {"type": "category", "values": list(s.index)},
        "y": {"name": "% of the national total", "min": 0, "format": "pct", "digits": 1},
        "series": [
            {"name": "Contracts", "data": col(s, "austender_contracts", 1)},
            {"name": "Contract value", "data": col(s, "austender_value", 1)},
            {"name": "Businesses", "data": col(s, "active_gst_abns", 1)},
        ],
        "source": "AusTender; ABR (lens: regions). Nominal values.",
    }


# ------------------------------------------------------------------------------------------------------------ national


@chart
def U64() -> dict:
    w = sql("SELECT year, entity, sum(value) AS v FROM {lens/national} WHERE indicator = 'WIPO.PAT.APP' GROUP BY 1, 2")
    p = pivot(w, "year", "entity", "v").fillna(0).loc[1980:2024]
    sh = 100 * p.div(p.sum(axis=1), axis=0)
    same(sh.loc[1980, "origin unknown"], 34.35, "unknown origin 1980")
    same(sh.loc[1990, "origin unknown"], 29.02, "unknown origin 1990")
    return {
        "type": "bar",
        "stack": True,
        "title": "WIPO's patent applications whose origin is not a current country",
        "subtitle": "% of patent applications by origin, all offices together",
        "x": {"type": "category", "values": [str(y) for y in sh.index]},
        "y": {"name": "% of applications", "min": 0, "format": "pct", "digits": 2},
        "series": [
            {"name": "Origin unknown", "data": col(sh, "origin unknown", 2)},
            {"name": "Former states (the Soviet Union and others)", "data": col(sh, "former state", 2)},
        ],
        "marks": {"x": [{"at": "1995", "label": "Compared from here"}]},
        "source": "WIPO IP statistics, filings by origin and office (lens: national)",
    }


@chart
def U65() -> dict:
    codes = {
        "OECD.MSTI.G": "Gross R&D (% of GDP)",
        "OECD.MSTI.B": "Business R&D (% of GDP)",
        "NV.IND.MANF.ZS": "Manufacturing (% of GDP)",
        "NE.EXP.GNFS.ZS": "Exports (% of GDP)",
    }
    inlist = ", ".join(f"'{c}'" for c in codes)
    oe = sql(f"""SELECT indicator, year, median(value) AS med, quantile_cont(value, 0.25) AS q1,
                        quantile_cont(value, 0.75) AS q3, count(*) AS n
                 FROM {{lens/national}} WHERE oecd AND indicator IN ({inlist}) GROUP BY 1, 2""")
    au = sql(f"SELECT indicator, year, value FROM {{lens/national}} WHERE australia AND indicator IN ({inlist})")
    a = au.pivot(index="year", columns="indicator", values="value")
    same(a.loc[2008, "OECD.MSTI.G"], 2.24, "GERD 2008")
    same(a.loc[2023, "OECD.MSTI.G"], 1.68, "GERD 2023")
    views = []
    for c, name in codes.items():
        o = oe[(oe.indicator == c) & (oe.n >= 10)].set_index("year").sort_index()
        years = sorted(set(o.index) | set(a[c].dropna().index))
        years = [y for y in years if y >= 1981]
        o = o.reindex(years)
        views.append(
            {
                "label": name,
                "subtitle": f"{name}: Australia against the OECD members' median and middle half",
                "x": {"type": "category", "values": [str(y) for y in years]},
                "series": [
                    {"name": "Australia", "data": [r(a[c].get(y), 2) for y in years], "width": 2.5},
                    {"name": "OECD median", "data": col(o, "med", 2), "colour": "ink", "line": "dashed"},
                    {"name": "OECD 75th percentile", "data": col(o, "q3", 2), "colour": "muted", "line": "dotted"},
                    {"name": "OECD 25th percentile", "data": col(o, "q1", 2), "colour": "muted", "line": "dotted"},
                ],
            }
        )
    return {
        "type": "line",
        "title": "Australia against the OECD",
        "y": {"name": "% of GDP", "min": 0, "format": "pct", "digits": 2},
        "views": views,
        "source": "OECD MSTI; World Bank WDI (lens: national). OECD lines where 10 or more members report.",
    }


@chart
def U66() -> dict:
    from eda import load_lens

    nat = load_lens("national")
    c = nat[nat.entity == "country"]
    rows = []
    for code, d in c.groupby("indicator"):
        a = d[d.australia]
        if a.empty:
            continue
        y = a.year.max()
        v = a.loc[a.year == y, "value"].iloc[0]
        o = d[d.oecd & (d.year == y)]
        rows.append(
            (code, d.indicator_name.iloc[0], int(y), len(o), int((o.value > v).sum() + 1), 100 * (o.value < v).mean())
        )
    pos = pd.DataFrame(rows, columns=["code", "name", "year", "n", "rank", "below"]).sort_values(
        "below", ascending=False
    )
    p = pos.set_index("code")
    same(p.loc["NE.EXP.GNFS.ZS", "rank"], 34, "exports rank")
    same(p.loc["IP.PAT.NRES", "rank"], 5, "non-resident patents rank")
    same(p.loc["OECD.MSTI.B", "rank"], 26, "BERD rank")

    def short(n: str) -> str:
        return (
            n.replace(" (BoP, current US$)", "")
            .replace(" (current US$)", "")
            .replace("(OECD MSTI)", "")
            .replace(", % of GDP", " (% of GDP)")
            .strip()
        )

    return {
        "type": "bar",
        "horizontal": True,
        "title": "Where Australia stands among OECD members",
        "subtitle": "% of OECD members below Australia, in Australia's latest year for each indicator (50 = the "
        "median member)",
        "x": {
            "type": "category",
            "values": [
                f"{short(n)} ({y}; {k}th of {m})"
                for n, y, k, m in zip(pos.name, pos.year, pos["rank"], pos.n, strict=True)
            ],
        },
        "y": {"name": "% of members below Australia", "min": 0, "max": 100, "format": "pct", "digits": 0},
        "series": [{"name": "% of members below Australia", "data": col(pos, "below", 1)}],
        "marks": {"y": [{"at": 50, "label": "Median member"}]},
        "source": "World Bank WDI, WIPO, OECD MSTI (lens: national)",
        "note": "Counts rank with a country's size: Australia's population is 14th of 38.",
    }


@chart
def U67() -> dict:
    t = sql("""
        WITH ipr AS (
            SELECT year(application_date) AS year,
                   count(*) FILTER (patent_type = 'standard' AND australian_applicant) AS res,
                   count(*) FILTER (patent_type = 'standard' AND NOT australian_applicant) AS nonres
            FROM {lens/rights} WHERE year(application_date) BETWEEN 1980 AND 2024 GROUP BY 1),
        wdi AS (
            SELECT year, max(value) FILTER (indicator = 'IP.PAT.RESD') AS wres, max(value) FILTER (indicator =
                'IP.PAT.NRES') AS wnon
            FROM {lens/national} WHERE australia GROUP BY 1)
        SELECT * FROM ipr JOIN wdi USING (year) ORDER BY year
    """).set_index("year")
    t["a"], t["o"] = t.res / t.wres, t.nonres / t.wnon
    same(t.loc[1989:2024, "a"].median(), 1.002, "median ratio, Australian applicants")
    same(t.loc[1980, "o"], 0.072, "overseas ratio 1980")
    return {
        "type": "line",
        "title": "The register against the World Bank: standard patent applications",
        "subtitle": "The register's count divided by the World Bank's, by year (1.00 = they agree)",
        "x": {"type": "category", "values": [str(y) for y in t.index]},
        "y": {"name": "Ratio", "min": 0, "max": 1.2, "format": "ratio", "digits": 3},
        "series": [
            {"name": "Australian applicants", "data": col(t, "a", 3)},
            {"name": "Overseas applicants", "data": col(t, "o", 3)},
        ],
        "marks": {"y": [{"at": 1, "label": "Agree"}], "x": [{"at": "1989", "label": "Origins recorded"}]},
        "source": "IP Australia, IP RAPID (lens: rights); World Bank WDI (lens: national)",
    }


@chart
def U70() -> dict:
    o = sql("""SELECT year, country, sum(value) AS v FROM {lens/national_indicators}
               WHERE indicator = 'WIPO.AU.10' GROUP BY 1, 2""")
    p = pivot(o, "year", "country", "v").fillna(0)
    sh = (100 * p.div(p.sum(axis=1), axis=0)).loc[1995:2024]
    same(sh.loc[2024, "United States"], 41.9, "US share 2024")
    same(sh.loc[2024, "China"], 8.3, "China share 2024")
    same(sh.loc[2024, "Australia"], 8.3, "Australia share 2024")
    who = ["United States", "Australia", "China", "Japan", "Germany"]
    return {
        "type": "line",
        "title": "Who files patents at IP Australia",
        "subtitle": "% of patent applications at IP Australia, by the applicant's origin, 1995 to 2024",
        "x": {"type": "category", "values": [str(y) for y in sh.index]},
        "y": {"name": "% of applications", "min": 0, "format": "pct", "digits": 1},
        "series": [{"name": c, "data": col(sh, c, 1)} for c in who],
        "source": "WIPO IP statistics, filings at IP Australia by origin (lens: national_indicators)",
    }


# ------------------------------------------------------------------------------------------------------------ industrie


def industries() -> pd.DataFrame:
    from eda import load_lens

    return load_lens("industries")


def div_names(df: pd.DataFrame) -> list[str]:
    return [f"{n} ({d})" for d, n in zip(df.index, df.division_name, strict=True)]


@chart
def U75() -> dict:
    i = industries()
    w = (
        i[i.fy.between(2017, 2026)]
        .groupby(["division", "division_name"])[["patents_standard", "trade_marks"]]
        .sum()
        .reset_index("division_name")
    )
    w["p"] = 100 * w.patents_standard / w.patents_standard.sum()
    w["t"] = 100 * w.trade_marks / w.trade_marks.sum()
    same(w.loc["C", "p"], 90.78, "manufacturing's share of standard patents")
    same(w.loc["C", "t"], 55.65, "manufacturing's share of trade marks")
    views = []
    for k, label in [("p", "Standard patents"), ("t", "Trade marks")]:
        s = w.sort_values(k, ascending=False)
        views.append(
            {
                "label": label,
                "subtitle": f"{label} filed FY2017 to FY2026: each industry's share (expected counts)",
                "x": {"type": "category", "values": div_names(s)},
                "series": [{"name": f"% of {label.lower()}", "data": col(s, k, 2)}],
            }
        )
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Where IP falls by industry",
        "y": {"name": "% of applications", "min": 0, "format": "pct", "digits": 2},
        "views": views,
        "source": "IP RAPID; ALP crosswalks (Lybbert and Zolas), ABS ANZSIC 2006 (lens: industries)",
        "note": "The patent crosswalk in the corpus leaves out services, so patents reach only goods-producing "
        "industries.",
    }


@chart
def U76() -> dict:
    i = industries()
    w = (
        i[i.fy.between(2017, 2026)]
        .groupby(["division", "division_name"])[
            ["patents_standard", "patents_standard_au", "trade_marks", "trade_marks_au"]
        ]
        .sum()
        .reset_index("division_name")
    )
    w["p"] = 100 * w.patents_standard_au / w.patents_standard.where(w.patents_standard > 50)
    w["t"] = 100 * w.trade_marks_au / w.trade_marks
    same(w.loc["C", "p"], 7.87, "Australian share of manufacturing's patents")
    views = []
    for k, label in [("t", "Trade marks"), ("p", "Standard patents")]:
        s = w.dropna(subset=[k]).sort_values(k, ascending=False)
        views.append(
            {
                "label": label,
                "subtitle": f"{label} filed FY2017 to FY2026: % filed by Australian applicants, by industry",
                "x": {"type": "category", "values": div_names(s)},
                "series": [{"name": "% Australian", "data": col(s, k, 2)}],
            }
        )
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Australian applicants' share, by industry",
        "y": {"name": "% filed by Australians", "min": 0, "max": 100, "format": "pct", "digits": 2},
        "views": views,
        "source": "IP RAPID; ALP crosswalks (lens: industries)",
        "note": "Patent shares only where the expected count is above 50.",
    }


@chart
def U77() -> dict:
    i = industries()
    last = i[i.fy == 2026].set_index("division").sort_values("businesses_end", ascending=False)
    same(last.loc["E", "businesses_end"], 478651, "construction businesses June 2026")
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Businesses by industry, June 2026",
        "x": {"type": "category", "values": div_names(last)},
        "y": {"name": "Businesses", "min": 0, "format": "int"},
        "series": [{"name": "Businesses", "data": col(last, "businesses_end")}],
        "source": "ABS, Counts of Australian Businesses (CABEE) (lens: industries)",
    }


@chart
def U78() -> dict:
    i = industries()
    x = i.groupby(["division", "division_name"]).berd.max().reset_index("division_name")
    x["share"] = 100 * x.berd / x.berd.sum()
    same(x.berd.sum() / 1e6, 24.41, "BERD total ($ billion)")
    same(x.loc["M", "share"], 37.6, "professional services' share")
    x = x.sort_values("share", ascending=False)
    wpi = i.pivot(index="fy", columns="division", values="wpi_index")
    g = (100 * (wpi.loc[2025] / wpi.loc[2010] - 1)).dropna().sort_values(ascending=False)
    names = i.drop_duplicates("division").set_index("division").division_name
    same(g["D"], 56.8, "utilities' wage growth")
    return {
        "type": "bar",
        "horizontal": True,
        "title": "R&D and wages by industry",
        "source": "ABS Business Expenditure on R&D 2023-24 and Wage Price Index (lens: industries)",
        "views": [
            {
                "label": "Business R&D, 2023-24",
                "subtitle": "Each industry's share of $24.41 billion of business R&D",
                "x": {"type": "category", "values": div_names(x)},
                "y": {"name": "% of business R&D", "min": 0, "format": "pct", "digits": 1},
                "series": [{"name": "Share of business R&D", "data": col(x, "share", 1)}],
            },
            {
                "label": "Wage growth, FY2010 to FY2025",
                "subtitle": "% rise in the Wage Price Index, by industry",
                "x": {"type": "category", "values": [f"{names[d]} ({d})" for d in g.index]},
                "y": {"name": "% rise", "min": 0, "format": "pct", "digits": 1},
                "series": [{"name": "Wage growth", "data": [r(v, 1) for v in g]}],
            },
        ],
    }


@chart
def U79() -> dict:
    b = (
        sql("""SELECT division, value FROM {lens/industry_indicators}
               WHERE source = 'bcs' AND indicator = 'BCS.BCS_INNACT.P_D_GSNEWY.9999.TOTAL.9999.0' AND period =
                   '2023'""")
        .set_index("division")
        .value
    )
    same(b["TOTAL"], 21.7, "all industries 2023")
    same(b["A"], 9.9, "agriculture 2023")
    names = industries().drop_duplicates("division").set_index("division").division_name
    d = b.drop("TOTAL", errors="ignore")
    d = d[d.index.isin(names.index)].sort_values(ascending=False)
    return {
        "type": "bar",
        "horizontal": True,
        "title": "Businesses that introduced a new good or service, 2023",
        "subtitle": "% of businesses, by industry (ABS Business Characteristics Survey)",
        "x": {"type": "category", "values": [f"{names[k]} ({k})" for k in d.index]},
        "y": {"name": "% of businesses", "min": 0, "format": "pct", "digits": 1},
        "series": [{"name": "Introduced a new good or service", "data": [r(v, 1) for v in d]}],
        "marks": {"y": [{"at": 21.7, "label": "All industries"}]},
        "source": "ABS Business Characteristics Survey (lens: industry_indicators)",
        "note": "Survey estimates; the ABS flags many for sampling error.",
    }


# ------------------------------------------------------------------------------------------------------------ instituti


def institutions() -> pd.DataFrame:
    from eda import load_lens

    return load_lens("institutions")


@chart
def U83() -> dict:
    g = institutions().groupby("year")[["arc_funding", "arc_industry_funding", "nhmrc_funding"]].sum(min_count=1) / 1e6
    g = g.loc[2001:2026]
    same(g.loc[2010, "arc_funding"], 757.9, "ARC funding 2010 ($m)")
    return {
        "type": "line",
        "title": "Research grants to the institutions",
        "subtitle": "$ million (current), by the year ARC funding starts or the NHMRC round",
        "x": {"type": "category", "values": [str(y) for y in g.index]},
        "y": {"name": "$ million", "min": 0, "format": "moneym", "digits": 1},
        "series": [
            {"name": "ARC funding", "data": col(g, "arc_funding", 1)},
            {"name": "ARC funding with industry partners", "data": col(g, "arc_industry_funding", 1)},
            {"name": "NHMRC funding", "data": col(g, "nhmrc_funding", 1)},
        ],
        "source": "ARC National Competitive Grants Program; NHMRC grant outcomes (lens: institutions)",
    }


@chart
def U84() -> dict:
    s = sql("""
        WITH r AS (SELECT ip_right_type, application_number, patent_type, founding_australian,
            year(application_date) AS year
                   FROM {lens/rights} WHERE patent_type IN ('standard', 'provisional') AND year(application_date)
                       BETWEEN 1990 AND 2026),
        x AS (SELECT DISTINCT ip_right_type, application_number FROM {lens/institution_rights})
        SELECT (year // 5) * 5 AS period, patent_type, count(*) FILTER (founding_australian) AS a,
               count(*) FILTER (founding_australian AND (ip_right_type, application_number) IN (SELECT * FROM x)) AS b
        FROM r GROUP BY ALL ORDER BY 2, 1""")
    s["pct"] = 100 * s.b / s.a
    p = pivot(s, "period", "patent_type", "pct")
    same(p.loc[1990, "standard"], 4.80, "share 1990 to 1994")
    same(p.loc[2020, "standard"], 8.96, "share 2020 to 2024")
    labels = [f"{int(y)} to {int(y) + 4}" if y < 2025 else "2025 to 2026" for y in p.index]
    return {
        "type": "line",
        "title": "The research institutions' share of Australian patent filing",
        "subtitle": "% of applications filed from Australia with a research institution among the filers, by "
        "five-year period",
        "x": {"type": "category", "values": labels},
        "y": {"name": "% of applications", "min": 0, "format": "pct", "digits": 2},
        "series": [
            {"name": "Standard patents", "data": col(p, "standard", 2)},
            {"name": "Provisional applications", "data": col(p, "provisional", 2)},
        ],
        "source": "IP RAPID; ROR and the reviewed link (lenses: institutions, institution_rights)",
        "note": "2025 to 2026 is part of a period.",
    }


# ------------------------------------------------------------------------------------------------------------ main


def main(names: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    unknown = set(names) - set(CHARTS)
    if unknown:
        sys.exit(f"no chart called {', '.join(sorted(unknown))}")
    failed = []
    for name, fn in CHARTS.items():
        if names and name not in names:
            continue
        try:
            spec = {"id": name, **fn()}
        except Mismatch as e:
            failed.append(f"{name}: {e}")
            continue
        text = json.dumps(spec, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        (OUT / f"{name}.json").write_text(text, encoding="utf-8")
        print(f"{name}: {len(text) / 1e3:.1f} kB")
    if failed:
        sys.exit("Not written, because the lens no longer gives the quoted number:\n- " + "\n- ".join(failed))


if __name__ == "__main__":
    main(sys.argv[1:])
