"""Federal Court IP judgments.

Enforcement costs and outcomes (Q1.3). This environment cannot fetch it: put the files in data/raw/fedcourt/ and run
`corpus run fedcourt`. To get them: A CSV of IP judgments (patents, trade marks, designs, copyright) with columns
citation, date, parties, right, outcome, url, from the Federal Court's judgments search or a licensed database. The
Federal Court site and AustLII refuse this environment, and AustLII's terms do not allow bulk downloading.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.
"""

from __future__ import annotations

from ..core import Ctx
from ._manual import read_dropped

HOW = (
    "A CSV of IP judgments (patents, trade marks, designs, copyright) with columns citation, date, parties, "
    "right, outcome, url, from the Federal Court's judgments search or a licensed database. The Federal Court "
    "site and AustLII refuse this environment, and AustLII's terms do not allow bulk downloading."
)


def run(ctx: Ctx) -> None:
    read_dropped(ctx, HOW)
