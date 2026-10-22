"""Australian wine geographical indications (Wine Australia's register of protected GIs and other terms).

For the cultural and regional identity pathway (section 2 of docs/data-plan.md); certification and collective trade
marks in IPGOD are the other side of it. Raw: the register page's HTML and its PDFs (the EU GI register, traditional
expressions, additional terms and quality wine terms; repo). Processed: `australian_gis`, one row per register line
with the state or zone, region and subregion as published (footnote markers kept).
"""

from __future__ import annotations

import re
from io import StringIO

import pandas as pd

from ..core import CorpusError, Ctx, http_get

BASE = "https://www.wineaustralia.com/labelling/register-of-protected-gis-and-other-terms/"
PAGES = ["geographical-indications", "traditional-expressions", "additional-terms", "quality-wine-terms"]


def run(ctx: Ctx) -> None:
    pdfs = set()
    table = None
    for p in PAGES:
        html = http_get(BASE + p).text
        ctx.raw_text(f"{p}.html", html)
        pdfs |= {u for u in re.findall(r'href="([^"]+\.pdf)"', html) if "values-and-behaviours" not in u}
        if p == "geographical-indications":
            tables = pd.read_html(StringIO(html))
            if not tables:
                raise CorpusError("wine_gi: the GI register page has no table")
            table = tables[0]
    for u in sorted(pdfs):
        url = u if u.startswith("http") else "https://www.wineaustralia.com" + u
        ctx.fetch(url, url.rsplit("/", 1)[1], keep="repo")
    table.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).lower()).strip("_") for c in table.columns]
    ctx.table(table.astype(str), "australian_gis", describe="Australian wine GIs: state or zone, region, subregion")
