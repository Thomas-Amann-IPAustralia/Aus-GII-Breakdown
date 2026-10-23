"""TM-Link (IP Australia and Swinburne University, 2020 release): trade marks from several offices under one schema,
with links between similar marks in different offices (international trade mark families).

For Q3: which Australian owners take their brands abroad, where, and when. Raw: each table's CSV (R2). Processed,
one Parquet table per TM-Link table, all columns as text as published (R2): `tm_link` (the links), `application`,
`owner`, `classification`, `madrid`, `property`. Left out: `description` (goods and services text) and `image-text`
(text read from logos), 1.5 GB of free text the research questions do not need. The dictionary the release cites
(minchulkim87.github.io/tmlink2020) is offline; the columns are as published.
"""

from __future__ import annotations

import duckdb

from ..core import Ctx, http_get

PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=tm-link"
TABLES = ["tm-link", "application", "owner", "classification", "madrid", "property"]


def run(ctx: Ctx) -> None:
    res = {r["name"]: r["url"] for r in http_get(PACKAGE).json()["result"]["resources"]}
    con = duckdb.connect()
    con.execute("SET memory_limit='8GB'; SET preserve_insertion_order=false")
    ctx.note("tmlink: description and image-text tables left out (free text, not needed)")
    for t in TABLES:
        csv = ctx.fetch(res[t], f"{t}.csv", keep="r2")
        name = t.replace("-", "_")
        out = ctx.cache / "processed" / f"{name}.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        src = f"read_csv('{csv}', all_varchar=true, header=true, strict_mode=false, quote='\"', escape='\"')"
        cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()]
        con.execute(f"COPY (SELECT * FROM {src}) TO '{out}' (FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 9)")
        rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
        ctx.keep_table(out, name, rows, cols, keep="r2", describe=f"TM-Link {t}, as published")
        csv.unlink()  # R2 holds it; free the disk for the next table
