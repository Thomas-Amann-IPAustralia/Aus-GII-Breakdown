"""The OECD's How's Life? current well-being indicators for Australia (data/raw/oecd/…current-wellbeing-australia.xlsx).

An OECD Data Explorer export: a 'Table' sheet with header rows labelled in column B (Domain, Measure, Unit of
measure, Time period), then one row per year, one column per measure. The rows are found by their labels, not
fixed positions, so a re-export with other measures still reads.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..lenses import Lenses
from ..model import BuildError, TimeVar, clean, number, slug

SRC = "oecd_wise"


def read(path: Path, lenses: Lenses) -> tuple[list[TimeVar], dict]:
    try:
        t = pd.read_excel(path, sheet_name="Table", engine="calamine", header=None)
    except Exception as e:  # noqa: BLE001
        raise BuildError(f"oecd_wise: cannot read {path} ({e}); check it is an OECD Data Explorer export") from e
    labels = {clean(t.iat[i, 1]): i for i in range(len(t)) if isinstance(t.iat[i, 1], str)}
    for need in ("Domain", "Measure", "Unit of measure"):
        if need not in labels:
            raise BuildError(f"oecd_wise: no {need!r} row in {path}; the export's layout changed")
    year_rows = [i for i in range(len(t)) if (y := number(t.iat[i, 1])) is not None and 1900 < y < 2100]
    out = []
    for c in range(2, t.shape[1]):
        measure = clean(t.iat[labels["Measure"], c])
        if not measure or measure == "Measure":
            continue
        values = {int(number(t.iat[i, 1])): v for i in year_rows if (v := number(t.iat[i, c])) is not None}
        if len(values) < 3:
            continue
        domain = clean(t.iat[labels["Domain"], c])
        out.append(
            TimeVar(
                id=f"oecd:{slug(measure)}",
                name=f"{measure} (OECD How's Life)",
                source=SRC,
                topic=f"Well-being: {domain}",
                lens=lenses.of(SRC),
                unit=clean(t.iat[labels["Unit of measure"], c]),
                values=values,
                description=f"OECD How's Life? current well-being, domain '{domain}'.",
            )
        )
    if not out:
        raise BuildError(f"oecd_wise: no measures with three or more years in {path}")
    return out, {"variables": len(out)}
