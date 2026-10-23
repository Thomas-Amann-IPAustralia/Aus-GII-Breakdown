"""2021 Census General Community Profile (GCP) for SA2s and postal areas: social capital, health and the workforce.

Stands in for the NATSEM small-area wellbeing and trust estimates, which cannot be fetched: the Census has no life
satisfaction or trust questions, but its small-area measures of social capital (volunteering, unpaid care for others,
residential stability), health (long-term conditions, including mental health conditions, and need for assistance)
and the local workforce (industry, occupation, fields of qualification) let wellbeing and cohesion sit beside regional
IP use (context, not effect; section 2 of docs/data-plan.md). Raw: the ABS DataPacks (short headers; R2). CC BY 4.0.

Processed, for `sa2` and `poa` (postal areas, which join to IP Australia's postcodes):
- `<geo>_g01` and so on: the selected GCP tables as published (one row per area, one column per cell; codes in the
  first column), joined across a table's parts (G19A, G19B and so on).
- `cells`: every cell's short name, long name and table, from the DataPack metadata, to read the columns.

Tables: G01 selected person characteristics; G02 medians and averages; G18 need for assistance; G19 and G20
long-term health conditions; G23 volunteering; G25 unpaid assistance to a person with a disability, health condition
or old age; G43 labour force, education and migration; G44 and G45 address one and five years ago; G46 labour force
status; G50 field of study; G54 industry of employment; G60 occupation.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import Ctx, unzip_member, unzip_names

URL = "https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_{geo}_for_AUS_short-header.zip"
TABLES = ["G01", "G02", "G18", "G19", "G20", "G23", "G25", "G43", "G44", "G45", "G46", "G50", "G54", "G60"]
GEOS = {"sa2": "SA2", "poa": "POA"}


def run(ctx: Ctx) -> None:
    cells = None
    for geo, code in GEOS.items():
        z = ctx.fetch(URL.format(geo=code), f"2021_GCP_{code}_for_AUS_short-header.zip", keep="r2")
        names = unzip_names(z)
        if cells is None:
            meta = next(n for n in names if re.search(r"Metadata_2021_GCP_DataPack.*\.xlsx$", n))
            sheets = pd.read_excel(unzip_member(z, meta, ctx.cache / "x"), sheet_name=None, header=None, dtype=str)
            d = sheets["Cell Descriptors Information"]
            head = next(i for i in range(30) if "Short" in " ".join(d.iloc[i].fillna("")))
            d.columns = [re.sub(r"[^a-z]+", "_", str(c).lower()).strip("_") for c in d.iloc[head]]
            cells = d.iloc[head + 1 :].dropna(how="all")
        for t in TABLES:
            parts = sorted(n for n in names if re.search(rf"2021Census_{t}[A-Z]?_AUST_{code}\.csv$", n))
            if not parts:
                ctx.note(f"{geo}: no {t} in the DataPack")
                continue
            df = None
            for n in parts:
                p = pd.read_csv(unzip_member(z, n, ctx.cache / "x"), dtype={f"{code}_CODE_2021": str})
                key = p.columns[0]
                df = p if df is None else df.merge(p, on=key, how="outer", suffixes=("", "_dup"))
            df = df[[c for c in df.columns if not c.endswith("_dup")]]
            ctx.table(df, f"{geo}_{t.lower()}", describe=f"2021 Census GCP {t}, by {code}")
    ctx.table(cells.astype(str).replace("nan", None), "cells", describe="Census GCP cell descriptors")
