"""Measuring What Matters (Treasury and ABS): the Australian Government's wellbeing framework, five themes (healthy,
secure, sustainable, cohesive, prosperous) and about 50 indicators, plus overall life satisfaction.

The outcome layer and vocabulary for public value (section 2 of docs/data-plan.md): used to frame and value outcomes,
not to correlate with IP measures. The ABS publishes each indicator as a web page whose charts carry their data as
HTML tables. Raw: each page's HTML (repo, gzipped). Processed: `indicators` (theme, indicator, title, URL) and `data`,
long: `theme`, `indicator`, `table` (its position on the page), `caption`, `row` (the table's first column, usually
the period or group), `column` (the series) and `value` (numeric where the cell is a number; `value_text` keeps it).
"""

from __future__ import annotations

import gzip
import re
from io import StringIO

import pandas as pd

from ..core import CorpusError, Ctx, http_get

BASE = "https://www.abs.gov.au"
ROOT = "/statistics/measuring-what-matters/measuring-what-matters-themes-and-indicators"
THEMES = ["healthy", "secure", "sustainable", "cohesive", "prosperous"]


def _captions(html: str) -> list[str | None]:
    caps, last = [], None
    for m in re.finditer(r"<h[2-4][^>]*>(.*?)</h[2-4]>|<caption[^>]*>(.*?)</caption>|<table", html, re.S | re.I):
        if m.group(0).lower().startswith("<table"):
            caps.append(last)
        else:
            last = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1) or m.group(2))).strip()
    return caps


def _keep(ctx: Ctx, name: str, html: str) -> None:
    p = ctx.raw / f"{name}.html.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
        f.write(html.encode())
    ctx.keep_raw(p)


def run(ctx: Ctx) -> None:
    pages = [("overall", f"{ROOT}/overall-life-satisfaction")]
    for t in THEMES:
        html = http_get(BASE + f"{ROOT}/{t}").text
        found = sorted(set(re.findall(rf'href="({ROOT}/{t}/[a-z0-9-]+)"', html)))
        pages += [(t, p) for p in found if not p.endswith("/print")]
    if len(pages) < 20:
        raise CorpusError(f"mwm: found only {len(pages)} indicator pages; has the site changed?")
    meta, rows = [], []
    for theme, p in pages:
        indicator = p.rsplit("/", 1)[1]
        html = http_get(BASE + p).text
        _keep(ctx, f"{theme}--{indicator}", html)
        title = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        meta.append(
            {
                "theme": theme,
                "indicator": indicator,
                "url": BASE + p,
                "title": re.sub(r"<[^>]+>|\s+", " ", title.group(1)).strip() if title else indicator,
            }
        )
        try:
            tables = pd.read_html(StringIO(html))
        except ValueError:
            ctx.note(f"mwm: no tables on {indicator}")
            continue
        caps = _captions(html)
        for i, t in enumerate(tables):
            t.columns = [" ".join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in t.columns]
            first = t.columns[0]
            long = t.astype(str).melt(id_vars=[first], var_name="column", value_name="value_text")
            long = long.rename(columns={first: "row"})
            long["value"] = pd.to_numeric(long["value_text"].str.replace(r"[,%$]", "", regex=True), errors="coerce")
            long.insert(0, "caption", caps[i] if i < len(caps) else None)
            long.insert(0, "table", i)
            long.insert(0, "indicator", indicator)
            long.insert(0, "theme", theme)
            rows.append(long)
    ctx.table(pd.DataFrame(meta), "indicators", describe="Measuring What Matters indicator pages")
    ctx.table(pd.concat(rows, ignore_index=True), "data", describe="Every table on the indicator pages, long")
