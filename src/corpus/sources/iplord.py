"""IPLORD 2020: IP Australia's applicant by financial year panel, 1904 to 2020, with the ABN where known.

The public 2020 release covers designs (`d_`), plant breeder's rights (`pbr_`) and trade marks (`tm_`, with
`tm_services_` for service classes); it has no patent columns, although its dictionary describes them. For patents,
and for years after 2020, use `iprapid/applicant_year`, built the same way from IP RAPID.

Raw: the release's zip (R2) and dictionary (repo). Processed: `iplord` (the full data set, typed: ids as text, years
and counts as integers, weighted counts as doubles), in R2; `iplord_abn`, the rows identified by an ABN (repo if it
fits), with `party_name` blank where the ABR records the ABN as an individual (a sole trader).
"""

from __future__ import annotations

import duckdb
import pandas as pd

from ..core import CorpusError, Ctx, individual_abns, unzip_member, unzip_names

ZIP = "https://data.gov.au/data/dataset/d61374dd-1a62-4132-913d-35d90cfdac81/resource/af2ba6bd-a751-41cc-889b-1d83611d572d/download/iplord_2020.zip"
DICTIONARY = "https://data.gov.au/data/dataset/d61374dd-1a62-4132-913d-35d90cfdac81/resource/808dafcd-7cb3-4a39-94d0-81211f138a6f/download/iplord-data-dictionary-2021.pdf"
MEMBER = "iplord_1901_2020_full_data_set.csv"


def _cast(c: str) -> str:
    q = f'"{c}"'
    if c == "lord_party_id":
        return f"regexp_replace({q}, '\\.0$', '') AS {q}"
    if (
        c.endswith("_financial_year")
        or c == "financial_year"
        or c.endswith("_class_scope")
        or (c.endswith("_count") and "_weighted_" not in c)
    ):
        return f"try_cast(try_cast({q} AS DOUBLE) AS INTEGER) AS {q}"
    if c.endswith("_weighted_count"):
        return f"try_cast({q} AS DOUBLE) AS {q}"
    return f"nullif(trim({q}), '') AS {q}"


def run(ctx: Ctx) -> None:
    ctx.fetch(DICTIONARY, "iplord-data-dictionary-2021.pdf", keep="repo")
    z = ctx.fetch(ZIP, "iplord_2020.zip", keep="r2")
    work = ctx.cache / "work"
    if MEMBER not in unzip_names(z):
        raise CorpusError(f"iplord: {MEMBER} is missing from the zip")
    csv = unzip_member(z, MEMBER, work)
    con = duckdb.connect()
    con.execute("SET memory_limit='8GB'; SET preserve_insertion_order=false")
    src = f"read_csv('{csv}', all_varchar=true, header=true)"
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()]
    if any(c.startswith("p_") for c in cols):
        ctx.note("iplord: this release now has patent columns; update the module's docstring")
    out = ctx.cache / "processed/iplord.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    con.execute(
        f"COPY (SELECT {', '.join(_cast(c) for c in cols)} FROM {src}) TO '{out}' (FORMAT parquet, "
        "COMPRESSION zstd, COMPRESSION_LEVEL 9)"
    )
    rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
    ctx.keep_table(out, "iplord", rows, cols, keep="r2", describe="The full IPLORD 2020 panel")
    sub = ctx.cache / "processed/iplord_abn.parquet"
    con = duckdb.connect()  # a fresh connection: DuckDB will not reuse one with an unfinished result
    con.register("ind", pd.DataFrame({"abn": sorted(individual_abns())}))  # sole traders: names stay out
    con.execute(
        f"COPY (SELECT * REPLACE (CASE WHEN lord_party_id IN (SELECT abn FROM ind) THEN NULL ELSE party_name END "
        f"AS party_name) FROM '{out}' WHERE lord_party_id_type = 'abn' ORDER BY lord_party_id, financial_year) "
        f"TO '{sub}' (FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 9)"
    )
    rows = con.execute(f"SELECT count(*) FROM '{sub}'").fetchone()[0]
    ctx.keep_table(sub, "iplord_abn", rows, cols, describe="IPLORD rows identified by an ABN")
    work.joinpath(MEMBER).unlink()
