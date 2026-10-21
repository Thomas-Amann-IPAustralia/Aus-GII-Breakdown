"""The two shapes every source is read into, and the helpers that keep the outputs deterministic.

A time variable is one Australian series by year; an economy variable is one value per economy (a snapshot). Ids are
`<source>:<code>` and stay stable while the source's codes do, so links into the explorer keep working.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path


class BuildError(Exception):
    """A stage could not do its job. The message is one line naming the source and what to check."""


@dataclass
class TimeVar:
    id: str
    name: str
    source: str
    topic: str
    lens: str
    unit: str | None
    values: dict[int, float]  # year -> value
    description: str | None = None
    parts_of: list[str] = field(default_factory=list)  # ids of composites built from this variable
    kind: str = "value"  # value, index, rank
    labels: dict[int, str] = field(default_factory=dict)  # year -> the source's own period label, where it differs
    note: str | None = None


@dataclass
class EconVar:
    id: str
    name: str
    source: str
    topic: str
    lens: str
    unit: str | None
    year: str | None  # the data year, or the most common one when economies differ
    values: dict[str, float]  # ISO3 -> value
    description: str | None = None
    parts_of: list[str] = field(default_factory=list)
    kind: str = "value"
    years: dict[str, int] = field(default_factory=dict)  # ISO3 -> its own data year, where economies differ
    note: str | None = None


def number(x) -> float | None:
    """A finite float, or None for blanks, '..', 'n.a.' and the like."""
    if x is None:
        return None
    if isinstance(x, bool):
        return None
    if isinstance(x, int | float):
        v = float(x)
    else:
        s = str(x).strip().replace(",", "")
        if not s or not re.fullmatch(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?", s):
            return None
        v = float(s)
    return v if math.isfinite(v) else None


def sig(v: float, digits: int = 6) -> float | int:
    """Rounded to six significant figures (the sources carry no more), as an int when whole."""
    r = float(f"{v:.{digits}g}")
    return int(r) if r.is_integer() and abs(r) < 1e15 else r


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def clean(s) -> str | None:
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return None
    t = re.sub(r"\s+", " ", str(s).replace("\\'", "'")).strip()  # WIPO's text escapes some apostrophes
    return t or None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(obj) -> str:
    """Canonical JSON: sorted keys, no spaces, UTF-8. The same inputs always give the same bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
