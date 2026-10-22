"""World Gender-Name Dictionary 2.0 (WIPO, 2021): first names with the gender they are given to, by country.

For estimating the gender of individual applicants in IPGOD from first names, the method WIPO and IP Australia have
used. IPGOD's public party data has no inventors, so this covers individual applicants (and owners) only.
Raw: the two Dataverse tables (R2). Processed: `name_gender_code` (name, ISO country code, gender F/M/?, and
`wgt`, the share of the name's bearers of that gender where known) and `name_gender` (the same without country).
Names are as WGND gives them (lower case, accents kept).
"""

from __future__ import annotations

import pandas as pd

from ..core import Ctx

FILES = {
    "name_gender_code": (4750348, "wgnd_2_0_name-gender-code.tab"),
    "name_gender": (4750351, "wgnd_2_0_name-gender_nocode.tab"),
}


def run(ctx: Ctx) -> None:
    for name, (fid, fname) in FILES.items():
        url = f"https://dataverse.harvard.edu/api/access/datafile/{fid}?format=original"
        f = ctx.fetch(url, fname, keep="r2")
        sep = "\t" if open(f, encoding="utf-8").readline().count("\t") else ","
        df = pd.read_csv(f, sep=sep, dtype=str, keep_default_na=False, na_values=[""])
        if "wgt" in df:
            df["wgt"] = pd.to_numeric(df["wgt"], errors="coerce")
        ctx.table(df, name, describe=f"WGND 2.0 {fname}")
