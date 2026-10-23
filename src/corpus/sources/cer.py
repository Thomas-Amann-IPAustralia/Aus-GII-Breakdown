"""Small-scale renewable installations by postcode (Clean Energy Regulator): solar panels, solar water heaters, heat
pumps, batteries, wind and hydro, monthly from 2011 (with 2001 to 2010 totals), as installations and capacity.

For the environmental pathway (section 2 of docs/data-plan.md): how fast green technologies spread, by place, beside
green patenting. Raw: each published file (repo; most are CSV, a few are Excel workbooks). Processed:
`installations`, long: `dataset` (the file's name, and the sheet's for a workbook),
`postcode`, `period` (YYYY-MM, or the historic total's label), `measure` (the column's measure, for example
"Installation Quantity" or "Rated Output In kW") and `value`.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get

PAGE = "https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data"
MONTHS = {
    m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)
}


def _period(col: str) -> tuple[str, str]:
    m = re.match(r"([A-Z][a-z]{2}) (\d{4}) - (.+)", col)
    if m:
        return f"{m.group(2)}-{MONTHS[m.group(1)]:02d}", m.group(3).strip()
    head, _, measure = col.rpartition(" - ") if " - " in col else (col, "", col)
    return head.strip(), measure.strip() or col


def run(ctx: Ctx) -> None:
    docs = sorted(set(re.findall(r'href="(/document/[^"]+)"', http_get(PAGE).text)))
    if not docs:
        raise CorpusError("cer: no documents on the postcode data page")
    frames = []
    for d in docs:
        name = d.rsplit("/", 1)[1]
        r = http_get("https://cer.gov.au" + d, timeout=300)
        is_xlsx = r.content[:2] == b"PK"  # some documents are Excel workbooks
        f = ctx.raw / f"{name}.{'xlsx' if is_xlsx else 'csv'}"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(r.content)
        ctx.keep_raw(f, url="https://cer.gov.au" + d)
        if is_xlsx:
            tables = []
            for sheet, raw in pd.read_excel(f, sheet_name=None, engine="calamine", header=None, dtype=str).items():
                head = next((i for i in range(min(15, len(raw))) if "postcode" in str(raw.iat[i, 0]).lower()), None)
                if head is None:
                    continue
                t = raw.iloc[head + 1 :].copy()
                t.columns = [str(c) for c in raw.iloc[head]]
                tables.append((f"{name}:{sheet}", t))
        else:
            tables = [(name, pd.read_csv(f, dtype=str))]
        for label, df in tables:
            pc = df.columns[0]
            long = df.melt(id_vars=[pc], var_name="column", value_name="value").rename(columns={pc: "postcode"})
            parts = long["column"].map(_period)
            long["period"], long["measure"] = parts.str[0], parts.str[1]
            long["value"] = pd.to_numeric(long["value"].astype(str).str.replace(",", ""), errors="coerce")
            long.insert(0, "dataset", label)
            frames.append(long.drop(columns=["column"]).dropna(subset=["value"]))
    ctx.table(pd.concat(frames, ignore_index=True), "installations", describe="Small-scale installations by postcode")
