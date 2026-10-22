"""Cultural and creative activity in Australia.

The size of the creative industries, where copyright and design protection operate (section 2 of docs/data-plan.md).
This environment cannot fetch it: put the files in data/raw/bcarr_creative/ and run `corpus run bcarr_creative`. To
get them: From the Bureau of Communications, Arts and Regional Research (infrastructure.gov.au), the cultural and
creative activity data tables (xlsx). The site refuses this environment.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.
"""

from __future__ import annotations

from ..core import Ctx
from ._manual import read_dropped

HOW = (
    "From the Bureau of Communications, Arts and Regional Research (infrastructure.gov.au), the cultural and "
    "creative activity data tables (xlsx). The site refuses this environment."
)


def run(ctx: Ctx) -> None:
    read_dropped(ctx, HOW)
