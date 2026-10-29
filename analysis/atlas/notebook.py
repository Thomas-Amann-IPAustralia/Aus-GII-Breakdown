"""Read the Stage 1 and Stage 2 notebooks into observation records: each observation's own words, the section it sits
in, the outputs above it (text, for checking numbers) and the charts above it (PNG), so the evidence pages quote the
notebooks rather than copy them by hand.

An observation is a block of markdown that starts `**U12 (descriptive).` (Stage 1) or `**B6 (observational).` (Stage
2) and runs to the next one or the end of its cell. Its evidence is the code cells between the previous markdown cell
that holds observations and its own cell: the outputs "directly above" it, as the notebook's rules put it.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "analysis" / "notebooks" / "01_univariate.ipynb"
# Each stage's notebook and the letter its observations carry (U: univariate, B: bivariate)
NOTEBOOKS = {1: NOTEBOOK, 2: ROOT / "analysis" / "notebooks" / "02_bivariate.ipynb"}

_START = re.compile(r"^(?:#### Observation |\*\*)([UB]\d+) \((descriptive|observational|causal|projected)[;)]", re.M)
_HEADING = re.compile(r"^(#{2,5}) (.+)$", re.M)


@dataclass
class Chart:
    cell_id: str
    index: int  # the PNG's position among that cell's outputs
    png: bytes


@dataclass
class Observation:
    id: str
    strength: str
    text: str  # the observation's own markdown, as written
    cell_id: str
    cell_index: int
    section: str  # the nearest heading above it, such as "1.2 Applications over time (`filing_fy`)"
    chapter: str  # the notebook's top-level section, such as "1. Lens: IP rights (one row per right)"
    evidence_text: str = ""  # the text outputs and code comments of the cells above it
    charts: list[Chart] = field(default_factory=list)
    stage: int = 1


def _source(cell: dict) -> str:
    s = cell["source"]
    return "".join(s) if isinstance(s, list) else s


def _text_outputs(cell: dict) -> str:
    out = []
    for o in cell.get("outputs", []):
        if "text" in o:
            out.append("".join(o["text"]))
        for mime in ("text/plain", "text/html"):
            if mime in o.get("data", {}):
                out.append("".join(o["data"][mime]))
    return "\n".join(out)


def read_all() -> list[Observation]:
    """Every observation of every stage: Stage 1's in notebook order, then Stage 2's."""
    return [o for stage, path in NOTEBOOKS.items() for o in read(path, stage)]


def read(path: Path = NOTEBOOK, stage: int = 1) -> list[Observation]:
    """Every observation in the notebook, in order."""
    cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
    found: list[Observation] = []
    chapter = section = ""
    pending_text: list[str] = []
    pending_charts: list[Chart] = []
    for i, cell in enumerate(cells):
        src = _source(cell)
        if cell["cell_type"] == "code":
            comments = "\n".join(line for line in src.splitlines() if line.strip().startswith("#"))
            pending_text += [comments, _text_outputs(cell)]
            for k, o in enumerate(cell.get("outputs", [])):
                png = o.get("data", {}).get("image/png")
                if png:
                    pending_charts.append(Chart(cell["id"], k, base64.b64decode("".join(png))))
            continue
        starts = list(_START.finditer(src))
        headings = list(_HEADING.finditer(src))

        def heading_to(pos: int, headings: list = headings) -> None:
            nonlocal chapter, section
            while headings and headings[0].start() < pos:
                h = headings.pop(0)
                level, title = len(h.group(1)), h.group(2).strip()
                if level == 2:
                    chapter, section = title, title
                elif not title.startswith(("Observation", "Repairs", "How the link")):
                    section = title

        for n, m in enumerate(starts):
            heading_to(m.start())
            # An observation ends at the next observation or the next heading, whichever comes first
            ends = [x.start() for x in starts[n + 1 : n + 2]] + [h.start() for h in headings if h.start() > m.start()]
            end = min(ends, default=len(src))
            found.append(
                Observation(
                    id=m.group(1),
                    strength=m.group(2),
                    text=src[m.start() : end].strip(),
                    cell_id=cell["id"],
                    cell_index=i,
                    section=section,
                    chapter=chapter,
                    evidence_text="\n".join(pending_text),
                    charts=list(pending_charts),
                    stage=stage,
                )
            )
        heading_to(len(src))
        if starts:
            pending_text, pending_charts = [], []
    return found
