"""Shared by sources this environment cannot fetch: read whatever CSV or xlsx files have been put in data/raw/<source>/.

Each file becomes one table (named from the file name; one per sheet for a workbook), with the header taken as the
first row that has values in at least three columns, every column as text, and column names in snake case. A source
with no files yet fails with one line saying what to download and where to put it.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx


def snake(s) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_") or "column"


def _framed(df: pd.DataFrame) -> pd.DataFrame | None:
    head = next((i for i in range(min(30, len(df))) if df.iloc[i].notna().sum() >= 3), None)
    if head is None:
        return None
    out = df.iloc[head + 1 :].dropna(how="all").copy()
    cols, seen = [], {}
    for c in df.iloc[head]:
        name = snake(c) if pd.notna(c) else "column"
        seen[name] = seen.get(name, 0) + 1
        cols.append(name if seen[name] == 1 else f"{name}_{seen[name]}")
    out.columns = cols
    return out.astype(str).replace("nan", None)


def read_dropped(ctx: Ctx, instructions: str) -> int:
    files = sorted(p for p in ctx.raw.glob("*") if p.suffix.lower() in (".csv", ".xlsx", ".xls"))
    if not files:
        raise CorpusError(f"{ctx.source}: no files in data/raw/{ctx.source}/ yet. {instructions}")
    n = 0
    for f in files:
        ctx.keep_raw(f)
        if f.suffix.lower() == ".csv":
            sheets = {"": pd.read_csv(f, header=None, dtype=str, encoding_errors="replace", on_bad_lines="skip")}
        else:
            sheets = pd.read_excel(f, sheet_name=None, header=None, dtype=str, engine="calamine")
        for sheet, df in sheets.items():
            t = _framed(df)
            if t is None or t.empty:
                continue
            name = snake(f.stem) + (f"__{snake(sheet)}" if sheet and len(sheets) > 1 else "")
            ctx.table(t, name, describe=f"{f.name}{' / ' + sheet if sheet else ''}, as published (text)")
            n += 1
    return n
