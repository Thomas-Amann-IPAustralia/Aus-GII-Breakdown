"""A fresh IP RAPID release, read raw, against OQ6, OQ7 and OQ13 (ADR 0027): is each one a misclassification?

    uv run python -m audit.recheck --work <dir>        # downloads about 1.4 GB; minutes

Independent of the corpus and the lenses: it takes the current release's zip from data.gov.au, keeps four of its CSVs
as Parquet (every column as text, as published) in `<work>`, and writes each check's table to
`analysis/audit/output/recheck/`. `docs/recheck-oq6-oq7-oq13.md` quotes them. The ASIC company register
(`asic/companies`, from the corpus) is the one other source, used only to ask whether companies without an ABN in IP
RAPID have one.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import duckdb

from corpus import path as corpus_path
from corpus.core import http_get

PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=iprapid"
MEMBERS = {
    "a": "application.csv",
    "l": "application_links.csv",
    "p": "party_activity.csv",
    "e": "application_events.csv",
}
OUT = Path(__file__).resolve().parent / "output" / "recheck"

D = "left({c}, 10)::DATE"
FY = "CAST(year({d}) + (month({d}) > 6)::INT AS INT)"

SETUP = f"""
CREATE TABLE conv AS
    SELECT DISTINCT application_number FROM l WHERE ip_right_type = 'trade_mark' AND link_type = 'convention_priority';
CREATE TABLE tm AS
WITH ev AS (
    SELECT application_number,
           min({D.format(c="event_effective_date")}) FILTER (event_category = 'exam_request_expedite') AS exp_d
    FROM e WHERE ip_right_type = 'trade_mark' GROUP BY 1),
lk AS (
    SELECT application_number, bool_or(link_type = 'madrid_import') AS madrid
    FROM l WHERE ip_right_type = 'trade_mark' GROUP BY 1),
fo AS (
    SELECT application_number, bool_or(country_code = 'au') AS au
    FROM p WHERE ip_right_type = 'trade_mark' AND party_role_category = 'applicant' AND is_founding = 'true'
    GROUP BY 1)
SELECT a.application_number, try_cast(a.application_number AS BIGINT) AS num,
       {D.format(c="a.application_date")} AS app_d, a.status, coalesce(lk.madrid, false) AS madrid, fo.au,
       conv.application_number IS NOT NULL AS priority, ev.exp_d
FROM a LEFT JOIN ev USING (application_number) LEFT JOIN lk USING (application_number)
LEFT JOIN fo USING (application_number) LEFT JOIN conv USING (application_number)
WHERE a.ip_right_type = 'trade_mark';
-- Australian organisations' applications: founding applicants in Australia that are organisations (U45's base)
CREATE TABLE ao AS
WITH f AS (
    SELECT ip_right_type, application_number, list(DISTINCT party_id) AS ids,
           bool_or(regexp_matches(upper(party_name), '\\bP(TY|ROPRIETARY)\\b')) AS pty,
           any_value(party_name) AS name
    FROM p WHERE party_role_category = 'applicant' AND is_founding = 'true' AND country_code = 'au'
                 AND party_type = 'organisation'
    GROUP BY ALL),
ab AS (
    SELECT ip_right_type, application_number,
           bool_or(nullif(trim(abn), '') IS NOT NULL) FILTER (party_role_category = 'applicant') AS has_abn,
           bool_or(nullif(trim(abn), '') IS NOT NULL) FILTER (party_role_category NOT LIKE '%agent%') AS any_role_abn
    FROM p GROUP BY ALL),
seen AS (
    SELECT party_id, min({D.format(c="a.application_date")}) AS first_d
    FROM p JOIN a USING (ip_right_type, application_number) WHERE party_role_category = 'applicant' GROUP BY 1)
SELECT f.ip_right_type, f.application_number, f.pty, f.name, coalesce(ab.has_abn, false) AS has_abn,
       coalesce(ab.any_role_abn, false) AS any_role_abn,
       {D.format(c="a.application_date")} AS app_d, {FY.format(d=D.format(c="a.application_date"))} AS fy,
       (SELECT min(seen.first_d) FROM unnest(f.ids) u(id) JOIN seen ON seen.party_id = u.id) AS first_d
FROM f JOIN a USING (ip_right_type, application_number) LEFT JOIN ab USING (ip_right_type, application_number);
"""

CHECKS = {
    # OQ6: every examination event on trade marks, by month, across the move between systems
    "oq6_exam_events_by_month": """
        PIVOT (SELECT left(event_effective_date, 7) AS month, event_type FROM e
               WHERE ip_right_type = 'trade_mark' AND event_category LIKE 'exam%'
                 AND event_effective_date BETWEEN '2018-05' AND '2019-05')
        ON event_type USING count(*) ORDER BY month""",
    "oq6_cutover_days": """
        PIVOT (SELECT left(event_effective_date, 10) AS day, event_type FROM e
               WHERE ip_right_type = 'trade_mark' AND event_type IN ('exam_request', 'expedited_exam_request')
                 AND event_effective_date BETWEEN '2018-11-01' AND '2018-11-30')
        ON event_type USING count(*) ORDER BY day""",
    "oq6_requests_by_month_and_priority": """
        SELECT strftime(exp_d, '%Y-%m') AS month, count(*) FILTER (NOT priority) AS without_priority,
               count(*) FILTER (priority) AS with_priority,
               count(*) FILTER (priority AND madrid) AS with_priority_madrid
        FROM tm WHERE exp_d BETWEEN '2018-01-01' AND '2019-12-31' GROUP BY 1 ORDER BY 1""",
    "oq6_share_by_fy": f"""
        SELECT {FY.format(d="app_d")} AS fy, count(*) AS marks,
               round(100 * avg((exp_d IS NOT NULL)::INT), 2) AS pct_all,
               round(100 * avg((exp_d IS NOT NULL)::INT) FILTER (NOT priority), 2) AS pct_without_priority,
               round(100 * avg((exp_d IS NOT NULL)::INT) FILTER (priority), 2) AS pct_with_priority,
               round(100 * avg((exp_d IS NOT NULL)::INT) FILTER (NOT priority AND au), 2)
                   AS pct_without_priority_australian,
               round(100 * avg(priority::INT), 1) AS pct_claiming_priority
        FROM tm WHERE app_d BETWEEN '1996-07-01' AND '2026-06-30' GROUP BY 1 ORDER BY 1""",
    "oq6_share_by_group_and_side": """
        SELECT CASE WHEN madrid THEN 'madrid' WHEN au THEN 'direct, Australian' ELSE 'direct, overseas' END AS mark,
               priority, app_d >= DATE '2018-11-13' AS after_move, count(*) AS marks,
               round(100 * avg((exp_d IS NOT NULL)::INT), 2) AS pct_expedite
        FROM tm WHERE app_d BETWEEN '2016-07-01' AND '2021-06-30' GROUP BY ALL ORDER BY ALL""",
    # OQ13: trade marks by calendar year, and where in the numbering the 2018 shortfall could sit
    "oq13_by_year": """
        SELECT year(app_d) AS year, count(*) AS marks, count(*) FILTER (madrid) AS madrid,
               count(*) FILTER (NOT madrid) AS direct
        FROM tm WHERE year(app_d) BETWEEN 2015 AND 2020 GROUP BY 1 ORDER BY 1""",
    "oq13_madrid_by_month": """
        SELECT strftime(app_d, '%Y-%m') AS month, count(*) FILTER (madrid) AS madrid,
               count(*) FILTER (NOT madrid) AS direct
        FROM tm WHERE app_d BETWEEN '2017-07-01' AND '2019-06-30' GROUP BY 1 ORDER BY 1""",
    "oq13_numbers_by_block": """
        SELECT num // 10000 * 10000 AS block_from, count(*) AS present, 10000 - count(*) AS missing,
               count(*) FILTER (madrid) AS madrid, approx_quantile(app_d, 0.5) AS median_filing_date
        FROM tm WHERE num BETWEEN 1800000 AND 2079999 GROUP BY 1 ORDER BY 1""",
    "oq13_longest_gaps": """
        WITH s AS (SELECT num, lead(num) OVER (ORDER BY num) AS nx FROM tm WHERE num BETWEEN 1800000 AND 2140000)
        SELECT num AS last_before, nx AS first_after, nx - num - 1 AS numbers_missing
        FROM s WHERE nx - num - 1 >= 20 ORDER BY numbers_missing DESC LIMIT 10""",
    "oq13_gap_anywhere": """
        SELECT 'application' AS tbl, count(*) AS rows FROM a
            WHERE try_cast(application_number AS BIGINT) BETWEEN 1978060 AND 1980352
        UNION ALL SELECT 'events', count(*) FROM e
            WHERE try_cast(application_number AS BIGINT) BETWEEN 1978060 AND 1980352
        UNION ALL SELECT 'party', count(*) FROM p
            WHERE try_cast(application_number AS BIGINT) BETWEEN 1978060 AND 1980352
        UNION ALL SELECT 'links to the range', count(*) FROM l
            WHERE try_cast(linked_application_number AS BIGINT) BETWEEN 1978060 AND 1980352
              AND ip_right_type = 'trade_mark' AND linked_application_country = 'au'""",
    # OQ7: the ABN on Australian organisations' applications
    "oq7_abn_by_fy": """
        SELECT ip_right_type, fy, count(*) AS applications, round(100 * avg(has_abn::INT), 1) AS pct_abn,
               round(100 * avg(has_abn::INT) FILTER (first_d >= app_d - INTERVAL 30 DAY), 1) AS pct_abn_new_applicant,
               round(100 * avg(has_abn::INT) FILTER (first_d < app_d - INTERVAL 30 DAY), 1)
                   AS pct_abn_earlier_applicant,
               round(100 * avg(has_abn::INT) FILTER (pty), 1) AS pct_abn_pty_companies
        FROM ao WHERE fy BETWEEN 2020 AND 2027 AND ip_right_type IN ('trade_mark', 'design', 'patent')
        GROUP BY ALL ORDER BY ALL""",
    "oq7_tm_abn_by_month": """
        SELECT strftime(app_d, '%Y-%m') AS month, count(*) AS applications,
               round(100 * avg(has_abn::INT), 1) AS pct_abn,
               round(100 * avg(has_abn::INT) FILTER (first_d >= app_d - INTERVAL 30 DAY), 1) AS pct_abn_new_applicant,
               round(100 * avg(has_abn::INT) FILTER (first_d < app_d - INTERVAL 30 DAY), 1) AS pct_abn_earlier_applicant
        FROM ao WHERE ip_right_type = 'trade_mark' AND app_d >= DATE '2023-07-01' GROUP BY 1 ORDER BY 1""",
    "oq7_abn_on_any_role": """
        SELECT fy, round(100 * avg(has_abn::INT), 1) AS pct_abn_applicant,
               round(100 * avg(any_role_abn::INT), 1) AS pct_abn_any_role_but_agents
        FROM ao WHERE ip_right_type = 'trade_mark' AND fy BETWEEN 2020 AND 2027 GROUP BY 1 ORDER BY 1""",
    "oq7_tm_australian_filers_by_type": f"""
        SELECT {FY.format(d=D.format(c="a.application_date"))} AS fy, party_type,
               count(DISTINCT application_number) AS trade_marks
        FROM p JOIN a USING (ip_right_type, application_number)
        WHERE p.ip_right_type = 'trade_mark' AND party_role_category = 'applicant' AND is_founding = 'true'
          AND country_code = 'au' AND a.application_date >= '2019-07-01'
        GROUP BY ALL ORDER BY ALL""",
    "oq7_party_abn_consistency": """
        SELECT count(*) AS parties, count(*) FILTER (abns > 0 AND blank > 0) AS with_abn_on_some_rows_only
        FROM (SELECT party_id, count(DISTINCT nullif(trim(abn), '')) AS abns,
                     count(*) FILTER (nullif(trim(abn), '') IS NULL) AS blank
              FROM p WHERE party_role_category = 'applicant' AND party_type = 'organisation' GROUP BY 1)""",
    "oq7_tm_pty_in_asic": """
        SELECT fy, has_abn AS abn_in_iprapid, count(*) AS applications,
               round(100 * avg((c.k IS NOT NULL)::INT), 1) AS pct_name_in_asic_with_abn,
               round(100 * avg((c.registered >= DATE '2024-07-01')::INT) FILTER (c.k IS NOT NULL), 1)
                   AS pct_company_registered_since_jul_2024
        FROM pty LEFT JOIN asic c USING (k) WHERE fy BETWEEN 2022 AND 2027 GROUP BY ALL ORDER BY ALL""",
    "oq7_tm_pty_by_company_age": """
        SELECT fy, CASE WHEN pty.app_d - c.registered < 365 THEN 'under a year old' ELSE 'older' END AS company,
               count(*) AS applications, round(100 * avg(has_abn::INT), 1) AS pct_abn
        FROM pty JOIN asic c USING (k) WHERE c.registered <= pty.app_d AND fy BETWEEN 2022 AND 2027
        GROUP BY ALL ORDER BY 2, 1""",
}

# A company name, normalised for an exact match: case, punctuation, "Limited", "The" and "Proprietary" set aside
NORM = (
    "regexp_replace(trim(regexp_replace(regexp_replace(upper({c}), '\\bPROPRIETARY\\b', 'PTY', 'g'), "
    "'\\bLIMITED\\b|\\bLTD\\b|\\bTHE\\b|[^A-Z0-9 ]', '', 'g')), '\\s+', ' ', 'g')"
)


def fetch(work: Path) -> None:
    res = http_get(PACKAGE).json()["result"]["resources"]
    z = next(r for r in res if r.get("format", "").upper() == "ZIP")
    print("release:", z.get("last_modified") or z.get("created"))
    zp = work / "iprapid.zip"
    subprocess.run(["curl", "-sS", "-L", "-o", str(zp), z["url"]], check=True)
    con = duckdb.connect()
    for member in MEMBERS.values():
        subprocess.run(["unzip", "-o", "-q", str(zp), member, "-d", str(work)], check=True)
        csv = work / member
        src = f"read_csv('{csv}', all_varchar=true, header=true, quote='\"', escape='\"', strict_mode=false)"
        con.execute(f"COPY (SELECT * FROM {src}) TO '{work / member.replace('.csv', '.parquet')}' (FORMAT parquet)")
        csv.unlink()
    zp.unlink()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True, help="a directory for the release (about 2 GB)")
    ap.add_argument("--no-fetch", action="store_true", help="use the Parquet files already in --work")
    args = ap.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    if not args.no_fetch:
        fetch(args.work)
    con = duckdb.connect(str(args.work / "recheck.duckdb"))
    con.execute("SET memory_limit='8GB'")
    for view, member in MEMBERS.items():
        pq = args.work / member.replace(".csv", ".parquet")
        con.execute(f"CREATE OR REPLACE VIEW {view} AS SELECT * FROM '{pq}'")
    for t in ("conv", "tm", "ao", "asic", "pty"):
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.execute(SETUP)
    con.execute(f"""
        CREATE TABLE asic AS SELECT {NORM.format(c="name")} AS k, min(registered) AS registered
        FROM '{corpus_path("asic", "companies")}' WHERE nullif(trim(abn), '') IS NOT NULL GROUP BY 1;
        CREATE TABLE pty AS SELECT *, {NORM.format(c="name")} AS k FROM ao WHERE ip_right_type = 'trade_mark' AND pty;
    """)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, q in CHECKS.items():
        df = con.execute(q).df()
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows")


if __name__ == "__main__":
    main()
