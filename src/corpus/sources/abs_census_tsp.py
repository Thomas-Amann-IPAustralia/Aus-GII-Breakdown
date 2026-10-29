"""2021 Census Time Series Profile (TSP) for SA2s: the 2011, 2016 and 2021 Censuses on 2021 boundaries (gap B6).

For Q2 and Q5: how each area's people, incomes, education and work changed over the decade, beside its IP. The 2021
General Community Profile (`abs_census`) is one Census; the Time Series Profile gives the same characteristics for
three Censuses on the same 2021 areas, so change can be read without boundary breaks. The ABS publishes it for SA2s
and larger areas, not for postal areas, so the regions lens apportions it from SA2s (ADR 0018's method). Raw: the
DataPack (short headers; R2). CC BY 4.0.

Processed:
- `cells`: long, one row per SA2, table, indicator and Census year: the indicator is the DataPack's short name
  without its year (`Tot_persons_P` for `Tot_persons_C11_P`), the label its long name without the year.

Tables (`TABLES`): T01 selected person characteristics; T02 medians and averages; T29 selected labour force,
education and migration characteristics; T34 industry of employment; T35 occupation. The age-by-sex tables (T28,
T31 to T33) are left out: they are large and the lens's questions need their totals only, which T01 and T29 carry.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx, unzip_member, unzip_names

URL = "https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_TSP_SA2_for_AUS_short-header.zip"
TABLES = {
    "T01": "Selected person characteristics",
    "T02": "Medians and averages",
    "T29": "Selected labour force, education and migration characteristics",
    "T34": "Industry of employment",
    "T35": "Occupation",
}
# a cell's Census year: `_C11`, `_C2011` or `_2011_Ce` (the names are cut to fit the DataPack's short headers)
YEAR = re.compile(r"_C(?:20)?(11|16|21)(?=_|$)|_20(11|16|21)_Ce(?=_|$)")


def labels(meta: pd.DataFrame) -> dict[str, str]:
    """Each short name without its year, to its long name without the year (`Total_persons_2011_Census_Males`
    becomes 'Total persons Males')."""
    head = next(i for i in range(30) if "Short" in " ".join(meta.iloc[i].fillna("").astype(str)))
    meta = meta.iloc[head + 1 :, [1, 2]].dropna()
    out = {}
    for short, long in meta.itertuples(index=False):
        key = YEAR.sub("", str(short))
        long = re.sub(r"_?(Census_year_)?20(11|16|21)(_Census)?", "", str(long))
        out.setdefault(key, long.replace("_", " ").strip())
    return out


def long_table(df: pd.DataFrame, table: str) -> pd.DataFrame:
    """A table as published (one row per SA2, a column per cell and year) made long."""
    key = df.columns[0]
    out = df.melt(id_vars=[key], var_name="column", value_name="value")
    year = out["column"].str.extract(YEAR).bfill(axis=1)[0]
    if year.isna().any():
        bad = out["column"][year.isna()].unique()[:5]
        raise CorpusError(f"abs_census_tsp: {table} has columns without a Census year: {bad}")
    return pd.DataFrame(
        {
            "sa2_code": out[key].astype(str),
            "table": table,
            "indicator": out["column"].str.replace(YEAR, "", regex=True),
            "census_year": ("20" + year).astype(int),
            "value": pd.to_numeric(out["value"], errors="coerce"),
        }
    ).dropna(subset=["value"])


def run(ctx: Ctx) -> None:
    z = ctx.fetch(URL, "2021_TSP_SA2_for_AUS_short-header.zip", keep="r2")
    names = unzip_names(z)
    meta = next(n for n in names if re.search(r"Metadata_2021_TSP_DataPack.*\.xlsx$", n))
    lab = labels(pd.read_excel(unzip_member(z, meta, ctx.cache / "x"), sheet_name=1, header=None, dtype=str))
    frames = []
    for t in TABLES:
        parts = sorted(n for n in names if re.search(rf"2021Census_{t}[A-Z]?_AUST_SA2\.csv$", n))
        if not parts:
            raise CorpusError(f"abs_census_tsp: no {t} in the DataPack")
        for n in parts:
            frames.append(long_table(pd.read_csv(unzip_member(z, n, ctx.cache / "x"), dtype={"SA2_CODE_2021": str}), t))
    out = pd.concat(frames, ignore_index=True).drop_duplicates(["sa2_code", "table", "indicator", "census_year"])
    out["label"] = out["indicator"].map(lab)
    ctx.log(f"{out.indicator.nunique():,} indicators, {out.sa2_code.nunique():,} SA2s, {len(out):,} values")
    ctx.table(out, "cells", describe="Census Time Series Profile (2011, 2016, 2021), by SA2, long")
