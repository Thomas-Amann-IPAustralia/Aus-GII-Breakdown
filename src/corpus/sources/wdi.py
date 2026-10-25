"""World Development Indicators comparator panel (World Bank): the indicators that bear on the IP system, for every
country and year, from the World Bank's API.

Raw: each indicator's API response (repo, gzipped JSON). Processed: `panel` (country ISO3 and name, indicator code
and name, year, value) and `countries` (ISO3, region, income group, and whether it is an aggregate rather than a
country).
"""

from __future__ import annotations

import gzip
import json

import pandas as pd

from ..core import Ctx, http_get

API = "https://api.worldbank.org/v2"
INDICATORS = [
    "IP.PAT.RESD",  # patent applications, residents
    "IP.PAT.NRES",  # patent applications, non-residents
    "IP.TMK.RSCT",  # trade mark applications, resident, by count (replaced IP.TMK.RESD, NRES and TOTL, withdrawn)
    "IP.TMK.NRCT",  # trade mark applications, nonresident, by count
    "IP.IDS.RSCT",  # industrial design applications, resident, by count
    "IP.IDS.NRCT",
    "IP.JRN.ARTC.SC",  # scientific and technical journal articles
    "BX.GSR.ROYL.CD",  # charges for the use of IP, receipts
    "BM.GSR.ROYL.CD",  # charges for the use of IP, payments
    "GB.XPD.RSDV.GD.ZS",  # R&D expenditure, % of GDP
    "SP.POP.SCIE.RD.P6",  # researchers per million
    "SP.POP.TECH.RD.P6",  # technicians per million
    "TX.VAL.TECH.MF.ZS",  # high-technology exports, % of manufactured exports
    "TX.VAL.TECH.CD",
    "IC.BUS.NREG",  # new businesses registered
    "IC.BUS.NDNS.ZS",  # new business density
    "NY.GDP.PCAP.PP.KD",  # GDP per capita, PPP, constant
    "NY.GDP.MKTP.PP.KD",
    "SP.POP.TOTL",
    "NV.IND.MANF.ZS",  # manufacturing value added, % of GDP
    "NE.EXP.GNFS.ZS",  # exports, % of GDP
    "BX.KLT.DINV.WD.GD.ZS",  # FDI net inflows, % of GDP
    "SE.TER.ENRR",  # tertiary enrolment, gross
    "SL.TLF.ADVN.ZS",  # labour force with advanced education
]


def run(ctx: Ctx) -> None:
    rows = []
    for code in INDICATORS:
        data, page, pages = [], 1, 1
        while page <= pages:
            resp = http_get(
                f"{API}/country/all/indicator/{code}", params={"format": "json", "per_page": 20000, "page": page}
            ).json()
            if len(resp) < 2:  # an archived or deleted indicator answers with a message only
                ctx.note(f"wdi: {code} is no longer in the API ({resp[0].get('message', [{}])[0].get('value')})")
                break
            pages = resp[0]["pages"]
            data += resp[1] or []
            page += 1
        if not data:
            continue
        p = ctx.raw / f"{code}.json.gz"
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
            f.write(json.dumps(data, sort_keys=True).encode())
        ctx.keep_raw(p, url=f"{API}/country/all/indicator/{code}")
        for d in data:
            if d.get("value") is not None:
                rows.append(
                    {
                        "iso3": d["countryiso3code"] or None,
                        "country": d["country"]["value"],
                        "indicator": code,
                        "indicator_name": d["indicator"]["value"],
                        "year": int(d["date"]),
                        "value": float(d["value"]),
                    }
                )
    ctx.table(pd.DataFrame(rows), "panel", describe="WDI indicators bearing on IP, every country and year")
    meta, cs = http_get(f"{API}/country", params={"format": "json", "per_page": 400}).json()
    countries = pd.DataFrame(
        [
            {
                "iso3": c["id"],
                "name": c["name"],
                "region": c["region"]["value"],
                "income": c["incomeLevel"]["value"],
                "aggregate": c["region"]["value"] == "Aggregates",
            }
            for c in cs
        ]
    )
    ctx.table(countries, "countries", describe="WDI countries and aggregates")
