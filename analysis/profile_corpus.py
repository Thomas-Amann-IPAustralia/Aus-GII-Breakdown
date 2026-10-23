"""Profile every processed table in the corpus: does it open, do its rows match the manifest, what is in each column.

    uv run python analysis/profile_corpus.py                  # all stages, every source
    uv run python analysis/profile_corpus.py --stage schema   # open every table, check rows against the manifest
    uv run python analysis/profile_corpus.py --stage columns  # per-column null rates, distinct counts, ranges
    uv run python analysis/profile_corpus.py --stage keys     # how well each join key links to its authoritative list
    uv run python analysis/profile_corpus.py --stage report   # PROFILE.md from the three CSVs
    uv run python analysis/profile_corpus.py --only iprapid rdti

Writes CSVs to analysis/output/. Reads with DuckDB straight off the Parquet files (R2 tables are downloaded once into
the corpus cache), so the big tables are never loaded whole into memory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd

import corpus
from corpus.core import read_manifest

OUT = Path(__file__).resolve().parent / "output"
BATCH = 40  # columns aggregated per scan
NESTED = ("STRUCT", "MAP", "UNION")
NUMERIC_PREFIXES = (
    "TINYINT",
    "SMALLINT",
    "INTEGER",
    "BIGINT",
    "HUGEINT",
    "UTINYINT",
    "USMALLINT",
    "UINTEGER",
    "UBIGINT",
    "FLOAT",
    "DOUBLE",
    "DECIMAL",
)
ORDERED = NUMERIC_PREFIXES + ("DATE", "TIMESTAMP", "TIME")


def q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def connect(tmp: Path) -> duckdb.DuckDBPyConnection:
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit='9GB'")
    con.execute(f"SET temp_directory='{tmp}'")
    con.execute("SET preserve_insertion_order=false")
    return con


def processed_tables(only: list[str] | None) -> list[tuple[str, str, dict]]:
    """(source, table, manifest entry) for every processed table."""
    out = []
    for source, s in read_manifest()["sources"].items():
        if only and source not in only:
            continue
        for key, f in s["files"].items():
            if key.startswith("processed/"):
                out.append((source, key.removeprefix("processed/"), f))
    return out


def schema_stage(con, tables) -> pd.DataFrame:
    rows = []
    for i, (source, name, f) in enumerate(tables, 1):
        r = {
            "source": source,
            "table": name,
            "location": f["location"],
            "manifest_rows": f.get("rows"),
            "manifest_bytes": f.get("bytes"),
        }
        t0 = time.time()
        try:
            p = corpus.path(source, name)  # downloads from R2 on first use
            t1 = time.time()
            (n,) = con.execute(f"SELECT num_rows FROM parquet_file_metadata('{p}')").fetchall()[0]
            cols = con.execute(f"DESCRIBE SELECT * FROM '{p}'").fetchall()
            r.update(
                rows=n,
                n_columns=len(cols),
                rows_match=(n == f.get("rows")),
                columns_match=([c[0] for c in cols] == f.get("columns")) if f.get("columns") else None,
                fetch_s=round(t1 - t0, 1),
                open_s=round(time.time() - t1, 2),
                ok=True,
                error="",
            )
            r["path"] = str(p)
        except Exception as e:  # keep going: the point is to find what does not open
            r.update(ok=False, error=f"{type(e).__name__}: {str(e)[:200]}")
        rows.append(r)
        flag = "ok " if r["ok"] else "ERR"
        print(f"[{i:3}/{len(tables)}] {flag} {source}/{name} {r.get('rows', '')}", flush=True)
    return pd.DataFrame(rows)


def column_stage(con, schema: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ok = schema[schema.ok]
    for i, t in enumerate(ok.itertuples(), 1):
        p = t.path
        cols = [(c[0], c[1]) for c in con.execute(f"DESCRIBE SELECT * FROM '{p}'").fetchall()]
        t0 = time.time()
        for b in range(0, len(cols), BATCH):
            batch = cols[b : b + BATCH]
            exprs = []
            for j, (c, typ) in enumerate(batch):
                qc, nested = q(c), typ.startswith(NESTED) or typ.endswith("]")
                exprs.append(f"count({qc}) AS nn{j}")
                if nested:
                    continue
                exprs.append(f"approx_count_distinct({qc}) AS nd{j}")
                if typ.startswith(ORDERED):
                    exprs.append(f"min({qc})::VARCHAR AS mn{j}")
                    exprs.append(f"max({qc})::VARCHAR AS mx{j}")
                elif typ == "VARCHAR":
                    exprs.append(f"count(*) FILTER (WHERE trim({qc}) = '') AS bl{j}")
                    exprs.append(f"min(length({qc})) AS lmin{j}")
                    exprs.append(f"max(length({qc})) AS lmax{j}")
                exprs.append(f"left(any_value({qc})::VARCHAR, 40) AS ex{j}")
            try:
                res = con.execute(f"SELECT count(*) AS n, {', '.join(exprs)} FROM '{p}'").fetchdf().iloc[0]
            except Exception as e:
                print(f"   column batch failed {t.source}/{t.table}: {str(e)[:120]}", file=sys.stderr)
                continue
            n = int(res["n"])
            for j, (c, typ) in enumerate(batch):
                g = {k: res.get(f"{k}{j}") for k in ("nn", "bl", "nd", "mn", "mx", "lmin", "lmax", "ex")}
                nn = int(g["nn"])
                rows.append(
                    {
                        "source": t.source,
                        "table": t.table,
                        "column": c,
                        "type": typ,
                        "rows": n,
                        "null_rate": round(1 - nn / n, 4) if n else None,
                        "blank_strings": None if pd.isna(g["bl"]) else int(g["bl"]),
                        "approx_distinct": None if pd.isna(g["nd"]) else int(g["nd"]),
                        "min": g["mn"],
                        "max": g["mx"],
                        "len_min": None if pd.isna(g["lmin"]) else int(g["lmin"]),
                        "len_max": None if pd.isna(g["lmax"]) else int(g["lmax"]),
                        "example": g["ex"],
                    }
                )
        print(
            f"[{i:3}/{len(ok)}] {t.source}/{t.table}: {len(cols)} cols, {t.rows:,} rows, {time.time() - t0:.1f}s",
            flush=True,
        )
    return pd.DataFrame(rows)


# Join keys -----------------------------------------------------------------------------------------------------------
# family -> (reference (source, table, expression), valid-format regex, targets (source, table, expression, filter))
KEYS = {
    "abn": (
        ("abr", "abns", "abn"),
        r"\d{11}",
        [
            ("abr", "abns", "abn", None),
            ("linkage", "abn_spine", "abn", None),
            ("asic", "companies", "abn", None),
            ("asic", "company_names", "abn", None),
            ("ato_ctt", "entities", "abn", None),
            ("rdti", "entities", "abn", None),
            ("austender", "contracts", "supplier_abn", None),
            ("iprapid", "party", "abn", None),
            ("iprapid", "patent_rights", "applicant_abn", None),
            ("iprapid", "patent_rights", "any_applicant_abn", None),
            ("iprapid", "trade_mark_rights", "applicant_abn", None),
            ("iprapid", "design_rights", "applicant_abn", None),
            ("iprapid", "pbr_rights", "applicant_abn", None),
            ("iplord", "iplord_abn", "lord_party_id", "lord_party_id_type = 'abn'"),
        ],
    ),
    "acn": (
        ("abr", "abns", "acn"),
        r"\d{9}",
        [
            ("abr", "abns", "acn", None),
            ("linkage", "abn_spine", "acn", None),
            ("asic", "companies", "acn", None),
            ("ato_ctt", "entities", "acn", None),
            ("rdti", "entities", "acn", None),
        ],
    ),
    "postcode": (
        ("abs_regions", "poa", "poa_code"),
        r"\d{4}",
        [
            ("abr", "abns", "postcode", None),
            ("linkage", "abn_spine", "postcode", None),
            ("cer", "installations", "postcode", None),
            ("austender", "contracts", "supplier_postcode", None),
            ("iplord", "iplord", "post_code", None),
            ("iprapid", "party", "post_code", None),
            ("iprapid", "applicant_year", "post_code", None),
            ("iprapid", "patent_rights", "applicant_postcode", None),
            ("iprapid", "trade_mark_rights", "applicant_postcode", None),
            ("iprapid", "design_rights", "applicant_postcode", None),
            ("iprapid", "pbr_rights", "applicant_postcode", None),
        ],
    ),
    "sa2": (
        ("abs_regions", "poa_sa2", "sa2_code"),
        r"\d{9}",
        [
            ("abs_regions", "poa", "sa2_code", None),
            ("abs_regions", "mesh_blocks", "sa2_code", None),
            ("abs_regions", "seifa_sa2", "statistical_area_level_2_sa2", None),
            ("abs_cabee", "cubes", "sa2_code", None),
            ("abs_census", "sa2_g01", "SA2_CODE_2021", None),
        ],
    ),
    "ipc4": (
        ("concordances", "ipc4_anzsic", "ipc4"),
        r"[A-H]\d{2}[A-Z]",
        [
            ("concordances", "alp_ipc4_isic4", "ipc4", None),
            ("concordances", "ipc4_anzsic", "ipc4", None),
            ("google_patents", "families", "left(ipc_first, 4)", None),
            ("google_patents", "members", "left(ipc_first, 4)", None),
            (
                "iprapid",
                "classification",
                "left(replace(classification, ' ', ''), 4)",
                "classification_system = 'ipc_mark'",
            ),
        ],
    ),
    "patent_application_number": (
        ("iprapid", "patent_rights", "application_number"),
        None,
        [
            ("iprapid", "patent_rights", "application_number", None),
            ("iprapid", "events", "application_number", "ip_right_type = 'patent'"),
            ("iprapid", "classification", "application_number", "ip_right_type = 'patent'"),
            ("iprapid", "party", "application_number", "ip_right_type = 'patent'"),
            ("concordances", "patent_fields", "application_number", None),
            (
                "google_patents",
                "members",
                "regexp_extract(application_number, '^AU-(\\d+)-', 1)",
                "country_code = 'AU'",
            ),
        ],
    ),
    "trade_mark_application_number": (
        ("iprapid", "trade_mark_rights", "application_number"),
        None,
        [
            ("iprapid", "trade_mark_rights", "application_number", None),
            ("iprapid", "classification", "application_number", "ip_right_type = 'trade_mark'"),
            ("tmlink", "application", "application_number", "ip_office = 'au'"),
            ("tmlink", "tm_link", "application_number", "ip_office = 'au'"),
            ("tmlink", "owner", "application_number", "ip_office = 'au'"),
        ],
    ),
}


def key_stage(con) -> pd.DataFrame:
    rows = []
    for family, (ref, regex, targets) in KEYS.items():
        rs, rt, rexpr = ref
        try:
            con.execute(
                f"CREATE OR REPLACE TEMP TABLE ref AS SELECT DISTINCT ({rexpr})::VARCHAR AS k "
                f"FROM '{corpus.path(rs, rt)}' WHERE ({rexpr}) IS NOT NULL"
            )
        except Exception as e:
            print(f"[{family}] reference {rs}/{rt} failed: {str(e)[:150]}", file=sys.stderr)
            continue
        n_ref = con.execute("SELECT count(*) FROM ref").fetchall()[0][0]
        for s, t, expr, flt in targets:
            r = {
                "family": family,
                "source": s,
                "table": t,
                "key_expression": expr,
                "filter": flt or "",
                "reference": f"{rs}/{rt}.{rexpr}",
                "reference_distinct": n_ref,
            }
            try:
                where = f"WHERE ({expr}) IS NOT NULL" + (f" AND {flt}" if flt else "")
                valid = f"count(*) FILTER (WHERE regexp_full_match(k, '{regex}'))" if regex else "NULL"
                con.execute(
                    f"CREATE OR REPLACE TEMP TABLE tk AS SELECT ({expr})::VARCHAR AS k, count(*) AS n "
                    f"FROM '{corpus.path(s, t)}' {where} GROUP BY 1"
                )
                (n_rows, n_dist, n_valid, d_in, r_in, ex, top_k, top_n) = con.execute(
                    f"SELECT sum(n), count(*), {valid}, count(*) FILTER (WHERE k IN (SELECT k FROM ref)), "
                    f"sum(n) FILTER (WHERE k IN (SELECT k FROM ref)), any_value(k), arg_max(k, n), max(n) FROM tk"
                ).fetchall()[0]
                n_rows, r_in = int(n_rows or 0), int(r_in or 0)
                r.update(
                    rows_with_key=n_rows,
                    distinct_keys=n_dist,
                    pct_valid_format=_pct(n_valid, n_dist),
                    pct_distinct_in_reference=_pct(d_in, n_dist),
                    pct_rows_in_reference=_pct(r_in, n_rows),
                    example=ex,
                    most_common_key=top_k,
                    most_common_rows=int(top_n or 0),
                    pct_rows_most_common=_pct(top_n, n_rows),
                    error="",
                )
            except Exception as e:
                r["error"] = f"{type(e).__name__}: {str(e)[:150]}"
            rows.append(r)
            print(
                f"[{family}] {s}/{t}.{expr}: "
                + (r["error"] or f"{r['distinct_keys']:,} keys, {r['pct_distinct_in_reference']}% in {rs}/{rt}"),
                flush=True,
            )
    return pd.DataFrame(rows)


def _pct(a, b):
    return None if a is None or not b else round(100 * a / b, 1)


# Report --------------------------------------------------------------------------------------------------------------
def md_table(df: pd.DataFrame) -> str:
    head = "| " + " | ".join(df.columns) + " |\n|" + "|".join("---" for _ in df.columns) + "|\n"
    return head + "\n".join(
        "| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |" for r in df.itertuples(index=False)
    )


def report_stage() -> str:
    tables, cols, keys = (pd.read_csv(OUT / f) for f in ("tables.csv", "columns.csv", "keys.csv"))
    out = [
        "# Corpus profile",
        "",
        "Generated by `analysis/profile_corpus.py` from the committed manifest and the data in",
        "the repo and R2. Regenerate it after any corpus rebuild. Reading notes are in `analysis/README.md`.",
        "",
    ]
    ok = tables[tables.ok]
    out += [
        "## Does it open",
        "",
        f"- {len(tables)} processed tables; {len(ok)} open; {int(tables.rows_match.eq(False).sum())} row-count and "
        f"{int(tables.columns_match.eq(False).sum())} column-list mismatches against `data/manifest.json`.",
        f"- {int(ok.rows.sum()):,} rows and {len(cols):,} columns in all; "
        f"{int((tables.location == 'r2').sum())} tables in R2, {int((tables.location == 'repo').sum())} in the repo.",
        "",
    ]
    inv = tables.groupby("source").agg(
        tables=("table", "count"),
        rows=("rows", "sum"),
        mb=("manifest_bytes", "sum"),
        in_r2=("location", lambda x: int((x == "r2").sum())),
    )
    inv["rows"], inv["mb"] = inv.rows.map("{:,.0f}".format), (inv.mb / 1e6).round(1)
    out += ["## Tables by source", "", md_table(inv.reset_index()), ""]

    k = keys.copy()
    k["column"] = k.source + "/" + k.table + "." + k.key_expression
    k["rows_with_key"] = k.rows_with_key.map(lambda v: "" if pd.isna(v) else f"{int(v):,}")
    k["distinct_keys"] = k.distinct_keys.map(lambda v: "" if pd.isna(v) else f"{int(v):,}")
    out += [
        "## Join keys",
        "",
        "`% rows linked` is the share of rows whose key is in the reference list; `% valid` is the share of distinct",
        "keys with the expected format; `most_common_key` and `% rows with it` expose placeholders. Reference lists:",
        "ABR for ABN and ACN, ABS POA for postcode, the POA to SA2",
        "concordance for SA2, the ALP IPC concordance for IPC, IP RAPID for application numbers.",
        "",
    ]
    for fam, g in k.groupby("family", sort=False):
        ref = g.reference.iloc[0]
        out += [
            f"### {fam} (reference: `{ref}`)",
            "",
            md_table(
                g[
                    [
                        "column",
                        "filter",
                        "rows_with_key",
                        "distinct_keys",
                        "pct_valid_format",
                        "pct_rows_in_reference",
                        "most_common_key",
                        "pct_rows_most_common",
                    ]
                ].rename(
                    columns={
                        "pct_valid_format": "% valid",
                        "pct_rows_in_reference": "% rows linked",
                        "pct_rows_most_common": "% rows with it",
                    }
                )
            ),
            "",
        ]

    allnull = cols[(cols.null_rate == 1) & (cols.rows > 0)]
    n_const = int(((cols.null_rate < 1) & (cols.approx_distinct <= 1) & (cols.rows > 1)).sum())
    out += [
        "## Column flags",
        "",
        f"- **All null** ({len(allnull)} columns): "
        + "; ".join(f"{s} ({len(g)})" for s, g in allnull.groupby("source"))
        + ". Listed in `analysis/output/columns.csv`.",
        f"- **Constant** (one distinct value, not null): {n_const} columns.",
        f"- **Over 90% null, not all null**: {int(((cols.null_rate > 0.9) & (cols.null_rate < 1)).sum())} columns.",
        "",
    ]
    blank = cols[cols.blank_strings.fillna(0) > 0].sort_values("blank_strings", ascending=False)
    blank = blank.assign(
        blank_strings=blank.blank_strings.astype(int), blank_pct=(100 * blank.blank_strings / blank.rows).round(1)
    )
    out += [
        "### Text columns holding empty strings (not NULL)",
        "",
        md_table(blank[["source", "table", "column", "rows", "blank_strings", "blank_pct"]]),
        "",
    ]
    d = cols[cols.type.str.startswith(("DATE", "TIMESTAMP"))]
    odd = d[(d["min"] < "1850") | (d["max"] > dt.date.today().isoformat())]
    out += [
        "### Dates before 1850 or after today (placeholders and scheduled dates)",
        "",
        md_table(odd[["source", "table", "column", "min", "max"]]),
        "",
    ]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["schema", "columns", "keys", "report", "all"], default="all")
    ap.add_argument("--only", nargs="*", help="limit to these source ids")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    con = connect(OUT / ".duckdb_tmp")
    tables = processed_tables(a.only)
    print(f"{len(tables)} processed tables")

    schema_csv = OUT / "tables.csv"
    if a.stage in ("schema", "all"):
        schema = schema_stage(con, tables)
        schema.to_csv(schema_csv, index=False)
    else:
        schema = pd.read_csv(schema_csv)
    if a.stage in ("columns", "all"):
        column_stage(con, schema).to_csv(OUT / "columns.csv", index=False)
    if a.stage in ("keys", "all"):
        key_stage(con).to_csv(OUT / "keys.csv", index=False)
    if a.stage in ("report", "all"):
        (OUT / "PROFILE.md").write_text(report_stage(), "utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
