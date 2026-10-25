"""PHIDU Social Health Atlas of Australia: health, wellbeing and social indicators by Population Health Area.

Modelled small-area estimates of mental health (psychological distress), self-assessed health and risk factors, with
Census health conditions, mortality, use of health services and social indicators (volunteering, education,
income support and more), beside regional IP use (context, not effect; section 2 of docs/data-plan.md). Replaces the
NATSEM wellbeing and trust estimates, which cannot be reached. CC BY-NC-SA 3.0 AU (non-commercial use only). The
site's files do not answer this environment, so the September 2026 workbooks were downloaded by hand from
https://phidu.torrens.edu.au/social-health-atlases/data and put in R2 under `raw/phidu/` (too big for GitHub's web
upload): Population Health Areas (demographic and social; health status; use and provision of health services) and
the socioeconomic quintiles. To update, replace them there and run `corpus run phidu`.

Population Health Areas (PHAs) are SA2s or groups of SA2s (2021 ASGS); each workbook's `PHAs` sheet lists them.

Processed:
- `indicators`, one row per workbook, sheet, area, indicator, sub-indicator, period and measure (long). Each sheet's
  columns sit under up to three label rows: `indicator` (the top one), `sub_indicator` (the rows below it, such as
  the cancer type or the developmental domain, joined with " | ") and `period`; a top row that is a caveat (a
  sentence, as on the cancer sheets) is kept as `note` instead. `area_type` is `pha`, `sa3` or `sa4` (each sheet lists
  the PHAs, then SA4 and SA3 totals, whose 5-digit SA3 codes look like PHA codes), `total` (state and national totals,
  named in `area_name`, with no code) or `quintile`; `area_code` is the area's code. For the quintiles workbook,
  `area_name` is the area type (capital cities, rest of state) and `quintile` the socioeconomic quintile. Every row's
  key is unique (ADR 0011: before, the sub-indicator was dropped, so 62,893 keys on the health sheets held several
  different values).
- `pha_sa2`: each PHA's SA2s (2021), from the `PHAs` sheet, with the section it is listed under (for example
  "NSW - Greater Sydney"). With `abs_regions/poa_sa2` it places the indicators in postal areas.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import BUCKET, CorpusError, Ctx, r2, raw_path, read_manifest

SKIP = {"Front_page", "Contents", "Topics", "PHAs", "Key", "Notes_on_the_data"}
KEY = [
    "workbook",
    "sheet",
    "area_type",
    "area_code",
    "area_name",
    "quintile",
    "indicator",
    "sub_indicator",
    "period",
    "measure",
]


def _text(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if pd.notna(v) else ""


def _labels(df: pd.DataFrame, rows: list[int]) -> list[list[str]]:
    """Each data column's label at each level (rows, top first), filled across like merged cells: a level carries
    over from the column to its left unless a higher level starts a new group in this column."""
    out, prev = [], [""] * len(rows)
    for j in range(2, df.shape[1]):
        cur, new_group = [], False
        for k, i in enumerate(rows):
            t = _text(df.iat[i, j])
            if t:
                new_group = True
            cur.append(t or ("" if new_group else prev[k]))
        out.append(cur)
        prev = cur
    return out


def sheet(df: pd.DataFrame) -> pd.DataFrame | None:
    """One sheet, long: label rows of indicators, the period above the header row, a measure per column."""
    h = next((i for i in range(min(12, len(df))) if _text(df.iat[i, 0]) in ("Code", "Area name")), None)
    if h is None or h < 2:
        return None
    first = next((_text(x) for x in df.iloc[0, 2:] if _text(x)), "")
    note_row = first.endswith(".")  # a caveat in a sentence, not a label
    label_rows = list(range(1 if note_row else 0, h - 1))
    labels = _labels(df, label_rows)
    note = " ".join(dict.fromkeys(_text(x) for x in df.iloc[0, 2:] if _text(x))) if note_row else None
    period = df.iloc[h - 1, 2:].map(_text).replace("", None).ffill()
    measure = df.iloc[h, 2:].map(_text)
    body = df.iloc[h + 1 :]
    col0 = body[0].map(_text)
    col1 = body[1].map(_text)
    quintiles = _text(df.iat[h, 0]) == "Area name"
    # column groups: a group starts where a label or period cell has text. Where two groups carry the same labels
    # and period (the quintiles' migrant sheets), each is told apart by its first measure.
    starts = [j for j in range(2, df.shape[1]) if any(_text(df.iat[i, j]) for i in [*label_rows, h - 1])]
    group = {j: max((s for s in starts if s <= j), default=2) for j in range(2, df.shape[1])}
    heads = {g: (tuple(labels[g - 2]), period[g]) for g in set(group.values())}
    repeated = {g for g in heads if list(heads.values()).count(heads[g]) > 1}
    area = col0.where(col0.str.fullmatch(r"\d+")) if not quintiles else None
    name = col0.replace("", None).ffill() if quintiles else col1.where(col1 != "", col0).replace("", None)
    # the PHAs come first, then named totals (no code), then each SA4 (3 digits) followed by its SA3s (5 digits, like
    # PHA codes), so the SA rows start at the first SA4
    sa_rows = area.str.len().eq(3).cumsum() > 0 if not quintiles else None
    kind = pd.Series("quintile" if quintiles else "total", index=body.index)
    if not quintiles:
        kind[area.str.len().eq(3)] = "sa4"
        kind[area.str.len().eq(5) & sa_rows] = "sa3"
        kind[area.str.len().eq(5) & ~sa_rows] = "pha"
    out = []
    for n, j in enumerate(range(2, df.shape[1])):
        values = pd.to_numeric(body[j], errors="coerce")
        keep = values.notna() & (name.notna() if quintiles else (area.notna() | name.notna()))  # not spacer rows
        if not keep.any():
            continue
        top, *rest = labels[n] if label_rows else [""]
        if group[j] in repeated:
            rest = [*rest, measure[group[j]]]
        out.append(
            pd.DataFrame(
                {
                    "area_type": kind[keep],
                    "area_code": None if quintiles else area[keep],
                    "area_name": name[keep],
                    "quintile": col1[keep] if quintiles else None,
                    "indicator": top or None,
                    "sub_indicator": " | ".join(r for r in rest if r) or None,
                    "period": period[j],
                    "measure": measure[j],
                    "note": note,
                    "value": values[keep],
                }
            )
        )
    return pd.concat(out, ignore_index=True) if out else None


def pha_sa2(df: pd.DataFrame) -> pd.DataFrame:
    """The PHAs sheet: SA2 codes (comma-separated), SA2 names, PHA code and PHA name, under section rows."""
    h = next(i for i in range(min(20, len(df))) if _text(df.iat[i, 0]) == "SA2 codes")
    rows, section = [], None
    for i in range(h + 1, len(df)):
        codes, pha, name = _text(df.iat[i, 0]), _text(df.iat[i, 2]), _text(df.iat[i, 3])
        if codes and not pha:
            section = codes
            continue
        for sa2 in re.findall(r"\d{9}", codes):
            rows.append((pha, name, sa2, section))
    return pd.DataFrame(rows, columns=["pha_code", "pha_name", "sa2_code", "section"])


def _build(ctx: Ctx, files: dict[str, object]) -> None:
    out, pairs = [], None
    for name, local in sorted(files.items()):
        for sname, df in pd.read_excel(local, sheet_name=None, header=None, engine="calamine").items():
            if sname == "PHAs" and pairs is None:
                pairs = pha_sa2(df)
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
    dupes = df.duplicated(KEY).sum()
    if dupes:
        raise CorpusError(f"phidu: {dupes} rows repeat a key ({', '.join(KEY)})")
    ctx.table(df, "indicators", describe="PHIDU Social Health Atlas indicators by PHA and quintile, long")
    if pairs is None:
        raise CorpusError("phidu: no workbook has a PHAs sheet")
    ctx.table(pairs, "pha_sa2", describe="PHIDU Population Health Areas and their SA2s (2021)")


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
    files = {}
    for key in sorted(keys):
        name = key.rsplit("/", 1)[-1]
        local = ctx.cache / name
        local.parent.mkdir(parents=True, exist_ok=True)
        r2().download_file(BUCKET, key, str(local))
        ctx.keep_raw(local, keep="r2")
        files[name] = local
    _build(ctx, files)


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """The tables again from the workbooks the manifest records (in R2), fetching nothing new."""
    names = [k.split("/", 1)[1] for k in read_manifest()["sources"]["phidu"]["files"] if k.startswith("raw/")]
    _build(ctx, {n: raw_path("phidu", n) for n in names})
