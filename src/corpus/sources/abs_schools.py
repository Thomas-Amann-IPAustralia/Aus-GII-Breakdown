"""ABS Schools: full-time equivalent student to teaching staff ratios, 2006 to the latest year (gap B7).

For the GII's indicator 2.1.5 (pupil-teacher ratio, secondary), blank for Australia in GII 2026 (F17): a supplementary
observation from Australia's own statistics, labelled as such beside the official release (ADR 0033). Raw: Table 53a
of the latest Schools release (repo). Processed: `ratios`, long: year, state or territory, school affiliation
(government, non-government, Catholic, independent, all), school level (primary, secondary, all) and the ratio. The
ABS's sort prefixes ("a NSW", "b Secondary School") are dropped, and the level's case made one. Licence: CC BY 4.0
(ABS).
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get

PAGE = "https://www.abs.gov.au/statistics/people/education/schools/latest-release"
TABLE = re.compile(r'href="(/statistics/people/education/schools/\d{4}/Table%2053a[^"]+\.xlsx)"')


def ratios(frame: pd.DataFrame) -> pd.DataFrame:
    """The data sheet, read with no header: the header row starts with 'Year'."""
    head = frame.index[frame[0].astype(str).str.strip().eq("Year")]
    if len(head) == 0:
        raise CorpusError("abs_schools: Table 53a has no header row starting with 'Year'")
    data = frame.loc[head[0] + 1 :, :4].dropna(how="any")
    data.columns = ["year", "state", "affiliation", "level", "ratio"]
    data = data[data["year"].astype(str).str.fullmatch(r"\d{4}")]
    out = data.assign(
        year=data["year"].astype(int),
        ratio=pd.to_numeric(data["ratio"], errors="coerce"),
        **{
            c: data[c].astype(str).str.replace(r"^[a-z] ", "", regex=True).str.strip()
            for c in ("state", "affiliation", "level")
        },
    )
    out["level"] = out["level"].str.capitalize()  # "Secondary School" in some years, "Secondary school" in others
    return out.dropna(subset=["ratio"]).reset_index(drop=True)


def run(ctx: Ctx) -> None:
    m = TABLE.search(http_get(PAGE).text)
    if m is None:
        raise CorpusError("abs_schools: no Table 53a on the latest Schools release")
    p = ctx.fetch("https://www.abs.gov.au" + m.group(1), "schools_table_53a.xlsx", keep="repo")
    book = pd.read_excel(p, sheet_name=None, header=None, engine="calamine", dtype=str)
    sheet = next((s for s in book if "data" in s.lower()), None)
    if sheet is None:
        raise CorpusError("abs_schools: Table 53a has no data sheet")
    out = ratios(book[sheet])
    ctx.log(f"{out.year.min()} to {out.year.max()}, {len(out):,} ratios")
    ctx.table(out, "ratios", describe="ABS Schools Table 53a: FTE student to FTE teaching staff ratios, long")
