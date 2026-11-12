"""Fingerprint the lens tables, column by column, so a change to any of them can be seen without the tables.

    uv run python -m eda.fingerprint            # write analysis/eda/fingerprints.json from the built tables
    uv run python -m eda.fingerprint --check    # say which lenses and columns differ from the committed file

The lens tables are rebuilt from the corpus and are not committed. A new source, or a change to `eda.build`, can
change a column that existing observations read without any source file changing (a join that repeats rows, say).
This file is the committed trace: for each lens its row count, and for each column a digest of its values.

A column's digest is the sum, over its rows, of the MD5 of each value written as text (nulls included), kept to 64
bits. It does not depend on the order of the rows, it changes if any value does, and it does not cancel when a value
is repeated. The lens build is reproducible (ADR 0039), so the same corpus and code give the same file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb

from . import build, data

FILE = Path(__file__).resolve().parent / "fingerprints.json"


def of(name: str) -> dict:
    """One lens table's row count and each column's digest."""
    path = data.LENS_DIR / f"{name}.parquet"
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute("SET memory_limit = '6GB'")  # it runs beside a notebook's kernel as well as on its own
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{path}')").fetchall()]
    digest = (
        "(sum(md5_number_lower(coalesce(CAST({c} AS VARCHAR), '<null>'))::HUGEINT) % 18446744073709551616)::UBIGINT"
    )
    parts = ", ".join(digest.format(c=f'"{c}"') for c in cols)
    row = con.execute(f"SELECT count(*), {parts} FROM read_parquet('{path}')").fetchone()
    return {"rows": row[0], "columns": {c: f"{v or 0:016x}" for c, v in zip(cols, row[1:], strict=True)}}


def built() -> dict:
    return {name: of(name) for name in build.LENSES if (data.LENS_DIR / f"{name}.parquet").exists()}


def committed() -> dict:
    return json.loads(FILE.read_text()) if FILE.exists() else {}


def differences(new: dict, old: dict) -> dict[str, dict]:
    """For each lens that differs: its rows before and now, and the columns added, dropped and changed."""
    out = {}
    for name in sorted(set(new) | set(old)):
        a, b = old.get(name), new.get(name)
        if a == b or b is None:  # unchanged, or not built here
            continue
        a = a or {"rows": None, "columns": {}}
        out[name] = {
            "rows": [a["rows"], b["rows"]],
            "added": sorted(set(b["columns"]) - set(a["columns"])),
            "dropped": sorted(set(a["columns"]) - set(b["columns"])),
            "changed": sorted(c for c in set(a["columns"]) & set(b["columns"]) if a["columns"][c] != b["columns"][c]),
        }
    return out


def main(argv: list[str]) -> None:
    new = built()
    if "--check" in argv:
        diff = differences(new, committed())
        if not diff:
            print(f"{len(new)} lens tables match analysis/eda/fingerprints.json")
            return
        for name, d in diff.items():
            print(f"{name}: rows {d['rows'][0]} -> {d['rows'][1]}")
            print(f"  added {d['added']}; dropped {d['dropped']}; changed {d['changed']}")
        sys.exit(1)
    FILE.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
    columns = sum(len(v["columns"]) for v in new.values())
    print(f"analysis/eda/fingerprints.json: {len(new)} lens tables, {columns} columns")


if __name__ == "__main__":
    main(sys.argv[1:])
