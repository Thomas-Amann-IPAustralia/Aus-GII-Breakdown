"""TGA's Australian Register of Therapeutic Goods (ARTG): every medicine and medical device on the register.

The health pathway (section 2 of docs/data-plan.md): how many sponsors supply each active ingredient (generic
competition), and which medicines and devices reach Australia. The TGA site does not respond to this environment, so
the ARTG search export was downloaded by hand (https://www.tga.gov.au/resources/artg, all entries, exported to xlsx)
into data/raw/tga/ (repo). The export is a snapshot of the current register: it has no start or cancellation dates.

Processed: `artg`, one row per ARTG entry and product (an entry can list several products, as 429 entries do; the
export's exact repeats are dropped), with `kind` medicine where there are active ingredients and device where there
is a device manufacturer; `artg_ingredients`, one row per entry and active ingredient (name in lower case, without
quantities), to join to PBS drugs and to patents' extension of term records by ingredient name.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx

COLUMNS = {
    "ARTG ID": "artg_id",
    "Product Name": "product_name",
    "Sponsor Name": "sponsor_name",
    "Manufacturer Name (Devices)": "device_manufacturer",
    "Active Ingredients": "active_ingredients",
}


def ingredients(s: str) -> list[str]:
    """'a, Quantity: 1 mg (Equivalent: b, Qty 1 mg); c, Quantity: 2 mg' -> ['a', 'c']."""
    s = re.sub(r"\([^()]*\)", "", s)
    names = (re.split(r",\s*(?:Quantity|Qty)\b", part)[0].strip().lower() for part in s.split(";"))
    return list(dict.fromkeys(n for n in names if n))


def run(ctx: Ctx) -> None:
    files = sorted(ctx.raw.glob("*.xlsx"))
    if not files:
        raise CorpusError(
            "tga: no export in data/raw/tga/ yet. From https://www.tga.gov.au/resources/artg, search all entries "
            "and export the results (xlsx)."
        )
    p = files[-1]
    ctx.keep_raw(p)
    df = pd.read_excel(p, dtype=str, engine="calamine")
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise CorpusError(f"tga: {p.name} has no column(s) {sorted(missing)}")
    df = df[list(COLUMNS)].rename(columns=COLUMNS)
    df = df[df["artg_id"].fillna("").str.fullmatch(r"\d+")]  # the export ends with a note on its filters
    df["artg_id"] = df["artg_id"].astype(int)
    df["device_manufacturer"] = df["device_manufacturer"].where(df["device_manufacturer"] != "Not Applicable")
    df["kind"] = "other"
    df.loc[df["device_manufacturer"].notna(), "kind"] = "device"
    df.loc[df["active_ingredients"].notna(), "kind"] = "medicine"
    df = df.drop_duplicates().sort_values("artg_id").reset_index(drop=True)
    ctx.table(df, "artg", describe=f"ARTG entries ({p.name}); no dates in the export")
    ing = df[["artg_id", "active_ingredients"]].dropna()
    ing = ing.assign(ingredient=ing["active_ingredients"].map(ingredients)).explode("ingredient")
    ing = ing.dropna(subset=["ingredient"])[["artg_id", "ingredient"]].drop_duplicates()
    ctx.table(ing, "artg_ingredients", describe="ARTG entry by active ingredient (lower case, no quantities)")
