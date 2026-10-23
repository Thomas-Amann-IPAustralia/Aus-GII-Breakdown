"""ABS research and experimental development (businesses, 8104.0; government and private non-profit, 8109.0;
higher education, 8111.0) and venture capital and later stage private equity (5678.0, discontinued after 2018-19).

Who does R&D in Australia, in which industries and fields, and how much, beside who uses the IP system. Raw: each
release's data cubes (repo). Processed: `cubes`, every table long (see `_abs_cube.read_cube`), with `release` and
`cube`.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get
from ._abs_cube import read_cube

BASE = "https://www.abs.gov.au/statistics"
RELEASES = {
    "berd": "industry/technology-and-innovation/research-and-experimental-development-businesses-australia",
    "goverd_pnp": "industry/technology-and-innovation/"
    "research-and-experimental-development-government-and-private-non-profit-organisations-australia",
    "herd": "industry/technology-and-innovation/"
    "research-and-experimental-development-higher-education-organisations-australia",
    "venture_capital": "economy/finance/venture-capital-and-later-stage-private-equity-australia",
}


def run(ctx: Ctx) -> None:
    frames = []
    for name, path in RELEASES.items():
        html = http_get(f"{BASE}/{path}/latest-release").text
        links = sorted(set(re.findall(r'href="(/statistics/[^"]+\.xlsx?)"', html)))
        if not links:
            raise CorpusError(f"abs_rd_vc: no data cubes on {name}'s latest release")
        for link in links:
            fname = f"{name}-{link.rsplit('/', 1)[1]}"
            f = ctx.fetch("https://www.abs.gov.au" + link, fname, keep="repo")
            t = read_cube(f)
            if t.empty:
                ctx.note(f"abs_rd_vc: nothing read from {fname}")
                continue
            frames.append(t.assign(release=name, cube=link.rsplit("/", 1)[1], period=link.rsplit("/", 2)[1]))
    ctx.table(pd.concat(frames, ignore_index=True), "cubes", describe="ABS R&D and venture capital cubes, long")
