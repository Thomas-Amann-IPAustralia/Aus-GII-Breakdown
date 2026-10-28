"""ATO taxation statistics, individuals by postcode (Individuals Table 6), every income year from 2012-13 (gap B3).

For Q2 and Q4: what people in each postcode earn and how many run a business, year by year, beside its IP (the
regions lens over time, and a denominator for individual applicants). Each year's Table 6 lists, for every postcode
with enough individuals, about 80 items as a count and an amount: individuals lodging, taxable income, salary and
wages, business income and losses, and so on. Raw: each year's workbook (R2). Processed: `items`, long: income year,
state, postcode, item (as the ATO names it in the latest year, without its footnote numbers; names that drift in
case or punctuation between years are made one), `unit` (`no.` or `$`) and value. The
sheet read is the one for all individuals (6B; from 2018-19 6A splits taxable from non-taxable). Licence: CC BY 2.5
AU (ATO).
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get

SEARCH = "https://data.gov.au/data/api/3/action/package_show?id=taxation-statistics-{y}"
FIRST, LAST = 2013, 2024  # income years ending 30 June


def _sheet(path) -> pd.DataFrame:
    """The all-individuals sheet: its header row names the state, the postcode and the items, with no taxable status."""
    book = pd.read_excel(path, sheet_name=None, header=None, engine="calamine", dtype=str)
    best = None
    for name, df in book.items():
        if name.lower().startswith(("title", "notes", "contents")):
            continue
        hit = df.index[df.apply(lambda r: r.astype(str).str.strip().str.lower().eq("postcode").any(), axis=1)]
        if len(hit) == 0:
            continue
        head = df.loc[hit[0]].astype(str)
        if head.str.contains("taxable status", case=False).any():
            continue
        best = (df, hit[0])
        break
    if best is None:
        raise CorpusError(f"ato_postcode: no all-individuals postcode sheet in {path.name}")
    df, h = best
    out = df.loc[h + 1 :].copy()
    out.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.loc[h]]
    return out


def items(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Long: one row per postcode and item, its unit read from the header's last word."""
    state = next(c for c in df.columns if c.lower().startswith("state"))
    pc = next(c for c in df.columns if c.lower() == "postcode")
    cols = [c for c in df.columns if re.search(r"(no\.|\$)$", c)]
    long = df.melt(id_vars=[state, pc], value_vars=cols, var_name="header", value_name="value")
    long = long[long[pc].astype(str).str.fullmatch(r"\d{3,4}")]
    long["unit"] = long["header"].str.extract(r"(no\.|\$)$")[0]
    long["item"] = (
        long["header"].str.replace(r"\s*(no\.|\$)$", "", regex=True).str.replace(r"(?<=[a-z\)])\d+$", "", regex=True)
    )
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    return pd.DataFrame(
        {
            "income_year": f"{year - 1}-{str(year)[2:]}",
            "state": long[state].astype(str).str.strip(),
            "postcode": long[pc].astype(str).str.zfill(4),
            "item": long["item"].str.strip(),
            "unit": long["unit"],
            "value": long["value"],
        }
    ).dropna(subset=["value"])


ALIASES = {"number of individuals": "individuals"}


def harmonise(df: pd.DataFrame) -> pd.DataFrame:
    """One name per item across years: names that differ only in case, spacing or punctuation ("Total business
    income - Primary production" and "Total business income - primary production"), or by a known alias, take the
    latest year's spelling."""
    key = df["item"].str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip().replace(ALIASES)
    latest = df.assign(key=key).sort_values("income_year").groupby("key")["item"].last()
    return df.assign(item=key.map(latest))


def run(ctx: Ctx) -> None:
    out = []
    for year in range(FIRST, LAST + 1):
        label = f"{year - 1}-{str(year)[2:]}"
        res = http_get(SEARCH.format(y=label)).json()["result"]["resources"]
        r = next((r for r in res if re.match(r"Individuals\s*[-–]\s*Table 6\b", r.get("name", ""), re.I)), None)
        if r is None:
            ctx.note(f"ato_postcode: no Individuals Table 6 for {label}; left out")
            continue
        p = ctx.fetch(r["url"], f"ts{str(year)[2:]}individual06.xlsx", keep="r2")
        out.append(items(_sheet(p), year))
        ctx.log(f"{label}: {len(out[-1]):,} values")
    df = harmonise(pd.concat(out, ignore_index=True))
    ctx.table(df, "items", describe="ATO individuals by postcode: Table 6 items, every income year, long")
