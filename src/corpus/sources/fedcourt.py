"""IP judgments of the Federal Court, the Full Federal Court, the High Court and the Copyright Tribunal.

Enforcement costs and outcomes (Q1.3): which rights are litigated, by whom, in which technologies and industries, how
long cases take from hearing to judgment, and which firms act. From the Open Australian Legal Corpus (Isaacus,
https://huggingface.co/datasets/isaacus/open-australian-legal-corpus; the collection is CC BY 4.0; the courts permit
judgments to be reproduced unaltered with acknowledgement of the court and the source), which holds every decision of
those courts to its last collection (10 March 2025 for this release). The corpus is streamed (9.4 GB) and only IP
decisions are kept: those the Federal Court files under the Intellectual Property practice area, or whose catchwords
or legislation name an IP Act, or (older judgments, without a cover page) whose opening cites one; every Copyright
Tribunal decision; High Court decisions whose opening cites an IP Act. Raw: those decisions (R2, gzipped JSON lines).

Processed (both in R2, because case names include individuals' names):
- `judgments`: one row per decision, with the fields of the Federal Court's cover page (court, judges, dates of
  hearing and judgment, catchwords, legislation, cases cited, practice area and sub-area, registry, number of
  paragraphs, solicitors' firms; counsel's names are left out; dates as written, and `*_last` as the last day
  they name, so a hearing over several days gives its last day), the rights involved (`rights`, from catchwords,
  legislation and sub-area) and the IP Acts cited in the text with counts.
- `judgment_text`: the full text of each decision, by `version_id`, for text analysis (outcomes, damages, costs).
"""

from __future__ import annotations

import gzip
import json
import re

import pandas as pd
import requests

from ..core import CorpusError, Ctx

URL = "https://huggingface.co/datasets/isaacus/open-australian-legal-corpus/resolve/main/corpus.jsonl"
COURTS = {"federal_court_of_australia", "high_court_of_australia"}

ACTS = {
    "patents": r"Patents Act (1990|1952|1903)",
    "trade_marks": r"Trade Marks Act (1995|1955|1905)",
    "designs": r"Designs Act (2003|1906)",
    "copyright": r"Copyright Act 1968",
    "plant_breeders_rights": r"Plant Breeder'?s'? Rights Act 1994|Plant Variety Rights Act 1987",
    "circuit_layouts": r"Circuit Layouts Act 1989",
}
RIGHTS = {
    "patents": r"\bPATENTS?\b|\bpatent",
    "trade_marks": r"TRADE ?MARKS?|trade ?mark",
    "designs": r"\bDESIGNS?\b|registered design",
    "copyright": r"COPYRIGHT|copyright",
    "plant_breeders_rights": r"PLANT BREEDER|plant breeder",
    "circuit_layouts": r"CIRCUIT LAYOUT|circuit layout",
    "passing_off": r"PASSING OFF|passing off",
    "confidential_information": r"CONFIDENTIAL INFORMATION|confidential information",
}
IP_HEAD = re.compile(r"^\s*(INTELLECTUAL PROPERTY|PATENTS?|TRADE ?MARKS?|COPYRIGHT|DESIGNS?|PLANT BREEDER)", re.M)
FIELD = re.compile(r"^([A-Z][A-Za-z()/' ]{2,60}):\s+(.*)$")
STOP = re.compile(r"^\s*(ORDERS|REASONS FOR JUDGMENT|JUDGMENT|THE COURT ORDERS)\s*$")
KEEP_FIELDS = {
    "file number": "file_number",
    "judge": "judges",
    "judges": "judges",
    "judgment of": "judges",
    "date of judgment": "date_of_judgment",
    "date of hearing": "date_of_hearing",
    "date of last submissions": "date_of_last_submissions",
    "catchwords": "catchwords",
    "legislation": "legislation",
    "cases cited": "cases_cited",
    "registry": "registry",
    "division": "division",
    "national practice area": "practice_area",
    "sub-area": "sub_area",
    "sub area": "sub_area",
    "category": "category",
    "number of paragraphs": "number_of_paragraphs",
    "appeal from": "appeal_from",
}


def cover(text: str) -> dict:
    """The Federal Court's cover page: 'Field:   value' lines, values continued on indented lines."""
    out: dict[str, list[str]] = {}
    key = None
    for line in text[:30000].splitlines():
        if STOP.match(line):
            break
        m = FIELD.match(line)
        if m:
            name = m.group(1).strip().lower()
            if name.startswith("solicitor"):
                key = "solicitors"
            else:
                key = KEEP_FIELDS.get(name, "_skip")
            if m.group(2).strip():
                out.setdefault(key, []).append(m.group(2).strip())
        elif key and line.startswith((" ", "\t")) and line.strip():
            out.setdefault(key, []).append(line.strip())
        elif not line.strip():
            continue
        else:
            key = None
    out.pop("_skip", None)
    out = {k: list(dict.fromkeys(v)) if k in ("judges", "solicitors") else v for k, v in out.items()}
    sep = {"catchwords": "\n", "legislation": "; ", "cases_cited": "\n", "solicitors": "; "}
    return {k: sep.get(k, " ").join(v) for k, v in out.items()}


def last_date(s) -> str | None:
    """'15-16 June 2010', '26 and 27 November 2013' -> the last day mentioned, as text pandas can parse."""
    found = re.findall(r"(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})", s or "")
    return " ".join(found[-1]) if found else None


def court(citation: str) -> str | None:
    m = re.search(r"\[\d{4}\]\s+([A-Za-z]+)\s+\d+", citation or "")
    return m.group(1) if m else None


def is_ip(d: dict) -> bool:
    if court(d["citation"]) == "ACopyT":
        return True
    head = d["text"][:12000]
    if d["source"] == "federal_court_of_australia":
        c = cover(head)
        if c.get("practice_area", "").lower().startswith("intellectual property"):
            return True
        if IP_HEAD.search(c.get("catchwords", "")):
            return True
        if any(re.search(a, c.get("legislation", "")) for a in ACTS.values()):
            return True
        if "catchwords" in c:
            return False
    return sum(len(re.findall(a, head)) for a in ACTS.values()) >= 2


def _stream(ctx: Ctx):
    """Yield the IP decisions, from the cached extract or by streaming the corpus once."""
    p = ctx.cache / "ip_decisions.jsonl.gz"
    if not p.exists():
        tmp = p.with_suffix(".part")
        p.parent.mkdir(parents=True, exist_ok=True)
        n = kept = 0
        with requests.get(URL, stream=True, timeout=300) as r, gzip.open(tmp, "wt") as out:
            if r.status_code != 200:
                raise CorpusError(f"fedcourt: GET {URL} answered {r.status_code}")
            for line in r.iter_lines():
                n += 1
                d = json.loads(line)
                if d.get("type") == "decision" and d.get("source") in COURTS and is_ip(d):
                    out.write(json.dumps(d, ensure_ascii=False) + "\n")
                    kept += 1
                if n % 20000 == 0:
                    ctx.log(f"{n:,} documents read, {kept:,} IP decisions")
        tmp.replace(p)
    ctx.keep_raw(p, keep="r2", url=URL)
    with gzip.open(p, "rt") as f:
        for line in f:
            yield json.loads(line)


def run(ctx: Ctx) -> None:
    rows, texts = [], []
    for d in _stream(ctx):
        c = cover(d["text"]) if d["source"] == "federal_court_of_australia" else {}
        basis = " ".join([c.get("catchwords", ""), c.get("legislation", ""), c.get("sub_area", "")])
        if not basis.strip():
            basis = d["text"][:12000]
        acts = {k: len(re.findall(a, d["text"])) for k, a in ACTS.items()}
        rows.append(
            {
                "version_id": d["version_id"],
                "citation": d["citation"],
                "court": court(d["citation"]),
                "date": d["date"],
                "url": d["url"],
                **{k: c.get(k) for k in dict.fromkeys(KEEP_FIELDS.values())},
                "solicitors": c.get("solicitors"),
                "rights": "; ".join(k for k, rx in RIGHTS.items() if re.search(rx, basis)) or None,
                **{f"cites_{k}": v for k, v in acts.items()},
                "cases_cited_count": len([x for x in (c.get("cases_cited") or "").split("\n") if x.strip()]) or None,
                "characters": len(d["text"]),
                "when_scraped": d["when_scraped"],
            }
        )
        texts.append({"version_id": d["version_id"], "text": d["text"]})
    df = pd.DataFrame(rows)
    for col in ("date_of_judgment", "date_of_hearing", "date_of_last_submissions"):
        df[col + "_last"] = pd.to_datetime(df[col].map(last_date), errors="coerce", format="mixed").dt.date
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["number_of_paragraphs"] = pd.to_numeric(df["number_of_paragraphs"], errors="coerce").astype("Int64")
    df = df.sort_values(["date", "citation"]).reset_index(drop=True)
    ctx.note(f"{len(df):,} IP decisions; corpus collected to {df['when_scraped'].max()[:10]}")
    ctx.table(df, "judgments", keep="r2", describe="IP judgments, cover-page fields, rights and IP Acts cited")
    ctx.table(pd.DataFrame(texts), "judgment_text", keep="r2", describe="Full text of each IP judgment")
