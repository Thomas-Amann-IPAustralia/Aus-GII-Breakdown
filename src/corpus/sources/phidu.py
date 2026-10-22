"""PHIDU Social Health Atlas of Australia: health, wellbeing and social indicators by Population Health Area.

Modelled small-area estimates of mental health (psychological distress), self-assessed health and risk factors, with
Census health conditions, mortality, use of health services and social indicators (volunteering, education,
income support and more), beside regional IP use (context, not effect; section 2 of docs/data-plan.md). Replaces the
NATSEM wellbeing and trust estimates, which cannot be reached. CC BY-NC-SA 3.0 AU (non-commercial use only). The
site's files do not answer this environment, so the September 2026 workbooks were downloaded by hand from
https://phidu.torrens.edu.au/social-health-atlases/data and put in R2 under `raw/phidu/` (too big for GitHub's web
upload): Population Health Areas (demographic and social; health status; use and provision of health services) and
the socioeconomic quintiles. To update, replace them there and run `corpus run phidu`.

Population Health Areas are SA2s or groups of SA2s (2021 ASGS); each workbook's `PHAs` sheet lists them.

Processed: `indicators`, one row per workbook, sheet, area, indicator, period and measure (long). `area_code` is the
PHA code (empty for state and national totals, whose names are in `area_name`); for the quintiles workbook,
`area_name` is the area type (capital cities, rest of state) and `quintile` the socioeconomic quintile.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import BUCKET, CorpusError, Ctx, r2

SKIP = {"Front_page", "Contents", "Topics", "PHAs", "Key", "Notes_on_the_data"}


def _text(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if pd.notna(v) else ""


def sheet(df: pd.DataFrame) -> pd.DataFrame | None:
    """One sheet, long: a title row of indicators, the period above the header row, a measure per column."""
    h = next((i for i in range(min(12, len(df))) if _text(df.iat[i, 0]) in ("Code", "Area name")), None)
    if h is None:
        return None
    indicator = df.iloc[0, 2:].map(_text).replace("", None).ffill()
    period = df.iloc[h - 1, 2:].map(_text).replace("", None).ffill()
    measure = df.iloc[h, 2:].map(_text)
    body = df.iloc[h + 1 :]
    col0 = body[0].map(_text)
    col1 = body[1].map(_text)
    quintiles = _text(df.iat[h, 0]) == "Area name"
    out = []
    for j in indicator.index:
        values = pd.to_numeric(body[j], errors="coerce")
        keep = values.notna()
        if not keep.any():
            continue
        part = pd.DataFrame(
            {
                "area_code": None if quintiles else col0.where(col0.str.fullmatch(r"\d+"))[keep],
                "area_name": (col0.replace("", None).ffill() if quintiles else col1.where(col1 != "", col0))[keep],
                "quintile": col1[keep] if quintiles else None,
                "indicator": indicator[j],
                "period": period[j],
                "measure": measure[j],
                "value": values[keep],
            }
        )
        out.append(part)
    return pd.concat(out, ignore_index=True) if out else None


def run(ctx: Ctx) -> None:
    keys = [
        o["Key"]
        for page in r2().get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix="raw/phidu/")
        for o in page.get("Contents", [])
        if o["Key"].endswith(".xlsx")
    ]
    if not keys:
        raise CorpusError(
            "phidu: no workbooks in R2 under raw/phidu/. From https://phidu.torrens.edu.au/social-health-atlases/data,"
            " the Population Health Area workbooks for Australia (and the quintiles workbook)."
        )
    out = []
    for key in sorted(keys):
        name = key.rsplit("/", 1)[-1]
        local = ctx.cache / name
        local.parent.mkdir(parents=True, exist_ok=True)
        r2().download_file(BUCKET, key, str(local))
        ctx.keep_raw(local, keep="r2")
        for sname, df in pd.read_excel(local, sheet_name=None, header=None, engine="calamine").items():
            if sname in SKIP:
                continue
            t = sheet(df)
            if t is None:
                ctx.note(f"{name} / {sname}: no header row found; left out")
                continue
            t.insert(0, "sheet", sname)
            t.insert(0, "workbook", name.removeprefix("phidu_data_").removesuffix("_aust.xlsx"))
            out.append(t)
            ctx.log(f"{name} / {sname}: {len(t):,} values")
    df = pd.concat(out, ignore_index=True)
    ctx.table(df, "indicators", describe="PHIDU Social Health Atlas indicators by PHA and quintile, long")
