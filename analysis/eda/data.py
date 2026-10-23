"""Reading the corpus and the lens tables through DuckDB.

Large tables are filtered and aggregated in DuckDB, so only small results reach pandas (and the notebook). Write
`{source/table}` for a corpus table and `{lens/name}` for a lens table inside the SQL:

    sql("SELECT ip_right_type, count(*) AS n FROM {lens/rights} GROUP BY 1")
"""

from __future__ import annotations

import re
from pathlib import Path

import duckdb
import pandas as pd

import corpus

ROOT = Path(__file__).resolve().parents[2]
LENS_DIR = ROOT / "analysis" / "eda" / "data"
MAX_ROWS = 250_000  # a larger result is almost always a query that forgot to aggregate

_REF = re.compile(r"\{([a-z0-9_]+)/([a-z0-9_]+)\}")


class TooManyRows(RuntimeError):
    """A query returned more rows than `max_rows`; aggregate in SQL, or pass a larger `max_rows` deliberately."""


def table(source: str, name: str) -> str:
    """A corpus table as a DuckDB `read_parquet(...)` expression (downloading it from R2 once, if needed)."""
    return f"read_parquet('{corpus.path(source, name)}')"


def lens_path(name: str) -> Path:
    """The lens table's Parquet file, built first if it is missing (see `eda.build`)."""
    p = LENS_DIR / f"{name}.parquet"
    if not p.exists():
        from . import build

        build.build(name)
    return p


def lens_table(name: str) -> str:
    """A lens table as a DuckDB `read_parquet(...)` expression."""
    return f"read_parquet('{lens_path(name)}')"


def resolve(query: str) -> str:
    """Replace each `{source/table}` and `{lens/name}` in `query` with its `read_parquet(...)` expression."""

    def sub(m: re.Match) -> str:
        source, name = m.groups()
        return lens_table(name) if source == "lens" else table(source, name)

    return _REF.sub(sub, query)


def connect() -> duckdb.DuckDBPyConnection:
    """A DuckDB connection sized for this machine (about 15 GB of memory and 4 cores)."""
    con = duckdb.connect()
    con.execute("SET memory_limit = '10GB'")
    con.execute("SET preserve_insertion_order = false")
    return con


def sql(query: str, *, max_rows: int | None = MAX_ROWS, con: duckdb.DuckDBPyConnection | None = None) -> pd.DataFrame:
    """Run `query` and return the result as a DataFrame, refusing results longer than `max_rows`."""
    con = con or connect()
    q = resolve(query)
    if max_rows is None:
        return con.sql(q).df()
    df = con.sql(f"SELECT * FROM ({q}) LIMIT {max_rows + 1}").df()
    if len(df) > max_rows:
        raise TooManyRows(f"the query returns more than {max_rows:,} rows; aggregate it, or pass max_rows")
    return df


def load_lens(name: str, columns: list[str] | None = None) -> pd.DataFrame:
    """A whole lens table as a DataFrame (the lenses are small enough: the largest, `rights`, is about 4.4 million
    rows, so pass `columns` for it).

    Types follow the variable register: dates become datetimes, years and counts whole numbers that allow missing
    values, and yes/no columns booleans that allow missing values.
    """
    from .style import register

    df = pd.read_parquet(lens_path(name), columns=columns)
    kinds = {c: v["kind"] for c, v in register().get(name, {}).items() if c in df.columns}
    for c, k in kinds.items():
        if k == "date":
            df[c] = pd.to_datetime(df[c])
        elif k in ("year", "count"):
            df[c] = df[c].astype("Int64")
        elif k == "binary":
            df[c] = df[c].astype("boolean")
    return df


PROFILE_DIR = ROOT / "analysis" / "output"


def corpus_tables() -> pd.DataFrame:
    """Every processed table in the corpus (from the profile in `analysis/output/tables.csv`): source, table, rows,
    columns and whether it lives in the repo or R2."""
    t = pd.read_csv(PROFILE_DIR / "tables.csv")
    return t[["source", "table", "location", "rows", "n_columns"]]


def corpus_columns(source: str, name: str) -> pd.DataFrame:
    """The profile of one corpus table's columns (type, % null, distinct values, range, an example)."""
    c = pd.read_csv(PROFILE_DIR / "columns.csv", dtype={"min": str, "max": str, "example": str})
    c = c[(c.source == source) & (c.table == name)]
    return c[["column", "type", "null_rate", "approx_distinct", "min", "max", "example"]].reset_index(drop=True)
