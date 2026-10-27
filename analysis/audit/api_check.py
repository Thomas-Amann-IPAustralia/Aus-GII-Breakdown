"""IP RAPID against IP Australia's live register (its APIs, ADR 0028): is it complete, is it accurate, and does the
register fill IP RAPID's gaps (OQ7, OQ13, OQ14)?

    uv run corpus run ipa_api                  # the register's records (about two hours)
    uv run python -m audit.api_check           # seconds: the tables below, from the corpus

Reads `ipa_api` and `iprapid` from the corpus and writes to `analysis/audit/output/api/`:

- `completeness.csv`: by right and year, the numbers each side has, and what the register says of those only one has;
- `fields.csv`: for the random sample, each field compared: agreed, differed, or missing on one side, with a 95%
  interval on the share that agrees where both have a value;
- `status.csv`: IP RAPID's status against the register's, for the sample;
- `gaps.csv`: what the register holds for IP RAPID's gaps: ABNs (OQ7), design applicants' countries (OQ14) and the
  missing trade mark numbers (OQ13);
- `expedite.csv`: for the sample, trade marks with an expedited-examination event in IP RAPID and in the register's
  own history, by financial year and convention priority claim (OQ6);
- `madrid.csv` (with `--live`, which asks the register): trade marks by year of lodgement and of filing, all and
  international registrations (Madrid), against IP RAPID's (OQ13).

Records the register changed after the IP RAPID release are left out of the field comparison (the searches say which
trade marks and designs changed; patents cannot be asked, so a few of their differences are timing).
`docs/audit-ipa-api.md` quotes the tables.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from corpus import path

OUT = Path(__file__).resolve().parent / "output" / "api"
FY = "CAST(year({d}) + (month({d}) > 6)::INT AS INT)"


def wilson(k, n, z: float = 1.96):
    k, n = np.asarray(k, float), np.asarray(n, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        p = k / n
        d = 1 + z**2 / n
        c = (p + z**2 / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - h, c + h


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for name, (src, table) in {
        "app": ("iprapid", "application"),
        "tmr": ("iprapid", "trade_mark_rights"),
        "dr": ("iprapid", "design_rights"),
        "pr": ("iprapid", "patent_rights"),
        "links": ("iprapid", "links"),
        "ev": ("iprapid", "events"),
        "nums": ("ipa_api", "numbers"),
        "tm": ("ipa_api", "trade_marks"),
        "ds": ("ipa_api", "designs"),
        "pt": ("ipa_api", "patents"),
        "abr": ("abr", "abns"),
    }.items():
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM '{path(src, table)}'")
    con.execute("""
        CREATE TABLE changed AS SELECT ip_right_type, application_number FROM nums WHERE changed_since_release;
        CREATE TABLE lk AS SELECT application_number,
               bool_or(link_type = 'madrid_import') AS madrid, bool_or(link_type = 'madrid_export') AS madrid_export,
               bool_or(link_type = 'convention_priority') AS conv
        FROM links WHERE ip_right_type = 'trade_mark' GROUP BY 1;
    """)
    return con


# -- completeness -----------------------------------------------------------------------------------------------------


def completeness(con) -> pd.DataFrame:
    """By right and year (IP RAPID's application year, else the register's): numbers on each side, and the register's
    answer for the numbers only one side has."""
    return con.execute("""
        WITH r AS (SELECT ip_right_type, application_number, year(application_date) AS y FROM app
                   WHERE ip_right_type IN ('trade_mark', 'design')),
        f AS (SELECT 'trade_mark' AS ip_right_type, application_number, found FROM tm
              UNION ALL SELECT 'design', application_number, found FROM ds),
        j AS (SELECT coalesce(r.ip_right_type, n.ip_right_type) AS ip_right_type,
                     coalesce(r.y, n.year) AS year, r.application_number IS NOT NULL AS in_iprapid,
                     n.application_number IS NOT NULL AS in_search, f.found
              FROM r FULL JOIN nums n USING (ip_right_type, application_number)
              LEFT JOIN f USING (ip_right_type, application_number))
        SELECT ip_right_type, year,
               count(*) FILTER (in_iprapid) AS iprapid,
               count(*) FILTER (in_search) AS register_search,
               count(*) FILTER (in_iprapid AND in_search) AS both,
               count(*) FILTER (in_search AND NOT in_iprapid) AS register_only,
               count(*) FILTER (in_iprapid AND NOT in_search) AS iprapid_only,
               count(*) FILTER (in_iprapid AND NOT in_search AND found) AS iprapid_only_in_register,
               count(*) FILTER (in_iprapid AND NOT in_search AND NOT found) AS iprapid_only_not_in_register
        FROM j GROUP BY ALL ORDER BY ALL
    """).df()


# -- fields -----------------------------------------------------------------------------------------------------------

# (right, field, IP RAPID's value, the register's value): SQL over `s` (the sample, IP RAPID's rights table `x` and
# the register's record `a`). Owner fields are compared for rights with one owner on both sides (the order of
# several differs), and as "any" for every right.
FIELDS = {
    "trade_mark": [
        ("application date (lodgement)", "x.application_date", "a.lodgement_date"),
        (
            "application date (lodgement, not Madrid)",
            "x.application_date",
            "a.lodgement_date",
            "NOT coalesce(lk.madrid, false)",
        ),
        (
            "application date (lodgement, Madrid)",
            "x.application_date",
            "a.lodgement_date",
            "coalesce(lk.madrid, false)",
        ),
        (
            "application date (Madrid: IR notification)",
            "x.application_date",
            "a.ir_notification_date",
            "coalesce(lk.madrid, false)",
        ),
        ("application date (Madrid: filing)", "x.application_date", "a.filing_date", "coalesce(lk.madrid, false)"),
        ("priority date", "x.priority_date", "a.priority_date"),
        ("registered (entered on register)", "x.gained_registration_status_date", "a.entered_on_register_date"),
        (
            "Nice classes",
            "list_sort(string_split(x.classes, ' ')::INT[])",
            "list_sort(string_split(a.classes, ',')::INT[])",
        ),
        ("number of owners", "x.applicant_count", "a.owner_count"),
        (
            "Madrid, either way (an international registration number)",
            "coalesce(lk.madrid or lk.madrid_export, false)",
            "a.ir_number IS NOT NULL",
        ),
        (
            "Madrid designation of Australia (an IR notification date)",
            "coalesce(lk.madrid, false)",
            "a.ir_notification_date IS NOT NULL",
        ),
        ("convention priority claimed", "coalesce(lk.conv, false)", "a.convention"),
        ("any owner in Australia", "x.any_applicant_in_australia", "a.any_owner_in_australia"),
        ("any owner's ABN", "x.any_applicant_abn", "a.any_owner_abn"),
        ("owner's country (one owner)", "x.applicant_country", "a.owner_country"),
        ("owner's state (one owner, Australia)", "x.applicant_state", "a.owner_state"),
        ("owner's postcode (one owner, Australia)", "x.applicant_postcode", "a.owner_postcode"),
        ("owner's ABN (one owner)", "x.applicant_abn", "a.owner_abn"),
    ],
    "design": [
        ("application date (filed)", "x.application_date", "a.filed_date"),
        ("priority date", "x.priority_date", "a.priority_date"),
        ("registered", "x.gained_registration_status_date", "a.registered_date"),
        ("certified (enforceable)", "x.gained_enforceable_status_date", "a.certified_date"),
        ("Locarno class", "x.main_class", "left(a.main_class, 2)"),
        ("number of owners", "x.applicant_count", "a.owner_count"),
        ("any owner in Australia", "x.any_applicant_in_australia", "a.any_owner_in_australia"),
        ("any owner's ABN", "x.any_applicant_abn", "a.any_owner_abn"),
        ("owner's country (one owner)", "x.applicant_country", "a.owner_country"),
        ("owner's state (one owner, Australia)", "x.applicant_state", "a.owner_state"),
        ("owner's postcode (one owner, Australia)", "x.applicant_postcode", "a.owner_postcode"),
        ("owner's ABN (one owner)", "x.applicant_abn", "a.owner_abn"),
    ],
    "patent": [
        ("type", "x.ip_right_sub_type", "a.patent_type"),
        ("application date (filed, not PCT)", "x.application_date", "a.filed_date", "NOT a.pct"),
        ("application date (PCT: national phase entry)", "x.application_date", "a.pct_national_phase_date", "a.pct"),
        ("earliest filing date (PCT: international filing)", "x.earliest_filed_date", "a.filed_date", "a.pct"),
        (
            "priority date (where the register has one)",
            "x.priority_date",
            "a.priority_date",
            "a.priority_date IS NOT NULL",
        ),
        (
            "priority date (where the register has none): IP RAPID's is the application date",
            "x.priority_date = x.application_date",
            "true",
            "a.priority_date IS NULL AND x.priority_date IS NOT NULL",
        ),
        (
            "granted (standard patents; sealing date)",
            "x.gained_enforceable_status_date",
            "a.sealing_date",
            "x.ip_right_sub_type = 'standard_complete'",
        ),
        (
            "IPC subclass (IP RAPID's main one among the register's)",
            "x.main_class IS NOT NULL",
            "list_contains(string_split(a.ipc_subclasses, ' '), x.main_class)",
            "x.main_class IS NOT NULL AND a.ipc_subclasses IS NOT NULL",
        ),
        ("number of applicants", "x.applicant_count", "a.owner_count"),
    ],
}
ONE_OWNER = "x.applicant_count = 1 AND a.owner_count = 1"
AU = " AND x.applicant_country = 'au' AND a.owner_country = 'au'"
TYPES = {"Standard": "standard_complete", "Provisional": "provisional", "Innovation": "innovation", "Petty": "petty"}


def _norm(v) -> str | None:
    if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NaT:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip().lower()
    return TYPES.get(str(v).strip(), s) if s else None


def fields(con) -> pd.DataFrame:
    rows = []
    tables = {"trade_mark": ("tmr", "tm"), "design": ("dr", "ds"), "patent": ("pr", "pt")}
    for right, specs in FIELDS.items():
        x, a = tables[right]
        base = (
            f"FROM {a} a JOIN {x} x USING (application_number) "
            f"{'LEFT JOIN lk USING (application_number)' if right == 'trade_mark' else ''} "
            f"WHERE a.found AND a.reasons LIKE '%sample%' AND application_number NOT IN "
            f"(SELECT application_number FROM changed WHERE ip_right_type = '{right}')"
        )
        for field, ix, ax, *where in specs:
            cond = "".join(f" AND {w}" for w in where)
            if "(one owner" in field:
                cond += f" AND {ONE_OWNER}" + (AU if "Australia" in field else "")
            vals = con.execute(f"SELECT {ix}, {ax} {base}{cond}").fetchall()
            pairs = [(_norm(i), _norm(j)) for i, j in vals]
            both = [(i, j) for i, j in pairs if i is not None and j is not None]
            rows.append(
                {
                    "ip_right_type": right,
                    "field": field,
                    "records": len(pairs),
                    "both_have": len(both),
                    "agree": sum(i == j for i, j in both),
                    "differ": sum(i != j for i, j in both),
                    "iprapid_only": sum(i is not None and j is None for i, j in pairs),
                    "register_only": sum(i is None and j is not None for i, j in pairs),
                    "neither": sum(i is None and j is None for i, j in pairs),
                }
            )
    df = pd.DataFrame(rows)
    df["agree_share"] = df.agree / df.both_have
    df["agree_low"], df["agree_high"] = wilson(df.agree, df.both_have)
    return df


# IP RAPID's trade mark statuses and the register's status groups they belong to (the register has several codes
# for one state, such as "Registered" and "Protected", the latter for Madrid marks)
TM_STATUS_GROUP = {
    "protected": "REGISTERED",
    "ceased": "REMOVED",
    "cancelled": "REMOVED",
    "removed": "REMOVED",
    "lapsed": "NEVER_REGISTERED",
    "withdrawn": "NEVER_REGISTERED",
    "linked": "NEVER_REGISTERED",
    "voided": "NEVER_REGISTERED",
    "refused": "REFUSED",
    "ex_parte_refused": "REFUSED",
    "inter_partes_refused": "REFUSED",
    "accepted": "PENDING",
    "published": "PENDING",
    "filed": "PENDING",
}


def status(con) -> pd.DataFrame:
    """IP RAPID's status against the register's, for the sample, split by whether the register changed the record
    after the release (unknown for patents)."""
    ch = "application_number IN (SELECT application_number FROM changed WHERE ip_right_type = '{r}')"
    df = con.execute(f"""
        SELECT 'trade_mark' AS ip_right_type, x.status AS iprapid, a.status_group || ': ' || a.status_code AS register,
               {ch.format(r="trade_mark")} AS changed_since_release, count(*) AS n
        FROM tm a JOIN tmr x USING (application_number) WHERE a.found AND a.reasons LIKE '%sample%' GROUP BY ALL
        UNION ALL
        SELECT 'design', x.status, a.status, {ch.format(r="design")}, count(*)
        FROM ds a JOIN dr x USING (application_number) WHERE a.found AND a.reasons LIKE '%sample%' GROUP BY ALL
        UNION ALL
        SELECT 'patent', x.status, a.status_code, NULL, count(*)
        FROM pt a JOIN pr x USING (application_number) WHERE a.found AND a.reasons LIKE '%sample%' GROUP BY ALL
        ORDER BY 1, 2, 5 DESC
    """).df()
    group = df.register.str.split(":").str[0]
    df["agrees"] = np.where(
        df.ip_right_type == "trade_mark",
        df.iprapid.map(TM_STATUS_GROUP) == group,
        df.iprapid.str.lower() == df.register.str.lower(),
    )
    return df


# -- gaps -------------------------------------------------------------------------------------------------------------


def expedite(con) -> pd.DataFrame:
    """Expedited examination of trade marks, as IP RAPID publishes it (an `exam_request_expedite` event) and as the
    register's history shows it ("Examination expedited", "Expedite", "Expedite Work Initiated" and so on)."""
    fy = FY.format(d="x.application_date")
    return con.execute(f"""
        WITH e AS (SELECT application_number FROM ev WHERE ip_right_type = 'trade_mark'
                   AND event_category = 'exam_request_expedite' GROUP BY 1)
        SELECT {fy} AS financial_year, coalesce(lk.conv, false) AS convention_priority, count(*) AS records,
               count(e.application_number) AS iprapid_expedite,
               count(*) FILTER (a.expedite_events IS NOT NULL) AS register_expedite,
               count(*) FILTER (a.expedite_events LIKE '%Examination expedited%') AS register_examination_expedited,
               count(*) FILTER (a.expedite_events IS NOT NULL AND e.application_number IS NOT NULL) AS both_record
        FROM tm a JOIN tmr x USING (application_number) LEFT JOIN lk USING (application_number)
        LEFT JOIN e USING (application_number)
        WHERE a.found AND a.reasons LIKE '%sample%' AND x.application_date >= '2001-07-01'
        GROUP BY ALL ORDER BY ALL
    """).df()


def gaps(con) -> pd.DataFrame:
    abn = con.execute(f"""
        WITH acn AS (SELECT acn, any_value(abn) AS abn FROM abr WHERE acn IS NOT NULL GROUP BY 1 HAVING count(*) = 1),
        t AS (SELECT a.*, x.application_date, b.abn IS NOT NULL AS in_abr, acn.abn AS acn_abn
              FROM tm a JOIN tmr x USING (application_number)
              LEFT JOIN (SELECT DISTINCT abn FROM abr) b ON b.abn = a.any_owner_abn
              LEFT JOIN acn ON acn.acn = lpad(a.owner_acn, 9, '0')
              WHERE a.reasons LIKE '%abn_%')
        SELECT CASE WHEN reasons LIKE '%abn_gap%' THEN 'abn_gap' ELSE 'abn_control' END AS gap,
               'FY' || {FY.format(d="application_date")} AS period, count(*) AS records,
               count(*) FILTER (found) AS in_register,
               count(*) FILTER (any_owner_abn IS NOT NULL) AS filled,
               count(*) FILTER (any_owner_abn IS NOT NULL AND in_abr) AS filled_in_abr,
               count(*) FILTER (owner_acn IS NOT NULL) AS with_acn,
               count(*) FILTER (any_owner_abn IS NULL AND acn_abn IS NOT NULL) AS abn_from_acn,
               count(*) FILTER (any_owner_abn IS NOT NULL OR acn_abn IS NOT NULL) AS filled_either
        FROM t GROUP BY ALL
    """).df()
    country = con.execute("""
        SELECT 'country_gap' AS gap, CAST(10 * (year(x.application_date) // 10) AS VARCHAR) || 's' AS period,
               count(*) AS records, count(*) FILTER (a.found) AS in_register,
               count(*) FILTER (a.owner_country IS NOT NULL) AS filled,
               count(*) FILTER (a.owner_country = 'au') AS filled_au,
               count(*) FILTER (a.found AND a.owner_count = 0) AS register_no_owner,
               count(*) FILTER (x.applicant_count = 0 OR x.applicant_count IS NULL) AS iprapid_no_applicant
        FROM ds a JOIN dr x USING (application_number) WHERE a.reasons LIKE '%country_gap%' GROUP BY ALL
    """).df()
    number = con.execute("""
        SELECT 'number_gap' AS gap, '1978060 to 1980352' AS period, count(*) AS records,
               count(*) FILTER (found) AS in_register, NULL AS filled
        FROM tm WHERE reasons LIKE '%number_gap%'
    """).df()
    return pd.concat([abn, country, number], ignore_index=True).sort_values(["gap", "period"])


def madrid(con, years=range(2012, 2026)) -> pd.DataFrame:
    """The register's counts of trade marks by year, all and Madrid, by two of its dates, beside IP RAPID's (by
    application date; Madrid: a `madrid_import` link)."""
    from corpus.ipa_api import Client

    client = Client("prod")
    iprapid = con.execute("""
        SELECT year(application_date) AS year, count(*) AS iprapid_all,
               count(*) FILTER (coalesce(lk.madrid, false)) AS iprapid_madrid
        FROM app LEFT JOIN lk USING (application_number) WHERE ip_right_type = 'trade_mark' GROUP BY 1
    """).df()
    rows = []
    for y in years:
        row = {"year": y}
        for date_type in ("LODGEMENT_DATE", "FILING"):
            date = {"date": {"type": date_type, "from": f"{y}-01-01", "to": f"{y}-12-31"}}
            row[f"register_{date_type.lower()}_all"] = client.count("trade_mark", [{"query": date}])["count"]
            ir = {**date, "flags": ["INTERNATIONAL_REGISTRATION"]}
            row[f"register_{date_type.lower()}_madrid"] = client.count("trade_mark", [{"query": ir}])["count"]
        rows.append(row)
    return pd.DataFrame(rows).merge(iprapid, on="year", how="left")


def main(argv: list[str] | None = None) -> None:
    import argparse

    p = argparse.ArgumentParser(prog="python -m audit.api_check")
    p.add_argument("--live", action="store_true", help="also ask the register for its yearly counts (madrid.csv)")
    a = p.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    con = connect()
    steps = [("completeness", completeness), ("fields", fields), ("status", status), ("gaps", gaps)]
    steps.append(("expedite", expedite))
    for name, fn in steps + ([("madrid", madrid)] if a.live else []):
        df = fn(con)
        df.to_csv(OUT / f"{name}.csv", index=False, float_format="%.6g")
        print(f"{name}: {len(df)} rows -> {OUT / name}.csv")


if __name__ == "__main__":
    main()
