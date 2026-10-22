"""Border enforcement of IP.

Enforcement against counterfeits, and consumer safety (section 2 of docs/data-plan.md). This environment cannot fetch
it: put the files in data/raw/abf/ and run `corpus run abf`. To get them: The Australian Border Force's figures on
notices of objection and seizures of counterfeit and pirated goods, from the Department of Home Affairs annual reports
(performance tables), entered as a CSV with columns year, measure, value, source. Not published as data.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.
"""

from __future__ import annotations

from ..core import Ctx
from ._manual import read_dropped

HOW = (
    "The Australian Border Force's figures on notices of objection and seizures of counterfeit and pirated goods,"
    " from the Department of Home Affairs annual reports (performance tables), entered as a CSV with columns "
    "year, measure, value, source. Not published as data."
)


def run(ctx: Ctx) -> None:
    read_dropped(ctx, HOW)
