"""ABS Characteristics of Australian Business, the latest release's data cubes (gap B4).

The ABS Data API's business characteristics flows (`abs_bcs`) stop at 2023; later releases are published as data
cubes only. This reads every cube of each release named in `RELEASES` (the ABS published 2024-25 after 2021-22, with
no 2023-24 release page): innovation activity, collaboration, finance and barriers, business profile and
performance, skills, ICT and cyber security, by industry division and employment size. Raw: each cube (repo).
Processed: `cubes`, every table long (see `_abs_cube.read_cube`: every published cell, with its unit where a row
states one, and its row in the sheet), with `release` and `cube`.
"""

from __future__ import annotations

import re
from urllib.parse import unquote

import pandas as pd

from ..core import CorpusError, Ctx, http_get
from ._abs_cube import read_cube

BASE = "https://www.abs.gov.au/statistics/industry/technology-and-innovation/characteristics-australian-business/"
RELEASES = ["2024-25"]


def run(ctx: Ctx) -> None:
    frames = []
    for rel in RELEASES:
        html = http_get(BASE + rel).text
        links = sorted(set(re.findall(r'href="(/statistics/[^"]+\.xlsx)"', html)))
        if not links:
            raise CorpusError(f"abs_bcs_cubes: no data cubes on the {rel} release")
        for link in links:
            url = "https://www.abs.gov.au" + link
            name = unquote(link.rsplit("/", 1)[1]).replace("–", "-")
            t = read_cube(ctx.fetch(url, name, keep="repo"))
            if t.empty:
                ctx.note(f"abs_bcs_cubes: nothing read from {name}")
                continue
            frames.append(t.assign(release=rel, cube=name))
    ctx.table(pd.concat(frames, ignore_index=True), "cubes", describe="ABS business characteristics cubes, long")
