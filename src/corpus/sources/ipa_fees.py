"""IP Australia's current fees, as its website lists them, for the direct cost of obtaining and keeping each right.

Raw: each fees page's HTML (repo, as fetched). Processed: `fees`, every table on those pages, long: `right`, `page`,
`table` (its position on the page), `heading` (the nearest heading above it), `row` (the row's first cell), `column`
and `value` (the cell as published, for example "$250"), with `amount_aud` parsed where the cell is a single dollar
amount. Historical schedules are not here: the Wayback Machine is blocked from this environment, and the dates of
major fee changes are in `policy_events`.
"""

from __future__ import annotations

import re
from io import StringIO

import pandas as pd

from ..core import CorpusError, Ctx, http_get

PAGES = {
    "patent": "https://www.ipaustralia.gov.au/patents/timeframes-and-fees",
    "trade_mark": "https://www.ipaustralia.gov.au/trade-marks/timeframes-and-fees",
    "design": "https://www.ipaustralia.gov.au/design-rights/timeframes-and-fees",
    "pbr_1": "https://www.ipaustralia.gov.au/plant-breeders-rights/timeframes-and-fees-application-part-1",
    "pbr_2": "https://www.ipaustralia.gov.au/plant-breeders-rights/timeframes-and-fees-application-part-2",
    "renewals": "https://www.ipaustralia.gov.au/manage-my-ip/how-to-renew-my-ip-right",
    "oppositions": "https://www.ipaustralia.gov.au/manage-my-ip/someone-is-using-my-ip/how-to-challenge-someone-elses-ip/"
    "opposition-and-objection-fees",
    "fee_review_2023_24": "https://www.ipaustralia.gov.au/about-us/accountability-and-reporting/fee-review-2023-24",
}


def _headings(html: str) -> list[str]:
    """The nearest heading before each <table>, in order."""
    out, last = [], None
    for m in re.finditer(r"<h[1-4][^>]*>(.*?)</h[1-4]>|<table", html, re.S | re.I):
        if m.group(0).lower().startswith("<table"):
            out.append(last)
        else:
            last = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return out


def run(ctx: Ctx) -> None:
    rows = []
    for right, url in PAGES.items():
        html = http_get(url).text
        ctx.raw_text(f"{right}.html", html)
        try:
            tables = pd.read_html(StringIO(html))
        except ValueError:
            ctx.note(f"ipa_fees: no tables on {url}")
            continue
        heads = _headings(html)
        for i, t in enumerate(tables):
            t = t.astype(str)
            first = t.columns[0]
            for _, r in t.iterrows():
                for c in t.columns[1:]:
                    rows.append(
                        {
                            "right": right.split("_")[0] if right.startswith("pbr") else right,
                            "page": url,
                            "table": i,
                            "heading": heads[i] if i < len(heads) else None,
                            "row": r[first],
                            "column": str(c),
                            "value": r[c],
                        }
                    )
    if not rows:
        raise CorpusError("ipa_fees: no fee tables found")
    df = pd.DataFrame(rows)
    amt = df["value"].str.fullmatch(r"\s*\$\s?[\d,]+(\.\d+)?\s*")
    df["amount_aud"] = pd.to_numeric(df["value"].where(amt).str.replace(r"[$,\s]", "", regex=True), errors="coerce")
    ctx.table(df, "fees", describe="IP Australia fee tables, long")
