"""Cultural and creative activity in Australia (BCARR satellite accounts).

The size of the creative industries, where copyright and design protection operate (section 2 of docs/data-plan.md):
output, gross value added and GDP for each cultural and creative domain, by industry division, and as a share of the
economy, by financial year. The site refuses this environment, so the workbooks were downloaded by hand from the
Bureau of Communications, Arts and Regional Research (infrastructure.gov.au) into data/raw/bcarr_creative/ (repo):
the 2015-16 to 2024-25 release and the 2008-09 to 2022-23 release (both on the refreshed methodology). To add a
release, put its workbook there and run `corpus run bcarr_creative`.

Processed: `activity`, one row per release, table, series and financial year (long; `table_title` names the domain
or breakdown, without its years; `unit` is $m or %). The two
summary tables comparing the first and last years are left out (their figures are in the yearly tables). Use the
newer release where they overlap; the older one runs back to 2008-09.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx

PERIOD = re.compile(r"^(\d{4})[–-](\d{2})$")
UNITS = {"$m", "%", "$"}


def _table(df: pd.DataFrame) -> pd.DataFrame | None:
    col0 = df[0].fillna("").astype(str).str.strip()
    first = next((i for i, v in enumerate(col0) if PERIOD.match(v)), None)
    if first is None:
        return None
    title = re.sub(r"^Table \d+[.:]\s*", "", col0.iloc[0])
    title = re.sub(r",\s*\d{4}[–-]\d{2} to \d{4}[–-]\d{2}$", "", title).replace("–", "-")
    head = df.iloc[1:first].fillna("").astype(str).map(str.strip)
    rows = []
    for j in range(1, df.shape[1]):
        cells = [c for c in head[j] if c]
        unit = next((c for c in cells if c in UNITS), None)
        label = " ".join(c for c in cells if c not in UNITS)
        if not label:
            continue
        for i in range(first, len(df)):
            m = PERIOD.match(col0.iloc[i])
            if not m:
                break
            v = pd.to_numeric(df.iat[i, j], errors="coerce")
            if pd.notna(v):
                rows.append((title, label, unit, int(m.group(1)) + 1, col0.iloc[i].replace("–", "-"), float(v)))
    return pd.DataFrame(rows, columns=["table_title", "series", "unit", "fy_end", "financial_year", "value"])


def run(ctx: Ctx) -> None:
    files = sorted(ctx.raw.glob("*.xlsx"))
    if not files:
        raise CorpusError(
            "bcarr_creative: no workbooks in data/raw/bcarr_creative/ yet. From the Bureau of Communications, Arts "
            "and Regional Research (infrastructure.gov.au), the cultural and creative activity data tables (xlsx)."
        )
    out = []
    for p in files:
        ctx.keep_raw(p)
        m = re.search(r"(\d{4}-\d{2})-to-(\d{4}-\d{2})", p.name)
        release = f"{m.group(1)} to {m.group(2)}" if m else p.stem
        for sheet, df in pd.read_excel(p, sheet_name=None, header=None, dtype=str, engine="calamine").items():
            if not sheet.startswith("Table"):
                continue
            t = _table(df)
            if t is not None and not t.empty:
                t.insert(0, "table", int(sheet.split()[1]))
                t.insert(0, "release", release)
                out.append(t)
    df = pd.concat(out, ignore_index=True)
    ctx.table(df, "activity", describe="Cultural and creative activity by domain and industry, $m and %, long")
