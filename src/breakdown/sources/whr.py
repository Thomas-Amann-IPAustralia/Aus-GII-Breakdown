"""The World Happiness Report 2026's data for figure 2.1 (data/raw/whr/whr-2026-figure-2-1.xlsx): each country's life
evaluation (a three-year average ending in the year shown) for 2011 to 2025, and the parts of it a model attributes
to six factors. Read twice: Australia's years (over time) and every country's latest year (economies compared).

The "explained by" columns are a split of the life evaluation itself, so they are linked to it (`parts_of`).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..countries import Countries
from ..lenses import Lenses
from ..model import BuildError, EconVar, TimeVar, number, slug

SRC = "whr"
SCORE = "Life evaluation (3-year average)"


def _columns(d: pd.DataFrame) -> list[str]:
    skip = {"Year", "Rank", "Country name", "Lower whisker", "Upper whisker"}
    cols = [c for c in d.columns if c not in skip]
    if SCORE not in cols:
        raise BuildError(f"whr: no {SCORE!r} column; the file's layout changed")
    return cols


def _meta(col: str) -> tuple[str, str, list[str]]:
    if col == SCORE:
        return "whr:life-evaluation", "Life evaluation, 3-year average (WHR)", []
    return (f"whr:{slug(col)}", f"Life evaluation {col[0].lower()}{col[1:]} (WHR)", ["whr:life-evaluation"])


def _read(path: Path) -> pd.DataFrame:
    try:
        return pd.read_excel(path, engine="calamine")
    except Exception as e:  # noqa: BLE001
        raise BuildError(f"whr: cannot read {path} ({e})") from e


def read_series(path: Path, lenses: Lenses) -> tuple[list[TimeVar], dict]:
    d = _read(path)
    au = d[d["Country name"] == "Australia"]
    if au.empty:
        raise BuildError(f"whr: no rows for Australia in {path}")
    out = []
    for col in _columns(d):
        vid, name, parts = _meta(col)
        values = {int(y): v for y, x in zip(au["Year"], au[col], strict=True) if (v := number(x)) is not None}
        out.append(
            TimeVar(
                id=vid,
                name=name,
                source=SRC,
                topic="Happiness",
                lens=lenses.of(SRC),
                unit="0-10 (Cantril ladder)" if not parts else "share of the 0-10 score",
                values=values,
                description="World Happiness Report 2026, data for figure 2.1. The year is the last of a three-year "
                "average.",
                parts_of=parts,
                kind="index" if not parts else "value",
            )
        )
    return out, {"variables": len(out), "years": sorted(int(y) for y in au["Year"])}


def read_latest(path: Path, countries: Countries, lenses: Lenses) -> tuple[list[EconVar], dict]:
    d = _read(path)
    latest = int(d["Year"].max())
    d = d[d["Year"] == latest]
    out, unmatched = [], set()
    for col in _columns(d):
        vid, name, parts = _meta(col)
        values = {}
        for country, x in zip(d["Country name"], d[col], strict=True):
            iso = countries.iso3(country)
            if iso is None:
                unmatched.add(country)
            elif (v := number(x)) is not None:
                values[iso] = v
        out.append(
            EconVar(
                id=vid,
                name=name,
                source=SRC,
                topic="Happiness",
                lens=lenses.of(SRC),
                unit="0-10 (Cantril ladder)" if not parts else "share of the 0-10 score",
                year=str(latest),
                values=values,
                description=f"World Happiness Report 2026, data for figure 2.1: {latest - 2}-{latest} average.",
                parts_of=parts,
                kind="index" if not parts else "value",
            )
        )
    return out, {"variables": len(out), "year": latest, "unmatched": sorted(unmatched)}
