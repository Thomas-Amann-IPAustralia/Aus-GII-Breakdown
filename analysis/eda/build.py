"""Build the lens tables: one analysis-ready table per unit of analysis, written to `analysis/eda/data/` (gitignored).

    uv run python -m eda.build              # every lens (about two minutes once the R2 tables are cached)
    uv run python -m eda.build firms        # one lens

| Lens | One row per | Built from |
|---|---|---|
| `rights` | IP right (patent, trade mark, design, plant breeder's right) | `iprapid/*_rights` |
| `firms` | ABN in any IP, R&D, procurement or tax source | `linkage/abn_spine`, `rights`, `rdti`, `ato_ctt` |
| `regions` | Postal area (the ABS's version of a postcode) | `abs_regions`, `abs_census`, `abr`, `rights`, `firms` |
| `national` | Country, year and indicator | `wdi/panel`, `wipo_ipstats/office_origin` |

Every column is described, in plain English, in `analysis/eda/variables.yaml`. Derived columns are defined here and
nowhere else, so a reader can check exactly how each was made.
"""

from __future__ import annotations

import sys
import time

import pycountry

from .data import LENS_DIR, connect, lens_table, resolve

# Filing counts for places use the ten latest complete Australian financial years (July to June; FY2026 = Jul 2025
# to Jun 2026). IP RAPID lists applications from filing, before publication: patents filed per year show no drop-off
# in FY2025 or FY2026 (35,065 and 41,257). Stage 1 checks this again.
WINDOW = (2017, 2026)
TODAY = "2026-10-22"  # the corpus build date, so ages do not change with the day the notebook is run

OECD = (
    "AUS AUT BEL CAN CHL COL CRI CZE DNK EST FIN FRA DEU GRC HUN ISL IRL ISR ITA JPN KOR LVA LTU LUX MEX NLD NZL NOR "
    "POL PRT SVK SVN ESP SWE CHE TUR GBR USA"
).split()


def _postcode(col: str) -> str:
    """A 4-digit Australian postcode from free text ('800' becomes '0800'), or NULL."""
    return (
        f"CASE WHEN regexp_full_match(trim({col}), '\\d{{4}}') THEN trim({col}) "
        f"WHEN regexp_full_match(trim({col}), '\\d{{3}}') THEN '0' || trim({col}) END"
    )


def _fy(col: str) -> str:
    """The Australian financial year (ending 30 June) of a date."""
    return f"(year({col}) + CASE WHEN month({col}) >= 7 THEN 1 ELSE 0 END)"


def rights_sql() -> str:
    parts = []
    for kind in ("patent", "trade_mark", "design", "pbr"):
        parts.append(f"""
        SELECT
            application_number,
            '{kind}' AS ip_right_type,
            ip_right_sub_type,
            status,
            application_date,
            {_fy("application_date")} AS filing_fy,
            priority_date,
            gained_registration_status_date AS registered_date,
            date_diff('day', application_date, gained_registration_status_date) AS days_to_registration,
            deemed_retired_date AS retired_date,
            applicant_count,
            applicant_type,
            applicant_country,
            applicant_state,
            CASE WHEN applicant_country = 'au' THEN {_postcode("applicant_postcode")} END AS applicant_postcode,
            any_applicant_abn AS applicant_abn,
            any_applicant_abn IS NOT NULL AS has_abn,
            any_applicant_in_australia AS australian_applicant,
            has_agent,
            main_class,
            main_area,
            class_count
        FROM {{iprapid/{kind}_rights}}""")
    return " UNION ALL ".join(parts)


def firms_sql() -> str:
    return f"""
    WITH ip AS (
        SELECT applicant_abn AS abn,
               count(*) FILTER (ip_right_type = 'patent') AS n_patents,
               count(*) FILTER (ip_right_type = 'trade_mark') AS n_trade_marks,
               count(*) FILTER (ip_right_type = 'design') AS n_designs
        FROM {lens_table("rights")} WHERE applicant_abn IS NOT NULL GROUP BY 1
    ),
    rd_year AS (  -- one value per ABN and year (a few claims are reported twice)
        SELECT abn, income_year, max(rd_expenditure) AS rd FROM {{rdti/entities}} WHERE abn IS NOT NULL GROUP BY 1, 2
    ),
    rd AS (
        SELECT abn, count(*) AS rdti_years, avg(rd) AS rd_expenditure_mean, arg_max(rd, income_year) AS rd_latest
        FROM rd_year GROUP BY 1
    ),
    tax_year AS (
        SELECT abn, income_year, max(total_income) AS income FROM {{ato_ctt/entities}}
        WHERE abn IS NOT NULL GROUP BY 1, 2
    ),
    tax AS (
        SELECT abn, count(*) AS ato_ctt_years, arg_max(income, income_year) AS total_income_latest
        FROM tax_year GROUP BY 1
    ),
    place AS (
        SELECT p.poa_code, p.ra_name, s.value AS irsad_decile
        FROM {{abs_regions/poa}} p
        LEFT JOIN {{abs_regions/seifa_poa}} s
          ON s.postal_area_code = p.poa_code AND s.index_type = 'IRSAD' AND s.measure = 'RWAD'
    )
    SELECT
        s.abn,
        s.entity_type_text AS entity_type,
        CASE
            WHEN s.entity_type_text = 'Australian Private Company' THEN 'Private company'
            WHEN s.entity_type_text = 'Australian Public Company' THEN 'Public company'
            WHEN s.entity_type_text = 'Individual/Sole Trader' THEN 'Sole trader'
            WHEN s.entity_type_text ILIKE '%superannuation%' THEN 'Super fund'
            WHEN s.entity_type_text ILIKE '%government%' OR s.entity_type_text ILIKE '%statutory%' THEN 'Government'
            WHEN s.entity_type_text ILIKE '%trust%' THEN 'Trust'
            WHEN s.entity_type_text ILIKE '%partnership%' THEN 'Partnership'
            WHEN s.entity_type_text IS NULL THEN NULL
            ELSE 'Other'
        END AS entity_group,
        s.abn_status = 'ACT' AS abn_active,
        s.gst_status = 'ACT' AS gst_registered,
        s.state,
        {_postcode("s.postcode")} AS postcode,
        place.ra_name AS remoteness,
        place.irsad_decile,
        s.asic_type,
        s.first_seen,
        round(date_diff('day', s.first_seen, DATE '{TODAY}') / 365.25, 1) AS age_years,
        s.in_iprapid_patent, s.in_iprapid_trade_mark, s.in_iprapid_design,
        s.in_rdti, s.in_austender, s.in_ato_ctt,
        s.patent_first_fy, s.trade_mark_first_fy, s.design_first_fy,
        s.ip_filed_total,
        coalesce(ip.n_patents, 0) AS n_patents,
        coalesce(ip.n_trade_marks, 0) AS n_trade_marks,
        coalesce(ip.n_designs, 0) AS n_designs,
        coalesce(rd.rdti_years, 0) AS rdti_years,
        rd.rd_expenditure_mean,
        rd.rd_latest,
        coalesce(tax.ato_ctt_years, 0) AS ato_ctt_years,
        tax.total_income_latest,
        s.austender_contracts,
        s.austender_value
    FROM {{linkage/abn_spine}} s
    LEFT JOIN ip USING (abn)
    LEFT JOIN rd USING (abn)
    LEFT JOIN tax USING (abn)
    LEFT JOIN place ON place.poa_code = {_postcode("s.postcode")}
    """


def regions_sql() -> str:
    lo, hi = WINDOW
    seifa = ",\n        ".join(
        f"max(value) FILTER (index_type = '{i}' AND measure = '{m}') AS {i.lower()}_{n}"
        for i in ("IRSAD", "IRSD", "IER", "IEO")
        for m, n in (("SCORE", "score"), ("RWAD", "decile"))
    )
    return f"""
    WITH seifa AS (
        SELECT postal_area_code AS poa_code,
        {seifa}
        FROM {{abs_regions/seifa_poa}} GROUP BY 1
    ),
    census AS (
        SELECT replace(POA_CODE_2021, 'POA', '') AS poa_code,
               Median_age_persons AS median_age,
               Median_tot_prsnl_inc_weekly AS median_personal_income_weekly,
               Median_tot_hhd_inc_weekly AS median_household_income_weekly,
               Median_rent_weekly AS median_rent_weekly,
               Average_household_size AS average_household_size
        FROM {{abs_census/poa_g02}}
    ),
    abr AS (
        SELECT postcode AS poa_code,
               count(*) FILTER (abn_status = 'ACT') AS active_abns,
               count(*) FILTER (abn_status = 'ACT' AND gst_status = 'ACT') AS active_gst_abns
        FROM {{abr/abns}} GROUP BY 1
    ),
    ip AS (
        SELECT applicant_postcode AS poa_code,
               count(*) FILTER (ip_right_type = 'patent') AS patents,
               count(*) FILTER (ip_right_type = 'trade_mark') AS trade_marks,
               count(*) FILTER (ip_right_type = 'design') AS designs
        FROM {lens_table("rights")}
        WHERE applicant_postcode IS NOT NULL AND filing_fy BETWEEN {lo} AND {hi}
        GROUP BY 1
    ),
    firms AS (
        SELECT postcode AS poa_code,
               count(*) FILTER (abn_active AND ip_filed_total > 0) AS ip_filing_firms,
               count(*) FILTER (abn_active AND in_rdti) AS rdti_firms,
               count(*) FILTER (abn_active AND in_rdti AND ip_filed_total = 0) AS rdti_firms_no_ip
        FROM {lens_table("firms")} GROUP BY 1
    )
    SELECT
        p.poa_code,
        p.state_name AS state,
        p.ra_name AS remoteness,
        p.share_major_cities,
        p.persons,
        seifa.* EXCLUDE (poa_code),
        census.* EXCLUDE (poa_code),
        coalesce(abr.active_abns, 0) AS active_abns,
        coalesce(abr.active_gst_abns, 0) AS active_gst_abns,
        coalesce(ip.patents, 0) AS patents,
        coalesce(ip.trade_marks, 0) AS trade_marks,
        coalesce(ip.designs, 0) AS designs,
        coalesce(firms.ip_filing_firms, 0) AS ip_filing_firms,
        coalesce(firms.rdti_firms, 0) AS rdti_firms,
        coalesce(firms.rdti_firms_no_ip, 0) AS rdti_firms_no_ip,
        1000.0 * coalesce(ip.patents, 0) / nullif(abr.active_gst_abns, 0) AS patents_per_1k_businesses,
        1000.0 * coalesce(ip.trade_marks, 0) / nullif(abr.active_gst_abns, 0) AS trade_marks_per_1k_businesses,
        1000.0 * coalesce(ip.designs, 0) / nullif(abr.active_gst_abns, 0) AS designs_per_1k_businesses
    FROM {{abs_regions/poa}} p
    LEFT JOIN seifa USING (poa_code)
    LEFT JOIN census USING (poa_code)
    LEFT JOIN abr USING (poa_code)
    LEFT JOIN ip USING (poa_code)
    LEFT JOIN firms USING (poa_code)
    WHERE p.ra_name NOT IN ('Outside Australia', 'Migratory - Offshore - Shipping (WA)')
      AND p.ra_name NOT LIKE 'No usual address%'
    """


def national_sql() -> str:
    iso3 = {c.alpha_2: c.alpha_3 for c in pycountry.countries}
    pairs = ", ".join(f"('{a2}', '{a3}')" for a2, a3 in sorted(iso3.items()))
    oecd = ", ".join(f"'{c}'" for c in OECD)
    wipo = {
        10: ("WIPO.PAT.APP", "Patent applications filed worldwide by residents (all offices)"),
        23: ("WIPO.PAT.GRANT", "Patent grants received worldwide by residents (all offices)"),
        48: ("WIPO.TM.CLASS", "Trade mark applications by residents, counted in classes (all offices)"),
        68: ("WIPO.DES.COUNT", "Industrial design applications by residents, counted in designs (all offices)"),
    }
    cases = " ".join(f"WHEN {k} THEN '{c}'" for k, (c, _) in wipo.items())
    names = " ".join(f"WHEN {k} THEN '{n}'" for k, (_, n) in wipo.items())
    return f"""
    WITH iso(a2, a3) AS (VALUES {pairs}),
    wdi AS (
        SELECT p.iso3, p.country, p.year, p.indicator, p.indicator_name, p.value, 'WDI' AS source
        FROM {{wdi/panel}} p JOIN {{wdi/countries}} c ON c.iso3 = p.iso3
        WHERE NOT c.aggregate
    ),
    wipo AS (
        SELECT iso.a3 AS iso3, any_value(o.origin) AS country, o.year,
               CASE o.indicator_id {cases} END AS indicator,
               CASE o.indicator_id {names} END AS indicator_name,
               sum(o.value) AS value, 'WIPO' AS source
        FROM {{wipo_ipstats/office_origin}} o JOIN iso ON iso.a2 = o.origin_code
        WHERE o.indicator_id IN ({", ".join(map(str, wipo))}) AND o.breakdown IS NULL
        GROUP BY iso.a3, o.year, o.indicator_id
    )
    SELECT *, iso3 IN ({oecd}) AS oecd, iso3 = 'AUS' AS australia
    FROM (SELECT * FROM wdi UNION ALL SELECT * FROM wipo)
    """


LENSES = {"rights": rights_sql, "firms": firms_sql, "regions": regions_sql, "national": national_sql}
ORDER = ["rights", "firms", "regions", "national"]  # firms and regions read the lenses before them


def build(name: str) -> None:
    """Write one lens table, atomically, and print its size."""
    LENS_DIR.mkdir(parents=True, exist_ok=True)
    out, tmp = LENS_DIR / f"{name}.parquet", LENS_DIR / f"{name}.parquet.tmp"
    t0 = time.time()
    con = connect()
    con.execute(f"COPY ({resolve(LENSES[name]())}) TO '{tmp}' (FORMAT parquet, COMPRESSION zstd)")
    tmp.replace(out)
    rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchall()[0][0]
    cols = len(con.sql(f"SELECT * FROM '{out}' LIMIT 0").columns)
    print(f"{name}: {rows:,} rows, {cols} columns, {out.stat().st_size / 1e6:.1f} MB, {time.time() - t0:.0f} s")


def main(argv: list[str]) -> None:
    names = argv or ORDER
    unknown = set(names) - set(LENSES)
    if unknown:
        sys.exit(f"unknown lens: {', '.join(sorted(unknown))} (choose from {', '.join(ORDER)})")
    for name in ORDER:
        if name in names:
            build(name)


if __name__ == "__main__":
    main(sys.argv[1:])
