"""IPGOD 2022: every Australian patent, trade mark, design and plant breeder's right application to early 2022.

Raw: the release's zip (R2) and its data dictionary (repo). Processed, one Parquet table per IPGOD table (R2), typed:
dates as dates, ABNs as 11-digit strings, flags as booleans. Then one summary per right type, a row per application
with its applicants and attorneys reduced to a few columns (repo where it fits):

- `<right>_application`, `_classification`, `_description`, `_events`, `_links`, `_party`: the IPGOD tables as published
  (right is patent, trade_mark, design or pbr).
- `<right>_rights`: one row per application: status and key dates; the number of current applicants; the first current
  applicant's party id, name, type, country, state, postcode and ABN; whether any applicant is in Australia; whether an
  attorney or agent acts; the main classification (patents: the first current IPC mark's four-character class;
  trade marks: the Nice classes, as a count and a list; designs: the Locarno class; PBR: the genus). Individuals'
  names are left out of these (repo) tables; the `_party` tables (R2) have them as IP Australia publishes them.
- `applicant_year`: applicant (ABN where IPGOD has one, else party id) by right by financial year: applications filed
  and rights that became enforceable, counted and weighted as IPLORD does. Unlike IPLORD 2020, it covers patents, and
  runs to early 2022.

IPGOD's public party data has no inventors, only applicants, owners, agents and other parties.
"""

from __future__ import annotations

import duckdb

from ..core import CorpusError, Ctx, unzip_member, unzip_names

ZIP = "https://data.gov.au/data/dataset/49017fd0-e7be-4fc0-88c8-046fc366d980/resource/fc07e1cc-c205-4806-aff9-826470937a0a/download/ipgod2022.zip"
DICTIONARY = "https://data.gov.au/data/dataset/49017fd0-e7be-4fc0-88c8-046fc366d980/resource/2a4ad939-d2ba-4082-b2a3-750a400884d1/download/ipgod2022-data-dictionary-v1-public.pdf"
RIGHTS = ("patent", "trade_mark", "design", "pbr")
TABLES = {  # file suffix -> table name
    "application": "application",
    "application-classification": "classification",
    "application-description": "description",
    "application-events": "events",
    "application-links": "links",
    "party-activity": "party",
}
DATES = {
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
    ctx.fetch(DICTIONARY, "ipgod2022-data-dictionary-v1-public.pdf", keep="repo")
    z = ctx.fetch(ZIP, "ipgod2022.zip", keep="r2")
    work = ctx.cache / "work"
    work.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit='8GB'; SET preserve_insertion_order=false")
    parquet: dict[str, str] = {}
    members = set(unzip_names(z))
    for right in RIGHTS:
        stem = right.replace("_", "-")
        for suffix, table in TABLES.items():
            member = f"{stem}-{suffix}.csv"
            if member not in members:
                raise CorpusError(f"ipgod: {member} is missing from the zip; has the release's layout changed?")
            name = f"{right}_{table}"
            out = ctx.cache / "processed" / f"{name}.parquet"
            out.parent.mkdir(parents=True, exist_ok=True)
            if not out.exists():  # the conversion is slow; a cached one is reused (delete the cache to redo)
                csv = unzip_member(z, member, work)
                src = f"read_csv('{csv}', all_varchar=true, header=true, quote='\"', escape='\"', strict_mode=false)"
                cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()]
                con.execute(f"COPY (SELECT {_select(cols)} FROM {src}) TO '{out}' (FORMAT parquet, COMPRESSION zstd)")
                csv.unlink()
            cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{out}'").fetchall()]
            rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
            ctx.keep_table(out, name, rows, cols, keep="r2")
            parquet[name] = str(out)
    for right in RIGHTS:
        _rights(ctx, con, right, parquet)
    _applicant_year(ctx, con, parquet)


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
      WITH app AS (SELECT * FROM '{p[f"{right}_application"]}'),
      party AS (SELECT * FROM '{p[f"{right}_party"]}' WHERE is_current IS NOT false),
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
               count(DISTINCT {main_class}) AS class_count,
               string_agg(DISTINCT {main_class}, ' ' ORDER BY {main_class}) AS classes
        FROM '{p[f"{right}_classification"]}' WHERE {cls} GROUP BY 1)
      SELECT app.application_number, app.ip_right_sub_type, app.status,
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
             c.main_class, c.class_count, c.classes
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

    An applicant is its ABN where IPGOD has one, else its IPGOD party id. Each application counts once for each of its
    founding applicants (`filed`), and 1/n for each of n (`filed_weighted`), as IPLORD does. Financial years end on
    30 June and are labelled by the year they end.
    """
    parts = []
    for right in RIGHTS:
        parts.append(f"""
        SELECT '{right}' AS ip_right_type, a.application_number, coalesce(pa.abn, pa.party_id) AS applicant_id,
               CASE WHEN pa.abn IS NULL THEN 'party_id' ELSE 'abn' END AS applicant_id_type,
               pa.party_type, pa.country_code, pa.state_code, pa.post_code,
               a.earliest_filed_date, a.gained_enforceable_status_date
        FROM '{p[f"{right}_application"]}' a
        JOIN '{p[f"{right}_party"]}' pa USING (application_number)
        WHERE pa.party_role_category = 'applicant' AND pa.is_founding""")
    out = ctx.cache / "processed/applicant_year.parquet"
    fy = "CAST(year({d}) + CASE WHEN month({d}) > 6 THEN 1 ELSE 0 END AS INTEGER)"
    con.execute(f"""
    COPY (
      WITH x AS ({" UNION ALL ".join(parts)}),
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
