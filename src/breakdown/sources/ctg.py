"""The Closing the Gap Annual Data Compilation Report 2026 (data/raw/closing-the-gap/ctgNN-*.csv), one file per
socio-economic outcome.

Each file is long: a row per table, year and breakdown (Indigenous status, sex, age, remoteness, disadvantage,
disability, and up to nine description fields), with a column per state and territory and the national figure in
`Aust`. Read here: national figures of actual values only. Trajectories (the target paths), linear-regression
estimates, assessments of progress and confidence intervals are left out, as are breakdowns with fewer than
`MIN_YEARS` years.

Years. A financial year (2018-19) is placed at the year it ends, as the World Bank labels Australia's fiscal years.
A period of three to five years (2010-12, 2016-2020) is placed at its middle year, rounded down, and keeps its own
label for display. A change over a period ("2016 to 2021") and periods longer than five years are left out. A
series whose labels would put two values in one year is left out whole.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from ..lenses import Lenses
from ..model import BuildError, TimeVar, clean, number

SRC = "ctg"
MIN_YEARS = 4
LAST_YEAR = 2026
VALUE_COLS = ("Aust", "Total")
NOT_KEYS = {
    "Year",
    "Data_Source",
    "Description7",
    "Uncertainty",
    "NSW",
    "Vic",
    "Qld",
    "WA",
    "SA",
    "Tas",
    "ACT",
    "NT",
    "Aust",
    "Total",
    "Total_5juris",
    "Total_6juris",
    "Aus Gov",
}
DEFAULTS = {"All people", "Persons", "All ages", "All areas", "All", "Total"}
UNITS = {
    "no.": "number",
    "%": "%",
    "% (AS)": "%, age-standardised",
    "rate": "rate",
    "rate (AS)": "rate, age-standardised",
    "'000": "thousands",
    "years": "years",
    "$": "$",
    "ratio": "ratio",
}


def place_year(label: str) -> int | None:
    """The year a period label is placed at, or None when it is left out (see the module's docstring)."""
    s = str(label).strip()
    if re.fullmatch(r"\d{4}", s):
        y = int(s)
        return y if y <= LAST_YEAR else None
    m = re.fullmatch(r"(\d{4})-(\d{2}|\d{4})", s)
    if not m:
        return None
    start = int(m.group(1))
    end = int(m.group(2)) if len(m.group(2)) == 4 else (start // 100) * 100 + int(m.group(2))
    if end < start:
        end += 100
    span = end - start
    if span == 1:
        y = end  # a financial year
    elif 2 <= span <= 4:
        y = start + span // 2  # a period of three to five years
    else:
        return None
    return y if y <= LAST_YEAR else None


def _topic(path: Path) -> str:
    m = re.match(r"ctg(\d+)-(.+)$", path.stem)
    return f"Closing the Gap {int(m.group(1))}: {m.group(2).replace('-', ' ')}" if m else "Closing the Gap"


def _name(key: dict) -> str:
    base = key.get("Description1") or key.get("Measure") or "Measure"
    details = [
        key[c]
        for c in sorted(key)
        if c.startswith("Description") and c not in ("Description1", "Description6") and key[c]
    ]
    how = key.get("Description6")
    quals = [key.get("Indigenous_Status")]
    for c in ("Sex", "Age", "Remoteness", "SEIFA_IRSD", "Disability_Status"):
        v = key.get(c)
        if v and v not in DEFAULTS:
            quals.append(v)
    name = base + "".join(f", {d}" for d in details)
    if how:
        name += f" [{how.lower()}]"
    q = "; ".join(x for x in quals if x)
    return f"{name} ({q}) (CtG)" if q else f"{name} (CtG)"


def read(folder: Path, lenses: Lenses) -> tuple[list[TimeVar], dict]:
    files = sorted(folder.glob("ctg*.csv"))
    if len(files) != 17:
        raise BuildError(f"ctg: expected 17 files ctg01…ctg17 in {folder}, found {len(files)}")
    out, counts = [], Counter()
    for path in files:
        try:
            d = pd.read_csv(path, dtype=str, encoding="utf-8", encoding_errors="replace")
        except Exception as e:  # noqa: BLE001
            raise BuildError(f"ctg: cannot read {path} ({e})") from e
        vcol = next((c for c in VALUE_COLS if c in d.columns), None)
        if vcol is None:
            raise BuildError(f"ctg: {path} has no national column (Aust or Total)")
        keep = pd.Series(True, index=d.index)
        if "Uncertainty" in d:
            keep &= d["Uncertainty"].isna()
        if "Description7" in d:
            keep &= d["Description7"].isna() | (d["Description7"] == "Actual")
        d = d[keep]
        keys = [c for c in d.columns if c not in NOT_KEYS]
        topic = _topic(path)
        for kv, g in d.groupby(keys, dropna=False, sort=True):
            key = {k: clean(v) for k, v in zip(keys, kv, strict=True)}
            values, labels, clash = {}, {}, False
            for label, x in zip(g["Year"], g[vcol], strict=True):
                v, y = number(x), place_year(label)
                if v is None:
                    continue
                if y is None:
                    counts["values_left_out_for_their_period"] += 1
                    continue
                if y in values:
                    clash = True
                    break
                values[y] = v
                if str(label).strip() != str(y):
                    labels[y] = str(label).strip()
            if clash:
                counts["series_with_clashing_years"] += 1
                continue
            if len(values) < MIN_YEARS:
                counts["series_too_short"] += 1
                continue
            digest = hashlib.sha1(repr(sorted(key.items())).encode()).hexdigest()[:10]
            source = Counter(g["Data_Source"].dropna()).most_common(1)
            out.append(
                TimeVar(
                    id=f"ctg:{key['Table_Number']}:{digest}",
                    name=_name(key),
                    source=SRC,
                    topic=topic,
                    lens=lenses.of(SRC),
                    unit=UNITS.get(key.get("Unit") or "", key.get("Unit")),
                    values=values,
                    description=f"Closing the Gap Annual Data Compilation Report 2026, table {key['Table_Number']} "
                    f"({key.get('Measure')}). National figure, actual values."
                    + (f" Source: {source[0][0]}." if source else ""),
                    labels=labels,
                    note="Some years are period averages or financial years, placed as the data notes say."
                    if labels
                    else None,
                )
            )
            counts["series"] += 1
    return out, dict(sorted(counts.items()))
