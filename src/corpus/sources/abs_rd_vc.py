"""ABS research and experimental development (businesses, 8104.0; government and private non-profit, 8109.0;
higher education, 8111.0) and venture capital and later stage private equity (5678.0, discontinued after 2018-19).

Who does R&D in Australia, in which industries and fields, and how much, beside who uses the IP system. Raw: each
release's data cubes (repo). Processed: `cubes`, every table long (see `_abs_cube.read_cube`: every published cell,
with its unit where a row states one, and its row in the sheet), with `release`, `cube` and `period`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from ..core import CorpusError, Ctx, http_get, raw_path, read_manifest
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


def _build(ctx: Ctx, files: list[tuple[str, str, object]]) -> None:
    """Every table of the cubes (release, URL, path), long."""
    frames = []
    for name, url, f in files:
        t = read_cube(f)
        if t.empty:
            ctx.note(f"abs_rd_vc: nothing read from {Path(f).name}")
            continue
        frames.append(t.assign(release=name, cube=url.rsplit("/", 1)[1], period=url.rsplit("/", 2)[1]))
    ctx.table(pd.concat(frames, ignore_index=True), "cubes", describe="ABS R&D and venture capital cubes, long")


def run(ctx: Ctx) -> None:
    files = []
    for name, path in RELEASES.items():
        html = http_get(f"{BASE}/{path}/latest-release").text
        links = sorted(set(re.findall(r'href="(/statistics/[^"]+\.xlsx?)"', html)))
        if not links:
            raise CorpusError(f"abs_rd_vc: no data cubes on {name}'s latest release")
        for link in links:
            url = "https://www.abs.gov.au" + link
            files.append((name, url, ctx.fetch(url, f"{name}-{link.rsplit('/', 1)[1]}", keep="repo")))
    _build(ctx, files)


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """`cubes` again from the cubes the manifest records (in the repo), fetching nothing."""
    files = []
    for k, f in sorted(read_manifest()["sources"]["abs_rd_vc"]["files"].items()):
        if k.startswith("raw/"):
            name = k.split("/", 1)[1]
            files.append((name.split("-", 1)[0], f["url"], raw_path("abs_rd_vc", name)))
    _build(ctx, files)
