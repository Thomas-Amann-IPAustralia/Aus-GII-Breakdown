"""The World Bank's World Development Indicators for Australia (data/raw/world-bank/wdi-australia.xls).

The Data sheet has one row per indicator and one column per year (1960 onwards); the Metadata - Indicators sheet
gives each indicator's definition and source. Indicators with fewer than `MIN_YEARS` years of data are left out:
too short to compare over time.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..lenses import Lenses
from ..model import BuildError, TimeVar, clean, number

SRC = "wdi"
MIN_YEARS = 5

# The first part of a WDI code names its topic.
TOPICS = {
    "AG": "Agriculture and rural development",
    "BG": "Balance of payments",
    "BM": "Balance of payments",
    "BN": "Balance of payments",
    "BX": "Balance of payments",
    "CM": "Financial sector",
    "DC": "Aid and debt",
    "DT": "Aid and debt",
    "EG": "Energy",
    "EN": "Environment",
    "ER": "Environment",
    "FB": "Financial sector",
    "FD": "Financial sector",
    "FI": "Financial sector",
    "FM": "Financial sector",
    "FR": "Financial sector",
    "FS": "Financial sector",
    "FX": "Financial sector",
    "FP": "Prices",
    "GB": "Science and technology",
    "GC": "Public sector",
    "GD": "Gender",
    "GF": "Public sector",
    "GOV": "Governance",
    "HD": "Human capital",
    "IC": "Private sector",
    "IE": "Infrastructure",
    "IP": "Science and technology",
    "IQ": "Statistical capacity",
    "IS": "Infrastructure",
    "IT": "Infrastructure",
    "LP": "Trade",
    "MS": "Public sector",
    "NE": "Economy (national accounts)",
    "NV": "Economy (national accounts)",
    "NY": "Economy (national accounts)",
    "PA": "Prices",
    "PX": "Prices",
    "SE": "Education",
    "SG": "Gender",
    "SH": "Health",
    "SI": "Poverty and inequality",
    "SL": "Labour",
    "SM": "Population",
    "SN": "Health",
    "SP": "Population",
    "ST": "Trade",
    "TG": "Trade",
    "TM": "Trade",
    "TT": "Trade",
    "TX": "Trade",
    "VC": "Social",
    "per": "Social protection",
}


def _topic(code: str) -> str:
    head = code.split(".")[0].split("_")[0]
    if code.startswith(("IP.PAT", "IP.TMK", "IP.IDS", "BX.GSR.ROYL", "BM.GSR.ROYL")):
        return "Intellectual property"
    return TOPICS.get(head, "Other")


def read(path: Path, lenses: Lenses) -> tuple[list[TimeVar], dict]:
    try:
        data = pd.read_excel(path, sheet_name="Data", header=3, engine="calamine")
        meta = pd.read_excel(path, sheet_name="Metadata - Indicators", engine="calamine")
    except Exception as e:  # noqa: BLE001
        raise BuildError(f"wdi: cannot read {path} ({e}); check it is the World Bank's country download") from e
    if not {"Indicator Code", "Indicator Name", "Country Code"} <= set(data.columns):
        raise BuildError(f"wdi: {path} has no 'Indicator Code' header on row 4; the download's layout changed")
    if set(data["Country Code"].dropna()) != {"AUS"}:
        raise BuildError(f"wdi: {path} holds countries other than Australia")
    notes = {r.INDICATOR_CODE: (clean(r.SOURCE_NOTE), clean(r.SOURCE_ORGANIZATION)) for r in meta.itertuples()}
    years = [c for c in data.columns if str(c).split(".")[0].isdigit()]

    out, short = [], 0
    for r in data.to_dict("records"):
        code = str(r["Indicator Code"]).strip()
        values = {int(float(y)): v for y in years if (v := number(r[y])) is not None}
        if len(values) < MIN_YEARS:
            short += 1
            continue
        name = clean(r["Indicator Name"])
        note, org = notes.get(code, (None, None))
        unit = name[name.rfind("(") + 1 : -1] if name.endswith(")") and "(" in name else None
        out.append(
            TimeVar(
                id=f"wdi:{code}",
                name=name,
                source=SRC,
                topic=_topic(code),
                lens=lenses.of("wdi", code),
                unit=unit,
                values=values,
                description=" ".join(b for b in [note, f"Source: {org}." if org else None] if b) or None,
                kind="rank" if "rank" in name.lower() else "value",
            )
        )
    return out, {"indicators": len(data), "kept": len(out), "too_short": short}
