"""The Global Innovation Index 2026: WIPO's data file (data/raw/wipo-gii/gii-2026-data.xlsx) and Appendix III.

Read as Econ's `econ.ingest.gii` reads it: the Index Structure sheet gives the tree (Index, SubIndex, Pillar,
SubPillar, Indicator) and each indicator's PROFILE (Score or Value, as the printed profile shows it); the Data sheet
gives each economy's score (0-100), rank and screened value. Every node gets a score variable; an indicator whose
profile shows a value also gets a value variable, in its own unit. Appendix III marks the indicators where a higher
value is worse ("bads", superscript a) and those given half weight (superscript b): the scores already turn bads
round, the values do not.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from statistics import median

import pandas as pd

from ..lenses import Lenses
from ..model import BuildError, EconVar, clean, number

SRC = "gii"
_MARKS = re.compile(r"[*†]+$")
_HEAD = re.compile(r"\*\*(\d+\.\d+\.\d+) (.+?)\*\*")


def _num(n) -> str:
    return "" if n is None or (isinstance(n, float) and pd.isna(n)) else str(n).strip()


def vid(num: str, what: str = "score") -> str:
    return f"gii:{what}:{num or 'GII'}"


def appendix_flags(path: Path) -> dict[str, dict[str, bool]]:
    """Appendix III's markers per indicator number (as in the data file, e.g. IN.4.3.1)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    out: dict[str, dict[str, bool]] = {}
    for i, line in enumerate(lines):
        m = _HEAD.search(line)
        if not m:
            continue
        num = m.group(1)
        pillar = int(num.split(".")[0])
        key = f"{'IN' if pillar <= 5 else 'OUT'}.{num}"
        for nxt in lines[i + 1 : i + 6]:
            if " | " in nxt:
                sups = "".join(re.findall(r"<sup>([^<]*)</sup>", nxt))
                out[key] = {"bad": "a" in sups, "half_weight": "b" in sups}
                break
    return out


def read(path: Path, appendix: Path, lenses: Lenses):
    try:
        book = pd.read_excel(path, sheet_name=None, engine="calamine")
        structure, econ, data = book["Index Structure"], book["Economies"], book["Data"]
    except Exception as e:  # noqa: BLE001 - one line naming the file is the point
        raise BuildError(f"gii: cannot read {path} ({e}); check it is WIPO's GII data file") from e
    flags = appendix_flags(appendix)

    economies = {}
    for r in econ.itertuples(index=False):
        economies[r.ISO3] = {
            "name": clean(r.ECONOMY_NAME),
            "income": clean(r.INCOME_GRP),
            "income_code": clean(r.INCOME_GRP_CODE),
            "region": clean(r.SUBREG_UN),
        }

    nodes = []
    for r in structure.itertuples(index=False):
        num = _num(r.NUM)
        raw = clean(r.NAME)
        marks = _MARKS.search(raw or "")
        nodes.append(
            {
                "num": num,
                "name": _MARKS.sub("", raw).strip(),
                "marks": marks.group(0) if marks else "",
                "level": clean(r.LEVEL_TYPE),
                "type": clean(r.TYPE),
                "profile": clean(r.PROFILE),
                "description": clean(r.DESCRIPTION),
                "source": clean(r.SOURCE),
                "website": clean(r.WEBSITE),
                **flags.get(num, {"bad": False, "half_weight": False}),
            }
        )
    by_num = {n["num"]: n for n in nodes}

    rows: dict[tuple[str, str], dict] = {}
    for r in data.to_dict("records"):
        rows[(r["ISO3"], _num(r["NUM"]))] = r
    missing = {k[1] for k in rows} - set(by_num)
    if missing:
        raise BuildError(f"gii: the Data sheet has numbers missing from Index Structure: {sorted(missing)[:5]}")

    variables: list[EconVar] = []
    for n in nodes:
        num = n["num"]
        parent = num.rsplit(".", 1)[0] if "." in num else ("" if num else None)
        topic = _topic(num, by_num)
        lens = lenses.of("gii", num)
        score = {iso: number(rows.get((iso, num), {}).get("SCORE")) for iso in economies}
        years = {iso: number(rows.get((iso, num), {}).get("DATAYR")) for iso in economies}
        years = {k: int(v) for k, v in years.items() if v is not None}
        mode_year = str(Counter(years.values()).most_common(1)[0][0]) if years else "2026 edition"
        label = "Global Innovation Index" if not num else f"{num} {n['name']}"
        about = _about(n)
        variables.append(
            EconVar(
                id=vid(num),
                name=f"{label} (score)",
                source=SRC,
                topic=topic,
                lens=lens,
                unit="score, 0-100",
                year=mode_year,
                values={k: v for k, v in score.items() if v is not None},
                description=about,
                parts_of=[vid(parent)] if parent is not None else [],
                kind="index",
                years=years if years else {},
            )
        )
        if n["level"] == "Indicator" and n["profile"] == "Value":
            value = {iso: number(rows.get((iso, num), {}).get("VALUE_SCREEN")) for iso in economies}
            variables.append(
                EconVar(
                    id=vid(num, "value"),
                    name=f"{label} (value)",
                    source=SRC,
                    topic=topic,
                    lens=lens,
                    unit=_unit(n["name"]),
                    year=mode_year,
                    values={k: v for k, v in value.items() if v is not None},
                    description=about,
                    parts_of=[vid(num)],
                    kind="value",
                    years=years,
                    note="Higher is worse (a 'bad' in Appendix III); the score turns it round." if n["bad"] else None,
                )
            )

    for col, name, unit in [
        ("POP", "Population", "thousands"),
        ("PPPGDP", "GDP, PPP", "billions of PPP$"),
        ("PPPPC", "GDP per capita, PPP", "PPP$"),
    ]:
        variables.append(
            EconVar(
                id=f"gii:economy:{col}",
                name=f"{name} (GII economy data)",
                source=SRC,
                topic="Economy size",
                lens="context",
                unit=unit,
                year="2026 edition",
                values={r.ISO3: v for r in econ.itertuples(index=False) if (v := number(getattr(r, col))) is not None},
                description=f"{name} as the GII 2026 data file gives it for each economy.",
            )
        )

    page = _page(nodes, rows, economies)
    return (
        economies,
        variables,
        page,
        {
            "nodes": len(nodes),
            "economies": len(economies),
            "bads": sum(n["bad"] for n in nodes),
            "half_weight": sum(n["half_weight"] for n in nodes),
        },
    )


def _topic(num: str, by_num: dict) -> str:
    if num in ("", "IN", "OUT"):
        return "GII headline"
    pillar = ".".join(num.split(".")[:2])
    return f"GII: {by_num[pillar]['name']}"


def _about(n: dict) -> str | None:
    bits = [n["description"]]
    if n["type"]:
        bits.append(
            {"Index": "A composite indicator.", "Survey": "A survey question.", "Data": "Hard data."}.get(n["type"], "")
        )
    if n["source"]:
        bits.append(f"Source: {n['source']}.")
    return " ".join(b for b in bits if b) or None


def _unit(name: str) -> str | None:
    m = re.search(r",\s*([^,]+)$", name)
    return m.group(1).strip() if m else None


def _page(nodes, rows, economies) -> dict:
    """What the GII breakdown page shows: Australia's numbers on every node, with the field to compare against."""
    high = [iso for iso, e in economies.items() if e["income_code"] == "HI"]
    out_nodes = []
    for n in nodes:
        num = n["num"]
        au = rows.get(("AUS", num), {})
        scores = {iso: number(rows.get((iso, num), {}).get("SCORE")) for iso in economies}
        scored = {k: v for k, v in scores.items() if v is not None}
        best = max(scored.items(), key=lambda kv: (kv[1], kv[0]), default=None)
        hi = [scored[i] for i in high if i in scored]
        out_nodes.append(
            {
                **{
                    k: n[k]
                    for k in (
                        "num",
                        "name",
                        "marks",
                        "level",
                        "type",
                        "profile",
                        "description",
                        "source",
                        "website",
                        "bad",
                        "half_weight",
                    )
                },
                "au": {
                    "score": number(au.get("SCORE")),
                    "rank": number(au.get("RANK")),
                    "value": number(au.get("VALUE_SCREEN")),
                    "year": number(au.get("DATAYR")),
                    "sw_overall": clean(au.get("SW_OVERALL")),
                    "sw_incgrp": clean(au.get("SW_INCGRP")),
                    "outdated": bool(number(au.get("OUTDATED"))),
                    "dmc": bool(number(au.get("DMC"))),
                },
                "n_scored": len(scored),
                "median_all": median(scored.values()) if scored else None,
                "median_high_income": median(hi) if hi else None,
                "best": {"iso3": best[0], "name": economies[best[0]]["name"], "score": best[1]} if best else None,
            }
        )
    league = []
    for iso, e in economies.items():
        r = rows.get((iso, ""), {})
        if number(r.get("SCORE")) is not None:
            league.append(
                {
                    "iso3": iso,
                    "name": e["name"],
                    "score": number(r.get("SCORE")),
                    "rank": number(r.get("RANK")),
                    "income": e["income"],
                    "region": e["region"],
                }
            )
    league.sort(key=lambda x: (x["rank"], x["iso3"]))
    return {
        "edition": 2026,
        "economies": len(economies),
        "high_income": len(high),
        "nodes": out_nodes,
        "league": league,
    }
