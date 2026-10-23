"""ASIC Company Dataset: every company registered in Australia, current and deregistered, as at the extract.

ASIC publishes one row per company name (current and former). Raw: the zip (R2) and help file (repo). Processed:
`company_names` (every row) and `companies` (one row per ACN: its current name, type, class, status, registration
and deregistration dates, ABN), typed and with snake_case columns.
"""

from __future__ import annotations

import duckdb

from ..core import CorpusError, Ctx, http_get, unzip_member, unzip_names

PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=asic-companies"
COLUMNS = {
    "Company Name": "company_name",
    "ACN": "acn",
    "Type": "type",
    "Class": "class",
    "Sub Class": "sub_class",
    "Status": "status",
    "Date of Registration": "registered",
    "Date of Deregistration": "deregistered",
    "Previous State of Registration": "previous_state",
    "State Registration number": "state_registration_number",
    "Modified since last report": "modified_since_last_report",
    "Current Name Indicator": "current_name_indicator",
    "ABN": "abn",
    "Current Name": "current_name",
    "Current Name Start Date": "current_name_start",
}


def run(ctx: Ctx) -> None:
    res = http_get(PACKAGE).json()["result"]["resources"]
    zips = [r for r in res if r.get("format", "").upper() == "ZIP"]
    helps = [r for r in res if r.get("format", "").upper() == "PDF"]
    if not zips:
        raise CorpusError("asic: no ZIP resource on data.gov.au; has the dataset changed?")
    if helps:
        ctx.fetch(helps[0]["url"], "company-dataset-help-file.pdf", keep="repo")
    z = ctx.fetch(zips[0]["url"], zips[0]["url"].rsplit("/", 1)[1], keep="r2")
    work = ctx.cache / "work"
    csv = unzip_member(z, unzip_names(z)[0], work)
    con = duckdb.connect()
    src = f"read_csv('{csv}', delim='\\t', all_varchar=true, header=true, quote='', strict_mode=false)"
    found = [r[0].lstrip("﻿") for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()]
    raw_names = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()]
    missing = set(COLUMNS) - set(found)
    if missing:
        raise CorpusError(f"asic: columns {sorted(missing)} are missing; has the layout changed?")
    sel = []
    for raw, name in zip(raw_names, found, strict=True):
        q, out = f'"{raw}"', COLUMNS.get(name)
        if out is None:
            continue
        if out in ("registered", "deregistered", "current_name_start"):
            sel.append(f"try_strptime(nullif(trim({q}), ''), '%d/%m/%Y')::DATE AS {out}")
        elif out in ("acn", "abn"):
            sel.append(f"nullif(regexp_replace(trim({q}), '\\s', '', 'g'), '') AS {out}")
        else:
            sel.append(f"nullif(trim({q}), '') AS {out}")
    names = ctx.cache / "processed/company_names.parquet"
    names.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY (SELECT {', '.join(sel)} FROM {src}) TO '{names}' (FORMAT parquet, COMPRESSION zstd)")
    n = con.execute(f"SELECT count(*) FROM '{names}'").fetchone()[0]
    ctx.keep_table(names, "company_names", n, list(COLUMNS.values()), describe="Every company name row as published")
    comp = ctx.cache / "processed/companies.parquet"
    con.execute(f"""COPY (
        SELECT acn, any_value(abn) AS abn,
               any_value(company_name ORDER BY current_name_indicator = 'Y' DESC) AS name,
               any_value(type) AS type, any_value(class) AS class, any_value(sub_class) AS sub_class,
               any_value(status) AS status, min(registered) AS registered, max(deregistered) AS deregistered,
               count(*) AS name_rows
        FROM '{names}' GROUP BY acn ORDER BY acn
      ) TO '{comp}' (FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 9)""")
    n = con.execute(f"SELECT count(*) FROM '{comp}'").fetchone()[0]
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{comp}'").fetchall()]
    ctx.keep_table(comp, "companies", n, cols, describe="One row per ACN")
    csv.unlink()
