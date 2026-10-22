"""IP RAPID: every Australian patent, trade mark, design and plant breeder's right application, updated weekly.

IP Australia's open data product, the successor to IPGOD (same tables and columns, all four rights in each table, plus
an application date and, for classifications, IP Australia's own technology area). The run takes the current weekly
release, so a rerun brings the corpus up to date.

Raw: the release's zip (R2) and its data dictionary (repo). Processed, typed (dates as dates, ABNs as 11-digit
strings, flags as booleans):

- `application`, `classification`, `description`, `events`, `links`, `party`: the IP RAPID tables as published, every
  right in each, with `ip_right_type` (patent, trade_mark, design, pbr) (R2).
- `<right>_rights`: one row per application of that right: status and key dates; the number of current applicants;
  the first current applicant's party id, name, type, country, state, postcode and ABN; whether any applicant is in
  Australia; whether an attorney or agent acts; the main classification (patents: the first current IPC mark's
  subclass, and IP Australia's technology area; trade marks: the Nice classes, as a count and a list; designs: the
  Locarno class; PBR: the genus). Individuals' names are left out of these (repo) tables; `party` (R2) has them as IP
  Australia publishes them.
- `applicant_year`: applicant (ABN where IP RAPID has one, else party id) by right by financial year: applications
  filed and rights that became enforceable, counted and weighted as IPLORD does (repo).

Useful event types (in `events`): extensions of term for pharmaceutical patents, lapses (renewals not paid),
assignments, registered licences, oppositions and their outcomes, examination requests. The public party data has
no inventors, only applicants, owners, agents and other parties.
"""

from __future__ import annotations

import duckdb

from ..core import CorpusError, Ctx, http_get, unzip_member, unzip_names

PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=iprapid"
RIGHTS = ("patent", "trade_mark", "design", "pbr")
TABLES = {  # member -> table name
    "application.csv": "application",
    "application_classification.csv": "classification",
    "application_description.csv": "description",
    "application_events.csv": "events",
    "application_links.csv": "links",
    "party_activity.csv": "party",
}
DATES = {
    "application_date",
    "earliest_filed_date",
    "priority_date",
    "gained_registration_status_date",
    "gained_enforceable_status_date",
    "enforceable_from_date",
    "deemed_retired_date",
    "classification_date",
    "classification_removal_date",
    "event_effective_date",
    "event_declared_date",
    "link_date",
    "effective_from_date",
    "effective_to_date",
}
BOOLS = {"is_current", "is_founding", "is_standing"}


def _select(columns: list[str]) -> str:
    out = []
    for c in columns:
        q = f'"{c}"'
        if c in DATES:
            out.append(f"try_cast(left({q}, 10) AS DATE) AS {q}")
        elif c in BOOLS:
            out.append(
                f"CASE lower({q}) WHEN 'true' THEN true WHEN '1' THEN true WHEN 'false' THEN false "
                f"WHEN '0' THEN false END AS {q}"
            )
        elif c == "abn":
            out.append(f"nullif(lpad(regexp_replace({q}, '\\.0$', ''), 11, '0'), '00000000000') AS abn")
        else:
            out.append(f"nullif(trim({q}), '') AS {q}")
    return ", ".join(out)


def run(ctx: Ctx) -> None:
    res = http_get(PACKAGE).json()["result"]["resources"]
    zips = [r for r in res if r.get("format", "").upper() == "ZIP"]
    pdfs = [r for r in res if r["url"].lower().endswith(".pdf")]
    if not zips:
        raise CorpusError("iprapid: no ZIP resource on data.gov.au; has the dataset changed?")
    for r in pdfs:
        ctx.fetch(r["url"], r["url"].rsplit("/", 1)[1], keep="repo")
    z = ctx.fetch(zips[0]["url"], "iprapid.zip", keep="r2", force=True)  # weekly: always the current release
    ctx.note(f"iprapid: release of {zips[0].get('last_modified') or zips[0].get('created')}")
    work = ctx.cache / "work"
    work.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit='8GB'; SET preserve_insertion_order=false")
    members = set(unzip_names(z))
    p: dict[str, str] = {}
    for member, name in TABLES.items():
        if member not in members:
            raise CorpusError(f"iprapid: {member} is missing from the zip; has the release's layout changed?")
        out = ctx.cache / "processed" / f"{name}.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        csv = unzip_member(z, member, work)
        src = f"read_csv('{csv}', all_varchar=true, header=true, quote='\"', escape='\"', strict_mode=false)"
        cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()]
        con.execute(f"COPY (SELECT {_select(cols)} FROM {src}) TO '{out}' (FORMAT parquet, COMPRESSION zstd)")
        csv.unlink()
        rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
        ctx.keep_table(out, name, rows, cols, keep="r2", describe=f"IP RAPID {member}, every right")
        p[name] = str(out)
    for right in RIGHTS:
        _rights(ctx, con, right, p)
    _applicant_year(ctx, con, p)


def _rights(ctx: Ctx, con, right: str, p: dict[str, str]) -> None:
    cls = {
        "patent": "classification_system = 'ipc_mark' AND is_current",
        "trade_mark": "classification_system = 'nice' AND is_current",
        "design": "classification_system = 'locarno' AND is_current",
        "pbr": "classification_system = 'genus_species' AND is_current",
    }[right]
    main_class = {
        "patent": "replace(left(classification, 4), ' ', '')",
        "trade_mark": "classification",
        "design": "left(classification, 2)",
        "pbr": "split_part(classification, ' ', 1)",
    }[right]
    out = ctx.cache / "processed" / f"{right}_rights.parquet"
    con.execute(f"""
    COPY (
      WITH app AS (SELECT * FROM '{p["application"]}' WHERE ip_right_type = '{right}'),
      party AS (SELECT * FROM '{p["party"]}' WHERE ip_right_type = '{right}' AND is_current IS NOT false),
      applicants AS (
        SELECT application_number, party_id, party_name, party_type, country_code, state_code, post_code, abn,
               row_number() OVER (PARTITION BY application_number
                                  ORDER BY is_founding DESC NULLS LAST, effective_from_date, party_id) AS k
        FROM party WHERE party_role_category IN ('applicant', 'owner')),
      a AS (
        SELECT application_number, count(DISTINCT party_id) AS applicant_count,
               bool_or(country_code = 'au') AS any_applicant_in_australia,
               any_value(abn ORDER BY k) FILTER (WHERE abn IS NOT NULL) AS any_applicant_abn
        FROM applicants GROUP BY 1),
      first AS (SELECT * FROM applicants WHERE k = 1),
      agents AS (
        SELECT application_number, count(DISTINCT party_id) AS agent_count
        FROM party WHERE party_role_category = 'applicant_agent' GROUP BY 1),
      c AS (
        SELECT application_number,
               any_value({main_class} ORDER BY classification_importance NULLS LAST, classification) AS main_class,
               any_value(classification_area ORDER BY classification_importance NULLS LAST, classification)
                 AS main_area,
               count(DISTINCT {main_class}) AS class_count,
               string_agg(DISTINCT {main_class}, ' ' ORDER BY {main_class}) AS classes
        FROM '{p["classification"]}' WHERE ip_right_type = '{right}' AND {cls} GROUP BY 1)
      SELECT app.application_number, app.ip_right_sub_type, app.status, app.application_date,
             app.earliest_filed_date, app.priority_date, app.gained_registration_status_date,
             app.gained_enforceable_status_date, app.enforceable_from_date, app.deemed_retired_date,
             coalesce(a.applicant_count, 0) AS applicant_count,
             first.party_id AS applicant_party_id,
             CASE WHEN first.party_type = 'individual' THEN NULL ELSE first.party_name END AS applicant_name,
             first.party_type AS applicant_type, first.country_code AS applicant_country,
             first.state_code AS applicant_state, first.post_code AS applicant_postcode,
             first.abn AS applicant_abn, a.any_applicant_abn,
             coalesce(a.any_applicant_in_australia, false) AS any_applicant_in_australia,
             coalesce(agents.agent_count, 0) > 0 AS has_agent,
             c.main_class, c.main_area, c.class_count, c.classes
      FROM app
      LEFT JOIN a USING (application_number)
      LEFT JOIN first USING (application_number)
      LEFT JOIN agents USING (application_number)
      LEFT JOIN c USING (application_number)
      ORDER BY app.earliest_filed_date, app.application_number
    ) TO '{out}' (FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 9)""")
    rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{out}'").fetchall()]
    ctx.keep_table(
        out,
        f"{right}_rights",
        rows,
        cols,
        describe="One row per application: status, dates, first current applicant, attorney use, classes",
    )


def _applicant_year(ctx: Ctx, con, p: dict[str, str]) -> None:
    """Applicant by financial year by right: applications filed and rights that became enforceable, as in IPLORD.

    An applicant is its ABN where IP RAPID has one, else its party id. Each application counts once for each of its
    founding applicants (`filed`), and 1/n for each of n (`filed_weighted`), as IPLORD does. Financial years end on
    30 June and are labelled by the year they end.
    """
    out = ctx.cache / "processed/applicant_year.parquet"
    fy = "CAST(year({d}) + CASE WHEN month({d}) > 6 THEN 1 ELSE 0 END AS INTEGER)"
    con.execute(f"""
    COPY (
      WITH x AS (
        SELECT a.ip_right_type, a.application_number, coalesce(pa.abn, pa.party_id) AS applicant_id,
               CASE WHEN pa.abn IS NULL THEN 'party_id' ELSE 'abn' END AS applicant_id_type,
               pa.party_type, pa.country_code, pa.state_code, pa.post_code,
               a.earliest_filed_date, a.gained_enforceable_status_date
        FROM '{p["application"]}' a
        JOIN '{p["party"]}' pa USING (ip_right_type, application_number)
        WHERE pa.party_role_category = 'applicant' AND pa.is_founding),
      n AS (SELECT ip_right_type, application_number, count(DISTINCT applicant_id) AS k FROM x GROUP BY 1, 2),
      y AS (
        SELECT x.*, n.k, {fy.format(d="earliest_filed_date")} AS filed_fy,
               {fy.format(d="gained_enforceable_status_date")} AS enforceable_fy
        FROM x JOIN n USING (ip_right_type, application_number)),
      ids AS (
        SELECT applicant_id, applicant_id_type, any_value(party_type) AS party_type,
               mode(country_code) AS country_code, mode(state_code) AS state_code, mode(post_code) AS post_code
        FROM y GROUP BY 1, 2),
      filed AS (
        SELECT applicant_id, applicant_id_type, ip_right_type, filed_fy AS financial_year,
               count(DISTINCT application_number) AS filed, sum(1.0 / k) AS filed_weighted
        FROM y WHERE filed_fy IS NOT NULL GROUP BY 1, 2, 3, 4),
      enf AS (
        SELECT applicant_id, applicant_id_type, ip_right_type, enforceable_fy AS financial_year,
               count(DISTINCT application_number) AS became_enforceable, sum(1.0 / k) AS became_enforceable_weighted
        FROM y WHERE enforceable_fy IS NOT NULL GROUP BY 1, 2, 3, 4)
      SELECT applicant_id, applicant_id_type, ids.party_type, ids.country_code, ids.state_code, ids.post_code,
             ip_right_type, financial_year,
             coalesce(filed, 0) AS filed, coalesce(filed_weighted, 0) AS filed_weighted,
             coalesce(became_enforceable, 0) AS became_enforceable,
             coalesce(became_enforceable_weighted, 0) AS became_enforceable_weighted
      FROM filed FULL JOIN enf USING (applicant_id, applicant_id_type, ip_right_type, financial_year)
      JOIN ids USING (applicant_id, applicant_id_type)
      ORDER BY applicant_id, ip_right_type, financial_year
    ) TO '{out}' (FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 9)""")
    rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{out}'").fetchall()]
    ctx.keep_table(
        out,
        "applicant_year",
        rows,
        cols,
        describe="Applicant (ABN or party id) by right by financial year: filed and became enforceable",
    )
