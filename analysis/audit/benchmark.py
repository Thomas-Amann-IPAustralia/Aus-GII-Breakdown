"""IP Australia's published figures against the lenses (ADR 0024): the audit's like-for-like checks.

    uv run python -m audit.benchmark        # seconds, once the lens tables are built (`eda.build`)

`analysis/audit/published.csv` holds figures IP Australia published in its Australian IP Reports (2015 to 2026) and
research, each with its report and page in the Econ repository's library (`library/elements/<doc_id>.jsonl`). This
recomputes each one from the lens tables on IP Australia's own definitions and writes
`analysis/audit/output/benchmark.csv`: the published value, the lens's value, their ratio (counts) or difference in
percentage points (shares), and whether they agree within the tolerance below. `docs/audit-ip-australia.md` quotes it.

IP Australia's definitions, as its reports state them or as the figures show them:
- a calendar year of filing (the reports count years, the notebook financial years);
- a resident application has a founding applicant in Australia (`founding_australian`): IP Australia says residency is
  how an applicant first gave its origin, and this definition reproduces its 2022 and 2025 resident standard patents
  exactly;
- a PCT application is counted when it enters the national phase (`application_date`, as in the lens).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from eda.data import connect, sql

HERE = Path(__file__).resolve().parent
PUBLISHED = HERE / "published.csv"
OUT = HERE / "output" / "benchmark.csv"

COUNT_TOLERANCE = 0.02  # a count agrees if the lens is within 2% of the published figure
SHARE_TOLERANCE = 1.0  # a share agrees if it is within 1 percentage point
LOOSE = {"prov_individual_share": 5.0}  # IP Australia gives these in words ("around one-third", "close to half")

STD = "patent_type = 'standard'"
PROV = "patent_type = 'provisional'"
TM = "ip_right_type = 'trade_mark'"
DES = "ip_right_type = 'design'"
PBR = "ip_right_type = 'pbr'"
RES = "founding_australian"
NONRES = "founding_australian = false"
STATES = ["nsw", "vic", "qld", "wa", "sa", "act", "tas", "nt"]
FIELDS = {"pharma": "16_pharmaceuticals", "medtech": "13_medical_technology", "biotech": "15_biotechnology"}

# measure: (kind, SQL giving `year` and `value`, how the lens counts it)
_by_filing = "SELECT year(application_date) AS year, {value} AS value FROM {{lens/rights}} WHERE {where} GROUP BY 1"


def _count(where: str) -> str:
    return _by_filing.format(value="count(*)", where=where)


def _share(part: str, where: str) -> str:
    return _by_filing.format(value=f"100.0 * avg(({part})::int)", where=where)


def _founder(name: str) -> str:
    """Standard applications with a founding applicant of this name (as IP Australia's leading-applicant tables)."""
    return f"""
        SELECT year(r.application_date) AS year, count(DISTINCT r.application_number) AS value
        FROM {{lens/rights}} r JOIN {{iprapid/party}} p
          ON p.ip_right_type = 'patent' AND p.application_number = r.application_number
        WHERE r.{STD} AND p.is_founding AND p.party_role_category = 'applicant' AND p.party_name ILIKE '{name}'
        GROUP BY 1"""


MEASURES: dict[str, tuple[str, str, str]] = {
    "std_apps": ("count", _count(STD), "standard patent applications"),
    "std_apps_res": ("count", _count(f"{STD} AND {RES}"), "standard, a founding applicant in Australia"),
    "std_apps_nonres": ("count", _count(f"{STD} AND {NONRES}"), "standard, founding applicants all overseas"),
    "std_apps_nonres_multi": (
        "count",
        _count(f"{STD} AND {NONRES} AND founder_count >= 2"),
        "standard, overseas, two or more founding applicants",
    ),
    "std_apps_us": (
        "count",
        _count(f"{STD} AND founder_country = 'us'"),
        "standard, first founding applicant in the US",
    ),
    "std_apps_cn": (
        "count",
        _count(f"{STD} AND founder_country = 'cn'"),
        "standard, first founding applicant in China",
    ),
    "std_apps_pct": ("count", _count(f"{STD} AND filing_route = 'pct'"), "standard, through the PCT"),
    "std_apps_direct": (
        "count",
        _count(f"{STD} AND filing_route IS DISTINCT FROM 'pct'"),
        "standard, not through the PCT",
    ),
    "std_pct_share": (
        "share",
        _share("filing_route = 'pct'", STD),
        "per cent of standard applications through the PCT",
    ),
    **{
        f"std_field_{k}": ("count", _count(f"{STD} AND main_area = '{v}'"), f"standard, main WIPO field {v}")
        for k, v in FIELDS.items()
    },
    **{
        f"std_res_state_{s}": (
            "count",
            _count(f"{STD} AND {RES} AND founder_state = '{s}'"),
            f"standard, first founding applicant in Australia in {s.upper()}",
        )
        for s in STATES
    },
    "std_apps_aristocrat": (
        "count",
        _founder("aristocrat technologies australia%"),
        "standard, a founding applicant named Aristocrat Technologies Australia (its US company apart)",
    ),
    "std_apps_csiro": (
        "count",
        _founder("commonwealth scientific and industrial research organ%"),
        "standard, a founding applicant named CSIRO",
    ),
    "std_grants": (
        "count",
        f"SELECT year(registered_date) AS year, count(*) AS value FROM {{lens/rights}} WHERE {STD} GROUP BY 1",
        "standard patents, by year of grant",
    ),
    "std_grants_res": (
        "count",
        f"""SELECT year(registered_date) AS year, count(*) AS value
            FROM {{lens/rights}} WHERE {STD} AND {RES} GROUP BY 1""",
        "standard patents granted, a founding applicant in Australia",
    ),
    "std_res_individual_share": (
        "share",
        _share("founder_type = 'individual'", f"{STD} AND {RES}"),
        "per cent of resident standard applications whose first founding applicant is an individual",
    ),
    "std_exam_to_accept_median_years": (
        "years",
        f"""SELECT year(exam_requested_date) AS year,
                   median(date_diff('day', exam_requested_date, accepted_date)) / 365.25 AS value
            FROM {{lens/rights}} WHERE {STD} AND accepted_date >= exam_requested_date GROUP BY 1""",
        "median years from the request for examination to acceptance, by year of request",
    ),
    "prov_apps": ("count", _count(PROV), "provisional applications"),
    "prov_apps_res": ("count", _count(f"{PROV} AND {RES}"), "provisional, a founding applicant in Australia"),
    "prov_individual_share": (
        "share",
        _share("founder_type = 'individual'", PROV),
        "per cent of provisionals whose first founding applicant is an individual",
    ),
    "second_tier_apps": ("count", _count("patent_type = 'second_tier'"), "innovation and petty patent applications"),
    "second_tier_nonres_share": (
        "share",
        _share(NONRES, "patent_type = 'second_tier' AND founding_australian IS NOT NULL"),
        "per cent of second-tier applications (known origin) with founding applicants all overseas",
    ),
    "tm_apps": ("count", _count(TM), "trade mark applications"),
    "tm_apps_res": ("count", _count(f"{TM} AND {RES}"), "trade marks, a founding applicant in Australia"),
    "tm_apps_madrid": ("count", _count(f"{TM} AND filing_route = 'madrid'"), "trade marks through the Madrid system"),
    "tm_apps_direct": (
        "count",
        _count(f"{TM} AND filing_route IS DISTINCT FROM 'madrid'"),
        "trade marks not through the Madrid system",
    ),
    "tm_res_individual_share": (
        "share",
        _share("founder_type = 'individual'", f"{TM} AND {RES}"),
        "per cent of resident trade marks whose first founding applicant is an individual",
    ),
    "tm_madrid_share": ("share", _share("filing_route = 'madrid'", TM), "per cent of trade marks through Madrid"),
    "tm_madrid_share_of_overseas": (
        "share",
        _share("filing_route = 'madrid'", f"{TM} AND {NONRES}"),
        "per cent of overseas applicants' trade marks through Madrid",
    ),
    "tm_registered": (
        "count",
        "SELECT year AS year, sum(trade_marks_registered) AS value FROM {lens/timeline} GROUP BY 1",
        "trade marks registered, by the date the registration was entered (the timeline lens)",
    ),
    "tm_in_force": (
        "count",
        f"""SELECT y.year, count(*) AS value
            FROM (SELECT unnest([2005, 2017]) AS year) y JOIN {{lens/rights}} r
              ON r.{TM} AND r.registered_date <= make_date(y.year, 12, 31)
             AND (r.retired_date IS NULL OR r.retired_date > make_date(y.year, 12, 31))
            GROUP BY 1""",
        "trade marks registered by 31 December and not ended by then",
    ),
    "des_apps": ("count", _count(DES), "design applications"),
    "des_apps_res": ("count", _count(f"{DES} AND {RES}"), "designs, a founding applicant in Australia"),
    "des_certified": (
        "count",
        f"SELECT year(certified_date) AS year, count(*) AS value FROM {{lens/rights}} WHERE {DES} GROUP BY 1",
        "designs certified, by year of certification",
    ),
    "pbr_apps": ("count", _count(PBR), "plant breeder's rights applications"),
    "pbr_apps_res": ("count", _count(f"{PBR} AND {RES}"), "plant breeder's rights, a founding applicant in Australia"),
    "pbr_registered": (
        "count",
        f"SELECT year(registered_date) AS year, count(*) AS value FROM {{lens/rights}} WHERE {PBR} GROUP BY 1",
        "plant breeder's rights registered, by year of registration",
    ),
}


# Figures from the lenses alone that the audit quotes beside the published ones (no published value to compare).
def _new_filers(where: str, ip_type: str = "patent", count: bool = False) -> str:
    """Founding applicants (by IP RAPID's party id, so ABNs play no part) filing a right of `ip_type` for the first
    time that year: their share of that year's applicants matching `where`, or their number."""
    first = "year(x.first_date) = f.year"
    value = f"count(*) FILTER (WHERE {first})" if count else f"100.0 * avg(({first})::int)"
    return f"""
    WITH firsts AS (
        SELECT p.party_id, min(r.application_date) AS first_date
        FROM {{lens/rights}} r JOIN {{iprapid/party}} p
          ON p.ip_right_type = r.ip_right_type AND p.application_number = r.application_number
        WHERE r.ip_right_type = '{ip_type}' AND p.is_founding AND p.party_role_category = 'applicant'
        GROUP BY 1),
    filers AS (
        SELECT DISTINCT year(r.application_date) AS year, p.party_id
        FROM {{lens/rights}} r JOIN {{iprapid/party}} p
          ON p.ip_right_type = r.ip_right_type AND p.application_number = r.application_number
        WHERE r.{where} AND p.is_founding AND p.party_role_category = 'applicant'
          AND year(r.application_date) BETWEEN 2019 AND 2025)
    SELECT f.year, {value} AS value
    FROM filers f JOIN firsts x USING (party_id) GROUP BY 1"""


CONTEXT: dict[str, tuple[str, str]] = {
    "des_apps_origin_unknown": (
        _count(f"{DES} AND founding_australian IS NULL"),
        "design applications with no founding applicant's country",
    ),
    "tm_apps_madrid_lens": (_count(f"{TM} AND filing_route = 'madrid'"), "trade marks through Madrid, every year"),
    "std_apps_res_lens": (_count(f"{STD} AND {RES}"), "resident standard applications, every year"),
    "std_res_first_applicant_lens": (
        _count(f"{STD} AND applicant_country = 'au'"),
        "standard applications whose first current applicant is in Australia (the older editions' residency)",
    ),
    "std_grants_res_first_applicant_lens": (
        f"""SELECT year(registered_date) AS year, count(*) AS value
            FROM {{lens/rights}} WHERE {STD} AND applicant_country = 'au' GROUP BY 1""",
        "standard patents granted whose first current applicant is in Australia (the older editions' residency)",
    ),
    "std_unclassified_lens": (
        _count(f"{STD} AND main_area IS NULL"),
        "standard applications with no WIPO field (not yet classified, or no class)",
    ),
    "std_res_founder_individual_pct": (
        _share("founder_type = 'individual'", f"{STD} AND {RES}"),
        "per cent of resident standard applications whose first founding applicant is an individual",
    ),
    "std_res_parties_individual_pct": (
        """SELECT year(r.application_date) AS year,
                  100.0 * count(DISTINCT p.party_id) FILTER (WHERE p.party_type = 'individual')
                        / count(DISTINCT p.party_id) AS value
           FROM {lens/rights} r JOIN {iprapid/party} p
             ON p.ip_right_type = 'patent' AND p.application_number = r.application_number
           WHERE r.patent_type = 'standard' AND r.founding_australian AND p.is_founding
             AND p.party_role_category = 'applicant' AND p.country_code = 'au'
           GROUP BY 1""",
        "per cent of distinct founding applicants in Australia on standard applications who are individuals",
    ),
    "prov_new_filer_pct": (
        _new_filers(PROV),
        "per cent of provisional applicants (founding, by party) whose first patent application is that year",
    ),
    "std_res_new_filer_pct": (
        _new_filers(f"{STD} AND {RES}"),
        "per cent of resident standard applicants (founding, by party) whose first patent application is that year",
    ),
    "tm_res_new_filers": (
        _new_filers(f"{TM} AND {RES}", "trade_mark", count=True),
        "trade mark applicants (founding, by party, a founding applicant in Australia) filing their first trade mark",
    ),
    "tm_res_filers": (
        f"""SELECT year(r.application_date) AS year, count(DISTINCT p.party_id) AS value
            FROM {{lens/rights}} r JOIN {{iprapid/party}} p
              ON p.ip_right_type = 'trade_mark' AND p.application_number = r.application_number
            WHERE r.{TM} AND r.{RES} AND p.is_founding AND p.party_role_category = 'applicant' GROUP BY 1""",
        "distinct founding applicants of resident trade mark applications",
    ),
    "std_exam_to_accept_median_years_lens": (
        MEASURES["std_exam_to_accept_median_years"][1],
        "median years from the request for examination to acceptance, by year of request",
    ),
    "institutions_std_res_pct": (
        """SELECT year(r.application_date) AS year,
                  100.0 * avg((r.application_number IN (SELECT application_number FROM {lens/institution_rights}
                                                        WHERE ip_right_type = 'patent'))::int) AS value
           FROM {lens/rights} r WHERE r.patent_type = 'standard' AND r.founding_australian GROUP BY 1""",
        "per cent of resident standard applications with a research institution among the founding applicants",
    ),
}


def context() -> pd.DataFrame:
    """The lens-only figures, 2013 to 2025."""
    con = connect()
    frames = []
    for name, (query, definition) in CONTEXT.items():
        df = sql(query, con=con)
        df = df[df["year"].between(2013, 2025)]
        df["figure"], df["definition"] = name, definition
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["value"] = out["value"].astype(float).round(2)
    return out[["figure", "year", "value", "definition"]].sort_values(["figure", "year"], ignore_index=True)


def state_shares(df: pd.DataFrame) -> pd.DataFrame:
    """Each state's share of resident standard applications, published and lens: IP Australia counts an application
    in every state its Australian applicants are in, the lens in its first founding applicant's, so counts differ more
    than shares."""
    s = df[df["measure"].str.startswith("std_res_state_")].copy()
    s["state"] = s["measure"].str.removeprefix("std_res_state_")
    for col in ["published", "lens"]:
        s[f"{col}_share"] = (100 * s[col] / s.groupby("year")[col].transform("sum")).round(1)
    s["difference"] = (s["lens_share"] - s["published_share"]).round(1)
    return s[["year", "state", "published", "lens", "published_share", "lens_share", "difference"]]


def lens_values() -> pd.DataFrame:
    """Every measure's value by year, from the lens tables."""
    con = connect()
    frames = []
    for measure, (kind, query, definition) in MEASURES.items():
        df = sql(query, con=con)
        df["measure"], df["kind"], df["lens_definition"] = measure, kind, definition
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def benchmark() -> pd.DataFrame:
    """The published figures beside the lens's, with their agreement."""
    pub = pd.read_csv(PUBLISHED)
    unknown = set(pub["measure"]) - set(MEASURES)
    if unknown:
        raise ValueError(f"published.csv names measures with no lens query: {sorted(unknown)}")
    out = pub.merge(lens_values(), on=["measure", "year"], how="left")
    out["lens"] = out["value"].astype(float)
    counts = out["kind"] == "count"
    out["ratio"] = (out["lens"] / out["published"]).where(counts).round(4)
    out["difference"] = (out["lens"] - out["published"]).round(2)
    tolerance = out["measure"].map(LOOSE).fillna(SHARE_TOLERANCE)
    out["agrees"] = ((out["ratio"] - 1).abs() <= COUNT_TOLERANCE).where(counts, out["difference"].abs() <= tolerance)
    out["lens"] = out["lens"].round(2)
    cols = ["measure", "year", "published", "lens", "ratio", "difference", "agrees", "observations", "source", "page"]
    return out[cols + ["note", "lens_definition"]].sort_values(["measure", "year"], ignore_index=True)


def summary(df: pd.DataFrame) -> pd.DataFrame:
    """Agreement by measure: how many figures, how many agree, and the range of ratios or differences."""
    g = df.groupby("measure", sort=False)
    return pd.DataFrame(
        {
            "figures": g.size(),
            "agree": g["agrees"].sum().astype(int),
            "ratio_min": g["ratio"].min(),
            "ratio_max": g["ratio"].max(),
            "difference_min": g["difference"].min(),
            "difference_max": g["difference"].max(),
        }
    )


def main() -> None:
    df = benchmark()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    summary(df).to_csv(OUT.with_name("summary.csv"))
    state_shares(df).to_csv(OUT.with_name("state_shares.csv"), index=False)
    context().to_csv(OUT.with_name("context.csv"), index=False)
    print(f"{len(df)} published figures; {int(df['agrees'].sum())} agree within tolerance. Written to {OUT.parent}")
    with pd.option_context("display.width", 160, "display.max_rows", 200):
        print(summary(df).to_string())


if __name__ == "__main__":
    main()
