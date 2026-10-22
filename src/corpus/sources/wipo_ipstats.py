"""WIPO IP statistics, filings by origin and office.

Q3: which countries' applicants file where, including trade marks, which the World Bank no longer publishes. This
environment cannot fetch it: put the files in data/raw/wipo_ipstats/ and run `corpus run wipo_ipstats`. To get them:
From the WIPO IP Statistics Data Center (https://www3.wipo.int/ipstats/), export as CSV, for all origins and all
available years: trade mark applications (class count) by origin; patent applications by origin; industrial design
applications (design count) by origin; PCT applications by origin; Madrid applications by origin. Its API is
undocumented, so this source reads the exports.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.
"""

from __future__ import annotations

from ..core import Ctx
from ._manual import read_dropped

HOW = (
    "From the WIPO IP Statistics Data Center (https://www3.wipo.int/ipstats/), export as CSV, for all origins and"
    " all available years: trade mark applications (class count) by origin; patent applications by origin; "
    "industrial design applications (design count) by origin; PCT applications by origin; Madrid applications by "
    "origin. Its API is undocumented, so this source reads the exports."
)


def run(ctx: Ctx) -> None:
    read_dropped(ctx, HOW)
