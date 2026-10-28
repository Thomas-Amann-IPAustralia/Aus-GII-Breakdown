"""Reserve Bank of Australia statistical tables: the cash rate (F1.1) and exchange rates (F11), monthly (gap B1).

Context for the timeline (Q4, Q5): the cost of money and the dollar's value move filing from overseas and investment
in R&D, so a policy or fee change is read beside them. Raw: each table as published (repo): `f1.1-data.csv` (money
market rates, monthly from 1969; the cash rate target from 1990), `f11-data.csv` (exchange rates, end of month, from
2010) and `f11hist-1969-2009.xls` (the same, July 1969 to December 2009). Processed: `series`, long: table, series
id, title, description, units, frequency, date (the day the RBA gives: a month's last business day or its end) and
value. Licence: CC BY 4.0 (RBA).
"""

from __future__ import annotations

import csv
import io

import pandas as pd

from ..core import CorpusError, Ctx

BASE = "https://www.rba.gov.au/statistics/tables/"
TABLES = {
    "F1.1": ["csv/f1.1-data.csv"],
    "F11": ["xls-hist/f11hist-1969-2009.xls", "csv/f11-data.csv"],
}
META = ["Title", "Description", "Frequency", "Type", "Units", "Source", "Publication date", "Series ID"]


def read(frame: pd.DataFrame, table: str) -> pd.DataFrame:
    """An RBA table read with no header: metadata rows labelled in the first column, then dated rows."""
    frame = frame.copy()
    label = frame[0].astype(str).str.strip()
    meta = {m: frame.loc[label == m].iloc[0, 1:] for m in META if (label == m).any()}
    if "Series ID" not in meta:
        raise CorpusError(f"rba: table {table} has no Series ID row")
    start = frame.index[label == "Series ID"][0] + 1
    data = frame.loc[start:].dropna(how="all")
    dates = pd.to_datetime(data[0].astype(str).str.strip(), format="mixed", dayfirst=True, errors="coerce")
    data = data[dates.notna()]
    out = []
    for col in frame.columns[1:]:
        sid = meta["Series ID"].get(col)
        if not isinstance(sid, str) or not sid.strip():
            continue
        v = pd.to_numeric(data[col], errors="coerce")
        keep = v.notna()
        out.append(
            pd.DataFrame(
                {
                    "table": table,
                    "series_id": sid.strip(),
                    "title": meta["Title"].get(col),
                    "description": meta.get("Description", pd.Series()).get(col),
                    "units": meta.get("Units", pd.Series()).get(col),
                    "frequency": meta.get("Frequency", pd.Series()).get(col),
                    "date": dates[data.index][keep].dt.date.values,
                    "value": v[keep].values,
                }
            )
        )
    return pd.concat(out, ignore_index=True)


def run(ctx: Ctx) -> None:
    parts = []
    for table, files in TABLES.items():
        for f in files:
            p = ctx.fetch(BASE + f, f.rsplit("/", 1)[1], keep="repo")
            if p.suffix == ".csv":
                frame = pd.DataFrame(list(csv.reader(io.StringIO(p.read_text("utf-8-sig"))))).replace("", None)
            else:
                frame = pd.read_excel(p, sheet_name="Data", header=None, engine="calamine", dtype=str)
            frame.columns = range(frame.shape[1])
            parts.append(read(frame, table))
    out = pd.concat(parts, ignore_index=True)
    # the historical file ends in December 2009 and the current one starts in January 2010; keep one row per date
    out = out.drop_duplicates(["table", "series_id", "date"], keep="last").sort_values(["table", "series_id", "date"])
    ctx.table(out.reset_index(drop=True), "series", describe="RBA cash rate and exchange rates, monthly, long")
