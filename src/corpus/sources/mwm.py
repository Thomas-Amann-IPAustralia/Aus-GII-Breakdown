"""Measuring What Matters (Treasury and ABS): the Australian Government's wellbeing framework, five themes (healthy,
secure, sustainable, cohesive, prosperous) and about 50 indicators, plus overall life satisfaction.

The outcome layer and vocabulary for public value (section 2 of docs/data-plan.md): used to frame and value outcomes,
not to correlate with IP measures. The ABS publishes each indicator as a web page whose charts carry their data as
HTML tables. Raw: each page's HTML (repo, gzipped). Processed: `indicators` (theme, indicator, title, URL) and `data`,
long, one row per filled cell: `theme`, `indicator`, `table` (its position on the page), `caption`, `row` (the
table's first column, usually the period or group), `block` (the group, where a table stacks two under one header, as
males then females), `column` (the series) and `value` (numeric where the cell is a number; `value_text` keeps it).
"""

from __future__ import annotations

import gzip
import re
from io import StringIO

import pandas as pd

from ..core import CorpusError, Ctx, http_get, raw_path, read_manifest

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


def _meta(theme: str, indicator: str, url: str, html: str) -> dict:
    title = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    return {
        "theme": theme,
        "indicator": indicator,
        "url": url,
        "title": re.sub(r"<[^>]+>|\s+", " ", title.group(1)).strip() if title else indicator,
    }


def _block_names(t: pd.DataFrame) -> list[str | None]:
    """Some pages stack two groups in one table (males, then females), separated by an empty row, under one header
    whose first series is each group's total: so the same row and column hold two values. Each block is named by the
    prefix its filled series share ("Females - Very safe (%)" gives "Females"), or numbered (ADR 0019)."""
    empty = t.isna().all(axis=1)
    block = empty.cumsum().where(~empty)
    if block.nunique() < 2:
        return [None] * len(t)
    names = {}
    for b, part in t[~empty].groupby(block[~empty]):
        filled = [c for c in part.columns[2:] if part[c].notna().any()]
        prefixes = {c.split(" - ", 1)[0] for c in filled if " - " in c}
        names[b] = prefixes.pop() if len(prefixes) == 1 and all(" - " in c for c in filled) else f"block {int(b) + 1}"
    return [names.get(b) for b in block]


def _tables(ctx: Ctx, theme: str, indicator: str, html: str) -> list[pd.DataFrame]:
    """Every table on a page, long: one row per filled cell (empty cells are not values)."""
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        ctx.note(f"mwm: no tables on {indicator}")
        return []
    caps, out = _captions(html), []
    for i, t in enumerate(tables):
        t.columns = [" ".join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in t.columns]
        first = t.columns[0]
        t.insert(1, "block", _block_names(t))
        t = t[t.drop(columns=["block"]).notna().any(axis=1)]
        long = t.melt(id_vars=[first, "block"], var_name="column", value_name="value_text")
        long = long.dropna(subset=["value_text"]).rename(columns={first: "row"})
        long["row"] = long["row"].map(lambda v: None if pd.isna(v) else _text(v))
        long["value_text"] = long["value_text"].map(_text)
        long["value"] = pd.to_numeric(long["value_text"].str.replace(r"[,%$]", "", regex=True), errors="coerce")
        long.insert(0, "caption", caps[i] if i < len(caps) else None)
        long.insert(0, "table", i)
        long.insert(0, "indicator", indicator)
        long.insert(0, "theme", theme)
        out.append(long)
    return out


def _text(v) -> str:
    """A cell as text; pandas reads a column of years as floats, so 2021.0 is written 2021."""
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """The tables again from the pages kept in the repo, fetching nothing."""
    files = read_manifest()["sources"]["mwm"]["files"]
    meta, rows = [], []
    for k in sorted(k for k in files if k.startswith("raw/") and k.endswith(".html.gz")):
        f = raw_path("mwm", k.split("/", 1)[1])
        theme, indicator = f.name.removesuffix(".html.gz").split("--", 1)
        html = gzip.decompress(f.read_bytes()).decode()
        ctx.keep_raw(f)
        path = f"{ROOT}/{indicator}" if theme == "overall" else f"{ROOT}/{theme}/{indicator}"
        meta.append(_meta(theme, indicator, BASE + path, html))
        rows += _tables(ctx, theme, indicator, html)
    ctx.table(pd.DataFrame(meta), "indicators", describe="Measuring What Matters indicator pages")
    ctx.table(pd.concat(rows, ignore_index=True), "data", describe="Every table on the indicator pages, long")


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
        meta.append(_meta(theme, indicator, BASE + p, html))
        rows += _tables(ctx, theme, indicator, html)
    ctx.table(pd.DataFrame(meta), "indicators", describe="Measuring What Matters indicator pages")
    ctx.table(pd.concat(rows, ignore_index=True), "data", describe="Every table on the indicator pages, long")
