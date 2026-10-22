"""NHMRC grant outcomes.

Health and medical research funding by institution, scheme and field (Q2 research institutions; Q3 public funding).
This environment cannot fetch it: put the files in data/raw/nhmrc_grants/ and run `corpus run nhmrc_grants`. To get
them: From https://www.nhmrc.gov.au/funding/data-research/outcomes, the summary of results and grant outcomes
workbooks (xlsx). The NHMRC site refuses this environment.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.
"""

from __future__ import annotations

from ..core import Ctx
from ._manual import read_dropped

HOW = (
    "From https://www.nhmrc.gov.au/funding/data-research/outcomes, the summary of results and grant outcomes "
    "workbooks (xlsx). The NHMRC site refuses this environment."
)


def run(ctx: Ctx) -> None:
    read_dropped(ctx, HOW)
