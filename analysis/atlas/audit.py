"""The review of Stage 1 against IP Australia's published evidence, for the atlas's own page (ADR 0024, 0025).

Three inputs meet here, and none of them is the notebook or an observation's content, which this page leaves as they
are (the owner's instruction, ADR 0025):
- the audit's record, `docs/audit-ip-australia.md`: each observation's verdict is read from its tables, so the page
  cannot drift from the record;
- the benchmark's outputs, `analysis/audit/output/`: the published figures beside the lens's, for the charts and the
  table of measures;
- the plain-English layer, `analysis/atlas/content/audit.yaml`.

The numbers rule holds here as on the observation pages: every number in the plain English must appear in the record
or in the benchmark's outputs, or the page is not built.
"""

from __future__ import annotations

import csv
import json
import re

import yaml

from . import build

RECORD = build.ROOT / "docs" / "audit-ip-australia.md"
OUTPUT = build.ROOT / "analysis" / "audit" / "output"
CONTENT = build.CONTENT / "audit.yaml"
CATEGORIES = ["corroborated", "consistent", "qualified", "disputed", "contradicted", "not testable"]
SHOWN = {  # the verdicts as the chart and the page name them, in order
    "corroborated": "Corroborated",
    "consistent": "Consistent",
    "disputed": "Disputed in part",
    "contradicted": "Contradicted",
    "not testable": "Not testable",
}
CHART_IDS = ["audit-verdicts", "audit-closeness", "audit-d1", "audit-d2"]
SOURCE = (
    "IP Australia, Australian IP Reports 2015 to 2026 (published figures); IP RAPID (lens: rights); audit benchmark"
)
# fields of the plain-English layer that hold identifiers, not prose (their numbers are not checked)
_IDS = {"measures", "figures", "affects", "chart", "id", "as_at"}

_ROW = re.compile(r"^\| (U\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$")
_GROUP = re.compile(r"^\| ([^|]+) \| ((?:U\d+, )*U\d+) \|$")


def _csv(name: str) -> list[dict]:
    with (OUTPUT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def category(label: str) -> str | None:
    """A verdict's category from the record's label ("Corroborated; designs qualified" is corroborated)."""
    low = label.lower()
    return next((c for c in CATEGORIES if low.startswith(c)), None)


def verdicts(record: str) -> tuple[list[dict], list[dict]]:
    """The record's verdicts: the observations it could test (section 5.1), and the groups it could not (5.2)."""
    tested, untested, part = [], [], None
    for line in record.splitlines():
        if line.startswith("### 5.1"):
            part = "tested"
        elif line.startswith("### 5.2"):
            part = "untested"
        elif line.startswith("## ") and part:
            break
        elif part == "tested" and (m := _ROW.match(line)):
            oid, label, evidence, follows = (g.strip() for g in m.groups())
            tested.append(
                {"id": oid, "label": label, "category": category(label), "evidence": evidence, "follows": follows}
            )
        elif part == "untested" and (m := _GROUP.match(line)):
            why, ids = m.groups()
            untested.append({"why": why.strip(), "ids": ids.split(", ")})
    return tested, untested


def page_numbers(record: str) -> set[str]:
    """Every number in the record and in the benchmark's outputs: what the plain English may quote."""
    out = build.numbers(record)
    for f in sorted(OUTPUT.glob("*.csv")):
        out |= build.numbers(f.read_text(encoding="utf-8"))
    return out


def _prose(x, key: str = "") -> list[str]:
    """The prose strings of the plain-English layer, without its identifier fields."""
    if key in _IDS:
        return []
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [s for k, v in x.items() for s in _prose(v, k)]
    if isinstance(x, list):
        return [s for v in x for s in _prose(v, key)]
    return []


def measures(content: dict, bench: list[dict]) -> tuple[list[dict], list[str]]:
    """The table of measures: each row's figures, how many agree, and the largest gap."""
    problems, rows, seen = [], [], set()
    by_measure: dict[str, list[dict]] = {}
    for r in bench:
        by_measure.setdefault(r["measure"], []).append(r)
    for g in content["measures"]:
        rs = [r for m in g["measures"] for r in by_measure.get(m, [])]
        for m in g["measures"]:
            if m not in by_measure:
                problems.append(f"audit: measure '{m}' is not in the benchmark")
            seen.add(m)
        counts = [r for r in rs if r["ratio"]]
        shares = [r for r in rs if not r["ratio"]]
        gap_pct = max((abs(float(r["ratio"]) - 1) * 100 for r in counts), default=None)
        gap_pts = max((abs(float(r["difference"])) for r in shares), default=None)
        years = sorted({int(r["year"]) for r in rs})
        rows.append(
            {
                "label": g["label"],
                "figures": len(rs),
                "agree": sum(r["agrees"] == "True" for r in rs),
                "years": f"{years[0]} to {years[-1]}" if len(years) > 1 else str(years[0]),
                "gap_pct": round(gap_pct, 2) if gap_pct is not None else None,
                "gap_pts": round(gap_pts, 2) if gap_pts is not None else None,
            }
        )
    for m in sorted(set(by_measure) - seen):
        problems.append(f"audit: benchmark measure '{m}' has no row in audit.yaml's measures")
    return rows, problems


def charts(content: dict, tested: list[dict], untested: list[dict], bench: list[dict], context: list[dict]) -> dict:
    """The page's four charts, from the record's verdicts and the benchmark's outputs."""
    counts = {c: sum(v["category"] == c for v in tested) for c in SHOWN}
    counts["not testable"] = sum(len(g["ids"]) for g in untested)
    verdict_chart = {
        "id": "audit-verdicts",
        "type": "bar",
        "horizontal": True,
        "title": "How the 99 observations stand against IP Australia's evidence",
        "subtitle": "Observations by verdict",
        "x": {"type": "category", "values": list(SHOWN.values())},
        "y": {"name": "Observations", "min": 0},
        "series": [{"name": "Observations", "data": [counts[c] for c in SHOWN]}],
        "source": "The audit's record (docs/audit-ip-australia.md)",
        "origin": "record",
    }

    discrepancy = {tuple(f.rsplit(" ", 1)) for d in content["findings"] for f in d["figures"]}
    label = {m: g["label"] for g in content["measures"] for m in g["measures"]}
    groups = {"agrees": [], "definition": [], "discrepancy": []}
    for r in bench:
        if not r["ratio"]:  # shares and times are not counts
            continue
        key = (
            "agrees"
            if r["agrees"] == "True"
            else "discrepancy"
            if (r["measure"], r["year"]) in discrepancy
            else "definition"
        )
        groups[key].append([float(r["published"]), float(r["lens"]), f"{label[r['measure']]}, {r['year']}"])
    top = max(p[0] for g in groups.values() for p in g) * 1.3
    closeness = {
        "id": "audit-closeness",
        "type": "scatter",
        "title": "IP Australia's published counts against the same counts from Stage 1's data",
        "subtitle": "One dot per published figure; on the line, the two are equal",
        "x": {"type": "log", "name": "IP Australia's published figure"},
        "y": {"type": "log", "name": "The same figure from Stage 1's data"},
        "series": [
            {"name": "Agrees within the tolerance", "colour": 0, "data": groups["agrees"]},
            {"name": "Differs: counted another way", "colour": 3, "data": groups["definition"]},
            {"name": "Differs: one of the four discrepancies", "colour": 1, "data": groups["discrepancy"], "size": 9},
            {"name": "Where the two are equal", "kind": "line", "colour": "muted", "data": [[2, 2], [top, top]]},
        ],
        "source": SOURCE,
    }

    b = {(r["measure"], r["year"]): r for r in bench}
    c = {(r["figure"], r["year"]): r for r in context}
    years = ["2014", "2021", "2023", "2025"]
    d1 = {
        "id": "audit-d1",
        "type": "bar",
        "title": "Australians' design applications: IP Australia's count and Stage 1's",
        "subtitle": "Design applications a year; the gap is close to the designs IP RAPID gives no country",
        "x": {"type": "category", "values": years},
        "y": {"name": "Design applications", "min": 0},
        "series": [
            {
                "name": "IP Australia: Australian applicants",
                "colour": 0,
                "data": [float(b[("des_apps_res", y)]["published"]) for y in years],
            },
            {
                "name": "Stage 1's data: an Australian filer",
                "colour": 2,
                "data": [float(b[("des_apps_res", y)]["lens"]) for y in years],
            },
            {
                "name": "Stage 1's data: no country recorded",
                "colour": "muted",
                "data": [float(c[("des_apps_origin_unknown", y)]["value"]) for y in years],
            },
        ],
        "source": SOURCE,
    }
    tm = sorted((r for r in bench if r["measure"] == "tm_apps"), key=lambda r: r["year"])
    d2 = {
        "id": "audit-d2",
        "type": "bar",
        "title": "Trade mark applications: Stage 1's count as a share of IP Australia's",
        "subtitle": "Stage 1's count divided by IP Australia's published count, by year of filing",
        "x": {"type": "category", "values": [r["year"] for r in tm]},
        "y": {"name": "Ratio", "min": 0.95, "max": 1.01, "format": "ratio", "digits": 4},
        "series": [{"name": "Ratio", "data": [float(r["ratio"]) for r in tm]}],
        "marks": {"y": [{"at": 1, "label": "Equal"}]},
        "labels": False,
        "source": SOURCE,
    }
    return {s["id"]: s for s in (verdict_chart, closeness, d1, d2)}


def page(write: bool = True) -> tuple[dict, list[str]]:
    """The audit page's data, with the problems found; with write=True, its charts are written too."""
    record = RECORD.read_text(encoding="utf-8")
    content = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))
    bench, context = _csv("benchmark.csv"), _csv("context.csv")
    tested, untested = verdicts(record)
    problems = []

    ids = [v["id"] for v in tested] + [i for g in untested for i in g["ids"]]
    if len(ids) != len(set(ids)):
        problems.append("audit: an observation has two verdicts in the record")
    for v in tested:
        if v["category"] is None:
            problems.append(f"audit: {v['id']}'s verdict '{v['label']}' is not one of {CATEGORIES}")
        note = content["notes"].get(v["id"])
        if not note:
            problems.append(f"audit: {v['id']} has a verdict in the record but no plain-English note")
        v["note"] = note
    for oid in sorted(set(content["notes"]) - {v["id"] for v in tested}):
        problems.append(f"audit: {oid} has a note but no verdict in the record's section 5.1")

    allowed = page_numbers(record)
    missing = set()
    for s in _prose(content):
        missing |= build.numbers(s) - allowed
    if missing:
        problems.append(f"audit: numbers not in the record or the benchmark: {', '.join(sorted(missing))}")

    table, more = measures(content, bench)
    problems += more
    specs = charts(content, tested, untested, bench, context)
    if write:
        build.CHARTS.mkdir(parents=True, exist_ok=True)
        for cid, spec in specs.items():
            (build.CHARTS / f"{cid}.json").write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":")))

    findings = [{k: v for k, v in d.items() if k != "figures"} for d in content["findings"]]
    out = {
        **{k: v for k, v in content.items() if k not in ("notes", "measures", "findings")},
        "findings": findings,
        "measures": table,
        "verdicts": tested,
        "untestable": untested,
        "counts": {SHOWN[c]: n for c, n in zip(SHOWN, specs["audit-verdicts"]["series"][0]["data"], strict=True)},
        "charts": CHART_IDS,
        "record": f"{build.REPO}/blob/main/docs/audit-ip-australia.md",
        "adr": f"{build.REPO}/blob/main/docs/adr/0024-audit-against-ip-australia.md",
    }
    return out, problems


def stale_charts() -> list[str]:
    """The audit charts whose committed JSON differs from what the build makes (for the tests)."""
    content = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))
    tested, untested = verdicts(RECORD.read_text(encoding="utf-8"))
    specs = charts(content, tested, untested, _csv("benchmark.csv"), _csv("context.csv"))
    stale = []
    for cid, spec in specs.items():
        p = build.CHARTS / f"{cid}.json"
        if not p.exists() or json.loads(p.read_text(encoding="utf-8")) != json.loads(json.dumps(spec)):
            stale.append(cid)
    return stale
