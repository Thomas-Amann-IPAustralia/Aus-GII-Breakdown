"""What would a re-run move? Bind each number an observation quotes to its place in the outputs above it, run the
notebooks again in a copy, and report which numbers moved (ADR 0059; `docs/plan-refresh-check.md`, steps 2 to 4).

    uv run python -m atlas.refresh bind             # how many quoted numbers can be traced, and how (no run needed)
    uv run python -m atlas.refresh run [1 2 3]      # run the notebooks in a copy (never in place); needs the lenses
    uv run python -m atlas.refresh report           # compare the copy with the reviewed notebooks; write the report
    uv run python -m atlas.refresh confirm          # clear the currency check's wait where nothing moved

**Nothing here changes a notebook or the atlas.** The reviewed notebooks are read; the copies are written to
`analysis/atlas/refresh_runs/` (gitignored), with the kernel working in `analysis/notebooks/` as it would in place.

**A place** is where a number sits in a code cell's output, named so that it can be found again after a re-run even
if rows are added or reordered:
- in a table, the cell's notebook id, the table, the row's label and the column's label (labels, not positions);
- in printed text, the cell's id and the line with its numbers masked ("rows: # columns: #"), and which number.

**A binding** ties a number in an observation's own words to its places:
- `exact`: the number is at that place as written;
- `rounded`: the place holds a longer value that rounds to it, or a share it gives as a percentage;
- `from <id>`: it is not in the outputs above, but is bound on the page of an observation this one names;
- `untraced`: none of these (worked out by arithmetic, read off a chart, or from the text of a law).
Years and one-digit numbers are not bound: they are labels and small counts, at home anywhere. A two-digit number
is bound only where exactly one place in the outputs above holds it.

**The report** says, for each observation, whether every bound number is where it was (`same`), which moved (old and
new), and which places are gone (a row or column that no longer exists, or a cell that failed).
"""

from __future__ import annotations

import copy
import datetime as dt
import html
import json
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from . import build, notebook

ROOT = Path(__file__).resolve().parents[2]
RUNS = Path(__file__).resolve().parent / "refresh_runs"
REPORT = ROOT / "docs" / "refresh-report.md"
_YEAR = re.compile(r"^(?:19|20)\d\d$")
_NUM = build._NUMBER
_CITED = re.compile(r"\b([UBM]\d+)\b")
_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def norm(n: str) -> str:
    """A number as the numbers rule writes it: no thousands commas, no trailing zeros after a decimal point."""
    n = n.rstrip(",").replace(",", "")
    return n.rstrip("0").rstrip(".") if "." in n else n


def substantive(n: str) -> bool:
    """Not a year, a one- or two-digit count, or a document's number written with leading zeros ("0016")."""
    return not _YEAR.match(n) and not ("." not in n and len(n.lstrip("-")) <= 2) and not re.match(r"^0\d", n)


def small(n: str) -> bool:
    """A two-digit count ("89 columns"): bound only where exactly one place holds it, since it could be anywhere."""
    return bool(re.fullmatch(r"[1-9]\d", n))


# ------------------------------------------------------------------------------------------------------- places
class _Tables(HTMLParser):
    """The tables in a piece of HTML: header rows and body rows of (tag, text, rowspan, colspan)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables: list[dict] = []
        self._part = self._row = self._cell = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self.tables.append({"head": [], "body": []})
        elif tag in ("thead", "tbody") and self.tables:
            self._part = "head" if tag == "thead" else "body"
        elif tag == "tr" and self.tables:
            self._row = []
        elif tag in ("th", "td") and self._row is not None:
            self._cell = [tag, "", int(a.get("rowspan") or 1), int(a.get("colspan") or 1)]

    def handle_data(self, data):
        if self._cell is not None:
            self._cell[1] += data

    def handle_endtag(self, tag):
        if tag in ("th", "td") and self._cell is not None:
            self._cell[1] = " ".join(self._cell[1].split())
            self._row.append(tuple(self._cell))
            self._cell = None
        elif tag == "tr" and self._row is not None and self.tables:
            self.tables[-1][self._part or "body"].append(self._row)
            self._row = None
        elif tag in ("thead", "tbody"):
            self._part = None


def _is_number(text: str) -> bool:
    return bool(re.fullmatch(r"-?[\d,]*\.?\d+%?", text.strip()))


def _table_cells(t: dict):
    """Each value cell of a table as (row label, column label, text)."""
    width = max((sum(c[3] for c in r) for r in t["head"] + t["body"]), default=0)
    cols = [[] for _ in range(width)]
    for r in t["head"]:
        j = 0
        for _, text, _, span in r:
            for k in range(span):
                if text and j + k < width:
                    cols[j + k].append(text)
            j += span
    labels = [" / ".join(dict.fromkeys(c)) for c in cols]  # a header repeated down the rows is said once
    carry: dict[int, tuple[str, int]] = {}  # index level -> (label, rows left), for a label spanning rows
    for n, r in enumerate(t["body"]):
        row, j, lead = [], 0, 0
        cells = list(r)
        while j in carry:  # labels carried down from a spanning cell above
            text, left = carry[j]
            row.append(text)
            carry[j] = (text, left - 1)
            if left - 1 <= 0:
                del carry[j]
            j += 1
            lead += 1
        values = []
        for tag, text, rowspan, span in cells:
            if tag == "th":
                row.append(text)
                if rowspan > 1:
                    carry[j] = (text, rowspan - 1)
                lead += 1
            else:
                values.append((j, text))
            j += span
        named = [x for x in row if x and not _is_number(x)]
        if not named:  # a plain numbered index: the row is known by its words, or failing that its position
            named = [text for _, text in values if text and not _is_number(text) and text != "NaN"][:2] or [f"row {n}"]
        label = " / ".join(named)
        for j, text in values:
            yield label, labels[j] if j < len(labels) and labels[j] else f"column {j}", text


def places(cell: dict) -> dict[str, str]:
    """Every place in a code cell's outputs: its key and the text there. Keys survive added and reordered rows."""
    out: dict[str, str] = {}
    seen: Counter = Counter()

    def put(key: str, text: str) -> None:
        seen[key] += 1
        out[key if seen[key] == 1 else f"{key} #{seen[key]}"] = text

    cid = cell.get("id", "?")
    tables = 0
    for o in cell.get("outputs", []):
        data = o.get("data", {})
        if "text/html" in data:
            p = _Tables()
            p.feed("".join(data["text/html"]))
            for t in p.tables:
                tables += 1
                for row, col, text in _table_cells(t):
                    if _NUM.search(text):
                        put(f"{cid} | table {tables} | {row} | {col}", text)
        elif "text" in o or "text/plain" in data:
            text = _ANSI.sub("", "".join(o.get("text") or data.get("text/plain")))
            for line in text.splitlines():
                if _NUM.search(line):
                    put(f"{cid} | line | {' '.join(_NUM.sub('#', line).split())[:160]}", line)
        elif o.get("output_type") == "error":
            put(f"{cid} | error", f"{o.get('ename')}: {html.unescape(str(o.get('evalue')))[:200]}")
    return out


def numbers_at(text: str) -> list[str]:
    return [norm(n) for n in _NUM.findall(text)]


# ----------------------------------------------------------------------------------------------------- bindings
@dataclass
class Evidence:
    """An observation with the code cells above it (those between the observation before it and its own cell)."""

    obs: notebook.Observation
    cells: list[dict]


def evidence(stage: int, cells: list[dict] | None = None) -> list[Evidence]:
    path = notebook.NOTEBOOKS[stage]
    cells = cells if cells is not None else json.loads(path.read_text(encoding="utf-8"))["cells"]
    obs = notebook.read(path, stage)
    marks = sorted({o.cell_index for o in obs})
    out = []
    for o in obs:
        prev = max((i for i in marks if i < o.cell_index), default=-1)
        out.append(Evidence(o, [c for c in cells[prev + 1 : o.cell_index] if c["cell_type"] == "code"]))
    return out


_NOTE = re.compile(r"\b(?:Corrected|Restated|Amended|Scoped|Reworded|Revised|Updated|Decision)\b[^.\n]{0,60}?\(")
_SECTION = re.compile(r"\((?:section |sections? )?\d+(?:\.\d+)+(?:[,;] ?\d+(?:\.\d+)+)*\)|\bsections? \d+(?:\.\d+)*")


def _spoken(text: str) -> tuple[set[str], set[str]]:
    """The numbers an observation states now, and those it only quotes from its past or uses as a section's number.

    A dated note ("- **Corrected (10 November 2026; ADR 0057):** this said 79 ...") quotes what the observation used
    to say; those values are history, not claims, and will never be in a current output."""
    blocks = re.split(r"\n(?=- |\*Amended|\*Corrected|\n)", text)
    now, past = set(), set()
    for b in blocks:
        nums = build.numbers(_SECTION.sub(" ", b))
        (past if _NOTE.search(b[:160]) else now).update(nums)
    refs = build.numbers(text) - build.numbers(_SECTION.sub(" ", text))
    return now, (past | refs) - now


def _fits(quoted: str, value: str) -> str | None:
    """How a quoted number can come from the value at a place: as written, rounded, or a share as a percentage."""
    if quoted == value:
        return "exact"
    try:
        x, v = float(quoted), float(value)
    except ValueError:
        return None
    d = len(quoted.split(".")[1]) if "." in quoted else 0
    if len(value.split(".")[1] if "." in value else "") > d and abs(round(v, d) - x) < 1e-9:
        return "rounded"
    if abs(v) <= 1 and abs(round(v * 100, d) - x) < 1e-9:
        return "percent"
    for scale, name in ((1e6, "millions"), (1e9, "billions"), (1e3, "thousands")):  # $214.6m for 214,600,000
        if abs(v) >= scale * 10 and d <= 2 and abs(round(v / scale, d) - x) < 1e-9 and "." in quoted:
            return name
    return None


def _form(how: str, quoted: str, value: str) -> str:
    """The value at a place, written the way the observation quotes it."""
    if how == "exact":
        return value
    d = len(quoted.split(".")[1]) if "." in quoted else 0
    v = float(value) * {"percent": 100, "millions": 1e-6, "billions": 1e-9, "thousands": 1e-3}.get(how, 1)
    return norm(f"{v:.{d}f}") if d else str(int(round(v)))


def bind(ev: Evidence) -> dict[str, dict]:
    """Each substantive number in the observation's own words, with how it is bound and where (its own cells only)."""
    at: dict[str, list[tuple[str, int]]] = defaultdict(list)  # value -> (place, which number there)
    for c in ev.cells:
        for key, text in places(c).items():
            for i, v in enumerate(numbers_at(text)):
                at[v].append((key, i))
    out = {}
    quoted, past = _spoken(ev.obs.text)
    for n in sorted(x for x in quoted if small(x) and len(at.get(x, [])) == 1):
        out[n] = {"how": "exact", "at": at[n], "small": True}
    for n in sorted(x for x in quoted | past if substantive(x)):
        if n in at:
            out[n] = {"how": "exact", "at": at[n]}
            continue
        loose = [(how, p) for v, ps in at.items() if (how := _fits(n, v)) for p in ps]
        if loose:
            how = next(
                h for h in ("rounded", "percent", "millions", "billions", "thousands") if any(x == h for x, _ in loose)
            )
            out[n] = {"how": how, "at": [p for h, p in loose if h == how]}
        elif n in past:  # what it used to say, or a section's number: not a claim to trace
            out[n] = {"how": "history", "at": []}
        else:
            out[n] = {"how": "untraced", "at": []}
    return out


def bind_all(stages=(1, 2, 3)) -> dict[str, dict]:
    """Every observation's bindings; a number not in its own outputs is looked for on the pages it names."""
    evs = {e.obs.id: e for s in stages for e in evidence(s)}
    own = {i: bind(e) for i, e in evs.items()}
    direct = ("exact", "rounded", "percent", "millions", "billions", "thousands")
    home: dict[str, list[str]] = defaultdict(list)  # a number of four or more digits -> the observations that hold it
    for i, b in own.items():
        for n, x in b.items():
            if x["how"] == "exact" and len(n.replace(".", "").lstrip("-")) >= 4:
                home[n].append(i)
    for i, b in own.items():
        cited = [c for c in dict.fromkeys(_CITED.findall(evs[i].obs.text)) if c != i and c in own]
        for n, x in b.items():
            if x["how"] != "untraced":
                continue
            for c in cited:
                theirs = own[c].get(n)
                if theirs and theirs["how"] in direct:
                    x.update(how=f"from {c}", at=theirs["at"], via=theirs["how"])
                    break
            else:  # not named nearby: a long number that exactly one other observation holds is that one's
                if len(home.get(n, [])) == 1:
                    c = home[n][0]
                    x.update(how=f"from {c}", at=own[c][n]["at"], via="exact")
    return own


# -------------------------------------------------------------------------------------------------------- the run
def run(stages=(1, 2, 3)) -> None:
    """Run each notebook in a copy, the kernel working where the notebook lives. The reviewed file is only read."""
    import nbformat
    from nbclient import NotebookClient

    RUNS.mkdir(exist_ok=True)
    for s in stages:
        src = notebook.NOTEBOOKS[s]
        nb = nbformat.read(src, as_version=4)
        t0 = time.time()
        client = NotebookClient(
            nb,
            timeout=None,
            kernel_name="python3",
            allow_errors=True,
            resources={"metadata": {"path": str(src.parent)}},
        )
        client.execute()
        nbformat.write(nb, RUNS / src.name)
        failed = sum(1 for c in nb.cells if any(o.get("output_type") == "error" for o in c.get("outputs", [])))
        meta = {
            "notebook": src.name,
            "ran": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "failed_cells": failed,
        }
        meta["seconds"] = round(time.time() - t0)
        (RUNS / f"{src.stem}.json").write_text(json.dumps(meta, indent=1))
        print(f"{src.name}: {meta['seconds']} s, {failed} failed cells")


# ----------------------------------------------------------------------------------------------------- the report
def compare(stages=(1, 2, 3)) -> dict:
    """Each observation's bound numbers, read again at the same places in the copies."""
    binds = bind_all()
    result: dict[str, dict] = {}
    runs = {}
    for s in stages:
        ran = RUNS / notebook.NOTEBOOKS[s].name
        if not ran.exists():
            continue
        runs[s] = json.loads((RUNS / f"{ran.stem}.json").read_text())
        new_cells = json.loads(ran.read_text(encoding="utf-8"))["cells"]
        new = {}
        for c in new_cells:
            if c["cell_type"] == "code":
                new.update(places(c))
        errors = {c.get("id") for c in new_cells if any(o.get("output_type") == "error" for o in c.get("outputs", []))}
        for e in evidence(s):
            b = binds[e.obs.id]
            r = {"same": 0, "moved": [], "gone": [], "untraced": [], "failed_cells": []}
            r["failed_cells"] = [c.get("id") for c in e.cells if c.get("id") in errors]
            old = {}
            for c in e.cells:
                old.update(places(c))
            for n, x in b.items():
                how = x.get("via") or x["how"]
                if x["how"] == "history":
                    continue
                if x["how"] == "untraced":
                    r["untraced"].append(n)
                    continue
                if x["how"].startswith("from "):  # read on the cited observation's page, which reports it there
                    r.setdefault("elsewhere", []).append({"number": n, "from": x["how"][5:]})
                    continue
                now, lost = set(), []
                for key, i in x["at"]:
                    text = new.get(key)
                    vals = numbers_at(text) if text is not None else []
                    if text is None or i >= len(vals):
                        lost.append(key)
                    else:
                        now.add(_form(how, n, vals[i]))
                if lost and not now:
                    r["gone"].append({"number": n, "places": len(lost), "where": lost[0]})
                elif now == {n} and not lost:
                    r["same"] += 1
                elif n in now and (len(now) > 1 or lost):  # still there at some places, not at others
                    r["moved"].append({"number": n, "now": sorted(now - {n}), "where": x["at"][0][0], "partly": True})
                else:
                    r["moved"].append({"number": n, "now": sorted(now), "where": x["at"][0][0]})
            said = build.numbers(e.obs.text)
            for m in r[
                "moved"
            ]:  # the prose was put right ahead of its output (a dated correction quotes the old value)
                m["already"] = bool(m["now"]) and all(v in said for v in m["now"])
            r["ahead"] = [m for m in r["moved"] if m["already"]]
            r["moved"] = [m for m in r["moved"] if not m["already"]]
            r["bound"] = r["same"] + len(r["moved"]) + len(r["gone"]) + len(r["ahead"])
            r["status"] = (
                "a cell failed"
                if r["failed_cells"]
                else "places gone"
                if r["gone"] and not r["moved"]
                else "moved"
                if r["moved"] or r["gone"]
                else "prose ahead of its output"
                if r["ahead"]
                else "same"
            )
            result[e.obs.id] = r
    return {"runs": runs, "observations": result}


def summary(binds: dict[str, dict]) -> Counter:
    c: Counter = Counter()
    for b in binds.values():
        for x in b.values():
            how = x["how"]
            if how == "exact":
                how = "exact, one place" if len(x["at"]) == 1 else "exact, several places"
            if how in ("millions", "billions", "thousands"):
                how = "scaled (thousands, millions)"
            if how == "history":
                how = "history (a dated note's old value, or a section's number): not traced by design"
            c["from another observation" if how.startswith("from ") else how] += 1
    return c


def write_report(res: dict) -> str:
    """The report in plain English: what a re-run moved, observation by observation."""
    from . import currency

    ents = currency.entries()
    obs = res["observations"]
    by = Counter(r["status"] for r in obs.values())
    n_bound = sum(r["bound"] for r in obs.values())
    n_same = sum(r["same"] for r in obs.values())
    n_moved = sum(len(r["moved"]) for r in obs.values())
    n_gone = sum(len(r["gone"]) for r in obs.values())
    lines = [
        "# Refresh report: what a re-run of the notebooks would move",
        "",
        f"Written by `python -m atlas.refresh report` on {dt.date.today().isoformat()} (ADR 0059). The three notebooks"
        " were run again **in a copy**; the reviewed notebooks and the atlas are unchanged. Each number an observation"
        " quotes was read again at the place it came from.",
        "",
        "## In brief",
        "",
        f"- **{len(obs)} observations compared.** {by.get('same', 0)} have every traced number where it was;"
        f" {by.get('moved', 0)} have at least one that moved; {by.get('places gone', 0)} have a place that no longer"
        f" exists; {by.get('a cell failed', 0)} sit under a cell that failed in the copy;"
        f" {by.get('prose ahead of its output', 0)} have prose already corrected to the new value, with a stored"
        " output that was never run again.",
        f"- **{n_bound:,} numbers traced to a place:** {n_same:,} the same, {n_moved:,} moved, {n_gone:,} with their"
        " place gone.",
        "- **Runs:** "
        + "; ".join(
            f"{m['notebook']} in {m['seconds'] // 60} min {m['seconds'] % 60} s ({m['failed_cells']} cells failed)"
            for m in res["runs"].values()
        )
        + ".",
        "",
    ]
    for status, title, note in [
        (
            "a cell failed",
            "Under a cell that failed in the copy",
            "The cell above raised an error, so nothing below it can be read. Fix the run before reading these.",
        ),
        ("moved", "Numbers that moved", "Old value, then what the same place holds now."),
        (
            "places gone",
            "Places that no longer exist",
            "The row, column or line the number came from is not in the new output.",
        ),
        (
            "prose ahead of its output",
            "Prose already corrected, output not yet run again",
            "A dated correction put the words right and quotes the old value; the re-run agrees with the words.",
        ),
    ]:
        rows = [(i, r) for i, r in obs.items() if r["status"] == status]
        if not rows:
            continue
        lines += [f"## {title} ({len(rows)} observations)", "", note, ""]
        for i, r in rows:
            lines.append(f"### {i}: {ents.get(i, {}).get('headline', '')}")
            lines.append("")
            lines.append(f"{r['same']} of {r['bound']} traced numbers are the same.")
            lines.append("")
            for m in r["moved"] + r["ahead"]:
                where = " | ".join(m["where"].split(" | ")[1:])
                part = " at some of its places" if m.get("partly") else ""
                lines.append(f"- **{m['number']}** is now **{', '.join(m['now'])}**{part} ({where})")
            for g in r["gone"]:
                lines.append(f"- **{g['number']}**: place gone ({' | '.join(g['where'].split(' | ')[1:])})")
            if r["failed_cells"]:
                lines.append(f"- cells that failed: {', '.join(r['failed_cells'])}")
            lines.append("")
    same = [i for i, r in obs.items() if r["status"] == "same"]
    lines += [f"## Nothing moved ({len(same)} observations)", "", ", ".join(same) or "None.", ""]
    untraced = sum(len(r["untraced"]) for r in obs.values())
    elsewhere = sum(len(r.get("elsewhere", [])) for r in obs.values())
    lines += [
        "## What this report cannot see",
        "",
        f"- **{untraced:,} quoted numbers are not traced** to a place (worked out by arithmetic, read off a chart, or"
        " from outside the outputs). A re-run could move them unseen.",
        f"- **{elsewhere:,} are read on another observation's page**, and are reported there.",
        "- **Charts** are not compared: a number that exists only in a drawing is not traced.",
        "- Years and one-digit numbers are not traced; a two-digit number only where exactly one place holds it.",
        "",
    ]
    text = "\n".join(lines)
    REPORT.write_text(text, encoding="utf-8")
    return text


def confirm() -> None:
    """Clear the currency check's wait for the observations a re-run left as they were, with what was compared.

    When a source or a lens table changes, the currency check waits on every observation that rests on it (ADR 0058).
    For those whose traced numbers all came out the same in the copy, this records that as the reason. The others are
    listed: their numbers moved, so their cells are re-run and their words amended by hand."""
    from . import currency

    res = json.loads((RUNS / "report.json").read_text())
    when = max(m["ran"] for m in res["runs"].values())[:10]
    done, left = [], []
    for oid, r in res["observations"].items():
        rv = currency.review(oid) or {}
        d = rv.get("data") or {}
        if not d or (d.get("confirmed") or {}).get("how"):
            continue
        if r["status"] in ("same", "prose ahead of its output") and r["bound"]:
            how = f"re-run in a copy on {when}: all {r['bound']} traced numbers as quoted"
            how += f"; {len(r['untraced'])} quoted numbers not traced" if r["untraced"] else ""
            currency.confirm([oid], how)
            done.append(oid)
        else:
            left.append(f"{oid} ({r['status']})")
    print(f"{len(done)} confirmed from the re-run; {len(left)} left for a person: {', '.join(left) or 'none'}")


def main(argv: list[str]) -> None:
    cmd, rest = (argv[0], argv[1:]) if argv else ("bind", [])
    stages = tuple(int(x) for x in rest) or (1, 2, 3)
    if cmd == "bind":
        binds = bind_all()
        c = summary(binds)
        total = sum(c.values())
        print(f"{total:,} substantive numbers quoted by {len(binds)} observations:")
        for k, v in c.most_common():
            print(f"  {k}: {v:,} ({100 * v / total:.1f}%)")
    elif cmd == "run":
        run(stages)
    elif cmd == "report":
        res = compare(stages)
        (RUNS / "report.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
        write_report(copy.deepcopy(res))
        by = Counter(r["status"] for r in res["observations"].values())
        print(f"{REPORT.relative_to(ROOT)}: {dict(by)}")
    elif cmd == "confirm":
        confirm()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
